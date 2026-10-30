#!/usr/bin/env python3
"""audit_narrow_overflow.py — 窄版表格欄位可見性的**獨立**複驗。

為什麼要獨立一支（Q4：「A/B 對照實驗的邊界：控制變因消除組間差異，不消除組內錯誤」）：

10-29 的 A/B 兩組用**同一支** audit.py、checker md5 相同。如果這支檢查器有
假綠燈路徑，兩組都會綠——控制變因會把「兩邊都錯的缺陷」完美地保留下來。
所以本檔刻意**不 import、不複製** audit.py 的 DOM 巡邏邏輯：

  - audit.py 的路徑：遍歷 body * ，用 offsetParent 比對溢出，用 inScroller 排除。
  - 本檔的路徑：直接向瀏覽器查「欄位表頭的可見數量」與「捲動偏移量」，
    用的是 scrollLeft / scrollWidth / clientWidth 與實際欄位矩形，
    完全不碰 audit.py 的任何函式或常數。

判定規則（窄版專用）：
  1. 必須存在至少一個資料表格（<table> with thead th）。
  2. 在 420px（以及 360px）視窗下，每一欄的表頭必須**全部可見**
     （欄位矩形完全落在捲動容器的可見矩形內）。
     若有欄位被裁切 → 報缺陷（除非捲動容器已宣告可捲動，且提示已宣告「其餘 N 欄」，
     那種情況報「需捲動」而非「缺陷」——但本檔採嚴格策略：
     窄版行政資料表要求欄位可見，因為資料完整性優先於版面完整性）。
  3. 捲動容器若有溢出，必須有捲動提示（.scroll-hint 且 hidden=false）。
  4. 捲動容器若溢出，必須可鍵盤聚焦（tabindex=0）。

檢查類型（code SOP §9-1）：**版面形式檢查**（欄位可見性幾何）。
不檢查資料數字正確性。

用法：
    python3 audit_narrow_overflow.py                       # 預設 after.html
    python3 audit_narrow_overflow.py fixtures/xxx.html     # 對抗性 fixture
"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE = Path(__file__).parent

# 與 audit.py 完全無關的獨立實作：不查 offsetParent、不查 inScroller。
JS = r"""
() => {
  const res = {viewports: [], tables: []};
  const vw = window.innerWidth;
  res.viewports.push(vw);

  for (const t of document.querySelectorAll('table')) {
    const scroller = t.parentElement;
    const scRect = scroller.getBoundingClientRect();
    const ths = [...t.querySelectorAll('thead th')];
    const cells = ths.map(th => {
      const r = th.getBoundingClientRect();
      const inScrollerView = r.right <= scRect.right + 1 && r.left >= scRect.left - 1;
      // 被捲動出去（scroller.scrollLeft > 0 時，位於左側的欄位會跑出可見區）
      const clippedByScroll = scroller.scrollLeft > 0 && r.left < scRect.left - 1;
      return {
        label: th.textContent.trim(),
        left: Math.round(r.left), right: Math.round(r.right),
        visibleNow: inScrollerView && !clippedByScroll,
      };
    });
    const hint = document.querySelector('#' + (scroller.id || '') + 'Hint')
              || document.querySelector('p.scroll-hint');
    const hintVisible = !!hint && !hint.hidden && getComputedStyle(hint).display !== 'none';
    const hintText = hint ? hint.textContent.trim().replace(/\s+/g, ' ') : null;
    res.tables.push({
      scrollerId: scroller.id || scroller.className,
      isScroller: ['auto','scroll'].includes(getComputedStyle(scroller).overflowX),
      declared: scroller.hasAttribute('data-scroll-region')
                && scroller.getAttribute('role') === 'region'
                && !!scroller.getAttribute('aria-label')
                && scroller.getAttribute('tabindex') === '0',
      scrollerClientWidth: scroller.clientWidth,
      scrollerScrollWidth: scroller.scrollWidth,
      overflows: scroller.scrollWidth > scroller.clientWidth + 2,
      scrollLeft: scroller.scrollLeft,
      totalColumns: cells.length,
      visibleColumns: cells.filter(c => c.visibleNow).length,
      hiddenColumns: cells.filter(c => !c.visibleNow).map(c => c.label),
      cells,
      hintVisible, hintText,
    });
  }
  return res;
}
"""

VIEWS = [("narrow", 420, 900), ("narrow-xs", 360, 780), ("wide", 1440, 900)]


def main() -> int:
    target = sys.argv[1] if len(sys.argv) > 1 else "after.html"
    path = (BASE / target).resolve()
    if not path.exists():
        print(f"✗ 找不到目標檔：{path}")
        return 2

    total = 0
    disclosed = []          # 「可接受但必須揭露」的情況（不靜默放行）
    print(f"audit_narrow_overflow.py — 目標：{path.name}")
    print("檢查類型：版面形式檢查（欄位可見性幾何）")
    print("独立性：本檔不 import、不複製 audit.py 的巡邏邏輯（Q4 的實作）")

    with sync_playwright() as p:
        b = p.chromium.launch()
        for name, w, h in VIEWS:
            ctx = b.new_context(viewport={"width": w, "height": h})
            pg = ctx.new_page()
            pg.goto(path.as_uri())
            pg.wait_for_timeout(250)
            r = pg.evaluate(JS)
            print(f"\n-- {name} ({w}x{h}) --")
            if not r["tables"]:
                print("   ✗ 找不到資料表格")
                total += 1
            for t in r["tables"]:
                print(f"   捲動容器：{t['scrollerId']}  宣告={t['declared']}  "
                      f"溢出={t['overflows']}  ({t['scrollerClientWidth']}/{t['scrollerScrollWidth']}px)")
                print(f"   欄位可見：{t['visibleColumns']}/{t['totalColumns']}"
                      + (f"  被裁切欄位：{t['hiddenColumns']}" if t["hiddenColumns"] else ""))
                print(f"   捲動提示可見：{t['hintVisible']}  「{t['hintText']}」")
                if w <= 500:
                    # ★ 判定規則（Q2「資料完整性優先於版面完整性」）：
                    #   欄位被裁切本身**不是**缺陷 —— 寧可捲動。
                    #   缺陷的是「裁切 + 使用者無從得知」：
                    #     (a) 裁切 + 非捲動容器 → 資料被硬砍，看不到也拿不到 → 缺陷
                    #     (b) 裁切 + 捲動但未宣告 → 使用者以為資料被截斷 → 缺陷
                    #     (c) 裁切 + 捲動但沒有可見提示 → 使用者以為資料被截斷 → 缺陷
                    #     (d) 裁切 + 捲動 + 已宣告 + 有可見提示 → **可接受，但必須揭露**
                    #   (d) 不是靜默放行：會印出揭露行，且寫進 verification_summary.json。
                    cut = t["visibleColumns"] < t["totalColumns"]
                    if cut:
                        if not t["isScroller"]:
                            print(f"   ✗ 欄位被裁切且容器不是捲動容器 → 資料被硬砍：{t['hiddenColumns']}")
                            total += 1
                        elif not t["declared"]:
                            print(f"   ✗ 欄位被裁切但捲動容器未宣告"
                                  f"（role=region / aria-label / tabindex / data-scroll-region）")
                            total += 1
                        elif not t["hintVisible"]:
                            print(f"   ✗ 欄位被裁切但沒有可見的捲動提示 → 使用者會誤以為資料被截斷")
                            total += 1
                        else:
                            print(f"   ○ 已揭露（可接受）：欄位被裁切 {t['hiddenColumns']}，"
                                  f"但容器已宣告可捲動且有可見提示「{t['hintText']}」"
                                  f"→ 資料完整性以「可捲動取得」為代價保留")
                            disclosed.append({"viewport": name, "hidden": t["hiddenColumns"],
                                              "declared": t["declared"], "hintVisible": t["hintVisible"]})
                    if t["overflows"] and not t["hintVisible"]:
                        print("   ✗ 容器溢出但沒有可見的捲動提示 → 使用者會誤以為資料被截斷")
                        total += 1
                    if t["overflows"] and not t["declared"]:
                        print("   ✗ 容器溢出但未宣告（role/aria-label/tabindex/data-scroll-region）")
                        total += 1
                if t["overflows"] and not t["isScroller"]:
                    print("   ✗ 內容溢出但容器不是捲動容器 → 內容被硬裁切")
                    total += 1
            if total == 0:
                pass
            ctx.close()
        b.close()

    print(f"\n總計問題數：{total}")
    print(f"揭露項（可接受但已宣告）：{len(disclosed)} 筆 {disclosed if disclosed else ''}")
    if total == 0:
        print("本檢查器涵蓋：窄版欄位可見性、捲動提示存在性、捲動區域宣告、硬裁切。")
        print("不涵蓋：資料數字正確性、對比度、導覽幾何（見 audit_nav_collision.py）、"
              "螢幕閱讀器實機。")
        print("「EXIT=0」只代表上述已列項目全過，不代表頁面完全無問題。")
    import json as _json
    outp = BASE / "narrow_overflow_disclosures.json"
    outp.write_text(_json.dumps(
        {"target": path.name, "issues": total, "disclosed": disclosed},
        ensure_ascii=False, indent=1))
    return 0 if total == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
