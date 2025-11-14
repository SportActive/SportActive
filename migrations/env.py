import os
import sys

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Додайте шлях до кореня вашого проекту до sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# --- Імпортуємо об'єкти Flask-додатка та SQLAlchemy ---
from app import app, db 

config = context.config

# ВИДАЛЕНО fileConfig - більше не потрібен

# --- target_metadata тепер визначається в контексті додатка ---
with app.app_context():
    target_metadata = db.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    # Беремо URL бази даних зі змінної оточення
    db_url = os.environ.get("DATABASE_URL") 
    if db_url is None:
        # Для локальної розробки
        db_url = config.get_main_option("sqlalchemy.url")
        if db_url is None:
            db_url = "sqlite:///local.db"

    connectable = engine_from_config(
        {"sqlalchemy.url": db_url}, 
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=True,
            compare_type=True,
            dialect_opts={"paramstyle": "named"},
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()