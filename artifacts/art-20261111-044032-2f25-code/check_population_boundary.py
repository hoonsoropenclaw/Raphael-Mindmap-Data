#!/usr/bin/env python3
"""宣告 ↔ 後果對帳：N / M / K 與對抗性探針註冊表。

這支腳本是 **code SOP §25-6** 的機械實作，也是 2026-11-11 學習卡
「宣告的可解析性：宣告指向的後果與探針必須是機械可定位的存在的實體」的落地機制。

病根（11-11 的實測）
---------------------
11-10 的 `xlsx_recon/declarations.py` 寫了 9 條宣告，每條都有 `consequence` 與 `probe`，
但其中 2 條指向的檔案（`checks/check_population_boundary.py`）**在整個工作目錄裡不存在**。

→ 宣告寫得越詳細、越像真的，越危險：它在宣稱一個不存在的檔案會讓它變紅。
使用者看到 9 條完整宣告，會合理地認為 9 條都被驗證過——實際上有幾條有後果是未知的。

本檢查器量的三個數字
--------------------
    N = 宣告條數
    M = 有**可執行後果**的條數（後果指向的檔案與符號真的存在 ＋ 探針真的註冊且可跑）
    K = 宣告了但無後果的條數（K > 0 即 exit≠0 並印出條號）

為什麼「檔案存在」要用 AST 而不是 grep
------------------------------------
宣告自己的 docstring、註解、甚至宣告文字裡都可能出現 "檔案.py:符號()" 的樣子。
字串比對會被這些文字騙過去——**AST 只認真的語法結構**。

退出碼
------
    0 = 全部宣告都有可執行後果，且每支檢查器都揭露了母體與未涵蓋維度
    1 = 有宣告沒有後果（K > 0），或某支檢查器沒揭露母體／未涵蓋維度
    2 = 交付集合不存在或無法讀取
"""
from __future__ import annotations

import argparse
import ast
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

#: 本檢查器**看**的母體（module-level 常數 → 可被機械解析）。
#:
#: 為什麼寫成常數而不是寫在 docstring：docstring 不可被機械解析成結構化欄位，
#: 「宣告要揭露」但沒有可檢查的形式 = 跟沒有一樣（11-11 的實測結論）。
POPULATION = (
    "交付集合內 xlsx_recon/declarations.py 的每一條宣告（id / rule / population / "
    "not_covered / consequence / probe 六欄全部必填），以及 checks/ 下的每一支檢查器"
)

#: 本檢查器**不看**的維度（誠實揭露，不得用沉默代替）。
NOT_COVERED = [
    "不驗證探針是否覆蓋了宣告語意的所有可能反例（探針是代表性反例，不是窮舉）",
    "不驗證 consequence 文字的語意是否正確（只驗證它指向的實體存在且可執行）",
    "不驗證 checks/ 以外的檔案是否揭露母體",
    "不驗證宣告宣稱的規則在**語意**上是否正確（只驗證後果機制存在）",
]

#: 遞迴保護：探針會再跑一次本檢查器，那一次不得再跑探針（否則無限遞迴）。
SKIP_PROBES_ENV = "XLSX_RECON_SKIP_PROBES"

#: `檔案.py:符號()` 的樣式。consequence 欄位裡必須用這個格式寫後果。
#: 為什麼要求括號：沒有括號的 "xlsx_recon/engine.py:reconcile" 會跟散文撞車，
#: 誤抓率太高（11-11 實測：10 個引用裡有 2 個是 docstring 文字）。
REF_RE = re.compile(r"([\w./\-]+\.py):([A-Za-z_]\w*)\(\)")

#: 探針必須註冊在 PROBES 裡；每個探針必須真的跑出一個明確結論。
#:
#: 探針的語意：**在交付集合的缺陷副本上跑對應的檢查器，必須 exit≠0**。
#: 只在乾淨副本上跑綠不算驗證（§9-2、§16-6 同紀律）。
PROBES: dict[str, object] = {}


