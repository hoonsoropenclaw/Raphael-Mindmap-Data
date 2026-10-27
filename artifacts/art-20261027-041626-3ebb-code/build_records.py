#!/usr/bin/env python3
"""產生 RUNLOG.md 與 README.md（code SOP §8：交付紀錄的數字必須機器回算）。

這個腳本是唯一寫出交付紀錄的地方：
  - 先跑測試、跑機械檢查、跑雙向驗證 → 拿到真實數字
  - 再把數字寫進 RUNLOG.md 與 README.md
  - 寫完之後重跑一次檢查，確認紀錄與實測一致（§8.3）

**不准手抄數字**：所有計數都來自這個腳本實際跑出來的結果。
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
PY = sys.executable


def run(cmd: list[str], cwd: Path) -> tuple[int, str]:
    proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=False)
    return proc.returncode, (proc.stdout + proc.stderr)


def pytest_count(text: str) -> tuple[int, int]:
    """從 pytest 輸出解析 (passed, failed)。"""
    passed = failed = 0
    m = re.search(r"(\d+) passed", text)
    if m:
        passed = int(m.group(1))
    m = re.search(r"(\d+) failed", text)
    if m:
        failed = int(m.group(1))
    m = re.search(r"(\d+) error", text)
    if m:
        failed += int(m.group(1))
    return passed, failed


def main() -> int:
    root = HERE

    # ---- 1. 跑 pytest ----
    rc_pytest, out_pytest = run([PY, "-m", "pytest", "test_merge_xlsx.py", "-q"], root)
    passed, failed = pytest_count(out_pytest)
    pytest_line = re.sub(r"\s+", " ", out_pytest.strip().splitlines()[-1]) if out_pytest.strip() else "(no output)"

    # ---- 2. 跑雙向驗證 ----
    rc_bidir, out_bidir = run([PY, "verify_checkers.py"], root)
    bidir_pass = rc_bidir == 0
    bidir_defect_caught = "defective" in out_bidir and "actual_exit=1" in out_bidir
    bidir_fixed_clean = "fixed" in out_bidir and "actual_exit=0" in out_bidir

    # ---- 3. 產生 verification_summary.json（機械檢查的唯一數字來源）----
    # 第一次檢查用 --defer-record-check：此刻磁碟上的 RUNLOG 還是「上一版」，
    # 拿舊版比對新支數只會產生假紅燈（實測 2026-10-27：舊 RUNLOG 38 項 vs 新 45 項）。
    # 這輪的用途是取得要寫進紀錄的支數；真正的比對由第 8 步「寫完後重檢」執行。
    rc_check, out_check = run(
        [PY, "check_delivery.py", str(root), "--write-summary", "--defer-record-check"], root
    )

    # ---- 4. 實跑一次主程式（dry-run + apply），取得真實執行輸出 ----
    rc_dry, out_dry = run([PY, "merge_xlsx.py", "testdata"], root)
    rc_apply, out_apply = run(
        [PY, "merge_xlsx.py", "testdata", "-o", "merged.xlsx",
         "--summary-csv", "summary.csv", "--issues-csv", "issues.csv",
         "--header-row-for", "d_無法解析.xlsx=0", "--apply"],
        root,
    )

    # ---- 5. 執行平台資訊（實測平台 vs 目標環境要分開）----
    import platform

    platform_now = f"{platform.system()} {platform.release()} ({platform.machine()})"
    python_now = sys.version.split()[0]

    # ---- 6. 寫 RUNLOG.md（所有數字來自上面實際跑出來的結果）----
    try:
        summary = json.loads((root / "verification_summary.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        summary = {"checks": [], "counters": {}}
    counters = summary.get("counters", {})
    n_checks = counters.get("checks_total", 0)
    n_checks_passed = counters.get("checks_passed", 0)
    # 測試計數也從同一份摘要取（唯一來源，不手抄）
    n_tests_passed = counters.get("tests_passed", passed)
    n_tests_failed = counters.get("tests_failed", failed)

    runlog = f"""# RUNLOG — merge_xlsx v4

> 本檔由 `build_records.py` 自動產生（code SOP §8：交付紀錄的數字必須機器回算，
> 禁止手抄）。每次重跑該腳本都會覆寫本檔並重跑驗證。

## 1. 測試（SOP §2）

```
$ python3 -m pytest test_merge_xlsx.py -q
{pytest_line}
```

