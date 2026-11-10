#!/usr/bin/env python3
"""自評缺陷敘述回算：敘述裡宣稱存在的東西，必須真的存在於產物中。

這支腳本是 **code SOP §24（敘述層也要能被驗證）** 的機械實作，
也是 2026-11-10 學習卡「自評缺陷敘述必須對得上產物」的落地機制。

病根（11-09 的實測）
---------------------
自評裡寫「第 7 頁時程表逐月列出 11 個節點」，
但第 7 頁實際上是「方案甲 820,000,000 元，分為三項續辦工作」——
**沒有時程表、沒有 11 個節點、沒有逐月**。

這個錯誤的自評不是無害的：下一輪會把它當成真缺陷去修，
而且修正會往錯誤方向走。它比「沒有自評」更糟，
因為它讓修正動作有一個錯誤的目標。

機制（兩層）
------------
1. **結構化 claims**（`--claims` 指向的 JSON）：
   每條 claim 的敘述中出現的**數字**與**定位語**（第 N 頁/列/步驟）
   都必須能在 corpus 裡找到對應。

2. **敘述檔的金額型數字漂移**（`--narrative` 指向的檔）：
   敘述檔裡出現的**金額型數字**（兩位小數或含千分位的數）
   必須能在 corpus 裡找到，否則就是「敘述裡有、產物裡沒有」。

   為什麼只查金額型數字、不查所有整數：
   整數型計數（檔案數、測試數）在敘述裡常帶修飾語（「8 個檔案」），
   機械比對的假陽性高；它們由第 1 層的結構化 claims 覆蓋。
   金額型數字則是**靜默錯了最慘**的一類（等式差一個小數點沒人看得出來）。

退出碼
------
    0 = 所有宣稱都能在產物中找到對應
    1 = 有宣稱找不到對應（印出該 claim 與找不到的 token）
    2 = claims 檔或 corpus 無法讀取
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

#: 本檢查器**看**的母體（module-level 常數 → 可被 AST 機械解析）。
#:
#: 為什麼寫成常數而不是寫在 docstring：docstring 不可被機械解析成結構化欄位，
#: 「宣告要揭露」但沒有可檢查的形式 = 跟沒有一樣（11-11 的實測結論）。
POPULATION = (
    "結構化 claims JSON 內的每一條 claim（含其 must_find 清單），"
    "以及 --narrative 指定的每個敘述檔（做金額型數字漂移掃描）"
)

#: 本檢查器**不看**的維度（誠實揭露，不得用沉默代替）。
NOT_COVERED = [
    "不驗證敘述的語意是否成立（只驗證宣稱存在的東西真的存在）",
    "不驗證整數型計數（檔案數、測試數）——那些由結構化 claims 覆蓋",
    "不驗證非金額型數字（版本號、秒數、百分比）的敘述對應",
    "不驗證 claims JSON 本身涵蓋了該揭露的每一件事（母體由呼叫端給定，不是本檢查器推導）",
]

#: 定位語：第 N 頁／列／步驟／項／筆。宣稱「在第 N 頁有 X」時，
#: corpus 必須真的出現「第 N」這個定位。
LOCATOR_RE = re.compile(r"第\s*(\d+)\s*(頁|列|步驟|項|筆|條|張|支)")

#: 金額型數字：兩位小數或含千分位。
#: 刻意排除：版本號（1.19.0）、秒數（2.38s）、百分比（28.5%）。
MONEY_RE = re.compile(r"(?<![\w.])-?\d{1,3}(?:,\d{3})*(?:\.\d{2})(?![\d%a-zA-Z])")

#: 整數型計數：兩位數以上。單一數字（0/1/2）不做檢查——它太常出現於
#: 步驟編號、條號、層級，機械比對會淹在假陽性裡。
COUNT_RE = re.compile(r"(?<![\w.\-])\d{2,}(?![\d.%a-zA-Z])")


def _norm(text: str) -> str:
    """正規化：去掉千分位與空白，讓 79194.50 與 79,194.50 視為同一個。"""
    return text.replace(",", "").replace(" ", "").replace("　", "")


def _money_tokens(text: str) -> list[str]:
    return [m.group(0) for m in MONEY_RE.finditer(text)]


def _count_tokens(text: str) -> list[str]:
    """整數型計數。只取 2 位數以上，且排除被小數／百分號黏住的。"""
    return [m.group(0) for m in COUNT_RE.finditer(text)]


def _locator_tokens(text: str) -> list[str]:
    return [m.group(0) for m in LOCATOR_RE.finditer(text)]


def load_corpus(paths: list[Path]) -> str:
    """把多個 corpus 檔案合併成一段可檢索的文字。"""
    chunks: list[str] = []
    for p in paths:
        try:
            chunks.append(p.read_text(encoding="utf-8"))
        except OSError as exc:
            raise FileNotFoundError(f"corpus 檔案無法讀取：{p}：{exc}") from exc
    return "\n".join(chunks)


def check_claims(claims: list[dict], corpus: str) -> list[dict]:
    """逐條檢查結構化 claims。回傳違規清單。"""
    corpus_n = _norm(corpus)
    violations: list[dict] = []
    for c in claims:
        text = str(c.get("text", ""))
        cid = str(c.get("id", "(無 id)"))
        tokens: list[str] = []
        tokens.extend(_money_tokens(text))
        tokens.extend(_count_tokens(text))
        tokens.extend(_locator_tokens(text))
        # 明確指定要出現的字串（不從敘述推導）
        for literal in c.get("must_find", []) or []:
            tokens.append(str(literal))
        missing = []
        for tok in tokens:
            if _norm(tok) not in corpus_n:
                missing.append(tok)
        if missing:
            violations.append({
                "id": cid,
                "text": text,
                "missing": missing,
            })
    return violations


def check_narrative_drift(paths: list[Path], corpus: str) -> list[dict]:
    """檢查敘述檔的金額型數字是否都能在 corpus 找到。回傳違規清單。"""
    corpus_n = _norm(corpus)
    violations: list[dict] = []
    for p in paths:
        try:
            text = p.read_text(encoding="utf-8")
        except OSError as exc:
            raise FileNotFoundError(f"敘述檔無法讀取：{p}：{exc}") from exc
        for lineno, line in enumerate(text.splitlines(), start=1):
            for tok in _money_tokens(line):
                if _norm(tok) not in corpus_n:
                    violations.append({
                        "file": p.name,
                        "line": lineno,
                        "missing": [tok],
                        "text": line.strip()[:160],
                    })
    return violations


def main() -> int:
    ap = argparse.ArgumentParser(
        description="自評缺陷敘述回算：宣稱存在的東西必須真的存在於產物中")
    ap.add_argument("--claims", required=True, type=Path,
                    help="結構化 claims JSON（{'claims': [{'id','text','must_find'}]}）")
    ap.add_argument("--corpus", required=True, nargs="+", type=Path,
                    help="產物文字流（可多個檔案）")
    ap.add_argument("--narrative", nargs="*", default=[], type=Path,
                    help="要接受金額型數字漂移掃描的敘述檔")
    ap.add_argument("--json", action="store_true", help="以 JSON 輸出結果")
    args = ap.parse_args()

    if not args.claims.exists():
        print(f"FAIL：claims 檔不存在：{args.claims}", file=sys.stderr)
        return 2

    try:
        raw = json.loads(args.claims.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        print(f"FAIL：claims 檔無法解析：{exc}", file=sys.stderr)
        return 2

    claims = raw.get("claims", []) if isinstance(raw, dict) else raw
    if not isinstance(claims, list):
        print("FAIL：claims 檔格式錯誤：應為 {'claims': [...]} 或 [...]", file=sys.stderr)
        return 2

    try:
        corpus = load_corpus(args.corpus)
    except FileNotFoundError as exc:
        print(f"FAIL：{exc}", file=sys.stderr)
        return 2

    claim_violations = check_claims(claims, corpus)
    drift_violations = check_narrative_drift(args.narrative, corpus) if args.narrative else []

    total = len(claim_violations) + len(drift_violations)
    population = {
        "claims_checked": len(claims),
        "narrative_files_scanned": len(args.narrative),
        "corpus_files": len(args.corpus),
    }
    not_covered = [
        "不驗證敘述的語意是否成立（只驗證宣稱存在的東西真的存在）",
        "不驗證整數型計數（檔案數、測試數）——那些由結構化 claims 覆蓋",
        "不驗證非金額型數字（版本號、秒數、百分比）的敘述對應",
    ]

    if args.json:
        print(json.dumps({
            "ok": total == 0,
            "population": population,
            "not_covered": not_covered,
            "claim_violations": claim_violations,
            "narrative_drift": drift_violations,
        }, ensure_ascii=False, indent=2))
    else:
        print("=" * 68)
        print("自評缺陷敘述回算")
        print("=" * 68)
        print(f"claims 條數      : {population['claims_checked']}")
        print(f"敘述檔掃描        : {population['narrative_files_scanned']}")
        print(f"corpus 檔案數     : {population['corpus_files']}")
        print("-" * 68)
        if total == 0:
            print("PASS：所有宣稱都能在產物中找到對應")
        else:
            print(f"FAIL（{total} 項）：")
            for v in claim_violations:
                print(f"  ✗ [{v['id']}] {v['text']}")
                print(f"      產物中找不到：{v['missing']}")
            for v in drift_violations:
                print(f"  ✗ {v['file']} 第 {v['line']} 行：{v['text']}")
                print(f"      產物中找不到：{v['missing']}")
        print("-" * 68)
        print("母體宣告（本檢查器**看**這些）：")
        print(f"  population: {population}")
        print("本檢查器**不看**這些（not_covered）：")
        for item in not_covered:
            print(f"  - {item}")
        print("=" * 68)

    return 0 if total == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
