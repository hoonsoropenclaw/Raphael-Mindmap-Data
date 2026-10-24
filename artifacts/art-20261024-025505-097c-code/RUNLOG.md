# RUNLOG — merge_xlsx v2（合併 Excel 並產生摘要）

日期：2026-10-24
環境：N100 Linux，Python 3.12.3（`/home/hoonsoropenclaw/raphael-harness/.venv/bin/python3`）
套件：openpyxl 3.1.5 / pytest 9.1.1
目標環境：使用者的 Windows（admin 軌，辦公自動化）

---

## 執行紀錄（全部實際跑過，輸出為真實結果）

### 1. 產生測試資料

```
$ python3 make_test_data.py
正常情境 → .../test_data
空資料情境 → .../test_data_empty
異常格式情境 → .../test_data_bad
完成
```

### 2. 測試套件（36 項全綠）

```
$ python3 -m pytest test_merge_xlsx.py -q
....................................                                     [100%]
36 passed in 0.43s
```

涵蓋範圍：
- 正常情境（3 個分頁、欄位聯集、數值合計、退款/負值警示、缺漏/獨有欄位）
- 空/缺資料情境（只有表頭、資料夾無 xlsx、輸入資料夾不存在）
- 異常格式情境（損毀 xlsx、偽裝 xlsx、密碼保護 xlsx、Excel 鎖檔 `~$`）
- 原子寫入（成功替換、不留暫存檔、失敗時舊檔完好、時間戳備份）
- Windows 路徑預檢（禁用字元、保留裝置名、MAX_PATH 260、UNC、跨 OS 守衛）
- CSV 編碼（utf-8-sig BOM、cp950、csv 模組 roundtrip）
- CLI 端到端（dry-run 不寫檔、apply 產出 6 分頁、重跑 idempotent、非法檔名擋下）
- 略過檔案回報（.xls/.xlsm 被回報原因、.csv 不列入噪音）

### 3. dry-run 預覽（不寫檔）

```
$ python3 merge_xlsx.py test_data
[merge_xlsx] 輸入資料夾：test_data
[merge_xlsx] 輸出 Excel：merged.xlsx
[merge_xlsx] 模式：dry-run（不寫檔）
  解析成功：2 個檔案 / 3 個分頁
  聯集欄位（6）：單號、處室、金額、數量、部門、備註
  合併後總列數：8
  退款/負值警示：1 筆

[dry-run] 沒有寫任何檔案。要真的輸出請加 --apply。
```

### 4. 實際輸出（--apply）

```
$ python3 merge_xlsx.py test_data --apply -o out/merged.xlsx --summary-csv out/summary.csv
[merge_xlsx] 模式：APPLY（會寫檔）
  解析成功：2 個檔案 / 3 個分頁
  聯集欄位（6）：單號、處室、金額、數量、部門、備註
  合併後總列數：8
  退款/負值警示：1 筆
  ✓ 寫出 out/merged.xlsx
  ✓ 寫出 out/summary.csv（utf-8-sig）
```

### 5. 重跑（idempotent + 時間戳備份）

```
$ python3 merge_xlsx.py test_data --apply -o out/merged.xlsx --summary-csv out/summary.csv
  ✓ 寫出 out/merged.xlsx
  ↻ 舊檔已備份到 out/merged.bak-20261024-025218.xlsx
  ✓ 寫出 out/summary.csv（utf-8-sig）
```

### 6. 數字回算驗證（不只看 exit code）

```python
# 從合併資料逐列把「金額」加總，與預期 2450+2650+1299 比對
回算 金額合計 = 6399 （預期 2450+2650+1299 = 6399 ）

# 交叉驗證：從「數值合計」分頁加總 vs 從「合併資料」加總
--- 數值合計（金額欄）---
  2026-01_2月經費.xlsx/一月: 2450
  2026-01_2月經費.xlsx/二月: 2650
  2026-03_3月經費.xlsx/三月: 1299
  三個分頁合計 = 6399 == 合併資料合計 6399 → True
```

