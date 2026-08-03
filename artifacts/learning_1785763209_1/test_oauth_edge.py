"""
Device Code Flow 邊界測試
========================
額外驗證：access_denied 應該拋 PermissionError、expired_token 拋 TimeoutError。
"""
import json
import threading
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer

import calendar_client as cc


class AlwaysDenyHandler(BaseHTTPRequestHandler):
    def log_message(self, *_a):
        pass
    def do_POST(self):  # noqa: N802
        length = int(self.headers.get("Content-Length", 0))
        self.rfile.read(length)
        self.send_response(400)
        self.send_header("Content-Type", "application/json")
        body = json.dumps({"error": "access_denied"}).encode()
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


class AlwaysExpireHandler(BaseHTTPRequestHandler):
    def log_message(self, *_a):
        pass
    def do_POST(self):  # noqa: N802
        length = int(self.headers.get("Content-Length", 0))
        self.rfile.read(length)
        self.send_response(400)
        self.send_header("Content-Type", "application/json")
        body = json.dumps({"error": "expired_token"}).encode()
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def _serve(handler_cls):
    srv = HTTPServer(("127.0.0.1", 0), handler_cls)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def test_access_denied():
    srv = _serve(AlwaysDenyHandler)
    base = f"http://127.0.0.1:{srv.server_address[1]}"
    orig = cc.OAUTH_TOKEN_URL
    cc.OAUTH_TOKEN_URL = base
    try:
        try:
            cc.poll_for_token("c", "s", "d", interval=0, expires_in=5)
            print("[FAIL] 應該拋 PermissionError")
        except PermissionError as e:
            print(f"[OK] access_denied 正確拋 PermissionError: {e}")
    finally:
        cc.OAUTH_TOKEN_URL = orig
        srv.shutdown()


def test_expired_token():
    srv = _serve(AlwaysExpireHandler)
    base = f"http://127.0.0.1:{srv.server_address[1]}"
    orig = cc.OAUTH_TOKEN_URL
    cc.OAUTH_TOKEN_URL = base
    try:
        try:
            cc.poll_for_token("c", "s", "d", interval=0, expires_in=5)
            print("[FAIL] 應該拋 TimeoutError")
        except TimeoutError as e:
            print(f"[OK] expired_token 正確拋 TimeoutError: {e}")
    finally:
        cc.OAUTH_TOKEN_URL = orig
        srv.shutdown()


if __name__ == "__main__":
    test_access_denied()
    test_expired_token()
    print("[OK] 邊界測試全部通過")
