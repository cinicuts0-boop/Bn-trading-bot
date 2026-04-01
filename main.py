
import yfinance as yf
import pandas as pd
import ta
import time
import requests

# 🔐 Telegram সেটিং
TELEGRAM_TOKEN = "8673237471:AAF8zpyUYnTsfJazfI-19x2o2Oi5VkDpuwU"
CHAT_ID = "8007854479"

# 📤 Telegram Send
def send_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        res = requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
        print("📤 Telegram Status:", res.status_code)
    except Exception as e:
        print("❌ Telegram Error:", e)

# 📊 NIFTY Data Fetch
def get_data():
    try:
        df = yf.download("^NSEI", interval="5m", period="1d", progress=False)

        # ✅ Safety check
        if df is None or df.empty:
            print("❌ Empty data from Yahoo")
            return None

        df = df.reset_index()

        # ✅ Normalize column names
        df.columns = [col.lower() for col in df.columns]

        # Ensure required columns exist
        if "close" not in df.columns:
            print("❌ 'close' column missing")
            return None

        df["close"] = df["close"].astype(float)

        return df

    except Exception as e:
        print("❌ Data Error:", e)
        return None

# 📈 Strategy
def strategy(df):
    try:
        df["rsi"] = ta.momentum.RSIIndicator(df["close"]).rsi()
        df["ema20"] = ta.trend.EMAIndicator(df["close"], window=20).ema_indicator()
        df["ema50"] = ta.trend.EMAIndicator(df["close"], window=50).ema_indicator()

        last = df.iloc[-1]

        price = float(last["close"])
        rsi = float(last["rsi"])
        ema20 = float(last["ema20"])
        ema50 = float(last["ema50"])

        signal = None

        if rsi < 40 and ema20 > ema50:
            signal = "BUY"
        elif rsi > 60 and ema20 < ema50:
            signal = "SELL"

        return signal, price, rsi

    except Exception as e:
        print("❌ Strategy Error:", e)
        return None, None, None

# 🤖 Bot Runner
def run_bot():
    print("🚀 REAL NIFTY Bot Started")

    last_signal = None

    while True:
        try:
            print("⏳ Fetching NIFTY data...")

            df = get_data()

            if df is None:
                time.sleep(10)
                continue

            signal, price, rsi = strategy(df)

            # ✅ Safety check
            if price is None:
                print("⚠️ Strategy failed")
                time.sleep(10)
                continue

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

        except Exception as e:
            print("❌ Bot Error:", e)
            time.sleep(10)

# ▶️ Run
run_bot()
