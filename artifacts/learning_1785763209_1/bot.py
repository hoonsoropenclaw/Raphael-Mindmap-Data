"""
Telegram 會議通知機器人
======================
功能：
  /start     — 打招呼 + 顯示 chat_id
  /today     — 列出今天剩餘事件
  /week      — 列出未來 7 天事件
  /add <...> — 快速建立事件（例：/add 明天 3 點 跟 John 開會）
  /reschedule <id> <分鐘>  — 把事件往後延 N 分鐘

背景排程器（APScheduler）：
  每 POLL_INTERVAL_SECONDS 秒掃一次「未來 REMINDER_LEAD_MINUTES 分鐘內」事件
  第一次推播，記到 state.json（避免重複打擾）
  點「延後 5 分鐘」→ patch 事件 + 標記已提醒

啟動流程：
  1. python3 bot.py
  2. 沒有 GOOGLE token → 自動走 Device Code Flow，console 印 user_code
  3. 使用者去 https://www.google.com/device 輸入，授權
  4. token 存進 ~/.local/share/hermes/secrets/google_calendar_token.json
  5. 開 Telegram 跟 bot 對話
"""
from __future__ import annotations

import json
import logging
import os
import sys
import time
from dataclasses import asdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

import calendar_client as cc

# ============================================================
#  常數
# ============================================================

# Secrets 放 ~/.local/share/hermes/secrets/（不在 repo 內、chmod 600）
SECRETS_DIR = Path.home() / ".local" / "share" / "hermes" / "secrets"
GOOGLE_TOKEN_PATH = SECRETS_DIR / "google_calendar_token.json"
TELEGRAM_ENV_PATH = SECRETS_DIR / "calendar-bot.env"

# State：已提醒事件 ID（避免重複打擾）— 也可放 sqlite，但 JSON 對單人場景就夠
STATE_PATH = Path.home() / ".local" / "share" / "hermes" / "calendar-bot-state.json"

# 找不到 user env 時，fallback 到當前目錄的 .env（開發友善）
load_dotenv(TELEGRAM_ENV_PATH if TELEGRAM_ENV_PATH.exists() else ".env")

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    level=logging.INFO,
)
log = logging.getLogger("calendar-bot")


# ============================================================
#  Token 管理
# ============================================================

def _persist_google_token(token: dict) -> None:
    """寫進磁碟並補上 _client_id/_client_secret/_scopes 給日後 refresh 用。"""
    token["_client_id"] = os.environ["GOOGLE_CLIENT_ID"]
    token["_client_secret"] = os.environ["GOOGLE_CLIENT_SECRET"]
    token["_scopes"] = os.environ.get("GOOGLE_SCOPES", "")
    cc.save_token(token, GOOGLE_TOKEN_PATH)
    log.info("Google token 已存到 %s (mode 600)", GOOGLE_TOKEN_PATH)


def ensure_google_token(allow_first_run: bool = True) -> dict:
    """檢查/刷新/初次取得 Google token；回傳可用的 token dict。

    allow_first_run=False：用於 callback 流程。如果 token 根本沒初始化過，
    不嘗試 Device Code Flow（會卡 60s 等 polling），直接 raise，
    讓上層告訴使用者「請先手動跑一次 bot.py 完成 OAuth」。
    """
    if not os.environ.get("GOOGLE_CLIENT_ID"):
        raise RuntimeError("缺少 GOOGLE_CLIENT_ID，請先建立 TV-and-Limited-Input OAuth client")

    token = cc.load_token(GOOGLE_TOKEN_PATH)
    if token and not cc.is_token_expired(token):
        return token

    if token and token.get("refresh_token"):
        log.info("Token 過期，用 refresh_token 換新...")
        new = cc.refresh_access_token(
            token["_client_id"], token["_client_secret"], token["refresh_token"],
        )
        token.update(new)
        _persist_google_token(token)
        return token

    if not allow_first_run:
        raise RuntimeError(
            "Google 尚未 OAuth 過。請先在終端機跑 `python3 bot.py` "
            "完成首次 Device Code Flow 驗證。"
        )

    # 全新走 Device Code Flow
    log.info("=== 首次 OAuth：走 Device Code Flow ===")
    dc = cc.request_device_code(
        os.environ["GOOGLE_CLIENT_ID"],
        os.environ.get("GOOGLE_SCOPES", "https://www.googleapis.com/auth/calendar.events"),
    )
    print()
    print("============================================================")
    print(f"  請到  {dc['verification_url']}  輸入以下代碼：")
    print()
    print(f"     >>>  {dc['user_code']}  <<<")
    print()
    print(f"  代碼將於 {dc['expires_in']} 秒後失效")
    print("============================================================")
    print()
    sys.stdout.flush()
    token = cc.poll_for_token(
        os.environ["GOOGLE_CLIENT_ID"],
        os.environ["GOOGLE_CLIENT_SECRET"],
        dc["device_code"],
        interval=int(dc.get("interval", 5)),
        expires_in=int(dc["expires_in"]),
    )
    _persist_google_token(token)
    return token


