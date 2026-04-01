

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

# 🛢️ Crude Price
def get_crude_price():
    try:
        df = yf.download("CL=F", period="1d", interval="1m", progress=False)

        if df is None or df.empty:
            return None

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        return float(df["Close"].iloc[-1])

    except Exception as e:
        print("❌ Price Error:", e)
        return None

# 📈 Strategy
def strategy(price_history):
    df = pd.DataFrame(price_history, columns=["close"])

    df["rsi"] = ta.momentum.RSIIndicator(df["close"]).rsi()
    df["ema20"] = ta.trend.EMAIndicator(df["close"], window=20).ema_indicator()
    df["ema50"] = ta.trend.EMAIndicator(df["close"], window=50).ema_indicator()

    last = df.iloc[-1]

    usd_price = float(last["close"])
    rsi = float(last["rsi"])
    ema20 = float(last["ema20"])
    ema50 = float(last["ema50"])

    mcx_price = usd_price * 80
    strike = round(mcx_price / 100) * 100

    signal = None
    option = None
    option_price = None

    # 🔥 SNIPER ENTRY CONDITIONS

    # BUY CE (strong reversal up)
    if rsi < 40 and ema20 > ema50:
        signal = "BUY"
        option = f"CRUDEOIL {int(strike)} CE"

        intrinsic = max(0, mcx_price - strike)
        option_price = max(100, intrinsic + (mcx_price * 0.02))

    # BUY PE (strong reversal down)
    elif rsi > 60 and ema20 < ema50:
        signal = "BUY"
        option = f"CRUDEOIL {int(strike)} PE"

        intrinsic = max(0, strike - mcx_price)
        option_price = max(100, intrinsic + (mcx_price * 0.02))

    return signal, option, mcx_price, rsi, option_price

# 🤖 BOT
def run_bot():
    print("🚀 AUTO STRIKE PRO BOT STARTED")

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

            if len(price_history) > 100:
                price_history.pop(0)

            if len(price_history) < 14:
                print("⏳ Collecting data...")
                time.sleep(5)
                continue

            signal, option, price, rsi, op = strategy(price_history)

            print(f"🛢️ CRUDE (MCX): {price} | RSI: {round(rsi,2)}")

            if signal and signal != last_signal:

                sl = op - 40
                tp1 = op + 50
                tp2 = op + 100

                msg = f"""
🚀 AUTO STRIKE SIGNAL

🔔 {signal}
🎯 {option}

💰 Crude (MCX): {round(price,2)}
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
