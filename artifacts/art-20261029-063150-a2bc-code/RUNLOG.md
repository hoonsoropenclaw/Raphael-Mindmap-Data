# 執行紀錄

## 1. 環境

- N100 Linux · Chromium（Playwright 內建）· Python 3.12
- 金鑰：無。全部檢查器不需要金鑰、不需要網路。

## 2. 三支機械檢查的實際執行結果

```bash
$ python3 a11y_check.py after.html          → EXIT=0
$ python3 audit.py                           → EXIT=0
$ python3 contrast_check.py after.html       → EXIT=0
```

- a11y_check.py：發現 1 項（阻擋 0／建議 1）
- audit.py（版面：溢出／截斷／重疊／觸控目標／console 錯誤）：總計問題數：0
- contrast_check.py：24/24 通過 → PASS

## 3. a11y_check.py 的涵蓋邊界（誠實揭露）

涵蓋：2.1.1／4.1.2（鍵盤可操作性、非原生 role=link、可及名稱）、1.3.1（th scope）、
1.4.11（元件邊界對比）、2.4.1（略過重複區塊）、2.4.7（焦點可見性）、
2.5.5／2.5.8（目標大小）、3.2.2（aria-pressed 與可及名稱一致性）。

**不涵蓋**：螢幕閱讀器實機測試（VoiceOver/NVDA）、動態內容廣播、翻譯與語言正確性、
色彩以外的視覺障礙情境、實際使用者的障礙情境、oklch 不支援時 canvas fillStyle 的靜默退化。

「EXIT=0」只代表上面列出的項目全過，**不代表頁面完全無障礙問題**。

## 4. 產出檔案

after.html、a11y_check.py、audit.py、contrast_check.py、4 張截圖（亮/暗 × 1440/420）、
RUNLOG.md（本檔）、verification_summary.json（機器可讀摘要）。
