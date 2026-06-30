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

