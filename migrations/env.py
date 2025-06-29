import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Ця частина додана для Flask-SQLAlchemy
# Додайте шлях до кореня вашого проекту до sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Імпортуйте об'єкт db з вашого Flask-додатка
from app import db # <--- ПЕРЕВІРТЕ ЦЕЙ РЯДОК ІМПОРТУ
from app import app # Імпортуємо app, бо db.metadata потребує контексту додатка

# target_metadata = None # Закомментуйте або видаліть цей рядок

# Якщо ви використовуєте Flask-SQLAlchemy, то target_metadata буде db.metadata
# Якщо ж ні, потрібно імпортувати всі ваші моделі сюди
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import Base
# target_metadata = Base.metadata

# target_metadata тепер визначається в контексті додатка
with app.app_context(): # <--- ДОДАНО: Alembic повинен працювати в контексті додатка
    target_metadata = db.metadata # <--- Переконайтеся, що цей рядок розкоментовано

# other values from the config, defined by the needs of env.py,
# can be acquired and passed to the MigrationContext constructor.
# ... (решта коду env.py)