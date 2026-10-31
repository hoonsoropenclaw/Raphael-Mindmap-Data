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


---

# 2026-10-31 — 方法增量修訂（Q1 宣告綁定 / Q2 裁決權歸屬 / Q4 權限三維）

> 本段是 2026-10-31 的實測紀錄。**上面 day 1–3 的數字是當時的實測值，保留不覆寫**；
> 本段的數字一律由 `scripts/run_all.sh` 產出後回算，不手抄。

## 為什麼做這件事

在 2026-10-10 既有資產（proj-20261008…）上做**方法增量**，不是重做。
今日命題來自 plan 階段的實測發現：

1. `plan.curriculum_frontier` 3 條**全是假陽性** —— 課綱 5 條對應既有卡 5 條全命中，
   但 frontier 說「沒學過」。照 frontier 選題會重學 3 條（違反鐵則 2）。
2. `plan.practice.scenario_hint` 指向的題目 **2026-10-10 就已完成**，plan 卻仍提示。

兩者共同病根：**宣告欄位與實測事實之間沒有綁定機制** → 今日 Q1 命題。

## 本次做了什麼

| # | 項目 | 檔案 |
|---|------|------|
| Q1 | 宣告與實測綁定閘門 | `gates/gate_claim_binding.py` |
| Q2 | 閘門裁決權外部化 | `gates/gate_external_threshold.py` + `fixtures/thresholds.json` |
| Q4 | 權限三維（可見性 × 可操作性 × 範圍） | `server/permissions.py`、`src/permissions/model.ts`、`src/permissions/masking.ts` |
| — | 後端授權邊界 | `server/app.py`（Actor 解析、可見流程過濾、PUT／transition 分離、401/403/404） |
| — | 授權對抗探針 | `scripts/probe_authz.sh`（34 案例，四欄格式：輸入 → 預期 → 實際 → 一致？） |
| — | 一鍵交付閘門 | `scripts/run_all.sh` |

## 評審後的修補歷程（這是本日的真正價值）

### 第一輪自評（self 50.0）與跨模型評審（judge 28.8，DeepSeek）都未過門檻 75

兩輪評審各自抓到的最高嚴重度缺陷都指向同一個根因：**hydrate 沒帶身分 → 前端 PUT 覆蓋伺服器資料**。

- 實測證據：伺服器端塞 7 個節點（含 `SERVER-ONLY-*` 標籤），**只開頁面不做任何操作**，
  伺服器端只剩 1,2,3,4 —— `SERVER-ONLY` 標籤全部消失、已核准狀態回到「待審」。
- 根因：React effect 執行順序是**子先於父**。`FlowEditor` 的 hydrate effect 是
  `AuthProvider` 的子 effect，所以它比 `setRequestIdentity()` 先跑 → 當下身分還是 null →
  GET 送出無身分請求 → 後端回 not-found → 前端當成「流程是空的」→ 保留寫死的 4 個預設節點
  → 400ms 後 debounced PUT 把伺服器真實資料覆蓋掉。
- 修法（三件一起做，缺一不可）：(a) hydrate effect 依賴 `user`，`user` 為 null 時不發請求；
  (b) hydrate 失敗時設 `hydrateFailed` → **禁止後續 PUT**；(c) 後端把 no-identity 與 not-found
  分成 401 / 404，前端遇到 no-identity 一律不得 PUT。
- 補一支對抗性 e2e 鎖住這條路徑（`opening the page must not overwrite server-side data`）。

### 第二輪修補時**真的跑出來的三個接線 bug**

這三個都是「閘門寫好了但接線沒接起來」，且**只有真的跑整套流程才會現形**：

1. **埠號衝突被偽裝成綠燈**（`run_all.sh`）
   埠 8000 被上一次 run 留下的 uvicorn 占用 → uvicorn 綁埠失敗立即退出 →
   腳本卻仍對 `/health` 送 curl → 拿到 200 → `READY=1` → **所有檢查都打在別的行程上**。
   與 `playwright.config.ts` 修掉的 `reuseExistingServer` 是同一族缺陷。
   修法：啟動前先確認埠是空的；被占用 → exit 2（環境錯誤），**不沿用**既有服務。
   另外把預設埠從 8000 → 8010、4173 → 4180（4173 被本機另一個長駐專案永久占用）。

2. **探針輸出缺 metric 欄位**
   `fixtures/thresholds.json` 宣告 `authz_probe` 的 metric 是 `inconsistent_count`，
   但 `probe_authz.sh` 只輸出 `consistent_count` → 外部裁決回 `status=error`（exit 2）。
   修法：兩個欄位都輸出（數值相同、不互相矛盾）。

