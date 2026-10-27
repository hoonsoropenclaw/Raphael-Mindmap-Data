"""v4 的回歸測試（pytest）。

測試設計對應 code SOP §2：
  - 至少 3 組輸入：正常 / 空缺資料 / 異常格式
  - 金額/計數類欄位必須含一筆「負值或退款」測試樣本
  - 測試資料本身要先驗證有效（SOP §2.7）

另外鎖住 v4 的六項改進（見 README「v4 相對 v3 的差異」）。
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest
from openpyxl import Workbook, load_workbook

sys.path.insert(0, str(Path(__file__).parent))

import merge_xlsx as M  # noqa: E402


HERE = Path(__file__).parent
SCRIPT = HERE / "merge_xlsx.py"


# ---------- 測試資料工廠 ----------
def _write(path: Path, sheets: dict[str, list[list]]) -> Path:
    wb = Workbook()
    wb.remove(wb.active)
    for name, rows in sheets.items():
        ws = wb.create_sheet(name)
        for row in rows:
            ws.append(row)
    path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(path)
    return path


# ---------- 1) 表頭列自動判定（v4 差異 1） ----------
def test_detect_header_skips_preface_row(tmp_path: Path):
    """說明列在前面時，表頭不是第一列。v3 會把說明列當表頭。"""
    f = _write(
        tmp_path / "preface.xlsx",
        {"S": [["本表為 112 年度結算表"], ["經費項目", "核定金額"], ["業務費", 100]]},
    )
    raws, err = M.read_raw_file(f)
    assert err is None
    decision = M.detect_header_row(raws[0], 2)
    assert decision.header_index == 1, f"應判定表頭在第 2 個非空列，實得 {decision.header_index}"
    assert decision.score >= M.HEADER_DETECT_THRESHOLD


def test_detect_header_manual_override_wins(tmp_path: Path):
    """--header-row 必須優先於自動判定。"""
    f = _write(tmp_path / "m.xlsx", {"S": [["A", "B"], [1, 2]]})
    raws, _ = M.read_raw_file(f)
    sheets = M.parse_sheets(raws, header_override=0)
    assert sheets[0].headers == ["A", "B"]
    assert sheets[0].header.method == "manual"


def test_detect_header_failure_gives_actionable_message(tmp_path: Path):
    """判定失敗要給可行動訊息（列出候選與門檻），不是靜默挑一個。"""
    # 全文字、沒有型別落差 → 全部候選 0 分
    f = _write(tmp_path / "amb.xlsx", {"S": [["甲", "乙"], ["丙", "丁"]]})
    raws, _ = M.read_raw_file(f)
    decision = M.detect_header_row(raws[0], 2)
    assert decision.header_index is None
    assert "--header-row" in decision.reason
    assert "門檻" in decision.reason or "差距" in decision.reason or "分數" in decision.reason
    assert "0-based" in decision.reason
    # 必須列出候選得分，讓使用者知道為什麼失敗
    assert decision.candidates, "失敗時也要列出候選與得分"


def test_detect_header_ambiguous_scores_reported(tmp_path: Path):
    """兩個候選得分幾乎一樣 → 模稜兩可，要回報而不是猜。"""
    # 第 1 列與第 2 列都能拿滿分：兩列都是文字欄名 + 下方有數值欄
    f = _write(
        tmp_path / "tie.xlsx",
        {"S": [["甲", "乙"], ["丙", "丁"], ["業務費", 100]]},
    )
    raws, _ = M.read_raw_file(f)
    decision = M.detect_header_row(raws[0], 2)
    # 第 1 列：甲/乙 下方是 丙/丁（文字）與 業務費/100 → 欄2 有型別落差 → 有分
    # 第 2 列：丙/丁 下方是 業務費/100 → 有分 → 兩者接近 → 模稜兩可
    assert decision.header_index is None
    assert "模稜兩可" in decision.reason or "差距" in decision.reason
    assert "--header-row" in decision.reason


def test_merged_cell_header_name_recovered(tmp_path: Path):
    """合併儲存格吞掉的欄名要補回來（否則欄位名變 Unnamed / 缺一欄）。"""
    wb = Workbook()
    ws = wb.active
    ws.title = "S"
    ws["A1"] = "經費項目"
    ws["B1"] = "核定金額"
    ws.merge_cells("A1:B1")
    ws.append(["業務費", 100])
    f = tmp_path / "merged.xlsx"
    wb.save(f)

    raws, _ = M.read_raw_file(f)
    sheets = M.parse_sheets(raws, header_override=None)
    assert sheets[0].headers == ["經費項目", "經費項目_2"], sheets[0].headers
    assert sheets[0].merge_filled_headers, "應該揭露欄名是借來的"
    assert any("合併儲存格" in w for w in sheets[0].warnings)


def test_header_only_sheet_is_supported(tmp_path: Path):
    """只有表頭沒有資料列的分頁不該被判成失敗。"""
    f = _write(tmp_path / "hdr.xlsx", {"S": [["經費項目", "核定金額"]]})
    raws, _ = M.read_raw_file(f)
    sheets = M.parse_sheets(raws, header_override=None)
    assert sheets[0].error is None
    assert sheets[0].headers == ["經費項目", "核定金額"]
    assert sheets[0].rows == []


# ---------- 2) 欄位型別正規化（v4 差異 2） ----------
@pytest.mark.parametrize(
    "raw,expected",
    [
        ("1,234", 1234.0),
        ("NT$2,000", 2000.0),
        ("１，２３４．５", 1234.5),      # 全形
        ("(500)", -500.0),               # 會計括號負數
        ("500-", -500.0),                # 尾端負號
        ("1.5萬", 15000.0),              # 萬進位
        ("-42", -42.0),
    ],
)
def test_parse_number_normalization(raw, expected):
    out = M.parse_number(raw, "核定金額", is_rate_column=False)
    assert out.ok, out.reason
    assert out.value == pytest.approx(expected)


def test_parse_number_percent_uses_column_semantics():
    """百分比語意由欄位語意決定：率欄 /100，件數欄不猜。"""
    rate = M.parse_number("45%", "執行率", is_rate_column=True)
    assert rate.ok
    assert rate.value == pytest.approx(0.45)

    count = M.parse_number("45%", "件數", is_rate_column=False)
    assert not count.ok
    assert "百分比" in count.reason or "不猜" in count.reason


def test_parse_number_rejects_garbage():
    out = M.parse_number("約一百萬", "核定金額", is_rate_column=False)
    assert not out.ok
    assert out.reason


def test_text_numbers_are_counted_in_sums(tmp_path: Path):
    """v3 的盲區：文字型金額被靜默漏算。v4 必須算進去。"""
    f = _write(
        tmp_path / "textnum.xlsx",
        {"S": [["經費項目", "核定金額"], ["業務費", "1,234"], ["設備費", "NT$2,000"]]},
    )
    raws, _ = M.read_raw_file(f)
    sheets = M.parse_sheets(raws, header_override=None)
    assert not sheets[0].error
    conv, unparsed, numeric = M.normalize_values(sheets, sheets[0].headers)
    assert sheets[0].numeric_sums["核定金額"] == pytest.approx(3234.0)
    assert sum(len(v) for v in unparsed.values()) == 0
    assert len(conv["核定金額"]) == 2, "兩個文字型數字都要有轉換留痕"


def test_unparseable_values_are_reported_not_dropped(tmp_path: Path):
    """無法解析的值要獨立成清單（不算 0、不丟棄）。"""
    f = _write(
        tmp_path / "bad.xlsx",
        {"S": [["經費項目", "核定金額"], ["業務費", "約一百萬"], ["設備費", 200000]]},
    )
    raws, _ = M.read_raw_file(f)
    sheets = M.parse_sheets(raws, header_override=0)
    _, unparsed, _ = M.normalize_values(sheets, sheets[0].headers)
    items = unparsed.get("核定金額", [])
    assert len(items) == 1
    assert items[0]["raw"] == "約一百萬"
    assert items[0]["reason"]
    # 可解析的那筆仍然要算進去
    assert sheets[0].numeric_sums["核定金額"] == pytest.approx(200000.0)


def test_negative_text_amount_triggers_alert(tmp_path: Path):
    """負值／退款警示要涵蓋「原本是文字」的值（v3 同一個盲區）。"""
    f = _write(
        tmp_path / "neg.xlsx",
        {"S": [["經費項目", "核定金額"], ["退款", "(500)"], ["業務費", 1000]]},
    )
    raws, _ = M.read_raw_file(f)
    sheets = M.parse_sheets(raws, header_override=0)
    M.normalize_values(sheets, sheets[0].headers)
    reasons = " ".join(a["reason"] for a in sheets[0].alerts)
    assert "負值" in reasons
    assert sheets[0].numeric_sums["核定金額"] == pytest.approx(500.0)


def test_label_column_not_treated_as_numeric(tmp_path: Path):
    """「經費項目」是標籤欄，不能因為含關鍵字「經費」就被當數值欄。"""
    f = _write(
        tmp_path / "label.xlsx",
        {"S": [["經費項目", "核定金額"], ["業務費", 100], ["設備費", 200]]},
    )
    raws, _ = M.read_raw_file(f)
    sheets = M.parse_sheets(raws, header_override=0)
    _, unparsed, numeric = M.normalize_values(sheets, sheets[0].headers)
    assert "經費項目" not in numeric
    assert sum(len(v) for v in unparsed.values()) == 0


def test_rate_column_scale_is_consistent_within_column(tmp_path: Path):
    """同一欄裡的原生值與文字值必須同一尺度（回歸：'0.5' 曾被算成 0.005）。"""
    f = _write(
        tmp_path / "rate.xlsx",
        {"S": [["經費項目", "執行率"], ["業務費", 0.95], ["設備費", "0.5"]]},
    )
    raws, _ = M.read_raw_file(f)
    sheets = M.parse_sheets(raws, header_override=0)
    M.normalize_values(sheets, sheets[0].headers)
    M.apply_normalized_values(sheets, sheets[0].headers, {"執行率"})
    # 原生 0.95 → 尺度已是比率 → 文字 '0.5' 不該被 /100（否則會變成 0.005）
    assert sheets[0].rows[0][1] == pytest.approx(0.95)   # 業務費（原生）
    assert sheets[0].rows[1][1] == pytest.approx(0.5)    # 設備費（文字）


def test_rate_column_with_percent_native_values(tmp_path: Path):
    """原生值是百分點（95）時，文字值要 x0.01 對齊。"""
    f = _write(
        tmp_path / "rate2.xlsx",
        {"S": [["經費項目", "執行率"], ["業務費", 95], ["設備費", "50%"]]},
    )
    raws, _ = M.read_raw_file(f)
    sheets = M.parse_sheets(raws, header_override=0)
    M.normalize_values(sheets, sheets[0].headers)
    M.apply_normalized_values(sheets, sheets[0].headers, {"執行率"})
    assert sheets[0].rows[1][1] == pytest.approx(0.5)   # '50%' → 0.5
    assert sheets[0].rows[0][1] == pytest.approx(95.0)  # 原生 95 不動（尺度 0.01 僅套文字值）


def test_rate_column_ambiguous_scale_is_disclosed(tmp_path: Path):
    """原生值同時有 ≤1 與 >1 → 尺度無法推導，必須揭露而不是猜。"""
    f = _write(
        tmp_path / "rate3.xlsx",
        {"S": [["經費項目", "執行率"], ["業務費", 0.95], ["設備費", 95]]},
    )
    raws, _ = M.read_raw_file(f)
    sheets = M.parse_sheets(raws, header_override=0)
    M.normalize_values(sheets, sheets[0].headers)
    notes = " ".join(sheets[0].column_warnings)
    assert "尺度" in notes


def test_rate_column_not_summed(tmp_path: Path):
    """率欄位不做合計（比率加總沒有意義）→ 改列平均。"""
    folder = tmp_path / "in"
    folder.mkdir()
    _write(folder / "a.xlsx", {"S": [["經費項目", "執行率"], ["業務費", 0.95], ["設備費", 0.5]]})
    out = tmp_path / "merged.xlsx"
    assert M.main([str(folder), "-o", str(out), "--apply"]) == 0
    wb = load_workbook(out)
    ws = wb["數值合計"]
    rows = list(ws.iter_rows(values_only=True))
    wb.close()
    rate_rows = [r for r in rows[1:] if r[2] and "執行率" in str(r[2])]
    assert rate_rows, "應該有執行率的列"
    assert "平均" in str(rate_rows[0][2])
    # 平均 = (0.95 + 0.5) / 2 = 0.725，不是合計 1.45
    assert rate_rows[0][3] == pytest.approx(0.725)


# ---------- 3) 輸入集合界定（v4 差異 3） ----------
def test_output_file_excluded_from_inputs(tmp_path: Path):
    """重跑時輸出檔／備份檔不能被當輸入（v3 實測：8 列 → 36 列、金額 double）。"""
    folder = tmp_path / "in"
    folder.mkdir()
    _write(folder / "a.xlsx", {"S": [["經費項目", "核定金額"], ["業務費", 100]]})
    out = tmp_path / "merged.xlsx"

    # 真實使用情境：輸出檔就放在「輸入資料夾裡」（行政使用者最常見的用法）
    out = folder / "merged.xlsx"
    rules = M.default_exclusion_rules(out, [])
    files, skipped, manifest = M.scan_inputs(folder, rules)
    assert [p.name for p in files] == ["a.xlsx"]

    # 產出後再掃一次：輸出檔與備份檔都必須被排除
    M.atomic_save_workbook(Workbook(), out, backup=True)
    (folder / f"{out.stem}.bak-20260101-000000").write_bytes(b"x")
    files2, skipped2, manifest2 = M.scan_inputs(folder, rules)
    assert [p.name for p in files2] == ["a.xlsx"], f"重跑把輸出當輸入了：{[p.name for p in files2]}"
    excluded_names = {n for n, _ in skipped2}
    assert "merged.xlsx" in excluded_names, skipped2
    # 輸入集合明細必須可稽核（每個檔案都有決定與理由）
    assert all(e["decision"] in ("納入", "排除", "略過") for e in manifest2)
    assert all(e["reason"] for e in manifest2)
    by_name = {e["name"]: e for e in manifest2}
    assert by_name["merged.xlsx"]["decision"] == "排除"
    assert "排除" in by_name["merged.xlsx"]["reason"]


def test_three_consecutive_runs_produce_identical_data(tmp_path: Path):
    """連續跑 3 次，合併資料必須完全一致（輸入集合界定的回歸鎖）。"""
    folder = tmp_path / "in"
    folder.mkdir()
    _write(folder / "a.xlsx", {"S": [["經費項目", "核定金額"], ["業務費", 100]]})
    _write(folder / "b.xlsx", {"S": [["經費項目", "核定金額"], ["設備費", 200]]})

    out = tmp_path / "out.xlsx"
    signatures = []
    for i in range(3):
        rc = M.main([str(folder), "-o", str(out), "--apply"])
        assert rc == 0
        wb = load_workbook(out)
        ws = wb["合併資料"]
        signatures.append(tuple(tuple(c.value for c in row) for row in ws.iter_rows()))
        wb.close()
    assert signatures[0] == signatures[1] == signatures[2]
    # 資料列數必須是 2（不是 4 / 6：備份與輸出被重新掃進去就會暴增）
    assert len(signatures[0]) - 1 == 2


def test_exclude_glob_user_rule(tmp_path: Path):
    folder = tmp_path / "in"
    folder.mkdir()
    _write(folder / "a.xlsx", {"S": [["經費項目"], ["x"]]})
    _write(folder / "草稿.xlsx", {"S": [["經費項目"], ["y"]]})
    rules = M.default_exclusion_rules(tmp_path / "o.xlsx", [])
    rules.append(M.ExclusionRule("使用者排除", "草稿*", "使用者指定", "glob"))
    files, skipped, manifest = M.scan_inputs(folder, rules)
    assert [p.name for p in files] == ["a.xlsx"]
    assert any(n == "草稿.xlsx" for n, _ in skipped)


# ---------- 4) Windows 實測揭露（v4 差異 4） ----------
def test_windows_path_validation_detects_illegal_names():
    problems = M.validate_windows_component("bad:name.xlsx")
    assert problems, "應偵測到 Windows 禁用字元"
    assert M.validate_windows_component("normal.xlsx") == []


def test_windows_reserved_device_name_detected():
    problems = M.validate_windows_component("CON.xlsx")
    assert problems
    assert "保留" in problems[0]


def test_windows_path_on_linux_is_rejected():
    """Windows 形式路徑在 Linux 上必須擋下（否則寫出怪檔名）。"""
    problems = M.validate_target_path("C:\\out\\merged.xlsx")
    if M.os.name != "nt":
        assert any("非 Windows" in p for p in problems)


# ---------- 5) 交付閘門機檢（v4 差異 5） ----------
def test_no_protection_disabling_flags():
    """不得提供關閉保護的旗標（code SOP §1.4 / §6 檢查 1）。"""
    import argparse

    parser = M.build_parser()
    dests = {a.dest for a in parser._actions}
    for banned in ("no_backup", "force", "skip_confirm", "no_backup_flag"):
        assert banned not in dests, f"發現關閉保護的旗標：{banned}"


def test_dry_run_by_default_writes_nothing(tmp_path: Path):
    folder = tmp_path / "in"
    folder.mkdir()
    _write(folder / "a.xlsx", {"S": [["經費項目", "核定金額"], ["業務費", 100]]})
    out = tmp_path / "merged.xlsx"
    rc = M.main([str(folder), "-o", str(out)])
    assert rc == 0
    assert not out.exists(), "dry-run 不該寫出檔案"


# ---------- 6) 其它回歸（v3 已修的缺陷不能復發） ----------
def test_formula_cells_are_flagged(tmp_path: Path):
    """公式儲存格沒有快取值時讀出來是空 → 必須警告。"""
    wb = Workbook()
    ws = wb.active
    ws.title = "S"
    ws.append(["經費項目", "核定金額"])
    ws.append(["業務費", "=1+1"])
    f = tmp_path / "formula.xlsx"
    wb.save(f)

    raws, _ = M.read_raw_file(f)
    assert raws[0].formula_cells, "應該偵測到公式儲存格"
    sheets = M.parse_sheets(raws, header_override=0)
    assert any("公式" in w for w in sheets[0].warnings)


def test_duplicate_header_names_deduplicated(tmp_path: Path):
    f = _write(tmp_path / "dup.xlsx", {"S": [["金額", "金額"], [1, 2]]})
    raws, _ = M.read_raw_file(f)
    sheets = M.parse_sheets(raws, header_override=0)
    assert sheets[0].headers == ["金額", "金額_2"]
    assert any("重複欄名" in w for w in sheets[0].warnings)


def test_old_format_reported_not_silently_skipped(tmp_path: Path):
    folder = tmp_path / "in"
    folder.mkdir()
    _write(folder / "a.xlsx", {"S": [["經費項目"], ["x"]]})
    (folder / "old.xls").write_bytes(b"junk")
    files, skipped, manifest = M.scan_inputs(folder, M.default_exclusion_rules(tmp_path / "o.xlsx", []))
    assert [p.name for p in files] == ["a.xlsx"]
    assert any("old.xls" == n and ".xls" in r for n, r in skipped)


def test_cli_returns_nonzero_when_header_undetectable(tmp_path: Path):
    """需要人工指定表頭列時，exit code 必須非 0（不能靜默少算資料）。"""
    folder = tmp_path / "in"
    folder.mkdir()
    _write(folder / "amb.xlsx", {"S": [["甲", "乙"], ["丙", "丁"]]})
    out = tmp_path / "merged.xlsx"
    rc = M.main([str(folder), "-o", str(out), "--apply"])
    assert rc != 0, "表頭無法判定時不該回傳 0"


def test_cli_exits_zero_after_per_file_override(tmp_path: Path):
    folder = tmp_path / "in"
    folder.mkdir()
    _write(folder / "amb.xlsx", {"S": [["甲", "乙"], ["丙", "丁"]]})
    out = tmp_path / "merged.xlsx"
    rc = M.main([
        str(folder), "-o", str(out), "--apply",
        "--header-row-for", "amb.xlsx=0",
    ])
    assert rc == 0
    assert out.exists()


def test_output_workbook_has_required_sheets(tmp_path: Path):
    folder = tmp_path / "in"
    folder.mkdir()
    _write(folder / "a.xlsx", {"S": [["經費項目", "核定金額"], ["業務費", 100]]})
    out = tmp_path / "merged.xlsx"
    assert M.main([str(folder), "-o", str(out), "--apply"]) == 0
    wb = load_workbook(out)
    names = wb.sheetnames
    for required in (
        "合併資料", "檔案摘要", "數值合計", "型別轉換",
        "無法解析", "退款警示", "輸入集合", "本次執行", "略過檔案",
    ):
        assert required in names, f"缺少分頁：{required}"
    wb.close()


def test_summary_csv_columns_match_sheet_columns(tmp_path: Path):
    """CSV 摘要欄位必須與工作表一一對應。"""
    import csv

    folder = tmp_path / "in"
    folder.mkdir()
    _write(folder / "a.xlsx", {"S": [["經費項目", "核定金額"], ["業務費", 100]]})
    out = tmp_path / "merged.xlsx"
    csv_path = tmp_path / "summary.csv"
    assert M.main([str(folder), "-o", str(out), "--summary-csv", str(csv_path), "--apply"]) == 0

    wb = load_workbook(out)
    ws = wb["檔案摘要"]
    sheet_header = [c.value for c in ws[1]]
    wb.close()
    with csv_path.open(encoding="utf-8-sig", newline="") as fh:
        csv_header = next(csv.reader(fh))
    assert sheet_header == csv_header


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
