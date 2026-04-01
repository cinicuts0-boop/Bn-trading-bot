
import requests
import pandas as pd
import ta
import time

TELEGRAM_TOKEN = "8673237471:AAF8zpyUYnTsfJazfI-19x2o2Oi5VkDpuwU"
CHAT_ID = "8007854479"


def get_data():
    url = "https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=5m&limit=100"
    
    res = requests.get(url)
    
    if res.status_code != 200:
        print("API Error:", res.text)
        return None

    data = res.json()

    # Check if data is list
    if not isinstance(data, list):
        print("Invalid Data:", data)
        return None

    df = pd.DataFrame(data, columns=[
        "time","open","high","low","close","volume",
        "close_time","qav","trades","tbbav","tbqav","ignore"
    ])

    df = df[["time","open","high","low","close","volume"]]
    df["close"] = df["close"].astype(float)

    return df
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

    # BUY CONDITION
    if rsi < 40 and ema20 > ema50:
        signal = "BUY"

    # SELL CONDITION
    elif rsi > 60 and ema20 < ema50:
        signal = "SELL"

    return signal, price, rsi

def run_bot():
    print("NIFTY Bot Started...")
    last_signal = None

    while True:
        df = get_data()
        signal, price, rsi = strategy(df)

        print(f"Price: {price} RSI: {rsi}")

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

💰 Entry: {price}
🎯 TP1: {tp1}
🎯 TP2: {tp2}
🛑 SL : {sl}

📈 RSI: {round(rsi,2)}
"""

            send_telegram(msg)
            print("Signal Sent:", signal)

            last_signal = signal
        else:
            print("No new signal")

        time.sleep(60)

run_bot()