def _register(name: str):
    def deco(fn):
        PROBES[name] = fn
        return fn
    return deco


# ----------------------------------------------------------------------
# 交付集合載入
# ----------------------------------------------------------------------

def load_declarations(delivery: Path) -> list:
    """從交付集合載入 DECLARATIONS（動態載入，不吃工作目錄的 sys.path）。

    為什麼要手動塞進 sys.modules：@dataclass 在建立類別時會回頭查
    sys.modules[cls.__module__].__dict__ 來解析型別註解。若模組不在
    sys.modules 裡，dataclass 會丟出
    「'NoneType' object has no attribute '__dict__'」。
    這是動態載入 dataclass 模組的必備步驟（11-11 實測踩到）。
    """
    mod_path = delivery / "xlsx_recon" / "declarations.py"
    if not mod_path.exists():
        raise FileNotFoundError(f"找不到宣告模組：{mod_path}")
    spec = importlib.util.spec_from_file_location("_decl_under_test", mod_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"無法載入宣告模組：{mod_path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    try:
        spec.loader.exec_module(mod)
    except Exception:
        sys.modules.pop(spec.name, None)
        raise
    decls = getattr(mod, "DECLARATIONS", None)
    if decls is None:
        raise RuntimeError(f"宣告模組沒有 DECLARATIONS：{mod_path}")
    return list(decls)


def symbols_in(path: Path) -> set[str]:
    """用 AST 抓出一支 Python 檔裡可被引用的符號（function / class，含巢狀）。"""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (SyntaxError, UnicodeDecodeError) as exc:
        raise RuntimeError(f"{path.name} 無法解析：{exc}") from exc
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(node.name)
    return names


# ----------------------------------------------------------------------
# 宣告 ↔ 後果對帳
# ----------------------------------------------------------------------

def check_consequences(delivery: Path, decls: list) -> dict:
    """逐條檢查 consequence 指向的檔案／符號是否存在。回傳明細。"""
    rows: list[dict] = []
    for d in decls:
        did = str(getattr(d, "id", "(無 id)"))
        refs = REF_RE.findall(str(getattr(d, "consequence", "")))
        resolved: list[str] = []
        dangling: list[str] = []
        for rel, sym in refs:
            target = delivery / rel
            if not target.exists():
                dangling.append(f"{rel}:{sym}()（檔案不存在）")
                continue
            try:
                syms = symbols_in(target)
            except RuntimeError as exc:
                dangling.append(f"{rel}:{sym}()（{exc}）")
                continue
            if sym not in syms:
                dangling.append(f"{rel}:{sym}()（符號不存在）")
                continue
            resolved.append(f"{rel}:{sym}()")
        rows.append({
            "id": did,
            "refs": [f"{r}:{s}()" for r, s in refs],
            "resolved": resolved,
            "dangling": dangling,
            "has_ref": bool(refs),
        })
    return {"rows": rows}


def check_probes(decls: list) -> dict:
    """逐條檢查 probe 名是否在註冊表裡。"""
    rows: list[dict] = []
    for d in decls:
        did = str(getattr(d, "id", "(無 id)"))
        pname = str(getattr(d, "probe", ""))
        if not pname:
            rows.append({"id": did, "probe": pname, "registered": False,
                         "reason": "宣告沒有寫 probe 名"})
            continue
        if pname not in PROBES:
            rows.append({"id": did, "probe": pname, "registered": False,
                         "reason": "探針未在 PROBES 註冊表裡"})
            continue
        fn = PROBES[pname]
        if not callable(fn):
            rows.append({"id": did, "probe": pname, "registered": False,
                         "reason": "探針已註冊但不可呼叫"})
            continue
        rows.append({"id": did, "probe": pname, "registered": True, "reason": ""})
    return {"rows": rows}


def check_checkers_declare_boundary(delivery: Path) -> list[dict]:
    """每支檢查器都必須揭露母體（POPULATION）與未涵蓋維度（NOT_COVERED）。

    為什麼是模組層級常數而不是 docstring：docstring 不可被機械解析成結構化欄位，
    宣告「要揭露」但沒有可檢查的形式 = 跟沒有一樣。
    """
    violations: list[dict] = []
    for py in sorted((delivery / "checks").glob("*.py")):
        if py.name == Path(__file__).name:
            # 這支檢查器自己也是宣告母體的檢查器——它同樣必須揭露。
            pass
        try:
            tree = ast.parse(py.read_text(encoding="utf-8"), filename=str(py))
        except (SyntaxError, UnicodeDecodeError) as exc:
            violations.append({"file": py.name, "problem": f"無法解析：{exc}"})
            continue
        found: dict[str, ast.AST] = {}
        for node in tree.body:
            if isinstance(node, ast.Assign) and len(node.targets) == 1:
                tgt = node.targets[0]
                if isinstance(tgt, ast.Name) and tgt.id in {"POPULATION", "NOT_COVERED"}:
                    found[tgt.id] = node.value
            elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                if node.target.id in {"POPULATION", "NOT_COVERED"}:
                    found[node.target.id] = node.value
        for required in ("POPULATION", "NOT_COVERED"):
            if required not in found:
                violations.append({"file": py.name, "problem": f"缺 {required} 宣告"})
                continue
            val = found[required]
            if required == "POPULATION":
                if not (isinstance(val, ast.Constant) and isinstance(val.value, str)
                        and val.value.strip()):
                    violations.append({"file": py.name, "problem": "POPULATION 必須是非空字串"})
            else:
                ok = (isinstance(val, (ast.List, ast.Tuple))
                      and len(val.elts) > 0)
                if not ok:
                    violations.append({"file": py.name, "problem": "NOT_COVERED 必須是非空清單"})
    return violations


# ----------------------------------------------------------------------
# 對抗性探針（缺陷副本 → 必須 exit≠0）
# ----------------------------------------------------------------------

def _copy_delivery(delivery: Path, tmp: Path) -> Path:
    clean = tmp / "delivery"
    shutil.copytree(delivery, clean, ignore=shutil.ignore_patterns(
        "__pycache__", "*.pyc", ".pytest_cache"))
    for pc in clean.rglob("__pycache__"):
        shutil.rmtree(pc, ignore_errors=True)
    return clean


def _run(cmd: list[str], cwd: Path, timeout: int = 180) -> int:
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    # 探針會再跑一次本檢查器 → 那一次不得再跑探針（否則無限遞迴）
    env[SKIP_PROBES_ENV] = "1"
    try:
        proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                              timeout=timeout, env=env)
    except subprocess.TimeoutExpired:
        return 99
    return proc.returncode


