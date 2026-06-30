import asyncio
import collections
import heapq
import json
import logging
import os
import time
from datetime import datetime, timezone
import requests
import websockets

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# ТВОИ АКТУАЛЬНЫЕ ДАННЫЕ
TELEGRAM_TOKEN = "8934915148:AAH0huhV9f--PLixZyy6EMcDWo_8mzGe8iw"
TELEGRAM_CHAT_ID = "478724812"

SYMBOL = "paxgusdt"
THRESHOLD_USD = 5000.0  # Порог $5,000
MIN_SCANS = 5  # Антиспуфинг
MIN_DURATION = 5

tracked_orders = {}


def send_telegram_message(text):
  url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
  payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "Markdown"}
  try:
    response = requests.post(url, json=payload)
    if response.status_code != 200:
      logging.error(f"Ошибка TG: {response.text}")
  except Exception as e:
    logging.error(f"Ошибка сети TG: {e}")


async def monitor_order_book():
  global tracked_orders
  uri = f"wss://stream.binance.us:9443/ws/{SYMBOL}@depth20@100ms"

  while True:
    try:
      async with websockets.connect(uri) as websocket:
        logging.info("Успешно подключено к Binance WS")
        send_telegram_message(
            "🚀 *Радар запущен на Koyeb!* Мониторинг PAXG/USDT активен 24/7."
        )

        async for message in websocket:
          data = json.loads(message)
          bids = data.get("bids", [])
          asks = data.get("asks", [])
          current_time = time.time()
          active_this_snapshot = set()

          for price_str, qty_str in bids:
            price = float(price_str)
            qty = float(qty_str)
            usd_volume = price * qty
            if usd_volume >= THRESHOLD_USD:
              order_key = f"bid_{price_str}"
              active_this_snapshot.add(order_key)
              if order_key not in tracked_orders:
                tracked_orders[order_key] = {
                    "first_seen": current_time,
                    "scans": 1,
                    "price": price,
                    "qty": qty,
                    "usd": usd_volume,
                    "type": "Покупка (Bid)",
                    "alerted": False,
                }
              else:
                tracked_orders[order_key]["scans"] += 1
                tracked_orders[order_key]["qty"] = qty
                tracked_orders[order_key]["usd"] = usd_volume

          for price_str, qty_str in asks:
            price = float(price_str)
            qty = float(qty_str)
            usd_volume = price * qty
            if usd_volume >= THRESHOLD_USD:
              order_key = f"ask_{price_str}"
              active_this_snapshot.add(order_key)
              if order_key not in tracked_orders:
                tracked_orders[order_key] = {
                    "first_seen": current_time,
                    "scans": 1,
                    "price": price,
                    "qty": qty,
                    "usd": usd_volume,
                    "type": "Продажа (Ask)",
                    "alerted": False,
                }
              else:
                tracked_orders[order_key]["scans"] += 1
                tracked_orders[order_key]["qty"] = qty
                tracked_orders[order_key]["usd"] = usd_volume

          for key, order in list(tracked_orders.items()):
            if key in active_this_snapshot:
              duration = current_time - order["first_seen"]
              if (
                  order["scans"] >= MIN_SCANS
                  and duration >= MIN_DURATION
                  and not order["alerted"]
              ):
                order["alerted"] = True
                emoji = "🟢" if "bid" in key else "🔴"
                msg = (
                    f"{emoji} *PAXGUSDT — Крупная заявка*\n"
                    f"-----------------------------\n"
                    f"*Направление:* {order['type']}\n"
                    f"*Цена:* ${order['price']:,.2f}\n"
                    f"*Объём:* {order['qty']:.4f} PAXG\n"
                    f"*Сумма (USD):* ${order['usd']:,.2f}\n"
                    f"*Порог:* ${THRESHOLD_USD:,.0f}\n"
                    f"*Время:* {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC"
                )
                send_telegram_message(msg)
            else:
              del tracked_orders[key]
    except Exception as e:
      await asyncio.sleep(5)


if __name__ == "__main__":
  asyncio.run(monitor_order_book())
