import requests
import pandas as pd
import ta
import time
import yfinance as yf

# 🔥 TELEGRAM SETUP
TELEGRAM_TOKEN = "8673237471:AAF8zpyUYnTsfJazfI-19x2o2Oi5VkDpuwU"
CHAT_ID = "8007854479"

# 🔥 DAILY STRIKE PRICES (CHANGE DAILY)
# CRUDEOIL STRIKES
CRUDE_CE_STRIKE = 9900
CRUDE_PE_STRIKE = 7500

# NIFTY STRIKES
NIFTY_CE_STRIKE = 22900
NIFTY_PE_STRIKE = 23000

# 📤 Telegram function
def send_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
        print("📤 Sent")
    except Exception as e:
        print("Telegram Error:", e)

# 🛢️ Crude Price (Yahoo MCX approximation)
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

# 📊 Nifty Price
def get_nifty_price():
    try:
        df = yf.download("^NSEI", period="1d", interval="5m", progress=False)
        if df is None or df.empty:
            return None
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return float(df["Close"].iloc[-1])
    except Exception as e:
        print("❌ Nifty Price Error:", e)
        return None

# 📈 Strategy
def strategy(price_history, strike_ce, strike_pe):
    df = pd.DataFrame(price_history, columns=["close"])
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
    option_price = None

    # 🔥 CE BUY Condition
    if rsi < 45 and ema20 > ema50:
        signal = "BUY"
        option = f"{strike_ce} CE"
        intrinsic = max(0, price - strike_ce)
        option_price = max(50, intrinsic + price*0.02)

    # 🔥 PE BUY Condition
    elif rsi > 55 and ema20 < ema50:
        signal = "BUY"
        option = f"{strike_pe} PE"
        intrinsic = max(0, strike_pe - price)
        option_price = max(50, intrinsic + price*0.02)

    return signal, option, price, rsi, option_price

# 🤖 AUTO STRIKE PRO BOT
def run_bot():
    print("🚀 AUTO STRIKE PRO BOT STARTED")
    crude_history = []
    nifty_history = []
    last_crude_signal = None
    last_nifty_signal = None

    while True:
        try:
            # --- Crude ---
            crude_price = get_crude_price()
            if crude_price:
                crude_history.append(crude_price)
                if len(crude_history) > 100:
                    crude_history.pop(0)
                if len(crude_history) >= 14:
                    signal, option, price, rsi, op = strategy(crude_history, CRUDE_CE_STRIKE, CRUDE_PE_STRIKE)
                    if signal and signal != last_crude_signal:
                        sl = op - 40
                        tp1 = op + 50
                        tp2 = op + 100
                        msg = f"""
🚀 AUTO STRIKE SIGNAL (CRUDE)

🔔 {signal}
🎯 {option}

💰 Price: {round(price,2)}
💸 Entry: ₹{round(op,2)}

🎯 TP1: ₹{round(tp1,2)}
🎯 TP2: ₹{round(tp2,2)}
🛑 SL : ₹{round(sl,2)}

📈 RSI: {round(rsi,2)}
"""
                        send_telegram(msg)
                        last_crude_signal = signal
                        print("🔥 Crude Signal Sent:", option)

            # --- Nifty ---
            nifty_price = get_nifty_price()
            if nifty_price:
                nifty_history.append(nifty_price)
                if len(nifty_history) > 100:
                    nifty_history.pop(0)
                if len(nifty_history) >= 14:
                    signal, option, price, rsi, op = strategy(nifty_history, NIFTY_CE_STRIKE, NIFTY_PE_STRIKE)
                    if signal and signal != last_nifty_signal:
                        sl = op - 50
                        tp1 = op + 60
                        tp2 = op + 120
                        msg = f"""
🚀 AUTO STRIKE SIGNAL (NIFTY)

🔔 {signal}
🎯 {option}

💰 Price: {round(price,2)}
💸 Entry: ₹{round(op,2)}

🎯 TP1: ₹{round(tp1,2)}
🎯 TP2: ₹{round(tp2,2)}
🛑 SL : ₹{round(sl,2)}

📈 RSI: {round(rsi,2)}
"""
                        send_telegram(msg)
                        last_nifty_signal = signal
                        print("🔥 Nifty Signal Sent:", option)

            # --- Wait ---
            time.sleep(10)

        except Exception as e:
            print("❌ Bot Error:", e)
            time.sleep(10)

run_bot()
