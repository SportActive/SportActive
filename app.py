from flask import Flask, render_template, request, redirect, url_for, flash, make_response
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy 
import os
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta 
import json 
import csv 
from io import StringIO 

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your_super_secret_key_here_please_change_this') 

# --- Настройка SQLAlchemy ---
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///site.db') 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app) 

# db.create_all() (удален из верхнего уровня, теперь только Alembic или в if __name__)

@app.context_processor
def utility_processor():
    def format_datetime_for_display(dt_str):
        if not dt_str:
            return "Н/Д"
        try:
            # Сначала парсим из формата БД (YYYY-MM-DD HH:MM:SS)
            dt_obj = datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
            # Затем форматируем в DD.MM.YYYY HH:MM
            return dt_obj.strftime('%d.%m.%Y %H:%M')
        except ValueError:
            # Если формат не соответствует, пробуем только дату (для last_fee_payment_date)
            try:
                dt_obj = datetime.strptime(dt_str, '%Y-%m-%d')
                return dt_obj.strftime('%d.%m.%Y')
            except ValueError:
                return dt_str # Возвращаем как есть, если не удалось распарсить
    
    def format_date_only_for_display(date_str):
        if not date_str:
            return "Н/Д"
        try:
            # Парсим из формата БД (YYYY-MM-DD)
            dt_obj = datetime.strptime(date_str, '%Y-%m-%d')
            # Форматируем в DD.MM.YYYY
            return dt_obj.strftime('%d.%m.%Y')
        except ValueError:
            return date_str # Возвращаем как есть
            
    return dict(enumerate=enumerate, 
                format_datetime_for_display=format_datetime_for_display,
                format_date_only_for_display=format_date_only_for_display)

# --- Настройка Flask-Login ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# --- Модели базы данных ---
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False) # Увеличено до 256
    role = db.Column(db.String(20), default='user') # 'user' или 'admin'
    has_paid_fees = db.Column(db.Boolean, default=False)
    last_fee_payment_date = db.Column(db.String(10), nullable=True, default=None) # Формат IndexError-MM-DD

    def is_admin(self):
        return self.role == 'admin'

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"User('{self.username}', '{self.role}')"

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(20), nullable=False) # Хранится Jamboree-MM-DD HH:MM:SS
    image_url = db.Column(db.String(255), nullable=True, default=None) 
    participants_json = db.Column(db.Text, default='[]') 
    teams_json = db.Column(db.Text, default='{}')

    @property
    def participants(self):
        return json.loads(self.participants_json)

    @participants.setter
    def participants(self, value):
        self.participants_json = json.dumps(value, ensure_ascii=False)

    @property
    def teams(self):
        return json.loads(self.teams_json)

    @teams.setter
    def teams(self, value):
        self.teams_json = json.dumps(value, ensure_ascii=False)

    def __repr__(self):
        return f"Event('{self.name}', '{self.date}')"

class GameLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_name = db.Column(db.String(100), nullable=False)
    event_date = db.Column(db.String(20), nullable=False)
    logged_at = db.Column(db.String(20), default=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    active_participants_json = db.Column(db.Text, default='[]')
    cancelled_participants_json = db.Column(db.Text, default='[]')
    teams_json = db.Column(db.Text, default='{}')
    image_url = db.Column(db.String(255), nullable=True, default=None)

    @property
    def active_participants(self):
        return json.loads(self.active_participants_json)

    @active_participants.setter
    def active_participants(self, value):
        self.active_participants_json = json.dumps(value, ensure_ascii=False)

    @property
    def cancelled_participants(self):
        return json.loads(self.cancelled_participants_json)

    @cancelled_participants.setter
    def cancelled_participants(self, value):
        self.cancelled_participants_json = json.dumps(value, ensure_ascii=False)

    @property
    def teams(self):
        return json.loads(self.teams_json)

    @teams.setter
    def teams(self, value):
        self.teams_json = json.dumps(value, ensure_ascii=False)

    def __repr__(self):
        return f"GameLog('{self.event_name}', '{self.event_date}')"

# --- НОВАЯ МОДЕЛЬ ДЛЯ ЖУРНАЛА ОПЛАТ ---
class FeeLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    payment_date = db.Column(db.String(10), nullable=False) # Дата оплаты, которую ввел админ (ДД-ММ-РРРР)
    logged_by_admin = db.Column(db.String(80), nullable=False) # Кто из админов отметил оплату
    logged_at = db.Column(db.String(20), default=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S')) # Время, когда запись попала в лог

    def __repr__(self):
        return f"FeeLog('{self.username}', '{self.payment_date}', '{self.logged_by_admin}')"


class Announcement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date = db.Column(db.String(20), nullable=False)
    author = db.Column(db.String(80), nullable=False)

    def __repr__(self):
        return f"Announcement('{self.title}', '{self.date}')"

class Poll(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(255), nullable=False)
    options_json = db.Column(db.Text, nullable=False)
    voted_users_json = db.Column(db.Text, default='[]')
    date = db.Column(db.String(20), nullable=False)
    author = db.Column(db.String(80), nullable=False)

    @property
    def options(self):
        return json.loads(self.options_json)

    @options.setter
    def options(self, value):
        self.options_json = json.dumps(value, ensure_ascii=False)

    @property
    def voted_users(self):
        return json.loads(self.voted_users_json)

    @voted_users.setter
    def voted_users(self, value):
        self.voted_users_json = json.dumps(value, ensure_ascii=False)

    def __repr__(self):
        return f"Poll('{self.question}', '{self.date}')"


# --- Загрузчик пользователя для Flask-Login ---
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# --- Маршруты для аутентификации ---

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Користувач з таким ім\'ям вже існує.', 'error')
            return render_template('register.html')

        hashed_password = generate_password_hash(password)
        
        is_first_user = (User.query.count() == 0)
        new_user_role = 'admin' if is_first_user else 'user' 
        
        new_user = User(username=username, password_hash=hashed_password, role=new_user_role, has_paid_fees=False)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Реєстрація успішна! Тепер ви можете увійти.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user_found = User.query.filter_by(username=username).first()
        
        if user_found and user_found.check_password(password):
            login_user(user_found)
            
            # --- Персоналізоване повідомлення про внески ---
            if user_found.has_paid_fees:
                flash('Вхід успішний! Ми дуже вдячні вам за ваш внесок на підтримку клубу.', 'success')
            else:
                flash('Вхід успішний! На жаль, ми ще не отримали від вас членський внесок. Нам буде важко без вашої допомоги організовувати діяльність клубу(', 'info') 
            # --- Кінець блоку ---

            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            flash('Неправильне ім\'я користувача або пароль.', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Ви вийшли з системи.', 'info')
    return redirect(url_for('index'))

# --- Основные маршруты приложения ---

@app.route('/')
def index():
    # === Логіка автоматичного логування завершених подій ===
    current_time = datetime.now()
    events_to_delete = [] 
    
    all_events_from_db = Event.query.order_by(Event.date).all()
    events_for_display = [] 

    for event in all_events_from_db:
        try:
            event_dt = datetime.strptime(event.date, '%Y-%m-%d %H:%M:%S')
            
            if event_dt < current_time: 
                active_participants = [p["username"] for p in event.participants if p.get("status") == "active"]
                cancelled_participants = [p["username"] for p in event.participants if p.get("status") == "cancelled"]

                new_log_entry = GameLog(
                    event_name=event.name,
                    event_date=event.date,
                    active_participants=active_participants, 
                    cancelled_participants=cancelled_participants, 
                    teams=event.teams, 
                    image_url=event.image_url
                )
                db.session.add(new_log_entry)
                events_to_delete.append(event) 
            else:
                events_for_display.append(event)
        except ValueError:
            events_for_display.append(event)
            flash(f"Подія '{event.name}' має невірний формат дати і не може бути автоматично залогована.", 'error')
            
    for event in events_to_delete:
        db.session.delete(event)
    
    db.session.commit() 
    # === Кінець логіки автоматичного логування ===

    all_users = User.query.all()
    users_fee_status = {u.username: u.has_paid_fees for u in all_users}

    user_events_next_7_days = []
    
    events_with_team_info = []
    for event in events_for_display: 
        processed_participants = []
        for p_entry in event.participants:
            assigned_team_name = ''
            for team_name, members in event.teams.items():
                if p_entry.get("username") in members:
                    assigned_team_name = team_name
                    break 
            
            p_entry_with_team = p_entry.copy()
            p_entry_with_team['assigned_team_name'] = assigned_team_name
            processed_participants.append(p_entry_with_team)
        
        event.processed_participants = processed_participants
        events_with_team_info.append(event)


        if current_user.is_authenticated:
            now = datetime.now()
            seven_days_from_now = now + timedelta(days=7)
            
            is_participant = False
            for p_entry in event.participants: 
                if p_entry.get("username") == current_user.username and p_entry.get("status") == "active":
                    is_participant = True
                    break
            
            if is_participant:
                try:
                    event_dt = datetime.strptime(event.date, '%Y-%m-%d %H:%M:%S')
                    if event_dt >= now and event_dt <= seven_days_from_now:
                        user_events_next_7_days.append(event)
                except ValueError:
                    continue
    
    return render_template('index.html', 
                           events=events_with_team_info, 
                           current_user=current_user, 
                           users_fee_status=users_fee_status,
                           user_events_next_7_days=user_events_next_7_days,
                           current_user_fee_message=current_user_fee_message if 'current_user_fee_message' in locals() else None)

@app.route('/add_event', methods=['POST'])
@login_required
def add_event():
    if not current_user.is_admin():
        flash('У вас немає дозволу на додавання подій.', 'error')
        return redirect(url_for('index'))

    event_name = request.form['event_name']
    event_datetime_str = request.form['event_datetime'] 
    image_url = request.form.get('image_url') 

    if event_name and event_datetime_str:
        try:
            dt_object = datetime.strptime(event_datetime_str, '%Y-%m-%dT%H:%M')
            formatted_datetime = dt_object.strftime('%Y-%m-%d %H:%M:%S')
        except ValueError:
            flash('Неправильний формат дати або часу. Використовуйте РРРР-ММ-ДД HH:MM.', 'error')
            return redirect(url_for('index'))

        new_event = Event(name=event_name, date=formatted_datetime, participants_json='[]', teams_json='{}', image_url=image_url if image_url else None)
        db.session.add(new_event)
        db.session.commit()
        flash('Подію успішно додано!', 'success')
    else:
        flash('Будь ласка, заповніть усі поля для події.', 'error')
    return redirect(url_for('index'))

# --- МАРШРУТ ДЛЯ РЕДАКТИРОВАНИЯ СОБЫТИЯ ---
@app.route('/edit_event/<int:event_id>', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    if not current_user.is_admin():
        flash('У вас немає дозволу на редагування подій.', 'error')
        return redirect(url_for('index'))

    event = Event.query.get_or_404(event_id)

    if request.method == 'POST':
        event_name = request.form['event_name']
        event_datetime_str = request.form['event_datetime']
        image_url = request.form.get('image_url')

        if event_name and event_datetime_str:
            try:
                dt_object = datetime.strptime(event_datetime_str, '%Y-%m-%dT%H:%M')
                formatted_datetime = dt_object.strftime('%Y-%m-%d %H:%M:%S')
            except ValueError:
                flash('Неправильний формат дати або часу. Використовуйте РРРР-ММ-ДД HH:MM.', 'error')
                return render_template('edit_event.html', event=event, current_user=current_user)

            event.name = event_name
            event.date = formatted_datetime
            event.image_url = image_url if image_url else None
            db.session.commit()
            flash('Подію успішно оновлено!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Будь ласка, заповніть усі поля для події.', 'error')
    
    if event.date:
        try:
            event_dt_obj = datetime.strptime(event.date, '%Y-%m-%d %H:%M:%S')
            event.formatted_datetime_local = event_dt_obj.strftime('%Y-%m-%dT%H:%M')
        except ValueError:
            event.formatted_datetime_local = ''
    else:
        event.formatted_datetime_local = ''

    return render_template('edit_event.html', event=event, current_user=current_user)

# --- МАРШРУТ ДЛЯ УДАЛЕНИЯ СОБЫТИЯ ---
@app.route('/delete_event/<int:event_id>', methods=['POST'])
@login_required
def delete_event(event_id):
    if not current_user.is_admin():
        flash('У вас немає дозволу на видалення подій.', 'error')
        return redirect(url_for('index'))

    event = Event.query.get_or_404(event_id)
    db.session.delete(event)
    db.session.commit()
    flash('Подію успішно видалено!', 'success')
    return redirect(url_for('index'))


@app.route('/toggle_participation/<int:event_id>', methods=['POST'])
@login_required
def toggle_participation(event_id):
    participant_name = current_user.username 
    
    event = Event.query.get_or_404(event_id)
    participants_list = event.participants 
    teams = event.teams

    found_participant_entry = None
    for entry in participants_list:
        if entry["username"] == participant_name:
            found_participant_entry = entry
            break

    if found_participant_entry:
        registration_time_str = found_participant_entry["timestamp"]
        registration_time = datetime.strptime(registration_time_str, '%Y-%m-%d %H:%M:%S')
        
        if datetime.now() - registration_time > timedelta(hours=1):
            found_participant_entry["status"] = "cancelled"
            flash(f'{participant_name}, вашу участь позначено як "Відмовився" для "{event.name}".', 'info')
        else:
            participants_list.remove(found_participant_entry)
            flash(f'{participant_name}, вашу участь скасовано для "{event.name}".', 'info')
        
        for team_name in teams:
            if participant_name in teams[team_name]:
                teams[team_name].remove(participant_name)
                break
    else:
        new_participant_entry = {
            "username": participant_name,
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "status": "active"
        }
        participants_list.append(new_participant_entry)
        flash(f'{participant_name}, ви успішно зареєструвалися на "{event.name}".', 'success')
    
    event.participants = participants_list 
    event.teams = teams 
    db.session.commit()

    return redirect(url_for('index'))

# --- Маршруты для объявлений ---

@app.route('/announcements', methods=['GET', 'POST'])
def announcements():
    if request.method == 'POST':
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('У вас немає дозволу на додавання оголошень.', 'error')
            return redirect(url_for('announcements'))

        title = request.form['title']
        content = request.form['content']
        if title and content:
            announcements_data = Announcement(
                title=title,
                content=content,
                date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                author=current_user.username
            )
            db.session.add(announcements_data)
            db.session.commit()
            flash('Оголошення успішно додано!', 'success')
            return redirect(url_for('announcements'))
        else:
            flash('Будь ласка, заповніть усі поля для оголошення.', 'error')
    
    ann = Announcement.query.order_by(Announcement.date.desc()).all()
    return render_template('announcements.html', announcements=ann, current_user=current_user)

# --- Маршруты для опросов ---

@app.route('/polls', methods=['GET', 'POST'])
def polls():
    if request.method == 'POST':
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('У вас немає дозволу на создание опитувань.', 'error')
            return redirect(url_for('polls'))

        question = request.form['question']
        options_raw = [request.form[f'option{i}'] for i in range(1, 6) if f'option{i}' in request.form and request.form[f'option{i}']]
        
        if not question or not options_raw:
            all_polls = Poll.query.order_by(Poll.date.desc()).all()
            flash('Будь ласка, заповніть питання та хоча б один варіант відповіді.', 'error')
            return render_template('polls.html', polls=all_polls, current_user=current_user)

        options_for_save = []
        for opt_text in options_raw:
            options_for_save.append({'text': opt_text, 'votes': 0})

        new_poll = Poll(
            question=question,
            options_json=json.dumps(options_for_save, ensure_ascii=False),
            voted_users_json='[]',
            date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            author=current_user.username
        )
        db.session.add(new_poll)
        db.session.commit()
        flash('Опитування успішно створено!', 'success')
        return redirect(url_for('polls'))
    
    all_polls = Poll.query.order_by(Poll.date.desc()).all()
    return render_template('polls.html', polls=all_polls, current_user=current_user)

@app.route('/vote_poll/<int:poll_id>', methods=['POST'])
@login_required
def vote_poll(poll_id):
    vote_option_index = request.form.get('option_index')
    
    if not vote_option_index:
        flash('Будь ласка, оберіть варіант для голосування.', 'error')
        return redirect(url_for('polls'))

    poll = Poll.query.get_or_404(poll_id)
    
    voted_users = poll.voted_users
    options = poll.options

    if current_user.username in voted_users:
        flash('Ви вже проголосували в цьому опитуванні.', 'info')
        return redirect(url_for('polls'))
    
    try:
        option_index = int(vote_option_index)
        if 0 <= option_index < len(options):
            options[option_index]['votes'] += 1
            voted_users.append(current_user.username)
            
            poll.options = options
            poll.voted_users = voted_users
            db.session.commit()
            
            flash('Ваш голос зараховано!', 'success')
        else:
            flash('Недійсний варіант голосування.', 'error')
    except ValueError:
        flash('Недійсний запит голосування.', 'error')
    
    return redirect(url_for('polls'))

# --- Маршруты для управления взносами ---

@app.route('/manage_fees', methods=['GET', 'POST']) 
@login_required
def manage_fees():
    if not current_user.is_admin():
        flash('У вас немає дозволу на керування внесками.', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        fee_date_str = request.form.get('fee_date')

        if user_id and fee_date_str:
            user = User.query.get(int(user_id))
            if user:
                try:
                    datetime.strptime(fee_date_str, '%Y-%m-%d')
                    user.has_paid_fees = True
                    user.last_fee_payment_date = fee_date_str
                    db.session.commit()
                    # --- НОВЕ: Логування оплати у FeeLog ---
                    new_fee_log = FeeLog(
                        username=user.username,
                        payment_date=fee_date_str,
                        logged_by_admin=current_user.username
                    )
                    db.session.add(new_fee_log)
                    db.session.commit()
                    # --- Кінець НОВОГО блоку ---
                    flash(f'Внески для {user.username} від {fee_date_str} успішно записано.', 'success')
                except ValueError:
                    flash('Недійсний формат дати. Використовуйте РРРР-ММ-ДД.', 'error')
            else:
                flash('Користувача не знайдено.', 'error')
        else:
            pass 
        return redirect(url_for('manage_fees'))

    users = User.query.order_by(User.username).all()
    return render_template('manage_fees.html', users=users, current_user=current_user)


# --- Маршруты для управления командами ---

@app.route('/manage_teams/<int:event_id>')
@login_required
def manage_teams(event_id):
    if not current_user.is_admin():
        flash('У вас немає дозволу на керування командами.', 'error')
        return redirect(url_for('index'))

    event = Event.query.get_or_404(event_id)
    
    all_active_participants = [p["username"] for p in event.participants if p.get("status") == "active"]

    assigned_participants = set()
    for team_name, members in event.teams.items():
        assigned_participants.update(members)
    
    unassigned_participants = [p for p in all_active_participants if p not in assigned_participants]
    
    return render_template('manage_teams.html', 
                           event=event, 
                           unassigned_participants=unassigned_participants,
                           current_user=current_user)

@app.route('/save_teams/<int:event_id>', methods=['POST'])
@login_required
def save_teams(event_id):
    if not current_user.is_admin():
        flash('У вас немає дозволу на керування командами.', 'error')
        return redirect(url_for('index'))

    event = Event.query.get_or_404(event_id)
    
    new_teams = {}
    for key, value in request.form.items():
        if key.startswith('team_name_'):
            team_index = key.replace('team_name_', '')
            team_name = value.strip()
            members_str = request.form.get(f'team_members_{team_index}', '').strip()
            if team_name:
                members = [m.strip() for m in members_str.split(',') if m.strip()]
                new_teams[team_name] = members
    
    event.teams = new_teams
    db.session.commit()
    
    flash('Команди успішно збережено!', 'success')
    
    return redirect(url_for('manage_teams', event_id=event.id))

# --- МАРШРУТЫ ДЛЯ ЖУРНАЛА СОБЫТИЙ (GAME LOG) ---
@app.route('/game_log')
@login_required
def game_log():
    if not current_user.is_admin():
        flash('У вас немає дозволу на перегляд журналу подій.', 'error')
        return redirect(url_for('index'))
    
    # Загружаем логи игр из БД, сортируем по дате логгирования (сначала новые)
    game_logs = GameLog.query.order_by(GameLog.logged_at.desc()).all() 
    return render_template('game_log.html', game_logs=game_logs, current_user=current_user)

@app.route('/export_game_log')
@login_required
def export_game_log():
    if not current_user.is_admin():
        flash('У вас немає дозволу на експорт журналу подій.', 'error')
        return redirect(url_for('index'))

    si = StringIO()
    cw = csv.writer(si)

    headers = [
        "Назва події", "Дата події", "Час логування", "Активні учасники", 
        "Відмовилися учасники", "Команди", "URL зображення"
    ]
    cw.writerow(headers)

    game_logs = GameLog.query.order_by(GameLog.logged_at.desc()).all()
    for log in game_logs:
        row = [
            log.event_name,
            format_datetime_for_display(log.event_date), # Форматируем дату для CSV
            format_datetime_for_display(log.logged_at), # Форматируем дату лога для CSV
            ", ".join(log.active_participants), 
            ", ".join(log.cancelled_participants), 
            json.dumps(log.teams, ensure_ascii=False), 
            log.image_url if log.image_url else ""
        ]
        cw.writerow(row)
    
    output = si.getvalue()
    response = make_response(output)
    response.headers["Content-Disposition"] = "attachment; filename=game_log.csv"
    response.headers["Content-type"] = "text/csv"
    return response

# --- НОВЫЕ МАРШРУТЫ ДЛЯ ЖУРНАЛА ОПЛАТ (FEE LOG) ---
@app.route('/fee_log')
@login_required
def fee_log():
    if not current_user.is_admin():
        flash('У вас немає дозволу на перегляд журналу оплат.', 'error')
        return redirect(url_for('index'))
    
    # Загружаем логи оплат из БД, сортируем по времени логгирования (сначала новые)
    fee_logs = FeeLog.query.order_by(FeeLog.logged_at.desc()).all()
    return render_template('fee_log.html', fee_logs=fee_logs, current_user=current_user)

@app.route('/export_fee_log')
@login_required
def export_fee_log():
    if not current_user.is_admin():
        flash('У вас немає дозволу на експорт журналу оплат.', 'error')
        return redirect(url_for('index'))

    si = StringIO()
    cw = csv.writer(si)

    headers = [
        "Користувач", "Дата оплати", "Хто відмітив", "Час логування"
    ]
    cw.writerow(headers)

    fee_logs = FeeLog.query.order_by(FeeLog.logged_at.desc()).all()
    for log in fee_logs:
        row = [
            log.username,