def _cli_on(clean: Path, dataset: str) -> int:
    return _run([sys.executable, "-m", "xlsx_recon",
                 "--input", f"tests/testdata/{dataset}", "--report-only"], clean)


@_register("probe_tampered_subtotal")
def _probe_tampered_subtotal(delivery: Path) -> tuple[bool, str]:
    """來源檔的小計被改錯 → CLI 必須 exit≠0。"""
    with tempfile.TemporaryDirectory(prefix="probe_") as tmp:
        clean = _copy_delivery(delivery, Path(tmp))
        rc = _cli_on(clean, "testdata_bad_subtotal")
    return rc != 0, f"CLI on testdata_bad_subtotal → exit={rc}（必須非 0）"


@_register("probe_unparseable_excluded")
def _probe_unparseable_excluded(delivery: Path) -> tuple[bool, str]:
    """無法解析的列必須被排除且留原因（不是靜默消失）。"""
    with tempfile.TemporaryDirectory(prefix="probe_") as tmp:
        clean = _copy_delivery(delivery, Path(tmp))
        rc = _run([sys.executable, "-m", "xlsx_recon", "--input",
                   "tests/testdata/testdata_clean", "--report-only", "--json"], clean)
        out = _capture([sys.executable, "-m", "xlsx_recon", "--input",
                        "tests/testdata/testdata_clean", "--report-only", "--json"], clean)
    try:
        data = json.loads(out)
    except (json.JSONDecodeError, TypeError):
        return False, "無法取得 JSON 對帳結果"
    excl = data["recon"]["excluded_rows_detail"]
    if not excl:
        return False, "乾淨資料集沒有任何被排除的列（探針前提不成立）"
    missing = [e for e in excl if not e.get("reason")]
    if missing:
        return False, f"有 {len(missing)} 筆被排除的列沒有原因留痕"
    return rc == 0, f"被排除列 {len(excl)} 筆，全部有 reason；CLI exit={rc}"