其他驗證結果：
- 退款警示：僅 1 筆 `('2026-03_3月經費.xlsx', '三月', 3, '金額', -300, '負值')` — 與測試資料一致
- 檔案摘要缺漏/獨有欄位：三月缺「數量」、獨有「部門、備註」— 與手算一致
- `summary.csv` 前 3 bytes = `b'\xef\xbb\xbf'` → **BOM 存在**（Excel 開不亂碼）
- `summary_cp950.csv` 前 3 bytes = `b'\xc0\xc9\xa6'` → 無 BOM、cp950 解碼正常

### 7. 錯誤情境（全部實跑，確認可行動訊息）

| 情境 | exit | 訊息 |
|---|---|---|
| 3 個壞 xlsx（損毀/偽裝/密碼） | 4 | 「無法開啟 … BadZipFile … 常見原因：檔案被 Excel 鎖住（關掉 Excel 再試）、檔案損毀、或密碼保護（先另存為無密碼版本）」 |
| 空資料夾 | 2 | 「內找不到 .xlsx 檔案。請確認資料夾正確、檔案副檔名是 .xlsx（.xls 舊格式請先在 Excel 另存為 .xlsx）」 |
| Windows 非法檔名 `C:\out\bad?name.xlsx` | 2 | 「檔名『bad?name.xlsx』含 Windows 禁用字元 ?」 |
| Windows 超長路徑（303 字元） | 2 | 「路徑長度 303 超過 Windows MAX_PATH 260；解法：改用較短路徑、或開啟 LongPathsEnabled + 程式 manifest 標 longPathAware」 |
| Windows 路徑在 Linux 上執行 | 2 | 「是 Windows 形式，但目前作業系統是 posix（非 Windows）… 請改用本機絕對路徑，或在 Windows 上執行本程式」 |
| 輸入資料夾不存在 | 2 | 「不是資料夾。請確認路徑是否存在，Windows 下可用引號包住含空格的路徑。」 |

---

## 本輪實作中發現並修掉的 4 個真實缺陷

### 缺陷 1（程式邏輯 bug）：「獨有欄位」永遠是空的
「獨有欄位」原本定義為 `sheet.headers - union`。但 union 本身就是所有分頁欄位的聯集，
所以這個集合恆為空 → 該欄永遠空白，等於沒有這個功能。
**修法**：改成相對於「其他所有分頁欄位的聯集」，只有自己有的才算獨有。
由 pytest `test_missing_and_extra_columns_reported` 抓到。

