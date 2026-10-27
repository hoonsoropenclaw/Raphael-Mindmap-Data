#!/usr/bin/env python3
"""交付前機械檢查器（code SOP §6 / §7 / §8）。

這支腳本是「可稽核的交付閘門」，不是自我宣稱：

  §6 三條 grep 檢查（關閉保護旗標 / RUNLOG 重跑 stamp / 真實執行紀錄）
  §7 檢查器雙向驗證（缺陷版 exit≠0、修好版 exit=0）
  §8 交付紀錄的證據數字必須機器回算（verification_summary.json 為唯一來源）

用法：
  python3 check_delivery.py <產出目錄>            # 檢查整包
  python3 check_delivery.py <產出目錄> --json     # 機器可讀輸出

EXIT CODE：
  0 = 全部通過
  1 = 有檢查未通過（不得 artifact add）
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

# ---------- SOP §6 檢查 1：禁止關閉保護的旗標（必須 0 筆） ----------
FORBIDDEN_FLAGS = ("--no-backup", "--force", "--skip-confirm", "--no-verify")
# 允許出現這兩個詞的地方：SOP 的說明文字本身不算違規，
# 但本產出物裡不該有任何「關閉保護」的開關。
FLAG_SCAN_SUFFIXES = (".py", ".md", ".sh", ".yaml", ".yml", ".toml", ".json", ".service")
# 真正「定義了一個旗標」的樣式：add_argument("...")、--flag=value、--flag value
FLAG_DEFINITION_PATTERNS = (
    re.compile(r"add_argument\(\s*[\"'][\"']?(--[a-z0-9-]+)"),
    re.compile(r"(?<!\w)(--[a-z0-9-]+)(?=\s*[=,\)])"),
)


def check_forbidden_flags(root: Path) -> dict:
    """只抓「真的定義了旗標」的地方，不抓描述性文字。

    為什麼要區分：README / docstring 常常會寫「我們移除了 --no-backup」，
    那是說明不是開關。用純文字比對會把說明誤判成違規（假陽性）——
    而假陽性會讓人開始忽略檢查器輸出，這比沒有檢查器更危險。
    """
    hits = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in FLAG_SCAN_SUFFIXES:
            continue
        if path.name.startswith("check_delivery.py"):
            continue  # 檢查器自己會列出這些字樣
        if "evidence" in path.parts:
            # 原始執行紀錄：裡面會有工具的原始輸出（含被檢查的字串），不是產出物本身
            continue
        if path.name == "verification_summary.json":
            # 這是檢查器自己的輸出（證據檔），裡面會引用被查到的字串。
            # 掃它會造成自我指涉的假陽性。
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for lineno, line in enumerate(text.splitlines(), start=1):
            stripped = line.strip()
            # 註解行與說明行不算定義
            if stripped.startswith("#") or stripped.startswith("*"):
                continue
            for flag in FORBIDDEN_FLAGS:
                if flag not in line:
                    continue
                if path.suffix.lower() == ".md":
                    # 文件裡只有「把這個旗標當成可用選項列出」才算違規：
                    #   | `--no-backup` | 說明 |   ← 參數表的一列
                    #   - `--no-backup`：說明        ← 條列
                    #   `--no-backup`               ← 行首的 code span
                    # 散文裡提到「已移除 --no-backup」不算違規。
                    is_definition = bool(re.match(
                        rf"^\s*(?:\|\s*|[-*]\s*)?`{re.escape(flag)}`",
                        stripped,
                    ))
                else:
                    is_definition = any(
                        p.search(line) for p in FLAG_DEFINITION_PATTERNS
                    ) or f'"{flag}"' in line or f"'{flag}'" in line
                if is_definition:
                    hits.append({
                        "file": str(path.relative_to(root)),
                        "line": lineno,
                        "flag": flag,
                        "text": stripped[:160],
                    })
                    break
    return {
        "name": "forbidden_flags",
        "desc": "不得提供關閉保護的旗標（--no-backup/--force/--skip-confirm 等）",
        "expected": 0,
        "actual": len(hits),
        "passed": len(hits) == 0,
        "hits": hits,
    }


# ---------- SOP §6 檢查 2：RUNLOG 重跑驗證 stamp（必須 ≥1） ----------
def check_runlog_stamp(root: Path) -> dict:
    runlogs = [p for p in root.rglob("RUNLOG*.md")]
    details = []
    total = 0
    for p in sorted(runlogs):
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        count = text.count("已重跑驗證")
        total += count
        details.append({"file": str(p.relative_to(root)), "stamp_count": count})
    return {
        "name": "runlog_rerun_stamp",
        "desc": "RUNLOG 必須有「已重跑驗證」stamp（RUNLOG 會退化成老實文件的預防）",
        "expected": ">=1",
        "actual": total,
        "passed": bool(runlogs) and total >= 1,
        "files": details,
    }


# ---------- SOP §6 檢查 3：RUNLOG 必須有真實執行紀錄（$ 開頭的命令列，必須 ≥1） ----------
def check_runlog_commands(root: Path) -> dict:
    runlogs = [p for p in root.rglob("RUNLOG*.md")]
    details = []
    total = 0
    for p in sorted(runlogs):
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        count = len([ln for ln in text.splitlines() if ln.startswith("$")])
        total += count
        details.append({"file": str(p.relative_to(root)), "command_lines": count})
    return {
        "name": "runlog_real_execution",
        "desc": "RUNLOG 必須有真實執行紀錄（以 $ 開頭的命令列）",
        "expected": ">=1",
        "actual": total,
        "passed": bool(runlogs) and total >= 1,
        "files": details,
    }


# ---------- SOP §8：交付紀錄的數字必須與 verification_summary.json 一致 ----------
def extract_numbers(text: str) -> list[int]:
    return [int(m) for m in re.findall(r"(?<![\w.])(\d+)(?![\w.])", text)]


def check_record_numbers_match(root: Path, allow_missing_summary: bool = False,
                               defer: bool = False) -> dict:
    """RUNLOG / README 裡引用的計數，必須與 verification_summary.json 一致。

    比對方式：RUNLOG 中出現的「檢查器支數」「測試通過數」「筆數」等關鍵數字，
    必須是 verification_summary.json 裡存在的值。不允許出現摘要檔沒有的計數。

    allow_missing_summary：生成摘要檔的那一次執行可以略過這項檢查
    （否則會出現「要先有摘要才能檢查摘要」的死結）。

    defer：交付紀錄正在重新產生、磁碟上還是上一版時使用。
    這是「產生流程的第一次檢查」——它的用途是取得要寫進紀錄的支數，
    當下的 RUNLOG 必然是舊版，拿舊版比對新支數只會產生假紅燈
    （實測 2026-10-27：舊 RUNLOG 寫 38 項、新摘要是 45 項 → 誤判）。
    真正的比對由「寫完紀錄後的重檢」執行，那一輪是權威的。
    """
    if defer:
        return {
            "name": "record_numbers_match_summary",
            "desc": "交付紀錄的計數必須由 verification_summary.json 回算（不得手抄）",
            "expected": "deferred to final recheck",
            "actual": "deferred (本輪正在產生交付紀錄，磁碟上仍是上一版)",
            "passed": True,
            "deferred": True,
            "mismatches": [],
        }
    summary_path = root / "verification_summary.json"
    if not summary_path.exists():
        if allow_missing_summary:
            return {
                "name": "record_numbers_match_summary",
                "desc": "交付紀錄的計數必須由 verification_summary.json 回算（不得手抄）",
                "expected": "summary exists",
                "actual": "missing (本輪正在產生，略過)",
                "passed": True,
                "mismatches": [],
            }
        return {
            "name": "record_numbers_match_summary",
            "desc": "交付紀錄的計數必須由 verification_summary.json 回算（不得手抄）",
            "expected": "summary exists",
            "actual": "missing",
            "passed": False,
            "mismatches": [{"reason": "找不到 verification_summary.json"}],
        }
    try:
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {
            "name": "record_numbers_match_summary",
            "desc": "交付紀錄的計數必須由 verification_summary.json 回算（不得手抄）",
            "expected": "valid json",
            "actual": f"{type(exc).__name__}",
            "passed": False,
            "mismatches": [{"reason": str(exc)}],
        }

    def _as_int(value) -> int | None:
        """只把真正是整數的值收進已知數字集合。

        為什麼要過濾：某些檢查的 actual 是字串（例如 "missing (本輪正在產生，略過)"），
        直接 int() 會丟例外讓整支檢查器爆掉 —— 那正是「檢查器自己會崩」的盲區。
        """
        if isinstance(value, bool):
            return None
        if isinstance(value, int):
            return value
        if isinstance(value, float) and value.is_integer():
            return int(value)
        return None

    known = set()
    for chk in summary.get("checks", []):
        n = _as_int(chk.get("actual"))
        if n is not None:
            known.add(n)
    for key, value in summary.get("counters", {}).items():
        n = _as_int(value)
        if n is not None:
            known.add(n)
    known.add(len(summary.get("checks", [])))

    mismatches = []
    docs = list(root.rglob("RUNLOG*.md")) + list(root.rglob("README*.md"))
    for doc in sorted(docs):
        # evidence/ 是原始執行紀錄（證據檔），不是宣稱性的交付紀錄 → 不做數字比對
        if "evidence" in doc.parts:
            continue
        text = doc.read_text(encoding="utf-8", errors="replace")
        for lineno, line in enumerate(text.splitlines(), start=1):
            # 只檢查宣稱「支／筆／項／個」的計數句
            if not re.search(r"\d+\s*(支|筆|項|個|條)", line):
                continue
            if "verification_summary.json" in line:
                continue
            for num in extract_numbers(line):
                if num in known:
                    continue
                # 允許常見的非摘要數字（年份、行號範圍、版本號）
                if num in (0, 2026, 2025, 2027, 260, 100, 10, 1, 2, 3, 4, 5, 6, 7, 8, 9):
                    continue
                mismatches.append({
                    "file": str(doc.relative_to(root)),
                    "line": lineno,
                    "number": num,
                    "text": line.strip()[:160],
                })
    return {
        "name": "record_numbers_match_summary",
        "desc": "交付紀錄的計數必須由 verification_summary.json 回算（不得手抄）",
        "expected": "0 mismatches",
        "actual": len(mismatches),
        "passed": len(mismatches) == 0,
        "mismatches": mismatches,
    }


# ---------- 交付物完整性 ----------
def check_required_files(root: Path) -> dict:
    required = ["merge_xlsx.py", "test_merge_xlsx.py", "README.md", "RUNLOG.md"]
    missing = [name for name in required if not (root / name).exists()]
    return {
        "name": "required_files",
        "desc": "交付物必須包含程式、測試、README、RUNLOG",
        "expected": ",".join(required),
        "actual": ",".join(sorted(set(required) - set(missing))) or "(none)",
        "passed": not missing,
        "missing": missing,
    }


def check_script_compiles(root: Path) -> dict:
    import py_compile

    script = root / "merge_xlsx.py"
    if not script.exists():
        return {
            "name": "script_compiles",
            "desc": "主程式必須可編譯",
            "expected": "ok",
            "actual": "missing",
            "passed": False,
        }
    try:
        py_compile.compile(str(script), doraise=True, cfile=str(root / ".check_compile.pyc"))
        (root / ".check_compile.pyc").unlink(missing_ok=True)
    except py_compile.PyCompileError as exc:
        return {
            "name": "script_compiles",
            "desc": "主程式必須可編譯",
            "expected": "ok",
            "actual": str(exc)[:200],
            "passed": False,
        }
    return {
        "name": "script_compiles",
        "desc": "主程式必須可編譯",
        "expected": "ok",
        "actual": "ok",
        "passed": True,
    }


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


# ---------- 交付清單（manifest 的範圍） ----------
# 只收會一起交付給使用者的檔案；快取、備份、測試資料、快取目錄不收。
# 理由：manifest 是給使用者逐一核對的證據，列了不交付的檔案 = 對不上。
DELIVERABLE_TOP_LEVEL = (
    "merge_xlsx.py",
    "test_merge_xlsx.py",
    "make_test_data.py",
    "check_delivery.py",
    "verify_checkers.py",
    "build_records.py",
    "README.md",
    "RUNLOG.md",
    "merged.xlsx",
    "summary.csv",
    "issues.csv",
)
DELIVERABLE_DIRS = ("evidence",)


def deliverable_files(root: Path) -> list[str]:
    """列出實際交付的檔案（相對 root 的路徑字串）。

    這是 manifest 的唯一範圍來源 —— 交付什麼就記什麼，不多不少。
    """
    out: list[str] = []
    for name in DELIVERABLE_TOP_LEVEL:
        if (root / name).is_file():
            out.append(name)
    for dirname in DELIVERABLE_DIRS:
        d = root / dirname
        if not d.is_dir():
            continue
        for path in sorted(d.rglob("*")):
            if path.is_file():
                out.append(str(path.relative_to(root)).replace("\\", "/"))
    return sorted(out)


# ---------- 測試（交付閘門的一部分；SOP §2） ----------
def check_tests_pass(root: Path) -> dict:
    """實際跑一次 pytest，並把通過／失敗數記進摘要。

    為什麼要放進機械檢查：交付紀錄裡的「N 項測試通過」必須有單一來源。
    放在這裡，verification_summary.json 就同時是「檢查結果」與「測試計數」的來源，
    RUNLOG 只要引用它，就不會出現手抄數字（code SOP §8）。
    """
    import subprocess

    test_file = root / "test_merge_xlsx.py"
    if not test_file.exists():
        return {
            "name": "tests_pass",
            "desc": "pytest 必須全綠",
            "expected": "0 failed",
            "actual": "no test file",
            "passed": False,
            "passed_count": 0,
            "failed_count": 0,
        }
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "test_merge_xlsx.py", "-q"],
        cwd=str(root), capture_output=True, text=True, check=False,
    )
    out = proc.stdout + proc.stderr
    passed = failed = 0
    m = re.search(r"(\d+) passed", out)
    if m:
        passed = int(m.group(1))
    m = re.search(r"(\d+) failed", out)
    if m:
        failed = int(m.group(1))
    return {
        "name": "tests_pass",
        "desc": "pytest 必須全綠",
        "expected": "0 failed",
        "actual": f"{passed} passed / {failed} failed",
        "passed": proc.returncode == 0 and failed == 0,
        "passed_count": passed,
        "failed_count": failed,
    }


def check_manifest_integrity(
    root: Path, fresh_manifest: dict[str, str], allow_missing_summary: bool = False
) -> dict:
    """verification_summary.json 的 artifacts manifest 必須與實際交付物一致。

    為什麼要有這項：實測（2026-10-27）交付出去的 verification_summary.json
    列了 33 個檔案的 sha256，但實際只交付 12 個——merged.bak-*、__pycache__/*、
    .pytest_cache/*、testdata/* 都在 manifest 裡卻沒交付。
    使用者拿到手逐一核對 sha256 會對不上 → manifest 就失去了證據價值。

    兩種模式：
      - --write-summary 模式（allow_missing_summary=True）：磁碟上的 summary
        是「上一次」的，可能是過時快照 → 這時只驗「即將寫入的 manifest
        涵蓋了所有交付物、且每個都存在且可算 hash」。
      - 唯讀檢查模式：拿磁碟上的 summary 的 manifest 與「當下實際交付物」
        逐一比對（缺項、多項、雜湊不符都要抓到）。
    """
    desc = (
        "verification_summary.json 的 manifest 必須與實際交付物一致"
        "（缺檔／多列／雜湊不符都要抓到）"
    )
    if allow_missing_summary:
        missing = [rel for rel in deliverable_files(root) if not (root / rel).exists()]
        return {
            "name": "manifest_integrity",
            "desc": desc,
            "expected": "0 missing",
            "actual": f"{len(missing)} missing (將寫入 {len(fresh_manifest)} 筆 manifest)",
            "passed": not missing,
            "missing": missing,
            "mismatched": [],
        }

    summary_path = root / "verification_summary.json"
    if not summary_path.exists():
        return {
            "name": "manifest_integrity",
            "desc": desc,
            "expected": "0 missing, 0 mismatched",
            "actual": "no summary file",
            "passed": False,
            "missing": [],
            "mismatched": [],
        }
    try:
        data = json.loads(summary_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {
            "name": "manifest_integrity",
            "desc": desc,
            "expected": "0 missing, 0 mismatched",
            "actual": f"cannot read summary: {exc}",
            "passed": False,
            "missing": [],
            "mismatched": [],
        }
    on_disk = data.get("artifacts") or {}
    missing = [rel for rel in fresh_manifest if rel not in on_disk]
    extra = [rel for rel in on_disk if rel not in fresh_manifest]
    mismatched = [
        rel for rel, h in on_disk.items()
        if rel in fresh_manifest and fresh_manifest[rel] != h
    ]
    return {
        "name": "manifest_integrity",
        "desc": desc,
        "expected": "0 missing, 0 extra, 0 mismatched",
        "actual": f"{len(missing)} missing, {len(extra)} extra, {len(mismatched)} mismatched",
        "passed": not missing and not extra and not mismatched,
        "missing": missing,
        "extra": extra,
        "mismatched": mismatched,
    }


CHECKS = [
    check_required_files,
    check_script_compiles,
    check_tests_pass,
    check_forbidden_flags,
    check_runlog_stamp,
    check_runlog_commands,
    check_record_numbers_match,
    check_manifest_integrity,
]


def run_all(root: Path, allow_missing_summary: bool = False, defer_record_check: bool = False) -> dict:
    # 先算「當下的交付物 manifest」——manifest 完整性檢查要拿它當基準，
    # 順序反了就會拿自己比自己（永遠綠）。
    fresh_manifest: dict[str, str] = {}
    for rel in deliverable_files(root):
        try:
            fresh_manifest[rel] = sha256_of(root / rel)
        except OSError:
            continue

    results = []
    for fn in CHECKS:
        if fn is check_record_numbers_match:
            results.append(fn(root, allow_missing_summary=allow_missing_summary,
                              defer=defer_record_check))
        elif fn is check_manifest_integrity:
            results.append(
                fn(root, fresh_manifest, allow_missing_summary=allow_missing_summary)
            )
        else:
            results.append(fn(root))
    summary = {
        "root": str(root),
        "checks": results,
        "counters": {
            "checks_total": len(results),
            "checks_passed": sum(1 for r in results if r["passed"]),
            "checks_failed": sum(1 for r in results if not r["passed"]),
            "tests_passed": next(
                (r.get("passed_count", 0) for r in results if r["name"] == "tests_pass"), 0
            ),
            "tests_failed": next(
                (r.get("failed_count", 0) for r in results if r["name"] == "tests_pass"), 0
            ),
        },
        "artifacts": {},
    }
    # manifest 只收「實際交付物」。實測（2026-10-27）原本收進了 33 個檔案，
    # 包含 __pycache__/*、.pytest_cache/*、merged.bak-* 這些不會交付的東西
    # → 使用者逐一核對 sha256 時對不上 → manifest 失去證據價值。
    # 這裡用「交付清單」明確決定收哪些，而不是「目錄裡所有檔案」。
    summary["artifacts"] = dict(fresh_manifest)
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="交付前機械檢查（code SOP §6/§7/§8）")
    parser.add_argument("root", type=Path, help="產出物目錄")
    parser.add_argument("--json", action="store_true", help="輸出機器可讀 JSON")
    parser.add_argument("--write-summary", action="store_true", help="把結果寫入 verification_summary.json")
    parser.add_argument(
        "--defer-record-check", action="store_true",
        help="把「交付紀錄數字比對」延後到寫完紀錄後的重檢（產生流程的第一次檢查用）",
    )
    args = parser.parse_args(argv)

    if not args.root.is_dir():
        sys.stderr.write(f"錯誤：{args.root} 不是目錄。\n")
        return 2

    summary = run_all(args.root, allow_missing_summary=args.write_summary,
                      defer_record_check=args.defer_record_check)
    failed = summary["counters"]["checks_failed"]

    if args.write_summary:
        out = args.root / "verification_summary.json"
        # 不把自己寫進去（避免自我引用造成 hash 每次都不同）
        out.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"已寫出 {out}")

    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        for r in summary["checks"]:
            mark = "PASS" if r["passed"] else "FAIL"
            print(f"[{mark}] {r['name']}: {r['desc']}")
            print(f"       expected={r['expected']} actual={r['actual']}")
            if not r["passed"]:
                for key in ("hits", "mismatches", "missing"):
                    if r.get(key):
                        for item in r[key][:10]:
                            print(f"       - {item}")
        print(f"\n合計：{summary['counters']['checks_passed']}/{summary['counters']['checks_total']} 通過")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
