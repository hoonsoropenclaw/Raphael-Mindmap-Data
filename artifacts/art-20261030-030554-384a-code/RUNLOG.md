# 執行紀錄（RUNLOG）

> **本檔的每一個數字都來自 `verification_summary.json`（由 `build.py` 機器回算）。**
> 不手抄（code SOP §8-2）。若要重算：`python3 build.py`。
> 交付檔案清單與 sha256 在 `manifest.json`（由**交付集合反推**，不是掃工作目錄）。

## 1. 環境

- N100 Linux · Chromium（Playwright 內建）· Python 3.12
- 金鑰：無。全部檢查器不需要金鑰、不需要網路。
- 資料來源：**本儀表板為練習用自擬示範資料，非使用者機關實際資料。**
  （此揭露同時出現在頁面資料來源說明、artifact notes 與本檔。）

## 2. 這次修的是什麼（修訂自 10-29 候選組 `art-20261029-063150-a2bc-code`）

10-29 的候選組 judge 給 61.5（門檻 75）→ 不及格，兩筆 high 缺陷：

| judge high 缺陷 | 本次處置 | 驗證證據 |
|---|---|---|
| 窄版（420px）表格三欄被裁切，且 `audit.py` 結構性放行該問題 | 窄版策略重寫（Q2）＋ `audit.py` 排除規則重寫（Q1） | `audit_narrow_overflow.py` EXIT=0；對抗性 fixture 被抓住 |
| 左側導覽欄與主內容區重疊 | 窄版導覽改為橫向條列 | `audit_nav_collision.py` EXIT=0；對抗性 fixture 被抓住 |

## 3. 修正前的實測（先實測 → 再修 → 再實測，code SOP §9-4）

`probe_before.py` 量測 420px 視窗（2026-10-30，修改前）：

```
.sidebar        216px（固定直向側欄，flex-shrink: 0）
.main           204px  →  只拿到視窗的 48.6%
.table-scroll   122px  →  內容納 320px 的 table
欄位可見        1 / 5  ← 「三欄被裁切」的實測根因
捲動容器宣告    tabindex=null, role=null, aria-label=null  ← 沒有任何宣告
```

## 4. 修正後的實測（`build.py` 機器回算，見 `verification_summary.json` 的 `geometry`）

| 視窗 | `.main` 寬度 | 主內容佔視窗 | 欄位可見 | 捲動容器 | 捲動提示 |
|---|---|---|---|---|---|
| after-wide (1440) | 1224px | 85.0% | 5 / 5 | 1142 / 1142（不溢出） | 不需要 |
| after-narrow (420) | 420px | 100.0% | 5 / 5 | 362 / 362（不溢出） | 不需要 |
| after-dark (1440) | 1224px | 85.0% | 5 / 5 | 1142 / 1142（不溢出） | 不需要 |
| after-dark-narrow (420) | 420px | 100.0% | 5 / 5 | 362 / 362（不溢出） | 不需要 |

- 420px 下主內容由 48.6% 提升到 100.0%；欄位可見由 1/5 提升到 5/5。
- 420px 表格已不需捲動（362px 容器容納 320px 表格）→ 資料完整性完整保留。
- 360px（`audit_narrow_overflow.py` 的 narrow-xs 情境）容器 302px / 表格 320px → 溢出，
  此時捲動提示自動出現（「表格可橫向捲動以查看其餘欄位（目前顯示 4／5 欄）」），
  屬**已揭露的可接受狀態**，見 `narrow_overflow_disclosures.json`。

## 5. 六支機械檢查的實際執行結果

```
$ python3 audit.py after.html                    → EXIT=0   問題數 0   最高排除率 46.4%
$ python3 audit_narrow_overflow.py after.html    → EXIT=0   問題數 0
$ python3 audit_nav_collision.py after.html      → EXIT=0   問題數 0
$ python3 audit_total_identity.py after.html     → EXIT=0   問題數 0
$ python3 a11y_check.py after.html               → EXIT=0   發現 1 項（阻擋 0／建議 1）
$ python3 contrast_check.py after.html           → EXIT=0   24/24 通過 → PASS
```

### 5.1 `audit.py` 的排除規則（Q1 的核心改寫）

改寫前的排除規則是**單一**的 `if (inScroller(el)) continue;`，靜默略過捲動容器內的所有元素，
RUNLOG 裡沒有任何一行提到跳過過什麼 → 這是 10-29 假綠燈的根因。

改寫後拆成兩型，且**兩型都必須留痕**：

