
import requests
import pandas as pd
import time
import ta
import os

TELEGRAM_TOKEN = os.getenv("8673237471:AAF8zpyUYnTsfJazfI-19x2o2Oi5VkDpuwU")
CHAT_ID = os.getenv("8007854479")

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

def get_data():
    url = "https://query1.finance.yahoo.com/v8/finance/chart/%5ENSEBANK"

    try:
        res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})

        if res.status_code != 200:
            print("API Error:", res.status_code)
            return None

        data = res.json()

        closes = data['chart']['result'][0]['indicators']['quote'][0]['close']
        df = pd.DataFrame(closes, columns=['close'])
        return df.dropna()

    except Exception as e:
        print("Data Error:", e)
        return None

def strategy():
    df = get_data()

    if df is None or df.empty:
        print("No data")
        return None

    df['rsi'] = ta.momentum.RSIIndicator(df['close'], window=14).rsi()
    last = df.iloc[-1]

    print("RSI:", last['rsi'])

    if last['rsi'] < 30:
        return "📈 BUY CE 51200"
    elif last['rsi'] > 70:
        return "📉 BUY PE 51200"

    return None

print("Bot Started...")

while True:
    try:
        signal = strategy()

        if signal:
            send_telegram(f"🚨 BankNifty: {signal}")
        else:
            print("No signal")

    except Exception as e:
        print("Error:", e)

    time.sleep(300)
