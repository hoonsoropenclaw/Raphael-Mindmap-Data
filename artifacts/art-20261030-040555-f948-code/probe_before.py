#!/usr/bin/env python3
"""probe_before.py — 量測「修正前」的窄版版面幾何（2026-10-30 修正前的基準）。

為什麼要有這一支（2026-10-30 修正，第一輪 judge 後補）：

第一輪評審指出 RUNLOG §3「修正前的實測」引用了一支不存在的 `probe_before.py`，
那些數字（.sidebar 216px / .main 204px / 欄位可見 1/5）無法被重跑驗證。
這正是 10-25 已記載的「宣稱本身沒有證據支撐」——寫下了數字卻交不出產生它的工具。

本檔把「修正前」變成**可重現**的：它量測的是 10-29 候選組的 after.html
（`workspace/scout-20261026-hyperui-a11y/deliver-candidate/after.html`），
而不是靠記憶重建一份假設的「修改前」頁面。

用法：
    python3 probe_before.py                    # 量測預設的 10-29 候選組 after.html
    python3 probe_before.py <path/to/after.html>

輸出（JSON，機器可讀）：
    {
      "source": "<被量測的檔案路徑>",
      "sha256": "<被量測檔案的 sha256>",
      "viewports": [
        {"name": "narrow", "width": 420,
         "sidebar_width": 216, "main_width": 204, "main_ratio": 0.486,
         "scroller_client_width": 122, "table_width": 320,
         "columns_visible": 1, "columns_total": 5,
         "scroller_declared": false}
      ],
      "note": "本檔量測的是 10-29 候選組（judge 61.5）的原始版面，作為本次修正的基準。"
    }

檢查類型（code SOP §9-1）：**基準量測**（不是缺陷檢查器，本身永遠回 0）。
它存在的目的只有一個：讓「修正前」的數字可以被第三方重跑驗證。
"""
import hashlib
import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = Path(__file__).parent

# 10-29 候選組的原始產物（本次修正的基準來源）
DEFAULT_TARGET = BASE.parent / "scout-20261026-hyperui-a11y" / "deliver-candidate" / "after.html"

VIEWS = [("narrow", 420, 900), ("wide", 1440, 900)]

JS = r"""
() => {
  const r = (sel) => {
    const el = document.querySelector(sel);
    if (!el) return null;
    const b = el.getBoundingClientRect();
    return {left: Math.round(b.left), right: Math.round(b.right),
            width: Math.round(b.width)};
  };
  const sc = document.querySelector('.table-scroll');
  const t = document.querySelector('table');
  const out = {sidebar: r('.sidebar'), main: r('.main')};
  if (sc) {
    const sr = sc.getBoundingClientRect();
    out.scrollerClientWidth = sc.clientWidth;
    out.scrollerScrollWidth = sc.scrollWidth;
    out.scrollerDeclared = sc.hasAttribute('data-scroll-region')
      && sc.getAttribute('role') === 'region'
      && !!sc.getAttribute('aria-label')
      && sc.getAttribute('tabindex') === '0';
    out.scrollerDeclaredDetail = {
      has_data_scroll_region: sc.hasAttribute('data-scroll-region'),
      role: sc.getAttribute('role'),
      aria_label: sc.getAttribute('aria-label'),
      tabindex: sc.getAttribute('tabindex'),
    };
  }
  if (t) {
    out.tableWidth = Math.round(t.getBoundingClientRect().width);
    const ths = [...t.querySelectorAll('thead th')];
    if (sc) {
      const sr = sc.getBoundingClientRect();
      out.columnsTotal = ths.length;
      out.columnsVisible = ths.filter(th => {
        const b = th.getBoundingClientRect();
        return b.right <= sr.right + 1 && b.left >= sr.left - 1;
      }).length;
    }
  }
  out.mainRatio = +(out.main.width / window.innerWidth).toFixed(3);
  return out;
}
"""


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_TARGET
    target = target.resolve()
    if not target.exists():
        print(f"✗ 找不到基準檔：{target}", file=sys.stderr)
        print("  請傳入 10-29 候選組的 after.html 路徑。", file=sys.stderr)
        return 2

    result = {
        "source": str(target),
        "sha256": sha256_file(target),
        "viewports": [],
        "note": "本檔量測的是 10-29 候選組（judge 61.5）的原始版面，作為本次修正的基準。",
    }

    with sync_playwright() as p:
        b = p.chromium.launch()
        for name, w, h in VIEWS:
            ctx = b.new_context(viewport={"width": w, "height": h})
            pg = ctx.new_page()
            pg.goto(target.as_uri())
            pg.wait_for_timeout(250)
            r = pg.evaluate(JS)
            entry = {"name": name, "width": w}
            entry.update(r)
            result["viewports"].append(entry)
            ctx.close()
        b.close()

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
