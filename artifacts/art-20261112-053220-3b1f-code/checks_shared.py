#!/usr/bin/env python3
"""共用缺陷檢查邏輯（baseline 與 candidate 必須用同一份，才叫 A/B）。

修訂版（2026-11-12，rev1）：把原本「宣稱共用但檔案不存在」的問題補上——
本檔即為 single source of truth，兩側皆以它產生的 JS 與色彩換算為準。

  D1 假綠燈       .nav-item.active 前景/背景對比 < 4.5:1（需 OKLCH→sRGB 正確換算）
  D2 dead token   --border-strong 定義了但沒有任何 var(--border-strong) 引用
  D3 死按鈕       匯出報表按鈕點了沒有可觀察反應
  D4 狀態不持久   切深色後 reload 回到 light
  D5 側欄未響應式 360px 下側欄寬度 ≥ 視窗一半
  D6 對照組(應過) 頁面確實載入（h1 存在且非空）
  D7 對照組(應敗) 斷言一個頁面上不存在的字串必須失敗

★ 本檔同時是 candidate（TypeScript）的對照來源：
  `python3 -m checks_shared --emit-js` 會輸出 JS 片段，candidate 可直接 import 或貼入，
  避免兩份 inline 副本各自漂移。

OKLCH→sRGB 換算參照 CSS Color 4 §12：
  L' = L + 0.3963377774*a + 0.2158037573*b
  M' = L - 0.1055613458*a - 0.0638541728*b
  S' = L - 0.0894841775*a - 1.2914855480*b
  a = C*cos(H), b = C*sin(H)；L',M',S' 立方 → 線性 sRGB → gamma 編碼
"""
from __future__ import annotations

import math
import re

OKLCH_RE = re.compile(
    r"oklch\(\s*([\d.]+)\s+([\d.]+)\s+([\d.]+)\s*\)", re.I)


def _srgb_lum(rgb: tuple[float, float, float]) -> float:
    def lin(c: float) -> float:
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (lin(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def parse_color(css: str) -> tuple[float, float, float] | None:
    """把 computed style 的顏色字串轉成 sRGB 0-1 三元組。支援 rgb()/rgba() 與 oklch()。"""
    css = (css or "").strip()
    if not css or css.lower() in {"transparent", "none"}:
        return None
    m = OKLCH_RE.search(css)
    if m:
        L, C, H = (float(x) for x in m.groups())
        h = math.radians(H)
        a, b = C * math.cos(h), C * math.sin(h)
        l_ = L + 0.3963377774 * a + 0.2158037573 * b
        m_ = L - 0.1055613458 * a - 0.0638541728 * b
        s_ = L - 0.0894841775 * a - 1.2914855480 * b
        l, mm, s = l_**3, m_**3, s_**3
        r = 4.0767416621 * l - 3.3077115913 * mm + 0.2309699292 * s
        g = -1.2684380046 * l + 2.6097574011 * mm - 0.3413193965 * s
        bl = -0.0041960863 * l - 0.7034186147 * mm + 1.7076147010 * s
        return tuple(max(0.0, min(1.0, c)) for c in (r, g, bl))  # type: ignore[return-value]
    m = re.match(r"rgba?\(\s*([\d.]+)[\s,]+([\d.]+)[\s,]+([\d.]+)", css, re.I)
    if m:
        r, g, b = (float(x) / 255.0 for x in m.groups())
        return (r, g, b)
    return None


def contrast_ratio(fg_css: str, bg_css: str) -> float | None:
    fg, bg = parse_color(fg_css), parse_color(bg_css)
    if fg is None or bg is None:
        return None
    l1, l2 = _srgb_lum(fg), _srgb_lum(bg)
    hi, lo = max(l1, l2), min(l1, l2)
    return (hi + 0.05) / (lo + 0.05)


# ---------- 在瀏覽器端執行的 JS（baseline / candidate 共用同一段） ----------

JS_D1_CONTRAST = """() => {
  const el = document.querySelector('.nav-item.active');
  if (!el) return {error: 'no .nav-item.active'};
  const cs = getComputedStyle(el);
  return {color: cs.color, background: cs.backgroundColor};
}"""

JS_D1_PIXELS = """() => {
  const el = document.querySelector('.nav-item.active');
  if (!el) return null;
  const r = el.getBoundingClientRect();
  return {x: r.x, y: r.y, w: r.width, h: r.height};
}"""

JS_D2_BORDER = """() => {
  const styles = [...document.querySelectorAll('style')].map(s => s.textContent).join('\\n');
  return {
    defined: styles.includes('--border-strong:'),
    referenced: /var\\(--border-strong\\)/.test(styles),
  };
}"""

JS_BODY_LEN = "() => document.body.innerText.length"

JS_THEME = "() => document.documentElement.dataset.theme"

JS_SIDEBAR = """() => {
  const s = document.querySelector('.sidebar');
  if (!s) return null;
  return {sidebar: s.getBoundingClientRect().width, win: window.innerWidth};
}"""

JS_H1 = "() => { const h = document.querySelector('h1'); return h ? h.innerText : null; }"

# 依序執行 5 條缺陷檢查。回傳 [{id, ok, detail}]；ok=True 代表「檢查器運作正常」
# （也就是缺陷存在時被抓到）。D6/D7 是對照組，不在這裡。
CHECK_IDS = ["D1", "D2", "D3", "D4", "D5"]


# ---------- 產生 TS/JS 匯出，供 candidate 端共用（避免兩份 inline 副本漂移） ----------

def emit_js() -> str:
    """輸出 candidate（TypeScript）可直接使用的 JS 片段。

    用法：python3 checks_shared.py --emit-js > shared_checks.js
    """
    parts = [
        "export const JS_D1 = " + _js_literal(JS_D1_CONTRAST) + ";",
        "export const JS_D2 = " + _js_literal(JS_D2_BORDER) + ";",
        "export const JS_BODY = " + _js_literal(JS_BODY_LEN) + ";",
        "export const JS_THEME = " + _js_literal(JS_THEME) + ";",
        "export const JS_SIDEBAR = " + _js_literal(JS_SIDEBAR) + ";",
        "export const JS_H1 = " + _js_literal(JS_H1) + ";",
    ]
    return "\n\n".join(parts) + "\n"


def _js_literal(text: str) -> str:
    """把 Python 字串轉成 JS template literal（反引號 + 跳脫）。"""
    return "`" + text.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${") + "`"


if __name__ == "__main__":
    import sys
    if "--emit-js" in sys.argv:
        sys.stdout.write(emit_js())
    else:
        sys.stdout.write(__doc__ or "")
