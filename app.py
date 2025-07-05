from flask import Flask, render_template, request, redirect, url_for, flash, make_response
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
import os
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import json
import csv
from io import StringIO
from sqlalchemy import func

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your_super_secret_key_here_please_change_this')

# --- Настройка SQLAlchemy ---
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///site.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

@app.context_processor
def utility_processor():
    def format_datetime_for_display(dt_str):
        if not dt_str:
            return "Н/Д"
        try:
            dt_obj = datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
            days_of_week_full = ["Понеділок", "Вівторок", "Середа", "Четвер", "П'ятниця", "Субота", "Неділя"]
            day_name = days_of_week_full[dt_obj.weekday()]
            return dt_obj.strftime(f'{day_name}, %d.%m.%Y %H:%M')
        except ValueError:
            try:
                dt_obj = datetime.strptime(dt_str, '%Y-%m-%d')
                return dt_obj.strftime('%d.%m.%Y')
            except ValueError:
                return dt_str
    
    def format_date_only_for_display(date_str):
        if not date_str:
            return "Н/Д"
        try:
            dt_obj = datetime.strptime(date_str, '%Y-%m-%d')
            return dt_obj.strftime('%d.%m.%Y')
        except ValueError:
            return date_str
            
    return dict(enumerate=enumerate, 
                format_datetime_for_display=format_datetime_for_display,
                format_date_only_for_display=format_date_only_for_display)

# --- Настройка Flask-Login ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# --- Налаштування Flask-Mail ---
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', 'aktivnosportivnimi@gmail.com')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', 'your_app_password')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', 'aktivnosportivnimi@gmail.com')

mail = Mail(app)


# --- Модели базы данных ---
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='user')
    has_paid_fees = db.Column(db.Boolean, default=False)
    last_fee_payment_date = db.Column(db.String(10), nullable=True, default=None)
    email = db.Column(db.String(120), unique=True, nullable=True)
    email_confirmed = db.Column(db.Boolean, default=False)
    email_confirmation_token = db.Column(db.String(256), nullable=True)

    def is_admin(self):
        return self.role == 'admin'

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.email_confirmed}')"

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(20), nullable=False)
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

class FeeLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    payment_date = db.Column(db.String(10), nullable=False)
    payment_period = db.Column(db.String(50), nullable=True, default=None)
    logged_by_admin = db.Column(db.String(80), nullable=False)
    logged_at = db.Column(db.String(20), default=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    def __repr__(self):
        return f"FeeLog('{self.username}', '{self.payment_date}', '{self.payment_period}', '{self.logged_by_admin}')"

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

# НОВА МОДЕЛЬ
class FinancialTransaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255), nullable=False)
    date = db.Column(db.String(10), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)
    logged_by_admin = db.Column(db.String(80), nullable=False)
    logged_at = db.Column(db.String(20), default=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    def __repr__(self):
        return f"FinancialTransaction('{self.date}', '{self.description}', {self.amount})"

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
        email = request.form['email'] 

        existing_user = User.query.filter_by(username=username).first()
        existing_email = User.query.filter_by(email=email).first()
        
        if existing_user:
            flash('Користувач з таким ім\'ям вже існує.', 'error')
            return render_template('register.html')
        if existing_email:
            flash('Ця електронна пошта вже зареєстрована.', 'error')
            return render_template('register.html')


        hashed_password = generate_password_hash(password)
        
        is_first_user = (User.query.count() == 0)
        new_user_role = 'admin' if is_first_user else 'user' 
        
        confirmation_token = os.urandom(24).hex() 
        new_user = User(username=username, password_hash=hashed_password, role=new_user_role, 
                        has_paid_fees=False, email=email, email_confirmed=False, 
                        email_confirmation_token=confirmation_token)
        db.session.add(new_user)
        db.session.commit()
        
        try:
            confirm_url = url_for('confirm_email', token=confirmation_token, _external=True)
            msg = Message('Будь ласка, підтвердьте свою електронну пошту', 
                          sender=app.config['MAIL_DEFAULT_SENDER'],
                          recipients=[email])
            msg.body = f"""Привіт, {username}!

Дякуємо за реєстрацію в Клубі спортивних ігор.
Будь ласка, підтвердьте свою електронну пошту, перейшовши за посиланням:
{confirm_url}

Якщо ви не реєструвалися на цьому сайті, будь ласка, проігноруйте цей лист.

З повагою,
Команда Клубу спортивних ігор
"""
            mail.send(msg)
            flash('Реєстрація успішна! На вашу електронну пошту було надіслано лист для підтвердження. Будь ласка, перевірте свою скриньку.', 'success')
        except Exception as e:
            flash(f'Реєстрація успішна, але не вдалося надіслати лист підтвердження: {e}. Будь ласка, зв\'яжіться з адміністратором.', 'warning')

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
            if not user_found.email_confirmed:
                flash('Будь ласка, підтвердьте свою електронну пошту, щоб увійти.', 'warning')
                return redirect(url_for('login'))

            login_user(user_found)
            
            if user_found.has_paid_fees:
                flash('Вхід успішний! Ми дуже вдячні вам за ваш внесок на підтримку клубу.', 'success')
            else:
                flash('Вхід успішний! На жаль, ми ще не отримали від вас членський внесок. Нам буде важко без вашої допомоги організовувати діяльність клубу(', 'info') 

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

@app.route('/confirm/<token>')
def confirm_email(token):
    user = User.query.filter_by(email_confirmation_token=token).first()
    if user:
        user.email_confirmed = True
        user.email_confirmation_token = None
        db.session.commit()
        flash('Ваша електронна пошта успішно підтверджена! Тепер ви можете увійти.', 'success')
        return redirect(url_for('login'))
    else:
        flash('Недійсний або прострочений токен підтвердження.', 'error')
        return redirect(url_for('login'))


# --- Основные маршруты приложения ---
@app.route('/')
def index():
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
                new_log_entry = GameLog(event_name=event.name, event_date=event.date, active_participants=active_participants, cancelled_participants=cancelled_participants, teams=event.teams, image_url=event.image_url)
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
            is_participant = any(p_entry.get("username") == current_user.username and p_entry.get("status") == "active" for p_entry in event.participants)
            
            if is_participant:
                try:
                    event_dt = datetime.strptime(event.date, '%Y-%m-%d %H:%M:%S')
                    if now <= event_dt <= seven_days_from_now:
                        user_events_next_7_days.append(event)
                except ValueError:
                    continue
    
    return render_template('index.html', events=events_with_team_info, current_user=current_user, users_fee_status=users_fee_status, user_events_next_7_days=user_events_next_7_days)

@app.route('/add_event', methods=['GET', 'POST'])
@login_required
def add_event():
    if not current_user.is_admin():
        flash('У вас немає дозволу на додавання подій.', 'error')
        return redirect(url_for('index'))

    if request.method == 'GET':
        return render_template('add_event.html', current_user=current_user)

    event_name = request.form['event_name']
    event_datetime_str = request.form['event_datetime'] 
    image_url = request.form.get('image_url') 

    if event_name and event_datetime_str:
        try:
            dt_object = datetime.strptime(event_datetime_str, '%Y-%m-%dT%H:%M')
            formatted_datetime = dt_object.strftime('%Y-%m-%d %H:%M:%S')
            new_event = Event(name=event_name, date=formatted_datetime, participants_json='[]', teams_json='{}', image_url=image_url if image_url else None)
            db.session.add(new_event)
            db.session.commit()
            flash('Подію успішно додано!', 'success')
            return redirect(url_for('index'))
        except ValueError:
            flash('Неправильний формат дати або часу. Використовуйте РРРР-ММ-ДД HH:MM.', 'error')
    else:
        flash('Будь ласка, заповніть усі поля для події.', 'error')
    
    return render_template('add_event.html', current_user=current_user)

@app.route('/edit_event/<int:event_id>', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    if not current_user.is_admin():
        flash('У вас немає дозволу на редагування подій.', 'error')
        return redirect(url_for('index'))

    event = Event.query.get_or_404(event_id)

    if request.method == 'POST':
        event.name = request.form['event_name']
        event_datetime_str = request.form['event_datetime']
        event.image_url = request.form.get('image_url') or None

        try:
            dt_object = datetime.strptime(event_datetime_str, '%Y-%m-%dT%H:%M')
            event.date = dt_object.strftime('%Y-%m-%d %H:%M:%S')
            db.session.commit()
            flash('Подію успішно оновлено!', 'success')
            return redirect(url_for('index'))
        except ValueError:
            flash('Неправильний формат дати або часу.', 'error')
    
    try:
        event_dt_obj = datetime.strptime(event.date, '%Y-%m-%d %H:%M:%S')
        event.formatted_datetime_local = event_dt_obj.strftime('%Y-%m-%dT%H:%M')
    except ValueError:
        event.formatted_datetime_local = ''

    return render_template('edit_event.html', event=event, current_user=current_user)

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

    found_participant_entry = next((entry for entry in participants_list if entry["username"] == participant_name), None)

    if found_participant_entry:
        registration_time = datetime.strptime(found_participant_entry["timestamp"], '%Y-%m-%d %H:%M:%S')
        if datetime.now() - registration_time > timedelta(hours=1):
            found_participant_entry["status"] = "cancelled"
            flash(f'{participant_name}, вашу участь позначено як "Відмовився" для "{event.name}".', 'info')
        else:
            participants_list.remove(found_participant_entry)
            flash(f'{participant_name}, вашу участь скасовано для "{event.name}".', 'info')
        
        for team_name, members in teams.items():
            if participant_name in members:
                members.remove(participant_name)
    else:
        new_participant_entry = {"username": participant_name, "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "status": "active"}
        participants_list.append(new_participant_entry)
        flash(f'{participant_name}, ви успішно зареєструвалися на "{event.name}".', 'success')
    
    event.participants = participants_list 
    event.teams = teams 
    db.session.commit()

    return redirect(url_for('index'))

# --- Маршруты для объявлений ---
@app.route('/announcements', methods=['GET', 'POST'])
@login_required 
def announcements():
    if request.method == 'POST':
        if not current_user.is_admin():
            flash('У вас немає дозволу на додавання оголошень.', 'error')
            return redirect(url_for('announcements'))

        title = request.form['title']
        content = request.form['content']
        if title and content:
            new_announcement = Announcement(title=title, content=content, date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'), author=current_user.username)
            db.session.add(new_announcement)
            db.session.commit()
            flash('Оголошення успішно додано!', 'success')
            return redirect(url_for('announcements'))
        else:
            flash('Будь ласка, заповніть усі поля для оголошення.', 'error')
    
    all_announcements = Announcement.query.order_by(Announcement.date.desc()).all()
    return render_template('announcements.html', announcements=all_announcements, current_user=current_user)

@app.route('/edit_announcement/<int:announcement_id>', methods=['GET', 'POST'])
@login_required
def edit_announcement(announcement_id):
    if not current_user.is_admin():
        flash('У вас немає дозволу на редагування оголошень.', 'error')
        return redirect(url_for('announcements'))

    announcement = Announcement.query.get_or_404(announcement_id)
    if request.method == 'POST':
        announcement.title = request.form['title']
        announcement.content = request.form['content']
        db.session.commit()
        flash('Оголошення успішно оновлено!', 'success')
        return redirect(url_for('announcements'))
    
    return render_template('edit_announcement.html', announcement=announcement, current_user=current_user)

@app.route('/delete_announcement/<int:announcement_id>', methods=['POST'])
@login_required
def delete_announcement(announcement_id):
    if not current_user.is_admin():
        flash('У вас немає дозволу на видалення оголошень.', 'error')
        return redirect(url_for('announcements'))

    announcement = Announcement.query.get_or_404(announcement_id)
    db.session.delete(announcement)
    db.session.commit()
    flash('Оголошення успішно видалено!', 'success')
    return redirect(url_for('announcements'))

# --- Маршруты для опросов ---
@app.route('/polls', methods=['GET', 'POST'])
@login_required 
def polls():
    if request.method == 'POST':
        if not current_user.is_admin():
            flash('У вас немає дозволу на створення опитувань.', 'error')
            return redirect(url_for('polls'))

        question = request.form['question']
        options_raw = [request.form[f'option{i}'] for i in range(1, 6) if request.form.get(f'option{i}')]
        
        if not question or not options_raw:
            flash('Будь ласка, заповніть питання та хоча б один варіант відповіді.', 'error')
        else:
            options_for_save = [{'text': opt_text, 'votes': 0} for opt_text in options_raw]
            new_poll = Poll(question=question, options_json=json.dumps(options_for_save, ensure_ascii=False), date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'), author=current_user.username)
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
    poll = Poll.query.get_or_404(poll_id)
    
    if current_user.username in poll.voted_users:
        flash('Ви вже проголосували в цьому опитуванні.', 'info')
        return redirect(url_for('polls'))
    
    if vote_option_index is not None:
        try:
            option_index = int(vote_option_index)
            options = poll.options
            if 0 <= option_index < len(options):
                options[option_index]['votes'] += 1
                voted_users = poll.voted_users
                voted_users.append(current_user.username)
                
                poll.options = options
                poll.voted_users = voted_users
                db.session.commit()
                flash('Ваш голос зараховано!', 'success')
            else:
                flash('Недійсний варіант голосування.', 'error')
        except (ValueError, IndexError):
            flash('Недійсний запит голосування.', 'error')
    else:
        flash('Будь ласка, оберіть варіант для голосування.', 'error')
    
    return redirect(url_for('polls'))

# --- НОВИЙ МАРШРУТ ДЛЯ КЕРУВАННЯ ФІНАНСАМИ ---
@app.route('/finances', methods=['GET', 'POST'])
@login_required
def finances():
    if not current_user.is_admin():
        flash('У вас немає дозволу на керування фінансами.', 'error')
        return redirect(url_for('index'))

    # Обробка POST-запитів (додавання транзакцій)
    if request.method == 'POST':
        form_type = request.form.get('form_type')

        # Форма для додавання загальної транзакції (дохід/витрата)
        if form_type == 'add_transaction':
            description = request.form.get('description')
            date_str = request.form.get('date')
            amount_str = request.form.get('amount')
            trans_type = request.form.get('transaction_type')

            if description and date_str and amount_str and trans_type:
                try:
                    amount = float(amount_str)
                    final_amount = -amount if trans_type == 'expense' else amount
                    
                    new_transaction = FinancialTransaction(
                        description=description,
                        date=date_str,
                        amount=final_amount,
                        transaction_type=trans_type,
                        logged_by_admin=current_user.username
                    )
                    db.session.add(new_transaction)
                    db.session.commit()
                    flash('Транзакцію успішно додано!', 'success')
                except ValueError:
                    flash('Невірний формат суми.', 'error')
            else:
                flash('Будь ласка, заповніть усі поля для транзакції.', 'error')

        # Форма для оновлення членського внеску
        elif form_type == 'update_user_fee':
            user_id = request.form.get('user_id')
            fee_date_str = request.form.get('fee_date')
            payment_period = request.form.get('payment_period')
            fee_amount_str = request.form.get('fee_amount')

            user = User.query.get(int(user_id)) if user_id else None
            if user and fee_date_str and payment_period and fee_amount_str:
                try:
                    fee_amount = float(fee_amount_str)
                    user.has_paid_fees = True
                    user.last_fee_payment_date = fee_date_str
                    
                    fee_description = f"Членський внесок ({payment_period}) від {user.username}"
                    new_fee_transaction = FinancialTransaction(
                        description=fee_description,
                        date=fee_date_str,
                        amount=fee_amount,
                        transaction_type='income',
                        logged_by_admin=current_user.username
                    )
                    db.session.add(new_fee_transaction)
                    db.session.commit()
                    flash(f'Внесок для {user.username} успішно оновлено та записано до фінансів.', 'success')
                except ValueError:
                    flash('Невірний формат суми внеску.', 'error')
            else:
                flash('Будь ласка, заповніть усі поля для оновлення внеску.', 'error')

        return redirect(url_for('finances', period=request.args.get('period', '')))

    # Логіка для GET-запиту (відображення сторінки)
    period = request.args.get('period', datetime.now().strftime('%Y-%m'))
    
    try:
        start_of_month = datetime.strptime(period, '%Y-%m')
    except ValueError:
        period = datetime.now().strftime('%Y-%m')
        start_of_month = datetime.strptime(period, '%Y-%m')

    end_of_month = (start_of_month + timedelta(days=32)).replace(day=1)

    start_balance = db.session.query(func.sum(FinancialTransaction.amount)).filter(
        FinancialTransaction.date < start_of_month.strftime('%Y-%m-%d')
    ).scalar() or 0.0

    transactions_this_month = FinancialTransaction.query.filter(
        FinancialTransaction.date >= start_of_month.strftime('%Y-%m-%d'),
        FinancialTransaction.date < end_of_month.strftime('%Y-%m-%d')
    ).order_by(FinancialTransaction.date.desc()).all()

    total_income = sum(t.amount for t in transactions_this_month if t.transaction_type == 'income')
    total_expenses = sum(t.amount for t in transactions_this_month if t.transaction_type == 'expense')

    end_balance = start_balance + total_income + total_expenses

    summary = {
        'start_balance': round(start_balance, 2),
        'total_income': round(total_income, 2),
        'total_expenses': round(abs(total_expenses), 2),
        'end_balance': round(end_balance, 2)
    }

    users = User.query.order_by(User.username).all()
    return render_template('finances.html', 
                           users=users, 
                           transactions=transactions_this_month,
                           summary=summary,
                           period_filter=period,
                           current_user=current_user)

# --- Маршруты для управления командами ---
@app.route('/manage_teams/<int:event_id>')
@login_required
def manage_teams(event_id):
    if not current_user.is_admin():
        flash('У вас немає дозволу на керування командами.', 'error')
        return redirect(url_for('index'))

    event = Event.query.get_or_404(event_id)
    all_active_participants = [p["username"] for p in event.participants if p.get("status") == "active"]
    assigned_participants = {member for members in event.teams.values() for member in members}
    unassigned_participants = [p for p in all_active_participants if p not in assigned_participants]
    
    return render_template('manage_teams.html', event=event, unassigned_participants=unassigned_participants, current_user=current_user)

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
            team_index = key.split('_')[-1]
            team_name = value.strip()
            if team_name:
                members_str = request.form.get(f'team_members_{team_index}', '')
                new_teams[team_name] = [m.strip() for m in members_str.split(',') if m.strip()]
    
    event.teams = new_teams
    db.session.commit()
    flash('Команди успішно збережено!', 'success')
    return redirect(url_for('manage_teams', event_id=event.id))

# --- Маршруты для логів ---
@app.route('/game_log')
@login_required
def game_log():
    if not current_user.is_admin():
        flash('У вас немає дозволу на перегляд журналу подій.', 'error')
        return redirect(url_for('index'))
    
    period_filter = request.args.get('period', '').strip()
    query = GameLog.query
    if period_filter:
        query = query.filter(GameLog.event_date.startswith(period_filter))
    game_logs = query.order_by(GameLog.logged_at.desc()).all()
    return render_template('game_log.html', game_logs=game_logs, current_user=current_user, period_filter=period_filter)

@app.route('/export_game_log')
@login_required
def export_game_log():
    if not current_user.is_admin():
        return redirect(url_for('index'))

    period_filter = request.args.get('period', '').strip()
    query = GameLog.query
    if period_filter:
        query = query.filter(GameLog.event_date.startswith(period_filter))
    game_logs = query.order_by(GameLog.logged_at.desc()).all()

    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(["Назва події", "Дата події", "Час логування", "Активні учасники", "Відмовилися учасники", "Команди", "URL зображення"])
    for log in game_logs:
        cw.writerow([log.event_name, format_datetime_for_display(log.event_date), format_datetime_for_display(log.logged_at), ", ".join(log.active_participants), ", ".join(log.cancelled_participants), json.dumps(log.teams, ensure_ascii=False), log.image_url or ""])
    
    output = si.getvalue()
    response = make_response('\ufeff' + output)
    response.headers["Content-Disposition"] = "attachment; filename=game_log.csv"
    response.headers["Content-type"] = "text/csv; charset=utf-8"
    return response

@app.route('/fee_log')
@login_required
def fee_log():
    if not current_user.is_admin():
        flash('У вас немає дозволу на перегляд журналу оплат.', 'error')
        return redirect(url_for('index'))
    
    period_filter = request.args.get('period', '').strip()
    query = FeeLog.query
    if period_filter:
        query = query.filter(FeeLog.payment_period == period_filter)
    fee_logs = query.order_by(FeeLog.logged_at.desc()).all()
    return render_template('fee_log.html', fee_logs=fee_logs, current_user=current_user, period_filter=period_filter)

@app.route('/export_fee_log')
@login_required
def export_fee_log():
    if not current_user.is_admin():
        return redirect(url_for('index'))

    period_filter = request.args.get('period', '').strip()
    query = FeeLog.query
    if period_filter:
        query = query.filter(FeeLog.payment_period == period_filter)
    fee_logs = query.order_by(FeeLog.logged_at.desc()).all()
    
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(["Користувач", "Дата оплати", "Період розрахунків", "Хто відмітив", "Час логування"])
    for log in fee_logs:
        cw.writerow([log.username, format_date_only_for_display(log.payment_date), log.payment_period or "", log.logged_by_admin, format_datetime_for_display(log.logged_at)])
    
    output = si.getvalue()
    response = make_response('\ufeff' + output)
    response.headers["Content-Disposition"] = "attachment; filename=fee_log.csv"
    response.headers["Content-type"] = "text/csv; charset=utf-8"
    return response

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)