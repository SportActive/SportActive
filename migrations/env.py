import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Додайте шлях до кореня вашого проекту до sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# --- Імпортуємо об'єкти Flask-додатка та SQLAlchemy ---
from flask import Flask # Імпортуємо Flask тут (для app.app_context)
from app import app, db 

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# --- target_metadata тепер визначається в контексті додатка ---
with app.app_context():
    target_metadata = db.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True, # Важливо для PostgreSQL
        compare_type=True, # Для кращого autogenerate
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.
    """
    connectable = None 

    # Беремо URL бази даних зі змінної оточення Render (DATABASE_URL)
    # Якщо її немає (локально), використовуємо URL з alembic.ini
    # alembic.ini тепер має містити ваш Railway URL для локальних міграцій
    db_url = os.environ.get("DATABASE_URL") 
    if db_url is None:
        db_url = config.get_main_option("sqlalchemy.url") # Це буде Railway URL з alembic.ini

    connectable = engine_from_config(
        {"sqlalchemy.url": db_url}, 
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=True, # Важливо для PostgreSQL
            compare_type=True, # Для кращого autogenerate
            dialect_opts={"paramstyle": "named"},
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()