### 缺陷 2（檢查器假陽性）：把磁碟機代號 `C:\` 當成檔名檢查
第一版 `validate_windows_path` 用 `wp.parts` 逐層檢查禁用字元，但 `C:\` 這個 anchor
本身含 `:` 和 `\`，被誤報成「檔名含禁用字元」→ 合法路徑 `C:\out\merged.xlsx` 被擋下。
**修法**：改用 `wp.anchor` 判斷並跳過 anchor 段。已補 `test_drive_letter_is_not_treated_as_filename` 做回歸保護。

### 缺陷 3（真實副作用，非 Windows 上寫出怪檔）
在 Linux 上跑 `-o 'C:\out\merged.xlsx'` 會真的建立一個檔名含反斜線的檔案
`C:\out\merged.xlsx`（8.9KB），輸出落在 cwd 而非預期磁碟機位置。
**修法**：加跨 OS 守衛 —— 非 Windows 上給 Windows 形式路徑直接擋下並說明原因。
已補 `test_windows_path_on_posix_is_rejected`，並確認擋下後 `ls | grep 'C:'` 為 0。

> 缺陷 2、3 都是「檢查器自身的判準沒對齊它要量測的東西」——
> 這跟 2026-10-23 那輪（audit.py 對位檢查誤報）是同一類病，已寫進本 RUNLOG 與 README。

### 缺陷 4（使用者體驗缺陷）：不支援的副檔名被靜默略過
第一版只支援 `.xlsx`，遇到 `.xls` / `.xlsm` 直接跳過、不留任何痕跡。
使用者看到「我的檔怎麼沒被合併」完全無從判斷原因。
**修法**：新增「略過檔案」分頁 + 終端機提示，逐檔回報略過原因
（如「副檔名 .xls 不支援（.xls 舊格式請在 Excel 另存為 .xlsx）」）。
過程中還發現一次自己的判斷錯：最初把 `.csv` 也放進略過清單，
但 .csv 不是 Excel 家族、列在那裡只是噪音 → 已從 `OTHER_EXCEL_SUFFIXES` 移除，
並補測試 `test_unsupported_suffix_is_reported_not_silently_dropped` 做雙向驗證。

---

## 已知限制（誠實列出，未修）

1. **只支援 .xlsx**：.xls 舊格式不支援。程式的錯誤訊息已提示「請在 Excel 另存為 .xlsx」，
   但沒有自動轉檔。Windows 上若使用者有大量 .xls，這是明確的功能缺口。
2. **密碼保護 xlsx 無法讀**：openpyxl 不支援加密檔。錯誤訊息已說明「先另存為無密碼版本」，
   但沒有自動請示密碼或跳過提示。
3. **沒有公式重算**：用 `data_only=True` 讀取，若來源檔的公式從未被 Excel 開過，
   讀到的是快取值或 None，不會重算。
4. **未在真實 Windows 環境實跑**：本次驗證環境是 Linux。Windows 專屬行為
   （MAX_PATH、LongPathsEnabled、Excel COM 開檔）是用 PureWindowsPath 在 Linux 上模擬驗證的，
   實際 Windows 上仍建議再跑一次。
5. **記憶體用量**：整個資料夾一次讀進記憶體。幾萬列以內沒問題，
   上百萬列會吃記憶體（需改成串流處理）。

---

## 交付檔案

| 檔案 | 說明 |
|---|---|
| `merge_xlsx.py` | 主程式（v3） |
| `conftest.py` | pytest 設定：自動產生三組測試資料（開箱即綠） |
| `test_merge_xlsx.py` | pytest 測試套件（42 項） |
| `make_test_data.py` | 測試資料產生器 |
| `out/merged.xlsx` | 實際輸出（6 分頁） |
| `out/summary.csv` | 摘要 CSV（utf-8-sig，含 BOM） |
| `README.md` | 使用說明 |
| `RUNLOG.md` | 本檔 |

## 輸出工作表（6 個）

`合併資料` / `檔案摘要` / `數值合計` / `退款警示` / `本次執行` / `略過檔案`

---

## 2026-10-24 評審後的修補（第 2 輪）

以下 6 個缺陷是 evaluate 階段實測發現的，全部已修 + 補回歸測試。

### 缺陷 5（Windows hard fail）：`os.fsync` 用唯讀 handle → EBADF

**這是最嚴重的一條：在目標平台 Windows 上 `--apply` 100% 崩潰，一個檔案都產不出來。**

舊碼：
```python
with open(tmp_path, "rb") as fh:
    os.fsync(fh.fileno())