# ============================================================
#  State：已提醒事件
# ============================================================

def _load_state() -> dict:
    if STATE_PATH.exists():
        try:
            return json.loads(STATE_PATH.read_text())
        except json.JSONDecodeError:
            log.warning("state.json 損壞，重置")
    return {"notified_event_ids": [], "snooze_until": {}}


def _save_state(state: dict) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, indent=2, default=str))
    os.chmod(STATE_PATH, 0o600)


def mark_notified(state: dict, event_id: str) -> None:
    if event_id not in state["notified_event_ids"]:
        state["notified_event_ids"].append(event_id)
        # 簡單 GC：超過 500 個就砍舊的
        state["notified_event_ids"] = state["notified_event_ids"][-500:]
        _save_state(state)


def is_snoozed(state: dict, event_id: str, now: datetime) -> bool:
    snooze_until = state.get("snooze_until", {}).get(event_id)
    if not snooze_until:
        return False
    try:
        until = datetime.fromisoformat(snooze_until)
    except ValueError:
        return False
    if now < until:
        return True
    # 過期就清掉
    state["snooze_until"].pop(event_id, None)
    _save_state(state)
    return False


def mark_snoozed(state: dict, event_id: str, minutes: int, now: datetime) -> datetime:
    until = now + timedelta(minutes=minutes)
    state["snooze_until"][event_id] = until.isoformat()
    # 從 notified 移除，這樣排程會再推一次
    if event_id in state["notified_event_ids"]:
        state["notified_event_ids"].remove(event_id)
    _save_state(state)
    return until


# ============================================================
#  Telegram 推播
# ============================================================

def _keyboard_for_event(event_id: str) -> InlineKeyboardMarkup:
    """每個提醒訊息的互動按鈕。"""
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ 確認", callback_data=f"ack:{event_id}"),
        InlineKeyboardButton("⏰ 延後 5 分", callback_data=f"snooze:{event_id}"),
        InlineKeyboardButton("❌ 取消", callback_data=f"cancel:{event_id}"),
    ]])


async def push_reminder(context: ContextTypes.DEFAULT_TYPE, event: cc.CalendarEvent) -> None:
    """主動推播提醒 + 附 inline keyboard。"""
    chat_id = int(os.environ["TELEGRAM_CHAT_ID"])
    caption = event.to_telegram_caption()
    try:
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"🔔 5 分鐘後開始\n\n{caption}",
            parse_mode="HTML",
            reply_markup=_keyboard_for_event(event.id),
            disable_web_page_preview=True,
        )
    except Exception as e:
        log.exception("推播失敗（event %s）：%s", event.id, e)


async def _safe_chat_id(update: Update) -> bool:
    """非白名單使用者直接略過、不回應（避免 bot 被亂戳）。"""
    allowed = os.environ.get("TELEGRAM_ALLOWED_USERS", "").strip()
    if not allowed:
        return True  # 沒設白名單 = 開放
    allowed_ids = {int(x) for x in allowed.split(",") if x.strip()}
    return bool(update.effective_user and update.effective_user.id in allowed_ids)


