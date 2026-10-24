"""merge_xlsx v2 的測試套件。

涵蓋：
  1. 正常情境（多檔多分頁、欄位聯集、數值合計、退款/負值警示）
  2. 空/缺資料情境（只有表頭、資料夾無 xlsx）
  3. 異常格式情境（損毀檔、偽裝檔、密碼保護檔）
  4. 原子寫入（os.replace + fsync；失敗時不留下半套檔）
  5. Windows 路徑預檢（禁用字元、保留裝置名、MAX_PATH 260）
  6. CSV 編碼（utf-8-sig BOM 存在；cp950 可解碼）

執行：python -m pytest test_merge_xlsx.py -v
"""
from __future__ import annotations

import csv
import io
import os
import sys
from pathlib import Path

import pytest
from openpyxl import load_workbook

sys.path.insert(0, str(Path(__file__).resolve().parent))

import merge_xlsx as mx  # noqa: E402

HERE = Path(__file__).resolve().parent
NORMAL = HERE / "test_data"
EMPTY = HERE / "test_data_empty"
BAD = HERE / "test_data_bad"


# ---------- 1. 正常情境 ----------
def test_normal_merges_all_files_and_sheets():
    results, usable, errors, _skipped = mx.merge_all(NORMAL, Path("/nonexistent/out.xlsx"))
    assert errors == [], f"正常資料不該有錯誤：{errors}"
    assert len(results) == 2, "應該解析到 2 個檔案"
    # 一月 + 二月 + 三月 = 3 個可合併分頁
    assert len(usable) == 3
    assert sum(len(s.rows) for s in usable) == 3 + 2 + 3


def test_union_headers_collects_all_columns():
    _, usable, _, _skipped = mx.merge_all(NORMAL, Path("/nonexistent/out.xlsx"))
    union = mx.union_headers(usable)
    # 欄位聯集：單號/處室/金額/數量/部門/備註
    for expected in ("單號", "處室", "金額", "數量", "部門", "備註"):
        assert expected in union, f"聯集欄位缺少 {expected}"
    assert len(union) == len(set(union)), "聯集欄位不應有重複"


def test_numeric_sums_are_correct():
    _, usable, _, _skipped = mx.merge_all(NORMAL, Path("/nonexistent/out.xlsx"))
    by_sheet = {s.sheet_name: s for s in usable}
    # 一月：1200 + 800 + 450 = 2450；數量：3+1+2 = 6
    assert by_sheet["一月"].numeric_sums["金額"] == 2450
    assert by_sheet["一月"].numeric_sums["數量"] == 6
    # 三月：1500 + (-300) + 99 = 1299
    assert by_sheet["三月"].numeric_sums["金額"] == 1299


def test_refund_and_negative_alerts_detected():
    _, usable, _, _skipped = mx.merge_all(NORMAL, Path("/nonexistent/out.xlsx"))
    alerts = [a for s in usable for a in s.alerts]
    assert len(alerts) == 1, f"應該只有 1 筆警示（-300 的金額列），實際 {alerts}"
    alert = alerts[0]
    assert alert["value"] == -300
    assert "負值" in alert["reason"]
    assert alert["file"].endswith("3月經費.xlsx")


def test_keyword_column_flagged_as_refund():
    """欄名含「退款」時，即使數值非負也要標示。"""
    _, usable, _, _skipped = mx.merge_all(NORMAL, Path("/nonexistent/out.xlsx"))
    # 目前測試資料沒有退款欄名欄，用單獨測試驗證邏輯
    sheet = mx.SheetData(file_name="x.xlsx", sheet_name="s", headers=["退款金額"])
    assert "退款" in sheet.headers[0]
    assert any("退款" in kw for kw in mx.REFUND_KEYWORDS)


def test_missing_and_extra_columns_reported():
    """三月缺「數量」、多「部門」「備註」→ 缺漏/獨有欄位要被記錄。

    注意「獨有欄位」的定義：相對於「其他所有分頁的聯集」而言，只出現在這個分頁的欄位。
    （若相對 union 定義則永遠是空——union 本身就是所有欄位的聯集。）
    """
    _, usable, _, _skipped = mx.merge_all(NORMAL, Path("/nonexistent/out.xlsx"))
    union = mx.union_headers(usable)
    march = next(s for s in usable if s.sheet_name == "三月")
    missing = [h for h in union if h not in march.headers]
    assert "數量" in missing

    # 獨有欄位：只出現在三月、其他分頁都沒有的欄位
    others = set()
    for s in usable:
        if s is not march:
            others |= set(s.headers)
    exclusive = [h for h in march.headers if h not in others]
    assert "部門" in exclusive and "備註" in exclusive, f"獨有欄位應含 部門/備註，實際 {exclusive}"