| 型 | 排除對象 | 排除理由 | 補償機制 | 解除條件 |
|---|---|---|---|---|
| A 設計意圖型 | 位於**已宣告**捲動區域內的元素 | 該區域已宣告 role=region + aria-label + tabindex，使用者與輔助科技知道它可捲動 | `audit_narrow_overflow.py`（以**不同實作路徑**獨立複驗，Q4） | 捲動區域失去任一宣告屬性時排除立即失效 |
| B 補償機制型 | 位於**未宣告**捲動區域內的元素 | **沒有理由** | — | **不排除**，直接報缺陷 |

實測輸出（skipped 清單，非靜默）：

```
skipped 清單（型 A 設計意圖型排除，共 52 筆／檢查對象 112 筆）：
    A/design-intent | 排除對象：TABLE
        理由：位於已宣告的捲動區域「caseTableScroll」內，該區域已宣告可捲動（role=region + aria-label + tabindex）
        補償機制：audit_narrow_overflow.py
        解除條件：該捲動區域失去任一宣告屬性時，本排除立即失效
排除率：52/112 = 46.4%（門檻 ≤ 90%）
```

排除率監控：若某條規則長期跳過 90% 以上的檢查對象，等於沒有檢查 → 判定失敗。

## 6. 對抗性實測（code SOP §9-2／§7.1）

`fixtures/` 下 6 份缺陷版檔案，**7 筆配對全部被抓住、0 筆漏抓**；
7 組雙向回歸（缺陷版 EXIT≠0、修好版 EXIT=0）**全部通過**。

```
$ bash run_checks.sh after.html
  ✓ 被抓住  EXIT=1  | audit.py                  × fixtures/defective_undeclared_scroller.html
      實際輸出摘要：✗ 未宣告的捲動容器 (1) / ✗ 溢出 (1)
  ✓ 被抓住  EXIT=1  | audit_narrow_overflow.py  × fixtures/defective_undeclared_scroller.html
      實際輸出摘要：✗ 欄位被裁切但捲動容器未宣告 / ✗ 容器溢出但沒有可見的捲動提示
  ✓ 被抓住  EXIT=1  | audit_total_identity.py   × fixtures/defective_total_mismatch.html
      實際輸出摘要：✗ 對帳等式不成立：總計 5,812 ≠ Σ 明細 4,812（差 1,000）
  ✓ 被抓住  EXIT=1  | audit_total_identity.py   × fixtures/defective_subtotal_double_count.html
      實際輸出摘要：✗ 對帳等式不成立：總計 9,624 ≠ Σ 明細 4,812（差 4,812）
  ✓ 被抓住  EXIT=1  | audit_total_identity.py   × fixtures/defective_subtotal_huizong_label.html
      實際輸出摘要：✗ 對帳等式不成立：總計 9,624 ≠ Σ 明細 4,812（差 4,812）
  ✓ 被抓住  EXIT=1  | audit_total_identity.py   × fixtures/defective_subtotal_unknown_label.html
      實際輸出摘要：✗ 對帳等式不成立：總計 4,812 ≠ Σ 明細 9,624（差 -4,812）
  ✓ 被抓住  EXIT=1  | audit_nav_collision.py    × fixtures/defective_nav_squeeze.html
      實際輸出摘要：✗ 窄版主內容只拿到視窗的 48.6%（門檻 85%）
  被抓住：7 筆　漏抓：0 筆

  ✓ audit.py                 缺陷版 EXIT=1（抓到）  修好版 EXIT=0（綠）
  ✓ audit_narrow_overflow.py 缺陷版 EXIT=1（抓到）  修好版 EXIT=0（綠）
  ✓ audit_total_identity.py  缺陷版 EXIT=1（抓到）  修好版 EXIT=0（綠）
  ✓ audit_total_identity.py  缺陷版 EXIT=1（抓到）  修好版 EXIT=0（綠）
  ✓ audit_total_identity.py  缺陷版 EXIT=1（抓到）  修好版 EXIT=0（綠）
  ✓ audit_nav_collision.py   缺陷版 EXIT=1（抓到）  修好版 EXIT=0（綠）
  雙向通過：7 組　失敗：0 組
```

### 6.1 對帳等式（Q3／code SOP §11）

母體明寫：

- 明細層母體 = `<table>` tbody 中所有 `<tr>` 的「案件數」欄（每列算 1 筆）
- 分組層母體 = 同上（本表只有一個分組維度：處室，每列自成一組）
- 總計層母體 = `.panel-sub` 中「合計 N 件」的 N
- 被排除者：thead、任何小計列（標籤集合見下）、平均天數欄、超時率欄（百分比／平均值不可加總）

三個數字由**同一個函式**回算：

```
✓ 對帳等式成立：總計 4,812 = Σ 分組合計 4,812 = Σ 明細值 4,812
```

