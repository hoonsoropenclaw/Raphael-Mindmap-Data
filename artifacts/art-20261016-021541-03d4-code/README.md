# 合併 Excel 工具 (merge_xlsx.py)

辦公自動化：admin 軌練習作品。給定一個資料夾，合併裡面所有 `.xlsx` / `.xlsm`
成單一檔案，並產生 3 張摘要工作表（檔案摘要、退款警示、本次執行）。

## 安裝
```bash
pip install pandas openpyxl
```

## 使用
```bash
# 先看會做什麼（不寫檔）
python merge_xlsx.py ./my_data

# 真的寫出檔案（會自動備份既有同名檔）
python merge_xlsx.py ./my_data --output ./out/merged.xlsx --no-dry-run
```

## 設計原則
- **預設 dry-run**：避免覆蓋毀損既有檔案；要執行寫入明確加 `--no-dry-run`
- **跨平台**：不依賴 pywin32 / COM，純 openpyxl + pandas
- **退款警示**：自動偵測欄名含 `退款 / 退費 / 折讓 / 溢付` 的負值列
- **可重跑**：已存在輸出檔會先備份為 `.bak` 再覆寫
- **跨 schema 安全**：欄位不一致以 None 補齊，不丟資料

## 參數
- `input_folder`（必）：要合併的資料夾
- `--output`, `-o`：輸出檔（預設 `merged.xlsx`）
- `--dry-run`：預設啟用，不寫檔
- `--no-dry-run`：真的要寫檔（會先備份）

## 測試
見 `RUNLOG.md`——4 個案例（正常、空、異常、含退款樣本）全綠。