# utils/logger.py
import sqlite3
import datetime
from config.database import DB_PATH

def init_logs_table():
    """Инициализирует таблицу логов"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            action TEXT,
            details TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def log_action(user_id: int, username: str, action: str, details: str = ""):
    """Логирует действие пользователя"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO logs (user_id, username, action, details)
        VALUES (?, ?, ?, ?)
    """, (user_id, username, action, details))
    conn.commit()
    conn.close()

def get_recent_logs(limit: int = 50):
    """Получает последние логи"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT user_id, username, action, details, timestamp
        FROM logs
        ORDER BY timestamp DESC
        LIMIT ?
    """, (limit,))
    logs = cursor.fetchall()
    conn.close()
    return logs
