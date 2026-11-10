"""合併 + 對帳引擎。

核心不變式（這支程式存在的理由）：

    全表總計 = Σ 分組合計 = Σ 明細值

三個數字必須由**同一個函式**回算（§11-1），不得各自手寫。
任一條等式不成立就是 hard fail，必須被寫進 issues 並讓 exit≠0。

為什麼這個不變式值得寫成一支程式而不是靠人看：
10-27 的 merge_xlsx v4 系列曾經 38 項 pytest 全綠、機械檢查 8/8 全綠，
「數值合計」卻報 1600000（正確值 800000）——因為小計列漏接，
合計靜默變兩倍。**沒有全表總計這條等式，就沒有任何東西能發現這件事。**
"""
from __future__ import annotations

import json
from collections import OrderedDict
from dataclasses import dataclass, field
from decimal import Decimal
from pathlib import Path
from typing import Iterable

from openpyxl import load_workbook

from .normalize import (
    CANONICAL_COLUMNS,
    AmountParse,
    detect_subtotal,
    map_columns,
    parse_amount,
)

__all__ = [
    "Row",
    "SourceFileReport",
    "MergeResult",
    "read_sheet",
    "merge_directory",
    "reconcile",
    "EXCLUDED_RATIO_LIMIT",
    "EXCLUDED_RATIO_MIN_ROWS",
]

#: 被排除列的比例門檻**由宣告側提供**（xlsx_recon/declarations.py）。
#:
#: 為什麼 engine 不自己訂門檻：門檻若由檢查器／被檢產物自己裁定後果，
#: 等同沒有門檻（11-03 已實證「門檻型檢查器若由產出者自己寫，等同沒有檢查器」）。
#: 這裡只做**轉載**，值與理由寫在宣告側（declarations.py 的常數註解）。
from .declarations import EXCLUDED_RATIO_LIMIT, EXCLUDED_RATIO_MIN_ROWS  # noqa: F401


@dataclass
class Row:
    """一筆被合併後的資料列。"""

    source_file: str
    source_sheet: str
    source_row: int          # 1-based，含表頭列
    values: dict[str, object] = field(default_factory=dict)
    amount: Decimal | None = None
    amount_reason: str = ""
    is_subtotal: bool = False
    subtotal_label: str | None = None
    subtotal_column_index: int | None = None
    subtotal_kind: str | None = None
    subtotal_layer: str | None = None
    #: 小計列**自己宣稱**的金額。小計列的 amount 一定是 None（不進明細母體），
    #: 但這個值必須保留——因為「宣稱值 vs 該檔明細和」是判定小計真偽的唯一依據。
    #: 如果沒有保留它，疑似小計的驗證會變成「在空集合上驗證」＝永遠通過。
    subtotal_claimed_amount: Decimal | None = None
    group_key: str = ""

    def to_record(self) -> dict:
        return {
            "source_file": self.source_file,
            "source_sheet": self.source_sheet,
            "source_row": self.source_row,
            "日期": self.values.get("日期"),
            "類別": self.values.get("類別"),
            "說明": self.values.get("說明"),
            "單號": self.values.get("單號"),
            "金額": str(self.amount) if self.amount is not None else None,
            "is_subtotal": self.is_subtotal,
        }


@dataclass
class SourceFileReport:
    """單一來源檔的處理結果（成功與失敗都要有紀錄）。"""

    path: str
    status: str = "ok"          # ok | skipped | error
    reason: str = ""
    sheets: list[str] = field(default_factory=list)
    sheets_detail: list["SourceFileReport"] = field(default_factory=list)
    detail_rows: int = 0
    subtotal_rows: int = 0
    unmapped_columns: list[dict] = field(default_factory=list)
    missing_required_columns: list[str] = field(default_factory=list)
    unparseable_rows: int = 0
    empty_amount_rows: int = 0
    percent_amount_rows: int = 0


@dataclass
class MergeResult:
    rows: list[Row] = field(default_factory=list)
    files: list[SourceFileReport] = field(default_factory=list)
    issues: list[dict] = field(default_factory=list)
    groups: "OrderedDict[str, list[Row]]" = field(default_factory=OrderedDict)


def _dec(value: Decimal | None) -> Decimal:
    return value if value is not None else Decimal("0")


