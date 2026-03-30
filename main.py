import time
import requests
import random  # (demo data)

# Telegram setup
BOT_TOKEN = "8673237471:AAF8zpyUYnTsfJazfI-19x2o2Oi5VkDpuwU"
CHAT_ID = "8007854479"

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

# Demo data (replace with real API later)
def get_data():
    return {
        "price": random.randint(51000, 51400),
        "rsi": random.randint(50, 80),
        "macd": random.uniform(-1, 1),
        "signal": random.uniform(-1, 1),
        "vwap": 51250
    }

def check_signal(data):
    if (
        data['price'] >= 51200 and
        data['rsi'] > 65 and
        data['macd'] < data['signal'] and
        data['price'] < data['vwap']
    ):
        return True
    return False

while True:
    data = get_data()
    
    if check_signal(data):
        msg = f"""🔴 BANKNIFTY 51200 PE BUY
Price: {data['price']}
RSI: {data['rsi']}"""
        send_telegram(msg)
        print("Signal sent")

    time.sleep(60)
