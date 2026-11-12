# 服務品質儀表板缺陷檢查工具（baseline：Playwright 直接寫）

依 `SPEC.md`／`checks_shared.py` 的 docstring 實作一支可重複執行的缺陷檢查工具，
對 `after.html` 檢查 5 條已知缺陷（D1–D5）＋ 2 條對照組（D6/D7）。

## 目標環境與實測狀態

| 項目 | 狀態 |
|---|---|
| 開發／驗證環境 | **Linux 6.8.0-136-generic（N100）、Python 3.12、Playwright + Chromium 156.0.8078.4** |
| 目標環境 | Windows |
| **Windows 實機驗收** | **未在真實 Windows 實機驗收**。Chromium 於 Windows 的 headless 行為、`py -3` launcher、中文檔名編碼（cp950）皆未實測，本工具僅在 Linux/N100 實跑過。 |

## 前置條件

```bash
python3 -m pip install playwright
python3 -m playwright install chromium
```

## 執行（三步）

```bash
# 1. 在本目錄啟動本機伺服器（頁面檔名是 after.html，URL 已含 /after.html）
python3 -m http.server 8933 --bind 127.0.0.1

# 2. 另開一個終端機，執行檢查
python3 defects_playwright.py

# 3. 看結果
cat baseline_result.json
```

> 註：舊版（rev0）把 URL 寫成 `http://127.0.0.1:8933/`，必須自行把
> `after.html` 改名成 `index.html` 才能跑；rev1 已修正為直接抓 `/after.html`，
> **不需要改名任何檔案**。

## 退出碼

| 碼 | 意義 |
|---|---|
| `0` | 5 條缺陷全抓，且 2 條對照組行為正確 |
| `1` | 有缺陷漏抓，或對照組失效（**這是「抓到問題」的正常結果**，不是執行失敗） |
| `2` | 執行環境錯誤（例：伺服器沒開、頁面載不到）。錯誤訊息寫在 `baseline_result.json` 的 `error` 欄位 |

## 7 條檢查各代表什麼

| ID | 檢查 | ok=True 的意義 | 現況（after.html） |
|---|---|---|---|
| D1 | 假綠燈：`.nav-item.active` 對比 < 4.5:1 | 對比不足的缺陷被抓到 | **NG** — 實測 10.77:1，該缺陷已於 10-30 修好 |
| D2 | dead token：`--border-strong` 定義但無 `var()` 引用 | dead token 被抓到 | **NG** — 實測有引用，該缺陷已修好 |
| D3 | 死按鈕：匯出報表按鈕無可觀察反應 | 死按鈕被抓到 | **OK** — before=596 after=596，可重現 |
| D4 | 狀態不持久：切深色後 reload 回 light | 不持久被抓到 | **OK** — toggle=dark reload=light，可重現 |
| D5 | 側欄未響應式：360px 下側欄 ≥ 視窗一半 | 側欄佔滿被抓到 | **OK** — sidebar=216 / win=360，可重現 |
| D6 | 對照組(應過)：h1 有內容 | 頁面確實載入 | **OK** |
| D7 | 對照組(應敗)：斷言不存在的字串必須失敗 | 對照組機制有效 | **OK** — wait_for 逾時＝預期失敗 |

★ **D1/D2 的 NG 不是缺陷沒抓到，是那兩條缺陷早已修好**（after.html 裡有
`judge fix` 註記）。因此預期結果是 **5/7 符合預期、exit code 1**。

## 已知限制

1. **D7 只把 `playwright.TimeoutError` 視為預期失敗**；其他例外會往外拋，
   不再被靜默吞掉（rev0 用 `except Exception` 會把任何錯誤都記成對照組正常）。
2. **任何路徑都會寫出 `baseline_result.json`**（含 `error` 欄位）——
   rev0 崩潰時什麼都不留（rev1 以 try/finally 保證）。
3. **本工具只驗 5 條已列缺陷**；「5/7 符合預期」不代表頁面沒有其他缺陷。
   覆蓋率 = 已列項目數 ÷ 實際問題類型數，這個比率不會印在輸出上。
4. **Windows 未實測**（見上表）。
5. `shots_failure/d1-active-nav.png` 由本腳本在每次執行後產生（證據用）。

## 檔案結構

```
after.html              被檢物（服務品質儀表板，與 candidate 組 byte-identical）
checks_shared.py        共用檢查邏輯（single source of truth）
                        另可用 `python3 checks_shared.py --emit-js` 匯出 JS 給 candidate 端
defects_playwright.py   baseline 執行器（Playwright 直接寫）
baseline_result.json    執行結果（含 error 欄位）
shots_failure/          失敗證據截圖
```