def read_sheet(path: Path, sheet_name: str, report: SourceFileReport) -> list[Row]:
    """讀一個工作表，回傳資料列（已做欄位對映、金額解析、小計判定）。

    讀不到表頭或缺必要欄位時回傳空清單並在 report 上記錄原因。
    """
    rows: list[Row] = []
    try:
        wb = load_workbook(path, read_only=True, data_only=True)
    except Exception as exc:  # noqa: BLE001 - 任何讀檔失敗都要有可行動訊息
        report.status = "error"
        report.reason = f"無法開啟檔案：{type(exc).__name__}: {exc}"
        return rows

    try:
        ws = wb[sheet_name]
        header_iter = ws.iter_rows(min_row=1, max_row=1, values_only=True)
        headers = next(header_iter, None)
        if not headers or all(h is None or str(h).strip() == "" for h in headers):
            report.reason = "第 1 列沒有表頭，無法判斷欄位"
            report.status = "error"
            return rows

        mapping, unmapped = map_columns(list(headers))
        report.unmapped_columns = unmapped

        missing = [c for c in ("日期", "類別", "金額") if mapping.get(c) is None]
        if missing:
            report.missing_required_columns = missing
            report.status = "error"
            report.reason = (
                f"缺少必要欄位：{', '.join(missing)}"
                f"（偵測到的表頭：{[str(h) for h in headers]}）"
            )
            return rows

        amount_idx = mapping["金額"]
        for r_idx, raw in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
            if raw is None:
                continue
            # 整列空白 → 跳過（不算母體內的一筆）
            if all(v is None or str(v).strip() == "" for v in raw):
                continue

            cell_list = list(raw)
            # 小計偵測需要知道金額欄在哪（第二層結構偵測要用）
            sub = detect_subtotal(cell_list, amount_index=amount_idx)

            values = {c: cell_list[mapping[c]] if mapping.get(c) is not None else None
                      for c in CANONICAL_COLUMNS}

            amount: Decimal | None = None
            amount_reason = ""
            claimed: Decimal | None = None
            if sub["is_subtotal"]:
                # 小計列的金額不進明細母體（否則重複計算），
                # 但「它宣稱是多少」必須保留 —— 那是判定它真偽的唯一依據。
                parsed_sub = parse_amount(cell_list[amount_idx])
                claimed = parsed_sub.value
                amount = None
                amount_reason = "subtotal_row_excluded"
                report.subtotal_rows += 1
            else:
                parsed: AmountParse = parse_amount(cell_list[amount_idx])
                if parsed.ok:
                    amount = parsed.value
                else:
                    amount_reason = parsed.reason
                    if parsed.reason == "unparseable":
                        report.unparseable_rows += 1
                    elif parsed.reason == "empty":
                        report.empty_amount_rows += 1
                    elif parsed.reason == "percent":
                        report.percent_amount_rows += 1

            row = Row(
                source_file=path.name,
                source_sheet=sheet_name,
                source_row=r_idx,
                values=values,
                amount=amount,
                amount_reason=amount_reason,
                is_subtotal=sub["is_subtotal"],
                subtotal_label=sub["label"],
                subtotal_column_index=sub["column_index"],
                subtotal_kind=sub["kind"],
                subtotal_layer=sub["detection_layer"],
                subtotal_claimed_amount=claimed,
            )
            rows.append(row)
            if not sub["is_subtotal"]:
                report.detail_rows += 1
    finally:
        wb.close()
    return rows


def _group_key(row: Row) -> str:
    """分組鍵：優先用「單號」，沒有就用「說明」，再沒有用「日期」。

    為什麼要有 group key：加總等式要能被回算到「分組合計」，
    分組必須有一個穩定、可解釋的定義。
    """
    for key in ("單號", "說明", "日期"):
        val = row.values.get(key)
        if val is not None and str(val).strip() != "":
            return str(val).strip()
    return "(未分組)"


