# 行政儀表板 — 窄版響應式修正版

> 本儀表板為**練習用自擬示範資料**，非使用者機關實際資料。
> 修訂自 2026-10-29 的候選組（`art-20261029-063150-a2bc-code`，judge 61.5 < 門檻 75）。

本交付物包含五個部分：

1. **成品**：`after.html`（單頁行政儀表板）＋ 4 張截圖（亮/暗 × 寬/窄）
   （設計 token 色階展示另置於 `design-tokens.html`，不混入行政頁面本體）
2. **機械檢查器**：6 支可獨立重跑的檢查器（版面／窄版溢出／導覽碰撞／對帳等式／無障礙／對比度）
3. **對抗性實測**：7 份缺陷版 fixture（8 筆配對）＋ 雙向回歸（缺陷版必須被抓住、修好版必須全綠）
   ＋ `verification_summary.json` 的 `fixtures` 陣列（逐筆記錄被哪支檢查器以什麼 exit code 抓住）
4. **交付閘門**：`run_checks.sh`（bash）＋ `run_checks.ps1`（Windows PowerShell 5.1+），同一套邏輯兩個實作
5. **執行紀錄**：`RUNLOG.md`（人讀）＋ `verification_summary.json`（機器讀）＋ `manifest.json`（交付集合指紋）

---

## 1. 環境需求

| 項目 | 版本／需求 | 說明 |
|---|---|---|
| Python | **3.10 以上**（實測 3.12.3） | 用到 `match` 以外的新語法不需要，但 3.10 是安全下限 |
| Playwright | `playwright`（Python 套件） | 6 支檢查器全部用 `playwright.sync_api` 量測真實版面 |
| Chromium | Playwright 內建版本 | `python3 -m playwright install chromium` 會自動下載 |
| Bash | GNU bash 4+ | 只有 `run_checks.sh` 需要；單跑檢查器不需要 bash |
| PowerShell | **5.1+**（Windows 內建） | 只有 `run_checks.ps1` 需要；**Windows 使用者走這條路** |

### 安裝（Linux / macOS）

```bash
cd <此交付目錄>

# 1) 建立虛擬環境（建議，避免污染系統 Python）
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 2) 安裝相依套件
pip install playwright

# 3) 下載 Chromium（約 150MB，只需一次）
python3 -m playwright install chromium
```

### 安裝（Windows — 原生 PowerShell，不需 Git Bash / WSL）

```powershell
cd <此交付目錄>

# 1) 建立虛擬環境
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2) 安裝相依套件
pip install playwright

# 3) 下載 Chromium（約 150MB，只需一次）
python -m playwright install chromium

# 4) 跑完整閘門（PowerShell 原生版，不需要 bash）
powershell -ExecutionPolicy Bypass -File .\run_checks.ps1
```

> **Windows 使用者注意**：`run_checks.sh` 是 bash 腳本，Windows 上需 Git Bash / WSL；
> 本次另外交付 **`run_checks.ps1`**（PowerShell 5.1+ 原生版），
> 判定邏輯與 bash 版**完全一致**（交付物全綠／fixture 被抓住／雙向回歸／§6 grep 四段閘門），
> 只把 `timeout` 換成 `Process.WaitForExit(ms)`、路徑改用 `Join-Path`。
> 若連 PowerShell 都不用，六支檢查器**全部可以直接用 Python 跑**（見下一節）。

> ⚠️ **實測狀態**：`run_checks.ps1` 的語法已用 PowerShell 7.4.6 解析器驗證通過，
> 但**閘門的端到端執行只在 Linux + bash 版實測過**——本機沒有 Windows 環境可跑。
> 首次在 Windows 上執行時，請先確認輸出中的四段計數
> （交付物失敗數／被抓住筆數／雙向通過組數／殘留旗標數）與 `verification_summary.json`
> 的一致；若不一致，以 bash 版為準並回報。


---

## 2. 怎麼跑（收到即用）

### 最小驗證：確認成品沒壞

