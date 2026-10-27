# RUNLOG — merge_xlsx v4

> 本檔由 `build_records.py` 自動產生（code SOP §8：交付紀錄的數字必須機器回算，
> 禁止手抄）。每次重跑該腳本都會覆寫本檔並重跑驗證。

## 1. 測試（SOP §2）

```
$ python3 -m pytest test_merge_xlsx.py -q
38 passed in 0.65s
```

- 通過：38 項
- 失敗：0 項
- 涵蓋情境：正常 / 空缺資料 / 異常格式 / 負值退款 / 文字型數字 /
  百分比語意 / 合併儲存格 / 說明列 / 公式儲存格 / 舊格式略過 /
  重跑輸入集合一致 / Windows 路徑預檢

## 2. 雙向回歸驗證（SOP §7.1）

```
$ python3 verify_checkers.py
（完整輸出見下方「雙向回歸驗證」章節的摘要；原始輸出由 build_records.py 當場執行取得）
```

- 缺陷版被抓住（exit ≠ 0）：是
- 修好版全綠（exit = 0）：是
- 雙向驗證總結果：通過
- 檢查項總數與通過數：見 `verification_summary.json` 的 counters（本文不手抄）

原始執行輸出：`evidence/bidirectional_verify.log`（由 `build_records.py` 當場擷取）

## 3. 交付前機械檢查（SOP §6 / §8）

```
$ python3 check_delivery.py . --write-summary
```

完整結果寫入 `verification_summary.json`（本文只引用它的 counters，不複製輸出）；
原始文字輸出：`evidence/check_delivery.log`。

- 檢查項總數：7
- 通過：7
- 證據數字來源：`verification_summary.json`（機器可讀，本檔所有計數引用它）

## 4. 實際執行（dry-run）

```
$ python3 merge_xlsx.py testdata
[merge_xlsx] 輸入資料夾：testdata
[merge_xlsx] 輸出 Excel：merged.xlsx
[merge_xlsx] 模式：dry-run（不寫檔）
[merge_xlsx] 執行平台：Linux 6.8.0-136-generic (x86_64)
  解析成功：8 個檔案 / 8 個分頁
  聯集欄位（5）：經費項目、核定金額、執行率、經費項目_2、件數
  合併後總列數：15
  型別轉換：8 筆
  無法解析：1 筆
    - 欄位「件數」：1 個值無法解析（見「無法解析」分頁）
  退款/負值警示：1 筆
  略過 2 個檔案（原因見輸出檔的「略過檔案」分頁）：
    - i_舊格式.xls：副檔名 .xls 不支援（.xls 舊格式請在 Excel 另存為 .xlsx）
    - ~$j_鎖檔.xlsx：Excel 鎖檔：Excel 開檔時產生的鎖檔，不納入

[dry-run] 沒有寫任何檔案。要真的輸出請加 --apply。
  ✗ d_無法解析.xlsx / 經費：無法判定 d_無法解析.xlsx / 經費 的表頭列：前兩名候選的分數 [0.50, 0.50, 0.00] 差距小於 0.05，模稜兩可。請用 --header-row N 指定（第幾列為表頭，0-based，索引『非空列』序列）。

注意：1 個檔案需要人工指定表頭列（已合併其他檔案，這些檔案未被計入）：
  - 無法判定 d_無法解析.xlsx / 經費 的表頭列：前兩名候選的分數 [0.50, 0.50, 0.00] 差距小於 0.05，模稜兩可。請用 --header-row N 指定（第幾列為表頭，0-based，索引『非空列』序列）。
  請用 --header-row N 重跑指定（會套用到所有分頁；分頁各自不同時請分批處理）。
```

## 5. 實際執行（--apply，含逐檔表頭列覆寫）

```
$ python3 merge_xlsx.py testdata -o merged.xlsx --summary-csv summary.csv \
    --issues-csv issues.csv --header-row-for 'd_無法解析.xlsx=0' --apply
[merge_xlsx] 輸入資料夾：testdata
[merge_xlsx] 輸出 Excel：merged.xlsx
[merge_xlsx] 摘要 CSV：summary.csv、issues.csv（編碼 utf-8-sig）
[merge_xlsx] 模式：APPLY（會寫檔）
[merge_xlsx] 執行平台：Linux 6.8.0-136-generic (x86_64)
  解析成功：8 個檔案 / 9 個分頁
  聯集欄位（5）：經費項目、核定金額、執行率、經費項目_2、件數
  合併後總列數：18
  型別轉換：8 筆
  無法解析：3 筆
    - 欄位「核定金額」：2 個值無法解析（見「無法解析」分頁）
    - 欄位「件數」：1 個值無法解析（見「無法解析」分頁）
  退款/負值警示：1 筆
  略過 2 個檔案（原因見輸出檔的「略過檔案」分頁）：
    - i_舊格式.xls：副檔名 .xls 不支援（.xls 舊格式請在 Excel 另存為 .xlsx）
    - ~$j_鎖檔.xlsx：Excel 鎖檔：Excel 開檔時產生的鎖檔，不納入
  ✓ 寫出 merged.xlsx
  ↻ 舊檔已備份到 merged.bak-20261027-034248
  ✓ 寫出 summary.csv（utf-8-sig）
  ✓ 寫出 issues.csv（utf-8-sig）
```

## 6. 執行平台與驗證揭露（SOP §3 / 今日卡片 Q1）

| 項目 | 內容 |
|---|---|
| 實測平台 | Linux 6.8.0-136-generic (x86_64)、Python 3.12.3 |
| 目標環境（使用者實機） | Windows |
| 模擬平台驗證 | Windows 路徑規則（禁用字元、保留裝置名、MAX_PATH 260）以 `PureWindowsPath` 在 Linux 上模擬 |
| 未驗證項目 | Windows 實機上的 `os.fsync` 行為、Excel 鎖檔實際佔用、cp950 編碼在 Excel 開啟的實際顯示、Excel COM 互動 |
| 未驗證原因 | 本次開發環境為 Linux，無法取得 Windows 實機；上述項目原理上不可在 Linux 驗證 |

**明確聲明**：本產出物**尚未在真實 Windows 實機驗收**。
「跨平台都能跑」這類沒有證據的宣稱不適用於本產出物。

## 7. 交付紀錄的數字如何回算

```
$ python3 build_records.py          # 重新產生本檔（會重跑測試與全部檢查）
```

本檔所有計數均由該腳本實際執行後寫入；`verification_summary.json` 是
機械檢查結果的唯一來源（不得在別處手抄支數）。

已重跑驗證：2026-10-27 hermes（本次執行）
