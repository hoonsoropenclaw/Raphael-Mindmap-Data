# 執行紀錄（RUNLOG）

練習題：把一個行政儀表板改成有設計 token 的版本（亮/暗雙主題、container query、
程式化對比度與版面稽核）。

環境：N100 Linux · Chromium（Playwright 內建）· Python 3.11
執行時間：2026-10-23

---

## 1. 對比度檢查（contrast_check.py）

### 第 1 次執行 — FAIL（10/12 通過）

```
-- 主題：dark（21 個 token）--
  OK    14.57:1  #E5E8EB on #14181B — 正文對卡片背景
  OK    15.56:1  #E5E8EB on #0D1013 — 正文對頁面背景
  OK     7.22:1  #A1A5A9 on #14181B — 次要文字對卡片背景
  OK     7.71:1  #A1A5A9 on #0D1013 — 次要文字對頁面背景
  OK    13.38:1  #E5E8EB on #1C2024 — 斑馬紋列上的正文
  OK     7.22:1  #6FA7EE on #14181B — 強調色文字對卡片背景
  OK     7.93:1  #090B0E on #6FA7EE — 按鈕文字對強調色底
  OK     6.52:1  #6FC087 on #162F1E — 達標徽章文字對其底色
  OK     6.31:1  #D7A955 on #3A2B0F — 觀察徽章文字對其底色
  OK     5.26:1  #E47C73 on #3E1E1C — 超標徽章文字對其底色
  FAIL   1.41:1  (需 ≥3.0)  #2F3338 on #14181B — 輸入框/分隔線對卡片
  FAIL   1.95:1  (需 ≥3.0)  #43484E on #14181B — 表格格線對卡片
  ⚠ out-of-gamut: 5 個（p-brand-300/400/500/600/700）
  10/12 通過 → FAIL
```

### 修檢查器本身的 3 個 bug（非設計問題）

| # | bug | 症狀 | 解法 |
|---|---|---|---|
| 1 | 註解裡寫的反面範例被當成違規命中 | 誤報 `filter: invert(1)`、`#22c55e`、`#ef4444` | 先 `COMMENT_RE.sub()` 剝掉 CSS 註解再掃描 |
| 2 | 亮色模式完全沒被檢查 | 12 項 SKIP 但程式回傳「通過」 | `parse_tokens` 改成依 theme 切區塊（`_theme_scope` / `_brace_block`） |
| 3 | `oklch\([^;]+\)` 的 `[^;]+` 吃到下一個分號 | `--surface-1: #ffffff; ... --state-good-bg: oklch(…)` 被誤認為一個 oklch 宣告 | 改成 `oklch\([^;()]*\)`，遇右括號即停 |

> 第 2 點是「假綠燈」最危險的形狀：檢查顯示通過，實際上一項都沒檢。
> 另外 `resolve()` 只對 aliases 呼叫，純字面值 token 從未寫回 `resolved`，
> 最後被誤判「未定義」→ 已改成 `for name in list(literals) + list(aliases)`。

### 第 2 次執行 — FAIL（16/24 通過，兩個主題都真的有在檢查了）

亮色新增的失敗（原本被 bug 2 藏住的）：
- `text-secondary` 4.19:1 / 4.01:1（需 ≥4.5）
- `state-good` 3.90:1、`state-warn` 3.75:1（需 ≥4.5）
- `border-default` 1.40:1、`border-strong` 1.89:1（需 ≥3.0）
- 8 個 out-of-gamut（5 個 primitive + 3 個引用它們的 semantic token）

暗色：
- `border-default` 1.41:1、`border-strong` 1.95:1（需 ≥3.0）

### 第 3 次執行 — PASS（24/24）

用程式實算 gamut 邊界與對比度後修正 token 值：

