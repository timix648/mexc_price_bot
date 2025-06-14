import asyncio
import os
import time
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from uptime_server import start_uptime_server  # 👈 Add this
from telegram_bot import run_bot
from monitor import start_monitoring
from dotenv import load_dotenv

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
    port = int(os.environ.get("PORT", 10000))  # Render scans port 10000+
    server = HTTPServer(('', port), HealthHandler)
    server.serve_forever()
# ─────────────────────────────────────────────────── #

async def main():
    print("⏳ Starting bot and monitor...")
    start_uptime_server()  # 👈 Launch the uptime server
    bot = asyncio.create_task(run_bot())
    monitor = asyncio.to_thread(start_monitoring)

    await asyncio.sleep(3)
    print("✅ Bot and monitor running...\n")
    await asyncio.gather(bot, monitor)

if __name__ == '__main__':
    # Start the fake HTTP server in a separate thread
    threading.Thread(target=run_health_check_server, daemon=True).start()

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
                loop.close()
            except Exception:
                pass
