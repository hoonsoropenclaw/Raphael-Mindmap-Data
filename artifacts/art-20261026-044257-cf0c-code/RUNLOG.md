# RUNLOG — scout 2026-10-26 A/B：markmead/hyperui 的 accessibility-review 方法

練習題：把 markmead/hyperui（MIT, risk=low, SHA 252efcfe39161db6e67cd877da001ee248d2bbf6）
的 `.claude/skills/accessibility-review/SKILL.md` 方法，實際套用在既有行政儀表板
（2026-10-23 的 token-dashboard `after.html`）上，做 A/B。

- 基準（baseline）：10-23 原始版本（只修版面與對比度，無障礙面向未處理）
- 候選（candidate）：同一份版面與 token，只套用 accessibility-review 方法帶來的 6 項修正

環境：N100 Linux · Chromium（Playwright 內建）· Python 3.12 + PYTHONPATH=/home/hoonsoropenclaw/.local/lib/python3.12/site-packages
執行時間：2026-10-26 04:37–04:45
金鑰：無（全部檢查器不需要金鑰、不需要網路；hyperui 為純 skill 套件，未執行任何下載的程式碼）

---

## 1. 為什麼要選 hyperui（相關性判斷）

今日領域：admin-presentation（主）＋ dev-ui-design（副）。scout 57 個新候選中，
真正對得上的只有兩類：pptx 產出工具鏈與 Tailwind/元件庫。逐個套用 playbook/05 的三問：

| 候選 | 1. 改善哪個 rubric 項目？ | 2. 取代 SOP 哪一步？ | 3. N100 能跑？ | 結論 |
|---|---|---|---|---|
| `markmead/hyperui` | code rubric 的 `robustness`/`readability`；dev-ui-design 的「無障礙對比與鍵盤操作」課程目標 | code SOP §6「交付前機械檢查」目前只查版面與對比，沒有 a11y 面向 | 純 Markdown 方法 + 自寫檢查器，可 | **vet + 試用** |
| `arcsin1/oh-my-ppt` | slides rubric 的 `visual_design` | slides SOP §3 工具鏈第 2 順位 | Electron 桌面 app，要 45MB+ | **reject** |
| `ningzimu/codex-ppt-skill` | slides rubric 的 `visual_design`（整頁生圖式 PPT） | — | 需 gpt-image-2 生圖 API 金鑰 | 不試（needs_secrets + 整頁圖片式不可編輯，與行政簡報「拿到就能改」需求相反） |
| `markmead/hyperui` 之外的 Tailwind 元件庫（daisyui / react-bits / cult-ui） | dev-ui-design 的元件來源 | — | 需 npm install 全家桶 | 不試（與今日的「鍵盤操作/無障礙」課程目標無直接關係，且 10-25 已驗證元件庫對行政產出無直接槓桿） |

## 2. vet 結果（只讀掃描，未執行任何下載的程式碼）

```
python -m harness tools vet markmead/hyperui
  → ok=true risk=low license=mit sha=252efcfe39161db6e67cd877da001ee248d2bbf6 needs_secrets=false
  findings: medium .gitignore（讀取憑證/金鑰路徑，僅為 .gitignore 條目本身）

python -m harness tools vet arcsin1/oh-my-ppt
  → ok=true risk=medium license=apache sha=b937ae5cc6049ec9b2cfc5cb4e35dff87fce1d17 needs_secrets=true
  findings: medium drizzle.config.ts / electron-builder.yml / package.json(postinstall electron-builder install-app-deps)
            medium resources/slide-pack-windows-amd64.exe（內含二進位執行檔）
            medium resources/chart.v4.js / anime.v4.js / katex/*.min.js（疑似混淆，超長單行）
            low+  6 個 .tsx（讀取憑證/金鑰路徑）
```

## 3. oh-my-ppt 為什麼被拒絕（vet 之後追查原始碼，不是只看 README）

追查 `@arcsin1/html2pptx@0.2.1`（npm pack 實測）：

```
package/package.json → "license": "AGPL-3.0-only"
```

**核心轉換套件是 AGPL-3.0-only（copyleft），與 repo 本身的 Apache-2.0 不同授權。**
把 AGPL 程式鏈進產出流程，會讓產出物的衍生授權成為爭議 → 直接擋掉。

