#!/usr/bin/env python3
"""Small local proxy for read-only OTCharts data. Keeps API key on the server."""
import json, os, urllib.parse, urllib.request
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BASE = "https://otcharts.com"
API_KEY = os.environ.get("OTCHARTS_API_KEY", "").strip()

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def send_json(self, status, obj):
        raw = json.dumps(obj).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path not in ("/api/candles", "/api/stream"):
            return super().do_GET()
        if not API_KEY:
            return self.send_json(503, {"error": "Missing OTCHARTS_API_KEY. Set it in your terminal, then restart server.py."})
        q = urllib.parse.parse_qs(parsed.query)
        venue = q.get("venue", ["otc"])[0]
        symbol = q.get("symbol", ["EURUSD_otc"])[0]
        if not symbol.replace("_", "").replace("-", "").isalnum() or venue not in ("otc", "forex"):
            return self.send_json(400, {"error": "Invalid venue or symbol."})
        headers = {"Authorization": "Bearer " + API_KEY, "Accept": "application/json"}
        if parsed.path == "/api/candles":
            try:
                tf = int(q.get("tf", ["60"])[0]); limit = min(500, max(1, int(q.get("limit", ["60"])[0])))
                params = urllib.parse.urlencode({"venue": venue, "symbol": symbol, "tf": tf, "limit": limit})
                req = urllib.request.Request(BASE + "/v1/candles?" + params, headers=headers)
                with urllib.request.urlopen(req, timeout=20) as r:
                    data = json.loads(r.read().decode())
                return self.send_json(200, data)
            except Exception as e:
                return self.send_json(502, {"error": "Provider candle request failed: " + str(e)})
        # Stream bytes from the upstream SSE connection without exposing the API key to the browser.
        try:
            params = urllib.parse.urlencode({"venue": venue, "symbol": symbol})
            req = urllib.request.Request(BASE + "/v1/stream?" + params, headers={**headers, "Accept": "text/event-stream"})
            upstream = urllib.request.urlopen(req, timeout=30)
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self.end_headers()
            while True:
                chunk = upstream.readline()
                if not chunk:
                    break
                self.wfile.write(chunk)
                self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError):
            pass
        except Exception as e:
            try:
                self.wfile.write(("event: error\ndata: " + json.dumps({"error": str(e)}) + "\n\n").encode())
                self.wfile.flush()
            except Exception:
                pass

if __name__ == "__main__":
    print("Market Companion Live is starting.")
    if not API_KEY:
        print("WARNING: OTCHARTS_API_KEY is not set; live data requests will show an error.")
    print("Open http://127.0.0.1:8000 in your browser. Stop with Ctrl+C.")
    ThreadingHTTPServer(("127.0.0.1", 8000), Handler).serve_forever()
