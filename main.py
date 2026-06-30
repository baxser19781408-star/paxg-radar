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

# ВПИСАЛИ ДАННЫЕ ПРЯМО В КОД, ЧТОБЫ НЕ БЫЛО ОШИБОК В НАСТРОЙКАХ RENDER
TOKEN = "8934915148:AAH0huhV9f--PLixZyy6EMcDWo_8mzGe8iw"
CHAT_ID = "478724812"

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
        print(f"Ошибка Бинанса: {e}")
        return []

def monitor_market():
    time.sleep(5)
    try:
        bot.send_message(CHAT_ID, "🚀 Радар запущен! Мониторинг PAXG/USDT активен.")
    except Exception as e:
        print(f"Ошибка старта: {e}")
    while True:
        try:
            large_volumes = check_order_book()
            if large_volumes:
                bot.send_message(CHAT_ID, "⚠️ **ПЛИТЫ:**\n\n" + "\n".join(large_volumes), parse_mode="Markdown")
            time.sleep(15)
        except Exception as e:
            time.sleep(20)

@bot.message_handler(commands=['start', 'status'])
def send_status(message):
    bot.reply_to(message, "📊 **Радар в сети!** Мониторинг PAXG/USDT 24/7.", parse_mode="Markdown")

@bot.message_handler(commands=['candidates', 'top'])
def send_top(message):
    large_volumes = check_order_book()
    if large_volumes:
        bot.reply_to(message, "🔍 **Плиты в стакане:**\n\n" + "\n".join(large_volumes), parse_mode="Markdown")
    else:
        bot.reply_to(message, "🔍 Крупных плит нет.")

if __name__ == "__main__":
    Thread(target=run_web_server, daemon=True).start()
    Thread(target=monitor_market, daemon=True).start()
    bot.infinity_polling()
