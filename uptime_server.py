from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

class UptimeHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/healthz":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Bot is alive")
        else:
            self.send_response(404)
            self.end_headers()

def run_uptime_server():
    server = HTTPServer(("0.0.0.0", 8080), UptimeHandler)
    print("🌐 Uptime server running on port 8080")
    server.serve_forever()

def start_uptime_server():
    thread = threading.Thread(target=run_uptime_server, daemon=True)
    thread.start()
