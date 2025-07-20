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
import itertools

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your_super_secret_key_here_please_change_this')

# --- Настройка SQLAlchemy ---
database_url = os.environ.get('DATABASE_URL', 'sqlite:///site.db')
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- Палітра кольорів для команд ---
TEAM_COLORS_PALETTE = [
    '#e0f7fa', '#dcedc8', '#fff9c4', '#ffcdd2', '#e1bee7', 
    '#d1c4e9', '#c5cae9', '#bbdefb', '#b2ebf2', '#b2dfdb'
]

@app.context_processor
def utility_processor():
    def format_datetime_for_display(dt_str):
        if not dt_str: return "Н/Д"
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
        if not date_str: return "Н/Д"
        try:
            dt_obj = datetime.strptime(date_str, '%Y-%m-%d')
            return dt_obj.strftime('%d.%m.%Y')
        except ValueError:
            return date_str
            
    return dict(enumerate=enumerate, 
                format_datetime_for_display=format_datetime_for_display,
                format_date_only_for_display=format_date_only_for_display)

@app.context_processor
def inject_unread_status():
    if not current_user.is_authenticated:
        return dict(has_unread_announcements=False, has_unread_polls=False)

    seen_items = current_user.seen_items
    
    all_announcement_ids = {a.id for a in Announcement.query.with_entities(Announcement.id).all()}
    seen_announcement_ids = set(seen_items.get('announcements', []))
    has_unread_announcements = bool(all_announcement_ids - seen_announcement_ids)
    
    all_poll_ids = {p.id for p in Poll.query.with_entities(Poll.id).all()}
    seen_poll_ids = set(seen_items.get('polls', []))
    has_unread_polls = bool(all_poll_ids - seen_poll_ids)
    
    return dict(has_unread_announcements=has_unread_announcements, has_unread_polls=has_unread_polls)


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
    nickname = db.Column(db.String(80), nullable=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='user')
    has_paid_fees = db.Column(db.Boolean, default=False)
    last_fee_payment_date = db.Column(db.String(10), nullable=True, default=None)
    email = db.Column(db.String(120), unique=True, nullable=True)
    email_confirmed = db.Column(db.Boolean, default=False)
    email_confirmation_token = db.Column(db.String(256), nullable=True)
    seen_items_json = db.Column(db.Text, default='{}')

    @property
    def seen_items(self):
        try:
            return json.loads(self.seen_items_json)
        except (json.JSONDecodeError, TypeError):
            return {}

    @seen_items.setter
    def seen_items(self, value):
        self.seen_items_json = json.dumps(value)

    def is_admin(self): return self.role == 'admin'
    def is_superuser(self): return self.role == 'superuser'
    def can_manage_events(self): return self.is_admin() or self.is_superuser()
    def can_view_finances(self): return self.is_admin() or self.is_superuser()
    def can_edit_finances(self): return self.is_admin()
    def check_password(self, password): return check_password_hash(self.password_hash, password)
    def __repr__(self): return f"User('{self.username}', '{self.nickname}')"

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(20), nullable=False)
    image_url = db.Column(db.String(255), nullable=True, default=None) 
    participants_json = db.Column(db.Text, default='[]') 
    teams_json = db.Column(db.Text, default='{}')
    comment = db.Column(db.Text, nullable=True)

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
    comment = db.Column(db.Text, nullable=True)

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
        username = request.form['username'].strip()
        nickname = request.form['nickname'].strip()
        password = request.form['password']
        email = request.form['email'].strip()

        if not nickname:
            nickname = username

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Користувач з таким логіном вже існує.', 'error')
            return render_template('register.html')
        
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            flash('Ця електронна пошта вже зареєстрована.', 'error')
            return render_template('register.html')
        
        hashed_password = generate_password_hash(password)
        is_first_user = (User.query.count() == 0)
        new_user_role = 'admin' if is_first_user else 'user' 
        
        confirmation_token = os.urandom(24).hex() 
        new_user = User(
            username=username, 
            nickname=nickname, 
            password_hash=hashed_password, 
            role=new_user_role, 
            email=email, 
            email_confirmation_token=confirmation_token
        )
        db.session.add(new_user)
        db.session.commit()
        
        try:
            confirm_url = url_for('confirm_email', token=confirmation_token, _external=True)
            msg = Message('Будь ласка, підтвердьте свою електронну пошту', sender=app.config['MAIL_DEFAULT_SENDER'], recipients=[email])
            msg.body = f"Привіт, {nickname}!\n\nДякуємо за реєстрацію.\nБудь ласка, підтвердьте свою пошту, перейшовши за посиланням:\n{confirm_url}"
            mail.send(msg)
            flash('Реєстрація успішна! На вашу пошту надіслано лист для підтвердження.', 'success')
        except Exception as e:
            flash(f'Реєстрація успішна, але не вдалося надіслати лист: {e}.', 'warning')

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
            flash(f'Вхід успішний! Привіт, {user_found.nickname or user_found.username}!', 'success')
            return redirect(request.args.get('next') or url_for('index'))
        else:
            flash('Неправильний логін або пароль.', 'error')
    
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
        flash('Ваша пошта успішно підтверджена! Тепер ви можете увійти.', 'success')
        return redirect(url_for('login'))
    else:
        flash('Недійсний токен підтвердження.', 'error')
        return redirect(url_for('login'))