- 通過：{n_tests_passed} 項
- 失敗：{n_tests_failed} 項
- 涵蓋情境：正常 / 空缺資料 / 異常格式 / 負值退款 / 文字型數字 /
  百分比語意 / 合併儲存格 / 說明列 / 公式儲存格 / 舊格式略過 /
  重跑輸入集合一致 / Windows 路徑預檢

## 2. 雙向回歸驗證（SOP §7.1）

```
$ python3 verify_checkers.py
（完整輸出見下方「雙向回歸驗證」章節的摘要；原始輸出由 build_records.py 當場執行取得）
```

- 缺陷版被抓住（exit ≠ 0）：{"是" if bidir_defect_caught else "否"}
- 修好版全綠（exit = 0）：{"是" if bidir_fixed_clean else "否"}
- 雙向驗證總結果：{"通過" if bidir_pass else "失敗"}
- 檢查項總數與通過數：見 `verification_summary.json` 的 counters（本文不手抄）

原始執行輸出：`evidence/bidirectional_verify.log`（由 `build_records.py` 當場擷取）

## 3. 交付前機械檢查（SOP §6 / §8）

本流程跑**兩輪**機械檢查，兩輪都必須綠：

```
$ python3 check_delivery.py . --write-summary --defer-record-check   # 第 1 輪：取得要寫進本檔的支數
$ python3 check_delivery.py . --write-summary                         # 第 2 輪：權威比對（寫完本檔後）
```

- 第 1 輪把「交付紀錄數字比對」標記為 deferred：那一刻磁碟上的本檔還是上一版，
  拿舊版比對新支數只會產生假紅燈（實測 2026-10-27：舊本檔測試支數 38，新摘要 45）。
- 第 2 輪是**權威**的一輪：本檔已用新支數重寫，數字必須逐一對得上摘要。
- 兩輪的完整結果寫入 `verification_summary.json`（本檔只引用它的 counters，不複製輸出）；
  原始文字輸出：`evidence/check_delivery.log`（第 2 輪）。

- 檢查項總數：{n_checks}
- 通過：{n_checks_passed}
- 證據數字來源：`verification_summary.json`（機器可讀，本檔所有計數引用它）

## 4. 實際執行（dry-run）

```
$ python3 merge_xlsx.py testdata
{out_dry.strip()}
```

## 5. 實際執行（--apply，含逐檔表頭列覆寫）

```
$ python3 merge_xlsx.py testdata -o merged.xlsx --summary-csv summary.csv \\
    --issues-csv issues.csv --header-row-for 'd_無法解析.xlsx=0' --apply
{out_apply.strip()}
```

## 6. 執行平台與驗證揭露（SOP §3 / 今日卡片 Q1）

| 項目 | 內容 |
|---|---|
| 實測平台 | {platform_now}、Python {python_now} |
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
"""
    (root / "RUNLOG.md").write_text(runlog, encoding="utf-8")

    # ---- 7. 寫 README.md ----
    readme = f"""# merge_xlsx v4 — 多 Excel 合併並產生摘要

把一個資料夾內的多個 `.xlsx` 合併成單一工作簿，並產生可稽核的摘要。

## 這是什麼（v4 改了什麼）

v3（2026-10-24）有兩個看不見的資料錯誤，v4 逐項修掉：

| # | v3 的問題 | v4 的做法 |
|---|---|---|
| 1 | 表頭固定取「第一個非空列」→ 前面有說明列就整批欄位名錯掉 | **表頭列自動判定**：以「型別互斥」為判準（欄名是文字、其下整欄是數值／日期），加上欄名唯一性、非空比例、合併儲存格補欄名；可用 `--header-row` 手動覆寫；判定失敗給可行動訊息而不是猜一個 |
| 2 | 金額欄只認 `int`/`float` → 文字型金額（`1,234`、`NT$2,000`、`45%`、全形）**靜默漏算** | **型別正規化**：NFKC 全形轉半形 → 去千分位／幣別 → 會計括號負數 → 百分比（依欄位語意決定是否 /100）→ 萬／億進位；無法解析的值獨立成「無法解析」清單並留痕 |
| 3 | 排除自己產生的檔案靠寫死的副檔名比對 | **輸入集合界定**：宣告式排除規則 + `--exclude-glob` + 每個輸入檔的納入／排除決定與 sha256（寫進「輸入集合」分頁）；連續 3 次執行輸出必須一致 |
| 4 | 交付紀錄宣稱「Windows 可用」但沒在 Windows 驗過 | **三欄揭露**：實測平台／模擬平台／未驗證項目分開寫；明確聲明尚未在 Windows 實機驗收 |
| 5 | 交付紀錄的計數是手抄的 | **機器回算**：機械檢查產出 `verification_summary.json`，RUNLOG 與本檔全部引用它；檢查器做雙向回歸驗證（缺陷版 exit≠0、修好版 exit=0） |
| 6 | 有 `--no-backup` 旗標可關掉備份保護 | **移除**：只保留 `--dry-run`（預設）/ `--apply` |

