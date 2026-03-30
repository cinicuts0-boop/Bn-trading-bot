
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
    data = requests.get(url).json()

    closes = data['chart']['result'][0]['indicators']['quote'][0]['close']
    df = pd.DataFrame(closes, columns=['close'])
    return df.dropna()

def strategy():
    df = get_data()

    df['rsi'] = ta.momentum.RSIIndicator(df['close'], window=14).rsi()
    df['ema'] = df['close'].ewm(span=20).mean()

    last = df.iloc[-1]

    if last['rsi'] < 30:
        return "📈 BUY CE 51200"

    elif last['rsi'] > 70:
        return "📉 BUY PE 51200"

    return None

while True:
    signal = strategy()

    if signal:
        send_telegram(f"🚨 BankNifty Signal: {signal}")

    time.sleep(300)  # 5 mins