# --- Основные маршруты приложения ---
@app.route('/')
def index():
    current_time = datetime.now()
    events_to_delete = []
    
    # Використовуємо .with_for_update() для уникнення race conditions при багатьох запитах
    all_events_from_db = Event.query.order_by(Event.date).all()
    
    for event in all_events_from_db:
        try:
            event_dt = datetime.strptime(event.date, '%Y-%m-%d %H:%M:%S')
            if event_dt < current_time:
                active_participants = [p["username"] for p in event.participants if p.get("status") == "active"]
                cancelled_participants = [p["username"] for p in event.participants if p.get("status") == "cancelled"]
                new_log_entry = GameLog(
                    event_name=event.name, event_date=event.date,
                    active_participants=active_participants, cancelled_participants=cancelled_participants,
                    teams=event.teams, image_url=event.image_url, comment=event.comment
                )
                db.session.add(new_log_entry)
                events_to_delete.append(event)
        except ValueError:
            flash(f"Подія '{event.name}' має невірний формат дати.", 'error')
            
    if events_to_delete:
        for event in events_to_delete:
            db.session.delete(event)
        db.session.commit()

    all_users = User.query.all()
    users_fee_status = {u.username: u.has_paid_fees for u in all_users}
    user_nicknames = {u.username: u.nickname or u.username for u in all_users}

    events_for_display = Event.query.filter(Event.date >= datetime.now().strftime('%Y-%m-%d %H:%M:%S')).order_by(Event.date).all()
    events_with_team_info = []

    for event in events_for_display:
        unique_team_names = sorted(list(event.teams.keys()))
        color_cycle = itertools.cycle(TEAM_COLORS_PALETTE)
        event.team_colors = {team_name: next(color_cycle) for team_name in unique_team_names}

        processed_participants = []
        for p_entry in event.participants:
            p_entry_with_team = p_entry.copy()
            p_entry_with_team['nickname'] = user_nicknames.get(p_entry['username'], p_entry['username'])
            p_entry_with_team['assigned_team_name'] = next((name for name, members in event.teams.items() if p_entry["username"] in members), '')
            processed_participants.append(p_entry_with_team)
        
        event.processed_participants = sorted(
            processed_participants,
            key=lambda x: (x.get('assigned_team_name') or 'zzzzzz', datetime.strptime(x['timestamp'], '%Y-%m-%d %H:%M:%S'))
        )
        events_with_team_info.append(event)
    
    user_events_next_7_days = []
    if current_user.is_authenticated:
        now = datetime.now()
        seven_days_from_now = now + timedelta(days=7)
        for event in events_for_display:
            if any(p.get("username") == current_user.username and p.get("status") == "active" for p in event.participants):
                try:
                    event_dt = datetime.strptime(event.date, '%Y-%m-%d %H:%M:%S')
                    if now <= event_dt <= seven_days_from_now:
                        user_events_next_7_days.append(event)
                except ValueError: continue

    return render_template('index.html', events=events_with_team_info, current_user=current_user, users_fee_status=users_fee_status, user_nicknames=user_nicknames, user_events_next_7_days=user_events_next_7_days)

