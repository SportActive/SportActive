# run_migration_script.py
from app import app, db, migrate_old_participants_to_orm
import sys

# Ми запускаємо міграцію в контексті Flask
if __name__ == '__main__':
    print("Спроба підключення до бази даних PostgreSQL...")
    try:
        with app.app_context():
            # Виклик функції міграції, яка візьме налаштування з app.py
            migrate_old_participants_to_orm(app)
            print("Перевірте логи вище. Міграція завершена.")
    except Exception as e:
        print(f"Помилка під час виконання міграції: {e}", file=sys.stderr)
        print("Міграція НЕ вдалася.", file=sys.stderr)