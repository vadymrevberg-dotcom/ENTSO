import sqlite3
from datetime import datetime, timedelta
import random

DB_NAME = "triggers.db"

def inject_demo_data():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        
        # 1. Добавляем 5 фейковых активных объектов
        clients = [
            ("Wrocław_Dom_Kowalski", "https://webhook.site/mock1", 0.0),
            ("Legnica_Pompa_Ciepla", "https://webhook.site/mock2", 50.0),
            ("Oława_EV_Charger", "https://webhook.site/mock3", -10.0),
            ("Karpacz_Pensjonat", "https://webhook.site/mock4", 10.0),
            ("Wałbrzych_Bojler", "https://webhook.site/mock5", 0.0)
        ]
        cursor.executemany("INSERT INTO user_triggers (user_label, webhook_url, threshold_pln_mwh) VALUES (?, ?, ?)", clients)

        # 2. Генерируем успешные срабатывания за последние 3 дня (Аномалии RCE)
        # Фильтр станет нечувствительным к регистру и пробелам
        overvoltage_count = len(df_logs[df_logs['reason'].str.contains("253V|253 V|Ochrona", case=False, na=False)])
        now = datetime.now()
        
        logs = []
        for i in range(12): # 12 срабатываний системы
            # Случайное время в пределах последних 3 дней (обычно днем, когда солнце светит)
            days_ago = random.randint(0, 2)
            hour = random.randint(11, 15) 
            minute = random.choice(["00", "15", "30", "45"])
            
            simulated_time = (now - timedelta(days=days_ago)).replace(hour=hour, minute=int(minute), second=0)
            
            # Генерируем низкую или отрицательную цену RCE (от -45.0 до 30.0 PLN)
            mock_price = round(random.uniform(-45.0, 30.0), 2)
            client = random.choice(clients)[0]
            
            logs.append((client, simulated_time.strftime('%Y-%m-%d %H:%M:%S'), reasons[0], mock_price))

        cursor.executemany("INSERT INTO execution_logs (user_label, timestamp, reason, price_pln_mwh) VALUES (?, ?, ?, ?)", logs)
        conn.commit()

if __name__ == "__main__":
    inject_demo_data()
    print("✅ Демо-данные успешно интегрированы. Дашборд готов к презентации.")