另外查到字型處理只寫 `a:latin` + `a:ea`（`grep typeface` 於 `dist/ooxml-writer-*.js`
共 14 處、其中 `a:latin` 4 處、`a:ea` 4 處），無法對應行政簡報的 CJK 字型交付需求
——與 10-25 拒絕 `singerla/pptx-automizer` 同一理由（那次是只寫 `a:latin`、從不寫 `a:ea`/`a:cs`）。

```
python -m harness tools reject arcsin1/oh-my-ppt --reason "..."   → status=rejected
```

## 4. hyperui 的 accessibility-review 方法怎麼用

`markmead/hyperui/.claude/skills/accessibility-review/SKILL.md` 是純 Markdown 的
WCAG 2.1 AA 稽核方法（不需執行任何程式碼，符合 playbook/05「對 skills/prompt 類不用執行」）。
它給的是：WCAG 條文速查表（1.1.1 / 1.3.1 / 1.4.3 / 1.4.11 / 2.1.1 / 2.4.3 / 2.4.7 /
2.5.5 / 4.1.2 …）＋ 8 類常見問題 ＋ 測試順序（自動掃描抓約 30% → 鍵盤巡覽 → 螢幕閱讀器
→ 對比 → 200% 縮放）＋ 稽核報告表格格式。

**本 harness 的缺口**：現有 code SOP §6 的機械檢查只有「版面（audit.py）」與
「對比（contrast_check.py）」，兩者對無障礙缺陷**永遠是綠的**——無障礙缺陷不會讓版面壞掉。
所以本次把 SKILL.md 的 WCAG 條文映射成一支可重跑的機械檢查 `a11y_check.py`。

## 5. a11y_check.py 的判準與雙向驗證

覆蓋（對應 SKILL.md 的條文）：2.1.1/4.1.2（鍵盤可操作性、非原生 role=link）、4.1.2/2.4.4
（可及名稱）、2.5.8 AA 24px / 2.5.5 AAA 44px（目標大小）、1.3.1（th 的 scope）、
1.4.11（元件邊界對比）、2.4.7（焦點可見性，真實按 Tab 量）、1.4.11（焦點指示對比）、
2.4.1（略過重複區塊）、4.1.2/3.2.2（aria-pressed 與可及名稱一致性）。

**檢查器自身的兩次修正（都是先寫錯、被自己的規則抓到）**：

1. 第 1 版只量 `backgroundColor` 對比 → 對 `.theme-toggle` 報假陽性。
   但它有 `border: 1px solid var(--border-default)`（5.99:1），而 1.4.11 判的是
   「元件邊界是否可辨識」，邊界可以是邊框。→ 改成「邊框 ≥3:1 或填色 ≥3:1 即通過」。
2. 第 2 版對透明底的 nav-item 報假陽性。判準要對：靠**文字本身**辨識的元件
   （無填色、無邊框、文字對比達 4.5:1）不需要邊界，1.4.3 才是它的判準；
   表單控制項（input/select/textarea）例外（沒有邊框就看不出欄位在哪）。
   → 改成「有可辨識邊界，或靠達標文字辨識 → 通過」。
   這兩次修正都寫進檢查器的註解（避免下一次有人改回去）。

**雙向回歸驗證**（code SOP §7.1）：

```
[1] 缺陷版 baseline/after.html   → a11y_check.py EXIT=1   （必須 ≠ 0）
[2] 修好版 candidate/after.html  → a11y_check.py EXIT=0   （必須 = 0）
```

基準版被攔下 14 項（阻擋 6／建議 8）：

```
阻擋 6 項：
  HIGH  鍵盤可操作性 ×5   div.nav-item（role="link" 的 div，沒有原生 Enter/Space 行為）
  MEDIUM aria-pressed 與可及名稱一致性 ×1
         按鈕可及名稱隨狀態改變（'切換深色模式' → '切換淺色模式'），
         螢幕閱讀器會讀出互相矛盾的名稱與狀態
建議 8 項：
  LOW  目標大小（AAA 44px）×7
  LOW  略過重複區塊（2.4.1 Level A）×1
         第一個鍵盤停點是 nav-item，不是「跳至主要內容」內部連結
```

## 6. 候選套用的 6 項修正（全部來自 SKILL.md 的條文）