@_register("probe_missing_required_column")
def _probe_missing_required_column(delivery: Path) -> tuple[bool, str]:
    """缺必要欄位 → CLI 必須 exit≠0 且不拖垮同批次其他檔。"""
    with tempfile.TemporaryDirectory(prefix="probe_") as tmp:
        clean = _copy_delivery(delivery, Path(tmp))
        rc = _cli_on(clean, "testdata_broken")
    return rc != 0, f"CLI on testdata_broken → exit={rc}（必須非 0）"


@_register("probe_k_gt_zero")
def _probe_k_gt_zero(delivery: Path) -> tuple[bool, str]:
    """本檢查器自己：宣告指向不存在的檔案 → 必須 exit≠0（K>0）。"""
    with tempfile.TemporaryDirectory(prefix="probe_") as tmp:
        clean = _copy_delivery(delivery, Path(tmp))
        decl = clean / "xlsx_recon" / "declarations.py"
        text = decl.read_text(encoding="utf-8")
        # 把其中一條宣告的後果指向一個不存在的檔案
        text = text.replace("checks/check_delivery.py:check_dependencies()",
                            "checks/check_not_exists.py:check_nothing()")
        decl.write_text(text, encoding="utf-8")
        rc = _run([sys.executable, "checks/check_population_boundary.py",
                   "--delivery", "."], clean)
    return rc != 0, f"注入不存在的後果 → 本檢查器 exit={rc}（必須非 0）"


@_register("probe_fake_claim")
def _probe_fake_claim(delivery: Path) -> tuple[bool, str]:
    """自評宣稱存在但產物裡沒有的東西 → check_selfeval_claims 必須 exit≠0。"""
    with tempfile.TemporaryDirectory(prefix="probe_") as tmp:
        clean = _copy_delivery(delivery, Path(tmp))
        # corpus 必須存在：否則 check_selfeval_claims 會以 exit=2（環境錯誤）離開，
        # 那不是「宣稱被抓住」的證據——探針必須打在**正確的失敗原因**上。
        (clean / "probe_corpus.txt").write_text(
            "第 1 頁 金額 100.00\n第 2 頁 金額 200.00\n", encoding="utf-8")
        claims = clean / "probe_claims.json"
        claims.write_text(json.dumps({"claims": [
            {"id": "PROBE-FAKE", "text": "第 99 頁有一筆金額 123456.78 的資料"}],
            "must_find": []}, ensure_ascii=False), encoding="utf-8")
        rc = _run([sys.executable, "checks/check_selfeval_claims.py",
                   "--claims", "probe_claims.json",
                   "--corpus", "probe_corpus.txt"], clean)
        out = _capture([sys.executable, "checks/check_selfeval_claims.py",
                        "--claims", "probe_claims.json",
                        "--corpus", "probe_corpus.txt", "--json"], clean)
    # 必須是「宣稱被抓住」的失敗（exit=1），不是「環境壞掉」的失敗（exit=2）。
    if rc == 2:
        return False, f"探針環境錯誤（exit=2）而不是宣稱被抓住（exit=1）：{out.strip()[-300:]}"
    try:
        data = json.loads(out)
    except (json.JSONDecodeError, TypeError):
        return False, "無法解析 check_selfeval_claims 的 JSON 輸出"
    if not data.get("claim_violations"):
        return False, "check_selfeval_claims 沒報出任何 claim_violations（宣稱沒被抓住）"
    return rc != 0, (
        f"注入假宣稱 → check_selfeval_claims exit={rc}，"
        f"報出 {len(data['claim_violations'])} 筆宣稱不對應"
    )


