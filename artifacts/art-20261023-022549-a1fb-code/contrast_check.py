#!/usr/bin/env python3
"""
contrast_check.py — 從 after.html 抽出 CSS token，算 WCAG 對比度並斷言。

為什麼不能用 OKLCH 的 L 直接算？
  今日學習（OKLCH 卡片）：WCAG 2.x 的對比公式定義在 sRGB 相對亮度上
  （0.2126R + 0.7152G + 0.0722B，先做 sRGB gamma 反線性化），
  與 OKLCH 的 L 不是同一個量（OKLCH 的 L 其實更接近 APCA 的 L）。
  所以必須 OKLCH → sRGB → 相對亮度 → 對比度，不能在 OKLCH 空間裡相減。

用法：
    python3 contrast_check.py after.html            # 檢查 after.html
    python3 contrast_check.py after.html --json     # 機器可讀輸出
退出碼：0 = 全部通過，1 = 有斷言失敗。

環境變數：無（不需要金鑰，不需要網路）
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path

# ---------- 色彩轉換：OKLCH → sRGB ----------

def oklch_to_srgb(L: float, C: float, H_deg: float) -> tuple[float, float, float]:
    """OKLCH → Oklab → 線性 sRGB → gamma 編碼 sRGB（0–1 各通道）。

    參照 CSS Color 4 §12：
      a = C * cos(H), b = C * sin(H)
      l_ = L + 0.3963377774*a + 0.2158037573*b
      m_ = L - 0.1055613458*a - 0.0638541728*b
      s_ = L - 0.0894841775*a - 1.2914855480*b
      l = l_^3, m = m_^3, s = s_^3
    """
    h = math.radians(H_deg)
    a = C * math.cos(h)
    b = C * math.sin(h)

    l_ = L + 0.3963377774 * a + 0.2158037573 * b
    m_ = L - 0.1055613458 * a - 0.0638541728 * b
    s_ = L - 0.0894841775 * a - 1.2914855480 * b

    l, m, s = l_ ** 3, m_ ** 3, s_ ** 3

    r = +4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s
    g = -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s
    bl = -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s

    def gamma(x: float) -> float:
        if x <= 0.0031308:
            return 12.92 * x
        return 1.055 * (x ** (1 / 2.4)) - 0.055

    return gamma(r), gamma(g), gamma(bl)


def srgb_relative_luminance(r: float, g: float, b: float) -> float:
    """WCAG 2.x 相對亮度：先把 gamma 編碼值反線性化，再加權。"""
    def lin(c: float) -> float:
        if c <= 0.04045:
            return c / 12.92
        return ((c + 0.055) / 1.055) ** 2.4

    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)


def contrast_ratio(c1: tuple[float, float, float], c2: tuple[float, float, float]) -> float:
    l1 = srgb_relative_luminance(*c1)
    l2 = srgb_relative_luminance(*c2)
    hi, lo = max(l1, l2), min(l1, l2)
    return (hi + 0.05) / (lo + 0.05)


# ---------- token 解析 ----------

OKLCH_RE = re.compile(
    r"oklch\(\s*([\d.]+)(%?)\s+([\d.]+)\s+([\d.]+)\s*\)"
)
# ★ 踩坑：原本用 oklch\([^;]+\)，`[^;]+` 會一路吃到下一個分號，
#   導致 `--surface-1: #ffffff; ... --state-good-bg: oklch(…)` 被誤認為一個
#   oklch 宣告。改成「只允許 oklch() 內的字元」：[^;()]*，遇到右括號就停。
VAR_RE = re.compile(r"--([\w-]+)\s*:\s*(oklch\([^;()]*\))")
COMMENT_RE = re.compile(r"/\*.*?\*/", re.S)


def build_view(html: str, theme: str) -> dict[str, tuple[float, float, float, float, float]]:
    """把所有 CSS 自訂屬性解析成統一檢視表 {name: (L, C, H, r, g, b)}。

    解析順序（★ 這是踩過的坑）：
      1. 先收集「字面定義」：oklch(...) 或 #hex（L/C/H 對 hex 來源為 NaN）
      2. 再收集「別名定義」：var(--other)（鏈式引用，最多解 8 層防循環）
      3. 逐個別名解析回字面值

    ★ 踩坑記錄：原本把 oklch 與 hex 拆成兩個獨立解析器，各自做 alias 解析，
      導致 `--text-primary: var(--p-neutral-900)`（oklch 別名）在 hex 解析器裡
      找不到落點而回傳 None，亮色模式 12 項檢查全部 SKIP —— 檢查通過了，
      但其實一個都沒檢查。這就是「靜默跳過」最危險的形狀：綠燈是假的。
    """
    scope = _theme_scope(html, theme)

    literals: dict[str, tuple[float, float, float, float, float]] = {}
    for name, expr in VAR_RE.findall(scope):
        m = OKLCH_RE.search(expr)
        if not m:
            continue
        L_raw, pct, C, H = m.groups()
        L = float(L_raw) / 100 if pct else float(L_raw)
        C, H = float(C), float(H)
        literals[name] = (L, C, H, *oklch_to_srgb(L, C, H))

    for name, hexv in re.findall(r"--([\w-]+)\s*:\s*(#[0-9a-fA-F]{3,8})\b", scope):
        h = hexv if len(hexv) == 7 else "#" + "".join(c * 2 for c in hexv[1:])
        r, g, b = (int(h[1:3], 16) / 255, int(h[3:5], 16) / 255, int(h[5:7], 16) / 255)
        literals.setdefault(name, (float("nan"), float("nan"), float("nan"), r, g, b))

    aliases = {
        m.group(1): m.group(2)
        for m in re.finditer(r"--([\w-]+)\s*:\s*var\(\s*(--[\w-]+)\s*\)", scope)
    }

    resolved: dict[str, tuple[float, float, float, float, float]] = {}

    def resolve(name: str, depth: int = 0):
        # ★ 踩坑：別名解析結果必須寫回 resolved，否則最後的成員檢查
        #   會把「已成功解析的別名」誤判為「未定義」。
        if name in resolved:
            return resolved[name]
        if name in literals:
            resolved[name] = literals[name]
            return literals[name]
        if name in aliases and depth < 8:
            value = resolve(aliases[name][2:], depth + 1)
            if value is not None:
                resolved[name] = value
            return value
        return None

    # 逐一把「所有已知的 token 名稱」解析並寫回 resolved。
    # ★ 踩坑：原本只對 aliases 呼叫 resolve()，導致純字面值 token
    #   （如 --surface-1: #ffffff、--state-good-bg: oklch(…)）從未進入
    #   resolved，最後的成員檢查就把它们誤判為「未定義」。
    for name in list(literals) + list(aliases):
        resolve(name)

    missing = [fg for fg, bg, *_ in CHECKS if fg not in resolved] + \
              [bg for fg, bg, *_ in CHECKS if bg not in resolved]
    if missing:
        raise ValueError(
            f"[{theme}] 無法解析 token: {sorted(set(missing))}；"
            f"已解析 {len(resolved)} 個。請檢查是否為 var() 引用鏈未閉合或拼字錯誤。"
        )
    return resolved


def _theme_scope(html: str, theme: str) -> str:
    """切出指定主題的區塊字串。"""
    if theme == "dark":
        start = html.find('[data-theme="dark"]')
        if start == -1:
            raise ValueError("找不到 [data-theme=\"dark\"] 區塊")
        return _brace_block(html, start)
    # light：移除 dark 區塊後掃描其餘（涵蓋 :root 與 :root,[data-theme=light]）
    start = html.find('[data-theme="dark"]')
    if start != -1:
        block = _brace_block(html, start)
        html = html.replace(block, "")
    return html


def _brace_block(html: str, start: int) -> str:
    i = html.index("{", start)
    depth, j = 0, i
    while j < len(html):
        if html[j] == "{":
            depth += 1
        elif html[j] == "}":
            depth -= 1
            if depth == 0:
                return html[i:j + 1]
        j += 1
    raise ValueError(f"從位置 {start} 起的區塊大括號未閉合")


def hex_str(rgb: tuple[float, float, float]) -> str:
    return "#" + "".join(f"{max(0, min(255, round(c * 255))):02X}" for c in rgb)


def to_rgb(entry):
    _, _, _, r, g, b = entry
    return (r, g, b)


# ---------- 檢查組合 ----------

# (前景 token, 背景 token, 最低比值, 說明, 門檻類型)
CHECKS = [
    ("text-primary", "surface-1", 4.5, "正文對卡片背景（WCAG AA 正文）", "normal"),
    ("text-primary", "surface-0", 4.5, "正文對頁面背景（WCAG AA 正文）", "normal"),
    ("text-secondary", "surface-1", 4.5, "次要文字對卡片背景（WCAG AA 正文）", "normal"),
    ("text-secondary", "surface-0", 4.5, "次要文字對頁面背景（WCAG AA 正文）", "normal"),
    ("text-primary", "surface-2", 4.5, "斑馬紋列上的正文（zebra row）", "normal"),
    ("accent", "surface-1", 4.5, "強調色文字對卡片背景", "normal"),
    ("text-on-accent", "accent", 4.5, "按鈕文字對強調色底", "normal"),
    ("state-good", "state-good-bg", 4.5, "達標徽章文字對其底色", "normal"),
    ("state-warn", "state-warn-bg", 4.5, "觀察徽章文字對其底色", "normal"),
    ("state-bad", "state-bad-bg", 4.5, "超標徽章文字對其底色", "normal"),
    ("border-default", "surface-1", 3.0, "輸入框/分隔線對卡片（非文字 UI WCAG AA）", "nontext"),
    ("border-strong", "surface-1", 3.0, "表格格線對卡片（非文字 UI）", "nontext"),
    # ★ 2026-10-23 新增：狀態選擇器上的文字疊色。
    # 這組原本漏測，導致 .nav-item.active 實測 4.11:1（AA 需 4.5）被 24/24 PASS 掩蓋。
    # 教訓：清單式驗證給的是「已列項目全過」，不是「全部符合」——
    #       每加一個 :hover / .active / [aria-selected] 的反色組合，就必須補一條。
    ("accent-on-subtle", "accent-subtle", 4.5, "選取中 nav 文字對其底色（狀態選擇器）", "normal"),
    ("text-primary", "accent-subtle", 4.5, "選取中 nav 區域的一般文字", "normal"),
    ("border-strong", "surface-2", 3.0, "內層 surface 上的格線", "nontext"),
]

# 明確禁止的東西（今日學習：不要純黑 / 不要原色）
BANNED_SUBSTRINGS = {
    "filter: invert(1)": "暗色模式不得用 filter: invert(1)（語意色語義會倒轉）",
    "#22c55e": "純綠原色被使用者明文拒絕，應用低彩度 OKLCH",
    "#ef4444": "純紅原色被使用者明文拒絕，應用低彩度 OKLCH",
    "#3b82f6": "純藍原色被使用者明文拒絕，應用低彩度 OKLCH",
    "#000000": "不得使用純黑基底（應用帶色調深灰，如 oklch(0.17 …)）",
    "#000": "不得使用純黑基底（應用帶色調深灰，如 oklch(0.17 …)）",
}


def check_theme(html: str, theme: str) -> dict:
    view = build_view(html, theme)
    results, failures = [], 0

    for fg, bg, min_ratio, why, kind in CHECKS:
        if fg not in view or bg not in view:
            missing = fg if fg not in view else bg
            results.append({"fg": fg, "bg": bg, "status": "SKIP", "why": why,
                            "reason": f"token {missing} 未在此主題定義"})
            failures += 1
            continue
        ratio = contrast_ratio(to_rgb(view[fg]), to_rgb(view[bg]))
        ok = ratio >= min_ratio
        results.append({
            "fg": fg, "bg": bg,
            "fg_hex": hex_str(to_rgb(view[fg])),
            "bg_hex": hex_str(to_rgb(view[bg])),
            "ratio": round(ratio, 2), "min": min_ratio, "kind": kind,
            "status": "PASS" if ok else "FAIL", "why": why,
        })
        if not ok:
            failures += 1

    # gamut 檢查只對 oklch() 來源有效（hex 來源 L/C/H 是 NaN）
    oog = []
    for name, entry in view.items():
        L, C, H, r, g, b = entry
        if L != L:  # NaN → hex 來源，跳過
            continue
        if not all(-1e-4 <= v <= 1 + 1e-4 for v in (r, g, b)):
            oog.append({"token": name,
                        "computed": hex_str((max(0, r), max(0, g), max(0, b)))})

    dark_base_not_black = None
    if "surface-0" in view:
        r, g, b = to_rgb(view["surface-0"])
        dark_base_not_black = not (r < 0.02 and g < 0.02 and b < 0.02)

    return {"theme": theme, "tokens": len(view), "checks": results,
            "out_of_gamut": oog, "surface0_not_pure_black": dark_base_not_black,
            "failures": failures,
            "pass": sum(1 for r in results if r["status"] == "PASS")}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("html", type=Path)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--strict-gamut", action="store_true",
                    help="任何超出 sRGB gamut 的 token 都視為失敗")
    args = ap.parse_args()

    raw = args.html.read_text(encoding="utf-8")
    # ★ 先剝掉 CSS 註解，否則註解裡提到的反面寫法會被誤判成命中
    html = COMMENT_RE.sub("", raw)

    themes = [check_theme(html, "light"), check_theme(html, "dark")]

    # --- 禁用字串掃描（對去掉註解後的 HTML） ---
    banned_hits = []
    for needle, why in BANNED_SUBSTRINGS.items():
        if needle in html:
            banned_hits.append({"pattern": needle, "reason": why})

    total_fail = sum(t["failures"] for t in themes)
    all_oog = [o for t in themes for o in t["out_of_gamut"]]
    verdict = "PASS" if total_fail == 0 and not banned_hits and not all_oog else "FAIL"

    payload = {
        "file": str(args.html),
        "themes": themes,
        "banned_patterns_hit": banned_hits,
        "summary": {
            "total": sum(len(t["checks"]) for t in themes),
            "pass": sum(t["pass"] for t in themes),
            "fail": total_fail,
            "out_of_gamut": len(all_oog),
            "verdict": verdict,
        },
    }

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"== 對比度檢查：{args.html} ==")
        for t in themes:
            print(f"\n-- 主題：{t['theme']}（{t['tokens']} 個 token）--")
            for r in t["checks"]:
                if r["status"] == "SKIP":
                    print(f"  SKIP  {r['fg']} / {r['bg']}  — {r['reason']}")
                    continue
                mark = "OK  " if r["status"] == "PASS" else "FAIL"
                print(f"  {mark}  {r['ratio']:>5.2f}:1  (需 ≥{r['min']})  "
                      f"{r['fg_hex']} on {r['bg_hex']}  — {r['why']}")
            if t["out_of_gamut"]:
                print(f"  ⚠ out-of-gamut（clipping 會偏移色相）: {len(t['out_of_gamut'])} 個")
                for o in t["out_of_gamut"]:
                    print(f"      {o['token']} → {o['computed']}")
            if t["surface0_not_pure_black"] is False:
                print("  ✗ 暗色基底是純黑")
        if banned_hits:
            print(f"\n  ✗ 禁用寫法命中 {len(banned_hits)} 處:")
            for b in banned_hits:
                print(f"      {b['pattern']} — {b['reason']}")
        s = payload["summary"]
        print(f"\n  {s['pass']}/{s['total']} 通過 → {s['verdict']}")

    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())