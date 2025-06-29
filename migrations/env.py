import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Ця частина додана для Flask-SQLAlchemy
# Додайте шлях до кореня вашого проекту до sys.path
# Це дозволить Alembic імпортувати app.py
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# --- НОВІ ІМПОРТИ ДЛЯ ФЛАСК-АЛЕМБІК КОНТЕКСТУ ---
from flask import current_app # Потрібно для app.app_context()
from app import app, db # Імпортуємо об'єкти Flask-додатка та SQLAlchemy


# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import Base
# target_metadata = Base.metadata

# --- ЗМІНА ТУТ: Використовуємо app.app_context() для target_metadata ---
# Це забезпечує, що db.metadata правильно завантажується
# у контексті Flask-додатка, що є критичним для Flask-SQLAlchemy.
with app.app_context():
    target_metadata = db.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired and passed to the MigrationContext constructor.
# ... (залиште цей коментар, він з оригінального env.py)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is additionally
    passed representing the target database.

    By itself, this precise rendering is just a example side
    effect, but it can also be used enginewise if the database
    is not available or if there are limitations to connecting
    into the database at migration time.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True, # Додаємо для PostgreSQL
        compare_type=True, # Додаємо для кращого autogenerate порівняння типів
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # ЗМІНА ТУТ: Використовуємо DATABASE_URL з Render, якщо він встановлений
    # Інакше використовуємо локальний URL з alembic.ini
    connectable = config.attributes.get("connection", None)
    if connectable is None:
        db_url = os.environ.get("DATABASE_URL") # Перевіряємо змінну оточення
        if db_url is None:
            # Якщо DATABASE_URL немає, використовуємо локальний URL з alembic.ini
            db_url = config.get_main_option("sqlalchemy.url")
        
        # Переконаємось, що ми завжди використовуємо правильний URL для підключення
        connectable = engine_from_config(
            {"sqlalchemy.url": db_url}, # Використовуємо знайдений DB URL
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
        )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=True, # Додайте це, якщо у вас були помилки з ALTER TABLE
            compare_type=True, # Додайте для кращого autogenerate порівняння типів
            dialect_opts={"paramstyle": "named"},
        )

        with context.begin_transaction():
            context.run_migrations()