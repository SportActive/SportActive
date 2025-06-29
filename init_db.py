import os
import sys
import time
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Додайте шлях до кореня проекту, щоб імпортувати app.py
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

# Імпортуємо app та db з вашого основного файлу
# Важливо: це лише для запуску цього скрипта,
# app.py сам по собі не повинен викликати db.create_all() на верхньому рівні.
from app import app, db 

if __name__ == '__main__':
    # Встановлюємо змінну середовища FLASK_APP для Flask-команд
    os.environ['FLASK_APP'] = 'app.py'

    # Перевіряємо, чи встановлений DATABASE_URL
    if not os.environ.get('DATABASE_URL'):
        print("DATABASE_URL is not set in environment variables. Cannot proceed with DB setup.")
        sys.exit(1)

    # Пробуємо підключитися та створити таблиці кілька разів
    # Це допомагає, якщо база даних ще не повністю готова
    max_retries = 10
    retry_delay_seconds = 5

    for i in range(max_retries):
        try:
            with app.app_context():
                print(f"Attempting to create database tables (attempt {i+1}/{max_retries})...")
                db.create_all()
                print("Database tables created successfully!")
            sys.exit(0) # Успіх, виходимо
        except Exception as e:
            print(f"Error creating database tables: {e}")
            if i < max_retries - 1:
                print(f"Retrying in {retry_delay_seconds} seconds...")
                time.sleep(retry_delay_seconds)
            else:
                print("Max retries reached. Database tables could not be created.")
                sys.exit(1) # Вихід з помилкою, якщо всі спроби невдалі