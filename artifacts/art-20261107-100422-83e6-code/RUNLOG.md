# 執行紀錄

## 1. 環境

- N100 Linux · Chromium（Playwright 內建）· Python 3.12
- 金鑰：無。全部檢查器不需要金鑰、不需要網路。

## 2. 機械檢查的實際執行結果

```bash
$ python3 a11y_check.py after.html --json      → EXIT=1
$ python3 audit.py                              → EXIT=1
$ python3 contrast_check.py after.html --json   → EXIT=1
```

- a11y_check.py：發現 16 項（阻擋 13／建議 3）
- audit.py（版面：溢出／截斷／重疊／觸控目標／console 錯誤）：總計問題數：16
- contrast_check.py：低於 WCAG 門檻 9 項

## 3. 檢查器的涵蓋邊界（誠實揭露）

涵蓋：鍵盤可操作性（2.1.1／4.1.2）、可及名稱、目標大小（2.5.5／2.5.8）、
表格標頭關聯（1.3.1）、元件邊界對比（1.4.11）、焦點可見性（2.4.7）、
略過重複區塊（2.4.1）、aria-pressed 與可及名稱一致性（4.1.2／3.2.2）、
文字對比（1.4.3）、版面溢出／截斷／重疊／觸控目標、console 錯誤。

**不涵蓋**：螢幕閱讀器實機測試（VoiceOver／NVDA）、動態內容廣播、
翻譯與語言正確性、色彩以外的視覺障礙情境、實際使用者的障礙情境、
純設計美學（那屬於人工視覺審查，不屬於機械可檢）。

「EXIT=0」只代表上面列出的項目全過，**不代表頁面完全無缺陷**。

## 4. 產出檔案

after.html、before.html、a11y_check.py、audit.py、contrast_check.py、shot.py、
6 張截圖（after：亮／暗 × 1440／420；before：亮 × 1440／420）、
RUNLOG.md（本檔）、verification_summary.json（機器可讀摘要）。
