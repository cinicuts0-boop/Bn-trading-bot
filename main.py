
import requests
import pandas as pd
import ta
import time

TELEGRAM_TOKEN = "8673237471:AAF8zpyUYnTsfJazfI-19x2o2Oi5VkDpuwU"
CHAT_ID = "8007854479"

# Telegram
def send_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
        print("📤 Sent")
    except Exception as e:
        print("Telegram Error:", e)

# 🔥 Crude Oil Price (free API)
def get_crude_price():
    try:
        url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
        res = requests.get(url)
        data = res.json()

        # ❗ Replace with crude logic (dummy for now)
        price = float(data["price"]) / 10   # simulate crude

        return price
    except:
        return None

# 📈 Strategy
def strategy(price_history):
    df = pd.DataFrame(price_history, columns=["close"])

    df["rsi"] = ta.momentum.RSIIndicator(df["close"]).rsi()

    last = df.iloc[-1]

    price = float(last["close"])
    rsi = float(last["rsi"])

    signal = None
    option = None
    option_price = None

    # 🔥 SIGNAL LOGIC
    if rsi < 45:
        signal = "BUY"
        option = "CRUDEOIL 9900 CE"
        option_price = max(50, abs(price - 9900) * 0.6)

    elif rsi > 55:
        signal = "BUY"
        option = "CRUDEOIL 7500 PE"
        option_price = max(50, abs(7500 - price) * 0.6)

    return signal, option, price, rsi, option_price

# 🤖 BOT
def run_bot():
    print("🚀 CRUDEOIL LIVE + SIGNAL PRO BOT STARTED")

    price_history = []
    last_signal = None

    while True:
        try:
            price = get_crude_price()

            if price is None:
                print("❌ Price fetch error")
                time.sleep(10)
                continue

            price_history.append(price)

            # Need minimum data for RSI
            if len(price_history) < 20:
                print("⏳ Collecting data...")
                time.sleep(5)
                continue

            signal, option, price, rsi, op = strategy(price_history)

            print(f"CRUDE: {price} RSI: {rsi}")

            if signal and signal != last_signal:

                sl = op - 30
                tp1 = op + 40
                tp2 = op + 80

                msg = f"""
🚀 CRUDEOIL SIGNAL

🔔 {signal}
🎯 {option}

💰 Crude Price: {round(price,2)}
💸 Entry: ₹{round(op,2)}

🎯 TP1: ₹{round(tp1,2)}
🎯 TP2: ₹{round(tp2,2)}
🛑 SL : ₹{round(sl,2)}

📈 RSI: {round(rsi,2)}
"""

                send_telegram(msg)
                print("🔥 Signal Sent:", option)

                last_signal = signal
            else:
                print("😴 No Trade")

            time.sleep(10)

        except Exception as e:
            print("Bot Error:", e)
            time.sleep(10)

run_bot()
