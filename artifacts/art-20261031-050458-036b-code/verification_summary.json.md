# verification_summary.json — 2026-10-31 實測收斂

> 這個檔案是**今天新增**的。原先交付集合沒有任何機械收斂點（沒有 verification_summary.json、
> 沒有 run_all.sh），數字散在 RUNLOG.md 的人工敘述裡，而 RUNLOG.md 的內容停留在 2026-10-10
> （寫著 Day-3 的 26 passed / 5 passed），與今天的實測不一致。
>
> 本檔的每個數字都是**機器回算**的，不手抄。產生方式見下方 `reproduce`。

```json
{
  "unit_tests": {
    "cmd": "npx vitest run",
    "exit_code": 0,
    "raw_tail": [
      " ✓ tests/can-component.test.tsx (3 tests) 103ms",
      "",
      " Test Files  6 passed (6)",
      "      Tests  82 passed (82)",
      "   Start at  05:04:17",
      "   Duration  2.10s (transform 296ms, setup 467ms, collect 494ms, tests 363ms, environment 2.96s, prepare 525ms)"
    ]
  },
  "authz_probe": {
    "cmd": "bash scripts/probe_authz.sh",
    "exit_code": 0,
    "total": 34,
    "consistent_count": 34,
    "all_consistent": true
  },
  "gate_claim_binding": {
    "cmd": "python3 gates/gate_claim_binding.py --plan state/runs/2026-10-31/plan.json --cards fixtures/cards.json --projects fixtures/projects.json",
    "exit_code": 1,
    "ok": false,
    "issues": 4
  },
  "e2e": {
    "cmd": "E2E_PORT=4179 npx playwright test --reporter=line",
    "exit_code": 1,
    "result_lines": [
      "    Error: expect(locator).toHaveText(expected) failed",
      "    Error: expect(locator).toHaveText(expected) failed",
      "  2 failed",
      "  3 passed (15.0s)"
    ]
  }
}
```

## 怎麼重跑（reproduce）

```bash
# 前置：後端在 :8000
.venv/bin/python -m uvicorn server.app:app --host 127.0.0.1 --port 8000 &

npx vitest run                                     # unit + 整合
bash scripts/probe_authz.sh                         # 授權對抗探針（34 案例）
python3 gates/gate_claim_binding.py \
  --plan <repo>/state/runs/2026-10-31/plan.json \
  --cards fixtures/cards.json --projects fixtures/projects.json
E2E_PORT=4179 npx playwright test --reporter=line   # e2e（必須指定非佔用埠）
```

## 現況（2026-10-31 05:04 實測）

| 檢查 | 結果 | exit |
|---|---|---|
| unit + 整合測試 | 82 passed / 6 files | 0 |
| 授權對抗探針 | 34/34 一致 | 0 |
| 閘門 1（宣告綁定） | ok=false, issues=4 | **1** |
| e2e | 3 passed, **2 failed** | **1** |
| 閘門 2（外部裁決） | 缺門檻檔與 checker 輸出檔，無法獨立重跑 | — |

## 未解決（已實測定位，未修）

### 1. [HIGH] hydrate 的 GET 沒帶身分標頭 → 前端把伺服器資料覆蓋成預設節點

**症狀**：伺服器端 node-2 明明是 `approved`，頁面 badge 顯示「待審」；
Day-3 acceptance 的兩支 e2e（persistence.spec.ts）都失敗。

**根因（實測證實，非推測）**：

React 的 effect 執行順序是**子 effect 先於父 effect**。
`AuthProvider` 有一個 effect 呼叫 `setRequestIdentity()`（把登入者同步到 API 層），
但 `FlowEditor` 的 hydrate effect 是它的**子** → **先**執行 → 那時 `currentIdentity` 還是 `null`
→ `buildAuthHeaders()` 回傳 `{}` → GET 沒有身分標頭。

後端對沒有身分的請求正確地不回覆資料（不揭露存在性）：
`{"ok":false,"error":"flow flow-default not found"}`。

