import requests
import pandas as pd
import ta
import time
import yfinance as yf

# 🛠 Daily strike update (change only these)
CRUDE_CE_STRIKE = 9900
CRUDE_PE_STRIKE = 8000
NIFTY_CE_STRIKE = 22900
NIFTY_PE_STRIKE = 23000

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

# 🛢 Fetch Crude or Nifty Price
def get_price(symbol, market="crude"):
    try:
        if market == "crude":
            df = yf.download("CL=F", period="1d", interval="1m", progress=False)
            if df is None or df.empty:
                return None
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            usd_price = float(df["Close"].iloc[-1])
            mcx_price = usd_price * 80
            return mcx_price
        elif market == "nifty":
            df = yf.download("^NSEI", period="1d", interval="5m", progress=False)
            if df is None or df.empty:
                return None
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            return float(df["Close"].iloc[-1])
    except Exception as e:
        print(f"❌ Price fetch error ({symbol}):", e)
        return None

# 📈 Strategy
def strategy(price_history, ce_strike, pe_strike):
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
    entry_price = None
    
    # CE BUY signal
    if rsi < 45 and ema20 > ema50:
        signal = "BUY"
        option = f"{ce_strike} CE"
        intrinsic = max(0, price - ce_strike)
        entry_price = max(100, intrinsic + price * 0.02)
    
    # PE BUY signal
    elif rsi > 55 and ema20 < ema50:
        signal = "BUY"
        option = f"{pe_strike} PE"
        intrinsic = max(0, pe_strike - price)
        entry_price = max(100, intrinsic + price * 0.02)
    
    return signal, option, price, rsi, entry_price

# 🤖 BOT
def run_bot(symbol="CRUDE", ce_strike=CRUDE_CE_STRIKE, pe_strike=CRUDE_PE_STRIKE, market="crude"):
    print(f"🚀 AUTO STRIKE PRO BOT STARTED ({symbol})")
    price_history = []
    last_signal = None
    
    while True:
        try:
            price = get_price(symbol, market)
            if price is None:
                time.sleep(10)
                continue
            price_history.append(price)
            if len(price_history) > 100:
                price_history.pop(0)
            if len(price_history) < 14:
                print("⏳ Collecting data...")
                time.sleep(5)
                continue
            
            signal, option, price, rsi, entry = strategy(price_history, ce_strike, pe_strike)
            print(f"🛢 {symbol}: {price} | RSI: {round(rsi,2)}")
            
            if signal and signal != last_signal:
                sl = entry - 40
                tp1 = entry + 50
                tp2 = entry + 100
                
                msg = f"""
🚀 AUTO STRIKE SIGNAL ({symbol})

🔔 {signal}
🎯 {option}

💰 Price: {round(price,2)}
💸 Entry: ₹{round(entry,2)}

🎯 TP1: ₹{round(tp1,2)}
🎯 TP2: ₹{round(tp2,2)}
🛑 SL : ₹{round(sl,2)}

📈 RSI: {round(rsi,2)}
"""
                send_telegram(msg)
                last_signal = signal
            else:
                print("😴 No Trade")
            
            time.sleep(10)
        
        except Exception as e:
            print("❌ Bot Error:", e)
            time.sleep(10)

# 🔹 Run for Crude
run_bot(symbol="CRUDE", ce_strike=CRUDE_CE_STRIKE, pe_strike=CRUDE_PE_STRIKE, market="crude")
