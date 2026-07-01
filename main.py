import os
import time
import requests
import telebot
from threading import Thread
from flask import Flask

TOKEN = "8934915148:AAFCG8tLzs_kkYaolTqmxcIX7xRKUj2mQCI"
CHAT_ID = "478724812"

bot = telebot.TeleBot(TOKEN)
app = Flask('')

@app.route('/')
def home():
    return "PAXG Radar Online"

def run_web_server():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

def diagnostic_mode():
    while True:
        try:
            # Делаем запрос к публичному API
            res = requests.get("https://api.binance.com/api/v3/depth?symbol=PAXGUSDT&limit=5", timeout=10)
            data = res.json()
            
            # Проверяем, есть ли данные в стакане
            bids = data.get('bids', [])
            count = len(bids)
            
            # Отправляем отчет в Telegram
            bot.send_message(CHAT_ID, f"📡 Диагностика: Получено заявок {count}. Первая: {bids[0] if count > 0 else 'пусто'}")
        except Exception as e:
            bot.send_message(CHAT_ID, f"📡 Диагностика ОШИБКА: {str(e)}")
        
        time.sleep(60) # Раз в минуту

if __name__ == "__main__":
    Thread(target=run_web_server, daemon=True).start()
    Thread(target=diagnostic_mode, daemon=True).start()
    bot.infinity_polling(none_stop=True)