小計列偵測標籤（多寫法並列，code SOP §11-2）：
`['合計', '小計', '總計', '累計', '彙總', '彙計', '總合', 'subtotal', 'sub total', 'total', 'sum']`

### 6.2 這輪對抗性實測**抓到的是檢查器自己的缺陷**（3 處）

這是本輪最重要的發現：**對抗性 fixture 不只驗產出物，也驗檢查器。**

1. **`audit_nav_collision.py` 的 `mainRatio` 恆為 NaN**
   - 症狀：`mainRatio: main ? +(main.width / window.innerWidth)...` —— `main` 是**元素**不是 rect，
     元素沒有 `.width` 屬性 → NaN。
   - 後果：`NaN < 0.85` 恆為 False → **「窄版主內容被擠壓」這條檢查永遠不觸發**（一條假綠燈）。
   - 實測：修正前 `audit_nav_collision.py` 對 `defective_nav_squeeze.html` 回 EXIT=0（漏抓）。
   - 修正：改用 `main.getBoundingClientRect().width`。修正後對同一 fixture 回 EXIT=1。

2. **`audit.py` 的重疊檢查對行內元素產生假陽性**
   - 症狀：`getBoundingClientRect()` 對「會換行的行內元素」回傳的是**所有行框的聯集**。
   - 實測：420px 下兩個 `<code>` 分別在 x=116–203 與 x=278–387（同一行內左右分開），
     聯集框卻是 116–203 與 29–387 → 被判為 `overlapX=87, overlapY=14`。
   - 修正：改用 `getClientRects()` **逐行比對**，只有同一行的行框才可能重疊。

3. **`audit_total_identity.py` 的小計列標籤集合漏了「彙總」**
   - 症狀：偵測集合只有 `['合計','小計','總計','累計','subtotal','total']`。
   - 後果：寫成「彙總」的彙總列被當成**明細** → Σ 明細靜默加倍 → 合計被報成兩倍。
   - 修正：補上「彙總／彙計／總合／sum」，並新增 `defective_subtotal_huizong_label.html`
     作為**判別式測試**（只有認得這個標籤才抓得到）。
   - 殘留邊界（誠實揭露）：小計列偵測是**標籤比對**不是語意判斷，
     寫法沒列到的標籤（例如 fixture 的「全室彙整」）仍會被當成明細 →
     由「總計 ≠ Σ 明細」這條等式抓出來（實測差額 −4,812）。
     → **兩道防線互補：標籤偵測擋常見寫法，等式擋所有漏接。**

### 6.3 對抗性 fixture 的設計陷阱（記錄下來避免下次踩）

- **CSS 覆寫順序**：fixture 的覆寫規則必須放在被覆寫規則**之後**。
  第一次把 fixture 的 `@container page { .app { flex-direction: row } }` 插在 `.app` 規則後面、
  但仍在 `@container page` 區塊**前面** → 同特異度下後者勝出 → **fixture 完全無效**，
  對缺陷檔案仍回 EXIT=0。已改為插在 `@container page` 區塊之後。
- **fixture 必須讓「錯誤可觀察」**：第一版 `defective_subtotal_double_count.html`
  讓「彙總列」存在但宣告的總計不變 → 偵測器認得標籤時 Σ 明細 = 4,812 = 宣告 → EXIT=0 漏抓。
  改成宣告 9,624 後才成為可觀察的缺陷。

## 7. 視覺驗證（code SOP §2-5：要看渲染後的成品，不是原始碼）

4 張截圖（`after-wide.png` / `after-narrow.png` / `after-dark.png` / `after-dark-narrow.png`）
**已實際看過並逐張描述**：

| 截圖 | 觀察結果 |
|---|---|
| after-narrow (420) | 導覽已改為橫向條列（總覽／案件量／滿意度／人力配置／系統LOG 一列排開）；表格 5 欄（處室／案件數／平均天數／超時率／狀態）**全部可見**；KPI 4 卡為 2×2；無重疊、無破版、無文字硬切斷 |
| after-dark-narrow (420) | 同上，暗色系對比正常，徽章（達標／觀察／超標）三色皆清晰 |
| after-wide (1440) | **直向側欄保留**（窄版規則未誤傷寬版）；KPI 4 卡同一列；表格 5 欄完整 |

## 8. 各檢查器的涵蓋邊界（誠實揭露，code SOP §7.3）