@_register("probe_self_contained_fails")
def _probe_self_contained_fails(delivery: Path) -> tuple[bool, str]:
    """交付集合不自足 → check_delivery 必須 exit≠0。"""
    with tempfile.TemporaryDirectory(prefix="probe_") as tmp:
        clean = _copy_delivery(delivery, Path(tmp))
        # 破壞入口：讓套件無法匯入
        (clean / "xlsx_recon" / "engine.py").write_text(
            "raise ImportError('probe: 故意破壞')\n", encoding="utf-8")
        rc = _run([sys.executable, "checks/check_delivery.py", "--delivery", "."], clean)
    return rc != 0, f"破壞入口 → check_delivery exit={rc}（必須非 0）"


@_register("probe_missing_dependency")
def _probe_missing_dependency(delivery: Path) -> tuple[bool, str]:
    """相依檔被刪 → check_delivery 必須 exit≠0 並指名缺哪一個。"""
    with tempfile.TemporaryDirectory(prefix="probe_") as tmp:
        clean = _copy_delivery(delivery, Path(tmp))
        (clean / "xlsx_recon" / "normalize.py").unlink()
        rc = _run([sys.executable, "checks/check_delivery.py", "--delivery", "."], clean)
    return rc != 0, f"刪掉 normalize.py → check_delivery exit={rc}（必須非 0）"


@_register("probe_transient_pollution")
def _probe_transient_pollution(delivery: Path) -> tuple[bool, str]:
    """交付集合內有執行期產物 → check_delivery 必須 exit≠0。"""
    with tempfile.TemporaryDirectory(prefix="probe_") as tmp:
        clean = _copy_delivery(delivery, Path(tmp))
        (clean / "xlsx_recon" / "__pycache__").mkdir(parents=True, exist_ok=True)
        (clean / "xlsx_recon" / "__pycache__" / "engine.cpython-312.pyc").write_bytes(b"\x00")
        rc = _run([sys.executable, "checks/check_delivery.py", "--delivery", "."], clean)
    return rc != 0, f"注入 __pycache__ → check_delivery exit={rc}（必須非 0）"


@_register("probe_missing_not_covered")
def _probe_missing_not_covered(delivery: Path) -> tuple[bool, str]:
    """某支檢查器缺 not_covered（或 POPULATION）→ 本檢查器必須 exit≠0。

    為什麼注入的是 checks/ 底下的檔案而不是 declarations.py：
    本檢查器的母體是「checks/ 下的每一支檢查器」——
    宣告檔（declarations.py）自己也有 not_covered 欄，但那是**宣告的欄位**，
    由 `check_consequences()` 的存在性檢查管，不屬於本檢查器的偵測母體。
    11-11 實測：原本這個探針改的是 declarations.py，
    而本檢查器根本不讀宣告檔的 not_covered → 探針 exit=0 → 探針自己失效。
    這正是「探針必須打在正確的失敗原因上」的反例。
    """
    with tempfile.TemporaryDirectory(prefix="probe_") as tmp:
        clean = _copy_delivery(delivery, Path(tmp))
        target = clean / "checks" / "check_delivery.py"
        text = target.read_text(encoding="utf-8")
        # 把 NOT_COVERED 清空 → 該檢查器就沒有揭露未涵蓋維度
        text = re.sub(r"NOT_COVERED\s*=\s*\[[^\]]*\]",
                      'NOT_COVERED = []', text, count=1, flags=re.S)
        if "NOT_COVERED = []" not in text:
            return False, "注入失敗：沒能在 check_delivery.py 裡清空 NOT_COVERED"
        target.write_text(text, encoding="utf-8")
        rc = _run([sys.executable, "checks/check_population_boundary.py",
                   "--delivery", "."], clean)
        out = _capture([sys.executable, "checks/check_population_boundary.py",
                        "--delivery", "."], clean)
    return rc != 0, f"清空 check_delivery.py 的 NOT_COVERED → 本檢查器 exit={rc}（必須非 0）"


