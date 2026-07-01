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
    return "Bot Online"

# Функция для принудительной отправки данных
def test_connection():
    time.sleep(10) # Ждем старта
    try:
        res = requests.get("https://api.binance.com/api/v3/depth?symbol=PAXGUSDT&limit=5", timeout=10)
        data = res.json()
        bids = data.get('bids', [])
        bot.send_message(CHAT_ID, f"📡 ТЕСТ: Получено заявок {len(bids)}. Первая: {bids[0]}")
    except Exception as e:
        bot.send_message(CHAT_ID, f"Ошибка теста: {str(e)}")

if __name__ == "__main__":
    Thread(target=lambda: app.run(host='0.0.0.0', port=10000), daemon=True).start()
    Thread(target=test_connection, daemon=True).start()
    bot.infinity_polling()
