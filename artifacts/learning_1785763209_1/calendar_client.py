"""
Google Calendar API 包裝層
=========================

設計目標：
1. 零瀏覽器即可 OAuth 認證（Device Code Flow，N100 headless 友善）
2. 提供三個核心操作：list / insert / patch
3. token 自動刷新 + 安全儲存（chmod 600）
4. graceful degradation：環境沒有 GOOGLE_CLIENT_ID 時，整個模組還能 import（方便測試）
"""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Google OAuth 2.0 端點（公開文件，無 secret）
OAUTH_TOKEN_URL = "https://oauth2.googleapis.com/token"
OAUTH_DEVICE_CODE_URL = "https://oauth2.googleapis.com/device/code"
OAUTH_GRANT_TYPE_DEVICE = "urn:ietf:params:oauth:grant-type:device_code"

# Device Code Flow 的 polling error code（MEMORY 已記錄）
POLL_ERROR_PENDING = "authorization_pending"   # 使用者還沒完成，繼續等
POLL_ERROR_SLOW_DOWN = "slow_down"             # 不是錯，interval += 5
POLL_ERROR_EXPIRED = "expired_token"           # 逾時，重新拿 device code
POLL_ERROR_ACCESS_DENIED = "access_denied"     # 使用者拒絕


@dataclass
class CalendarEvent:
    """會議事件的最小可操作單位。"""
    id: str
    summary: str
    start: datetime  # 永遠是 timezone-aware UTC
    end: datetime
    location: str | None = None
    description: str | None = None
    meet_link: str | None = None
    html_link: str | None = None

    def minutes_until_start(self, now: datetime | None = None) -> float:
        now = now or datetime.now(timezone.utc)
        return (self.start - now).total_seconds() / 60

    def to_telegram_caption(self) -> str:
        """產生 Telegram 訊息內文。"""
        start_local = self.start.astimezone().strftime("%Y-%m-%d %H:%M %Z")
        end_local = self.end.astimezone().strftime("%H:%M %Z")
        lines = [f"📅 <b>{_escape(self.summary)}</b>",
                 f"🕐 {start_local} → {end_local}"]
        if self.location:
            lines.append(f"📍 {_escape(self.location)}")
        if self.meet_link:
            lines.append(f"🔗 <a href=\"{self.meet_link}\">加入 Google Meet</a>")
        if self.html_link:
            lines.append(f"📝 <a href=\"{self.html_link}\">在行事曆開啟</a>")
        return "\n".join(lines)


def _escape(s: str) -> str:
    """Telegram HTML 模式最基本跳脫。"""
    return (s.replace("&", "&amp;")
             .replace("<", "&lt;")
             .replace(">", "&gt;"))


# ============================================================
#  Device Code Flow（自製，urllib-only，零新依賴）
# ============================================================

def request_device_code(client_id: str, scopes: str) -> dict[str, Any]:
    """第一步：跟 Google 拿 device_code + user_code + verification_url。

    使用者打開 verification_url、輸入 user_code、登入並授權。
    """
    data = urllib.parse.urlencode({
        "client_id": client_id,
        "scope": scopes,
    }).encode("utf-8")
    req = urllib.request.Request(
        OAUTH_DEVICE_CODE_URL,
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))


