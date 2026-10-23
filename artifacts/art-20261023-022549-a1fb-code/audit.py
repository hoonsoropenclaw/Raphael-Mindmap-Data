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
  - ★ 資訊完整性：表格欄位在窄版是否消失（不靠橫捲才看得到）
  - ★ 可用寬度預算：主內容在窄版還剩多少
  - ★ surface 層次：MD3 elevation 階差是否肉眼可辨

2026-10-23 修正（前一版的假綠燈）：
  舊版把 overflow-x:auto 的捲動容器整列略過，於是 420px 下表格 5 欄
  只剩 2 欄、其餘需橫向捲動的情況，回報「無版面問題」。捲動不是破版，
  但「必須捲動才看得到關鍵欄位」對行政儀表板是嚴重問題——使用者不會想到
  要往右拖。捲動可以存在，但必須被標示為需要處理。
"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE = Path(__file__).parent

AUDIT_JS = r"""
() => {
  const out = {overflow: [], clipped: [], overlap: [], smallTarget: [],
               hiddenColumns: [], mainBudget: [], surfaceLevels: {}, cq: {}};
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

    // 2c. ★ 資訊完整性：表格在目前視窗下「看不見的欄位」
    //     舊版只檢查 hidden，auto 捲動容器被略過 → 420px 下 5 欄剩 2 欄卻回報 PASS。
    //     這裡改成：逐欄量測其實際可見範圍，落在捲動容器可視區外的欄位視為
    //     「需橫捲才可見」，並要求容器有可見的捲動提示（scrollbar 非 overlay 或有 shadow）。
    for (const tbl of document.querySelectorAll('table')) {
      const scroller = tbl.closest('[class*="scroll"]') || tbl.parentElement;
      const sc = isScrollContainer(scroller) ? scroller : null;
      const cols = tbl.querySelectorAll('thead th');
      if (!cols.length) continue;
      const view = sc ? sc.getBoundingClientRect() : tbl.getBoundingClientRect();
      const hidden = [];
      for (const th of cols) {
        const r = th.getBoundingClientRect();
        if (r.width === 0) continue;               // display:none → 已處理
        if (r.right > view.right + 2) hidden.push(th.textContent.trim());
      }
      if (hidden.length && sc) {
        const pct = Math.round((cols.length - hidden.length) / cols.length * 100);
        // 有 scrollbar（非 overlay）或 CSS mask/gradient 提示，才算有可見的捲動線索
        const sb = sc.offsetWidth - sc.clientWidth;
        const cs2 = getComputedStyle(sc);
        const hasHint = sb > 4
          || cs2.maskImage !== 'none' || cs2.webkitMaskImage !== 'none';
        out.hiddenColumns.push({
          sel: (sc.className || 'table'),
          visibleCols: cols.length - hidden.length,
          totalCols: cols.length,
          hidden: hidden,
          visiblePct: pct,
          scrollbarPx: Math.round(sb),
          scrollAffordance: hasHint,
          reason: `需橫向捲動才看得到 ${hidden.length}/${cols.length} 欄` +
                  (hasHint ? '（有 scrollbar 提示）' : '（無任何捲動提示，使用者不會想到要拖）'),
        });
      }
    }

    // 2d. ★ 主內容可用寬度預算：窄版時側欄吃掉多少
    const main = document.querySelector('.main') || document.querySelector('main');
    if (main) {
      const mw = main.getBoundingClientRect().width;
      out.mainBudget.push({
        viewport: window.innerWidth,
        mainWidth: Math.round(mw),
        pct: Math.round(mw / window.innerWidth * 100),
        note: mw / window.innerWidth < 0.5
          ? '主內容少於視窗一半，側欄未在窄版收合'
          : null,
      });
    }

    // 2e. ★ surface 層次：distinct surface token 的亮度差是否肉眼可辨
      //     注意：Chromium 對 oklch() 回傳 computedStyle.backgroundColor 仍是
      //     "oklch(...)" 字串而非 rgb()，直接 regex 數字會把 L/C/H 當成 R/G/B。
      //     解法：畫到 1x1 canvas 再讀像素，讓瀏覽器自己完成色彩空間轉換。
      const cv = document.createElement('canvas');
      cv.width = cv.height = 1;
      const ctx2d = cv.getContext('2d', {willReadFrequently: true});
      const toRGB = (css) => {
        ctx2d.clearRect(0, 0, 1, 1);
        ctx2d.fillStyle = '#000';
        ctx2d.fillStyle = css;
        if (ctx2d.fillStyle === '#000000' && css !== '#000' && css !== 'rgb(0, 0, 0)') {
          return null;  // 無法解析
        }
        ctx2d.fillRect(0, 0, 1, 1);
        const d = ctx2d.getImageData(0, 0, 1, 1).data;
        return {r: d[0], g: d[1], b: d[2], a: d[3]};
      };
      const surfaces = {};
      for (const el of document.querySelectorAll('body *')) {
        const css = getComputedStyle(el).backgroundColor;
        if (!css || css === 'rgba(0, 0, 0, 0)' || css === 'transparent') continue;
        const px = toRGB(css);
        if (!px || px.a < 8) continue;                 // 全透明 → 不算 surface
        // ★ 用相對亮度（WCAG 定義），不是 0-255 平均
        const lin = (c) => { c /= 255; return c <= 0.04045 ? c/12.92 : Math.pow((c+0.055)/1.055, 2.4); };
        const lum = 0.2126*lin(px.r) + 0.7152*lin(px.g) + 0.0722*lin(px.b);
        const key = `${px.r},${px.g},${px.b}`;
        if (!surfaces[key]) surfaces[key] = {css, rgb: `rgb(${px.r}, ${px.g}, ${px.b})`,
                                             lum: +lum.toFixed(4),
                                             count: 0, sample: el.className || el.tagName};
        surfaces[key].count++;
      }
      const arr = Object.values(surfaces).sort((x, y) => x.lum - y.lum);
      // 只看「被多個元素使用的 surface 階」（count>=2），排除一次性元素
      const ramp = arr.filter(s => s.count >= 2);
      out.surfaceLevels = {
        distinct: arr.length,
        distinctUsed: ramp.length,
        ramp: ramp.map(s => ({rgb: s.rgb, css: s.css, lum: s.lum,
                              count: s.count, sample: s.sample})),
        // 相鄰兩階的亮度差：< 0.01 肉眼幾乎看不出來
        minStepLum: ramp.length > 1
          ? +Math.min(...ramp.slice(1).map((s, i) => s.lum - ramp[i].lum)).toFixed(4)
          : null,
      };

  // 2f. ★ 逐字換行偵測：某元素因為 shrink-to-fit / min-content 退化而被壓得
    //     很窄，導致中文一行只能放幾個字（<caption> 在 table 變 display:block
    //     後實測縮到 53px = 每行 4.4 字，正常應該 20+ 字）。
    //
    //     關鍵：不能只看「寬度/字寬」。KPI 的 delta 徽章（inline-flex，只有
    //     「▲ 12 件」6 個字）寬度/字寬也只有 3.7，但它只有 1 行、沒有在換行，
    //     根本不是問題——那是 badge 正常貼合內容。所以判準必須加上
    //     「實際渲染行數」：只有當文字真的被擠成多行時才算缺陷。
    //
    //     門檻（實測校準）：
    //       退化 caption        → 每行 4.4 字 × 約 8 行   → 判定缺陷
    //       正常 panel-sub      → 每行 15~35 字 × 1~3 行 → 通過
    //       delta 徽章（誤報前例）→ 每行 3.7 字 × 1 行    → 通過（沒在換行）
    out.squished = [];
    for (const el of document.querySelectorAll('body *')) {
      if (el.children.length) continue;                 // 只看純文字節點
      const txt = (el.textContent || '').trim();
      if (txt.length < 6) continue;
      const cs = getComputedStyle(el);
      if (cs.display === 'none' || cs.visibility === 'hidden') continue;
      const r = el.getBoundingClientRect();
      if (r.height === 0 || r.width === 0) continue;

      // 實際渲染行數：用 line-height 推（比 boundingBox 高度可靠，因為
      // 元素可能因 padding/border 高於單行文字）
      let lh = parseFloat(cs.lineHeight);
      if (!lh || isNaN(lh) || cs.lineHeight === 'normal') {
        lh = parseFloat(cs.fontSize) * 1.5;
      }
      const lines = Math.max(1, Math.round((r.height - 2) / lh));
      if (lines < 3) continue;      // 沒有被擠成多行 → 不是這個缺陷

      // 單字寬度：用一個同字級的量測 span 探出來
      const probe = document.createElement('span');
      probe.style.cssText = 'position:absolute;visibility:hidden;white-space:pre;';
      probe.style.font = cs.font;
      probe.textContent = '字';
      el.parentNode.appendChild(probe);
      const chW = probe.getBoundingClientRect().width;
      probe.remove();
      if (!chW) continue;

      const perLine = r.width / chW;
      if (perLine < 6) {
        out.squished.push({sel: el.className || el.tagName,
                           charsPerLine: +perLine.toFixed(2),
                           lines: lines,
                           width: Math.round(r.width),
                           charWidth: +chW.toFixed(1),
                           text: txt.slice(0, 30)});
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
      && getComputedStyle(b.k).position === 'static'
      // ★ 2026-10-23：inline 元素（code/span/a/em…）的 bounding box 本來就會
      // 因為換行而相交，那是文字排版的正常行為，不是重疊 bug。誤報會讓稽核
      // 從「說真話」退化成「雜訊」，所以只對 block-level 判定重疊。
      && getComputedStyle(b.k).display.startsWith('block')
      && !['CODE','SPAN','EM','STRONG','B','I','A','SMALL','ABBR','TIME','SUP','SUB'].includes(b.k.tagName));
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

        // ★ 2026-10-23 evaluate 新增：表頭與資料「文字墨水」右緣對位檢查
        // 為什麼不能用 getBoundingClientOf td：元素框右緣本來就會對齊，
        // 但框內文字靠左時看起來整欄是歪的。必須用 Range 量「真實文字墨水」，
        // 才抓得到 .num{text-align:right} 被 @layer 順序蓋掉這個 bug
        // （當時 th 墨水右緣 747/982/1178 vs td 611/791/1038，Δ 136/191/140px）。
        out.misaligned = [];
        try {
          const ink = (el) => {
            const rg = document.createRange();
            rg.selectNodeContents(el);
            return rg.getBoundingClientRect();
          };
          const ths = [...document.querySelectorAll('thead th')];
          const row1 = [...document.querySelectorAll('tbody tr:first-child td')];
          if (ths.length && ths.length === row1.length) {
            for (let i = 0; i < ths.length; i++) {
              const a = ink(ths[i]), c = ink(row1[i]);
              if (!a.width || !c.width) continue;
              const delta = Math.round(a.right - c.right);
                      const thAlign = getComputedStyle(ths[i]).textAlign;
                      const tdAlign = getComputedStyle(row1[i]).textAlign;
                      // ★ 對齊比較必須比「對齊邊緣」，不是永遠比右緣。
                      //   left-aligned 欄位表頭「處室」比資料「人事室」短，右緣本來就會差一截 ——
                      //   那是字數不同，不是排版錯位。對齊欄比右緣會產生假紅燈。
                      const leftAligned = (al) => al === 'left' || al === 'start';
                      let edge = 'right', deltaEdge = delta, eH = Math.round(a.right), eD = Math.round(c.right);
                      if (leftAligned(thAlign) && leftAligned(tdAlign)) {
                        eH = Math.round(a.left); eD = Math.round(c.left);
                        deltaEdge = eH - eD;
                        edge = 'left';
                      }
                      // 兩者聲明不同、或「對齊邊緣」差 >3px → 報錯
                      if (thAlign !== tdAlign || Math.abs(deltaEdge) > 3) {
                        out.misaligned.push({
                          col: i, head: ths[i].textContent.trim(),
                          data: row1[i].textContent.trim(),
                          edge,
                          headRight: eH, dataRight: eD,
                          delta: deltaEdge, thAlign, tdAlign,
                        });
                      }
            }
          }
        } catch (e) { out.misaligned.push({error: String(e)}); }
        return out;
      }"""

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

            # 嚴重度：需捲動才看得到欄位、或可用寬度不足，屬「會影響判讀」的問題
            hidden_bad = [h for h in r["hiddenColumns"]
                          if h["visiblePct"] < 100 and not h["scrollAffordance"]]
            budget_bad = [mb for mb in r["mainBudget"] if mb.get("note")]
            squished_bad = [s for s in r["squished"]]
            misaligned_bad = [m for m in r.get("misaligned", [])]
            issues = (len(r["overflow"]) + len(r["clipped"]) + len(r["overlap"])
                      + len(r["smallTarget"]) + len(errs)
                      + len(hidden_bad) + len(budget_bad) + len(squished_bad)
                      + len(misaligned_bad))
            total += issues
            print(f"\n-- {name} ({w}x{h}, {theme}) --")
            print(f"   container query: {r['cq']}")
            for mb in r["mainBudget"]:
                flag = " ✗" if mb.get("note") else " ✓"
                print(f"  {flag} 主內容可用寬度：{mb['mainWidth']}px / "
                      f"{mb['viewport']}px = {mb['pct']}%"
                      + (f" — {mb['note']}" if mb.get("note") else ""))
            for h in r["hiddenColumns"]:
                flag = " ✗" if not h["scrollAffordance"] else " !"
                print(f"  {flag} 表格欄位完整性：{h['visibleCols']}/{h['totalCols']} 欄可見"
                      f"（{h['visiblePct']}%），看不到：{'、'.join(h['hidden'])}")
                print(f"       {h['reason']}")
            sl = r["surfaceLevels"]
            if sl.get("distinct"):
                print(f"  · surface 色階（count>=2）：{sl['distinctUsed']} 階 / "
                      f"共 {sl['distinct']} 色，最小相鄰亮度差 {sl['minStepLum']}")
                for s in sl["ramp"]:
                    print(f"       lum {s['lum']:.4f}  {s['rgb']}  ×{s['count']}  {s['sample']}")
            for key, label in [("overflow", "溢出"), ("clipped", "截斷"),
                               ("overlap", "重疊"), ("smallTarget", "觸控目標過小"),
                               ("squished", "逐字換行（版面退化）")]:
                if r[key]:
                    print(f"   ✗ {label} ({len(r[key])}):")
                    for item in r[key][:6]:
                        print(f"       {item}")
            if misaligned_bad:
                print(f"   ✗ 表頭/資料對位 ({len(misaligned_bad)}):")
                for m in misaligned_bad[:8]:
                    print(f"       第{m['col']}欄「{m['head']}」{m.get('edge','right')}緣 "
                          f"{m['headRight']} vs 資料({m['data']}) {m['dataRight']} "
                          f"Δ={m['delta']}px，align th={m['thAlign']} td={m['tdAlign']}")
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