| # | SKILL.md 條文 | 修正 |
|---|---|---|
| 1 | 2.1.1 鍵盤 / 4.1.2 名稱角色值 | 5 個 `div[role=link][tabindex=0]` → 真正的 `<a href="#…">`（有原生 Enter 行為與連結角色） |
| 2 | 4.1.2 / 3.2.2 | 主題切換按鈕可及名稱固定為「深色模式」，狀態只由 `aria-pressed` 表達（不再改 textContent） |
| 3 | 2.4.1 略過區塊（Level A） | 加入 skip link「跳至主要內容」（`left:-9999px` 移出畫面外，`:focus` 時回到原位）＋ `<main id="main-content">` 與 3 個 section 錨點 |
| 4 | 2.5.5 目標大小 | nav-item / .btn / .theme-toggle 全部 `min-height: 44px` |
| 5 | 1.4.11 非文字對比 | `.nav-item.active` 加 `border-left: 3px solid var(--accent)`（底色 accent-subtle 對 surface 只有 1.35:1，單靠底色不足以表達「目前所在頁面」） |
| 6 | 1.4.3 / 4.1.2 | 改成 `<a>` 後 UA 預設底線跑出來 → `text-decoration: none`（連結外觀由元件層決定） |

**控制變因**：版面、token、數據、文案、圖表全部不動；只動無障礙屬性與目標尺寸。
驗證：`grep` 確認內容字串在兩版完全一致（案件總數 1/1、資訊維運 2/2、oklch 56/56）。

## 7. 三支機械檢查在候選版的結果（無回歸）

```
$ python3 a11y_check.py after.html        → EXIT=0   （14 項 → 1 項建議級：skip-link 38px < AAA 44px，AA 已過）
$ python3 audit.py                         → EXIT=0   總計問題數 0（4 視窗：溢出/截斷/重疊/觸控目標/console 錯誤）
$ python3 contrast_check.py after.html     → EXIT=0   24/24 通過 → PASS
```

**a11y_check.py 的涵蓋邊界（誠實揭露，不寫「全部通過」）**：
涵蓋 2.1.1／1.3.1／1.4.11／2.4.1／2.4.7／2.5.5／2.5.8／3.2.2／4.1.2；
**不涵蓋**螢幕閱讀器實機測試（VoiceOver/NVDA）、動態內容廣播、翻譯與語言正確性、
色彩以外的視覺障礙情境、實際使用者的障礙情境。
「EXIT=0」只代表上面列出的項目全過，不代表頁面完全無障礙問題。

## 8. 渲染檢查（看圖，不看原始碼）

以 `shot.py` 產生 4 張截圖（亮/暗 × 1440/420，device_scale_factor=2），
再用 vision 實際檢視 `after-wide.png`：
- 左側「總覽」的選取指示邊框**看得出來**（深藍色左邊框 + 淡藍底）
- 按鈕（深色模式／匯出報表）高度正常、沒有跑版或文字截斷
- KPI 4 欄、表格 6 列、token 色階皆完整呈現，沒有溢出／重疊／截斷
- 過程中發現並修掉一個**只有看圖才會發現**的回歸：改成 `<a>` 後 UA 預設底線跑出來
  → 加 `text-decoration: none` 後重截圖確認。

## 9. 產出檔案

```
deliver-baseline/   after.html, a11y_check.py, audit.py, contrast_check.py, 4 張截圖
deliver-candidate/  after.html, a11y_check.py, audit.py, contrast_check.py, 4 張截圖
baseline_a11y.json  基準版 a11y 稽核結果（機器可讀）
candidate_a11y.json 候選版 a11y 稽核結果（機器可讀）
```

## 10. 結論

hyperui 的 accessibility-review 方法**有可操作的增量**：它把「無障礙」從一句期望
變成 9 條可機械檢查的判準，補上了本 harness 現有機械檢查（版面 + 對比）完全看不到的
一整個缺陷家族。基準版在版面與對比都是綠的（audit EXIT=0、contrast 24/24），
但無障礙面向有 6 項阻擋級缺陷——這正是 10-23 那件作品被判 78.8 而非更高的原因之一，
而當時沒有任何一支檢查器看得到。

採用方式：把 `a11y_check.py` 併入 code SOP §6 的交付前機械檢查清單，
並在 SOP 記錄「無障礙缺陷不會讓版面壞掉，版面檢查對它永遠是綠的」這個邊界。
