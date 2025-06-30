import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool, text # Додаємо 'text' для спеціальних команд

from alembic import context

# Додайте шлях до кореня вашого проекту до sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# --- Імпортуємо об'єкти Flask-додатка та SQLAlchemy ---
from flask import Flask # Імпортуємо Flask тут
from app import app, db 

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# --- target_metadata тепер визначається в контексті додатка ---
# Це забезпечує, що db.metadata правильно завантажується
# у контексті Flask-додатка, що є критичним для Flask-SQLAlchemy.
with app.app_context():
    target_metadata = db.metadata

# --- ВАЖЛИВО: Очистка таблиць Alembic (якщо вони були створені в SQLite) ---
# Це для того, щоб Alembic не думав, що міграції вже застосовані,
# якщо він помилково запускався з SQLite.
# Виконується тільки якщо БД не SQLite
def clear_alembic_history_if_sqlite(connection):
    if str(connection.dialect) == 'sqlite':
        print("WARNING: Alembic connected to SQLite locally. Clearing alembic_version table.")
        try:
            connection.execute(text("DROP TABLE IF EXISTS alembic_version;"))
            connection.execute(text("COMMIT;"))
        except Exception as e:
            print(f"Could not drop alembic_version table: {e}")

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
    connectable = None # Ініціалізуємо тут
    
    # Беремо URL бази даних зі змінної оточення Render (DATABASE_URL)
    # Якщо її немає (локально), використовуємо URL з alembic.ini
    db_url = os.environ.get("DATABASE_URL") 
    if db_url is None:
        db_url = config.get_main_option("sqlalchemy.url")
    
    # === ЗМІНА ТУТ: Використовуємо явне створення connectable ===
    connectable = engine_from_config(
        {"sqlalchemy.url": db_url}, 
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    # =========================================================

    with connectable.connect() as connection:
        # Очистка історії Alembic, якщо раніше був SQLite
        clear_alembic_history_if_sqlite(connection)

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