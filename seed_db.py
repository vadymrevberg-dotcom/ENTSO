import sqlite3
from datetime import datetime, timedelta
import random

DB_NAME = "triggers.db"

def inject_demo_data():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        
        # ОЧИСТКА: Удаляем старые демо-данные, чтобы не плодить дубликаты
        cursor.execute("DELETE FROM user_triggers")
        cursor.execute("DELETE FROM execution_logs")
        
        # 1. Добавляем объекты
        clients = [
            ("Wrocław_Dom_Kowalski", "https://webhook.site/mock1", 0.0),
            ("Legnica_Pompa_Ciepla", "https://webhook.site/mock2", 50.0),
            ("Oława_EV_Charger", "https://webhook.site/mock3", -10.0),
            ("Karpacz_Pensjonat", "https://webhook.site/mock4", 10.0),
            ("Wałbrzych_Bojler", "https://webhook.site/mock5", 0.0)
        ]
        cursor.executemany("INSERT INTO user_triggers (user_label, webhook_url, threshold_pln_mwh) VALUES (?, ?, ?)", clients)

        # 2. Генерируем ЛОГИ
        now = datetime.now()
        logs = []
        
        # Создаем 20 записей, чтобы статистика была видна
        for i in range(20):
            days_ago = random.randint(0, 3)
            hour = random.randint(10, 16) # Пик солнца
            simulated_time = (now - timedelta(days=days_ago)).replace(hour=hour, minute=random.choice([0, 15, 30, 45]), second=0)
            
            client_label = random.choice(clients)[0]
            
            # ЧЕРЕДУЕМ: 50% случаев - 253V, 50% - RCE тарифы
            if i % 2 == 0:
                reason = "Ochrona 253V (Wykryto 253.4V)"
                price = 0.0 # При защите цена не важна
            else:
                reason = "Tania energia z giełdy (RCE)"
                price = round(random.uniform(-40.0, 25.0), 2) # Отрицательные цены для вау-эффекта
            
            logs.append((client_label, simulated_time.strftime('%Y-%m-%d %H:%M:%S'), reason, price))

        cursor.executemany("INSERT INTO execution_logs (user_label, timestamp, reason, price_pln_mwh) VALUES (?, ?, ?, ?)", logs)
        conn.commit()

if __name__ == "__main__":
    inject_demo_data()
    print("🚀 БАЗА ОБНОВЛЕНА!")
    print("- Объекты добавлены.")
    print("- Логи 253V и RCE сгенерированы.")
    print("Теперь обновляй дашборд.")
