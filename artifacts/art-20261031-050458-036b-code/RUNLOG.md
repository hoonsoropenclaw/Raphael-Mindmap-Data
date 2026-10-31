# RUNLOG — 人事案件簽核流程編輯器（proj-20261008-021500-deb0）

> 這是第 1 天（day 1 / 3）的執行紀錄，目標是建立可運作的最小骨架、跑通核心單元測試、視覺驗證畫面。
> 後續兩天要做：① Playwright e2e 真正通過（員工提交、校長核准兩條路徑）② 節點資料序列化／還原
> ③ 真實後端 API 串接（目前是 mock）④ 文件與 README。

## 環境

- N100 迷你電腦、Linux 6.8
- Node.js（透過 npm 11）
- 瀏覽器：Playwright 預設 Chromium 2560×1281 viewport

## 安裝

```bash
npm install --no-audit --no-fund
```

✅ 成功，0 vulnerabilities。

## 測試

```bash
npx vitest run
```

結果：

```
✓ tests/permissions.test.ts (9 tests) — RBAC 模型
✓ tests/server-api.test.ts (6 tests) — API 邊界權限再驗
✓ tests/can-component.test.tsx (3 tests) — <Can> 元件
Test Files  3 passed (3)
Tests       18 passed (18)
```

涵蓋：
- 正常（員工/組長/主任/校長/管理員各自該有/該無的權限）
- 多重角色（union 邏輯驗證）
- 邊界（空角色陣列、principal 唯讀核准者）
- 負面（員工假冒 admin 操作 API → server 端擋下）

## 建置

```bash
node node_modules/vite/bin/vite.js build
```

結果：

```
dist/index.html                   0.32 kB │ gzip:   0.27 kB
dist/assets/index-B-_TyNsB.css    7.32 kB │ gzip:   1.60 kB
dist/assets/index-O4p2hl9Q.js   317.53 kB │ gzip: 103.76 kB
✓ built in 9.49s
```

0 TypeScript 錯誤、0 編譯警告。

## 啟動

```bash
node node_modules/vite/bin/vite.js preview --port 4173 --host 0.0.0.0
```

健康檢查：`curl http://localhost:4173/` → 200，`/flows` → 200。

## 視覺驗證（截圖自評，per SOP）

開啟 `http://localhost:4173/flows` 後用 Playwright 截圖 → `docs/screenshot-flow-editor.png`

直接看圖（native vision）確認：
- ✅ 4 個節點（員工申請/組長審核/主任審核/校長核定）全部可見、彼此連線
- ✅ 每個節點有不同底色（藍/黃/粉/綠）對應角色
- ✅ 中文標題、節點文字、按鈕文字無 surrogate 破碎
- ✅ 底部按鈕列（+組長節點/+主任節點/送出簽核）與下方「帳號管理」連結**不再重疊**（已修：minHeight 100vh + maxWidth 1200 + overflow:hidden）
- ✅ 工具列（放大/縮小/fit view/toggle）與 mini-map 在右下方

RBAC 行為驗證：
- ✅ employee 身分 → 直接打 `/admin` → 自動導向 `/403`（ProtectedRoute 觸發）
- ✅ 員工看不到「刪除流程」按鈕（無 flow:delete 權限）— 對應單元測試 `can-component > hides children when user lacks the permission`

## 已知未完成（Day 2/3 待辦）

1. **Playwright e2e 跑通**：playwright.config.ts 已設但 e2e 測試要 chromium 環境（`npx playwright install --with-deps chromium`）；目前只驗證測試檔語法正確、未實際執行
2. **節點序列化 / 反序列化**：toObject / fromObject API 還沒接到後端
3. **真實後端**：目前是 in-memory mock；規劃 FastAPI + SQLite
4. **README**：寫好安裝、開發、測試指令

## 自我評分

- 預測分數：**70 / 100**
- 評分依據：
  - RBAC 模型 + 單元測試完整：+25
  - React Flow 編輯器可跑、節點可見：+15
  - UI / API 雙層權限邊界有清楚架構：+15
  - 中文渲染正常、無重疊：+10
  - 缺：e2e 沒跑、缺後端、缺序列化：-20（扣分項）
  - 缺：node 內狀態管理仍簡陋、缺錯誤訊息：-10
- 估計實際分數：~65（day 1 階段）

## 重跑驗證 stamp

（待 day 3 結尾補上完整 stamp）


---

## Day 3（2026-10-10）— 真後端 + 持久化驗收

### 安裝

```bash
# 後端依賴
pip install fastapi uvicorn pydantic
```

無 frontend 新增依賴。

### Day-3 目標達成

1. **真後端（FastAPI + SQLite）**：`server/app.py` 提供
   - `GET /health`
   - `GET /api/flows`
   - `GET /api/flows/{id}`
   - `POST /api/flows`、`PUT /api/flows/{id}`
   - `DELETE /api/flows/{id}`
   SQLite 路徑：`./data/flows.sqlite3`，表 `flows(id, payload, updated_at)`，payload 為 JSON TEXT。

