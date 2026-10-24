# merge_xlsx v2 — 合併資料夾內多個 Excel 並產生摘要

把一個資料夾裡所有 `.xlsx` 合併成一份，並輸出摘要（來源追溯、數值合計、退款/負值警示）。
目標環境：**Windows**（行政／辦公自動化情境）；跨平台（Windows / macOS / Linux）都能跑。

## 安裝

```bash
pip install openpyxl
```

只用到 `openpyxl` 一個套件（不用 pandas）。

## 執行

```bash
# 1) 先預覽（預設 dry-run，不寫任何檔案）
python merge_xlsx.py <輸入資料夾>

# 2) 真的輸出
python merge_xlsx.py <輸入資料夾> --apply -o out/merged.xlsx

# 3) 同時輸出摘要 CSV（給 Excel 開）
python merge_xlsx.py <輸入資料夾> --apply \
    -o out/merged.xlsx --summary-csv out/summary.csv

# 4) 摘要 CSV 用 cp950（給舊系統／舊 Excel）
python merge_xlsx.py <輸入資料夾> --apply \
    --summary-csv out/summary.csv --csv-encoding cp950
```

## 參數

| 參數 | 預設 | 說明 |
|---|---|---|
| `input_folder` | 必填 | 要合併的資料夾（只讀這個目錄一層，不遞迴） |
| `-o, --output` | `merged.xlsx` | 輸出 Excel 路徑 |
| `--summary-csv` | 無 | 另存摘要 CSV 的路徑 |
| `--csv-encoding` | `utf-8-sig` | 摘要 CSV 編碼：`utf-8-sig` / `cp950` / `utf-8` |
| `--apply` | 關 | 真的寫檔（**預設 dry-run**） |
| `--no-backup` | 關 | 覆寫前不建立時間戳備份 |

**沒有 `--apply` 就絕對不會寫任何檔案**（破壞性動作一律需明確旗標）。

## 輸出內容（6 個工作表）

| 分頁 | 內容 |
|---|---|
| `合併資料` | 所有分頁資料串接（欄位取聯集，缺漏欄位留白），附 `_來源檔` / `_來源分頁` / `_來源列號` |
| `檔案摘要` | 每檔每分頁：資料列數、欄位數、狀態、錯誤訊息、**缺漏欄位**、**獨有欄位**、**警告** |
| `數值合計` | 每欄合計 + 非空數值格數 |
| `退款警示` | 欄名含退款關鍵字（退款/退費/折讓/溢付/沖銷/refund/credit）**或**數值為負 |
| `本次執行` | 執行時間、輸入、輸出、編碼、各項統計 |
| `略過檔案` | 被略過的檔案與原因（`.xls`/`.xlsm` 等不支援格式、輸出檔本身）——不靜默略過 |

## 這版（v3）跟前版差在哪

| 項目 | v1 | v2 | v3 |
|---|---|---|---|
| 寫檔 | 直接 `wb.save()` 覆蓋 | 暫存檔 + fsync + `os.replace` | 同 v2，但 **fsync 用可寫 handle**（Windows 才不會 EBADF 崩潰） |
| 備份 | 固定 `.bak`（每次被覆蓋＝沒版本） | 時間戳備份 `merged.bak-YYYYMMDD-HHMMSS.xlsx` | 時間戳備份 `merged.bak-YYYYMMDD-HHMMSS`（**不保留 .xlsx**）＋ 明確排除，**重跑不會自我合併** |
| 摘要 CSV | 無 | `--summary-csv`，預設 **utf-8-sig（含 BOM）**，Excel 直接開不亂碼 | 同 v2 |
| 路徑檢查 | 無 | Windows 禁用字元 / 保留裝置名 / **MAX_PATH 260** 預檢 | 同 v2 |
| 欄位不一致 | `pd.concat` 靜默補 NaN | 欄位聯集 + 缺漏/獨有欄位報告 | 同 v2 ＋ **重複欄名自動去重**（不再遺失資料） |
| 來源追溯 | 無 | `_來源檔`/`_來源分頁`/`_來源列號` | 同 v2 ＋ **列號對齊原始 Excel**（空列不再造成偏移） |
| 依賴 | pandas + openpyxl | 只要 openpyxl | 同 v2 ＋ pytest（僅測試用） |
| 壞檔 | 略過 | 略過並記錄可行動錯誤訊息 | 同 v2 |
| 不支援格式 | 靜默略過 | 回報略過原因 | 同 v2 |
| 寫入失敗 | 崩潰 | 崩潰（裸 traceback） | **可行動訊息 + exit code 3** |
| 測試開箱狀態 | — | 紅燈（測試資料未交付，12 failed） | **綠燈**（conftest.py 自動產生測試資料，42 項全綠） |

## Windows 使用注意

1. **預設輸出 CSV 是 utf-8-sig（有 BOM）** — Excel 開會正確顯示繁體中文。
   若要餵給舊系統（cp950），加 `--csv-encoding cp950`。
2. **`.xls` 舊格式不支援** — 請先在 Excel「另存為」`.xlsx`。程式遇到時會明確提示。
3. **路徑超過 260 字元** — 程式會擋下並提示解法（縮短路徑，或開啟
   `LongPathsEnabled` registry + 程式 manifest 標 `longPathAware`）。
4. **含空白的路徑要加引號**：`python merge_xlsx.py "C:\我的文件\經費"`
5. **Excel 開著檔時**會產生 `~$xxx.xlsx` 鎖檔 —— 程式會自動略過。
6. **加密（密碼保護）的 xlsx 讀不了** — 請先另存為無密碼版本。

## 測試

```bash
pip install pytest
pytest -q
```

42 項測試全綠。**測試資料由 `conftest.py` 自動產生**，不需要先手動執行任何指令——
在乾淨目錄 clone 後直接 `pytest -q` 就是全綠。

> 這個設計是 2026-10-24 評審修補的：舊版把三組測試資料當成手動前置步驟，
> 結果交付物本身開箱是紅的（12 failed），「36 項全綠」的宣稱在交付物上不可重現。

測試涵蓋：正常合併、空/缺資料、損毀/偽裝/密碼 xlsx、原子寫入與時間戳備份、
Windows 路徑預檢、CSV 編碼、CLI 端到端、略過檔案回報，以及 5 條針對真實缺陷的
回歸測試（重跑自我合併、舊版備份檔排除、來源列號對位、重複表頭不遺失資料、
fsync 使用可寫 handle）。

## 已知限制

- 整個資料夾一次讀進記憶體（幾十萬列以內沒問題，上百萬列需改串流）
- 公式不會重算（讀的是 Excel 存下的值）
- 只支援 `.xlsx`；`.xls`／`.xlsm` 會被略過並在「略過檔案」分頁回報原因
- 只處理輸入資料夾一層（不遞迴子資料夾）
- **尚未在真實 Windows 主機實跑**：Windows 專屬行為（MAX_PATH、LongPathsEnabled、
  Excel 鎖檔）是用 PureWindowsPath 在 Linux 上模擬驗證的。已知的 Windows 差異
  （`os.fsync` 需要可寫 handle）已依 maigret PR #3143 的結論修正並加回歸測試，
  但仍建議在真實 Windows 上跑一次完整流程再正式使用。
