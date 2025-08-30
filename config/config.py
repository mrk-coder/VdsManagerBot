# config/config.py
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
BACKUP_STORAGE_PATH = os.getenv("BACKUP_STORAGE_PATH", os.path.expanduser("~/backups"))

# Настройки почты для отправки больших бэкапов
EMAIL_CONFIG = {
    'smtp_server': os.getenv('SMTP_SERVER'),
    'port': int(os.getenv('SMTP_PORT', 465)), # 465 для SSL
    'sender_email': os.getenv('SENDER_EMAIL'),
    'password': os.getenv('SENDER_PASSWORD'), # Используйте App Password для Yandex
}
# Если хоть одна переменная не задана, отключаем почту
if not all([EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['sender_email'], EMAIL_CONFIG['password']]):
    EMAIL_CONFIG = None

CPU_THRESHOLD = int(os.getenv("CPU_THRESHOLD", "80"))
MEMORY_THRESHOLD = int(os.getenv("MEMORY_THRESHOLD", "85"))
DISK_THRESHOLD = int(os.getenv("DISK_THRESHOLD", "90"))

# Подключение Яндекс.Диск для бэкапа
YANDEX_DISK_TOKEN = os.getenv('YANDEX_DISK_TOKEN')