| 檢查器 | 類型 | 涵蓋 | 不涵蓋 |
|---|---|---|---|
| `audit.py` v2 | 版面形式 | 溢出／截斷／重疊／觸控目標／console 錯誤／捲動區域宣告／排除率 | 資料數字、對比度、欄位可見性、導覽幾何、螢幕閱讀器實機 |
| `audit_narrow_overflow.py` | 版面形式 | 窄版欄位可見性、捲動提示存在性、捲動區域宣告、硬裁切 | 資料數字、對比度、導覽幾何 |
| `audit_nav_collision.py` | 版面形式 | 導覽／主內容相交、窄版主內容佔比、整頁水平捲動、導覽目標大小 | 表格欄位可見性、資料數字、對比度 |
| `audit_total_identity.py` | **★ 核心正確性** | 總計＝Σ分組＝Σ明細的三層等式、小計列偵測與排除、不可加總欄位排除 | 版面、對比度、跨檔合併、小計列**語意**判斷（只做標籤比對） |
| `a11y_check.py` | 無障礙 | 2.1.1／4.1.2／1.3.1／1.4.11／2.4.1／2.4.7／2.5.5／2.5.8／3.2.2 | 螢幕閱讀器實機、動態內容廣播、翻譯、oklch 不支援時的 canvas 靜默退化 |
| `contrast_check.py` | 對比度 | 24 組預先列舉的配對（文字×背景、徽章、非文字 UI） | 未列舉的配對組合（**覆蓋率不會印在輸出上**） |

**「EXIT=0」只代表已列項目全過，不代表產出物完全無問題。**

## 9. 未修／揭露的項目（code SOP §5：缺陷必須標處置狀態）

| 項目 | 狀態 | 說明 |
|---|---|---|
| `a11y_check.py` 發現 1 項建議：skip-link 尺寸 116×38px 未達 AAA 44×44px | `deferred` | **AA 已過**（2.5.5 的 AA 門檻是 24×24）。skip-link 是鍵盤專用元素、預設移到畫面外，取得焦點才顯示，尺寸 44px 會讓它顯示時佔掉視角較多。維持原狀。 |
| 360px 下表格仍需橫向捲動（4/5 欄可見） | `disclosed`（可接受） | 容器已宣告（role/aria-label/tabindex）且有可見提示「表格可橫向捲動以查看其餘欄位（目前顯示 4／5 欄）」。依 Q2「資料完整性優先於版面完整性」，寧可捲動也不砍欄位。見 `narrow_overflow_disclosures.json`。 |
| 小計列偵測是標籤比對非語意判斷 | `disclosed`（邊界） | 見 §6.2-3。由等式這條線兜底。 |
| 螢幕閱讀器實機測試（VoiceOver / NVDA） | `wont-fix` | 本環境無螢幕閱讀器、無 Windows／macOS 實機，無法驗證。已在檢查器涵蓋邊界揭露。 |

## 10. 部署／執行路徑（code SOP §3）

- 一次性腳本：在 N100 Linux 上執行，無部署需求。
- 執行方式：

```bash
cd workspace/practice-20261030-narrow-fix
python3 build.py          # 產生截圖 + verification_summary.json + manifest.json
bash run_checks.sh        # 交付閘門（6 支檢查器 + 對抗性 fixture + 雙向回歸 + §6 grep）
```

- 開啟產出：`after.html`（單一自帶檔案，無外部相依、無金鑰、無網路需求）。
- **未在真實 Windows 實機驗收**：本產出是網頁靜態檔，不涉及 Windows 專屬行為，
  但瀏覽器行為以 Chromium 為準；未在 Safari／Firefox 實測。

## 11. §6 交付前機械檢查（grep 閘門，輸出由 `run_checks.sh` 第 4 節產生）

```
$ bash run_checks.sh after.html          # 第 4 節
  殘留旗標數：0（必須 0）
    ★ 註：本節刻意不逐一列出被禁用的旗標字串 —— 把它寫進本檔會讓
      §6 的 grep 閘門命中本檔自己（自我匹配），殘留旗標數會變成 1。
      實際被 grep 的旗標清單見 run_checks.sh 第 4 節原始碼。
  stamp 數：3（必須 ≥ 1）
  執行紀錄數：54（必須 ≥ 1）
```

★ 這個自我匹配是本輪實測才發現的：第一次寫 RUNLOG 時把 grep 的完整指令
（含禁用旗標字串）貼進第 11 節 → 第 4 節的閘門回報「殘留旗標數：1」，
指向 RUNLOG.md 自己。已改為不列出旗標字串。

## 12. 已重跑驗證

已重跑驗證：2026-10-30 拉斐爾（hermes）— `bash run_checks.sh after.html` 全綠，
6 支檢查器 EXIT=0、7 筆對抗性 fixture 全被抓住、7 組雙向回歸全過、§6 grep 全過。