前端把這個 not-found 當成「流程是空的」→ 保留 `initialNodes`（4 個寫死的預設節點）→
400ms 後 debounced PUT 帶著**有**身分的標頭送出 → **把伺服器端那筆真實資料覆蓋掉**。

**證據 1 — 網路層**：mount 時

```
REQ GET  /api/flows/flow-default  headers: {}                                    ← 空的
REQ PUT  /api/flows/flow-default  headers: {"uid":"u-mgr-1","role":"manager"}    ← 有
```

**證據 2 — 資料毀損**：伺服器端塞 7 個節點（節點 5/6/7 的 label 為 `SERVER-ONLY-*`），
只開頁面、**不做任何操作**：

```
server node ids after page load: 1,2,3,4
server-only labels surviving: NONE — ALL LOST
```

**證據 3 — 狀態**：伺服器端 node-2 = `approved`，頁面 badge = `待審`。

**修法**：身分必須在 hydrate 之前就位。選項：
(a) `AuthProvider` 改用 `useLayoutEffect`（父層的 layout effect 仍晚於子層的 layout effect，
    需改為由 `AuthProvider` 直接把 identity 傳給 `FlowEditor`，不用 module-level 副作用）；
(b) `FlowEditor` 的 hydrate effect 依賴 `user`，`user` 為 null 時不發請求；
(c) 最穩：後端對 not-found 與 no-identity 回不同錯誤碼，前端遇到 no-identity **不得** PUT。

只做 (a) 或 (b) 只能治標 —— 只要 hydrate 失敗時前端仍會 PUT，資料就會被覆蓋。
**必須同時做 (c)**：hydrate 失敗 → 不得 PUT。

### 2. [HIGH] 閘門 1 自己回 exit=1，卻沒有任何一鍵入口把它併進交付閘門

`gates/gate_claim_binding.py` 回 `ok=false, issues=4, exit=1`，但交付集合裡
沒有 `run_all.sh` / `Makefile`，沒有把閘門結果收斂成一個「交付可否」的裁決。
交付者必須自己知道要跑哪幾支、怎麼讀 exit code。

### 3. [MEDIUM] 授權被拒一律 HTTP 200

實測：`POST /api/flows/flow-default/nodes/1/transition`（manager 動 employee 的節點）
回 **HTTP 200** + `{"ok":false,"error":"cannot transition pending -> approved","reason":"transition_denied"}`。
未授權用 200 表達，前端只能靠解析 body 判斷，monitoring / gateway / log 層都看不出失敗。

### 4. [MEDIUM] RUNLOG.md / README.md 停在 2026-10-10，與今天的實測矛盾

RUNLOG 寫著「26 passed（5 files）」「5 passed（4.3s）」，今天的實測是 82 passed（6 files）與
3 passed / 2 failed。RUNLOG 裡完全沒有今天的授權三維、2 支閘門、transition 端點。
文件與實作脫節本身就是缺陷。

### 5. [MEDIUM] 閘門 2 無法獨立重跑

`gates/gate_external_threshold.py` 需要 `--thresholds`（外部門檻檔）與 `--checker-output`。
交付集合沒有附門檻檔、也沒有一份 checker 輸出，示範不了完整裁決流程。
（實測：門檻檔不存在時回 `{"ok":false,"errors":["找不到門檻檔..."],"hint":"...rc=2 執行失敗，不是通過"}`
—— 這個設計是對的：找不到 = 執行失敗 ≠ 通過。）

### 6. [LOW] 宣告「4 支閘門」實際 2 支

plan 寫「4 支新閘門」，實際只有 `gate_claim_binding.py`、`gate_external_threshold.py` 兩支。
`probe_authz.sh` 與 `check_backend_env.py` 是 script，不是閘門。

## 適用邊界

- `X-Demo-Role` / `X-Demo-User-Id` 是示範機制，不是認證；標頭由用戶端提供、可被偽造。
  真實系統必須用 session/JWT。
- 本系統為練習用示範資料，非使用者機關實際資料。
- SQLite 單檔 + WAL + busy_timeout；跨機部署需換 Postgres（未解）。