## 安裝

```bash
pip install openpyxl
```

只需要 openpyxl。其餘全部用 Python 標準函式庫。

## 執行

```bash
# dry-run（預設）：只預覽，不寫任何檔案
python merge_xlsx.py <資料夾>

# 真的輸出
python merge_xlsx.py <資料夾> --apply \\
    -o out/merged.xlsx \\
    --summary-csv out/summary.csv \\
    --issues-csv out/issues.csv

# 表頭列自動判定失敗時，手動指定（0-based，索引「非空列」序列）
python merge_xlsx.py <資料夾> --apply --header-row 2

# 只對特定檔案指定（不同檔案表頭列位置不同時）
python merge_xlsx.py <資料夾> --apply --header-row-for '2026Q3.xlsx=2'
```

### 參數

| 參數 | 預設 | 說明 |
|---|---|---|
| `input_folder` | （必要） | 要合併的資料夾 |
| `-o, --output` | `merged.xlsx` | 輸出 Excel |
| `--summary-csv` | 無 | 檔案摘要 CSV |
| `--issues-csv` | 無 | 型別轉換／無法解析問題清單 CSV |
| `--csv-encoding` | `utf-8-sig` | CSV 編碼（`utf-8-sig` 讓 Excel 直接開不亂碼；`cp950` 給舊系統） |
| `--header-row` | 自動判定 | 手動指定表頭列（0-based，索引「非空列」序列） |
| `--header-row-for` | 無 | 只對特定檔案指定（`檔名=N`，可重複） |
| `--exclude-glob` | 無 | 額外排除的檔名樣式（可重複） |
| `--apply` | 關 | 真的寫檔（預設 dry-run） |

### 退出碼

| 碼 | 意義 |
|---|---|
| 0 | 成功 |
| 2 | 用法／路徑錯誤 |
| 3 | 輸出失敗（權限、磁碟、鎖檔） |
| 4 | 所有檔案都解析失敗 |
| 5 | 有檔案需要人工指定表頭列（已合併其他檔案，但這些檔案未被計入） |

## 輸出工作簿的分頁

| 分頁 | 內容 |
|---|---|
| 合併資料 | 跨檔聯集欄位 + `_來源檔` / `_來源分頁` / `_來源列號` |
| 檔案摘要 | 每檔每分頁的列數、欄位、表頭列判定結果與依據、缺漏／獨有欄位、警告 |
| 數值合計 | 每欄合計與非空數值格數（用正規化後的數值） |
| 型別轉換 | 每一筆文字→數值的轉換留痕（原始值／正規化值／套用規則） |
| 無法解析 | 轉型失敗的值（獨立成表，不混在空值裡、不算 0） |
| 退款警示 | 退款關鍵欄或負值（含「原本是文字」的負值） |
| 輸入集合 | 每個輸入檔的納入／排除決定、理由、sha256 |
| 本次執行 | 時間、平台、輸入輸出、統計 |
| 略過檔案 | 被略過的檔案與原因 |

## 適用邊界

- **輸入只支援 `.xlsx`**（`.xls` / `.xlsm` / `.xlsb` 會被略過並回報原因）。舊格式請先在 Excel 另存為 `.xlsx`。
- **表頭列判定假設「欄名是文字、資料欄有數值或日期」**。若整個分頁都是文字（沒有任何型別落差），判定會失敗並要求 `--header-row` 手動指定 —— 這是刻意的：不猜。
- **百分比語意由欄位語意決定**（欄名含「率／百分比／佔比」→ /100）。同一個值在「執行率」欄與「件數」欄的正確解讀不同，腳本不從值本身猜。
- **公式必須由 Excel 計算並存檔**才有快取值；未存檔的公式讀出來是空值，腳本會在警告中揭露哪些儲存格是公式。
- **尚未在真實 Windows 實機驗收**（見 RUNLOG §6 的三欄揭露）。
- 合併資料會讀進記憶體；極大檔案（數十萬列）建議先分批處理。

### 小計列（合計／小計／總計）會被自動排除

來源資料常有一列「合計」；那一列**不是資料列**，若照樣累加，數值合計會 double。
腳本會在累加前偵測這類列（標籤欄的值命中 `合計／小計／總計／累計／總合／總額／total／subtotal／sum／grand total`）：