# ---------- 2. 空 / 缺資料情境 ----------
def test_empty_sheet_is_reported_not_crashed():
    """只有表頭的分頁：不算錯誤，但要標示「只有表頭」且不貢獻資料列。"""
    results, usable, errors, _skipped = mx.merge_all(EMPTY, Path("/nonexistent/out.xlsx"))
    assert len(results) == 1
    assert errors == [], "只有表頭不是錯誤"
    assert len(usable) == 1, "分頁本身可用（表頭有效）"
    assert usable[0].rows == [], "沒有資料列"
    assert usable[0].headers == ["單號", "金額"]


def test_folder_without_xlsx_gives_actionable_error(tmp_path, capsys):
    empty_dir = tmp_path / "no_xlsx"
    empty_dir.mkdir()
    (empty_dir / "readme.txt").write_text("不是 excel", encoding="utf-8")
    rc = mx.main([str(empty_dir), "--apply"])
    assert rc == 2
    err = capsys.readouterr().err
    assert "找不到" in err
    assert ".xlsx" in err, "訊息要說明要找什麼副檔名"
    assert "另存為" in err, "要給可行動解法（舊 .xls 請另存為 .xlsx）"


def test_missing_input_folder_gives_exit_code_2(tmp_path):
    rc = mx.main([str(tmp_path / "nope"), "--apply"])
    assert rc == 2


def test_empty_folder_gives_exit_code_2(tmp_path):
    rc = mx.main([str(tmp_path), "--apply"])
    assert rc == 2, "空資料夾應回 2 並給可行動訊息"


# ---------- 3. 異常格式情境 ----------
def test_broken_files_are_skipped_with_message():
    results, usable, errors, _skipped = mx.merge_all(BAD, Path("/nonexistent/out.xlsx"))
    assert len(results) == 3, "3 個壞檔都要被記錄（不可靜默略過）"
    assert usable == []
    assert len(errors) == 3
    joined = " ".join(errors)
    assert "無法開啟" in joined
    assert "常見原因" in joined, "錯誤訊息要可行動（說明常見原因）"


def test_bad_folder_cli_returns_error_code(tmp_path):
    out = tmp_path / "merged.xlsx"
    rc = mx.main([str(BAD), "-o", str(out), "--apply"])
    assert rc == 4, "全部解析失敗應回 4（區分於「沒檔案」的 2）"


def test_locked_temp_file_is_skipped():
    """Excel 開檔會產生 ~$xxx.xlsx 鎖檔，必須被跳過而不是報錯。"""
    d = HERE / "_tmp_locked"
    d.mkdir(exist_ok=True)
    (d / "~$test.xlsx").write_bytes(b"lock")
    try:
        results, _, errors, _skipped = mx.merge_all(d, Path("/nonexistent/out.xlsx"))
        assert results == [], "鎖檔不該被當成輸入"
        assert errors == []
    finally:
        (d / "~$test.xlsx").unlink()
        d.rmdir()


def test_unsupported_suffix_is_reported_not_silently_dropped(tmp_path):
    """.xls / .xlsm 必須被「略過並回報原因」，不能靜默消失。"""
    d = tmp_path / "mixed"
    d.mkdir()
    from openpyxl import Workbook

    wb = Workbook()
    wb.active.append(["a"])
    wb.save(d / "ok.xlsx")
    (d / "舊格式.xls").write_bytes(b"\xd0\xcf\x11\xe0")
    (d / "含巨集.xlsm").write_bytes(b"\xd0\xcf\x11\xe0")
    (d / "一般.csv").write_text("a,b\n1,2\n", encoding="utf-8")

    results, _, _, skipped = mx.merge_all(d, Path("/nonexistent/out.xlsx"))
    assert len(results) == 1, "只有 .xlsx 該被合併"
    names = {name for name, _ in skipped}
    assert "舊格式.xls" in names
    assert "含巨集.xlsm" in names
    reasons = {name: reason for name, reason in skipped}
    assert "另存為 .xlsx" in reasons["舊格式.xls"], "要給可行動解法"
    # .csv 不屬於 Excel 家族，不該列出來騷擾使用者
    assert "一般.csv" not in names


