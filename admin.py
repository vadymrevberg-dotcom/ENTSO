import database

def main():
    database.init_db()
    print("--- УПРАВЛЕНИЕ ТРИГГЕРАМИ OZE ---")
    print("1. Добавить новый Webhook")
    print("2. Показать активные триггеры")
    print("3. Выход")
    
    choice = input("\nВыбор: ")
    
    if choice == '1':
        label = input("Введите имя клиента (напр. Test_User): ")
        url = input("Вставьте URL с webhook.site: ")
        threshold = float(input("Порог цены PLN/MWh (для теста поставь 1000.0): "))
        
        database.add_trigger(label, url, threshold)
        print(f"✅ Триггер для {label} добавлен.")
        
    elif choice == '2':
        clients = database.get_active_triggers()
        for c in clients:
            print(f"ID: {c[0]} | URL: {c[1]} | Порог: {c[2]}")

if __name__ == "__main__":
    main()