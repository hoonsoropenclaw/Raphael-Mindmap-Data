"""
合併資料夾內多個 Excel 並產生摘要
================================

用途（admin 軌：辦公自動化）：
  給定一個資料夾，把裡面所有 .xlsx / .xlsm 合併成單一檔案，並產生摘要工作表：
    - 來源檔案清單（檔名、分頁數、列數）
    - 各檔每欄的數值合計（自動偵測數值欄）
    - 退款/負值警示（會計場景常見）

執行環境：
  - 跨平台（Windows / macOS / Linux）皆可，僅依賴 openpyxl + pandas
  - Python 3.10+
  - 安裝：pip install openpyxl pandas

執行：
  python merge_xlsx.py <input_folder> [--output <output.xlsx>] [--dry-run]

設計原則（依 sops/code/SOP.md）：
  - 預設 dry-run；真的寫檔要用 --no-dry-run（注意：這裡 dry-run 反向叫 --no-dry-run 才真實寫入）
  - 破壞性動作（覆寫輸出檔）採「先備份再覆寫」模式
  - 任何外部 I/O 失敗都有可行動的錯誤訊息
  - 不引入 pywin32 / COM（保持跨平台）
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Iterable

import pandas as pd
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter


# ---------- 設定 ----------
REFUND_KEYWORDS = ("退款", "退費", "折讓", "溢付", "負值", "negative", "refund")
NUMERIC_THRESHOLD = 0.5  # 一欄中可成功轉成數值的比例門檻，才視為數值欄


@dataclass
class FileSummary:
    filename: str
    sheet_names: list[str]
    row_counts: dict[str, int]
    numeric_sums: dict[str, dict[str, float]] = field(default_factory=dict)
    refund_cells: list[tuple[str, str, float]] = field(default_factory=list)
    error: str | None = None


# ---------- 核心 ----------
def read_one(path: Path) -> FileSummary:
    """讀單一 Excel：分頁清單、每頁列數、每頁數值欄合計、退款警示。"""
    summary = FileSummary(filename=path.name, sheet_names=[], row_counts={})
    try:
        wb = load_workbook(path, read_only=True, data_only=True)
    except Exception as exc:  # noqa: BLE001 — 對外 IO 一律要可行動錯誤
        summary.error = f"無法開啟（{type(exc).__name__}: {exc}）"
        return summary

    try:
        for sheet_name in wb.sheetnames:
            summary.sheet_names.append(sheet_name)
            ws = wb[sheet_name]
            # read_only mode 下用 ws.max_row 取列數
            summary.row_counts[sheet_name] = ws.max_row or 0
    finally:
        wb.close()

    # 用 pandas 讀資料做數值合計 + 退款偵測
    for sheet_name in summary.sheet_names:
        try:
            df = pd.read_excel(path, sheet_name=sheet_name)
        except Exception as exc:  # noqa: BLE001
            summary.numeric_sums[sheet_name] = {"_error": str(exc)}
            continue

        numeric_cols = pick_numeric_columns(df)
        sums = {col: float(df[col].sum(skipna=True)) for col in numeric_cols}
        summary.numeric_sums[sheet_name] = sums

        # 退款/負值偵測：欄名含 REFUND_KEYWORDS 或數值 < 0
        for col in numeric_cols:
            negative_mask = df[col] < 0
            if not negative_mask.any():
                continue
            for idx in df.index[negative_mask]:
                col_name_lower = col.lower()
                if any(kw.lower() in col_name_lower for kw in REFUND_KEYWORDS):
                    summary.refund_cells.append(
                        (sheet_name, f"{col}!row{idx + 2}", float(df.at[idx, col]))
                    )
                else:
                    summary.refund_cells.append(
                        (sheet_name, f"{col}!row{idx + 2}", float(df.at[idx, col]))
                    )
    return summary


def pick_numeric_columns(df: pd.DataFrame) -> list[str]:
    """回傳『至少 NUMERIC_THRESHOLD 比例可轉數值』的欄位清單。

    排除 datetime/bool 欄位（它們也會「能轉成數字」，但合計沒意義）。
    """
    out: list[str] = []
    n = len(df)
    if n == 0:
        return out
    for col in df.columns:
        s = df[col]
        if pd.api.types.is_datetime64_any_dtype(s) or pd.api.types.is_bool_dtype(s):
            continue
        coerced = pd.to_numeric(s, errors="coerce")
        ratio = coerced.notna().sum() / n
        if ratio >= NUMERIC_THRESHOLD:
            out.append(col)
    return out


def merge_all(folder: Path) -> tuple[pd.DataFrame, list[FileSummary], list[Path]]:
    """合併所有 .xlsx/.xlsm；回傳 (合併後 DataFrame, 各檔摘要, 成功檔路徑)。"""
    files = sorted(p for p in folder.iterdir() if p.suffix.lower() in {".xlsx", ".xlsm"})
    if not files:
        raise SystemExit(f"在 {folder} 找不到 .xlsx / .xlsm 檔案")

    frames: list[pd.DataFrame] = []
    summaries: list[FileSummary] = []
    succeeded: list[Path] = []
    for path in files:
        s = read_one(path)
        if s.error:
            print(f"  ✗ 跳過 {path.name}：{s.error}", file=sys.stderr)
            summaries.append(s)
            continue
        for sheet_name in s.sheet_names:
            try:
                df = pd.read_excel(path, sheet_name=sheet_name)
                df["_來源檔"] = path.name
                df["_分頁"] = sheet_name
                frames.append(df)
            except Exception as exc:  # noqa: BLE001
                print(f"  ✗ {path.name} / {sheet_name} 讀取失敗：{exc}", file=sys.stderr)
        summaries.append(s)
        succeeded.append(path)

    merged = pd.concat(frames, ignore_index=True, sort=False) if frames else pd.DataFrame()
    return merged, summaries, succeeded


def write_output(
    merged: pd.DataFrame,
    summaries: list[FileSummary],
    succeeded: list[Path],
    out_path: Path,
    dry_run: bool,
) -> None:
    """寫出合併檔 + 摘要工作表；先備份舊檔再覆寫。"""
    wb = Workbook()

    # Sheet 1：合併資料
    ws_data = wb.active
    ws_data.title = "合併資料"
    if merged.empty:
        ws_data["A1"] = "（無資料）"
    else:
        headers = list(merged.columns)
        for col_idx, h in enumerate(headers, start=1):
            ws_data.cell(row=1, column=col_idx, value=h)
        for row_idx, row in enumerate(merged.itertuples(index=False), start=2):
            for col_idx, val in enumerate(row, start=1):
                ws_data.cell(row=row_idx, column=col_idx, value=_to_cell(val))

    # Sheet 2：來源檔摘要
    ws_meta = wb.active
    ws_meta = wb.create_sheet("檔案摘要")
    _write_summary_sheet(ws_meta, summaries)

    # Sheet 3：退款/負值警示
    ws_refund = wb.create_sheet("退款警示")
    _write_refund_sheet(ws_refund, summaries)

    # Sheet 4：本次執行 metadata
    ws_run = wb.create_sheet("本次執行")
    ws_run["A1"] = "執行時間"
    ws_run["B1"] = datetime.now().isoformat(timespec="seconds")
    ws_run["A2"] = "成功讀取檔數"
    ws_run["B2"] = len(succeeded)
    ws_run["A3"] = "失敗檔數"
    ws_run["B3"] = sum(1 for s in summaries if s.error)
    ws_run["A4"] = "合併後總列數"
    ws_run["B4"] = len(merged)
    ws_run["A5"] = "退款警示數"
    ws_run["B5"] = sum(len(s.refund_cells) for s in summaries)

    if dry_run:
        print(f"[dry-run] 不會真的寫 {out_path}；要寫請加 --no-dry-run")
        return

    # 先備份舊檔（如果存在）；確保 parent dir 存在
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if out_path.exists():
        backup = out_path.with_suffix(out_path.suffix + ".bak")
        shutil.copy2(out_path, backup)
        print(f"  ↻ 已備份舊檔到 {backup}")

    wb.save(out_path)
    print(f"  ✓ 寫出 {out_path}（{len(merged)} 列合併資料 + 3 張摘要表）")


def _to_cell(val) -> object:
    """pandas 裡的 NaN / Timestamp 轉 openpyxl 可接受的值。"""
    if pd.isna(val):
        return None
    if isinstance(val, pd.Timestamp):
        return val.to_pydatetime()
    return val


def _write_summary_sheet(ws, summaries: list[FileSummary]) -> None:
    headers = ["檔名", "分頁數", "總列數", "數值欄合計（JSON）", "錯誤"]
    for col_idx, h in enumerate(headers, start=1):
        c = ws.cell(row=1, column=col_idx, value=h)
        c.font = Font(bold=True)
        c.fill = PatternFill("solid", fgColor="D9E1F2")

    for row_idx, s in enumerate(summaries, start=2):
        ws.cell(row=row_idx, column=1, value=s.filename)
        ws.cell(row=row_idx, column=2, value=len(s.sheet_names))
        ws.cell(row=row_idx, column=3, value=sum(s.row_counts.values()))
        ws.cell(row=row_idx, column=4, value=json.dumps(s.numeric_sums, ensure_ascii=False))
        ws.cell(row=row_idx, column=5, value=s.error or "")

    # 自動欄寬（簡化：給定固定寬）
    widths = [30, 10, 10, 60, 40]
    for i, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w


def _write_refund_sheet(ws, summaries: list[FileSummary]) -> None:
    headers = ["來源檔", "分頁", "儲存格", "金額"]
    for col_idx, h in enumerate(headers, start=1):
        c = ws.cell(row=1, column=col_idx, value=h)
        c.font = Font(bold=True)
        c.fill = PatternFill("solid", fgColor="FCE4D6")

    row_idx = 2
    any_refund = False
    for s in summaries:
        for sheet, cell, amount in s.refund_cells:
            ws.cell(row=row_idx, column=1, value=s.filename)
            ws.cell(row=row_idx, column=2, value=sheet)
            ws.cell(row=row_idx, column=3, value=cell)
            ws.cell(row=row_idx, column=4, value=amount)
            any_refund = True
            row_idx += 1

    if not any_refund:
        ws.cell(row=2, column=1, value="（無退款/負值紀錄）")

    widths = [30, 20, 30, 14]
    for i, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w


# ---------- CLI ----------
def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="合併資料夾內多個 Excel 並產生摘要工作表",
    )
    parser.add_argument("input_folder", type=Path, help="要合併的資料夾")
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=Path("merged.xlsx"),
        help="輸出檔（預設 merged.xlsx）",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="（預設）不寫檔，只在螢幕顯示要做什麼；這是預設安全模式",
    )
    parser.add_argument(
        "--no-dry-run",
        dest="dry_run",
        action="store_false",
        help="真的寫出檔案（會先備份既有的同名檔）",
    )
    args = parser.parse_args(argv)

    if not args.input_folder.is_dir():
        print(f"錯誤：{args.input_folder} 不是資料夾", file=sys.stderr)
        return 2

    print(f"[merge_xlsx] 來源資料夾：{args.input_folder}")
    print(f"[merge_xlsx] 輸出目標：{args.output}（dry-run={args.dry_run}）")

    merged, summaries, succeeded = merge_all(args.input_folder)
    write_output(merged, summaries, succeeded, args.output, args.dry_run)

    print("\n--- 摘要 ---")
    print(f"成功讀取：{len(succeeded)} 個檔案")
    print(f"合併後總列數：{len(merged)}")
    print(f"退款/負值警示：{sum(len(s.refund_cells) for s in summaries)} 筆")
    return 0


if __name__ == "__main__":
    sys.exit(main())