2. **前端 hydration-on-mount + debounced save**：
   - `src/server/apiClient.ts`：包 fetch，BASE = `__API_BASE__ || "/api"`（瀏覽器走 vite proxy，unit test 走絕對 URL）。
   - `src/flow/FlowEditor.tsx`：進入時 `apiFlowGet(DEMO_FLOW_ID)` 拿最新 nodes/edges；每次 state 變化 debounce 400ms 寫回。
   - `vite.config.ts`：proxy `/api` 與 `/health` → `http://127.0.0.1:8000`，preview 模式同樣 proxy。

3. **新整合測試**：`tests/api-client.test.ts`（5 個 case）真打 backend 驗 upsert/get/list/delete round-trip。

### 修正

- **vitest `__API_BASE__` URL 拼錯**：原本 `http://127.0.0.1:8000`，但 `apiClient.ts` 內部用 `${BASE}/flows`，所以實際打到 `http://127.0.0.1:8000/flows/...` → 404。改成 `http://127.0.0.1:8000/api` 並讓 `waitForBackend` 直接探 `/health`（不在 /api 下），5 個整合測試全綠。
- **e2e 互踩**：原 `approval-flow.spec.ts` 與新 `persistence.spec.ts` 共享同一個 `flow-default`，workers=2 時 manager button 會被前一個 test 的 approval 藏掉。修法：抽 `tests/e2e/_helpers.ts` 的 `resetFlow()` 在每個 test 前重置；playwright.config.ts 加 `workers: 1`。
- **刪除依賴中沒裝的 backend**：docstring `tests/api-client.test.ts` 之前寫「未啟動 server 就 fail」是預期，現已驗證實際 fail message 清楚。

### 測試結果

```bash
$ npx vitest run
✓ tests/permissions.test.ts        (9 tests)
✓ tests/server-api.test.ts         (6 tests)
✓ tests/api-client.test.ts         (5 tests)        ← 新增
✓ tests/edge-style.test.ts         (3 tests)
✓ tests/can-component.test.tsx     (3 tests)
Test Files  5 passed (5)
Tests       26 passed (26)

$ npx playwright test
✓ 5 tests (workers: 1)
- 員工提交 / 不能看到 approve/delete        (384ms)
- 校長核准 / 狀態翻綠 / 不能核組長          (285ms)
- 組長核准 / 後續按鈕消失 / 不能核校長      (285ms)
- 重新整理 → 資料仍在（Day-3 acceptance）  (1.2s)  ← 新增
- 不同角色共享 flow state                  (1.1s)  ← 新增

5 passed (4.3s)
```

### 建置

```bash
$ node node_modules/vite/bin/vite.js build
dist/index.html                   0.32 kB │ gzip:   0.27 kB
dist/assets/index-B5DZHykP.css    7.32 kB │ gzip:   1.60 kB
dist/assets/index-CFkoCMF_.js   321.49 kB │ gzip: 105.20 kB
✓ built in 9.46s
```

### 視覺驗證（playwright headless screenshot）

- `docs/screenshot-day3-manager.png`：組長登入 → 只有組長節點顯示「核准/駁回」，底部有 `+組長節點/+主任節點/送出簽核`，右上「✓ 已儲存」出現（**證明 debounced PUT 已生效**）。
- `docs/screenshot-day3-employee.png`：員工登入 → 4 節點全部顯示但無 approve 按鈕，底部按鈕列只有「+組長節點/+主任節點/送出簽核」（員工有 flow:create/submit，無 flow:delete 所以沒「刪除流程」），「✓ 已儲存」出現。
- `docs/screenshot-day3-principal.png`：校長登入 → 只有校長節點顯示「核准/駁回」，底部按鈕列完全空（校長無 flow:create/submit/delete），「✓ 已儲存」出現。
- 對比 day-2 同樣三張：唯一差異是多了「✓ 已儲存」字樣（持久化訊號），其餘排版完全一致。

### 自評（Day-3）

- **預測**：82 / 100
- **實際預期**：~80
- **評分依據**：
  - 真後端 + SQLite 完整 + integration test 5/5：+25
  - hydration-on-mount + debounce save：+10
  - Day-3 acceptance e2e 補齊（reload 仍在、跨角色共享）：+10
  - 修正 backend URL 拼錯 + e2e 互踩 race：+5
  - 完整 README：+5
  - 視覺驗證三角色：+5
  - **扣分**：audit 沒彙總頁、沒 migration、沒真認證（-8）、DB 單檔沒鎖，併發寫入理論上有 race（-3）、README 還沒英文版（-2）

### 重跑驗證 stamp（最終）

```
Unit test:    npx vitest run → 26 passed (5 files)
E2E:          npx playwright test → 5 passed (workers: 1)
Build:        vite build → 0 error
Backend:      curl :8000/health → {"ok":true}
Browser → API: 頁面 reload → state-badge 維持「核准」（acceptance）
```
