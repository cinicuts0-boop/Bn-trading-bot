
import yfinance as yf
import pandas as pd
import ta
import time
import requests

# 🔐 Telegram সেটিং
TELEGRAM_TOKEN = "8673237471:AAF8zpyUYnTsfJazfI-19x2o2Oi5VkDpuwU"
CHAT_ID = "8007854479"

def send_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
        print("📤 Telegram Sent")
    except Exception as e:
        print("Telegram Error:", e)

# 📊 NIFTY Data Fetch
def get_data():
    try:
        df = yf.download("^NSEI", interval="5m", period="1d")

        if df.empty:
            print("❌ No data received")
            return None

        df = df.reset_index()
        df = df.rename(columns={
            "Open":"open",
            "High":"high",
            "Low":"low",
            "Close":"close",
            "Volume":"volume"
        })

        return df

    except Exception as e:
        print("Data Error:", e)
        return None

# 📈 Strategy
def strategy(df):
    df["rsi"] = ta.momentum.RSIIndicator(df["close"]).rsi()
    df["ema20"] = ta.trend.EMAIndicator(df["close"], window=20).ema_indicator()
    df["ema50"] = ta.trend.EMAIndicator(df["close"], window=50).ema_indicator()

    last = df.iloc[-1]

    price = last["close"]
    rsi = last["rsi"]
    ema20 = last["ema20"]
    ema50 = last["ema50"]

    signal = None

    if rsi < 40 and ema20 > ema50:
        signal = "BUY"

    elif rsi > 60 and ema20 < ema50:
        signal = "SELL"

    return signal, price, rsi

# 🤖 Bot Runner
def run_bot():
    print("🚀 REAL NIFTY Bot Started")

    last_signal = None

    while True:
        print("⏳ Fetching NIFTY data...")

        df = get_data()

        if df is None:
            print("❌ Data failed. Retry...")
            time.sleep(10)
            continue

        signal, price, rsi = strategy(df)

        print(f"📊 Price: {price} | RSI: {round(rsi,2)}")

        if signal and signal != last_signal:

            if signal == "BUY":
                tp1 = price + 50
                tp2 = price + 100
                sl = price - 30
            else:
                tp1 = price - 50
                tp2 = price - 100
                sl = price + 30

            msg = f"""
📊 NIFTY SIGNAL

🔔 {signal}
💰 Entry: {round(price,2)}

🎯 TP1: {round(tp1,2)}
🎯 TP2: {round(tp2,2)}
🛑 SL : {round(sl,2)}

📈 RSI: {round(rsi,2)}
"""

            send_telegram(msg)
            print("🔥 Signal Sent:", signal)

            last_signal = signal
        else:
            print("😴 No Signal")

        time.sleep(60)

# ▶️ Run
run_bot()
