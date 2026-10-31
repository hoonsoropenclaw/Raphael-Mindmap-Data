# 人事案件簽核流程編輯器

> 一個 RBAC（角色權限）正確的 Web App：用 React Flow 拖拉編輯簽核流程，FastAPI + SQLite 做真後端持久化。
> Day-3 完成重新整理資料仍在；2026-10-31 做方法增量修訂（權限三維 + 兩支綁定閘門 + 對抗性 e2e）。

## 功能

- **React Flow 編輯器**：拖拉新增節點、連線、刪除流程
- **5 個角色 × 7 種權限** 的細粒度 RBAC：
  - `employee`：讀 / 建立 / 提交
  - `manager`、`director`：讀 / 建立 / 編輯 / 提交 / 核准
  - `principal`：唯讀 / 核准
  - `admin`：全部 + 使用者管理
- **節點狀態機**：`pending` → `approved` / `rejected`，含 audit（誰、何時）
- **真後端持久化**：FastAPI + SQLite，每個節點動作都 debounce 寫入 DB
- **權限三維表達（2026-10-31 新增）**：可見性 × 可操作性 × 範圍
  - 可見性：看不到的節點連框都不渲染，連邊也一併過濾（不洩漏「有一個你看不到的關卡」）
  - 可操作性：看得到但不可操作 → 節點照常渲染，沒有核准／駁回按鈕
  - 範圍：`own`（擁有者）／`department`（同部門）／`all`
- **後端授權邊界（2026-10-31 新增）**：授權從「前端 mock」搬到後端
  - `X-Demo-Role` / `X-Demo-User-Id` 解析出 Actor
  - 流程清單只回傳可見流程（不揭露不可見流程的**存在性**）
  - PUT（改流程圖結構）與 transition（改節點狀態）**分離**，狀態與稽核軌跡由伺服器擁有
- **兩支綁定閘門（2026-10-31 新增）**：
  - `gates/gate_claim_binding.py` — Q1：計畫欄位（frontier / scenario_hint）必須由實測核對
  - `gates/gate_external_threshold.py` — Q2：通過門檻只能由**外部檔案**定義，被檢物不得自訂
- **對抗性 e2e（2026-10-31 新增）**：`opening the page must not overwrite server-side data`
  —— 伺服器塞 7 個節點 → 只開頁面不操作 → 斷言伺服器端節點數與標籤完全不變

## 快速開始

需要 Node 18+、Python 3.10+、FastAPI / uvicorn / pydantic（pip install fastapi uvicorn pydantic）。

### 1. 安裝前端依賴

```bash
npm install --no-audit --no-fund
```

### 2. 一鍵跑完所有檢查（**推薦**）

```bash
bash scripts/run_all.sh
```

這支腳本會依序跑 unit tests → 授權對抗探針 → 綁定閘門 → e2e → 外部裁決，
任一支 exit≠0 就整體 exit≠0（**交付被擋住**）。門檻值全部從 `fixtures/thresholds.json` 讀，
腳本本身不內嵌任何門檻常數。

### 3. 手動啟動（開發用）

```bash
# 後端（預設 :8010，可用 API_PORT 覆寫）
python3 -m uvicorn server.app:app --port 8010

# 前端（預設 :4180，可用 E2E_PORT 覆寫）
npm run preview
```

打開 http://localhost:4180 ，用 `?as=manager` / `?as=principal` / `?as=employee` 直接以指定角色登入。

DB 會自動建立在 `./data/flows.sqlite3`。

> ⚠️ **埠號守衛**：`run_all.sh` 啟動前會先確認後端埠是空的。
> 埠被占用時直接 exit 2（環境錯誤），**不會**沿用既有服務——
> 否則所有檢查會打在別的行程上，得到「綠燈但沒測到東西」的假結果。
> 這與 `playwright.config.ts` 的 `reuseExistingServer: false` 是同一個設計原則。

### 4. 跑測試

```bash
# Unit + integration（需要後端在 API_PORT，預設 :8010）
npx vitest run

# E2E（會自動啟動 preview server）
npx playwright install chromium   # 第一次才需要
npx playwright test
```

