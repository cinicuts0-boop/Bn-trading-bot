
import yfinance as yf
import pandas as pd
import ta
import time
import requests

TELEGRAM_TOKEN = "8673237471:AAF8zpyUYnTsfJazfI-19x2o2Oi5VkDpuwU"
CHAT_ID = "8007854479"

# 📤 Telegram
def send_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
        print("📤 Sent")
    except Exception as e:
        print("Telegram Error:", e)

# 📊 NIFTY DATA
def get_data():
    try:
        df = yf.download("^NSEI", interval="5m", period="1d", progress=False)

        if df is None or df.empty:
            return None

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        df = df.reset_index()

        df = df.rename(columns={
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Volume": "volume"
        })

        df["close"] = df["close"].astype(float)

        return df

    except Exception as e:
        print("Data Error:", e)
        return None

# 📈 STRATEGY (UPDATED 🔥)
def strategy(df):
    try:
        df["rsi"] = ta.momentum.RSIIndicator(df["close"]).rsi()

        last = df.iloc[-1]

        price = float(last["close"])
        rsi = float(last["rsi"])

        signal = None
        option = None
        option_price = None

        # 🔥 OPTIONS LOGIC + PRICE
        if rsi < 48:
            signal = "BUY"
            option = "NIFTY 7APR 22900 CE"
            option_price = (price - 22900) + 120   # adjust value if needed

        elif rsi > 52:
            signal = "BUY"
            option = "NIFTY 7APR 23000 PE"
            option_price = (23000 - price) + 120

        return signal, option, price, rsi, option_price

    except Exception as e:
        print("Strategy Error:", e)
        return None, None, None, None, None

# 🤖 BOT
def run_bot():
    print("🚀 OPTIONS BOT (WITH PRICE) STARTED")

    last_signal = None

    while True:
        try:
            print("⏳ Checking market...")

            df = get_data()

            if df is None:
                print("❌ Data error")
                time.sleep(10)
                continue

            signal, option, price, rsi, option_price = strategy(df)

            if price is None:
                print("⚠️ Strategy failed")
                time.sleep(10)
                continue

            print(f"📊 NIFTY: {price} | RSI: {round(rsi,2)}")

            if signal and signal != last_signal:

                msg = f"""
📊 NIFTY OPTIONS SIGNAL

🔔 {signal}

🎯 {option}

💰 NIFTY: {round(price,2)}
💸 Option Price: ₹{round(option_price,2)}

📈 RSI: {round(rsi,2)}
"""

                send_telegram(msg)
                print("🔥 Signal Sent:", option)

                last_signal = signal

            else:
                print("😴 No Trade")

            time.sleep(60)

        except Exception as e:
            print("Bot Error:", e)
            time.sleep(10)

run_bot()
