import requests
import pandas as pd
import time
import os
from telegram import Bot

TOKEN = os.getenv("8673237471:AAF8zpyUYnTsfJazfI-19x2o2Oi5VkDpuwU")
CHAT_ID = os.getenv("8007854479")

bot = Bot(token=TOKEN)

SYMBOL = "ETHUSDT"
INTERVAL = "15m"

def get_data():
    url = f"https://api.binance.com/api/v3/klines?symbol={SYMBOL}&interval={INTERVAL}&limit=100"
    data = requests.get(url).json()
    
    df = pd.DataFrame(data, columns=[
        "time","open","high","low","close","volume",
        "ct","qav","trades","tbv","tqv","ignore"
    ])
    
    df["close"] = df["close"].astype(float)
    return df

def calculate_rsi(df, period=14):
    delta = df["close"].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi

def calculate_macd(df):
    exp1 = df["close"].ewm(span=12).mean()
    exp2 = df["close"].ewm(span=26).mean()
    macd = exp1 - exp2
    signal = macd.ewm(span=9).mean()
    return macd, signal

def send_signal(signal, price, rsi):
    message = f"""
🚨 {signal} SIGNAL — ETH/USDT

💰 Price: ${price}
📊 RSI: {round(rsi,2)}

🎯 TP1: {round(price*1.01,2)}
🎯 TP2: {round(price*1.02,2