## 專案結構

```
src/
  App.tsx                   SPA 殼 + 路由
  main.tsx                  entry
  auth/AuthContext.tsx      角色登入（?as=role URL 參數）
  permissions/
    model.ts                權限三維模型（純函式）
    masking.ts              欄位層遮蔽（masking）
    Can.tsx                 UI 級權限 gate
    ProtectedRoute.tsx      路由級權限 gate
  flow/
    FlowEditor.tsx          主編輯器（useNodesState / useEdgesState / debounced save）
    ApprovalNode.tsx        自訂節點（含 audit badge / 核准駁回按鈕）
    types.ts
  server/
    apiClient.ts            fetch 包裝，自動打 /api
    api.ts                  legacy mock（給 src/server/api 邊界測試用）
server/
  app.py                    FastAPI + SQLite 真後端（含授權邊界）
  permissions.py            三維授權守門（server 端）
gates/
  gate_claim_binding.py     Q1 綁定閘門
  gate_external_threshold.py Q2 外部裁決閘門
scripts/
  run_all.sh                一鍵交付閘門（exit code 收斂）
  probe_authz.sh            授權對抗探針（34 筆四欄格式案例）
  check_backend_env.py      後端套件環境檢查
fixtures/
  thresholds.json           唯一的門檻來源
  cards.json / projects.json / plan_today.json  綁定閘門的輸入
tests/
  permissions.test.ts        權限模型測試
  can-component.test.tsx     <Can> 元件測試
  server-api.test.ts         server-side re-check 邊界測試
  edge-style.test.ts         edge 顏色/方向測試
  api-client.test.ts         FastAPI 整合測試（需要後端）
  permission_matrix.test.ts  三維授權矩陣測試
  e2e/
    _helpers.ts              resetFlow()、FLOWS_AS()
    approval-flow.spec.ts    3 條原始 e2e
    persistence.spec.ts      2 條 day-3 持久化 e2e + 1 條對抗性 e2e
docs/                       各 day 的截圖與截圖分析
```

## 實測結果（2026-10-31，數字由 scripts/run_all.sh 產出，不手抄）

| 檢查 | 結果 | exit |
|------|------|------|
| `unit_tests` | 82 passed / 6 test files | 0 |
| `authz_probe` | 34 案例，34 一致，0 不一致 | 0 |
| `gate_claim_binding` | ok=true，issues=0 | 0 |
| `e2e` | 6 passed | 0 |
| `external_threshold` | 2 subjects 全過，0 failed，0 errors | 0 |
| **交付閘門總裁決** | **通過（全部 exit=0）** | **0** |

重跑方式：`bash scripts/run_all.sh`（輸出在 `/tmp/run_all_*.log`）

## 適用邊界（務必揭露）

- **X-Demo-Role / X-Demo-User-Id 是示範機制，不是認證。** 標頭由用戶端提供、可被偽造。
  真實系統必須換成已驗證的 session / JWT。本限制在 README 與 `server/app.py` docstring 有明文揭露。
- 本系統為練習用示範資料，非使用者機關實際資料。
- SQLite 單檔 + WAL + busy_timeout，跨機部署需換 Postgres（未解）。
- 本次實測平台是 Linux；Windows 段落未實測（見下方「已知限制」）。

## 已知限制

- 沒有真實認證（OAuth / session），AuthContext 從 URL `?as=` 模擬登入
- 沒有 migration 工具，schema 改動要 `rm data/flows.sqlite3`
- 沒有 audit log 完整介面（節點 `actedBy` 有寫但 UI 沒彙總頁）
- 一個 demo flow id（`flow-default`），沒有 flow 列表頁 / 路由
- **未在 Windows 上實測**：README 的命令是 Unix 形式。Windows 需改用
  `py -m uvicorn ... --port 8010`、`.venv\Scripts\python.exe`、背景執行用 `Start-Process`。
  實測平台揭露原則：Windows 段落是**依 Unix 實測結果推導**的，不是 Windows 實測結果。
- **SQLite 併發寫入未實測**：busy_timeout 有設但沒有併發壓力測試。
  目前定位為單使用者示範，不支援併發寫入。
