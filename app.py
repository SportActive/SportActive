from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy # Імпортуємо SQLAlchemy
import os
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json # Залишаємо для тимчасового використання або якщо потрібен для інших цілей

app = Flask(__name__)
# ВАЖНО: Секретный ключ теперь может быть взят из переменной окружения
app.secret_key = os.environ.get('SECRET_KEY', 'your_super_secret_key_here_please_change_this') 

# --- Настройка SQLAlchemy ---
# Берем URL базы данных из переменной окружения DATABASE_URL
# Это стандартная практика для хостингов типа Render
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///site.db') 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Отключаем отслеживание изменений, чтобы избежать предупреждений

db = SQLAlchemy(app) # Инициализируем SQLAlchemy

# --- Настройка Flask-Login ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# --- Модели базы данных ---
# Теперь User - это модель SQLAlchemy
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default='user') # 'user' или 'admin'
    has_paid_fees = db.Column(db.Boolean, default=False)

    # Добавляем отношения с другими моделями (пока закомментируем, добавим позже)
    # events = db.relationship('Event', secondary='event_participants', backref=db.backref('users', lazy='dynamic'))
    # announcements = db.relationship('Announcement', backref='author_user', lazy=True)
    # polls = db.relationship('Poll', backref='author_user', lazy=True)

    def is_admin(self):
        return self.role == 'admin'

    # Метод для проверки пароля
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"User('{self.username}', '{self.role}')"

# Модель Event
class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(10), nullable=False) # Дата в формате YYYY-MM-DD
    # participants и teams будут храниться как JSON-строки для простоты,
    # но в идеале для teams лучше создать отдельную таблицу Team и TeamMembership
    # Для participants можно использовать secondary table, но для начала JSON-строка
    participants_json = db.Column(db.Text, default='[]') # Храним как JSON-строку
    teams_json = db.Column(db.Text, default='{}') # Храним как JSON-строку

    # Геттеры и сеттеры для работы с JSON-полями
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

# Модель Announcement
class Announcement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date = db.Column(db.String(20), nullable=False) # Дата и время
    author = db.Column(db.String(80), nullable=False) # Имя автора

    def __repr__(self):
        return f"Announcement('{self.title}', '{self.date}')"

# Модель Poll
class Poll(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(255), nullable=False)
    options_json = db.Column(db.Text, nullable=False) # Храним список словарей опций как JSON
    voted_users_json = db.Column(db.Text, default='[]') # Храним список проголосовавших пользователей как JSON
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
    # Теперь загружаем пользователя из базы данных
    return User.query.get(int(user_id))


# --- Маршруты для аутентификации ---

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Проверяем, существует ли пользователь уже в БД
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Користувач з таким ім\'ям вже існує.', 'error')
            return render_template('register.html')

        hashed_password = generate_password_hash(password)
        
        # Первый зарегистрированный пользователь становится админом
        # Проверяем, есть ли уже пользователи в БД
        is_first_user = (User.query.count() == 0)
        new_user_role = 'admin' if is_first_user else 'user' 
        
        new_user = User(username=username, password_hash=hashed_password, role=new_user_role, has_paid_fees=False)
        db.session.add(new_user)
        db.session.commit() # Сохраняем пользователя в БД
        
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

        # Ищем пользователя в БД
        user_found = User.query.filter_by(username=username).first()
        
        if user_found and user_found.check_password(password):
            login_user(user_found)
            flash('Вхід успішний!', 'success')
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
    # Загружаем события из БД
    events = Event.query.order_by(Event.date).all()
    # Загружаем всех пользователей для статуса взносов
    all_users = User.query.all()
    users_fee_status = {u.username: u.has_paid_fees for u in all_users}
    return render_template('index.html', events=events, current_user=current_user, users_fee_status=users_fee_status)

@app.route('/add_event', methods=['POST'])
@login_required
def add_event():
    if not current_user.is_admin():
        flash('У вас немає дозволу на додавання подій.', 'error')
        return redirect(url_for('index'))

    event_name = request.form['event_name']
    event_date = request.form['event_date']
    if event_name and event_date:
        # Создаем новую запись Event и сохраняем в БД
        new_event = Event(name=event_name, date=event_date, participants_json='[]', teams_json='{}')
        db.session.add(new_event)
        db.session.commit()
        flash('Подію успішно додано!', 'success')
    else:
        flash('Будь ласка, заповніть усі поля для події.', 'error')
    return redirect(url_for('index'))