- 該列**不計入**「數值合計」分頁；
- 該列**仍保留**在「合併資料」分頁（資料不遺失）；
- 被排除的列會寫在「檔案摘要」的「排除的小計列」欄（含列號、判斷依據的欄名與原因），不是靜默處理。

**標籤欄不一定是第一欄**：若小計標籤在第二欄（例如「代號／分類／金額」的分類欄），
腳本會一併檢查所有候選標籤欄，不會漏接。

**比對是「完全相符」不是「包含」**：資料列的名稱若只是含「合計」字樣
（例如專案名稱叫「合計專案A」），那是真實資料，不會被誤判成小計列。

### 輸入資料夾會遞迴掃描（支援年度別子資料夾）

使用者的行政資料常按年度／單位分資料夾放（`113年度/`、`114年度/`）。
腳本會遞迴掃描，來源在「輸入集合」與「檔案摘要」裡以**相對路徑**標示
（如 `113年度/預算.xlsx`），因此不同子資料夾的同名檔不會互相蓋掉。

### 自我合併防護靠「內容判斷」，不靠檔名

重跑時若輸入資料夾裡放著上一次自己產出的合併工作簿，資料會重複、金額 double。
本工具的產出物含 `本次執行`／`輸入集合` 分頁，腳本會**讀內容**辨識並排除，
所以即使輸出檔改名（例如 `-o merged2.xlsx`）也擋得住。
被排除時會在「略過檔案」分頁寫明原因。

### 無原名的欄位

合併儲存格讓某欄沒有自己的欄名時，腳本依該欄的**資料型別**重新命名並標示
`欄N（數值）`（該欄是數值時）或 `欄N（無原名）`（其他情形），
不會借用左鄰欄名造成語意誤導（例如把金額欄叫成「經費項目_2」）。
原借用的名稱與改名理由會寫在該分頁的警告欄。

## 交付物與驗證

```
merge_xlsx.py            主程式
test_merge_xlsx.py       回歸測試（pytest）
make_test_data.py        測試資料產生器
check_delivery.py        交付前機械檢查（§6 / §8）
verify_checkers.py       檢查器的雙向回歸驗證（§7.1）
build_records.py         產生 RUNLOG.md / README.md（數字機器回算）
verification_summary.json 機械檢查結果（唯一數字來源）
```

驗證方式（數字見 RUNLOG，勿手抄）：

```bash
python3 -m pytest test_merge_xlsx.py -q     # 測試
python3 verify_checkers.py                  # 檢查器雙向驗證
python3 check_delivery.py . --write-summary # 交付前機械檢查
```
"""
    (root / "README.md").write_text(readme, encoding="utf-8")

    # ---- 8. 寫完紀錄後重跑一次檢查並比對（§8.3）----
    # 這一輪是權威的：RUNLOG 已被新支數重寫，數字必須逐一對得上摘要。
    rc_recheck, out_recheck = run([PY, "check_delivery.py", str(root), "--write-summary"], root)

    # ---- 7b. 原始執行輸出另存 evidence/（不手抄數字進紀錄）----
    evidence_dir = root / "evidence"
    evidence_dir.mkdir(exist_ok=True)
    (evidence_dir / "bidirectional_verify.log").write_text(out_bidir, encoding="utf-8")
    # check_delivery.log 存「權威那一輪」（第 2 輪，重檢）的輸出，
    # 不是第 1 輪（那一輪有 deferred 項目，會被誤讀成漏檢）。
    (evidence_dir / "check_delivery.log").write_text(out_recheck, encoding="utf-8")
    (evidence_dir / "pytest.log").write_text(out_pytest, encoding="utf-8")
    (evidence_dir / "run_dry_run.log").write_text(out_dry, encoding="utf-8")
    (evidence_dir / "run_apply.log").write_text(out_apply, encoding="utf-8")

    print(f"pytest: passed={passed} failed={failed} rc={rc_pytest}")
    print(f"bidirectional: rc={rc_bidir} caught={bidir_defect_caught} clean={bidir_fixed_clean}")
    print(f"check_delivery (write): rc={rc_check}")
    print(f"check_delivery (recheck): rc={rc_recheck}")
    print(f"dry-run rc={rc_dry}  apply rc={rc_apply}")
    print("已產生 RUNLOG.md / README.md")
    return 0 if (rc_pytest == 0 and bidir_pass and rc_check == 0 and rc_recheck == 0) else 1


if __name__ == "__main__":
    raise SystemExit(main())
