import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

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

# Імпортуємо ваш додаток Flask та об'єкт db
import sys
import os
sys.path.append(os.getcwd()) # Додаємо поточну директорію до шляху Python
from app import db # Імпортуємо об'єкт db з вашого app.py

target_metadata = db.metadata # Вказуємо Alembic використовувати метадані SQLAlchemy з вашого db об'єкта

# other values from the config, defined by the needs of env.py,
# can be acquired a number of ways:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    too.  By skipping the Engine creation we don't even connect to
    the database.

    Calls to context.execute() here emit the given string to the
    script output.

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

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata,
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