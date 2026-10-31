# 人事案件簽核流程編輯器

> 一個 RBAC（角色權限）正確的 Web App：用 React Flow 拖拉編輯簽核流程，FastAPI + SQLite 做真後端持久化。Day-3 完成：重新整理頁面資料仍在。

## 功能

- **React Flow 編輯器**：拖拉新增節點、連線、刪除流程
- **5 個角色 × 7 種權限** 的細粒度 RBAC：
  - `employee`：讀 / 建立 / 提交
  - `manager`、`director`：讀 / 建立 / 編輯 / 提交 / 核准
  - `principal`：唯讀 / 核准
  - `admin`：全部 + 使用者管理
- **節點狀態機**：`pending` → `approved` / `rejected`，含 audit（誰、何時）
- **真後端持久化**：FastAPI + SQLite，每個節點動作都 debounce 寫入 DB
- **Playwright e2e 涵蓋三條路徑**：員工提交、校長核准、組長核准
- **Day-3 驗收 e2e**：核准後 reload，狀態仍在；不同角色共享同一份 flow state

## 快速開始

需要 Node 18+、Python 3.10+、FastAPI / uvicorn / pydantic（pip install fastapi uvicorn pydantic）。

### 1. 安裝前端依賴

```bash
npm install --no-audit --no-fund
```

### 2. 啟動後端（port 8000）

```bash
python3 -m uvicorn server.app:app --port 8000
```

DB 會自動建立在 `./data/flows.sqlite3`。

### 3. 啟動前端（port 4173）

```bash
npm run preview     # production build + preview (vite proxy /api → :8000)
# 或
npm run dev         # dev server
```

打開 http://localhost:4173 ，用 `?as=manager` / `?as=principal` / `?as=employee` 直接以指定角色登入。

### 4. 跑測試

```bash
# Unit + integration（需要 backend 在 :8000）
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
    model.ts                RBAC 模型（純函式）
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
  app.py                    FastAPI + SQLite 真後端
tests/
  permissions.test.ts        9 個 RBAC 模型測試
  can-component.test.tsx     <Can> 元件測試
  server-api.test.ts        server-side re-check 邊界測試（6 個）
  edge-style.test.ts        edge 顏色/方向測試
  api-client.test.ts        FastAPI 整合測試（5 個，需要 backend）
  e2e/
    _helpers.ts             resetFlow()、FLOWS_AS()
    approval-flow.spec.ts   3 條原始 e2e
    persistence.spec.ts     2 條 day-3 持久化 e2e（reload / 跨角色）
docs/                       各 day 的截圖與截圖分析
```

## Day 進度

| Day | 範圍 | 結果 |
|-----|------|------|
| 1 | 骨架：RBAC 模型 + Vitest 18/18 + Vite build + 視覺驗證 | ✅ |
| 2 | 節點內 核准/駁回 + 連線方向+狀態色 + Playwright e2e 跑通 | ✅ 21/21 + 3/3 |
| 3 | FastAPI + SQLite 真後端 + hydration-on-mount + 持久化驗收 | ✅ 26/26 + 5/5 |

## 已知限制

- 沒有真實認證（OAuth / session），AuthContext 從 URL `?as=` 模擬登入
- 沒有 migration 工具，schema 改動要 `rm data/flows.sqlite3`
- 沒有 audit log 完整介面（節點 `actedBy` 有寫但 UI 沒彙總頁）
- 一個 demo flow id（`flow-default`），沒有 flow 列表頁 / 路由