# ---------- 4. 原子寫入 ----------
def test_atomic_write_bytes_creates_file(tmp_path):
    target = tmp_path / "out.bin"
    mx.atomic_write_bytes(target, b"hello")
    assert target.read_bytes() == b"hello"


def test_atomic_write_leaves_no_temp_files(tmp_path):
    target = tmp_path / "out.bin"
    mx.atomic_write_bytes(target, b"hello")
    leftovers = [p.name for p in tmp_path.iterdir() if p.name != "out.bin"]
    assert leftovers == [], f"不應留下暫存檔：{leftovers}"


def test_atomic_write_replaces_content_atomically(tmp_path):
    """寫入成功時：舊內容被完整替換，不是追加。"""
    target = tmp_path / "out.bin"
    target.write_bytes(b"ORIGINAL")
    mx.atomic_write_bytes(target, b"x" * 10)
    assert target.read_bytes() == b"x" * 10
    assert list(p.name for p in tmp_path.iterdir()) == ["out.bin"], "不應留暫存檔"


def test_atomic_write_failure_keeps_old_file_intact(tmp_path):
    """寫入失敗時：舊檔完整、不留半套輸出、不留暫存檔。"""
    target = tmp_path / "out.bin"
    target.write_bytes(b"ORIGINAL")
    with pytest.raises(ValueError):
        # 用不可編碼的 payload 觸發 UnicodeEncodeError（在寫入中途失敗）
        mx.atomic_write_bytes(target, "繁中".encode("ascii"))
    assert target.read_bytes() == b"ORIGINAL", "舊檔必須完好"
    assert list(p.name for p in tmp_path.iterdir()) == ["out.bin"], "失敗後不應留暫存檔"


def test_atomic_write_exception_does_not_corrupt(tmp_path):
    target = tmp_path / "out.bin"
    target.write_bytes(b"ORIGINAL")
    with pytest.raises(ValueError):
        # 用不可編碼的 payload 觸發 UnicodeEncodeError
        mx.atomic_write_bytes(target, "繁中".encode("ascii"))
    assert target.read_bytes() == b"ORIGINAL", "舊檔必須完好"
    assert list(p.name for p in tmp_path.iterdir()) == ["out.bin"]


def test_atomic_save_workbook_backs_up_with_timestamp(tmp_path):
    from openpyxl import Workbook

    target = tmp_path / "merged.xlsx"
    wb = Workbook()
    wb.active["A1"] = "v1"
    mx.atomic_save_workbook(wb, target, backup=True)
    assert target.exists()

    wb2 = Workbook()
    wb2.active["A1"] = "v2"
    backup = mx.atomic_save_workbook(wb2, target, backup=True)
    assert backup is not None and backup.exists()
    assert ".bak-" in backup.name, "備份必須帶時間戳，不能用固定 .bak"
    # 備份副檔名刻意不保留 .xlsx：否則重跑時備份檔會被 .xlsx 掃描器選中當成輸入合併
    # （實測：8 列 → 36 列、金額 6399 → 12798）。
    assert backup.suffix != ".xlsx", "備份檔不可保留 .xlsx 副檔名，否則會被重跑時自我合併"
    # 內容仍是有效 xlsx（只是副檔名不是 .xlsx，openpyxl 不會依副檔名判斷，用二進位讀取驗證）
    assert backup.read_bytes()[:2] == b"PK", "備份必須是完整的 xlsx（zip）內容"
    assert load_workbook(target).active["A1"].value == "v2"


def test_atomic_save_workbook_no_backup_option(tmp_path):
    from openpyxl import Workbook

    target = tmp_path / "merged.xlsx"
    wb = Workbook()
    wb.save(target)
    wb2 = Workbook()
    backup = mx.atomic_save_workbook(wb2, target, backup=False)
    assert backup is None
    assert not list(tmp_path.glob("*.bak-*"))


# ---------- 5. Windows 路徑預檢 ----------
def test_looks_like_windows_path_detection():
    assert mx.looks_like_windows_path(r"C:\Users\test")
    assert mx.looks_like_windows_path(r"\\server\share\file.xlsx")
    assert not mx.looks_like_windows_path("/home/user/file.xlsx")
    assert not mx.looks_like_windows_path("")


def test_illegal_windows_chars_rejected():
    problems = mx.validate_windows_component("bad:name.xlsx")
    assert problems, "含 : 的檔名應被擋"
    assert "禁用字元" in problems[0]


