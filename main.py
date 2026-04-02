
import requests
import pandas as pd
import ta
import time
import yfinance as yf

TELEGRAM_TOKEN = "8633538252:AAGIDwplfgtsGcGvZPCJmMrnX_R0dGOzOAc"
CHAT_ID = "8007854479"

last_update_id = None
manual_price = None

# 🔥 NEW STRIKE VARIABLES
CURRENT_STRIKE = 7500
OPTION_TYPE = "PE"

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

# 🔥 READ TELEGRAM COMMAND
def read_telegram():
    global last_update_id, manual_price, CURRENT_STRIKE, OPTION_TYPE

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
    res = requests.get(url).json()

    for update in res["result"]:
        uid = update["update_id"]

        if last_update_id is None or uid > last_update_id:
            last_update_id = uid

            try:
                text = update["message"]["text"]

                # 🔥 PRICE COMMAND
                if text.startswith("/setprice"):
                    price = float(text.split(" ")[1])
                    manual_price = price
                    send_telegram(f"✅ Price updated: ₹{price}")

                # 🔥 STRIKE COMMAND
                elif text.startswith("/setstrike"):
                    parts = text.split(" ")

                    CURRENT_STRIKE = int(parts[1])
                    OPTION_TYPE = parts[2].upper()

                    send_telegram(f"✅ Strike updated: {CURRENT_STRIKE} {OPTION_TYPE}")

            except:
                pass

# 🔥 FAKE PRICE (signal only)
def get_crude_price():
    df = yf.download("CL=F", period="1d", interval="1m", progress=False)

    if df is None or df.empty:
        return None

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    return float(df["Close"].iloc[-1])

# 📈 STRATEGY
def strategy(price_history):
    df = pd.DataFrame(price_history, columns=["close"])

    df["rsi"] = ta.momentum.RSIIndicator(df["close"]).rsi()
    last = df.iloc[-1]

    price = float(last["close"])
    rsi = float(last["rsi"])

    signal = None

    if rsi < 45:
        signal = "BUY"
    elif rsi > 55:
        signal = "SELL"

    return signal, price, rsi

# 🔥 TARGET (FIXED BUY/SELL LOGIC)
def get_targets(price, signal):

    if signal == "BUY":
        sl = round(price - 2, 2)
        tp1 = round(price + 3, 2)
        tp2 = round(price + 6, 2)

    elif signal == "SELL":
        sl = round(price + 2, 2)
        tp1 = round(price - 3, 2)
        tp2 = round(price - 6, 2)

    return sl, tp1, tp2

# 🤖 BOT
def run_bot():
    print("🚀 STRIKE + PRICE BOT STARTED")

    price_history = []
    last_signal_time = 0

    while True:
        try:
            read_telegram()

            price = get_crude_price()

            if price is None:
                time.sleep(10)
                continue

            price_history.append(price)

            if len(price_history) > 100:
                price_history.pop(0)

            if len(price_history) < 20:
                print("Collecting...")
                time.sleep(5)
                continue

            signal, price, rsi = strategy(price_history)

            print("Signal:", signal, "RSI:", round(rsi,2))

            if signal and manual_price:

                sl, tp1, tp2 = get_targets(manual_price, signal)

                msg = f"""
🚀 CRUDEOIL SIGNAL

🔔 {signal}
🎯 CRUDEOIL {CURRENT_STRIKE} {OPTION_TYPE}

💰 Entry: ₹{manual_price}

🎯 TP1: ₹{tp1}
🎯 TP2: ₹{tp2}
🛑 SL: ₹{sl}

📈 RSI: {round(rsi,2)}
"""

                send_telegram(msg)

                time.sleep(60)

            else:
                print("Waiting input...")

            time.sleep(10)

        except Exception as e:
            print("ERROR:", e)
            time.sleep(10)

last_update_id = None
run_bot()
manual_price = None


def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

# 🔥 READ TELEGRAM COMMAND
def read_telegram():
    global last_update_id, manual_price

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
    res = requests.get(url).json()

    for update in res["result"]:
        uid = update["update_id"]

        if last_update_id is None or uid > last_update_id:
            last_update_id = uid

            try:
                text = update["message"]["text"]

                # 🔥 COMMAND
                if text.startswith("/setprice"):
                    price = float(text.split(" ")[1])
                    manual_price = price

                    send_telegram(f"✅ Price updated: ₹{price}")

            except:
                pass

# 🔥 FAKE PRICE (signal only)
def get_crude_price():
    df = yf.download("CL=F", period="1d", interval="1m", progress=False)

    if df is None or df.empty:
        return None

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    return float(df["Close"].iloc[-1])

# 📈 STRATEGY
def strategy(price_history):
    df = pd.DataFrame(price_history, columns=["close"])

    df["rsi"] = ta.momentum.RSIIndicator(df["close"]).rsi()
    last = df.iloc[-1]

    price = float(last["close"])
    rsi = float(last["rsi"])

    signal = None

    if rsi < 45:
        signal = "BUY"
    elif rsi > 55:
        signal = "SELL"

    return signal, price, rsi

# 🔥 TARGET CALCULATION (USE MANUAL PRICE)
def get_targets(price):
    sl = round(price - 2, 2)
    tp1 = round(price + 3, 2)
    tp2 = round(price + 6, 2)
    return sl, tp1, tp2

# 🤖 BOT
def run_bot():
    print("🚀 PRICE INPUT BOT STARTED")

    price_history = []
    last_signal_time = 0

    while True:
        try:
            read_telegram()  # 🔥 check commands

            price = get_crude_price()

            if price is None:
                time.sleep(10)
                continue

            price_history.append(price)

            if len(price_history) > 100:
                price_history.pop(0)

            if len(price_history) < 20:
                print("Collecting...")
                time.sleep(5)
                continue

            signal, price, rsi = strategy(price_history)

            print("Signal:", signal, "RSI:", round(rsi,2))

            # 🔥 USE MANUAL PRICE
            if signal and manual_price:

                sl, tp1, tp2 = get_targets(manual_price)

                msg = f"""
🚀 CRUDEOIL SIGNAL

🔔 {signal}

💰 Entry (Manual): ₹{manual_price}

🎯 TP1: ₹{tp1}
🎯 TP2: ₹{tp2}
🛑 SL: ₹{sl}

📈 RSI: {round(rsi,2)}
"""

                send_telegram(msg)

                time.sleep(60)

            else:
                print("Waiting price input...")

            time.sleep(10)

        except Exception as e:
            print("ERROR:", e)
            time.sleep(10)

if __name__ == "__main__":
    run_bot()
