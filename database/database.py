# database/database.py
import sqlite3
import os
from config.database import DB_PATH

def init_db():
    if not os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                user_id INTEGER UNIQUE,
                is_admin BOOLEAN DEFAULT 0
            )
        """)
        conn.commit()
        conn.close()
    
    # Инициализируем таблицу логов
    init_logs_table()

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

def add_user(user_id: int, is_admin: bool = False):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (user_id, is_admin) VALUES (?, ?)", (user_id, is_admin))
    conn.commit()
    conn.close()

def is_user_allowed(user_id: int) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def is_admin(user_id: int) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT is_admin FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result and result[0] == 1

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
