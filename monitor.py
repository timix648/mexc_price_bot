import time
import requests
import os
import socket
import json
from dotenv import load_dotenv
from storage import update_cache, load_cache

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
FUTURES_TICKER_URL = "https://contract.mexc.com/api/v1/contract/ticker"
FUTURES_SYMBOLS_URL = "https://contract.mexc.com/api/v1/contract/detail"
FUTURES_SYMBOLS = set()
FUTURES_REFRESH_INTERVAL = 10800  # 3 hours

price_cache = load_cache()
alert_tracker = {}
last_futures_refresh = 0

ALERT_INTERVALS = {
    "pump": 1800,
    "dump": 1800
}

def send_alert(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}
    requests.post(url, data=data)

def wait_for_dns():
    while True:
        try:
            socket.gethostbyname("contract.mexc.com")
            return
        except socket.gaierror:
            print("Waiting for DNS resolution...")
            time.sleep(5)

def refresh_futures_symbols(retries=5, delay=5):
    for attempt in range(retries):
        try:
            response = requests.get(FUTURES_SYMBOLS_URL, timeout=10)
            response.raise_for_status()
            data = response.json()
            return {item["symbol"] for item in data["data"]}  # KEEP AS "BTC_USDT"
        except Exception as e:
            print(f"[Attempt {attempt+1}] Error refreshing futures symbols: {e}")
            time.sleep(delay)
    return set()

def fetch_futures_prices():
    try:
        response = requests.get(FUTURES_TICKER_URL)
        response.raise_for_status()
        return response.json()["data"]
    except requests.RequestException as e:
        print(f"Error fetching futures prices: {e}")
        return []

def should_alert(symbol, kind, now):
    return now - alert_tracker.get((symbol, kind), 0) >= ALERT_INTERVALS[kind]

def record_alert(symbol, kind, now):
    alert_tracker[(symbol, kind)] = now

def check_price_changes():
    global FUTURES_SYMBOLS, last_futures_refresh, price_cache

    now = time.time()

    if now - last_futures_refresh > FUTURES_REFRESH_INTERVAL or not FUTURES_SYMBOLS:
        wait_for_dns()
        FUTURES_SYMBOLS = refresh_futures_symbols()
        last_futures_refresh = now
        print(f"Fetched {len(FUTURES_SYMBOLS)} futures symbols")

    data = fetch_futures_prices()
    print(f"Fetched {len(data)} futures prices")

    checked = 0

    for item in data:
        symbol = item.get("symbol")
        if symbol not in FUTURES_SYMBOLS:
            continue

        try:
            last_price = float(item.get("lastPrice", 0))
            if last_price <= 0:
                continue
        except:
            continue

        checked += 1
        if symbol not in price_cache:
            price_cache[symbol] = [(now, last_price)]
            continue

        price_cache[symbol].append((now, last_price))
        price_cache[symbol] = [(t, p) for t, p in price_cache[symbol] if now - t <= 1800]

        # Persist cache
        update_cache(price_cache)

        thirty_min_ago_prices = [p for t, p in price_cache[symbol] if now - t >= 1800 - 60]

        if thirty_min_ago_prices:
            old_price = thirty_min_ago_prices[0]
            percent_change = ((last_price - old_price) / old_price) * 100 if old_price else 0

            print(f"[PUMP?] {symbol}: {old_price:.6f} → {last_price:.6f} ({percent_change:.2f}%)")
            if percent_change >= 18 and should_alert(symbol, "pump", now):
                send_alert(
                    f"🚀 <b>{symbol}</b> pumped {percent_change:.2f}% in the last 30 minutes!\n"
                    f"<b>From:</b> {old_price:.6f} → <b>To:</b> {last_price:.6f}"
                )
                record_alert(symbol, "pump", now)

            print(f"[DUMP?] {symbol}: {old_price:.6f} → {last_price:.6f} ({percent_change:.2f}%)")
            if percent_change <= -7 and should_alert(symbol, "dump", now):
                send_alert(
                    f"🔻 <b>{symbol}</b> dumped {percent_change:.2f}% in the last 30 minutes!\n"
                    f"<b>From:</b> {old_price:.6f} → <b>To:</b> {last_price:.6f}"
                )
                record_alert(symbol, "dump", now)

    print(f"Checked {checked} futures tokens this cycle.")

def start_monitoring():
    while True:
        try:
            check_price_changes()
            time.sleep(60)
        except Exception as e:
            print(f"Monitor error: {e}")
            time.sleep(10)
