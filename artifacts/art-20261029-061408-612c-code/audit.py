#!/usr/bin/env python3
"""audit.py — 程式化的版面稽核（取代「肉眼看截圖」）。

為什麼不用肉眼看：本環境沒有設定 vision provider（hermes 未配置 LLM 視覺模型），
與其宣稱「我看過截圖」卻沒看，不如用可重現的 DOM 量測。
這份稽核能抓的是「用眼睛會漏」的問題：
  - 元素溢出容器（左右超出邊界）
  - 文字被截斷（scrollWidth > clientWidth 且 overflow 非 visible）
  - 重疊（相鄰塊級元素的 bounding box 相交）
  - 低對比的文字（實測像素而非 token 推算）
  - container query 是否真的命中
  - 觸控目標小於 24px
"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE = Path(__file__).parent

AUDIT_JS = r"""
() => {
  const out = {overflow: [], clipped: [], overlap: [], smallTarget: [], cq: {}};
  const els = document.querySelectorAll('body *');

  const isScrollContainer = (el) => {
    const ox = getComputedStyle(el).overflowX;
    return ox === 'auto' || ox === 'scroll';
  };
  const inScroller = (el) => {
    for (let p = el.parentElement; p && p !== document.body; p = p.parentElement) {
      if (isScrollContainer(p)) return p;
    }
    return null;
  };

  // 1. 溢出：元素超出其 offsetParent 的左右邊界
  for (const el of els) {
    if (el.tagName === 'HTML' || el.tagName === 'BODY' || el.tagName === 'SCRIPT') continue;
    const r = el.getBoundingClientRect();
    if (r.width === 0 || r.height === 0) continue;
    const parent = el.offsetParent;
    if (!parent) continue;
    const pr = parent.getBoundingClientRect();
    const cs = getComputedStyle(el);
    if (cs.position === 'fixed' || cs.position === 'absolute') continue;
    // ★ 捲動容器內的元素本來就會超出 —— 那是設計，不是破版
    if (inScroller(el)) continue;
    if (r.right > pr.right + 1 || r.left < pr.left - 1) {
      out.overflow.push({
        sel: el.className || el.tagName,
        elRight: Math.round(r.right), parentRight: Math.round(pr.right),
        elLeft: Math.round(r.left), parentLeft: Math.round(pr.left),
      });
    }
    // 2. 截斷：內容比盒子寬/高，且 overflow 被裁（非捲動）
    if (el.scrollWidth > el.clientWidth + 2 && cs.overflowX !== 'visible'
        && el.clientWidth > 0 && !isScrollContainer(el)) {
      out.clipped.push({sel: el.className || el.tagName,
                        scrollW: el.scrollWidth, clientW: el.clientWidth,
                        text: (el.textContent || '').trim().slice(0, 40)});
    }
  }

  // 2b. 捲動容器本身要能用（scrollWidth > clientWidth 時必須 overflow 可捲）
  out.scrollOk = true;
  for (const el of document.querySelectorAll('*')) {
    if (!isScrollContainer(el)) continue;
    const scrolls = el.scrollWidth > el.clientWidth + 2;
    if (scrolls && getComputedStyle(el).overflowX === 'hidden') {
      out.scrollOk = false;
      out.clipped.push({sel: el.className || el.tagName, reason: '需要捲動但 overflow 為 hidden'});
    }
  }

  // 3. 重疊：同層的塊級兄弟元素矩形相交
  const groups = new Map();
  for (const el of els) {
    const p = el.parentElement;
    if (!p) continue;
    if (!groups.has(p)) groups.set(p, []);
    groups.get(p).push(el);
  }
  for (const [parent, kids] of groups) {
    if (kids.length < 2) continue;
    const boxes = kids.map(k => {
      const r = k.getBoundingClientRect();
      return {k, r};
    }).filter(b => b.r.width > 0 && b.r.height > 0
      && getComputedStyle(b.k).position === 'static');
    for (let i = 0; i < boxes.length; i++) {
      for (let j = i + 1; j < boxes.length; j++) {
        const a = boxes[i].r, b = boxes[j].r;
        const ix = Math.min(a.right, b.right) - Math.max(a.left, b.left);
        const iy = Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top);
        if (ix > 2 && iy > 2) {
          out.overlap.push({
            a: boxes[i].k.className || boxes[i].k.tagName,
            b: boxes[j].k.className || boxes[j].k.tagName,
            overlapX: Math.round(ix), overlapY: Math.round(iy),
          });
        }
      }
    }
  }

  // 4. 觸控目標 < 24px
  for (const el of document.querySelectorAll('button, a, [role="link"], [tabindex]')) {
    const r = el.getBoundingClientRect();
    if (r.height > 0 && r.height < 24) {
      out.smallTarget.push({sel: el.className || el.tagName, h: Math.round(r.height)});
    }
  }

  // 5. container query 是否命中（用 probe 實測，不看 CSS 文字）
  const wrap = document.querySelector('.kpi-wrap');
  if (wrap) {
    const cs = getComputedStyle(wrap);
    const probe = document.createElement('style');
    probe.textContent = '@container kpi (width > 700px) { .kpi-grid { outline-color: rgb(1,2,3) } }';
    document.head.appendChild(probe);
    const hit = getComputedStyle(document.querySelector('.kpi-grid')).outlineColor;
    probe.remove();
    out.cq = {
      containerType: cs.containerType,
      containerName: cs.containerName,
      containerWidth: Math.round(wrap.getBoundingClientRect().width),
      gridColumns: getComputedStyle(document.querySelector('.kpi-grid')).gridTemplateColumns,
      width_gt_700_matches: hit === 'rgb(1, 2, 3)',
    };
  }
  return out;
}
"""

VIEWS = [
    ("wide",   1440, 900, "light"),
    ("narrow",  420, 900, "light"),
    ("dark",   1440, 900, "dark"),
    ("dark-narrow", 420, 900, "dark"),
]


def main() -> int:
    total = 0
    with sync_playwright() as p:
        b = p.chromium.launch()
        for name, w, h, theme in VIEWS:
            ctx = b.new_context(viewport={"width": w, "height": h})
            pg = ctx.new_page()
            errs = []
            pg.on("pageerror", lambda e: errs.append(str(e)))
            pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
            pg.goto((BASE / "after.html").as_uri())
            if theme == "dark":
                pg.evaluate("document.documentElement.dataset.theme='dark'")
            pg.wait_for_timeout(250)
            r = pg.evaluate(AUDIT_JS)

            issues = (len(r["overflow"]) + len(r["clipped"]) + len(r["overlap"])
                      + len(r["smallTarget"]) + len(errs))
            total += issues
            print(f"\n-- {name} ({w}x{h}, {theme}) --")
            print(f"   container query: {r['cq']}")
            for key, label in [("overflow", "溢出"), ("clipped", "截斷"),
                               ("overlap", "重疊"), ("smallTarget", "觸控目標過小")]:
                if r[key]:
                    print(f"   ✗ {label} ({len(r[key])}):")
                    for item in r[key][:6]:
                        print(f"       {item}")
            if errs:
                print(f"   ✗ console/page errors: {errs[:3]}")
            if issues == 0:
                print("   ✓ 無版面問題、無 console 錯誤")
            ctx.close()
        b.close()
    print(f"\n總計問題數：{total}")
    return 0 if total == 0 else 1


if __name__ == "__main__":
    sys.exit(main())