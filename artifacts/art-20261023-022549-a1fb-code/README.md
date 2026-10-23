# 服務品質儀表板 — 設計 token 重構

把一個「能用就好」的行政儀表板（`before.html`）重構成有完整設計 token 系統的版本
（`after.html`），並附兩個可重跑的驗證腳本。

今天新學的四個概念全部實際用在產出上：

| 概念 | 在哪裡用 |
|---|---|
| CSS Cascade Layers（`@layer`） | `reset, vendor, theme, base, components, utilities` 六層契約 |
| OKLCH 感知均勻色階 | 全系統鎖 H=250 的中性階 + 低彩度語意色 |
| Container Queries | KPI 網格自適應，1440px 四欄 ↔ 420px 一欄，同一支元件 |
| 暗色 elevation / tone-mapping | MD3 五階 surface（越上層越亮）+ 語意色降飽和 |

## 檔案

```
before.html        對照組：硬編碼 hex、原色、!important 軍備競賽
after.html         重構版：六層 cascade + 三層 token + 雙主題
contrast_check.py  對比度檢查：OKLCH→sRGB→WCAG 相對亮度，斷言 24 組配對
audit.py           版面稽核：溢出／截斷／重疊／觸控目標／container query 實測
shot.py            截圖：亮暗 × 寬窄 4 組 + before 對照 2 組
shots/             輸出圖（device_scale_factor=2）
RUNLOG.md          執行紀錄（含 3 輪失敗與修正）
```

## 執行

`contrast_check.py` 只用標準函式庫，**任何 python3 都能直接跑**：

```bash
python3 contrast_check.py after.html              # WCAG 對比度（exit 0 = 全過）
python3 contrast_check.py after.html --json       # 機器可讀輸出
```

`audit.py` 與 `shot.py` 需要 `playwright`。**注意：不能直接用系統 `python3`**——
本機（Ubuntu + PEP 668）預設 python3 沒有裝 playwright，實測會得到
`ModuleNotFoundError: No module named 'playwright'`。兩種做法任選其一：

```bash
# 做法 A：用已裝好 playwright 的解譯器（本機實際使用的路徑）
~/.agent-reach-venv/bin/python audit.py           # 版面稽核（exit 0 = 無問題）
~/.agent-reach-venv/bin/python shot.py            # 產生 shots/ 6 張截圖

# 做法 B：在自己的 venv 裡裝
python3 -m venv .venv && . .venv/bin/activate
pip install playwright && playwright install chromium
python audit.py
```

無需金鑰、無需網路（安裝套件除外）。`audit.py` 與 `shot.py` 只讀檔、
只寫入自己的 `shots/` 目錄，重跑安全、不會動到其他資料。

## 設計系統摘要

**三層 token**（今日學習 #2 的實際應用）：

```
primitive   --p-neutral-950 … --p-neutral-50    純值，OKLCH，全系統鎖 H=250
            --p-brand-300 … --p-brand-700
            --p-space-1 … --p-space-6         4 的倍數
            --p-text-xs … --p-text-3xl        modular scale 1.125

semantic    --surface-0 … --surface-4          elevation 五階
            --text-primary/secondary/tertiary
            --accent / --accent-hover / --accent-subtle
            --state-good/warn/bad + 各自 -bg
            --border-subtle/default/strong

component   元件只引用 semantic（.btn 寫 var(--accent)，不寫色碼）
```

**亮/暗切換 = 換 token 集合**，不是改元件樣式。元件完全不知道主題的存在。

**暗色 elevation = 越上層越亮**（不是越暗）：

```css
--surface-0: oklch(0.170 …)   /* app 背景，非純黑 */
--surface-4: oklch(0.310 …)   /* modal，最亮 */
```

**語意色降飽和**（暗色模式 L↑ C↓，色相不變）：

```css
--state-good: light oklch(0.50 0.100 152) → dark oklch(0.74 0.100 152)
```

## 對比度結果（實測，非宣稱）

亮色 12 組全過，最低 4.78:1；暗色 12 組全過，最低 4.92:1。
非文字 UI（輸入框邊框、表格格線）皆 ≥3:1。
out-of-gamut token：0 個。

所有色值都是**程式實算**出來的 —— 品牌色的 C 值是「sRGB gamut 內最大值 × 0.96」，
不是照抄 Tailwind（照抄的話 5 個 token 全部超出 gamut，瀏覽器會 clip 並讓色相偏移）。

## 適用邊界

- 這是**單檔示範**，不是可部署的應用系統。真實專案應該把 token 抽到獨立的
  `tokens.css`，用 Style Dictionary 或 Tailwind preset 編譯成多平台格式。
- `contrast_check.py` 只解析**字面值** `oklch()` 與 `#hex`，不支援
  `color-mix()`、相對色語法 `oklch(from …)`、以及 runtime 計算的色值。
  專案若用到這些，需要擴充解析器（目前遇到會報「無法解析 token」而不是靜默跳過）。
- `audit.py` 檢的是幾何問題（溢出/重疊/截斷），**不判斷視覺美感**。
| 本次未做視覺驗證：環境未配置 vision provider，`vision_analyze` 無法使用。
  對比與版面用程式量化，但「好不好看」需要真人看截圖後給分。

> ⚠️ **2026-10-23 evaluate 更新**：上述限制已解除——evaluate 階段已用
> `vision_analyze` 實際看過 4 張截圖，並因此抓到兩個先前漏掉的缺陷
> （註冊的截圖是 container query 修正前的舊版、表格數字欄被 @layer 順序蓋掉
> 對齊而整欄歪掉）。兩者都已修正並重新產生截圖。

## 這次踩到的坑（都在 RUNLOG 有完整紀錄）

1. **帶 `container-type` 的元素不能查自己** —— container query 只作用於後代。
   MDN 沒在顯眼處寫這條，我憑直覺寫錯了，1440px 下容器查詢完全沒命中。
2. **`oklch\([^;]+\)` 的貪婪匹配** —— `[^;]+` 會吃到下一個分號，
   讓一個 `#ffffff` 宣告後面跟的 `oklch()` 被誤認為同一個 token。
3. **亮色模式完全沒被檢查卻回報「通過」** —— 字典「最後賦值勝」讓 dark 區塊
   永遠覆蓋 light。假綠燈比紅燈危險。
4. **負 margin 壓縮的是自己的空間，不是別人的** —— `margin-top: calc(-1 * x)`
   想把副標往上拉，實際上副標自己往上跑，於是跟標題重疊 8px。
5. **（evaluate 新增）`@layer` 順序贏過 class 具體度** —— `.num{text-align:right}`
   寫在 `@layer base`，`th,td{text-align:left}` 寫在 `@layer components`，
   base < components 讓低 layer 無條件落敗，`.num` 的 0-1-0 具體度形同虛設，
   結果三個數字欄全部靠左、與右對齊的表頭錯開 137–191px，肉眼明顯不對齊。
   **修法**：同一条規則放進同一個 layer。`audit.py` 已新增「表頭/資料文字墨水
   對位」檢查（用 `Range` 量真實文字範圍，不是元素框），並做過雙向回歸驗證：
   對未修正版報 3 個錯、對修正版報 0 個錯。
6. **（evaluate 新增）對齊檢查不能永遠比右緣** —— 我第一版檢查把
   left-aligned 欄位也拿去比右緣，於是「處室」vs「人事室」這種字數差
   被誤報（Δ=-18px）。**修法**：依 `text-align` 決定要比左緣還是右緣。
   連續兩次被自己的檢查器騙，值得記下來。