```

Windows 的 `os.fsync()` 底層是 MSVCRT `_commit()` → `FlushFileBuffers()`，
而 `FlushFileBuffers` 要求 handle 具備 `GENERIC_WRITE` 權限；
用 `"rb"` 開的 handle 只有 `GENERIC_READ` → `_commit` 回 `EBADF` →
`OSError: [Errno 9] Bad file descriptor`。
POSIX 則允許對 `O_RDONLY` fd 做 fsync，所以 **Linux 上完全正常、CI 抓不到**。

外部佐證：`soxoj/maigret` PR #3143（2026-10-04 merged）修的是完全同一種 bug，
原文：「os.fsync on Windows is FlushFileBuffers, which needs write access and raises
EBADF on a handle opened read-only. POSIX permits the operation, so the bug was not
detected by the Ubuntu-based CI workflow.」該 PR 的回歸測試斷言的是
「flush 用的 handle 必須可寫」，而不是斷言最終檔案存在。

**修法**：`open(tmp_path, "rb+")`，並補回歸測試
`test_fsync_uses_writable_handle`（用 monkeypatch 追蹤 open 的 mode，斷言含 `+`）。

> 教訓：**Windows 專屬行為只有真實 Windows 才驗得到**，PureWindowsPath 模擬不了
> 作業系統核心 API 的權限檢查。這類差異要靠「讀作業系統文件 + 找同型 bug 上游」，
> 不是靠「在 Linux 上多寫幾個測試」。

### 缺陷 6（資料靜默損毀）：重跑時把備份檔當成輸入合併

時間戳備份檔 `merged.bak-YYYYMMDD-HHMMSS.xlsx` 結尾仍是 `.xlsx`，
而排除清單只有「輸出檔本身」→ 重跑時備份檔被選中當輸入。

實測：同一資料夾連跑 3 次 → 第 3 次 **36 列（應 8 列）、27 欄（應 6 欄）、
金額合計 12798（應 6399，正好 double）、退款警示 3 筆（應 1 筆）**，完全靜默。

README 預設 `-o merged.xlsx`，所以 `cd 進資料夾 && python merge_xlsx.py . --apply`
這個最自然用法第二次執行就埋雷、第三次必爆。

**修法（雙管齊下）**：
1. 備份副檔名去掉 `.xlsx` → `merged.bak-YYYYMMDD-HHMMSS`，永遠不會被 .xlsx 掃描器選中
2. 新增 `excluded_artifacts()`：以 output_path 的 stem 前綴排除輸出檔本體 + 所有備份 + CSV 摘要，
   同時也排除舊版（v2 舊碼）留下的 `.bak-*.xlsx`

回歸測試：`test_rerun_output_inside_input_folder_does_not_self_merge`（連跑 3 次，
斷言列數與金額合計不變）、`test_legacy_bak_xlsx_backup_is_excluded`。

### 缺陷 7（資料靜默遺失）：重複表頭

表頭 `['金額','金額','備註']` + 資料列 `[100,200,'x']` →
`dict(zip(headers, values))` 讓後者覆蓋前者 → 合併資料的「金額」只剩 200，**100 無聲蒸發**；
但數值合計仍用 numeric_sums 算 100+200=300 → 同一個工作簿兩個分頁對同一欄位給出矛盾數字。

**修法**：讀表頭時偵測重複並自動改名（`金額_2`），同時在「檔案摘要」新增「警告」欄記錄。
回歸測試：`test_duplicate_header_does_not_lose_data`。

### 缺陷 8（來源追溯不可信）：`_來源列號` 與原始 Excel 對不上

程式先濾掉全空列、再用過濾後的索引從 2 起算 → 原始檔中間有空白列時列號逐列偏移。
實測（A1@row2、A2@row4、A3@row6）→ 程式回報 2、3、4。使用者拿這個欄位回原始檔核對會對到錯的列，
**比沒有追溯欄更糟，因為它看起來可信**。

**修法**：過濾空列前先記下原始列號（`SheetData.row_numbers`），`_來源列號` 填原始值。
回歸測試：`test_source_row_number_matches_original_excel`。

### 缺陷 9（體驗）：輸出失敗裸 traceback

輸出目錄無寫入權限 → 直接丟 PermissionError 完整 traceback、exit 1、零訊息。
違反 docstring 自己寫的「任何外部 I/O 失敗都要有可行動的錯誤訊息」。
而寫檔是整個工具唯一會壞掉資料的步驟，卻是防護最薄的一環。

**修法**：`main()` 包 try/except PermissionError / OSError → 可行動訊息 +
明確 exit code 3（區分於 2=用法錯誤、4=資料全壞）。
回歸測試：`test_output_permission_error_returns_actionable_message`。

### 缺陷 10（假綠燈）：交付物開箱是紅的

在交付目錄直接跑 `pytest` → **12 failed / 24 passed**（三組測試資料目錄沒交付，
`make_test_data.py` 雖在但不會自動執行）。RUNLOG 宣稱「36 項全綠」只在
「使用者還原過工作目錄」的前提下成立 —— 這是假綠燈。

**修法**：新增 `conftest.py`，用 session-scoped autouse fixture 自動產生測試資料。
現在在乾淨目錄（只複製 6 個交付檔、無 test_data）直接 `pytest -q` → **42 passed**。

### 第 2 輪修補後的實測

```
$ cd /tmp/delivery_check   # 只複製交付檔，沒有 test_data
$ python -m pytest -q
..........................................                               [100%]
42 passed in 0.54s

$ for i in 1 2 3; do python merge_xlsx.py work --apply -o work/merged.xlsx; done
  聯集欄位（6）：單號、處室、金額、數量、部門、備註
  合併後總列數：8          ← 三次都是 8（修補前第 3 次是 36）
  退款/負值警示：1 筆      ← 三次都是 1（修補前第 3 次是 3）
$ python -c "回算金額合計"
6399                       ← 修補前是 12798
```

