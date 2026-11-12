#!/usr/bin/env python3
"""baseline：現行 code SOP 的做法 —— 用 Playwright 直接寫 Python 腳本做同樣的檢查。

修訂版 rev1（2026-11-12，依 eval judge 的 8 條缺點修正）：
  F1 交付物開箱即崩 → 頁面路徑改為 /after.html（不再依賴 index.html 這個未說明的假設），
                      並在 README 寫明三步啟動指令。
  F2 崩潰路徑無診斷產物 → 整段流程用 try/finally 包覆，finally 無條件寫出
                      baseline_result.json（即使 results 空也寫，並記 error 欄位）。
  F3 對照組寬鬆 except 吞掉真錯誤 → 只捕捉 playwright TimeoutError，其餘往外拋，
                      並把例外訊息寫進 detail。
  F4 宣稱共用 shared_checks.js 但檔案不存在 → 檢查邏輯一律從 checks_shared.py 取得，
                      並新增 `python3 checks_shared.py --emit-js` 供 candidate 端共用。
  F5 A/B 有框架以外的變因 → D3 固定等待 300ms、D4 固定 page.reload()、D5 固定 360px，
                      與 candidate 對齊（見 notes）。

檢查邏輯與 candidate（e2e 框架）共用 checks_shared.py，以確保「唯一變因 = 測試框架」。

  D1 假綠燈       .nav-item.active 對比 < 4.5:1
  D2 dead token   --border-strong 定義但無引用
  D3 死按鈕       匯出報表按鈕點了沒反應
  D4 狀態不持久   切深色後 reload 回到 light
  D5 側欄未響應式 360px 下側欄 ≥ 視窗一半
  D6 對照組(應過) h1 有內容
  D7 對照組(應敗) 斷言不存在的字串必須失敗

退出碼：0 = 5 條缺陷全抓且 2 條對照組行為正確；1 = 有缺陷漏抓或對照組失效。
★ 2 = 執行環境錯誤（頁面載不到等），此時 result.json 會有 error 欄位。
"""
from __future__ import annotations

import json
import sys
import traceback
from pathlib import Path

from playwright.sync_api import TimeoutError as PWTimeout
from playwright.sync_api import sync_playwright

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from checks_shared import (  # noqa: E402
    JS_BODY_LEN, JS_D1_CONTRAST, JS_D2_BORDER, JS_H1, JS_SIDEBAR, JS_THEME,
    contrast_ratio,
)

# ★ F1：明確指向交付的頁面檔，不依賴「必須改名成 index.html」這個未說明的假設
PAGE_PATH = "/after.html"
PORT = 8933
BASE_URL = f"http://127.0.0.1:{PORT}{PAGE_PATH}"

# ★ F5：與 candidate 對齊的固定等待／重載策略
D3_WAIT_MS = 300
D7_TIMEOUT_MS = 1200


def run_checks() -> list[dict]:
    results: list[dict] = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport={"width": 1280, "height": 800})
        page = ctx.new_page()
        page.goto(BASE_URL)

        # D6 對照組：頁面載入
        h1 = page.evaluate(JS_H1)
        results.append({"id": "D6", "label": "對照組(應過) h1 有內容",
                        "ok": bool(h1 and h1.strip()), "detail": repr(h1)})

        # D1 假綠燈
        d1 = page.evaluate(JS_D1_CONTRAST)
        ratio = contrast_ratio(d1.get("color", ""), d1.get("background", "")) \
            if "error" not in d1 else None
        results.append({"id": "D1", "label": "假綠燈：active 對比 < 4.5:1",
                        "ok": ratio is not None and ratio < 4.5,
                        "detail": f"ratio={ratio:.3f} color={d1.get('color')} bg={d1.get('background')}"
                        if ratio is not None else str(d1)})

        # D2 dead token
        d2 = page.evaluate(JS_D2_BORDER)
        results.append({"id": "D2", "label": "dead token：--border-strong 定義但無引用",
                        "ok": bool(d2["defined"] and not d2["referenced"]),
                        "detail": json.dumps(d2, ensure_ascii=False)})

        # D3 死按鈕
        before = page.evaluate(JS_BODY_LEN)
        page.locator("button.btn").click()
        page.wait_for_timeout(D3_WAIT_MS)
        after = page.evaluate(JS_BODY_LEN)
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
        page2.goto(BASE_URL)
        w = page2.evaluate(JS_SIDEBAR)
        results.append({"id": "D5", "label": "側欄未響應式：360px 下側欄 ≥ 視窗一半",
                        "ok": bool(w and w["sidebar"] >= w["win"] * 0.5),
                        "detail": json.dumps(w, ensure_ascii=False)})
        ctx2.close()

        # D7 對照組：斷言不存在的字串必須失敗
        # ★ F3：只把「等待逾時」視為預期失敗；其他例外往外拋，不再被靜默吞掉
        d7_ok, d7_detail = False, ""
        try:
            page.locator("h1:has-text('__NO_SUCH_TEXT_9f3a__')").wait_for(timeout=D7_TIMEOUT_MS)
            d7_detail = "竟然沒有失敗：斷言不存在的字串居然成功了"
        except PWTimeout as e:
            d7_ok = True
            d7_detail = f"wait_for 逾時＝預期失敗（{type(e).__name__}）"
        results.append({"id": "D7", "label": "對照組(應敗) 斷言不存在的字串必須失敗",
                        "ok": d7_ok, "detail": d7_detail})

        browser.close()
    return results


def take_screenshot() -> str | None:
    """現行 SOP 的慣例：自己寫 shot.py 截圖（額外工作，且要自己維護）。"""
    shots_dir = HERE / "shots_failure"
    shots_dir.mkdir(exist_ok=True)
    path = shots_dir / "d1-active-nav.png"
    try:
        with sync_playwright() as p2:
            b2 = p2.chromium.launch()
            c2 = b2.new_context(viewport={"width": 1280, "height": 800})
            pg2 = c2.new_page()
            pg2.goto(BASE_URL)
            pg2.screenshot(path=str(path))
            b2.close()
    except Exception as e:  # 截圖失敗不影響主流程，但必須記錄
        return f"截圖失敗：{type(e).__name__}: {e}"
    return str(path)


def main() -> int:
    results: list[dict] = []
    error = None
    try:
        results = run_checks()
    except Exception as e:
        error = f"{type(e).__name__}: {e}"
        traceback.print_exc()
    finally:
        # ★ F2：任何路徑都一定要留下可讀的結果檔（包含錯誤訊息）
        shot_note = take_screenshot()
        out = {"variant": "baseline", "tool": "playwright-python (現行 code SOP)",
               "page_url": BASE_URL, "results": results,
               "error": error, "screenshot": shot_note}
        (HERE / "baseline_result.json").write_text(
            json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

    print("=== baseline（playwright 直接寫）===")
    if error:
        print(f"  執行錯誤：{error}")
        print("  （詳細錯誤已寫入 baseline_result.json 的 error 欄位）")
        return 2
    bad = 0
    for r in results:
        print(f"  {'OK ' if r['ok'] else 'NG '} {r['id']} {r['label']}  | {r['detail']}")
        if not r["ok"]:
            bad += 1
    print(f"結果：{len(results)-bad}/{len(results)} 項符合預期")
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
