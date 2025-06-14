# Only run asyncio.run ONCE at the top level
import asyncio
import threading
import os
from dotenv import load_dotenv

from telegram_bot import run_bot
from monitor import start_monitoring
from uptime_server import run_uptime_server

load_dotenv()

# ✅ Run uptime server once (if not already running)
def start_uptime_once():
    try:
        threading.Thread(target=run_uptime_server, daemon=True).start()
    except OSError as e:
        print(f"⚠️ Uptime server issue: {e}")

async def main():
    start_uptime_once()

    bot = asyncio.create_task(run_bot())
    monitor = asyncio.to_thread(start_monitoring)

    print("✅ Bot and monitor running...\n")
    await asyncio.gather(bot, monitor)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except RuntimeError as e:
        if "running event loop" in str(e):
            print("⚠️ Event loop already running — ignoring redundant close")
        else:
            raise