def test_reserved_device_name_rejected():
    problems = mx.validate_windows_component("NUL.xlsx")
    assert problems
    assert "保留裝置名" in problems[0]


def test_max_path_over_260_rejected():
    long_path = "C:\\" + "a" * 300
    problems = mx.validate_windows_path(long_path)
    assert any("MAX_PATH" in p for p in problems), f"應提示 MAX_PATH：{problems}"
    assert any("LongPathsEnabled" in p for p in problems), "要給可行動解法"


def test_unc_path_under_limit_accepted():
    problems = mx.validate_windows_path(r"\\server\share\2026\report.xlsx")
    assert problems == [], f"正常 UNC 路徑不該有問題：{problems}"


def test_validate_target_path_uses_windows_rules_for_drive_paths():
    problems = mx.validate_target_path(r"C:\out\bad?name.xlsx")
    assert any("禁用字元" in p for p in problems)


def test_windows_path_on_posix_is_rejected():
    """Windows 路徑在非 Windows 上必須被擋（否則會寫出字面檔名 C:\\... 的怪檔）。"""
    import os as _os

    if _os.name == "nt":
        pytest.skip("Windows 上本來就該接受 Windows 路徑")
    problems = mx.validate_target_path(r"C:\out\merged.xlsx")
    assert any("非 Windows" in p for p in problems), f"應提示跨 OS 問題：{problems}"


def test_drive_letter_is_not_treated_as_filename():
    """磁碟機代號 C:\\ 本身合法，不該被誤報成「含禁用字元的檔名」。"""
    problems = mx.validate_windows_path(r"C:\out\merged.xlsx")
    assert problems == [], f"合法 Windows 路徑不該有問題：{problems}"


# ---------- 6. CSV 編碼 ----------
def test_csv_written_with_utf8_sig_bom(tmp_path):
    rows = [["檔名", "分頁"], ["a.xlsx", "一月"]]
    target = tmp_path / "summary.csv"
    mx.atomic_write_csv(target, rows, "utf-8-sig")
    raw = target.read_bytes()
    assert raw.startswith(b"\xef\xbb\xbf"), "utf-8-sig 必須有 BOM，否則 Excel 會亂碼"
    decoded = raw.decode("utf-8-sig")
    assert "一月" in decoded


def test_csv_written_with_cp950(tmp_path):
    rows = [["檔名"], ["繁中測試.xlsx"]]
    target = tmp_path / "summary_cp950.csv"
    mx.atomic_write_csv(target, rows, "cp950")
    raw = target.read_bytes()
    assert not raw.startswith(b"\xef\xbb\xbf")
    assert "繁中測試" in raw.decode("cp950")


def test_csv_roundtrip_with_csv_module(tmp_path):
    rows = [["檔名", "狀態"], ["a.xlsx", "成功"], ["b.xlsx", "失敗"]]
    target = tmp_path / "s.csv"
    mx.atomic_write_csv(target, rows, "utf-8-sig")
    with open(target, encoding="utf-8-sig", newline="") as fh:
        parsed = list(csv.reader(fh))
    assert parsed == rows


# ---------- 整合：CLI 端到端 ----------
def test_cli_dry_run_writes_nothing(tmp_path, capsys):
    out = tmp_path / "merged.xlsx"
    rc = mx.main([str(NORMAL), "-o", str(out)])
    assert rc == 0
    assert not out.exists(), "dry-run 不該寫檔"
    assert "dry-run" in capsys.readouterr().out


def test_cli_apply_writes_workbook_with_all_sheets(tmp_path):
    out = tmp_path / "merged.xlsx"
    csv_out = tmp_path / "summary.csv"
    rc = mx.main([str(NORMAL), "-o", str(out), "--summary-csv", str(csv_out), "--apply"])
    assert rc == 0
    assert out.exists() and csv_out.exists()

    wb = load_workbook(out)
    assert set(wb.sheetnames) == {
        "合併資料", "檔案摘要", "數值合計", "退款警示", "本次執行", "略過檔案"
    }
    ws = wb["合併資料"]
    assert ws.max_row == 9, f"1 表頭 + 8 資料列，實際 {ws.max_row}"
    headers = [c.value for c in ws[1]]
    assert "_來源檔" in headers and "_來源分頁" in headers

    wb2 = load_workbook(out, data_only=True)
    run = {r[0].value: r[1].value for r in wb2["本次執行"].iter_rows()}
    assert run["解析檔數"] == 2
    assert run["可用分頁數"] == 3
    assert run["合併後總列數"] == 8
    assert run["警示筆數"] == 1


