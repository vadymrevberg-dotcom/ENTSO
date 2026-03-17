import time
from datetime import datetime
import oze_dispatcher
import database

def run_pipeline():
    print(f"--- СТАРТ ЦИКЛА RCE: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")
    try:
        database.init_db()

        # БЛОК 1: Жесткая рыночная автоматизация (без LLM)
        print("\n[STEP 1] Анализ цен ENTSO-E и диспетчеризация сигналов...")
        oze_dispatcher.dispatch_signals()

        # БЛОК 2: Отчетность (в 21:00)
        current_hour = datetime.now().hour
        if current_hour == 21: 
            print("\n[STEP 2] Формирование суточного отчета...")
            import daily_report
            has_data, report_text = daily_report.generate_daily_report()
            if has_data:
                # Отправка себе в ТГ
                daily_report.bot.send_message(daily_report.ADMIN_CHAT_ID, report_text, parse_mode='HTML')
        
        print("\n--- ЦИКЛ ЗАВЕРШЕН ---\n")
        
    except Exception as e:
        print(f"❌ КРИТИЧЕСКИЙ СБОЙ: {e}")

if __name__ == "__main__":
    print("⚙️ СИСТЕМА ПЕРЕВЕДЕНА В АВТОНОМНЫЙ РЕЖИМ (СИНХРОНИЗАЦИЯ PT15M)")
    while True:
        try:
            now = datetime.now()
            minutes_to_wait = 15 - (now.minute % 15)
            seconds_to_wait = (minutes_to_wait * 60) - now.second
            target_minute = (now.minute + minutes_to_wait) % 60
            print(f"\n⏳ Синхронизация с сетью. Сон: {seconds_to_wait} сек. Старт в XX:{target_minute:02d}:00")
            time.sleep(seconds_to_wait)
            run_pipeline()
        except KeyboardInterrupt:
            break
        except Exception as e:
            time.sleep(60)