from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy 
import os
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta 
import json 

app = Flask(__name__)
# ВАЖНО: Секретный ключ теперь может быть взят из переменной окружения
app.secret_key = os.environ.get('SECRET_KEY', 'your_super_secret_key_here_please_change_this') 

# --- Настройка SQLAlchemy ---
# Берем URL базы данных из переменной окружения DATABASE_URL
# Это стандартная практика для хостингов типа Render
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///site.db') 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Отключаем отслеживание изменений, чтобы избежать предупреждений

db = SQLAlchemy(app) # Инициализируем SQLAlchemy

# === НОВОЕ ДОБАВЛЕНИЕ ТУТ: ГАРАНТОВАННОЕ СОЗДАНИЕ ТАБЛИЦ ПРИ ЗАПУСКЕ ===
# Этот блок создаст все таблицы в БД, если их еще нет.
# Это решение для проблем с UndefinedTable на Render.
with app.app_context():
    db.create_all() 
# ======================================================================

# Делаем 'enumerate' доступным во всех Jinja2 шаблонах
@app.context_processor
def utility_processor():
    return dict(enumerate=enumerate)

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

    def is_admin(self):
        return self.role == 'admin'

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"User('{self.username}', '{self.role}')"

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(10), nullable=False) # Дата в формате YYYY-MM-DD
    # participants теперь будет хранить список словарей
    # [{"username": "Іван", "timestamp": "YYYY-MM-DD HH:MM:SS", "status": "active"}]
    participants_json = db.Column(db.Text, default='[]') 
    teams_json = db.Column(db.Text, default='{}')

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

class Announcement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date = db.Column(db.String(20), nullable=False) # Дата и время
    author = db.Column(db.String(80), nullable=False) # Имя автора

    def __repr__(self):
        return f"Announcement('{self.title}', '{self.date}')"

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
        return json.loads(self