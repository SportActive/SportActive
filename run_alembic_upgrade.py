import os
import sys
import time
import subprocess # Додано для запуску зовнішніх команд

if __name__ == '__main__':
    # Перевіряємо, чи встановлений DATABASE_URL
    if not os.environ.get('DATABASE_URL'):
        print("DATABASE_URL is not set in environment variables. Cannot proceed with Alembic upgrade.")
        sys.exit(1)

    max_retries = 10
    retry_delay_seconds = 10 # Збільшено затримку

    alembic_path = os.path.join(os.environ.get('VIRTUAL_ENV', ''), 'bin', 'alembic')
    # На Render VIRTUAL_ENV - це /opt/render/project/src/.venv
    # тому шлях буде /opt/render/project/src/.venv/bin/alembic
    if not os.path.exists(alembic_path):
        # Fallback, якщо VIRTUAL_ENV не встановлено або шлях інший
        alembic_path = "/opt/render/project/src/.venv/bin/alembic" 
        if not os.path.exists(alembic_path):
            print(f"Error: alembic executable not found at {alembic_path}. Ensure virtualenv is correctly set up.")
            sys.exit(1)

    for i in range(max_retries):
        try:
            print(f"Attempting to run alembic upgrade head (attempt {i+1}/{max_retries})...")
            # Запускаємо alembic як підпроцес
            result = subprocess.run(
                [alembic_path, "upgrade", "head"],
                capture_output=True,
                text=True,
                check=True # Кидає виняток, якщо команда поверне ненульовий код
            )
            print("Alembic upgrade successful!")
            print(result.stdout)
            if result.stderr:
                print("Alembic stderr:", result.stderr)
            sys.exit(0) # Успіх, виходимо
        except subprocess.CalledProcessError as e:
            print(f"Alembic upgrade failed with error: {e}")
            print("Alembic stdout:", e.stdout)
            print("Alembic stderr:", e.stderr)
            if i < max_retries - 1:
                print(f"Retrying in {retry_delay_seconds} seconds...")
                time.sleep(retry_delay_seconds)
            else:
                print("Max retries reached. Alembic upgrade could not be completed.")
                sys.exit(1) # Вихід з помилкою, якщо всі спроби невдалі
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            sys.exit(1) # Вихід з помилкою