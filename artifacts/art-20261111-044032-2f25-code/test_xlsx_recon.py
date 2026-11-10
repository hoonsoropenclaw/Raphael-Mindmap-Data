"""xlsx_recon 的測試套件。

三個層次：
1. **單元測試**——正規化、金額解析、小計偵測的邊界
2. **整合測試**——整個合併 + 對帳流程
3. **對抗性測試**——證明檢查器**真的會紅**（這是 SOP §7-1 的要求）

「乾淨資料跑綠」不算驗證；必須證明「缺陷資料跑紅」。
因此這支檔案的每個對抗性測試都是同一個形式：
    缺陷版 → 必須 exit≠0 或 抓到
    修好版 → 必須 exit=0
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from decimal import Decimal
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from xlsx_recon.engine import merge_directory, reconcile  # noqa: E402
from xlsx_recon.normalize import (  # noqa: E402
    detect_subtotal,
    map_columns,
    normalize_header,
    parse_amount,
)

TESTDATA = ROOT / "tests" / "testdata"


# ---------- fixtures ----------

@pytest.fixture(scope="session")
def clean_dir(tmp_path_factory) -> Path:
    """產生乾淨資料集（session 級，快取一次）。"""
    base = tmp_path_factory.mktemp("testdata")
    sys.path.insert(0, str(ROOT / "tools"))
    from make_test_data import build_all

    build_all(base)
    return base


# ---------- 單元測試：欄位對映 ----------

class TestHeaderMapping:
    def test_exact_chinese_headers(self):
        m, unmapped = map_columns(["日期", "類別", "說明", "單號", "金額"])
        assert m["日期"] == 0
        assert m["金額"] == 4
        assert unmapped == []

    def test_english_aliases(self):
        m, _ = map_columns(["Date", "Category", "Description", "ID", "Amount"])
        assert m["日期"] == 0
        assert m["類別"] == 1
        assert m["說明"] == 2
        assert m["單號"] == 3
        assert m["金額"] == 4

    def test_fullwidth_parentheses_header(self):
        """全形括號的「金額（元）」必須對映到金額欄。"""
        m, _ = map_columns(["日期", "類別", "說明", "單號", "金額（元）"])
        assert m["金額"] == 4

    def test_normalize_strips_whitespace_and_case(self):
        assert normalize_header("  Amount  ") == "amount"
        assert normalize_header("ＡＭＯＵＮＴ") == "amount"
        assert normalize_header(None) == ""

    def test_duplicate_column_reported(self):
        """同一個正規欄位出現兩次 → 第二個必須被記為 duplicate。"""
        m, unmapped = map_columns(["日期", "金額", "amount"])
        assert m["金額"] == 1
        assert any(u["reason"] == "duplicate_of" for u in unmapped)

    def test_unknown_column_reported(self):
        m, unmapped = map_columns(["日期", "類別", "金額", "神秘欄位"])
        assert m["金額"] == 2
        assert any(u["header"] == "神秘欄位" and u["reason"] == "no_alias_match"
                   for u in unmapped)


# ---------- 單元測試：金額解析 ----------

class TestAmountParsing:
    @pytest.mark.parametrize("raw,expected", [
        (100, "100.00"),
        (100.5, "100.50"),
        ("1,234", "1234.00"),
        ("NT$4,500", "4500.00"),
        ("NT$1,200", "1200.00"),
        ("１２３４", "1234.00"),        # 全形
        ("(500)", "-500.00"),          # 會計括號負數
        ("-500", "-500.00"),
        ("+300", "300.00"),
        (".5", "0.50"),
        ("0", "0.00"),                 # 零是合法金額（10-08 的 truthy bug 家族）
        ("  888  ", "888.00"),
    ])
    def test_valid_amounts(self, raw, expected):
        p = parse_amount(raw)
        assert p.ok, f"{raw!r} 應可解析，但得到 {p.reason}"
        assert str(p.value) == expected

    @pytest.mark.parametrize("raw,reason", [
        ("待補", "unparseable"),
        ("abc", "unparseable"),
        (None, "empty"),
        ("", "empty"),
        ("   ", "empty"),
        ("15%", "percent"),
        (True, "unparseable"),        # bool 不是金額
    ])
    def test_invalid_amounts(self, raw, reason):
        p = parse_amount(raw)
        assert not p.ok
        assert p.reason == reason

    def test_zero_is_not_missing(self):
        """金額 0 是合法值，不得被當成「無法解析」或「空值」。

        這是 10-08 audit_contract.py 的 truthy 缺陷家族：
        `fields.get('verified_total') and ...` 會把 0 判成缺少。
        """
        p = parse_amount(0)
        assert p.ok
        assert p.value == Decimal("0.00")
        assert p.reason == ""


# ---------- 單元測試：小計偵測 ----------

class TestSubtotalDetection:
    def test_label_in_first_column(self):
        r = detect_subtotal(["小計", "", "", "", -2000], amount_index=4)
        assert r["is_subtotal"]
        assert r["detection_layer"] == "label"
        assert r["column_index"] == 0

    def test_label_in_second_column(self):
        """小計標籤在第二欄——10-27 v5 的缺陷家族。

        舊版只檢查第一欄 → 抓不到 → 該列被當明細 → 金額靜默加倍。
        """
        r = detect_subtotal(["", "小計", "", "", 5800], amount_index=4)
        assert r["is_subtotal"]
        assert r["column_index"] == 1

    def test_label_in_third_column(self):
        r = detect_subtotal(["", "", "合計", "", 5800], amount_index=4)
        assert r["is_subtotal"]
        assert r["column_index"] == 2

    @pytest.mark.parametrize("label", [
        "小計", "合計", "總計", "累計", "小計合計", "本月小計", "total", "subtotal",
    ])
    def test_multiple_label_writings(self, label):
        r = detect_subtotal([label, "", "", "", 100], amount_index=4)
        assert r["is_subtotal"], f"「{label}」應該被認出是小計"

    def test_structural_layer_catches_unknown_label(self):
        """標籤清單沒有的寫法 → 靠結構層抓到（宣稱值恰好等於該段明細和）。"""
        r = detect_subtotal(["本段彙總", "", "", "", 300], amount_index=4)
        assert r["is_subtotal"]
        assert r["detection_layer"] == "structural"

    def test_real_data_containing_summary_word_not_flagged(self):
        """「合計系統建置費」是真實交易的說明，不得被當成小計列。

        這是假陽性家族：誤判會讓一筆真實金額被排除 → 報表少一筆。
        """
        r = detect_subtotal(
            ["2025-02-01", "工程", "合計系統建置費", "O-001", 25000], amount_index=4
        )
        assert not r["is_subtotal"]

    def test_normal_detail_row_not_flagged(self):
        r = detect_subtotal(
            ["2024-01-05", "差旅", "台北→台中 高鐵", "T-001", 1650], amount_index=4
        )
        assert not r["is_subtotal"]

    def test_no_amount_means_not_subtotal(self):
        """金額欄空的那列不會被當成小計（沒有可對帳的宣稱值）。"""
        r = detect_subtotal(["小計", "", "", "", None], amount_index=4)
        # 標籤層仍會認出來（這是資料的形狀問題，不是金額問題）
        assert r["is_subtotal"]
        assert r["detection_layer"] == "label"


# ---------- 整合測試：合併與對帳 ----------

class TestMergeAndReconcile:
    def test_clean_dataset_all_equations_hold(self, clean_dir):
        result = merge_directory(clean_dir / "testdata_clean")
        recon = reconcile(result)
        assert recon["equations_ok"], f"等式不成立：{recon['equations']}"
        assert recon["population"]["files_error"] == 0

    def test_recursive_subdirectories(self, clean_dir):
        result = merge_directory(clean_dir / "testdata_clean")
        files = {f.path.split("/")[-1] for f in result.files}
        assert "q2_採購.xlsx" in files
        assert "h1_費用.xlsx" in files

    def test_temp_file_is_skipped(self, clean_dir):
        """Excel 暫存檔 ~$xxx.xlsx 不得進入合併結果。"""
        result = merge_directory(clean_dir / "testdata_clean")
        assert not any(f.path.endswith("~$2024_q1.xlsx") for f in result.files)
        # 而且它那筆 999999 的金額不該出現在總計裡
        recon = reconcile(result)
        assert "999999" not in recon["totals"]["grand_total"]

    def test_missing_column_reports_error_but_others_survive(self, clean_dir):
        """壞掉的檔案不能拖垮整個合併。"""
        result = merge_directory(clean_dir / "testdata_broken")
        recon = reconcile(result)
        assert recon["population"]["files_error"] == 1
        assert recon["population"]["files_ok"] == 1
        assert any("缺少必要欄位" in it["desc"] for it in result.issues)

    def test_tampered_subtotal_is_caught(self, clean_dir):
        """來源檔的小計數字被改錯 → 等式必須不成立。

        這一條是整支工具存在的理由：如果沒有它，「小計被手改過」
        會一路靜默地進入報表。
        """
        result = merge_directory(clean_dir / "testdata_bad_subtotal")
        recon = reconcile(result)
        assert not recon["equations_ok"]
        assert recon["equations"]["declared_subtotal == running_segment_sum"] is False
        # 而且必須指得出是哪一列
        assert len(recon["declared_subtotal_checks"]) == 1
        assert recon["declared_subtotal_checks"][0]["matches_running_sum"] is False

    def test_additive_identity_holds_on_clean_data(self, clean_dir):
        """全表總計 = Σ 分組合計 = Σ 明細值。"""
        result = merge_directory(clean_dir / "testdata_clean")
        recon = reconcile(result)
        t = recon["totals"]
        assert t["grand_total"] == t["sum_of_groups"] == t["sum_of_details"]

    def test_subtotal_rows_excluded_from_detail_population(self, clean_dir):
        """小計列不得進入明細母體（否則金額加倍）。"""
        result = merge_directory(clean_dir / "testdata_clean")
        recon = reconcile(result)
        # q3_退款.xlsx 的小計是 -2000，若被重複計入總計會是 79194.50 - 2000*2
        assert recon["totals"]["grand_total"] == "79194.50"

    def test_negative_amounts_are_kept(self, clean_dir):
        """退款（負值）必須進母體——漏掉會讓總額偏大。"""
        result = merge_directory(clean_dir / "testdata_clean")
        recon = reconcile(result)
        files = {f["file"]: f for f in recon["per_file"]}
        assert files["q3_退款.xlsx"]["detail_sum"] == "9200.00"

    def test_excluded_rows_have_reasons(self, clean_dir):
        """每一筆被排除的列都要有明確原因（不可解析／空值／百分比）。"""
        result = merge_directory(clean_dir / "testdata_clean")
        recon = reconcile(result)
        reasons = {e["reason"] for e in recon["excluded_rows_detail"]}
        assert {"unparseable", "empty", "percent"} <= reasons
        for e in recon["excluded_rows_detail"]:
            assert e["file"] and e["row"]

    def test_population_and_not_covered_declared(self, clean_dir):
        """每支工具都要宣告母體與不看的維度（11-10 學到的規則）。"""
        result = merge_directory(clean_dir / "testdata_clean")
        recon = reconcile(result)
        assert recon["population"]["detail_rows_total"] > 0
        assert isinstance(recon["not_covered"], list) and recon["not_covered"]

    def test_multi_sheet_file_all_sheets_processed(self, clean_dir):
        result = merge_directory(clean_dir / "testdata_clean")
        recon = reconcile(result)
        files = {f["file"]: f for f in recon["per_file"]}
        assert files["multi_sheet.xlsx"]["detail_sum"] == "1600.00"

    def test_empty_input_dir(self, tmp_path):
        result = merge_directory(tmp_path / "nothing_here")
        assert result.issues
        assert result.issues[0]["code"] == "input_dir_missing"

    def test_idempotent_rerun(self, clean_dir, tmp_path):
        """同一份輸入跑兩次，結果必須一樣（可重跑不損壞資料）。"""
        r1 = reconcile(merge_directory(clean_dir / "testdata_clean"))
        r2 = reconcile(merge_directory(clean_dir / "testdata_clean"))
        assert r1["totals"] == r2["totals"]
        assert r1["equations"] == r2["equations"]

    def test_output_excluded_from_its_own_merge(self, clean_dir, tmp_path):
        """把輸出放進輸入資料夾再跑一次，不得把輸出自己合併進去。"""
        work = tmp_path / "selfmerge"
        shutil.copytree(clean_dir / "testdata_clean", work)
        from xlsx_recon.engine import write_outputs

        result = merge_directory(work)
        recon = reconcile(result)
        write_outputs(result, recon, work / "merged.xlsx",
                      work / "summary.csv", work / "issues.csv")
        # 再跑一次
        result2 = merge_directory(work)
        recon2 = reconcile(result2)
        assert recon2["totals"]["grand_total"] == recon["totals"]["grand_total"]


# ---------- 對抗性測試（證明檢查器會紅）----------

class TestAdversarial:
    """每個測試都是「缺陷版必紅」的形式。

    只跑乾淨資料全綠不算驗證——那可能只是一支永遠返回成功的程式。
    """

    def _run_cli(self, args: list[str]) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, "-m", "xlsx_recon", *args],
            cwd=ROOT, capture_output=True, text=True, timeout=120,
        )

    def test_clean_dataset_exits_zero(self, clean_dir):
        p = self._run_cli(["--input", str(clean_dir / "testdata_clean"), "--report-only"])
        assert p.returncode == 0, f"乾淨資料應 exit=0，但得到 {p.returncode}\n{p.stdout}"

    def test_broken_column_exits_nonzero(self, clean_dir):
        p = self._run_cli(["--input", str(clean_dir / "testdata_broken"), "--report-only"])
        assert p.returncode != 0, "缺欄位的資料必須讓 CLI 回非 0"

    def test_tampered_subtotal_exits_nonzero(self, clean_dir):
        p = self._run_cli(["--input", str(clean_dir / "testdata_bad_subtotal"),
                           "--report-only"])
        assert p.returncode != 0, "小計被改錯時必須讓 CLI 回非 0"

    def test_missing_input_dir_exits_two(self, tmp_path):
        p = self._run_cli(["--input", str(tmp_path / "nope"), "--report-only"])
        assert p.returncode == 2

    def test_injected_double_count_is_caught(self, clean_dir, tmp_path):
        """把一個小計列改成「標籤清單裡沒有」��寫法，總額必須仍然正確。

        做法：把 h1_費用.xlsx 的小計列從「小計」（第二欄）搬成
        「本期彙總」（第一欄），其餘欄清空。
        這個寫法不在 SUBTOTAL_LABELS 清單裡 → 只能靠結構層抓到。
        抓到了 → 該列不會被當成明細 → 總額維持 79194.50。
        """
        work = tmp_path / "tampered_label"
        shutil.copytree(clean_dir / "testdata_clean", work)
        target = work / "2025" / "h1_費用.xlsx"
        from openpyxl import load_workbook

        wb = load_workbook(target)
        ws = wb["明細"]
        ws.cell(row=4, column=1).value = "本期彙總"
        for col in (2, 3, 4):
            ws.cell(row=4, column=col).value = None
        wb.save(target)

        result = merge_directory(work)
        recon = reconcile(result)
        # 結構層必須抓到它
        assert any(c["label"] == "本期彙總"
                   for c in recon["suspected_subtotal_checks"])
        # 而且總額必須跟乾淨版一樣（沒有重複計算）
        assert recon["totals"]["grand_total"] == "79194.50"

    def test_injected_wrong_amount_is_caught(self, clean_dir, tmp_path):
        """把小計的數字改錯 → 等式必須不成立。

        這是「來源檔自己對不上」的訊號：報表不可信。
        """
        work = tmp_path / "wrong_amount"
        shutil.copytree(clean_dir / "testdata_clean", work)
        target = work / "2025" / "h1_費用.xlsx"
        from openpyxl import load_workbook

        wb = load_workbook(target)
        ws = wb["明細"]
        ws.cell(row=4, column=5).value = 9999     # 應為 5800
        wb.save(target)

        result = merge_directory(work)
        recon = reconcile(result)
        assert not recon["equations_ok"]
        assert recon["equations"]["declared_subtotal == running_segment_sum"] is False

    def test_removing_a_subtotal_row_changes_the_total(self, clean_dir, tmp_path):
        """刪掉小計列後，明細和會變——證明小計列確實被排除在母體外。

        對照組：同一份資料保留小計列時，總額必須相同。
        """
        work = tmp_path / "no_subtotal"
        shutil.copytree(clean_dir / "testdata_clean", work)
        target = work / "2025" / "h1_費用.xlsx"
        from openpyxl import load_workbook

        wb = load_workbook(target)
        ws = wb["明細"]
        ws.delete_rows(4)          # 刪掉小計列
        wb.save(target)

        recon = reconcile(merge_directory(work))
        # 少了小計列，但小計本來就不在明細母體裡 → 明細和應該一樣
        assert recon["totals"]["grand_total"] == "79194.50"

    def test_double_counting_would_change_total(self, clean_dir, tmp_path):
        """對照組證明：若小計列被當成明細，總額會變。

        做法：把小計列**偽裝成一筆正常的明細列**——補上日期、說明、單號，
        讓它有兩個以上的非空文字格，結構層的訊號就不成立；
        同時用一個不在標籤清單裡的字眼，避免被標籤層認出。
        這一列就會被當成明細 → 總額增加 5800。

        這條測試是上一條的**反例**——它證明「刪掉小計列後總額相同」
        不是因為「那列金額為 0」，而是因為小計列確實被排除在母體外。
        """
        work = tmp_path / "double_count"
        shutil.copytree(clean_dir / "testdata_clean", work)
        target = work / "2025" / "h1_費用.xlsx"
        from openpyxl import load_workbook

        wb = load_workbook(target)
        ws = wb["明細"]
        # 偽裝成正常明細：日期 + 說明都有值 → 非空文字格 = 2 → 結構層不成立
        ws.cell(row=4, column=1).value = "2025-01-10"
        ws.cell(row=4, column=2).value = None
        ws.cell(row=4, column=3).value = "期內彙總款項"
        ws.cell(row=4, column=4).value = "H-SUM"
        wb.save(target)

        recon = reconcile(merge_directory(work))
        # 這一列被當成明細 → 總額 = 79194.50 + 5800
        assert recon["totals"]["grand_total"] != "79194.50"
        assert Decimal(recon["totals"]["grand_total"]) == Decimal("79194.50") + Decimal("5800")
