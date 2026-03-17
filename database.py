import sqlite3
from datetime import datetime

DB_NAME = "triggers.db"

def init_db():
    """Инициализация ядра данных: Настройки клиентов + Журнал операций (Ledger)."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        
        # Таблица 1: Операционные контракты (Клиенты)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_triggers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_label TEXT,
                webhook_url TEXT NOT NULL,
                threshold_pln_mwh REAL,
                is_active INTEGER DEFAULT 1
            )
        """)
        
        # Таблица 2: Стратегический актив (Логи успешных срабатываний)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS execution_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_label TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                reason TEXT,
                price_pln_mwh REAL
            )
        """)
        conn.commit()

def add_trigger(label, url, threshold):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO user_triggers (user_label, webhook_url, threshold_pln_mwh) VALUES (?, ?, ?)",
                       (label, url, threshold))
        conn.commit()

def get_active_triggers():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT user_label, webhook_url, threshold_pln_mwh FROM user_triggers WHERE is_active = 1")
        return cursor.fetchall()

def log_execution(user_label, reason, price_pln_mwh):
    """Фиксация факта срабатывания. Накопление Data-актива для аналитики и B2B продаж."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO execution_logs (user_label, reason, price_pln_mwh) VALUES (?, ?, ?)",
                       (user_label, reason, price_pln_mwh))
        conn.commit()

def clear_all_triggers():
    """Kill Switch для клиентов. ВНИМАНИЕ: Логи (execution_logs) жестко сохраняются."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM user_triggers")
        # Сброс счетчика ID только для таблицы клиентов
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='user_triggers'")
        conn.commit()
    print("🗑 База данных клиентов СТЕРТА. Система готова к приему реального трафика.")

if __name__ == "__main__":
    init_db()
    print("✅ Ядро данных инициализировано. Ledger активен.")