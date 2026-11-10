#!/usr/bin/env python3
"""建置交付集合並產生**單一權威摘要**。

code SOP §24-1 的規定：同一份交付紀錄裡所有關於驗證的數字，
必須來自同一個快照；禁止在權威摘要產生之前先印出任何含數字的交付紀錄。
這個腳本是那個「權威輪」——它跑完所有檢查、把結果寫進
`verification_summary.json`，RUNLOG 與 `artifact add --notes` 一律從它取值。

用法：
    python3 tools/build_records.py --delivery ./delivery
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


RUNLOG_PATH = ROOT / "RUNLOG.md"

#: RUNLOG 裡由機器注入的欄位（佔位符 → 實際值）
#: 為什麼要注入：手寫的數字在下一次建置後一定會變成過期資料。
#: 11-04 的 §24 記錄的正是這個家族——同一份交付物裡對同一件事有四種說法，
#: 而其中一種是「我記得」。
RUNLOG_PLACEHOLDERS = {
    "{{SEALED_AT}}": None,          # 簽章時間
    "{{FILE_COUNT}}": None,          # 交付檔案數
    "{{PYTEST_RESULT}}": None,       # pytest 輸出摘要
    "{{GATE_RESULT}}": None,         # 交付閘門輸出摘要
    "{{BUILD_RESULT}}": None,        # 建置結果輸出摘要
}


def inject_runlog_numbers(delivery: Path, values: dict[str, str]) -> None:
    """把機器回算的數字注入 RUNLOG 的佔位符。

    注入後的 RUNLOG 才會被複製進交付集合——所以交付集合裡的 RUNLOG
    與那一輪的 verification_summary.json 一定是**同版**的。

    每次呼叫都是從**來源 RUNLOG** 重新注入（不是從交付集合裡那份），
    否則第二次注入會把第一次注入的結果覆蓋掉。
    """
    src = RUNLOG_PATH
    if not src.exists():
        return
    text = src.read_text(encoding="utf-8")
    for key, val in values.items():
        if val is None:
            continue
        text = text.replace(key, str(val))
    # 未被替換的佔位符 = 機器算不出來 → 必須讓它顯眼，不能靜默留下
    leftover = [k for k in RUNLOG_PLACEHOLDERS if k in text]
    if leftover:
        print(f"警告：RUNLOG 仍有未注入的佔位符：{leftover}", file=sys.stderr)
    out = delivery / "RUNLOG.md"
    out.write_text(text, encoding="utf-8")


def clean_transients(root: Path) -> None:
    """清掉交付集合內的執行期產物（__pycache__／.pyc／.pytest_cache）。

    為什麼需要：那些檔案是「執行」的產物，不是「交付」的內容。
    11-04 的 xlsx-ledger v7 交付集合裡有 19 個這樣的檔案，
    而且全部的 mtime 都晚於簽章時間——使用者拿到手時看到的是被污染的集合。
    """
    for pc in root.rglob("__pycache__"):
        shutil.rmtree(pc, ignore_errors=True)
    for pcf in root.rglob("*.pyc"):
        pcf.unlink(missing_ok=True)
    for pcf in root.rglob("*.pyo"):
        pcf.unlink(missing_ok=True)
    for pdir in root.rglob(".pytest_cache"):
        shutil.rmtree(pdir, ignore_errors=True)


def compute_manifest(root: Path) -> dict[str, str]:
    """回算交付集合的 sha256 manifest（排除簽章檔案與暫存物）。"""
    manifest: dict[str, str] = {}
    for p in sorted(root.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(root)
        if any(part in {"__pycache__", ".pytest_cache"} for part in rel.parts):
            continue
        if p.suffix in {".pyc", ".pyo"}:
            continue
        if p.name in {"delivery_manifest.json", "verification_summary.json"}:
            continue
        manifest[str(rel)] = sha256(p)
    return manifest


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def run(cmd: list[str], cwd: Path, timeout: int = 300) -> dict:
    """跑一條指令並記錄結束碼與輸出摘要。

    設 PYTHONDONTWRITEBYTECODE=1：**任何**在交付集合裡跑的 Python 都不該
    留下 __pycache__／.pyc——那些是執行期產物，不屬於交付內容。
    11-04 的 xlsx-ledger v7 交付集合裡有 19 個這樣的檔案。
    """
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    try:
        proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                              timeout=timeout, env=env)
    except subprocess.TimeoutExpired:
        return {"cmd": " ".join(cmd), "exit_code": "TIMEOUT", "output": ""}
    out = (proc.stdout or "") + (proc.stderr or "")
    return {
        "cmd": " ".join(cmd),
        "exit_code": proc.returncode,
        "output_tail": "\n".join(out.strip().splitlines()[-15:]),
    }


def build_delivery(target: Path) -> list[str]:
    """把要交付的檔案複製到 target，回傳相對路徑清單。"""
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True)

    copied: list[str] = []

    # 套件本體
    shutil.copytree(ROOT / "xlsx_recon", target / "xlsx_recon",
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    copied.append("xlsx_recon/")

    # 檢查器
    shutil.copytree(ROOT / "checks", target / "checks",
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    copied.append("checks/")

    # 工具
    shutil.copytree(ROOT / "tools", target / "tools",
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    copied.append("tools/")

    # 測試（含測試資料）
    shutil.copytree(ROOT / "tests", target / "tests",
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest_cache"))
    copied.append("tests/")

    # 文件
    for name in ("README.md", "RUNLOG.md"):
        src = ROOT / name
        if src.exists():
            shutil.copy2(src, target / name)
            copied.append(name)

    return copied


def main() -> int:
    ap = argparse.ArgumentParser(description="建置交付集合並產生權威摘要")
    ap.add_argument("--delivery", required=True, type=Path, help="交付集合輸出目錄")
    ap.add_argument("--skip-build", action="store_true", help="不重新複製檔案，只重跑檢查")
    ap.add_argument("--pycache-dir", default=None,
                    help="pytest 的 pycache 目錄（避免它在交付集合內產生暫存檔）")
    args = ap.parse_args()

    delivery: Path = args.delivery
    if not args.skip_build:
        build_delivery(delivery)

    # **pytest 必須在交付集合外跑**（§23-1）。
    # 否則 pytest 會在交付集合裡產生 __pycache__／.pyc，
    # 讓「簽章時點」與「使用者到手時點」不一致——
    # 這正是 11-04 xlsx-ledger v7 的失效模式（交付集合裡有 19 個執行期產物）。
    #
    # 注意：--basetemp 必須給**絕對路徑**。pytest 會把相對路徑解析成
    # 相對於 cwd（= 交付集合）的路徑，那樣 basetemp 就落在交付集合裡了。
    # 踩過的坑：這裡原本用相對路徑 → basetemp 落進 delivery/ →
    # pytest 的 tmp_path_factory 直接 FileNotFoundError，22 個測試全掛。
    pycache_dir = args.pycache_dir
    if pycache_dir is None:
        pycache_dir = str((delivery.parent / ".pytest_cache_outside_delivery").resolve())
    pycache_path = Path(pycache_dir)
    pycache_path.mkdir(parents=True, exist_ok=True)
    basetemp = pycache_path / "basetemp"
    # pytest 要求 basetemp 的父目錄存在，且 basetemp 本身不存在或可清空
    if basetemp.exists():
        shutil.rmtree(basetemp, ignore_errors=True)
    pycache_path.mkdir(parents=True, exist_ok=True)

    steps: list[tuple[str, str, dict]] = []

    # --- 步驟 1：pytest（在交付集合裡跑，但暫存檔導到外面）---
    steps.append(("pytest 全套測試", "0", run(
        [sys.executable, "-m", "pytest", "tests/", "-q",
         "-p", "no:cacheprovider",
         f"--basetemp={basetemp}"],
        cwd=delivery,
    )))
    # 跑完立刻清掉交付集合內的暫存物（它們是執行期產物，不屬於交付內容）
    for pc in delivery.rglob("__pycache__"):
        shutil.rmtree(pc, ignore_errors=True)
    for pcf in delivery.rglob("*.pyc"):
        pcf.unlink(missing_ok=True)

    # --- 步驟 2：CLI 在乾淨資料上的實跑 ---
    steps.append(("CLI 實跑（乾淨資料）", "0", run(
        [sys.executable, "-m", "xlsx_recon",
         "--input", "tests/testdata/testdata_clean", "--report-only"],
        cwd=delivery,
    )))

    # --- 步驟 3：CLI 在缺陷資料上的實跑（必須非 0）---
    steps.append(("CLI 實跑（缺陷資料，必須非 0）", "nonzero", run(
        [sys.executable, "-m", "xlsx_recon",
         "--input", "tests/testdata/testdata_bad_subtotal", "--report-only"],
        cwd=delivery,
    )))

    # --- 步驟 4：對帳結果（機器回算的權威數字）---
    recon_path = delivery / "recon_summary.json"
    steps.append(("對帳結果 JSON 回算", "0", run(
        [sys.executable, "-m", "xlsx_recon",
         "--input", "tests/testdata/testdata_clean", "--report-only", "--json"],
        cwd=delivery,
    )))
    # 把 JSON 輸出存檔（上面的 run 只留尾巴）
    proc = subprocess.run(
        [sys.executable, "-m", "xlsx_recon",
         "--input", "tests/testdata/testdata_clean", "--report-only", "--json"],
        cwd=delivery, capture_output=True, text=True, timeout=180,
    )
    try:
        recon_path.write_text(proc.stdout, encoding="utf-8")
    except OSError as exc:
        print(f"警告：無法寫入 {recon_path}：{exc}", file=sys.stderr)

    # **所有會產生暫存物的步驟都跑完了 → 現在才清一次。**
    # 順序很重要：簽章之後任何在交付集合裡的執行都會讓 mtime 晚於簽章時間
    # → §23-3 的檢查會亮紅。這不是誤報，這正是它要抓的東西。
    clean_transients(delivery)

    # --- 步驟 5：交付閘門（在交付集合裡跑，§15）---
    # 閘門此刻還沒有簽章時間可用（summary 還沒寫），
    # 所以先用「不檢查簽章時點」的方式跑一次：自足性 + 乾淨度 + 相依完整性。
    # 簽章後會再跑一次「含簽章時點」的版本——那是權威輪。
    steps.append(("交付閘門（自足性/乾淨度/相依）", "0", run(
        [sys.executable, "checks/check_delivery.py", "--delivery", "."],
        cwd=delivery,
    )))

    # 閘門跑完可能又產生暫存物 → 再清一次
    clean_transients(delivery)

    # --- 步驟 5b：宣告 ↔ 後果對帳（§25-6 的 N/M/K）---
    #
    # 為什麼必須接進交付裁決：§25-6 說「K>0 即 exit≠0 並印出條號」，
    # 而且「K=0 也要把 N／M 印進 verification_summary.json」。
    # 如果這支檢查器不在建置流程裡跑，它就只是另一支躺在 tools/ 裡的程式——
    # 宣告寫得再漂亮，綠燈也不會被它約束（11-11 的實測結論）。
    #
    # 這一輪刻意**不**用 --skip-probes：探針必須真的跑過才知道後果可執行。
    # 探針在交付集合的**缺陷副本**上跑（臨時目錄），不會污染交付集合本身。
    boundary_json_path = delivery / "declaration_reconciliation.json"
    steps.append(("宣告 ↔ 後果對帳（N/M/K）", "0", run(
        [sys.executable, "checks/check_population_boundary.py",
         "--delivery", ".", "--json"],
        cwd=delivery,
    )))
    # 把 N/M/K 存成獨立檔案（給 summary 引用，也給人直接讀）
    try:
        proc = subprocess.run(
            [sys.executable, "checks/check_population_boundary.py",
             "--delivery", ".", "--json"],
            cwd=delivery, capture_output=True, text=True, timeout=600,
        )
        boundary_json_path.write_text(proc.stdout, encoding="utf-8")
        boundary_data = json.loads(proc.stdout)
    except (subprocess.TimeoutExpired, json.JSONDecodeError, OSError) as exc:
        boundary_data = {}
        print(f"警告：無法取得宣告對帳結果：{exc}", file=sys.stderr)

    # 探針在臨時目錄跑，交付集合本身不該有暫存物 → 再清一次
    clean_transients(delivery)

    # --- 簽章（這是「使用者到手時點」的基準）---
    # §23-3：交付集合內任一檔案的 mtime 晚於 generated_at 即代表集合被改動過。
    # 所以簽章必須在**所有內容檔案都寫完、暫存物清乾淨之後**才進行。
    sealed_at = datetime.now().astimezone().isoformat(timespec="seconds")

    # --- RUNLOG 數字注入（第一輪：簽章時間、pytest 與 gate 輸出）---
    # 交付集合裡的 RUNLOG 必須與這一輪的機器回算**同版**。
    pytest_step = next((s for n, e, s in steps if n == "pytest 全套測試"), {})
    gate_step = next((s for n, e, s in steps if n.startswith("交付閘門（自足性")), {})
    inject_runlog_numbers(delivery, {
        "{{SEALED_AT}}": sealed_at,
        "{{PYTEST_RESULT}}": pytest_step.get("output_tail", ""),
        "{{GATE_RESULT}}": gate_step.get("output_tail", ""),
    })

    # --- manifest（RUNLOG 注入之後才計算，sha256 才正確）---
    manifest = compute_manifest(delivery)
    (delivery / "delivery_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # --- 步驟 6：交付閘門（**含簽章時點**的權威輪）---
    # §23-3 的 mtime 檢查只有在簽章之後才有意義。
    steps.append(("交付閘門（簽章後權威輪）", "0", run(
        [sys.executable, "checks/check_delivery.py", "--delivery", ".",
         "--signed-at", sealed_at],
        cwd=delivery,
    )))

    # 權威輪跑完 → 再清一次暫存物
    clean_transients(delivery)

    # --- 權威摘要 ---
    # §24-1：所有關於驗證的數字必須來自同一個快照。
    # generated_at = 簽章時間（sealed_at），不是「現在」——
    # 否則 summary 的 mtime 會比它自己宣告的簽章時間晚，§23-3 的檢查會自我矛盾。
    summary = {
        "generated_at": sealed_at,
        "tool": "xlsx_recon",
        "version": "1.0.0",
        "sop_version": "code v1.19.0",
        "steps": [
            {"name": name, "expected_exit": expected, **s}
            for name, expected, s in steps
        ],
        "step_exit_codes": {name: s["exit_code"] for name, expected, s in steps},
        "file_manifest_sha256": {},       # 下面填（RUNLOG 注入後才有最終值）
        "file_count": 0,                  # 同上
        "notes": {
            "authority": "本檔是唯一權威摘要；RUNLOG 與 artifact notes 的數字一律引用這裡。",
            "no_manual_counts": "檔案數與步驟結束碼皆由本腳本回算，未手抄。",
            "seal_semantics": "generated_at 是簽章時點；交付集合內任一檔案的 mtime "
                              "晚於它即代表集合在簽章後被改動過（§23-3）。",
        },
    }

    # --- 建置結果文字（給 RUNLOG 的 {{BUILD_RESULT}} 與螢幕輸出共用）---
    # 兩者必須是**同一份文字**——否則 RUNLOG 裡的建置結果會與螢幕上的不一致
    # （11-04 的 §24：同一份交付物裡對同一件事有四種說法）。
    result_lines = ["=" * 68, "建置結果", "=" * 68]
    all_ok = True
    for name, expected, s in steps:
        actual = s["exit_code"]
        ok = (actual != 0) if expected == "nonzero" else (actual == 0)
        all_ok = all_ok and ok
        status = "OK " if ok else "FAIL"
        exp_text = "非 0" if expected == "nonzero" else "0"
        result_lines.append(f"  [{status}] {name}")
        result_lines.append(f"          結束碼 = {actual}（預期 {exp_text}）")
        if not ok:
            result_lines.append("          " + s.get("output_tail", "").replace("\n", "\n          "))
    build_result_text = "\n".join(result_lines)

    # --- RUNLOG 最終注入（含 build result）---
    # 這是最後一次注入：build result 裡有檔案數與簽章時間，
    # 而它們此時已經確定。注入後 manifest 與 summary 才寫入（sha256 才對）。
    file_count = len(compute_manifest(delivery))
    inject_runlog_numbers(delivery, {
        "{{SEALED_AT}}": sealed_at,
        "{{FILE_COUNT}}": str(file_count),
        "{{PYTEST_RESULT}}": pytest_step.get("output_tail", ""),
        "{{GATE_RESULT}}": gate_step.get("output_tail", ""),
        "{{BUILD_RESULT}}": build_result_text,
    })

    # --- manifest（RUNLOG 注入之後才計算，sha256 才正確）---
    manifest = compute_manifest(delivery)
    (delivery / "delivery_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # --- 權威摘要（manifest 已知）---
    summary["file_manifest_sha256"] = manifest
    summary["file_count"] = len(manifest)
    (delivery / "verification_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # --- 結果 ---
    print("=" * 68)
    print("建置結果")
    print("=" * 68)
    all_ok = True
    for name, expected, s in steps:
        actual = s["exit_code"]
        ok = (actual != 0) if expected == "nonzero" else (actual == 0)
        all_ok = all_ok and ok
        status = "OK " if ok else "FAIL"
        exp_text = "非 0" if expected == "nonzero" else "0"
        print(f"  [{status}] {name}")
        print(f"          結束碼 = {actual}（預期 {exp_text}）")
        if not ok:
            print("          " + s.get("output_tail", "").replace("\n", "\n          "))
    print(f"  交付檔案數：{len(manifest)}")
    print(f"  簽章時間：{sealed_at}")
    print(f"  摘要已寫入：{delivery / 'verification_summary.json'}")
    print("=" * 68)
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
