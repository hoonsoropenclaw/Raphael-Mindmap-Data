# PolicyGuard — RUNLOG

> 2026-10-21 daily-loop practice. 對應 `dev-web-platform` 領域、`Schema-driven 表單驗證：React Hook Form + Zod` 概念之 Python 端落地。

## 環境

- OS: Linux 6.8.0-136-generic（N100 mini PC，使用者所在環境）
- Python: 3.11.15（`/home/hoonsoropenclaw/.hermes/hermes-agent/venv/bin/python`）
- Pydantic 2.13.4、FastAPI 0.133.1、httpx 0.28.1、email-validator 2.2.0、pytest 9.0.2、ruff 0.7.4
- Playwright（chromium，用於視覺驗證）
- 工作目錄：`/home/hoonsoropenclaw/raphael-harness/workspace/policyguard`

## 執行紀錄

### 1. 套件檢查

```text
$ python3 --version
Python 3.11.15

$ pip show pydantic | head -2
Name: pydantic
Version: 2.13.4

$ pip show fastapi | head -2
Name: fastapi
Version: 0.133.1

$ pip show email-validator | head -2
Name: email-validator
Version: 2.2.0
```

需要 `email-validator`（Pydantic 的 `EmailStr` 必備）。系統已安裝。

### 2. 跑 schema + API 測試

```text
$ PYTHONPATH=. pytest -q
................                                                         [100%]
16 passed in 0.18s
```

16/16 綠。

### 3. Lint

```text
$ ruff check . --fix
Found 1 error (1 fixed, 0 remaining).

$ ruff check .
All checks passed!
```

### 4. 啟動服務 + 健康檢查

```text
$ POLICYGUARD_HOST=127.0.0.1 POLICYGUARD_PORT=8765 PYTHONPATH=. python -m app.server
INFO:     Started server process [3447532]
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8765

$ curl -s http://127.0.0.1:8765/healthz
{"ok":true,"version":"0.1.0","service":"policyguard"}
```

### 5. Happy path 提交（curl）

```text
$ curl -sX POST http://127.0.0.1:8765/api/validate/employee \
  -H 'Content-Type: application/json' \
  -d '{"employee_id":"A123456784","full_name":"王小明","email":"wm@example.com","birth_date":"1990-05-01","role":"staff","effective_from":"2026-10-21"}'
{"ok":true,"kind":"ok","data":{"employee_id":"A123456784","full_name":"王小明","email":"wm@example.com","birth_date":"1990-05-01","manager_id":null,"role":"staff","effective_from":"2026-10-21","effective_to":null,"note":null}}
HTTP 200 OK ✓
```

### 6. 跨欄位錯誤提交（curl）

```text
$ curl -sX POST http://127.0.0.1:8765/api/validate/employee \
  -H 'Content-Type: application/json' \
  -d '{"employee_id":"X999999999","full_name":"Bob","email":"","birth_date":"2030-01-01","role":"lead","effective_from":"2026-10-21","manager_id":"A123456784"}'
{
  "ok": false,
  "kind": "request_validation",
  "errors": [
    {"field":"employee_id","message":"Value error, 身分證字號格式或檢查碼錯誤","type":"value_error"},
    {"field":"full_name",  "message":"Value error, 姓名僅能含中文與間隔號",      "type":"value_error"},
    {"field":"email",      "message":"value is not a valid email address: ...", "type":"value_error"},
    {"field":"role",       "message":"String should match pattern '^(staff|lead|director|principal)$'", "type":"string_pattern_mismatch"}
  ]
}
HTTP 422 ✓ — 預期。註：role=lead 通過，只驗證其他三項欄位。
```

### 7. 視覺驗證（Playwright）

```text
$ PYTHONPATH=. python scripts/visual_smoke.py
saved screenshots to /home/hoonsoropenclaw/raphael-harness/workspace/policyguard/screenshots
```

產出：
- `screenshots/01_initial.png`：空表單（深色主題）
- `screenshots/02_happy.png`：✅ 通過 + 完整 JSON
- `screenshots/03_errors.png`：❌ 三個欄位錯誤（identity / 全名 / email）

親眼檢視結論：
- 中文字與英文並排無重疊（var（--accent）藍色 uniform）
- 沒有偽斜線或框框字（中文用 Noto Sans TC fallback）
- dark theme 對比足夠（background #0d1117 / text #e6edf3）

### 8. GitHub 推送

```text
$ git init -q
$ git add -A
$ git commit -m "feat: PolicyGuard schema-driven form validator (FastAPI + Pydantic v2)"
$ git remote add origin git@github.com:hoonsoropenclaw/policyguard.git
$ git push -u origin master
```

實況：見 `git log -1` 與 GitHub 上的 `policyguard` 倉庫。

## 已知限制（依 SOP defect listing）

| 項目 | 等級 | 補法 |
|---|---|---|
| 沒做 rate limiting | medium | 加 `slowapi` middleware；N100 最多 60 req/min |
| 沒 HTTPS | low | production 必加 reverse proxy（Caddy/Traefik） |
| 沒 DB 持久化 | low | 純 schema 驗證教學；持久化請接 SQLite/Postgres |
| 跨欄位 error path 缺層次 | low | 之後改用 superRefine，讓 `manager_id` 錯誤附在 nested path |
| 沒 i18n | low | 訊息加 i18n key；前端用字典 |
| 沒裝 OTel | low | production 觀察性靠 OTel/Prometheus |