def test_cli_apply_is_idempotent(tmp_path):
    """重跑同一命令，輸出內容一致（可重跑不損壞資料）。"""
    out = tmp_path / "merged.xlsx"
    mx.main([str(NORMAL), "-o", str(out), "--apply"])
    first = load_workbook(out)["合併資料"].max_row
    mx.main([str(NORMAL), "-o", str(out), "--apply"])
    second = load_workbook(out)["合併資料"].max_row
    assert first == second == 9
    assert list(tmp_path.glob("*.bak-*")), "第二次執行應產生時間戳備份"


def test_rerun_output_inside_input_folder_does_not_self_merge(tmp_path):
    """回歸測試（2026-10-24 evaluate 抓到）：輸出寫在輸入資料夾內、連跑 3 次仍須穩定。

    這是使用者最自然的用法：cd 進資料夾後 `python merge_xlsx.py . --apply`（預設 -o merged.xlsx）。
    舊版把時間戳備份檔（.bak-*.xlsx）當成輸入合併 → 8 列變 36 列、金額 6399 變 12798。
    """
    import shutil as _shutil

    work = tmp_path / "work"
    work.mkdir()
    for src in sorted(NORMAL.glob("*.xlsx")):
        _shutil.copy2(src, work / src.name)

    out = work / "merged.xlsx"
    expected_rows = 8
    expected_sum = 6399
    for i in range(3):
        rc = mx.main([str(work), "-o", str(out), "--apply"])
        assert rc == 0, f"第 {i + 1} 次執行應成功"
        wb = load_workbook(out, data_only=True)
        ws = wb["合併資料"]
        assert ws.max_row - 1 == expected_rows, (
            f"第 {i + 1} 次執行資料列數應維持 {expected_rows}，實際 {ws.max_row - 1}"
            "（備份檔被當成輸入合併了）"
        )
        # 金額合計必須維持 6399（= 2450 + 2650 + 1299）
        total = sum(
            r[3].value
            for r in wb["數值合計"].iter_rows(min_row=2)
            if r[2].value == "金額"
        )
        assert total == expected_sum, (
            f"第 {i + 1} 次執行金額合計應維持 {expected_sum}，實際 {total}（資料被重複合併）"
        )


def test_legacy_bak_xlsx_backup_is_excluded(tmp_path):
    """舊版（v2 舊碼）留下的 merged.bak-*.xlsx 也必須被排除。"""
    import shutil as _shutil

    work = tmp_path / "work"
    work.mkdir()
    for src in sorted(NORMAL.glob("*.xlsx")):
        _shutil.copy2(src, work / src.name)
    # 模擬舊版備份檔：名字帶 .bak- 且仍以 .xlsx 結尾
    legacy = work / "merged.bak-20260101-000000.xlsx"
    _shutil.copy2(sorted(NORMAL.glob("*.xlsx"))[0], legacy)

    out = work / "merged.xlsx"
    mx.main([str(work), "-o", str(out), "--apply"])
    ws = load_workbook(out, data_only=True)["合併資料"]
    assert ws.max_row - 1 == 8, f"舊版備份檔不應被合併（實際 {ws.max_row - 1} 列）"


def test_source_row_number_matches_original_excel(tmp_path):
    """回歸測試（2026-10-24 evaluate 抓到）：_來源列號 必須對得上原始 Excel 的實際列號。

    原始檔中間有空白列時，舊版先濾掉空列再從 2 起算 → 列號逐列偏移，來源追溯不可信。
    """
    from openpyxl import Workbook

    src = tmp_path / "有空白列.xlsx"
    wb = Workbook()
    ws = wb.active
    ws.title = "資料"
    ws.append(["單號", "金額"])
    ws.append(["A1", 100])
    ws.append([None, None])   # 空白分隔列（真實 Excel 常見）
    ws.append(["A2", 200])
    ws.append([None, None])   # 空白分隔列
    ws.append(["A3", 300])
    wb.save(src)

    out = tmp_path / "merged.xlsx"
    mx.main([str(tmp_path), "-o", str(out), "--apply"])
    ws2 = load_workbook(out, data_only=True)["合併資料"]
    headers = [c.value for c in ws2[1]]
    col_id = headers.index("_來源列號")
    got = {r[0]: r[col_id] for r in ws2.iter_rows(min_row=2, values_only=True)}
    assert got == {"A1": 2, "A2": 4, "A3": 6}, f"_來源列號 應等於原始 Excel 列號，實際 {got}"


