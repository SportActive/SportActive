import smtplib
from email.message import EmailMessage
import os

# --- ВСТАВТЕ ВАШІ ДАНІ ТУТ ---
# Важливо: використовуйте одинарні або подвійні лапки
SENDER_EMAIL = "aktivnosportivnimi@gmail.com"
APP_PASSWORD = "nlchktfebkiqjxjv"  # <-- Ваш 16-значний пароль для додатків, без пробілів
RECIPIENT_EMAIL = "aktivnosportivnimi@gmail.com" # Можна надіслати собі ж для перевірки
# -----------------------------

# Створюємо повідомлення
msg = EmailMessage()
msg.set_content("Це тестовий лист для перевірки налаштувань SMTP.")
msg['Subject'] = 'Тест SMTP з Python'
msg['From'] = SENDER_EMAIL
msg['To'] = RECIPIENT_EMAIL

print(f"Намагаюся надіслати лист з {SENDER_EMAIL} на {RECIPIENT_EMAIL}...")

try:
    # Підключаємось до сервера Gmail
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()  # Вмикаємо безпечне з'єднання
    
    # Логінимось, використовуючи пароль для додатків
    print("Логінюся на сервер...")
    server.login(SENDER_EMAIL, APP_PASSWORD)
    
    # Надсилаємо лист
    print("Надсилаю лист...")
    server.send_message(msg)
    
    # Закриваємо з'єднання
    server.quit()
    
    print("\n✅ Успіх! Лист успішно надіслано.")
    print("Це означає, що ваш логін та пароль для додатків ПРАВИЛЬНІ.")
    print("Проблема, ймовірно, у тому, як змінні середовища налаштовані на Railway.")

except Exception as e:
    print(f"\n❌ Помилка: {e}")
    print("\nНе вдалося надіслати лист. Це означає, що:")
    print("1. Ваш логін (SENDER_EMAIL) або пароль (APP_PASSWORD) НЕПРАВИЛЬНІ.")
    print("2. Перевірте, чи правильно скопіювали 16-значний пароль без пробілів.")
    print("3. Можливо, антивірус або файрвол на вашому комп'ютері блокує з'єднання.")