```bash
python3 audit.py after.html              # 版面形式檢查        → 期望 EXIT=0
python3 audit_narrow_overflow.py         # 窄版欄位可見性      → 期望 EXIT=0
python3 audit_nav_collision.py           # 導覽／主內容幾何    → 期望 EXIT=0
python3 audit_total_identity.py          # 對帳等式            → 期望 EXIT=0
python3 a11y_check.py                    # 無障礙              → 期望 EXIT=0（可能有建議）
python3 contrast_check.py                # 對比度              → 期望 EXIT=0
```

每支檢查器都可帶檔案路徑參數（預設是 `after.html`）：

```bash
python3 audit.py fixtures/defective_cell_hardclip.html   # 對缺陷版跑，必須 EXIT≠0
```

### 完整閘門（含對抗性實測）

```bash
bash run_checks.sh              # 全部（Linux / macOS / Git Bash / WSL）
bash run_checks.sh --quick      # 只跑最終交付物（跳過對抗性 fixture）
```

Windows（原生 PowerShell，不需 Git Bash / WSL）：

```powershell
powershell -ExecutionPolicy Bypass -File .\run_checks.ps1
powershell -ExecutionPolicy Bypass -File .\run_checks.ps1 -Quick
```

閘門的**通過條件**（全部滿足才算通過）：

| 條件 | 數值 |
|---|---|
| 最終交付物 6 支檢查器 | 全部 EXIT=0 |
| 對抗性 fixture | 被抓住 8 筆、漏抓 0 筆、**執行失敗 0 筆** |
| 雙向回歸 | 通過 8 組、失敗 0 組、**執行失敗 0 組** |
| §6 grep 閘門 | 殘留危險旗標 0、RUNLOG 有「已重跑驗證」stamp ≥1 |

> ⚠️ **「執行失敗」不等於「缺陷被抓住」**：檢查器找不到目標檔時回 EXIT=2、
> timeout 回 EXIT=124，兩者都會讓閘門失敗，不會被算成通過。
> （bash 版由 `timeout` 產生 124；PowerShell 版由 `Process.WaitForExit(ms)` 逾時產生 124。）

### 對抗性實測的逐筆結果在哪裡？

`verification_summary.json` 的 **`fixtures` 陣列**記錄了每一筆的
`{fixture, checker, exit_code, status, issue_summary}`——
即「哪支檢查器、以什麼 exit code、被什麼 issue 摘要抓住」。
`status` 取值：`caught`（缺陷被抓住）／`missed`（漏抓）／`checker_error`（檢查器沒跑起來）。
這區塊由 `build.py` 解析 `run_checks.sh` 的實際輸出產生，不手抄。

### 為什麼有兩套閘門（bash + PowerShell）？

因為**閘門本身寫錯時會報綠**。本輪實測在寫第二套實作時抓到三個「形同虛設」的閘門 bug：

| # | 閘門 bug | 症狀 | 修法 |
|---|---|---|---|
| 1 | PowerShell `Get-ChildItem -Include` 對目錄路徑回傳 **0 檔** | 殘留旗標數恆為 0 → 那條閘門從未檢查過任何檔案 | 改用 `-Recurse -File \| Where-Object { $_.Extension -in '.py','.md' }` |
| 2 | bash `grep -c "^\$"`（雙引號）數的是**空行**不是指令行 | 數字虛高 7 倍（55 vs 真實 8），卻因「≥1」而一直看起來是過的 | 改單引號版 `grep -c '^\$'` |
| 3 | bash `grep -n ... *.py *.md` 只掃**頂層** | 子目錄若有 .py/.md 就漏掉 | 改 `grep -rn --include='*.py' --include='*.md' .` 並排除閘門腳本自己 |