# ... (інші маршрути) ...

# --- Маршруты для объявлений ---
@app.route('/announcements', methods=['GET', 'POST'])
@login_required 
def announcements():
    if request.method == 'POST':
        # ЦЯ ДІЯ ЛИШЕ ДЛЯ АДМІНА
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

# --- Маршрут для керування фінансами ---
@app.route('/finances', methods=['GET', 'POST'])
@login_required
def finances():
    # ОНОВЛЕНА ПЕРЕВІРКА
    if not current_user.can_view_finances():
        flash('У вас немає дозволу на перегляд цієї сторінки.', 'error')
        return redirect(url_for('index'))

    if request.method == 'POST':
        # ТІЛЬКИ АДМІН МОЖЕ ЗМІНЮВАТИ ФІНАНСИ
        if not current_user.can_edit_finances():
            flash('У вас немає дозволу на виконання цієї дії.', 'error')
            return redirect(url_for('finances'))

        form_type = request.form.get('form_type')
        if form_type == 'add_transaction':
            description = request.form.get('description')
            date_str = request.form.get('date')
            amount_str = request.form.get('amount')
            trans_type = request.form.get('transaction_type')

            if description and date_str and amount_str and trans_type:
                try:
                    amount = float(amount_str)
                    final_amount = -amount if trans_type == 'expense' else amount
                    new_transaction = FinancialTransaction(description=description, date=date_str, amount=final_amount, transaction_type=trans_type, logged_by_admin=current_user.username)
                    db.session.add(new_transaction)
                    db.session.commit()
                    flash('Транзакцію успішно додано!', 'success')
                except ValueError:
                    flash('Невірний формат суми.', 'error')
            else:
                flash('Будь ласка, заповніть усі поля для транзакції.', 'error')

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
                    new_fee_transaction = FinancialTransaction(description=fee_description, date=fee_date_str, amount=fee_amount, transaction_type='income', logged_by_admin=current_user.username)
                    db.session.add(new_fee_transaction)
                    db.session.commit()
                    flash(f'Внесок для {user.username} успішно оновлено та записано до фінансів.', 'success')
                except ValueError:
                    flash('Невірний формат суми внеску.', 'error')
            else:
                flash('Будь ласка, заповніть усі поля для оновлення внеску.', 'error')

        return redirect(url_for('finances', period=request.args.get('period', '')))

    period = request.args.get('period', datetime.now().strftime('%Y-%m'))
    
    try:
        start_of_month = datetime.strptime(period, '%Y-%m')
    except ValueError:
        period = datetime.now().strftime('%Y-%m')
        start_of_month = datetime.strptime(period, '%Y-%m')

    end_of_month = (start_of_month + timedelta(days=32)).replace(day=1)

    start_balance = db.session.query(func.sum(FinancialTransaction.amount)).filter(FinancialTransaction.date < start_of_month.strftime('%Y-%m-%d')).scalar() or 0.0
    transactions_this_month = FinancialTransaction.query.filter(FinancialTransaction.date >= start_of_month.strftime('%Y-%m-%d'), FinancialTransaction.date < end_of_month.strftime('%Y-%m-%d')).order_by(FinancialTransaction.date.desc()).all()
    total_income = sum(t.amount for t in transactions_this_month if t.transaction_type == 'income')
    total_expenses = sum(t.amount for t in transactions_this_month if t.transaction_type == 'expense')
    end_balance = start_balance + total_income + total_expenses

    summary = {'start_balance': round(start_balance, 2), 'total_income': round(total_income, 2), 'total_expenses': round(abs(total_expenses), 2), 'end_balance': round(end_balance, 2)}
    users = User.query.order_by(User.username).all()
    
    return render_template('finances.html', users=users, transactions=transactions_this_month, summary=summary, period_filter=period, current_user=current_user)

