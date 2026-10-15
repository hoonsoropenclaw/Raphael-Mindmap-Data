# RUNLOG — merge_xlsx.py

## 環境
- Python 3.11.15（uv-managed cpython）
- pandas 3.0.6 / openpyxl 3.1.5
- 平台：Linux x86_64

## 執行紀錄

### 1. 產生測試資料
```
$ python _make_test_data.py test_data
已產生 6 個測試檔到 test_data
```
產出：6 個 .xlsx（3 個月收入、1 退款單、1 壞檔含 N/A、1 多分頁）

### 2. 合併（首次，無舊檔）
```
$ python merge_xlsx.py test_data --output out/merged.xlsx --no-dry-run
[merge_xlsx] 來源資料夾：test_data
[merge_xlsx] 輸出目標：out/merged.xlsx（dry-run=False）
  ✓ 寫出 out/merged.xlsx（28 列合併資料 + 3 張摘要表）

--- 摘要 ---
成功讀取：6 個檔案
合併後總列數：28
退款/負值警示：4 筆
```

### 3. 合併（第二次，驗證備份機制）
```
$ python merge_xlsx.py test_data --output out/merged.xlsx --no-dry-run
  ↻ 已備份舊檔到 out/merged.xlsx.bak
  ✓ 寫出 out/merged.xlsx（28 列合併資料 + 3 張摘要表）
```
✅ 既有檔自動被備份為 `.bak`，可重跑不損壞資料。

### 4. 空資料夾
```
$ python merge_xlsx.py test_data_empty --output out/empty.xlsx --no-dry-run
在 test_data_empty 找不到 .xlsx / .xlsm 檔案
exit 0
```
✅ 有可行動的錯誤訊息，不靜默失敗。

### 5. 驗證輸出
讀回 out/merged.xlsx：
- 分頁：`['合併資料', '檔案摘要', '退款警示', '本次執行']`
- 退款警示：4 筆負值（含欄名「退款金額」自動偵測）
- 檔案摘要：JSON 含每檔數值欄合計
- 本次執行：含 timestamp、筆數

## 測試案例對應 SOP §2.1
| 案例 | 狀態 | 說明 |
|------|------|------|
| 正常（同 schema 多檔） | ✅ | 3 個月收入檔正確合併為 15 列 |
| 空/缺資料 | ✅ | 空資料夾給出可行動錯誤 |
| 異常格式 | ✅ | 壞檔的 N/A 留 None，不破壞合併 |
| 退款樣本 | ✅ | 退款單 4 筆負值全部偵測 |

## 已知限制
- 跨檔 schema 不一致時以 None 補齊（不嘗試 schema 對齊）
- 第一頁第一列當標題；標題錯位需手動修
- 大檔（>100MB）建議先用 `read_only=True` 模式

## 已重跑驗證
已重跑驗證：2026-10-16 hermes（cron 自動學習循環）