from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer
from datetime import datetime
import json
import os
import secrets # <-- 1. ДОДАНО ІМПОРТ

db = SQLAlchemy()

SECRET_KEY = os.environ.get('SECRET_KEY', 'your_super_secret_key_here_please_change_this')
s = URLSafeTimedSerializer(SECRET_KEY)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    nickname = db.Column(db.String(80), nullable=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='user')
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
            user_id = s.loads(token, salt='password-reset-salt', max_age=expires_sec).get('user_id')
        except Exception: 
            return None
        return User.query.get(user_id)
        
    def is_admin(self): return self.role == 'admin'
    def is_superuser(self): return self.role == 'superuser'
    def can_manage_events(self): return self.role in ['admin', 'superuser']
    def can_view_finances(self): return self.role in ['admin', 'superuser']
    def can_edit_finances(self): return self.role == 'admin'
    def check_password(self, password): return check_password_hash(self.password_hash, password)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(20), nullable=False)
    image_url = db.Column(db.String(255), nullable=True)
    teams_json = db.Column(db.Text, default='{}')
    comment = db.Column(db.Text, nullable=True)
    max_participants = db.Column(db.Integer, nullable=True)
    @property
    def teams(self): return json.loads(self.teams_json)
    @teams.setter
    def teams(self, value): self.teams_json = json.dumps(value, ensure_ascii=False)

class EventParticipant(db.Model):
    __tablename__ = 'event_participant'
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id', ondelete='CASCADE'), nullable=False)
    # --- ЗМІНА: Дозволяємо user_id бути порожнім (для гостей) ---
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=True)
    # --- КІНЕЦЬ ЗМІНИ ---
    join_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), nullable=True)
    user = db.relationship('User', backref=db.backref('participations', lazy='dynamic'))
    event = db.relationship('Event', backref=db.backref('real_participants', lazy='dynamic', cascade='all, delete-orphan'))

class GameLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_name = db.Column(db.String(100), nullable=False)
    event_date = db.Column(db.String(30), nullable=False)
    logged_at = db.Column(db.String(30), nullable=False, default=lambda: datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'))
    active_participants_json = db.Column(db.Text, default='[]')
    cancelled_participants_json = db.Column(db.Text, default='[]')
    teams_json = db.Column(db.Text, default='{}')
    comment = db.Column(db.Text, nullable=True)
    @property
    def active_participants(self): return json.loads(self.active_participants_json)
    @property
    def cancelled_participants(self): return json.loads(self.cancelled_participants_json)

class Announcement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date = db.Column(db.String(20), nullable=False)
    author = db.Column(db.String(80), nullable=False)

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
    def voted_users(self, value): self.voted_users_json = json.dumps(value)

class FinancialTransaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255), nullable=False)
    date = db.Column(db.String(10), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)
    logged_by_admin = db.Column(db.String(80), nullable=False)
    logged_at = db.Column(db.String(30), nullable=False, default=lambda: datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'))
    
class RemovedParticipantLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    removed_user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id', ondelete='CASCADE'), nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    reason = db.Column(db.String(255), default="Перенесено на інший день")
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    removed_user = db.relationship('User', foreign_keys=[removed_user_id])
    event = db.relationship('Event', foreign_keys=[event_id])
    admin = db.relationship('User', foreign_keys=[admin_id])

# --- 4. НОВА ТАБЛИЦЯ ДЛЯ КОДІВ ЗАПРОШЕНЬ ---
class InviteCode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(16), unique=True, nullable=False)
    is_used = db.Column(db.Boolean, default=False, nullable=False)
    generated_by = db.Column(db.String(80), nullable=False) # Ім'я адміна
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    used_by_username = db.Column(db.String(80), nullable=True) # Хто використав