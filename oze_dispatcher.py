import requests
import os 
import database
import entso_parser
import telebot 
from datetime import datetime

BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

def dispatch_signals():
    print(f"--- URUCHOMIENIE DYSPOZYTORA RCE ---")
    
    market_data = entso_parser.get_tomorrow_prices() # Или цены на сегодня
    if not market_data:
        print("❌ Brak danych z giełdy. Przerywam cykl.")
        return

    rate = entso_parser.get_pln_rate()
    clients = database.get_active_triggers()
    
    for label, url, threshold in clients:
        formatted_slots = []
        # Ищем текущий или ближайший слот
        for slot in market_data:
            price_pln = slot['price_raw'] * rate
            if price_pln <= threshold:
                formatted_slots.append({
                    "time": slot['ts'].strftime('%H:%M'),
                    "price": round(price_pln, 2)
                })

        if formatted_slots:
            reason = "Tania energia z giełdy (RCE)"
            
            payload = {
                "source": "OZE_RCE_SYSTEM",
                "verdict": "ACTIVATE_LOAD",
                "reason": reason,
                "details": formatted_slots[:3]
            }
            
            # 1. Выстрел вебхука
            success = execute_webhook(label, url, payload)
            
            if success:
                # 2. ФИКСАЦИЯ АКТИВА (Запись в Ledger)
                recorded_price = formatted_slots[0]['price']
                database.log_execution(label, reason, recorded_price)
                print(f"💾 Statystyka zapisana: {label} (Cena: {recorded_price} PLN/MWh)")
                
                # 3. Уведомление в Telegram
                if label.startswith("tg_"):
                    chat_id = label.replace("tg_", "")
                    send_tg_notification(chat_id, reason, formatted_slots)

def execute_webhook(label, url, payload):
    try:
        res = requests.post(url, json=payload, timeout=5)
        if res.status_code < 300:
            print(f"✅ Sygnał dostarczony: {label}")
            return True
        return False
    except:
        print(f"❌ Błąd komunikacji z: {label}")
        return False

def send_tg_notification(chat_id, reason, slots):
    try:
        msg = f"🚀 <b>Zadziałał wyzwalacz automatyki!</b>\n\nPowód: <code>{reason}</code>\n"
        if slots:
            msg += f"Najbliższy interwał: {slots[0]['time']} ({slots[0]['price']} PLN/MWh)"
        
        bot.send_message(chat_id, msg, parse_mode='HTML')
    except Exception as e:
        pass

if __name__ == "__main__":
    dispatch_signals()