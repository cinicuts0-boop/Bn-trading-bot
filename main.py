
import requests
import pandas as pd
import ta
import time
import yfinance as yf

TELEGRAM_TOKEN = "8673237471:AAF8zpyUYnTsfJazfI-19x2o2Oi5VkDpuwU"
CHAT_ID = "8007854479"

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

# 🔥 Crude price
def get_crude_price():
    df = yf.download("CL=F", period="1d", interval="1m", progress=False)

    if df is None or df.empty:
        return None

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    return float(df["Close"].iloc[-1])

# 📈 Strategy
def strategy(price_history):
    df = pd.DataFrame(price_history, columns=["close"])

    df["rsi"] = ta.momentum.RSIIndicator(df["close"]).rsi()
    df["ema"] = ta.trend.EMAIndicator(df["close"], window=20).ema_indicator()

    macd = ta.trend.MACD(df["close"])
    df["macd"] = macd.macd()
    df["signal_line"] = macd.macd_signal()

    last = df.iloc[-1]

    price = float(last["close"])
    rsi = float(last["rsi"])
    ema = float(last["ema"])

    signal = None
    option = None

    if rsi < 40 and price > ema and last["macd"] > last["signal_line"]:
        signal = "BUY"
        option = "CRUDEOIL PE"

    elif rsi > 60 and price < ema and last["macd"] < last["signal_line"]:
        signal = "BUY"
        option = "CRUDEOIL CE"

    return signal, option, price, rsi

# 🔥 Entry Zone
def get_entry_zone(price):
    return round(price - 0.5, 2), round(price + 0.5, 2)

# 🔥 Targets
def get_targets(price):
    sl = round(price - 1.0, 2)
    tp1 = round(price + 1.5, 2)
    tp2 = round(price + 3.0, 2)
    return sl, tp1, tp2

# 🤖 BOT
def run_bot():
    print("🚀 FIXED CRUDE BOT STARTED")

    price_history = []
    last_signal_time = 0

    while True:
        try:
            price = get_crude_price()

            if price is None:
                time.sleep(10)
                continue

            price_history.append(price)

            if len(price_history) > 100:
                price_history.pop(0)

            if len(price_history) < 30:
                print("Collecting data...")
                time.sleep(5)
                continue

            signal, option, price, rsi = strategy(price_history)

            print(f"USD Crude: {price} | RSI: {round(rsi,2)}")

            # ✅ Correct indentation (INSIDE TRY)
            if signal and (time.time() - last_signal_time > 300):

                entry_low, entry_high = get_entry_zone(price)
                sl, tp1, tp2 = get_targets(price)

                msg = f"""
🚀 CRUDEOIL PRO SIGNAL

🔔 {signal}
🎯 {option}

📥 ENTRY ZONE: ₹{entry_low} - ₹{entry_high}

🎯 TP1: ₹{tp1}
🎯 TP2: ₹{tp2}
🛑 SL: ₹{sl}

📌 Chart பார்த்து confirm பண்ணி entry எடுக்கவும்

📈 RSI: {round(rsi,2)}
"""

                send_telegram(msg)
                last_signal_time = time.time()

            else:
                print("No trade")

            time.sleep(10)

        except Exception as e:
            print("Error:", e)
            time.sleep(10)

run_bot()
