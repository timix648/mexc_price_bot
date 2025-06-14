import asyncio
import os
import time
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from dotenv import load_dotenv

from telegram_bot import run_bot
from monitor import start_monitoring
from uptime_server import run_uptime_server

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
    try:
        server = HTTPServer(('', port), HealthHandler)
        server.serve_forever()
    except OSError as e:
        if e.errno == 98:
            print(f"⚠️ Health server: Port {port} already in use. Skipping...")

# ─────────────────────────────────────────────────── #

# Start both HTTP servers safely in threads
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
    first_run = True
    while True:
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(main())
        except Exception as e:
            print(f"\n❌ Crash occurred: {e}")
            print("🔁 Restarting in 10 seconds...\n")
            time.sleep(10)
            if not first_run:
                print("✅ Recovered: Bot and monitor are back online!\n")
            first_run = False
        finally:
            try:
                if not loop.is_closed():
                    loop.stop()
                    loop.close()
            except Exception:
                pass