@app.route('/toggle_participation/<int:event_id>', methods=['POST'])
@login_required
def toggle_participation(event_id):
    participant_name = current_user.username 
    
    # Ищем событие в БД
    event = Event.query.get_or_404(event_id)
    
    participants = event.participants # Получаем список участников
    teams = event.teams # Получаем словарь команд

    if participant_name in participants:
        participants.remove(participant_name)
        # Также удаляем из списка команд, если был
        for team_name in teams:
            if participant_name in teams[team_name]:
                teams[team_name].remove(participant_name)
                break 
        flash(f'{participant_name}, вашу участь скасовано для "{event.name}".', 'info')
    else:
        participants.append(participant_name)
        flash(f'{participant_name}, ви успішно зареєструвалися на "{event.name}".', 'success')
    
    event.participants = participants # Обновляем JSON-строку
    event.teams = teams # Обновляем JSON-строку
    db.session.commit() # Сохраняем изменения в БД

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
            # Создаем новую запись Announcement и сохраняем в БД
            new_announcement = Announcement(
                title=title,
                content=content,
                date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                author=current_user.username
            )
            db.session.add(new_announcement)
            db.session.commit()
            flash('Оголошення успішно додано!', 'success')
            return redirect(url_for('announcements'))
        else:
            flash('Будь ласка, заповніть усі поля для оголошення.', 'error')
    
    # Загружаем объявления из БД, сортируем по дате
    ann = Announcement.query.order_by(Announcement.date.desc()).all()
    return render_template('announcements.html', announcements=ann, current_user=current_user)

# --- Маршруты для опросов ---

@app.route('/polls', methods=['GET', 'POST'])
def polls():
    if request.method == 'POST':
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('У вас немає дозволу на створення опитувань.', 'error')
            return redirect(url_for('polls'))

        question = request.form['question']
        options_raw = [request.form[f'option{i}'] for i in range(1, 6) if f'option{i}' in request.form and request.form[f'option{i}']]
        
        if not question or not options_raw:
            flash('Будь ласка, заповніть питання та хоча б один варіант відповіді.', 'error')
            # Важно: при возврате на страницу с ошибкой, передать текущие опросы
            all_polls = Poll.query.order_by(Poll.date.desc()).all()
            return render_template('polls.html', polls=all_polls, current_user=current_user)

        options_for_save = []
        for opt_text in options_raw:
            options_for_save.append({'text': opt_text, 'votes': 0})

        # Создаем новую запись Poll и сохраняем в БД
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
    
    # Загружаем опросы из БД, сортируем по дате
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
            
            poll.options = options # Обновляем JSON-строку
            poll.voted_users = voted_users # Обновляем JSON-строку
            db.session.commit() # Сохраняем изменения в БД
            
            flash('Ваш голос зараховано!', 'success')
        else:
            flash('Недійсний варіант голосування.', 'error')
    except ValueError:
        flash('Недійсний запит голосування.', 'error')
    
    return redirect(url_for('polls'))

# --- Маршруты для управления взносами ---

@app.route('/manage_fees')
@login_required
def manage_fees():
    if not current_user.is_admin():
        flash('У вас немає дозволу на керування внесками.', 'error')
        return redirect(url_for('index'))
    
    # Загружаем пользователей из БД
    users = User.query.order_by(User.username).all()
    return render_template('manage_fees.html', users=users, current_user=current_user)

@app.route('/toggle_fee_status/<int:user_id>', methods=['POST'])
@login_required
def toggle_fee_status(user_id):
    if not current_user.is_admin():
        flash('У вас немає дозволу на керування внесками.', 'error')
        return redirect(url_for('index'))
    
    # Ищем пользователя в БД
    user = User.query.get_or_404(user_id)
    
    user.has_paid_fees = not user.has_paid_fees # Изменяем статус
    db.session.commit() # Сохраняем изменения в БД
    
    flash(f'Статус внесків для {user.username} оновлено.', 'success')
    
    return redirect(url_for('manage_fees'))

# --- Маршруты для управления командами ---

@app.route('/manage_teams/<int:event_id>')
@login_required
def manage_teams(event_id):
    if not current_user.is_admin():
        flash('У вас немає дозволу на керування командами.', 'error')
        return redirect(url_for('index'))

    event = Event.query.get_or_404(event_id)
    
    all_participants = event.participants
    assigned_participants = set()
    for team_name, members in event.teams.items():
        assigned_participants.update(members)
    
    unassigned_participants = [p for p in all_participants if p not in assigned_participants]
    
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
    
    event.teams = new_teams # Обновляем JSON-строку
    db.session.commit() # Сохраняем изменения в БД
    
    flash('Команди успішно збережено!', 'success')
    
    return redirect(url_for('manage_teams', event_id=event_id))


if __name__ == '__main__':
    # При первом запуске или для создания таблиц
    # В реальном приложении это делается с помощью Alembic или других инструментов миграции
    with app.app_context():
        db.create_all() # Создаст таблицы в БД, если их еще нет
    app.run(debug=True)