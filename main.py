import os
import time
import requests
import telebot
from threading import Thread
from flask import Flask

# Твой новый токен
TOKEN = "8934915148:AAFCG8tLzs_kkYaolTqmxcIX7xRKUj2mQCI"
CHAT_ID = "478724812"

bot = telebot.TeleBot(TOKEN)
app = Flask('')

@app.route('/')
def home():
    return "PAXG Radar Online"

def run_web_server():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

def monitor_market():
    # Цикл мониторинга
    while True:
        try:
            # Запрос к стакану Binance
            res = requests.get("https://api.binance.com/api/v3/depth?symbol=PAXGUSDT&limit=20", timeout=10)
            if res.status_code == 200:
                data = res.json()
                bids = data.get('bids', [])
                
                # Ищем плиты > 5000$
                for price, qty in bids:
                    total_usd = float(price) * float(qty)
                    if total_usd >= 5000:
                        bot.send_message(CHAT_ID, f"⚠️ КРУПНАЯ ПЛИТА:\nЦена: {price}\nОбъем: {qty} PAXG\nСумма: {total_usd:.0f}$")
                        time.sleep(10) # Чтобы не спамить одной и той же плитой
            
        except Exception as e:
            print(f"Ошибка мониторинга: {e}")
        
        time.sleep(30) # Пауза между проверками

@bot.message_handler(commands=['status'])
def send_status(message):
    bot.reply_to(message, "✅ Радар работает и мониторит Binance!")

if __name__ == "__main__":
    # Запуск сервера
    Thread(target=run_web_server, daemon=True).start()
    # Запуск мониторинга
    Thread(target=monitor_market, daemon=True).start()
    # Запуск бота
    bot.infinity_polling(none_stop=True)