> ★ 為什麼排除閘門腳本自己？因為腳本裡必須寫出那些被禁用的旗標字串
> 才能搜尋它們 —— 不排除的話閘門會命中自己、殘留旗標數永遠 ≥1、永遠失敗。
> 這與 `RUNLOG.md` 第 11 節「不把旗標字串貼進 RUNLOG」是同一個道理。
>
> ★ 方法論：**寫第二套獨立實作，要求兩套的四段計數完全一致。**
> 差異一出現就代表其中一邊有 bug，而不是「環境不同所以正常」。
> 本輪的實際落差（執行紀錄數 55 vs 8、殘留旗標數 0 但只掃了 0 檔）
> 就是這樣抓出來的 —— 只看一套的程式碼永遠看不出來。

### 重跑截圖與摘要

```bash
python3 build.py                # 重新產生 4 張截圖 + verification_summary.json + manifest.json
```

`build.py` 是**唯一**的數字來源：`RUNLOG.md` 與 artifact notes 裡的每個數字都引用它產生的
`verification_summary.json`，不手抄。

### 重跑「修正前」的基準

```bash
python3 probe_before.py         # 量測 10-29 候選組的原始版面（RUNLOG §3 的數字來源）
```

---

## 3. 六支檢查器各自負責什麼

| 檢查器 | 檢查類型 | 涵蓋 | **不**涵蓋 |
|---|---|---|---|
| `audit.py` | 版面形式 | 溢出、截斷、重疊、觸控目標、console 錯誤、捲動區域宣告、排除率 | 資料數字、對比度、導覽幾何 |
| `audit_narrow_overflow.py` | 版面形式（獨立實作） | 窄版欄位可見性、捲動提示存在性、捲動區域宣告、**儲存格硬裁切** | 資料數字、對比度、導覽幾何 |
| `audit_nav_collision.py` | 版面形式 | 導覽／主內容相交、窄版主內容佔比、整頁水平捲動 | 欄位可見性、資料數字 |
| `audit_total_identity.py` | **核心正確性** | 總計 = Σ 分組合計 = Σ 明細值、小計列偵測、母體明寫 | 版面、對比度 |
| `a11y_check.py` | 無障礙 | 可機械判定的 WCAG 條文 | 螢幕閱讀器實機 |
| `contrast_check.py` | 對比度 | 前景／背景對比度比值 | 其他無障礙條文 |

`audit_narrow_overflow.py` **刻意不 import、不複製** `audit.py` 的 DOM 巡邏邏輯：
兩支用不同的量測路徑（`offsetParent` vs `scrollWidth/clientWidth` + 欄位矩形）。
理由是 A/B 實驗的邊界——控制變因消除的是組間差異，不是組內錯誤；
若同一支檢查器有假綠燈路徑，兩組都會綠。

---

## 4. 排除規則怎麼運作（`audit.py` 的核心改寫）

`audit.py` 的「型 A 設計意圖型」排除會把**已宣告捲動區域內**的元素排除掉，不再檢查
它們的溢出／截斷。排除不是靜默的：每一筆排除都會進入 `skipped` 清單，附上
**排除對象、排除理由、補償機制、解除條件**。

**排除率監控（兩級）**：若某條規則跳過的檢查對象過多，等於沒有檢查。
門檻為 **警告 >30%／失敗 >60%**；超過警告門檻時 `audit.py` 會印警告，
數字也會寫進 `verification_summary.json`（`skip_ratio_warn_pct`／`skip_ratio_fail_pct`／
`skip_ratio_over_warn`）。

本次實測排除率 **54.7%（52/95）** → 超過警告門檻，因此：
被排除的元素**不由 `audit.py` 覆蓋**，完全依賴補償機制 `audit_narrow_overflow.py`。
該機制若失效，這些元素將無任何檢查（解除條件見 `audit.py` 的 skipped 清單）。

### ★ 補償機制必須「被覆蓋」，不只是「被指名」

第一輪評審後的修正：舊版只檢查「`COMPENSATORS` 裡有沒有這個名字」，
名字存在就整類排除。但被指名的檢查器可能根本沒查被排除的那幾項。

實測反例（修正前）：一個 `overflow:hidden` 的儲存格（內容被硬砍、資料真的看不到）——
`audit.py` 把它排除（skipped）、被指名的 `audit_narrow_overflow.py` 也不查
→ **兩支都 EXIT=0**，缺陷靜默通過。

