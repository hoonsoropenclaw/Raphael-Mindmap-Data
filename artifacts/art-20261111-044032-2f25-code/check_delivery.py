#!/usr/bin/env python3
"""交付閘門：檢查交付集合是否自足、乾淨、可重跑。

這支腳本是 **code SOP §28** 的機械實作。三件事：

1. **自足性（§28-2）**：把交付集合複製到一個**只含交付檔的空目錄**，
   在該目錄執行入口腳本，必須 EXIT=0。
   在工作目錄跑綠**不構成**自足性證據——那是 §15 的同一條紀律。

2. **乾淨度（§23）**：交付集合內不得有 `__pycache__`／`.pyc`／暫存目錄，
   而且任一檔案的 mtime 不得晚於 `verification_summary.json` 的 `generated_at`
   （那代表集合在簽章之後被改動過，例如有人又在交付集合裡跑了一次測試）。

3. **相依完整性（§28-1）**：由入口腳本的 import／呼叫關係反推相依集合，
   每一支都必須存在於交付集合內。缺任一項 → EXIT≠0，並印出缺什麼。

退出碼：
    0 = 全部通過
    1 = 有項目未通過（明細印在畫面上）
    2 = 交付集合不存在或結構無法辨識
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

#: 本檢查器**看**的母體（module-level 常數 → 可被 AST 機械解析）。
#:
#: 為什麼寫成常數而不是寫在 docstring：docstring 不可被機械解析成結構化欄位，
#: 「宣告要揭露」但沒有可檢查的形式 = 跟沒有一樣（11-11 的實測結論）。
POPULATION = (
    "交付集合根目錄下的全部檔案與目錄（偵測暫存物時不套用收錄清單的排除規則），"
    "以及入口腳本的 import／subprocess 呼叫關係所推出的相依集合"
)

#: 本檢查器**不看**的維度（誠實揭露，不得用沉默代替）。
NOT_COVERED = [
    "不驗證交付集合的**功能正確性**（那是 pytest 與 CLI 實跑的責任，本檢查器只驗結構）",
    "不驗證第三方相依（openpyxl）有沒有安裝在目標環境",
    "不驗證目標使用環境的相容性（Windows + Excel 實機行為未驗收）",
    "不驗證宣告（declarations.py）的語意是否成立——那是 check_population_boundary.py 的責任",
]

# 交付集合內允許存在的目錄（相依套件本體）
ALLOWED_DIRS = {"xlsx_recon", "checks", "tools", "tests"}
# 明確不該出現在交付集合裡的暫存物
TRANSIENT_NAMES = {"__pycache__", ".pytest_cache", ".git", ".mypy_cache", ".ruff_cache"}
TRANSIENT_SUFFIXES = {".pyc", ".pyo"}


def list_delivery_files(root: Path) -> list[Path]:
    """列出交付集合的**所有**檔案（不排除任何目錄）。

    為什麼不排除：11-04 的 xlsx-ledger v7 用同一組排除規則去列檔案
    **和**去偵測暫存檔 → 偵測分支結構上不可達（永遠綠）。
    這裡用一份**不排除任何東西**的清單，偵測母體才對得起被偵測母體。
    """
    out: list[Path] = []
    for p in sorted(root.rglob("*")):
        if p.is_file():
            out.append(p)
    return out


def list_manifest_files(root: Path, manifest_name: str = "delivery_manifest.json") -> list[Path]:
    """列出 manifest 收錄範圍內的檔案（排除暫存物）。"""
    return [
        p for p in list_delivery_files(root)
        if not any(part in TRANSIENT_NAMES for part in p.relative_to(root).parts)
        and p.suffix not in TRANSIENT_SUFFIXES
        and p.name != manifest_name
    ]


def collect_imports(py_file: Path, package_root: Path) -> set[str]:
    """用 AST 解析一支 Python 檔的 import 關係，回推它依賴哪些模組檔。

    同時用 grep 補抓「以字串呼叫子腳本」的情況（例如
    `subprocess.run([sys.executable, "checks/check_x.py"])`）——
    AST 看不到字串裡的檔名，但那正是 11-09 的失效模式
    （build.sh 引用的 46 個相依檔一支都沒進交付集合）。
    """
    deps: set[str] = set()
    try:
        tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
    except (SyntaxError, UnicodeDecodeError):
        tree = None

    if tree is not None:
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    deps.add(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                if node.level and node.level > 0:
                    # 相對 import（from .engine import X / from ..pkg.mod import Y）
                    # 必須**解析成檔案路徑**，不能只記模組名——
                    # 11-09 的失效模式就是 build.sh 引用的相依一支都沒進交付集合，
                    # 而當時沒有任何一支檢查器把這個關係反推出來。
                    #
                    # 這裡的坑：相對 import 的基底是**檔案所在的套件**，
                    # 不是套件根目錄。xlsx_recon/cli.py 的 `from .engine import X`
                    # 指的是 xlsx_recon/engine.py。
                    pkg_parts = list(py_file.parent.relative_to(package_root).parts)
                    # level=1 表示「當前套件」，level=2 表示「上一層」
                    if node.level - 1 > 0:
                        pkg_parts = pkg_parts[: len(pkg_parts) - (node.level - 1)]
                    base = package_root.joinpath(*pkg_parts) if pkg_parts else package_root
                    if node.module:
                        target = base / (node.module.replace(".", "/") + ".py")
                        deps.add(str(target.relative_to(package_root)))
                    else:
                        # from . import engine
                        for alias in node.names:
                            target = base / (alias.name.replace(".", "/") + ".py")
                            deps.add(str(target.relative_to(package_root)))
                elif node.module:
                    deps.add(node.module.split(".")[0])

    # 字串裡出現的相對 .py 路徑（subprocess 呼叫子腳本的寫法）
    # 只掃**實際會被當成字串常值**的地方，且**排除 docstring**——
    # 否則 docstring 裡舉例寫的 "checks/check_x.py" 會被當成真相依（假陽性）。
    # docstring 的識別：Module / ClassDef / FunctionDef 的第一個字串常值陳述。
    docstring_nodes: set[int] = set()
    if tree is not None:
        for node in ast.walk(tree):
            if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef,
                                 ast.AsyncFunctionDef)):
                body = getattr(node, "body", [])
                if body and isinstance(body[0], ast.Expr) and \
                        isinstance(body[0].value, ast.Constant) and \
                        isinstance(body[0].value.value, str):
                    docstring_nodes.add(id(body[0].value))

    literal_paths: set[str] = set()
    if tree is not None:
        for node in ast.walk(tree):
            if not isinstance(node, ast.Constant) or not isinstance(node.value, str):
                continue
            if id(node) in docstring_nodes:
                continue
            for m in re.finditer(r"([\w./-]+\.py)", node.value):
                literal_paths.add(m.group(1))
    for m in literal_paths:
        deps.add(m)

    # 套件內的相對 import（from .engine import ... → xlsx_recon/engine.py）
    resolved: set[str] = set()
    for dep in deps:
        if dep.endswith(".py"):
            candidate = package_root / dep
            if candidate.exists():
                resolved.add(str(candidate.relative_to(package_root)))
                continue
            # 相對 import 解析出的路徑即使不存在，也要保留在 deps 裡，
            # 否則缺漏會被靜默丟掉 → 檢查器變成永遠綠。
            resolved.add(dep)
            continue
        if dep in ALLOWED_DIRS and (package_root / dep).is_dir():
            resolved.add(dep)
    return resolved


def check_dependencies(root: Path, entry: Path) -> tuple[list[str], list[str]]:
    """回傳 (缺漏的相依, 已解析的相依清單)。

    缺漏判定：相依路徑在交付集合內**不存在**。
    這裡有個關鍵細節：相對 import 解析出的路徑若不存在，
    必須被報成缺漏——否則「入口腳本在空目錄跑不起來」這件事
    只會在自足性實測時才發現，而自足性實測的失敗訊息是
    「ModuleNotFoundError」，不是「缺哪一個相依檔」。
    前者要人自己推論，後者直接可用。
    """
    missing: list[str] = []
    resolved: list[str] = []
    for py in sorted(root.rglob("*.py")):
        rel = py.relative_to(root)
        if any(part in TRANSIENT_NAMES for part in rel.parts):
            continue
        for dep in collect_imports(py, root):
            dep_path = root / dep
            if dep_path.exists():
                resolved.append(f"{rel} → {dep}")
            else:
                missing.append(f"{rel} 引用了不存在的相依：{dep}")
    return missing, resolved


def check_cleanliness(root: Path, signed_at: str | None) -> tuple[list[str], list[str]]:
    """檢查交付集合的乾淨度。回傳 (問題清單, 暫存檔清單)。"""
    problems: list[str] = []
    transients: list[str] = []

    for p in list_delivery_files(root):
        rel = p.relative_to(root)
        if any(part in TRANSIENT_NAMES for part in rel.parts):
            transients.append(str(rel))
        elif p.suffix in TRANSIENT_SUFFIXES:
            transients.append(str(rel))

    if transients:
        problems.append(
            f"交付集合內有暫存物 {len(transients)} 個：{transients[:10]}"
            f"{' ...' if len(transients) > 10 else ''}"
        )

    # 簽章後被改動（§23-3）
    if signed_at:
        signed = None
        try:
            signed = datetime.fromisoformat(signed_at)
        except ValueError:
            problems.append(f"verification_summary.json 的 generated_at 無法解析：{signed_at!r}")
        if signed is not None:
            # signed_at 帶時區（ISO 8601 with offset），但檔案 mtime 是 UTC 的
            # naive datetime → 必須統一成 aware UTC 才能比較。
            # 否則 TypeError: can't compare offset-naive and offset-aware datetimes
            if signed.tzinfo is None:
                signed = signed.astimezone()
            signed_utc = signed.astimezone(timezone.utc)
            late: list[str] = []
            for p in list_delivery_files(root):
                # 簽章檔案本身必然寫在簽章之後（summary 與 manifest 是在簽章時刻產生的），
                # 把它们算進去會讓這條檢查自我矛盾而恆紅。
                # 這不是放水——它們的 sha256 由 manifest 雙向對帳把關。
                # recon_summary.json 同理：它是對帳結果的機器回算輸出，
                # 由 build_records 在簽章前一刻產生。
                if p.name in {"verification_summary.json", "delivery_manifest.json",
                              "recon_summary.json"}:
                    continue
                mtime = datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc)
                # **比較到秒**（不是微秒）。sealed_at 是秒精度，
                # 而檔案 mtime 有微秒精度 → 同一秒內寫的檔案會被判成「晚於簽章」。
                # 那是競態，不是缺陷。秒精度正好對應 sealed_at 的精度。
                if mtime.replace(microsecond=0) > signed_utc.replace(microsecond=0):
                    late.append(f"{p.relative_to(root)} "
                                f"({mtime.astimezone().isoformat(timespec='seconds')})")
            if late:
                problems.append(
                    f"有 {len(late)} 個檔案的 mtime 晚於簽章時間 {signed_at}：{late[:8]}"
                    f"{' ...' if len(late) > 8 else ''}"
                )
    return problems, transients


def check_self_contained(root: Path, entry_cmd: list[str]) -> tuple[bool, str, str]:
    """把交付集合複製到空目錄，執行入口腳本。回傳 (是否通過, 輸出, 結束碼)。"""
    with tempfile.TemporaryDirectory(prefix="cleanroom_") as tmp:
        clean = Path(tmp) / "delivery"
        shutil.copytree(root, clean, ignore=shutil.ignore_patterns(*TRANSIENT_NAMES))
        # 清掉任何殘留的快取
        for pc in clean.rglob("__pycache__"):
            shutil.rmtree(pc, ignore_errors=True)

        env = dict(os.environ)
        # 不得用 PYTHONPATH 指回工作目錄（§28-2）
        env.pop("PYTHONPATH", None)
        # 空目錄實跑不得留下 __pycache__（否則交付集合會被污染）
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        try:
            proc = subprocess.run(
                entry_cmd, cwd=clean, env=env, capture_output=True,
                text=True, timeout=180,
            )
        except subprocess.TimeoutExpired:
            return False, "", "TIMEOUT"
        output = (proc.stdout or "") + (proc.stderr or "")
        return proc.returncode == 0, output, str(proc.returncode)


def main() -> int:
    ap = argparse.ArgumentParser(description="交付集合閘門：自足性 + 乾淨度 + 相依完整性")
    ap.add_argument("--delivery", required=True, type=Path, help="交付集合根目錄")
    ap.add_argument("--entry", default=None,
                    help="入口指令（預設：python -m xlsx_recon --help）")
    ap.add_argument("--signed-at", default=None,
                    help="簽章時間（ISO 格式）。不給則讀 verification_summary.json 的 generated_at")
    ap.add_argument("--skip-self-contained", action="store_true",
                    help="跳過空目錄實跑（僅供診斷；正式交付不得使用）")
    args = ap.parse_args()

    root: Path = args.delivery
    if not root.is_dir():
        print(f"FAIL：交付集合不存在：{root}", file=sys.stderr)
        return 2

    entry_cmd = args.entry.split() if args.entry else [
        sys.executable, "-m", "xlsx_recon", "--help"
    ]

    failures: list[str] = []
    notes: list[str] = []

    # --- 1. 相依完整性 ---
    missing, resolved = check_dependencies(root, root)
    if missing:
        failures.append(f"相依完整性：{len(missing)} 項缺漏")
        for m in missing:
            failures.append(f"    - {m}")
    notes.append(f"相依關係：解析到 {len(resolved)} 筆，缺漏 {len(missing)} 筆")

    # --- 2. 乾淨度 ---
    signed_at = args.signed_at
    summary_path = root / "verification_summary.json"
    if signed_at is None and summary_path.exists():
        try:
            signed_at = json.loads(summary_path.read_text(encoding="utf-8")).get("generated_at")
        except (json.JSONDecodeError, OSError):
            failures.append("verification_summary.json 無法解析")
    clean_problems, transients = check_cleanliness(root, signed_at)
    failures.extend(clean_problems)
    notes.append(f"乾淨度：暫存物 {len(transients)} 個，簽章時間 {signed_at or '（無）'}")

    # --- 3. 自足性（空目錄實跑）---
    if args.skip_self_contained:
        notes.append("自足性：已跳過（--skip-self-contained，正式交付不得使用）")
    else:
        ok, output, code = check_self_contained(root, entry_cmd)
        notes.append(f"自足性：空目錄實跑結束碼 {code}")
        if not ok:
            failures.append(
                f"自足性：入口腳本在只含交付集合的空目錄中 EXIT={code}（必須為 0）"
            )
            tail = "\n".join(output.strip().splitlines()[-20:])
            failures.append(f"    --- 空目錄實跑輸出（末 20 行）---\n{tail}")

    print("=" * 68)
    print("交付集合閘門")
    print("=" * 68)
    print(f"交付集合：{root}")
    for n in notes:
        print(f"  · {n}")
    print("-" * 68)
    if failures:
        print(f"FAIL（{len(failures)} 項）：")
        for f in failures:
            print(f"  ✗ {f}")
        print("=" * 68)
        return 1
    print("PASS：自足性 / 乾淨度 / 相依完整性 全部通過")
    print("=" * 68)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
