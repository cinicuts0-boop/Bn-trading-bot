
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

    except:
        return None

# 📈 STRATEGY
def strategy(df):
    df["rsi"] = ta.momentum.RSIIndicator(df["close"]).rsi()
    df["ema20"] = ta.trend.EMAIndicator(df["close"], window=20).ema_indicator()
    df["ema50"] = ta.trend.EMAIndicator(df["close"], window=50).ema_indicator()

    last = df.iloc[-1]

    price = float(last["close"])
    rsi = float(last["rsi"])
    ema20 = float(last["ema20"])
    ema50 = float(last["ema50"])

    signal = None
    option = None

    # 🔥 OPTIONS LOGIC
    if rsi < 40 and ema20 > ema50:
        signal = "BUY"
        option = "22900 CE"

    elif rsi > 60 and ema20 < ema50:
        signal = "BUY"
        option = "23000 PE"

    return signal, option, price, rsi

# 🤖 BOT
def run_bot():
    print("🚀 OPTIONS PRO BOT STARTED")

    last_signal = None

    while True:
        print("⏳ Checking market...")

        df = get_data()

        if df is None:
            print("❌ Data error")
            time.sleep(10)
            continue

        signal, option, price, rsi = strategy(df)

        print(f"NIFTY: {price} RSI: {rsi}")

        if signal and signal != last_signal:

            msg = f"""
📊 NIFTY OPTIONS SIGNAL

🔔 {signal} {option}

💰 NIFTY: {round(price,2)}

🎯 TRADE:
👉 {option}

📈 RSI: {round(rsi,2)}
"""

            send_telegram(msg)
            print("🔥 Signal Sent:", option)

            last_signal = signal

        else:
            print("😴 No Trade")

        time.sleep(60)

run_bot()
