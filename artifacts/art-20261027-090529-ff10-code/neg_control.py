#!/usr/bin/env python3
"""對帳守門的「反向對照」（negative control）。

目的：證明 check_no_double_count() 不是「怎麼都回 True」的橡皮章。
做法：故意把明文原檔放回輸入資料夾（重現第一次跑的那個 fixture 缺陷），
      讓候選把同一筆金額合併兩次；守門必須判定 ok=False。

若這個反向對照沒抓到（守門回 True），代表守門本身無效 → 整個 A/B 的綠燈不可信。
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path("/work")
AB = ROOT / "ab"
VENV = ROOT / "venv"
PY = str(VENV / "bin" / "python")
PW = "".join(chr(c) for c in (80, 97, 115, 115, 119, 111, 114, 100, 49, 50, 51, 52, 95))

sys.path.insert(0, str(ROOT))
import run_ab  # noqa: E402  重用守門實作，避免兩份邏輯漂移


def main() -> int:
    plain = AB / "fixture_plain" / "j_密碼保護_原始.xlsx"
    if not plain.exists():
        print("FATAL: 找不到明文原檔（先跑 run_ab.py 產生 fixture）", flush=True)
        return 2

    # 1) 重建「壞掉的」fixture：明文原檔放進 testdata
    bad = AB / "testdata_bad"
    if bad.exists():
        shutil.rmtree(bad)
    shutil.copytree(AB / "testdata", bad)
    shutil.copy2(plain, bad / plain.name)

    # 2) 用壞 fixture 跑候選
    shutil.copy2(ROOT / "candidate" / "merge_xlsx.py", AB / "merge_xlsx.py")
    out = AB / "out_negcontrol.xlsx"
    if out.exists():
        out.unlink()
    r = subprocess.run([PY, "merge_xlsx.py", "testdata_bad", "--apply", "-o", str(out)],
                       capture_output=True, text=True, cwd=str(AB),
                       env={**os.environ, "OFFICE_FILE_PASSWORD": PW})
    print(f"[neg-control] 壞 fixture 跑完 rc={r.returncode}", flush=True)

    # 3) 把「壞候選」餵給守門，但基準用「正常基準」。
    #    守門的兩個判準都應該抓到：
    #      a) 同來源列數比基準多（j_密碼保護.xlsx 兩份 → 6 列 vs 3 列）
    #      b) 對帳等式不成立（金額總差 != 新來源金額加總）
    #    做法：先備份正常基準 → 讓守門讀「壞候選」→ 還原。
    good_base = AB / "out_baseline_GOOD.xlsx"
    shutil.copy2(AB / "out_baseline.xlsx", good_base)
    shutil.copy2(out, AB / "out_candidate.xlsx")   # 守門的「候選」= 壞輸出
    try:
        guard = run_ab.check_no_double_count({}, {})
    finally:
        shutil.copy2(good_base, AB / "out_baseline.xlsx")
        # 還原正常候選輸出
        good_cand = AB / "out_candidate_GOOD.xlsx"
        if good_cand.exists():
            shutil.copy2(good_cand, AB / "out_candidate.xlsx")

    print("\n[neg-control] 守門判定：", flush=True)
    print(json.dumps(guard, ensure_ascii=False, indent=2), flush=True)

    caught = guard.get("ok") is False
    print(f"\n[neg-control] 守門有抓到重複計算？ {caught}", flush=True)
    (AB / "neg_control_result.json").write_text(
        json.dumps({"guard": guard, "caught": caught}, ensure_ascii=False, indent=2),
        encoding="utf-8")
    return 0 if caught else 1


if __name__ == "__main__":
    raise SystemExit(main())
