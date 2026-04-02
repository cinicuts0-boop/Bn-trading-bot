

import requests
import pandas as pd
import ta
import time
import yfinance as yf

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

# 🔥 REAL Crude Oil Price (Yahoo)
def get_crude_price():
    try:
        df = yf.download("CL=F", period="1d", interval="1m", progress=False)

        if df is None or df.empty:
            return None

        # MultiIndex fix
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        price = float(df["Close"].iloc[-1])

        return price

    except Exception as e:
        print("❌ Yahoo Error:", e)
        return None

# 📈 Strategy
def strategy(price_history):
    df = pd.DataFrame(price_history, columns=["close"])

    df["rsi"] = ta.momentum.RSIIndicator(df["close"]).rsi()

    last = df.iloc[-1]

    price = float(last["close"])   # USD crude
    rsi = float(last["rsi"])

    # 🔥 Convert to MCX (approx)
    mcx_price = price * 80

    signal = None
    option = None
    option_price = None

    # 🔥 BETTER LOGIC
    if rsi < 45:
        signal = "BUY"
        option = "CRUDEOIL 9900 CE"

        option_price = max(100, abs(mcx_price - 9900) * 0.35)

    elif rsi > 55:
        signal = "BUY"
        option = "CRUDEOIL 7500 PE"

        option_price = max(100, abs(7500 - mcx_price) * 0.35)

    return signal, option, mcx_price, rsi, option_price

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

            # keep last 100 candles only
            if len(price_history) > 100:
                price_history.pop(0)

            # Need minimum data for RSI
            if len(price_history) < 20:
                print("⏳ Collecting data...")
                time.sleep(5)
                continue

            signal, option, price, rsi, op = strategy(price_history)

            print(f"🛢️ CRUDE: {price} | RSI: {round(rsi,2)}")

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
            print("❌ Bot Error:", e)
            time.sleep(10)

run_bot()

