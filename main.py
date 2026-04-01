
import requests
import time

TELEGRAM_TOKEN = "8673237471:AAF8zpyUYnTsfJazfI-19x2o2Oi5VkDpuwU"
CHAT_ID = "8007854479"

# Telegram
def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

# NSE headers (IMPORTANT)
headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br"
}

# Get option chain
def get_option_price():
    try:
        url = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"

        session = requests.Session()

        # Step 1: open NSE homepage (cookie set)
        session.get("https://www.nseindia.com", headers=headers, timeout=5)

        # Step 2: get option chain
        res = session.get(url, headers=headers, timeout=5)

        data = res.json()

        # ✅ SAFE CHECK
        if "records" not in data:
            print("❌ NSE blocked / invalid response")
            return None, None

        for item in data["records"]["data"]:
            if item.get("strikePrice") == 22900:

                ce = item.get("CE", {})
                pe = item.get("PE", {})

                ce_price = ce.get("lastPrice")
                pe_price = pe.get("lastPrice")

                return ce_price, pe_price

        return None, None

    except Exception as e:
        print("❌ Fetch Error:", e)
        return None, None

# BOT
def run_bot():
    print("🚀 LIVE NSE OPTION BOT STARTED")

    while True:
        try:
            ce, pe = get_option_price()

            if ce is None:
                print("❌ Data error")
                time.sleep(10)
                continue

            print(f"22900 CE: ₹{ce} | 23000 PE: ₹{pe}")

            msg = f"""
📊 LIVE NIFTY OPTIONS

🟢 22900 CE: ₹{ce}
🔴 23000 PE: ₹{pe}
"""

            send_telegram(msg)

            time.sleep(60)

        except Exception as e:
            print("Error:", e)
            time.sleep(10)

run_bot()
