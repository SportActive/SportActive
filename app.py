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
from itsdangerous import URLSafeTimedSerializer
import logging

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your_super_secret_key_here_please_change_this')

# Налаштування базового логування
logging.basicConfig(level=logging.INFO)

# --- Настройка SQLAlchemy ---
database_url = os.environ.get('DATABASE_URL', 'sqlite:///site.db')
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
s = URLSafeTimedSerializer(app.secret_key)

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
    has_paid_fees = db.Column(db.Boolean, default=False) # Це поле більше не використовується для логіки, але залишаємо для сумісності
    last_fee_payment_date = db.Column(db.String(10), nullable=True, default=None) # Це поле більше не використовується
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

    def get_reset_token(self, expires_sec=1800):
        return s.dumps({'user_id': self.id}, salt='password-reset-salt')

    @staticmethod
    def verify_reset_token(token, expires_sec=1800):
        try:
            data = s.loads(token, salt='password-reset-salt', max_age=expires_sec)
            user_id = data.get('user_id')
        except Exception:
            return None
        return User.query.get(user_id)

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

# НОВА МОДЕЛЬ: Для зв'язку Event-User
class EventParticipant(db.Model):
    __tablename__ = 'event_participant'
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # Зберігаємо team_name на момент запису
    team_name = db.Column(db.String(80), default=None)
    join_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # НОВЕ: Статус для відстеження пізньої відмови або зняття адміном
    status = db.Column(db.String(20), default='active') 

    user = db.relationship('User', backref=db.backref('participations', lazy='dynamic'))
    event = db.relationship('Event', backref=db.backref('real_participants', lazy='dynamic'))

    def __repr__(self):
        return f'<EventParticipant Event:{self.event_id} User:{self.user_id} Status:{self.status}>'

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
    def active_participants(self): return json.loads(self.active_participants_json)
    @active_participants.setter
    def active_participants(self, value): self.active_participants_json = json.dumps(value, ensure_ascii=False)
    @property
    def cancelled_participants(self): return json.loads(self.cancelled_participants_json)
    @cancelled_participants.setter
    def cancelled_participants(self, value): self.cancelled_participants_json = json.dumps(value, ensure_ascii=False)
    @property
    def teams(self): return json.loads(self.teams_json)
    @teams.setter
    def teams(self, value): self.teams_json = json.dumps(value, ensure_ascii=False)
    def __repr__(self): return f"GameLog('{self.event_name}', '{self.event_date}')"

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
    def options(self): return json.loads(self.options_json)
    @options.setter
    def options(self, value): self.options_json = json.dumps(value, ensure_ascii=False)
    @property
    def voted_users(self): return json.loads(self.voted_users_json)
    @voted_users.setter
    def voted_users(self, value): self.voted_users_json = json.dumps(value, ensure_ascii=False)
    def __repr__(self): return f"Poll('{self.question}', '{self.date}')"

class FinancialTransaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255), nullable=False)
    date = db.Column(db.String(10), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)
    logged_by_admin = db.Column(db.String(80), nullable=False)
    logged_at = db.Column(db.String(20), default=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    def __repr__(self): return f"FinancialTransaction('{self.date}', '{self.description}', {self.amount})"


# --- МОДЕЛЬ ЛОГУ ВИДАЛЕНИХ УЧАСНИКІВ ---
class RemovedParticipantLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # Хто був видалений
    removed_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # З якої події
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    # Хто видалив
    admin_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # Причина видалення (фіксована)
    reason = db.Column(db.String(255), default="Перенесено на інший день")
    # Дата і час
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # Зв'язки для легкого доступу
    removed_user = db.relationship('User', foreign_keys=[removed_user_id], backref=db.backref('removal_logs', lazy='dynamic'))
    event = db.relationship('Event', foreign_keys=[event_id], backref=db.backref('removal_logs_by_event', lazy='dynamic'))
    admin = db.relationship('User', foreign_keys=[admin_id], backref=db.backref('removals_made', lazy='dynamic'))

    def __repr__(self):
        return f'<RemovedParticipantLog Event:{self.event_id} User:{self.removed_user_id}>'
# --- КІНЕЦЬ МОДЕЛІ ЛОГУ ---


# --- Загрузчик пользователя для Flask-Login ---
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# --- Тимчасова функція для міграції старих JSON-даних до ORM-моделі (ЗАЛИШЕНО ДЛЯ ПОВНОТИ) ---
def migrate_old_participants_to_orm(app):
    with app.app_context():
        if EventParticipant.query.count() > 0:
            app.logger.info("ORM-таблиця EventParticipant вже містить дані. Міграція пропущена.")
            return

        app.logger.info("Запуск міграції старих даних про учасників...")
        
        events = Event.query.all()
        migrated_count = 0
        
        for event in events:
            old_participants_list = event.participants 
            
            for p_entry in old_participants_list:
                username = p_entry.get('username')
                timestamp_str = p_entry.get('timestamp')
                status = p_entry.get('status')
                
                if status == 'cancelled':
                    continue
                
                user = User.query.filter_by(username=username).first()
                
                if user:
                    try:
                        join_date_dt = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                    except ValueError:
                        app.logger.error(f"Некоректний формат часу для {username} у події {event.id}. Використано поточний час.")
                        join_date_dt = datetime.utcnow()
                        
                    new_participant = EventParticipant(
                        event_id=event.id,
                        user_id=user.id,
                        join_date=join_date_dt
                    )
                    db.session.add(new_participant)
                    migrated_count += 1
                else:
                    app.logger.warning(f"Користувач {username} не знайдений для міграції (Event ID: {event.id}).")

        db.session.commit()
        app.logger.info(f"Міграція завершена. Додано {migrated_count} записів до EventParticipant.")
# --- КІНЕЦЬ тимчасової функції ---


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
            flash(f'Реєстрація успішна, але не вдалося надіслати лист. {e}', 'warning')

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
            
            # ЛОГУВАННЯ УСПІШНОГО ВХОДУ
            app.logger.info(f"Successful login for user: '{username}'")
            
            flash(f'Вхід успішний! Привіт, {user_found.nickname or user_found.username}!', 'success')
            return redirect(request.args.get('next') or url_for('index'))
        else:
            # ЛОГУВАННЯ НЕВДАЛОГО ВХОДУ
            app.logger.warning(f"Failed login attempt for username: '{username}'")
            
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

@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            token = user.get_reset_token()
            reset_url = url_for('reset_password', token=token, _external=True)
            msg = Message('Запит на відновлення пароля', sender=app.config['MAIL_DEFAULT_SENDER'], recipients=[user.email])
            msg.body = f"""Привіт, {user.nickname or user.username}!

Щоб відновити ваш пароль, будь ласка, перейдіть за посиланням нижче.
Посилання буде активним протягом 30 хвилин.

{reset_url}

Якщо ви не робили цей запит, просто проігноруйте цей лист."""
            try:
                mail.send(msg)
            except Exception as e:
                flash(f'Не вдалося надіслати лист. Помилка: {e}', 'error')
                return redirect(url_for('reset_password_request'))
        
        flash('Якщо такий email зареєстровано, на нього було надіслано інструкції з відновлення пароля.', 'info')
        return redirect(url_for('login'))

    return render_template('reset_request.html')

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    user = User.verify_reset_token(token)
    if not user:
        flash('Посилання для відновлення пароля недійсне або його термін дії закінчився.', 'error')
        return redirect(url_for('reset_password_request'))

    if request.method == 'POST':
        password = request.form.get('password')
        user.password_hash = generate_password_hash(password)
        db.session.commit()
        flash('Ваш пароль успішно оновлено! Тепер ви можете увійти.', 'success')
        return redirect(url_for('login'))

    return render_template('reset_password.html', token=token)

# --- МАРШРУТ УЧАСТІ (ОНОВЛЕНО) ---
@app.route('/toggle_participation/<int:event_id>', methods=['POST'])
@login_required
def toggle_participation(event_id):
    event = Event.query.get_or_404(event_id)
    # Шукаємо запис, незалежно від статусу
    participant_entry = EventParticipant.query.filter_by(event_id=event_id, user_id=current_user.id).first()
    
    if participant_entry:
        if participant_entry.status == 'active':
            # --- ЛОГІКА СКАСУВАННЯ УЧАСТІ З ПЕРЕВІРКОЮ ЧАСУ (1-ГОДИННЕ ВІКНО) ---
            time_since_join = datetime.utcnow() - participant_entry.join_date
            
            if time_since_join <= timedelta(hours=1):
                # 1. Скасування впродовж 1 години: Повністю видаляємо
                db.session.delete(participant_entry)
                flash(f'Вашу участь у події "{event.name}" скасовано (повністю видалено).', 'info')
            else:
                # 2. Скасування після 1 години: Змінюємо статус на 'refused'
                participant_entry.status = 'refused'
                flash(f'Ви відмовилися від участі у події "{event.name}". Вас позначено як "Відмовився".', 'warning')
                
            # Видаляємо зі списку команд (логіка JSON)
            teams = event.teams
            for team_name, members in teams.items():
                if current_user.username in members: members.remove(current_user.username)
            event.teams = teams
            
        elif participant_entry.status in ('refused', 'removed'):
            # Якщо вже відмовився/знятий, відновлюємо участь
            participant_entry.status = 'active'
            participant_entry.join_date = datetime.utcnow() # Оновлюємо час запису
            flash(f'Ваша участь у події "{event.name}" відновлена!', 'success')
            
    else:
        # Реєстрація на подію (новий учасник)
        participants_count = EventParticipant.query.filter_by(event_id=event_id).filter(
            EventParticipant.status.in_(['active'])
        ).count()
        
        # NOTE: У вашій моделі Event немає поля max_participants. Якщо воно з'явиться, додати перевірку тут.
        # if event.max_participants is not None and participants_count >= event.max_participants:
        #     flash('На жаль, кількість учасників досягла максимуму.', 'error')
        #     return redirect(url_for('index'))

        new_participant = EventParticipant(
            event_id=event_id, 
            user_id=current_user.id,
            team_name=current_user.nickname or current_user.username,
            status='active' 
        )
        db.session.add(new_participant)
        flash(f'Ви успішно зареєструвалися на подію!', 'success')
    
    db.session.commit()
    return redirect(url_for('index'))


# --- МАРШРУТ ЗНЯТТЯ АДМІНІСТРАТОРОМ (ОНОВЛЕНО) ---
@app.route('/api/event/<int:event_id>/remove_participant', methods=['POST'])
@login_required
def remove_participant_api(event_id):
    """
    Адміністратор знімає учасника з гри миттєво з фіксованою поміткою.
    """
    if not current_user.can_manage_events():
        flash('У вас немає дозволу на цю дію.', 'error')
        return redirect(url_for('index')) 

    user_id_to_remove = request.form.get('user_id', type=int)
    FIXED_REASON = "Перенесено на інший день" # Фіксована помітка
    
    if not user_id_to_remove:
        flash('Не вказано ID користувача для видалення.', 'error')
        return redirect(url_for('index') + f'#event-{event_id}')

    participant_to_update = EventParticipant.query.filter_by(
        event_id=event_id, 
        user_id=user_id_to_remove
    ).first()
    event = Event.query.get(event_id)
    removed_user_obj = User.query.get(user_id_to_remove)

    if participant_to_update and event and removed_user_obj:
        try:
            # 1. Створюємо запис у лозі з фіксованою причиною
            log = RemovedParticipantLog(
                removed_user_id=user_id_to_remove,
                event_id=event_id,
                admin_id=current_user.id,
                reason=FIXED_REASON 
            )
            db.session.add(log)
            
            # 2. Змінюємо статус учасника на 'removed'
            participant_to_update.status = 'removed'
            
            # 3. Видаляємо з команд (логіка JSON)
            teams = event.teams
            username_to_remove = removed_user_obj.username
            for team_name, members in teams.items():
                if username_to_remove in members: members.remove(username_to_remove)
            event.teams = teams 
            
            db.session.commit()
            
            removed_user_name = removed_user_obj.nickname or removed_user_obj.username
            flash(f'Учасника ({removed_user_name}) знято з гри. Помітка: "{FIXED_REASON}"', 'success')

        except Exception as e:
            db.session.rollback()
            logging.error(f"Помилка видалення учасника: {e}")
            flash('Помилка сервера при видаленні учасника.', 'error')
    else:
        flash('Учасника не знайдено у цій події або подія/користувач не існує.', 'error')

    return redirect(url_for('index') + f'#event-{event_id}')

# --- ГОЛОВНА СТОРІНКА (ОНОВЛЕНО) ---
@app.route('/')
def index():
    current_time = datetime.now()
    events_to_delete = []
    
    all_events_from_db = Event.query.order_by(Event.date).all()
    
    for event in all_events_from_db:
        try:
            event_dt = datetime.strptime(event.date, '%Y-%m-%d %H:%M:%S')
            if event_dt < current_time:
                # Використовуємо JSON-структуру для логування, як у вашому оригіналі
                active_participants = [p.user.username for p in EventParticipant.query.filter_by(event_id=event.id).filter(EventParticipant.status.in_(['active'])).all()]
                
                cancelled_participants = [p.user.username for p in EventParticipant.query.filter_by(event_id=event.id).filter(EventParticipant.status.in_(['refused', 'removed'])).all()]
                
                new_log_entry = GameLog(
                    event_name=event.name, event_date=event.date,
                    active_participants=active_participants, cancelled_participants=cancelled_participants,
                    teams=event.teams, image_url=event.image_url, comment=event.comment
                )
                db.session.add(new_log_entry)
                
                # Видалення відповідних EventParticipant записів
                EventParticipant.query.filter_by(event_id=event.id).delete()
                
                events_to_delete.append(event)
                
        except ValueError:
            app.logger.error(f"Could not parse date for event '{event.name}': {event.date}")
            
    if events_to_delete:
        for event in events_to_delete:
            db.session.delete(event)
        db.session.commit()

    # Оновлена логіка перевірки внесків
    current_month_str = datetime.now().strftime('%Y-%m')
    paid_transactions = FinancialTransaction.query.filter(
        FinancialTransaction.description.like(f"%Членський внесок ({current_month_str})%")
    ).all()
    paid_users_for_current_month = {t.description.split(' від ')[-1] for t in paid_transactions if ' від ' in t.description}

    all_users = User.query.all()
    user_nicknames = {u.username: u.nickname or u.username for u in all_users}

    events_for_display = Event.query.filter(Event.date >= datetime.now().strftime('%Y-%m-%d %H:%M:%S')).order_by(Event.date).all()
    events_with_team_info = []

    for event in events_for_display:
        unique_team_names = sorted(list(event.teams.keys()))
        color_cycle = itertools.cycle(TEAM_COLORS_PALETTE)
        event.team_colors = {team_name: next(color_cycle) for team_name in unique_team_names}

        # 2. Отримання та обробка учасників
        # Отримуємо ВСІХ учасників (активних, відмовилися, знятих) для відображення списку
        all_participants_entries = EventParticipant.query.filter_by(event_id=event.id).order_by(EventParticipant.join_date.asc()).all()
        
        processed_participants = []
        is_participant = False
        
        for p_entry in all_participants_entries:
            user = User.query.get(p_entry.user_id)
            if not user: continue 

            p_dict = {
                'id': p_entry.id,
                'user_id': user.id,
                'username': user.username,
                'nickname': user.nickname or user.username,
                'assigned_team_name': next((name for name, members in event.teams.items() if user.username in members), ''),
                'timestamp': p_entry.join_date.strftime('%Y-%m-%d %H:%M:%S'),
                'status': p_entry.status, 
                'stats': None 
            }
            
            processed_participants.append(p_dict)
            
            # Прапорець is_participant встановлюється, лише якщо статус 'active'
            if current_user.is_authenticated and user.id == current_user.id and p_entry.status == 'active':
                is_participant = True
            
        event.processed_participants = processed_participants 
        event.is_participant = is_participant 
        
        # 3. Підрахунок АКТИВНИХ учасників для ліміту
        event.active_participants_count = EventParticipant.query.filter_by(event_id=event.id).filter(
            EventParticipant.status.in_(['active'])
        ).count()
        
        # 4. Логіка розрахунку статистики (ТІЛЬКИ ДЛЯ АКТИВНИХ)
        if current_user.is_authenticated and current_user.can_manage_events():
            current_time_str = current_time.strftime('%Y-%m-%d %H:%M:%S')
            next_seven_days_date_str = (current_time + timedelta(days=7)).strftime('%Y-%m-%d %H:%M:%S')
            last_thirty_days_date_str = (current_time - timedelta(days=30)).strftime('%Y-%m-%d %H:%M:%S')

            for p_dict in event.processed_participants:
                user_id = p_dict['user_id']
                
                if p_dict['status'] == 'active':
                    # 1. Ігри на цьому тижні (лише активні)
                    weekly_count = db.session.query(EventParticipant).join(Event).filter(
                        EventParticipant.user_id == user_id,
                        EventParticipant.status == 'active', 
                        Event.date >= current_time_str,
                        Event.date <= next_seven_days_date_str,
                    ).count()

                    # 2. Ігри за останні 30 днів (лише активні)
                    monthly_count = db.session.query(EventParticipant).join(Event).filter(
                        EventParticipant.user_id == user_id,
                        EventParticipant.status == 'active', 
                        Event.date >= last_thirty_days_date_str,
                        Event.date < current_time_str,
                    ).count()
                    
                    p_dict['stats'] = {
                        'weekly_count': weekly_count,
                        'monthly_count': monthly_count
                    }
                else:
                    p_dict['stats'] = None # Не показуємо статистику для неактивних

        events_with_team_info.append(event)
    
    user_events_next_7_days = [e for e in events_with_team_info if e.is_participant]
    
    # !!! ПЕРЕДАННЯ EventParticipant У ШАБЛОН ТА КОНТРОЛЬ ВІДСТУПІВ !!!
    return render_template('index.html', events=events_with_team_info, current_user=current_user, user_nicknames=user_nicknames, user_events_next_7_days=user_events_next_7_days, paid_users_for_current_month=paid_users_for_current_month, EventParticipant=EventParticipant, RemovedParticipantLog=RemovedParticipantLog)

@app.route('/add_event', methods=['GET', 'POST'])
@login_required
def add_event():
    if not current_user.can_manage_events():
        flash('У вас немає дозволу на додавання подій.', 'error')
        return redirect(url_for('index'))

    if request.method == 'POST':
        event_name = request.form['event_name']
        event_datetime_str = request.form['event_datetime'] 
        image_url = request.form.get('image_url')
        comment = request.form.get('comment')

        if event_name and event_datetime_str:
            try:
                dt_object = datetime.strptime(event_datetime_str, '%Y-%m-%dT%H:%M')
                formatted_datetime = dt_object.strftime('%Y-%m-%d %H:%M:%S')
                new_event = Event(
                    name=event_name, date=formatted_datetime,
                    image_url=image_url if image_url else None,
                    comment=comment, participants_json='[]', teams_json='{}'
                )
                db.session.add(new_event)
                db.session.commit()
                flash('Подію успішно додано!', 'success')
                return redirect(url_for('index'))
            except ValueError:
                flash('Неправильний формат дати.', 'error')
        else:
            flash('Будь ласка, заповніть усі поля.', 'error')
    
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
        event.comment = request.form.get('comment')

        try:
            dt_object = datetime.strptime(event_datetime_str, '%Y-%m-%dT%H:%M')
            event.date = dt_object.strftime('%Y-%m-%d %H:%M:%S')
            db.session.commit()
            flash('Подію успішно оновлено!', 'success')
            return redirect(url_for('index'))
        except ValueError:
            flash('Неправильний формат дати.', 'error')
    
    try:
        event.formatted_datetime_local = datetime.strptime(event.date, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%dT%H:%M')
    except (ValueError, TypeError):
        event.formatted_datetime_local = ''

    return render_template('edit_event.html', event=event, current_user=current_user)

@app.route('/delete_event/<int:event_id>', methods=['POST'])
@login_required
def delete_event(event_id):
    if not current_user.is_admin():
        flash('У вас немає дозволу на видалення подій.', 'error')
        return redirect(url_for('index'))

    event = Event.query.get_or_404(event_id)
    
    # Видаляємо пов'язані EventParticipant та RemovedParticipantLog записи перед видаленням Event
    EventParticipant.query.filter_by(event_id=event_id).delete()
    RemovedParticipantLog.query.filter_by(event_id=event_id).delete()
    
    db.session.delete(event)
    db.session.commit()
    flash('Подію успішно видалено!', 'success')
    return redirect(url_for('index'))

@app.route('/manage_teams/<int:event_id>')
@login_required
def manage_teams(event_id):
    if not current_user.can_manage_events():
        flash('У вас немає дозволу на керування командами.', 'error')
        return redirect(url_for('index'))

    event = Event.query.get_or_404(event_id)
    all_users = User.query.all()
    user_nicknames = {u.username: u.nickname or u.username for u in all_users}
    
    # Використовуємо реальних учасників з EventParticipant
    all_active_participants = [p.user.username for p in EventParticipant.query.filter_by(event_id=event_id).all()]
    assigned_participants = {member for members in event.teams.values() for member in members}
    unassigned_participants = [p for p in all_active_participants if p not in assigned_participants]
    
    return render_template('manage_teams.html', event=event, unassigned_participants=unassigned_participants, user_nicknames=user_nicknames, current_user=current_user)

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

@app.route('/finances', methods=['GET', 'POST'])
@login_required
def finances():
    if not current_user.can_view_finances():
        flash('У вас немає дозволу на перегляд цієї сторінки.', 'error')
        return redirect(url_for('index'))

    if request.method == 'POST':
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
                    fee_description = f"Членський внесок ({payment_period}) від {user.username}"
                    new_fee_transaction = FinancialTransaction(description=fee_description, date=fee_date_str, amount=fee_amount, transaction_type='income', logged_by_admin=current_user.nickname or current_user.username)
                    db.session.add(new_fee_transaction)
                    db.session.commit()
                    flash(f'Внесок для {user.nickname or user.username} успішно оновлено.', 'success')
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
    
    current_month_str = datetime.now().strftime('%Y-%m')
    paid_transactions = FinancialTransaction.query.filter(FinancialTransaction.description.like(f"%Членський внесок ({current_month_str})%")).all()
    paid_users_for_current_month = {t.description.split(' від ')[-1] for t in paid_transactions if ' від ' in t.description}
    
    return render_template('finances.html', users=users, transactions=transactions_this_month, summary=summary, period_filter=period, current_user=current_user, paid_users_for_current_month=paid_users_for_current_month)

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
            author_nickname = current_user.nickname or current_user.username
            new_announcement = Announcement(title=title, content=content, date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'), author=author_nickname)
            db.session.add(new_announcement)
            db.session.commit()
            flash('Оголошення успішно додано!', 'success')
        else:
            flash('Будь ласка, заповніть усі поля.', 'error')
        return redirect(url_for('announcements'))
    
    all_announcements = Announcement.query.order_by(Announcement.date.desc()).all()
    seen_items = current_user.seen_items
    seen_ids = set(seen_items.get('announcements', []))
    ids_on_page = {a.id for a in all_announcements}
    if not ids_on_page.issubset(seen_ids):
        seen_ids.update(ids_on_page)
        seen_items['announcements'] = list(seen_ids)
        current_user.seen_items = seen_items
        db.session.commit()

    return render_template('announcements.html', announcements=all_announcements, current_user=current_user)

if __name__ == '__main__':
    with app.app_context():
        # !!! ПІСЛЯ ПЕРШОГО УСПІШНОГО ЗАПУСКУ ЦЕЙ РЯДОК МАЄ БУТИ ВИДАЛЕНИЙ/ЗАКОМЕНТОВАНИЙ !!!
        # Він потрібен лише для одноразової міграції старих даних.
       # migrate_old_participants_to_orm(app)
        # db.create_all() # Використовуйте alembic для міграцій!
        pass
    app.run(debug=True)