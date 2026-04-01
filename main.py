
import requests
import pandas as pd
import ta
import time
import yfinance as yf

TELEGRAM_TOKEN = "8673237471:AAF8zpyUYnTsfJazfI-19x2o2Oi5VkDpuwU"
CHAT_ID = "8007854479"

# 🔥 Daily Strike Prices (Change manually daily)

CRUDE_CE_STRIKE = 22900      # CRUDE CE Strike
CRUDE_PE_STRIKE = 23000      # CRUDE PE Strike

NIFTY_CE_STRIKE = 22900      # Nifty CE Strike
NIFTY_PE_STRIKE = 23000      # Nifty PE Strike

# 📤 Telegram
def send_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
        print("📤 Sent")
    except Exception as e:
        print("Telegram Error:", e)

# 🛢️ Crude Price (Yahoo MCX approx)
def get_crude_price():
    try:
        df = yf.download("CL=F", period="1d", interval="1m", progress=False)
        if df is None or df.empty:
            return None
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return float(df["Close"].iloc[-1]) * 80   # USD -> MCX approx
    except:
        return None

# 📊 Nifty Price
def get_nifty_price():
    try:
        df = yf.download("^NSEI", interval="5m", period="1d", progress=False)
        if df is None or df.empty:
            return None
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return float(df["Close"].iloc[-1])
    except:
        return None

# 📈 Strategy
def strategy(price_history, strike, instrument="CRUDE"):
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

    # 🔥 Entry Logic
    if instrument == "CRUDE":
        if rsi < 45 and ema20 > ema50:
            signal = "BUY"
            option = f"CRUDEOIL {strike} CE"
        elif rsi > 55 and ema20 < ema50:
            signal = "BUY"
            option = f"CRUDEOIL {strike} PE"
    elif instrument == "NIFTY":
        if rsi < 45:
            signal = "BUY"
            option = f"NIFTY {strike} CE"
        elif rsi > 55:
            signal = "BUY"
            option = f"NIFTY {strike} PE"

    return signal, option, price, rsi

# 🤖 BOT
def run_bot():
    print("🚀 AUTO STRIKE PRO BOT STARTED")
    crude_history = []
    nifty_history = []
    last_signal = None

    while True:
        try:
            crude_price = get_crude_price()
            nifty_price = get_nifty_price()

            if crude_price is None or nifty_price is None:
                print("❌ Price fetch error")
                time.sleep(10)
                continue

            crude_history.append(crude_price)
            nifty_history.append(nifty_price)

            if len(crude_history) > 100:
                crude_history.pop(0)
            if len(nifty_history) > 100:
                nifty_history.pop(0)

            if len(crude_history) < 14 or len(nifty_history) < 14:
                print("⏳ Collecting data...")
                time.sleep(5)
                continue

            # 🔹 Crude Strategy
            c_signal, c_option, c_price, c_rsi = strategy(crude_history, CRUDE_STRIKE, "CRUDE")
            # 🔹 Nifty Strategy
            n_signal, n_option, n_price, n_rsi = strategy(nifty_history, NIFTY_CE_STRIKE, "NIFTY")

            # Send signals if new
            for sig, opt, prc, rsi in [(c_signal, c_option, c_price, c_rsi), (n_signal, n_option, n_price, n_rsi)]:
                if sig and sig != last_signal:
                    msg = f"""
🚀 AUTO STRIKE SIGNAL

🔔 {sig}
🎯 {opt}

💰 Price: {round(prc,2)}
📈 RSI: {round(rsi,2)}
"""
                    send_telegram(msg)
                    print("🔥 Signal Sent:", opt)
                    last_signal = sig
                else:
                    print("😴 No Trade:", opt)

            time.sleep(10)

        except Exception as e:
            print("❌ Bot Error:", e)
            time.sleep(10)

run_bot()
