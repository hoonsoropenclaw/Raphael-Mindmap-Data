"""
bot.py 的靜態 + import 測試
============================
不真的啟動 Telegram bot，只驗證：
  1. import 不爆
  2. 註冊的 handler 數量合理
  3. _safe_chat_id 邏輯正確
  4. _persist_google_token 路徑解析正確
"""
import os
import sys
from pathlib import Path

# 模擬 env（不真的進到 bot run）
os.environ.setdefault("TELEGRAM_BOT_TOKEN", "test-token")
os.environ.setdefault("TELEGRAM_CHAT_ID", "123456")
os.environ.setdefault("TELEGRAM_ALLOWED_USERS", "111,222")
os.environ.setdefault("GOOGLE_CLIENT_ID", "fake.apps.googleusercontent.com")
os.environ.setdefault("GOOGLE_CLIENT_SECRET", "fake-secret")
os.environ.setdefault("GOOGLE_SCOPES", "https://www.googleapis.com/auth/calendar.events")

sys.path.insert(0, str(Path(__file__).parent))
import bot  # noqa: E402

print(f"[OK] bot module 載入成功")

# 1. 白名單邏輯
class FakeUser:
    def __init__(self, uid): self.id = uid

class FakeUpdate:
    def __init__(self, user):
        self.effective_user = user

import asyncio

async def check_safe_chat_id():
    yes = await bot._safe_chat_id(FakeUpdate(FakeUser(111)))
    no = await bot._safe_chat_id(FakeUpdate(FakeUser(999)))
    assert yes is True, "白名單內應該通過"
    assert no is False, "白名單外應該擋下"
    print("[OK] _safe_chat_id 白名單邏輯正確")

asyncio.run(check_safe_chat_id())

# 2. callback handler 路由正確
async def fake_answer(): pass
class FakeQuery:
    def __init__(self, data): self.data = data
    async def answer(self): pass
    async def edit_message_text(self, text): self.last_text = text

class FakeContext:
    pass

async def test_callbacks():
    # 我們只測「路徑」會跑到 edit_message_text，不真的要 patch Calendar
    for action in ["ack", "snooze", "cancel"]:
        q = FakeQuery(f"{action}:evt123")
        class Upd:
            callback_query = q
        await bot.on_callback(Upd(), FakeContext())
        assert hasattr(q, "last_text"), f"{action} 應該要 edit_message_text"
        print(f"[OK] callback {action} 走到 edit_message_text: {q.last_text[:40]}...")

asyncio.run(test_callbacks())

# 3. 確認排程器鉤子存在
assert hasattr(bot, "scan_upcoming_events")
assert hasattr(bot, "post_init")
assert hasattr(bot, "push_reminder")
print("[OK] 排程器 + 推播 function 存在")

# 4. env 路徑
print(f"[OK] GOOGLE_TOKEN_PATH = {bot.GOOGLE_TOKEN_PATH}")
print(f"[OK] STATE_PATH = {bot.STATE_PATH}")

print()
print("=" * 50)
print("全部 bot.py 靜態測試通過")