@_register("probe_hollow_population")
def _probe_hollow_population(delivery: Path) -> tuple[bool, str]:
    """母體被掏空（多數列無法解析）→ CLI 必須 exit≠0，即使等式仍成立。"""
    with tempfile.TemporaryDirectory(prefix="probe_") as tmp:
        clean = _copy_delivery(delivery, Path(tmp))
        rc = _cli_on(clean, "testdata_hollow")
        out = _capture([sys.executable, "-m", "xlsx_recon", "--input",
                        "tests/testdata/testdata_hollow", "--report-only", "--json"], clean)
    try:
        data = json.loads(out)
        hollow = data["recon"].get("population_not_hollowed")
    except (json.JSONDecodeError, TypeError, KeyError):
        hollow = None
    if hollow is True:
        return False, "母體被掏空但 population_not_hollowed=True（門檻沒生效）"
    return rc != 0, f"掏空母體 → CLI exit={rc}，population_not_hollowed={hollow}（必須 exit 非 0）"


def _capture(cmd: list[str], cwd: Path, timeout: int = 180) -> str:
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env[SKIP_PROBES_ENV] = "1"
    try:
        proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                              timeout=timeout, env=env)
    except subprocess.TimeoutExpired:
        return ""
    return proc.stdout or ""


# ----------------------------------------------------------------------
# 主流程
# ----------------------------------------------------------------------

def run_probe(pname: str, delivery: Path) -> dict:
    """執行一支探針，回傳 (是否通過, 說明)。"""
    fn = PROBES.get(pname)
    if fn is None:
        return {"probe": pname, "ok": False, "detail": "探針未註冊"}
    try:
        ok, detail = fn(delivery)  # type: ignore[misc]
    except Exception as exc:  # noqa: BLE001 - 探針爆掉就是探針不可執行
        return {"probe": pname, "ok": False,
                "detail": f"探針執行失敗（不可執行）：{type(exc).__name__}: {exc}"}
    return {"probe": pname, "ok": bool(ok), "detail": detail}


