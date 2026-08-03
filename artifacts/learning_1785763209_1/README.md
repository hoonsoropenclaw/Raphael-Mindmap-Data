# Google Calendar × Telegram 會議通知機器人

> 即時會議提醒系統：Google Calendar OAuth (Device Code Flow，不需瀏覽器) +
> APScheduler 排程掃描 + Telegram 推播 + inline keyboard 互動確認/延後/取消。

## 為什麼用 Device Code Flow？

N100 headless server 跑 OAuth 用 `InstalledAppFlow`（瀏覽器 loopback）會卡住。
**Device Code Flow** 是官方為 TV/limited-input 設計的：使用者在自己的電腦開
`google.com/device` 輸入 user_code，就能在 headless server 拿到 token。

**前置設定**：
1. Google Cloud Console → APIs & Services → Credentials
2. 建立 OAuth client，**類型必須選「TV 和 limited-input devices」**（選錯會 401）
3. Enable Google Calendar API
4. 把 client_id / client_secret 填到 `~/.local/share/hermes/secrets/calendar-bot.env`

## 快速啟動

```bash
# 1. 準備 secrets（**不要 commit**）
mkdir -p ~/.local/share/hermes/secrets
cp secrets.example.env ~/.local/share/hermes/secrets/calendar-bot.env
chmod 600 ~/.local/share/hermes/secrets/calendar-bot.env
$EDITOR ~/.local/share/hermes/secrets/calendar-bot.env
#   → 填入 GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET / TELEGRAM_BOT_TOKEN
#   → TELEGRAM_CHAT_ID 是你的 chat_id（先隨便填，第一次啟動時 /start 會回傳）

# 2. 安裝依賴
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3. 跑 bot（**首次會印 user_code**）
python3 bot.py
#   → 看到「請到 https://www.google.com/device 輸入 ABCD-1234」
#   → 用瀏覽器開那個網址，輸入代碼，登入授權
#   → 回 bot 看到「排程器啟動，每 30 秒掃一次」
#   → 用 Telegram 跟你的 bot 對話

# 4. 拿 chat_id
#   Telegram → /start → bot 回「你的 chat_id = 123456789」
#   把這個數字填回 calendar-bot.env 的 TELEGRAM_CHAT_ID，重啟 bot
```

## 檔案總覽

| 檔 | 角色 |
|----|------|
| `calendar_client.py` | Google Calendar 包裝層（OAuth + events.list/insert/patch/delete + quickAdd） |
| `bot.py` | Telegram bot 主程式（命令 + 推播 + inline keyboard） |
| `web_output.html` | 控制儀表板（時間軸 + 流程圖 + 互動 demo） |
| `requirements.txt` | Python 依賴 |
| `secrets.example.env` | 環境變數模板 |
| `test_oauth_flow.py` | Device Code Flow 單元測試（fake server 跑 polling 三個 error code） |
| `test_oauth_edge.py` | Device Code Flow 邊界測試（access_denied / expired_token） |
| `test_bot_imports.py` | bot.py import / handler routing 測試 |

## Telegram 互動流程

1. **APScheduler 每 30 秒** 掃「未來 5 分鐘內事件」
2. 沒提醒過 → **Telegram 推播**含 inline keyboard
3. 使用者三選一：
   - ✅ 確認 → 標記 notified（不再打擾）
   - ⏰ 延後 5 分 → patch 行事曆 + 5 分鐘後再推
   - ❌ 取消 → 從行事曆刪除

## 指令列表

| 指令 | 用途 |
|------|------|
| `/start` | 確認 bot 活著、回傳 chat_id |
| `/today` | 今天剩餘事件 |
| `/week` | 未來 7 天事件 |
| `/add 明天 3 點 跟 John 開會` | 自然語言建立事件（走 Calendar API quickAdd） |
| `/reschedule <event_id> 10` | 延後 10 分鐘 |
| `/whoami` | 顯示 chat_id / user_id |

## 部署到背景服務

```bash
# systemd unit 或 tmux
# 簡單做法：tmux
tmux new -d -s calendar-bot 'cd /path/to/this && source .venv/bin/activate && python3 bot.py'

# 開機自啟（crontab）
@reboot tmux new -d -s calendar-bot 'cd /path/to/this && source .venv/bin/activate && python3 bot.py'
```

## 已知限制

- **單行事曆**：目前只接 `primary` calendar。多人多帳號要改 `list_upcoming_events()` 接受 `calendar_id` 參數。
- **JSON state**：已提醒事件 ID 存 JSON（單人場景夠用）；>500 個事件自動 GC 舊的。
- **OAuth token 在磁碟**：`~/.local/share/hermes/secrets/google_calendar_token.json` (chmod 600)。
  若機器被入侵，攻擊者能 refresh 90 天到期的 refresh_token。**正式部署請改用 secrets manager**。

## 測試

```bash
# OAuth polling 三個 error code（authorization_pending / slow_down / access_denied）
python3 test_oauth_flow.py

# OAuth 邊界（access_denied / expired_token）
python3 test_oauth_edge.py

# bot handler routing（不真的打 Telegram）
python3 test_bot_imports.py
```
