#!/usr/bin/env python3
"""contrast_check.py — 通用文字對比稽核（computed style，不依賴特定 token 命名）。

為什麼是「通用」而不是綁定某套 token：
  2026-10-26 的舊版 contrast_check.py 會先解析 CSS token，token 命名不同就直接
  ValueError 崩潰——那次崩潰本身是「檢查器量錯對象」的實例：檢查器應該量
  「讀者實際看到的顏色對比」，而不是「我的 token 表有沒有對齊」。
  本版直接量 computed style + 實際渲染像素，與 token 命名無關。

用法：
    python3 contrast_check.py after.html            # 人類可讀 + 結束碼
    python3 contrast_check.py after.html --json     # 機器可讀 JSON

結束碼：
    0 = 兩個主題下都沒有低於門檻的文字
    1 = 有低於門檻的文字
    2 = 執行失敗（環境／檔案問題，不是產品缺陷）

門檻（WCAG 2.2）：
    一般文字 < 18pt 或 < 14pt 粗體 → 4.5:1
    大字（>=18pt 或 >=14pt 粗體）→ 3:1
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

AA_NORMAL = 4.5
AA_LARGE = 3.0

# 取樣 JS：找出所有含直接文字節點的元素，量其前景色與「有效背景色」。
JS = r"""
() => {
  function parseRGB(s) {
    const m = s.match(/rgba?\(([^)]+)\)/);
    if (!m) return null;
    const p = m[1].split(',').map(x => parseFloat(x.trim()));
    return { r: p[0], g: p[1], b: p[2], a: p.length > 3 ? p[3] : 1 };
  }
  function effectiveBg(el) {
    let p = el;
    while (p && p !== document.documentElement) {
      const c = parseRGB(getComputedStyle(p).backgroundColor);
      if (c && c.a > 0.05) return c;
      p = p.parentElement;
    }
    const c = parseRGB(getComputedStyle(document.documentElement).backgroundColor);
    return c && c.a > 0.05 ? c : { r: 255, g: 255, b: 255, a: 1 };
  }
  const out = [];
  const all = document.querySelectorAll('body *');
  for (const el of all) {
    // 只看「直接含文字」的元素，避免同一段文字被子元素重複計數
    let hasText = false;
    for (const n of el.childNodes) {
      if (n.nodeType === 3 && n.textContent.trim().length > 0) { hasText = true; break; }
    }
    if (!hasText) continue;
    const cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden') continue;
    const fg = parseRGB(cs.color);
    const bg = effectiveBg(el);
    if (!fg || !bg) continue;
    const size = parseFloat(cs.fontSize) || 16;
    const weight = parseInt(cs.fontWeight, 10) || 400;
    const isLarge = size >= 18 || (size >= 14 && weight >= 700);
    const rect = el.getBoundingClientRect();
    if (rect.width < 1 || rect.height < 1) continue;
    out.push({
      text: (el.textContent || '').trim().slice(0, 60),
      tag: el.tagName.toLowerCase(),
      cls: (el.className && typeof el.className === 'string') ? el.className : '',
      fg: fg, bg: bg, fontSize: size, fontWeight: weight, isLarge: isLarge
    });
  }
  return out;
}
"""


def srgb_to_lin(c: float) -> float:
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def luminance(rgb: dict) -> float:
    r = srgb_to_lin(rgb["r"])
    g = srgb_to_lin(rgb["g"])
    b = srgb_to_lin(rgb["b"])
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def ratio(fg: dict, bg: dict) -> float:
    l1 = luminance(fg)
    l2 = luminance(bg)
    if l1 < l2:
        l1, l2 = l2, l1
    return (l1 + 0.05) / (l2 + 0.05)


def check_theme(page, html: Path, theme: str) -> dict:
    page.goto(html.as_uri())
    if theme == "dark":
        page.evaluate("document.documentElement.dataset.theme='dark'")
    page.wait_for_timeout(250)
    samples = page.evaluate(JS)
    findings = []
    for s in samples:
        r = ratio(s["fg"], s["bg"])
        need = AA_LARGE if s["isLarge"] else AA_NORMAL
        if r + 1e-9 < need:
            findings.append({
                "text": s["text"], "selector": f"{s['tag']}.{s['cls']}".strip("."),
                "font_size_px": s["fontSize"], "font_weight": s["fontWeight"],
                "large_text": s["isLarge"], "required": need,
                "measured": round(r, 2),
                "fg": f"rgb({s['fg']['r']:.0f},{s['fg']['g']:.0f},{s['fg']['b']:.0f})",
                "bg": f"rgb({s['bg']['r']:.0f},{s['bg']['g']:.0f},{s['bg']['b']:.0f})",
            })
    findings.sort(key=lambda x: x["measured"])
    return {"theme": theme, "n_sampled": len(samples), "n_findings": len(findings),
            "findings": findings}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("html")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    html = Path(args.html).resolve()
    if not html.exists():
        print(f"找不到檔案：{html}", file=sys.stderr)
        return 2
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            ctx = browser.new_context(viewport={"width": 1440, "height": 900})
            page = ctx.new_page()
            themes = [check_theme(page, html, "light"), check_theme(page, html, "dark")]
            browser.close()
    except Exception as e:  # 環境問題不是產品缺陷
        print(f"執行失敗（環境問題，非產品缺陷）：{type(e).__name__}: {e}", file=sys.stderr)
        return 2

    total = sum(t["n_findings"] for t in themes)
    if args.json:
        print(json.dumps({"themes": themes, "n_findings": total}, ensure_ascii=False, indent=2))
    else:
        print("== contrast_check.py（WCAG 2.2 文字對比）==")
        for t in themes:
            print(f"-- {t['theme']}：取樣 {t['n_sampled']} 個含文字元素，"
                  f"低於門檻 {t['n_findings']} 項")
            for f in t["findings"]:
                print(f"   [{f['required']}:1 門檻] {f['selector']} 「{f['text']}」")
                print(f"      實測 {f['measured']}:1（前景 {f['fg']} / 背景 {f['bg']}，"
                      f"{f['font_size_px']}px weight {f['font_weight']}）")
        print(f"\n總計低於門檻：{total} 項")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