def poll_for_token(client_id: str, client_secret: str, device_code: str,
                   interval: int, expires_in: int) -> dict[str, Any]:
    """第二步：背景 polling 拿 access_token。

    處理 MEMORY 記錄的三個 error code：
    - authorization_pending → 繼續 polling
    - slow_down             → interval += 5（不是錯）
    - access_denied         → 拋 PermissionError 給上層

    Returns: {"access_token", "refresh_token", "expires_in", "scope", "token_type"}
    """
    deadline = time.monotonic() + expires_in
    current_interval = interval
    while time.monotonic() < deadline:
        data = urllib.parse.urlencode({
            "client_id": client_id,
            "client_secret": client_secret,
            "device_code": device_code,
            "grant_type": OAUTH_GRANT_TYPE_DEVICE,
        }).encode("utf-8")
        req = urllib.request.Request(
            OAUTH_TOKEN_URL, data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            try:
                err = json.loads(body)
            except json.JSONDecodeError:
                raise RuntimeError(f"OAuth 端點回非 JSON 錯誤: {body}") from e
            code = err.get("error", "")
            if code == POLL_ERROR_PENDING:
                time.sleep(current_interval)
                continue
            if code == POLL_ERROR_SLOW_DOWN:
                current_interval += 5
                time.sleep(current_interval)
                continue
            if code == POLL_ERROR_ACCESS_DENIED:
                raise PermissionError("使用者在 Google 端拒絕授權")
            if code == POLL_ERROR_EXPIRED:
                raise TimeoutError("device_code 過期，請重新執行")
            raise RuntimeError(f"OAuth 未知 error: {code} / {body}") from e
    raise TimeoutError("Device Code Flow 整段 timeout（{}s）".format(expires_in))


def save_token(token: dict[str, Any], path: Path) -> None:
    """把 token 寫到磁碟並鎖權限。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    # 補上 expires_at 方便下次重 load 用
    token = dict(token)
    token["expires_at"] = time.time() + int(token.get("expires_in", 3600))
    path.write_text(json.dumps(token, indent=2))
    os.chmod(path, 0o600)


def load_token(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return None


def is_token_expired(token: dict[str, Any]) -> bool:
    """5 分鐘安全邊際，提早判定過期以便 refresh。"""
    return time.time() >= float(token.get("expires_at", 0)) - 300


def refresh_access_token(client_id: str, client_secret: str,
                         refresh_token: str) -> dict[str, Any]:
    """refresh_token 換新 access_token。"""
    data = urllib.parse.urlencode({
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
    }).encode("utf-8")
    req = urllib.request.Request(
        OAUTH_TOKEN_URL, data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        result = json.loads(resp.read().decode("utf-8"))
    if "error" in result:
        raise RuntimeError(f"refresh 失敗: {result}")
    return result


# ============================================================
#  Calendar API 業務層
# ============================================================

def _parse_event_datetime(raw: dict[str, Any]) -> datetime:
    """Calendar API 的 start/end 是 dict 結構：{'dateTime': '...', 'timeZone': '...'}"""
    dt_str = raw.get("dateTime") or raw.get("date")
    if not dt_str:
        raise ValueError(f"事件缺少 dateTime/date 欄位: {raw}")
    if "T" in dt_str:
        # dateTime 含時區或 Z
        if dt_str.endswith("Z"):
            dt_str = dt_str[:-1] + "+00:00"
        return datetime.fromisoformat(dt_str)
    # all-day 事件用 date（這版簡化不支援，但避免崩潰）
    d = datetime.fromisoformat(dt_str).replace(tzinfo=timezone.utc)
    return d


def _extract_meet_link(entry: list[dict[str, Any]] | None) -> str | None:
    if not entry:
        return None
    for e in entry:
        if e.get("entryPointType") == "video" and e.get("uri", "").startswith("https://meet.google.com/"):
            return e["uri"]
    return None


def _event_from_api(raw: dict[str, Any]) -> CalendarEvent:
    return CalendarEvent(
        id=raw["id"],
        summary=raw.get("summary", "(無標題)"),
        start=_parse_event_datetime(raw["start"]),
        end=_parse_event_datetime(raw["end"]),
        location=raw.get("location"),
        description=raw.get("description"),
        meet_link=_extract_meet_link(raw.get("conferenceData", {}).get("entryPoint") if raw.get("conferenceData") else raw.get("conferenceData")),
        html_link=raw.get("htmlLink"),
    )


def get_calendar_service(token: dict[str, Any]):
    """建一個 googleapiclient service 物件，token 由呼叫端控管。"""
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build

    creds = Credentials(
        token=token["access_token"],
        refresh_token=token.get("refresh_token"),
        token_uri=OAUTH_TOKEN_URL,
        client_id=token.get("_client_id"),
        client_secret=token.get("_client_secret"),
        scopes=token.get("_scopes", "").split() if token.get("_scopes") else None,
    )
    return build("calendar", "v3", credentials=creds, cache_discovery=False)


def list_upcoming_events(token: dict[str, Any], minutes_ahead: int = 10,
                         calendar_id: str = "primary") -> list[CalendarEvent]:
    """列出從現在起 `minutes_ahead` 分鐘內即將開始的事件。"""
    from googleapiclient.errors import HttpError

    service = get_calendar_service(token)
    now = datetime.now(timezone.utc)
    time_max = datetime.fromtimestamp(now.timestamp() + minutes_ahead * 60, tz=timezone.utc)
    try:
        result = service.events().list(
            calendarId=calendar_id,
            timeMin=now.isoformat(),
            timeMax=time_max.isoformat(),
            maxResults=20,
            singleEvents=True,
            orderBy="startTime",
        ).execute()
    except HttpError as e:
        # 401 = token 過期；上層該 refresh
        if e.resp.status == 401:
            raise PermissionError("Calendar API 401，token 過期") from e
        raise

    events = [_event_from_api(item) for item in result.get("items", [])]
    return events


def create_quick_event(token: dict[str, Any], text: str,
                       calendar_id: str = "primary") -> CalendarEvent:
    """用自然語言一句話建立事件（"明天 3 點 跟 John 開會"）。"""
    from googleapiclient.errors import HttpError

    service = get_calendar_service(token)
    try:
        result = service.events().quickAdd(
            calendarId=calendar_id, text=text,
        ).execute()
    except HttpError as e:
        raise RuntimeError(f"quickAdd 失敗: {e}") from e
    return _event_from_api(result)


def reschedule_event(token: dict[str, Any], event_id: str,
                     new_start: datetime, duration_minutes: int,
                     calendar_id: str = "primary") -> CalendarEvent:
    """把事件改到 new_start 並維持原 duration（或用傳入的覆蓋）。"""
    from googleapiclient.errors import HttpError

    service = get_calendar_service(token)
    new_end = datetime.fromtimestamp(new_start.timestamp() + duration_minutes * 60, tz=new_start.tzinfo)
    patch_body = {
        "start": {"dateTime": new_start.isoformat()},
        "end": {"dateTime": new_end.isoformat()},
    }
    try:
        result = service.events().patch(
            calendarId=calendar_id, eventId=event_id, body=patch_body,
        ).execute()
    except HttpError as e:
        raise RuntimeError(f"patch 失敗: {e}") from e
    return _event_from_api(result)
