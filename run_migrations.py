from app import app, db
import os
import sys
import time

# Дозволяємо Flask-додатку повністю ініціалізуватися та підключитися до БД
# Можливо, потрібна невелика затримка для стабілізації підключення
time.sleep(5) # Затримка на 5 секунд (можна збільшити/зменшити за потреби)

with app.app_context():
    print("Attempting to create database tables...")
    try:
        db.create_all()
        print("Database tables created successfully!")
    except Exception as e:
        print(f"Error creating database tables: {e}")
        # Якщо виникла помилка, можливо, база даних недоступна.
        # Можна вийти з кодом помилки, щоб зупинити розгортання.
        sys.exit(1) # Выход с ошибкой, если создание таблиц не удалось