# ============================================================
#  APScheduler 排程：掃描即將到來事件
# ============================================================

async def scan_upcoming_events(context: ContextTypes.DEFAULT_TYPE) -> None:
    """每 30 秒跑一次。"""
    try:
        token = ensure_google_token()
    except Exception as e:
        log.error("token 檢查失敗：%s", e)
        return
    try:
        events = cc.list_upcoming_events(
            token,
            minutes_ahead=int(os.environ.get("REMINDER_LEAD_MINUTES", 5)) + 1,
        )
    except PermissionError as e:
        log.warning("token 過期，下次重試（%s）", e)
        return
    except Exception as e:
        log.exception("掃描事件失敗：%s", e)
        return

    state = _load_state()
    now = datetime.now(timezone.utc)
    for event in events:
        if event.id in state["notified_event_ids"]:
            continue
        if is_snoozed(state, event.id, now):
            continue
        # 還沒到提醒時間（差太多）就略過
        lead = int(os.environ.get("REMINDER_LEAD_MINUTES", 5))
        if event.minutes_until_start(now) > lead:
            continue
        log.info("推播提醒：%s @ %s", event.summary, event.start)
        await push_reminder(context, event)
        mark_notified(state, event.id)


# ============================================================
#  Command Handlers
# ============================================================

HELP_TEXT = """\
🤖 會議通知 bot

指令：
  /start          確認 bot 活著 + 顯示你的 chat_id
  /today          今天剩餘事件
  /week           未來 7 天事件
  /add <自然語言>  快速建立事件（例：/add 明天 3 點 跟 John 開會）
  /reschedule <id> <分鐘>  延後 N 分鐘
  /whoami         顯示你跟哪些 chat_id 配對

提醒按鈕（自動推播時附加）：
  ✅ 確認 — 把這事件從「未通知」清單移除
  ⏰ 延後 5 分 — 5 分鐘後再提醒一次（patch 行事曆）
  ❌ 取消 — 把事件刪掉
"""


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _safe_chat_id(update):
        return
    chat_id = update.effective_chat.id
    user = update.effective_user
    await update.message.reply_text(
        f"{HELP_TEXT}\n你的 chat_id = <code>{chat_id}</code>\nuser_id = <code>{user.id if user else '?'}</code>",
        parse_mode="HTML",
    )