```
-- 主題：light（40 個 token）--
  OK    15.15:1  #23262A on #FFFFFF  — 正文對卡片背景
  OK    14.51:1  #23262A on #F9FAFB  — 正文對頁面背景
  OK     6.53:1  #595E64 on #FFFFFF  — 次要文字對卡片背景
  OK     6.25:1  #595E64 on #F9FAFB  — 次要文字對頁面背景
  OK    14.51:1  #23262A on #F9FAFB  — 斑馬紋列上的正文
  OK     5.12:1  #196EC9 on #FFFFFF  — 強調色文字對卡片背景
  OK     5.12:1  #FFFFFF on #196EC9  — 按鈕文字對強調色底
  OK     4.86:1  #2F7346 on #DBF2E0  — 達標徽章文字對其底色
  OK     6.21:1  #7B4C10 on #FBEBCF  — 觀察徽章文字對其底色
  OK     4.78:1  #A34943 on #FDE2DF  — 超標徽章文字對其底色
  OK     5.99:1  #5E646A on #FFFFFF  — 輸入框/分隔線對卡片（非文字 UI）
  OK     5.99:1  #5E646A on #FFFFFF  — 表格格線對卡片（非文字 UI）

-- 主題：dark（21 個 token）--
  OK    14.57:1  #E5E8EB on #14181B  — 正文對卡片背景
  OK    15.56:1  #E5E8EB on #0D1013  — 正文對頁面背景
  OK     7.22:1  #A1A5A9 on #14181B  — 次要文字對卡片背景
  OK     7.71:1  #A1A5A9 on #0D1013  — 次要文字對頁面背景
  OK    13.38:1  #E5E8EB on #1C2024  — 斑馬紋列上的正文
  OK     8.06:1  #7DB1F2 on #14181B  — 強調色文字對卡片背景
  OK     7.20:1  #1B222B on #7DB1F2  — 按鈕文字對強調色底
  OK     6.48:1  #79BD8C on #162F1E  — 達標徽章文字對其底色
  OK     6.79:1  #D9B06B on #3A2B0F  — 觀察徽章文字對其底色
  OK     5.26:1  #E47C73 on #3E1E1C  — 超標徽章文字對其底色
  OK     4.92:1  #81878D on #14181B  — 輸入框/分隔線對卡片（非文字 UI）
  OK     5.54:1  #8A9096 on #14181B  — 表格格線對卡片（非文字 UI）

  24/24 通過 → PASS     （out-of-gamut 0 個）
```

實際修正的 token 值（皆為程式實算，非目測）：

| token | 原值 | 新值 | 理由 |
|---|---|---|---|
| `--p-brand-300…700` | C = 0.105/0.165/0.214/0.245/0.220 | C = 0.094/0.147/0.185/0.161/0.137 | 原值全部超出 sRGB gamut，瀏覽器會 clip 並讓色相偏移（CSSWG #9449）。新值 = gamut 內最大值 × 0.96 |
| `--text-secondary`（亮） | `var(--p-neutral-600)` = 4.19:1 | `oklch(0.480 0.011 250)` = 6.25:1 | 未達 WCAG AA 正文 4.5:1 |
| `--p-green-600` | L=0.55 → 3.90:1 | L=0.50 → 4.86:1 | 徽章文字/底色未達標 |
| `--p-amber-600` | L=0.58 → 3.75:1 | L=0.46 → 6.21:1 | 黃色在淺底上天生難對比，需要更暗 |
| `--border-default`（亮） | `var(--p-neutral-300)` = 1.40:1 | `oklch(0.500 0.012 250)` = 5.99:1 | 非文字 UI 需 ≥3:1 |
| `--border-default`（暗） | L=0.320 = 1.41:1 | L=0.620 = 4.92:1 | 同上 |
| `--border-strong`（暗） | L=0.400 = 1.95:1 | L=0.650 = 5.54:1 | 同上 |

---

## 2. 版面稽核（audit.py）

### 第 1 次執行 — 10 個問題

```
-- wide (1440x900, light) --
   container query: gridColumns='1176px'   ← ★ 只有一欄！預期 4 欄
   ✗ 重疊 (2): H2 vs panel-sub (8px)、TABLE vs panel-sub (8px)
-- narrow (420x900, light) --
   ✗ 溢出 (1): TABLE elRight=517 > parentRight=420
   ✗ 重疊 (2): 同上
總計問題數：10
```

### ★ 最重要的發現：container 不能查自己

`gridColumns='1176px'` 表示 `@container kpi (width > 720px)` **完全沒命中**，
即使 1440px 視窗下容器寬度有 1176px。

診斷過程：

```
getComputedStyle('.kpi-grid').containerType  → 'inline-size'   （值存在！）
getComputedStyle('.kpi-grid').containerName  → 'kpi'
getBoundingClientRect().width                → 1176
CSS.supports('container-type','inline-size')  → true
```

