#!/usr/bin/env python3
"""shot.py — 用 Playwright 對 after.html 截圖（亮/暗 × 寬/窄），存到 shots/。"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE = Path(__file__).parent
SHOTS = BASE / "shots"
SHOTS.mkdir(exist_ok=True)

VIEWS = [
    ("wide",   1440, 900, "light"),
    ("narrow",  420, 900, "light"),
    ("dark",   1440, 900, "dark"),
    ("dark-narrow", 420, 900, "dark"),
]


def main() -> int:
    ok = True
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for name, w, h, theme in VIEWS:
            ctx = browser.new_context(viewport={"width": w, "height": h},
                                      device_scale_factor=2)
            page = ctx.new_page()
            errors = []
            page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
            page.on("pageerror", lambda e: errors.append(str(e)))
            page.goto((BASE / "after.html").as_uri())
            if theme == "dark":
                page.evaluate("document.documentElement.dataset.theme='dark'")
            page.wait_for_timeout(400)
            out = SHOTS / f"after-{name}.png"
            page.screenshot(path=str(out), full_page=True)

            # 順便量測 container query 是否真的生效
            cols = page.evaluate(
                "getComputedStyle(document.querySelector('.kpi-grid')).gridTemplateColumns")
            card_pad = page.evaluate(
                "getComputedStyle(document.querySelector('.kpi-card')).paddingLeft")
            print(f"  {name:12s} {w}x{h} {theme:5s} → {out.name}  "
                  f"kpi-grid columns={cols}  card padding={card_pad}")
            if errors:
                ok = False
                print(f"      ✗ console errors: {errors}")
            ctx.close()

        # 順便截 before.html 當對照
        for name, w, h in [("wide", 1440, 900), ("narrow", 420, 900)]:
            ctx = browser.new_context(viewport={"width": w, "height": h},
                                      device_scale_factor=2)
            page = ctx.new_page()
            page.goto((BASE / "before.html").as_uri())
            page.wait_for_timeout(300)
            out = SHOTS / f"before-{name}.png"
            page.screenshot(path=str(out), full_page=True)
            print(f"  {'before-'+name:12s} {w}x{h}       → {out.name}")
            ctx.close()
        browser.close()
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())