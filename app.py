from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import json
import os
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_super_secret_key_here_please_change_this' # ВАЖНО: Замените на случайную, сложную строку!

# --- Настройка Flask-Login ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Файлы для хранения данных
DATA_FILE = 'events.json'
USERS_FILE = 'users.json'
ANNOUNCEMENTS_FILE = 'announcements.json'
POLLS_FILE = 'polls.json'

# --- Модель пользователя для Flask-Login ---
class User(UserMixin):
    def __init__(self, id, username, password_hash, role='user', has_paid_fees=False):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.role = role
        self.has_paid_fees = has_paid_fees

    def is_admin(self):
        return self.role == 'admin'

    @staticmethod
    def get(user_id):
        users = load_users()
        for user_data in users:
            if str(user_data['id']) == str(user_id):
                return User(user_data['id'], user_data['username'], user_data['password_hash'], 
                            user_data.get('role', 'user'), user_data.get('has_paid_fees', False))
        return None

# --- Функции для загрузки/сохранения данных ---
def load_events():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            events = json.load(f)
            # Добавляем поле 'teams' если его нет (для обратной совместимости)
            for event in events:
                if 'teams' not in event:
                    event['teams'] = {} # Пустой словарь для команд
            return events
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

def load_announcements():
    if os.path.exists(ANNOUNCEMENTS_FILE):
        with open(ANNOUNCEMENTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_announcements(announcements):
    with open(ANNOUNCEMENTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(announcements, f, ensure_ascii=False, indent=4)

def load_polls():
    if os.path.exists(POLLS_FILE):
        with open(POLLS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_polls(polls):
    with open(POLLS_FILE, 'w', encoding='utf-8') as f:
        json.dump(polls, f, ensure_ascii=False, indent=4)

# --- Функция загрузки пользователя для Flask-Login ---
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

# --- Маршруты для аутентификации (без изменений, кроме добавления has_paid_fees при регистрации) ---

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        users = load_users()
        if any(u['username'] == username for u in users):
            flash('Користувач з таким ім\'ям вже існує.', 'error')
            return render_template('register.html')

        hashed_password = generate_password_hash(password)
        
        new_id = 1
        if users:
            new_id = max(u['id'] for u in users) + 1

        new_user_role = 'admin' if not users else 'user' 
        
        users.append({'id': new_id, 'username': username, 'password_hash': hashed_password, 'role': new_user_role, 'has_paid_fees': False})
        save_users(users)
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

        users = load_users()
        user_found = None
        for user_data in users:
            if user_data['username'] == username:
                if check_password_hash(user_data['password_hash'], password):
                    user_found = User(user_data['id'], user_data['username'], user_data['password_hash'], 
                                      user_data.get('role', 'user'), user_data.get('has_paid_fees', False))
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
@login_required
def logout():
    logout_user()
    flash('Ви вийшли з системи.', 'info')
    return redirect(url_for('index'))

# --- Основные маршруты приложения (изменена передача данных пользователей) ---

@app.route('/')
def index():
    events = load_events()
    all_users_data = load_users() 
    users_fee_status = {u['username']: u.get('has_paid_fees', False) for u in all_users_data}
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
        events = load_events()
        events.append({
            'id': len(events) + 1,
            'name': event_name,
            'date': event_date,
            'participants': [],
            'teams': {} # Додаємо порожній словник для команд
        })
        save_events(events)
        flash('Подію успішно додано!', 'success')
    else:
        flash('Будь ласка, заповніть усі поля для події.', 'error')
    return redirect(url_for('index'))

@app.route('/toggle_participation/<int:event_id>', methods=['POST'])
@login_required
def toggle_participation(event_id):
    participant_name = current_user.username 
    
    events = load_events()
    found_event = False
    for event in events:
        if event['id'] == event_id:
            found_event = True
            if participant_name in event['participants']:
                event['participants'].remove(participant_name)
                # Також видаляємо зі списку команд, якщо був
                for team_name in event['teams']:
                    if participant_name in event['teams'][team_name]:
                        event['teams'][team_name].remove(participant_name)
                        break # Користувач може бути тільки в одній команді
                flash(f'{participant_name}, вашу участь скасовано для "{event["name"]}".', 'info')
            else:
                event['participants'].append(participant_name)
                flash(f'{participant_name}, ви успішно зареєструвалися на "{event["name"]}".', 'success')
            break
    
    if not found_event:
        flash('Подія не знайдена.', 'error')

    save_events(events)
    return redirect(url_for('index'))

# --- Маршруты для объявлений (без изменений) ---

@app.route('/announcements')
def announcements():
    ann = load_announcements()
    ann.sort(key=lambda x: datetime.strptime(x['date'], '%Y-%m-%d %H:%M:%S'), reverse=True)
    return render_template('announcements.html', announcements=ann, current_user=current_user)

@app.route('/add_announcement', methods=['GET', 'POST'])
@login_required
def add_announcement():
    if not current_user.is_admin():
        flash('У вас немає дозволу на додавання оголошень.', 'error')
        return redirect(url_for('announcements'))

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        if title and content:
            announcements = load_announcements()
            new_id = 1
            if announcements:
                new_id = max(a['id'] for a in announcements) + 1

            announcements.append({
                'id': new_id,
                'title': title,
                'content': content,
                'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'author': current_user.username
            })
            save_announcements(announcements)
            flash('Оголошення успішно додано!', 'success')
            return redirect(url_for('announcements'))
        else:
            flash('Будь ласка, заповніть усі поля для оголошення.', 'error')
    
    return render_template('add_announcement.html')

# --- Маршруты для опросов (без изменений) ---

@app.route('/polls')
def polls():
    all_polls = load_polls()
    all_polls.sort(key=lambda x: datetime.strptime(x['date'], '%Y-%m-%d %H:%M:%S'), reverse=True)
    return render_template('polls.html', polls=all_polls, current_user=current_user)

@app.route('/create_poll', methods=['GET', 'POST'])
@login_required
def create_poll():
    if not current_user.is_admin():
        flash('У вас немає дозволу на створення опитувань.', 'error')
        return redirect(url_for('polls'))

    if request.method == 'POST':
        question = request.form['question']
        options_raw = [request.form[f'option{i}'] for i in range(1, 6) if f'option{i}' in request.form and request.form[f'option{i}']]
        
        if not question or not options_raw:
            flash('Будь ласка, заповніть питання та хоча б один варіант відповіді.', 'error')
            return render_template('create_poll.html')

        polls_data = load_polls()
        new_poll_id = 1
        if polls_data:
            new_poll_id = max(p['id'] for p in polls_data) + 1
        
        options_for_save = []
        for opt_text in options_raw:
            options_for_save.append({'text': opt_text, 'votes': 0})

        polls_data.append({
            'id': new_poll_id,
            'question': question,
            'options': options_for_save,
            'voted_users': [],
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'author': current_user.username
        })
        save_polls(polls_data)
        flash('Опитування успішно створено!', 'success')
        return redirect(url_for('polls'))
    
    return render_template('create_poll.html')

@app.route('/vote_poll/<int:poll_id>', methods=['POST'])
@login_required
def vote_poll(poll_id):
    vote_option_index = request.form.get('option_index')
    
    if not vote_option_index:
        flash('Будь ласка, оберіть варіант для голосування.', 'error')
        return redirect(url_for('polls'))

    polls_data = load_polls()
    found_poll = False
    for poll in polls_data:
        if poll['id'] == poll_id:
            found_poll = True
            if current_user.username in poll['voted_users']:
                flash('Ви вже проголосували в цьому опитуванні.', 'info')
                return redirect(url_for('polls'))
            
            try:
                option_index = int(vote_option_index)
                if 0 <= option_index < len(poll['options']):
                    poll['options'][option_index]['votes'] += 1
                    poll['voted_users'].append(current_user.username)
                    save_polls(polls_data)
                    flash('Ваш голос зараховано!', 'success')
                else:
                    flash('Недійсний варіант голосування.', 'error')
            except ValueError:
                flash('Недійсний запит голосування.', 'error')
            break
    
    if not found_poll:
        flash('Опитування не знайдено.', 'error')

    return redirect(url_for('polls'))

# --- Маршруты для управления взносами (без изменений) ---

@app.route('/manage_fees')
@login_required
def manage_fees():
    if not current_user.is_admin():
        flash('У вас немає дозволу на керування внесками.', 'error')
        return redirect(url_for('index'))
    
    users = load_users()
    users.sort(key=lambda u: u['username'].lower())
    return render_template('manage_fees.html', users=users, current_user=current_user)

@app.route('/toggle_fee_status/<int:user_id>', methods=['POST'])
@login_required
def toggle_fee_status(user_id):
    if not current_user.is_admin():
        flash('У вас немає дозволу на керування внесками.', 'error')
        return redirect(url_for('index'))
    
    users = load_users()
    found_user = False
    for user in users:
        if user['id'] == user_id:
            found_user = True
            user['has_paid_fees'] = not user.get('has_paid_fees', False)
            save_users(users)
            flash(f'Статус внесків для {user["username"]} оновлено.', 'success')
            break
    
    if not found_user:
        flash('Користувача не знайдено.', 'error')
    
    return redirect(url_for('manage_fees'))

# --- НОВЫЕ МАРШРУТЫ ДЛЯ УПРАВЛЕНИЯ КОМАНДАМИ ---

@app.route('/manage_teams/<int:event_id>')
@login_required
def manage_teams(event_id):
    if not current_user.is_admin():
        flash('У вас немає дозволу на керування командами.', 'error')
        return redirect(url_for('index'))

    events = load_events()
    event = next((e for e in events if e['id'] == event_id), None)

    if not event:
        flash('Подія не знайдена.', 'error')
        return redirect(url_for('index'))
    
    # Отримуємо всіх учасників, які підтвердили участь у цій події
    all_participants = event.get('participants', [])
    
    # Визначаємо, які учасники вже в командах
    assigned_participants = set()
    for team_name, members in event.get('teams', {}).items():
        assigned_participants.update(members)
    
    # Учасники, які ще не розподілені по командам
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

    events = load_events()
    found_event = False
    for event in events:
        if event['id'] == event_id:
            found_event = True
            new_teams = {}
            # Перебираємо всі поля форми, які починаються з 'team_name_'
            for key, value in request.form.items():
                if key.startswith('team_name_'):
                    team_index = key.replace('team_name_', '')
                    team_name = value.strip()
                    # Отримуємо учасників для цієї команди
                    members_str = request.form.get(f'team_members_{team_index}', '').strip()
                    if team_name: # Тільки якщо назва команди не порожня
                        # Розділяємо учасників за комою, видаляємо пробіли та пусті елементи
                        members = [m.strip() for m in members_str.split(',') if m.strip()]
                        new_teams[team_name] = members
            
            event['teams'] = new_teams
            save_events(events)
            flash('Команди успішно збережено!', 'success')
            break
    
    if not found_event:
        flash('Подія не знайдена.', 'error')
    
    return redirect(url_for('manage_teams', event_id=event_id))


if __name__ == '__main__':
    app.run(debug=True)