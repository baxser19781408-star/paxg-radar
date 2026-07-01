import os
import time
import requests
import telebot
from threading import Thread
from flask import Flask

TOKEN = "8934915148:AAH0huhV9f--PLixZyy6EMcDWo_8mzGe8iw"
CHAT_ID = "478724812"

bot = telebot.TeleBot(TOKEN)
app = Flask('')

@app.route('/')
def home():
    return "Bot is running"

def run_web_server():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

def monitor_binance():
    while True:
        try:
            print("Начинаю запрос к Binance...")
            # Получаем стакан
            res = requests.get("https://api.binance.com/api/v3/depth?symbol=PAXGUSDT&limit=20", timeout=10)
            if res.status_code == 200:
                data = res.json()
                bids_count = len(data.get('bids', []))
                print(f"Данные получены! В стакане {bids_count} заявок на покупку.")
                # Если всё ок, шлем админу короткий отчет раз в 5 минут
                bot.send_message(CHAT_ID, f"📡 Мониторинг активен. В стакане {bids_count} заявок.")
            else:
                print(f"Ошибка Binance: {res.status_code}")
        except Exception as e:
            print(f"Критическая ошибка мониторинга: {e}")
        
        time.sleep(300) # Проверка раз в 5 минут

@bot.message_handler(commands=['status'])
def send_status(message):
    bot.reply_to(message, "✅ Радар в сети и мониторит Binance!")

if __name__ == "__main__":
    Thread(target=run_web_server, daemon=True).start()
    Thread(target=monitor_binance, daemon=True).start()
    bot.infinity_polling()