# --- Маршрути для редагування та видалення транзакцій ---
@app.route('/edit_transaction/<int:transaction_id>', methods=['GET', 'POST'])
@login_required
def edit_transaction(transaction_id):
    if not current_user.can_edit_finances():
        flash('У вас немає дозволу на цю дію.', 'error')
        return redirect(url_for('finances'))

    transaction = FinancialTransaction.query.get_or_404(transaction_id)
    if request.method == 'POST':
        # ... (логіка збереження)
        transaction.description = request.form.get('description')
        transaction.date = request.form.get('date')
        transaction.transaction_type = request.form.get('transaction_type')
        try:
            amount = float(request.form.get('amount'))
            transaction.amount = -amount if transaction.transaction_type == 'expense' else amount
            db.session.commit()
            flash('Транзакцію успішно оновлено!', 'success')
            return redirect(url_for('finances'))
        except (ValueError, TypeError):
            flash('Невірний формат суми.', 'error')

    transaction.form_amount = abs(transaction.amount)
    return render_template('edit_transaction.html', transaction=transaction, current_user=current_user)

@app.route('/delete_transaction/<int:transaction_id>', methods=['POST'])
@login_required
def delete_transaction(transaction_id):
    if not current_user.can_edit_finances():
        flash('У вас немає дозволу на цю дію.', 'error')
        return redirect(url_for('finances'))

    transaction = FinancialTransaction.query.get_or_404(transaction_id)
    db.session.delete(transaction)
    db.session.commit()
    flash('Транзакцію успішно видалено.', 'success')
    return redirect(url_for('finances'))

# --- НОВИЙ МАРШРУТ ДЛЯ ОНОВЛЕННЯ РОЛІ КОРІСТУВАЧА ---
@app.route('/update_user_role/<int:user_id>', methods=['POST'])
@login_required
def update_user_role(user_id):
    if not current_user.is_admin():
        flash('Тільки адміністратор може змінювати ролі.', 'error')
        return redirect(url_for('finances'))

    user_to_update = User.query.get_or_404(user_id)
    new_role = request.form.get('role')

    if new_role in ['user', 'superuser', 'admin']:
        # Заборона адміну понижувати власну роль, якщо він останній адмін
        if user_to_update.id == current_user.id and user_to_update.is_admin() and new_role != 'admin':
            admin_count = User.query.filter_by(role='admin').count()
            if admin_count <= 1:
                flash('Ви не можете змінити роль єдиного адміністратора.', 'error')
                return redirect(url_for('finances'))

        user_to_update.role = new_role
        db.session.commit()
        flash(f'Роль для користувача {user_to_update.username} оновлено на "{new_role}".', 'success')
    else:
        flash('Неприпустима роль.', 'error')

    return redirect(url_for('finances'))

# --- Маршруты для управления командами ---
@app.route('/manage_teams/<int:event_id>')
@login_required
def manage_teams(event_id):
    if not current_user.can_manage_events():
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
    if not current_user.can_manage_events():
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
    headers = ["Назва події", "Дата події", "Час логування", "Активні учасники", "Відмовилися учасники", "Команди", "URL зображення", "Коментар"]
    cw.writerow(headers)
    for log in game_logs:
        row = [log.event_name, format_datetime_for_display(log.event_date), format_datetime_for_display(log.logged_at), ", ".join(log.active_participants), ", ".join(log.cancelled_participants), json.dumps(log.teams, ensure_ascii=False), log.image_url or "", log.comment or ""]
        cw.writerow(row)
    
    output = si.getvalue()
    response = make_response('\ufeff' + output)
    response.headers["Content-Disposition"] = "attachment; filename=game_log.csv"
    response.headers["Content-type"] = "text/csv; charset=utf-8"
    return response

@app.route('/export_finances')
@login_required
def export_finances():
    if not current_user.can_view_finances():
        flash('У вас немає дозволу на експорт.', 'error')
        return redirect(url_for('finances'))

    period_filter = request.args.get('period', '').strip()

    query = FinancialTransaction.query
    if period_filter:
        query = query.filter(FinancialTransaction.date.startswith(period_filter))

    transactions = query.order_by(FinancialTransaction.date.asc()).all()

    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(["Дата", "Опис", "Тип", "Сума", "Хто додав", "Час додавання"])
    for t in transactions:
        row = [t.date, t.description, "Дохід" if t.transaction_type == 'income' else "Витрата", t.amount, t.logged_by_admin, format_datetime_for_display(t.logged_at)]
        cw.writerow(row)

    output = si.getvalue()
    filename = f"finances_{period_filter}.csv" if period_filter else "finances_all.csv"
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    response.headers["Content-type"] = "text/csv; charset=utf-8"
    return response


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)