#!/usr/bin/env python3
"""audit_nav_collision.py — 導覽列與主內容的幾何碰撞檢查。

對應 10-29 judge 的另一筆 high 缺陷：「左側導覽欄（約 200px）與主內容區重疊」。

這支檢查器的判準與 audit.py 的「同層兄弟重疊」**不同**：
audit.py 只比對「同一個 parent 下的兄弟元素」，而 sidebar 與 main 是
`.app` 下的兩個**不同類型**的區塊容器（而且寬版時是並排、窄版時是上下堆疊）。
所以這支檢查器直接量「導覽區與主內容區的矩形是否相交」。

另外這支檢查器會驗一個更重要的命題：**窄版時主內容必須拿到足夠的寬度**。
10-29 的實測（probe，420px）：.sidebar 216px / .main 204px → 主內容只拿到視窗的 48.6%，
表格的捲動容器只剩 122px，320px 的表格只能看到 1/5 欄。
→ 光「不重疊」不夠，還要檢查「主內容沒有被導覽擠壓到不可用」。

檢查類型（code SOP §9-1）：**版面形式檢查**（區塊幾何配置）。

用法：
    python3 audit_nav_collision.py                  # 預設 after.html
    python3 audit_nav_collision.py fixtures/xxx.html
"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE = Path(__file__).parent

# 窄版時主內容至少要拿到視窗寬度的這個比例（低於此值視為被導覽擠壓）
MIN_MAIN_RATIO = 0.85

JS = r"""
() => {
  const rect = (el) => {
    if (!el) return null;
    const r = el.getBoundingClientRect();
    return {left: Math.round(r.left), right: Math.round(r.right),
            top: Math.round(r.top), bottom: Math.round(r.bottom),
            width: Math.round(r.width), height: Math.round(r.height)};
  };
  const sidebar = document.querySelector('.sidebar');
  const main = document.querySelector('.main');
  const nav = document.querySelector('.nav');
  const items = [...document.querySelectorAll('.nav-item')];
  const app = document.querySelector('.app');
  return {
    viewport: {w: window.innerWidth, h: window.innerHeight},
    docScrollWidth: document.documentElement.scrollWidth,
    pageHScroll: document.documentElement.scrollWidth > window.innerWidth + 1,
    sidebar: rect(sidebar),
    main: rect(main),
    nav: rect(nav),
    app: rect(app),
    appFlexDirection: app ? getComputedStyle(app).flexDirection : null,
    navItemCount: items.length,
    navItemHeights: items.map(a => Math.round(a.getBoundingClientRect().height)),
    navItemTops: items.map(a => Math.round(a.getBoundingClientRect().top)),
    // ★ 修正：main 是元素、不是 rect；元素沒有 .width 屬性 → NaN。
    //   這個 NaN 讓「窄版主內容佔比」這條檢查**永遠不觸發**（NaN < 門檻 為 False），
    //   等於一條假綠燈。實測：修正前 nav_collision 對擠壓缺陷回 EXIT=0。
    mainRatio: main
      ? +(main.getBoundingClientRect().width / window.innerWidth).toFixed(3)
      : null,
  };
}
"""

VIEWS = [("wide", 1440, 900), ("narrow", 420, 900), ("narrow-xs", 360, 780)]


def main() -> int:
    target = sys.argv[1] if len(sys.argv) > 1 else "after.html"
    path = (BASE / target).resolve()
    if not path.exists():
        print(f"✗ 找不到目標檔：{path}")
        return 2

    total = 0
    print(f"audit_nav_collision.py — 目標：{path.name}")
    print("檢查類型：版面形式檢查（區塊幾何配置）")

    with sync_playwright() as p:
        b = p.chromium.launch()
        for name, w, h in VIEWS:
            ctx = b.new_context(viewport={"width": w, "height": h})
            pg = ctx.new_page()
            pg.goto(path.as_uri())
            pg.wait_for_timeout(250)
            r = pg.evaluate(JS)
            print(f"\n-- {name} ({w}x{h}) --")
            print(f"   app flex-direction：{r['appFlexDirection']}")
            print(f"   sidebar：{r['sidebar']}")
            print(f"   main：{r['main']}")
            print(f"   主內容佔視窗寬度：{r['mainRatio']}")

            # 1. 導覽與主內容不得相交
            if r["sidebar"] and r["main"]:
                ix = min(r["sidebar"]["right"], r["main"]["right"]) - max(r["sidebar"]["left"], r["main"]["left"])
                iy = min(r["sidebar"]["bottom"], r["main"]["bottom"]) - max(r["sidebar"]["top"], r["main"]["top"])
                if ix > 2 and iy > 2:
                    print(f"   ✗ 導覽欄與主內容重疊（overlapX={ix}, overlapY={iy}）")
                    total += 1
                else:
                    print(f"   ✓ 導覽欄與主內容無交集（ix={ix}, iy={iy}）")

            # 2. 窄版主內容不得被擠壓
            if w <= 500 and r["mainRatio"] is not None and r["mainRatio"] < MIN_MAIN_RATIO:
                print(f"   ✗ 窄版主內容只拿到視窗的 {r['mainRatio']:.1%}"
                      f"（門檻 {MIN_MAIN_RATIO:.0%}）→ 主內容被導覽擠壓到不可用")
                total += 1

            # 3. 整頁不得有水平捲動（WCAG 1.4.10 Reflow）
            if r["pageHScroll"]:
                print(f"   ✗ 整頁出現水平捲動（docScrollWidth={r['docScrollWidth']} > {w}）"
                      f"→ 違反 1.4.10 Reflow（頁面層級橫向捲動不可）")
                total += 1

            # 4. 導覽項目必須全部可達且不小於 24px
            small = [h for h in r["navItemHeights"] if h < 24]
            if small:
                print(f"   ✗ 導覽項目高度 < 24px：{small}")
                total += 1
            if r["navItemCount"] == 0:
                print("   ✗ 找不到導覽項目")
                total += 1
            ctx.close()
        b.close()

    print(f"\n總計問題數：{total}")
    if total == 0:
        print("本檢查器涵蓋：導覽/主內容相交、窄版主內容佔比、整頁水平捲動、導覽目標大小。")
        print("不涵蓋：表格欄位可見性（見 audit_narrow_overflow.py）、資料數字、對比度、"
              "螢幕閱讀器實機。")
        print("「EXIT=0」只代表上述已列項目全過，不代表頁面完全無問題。")
    return 0 if total == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