修正後兩道防線：

1. `audit.py` 的 `EXCLUDED_CHECKS` 宣告被排除的是哪幾項（`overflow` / `clipped`），
   `COMPENSATOR_COVERAGE` 宣告每支補償機制覆蓋哪幾項；**兩邊必須逐項對得上**
   才允許排除。對不上 → 排除不成立 → 元素回到檢查範圍。
2. `audit_narrow_overflow.py` 真的實作了 `overflow` / `clipped` 的偵測
   （儲存格 `scrollWidth > clientWidth` 且 `overflow` 非 visible/scroll → 硬裁切 → 缺陷）。

並新增對抗性 fixture `fixtures/defective_cell_hardclip.html` 專門盯這個邊界。

---

## 5. 交付集合

`manifest.json` 列出交付集合的每個檔案與其 sha256（由交付集合反推，不是掃工作目錄）。

> **manifest.json 本身不在清單內**：manifest 的內容若包含自己的 sha256 會形成自指方程
> （寫檔這個動作本身就改變該檔的雜湊），寫入後立即失效。要驗證 manifest 本身未被竄改，
> 請用 artifact 紀錄裡的指紋。

`fixtures/` 下的 **7 份**缺陷版 fixture（8 筆配對）與 6 支檢查器**必須一起交付**：
沒有缺陷版，「檢查器能抓住問題」這句話就沒有證據。

交付集合另含 `run_checks.sh`（Linux/macOS/bash）與 `run_checks.ps1`（Windows PowerShell 5.1+），
兩者是同一套閘門邏輯的兩個實作。

> ⚠️ **交付時的路徑陷阱**：`harness artifact add` 會把檔案平鋪複製（丟掉子目錄前綴）。
> 所以 `fixtures/xxx.html` 在 artifact 裡會變成 `xxx.html`。
> → 收到交付物後請手動把 7 份 fixture 放進 `fixtures/` 子目錄，
> 否則 `run_checks.sh` / `run_checks.ps1` 的前置檢查會直接讓閘門失敗（這是刻意設計：
> 寧可失敗，不要假綠燈）。

---

## 6. 已知邊界（誠實揭露）

| 項目 | 狀態 | 說明 |
|---|---|---|
| Windows 實機驗收 | **未做** | 本次只在 N100 Linux + Playwright Chromium 驗證。已交付 PowerShell 原生版 `run_checks.ps1`（語法經 PS 7.4.6 解析器驗證），但**閘門端到端未在 Windows 實跑**——本機無 Windows 環境。 |
| Safari / Firefox | **未做** | 只在 Chromium 量測。 |
| 螢幕閱讀器實機 | **未做** | `a11y_check.py` 只涵蓋可機械判定的 WCAG 條文（本頁機械可查部分為 0 項發現）。 |
| 360px 窄版 | **已修** | 5 欄在 360px 不需捲動即可全部可見（`narrow_overflow_disclosures.json` 的 `disclosed` 為空陣列）。 |
| skip-link 目標尺寸 | **已修** | 已加 `min-height/min-width: 44px`，符合 WCAG 2.5.5 目標尺寸（AAA）。 |
| 小計列偵測 | 標籤比對 | 靠標籤字樣比對，非語意判斷；由對帳等式兜底。 |
| `audit.py` 排除率 | **已揭露** | 實測 54.7%（52/95）超過 30% 警告門檻 → 檢查器會印警告、摘要會記 `skip_ratio_over_warn: true`。被排除的元素不由 `audit.py` 覆蓋，完全依賴補償機制 `audit_narrow_overflow.py`；解除條件見 `audit.py` 的 skipped 清單。 |

---

## 7. 資料來源

本儀表板為**練習用自擬示範資料**，非使用者機關實際資料。
此揭露同時出現在頁面資料來源說明、`RUNLOG.md` 與 artifact notes 三處。

案件數、超時率、總務處櫃台等資料皆為虛構示範值，
「113 年度第 2 季」的期間字樣僅為示範版面的一部分。
