#!/usr/bin/env python3
"""雙向回歸驗證（code SOP §7.1）：證明 check_delivery.py 真的能抓出違規。

這支腳本做三件事：
  1. 造出「缺陷版」產出物（植入已知違規）
  2. 對缺陷版跑 check_delivery.py → 必須 exit != 0
  3. 對修好版跑 check_delivery.py → 必須 exit == 0

只有 [2] 與 [3] 都成立，檢查器才算有效。
（只跑 [3] 的檢查等於沒寫 —— 它可能只是永遠返回綠燈。）

用法：python3 verify_checkers.py
EXIT: 0 = 雙向驗證通過
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).parent
CHECKER = HERE / "check_delivery.py"
FIXED = HERE / "merge_xlsx.py"

REQUIRED_FILES = {
    "merge_xlsx.py": None,          # 缺陷版會換成帶違規旗標的版本
    "test_merge_xlsx.py": None,
    "README.md": "# 缺陷版測試\n",
    "RUNLOG.md": "# 缺陷版 RUNLOG\n",
}


def build_fixed(root: Path) -> Path:
    """修好版：所有檢查都應該通過。"""
    root.mkdir(parents=True, exist_ok=True)
    shutil.copy2(FIXED, root / "merge_xlsx.py")
    shutil.copy2(HERE / "test_merge_xlsx.py", root / "test_merge_xlsx.py")
    # check_delivery.py 也要複製過去：測試會 import 它
    # （manifest 完整性測試是「檢查器驗證檢查器」，缺了模組就測不成）。
    shutil.copy2(CHECKER, root / "check_delivery.py")
    (root / "README.md").write_text(
        "# 修好版\n\n這是雙向驗證用的修好版產出物。\n", encoding="utf-8"
    )
    (root / "RUNLOG.md").write_text(
        "# RUNLOG\n\n$ python3 check_delivery.py .\n[PASS] forbidden_flags\n\n"
        "已重跑驗證：2026-10-27 hermes\n",
        encoding="utf-8",
    )
    # 先產生一次 summary，讓數字檢查有來源
    subprocess.run(
        [sys.executable, str(CHECKER), str(root), "--write-summary"],
        capture_output=True, text=True, check=False,
    )
    return root


def build_defective(root: Path) -> Path:
    """缺陷版：植入五種違規，各對應一支檢查器。

      ① 關閉保護的旗標（--no-backup）
      ② RUNLOG 缺「已重跑驗證」stamp
      ③ RUNLOG 缺真實執行紀錄（沒有 $ 開頭的命令列）
      ④ 交付紀錄裡有摘要檔沒有的計數（手抄的數字）
      ⑤ manifest 列了不存在的檔案（模擬 2026-10-27 的真實缺陷：
         verification_summary.json 列了 33 個檔案但只交付 12 個）
    """
    root.mkdir(parents=True, exist_ok=True)
    src = FIXED.read_text(encoding="utf-8")
    # 缺陷版必須真的提供一個「關閉保護的旗標」→ 檢查器應該抓到它。
    # 用 argparse 的正式寫法，而不是只有文字。
    # 旗標名稱用拼接組出來，避免本檔自己被旗標掃描器判成違規
    # （檢查器不該因為「描述如何製造缺陷版」而自己紅燈 —— 那是假陽性）。
    banned_flag = "--" + "no-" + "backup"
    broken = src.replace(
        '    parser.add_argument(\n'
        '        "--apply", action="store_true",\n'
        '        help="真的寫出檔案（預設 dry-run：只預覽不寫）",\n'
        '    )',
        '    parser.add_argument(\n'
        f'        "{banned_flag}", action="store_true",\n'
        '        help="覆寫前不建立時間戳備份（關閉保護，違規）",\n'
        '    )\n'
        '    parser.add_argument(\n'
        '        "--apply", action="store_true",\n'
        '        help="真的寫出檔案（預設 dry-run：只預覽不寫）",\n'
        '    )',
    )
    assert broken != src, "缺陷版植入失敗：找不到 --apply 參數定義"
    (root / "merge_xlsx.py").write_text(broken, encoding="utf-8")
    shutil.copy2(HERE / "test_merge_xlsx.py", root / "test_merge_xlsx.py")
    (root / "README.md").write_text(
        "# 缺陷版測試\n\n本產出物含 5 項違規，用來證明檢查器有效。\n",
        encoding="utf-8",
    )
    # ② 缺 stamp ③ 缺 $ 執行紀錄 ④ 手抄計數 999 筆
    (root / "RUNLOG.md").write_text(
        "# RUNLOG\n\n實測共產生 999 筆紀錄。\n",
        encoding="utf-8",
    )
    # ⑤ manifest 列入不存在的檔案（真實缺陷的複製）
    (root / "verification_summary.json").write_text(
        json.dumps(
            {
                "root": str(root),
                "checks": [],
                "counters": {"checks_total": 0, "checks_passed": 0},
                "artifacts": {
                    "merge_xlsx.py": "0" * 64,
                    "merged.bak-20260101-000000": "1" * 64,
                },
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    return root

def run_checker(root: Path) -> tuple[int, str]:
    proc = subprocess.run(
        [sys.executable, str(CHECKER), str(root), "--json"],
        capture_output=True, text=True, check=False,
    )
    return proc.returncode, proc.stdout


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="verify_checkers_"))
    results = []
    all_ok = True

    # ---- [1] 缺陷版：必須被抓住 → exit != 0 ----
    defective = build_defective(tmp / "defective")
    rc, out = run_checker(defective)
    caught = rc != 0
    failed_names = []
    try:
        data = json.loads(out)
        failed_names = [c["name"] for c in data["checks"] if not c["passed"]]
    except (json.JSONDecodeError, KeyError):
        pass
    expected_caught = {
        "forbidden_flags",
        "runlog_rerun_stamp",
        "runlog_real_execution",
        "record_numbers_match_summary",
        "manifest_integrity",
    }
    missing = expected_caught - set(failed_names)
    ok = caught and not missing
    all_ok &= ok
    results.append({
        "case": "defective",
        "expected": "exit != 0 且至少抓到 " + ",".join(sorted(expected_caught)),
        "actual_exit": rc,
        "failed_checks": failed_names,
        "passed": ok,
    })

    # ---- [2] 修好版：必須全綠 → exit == 0 ----
    fixed = build_fixed(tmp / "fixed")
    rc2, out2 = run_checker(fixed)
    failed2 = []
    try:
        data2 = json.loads(out2)
        failed2 = [c["name"] for c in data2["checks"] if not c["passed"]]
    except (json.JSONDecodeError, KeyError):
        pass
    ok2 = rc2 == 0 and not failed2
    all_ok &= ok2
    results.append({
        "case": "fixed",
        "expected": "exit == 0 且 0 個檢查失敗",
        "actual_exit": rc2,
        "failed_checks": failed2,
        "passed": ok2,
    })

    print("=" * 70)
    print("雙向回歸驗證（code SOP §7.1）")
    print("=" * 70)
    for r in results:
        mark = "PASS" if r["passed"] else "FAIL"
        print(f"[{mark}] {r['case']}: {r['expected']}")
        print(f"       actual_exit={r['actual_exit']} failed_checks={r['failed_checks']}")
    print("-" * 70)
    if all_ok:
        print("雙向驗證通過：檢查器能抓住缺陷版，修好版全綠。")
    else:
        print("雙向驗證失敗：檢查器本身不可信，不可宣稱『已驗證』。")
    print(f"（缺陷版路徑：{tmp / 'defective'}；修好版路徑：{tmp / 'fixed'}）")
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
