
import requests
import pandas as pd
import time
import ta

TELEGRAM_TOKEN = "8673237471:AAF8zpyUYnTsfJazfI-19x2o2Oi5VkDpuwU"
CHAT_ID = "8007854479"

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

def get_data():
    url = "https://query1.finance.yahoo.com/v8/finance/chart/%5ENSEI"

    try:
        res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)

        if res.status_code != 200:
            print("API Error:", res.status_code)
            return None

        data = res.json()
        result = data['chart']['result'][0]

        closes = result['indicators']['quote'][0]['close']
        timestamps = result['timestamp']

        df = pd.DataFrame({
            "time": pd.to_datetime(timestamps, unit='s'),
            "close": closes
        })

        return df.dropna()

    except Exception as e:
        print("Data Error:", e)
        return None


def strategy():
    df = get_data()

    if df is None or df.empty:
        return None

    df['rsi'] = ta.momentum.RSIIndicator(df['close'], window=14).rsi()
    df['ema'] = df['close'].ewm(span=50).mean()

    last = df.iloc[-1]

    print("Price:", last['close'], "RSI:", last['rsi'])

    # 🎯 Your specific strikes
    CE_1 = "NIFTY 7APR 22900 CE"
    CE_2 = "NIFTY 7APR 23000 CE"

    # Strategy
    if last['rsi'] < 30 and last['close'] > last['ema']:
        return f"📈 BUY {CE_1} or {CE_2}"

    elif last['rsi'] > 70 and last['close'] < last['ema']:
        return f"📉 MARKET WEAK (Avoid CE / Look PE)"

    return None


print("NIFTY Bot Started...")

last_signal = None

while True:
    try:
        signal = strategy()

        if signal and signal != last_signal:
            send_telegram(f"🚨 {signal}")
            last_signal = signal
        else:
            print("No new signal")

    except Exception as e:
        print("Error:", e)

    time.sleep(300)