async def cmd_today(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _safe_chat_id(update):
        return
    try:
        token = ensure_google_token()
    except Exception as e:
        await update.message.reply_text(f"❌ Google OAuth 失敗：{e}")
        return
    try:
        # 列出今天剩餘事件（從現在到 23:59）
        now = datetime.now(timezone.utc)
        end_of_day = now.replace(hour=23, minute=59, second=59, microsecond=0)
        # 借用 quick list 邏輯 — 為了簡化，重寫一個臨時函式
        from googleapiclient.discovery import build
        from google.oauth2.credentials import Credentials
        creds = Credentials(
            token=token["access_token"],
            refresh_token=token.get("refresh_token"),
            token_uri=cc.OAUTH_TOKEN_URL,
            client_id=token.get("_client_id"),
            client_secret=token.get("_client_secret"),
            scopes=token.get("_scopes", "").split() or None,
        )
        service = build("calendar", "v3", credentials=creds, cache_discovery=False)
        result = service.events().list(
            calendarId="primary",
            timeMin=now.isoformat(),
            timeMax=end_of_day.isoformat(),
            maxResults=20,
            singleEvents=True,
            orderBy="startTime",
        ).execute()
        events = result.get("items", [])
    except Exception as e:
        await update.message.reply_text(f"❌ 拉事件失敗：{e}")
        return

    if not events:
        await update.message.reply_text("今天剩餘沒有事件 🎉")
        return
    lines = ["📅 <b>今天剩餘事件：</b>\n"]
    for raw in events:
        ev = cc._event_from_api(raw)  # noqa: SLF001 — 內部 helper 共用 OK
        lines.append(ev.to_telegram_caption() + "\n")
    await update.message.reply_text("\n".join(lines), parse_mode="HTML", disable_web_page_preview=True)


async def cmd_week(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _safe_chat_id(update):
        return
    try:
        token = ensure_google_token()
    except Exception as e:
        await update.message.reply_text(f"❌ Google OAuth 失敗：{e}")
        return
    from googleapiclient.discovery import build
    from google.oauth2.credentials import Credentials
    creds = Credentials(
        token=token["access_token"],
        refresh_token=token.get("refresh_token"),
        token_uri=cc.OAUTH_TOKEN_URL,
        client_id=token.get("_client_id"),
        client_secret=token.get("_client_secret"),
        scopes=token.get("_scopes", "").split() or None,
    )
    service = build("calendar", "v3", credentials=creds, cache_discovery=False)
    now = datetime.now(timezone.utc)
    end_week = now + timedelta(days=7)
    result = service.events().list(
        calendarId="primary",
        timeMin=now.isoformat(),
        timeMax=end_week.isoformat(),
        maxResults=50,
        singleEvents=True,
        orderBy="startTime",
    ).execute()
    events = result.get("items", [])
    if not events:
        await update.message.reply_text("未來 7 天沒有事件 🎉")
        return
    lines = ["📆 <b>未來 7 天事件：</b>\n"]
    for raw in events:
        ev = cc._event_from_api(raw)  # noqa: SLF001
        lines.append(ev.to_telegram_caption() + "\n")
    await update.message.reply_text("\n".join(lines), parse_mode="HTML", disable_web_page_preview=True)


async def cmd_add(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _safe_chat_id(update):
        return
    text = " ".join(context.args)
    if not text:
        await update.message.reply_text("用法：/add 明天 3 點 跟 John 開會")
        return
    try:
        token = ensure_google_token()
        ev = cc.create_quick_event(token, text)
        await update.message.reply_text(
            f"✅ 已建立：<b>{ev.summary}</b>\n🕐 {ev.start.astimezone().strftime('%Y-%m-%d %H:%M %Z')}",
            parse_mode="HTML",
        )
    except Exception as e:
        await update.message.reply_text(f"❌ 建立失敗：{e}")


async def cmd_reschedule(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _safe_chat_id(update):
        return
    if len(context.args) < 2:
        await update.message.reply_text("用法：/reschedule <event_id> <延後分鐘>")
        return
    event_id, minutes = context.args[0], int(context.args[1])
    try:
        token = ensure_google_token()
        # 抓現有事件
        from googleapiclient.discovery import build
        from google.oauth2.credentials import Credentials
        creds = Credentials(
            token=token["access_token"],
            refresh_token=token.get("refresh_token"),
            token_uri=cc.OAUTH_TOKEN_URL,
            client_id=token.get("_client_id"),
            client_secret=token.get("_client_secret"),
            scopes=token.get("_scopes", "").split() or None,
        )
        service = build("calendar", "v3", credentials=creds, cache_discovery=False)
        ev_raw = service.events().get(calendarId="primary", eventId=event_id).execute()
        ev = cc._event_from_api(ev_raw)  # noqa: SLF001
        new_start = ev.start + timedelta(minutes=minutes)
        duration = int((ev.end - ev.start).total_seconds() / 60)
        ev2 = cc.reschedule_event(token, event_id, new_start, duration)
        await update.message.reply_text(
            f"✅ 已改時間：<b>{ev2.summary}</b>\n🕐 {ev2.start.astimezone().strftime('%Y-%m-%d %H:%M %Z')}",
            parse_mode="HTML",
        )
    except Exception as e:
        await update.message.reply_text(f"❌ 改時間失敗：{e}")


async def cmd_whoami(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    user = update.effective_user
    await update.message.reply_text(
        f"chat_id = {chat_id}\nuser_id = {user.id if user else '?'}",
    )


# ============================================================
#  Callback Handlers（按鈕）
# ============================================================

async def on_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query:
        return
    await query.answer()  # 一定要 answer 一次才能移除按鈕 loading 動畫
    data = query.data or ""
    action, _, event_id = data.partition(":")

    state = _load_state()

    if action == "ack":
        mark_notified(state, event_id)
        await query.edit_message_text(f"✅ 已確認（{event_id}）— 不再提醒")
    elif action == "snooze":
        now = datetime.now(timezone.utc)
        until = mark_snoozed(state, event_id, int(os.environ.get("SNOOZE_MINUTES", 5)), now)
        # 同步 patch 行事曆：延後 5 分鐘（讓真的會議也跟著延）
        try:
            token = ensure_google_token(allow_first_run=False)
            from googleapiclient.discovery import build
            from google.oauth2.credentials import Credentials
            creds = Credentials(
                token=token["access_token"],
                refresh_token=token.get("refresh_token"),
                token_uri=cc.OAUTH_TOKEN_URL,
                client_id=token.get("_client_id"),
                client_secret=token.get("_client_secret"),
                scopes=token.get("_scopes", "").split() or None,
            )
            service = build("calendar", "v3", credentials=creds, cache_discovery=False)
            ev_raw = service.events().get(calendarId="primary", eventId=event_id).execute()
            ev = cc._event_from_api(ev_raw)  # noqa: SLF001
            new_start = ev.start + timedelta(minutes=int(os.environ.get("SNOOZE_MINUTES", 5)))
            cc.reschedule_event(token, event_id, new_start, int((ev.end - ev.start).total_seconds() / 60))
        except Exception as e:
            log.warning("patch snooze 失敗（不影響提醒邏輯）：%s", e)
        until_local = until.astimezone().strftime("%H:%M %Z")
        await query.edit_message_text(f"⏰ 已延後到 {until_local} 再提醒你一次")
    elif action == "cancel":
        try:
            token = ensure_google_token(allow_first_run=False)
            from googleapiclient.discovery import build
            from google.oauth2.credentials import Credentials
            creds = Credentials(
                token=token["access_token"],
                refresh_token=token.get("refresh_token"),
                token_uri=cc.OAUTH_TOKEN_URL,
                client_id=token.get("_client_id"),
                client_secret=token.get("_client_secret"),
                scopes=token.get("_scopes", "").split() or None,
            )
            service = build("calendar", "v3", credentials=creds, cache_discovery=False)
            service.events().delete(calendarId="primary", eventId=event_id).execute()
        except Exception as e:
            await query.edit_message_text(f"❌ 刪除失敗：{e}")
            return
        await query.edit_message_text(f"🗑️ 已刪除事件 {event_id}")
    else:
        await query.edit_message_text(f"未知動作：{action}")


# ============================================================
#  入口
# ============================================================

async def post_init(application: Application) -> None:
    """Application 啟動後掛排程器。"""
    scheduler = AsyncIOScheduler(timezone="UTC")
    interval = int(os.environ.get("POLL_INTERVAL_SECONDS", 30))
    scheduler.add_job(
        scan_upcoming_events,
        "interval",
        seconds=interval,
        args=[application],
        id="scan",
        replace_existing=True,
    )
    scheduler.start()
    log.info("排程器啟動，每 %d 秒掃一次「未來 %d 分鐘內」事件",
             interval, int(os.environ.get("REMINDER_LEAD_MINUTES", 5)))
    # 啟動時先驗一次 token
    try:
        ensure_google_token()
    except Exception as e:
        log.error("Google token 取得失敗：%s", e)


def main() -> None:
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not bot_token:
        print("錯誤：缺少 TELEGRAM_BOT_TOKEN", file=sys.stderr)
        print("請在 ~/.local/share/hermes/secrets/calendar-bot.env 設定", file=sys.stderr)
        sys.exit(1)

    app = Application.builder().token(bot_token).post_init(post_init).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("today", cmd_today))
    app.add_handler(CommandHandler("week", cmd_week))
    app.add_handler(CommandHandler("add", cmd_add))
    app.add_handler(CommandHandler("reschedule", cmd_reschedule))
    app.add_handler(CommandHandler("whoami", cmd_whoami))
    app.add_handler(CallbackQueryHandler(on_callback))

    log.info("Telegram bot 啟動中...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