在 layer 外插入探針測試：

```
@container kpi (width > 700px) { .kpi-grid { outline: 3px solid red } }
→ outline = 3px   （命中！）
```

差異只在於：**原本 `.kpi-grid` 自己帶 `container: kpi`，探針測的是沒有
container 的元素**。最小重現：

```html
.wrapper { container: kpi / inline-size; }
.grid { display: grid; }
@container kpi (width > 400px) { .grid { grid-template-columns: repeat(3,1fr); } }
.selfc { container: self / inline-size; display: grid; }
@container self (width > 300px) { .selfc { grid-template-columns: repeat(4,1fr); } }
```

實測結果：

```
容器外元素 .grid（正常用法）  → '266.656px 266.672px 266.672px'  ✔ 命中
容器自身 .selfc（自己查自己） → '800px'                            ✘ 未命中
容器的後代 .kid（查得到）     → flex                             ✔ 命中
```

**結論：帶 `container-type` 的元素不能查自己；container query 只作用於後代。**
這點 MDN 沒有寫在顯眼位置，是我今天寫進卡片時憑直覺以為可以，
實測才發現是錯的 —— 卡片稍後要更正。

修法：新增 `.kpi-wrap` 與 `.mini-wrap` 兩個純容器元素包住被查詢的元件。
`.mini-panel` 有同樣的 bug，一併修掉。

修完：

```
-- wide   -- gridColumns='285px 285px 285px 285px'  width_gt_700_matches: True
-- narrow -- gridColumns='156px'                   width_gt_700_matches: False
```

### 第 2 次執行 — 4 個問題

重疊修好了（`.panel-sub` 的負 margin `calc(-1 * space-2)` 改成正常 margin 流程），
剩下 4 個是「表格在窄視窗溢出」。這是**真的問題**，不只是稽核器誤報。

### 第 3 次執行 — 0 個問題

修法：`.table-scroll { overflow-x: auto }` 包住表格 + `table { min-width: 320px }`。
同時修正稽核器：捲動容器內的元素本來就會超出，那是設計不是破版，
但如果「需要捲動卻 overflow: hidden」則要抓（新增 `scrollOk` 檢查）。

最終輸出：

```
-- wide (1440x900, light)      -- ✓ 無版面問題、無 console 錯誤
-- narrow (420x900, light)     -- ✓ 無版面問題、無 console 錯誤
-- dark (1440x900, dark)       -- ✓ 無版面問題、無 console 錯誤
-- dark-narrow (420x900, dark) -- ✓ 無版面問題、無 console 錯誤
總計問題數：0
```

---

## 3. 截圖（shot.py）

```
wide         1440x900 light → after-wide.png         kpi-grid 4 欄, card padding=16px
narrow        420x900 light → after-narrow.png       kpi-grid 1 欄, card padding=12px
dark         1440x900 dark  → after-dark.png        kpi-grid 4 欄, card padding=16px
dark-narrow   420x900 dark  → after-dark-narrow.png  kpi-grid 1 欄, card padding=12px
before-wide  1440x900       → before-wide.png        （對照組）
before-narrow 420x900       → before-narrow.png      （對照組）
```

`cqi` 單位實測生效：1440px 視窗 padding=16px（clamp 上界），420px 視窗 padding=12px。
`device_scale_factor=2`（Retina 密度）。

**誠實揭露：本環境沒有配置 vision provider**
（`hermes setup` 未設定視覺模型，`vision_analyze` 回報
`No LLM provider configured for task=vision`）。
因此我**沒有真的用眼睛看過截圖**，改以 `audit.py` 的 DOM 量測替代。
對「溢出／重疊／截斷／對比」這四類問題，程式化量測比肉眼更嚴謹且可重現；
但對「視覺美感、使用者覺得喜不喜歡」這類判斷，本作品未經視覺驗證。

---

## 4. 重跑驗證

已重跑驗證：2026-10-23 拉斐爾（`hermes`）

```bash
cd workspace/practice/token-dashboard
python3 contrast_check.py after.html    # → 24/24 通過 → PASS, exit 0
python3 audit.py                        # → 總計問題數：0, exit 0
python3 shot.py                         # → 6 張截圖, exit 0
```

三個腳本全部 exit 0。所有數字皆為本次實際執行輸出，非預期值。