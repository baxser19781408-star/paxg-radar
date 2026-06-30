import os
import time
import requests
import telebot
from threading import Thread
from flask import Flask

app = Flask('')

@app.route('/')
def home():
    return "PAXG Radar is working perfectly!"

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

TOKEN = os.environ.get("TELEGRAM_TOKEN", "ТВОЙ_ТОКЕН")
CHAT_ID = os.environ.get("CHAT_ID", "ТВОЙ_ID")

bot = telebot.TeleBot(TOKEN)
BINANCE_API_URL = "https://api.binance.com/api/v3/depth"
VOLUME_THRESHOLD = 50.0 

def check_order_book():
    try:
        params = {"symbol": "PAXGUSDT", "limit": 100}
        response = requests.get(BINANCE_API_URL, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            bids = data.get("bids", [])
            asks = data.get("asks", [])
            alerts = []
            
            for price, qty in bids[:50]:
                if float(qty) >= VOLUME_THRESHOLD:
                    alerts.append(f"🟢 Плита на ПОКУПКУ: {float(qty):.2f} PAXG по цене {float(price):.2f}")
            for price, qty in asks[:50]:
                if float(qty) >= VOLUME_THRESHOLD:
                    alerts.append(f"🔴 Плита на ПРОДАЖУ: {float(qty):.2f} PAXG по цене {float(price):.2f}")
            return alerts
        return []
    except Exception as e:
        print(f"Ошибка при запросе к стакану: {e}")
        return []

def monitor_market():
    time.sleep(5)
    try:
        bot.send_message(CHAT_ID, "🚀 Радар успешно перезапущен на Render!\nВеб-порт активен, мониторинг PAXG/USDT запущен 24/7.")
    except Exception as e:
        print(f"Не удалось отправить стартовый пост: {e}")

    while True:
        try:
            large_volumes = check_order_book()
            if large_volumes:
                message_text = "⚠️ **ОБНАРУЖЕНЫ КРУПНЫЕ ПЛИТЫ:**\n\n" + "\n".join(large_volumes)
                bot.send_message(CHAT_ID, message_text, parse_mode="Markdown")
            time.sleep(15)
        except Exception as e:
            print(f"Ошибка в цикле мониторинга: {e}")
            time.sleep(20)

@bot.message_handler(commands=['start', 'status'])
def send_status(message):
    try:
        res = requests.get("https://api.binance.com/api/v3/ticker/price", params={"symbol": "PAXGUSDT"}, timeout=5)
        price_text = ""
        if res.status_code == 200:
            price_text = f"\nТекущая цена PAXG: `{res.json()['price']}` USDT"
        bot.reply_to(message, f"📊 **Радар работает в штатном режиме!**\nПроверка стаканов идет непрерывно на сервере Render.{price_text}", parse_mode="Markdown")
    except Exception as e:
        bot.reply_to(message, "📊 Радар работает, но не удалось запросить цену.")

@bot.message_handler(commands=['candidates', 'top'])
def send_top(message):
    bot.send_chat_action(message.chat.id, 'typing')
    large_volumes = check_order_book()
    if large_volumes:
        message_text = "🔍 **Текущие крупные ордера в стакане:**\n\n" + "\n".join(large_volumes)
        bot.reply_to(message, message_text, parse_mode="Markdown")
    else:
        bot.reply_to(message, "🔍 Прямо сейчас крупных плит (от 50 PAXG) в топ-50 стакана не найдено. Рынок спокойный.")

if __name__ == "__main__":
    Thread(target=run_web_server, daemon=True).start()
    Thread(target=monitor_market, daemon=True).start()
    bot.infinity_polling()
