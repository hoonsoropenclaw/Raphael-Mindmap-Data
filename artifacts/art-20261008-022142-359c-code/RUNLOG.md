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
