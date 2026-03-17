import telebot
import database
import os

# Твой рабочий токен
BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

# Словарь для временного хранения данных пользователя при регистрации
user_steps = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    text = (
        "⚡️ <b>OZE Smart Trigger | Autopilot Falownika</b>\n\n"
        "Chronię Twój falownik przed wyłączeniami z powodu 253V i włączam obciążenie, gdy energia na giełdzie jest darmowa (lub ujemna).\n\n"
        "Komendy:\n"
        "/register - Podłącz swój inteligentny dom (Webhook)\n"
        "/status - Sprawdź aktualne ustawienia\n"
        "/help - Instrukcja obsługi"
    )
    bot.send_message(message.chat.id, text, parse_mode='HTML')

@bot.message_handler(commands=['status'])
def check_status(message):
    user_label = f"tg_{message.chat.id}"
    clients = database.get_active_triggers()
    
    # Ищем пользователя в базе
    user_data = next((c for c in clients if c[0] == user_label), None)
    
    if user_data:
        bot.send_message(message.chat.id, f"✅ <b>Twój status: Aktywny</b>\n\n🔗 Webhook: <code>{user_data[1]}</code>\n💰 Próg załączenia: {user_data[2]} PLN/MWh", parse_mode='HTML')
    else:
        bot.send_message(message.chat.id, "❌ Nie podłączyłeś jeszcze systemu. Kliknij /register.")

@bot.message_handler(commands=['register'])
def start_registration(message):
    msg = bot.send_message(message.chat.id, "🔗 Wyślij mi swój <b>Webhook URL</b> (link z Home Assistant, Shelly lub webhook.site do testów):", parse_mode='HTML')
    bot.register_next_step_handler(msg, process_webhook_step)

def process_webhook_step(message):
    url = message.text.strip()
    if not url.startswith("http"):
        msg = bot.send_message(message.chat.id, "❌ Błąd. URL musi zaczynać się od http:// lub https://. Spróbuj ponownie:")
        bot.register_next_step_handler(msg, process_webhook_step)
        return
        
    user_steps[message.chat.id] = {'url': url}
    msg = bot.send_message(message.chat.id, "💰 Przy jakiej cenie na giełdzie (w PLN/MWh) mam włączyć Twoje obciążenie? (Na przykład: 0 lub -10):")
    bot.register_next_step_handler(msg, process_threshold_step)

def process_threshold_step(message):
    try:
        threshold = float(message.text.strip())
        url = user_steps[message.chat.id]['url']
        user_label = f"tg_{message.chat.id}" # Уникальный ID клиента
        
        # Запись в базу данных
        database.add_trigger(user_label, url, threshold)
        
        bot.send_message(message.chat.id, "✅ <b>System został pomyślnie aktywowany!</b>\n\nMój radar skanuje sieć PSE i ceny z ENTSO-E. Gdy tylko warunki zostaną spełnione, wyślę sygnał na Twój Webhook.", parse_mode='HTML')
        
        # Очистка кэша
        del user_steps[message.chat.id]
        
    except ValueError:
        msg = bot.send_message(message.chat.id, "❌ Błąd. Wprowadź liczbę (np. -50.5). Spróbuj ponownie:")
        bot.register_next_step_handler(msg, process_threshold_step)

if __name__ == "__main__":
    database.init_db()
    print("🤖 Bot Telegram uruchomiony. Oczekiwanie na klientów...")
    bot.infinity_polling()