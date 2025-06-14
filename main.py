import asyncio
import os
import time
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from dotenv import load_dotenv

from telegram_bot import run_bot
from monitor import start_monitoring
from uptime_server import run_uptime_server  # renamed to match function
load_dotenv()

# ─────── FAKE HEALTH CHECK SERVER FOR RENDER ─────── #
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/healthz":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")
        else:
            self.send_response(404)
            self.end_headers()

def run_health_check_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('', port), HealthHandler)
    server.serve_forever()
# ─────────────────────────────────────────────────── #

# Ensure uptime server runs only once globally
threading.Thread(target=run_uptime_server, daemon=True).start()
threading.Thread(target=run_health_check_server, daemon=True).start()

async def main():
    print("⏳ Starting bot and monitor...")

    bot = asyncio.create_task(run_bot())
    monitor = asyncio.to_thread(start_monitoring)

    await asyncio.sleep(3)
    print("✅ Bot and monitor running...\n")

    await asyncio.gather(bot, monitor)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 Shutdown requested. Exiting gracefully...")