3. **`BASE` 沒 export → python heredoc 讀不到**
   `NameError: name 'BASE' is not defined` → 探針輸出是空 → 外部裁決 rc=2。
   修法：`export BASE`，python 端用 `os.environ["BASE"]` 讀。

修完之後**還有一層隱藏的真相被揭開**：上面三個 bug 讓「所有檢查都打在別的行程上」，
所以第一輪看到的「e2e 2 failed、unit 全綠」其實**不是真實狀態**。
埠號守衛修好、檢查打到正確行程後，真實狀態才浮現 —— 而真實狀態比第一輪報告的**更好**
（e2e 6/6 全過、unit 82/82、probe 34/34）。

### 連帶修掉的三個 harness 層根因（Q1 閘門抓出來的真 bug）

`gate_claim_binding.py` 報 `issues=4` 不是閘門壞掉，是**閘門抓到了真的問題**：

1. `harness/knowledge.py` 的 `check_novelty` 只用字元 bigram **Jaccard**，
   而 Jaccard **同時懲罰長度差異** → 課綱短語 vs 卡片長標題被壓低
   （實測 `similarity('表單驗證（schema 驅動）', 'Schema-driven 表單驗證：React Hook Form + Zod') = 0.235`，
   遠低於 `dup_threshold` 0.62 → 判成 novel）。
   修法：加 `containment`（短字串被涵蓋的比例）與 `token_containment`（詞元化，中英混排不切跨詞碎片），
   分數改為 `max(jaccard, containment×0.85, token_containment×0.9)`。
   **回歸實測：87 張卡自我檢查全部維持 duplicate（0 回歸）；負向測試
   （WebGPU 算子管線調優 / IndexedDB 交易隔離層級）仍為 novel。**

2. `harness/runs.py` 的 `practice.scenario_hint` **無條件取 `practice_scenarios[0]`**，
   不檢查歷史 → 一直提示已完成題目。
   修法：`_pick_scenario()` 用詞彙重疊比對既有完成專案，跳過重疊 ≥ 0.34 的場景；
   全部重疊時回 `None` + 說明「不應重做，請開新專案」，並把判斷依據寫進
   `practice.scenario_selection_note`（欄位不是黑箱產生的）。

3. `gate_claim_binding` 本身驗證了 `plan.json` 的 `frontier` 與 `scenario_hint`
   都與實測事實綁定 —— 這就是 Q1 的機制本身。

## 實測結果（數字由 `scripts/run_all.sh` 產出後回算）

```json
{
  "unit_tests":           { "passed": 82, "test_files": 6, "exit_code": 0 },
  "authz_probe":          { "total": 34, "consistent_count": 34, "inconsistent_count": 0, "exit_code": 0 },
  "gate_claim_binding":   { "ok": true, "issues": 0, "exit_code": 0 },
  "e2e":                  { "passed": 6, "exit_code": 0 },
  "external_threshold":   { "ok": true, "passed": 2, "failed": 0, "errors": 0, "exit_code": 0 }
}
```

**交付閘門總裁決：通過（全部檢查 exit=0）**

### 重跑驗證 stamp（2026-10-31 最終）

```
bash scripts/run_all.sh
  → unit_tests            exit=0   82 passed / 6 files
  → authz_probe           exit=0   34/34 一致
  → gate_claim_binding    exit=0   ok=true issues=0
  → e2e                   exit=0   6 passed
  → external_threshold    exit=0   2 subjects 全過
  → 交付閘門：通過
```

## 適用邊界與未解事項（明文揭露）

- **X-Demo-Role / X-Demo-User-Id 是示範機制，不是認證**，標頭可被偽造；
  真實系統必須換成已驗證的 session / JWT。
- 本系統為練習用示範資料，非使用者機關實際資料。
- SQLite 單檔 + WAL + busy_timeout；跨機部署需換 Postgres（未解）。
- **Windows 未實測**：README 的 Windows 段落是依 Unix 實測結果推導，不是 Windows 實測結果。
- **SQLite 併發寫入未實測**：busy_timeout 有設但沒有併發壓力測試；
  目前定位為單使用者示範，不支援併發寫入。
- 閘門 2 的門檻檔與 checker 輸出檔已納入交付集合（`fixtures/thresholds.json`、
  `fixtures/checker_output_pass.json`、`fixtures/checker_output_fail.json`），
  可獨立重跑；`run_all.sh` 會產生當次實際的 checker 輸出。
