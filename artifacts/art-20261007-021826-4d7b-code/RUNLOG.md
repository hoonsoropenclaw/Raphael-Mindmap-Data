# RUNLOG — merge_xlsx.py

執行環境：Linux 6.8.0-136-generic，Python 3.12（.venv），openpyxl 3.1.5、pandas 3.0.6。

## T1 正常（happy path）

```bash
python merge_xlsx.py --input inputs --output output/t1.xlsx
```

結果：`exit=0`

```
找到 3 個檔案:
  - 學務處_2026-08.xlsx
  - 教務處_2026-07.xlsx
  - 總務處_2026-09.xlsx

=== 摘要 ===
總筆數: 30, 總金額: 84300
                  筆數      總金額
來源檔
學務處_2026-08.xlsx  10  28100.0
教務處_2026-07.xlsx  10  28100.0
總務處_2026-09.xlsx  10  28100.0

寫入完成: output/t1.xlsx
```

讀回驗收（`openpyxl.load_workbook`）：
- 工作表 = `['原始合併', '摘要']`
- 原始合併：31 列 × 5 欄（標題 + 30 筆）
- 摘要：KPI 區（總筆數/總金額/來源檔數）+ by_src 表格
- 圖表：1 張 BarChart 已嵌入「摘要」工作表

## T2 邊界：空資料夾

```bash
mkdir -p empty
python merge_xlsx.py --input empty --output output/t2.xlsx
```

結果：`exit=1`，stderr：
```
錯誤：資料夾內沒有 .xlsx: workspace/practice-merge-xlsx/empty
```

✅ 給可行動提示（指明哪個資料夾），未崩潰。

## T3 邊界：缺欄位的檔

```bash
# 建一個缺欄位的檔
python -c "import pandas as pd; pd.DataFrame({'項目':['x'],'金額':[100]}).to_excel('bad/缺欄位.xlsx', index=False)"
python merge_xlsx.py --input bad --output output/t3.xlsx
```

結果：`exit=1`：
```
錯誤：缺欄位.xlsx 缺少必要欄位: ['備註', '日期']（需要 ['備註', '日期', '金額', '項目']）
```

✅ 指出哪個檔缺什麼欄位、應該要哪些欄位。

## T4 異常：輸入資料夾不存在

```bash
python merge_xlsx.py --input /tmp/不存在_xyz --output output/t4.xlsx
```

結果：`exit=1`：
```
錯誤：找不到輸入資料夾: /tmp/不存在_xyz
```

✅ 早失敗，未建立任何 output。

## T5 邊界：覆寫既有 output（驗證備份）

```bash
python merge_xlsx.py --input inputs --output output/t1.xlsx  # 第一次
python merge_xlsx.py --input inputs --output output/t1.xlsx  # 第二次（覆寫）
ls output/t1.xlsx.bak
```

結果：
- exit=0 兩次都成功
- `output/t1.xlsx.bak` 自動產生

✅ 破壞性動作（覆寫）有自動備份，符合 SOP「可重跑不損壞資料」。

## 驗收總結

| 測試 | 情境 | 退出碼 | 訊息可行動 |
|---|---|---|---|
| T1 | 3 個正常檔 | 0 | ✅ 摘要印出、圖表存在 |
| T2 | 空資料夾 | 1 | ✅ 指明資料夾路徑 |
| T3 | 缺欄位 | 1 | ✅ 指明哪個檔缺什麼 |
| T4 | 不存在資料夾 | 1 | ✅ 早失敗，未建輸出 |
| T5 | 覆寫既有 | 0 | ✅ 自動備份為 .bak |

符合 SOP 要求：
- 至少 3 組輸入 ✅（T2/T3/T4 都是邊界）
- 破壞性動作（覆寫）需可逆 ✅（自動 .bak）
- 金鑰走環境變數 ✅（本腳本無金鑰需求）
- 錯誤訊息可行動 ✅（含檔名、欄位、預期值）
- 實際執行紀錄 ✅（本檔）