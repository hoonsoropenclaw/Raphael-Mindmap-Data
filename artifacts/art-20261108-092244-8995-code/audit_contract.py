#!/usr/bin/env python3
"""audit_contract.py — 依 SPEC.md 檢查簡報契約缺陷。

用法：
    python3 audit_contract.py <fixture.json> [--out findings.json]

結束碼：0 = 無發現、1 = 有發現、2 = 執行錯誤。
規則全部以 SPEC.md 為準，不得綁定任何特定頁面 id、數字或來源字串。
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

EXIT_OK, EXIT_FINDINGS, EXIT_ERROR = 0, 1, 2

# 「90 秒」「2 分鐘」「1.5 分鐘」「二秒」——只認秒／分鐘，避免「分成三部分」誤判
TIME_RE = re.compile(r"(?:\d+(?:\.\d+)?|[零一二三四五六七八九十百兩]+)\s*(?:秒|分鐘)")
# 「已驗算」「已核對」「已確認」
CLAIM_RE = re.compile(r"已(?:經)?(?:驗算|核對|確認)")
# 括號內的單位
AXIS_UNIT_RE = re.compile(r"[（(]\s*([^）)]+?)\s*[）)]")
# 數字＋單位，例如「3 億」「8.2 億」「42 件」
NUM_UNIT_RE = re.compile(r"\d[\d,]*(?:\.\d+)?\s*([^\d\s，,。、；;:：%％]+)")

# SPEC.md §2 列出的同義詞組
SYNONYM_GROUPS = [("校舍", "校園"), ("安東", "Anton"), ("資料", "數據"), ("公文", "文書")]


def die(msg: str) -> int:
    print(f"audit_contract: 錯誤：{msg}", file=sys.stderr)
    return EXIT_ERROR


def normalize_text(s: str) -> str:
    return unicodedata.normalize("NFKC", s or "")


def normalize_source(s: str) -> str:
    """正規化來源字串：去括號內容、日期、空白與標點差異。"""
    t = normalize_text(s)
    t = re.sub(r"[（(][^）)]*[）)]", "", t)
    t = re.sub(r"\d{2,4}[/-]\d{1,2}[/-]\d{1,2}", "", t)
    t = re.sub(r"[\s　]+", "", t)
    t = t.replace("：", ":").replace("，", ",").replace("、", ",")
    t = t.replace("「", "").replace("」", "")
    t = re.sub(r"發布$", "", t)
    return t.strip()


def axis_unit(chart: dict) -> str:
    m = AXIS_UNIT_RE.search(normalize_text(chart.get("axis_label", "")))
    return m.group(1).strip() if m else ""


def chart_units(chart: dict) -> set[str]:
    units: set[str] = set()
    for key in ("ticks", "value_labels"):
        for raw in chart.get(key) or []:
            m = NUM_UNIT_RE.search(normalize_text(str(raw)))
            if m:
                units.add(m.group(1).strip())
    return units


def slide_text(slide: dict) -> str:
    parts = [str(slide.get("title", "")), str(slide.get("notes", "")),
             str(slide.get("footer", ""))]
    chart = slide.get("chart")
    if isinstance(chart, dict):
        parts.append(str(chart.get("footer", "")))
        parts.append(str(chart.get("axis_label", "")))
    return "\n".join(parts)


def find_defects(slide: dict) -> list[dict]:
    sid = slide.get("id")
    fields = slide.get("fields") if isinstance(slide.get("fields"), dict) else {}
    chart = slide.get("chart") if isinstance(slide.get("chart"), dict) else None
    notes = normalize_text(str(slide.get("notes", "")))
    title = normalize_text(str(slide.get("title", "")))
    out: list[dict] = []

    # 1) unit_mismatch：軸標題單位 vs 刻度／數值標籤單位
    if chart:
        au = axis_unit(chart)
        used = chart_units(chart)
        if au and used and au not in used:
            out.append({
                "slide_id": sid, "category": "unit_mismatch",
                "evidence": f"{chart.get('axis_label')} / ticks={chart.get('ticks')} / "
                            f"value_labels={chart.get('value_labels')}",
            })

    # 2) duplicate_source：同一來源在圖內 footer 與頁尾各宣告一次
    if chart:
        cf = normalize_source(str(chart.get("footer", "")))
        sf = normalize_source(str(slide.get("footer", "")))
        if cf and sf and cf == sf:
            out.append({
                "slide_id": sid, "category": "duplicate_source",
                "evidence": f"chart.footer={chart.get('footer')} | slide.footer={slide.get('footer')}",
            })

    # 3) missing_time_budget：講者備註沒有時間配額
    if not TIME_RE.search(notes):
        out.append({
            "slide_id": sid, "category": "missing_time_budget",
            "evidence": f"notes={slide.get('notes')}",
        })

    # 4) unverified_claim：宣稱已驗算但沒有驗算憑證欄位
    claim_txt = f"{notes}\n{title}"
    if CLAIM_RE.search(claim_txt) and not (
            fields.get("verified_total") and fields.get("verified_by")):
        out.append({
            "slide_id": sid, "category": "unverified_claim",
            "evidence": f"notes={slide.get('notes')} fields={fields}",
        })

    # 5) terminology_drift：同頁並存同義詞兩種說法，且沒有 disambiguation
    text = slide_text(slide)
    for a, b in SYNONYM_GROUPS:
        if a in text and b in text and not fields.get("disambiguation"):
            out.append({
                "slide_id": sid, "category": "terminology_drift",
                "evidence": f"title={slide.get('title')} notes={slide.get('notes')}",
            })
            break

    out.sort(key=lambda d: d["category"])
    return out


def load_fixture(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"找不到輸入檔：{path}")
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as e:
        raise OSError(f"無法讀取輸入檔 {path}：{e}") from e
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"輸入檔 {path} 不是合法 JSON：{e}") from e
    if not isinstance(data, dict):
        raise ValueError(f"輸入檔 {path} 的最上層必須是物件，實際是 {type(data).__name__}")
    slides = data.get("slides")
    if not isinstance(slides, list):
        raise ValueError(f"輸入檔 {path} 的欄位 'slides' 必須是陣列，"
                         f"實際是 {type(slides).__name__}")
    for i, s in enumerate(slides):
        if not isinstance(s, dict):
            raise ValueError(f"輸入檔 {path} 的 slides[{i}] 必須是物件")
        if not isinstance(s.get("id"), str) or not s.get("id"):
            raise ValueError(f"輸入檔 {path} 的 slides[{i}] 缺少字串欄位 'id'")
    return data


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="依 SPEC.md 檢查簡報契約缺陷")
    ap.add_argument("fixture", help="輸入 JSON 檔")
    ap.add_argument("--out", default=None, help="另外把結果寫到這個檔")
    a = ap.parse_args(argv)

    try:
        data = load_fixture(Path(a.fixture))
    except (FileNotFoundError, OSError, ValueError) as e:
        return die(str(e))

    findings: list[dict] = []
    for slide in data["slides"]:
        findings.extend(find_defects(slide))
    findings.sort(key=lambda d: (str(d["slide_id"]), d["category"]))

    payload = {"findings": findings}
    text = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)
    print(text)
    if a.out:
        try:
            Path(a.out).write_text(text + "\n", encoding="utf-8")
        except OSError as e:
            return die(f"無法寫出結果檔 {a.out}：{e}")
    return EXIT_FINDINGS if findings else EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