def main() -> int:
    ap = argparse.ArgumentParser(
        description="宣告 ↔ 後果對帳（N/M/K）＋ 檢查器母體揭露檢查")
    ap.add_argument("--delivery", required=True, type=Path, help="交付集合根目錄")
    ap.add_argument("--json", action="store_true", help="以 JSON 輸出")
    ap.add_argument("--skip-probes", action="store_true",
                    help="只做 N/M/K 對帳，不實跑探針（診斷用；正式交付不得使用）")
    args = ap.parse_args()

    delivery: Path = args.delivery
    if not delivery.is_dir():
        print(f"FAIL：交付集合不存在：{delivery}", file=sys.stderr)
        return 2

    try:
        decls = load_declarations(delivery)
    except Exception as exc:  # noqa: BLE001
        print(f"FAIL：無法載入宣告模組：{exc}", file=sys.stderr)
        return 2

    cons = check_consequences(delivery, decls)
    pros = check_probes(decls)
    boundary_violations = check_checkers_declare_boundary(delivery)

    # 探針實跑結果
    probe_results: list[dict] = []
    skip_probes = args.skip_probes or os.environ.get(SKIP_PROBES_ENV) == "1"
    if not skip_probes:
        seen: set[str] = set()
        for d in decls:
            pname = str(getattr(d, "probe", ""))
            if not pname or pname in seen:
                continue
            seen.add(pname)
            probe_results.append(run_probe(pname, delivery))
    probe_by_name = {p["probe"]: p for p in probe_results}

    n = len(decls)
    m = 0
    k_rows: list[dict] = []
    cons_by_id = {c["id"]: c for c in cons["rows"]}
    for p in pros["rows"]:
        c = cons_by_id.get(p["id"], {})
        has_ref = bool(c.get("has_ref"))
        resolved = bool(c.get("resolved"))
        probe_ok = p.get("registered", False)
        if not args.skip_probes and not skip_probes:
            pr = probe_by_name.get(p.get("probe", ""))
            probe_ok = probe_ok and bool(pr and pr.get("ok"))
        if has_ref and resolved and probe_ok:
            m += 1
        else:
            reasons: list[str] = []
            if not has_ref:
                reasons.append("consequence 沒有可解析的『檔案.py:符號()』引用")
            if has_ref and not resolved:
                reasons.append("後果指向的檔案或符號不存在：" +
                               "；".join(c.get("dangling", [])))
            if not p.get("registered"):
                reasons.append(f"探針不可用：{p.get('reason') or p.get('probe')}")
            elif not args.skip_probes:
                pr = probe_by_name.get(p.get("probe", ""), {})
                reasons.append(f"探針實測未通過：{pr.get('detail')}")
            k_rows.append({"id": p["id"], "reasons": reasons})

    k = n - m
    ok = (k == 0) and not boundary_violations
    result = {
        "ok": ok,
        "declaration_reconciliation": {
            "N": n, "M": m, "K": k,
            "K_items": k_rows,
            "consequence_rows": cons["rows"],
            "probe_rows": pros["rows"],
        },
        "probe_results": probe_results,
        "checker_boundary_violations": boundary_violations,
        "population": {
            "declarations": n,
            "checkers_scanned": len(list((delivery / "checks").glob("*.py"))),
        },
        "not_covered": [
            "不驗證探針是否覆蓋了宣告語意的**所有**可能反例（探針是代表性反例，不是窮舉）",
            "不驗證 consequence 文字的語意是否正確（只驗證它指向的實體存在且可執行）",
            "不驗證 checkers/ 以外的檔案是否揭露母體",
        ],
    }

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("=" * 68)
        print("宣告 ↔ 後果對帳")
        print("=" * 68)
        print(f"宣告條數 N = {n}")
        print(f"有可執行後果 M = {m}")
        print(f"宣告了但無後果 K = {k}")
        print("-" * 68)
        for r in probe_results:
            print(f"  [{'OK  ' if r['ok'] else 'FAIL'}] 探針 {r['probe']}：{r['detail']}")
        if k_rows:
            print("-" * 68)
            print(f"FAIL：{k} 條宣告沒有可執行後果：")
            for item in k_rows:
                print(f"  ✗ {item['id']}")
                for rsn in item["reasons"]:
                    print(f"      - {rsn}")
        if boundary_violations:
            print("-" * 68)
            print(f"FAIL：{len(boundary_violations)} 支檢查器沒有揭露母體／未涵蓋維度：")
            for v in boundary_violations:
                print(f"  ✗ {v['file']}：{v['problem']}")
        print("-" * 68)
        if ok:
            print(f"PASS：N={n} / M={m} / K={k}，所有宣告都有可執行後果")
        else:
            print(f"FAIL：N={n} / M={m} / K={k}（K>0 即不可交付）")
        print("母體宣告（本檢查器**看**這些）：")
        print(f"  population: {result['population']}")
        print("本檢查器**不看**這些（not_covered）：")
        for item in result["not_covered"]:
            print(f"  - {item}")
        print("=" * 68)

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
