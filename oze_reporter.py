import sqlite3
import os
import telebot
from datetime import datetime

# Конфигурация
BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
DB_NAME = "triggers.db"

# ТВОЙ ТЕЛЕГРАМ ID (чтобы бот знал, кому слать отчет)
# Вставь сюда свой ID. Если не знаешь его, напиши боту @userinfobot
ADMIN_CHAT_ID = "765038933" 

bot = telebot.TeleBot(BOT_TOKEN)

def generate_daily_report():
    today = datetime.now().strftime('%Y-%m-%d')
    
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        
        # Считаем статистику за сегодня
        cursor.execute("SELECT reason, COUNT(*) FROM execution_logs WHERE date(timestamp) = ? GROUP BY reason", (today,))
        stats = cursor.fetchall()
        
        # Считаем уникальных клиентов, которых мы спасли сегодня
        cursor.execute("SELECT COUNT(DISTINCT user_label) FROM execution_logs WHERE date(timestamp) = ?", (today,))
        active_users_saved = cursor.fetchone()[0]

    total_triggers = sum([count for _, count in stats])

    if total_triggers == 0:
        return None, "Brak danych z dzisiaj. System czeka na anomalie."

    # Формирование "боевого" отчета для соцсетей
    # Формирование "боевого" отчета для B2B продаж
    report = f"📊 <b>RAPORT DOBOWY RCE: {today}</b>\n"
    report += "━━━━━━━━━━━━━━━━━━━━\n"
    report += f"⚡️ <b>Aktywne obiekty:</b> {active_users_saved}\n"
    report += f"✅ <b>Wysłane sygnały (Tanie godziny):</b> {total_triggers}\n\n"
    
    report += "<b>[ ANALIZA GIEŁDY ]</b>\n"
    # Для отчета берем минимальную цену за сегодня, по которой мы включили устройства
    cursor.execute("SELECT MIN(price_pln_mwh) FROM execution_logs WHERE date(timestamp) = ?", (today,))
    min_price = cursor.fetchone()[0]
    if min_price is not None:
        report += f"▪️ Najniższa przechwycona cena: <b>{min_price:.2f} PLN/MWh</b>\n"

    report += "\n"
    report += "🤖 <i>System zarządzania Taryfami Dynamicznymi</i>\n"
    report += "<i>Monitoring ENTSO-E 24/7. Gotowe do wdrożenia B2B.</i>"

    return True, report

if __name__ == "__main__":
    print("--- GENERATOR RAPORTÓW OZE ---")
    has_data, report_text = generate_daily_report()
    
    # Выводим в консоль для проверки
    clean_text = report_text.replace('<b>', '').replace('</b>', '').replace('<i>', '').replace('</i>', '')
    print(clean_text)
    
    if has_data and ADMIN_CHAT_ID != "765038933":
        try:
            bot.send_message(ADMIN_CHAT_ID, report_text, parse_mode='HTML')
            print(f"\n✅ Raport wysłany na TG (ID: {ADMIN_CHAT_ID}). Zrób screen i publikuj!")
        except Exception as e:
            print(f"\n❌ Błąd wysyłania do TG: {e}")
    else:
        print("\n⚠️ Wpisz swój ADMIN_CHAT_ID w kodzie, aby otrzymać raport na telefon.")