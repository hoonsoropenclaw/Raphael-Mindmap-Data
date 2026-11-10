"""xlsx_recon — 資料夾內多個 Excel 的合併與對帳工具。

用途
----
把一個資料夾（含子資料夾）內的多個 Excel 活頁簿合併成一張明細表，
並用**加總等式**驗證合併結果沒有重複計算或漏算：

    全表總計 = Σ 分組合計 = Σ 明細值

為什麼需要這個等式
------------------
合併報表最常見也最難察覺的錯誤是「小計列被當成明細列一起加總」，
結果報表上的數字是正確值的兩倍。這種錯誤不會讓程式出錯、
不會讓檔案打不開，只是數字 quietly 錯了——**沒有等式就沒有任何東西能發現它**。

使用方式
--------
    # 預覽（不寫任何檔案）
    python -m xlsx_recon --input ./資料夾 --dry-run

    # 真的合併並寫出輸出
    python -m xlsx_recon --input ./資料夾 --out-dir ./輸出

    # 只看對帳結果，不寫檔
    python -m xlsx_recon --input ./資料夾 --report-only

結束碼
------
    0 = 全部等式成立
    1 = 有等式不成立或來源檔錯誤（詳見 issues CSV 與畫面輸出）
    2 = 找不到任何可處理的 Excel 檔

環境需求
--------
Python 3.10+ 與 openpyxl。Python 3.12 已實測通過。
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .engine import merge_directory, reconcile, write_outputs

__all__ = ["main", "build_parser"]

__version__ = "1.0.0"


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="xlsx_recon",
        description="合併資料夾內多個 Excel 並用加總等式驗證結果",
    )
    p.add_argument("--input", required=True, type=Path, help="輸入資料夾（會遞迴子資料夾）")
    p.add_argument("--out-dir", type=Path, default=None,
                   help="輸出目錄（預設：輸入資料夾）。指定時會寫出 merged.xlsx / summary.csv / issues.csv")
    p.add_argument("--dry-run", action="store_true",
                   help="只預覽不合併，不寫任何檔案（預設行為除非指定 --out-dir）")
    p.add_argument("--report-only", action="store_true",
                   help="只輸出對帳報告到 stdout，不寫檔案")
    p.add_argument("--json", action="store_true",
                   help="以 JSON 輸出對帳報告到 stdout（給其他程式接）")
    p.add_argument("--no-recursive", action="store_true", help="不遞迴子資料夾")
    p.add_argument("--version", action="version", version=f"xlsx_recon {__version__}")
    return p


def _print_human(recon: dict, files) -> None:
    pop = recon["population"]
    tot = recon["totals"]
    print("=" * 68)
    print("xlsx_recon 對帳報告")
    print("=" * 68)
    print(f"掃描檔案數        : {pop['files_scanned']}"
          f"（成功 {pop['files_ok']}／錯誤 {pop['files_error']}／略過 {pop['files_skipped']}）")
    print(f"明細列數          : {pop['detail_rows_total']}"
          f"（有金額 {pop['detail_rows_with_amount']}／排除 {pop['detail_rows_excluded']}）")
    print(f"小計列（已排除）  : {pop['subtotal_rows_detected']}")
    print(f"分組數            : {pop['groups']}")
    print("-" * 68)
    print(f"全表總計          : {tot['grand_total']}")
    print(f"Σ 分組合計        : {tot['sum_of_groups']}")
    print(f"Σ 明細值          : {tot['sum_of_details']}")
    print(f"（小計列已排除之和: {tot['subtotal_rows_excluded_sum']}）")
    print("-" * 68)
    print("加總等式：")
    for name, ok in recon["equations"].items():
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
    # --- 母體完整性（與等式是兩個獨立結論）---
    #
    # 為什麼要分開印：equations_ok=True 只代表「等式成立」，
    # population_not_hollowed=True 才代表「等式有意義」。
    # 如果只印等式，使用者會把「等式成立」當成「資料可信」——
    # 那正是 11-11 學到的失效形狀（等式在一個被掏空的母體上平凡成立）。
    print("-" * 68)
    print("母體完整性：")
    hollow = not recon.get("population_not_hollowed", True)
    print(f"  [{'FAIL' if hollow else 'PASS'}] population_not_hollowed"
          f"（排除比例上限 {recon['population'].get('excluded_ratio_limit')}）")
    print(f"        全體排除比例：{recon['population'].get('excluded_ratio_overall')}")
    for pe in recon.get("per_file_exclusion", []):
        if not pe.get("evaluable", True):
            flag = "n/a "
            note = f"（明細列 {pe['detail_rows']} < 分母下限，不判）"
        elif pe["over_limit"]:
            flag = "FAIL"
            note = "（超過上限）"
        else:
            flag = "ok  "
            note = ""
        print(f"  [{flag}] {pe['file']}：排除 {pe['excluded_rows']}/{pe['detail_rows']}"
              f" = {pe['excluded_ratio']}{note}")
    print("-" * 68)
    print("母體宣告（本工具**看**這些）：")
    print(f"  population: 掃描檔案 {pop['files_scanned']}、"
          f"明細列 {pop['detail_rows_total']}、小計列 {pop['subtotal_rows_detected']}、"
          f"分組 {pop['groups']}")
    print("本工具**不看**這些（not_covered）：")
    for item in recon["not_covered"]:
        print(f"  - {item}")
    if recon["excluded_rows_detail"]:
        print("-" * 68)
        print("被排除的列（不進加總母體）：")
        for ex in recon["excluded_rows_detail"][:20]:
            print(f"  {ex['file']} / {ex['sheet']} / 第 {ex['row']} 列"
                  f"  原因={ex['reason']}  原始值={ex['raw']!r}")
        if len(recon["excluded_rows_detail"]) > 20:
            print(f"  ...（另有 {len(recon['excluded_rows_detail']) - 20} 筆，詳見 issues.csv）")
    if recon["suspected_subtotal_checks"]:
        print("-" * 68)
        print("疑似小計列（結構層偵測，已獨立驗證）：")
        for c in recon["suspected_subtotal_checks"]:
            mark = "OK" if c["matches_running_sum"] else "MISMATCH"
            print(f"  [{mark}] {c['file']} / {c['sheet']} / 第 {c['row']} 列"
                  f"  標籤={c['label']!r}  宣稱={c['claimed_amount']}"
                  f"  該段明細和={c['running_detail_sum']}  → {c['verdict']}")
    if recon["declared_subtotal_checks"]:
        print("-" * 68)
        print("已宣告小計列（逐列核對所涵蓋的區段）：")
        for c in recon["declared_subtotal_checks"]:
            mark = "OK" if c["matches_running_sum"] else "MISMATCH"
            print(f"  [{mark}] {c['file']} / {c['sheet']} / 第 {c['row']} 列"
                  f"  標籤={c['label']!r}  宣稱={c['claimed_amount']}"
                  f"  該段明細和={c['running_detail_sum']}")
    print("=" * 68)


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    input_dir: Path = args.input
    if not input_dir.exists():
        print(f"錯誤：輸入資料夾不存在：{input_dir}", file=sys.stderr)
        return 2
    if not input_dir.is_dir():
        print(f"錯誤：輸入路徑不是資料夾：{input_dir}", file=sys.stderr)
        return 2

    result = merge_directory(
        input_dir,
        recursive=not args.no_recursive,
        exclude_output=True,
    )
    recon = reconcile(result)

    if args.json:
        print(json.dumps({"recon": recon,
                          "files": [
                              {"path": f.path, "status": f.status, "reason": f.reason,
                               "detail_rows": f.detail_rows, "subtotal_rows": f.subtotal_rows,
                               "unparseable_rows": f.unparseable_rows,
                               "empty_amount_rows": f.empty_amount_rows,
                               "percent_amount_rows": f.percent_amount_rows,
                               "unmapped_columns": f.unmapped_columns,
                               "missing_required_columns": f.missing_required_columns}
                              for f in result.files],
                          "issues": result.issues},
                         ensure_ascii=False, indent=2))
    else:
        _print_human(recon, result.files)
        if result.issues:
            print("-" * 68)
            print("問題清單：")
            for it in result.issues:
                loc = it.get("file", "")
                if it.get("sheet"):
                    loc += f" / {it['sheet']}"
                print(f"  [{it.get('severity', '')}] {it.get('code', '')} {loc}: {it.get('desc', '')}")

    if recon["population"]["files_scanned"] == 0:
        print("錯誤：沒有找到任何 Excel 檔。", file=sys.stderr)
        return 2

    write_requested = bool(args.out_dir) and not args.dry_run and not args.report_only
    if write_requested:
        out_dir: Path = args.out_dir
        write_outputs(
            result, recon,
            out_dir / "merged.xlsx",
            out_dir / "summary.csv",
            out_dir / "issues.csv",
        )
        print(f"已寫出輸出到：{out_dir}")
        print("  merged.xlsx      合併後的明細表")
        print("  summary.csv      分組合計 + 全表總計")
        print("  issues.csv       問題與被排除的列")
        print("  merge_summary.json 機器回算的對帳結果（其他文件一律引用這份）")

    if not recon["equations_ok"]:
        print("錯誤：加總等式不成立，結果不可信。詳見上方等式檢查。", file=sys.stderr)
        return 1
    if not recon.get("population_not_hollowed", True):
        hollow = recon["population"].get("hollow_files", [])
        print(
            "錯誤：母體被掏空——等式雖然成立，但它在一個幾乎空的母體上成立，"
            f"結果不可信。被掏空的來源檔：{hollow}", file=sys.stderr)
        return 1
    if result.issues:
        print("警告：有來源檔處理失敗，詳見問題清單。", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