def test_duplicate_header_does_not_lose_data(tmp_path):
    """回歸測試（2026-10-24 evaluate 抓到）：重複表頭不得靜默遺失資料。

    舊版 dict(zip(headers, values)) 讓後者覆蓋前者 → 金額 100 無聲消失，
    但數值合計仍算 100+200=300，兩個分頁互相矛盾。
    """
    from openpyxl import Workbook

    src = tmp_path / "重複表頭.xlsx"
    wb = Workbook()
    ws = wb.active
    ws.title = "資料"
    ws.append(["金額", "金額", "備註"])
    ws.append([100, 200, "x"])
    wb.save(src)

    out = tmp_path / "merged.xlsx"
    mx.main([str(tmp_path), "-o", str(out), "--apply"])
    wb2 = load_workbook(out, data_only=True)
    ws2 = wb2["合併資料"]
    headers = [c.value for c in ws2[1]]
    assert len(set(headers)) == len(headers), f"欄名不可重複：{headers}"
    values = [ws2.cell(row=2, column=i + 1).value for i in range(len(headers))]
    assert 100 in values, f"重複表頭不可遺失資料（100 消失），實際 {values}"
    assert 200 in values, f"重複表頭不可遺失資料（200 消失），實際 {values}"
    # 兩個分頁對同一批資料必須一致：去重後 金額=100、金額_2=200，合計仍為 300
    sums = {
        r[2]: r[3]
        for r in wb2["數值合計"].iter_rows(min_row=2, values_only=True)
        if r[2] in ("金額", "金額_2")
    }
    assert sums == {"金額": 100, "金額_2": 200}, f"數值合計應分列記錄 100 與 200，實際 {sums}"
    assert sum(sums.values()) == 300, "合計必須是 100+200=300"


def test_output_permission_error_returns_actionable_message(tmp_path, capsys):
    """輸出目錄無寫入權限時，應給可行動訊息與明確 exit code，不能裸 traceback。"""
    import os as _os

    outdir = tmp_path / "readonly"
    outdir.mkdir()
    _os.chmod(outdir, 0o555)
    try:
        rc = mx.main([str(NORMAL), "-o", str(outdir / "merged.xlsx"), "--apply"])
        captured = capsys.readouterr()
        assert rc == 3, f"輸出失敗應回 exit code 3，實際 {rc}"
        assert "Traceback" not in captured.err, f"不應出現裸 traceback：{captured.err}"
        assert "權限" in captured.err or "Permission" in captured.err, captured.err
    finally:
        _os.chmod(outdir, 0o755)


def test_fsync_uses_writable_handle(tmp_path, monkeypatch):
    """回歸測試（2026-10-24 evaluate 抓到，Windows hard fail）。

    Windows 的 os.fsync() → FlushFileBuffers() 需要 GENERIC_WRITE；
    用 "rb" 開的 handle 會回 EBADF (OSError [Errno 9] Bad file descriptor)。
    POSIX 允許對唯讀 fd 做 fsync → Linux CI 抓不到這個 bug。

    因此測試要斷言「flush 用的 handle 是可寫的」，不能只斷言最終檔案存在。
    """
    from openpyxl import Workbook

    opened_modes: list[str] = []
    real_open = open

    def tracking_open(file, mode="r", *args, **kwargs):
        if isinstance(file, (str, os.PathLike)) and str(file).endswith(".xlsx") and "r" in mode:
            opened_modes.append(mode)
        return real_open(file, mode, *args, **kwargs)

    target = tmp_path / "merged.xlsx"
    wb = Workbook()
    wb.active["A1"] = "v"
    monkeypatch.setattr("builtins.open", tracking_open)
    mx.atomic_save_workbook(wb, target, backup=False)

    assert opened_modes, "應該有開啟暫存檔做 flush"
    for mode in opened_modes:
        assert "+" in mode, (
            f"flush 必須用可寫 handle（'rb+'），實測用 {mode!r} → Windows 會 EBADF"
            "（FlushFileBuffers 需要 GENERIC_WRITE）"
        )


def test_cli_rejects_illegal_windows_output_name(tmp_path):
    rc = mx.main([str(NORMAL), "-o", "C:\\out\\bad?name.xlsx", "--apply"])
    assert rc == 2, "非法 Windows 檔名應被擋下"