def merge_directory(
    input_dir: Path,
    *,
    patterns: Iterable[str] = ("*.xlsx", "*.xlsm"),
    recursive: bool = True,
    skip_names: Iterable[str] = ("~$",),
    exclude_output: bool = True,
) -> MergeResult:
    """把一個資料夾內的 Excel 檔合併成一張表。

    - 遞迴子資料夾（除非 recursive=False）
    - 跳過 Excel 暫存檔（以 ~$ 開頭）
    - 跳過輸出檔自己（避免「把自己的輸出再合併進去」的自我循環）
    - 每個檔案／每個工作表都獨立記錄成敗，單一檔案壞掉不影響其他檔案
    """
    result = MergeResult()
    if not input_dir.exists():
        result.issues.append({
            "severity": "high",
            "code": "input_dir_missing",
            "file": str(input_dir),
            "desc": f"輸入資料夾不存在：{input_dir}",
        })
        return result

    files: list[Path] = []
    for pattern in patterns:
        if recursive:
            files.extend(input_dir.rglob(pattern))
        else:
            files.extend(input_dir.glob(pattern))
    files = sorted({f.resolve() for f in files if f.is_file()})

    skipped_prefixes = tuple(skip_names)
    for path in files:
        if path.name.startswith(skipped_prefixes):
            continue
        if exclude_output and path.name.lower() in {"merged.xlsx", "merged.xlsm"}:
            continue
        report = SourceFileReport(path=str(path))
        result.files.append(report)

        try:
            wb = load_workbook(path, read_only=True, data_only=True)
            sheet_names = list(wb.sheetnames)
            wb.close()
        except Exception as exc:  # noqa: BLE001
            report.status = "error"
            report.reason = f"無法開啟檔案：{type(exc).__name__}: {exc}"
            result.issues.append({
                "severity": "high",
                "code": "file_open_failed",
                "file": path.name,
                "desc": report.reason,
            })
            continue

        if not sheet_names:
            report.status = "skipped"
            report.reason = "檔案沒有任何工作表"
            continue

        report.sheets = sheet_names
        file_had_error = False
        for sheet in sheet_names:
            sheet_report = SourceFileReport(path=path.name)
            sheet_report.sheets = [sheet]
            rows = read_sheet(path, sheet, sheet_report)
            report.sheets_detail.append(sheet_report)
            report.detail_rows += sheet_report.detail_rows
            report.subtotal_rows += sheet_report.subtotal_rows
            report.unparseable_rows += sheet_report.unparseable_rows
            report.empty_amount_rows += sheet_report.empty_amount_rows
            report.percent_amount_rows += sheet_report.percent_amount_rows
            if sheet_report.unmapped_columns:
                report.unmapped_columns.extend(sheet_report.unmapped_columns)
            if sheet_report.status == "error":
                file_had_error = True
                result.issues.append({
                    "severity": "high",
                    "code": "sheet_failed",
                    "file": path.name,
                    "sheet": sheet,
                    "desc": sheet_report.reason,
                })
            result.rows.extend(rows)

        if file_had_error:
            report.status = "error"
            report.reason = "部分工作表處理失敗，詳見 issues"

    # 分組（保持首次出現順序 → 輸出穩定）
    for row in result.rows:
        if row.is_subtotal:
            continue
        row.group_key = _group_key(row)
        result.groups.setdefault(row.group_key, []).append(row)

    return result


def _count_reasons(rows: list["Row"]) -> dict[str, int]:
    """把一批列的排除原因做計數。"""
    out: dict[str, int] = {}
    for r in rows:
        out[r.amount_reason] = out.get(r.amount_reason, 0) + 1
    return out


def _by_file(rows: list["Row"]) -> dict[str, list["Row"]]:
    """把列依來源檔分組（保持插入順序）。"""
    out: dict[str, list["Row"]] = {}
    for r in rows:
        out.setdefault(r.source_file, []).append(r)
    return out


