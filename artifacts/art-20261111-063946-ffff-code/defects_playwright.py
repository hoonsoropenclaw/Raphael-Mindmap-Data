#!/usr/bin/env python3
"""baseline：現行 code SOP 的做法 —— 用 Playwright 直接寫 Python 腳本做同樣的檢查。

檢查邏輯與 candidate（e2e 框架）共用 shared_checks.js／checks_shared.py，
以確保「唯一變因 = 測試框架」，不是「檢查內容不同」。

  D1 假綠燈       .nav-item.active 對比 < 4.5:1
  D2 dead token   --border-strong 定義但無引用
  D3 死按鈕       匯出報表按鈕點了沒反應
  D4 狀態不持久   切深色後 reload 回 light
  D5 側欄未響應式 360px 下側欄 ≥ 視窗一半
  D6 對照組(應過) h1 有內容
  D7 對照組(應敗) 斷言不存在的字串必須失敗

退出碼：0 = 5 條缺陷全抓且 2 條對照組行為正確；1 = 有缺陷漏抓或對照組失效。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from checks_shared import contrast_ratio  # noqa: E402

JS = HERE / "shared_checks.js"
HTML = HERE / "after.html"

JS_D1 = """() => {
  const el = document.querySelector('.nav-item.active');
  if (!el) return {error: 'no .nav-item.active'};
  const cs = getComputedStyle(el);
  return {color: cs.color, background: cs.backgroundColor};
}"""
JS_D2 = """() => {
  const styles = [...document.querySelectorAll('style')].map(s => s.textContent).join('\\n');
  return {defined: styles.includes('--border-strong:'), referenced: /var\\(--border-strong\\)/.test(styles)};
}"""
JS_BODY = "() => document.body.innerText.length"
JS_THEME = "() => document.documentElement.dataset.theme"
JS_SIDEBAR = """() => {
  const s = document.querySelector('.sidebar');
  if (!s) return null;
  return {sidebar: s.getBoundingClientRect().width, win: window.innerWidth};
}"""
JS_H1 = "() => { const h = document.querySelector('h1'); return h ? h.innerText : null; }"


def main() -> int:
    results: list[dict] = []
    url = "http://127.0.0.1:8933/"   # 與 candidate 同一種服務方式（HTTP），避免把「載入機制」當成變因
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport={"width": 1280, "height": 800})
        page = ctx.new_page()
        page.goto(url)

        # D6 對照組：頁面載入
        h1 = page.evaluate(JS_H1)
        results.append({"id": "D6", "label": "對照組(應過) h1 有內容",
                        "ok": bool(h1 and h1.strip()), "detail": repr(h1)})

        # D1 假綠燈
        d1 = page.evaluate(JS_D1)
        ratio = contrast_ratio(d1.get("color", ""), d1.get("background", "")) \
            if "error" not in d1 else None
        results.append({"id": "D1", "label": "假綠燈：active 對比 < 4.5:1",
                        "ok": ratio is not None and ratio < 4.5,
                        "detail": f"ratio={ratio:.3f} color={d1.get('color')} bg={d1.get('background')}"
                        if ratio is not None else str(d1)})

        # D2 dead token
        d2 = page.evaluate(JS_D2)
        results.append({"id": "D2", "label": "dead token：--border-strong 定義但無引用",
                        "ok": bool(d2["defined"] and not d2["referenced"]),
                        "detail": json.dumps(d2, ensure_ascii=False)})

        # D3 死按鈕
        before = page.evaluate(JS_BODY)
        page.locator("button.btn").click()
        page.wait_for_timeout(300)
        after = page.evaluate(JS_BODY)
        results.append({"id": "D3", "label": "死按鈕：匯出報表按鈕無可觀察反應",
                        "ok": after == before, "detail": f"before={before} after={after}"})

        # D4 狀態不持久
        page.locator("#themeBtn").click()
        themed = page.evaluate(JS_THEME)
        page.reload()
        after_reload = page.evaluate(JS_THEME)
        results.append({"id": "D4", "label": "狀態不持久：切深色後 reload 回 light",
                        "ok": after_reload != themed,
                        "detail": f"after-toggle={themed} after-reload={after_reload}"})

        # D5 側欄未響應式
        ctx2 = browser.new_context(viewport={"width": 360, "height": 800})
        page2 = ctx2.new_page()
        page2.goto(url)
        w = page2.evaluate(JS_SIDEBAR)
        results.append({"id": "D5", "label": "側欄未響應式：360px 下側欄 ≥ 視窗一半",
                        "ok": bool(w and w["sidebar"] >= w["win"] * 0.5),
                        "detail": json.dumps(w, ensure_ascii=False)})
        ctx2.close()

        # D7 對照組：斷言不存在的字串必須失敗
        d7_ok = False
        try:
            page.locator("h1").filter(has_text="__NO_SUCH_TEXT_9f3a__")
            page.wait_for_timeout(200)
            page.locator("text=__NO_SUCH_TEXT_9f3a__").count()
            page.locator("h1:has-text('__NO_SUCH_TEXT_9f3a__')").wait_for(timeout=1200)
        except Exception:
            d7_ok = True
        results.append({"id": "D7", "label": "對照組(應敗) 斷言不存在的字串必須失敗",
                        "ok": d7_ok, "detail": "wait_for 逾時＝預期失敗" if d7_ok else "竟然沒有失敗"})

        browser.close()

    # 現行 SOP 的慣例：自己寫 shot.py 截圖（這是額外工作，且要自己維護）
    shots_dir = HERE / "shots_failure"
    shots_dir.mkdir(exist_ok=True)
    with sync_playwright() as p2:
        b2 = p2.chromium.launch()
        c2 = b2.new_context(viewport={"width": 1280, "height": 800})
        pg2 = c2.new_page()
        pg2.goto("http://127.0.0.1:8933/")
        pg2.screenshot(path=str(shots_dir / "d1-active-nav.png"))
        b2.close()

    out = {"variant": "baseline", "tool": "playwright-python (現行 code SOP)",
           "results": results}
    (HERE / "baseline_result.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"=== baseline（playwright 直接寫）===")
    bad = 0
    for r in results:
        print(f"  {'OK ' if r['ok'] else 'NG '} {r['id']} {r['label']}  | {r['detail']}")
        if not r["ok"]:
            bad += 1
    print(f"結果：{len(results)-bad}/{len(results)} 項符合預期")
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
