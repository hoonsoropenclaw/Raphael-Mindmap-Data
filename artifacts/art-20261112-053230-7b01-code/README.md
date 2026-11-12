# 服務品質儀表板缺陷檢查工具（candidate：e2e-inc/e2e 框架）

與 baseline（Playwright 直接寫）**同一份** `after.html`、**同一份** 5 條檢查邏輯，
唯一變因＝測試框架（`e2e-inc/e2e`，Apache-2.0，vetted SHA=373588756937562aa89c7dd7f7995ac6b16db972）。

## 目標環境與實測狀態

| 項目 | 狀態 |
|---|---|
| 開發／驗證環境 | **Linux 6.8.0-136-generic（N100）、Node v22.22.3、e2e 0.23.0、@e2e-dev/web 0.15.5、Chromium 156.0.8078.4** |
| 目標環境 | Windows |
| **Windows 實機驗收** | **未在真實 Windows 實機驗收**。npm 於 Windows 的安裝差異、Chromium 於 Windows 的 headless 行為、框架在 Windows 的路徑處理皆未實測，本工具僅在 Linux/N100 實跑過。 |

## 前置條件

```bash
npm ci     # 有 package-lock.json，版本已鎖定（e2e 0.23.0 / @e2e-dev/web 0.15.5）
```

## 執行（三步）

```bash
# 1. 在本目錄啟動本機伺服器
python3 -m http.server 8932 --bind 127.0.0.1

# 2. 執行測試
npx e2e run

# 3. 看結果
cat .e2e/report.json
```

> 註：rev0 把 spec 交付在根目錄 `defects.e2e.ts`，但框架預設 glob 是
> `tests/**/*.e2e.ts`，直接跑會得到 `configuration error NO_TESTS (collection)`。
> **rev1 已把 spec 放到 `tests/defects.e2e.ts`，並在 `e2e.config.ts` 明確設定
> `tests: ['tests/**/*.e2e.ts']`，不需要手動搬檔。**

## 退出碼

| 碼 | 意義 |
|---|---|
| `0` | 所有測試的結果都符合預期（見下方「7 條測試的預期結果」） |
| `1` | 有測試的結果**不符合預期**（有缺陷漏抓，或對照組失效） |
| `2` | 設定／收集錯誤（例如找不到測試檔、埠沒開） |

## 7 條測試的預期結果（★ failed 的兩種語意）

框架的 `status` 只有 passed/failed，**但這裡 failed 有兩種相反語意**，
測試標題與 `EXPECTED_OUTCOME` 常數都標明了預期：

| ID | 預期 status | 預期 outcome | 意義 | 現況（after.html） |
|---|---|---|---|---|
| D1 | **failed** | `defect-already-fixed` | 缺陷早已修好，斷言 <4.5:1 不成立 → failed 是**正確** | 實測 10.77:1 |
| D2 | **failed** | `defect-already-fixed` | 缺陷早已修好，`referenced=true` → failed 是**正確** | 有 var() 引用 |
| D3 | passed | `defect-caught` | 死按鈕仍可重現 | before=596 after=596 |
| D4 | passed | `defect-caught` | 主題不持久仍可重現 | toggle=dark reload=light |
| D5 | passed | `defect-caught` | 側欄未響應式仍可重現 | sidebar=216 / win=360 |
| D6 | passed | `control-pass` | 對照組：頁面確實載入 | — |
| D7 | **failed** | `control-fail` | 對照組正確地失敗 → failed 是**正確** | wait 5.0s 後 give up |

★ 因此 **3 failed | 4 passed 是預期結果，exit code 1 也是預期結果**。
（rev0 的 report.json 沒有 expected-outcome 欄位，讀者只看到「3 個 failed」
會合理地誤以為有 3 個缺陷沒抓到；rev1 已在測試標題與 EXPECTED_OUTCOME 標明。）

## 產出的證據

| 路徑 | 內容 |
|---|---|
| `.e2e/report.json` | 機器可讀報告：逐測試狀態、逐步 api/status/duration、環境版本、run.summary |
| `.e2e/results/<test>/trace.md` | 人可讀的失敗步驟紀錄（錯誤訊息、逐步時間、Look at 行號） |
| `.e2e/results/<test>/attempt-1/screenshots/001-failure.png` | 失敗當下的畫面 |
| `.e2e/results/<test>/attempt-1/screen-at-failure.txt` | 失敗當下的無障礙樹（accessibility tree） |

> ★ rev0 的 `meta.notes` 宣稱交付了 screen-at-failure，但實際交付集合裡
> **一份都沒有**；rev1 已把 `.e2e/results/` 整棵樹納入交付。
>
> ★ 注意：D1／D2／D7 三個失敗的畫面目前是**同一張**（sha256 相同），
> 因為三場失敗發生在同一頁的同一狀態。rev0 把它複製成
> `attempt-1.png` 與 `attempt-1-001-failure.png` 兩個重複檔交付；
> rev1 依框架原生目錄結構交付，不再產生重複檔。

## 已知限制

1. **本工具只驗 5 條已列缺陷**；「5/7 符合預期」不代表頁面沒有其他缺陷。
   覆蓋率 = 已列項目數 ÷ 實際問題類型數，這個比率不會印在輸出上。
2. **Windows 未實測**（見上表）。
3. `e2e` 框架預設會收集匿名遙測（指令、版本、OS、執行摘要，不含測試名稱與資料）；
   需停用請執行 `npx e2e telemetry disable` 或設 `E2E_TELEMETRY_DISABLED=1`。
4. 失敗時框架會把畫面與無障礙樹寫進產物目錄，內容含頁面可見文字
   （本頁為示範資料、無個資）；若換成真實頁面，交付前應先檢視。

## 檔案結構

```
after.html                      被檢物（與 baseline 組 byte-identical）
shared_checks.js                共用檢查邏輯（由 baseline 的 checks_shared.py --emit-js 產生）
tests/defects.e2e.ts            測試規格（含 EXPECTED_OUTCOME 語意標記）
e2e.config.ts                   框架設定（明確指定 tests glob 與 8932 埠）
package.json / package-lock.json 依賴與鎖版
.e2e/report.json                執行結果
.e2e/results/                   逐步紀錄、截圖、無障礙樹
```
