#!/usr/bin/env python3
"""a11y_check.py — WCAG 2.x AA 機械化無障礙稽核（可重跑、有結束碼、可機器讀取）。

為什麼需要這一支（不是重複 audit.py）：
  audit.py 查的是「版面壞掉」：溢出／截斷／重疊／觸控目標<24px／console 錯誤／container query。
  無障礙缺陷**不會讓版面壞掉**，所以版面稽核對它們永遠是綠的。2026-10-23 的作品
  audit.py EXIT=0、contrast_check.py 24/24 全過，但：5 個導覽項是 <div role="link">
  （沒有 href、沒有 Enter/Space 行為）、沒有略過導覽的 skip link、表格 th 的 scope 未覆蓋、
  主題切換按鈕的可及名稱會隨狀態改變（aria-pressed + 改名 = 螢幕閱讀器讀出矛盾組合）。
  這支腳本專查這幾類，判準直接寫在 WCAG 條文上。

用法：
    python3 a11y_check.py after.html                 # 人類可讀 + 結束碼
    python3 a11y_check.py after.html --json          # 機器可讀 JSON（stdout）
    python3 a11y_check.py after.html --out a11y.json # 同時寫檔

結束碼：
    0 = 沒有 high/medium 等級發現（可能有 low 建議級）
    1 = 有 high/medium 等級發現
    2 = 執行失敗（環境／檔案問題，不是產品缺陷）

涵蓋範圍（誠實揭露，不宣稱「全部通過」）：
  涵蓋：鍵盤可操作性(2.1.1/4.1.2)、可及名稱(4.1.2/2.4.4)、目標大小(2.5.8 AA / 2.5.5 AAA)、
        表格標頭關聯(1.3.1)、元件邊界對比(1.4.11)、焦點可見性(2.4.7)、焦點指示對比(1.4.11)、
        略過重複區塊(2.4.1)、aria-pressed 與可及名稱一致性(4.1.2/3.2.2)。
  不涵蓋：螢幕閱讀器實機測試、VoiceOver/NVDA、動態內容廣播、翻譯與語言正確性、
        色彩以外的視覺障礙情境、實際使用者的障礙情境。
  「EXIT=0」只代表上面列出的項目全過，不代表頁面完全無障礙問題。

環境：需要 playwright（Python）。不需要金鑰、不需要網路。
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

# ---------------------------------------------------------------- JS 輔助函式

JS_LIB = r"""
(() => {
  const cvs = document.createElement('canvas');
  cvs.width = cvs.height = 1;
  const ctx = cvs.getContext('2d', { willReadFrequently: true });

  function toRGBA(color) {
    if (!color) return null;
    ctx.clearRect(0, 0, 1, 1);
    ctx.fillStyle = '#000000';
    ctx.fillStyle = color;                 // 不合法的值會保留 #000000
    ctx.fillRect(0, 0, 1, 1);
    const d = ctx.getImageData(0, 0, 1, 1).data;
    if (d[3] === 0) return null;           // 全透明
    return [d[0], d[1], d[2]];
  }

  function lum(rgb) {
    const f = rgb.map(v => {
      v /= 255;
      return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4);
    });
    return 0.2126 * f[0] + 0.7152 * f[1] + 0.0722 * f[2];
  }

  function ratio(a, b) {
    if (!a || !b) return null;
    const l1 = lum(a), l2 = lum(b);
    const hi = Math.max(l1, l2), lo = Math.min(l1, l2);
    return Math.round(((hi + 0.05) / (lo + 0.05)) * 100) / 100;
  }

  function sel(el) {
    if (!el) return '(null)';
    let s = el.tagName.toLowerCase();
    if (el.id) s += '#' + el.id;
    const cn = (el.className || '').toString().trim();
    if (cn) s += '.' + cn.split(/\s+/).join('.');
    const txt = (el.textContent || '').trim().replace(/\s+/g, ' ').slice(0, 24);
    return txt ? s + ' 「' + txt + '」' : s;
  }

  function opaqueBg(el, skipSelf) {
    let n = skipSelf ? (el ? el.parentElement : null) : el;
    while (n) {
      const bg = toRGBA(getComputedStyle(n).backgroundColor);
      if (bg) return bg;
      n = n.parentElement;
    }
    return [255, 255, 255];
  }

  function accName(el) {
    if (!el) return '';
    const direct = (el.getAttribute('aria-label') || '').trim();
    if (direct) return direct;
    const by = el.getAttribute('aria-labelledby');
    if (by) {
      const t = by.split(/\s+/)
        .map(id => (document.getElementById(id) || {}).textContent || '')
        .join(' ').trim();
      if (t) return t;
    }
    if (el.tagName === 'INPUT' && (el.getAttribute('type') || '') === 'image') {
      return (el.getAttribute('alt') || '').trim();
    }
    const txt = (el.textContent || '').trim().replace(/\s+/g, ' ');
    if (txt) return txt;
    return (el.getAttribute('title') || '').trim() || (el.getAttribute('alt') || '').trim();
  }

  const FOCUSABLE = 'a[href],button,input,select,textarea,[tabindex]:not([tabindex="-1"])';

  function audit() {
    const findings = [];
    const measured = { interactive: 0, focusables: 0, tables: 0, th_cells: 0 };

    // 1. 鍵盤可操作性（2.1.1 / 4.1.2）
    document.querySelectorAll('[role="link"],[role="button"],[role="tab"],[role="menuitem"],[role="checkbox"],[role="switch"]')
      .forEach(el => {
        const native = ['A', 'BUTTON', 'INPUT', 'SELECT', 'TEXTAREA'].includes(el.tagName);
        const isDeadAnchor = el.tagName === 'A' && !el.hasAttribute('href');
        if (!native || isDeadAnchor) {
          findings.push({
            check: '鍵盤可操作性',
            wcag: '2.1.1 鍵盤 / 4.1.2 名稱角色值',
            severity: 'high',
            where: sel(el),
            detail: 'role=' + el.getAttribute('role') + ' 但不是原生可啟動元素（' +
              el.tagName.toLowerCase() + (isDeadAnchor ? ' 無 href' : '') +
              '）：沒有原生 Enter/Space 行為，鍵盤與螢幕閱讀器使用者無法操作這個控制項。',
          });
        }
      });

    // 2. 可及名稱（4.1.2 / 2.4.4）
    const focusables = Array.from(document.querySelectorAll(FOCUSABLE));
    measured.focusables = focusables.length;
    focusables.forEach(el => {
      if (!accName(el)) {
        findings.push({
          check: '可及名稱',
          wcag: '4.1.2 名稱角色值 / 2.4.4 連結用途',
          severity: 'high',
          where: sel(el),
          detail: '沒有任何可及名稱（aria-label／aria-labelledby／內容文字／title／alt 皆空），螢幕閱讀器只會讀出角色或空白。',
        });
      }
    });

    // 3. 目標大小（2.5.8 AA ≥24px；2.5.5 AAA ≥44px）
    focusables.forEach(el => {
      const r = el.getBoundingClientRect();
      if (r.width === 0 && r.height === 0) return;
      measured.interactive += 1;
      const w = Math.round(r.width), h = Math.round(r.height);
      if (w < 24 || h < 24) {
        findings.push({
          check: '目標大小',
          wcag: '2.5.8 目標大小（最小，AA）',
          severity: 'high',
          where: sel(el),
          detail: '尺寸 ' + w + '×' + h + 'px，小於 AA 要求的 24×24px。',
        });
      } else if (w < 44 || h < 44) {
        findings.push({
          check: '目標大小（建議）',
          wcag: '2.5.5 目標大小（增強，AAA）',
          severity: 'low',
          where: sel(el),
          detail: '尺寸 ' + w + '×' + h + 'px，未達 AAA 的 44×44px（AA 已過）。',
        });
      }
    });

    // 4. 表格標頭關聯（1.3.1）
    document.querySelectorAll('table').forEach(t => { measured.tables += 1; });
    document.querySelectorAll('table th').forEach(th => {
      measured.th_cells += 1;
      if (!th.hasAttribute('scope') && !th.hasAttribute('headers')) {
        findings.push({
          check: '表格標頭關聯',
          wcag: '1.3.1 資訊與結構',
          severity: 'medium',
          where: sel(th),
          detail: 'th 沒有 scope（或 headers），螢幕閱讀器無法判斷這個儲存格標示哪一欄／哪一列。',
        });
      }
    });

    // 5. 非文字對比（1.4.11）
    //    判準要對，否則整支檢查器就會變成「報假警的噪音」：
    //    - 1.4.11 判的是「元件邊界是否可辨識」，邊界可以是**邊框**而不是填色；
    //    - 但如果元件是**靠文字本身辨識**的（沒有填色、沒有邊框、文字對比達標），
    //      就不需要邊界 —— 1.4.3（文字對比）才是它的判準，不該用 1.4.11 誤傷。
    //    - 表單控制項（input/select/textarea）例外：沒有邊框就看不出欄位在哪，必查。
    const FORM_TAGS = ['INPUT', 'SELECT', 'TEXTAREA'];
    focusables.forEach(el => {
      const cs = getComputedStyle(el);
      const adj = opaqueBg(el, true);

      // 邊框：有 border-width 且不是 none/transparent
      const bw = parseFloat(cs.borderTopWidth || '0');
      const bs = cs.borderTopStyle;
      const bc = toRGBA(cs.borderTopColor);
      const borderRatio = (bw > 0 && bs !== 'none' && bc) ? ratio(bc, adj) : null;

      const own = toRGBA(cs.backgroundColor);
      const fillRatio = own ? ratio(own, adj) : null;

      const borderOk = borderRatio !== null && borderRatio >= 3;
      const fillOk = fillRatio !== null && fillRatio >= 3;
      if (borderOk || fillOk) return;                 // 有可辨識邊界 → 通過

      // 靠文字辨識的元件：文字對比達 4.5:1 → 不適用 1.4.11 的邊界要求
      const textColor = toRGBA(cs.color);
      const textRatio = textColor ? ratio(textColor, own || adj) : null;
      const textIdentifies = !FORM_TAGS.includes(el.tagName)
        && (el.textContent || '').trim().length > 0
        && textRatio !== null && textRatio >= 4.5;
      if (textIdentifies) return;

      const which = borderRatio !== null
        ? ('邊框對比 ' + borderRatio + ':1')
        : ('填色對比 ' + (fillRatio === null ? '不可量' : fillRatio + ':1'));
      findings.push({
        check: '非文字對比（元件邊界）',
        wcag: '1.4.11 非文字對比',
        severity: 'medium',
        where: sel(el),
        detail: which + '，低於 3:1；此元件沒有可辨識邊界、也不能靠對比達標的文字辨識，'
                + '只看得出控制項在哪個位置（表單欄位沒有邊框尤其明顯）。',
      });
    });

    return { findings, measured };
  }

  function resetFocus() {
    if (document.activeElement && document.activeElement.blur) document.activeElement.blur();
    return document.activeElement === document.body;
  }

  function tabStep() {
    const el = document.activeElement;
    if (!el || el === document.body) return { none: true };
    const cs = getComputedStyle(el);
    const outlineVisible = cs.outlineStyle !== 'none' && parseFloat(cs.outlineWidth || '0') > 0;
    const indicator = toRGBA(cs.outlineColor);
    const adj = opaqueBg(el, true);
    const href = el.getAttribute('href') || '';
    const targetExists = href.startsWith('#') && href.length > 1
      ? !!document.getElementById(href.slice(1))
      : false;
    return {
      tag: el.tagName.toLowerCase(),
      sel: sel(el),
      href,
      targetExists,
      rect: (r => ({ w: Math.round(r.width), h: Math.round(r.height) }))(el.getBoundingClientRect()),
      focus_visible: outlineVisible,
      outline_width: cs.outlineWidth,
      indicator_ratio: indicator ? ratio(indicator, adj) : null,
      name: accName(el),
    };
  }

  window.__a11y = { audit, tabStep, resetFocus, accName, sel, ratio, toRGBA };
})()
"""

SEV_FAIL = {"high", "medium"}


def _fmt(f: dict) -> str:
    return ("  [{sev}] {check}（{wcag}）\n      位置：{where}\n      問題：{detail}"
            .format(sev=f["severity"].upper(), check=f["check"], wcag=f["wcag"],
                    where=f["where"], detail=f["detail"]))


def run(path: Path) -> dict:
    findings: list[dict] = []
    measured: dict = {}
    order: list[dict] = []
    page_errors: list[str] = []
    pressed_check = None

    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport={"width": 1440, "height": 900})
        page = ctx.new_page()
        page.on("pageerror", lambda e: page_errors.append(str(e)))
        page.goto(path.as_uri())
        page.wait_for_timeout(300)
        page.evaluate(JS_LIB)

        res = page.evaluate("() => window.__a11y.audit()")
        findings.extend(res["findings"])
        measured.update(res["measured"])

        # 真實鍵盤巡覽（Tab）：量焦點可見性與焦點指示對比
        page.evaluate("() => window.__a11y.resetFocus()")
        for _ in range(60):
            page.keyboard.press("Tab")
            step = page.evaluate("() => window.__a11y.tabStep()")
            if step.get("none"):
                break
            order.append(step)
        measured["tab_stops"] = len(order)

        for s in order:
            if not s.get("focus_visible"):
                findings.append({
                    "check": "焦點可見性",
                    "wcag": "2.4.7 焦點可見",
                    "severity": "high",
                    "where": s["sel"],
                    "detail": "鍵盤 Tab 至此元素時沒有可見的焦點指示（outline none/寬度 0），使用者不知道焦點在哪。",
                })
            ir = s.get("indicator_ratio")
            if ir is not None and ir < 3:
                findings.append({
                    "check": "焦點指示對比",
                    "wcag": "1.4.11 非文字對比",
                    "severity": "medium",
                    "where": s["sel"],
                    "detail": "焦點指示與相鄰背景對比 " + str(ir) + ":1，低於 3:1。",
                })

        # 2.4.1 略過重複區塊：第一個 Tab 停點應該是跳至主要內容的連結
        first = order[0] if order else None
        if first and not (first.get("tag") == "a" and str(first.get("href", "")).startswith("#")
                          and first.get("targetExists")):
            findings.append({
                "check": "略過重複區塊",
                "wcag": "2.4.1 略過區塊（Level A）",
                "severity": "low",
                "where": first["sel"],
                "detail": "第一個鍵盤停點不是「跳至主要內容」的內部連結（目前停點：" +
                          first["sel"] + "），鍵盤使用者每次都要逐一 Tab 過導覽列。",
            })

        # 4.1.2 / 3.2.2：aria-pressed 的按鈕，可及名稱不得隨狀態改變
        pressed_check = page.evaluate("""() => {
          const el = document.querySelector('[aria-pressed]');
          if (!el) return null;
          const before = window.__a11y.accName(el);
          el.click();
          const after = window.__a11y.accName(el);
          const state = el.getAttribute('aria-pressed');
          el.click();                                  // 還原，避免影響後續截圖
          return { before: before, after: after, state: state, sel: window.__a11y.sel(el) };
        }""")
        if pressed_check and pressed_check["before"] != pressed_check["after"]:
            findings.append({
                "check": "aria-pressed 與可及名稱一致性",
                "wcag": "4.1.2 名稱角色值 / 3.2.2 輸入時",
                "severity": "medium",
                "where": pressed_check["sel"],
                "detail": "aria-pressed 按鈕的可及名稱會隨狀態改變（'" + pressed_check["before"] +
                          "' → '" + pressed_check["after"] + "'），螢幕閱讀器會讀出互相矛盾的名稱與狀態。",
            })

        measured["page_errors"] = len(page_errors)
        browser.close()

    n_fail = sum(1 for f in findings if f["severity"] in SEV_FAIL)
    n_adv = len(findings) - n_fail
    return {
        "file": str(path),
        "measured": measured,
        "tab_order": [s["sel"] for s in order],
        "findings": findings,
        "n_findings": len(findings),
        "n_fail": n_fail,
        "n_advice": n_adv,
        "exit_code": 1 if n_fail else 0,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("html")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--out")
    a = ap.parse_args()

    path = Path(a.html).resolve()
    if not path.exists():
        print("FAIL: 找不到檔案 " + str(path))
        return 2
    try:
        rep = run(path)
    except Exception as e:                       # noqa: BLE001
        print("FAIL: 執行失敗（環境問題，不是產品缺陷）：" + str(e))
        return 2

    if a.json:
        text = json.dumps(rep, ensure_ascii=False, indent=2)
        if a.out:
            Path(a.out).write_text(text, encoding="utf-8")
        print(text)
    else:
        m = rep["measured"]
        print("== a11y_check.py ==")
        print("檔案：" + rep["file"])
        print("量測：可聚焦元素 {focusables}、有尺寸互動元素 {interactive}、表格 {tables}（th {th_cells}）、"
              "鍵盤停點 {tab_stops}、console 錯誤 {page_errors}".format(**m))
        if rep["tab_order"]:
            print("鍵盤順序：")
            for i, s in enumerate(rep["tab_order"], 1):
                print("  {}. {}".format(i, s))
        if rep["findings"]:
            print("發現 {} 項（阻擋 {}／建議 {}）：".format(
                rep["n_findings"], rep["n_fail"], rep["n_advice"]))
            for f in rep["findings"]:
                print(_fmt(f))
        else:
            print("發現 0 項。")
        print("結束碼：" + str(rep["exit_code"]))
    return rep["exit_code"]


if __name__ == "__main__":
    sys.exit(main())
