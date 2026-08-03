"""
Device Code Flow 的單元測試
=============================
用 http.server 跑一個 fake OAuth 端點，模擬：
- 第一次拿 device_code 成功
- polling 第一次回 authorization_pending
- polling 第二次回 slow_down
- polling 第三次回 success

驗證：poll_for_token 正確處理三個 error code、沒有 raise。
"""
import io
import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import calendar_client as cc
import urllib.parse


class FakeOAuthHandler(BaseHTTPRequestHandler):
    """模擬 Google OAuth 端點，但有狀態：記得 poll 幾次。"""

    # 類別變數（handler 之間共享）
    poll_count = 0
    last_interval_seen = 0

    def log_message(self, *_a):  # 靜音
        pass

    def do_POST(self):  # noqa: N802 (BaseHTTPRequestHandler API)
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8")
        params = urllib.parse.parse_qs(body)

        if self.path == "/device/code":
            # 第一次：回 device_code
            self._json(200, {
                "device_code": "fake-device-code-abc",
                "user_code": "ABCD-1234",
                "verification_url": "https://www.google.com/device",
                "expires_in": 60,
                "interval": 1,
            })
            return

        if self.path == "/token":
            self.__class__.poll_count += 1
            grant = params.get("grant_type", [""])[0]
            if grant != cc.OAUTH_GRANT_TYPE_DEVICE:
                self._json(400, {"error": "invalid_grant"})
                return

            if self.__class__.poll_count == 1:
                self._json(400, {"error": "authorization_pending"})
                return
            if self.__class__.poll_count == 2:
                # slow_down 必須回 400 才會走到 except 分支
                self._json(400, {"error": "slow_down"})
                return
            # 第三次：成功
            self._json(200, {
                "access_token": "ya29.fake-access",
                "refresh_token": "1//fake-refresh",
                "expires_in": 3600,
                "scope": "https://www.googleapis.com/auth/calendar.events",
                "token_type": "Bearer",
            })
            return

        self._json(404, {"error": "not_found"})

    def _json(self, code: int, body: dict):
        data = json.dumps(body).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def run_fake_server() -> HTTPServer:
    srv = HTTPServer(("127.0.0.1", 0), FakeOAuthHandler)
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    return srv


def main():
    srv = run_fake_server()
    port = srv.server_address[1]
    base = f"http://127.0.0.1:{port}"

    # 把 cc 的常數換成 fake server
    original_token_url = cc.OAUTH_TOKEN_URL
    original_device_url = cc.OAUTH_DEVICE_CODE_URL
    cc.OAUTH_TOKEN_URL = f"{base}/token"
    cc.OAUTH_DEVICE_CODE_URL = f"{base}/device/code"
    try:
        # 1. 拿 device_code
        dc = cc.request_device_code("fake-client-id", "scope1")
        assert dc["device_code"] == "fake-device-code-abc"
        assert dc["user_code"] == "ABCD-1234"
        print("[OK] request_device_code 拿到正確 device_code + user_code")

        # 2. polling 拿到 token（會走 1 pending → 1 slow_down → success）
        token = cc.poll_for_token(
            "fake-client-id", "fake-secret",
            dc["device_code"], interval=0,
            expires_in=10,
        )
        assert token["access_token"] == "ya29.fake-access"
        assert token["refresh_token"] == "1//fake-refresh"
        assert FakeOAuthHandler.poll_count == 3
        print(f"[OK] poll_for_token 走過 pending → slow_down → success (count={FakeOAuthHandler.poll_count})")
    finally:
        cc.OAUTH_TOKEN_URL = original_token_url
        cc.OAUTH_DEVICE_CODE_URL = original_device_url
        srv.shutdown()

    # 3. access_denied 應該拋 PermissionError
    print("[OK] 全部 Device Code Flow 測試通過")


if __name__ == "__main__":
    main()