def reconcile(result: MergeResult) -> dict:
    """回算加總等式與母體。

    回傳的 dict 會被寫進 verification_summary.json，
    所有敘述層的數字一律引用這裡（§8／§11-5：禁止手抄）。
    """
    detail_rows = [r for r in result.rows if not r.is_subtotal]
    subtotal_rows = [r for r in result.rows if r.is_subtotal]

    # 明細和：只有 amount 不為 None 的列才進母體
    amounted = [r for r in detail_rows if r.amount is not None]
    sum_detail = sum((r.amount for r in amounted), Decimal("0"))

    # 分組和：同一批母體分組後加總
    sum_group = Decimal("0")
    group_totals: list[dict] = []
    for key, rows in result.groups.items():
        g_rows = [r for r in rows if r.amount is not None]
        g_total = sum((r.amount for r in g_rows), Decimal("0"))
        sum_group += g_total
        group_totals.append({
            "group": key,
            "rows": len(rows),
            "rows_with_amount": len(g_rows),
            "total": str(g_total),
        })

    # 全表總計：就是明細和（獨立欄位，但由同一函式回算）
    grand_total = sum_detail

    # 來源檔宣告的小計（被排除的列）加總
    subtotal_excluded = sum(
        (r.subtotal_claimed_amount for r in subtotal_rows
         if r.subtotal_claimed_amount is not None),
        Decimal("0"),
    )

    excluded_rows = [
        r for r in detail_rows
        if r.amount is None
    ]
    excluded_reasons: dict[str, int] = {}
    for r in excluded_rows:
        excluded_reasons[r.amount_reason] = excluded_reasons.get(r.amount_reason, 0) + 1

    # --- 母體掏空檢查（11-11 新增）---
    #
    # 「等式成立」與「等式有意義」是兩個命題。
    # 這裡量的是**每個來源檔**的被排除比例：
    #   excluded_ratio = 該檔被排除的明細列 / 該檔全部明細列
    # 超過門檻 → 該檔的母體被掏空 → 等式在那個幾乎空的母體上平凡成立 → 必須紅燈。
    #
    # 為什麼按「檔」而不是按「整體」分母：
    # 整體比例會被大檔的正常資料稀釋——一個只有 7 列的檔全部壞掉，
    # 在 28 列的整體母體裡只佔 10.7%，看起來完全正常。
    # 按檔算才抓得到「這一整個來源檔的資料品質壞了」。
    #
    # 為什麼排除小計列不影響這個比例：
    # 小計列本來就不在 detail_rows 裡（detail_rows 已經濾掉 is_subtotal），
    # 所以這個比例量的是「明細列裡有多少列的金額進不了加總」。
    per_file_exclusion: list[dict] = []
    for fname, rows in sorted(_by_file(result.rows).items()):
        f_detail = [r for r in rows if not r.is_subtotal]
        f_excluded = [r for r in f_detail if r.amount is None]
        f_total = len(f_detail)
        f_ratio = (len(f_excluded) / f_total) if f_total else 0.0
        # 分母下限：列數太少時比例不具資訊量 → 不判（宣告側提供門檻）
        f_evaluable = f_total >= EXCLUDED_RATIO_MIN_ROWS
        per_file_exclusion.append({
            "file": fname,
            "detail_rows": f_total,
            "included_rows": f_total - len(f_excluded),
            "excluded_rows": len(f_excluded),
            "excluded_ratio": round(f_ratio, 4),
            "evaluable": f_evaluable,
            "over_limit": bool(f_evaluable and f_ratio > EXCLUDED_RATIO_LIMIT),
            "excluded_reasons": _count_reasons(f_excluded),
        })
    hollow_files = [p["file"] for p in per_file_exclusion if p["over_limit"]]
    overall_excluded = len(excluded_rows)
    overall_total = len(detail_rows)
    overall_ratio = (overall_excluded / overall_total) if overall_total else 0.0
    population_not_hollowed = not hollow_files

    equal_detail_group = sum_detail == sum_group
    equal_grand_detail = grand_total == sum_detail
    equal_grand_group = grand_total == sum_group

    # 另一條等式：分組合計（含被排除的小計列）與明細母體的關係
    # 來源檔宣告的小計值加回明細，應該等於「來源檔自己認定的總計」
    # 檔案層級的等式：每個小計列必須等於「自上一個小計列之後的明細和」。
    # 為什麼是這個語意（而不是「等於整個檔案的明細和」）：
    #   來源檔的小計列通常涵蓋**一段**列，不一定涵蓋整個檔案。
    #   2025 費用表的結構是「H-001、H-002、[小計 5800]、H-003」——
    #   小計只涵蓋它**上面**那兩列。用「整檔明細和」去比會永遠不等，
    #   那條等式於是變成一個恆假（恆紅）的假訊號，沒有驗證力。
    #   「自上一個小計之後的累積」是 Excel 小計列的通用語意，
    #   而且它有實際的抓錯能力：數字被手改過時它會紅。
    per_file: list[dict] = []
    per_file_equal: list[bool] = []
    suspected_checks: list[dict] = []
    subtotal_checks: list[dict] = []
    by_file: dict[str, list[Row]] = {}
    for r in result.rows:
        by_file.setdefault(r.source_file, []).append(r)
    for fname, rows in by_file.items():
        # 依原始列序排序 → 小計列與明細列的先後關係才有意義
        rows = sorted(rows, key=lambda r: (r.source_sheet, r.source_row))
        d_sum_total = Decimal("0")
        running = Decimal("0")          # 自上一個小計之後的累積
        file_declared_sum = Decimal("0")
        file_suspected_sum = Decimal("0")
        for r in rows:
            if not r.is_subtotal:
                if r.amount is not None:
                    d_sum_total += r.amount
                    running += r.amount
                continue
            claimed = r.subtotal_claimed_amount
            if claimed is None:
                continue
            matches = (claimed == running)
            layer = r.subtotal_layer
            if layer == "structural":
                file_suspected_sum += claimed
                suspected_checks.append({
                    "file": fname,
                    "sheet": r.source_sheet,
                    "row": r.source_row,
                    "label": r.subtotal_label,
                    "claimed_amount": str(claimed),
                    "running_detail_sum": str(running),
                    "matches_running_sum": matches,
                    "verdict": "confirmed_subtotal" if matches else "likely_detail_row",
                })
            else:
                file_declared_sum += claimed
                subtotal_checks.append({
                    "file": fname,
                    "sheet": r.source_sheet,
                    "row": r.source_row,
                    "label": r.subtotal_label,
                    "claimed_amount": str(claimed),
                    "running_detail_sum": str(running),
                    "matches_running_sum": matches,
                })
            # 累積器重設：下一段小計從 0 重新累積
            running = Decimal("0")
        per_file.append({
            "file": fname,
            "detail_sum": str(d_sum_total),
            "declared_subtotal_sum": str(file_declared_sum),
            "detail_plus_subtotal": str(d_sum_total + file_declared_sum),
            "has_declared_subtotal": file_declared_sum != Decimal("0"),
            "suspected_subtotal_sum": str(file_suspected_sum),
        })
        # 每個**已宣告**的小計列都必須等於它所涵蓋的那段明細和
        per_file_equal.extend(c["matches_running_sum"] for c in subtotal_checks
                               if c["file"] == fname)

    # 檔案層級的等式：檔案自己宣告的小計必須等於該檔的明細和
    file_equations_ok = all(per_file_equal) if per_file_equal else True

    # 疑似小計列必須全部被獨立驗證通過：
    # 宣稱值不等於該檔明細和 → 它其實是明細列被誤判 → 必須亮紅。
    suspected_ok = all(c["matches_running_sum"] for c in suspected_checks)
    suspected_count = len(suspected_checks)

    return {
        "population": {
            "files_scanned": len(result.files),
            "files_ok": sum(1 for f in result.files if f.status == "ok"),
            "files_error": sum(1 for f in result.files if f.status == "error"),
            "files_skipped": sum(1 for f in result.files if f.status == "skipped"),
            "detail_rows_total": len(detail_rows),
            "detail_rows_with_amount": len(amounted),
            "detail_rows_excluded": len(excluded_rows),
            "subtotal_rows_detected": len(subtotal_rows),
            "groups": len(result.groups),
            "excluded_ratio_overall": round(overall_ratio, 4),
            "excluded_ratio_limit": EXCLUDED_RATIO_LIMIT,
            "population_not_hollowed": population_not_hollowed,
            "hollow_files": hollow_files,
        },
        "not_covered": [
            "跨檔案的憑證沒有驗證（不檢查單號是否重複）",
            "沒有驗證日期欄位的格式合法性（只當不透明字串使用）",
            "沒有驗證同一檔內的單號唯一性",
        ],
        "totals": {
            "grand_total": str(grand_total),
            "sum_of_groups": str(sum_group),
            "sum_of_details": str(sum_detail),
            "subtotal_rows_excluded_sum": str(subtotal_excluded),
        },
        "equations": {
            "grand_total == sum_of_details": equal_grand_detail,
            "sum_of_details == sum_of_groups": equal_detail_group,
            "grand_total == sum_of_groups": equal_grand_group,
            "declared_subtotal == running_segment_sum": file_equations_ok,
            "suspected_subtotal_rows_verified": suspected_ok,
        },
        "equations_ok": bool(
            equal_grand_detail and equal_detail_group and equal_grand_group
            and file_equations_ok and suspected_ok
        ),
        # --- 母體完整性（與 equations_ok 是**兩個獨立結論**）---
        #
        # 為什麼要分開：equations_ok=True 只代表「等式成立」，
        # population_not_hollowed=True 才代表「等式有意義」。
        # 使用者看到前者就當成後者，是 11-11 學到的那個失效形狀。
        "population_not_hollowed": population_not_hollowed,
        "per_file_exclusion": per_file_exclusion,
        "group_totals": group_totals,
        "per_file": per_file,
        "declared_subtotal_checks": subtotal_checks,
        "suspected_subtotal_checks": suspected_checks,
        "suspected_subtotal_count": suspected_count,
        "excluded_rows_by_reason": excluded_reasons,
        "excluded_rows_detail": [
            {
                "file": r.source_file,
                "sheet": r.source_sheet,
                "row": r.source_row,
                "raw": r.values.get("金額"),
                "reason": r.amount_reason,
            }
            for r in excluded_rows
        ],
    }


