# RUNLOG — scout 2026-10-26 A/B（baseline版）

練習題：把 `markmead/hyperui`（MIT，SHA `252efcfe39161db6e67cd877da001ee248d2bbf6`）
`.claude/skills/accessibility-review/SKILL.md` 的 WCAG 2.1 AA 稽核方法，實際套用在
2026-10-23 的行政儀表板（token-dashboard `after.html`）上，做 A/B。

- 本版角色：**baseline**
- 原始 2026-10-23 版本：版面與對比都已修好，但**無障礙面向完全未處理**

## 1. 環境

- N100 Linux · Chromium（Playwright 內建）· Python 3.12
- 金鑰：無。全部檢查器不需要金鑰、不需要網路。
- hyperui 為純 Markdown skill 套件，**未執行任何下載的程式碼**（符合 playbook/05「對 skills/prompt 類不用執行」）。

## 2. 三支機械檢查的實際執行結果

```bash
$ python3 a11y_check.py after.html          → EXIT=1
$ python3 audit.py                           → EXIT=0
$ python3 contrast_check.py after.html       → EXIT=0
```

- a11y_check.py：發現 14 項（阻擋 6／建議 8）
- audit.py（版面：溢出／截斷／重疊／觸控目標／console 錯誤）：總計問題數 0
- contrast_check.py：24/24 通過 → PASS

## 3. a11y_check.py 的涵蓋邊界（誠實揭露）

涵蓋：2.1.1／4.1.2（鍵盤可操作性、非原生 role=link、可及名稱）、1.3.1（th scope）、
1.4.11（元件邊界對比）、2.4.1（略過重複區塊）、2.4.7（焦點可見性）、
2.5.5／2.5.8（目標大小）、3.2.2（aria-pressed 與可及名稱一致性）。

**不涵蓋**：螢幕閱讀器實機測試（VoiceOver/NVDA）、動態內容廣播、翻譯與語言正確性、
色彩以外的視覺障礙情境、實際使用者的障礙情境、oklch 不支援時 canvas fillStyle 的靜默退化。

「EXIT=0」只代表上面列出的項目全過，**不代表頁面完全無障礙問題**。

## 4. 雙向回歸驗證（缺陷版 EXIT≠0 / 修好版 EXIT=0）

```
[1] 缺陷版（本版 after.html，基準版（阻擋級缺陷仍在））：a11y_check.py EXIT=1
[2] 修好版（另一版 after.html，候選版）：a11y_check.py EXIT=0
```

兩版檔案都在本工作區（`deliver-baseline/after.html`、`deliver-candidate/after.html`），
可逐字元 diff 驗證：唯一差異是無障礙屬性與目標尺寸。

## 5. 控制變因驗證（兩版逐項比對）

```
$ diff <(grep -oE "\-\-[a-z-]+: oklch\([^)]*\)" deliver-baseline/after.html | sort) \
       <(grep -oE "\-\-[a-z-]+: oklch\([^)]*\)" deliver-candidate/after.html | sort)
→ 無差異（20/20 個 color token 逐一相同）
$ diff deliver-baseline/after.html deliver-candidate/after.html | wc -l
→ 73 行（全部是無障礙屬性、skip link、target size、border-left 指示）
```

內容字串計數（兩版逐一相同）：「案件總數」1、「資訊維運」2、「總覽」2、「匯出報表」1、「各處室案件處理概況」1

## 6. 產出檔案

after.html、a11y_check.py、audit.py、contrast_check.py、4 張截圖（亮/暗 × 1440/420）、
RUNLOG.md（本檔）、verification_summary.json（機器可讀摘要）。
