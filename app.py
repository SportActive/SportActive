from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import json
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
# ВАЖНО: Замените 'your_super_secret_key_here_please_change_this' на случайную, сложную строку!
app.secret_key = 'your_super_secret_key_here_please_change_this' 

# --- Настройка Flask-Login ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' # Перенаправлять на страницу логина, если пользователь не авторизован

# Файлы для хранения данных
DATA_FILE = 'events.json'
USERS_FILE = 'users.json' # Файл для хранения данных пользователей

# --- Модель пользователя для Flask-Login ---
class User(UserMixin):
    def __init__(self, id, username, password_hash, role='user'): # Добавлено 'role' с значением по умолчанию 'user'
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.role = role # Храним роль пользователя

    def is_admin(self):
        return self.role == 'admin' # Вспомогательная функция для проверки роли

    @staticmethod
    def get(user_id):
        users = load_users()
        for user_data in users:
            if str(user_data['id']) == str(user_id):
                # Проверяем, есть ли поле 'role', если нет - ставим 'user' по умолчанию (для старых пользователей)
                return User(user_data['id'], user_data['username'], user_data['password_hash'], user_data.get('role', 'user'))
        return None

# --- Функции для загрузки/сохранения данных ---
def load_events():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_events(events):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(events, f, ensure_ascii=False, indent=4)

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_users(users):
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=4)

# --- Функция загрузки пользователя для Flask-Login ---
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

# --- Маршруты для аутентификации ---

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index')) # Если уже авторизован, перенаправить на главную

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        users = load_users()
        # Проверка, существует ли пользователь с таким именем
        if any(u['username'] == username for u in users):
            flash('Користувач з таким ім\'ям вже існує.', 'error')
            return render_template('register.html')

        # Хеширование пароля
        hashed_password = generate_password_hash(password)
        
        # Генерируем новый ID для пользователя
        new_id = 1
        if users:
            new_id = max(u['id'] for u in users) + 1

        # Если это первый пользователь, делаем его администратором
        new_user_role = 'admin' if not users else 'user' 

        users.append({'id': new_id, 'username': username, 'password_hash': hashed_password, 'role': new_user_role})
        save_users(users)
        flash('Реєстрація успішна! Тепер ви можете увійти.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index')) # Если уже авторизован, перенаправить на главную

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        users = load_users()
        user_found = None
        for user_data in users:
            if user_data['username'] == username:
                if check_password_hash(user_data['password_hash'], password):
                    # Важно: передаем роль пользователя при создании объекта User
                    user_found = User(user_data['id'], user_data['username'], user_data['password_hash'], user_data.get('role', 'user'))
                    break
        
        if user_found:
            login_user(user_found)
            flash('Вхід успішний!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            flash('Неправильне ім\'я користувача або пароль.', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required # Доступно только авторизованным пользователям
def logout():
    logout_user()
    flash('Ви вийшли з системи.', 'info')
    return redirect(url_for('index'))

# --- Основные маршруты приложения ---

@app.route('/')
def index():
    events = load_events()
    # Передаем информацию о текущем пользователе в шаблон
    return render_template('index.html', events=events, current_user=current_user)

@app.route('/add_event', methods=['POST'])
@login_required # Только авторизованные пользователи могут добавлять события
def add_event():
    # Проверка на роль администратора
    if not current_user.is_admin():
        flash('У вас немає дозволу на додавання подій.', 'error')
        return redirect(url_for('index'))

    event_name = request.form['event_name']
    event_date = request.form['event_date']
    if event_name and event_date:
        events = load_events()
        events.append({
            'id': len(events) + 1,
            'name': event_name,
            'date': event_date,
            'participants': [] # Список участников, которые подтвердили участие
        })
        save_events(events)
        flash('Подію успішно додано!', 'success')
    else:
        flash('Будь ласка, заповніть усі поля для події.', 'error')
    return redirect(url_for('index'))

@app.route('/toggle_participation/<int:event_id>', methods=['POST'])
@login_required # Только авторизованные пользователи могут отмечать участие
def toggle_participation(event_id):
    # Имя участника берем из имени текущего пользователя
    participant_name = current_user.username 
    
    events = load_events()
    found_event = False
    for event in events:
        if event['id'] == event_id:
            found_event = True
            if participant_name in event['participants']:
                event['participants'].remove(participant_name) # Удалить, если уже есть
                flash(f'{participant_name}, вашу участь скасовано для "{event["name"]}".', 'info')
            else:
                event['participants'].append(participant_name) # Добавить, если нет
                flash(f'{participant_name}, ви успішно зареєструвалися на "{event["name"]}".', 'success')
            break
    
    if not found_event:
        flash('Подія не знайдена.', 'error')

    save_events(events)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True) # debug=True позволяет автоматическое перезагрузку при изменениях