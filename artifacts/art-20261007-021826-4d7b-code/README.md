# merge_xlsx — 合併多個 Excel 並產生摘要

## 用途
把資料夾內多個 `.xlsx`（每個檔一個工作表，含 `項目`、`金額` 等欄位）合併成一份帶摘要與長條圖的輸出 Excel。

## 安裝
```bash
pip install openpyxl pandas
```

## 執行
```bash
python merge_xlsx.py --input <資料夾> --output <output.xlsx>
```

可選：
- `--no-backup`：覆寫 output 時不備份（預設會自動備份成 `.bak`）

## 輸入格式
每個 xlsx 必須含以下欄位（順序不限）：
- `項目`（str）
- `日期`（可為字串或日期型別）
- `金額`（數字，缺值會視為 0）
- `備註`（可空）

排除 `~$` 開頭的 Excel 暫存檔。

## 輸出格式
兩個工作表：
1. **原始合併**：所有檔 concat，附 `來源檔` 欄
2. **摘要**：
   - KPI（總筆數、總金額、來源檔數）
   - 各來源檔的筆數與金額彙總
   - Top 5 高金額項目
   - 各來源檔總金額長條圖（BarChart）

## 退出碼
| 碼 | 意義 |
|---|---|
| 0 | 成功 |
| 1 | 使用者錯誤（資料夾不存在/空/欄位缺） |
| 2 | 程式未預期錯誤 |

## 已知限制
- 欄位缺失整個檔案被拒（不接受部分讀取）
- 中文字型靠開啟端 Office（字體）顯示；本腳本未綁字型
- 一次性讀全部檔進記憶體；上千萬列需改 chunked 處理

## 參考
- 卡片 `office-automatio--openpyxl-與-pandas-處理-excel`
- 卡片 `office-automatio--排程與錯誤通知`