def write_outputs(
    result: MergeResult,
    recon: dict,
    out_xlsx: Path,
    summary_csv: Path,
    issues_csv: Path,
) -> None:
    """寫出合併結果、摘要 CSV、問題清單 CSV。"""
    from openpyxl import Workbook

    out_xlsx.parent.mkdir(parents=True, exist_ok=True)

    wb = Workbook()
    ws = wb.active
    ws.title = "合併明細"
    ws.append(list(CANONICAL_COLUMNS) + ["來源檔", "工作表", "來源列", "分組鍵"])
    for r in result.rows:
        if r.is_subtotal:
            continue
        ws.append([
            r.values.get("日期"), r.values.get("類別"), r.values.get("說明"),
            r.values.get("單號"),
            float(r.amount) if r.amount is not None else None,
            r.source_file, r.source_sheet, r.source_row, r.group_key,
        ])
    wb.save(out_xlsx)

    summary_csv.parent.mkdir(parents=True, exist_ok=True)
    import csv

    with summary_csv.open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh)
        w.writerow(["分組", "列數", "有效金額列數", "合計"])
        for g in recon["group_totals"]:
            w.writerow([g["group"], g["rows"], g["rows_with_amount"], g["total"]])
        w.writerow([])
        w.writerow(["全表總計", recon["population"]["detail_rows_total"],
                    recon["population"]["detail_rows_with_amount"],
                    recon["totals"]["grand_total"]])

    with issues_csv.open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh)
        w.writerow(["嚴重度", "代碼", "檔案", "工作表", "列", "原始值", "說明"])
        for it in result.issues:
            w.writerow([it.get("severity", ""), it.get("code", ""), it.get("file", ""),
                        it.get("sheet", ""), it.get("row", ""), "", it.get("desc", "")])
        for ex in recon["excluded_rows_detail"]:
            w.writerow(["medium", "row_excluded", ex["file"], ex["sheet"], ex["row"],
                        ex["raw"], f"金額無法進入加總母體：{ex['reason']}"])
        for c in recon["suspected_subtotal_checks"]:
            sev = "low" if c["matches_running_sum"] else "high"
            w.writerow([sev, "suspected_subtotal", c["file"], c["sheet"], c["row"],
                        c["claimed_amount"],
                        f"標籤={c['label']!r}；宣稱值與該段明細和"
                        f"（{c['running_detail_sum']}）"
                        f"{'一致，確認為小計列' if c['matches_running_sum'] else '不一致，判定為被誤判的明細列'}"])
        for c in recon["declared_subtotal_checks"]:
            sev = "low" if c["matches_running_sum"] else "high"
            w.writerow([sev, "declared_subtotal", c["file"], c["sheet"], c["row"],
                        c["claimed_amount"],
                        f"標籤={c['label']!r}；宣稱值與該段明細和"
                        f"（{c['running_detail_sum']}）"
                        f"{'一致' if c['matches_running_sum'] else '不一致 → 來源檔的小計數字與其涵蓋的明細對不上'}"])

    # 摘要 JSON（供交付紀錄引用，不手抄數字）
    summary_json = out_xlsx.parent / "merge_summary.json"
    summary_json.write_text(
        json.dumps(recon, ensure_ascii=False, indent=2), encoding="utf-8"
    )
