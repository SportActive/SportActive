from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_ # <--- ОСНОВНЕ ВИПРАВЛЕННЯ ТУТ
from flask_mail import Mail, Message
import os
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import json
from sqlalchemy import func
import itertools

# ===== ЗМІНА 1: Імпортуємо db та всі моделі з models.py =====
from models import db, User, Event, EventParticipant, GameLog, Announcement, Poll, RemovedParticipantLog, FinancialTransaction

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your_super_secret_key_here_please_change_this')

# --- Налаштування конфігурації ---
database_url = os.environ.get('DATABASE_URL', 'sqlite:///site.db')
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config.update(
    MAIL_SERVER=os.environ.get('MAIL_SERVER', 'smtp.gmail.com'),
    MAIL_PORT=int(os.environ.get('MAIL_PORT', 587)),
    MAIL_USE_TLS=os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1'],
    MAIL_USERNAME=os.environ.get('MAIL_USERNAME'),
    MAIL_PASSWORD=os.environ.get('MAIL_PASSWORD'),
    MAIL_DEFAULT_SENDER=os.environ.get('MAIL_DEFAULT_SENDER')
)

# ===== ЗМІНА 2: Ініціалізуємо розширення =====
db.init_app(app)
mail = Mail(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# ===== ЗМІНА 3: Реєструємо Blueprint =====
from admin_routes import admin_bp
app.register_blueprint(admin_bp)

# --- Палітра кольорів для команд ---
TEAM_COLORS_PALETTE = [
    '#e0f7fa', '#dcedc8', '#fff9c4', '#ffcdd2', '#e1bee7',
    '#d1c4e9', '#c5cae9', '#bbdefb', '#b2ebf2', '#b2dfdb'
]

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.context_processor
def utility_processor():
    def format_datetime_for_display(dt_str):
        if not dt_str: return "Н/Д"
        try:
            if isinstance(dt_str, datetime):
                dt_obj = dt_str
            else:
                dt_obj = datetime.strptime(str(dt_str), '%Y-%m-%d %H:%M:%S')
            
            days_of_week_full = ["Понеділок", "Вівторок", "Середа", "Четвер", "П'ятниця", "Субота", "Неділя"]
            day_name = days_of_week_full[dt_obj.weekday()]
            return dt_obj.strftime(f'{day_name}, %d.%m.%Y %H:%M')
        except (ValueError, TypeError):
            return str(dt_str)
    return dict(format_datetime_for_display=format_datetime_for_display)

@app.context_processor
def inject_unread_status():
    if not current_user.is_authenticated:
        return dict(has_unread_announcements=False, has_unread_polls=False)
    
    try:
        seen_items = current_user.seen_items
        all_announcement_ids = {a.id for a in Announcement.query.with_entities(Announcement.id).all()}
        seen_announcement_ids = set(seen_items.get('announcements', []))
        has_unread_announcements = bool(all_announcement_ids - seen_announcement_ids)
        all_poll_ids = {p.id for p in Poll.query.with_entities(Poll.id).all()}
        seen_poll_ids = set(seen_items.get('polls', []))
        has_unread_polls = bool(all_poll_ids - seen_poll_ids)
        return dict(has_unread_announcements=has_unread_announcements, has_unread_polls=has_unread_polls)
    except Exception:
        return dict(has_unread_announcements=False, has_unread_polls=False)

@app.route('/')
def index():
    current_time = datetime.utcnow()
    current_time_str = current_time.strftime('%Y-%m-%d %H:%M:%S')

    past_events = Event.query.filter(Event.date < current_time_str).all()
    if past_events:
        for event in past_events:
            active_participants = [p.user.username for p in event.real_participants if p.status == 'active' or p.status is None]
            cancelled_participants = [p.user.username for p in event.real_participants if p.status in ['refused', 'removed']]
            new_log_entry = GameLog(
                event_name=event.name,
                event_date=event.date,
                active_participants_json=json.dumps(active_participants, ensure_ascii=False),
                cancelled_participants_json=json.dumps(cancelled_participants, ensure_ascii=False),
                teams_json=json.dumps(event.teams, ensure_ascii=False),
                comment=event.comment
            )
            db.session.add(new_log_entry)
            db.session.delete(event)
        db.session.commit()

    user_nicknames = {u.username: u.nickname or u.username for u in User.query.all()}
    events_for_display = Event.query.filter(Event.date >= current_time_str).order_by(Event.date).all()
    
    weekly_counts = {}
    monthly_counts = {}
    if current_user.is_authenticated and current_user.can_manage_events():
        all_users_map = {u.username: u.id for u in User.query.all()}
        
        seven_days_later_str = (current_time + timedelta(days=7)).strftime('%Y-%m-%d %H:%M:%S')
        weekly_results = db.session.query(EventParticipant.user_id, func.count(EventParticipant.id)) \
                                   .join(Event) \
                                   .filter(Event.date >= current_time_str, Event.date <= seven_days_later_str) \
                                   .filter(or_(EventParticipant.status == 'active', EventParticipant.status == None)) \
                                   .group_by(EventParticipant.user_id).all()
        weekly_counts = dict(weekly_results)

        thirty_days_ago_str = (current_time - timedelta(days=30)).strftime('%Y-%m-%d %H:%M:%S')
        past_logs = GameLog.query.filter(GameLog.event_date >= thirty_days_ago_str, GameLog.event_date < current_time_str).all()
        
        monthly_counts = {}
        for log in past_logs:
            for username in log.active_participants:
                user_id = all_users_map.get(username)
                if user_id:
                    monthly_counts[user_id] = monthly_counts.get(user_id, 0) + 1

    for event in events_for_display:
        event.team_colors = {team_name: color for team_name, color in zip(sorted(event.teams.keys()), itertools.cycle(TEAM_COLORS_PALETTE))}
        event.processed_participants = []
        for p_entry in event.real_participants.order_by(EventParticipant.join_date.asc()).all():
            p_dict = {
                'user_id': p_entry.user.id,
                'username': p_entry.user.username,
                'nickname': p_entry.user.nickname or p_entry.user.username,
                'timestamp': p_entry.join_date,
                'status': p_entry.status or 'active',
                'assigned_team_name': next((name for name, members in event.teams.items() if p_entry.user.username in members), None),
                'stats': None
            }
            if current_user.is_authenticated and current_user.can_manage_events():
                 p_dict['stats'] = {
                    'weekly_count': weekly_counts.get(p_entry.user_id, 0),
                    'monthly_count': monthly_counts.get(p_entry.user_id, 0)
                }
            event.processed_participants.append(p_dict)
        
        event.active_participants_count = sum(1 for p in event.processed_participants if p['status'] == 'active')

    return render_template('index.html', events=events_for_display, user_nicknames=user_nicknames)

@app.route('/toggle_participation/<int:event_id>', methods=['POST'])
@login_required
def toggle_participation(event_id):
    event = Event.query.get_or_404(event_id)
    participant_entry = EventParticipant.query.filter_by(event_id=event_id, user_id=current_user.id).first()

    if participant_entry and participant_entry.status == 'removed':
        flash('Адміністратор зняв вас з гри. Зверніться до нього для поновлення участі.', 'warning')
        return redirect(url_for('index', _anchor=f'event-{event_id}'))

    if participant_entry:
        if participant_entry.status == 'active' or participant_entry.status is None:
            time_since_join = datetime.utcnow() - participant_entry.join_date
            if time_since_join <= timedelta(hours=1):
                db.session.delete(participant_entry)
                flash(f'Вашу участь у події "{event.name}" скасовано (повністю видалено).', 'info')
            else:
                participant_entry.status = 'refused'
                flash(f'Ви відмовилися від участі у події "{event.name}". Вас позначено як "Відмовився".', 'warning')
            
            teams = event.teams
            for team_name, members in list(teams.items()):
                if current_user.username in members:
                    members.remove(current_user.username)
            event.teams = teams
        else: # 'refused'
            participant_entry.status = 'active'
            participant_entry.join_date = datetime.utcnow()
            flash(f'Ваша участь у події "{event.name}" відновлена!', 'success')
    else:
        new_participant = EventParticipant(event_id=event_id, user_id=current_user.id, status='active')
        db.session.add(new_participant)
        flash('Ви успішно зареєструвалися на подію!', 'success')

    db.session.commit()
    return redirect(url_for('index', _anchor=f'event-{event_id}'))

@app.route('/api/admin/toggle_participant/<int:event_id>/<int:user_id>', methods=['POST'])
@login_required
def admin_toggle_participant_status(event_id, user_id):
    if not current_user.can_manage_events():
        flash('У вас немає дозволу на цю дію.', 'error')
        return redirect(url_for('index'))
    participant = EventParticipant.query.filter_by(event_id=event_id, user_id=user_id).first()
    user_obj = User.query.get(user_id)
    if not participant or not user_obj:
        flash('Учасника не знайдено у цій події.', 'error')
        return redirect(url_for('index', _anchor=f'event-{event_id}'))
    try:
        if participant.status == 'active' or participant.status is None:
            participant.status = 'removed'
            log = RemovedParticipantLog(removed_user_id=user_id, event_id=event_id, admin_id=current_user.id)
            db.session.add(log)
            flash(f'Учасника "{user_obj.nickname or user_obj.username}" знято з гри.', 'success')
        else:
            participant.status = 'active'
            flash(f'Учасника "{user_obj.nickname or user_obj.username}" повернуто в гру.', 'success')
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logging.error(f"Помилка при зміні статусу учасника: {e}")
        flash('Помилка сервера при зміні статусу учасника.', 'error')
    return redirect(url_for('index', _anchor=f'event-{event_id}'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated: return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username'].strip()
        nickname = request.form['nickname'].strip() or username
        password = request.form['password']
        email = request.form['email'].strip()
        if User.query.filter_by(username=username).first():
            flash('Користувач з таким логіном вже існує.', 'error')
            return render_template('register.html')
        if User.query.filter_by(email=email).first():
            flash('Ця електронна пошта вже зареєстрована.', 'error')
            return render_template('register.html')
        hashed_password = generate_password_hash(password)
        new_user_role = 'admin' if User.query.count() == 0 else 'user'
        confirmation_token = os.urandom(24).hex()
        new_user = User(username=username, nickname=nickname, password_hash=hashed_password, role=new_user_role, email=email, email_confirmation_token=confirmation_token)
        db.session.add(new_user)
        db.session.commit()
        try:
            confirm_url = url_for('confirm_email', token=confirmation_token, _external=True)
            msg = Message('Підтвердження пошти', recipients=[email], body=f"Привіт, {nickname}!\n\nДля підтвердження пошти перейдіть за посиланням:\n{confirm_url}")
            mail.send(msg)
            flash('Реєстрація успішна! На вашу пошту надіслано лист для підтвердження.', 'success')
        except Exception as e:
            flash(f'Реєстрація успішна, але не вдалося надіслати лист. {e}', 'warning')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated: return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            if not user.email_confirmed:
                flash('Будь ласка, підтвердьте свою електронну пошту, щоб увійти.', 'warning')
                return redirect(url_for('login'))
            login_user(user)
            flash(f'Вхід успішний! Привіт, {user.nickname or user.username}!', 'success')
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
            msg = Message('Запит на відновлення пароля', recipients=[user.email])
            msg.body = f"""Привіт, {user.nickname or user.username}!
Щоб відновити ваш пароль, будь ласка, перейдіть за посиланням нижче.
Посилання буде активним протягом 30 хвилин.
{reset_url}
Якщо ви не робили цей запит, просто проігноруйте цей лист."""
            try:
                mail.send(msg)
            except Exception as e:
                flash(f'Не вдалося надіслати лист. Помилка: {e}', 'error')
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
    
@app.route('/add_event', methods=['GET', 'POST'])
@login_required
def add_event():
    if not current_user.can_manage_events():
        flash('У вас немає дозволу.', 'error')
        return redirect(url_for('index'))
    if request.method == 'POST':
        event_name = request.form['event_name']
        event_datetime_str = request.form['event_datetime']
        max_participants_str = request.form.get('max_participants')
        if event_name and event_datetime_str:
            try:
                dt_object = datetime.strptime(event_datetime_str, '%Y-%m-%dT%H:%M')
                formatted_datetime = dt_object.strftime('%Y-%m-%d %H:%M:%S')
                new_event = Event(
                    name=event_name,
                    date=formatted_datetime,
                    image_url=request.form.get('image_url') or None,
                    comment=request.form.get('comment'),
                    max_participants=int(max_participants_str) if max_participants_str and max_participants_str.isdigit() else None
                )
                db.session.add(new_event)
                db.session.commit()
                flash('Подію успішно додано!', 'success')
                return redirect(url_for('index'))
            except ValueError:
                flash('Неправильний формат дати.', 'error')
        else:
            flash('Будь ласка, заповніть усі поля.', 'error')
    return render_template('add_event.html')

@app.route('/edit_event/<int:event_id>', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    if not current_user.is_admin():
        flash('У вас немає дозволу.', 'error')
        return redirect(url_for('index'))
    event = Event.query.get_or_404(event_id)
    if request.method == 'POST':
        try:
            event.name = request.form['event_name']
            dt_object = datetime.strptime(request.form['event_datetime'], '%Y-%m-%dT%H:%M')
            event.date = dt_object.strftime('%Y-%m-%d %H:%M:%S')
            event.image_url = request.form.get('image_url') or None
            event.comment = request.form.get('comment')
            max_participants_str = request.form.get('max_participants')
            event.max_participants = int(max_participants_str) if max_participants_str and max_participants_str.isdigit() else None
            db.session.commit()
            flash('Подію успішно оновлено!', 'success')
            return redirect(url_for('index'))
        except ValueError:
            flash('Неправильний формат дати.', 'error')
    try:
        dt_object = datetime.strptime(event.date, '%Y-%m-%d %H:%M:%S')
        event.formatted_datetime_local = dt_object.strftime('%Y-%m-%dT%H:%M')
    except ValueError:
        event.formatted_datetime_local = ''
    return render_template('edit_event.html', event=event)

@app.route('/delete_event/<int:event_id>', methods=['POST'])
@login_required
def delete_event(event_id):
    if not current_user.is_admin():
        flash('У вас немає дозволу.', 'error')
        return redirect(url_for('index'))
    event = Event.query.get_or_404(event_id)
    db.session.delete(event)
    db.session.commit()
    flash('Подію успішно видалено!', 'success')
    return redirect(url_for('index'))

@app.route('/manage_teams/<int:event_id>')
@login_required
def manage_teams(event_id):
    if not current_user.can_manage_events():
        flash('У вас немає дозволу.', 'error')
        return redirect(url_for('index'))
    event = Event.query.get_or_404(event_id)
    user_nicknames = {u.username: u.nickname or u.username for u in User.query.all()}
    active_participants = [p.user.username for p in event.real_participants if p.status == 'active' or p.status is None]
    assigned_participants = {member for members in event.teams.values() for member in members}
    unassigned_participants = [p for p in active_participants if p not in assigned_participants]
    return render_template('manage_teams.html', event=event, unassigned_participants=unassigned_participants, user_nicknames=user_nicknames)

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

if __name__ == '__main__':
    app.run(debug=True)