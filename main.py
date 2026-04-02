
import requests
import pandas as pd
import ta
import time
import yfinance as yf
import datetime

TELEGRAM_TOKEN = "8673237471:AAF8zpyUYnTsfJazfI-19x2o2Oi5VkDpuwU"
CHAT_ID = "8007854479"

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

def market_open():
    now = datetime.datetime.now().time()
    return now >= datetime.time(9, 0) and now <= datetime.time(23, 30)

def get_price():
    df = yf.download("CL=F", period="1d", interval="1m", progress=False)

    if df is None or df.empty:
        return None

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    return float(df["Close"].iloc[-1])

def strategy(price_history):
    df = pd.DataFrame(price_history, columns=["close"])

    # Indicators
    df["rsi"] = ta.momentum.RSIIndicator(df["close"]).rsi()
    df["ema"] = ta.trend.EMAIndicator(df["close"], window=20).ema_indicator()

    macd = ta.trend.MACD(df["close"])
    df["macd"] = macd.macd()
    df["signal"] = macd.macd_signal()

    last = df.iloc[-1]

    price = float(last["close"])
    rsi = float(last["rsi"])
    ema = float(last["ema"])
    macd_val = float(last["macd"])
    signal_val = float(last["signal"])

    mcx_price = price * 80

    trade = None
    option = None

    # BUY CE
    if rsi < 40 and price > ema and macd_val > signal_val:
        trade = "BUY"
        option = "CRUDEOIL CE"

    # BUY PE
    elif rsi > 60 and price < ema and macd_val < signal_val:
        trade = "BUY"
        option = "CRUDEOIL PE"

    return trade, option, mcx_price, rsi

def run_bot():
    print("🚀 ADVANCED CRUDE BOT STARTED")

    price_history = []
    last_signal_time = 0

    while True:
        try:
            if not market_open():
                print("⏰ Market Closed")
                time.sleep(60)
                continue

            price = get_price()

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

            print(f"Price: {price} | RSI: {round(rsi,2)}")

            # Cooldown 5 min
            if signal and (time.time() - last_signal_time > 300):

                entry = 120
                sl = entry - 30
                tp1 = entry + 40
                tp2 = entry + 80

                msg = f"""
🚀 CRUDEOIL PRO SIGNAL

🔔 {signal}
🎯 {option}

💰 Price: {round(price,2)}
💸 Entry: ₹{entry}

🎯 TP1: ₹{tp1}
🎯 TP2: ₹{tp2}
🛑 SL: ₹{sl}

📊 RSI: {round(rsi,2)}
"""

                send_telegram(msg)
                print("🔥 Signal Sent")

                last_signal_time = time.time()

            else:
                print("No trade")

            time.sleep(10)

        except Exception as e:
            print("Error:", e)
            time.sleep(10)

run_bot()
