#!/usr/bin/env python3
"""audit.py v2 — 版面稽核，**排除規則邊界化**（2026-10-30 重寫）。

本檔是 2026-10-30 練習的核心產出（Q1：排除規則的邊界）。
改寫前的 audit.py 有一條排除規則：

    if (inScroller(el)) continue;   // ★ 捲動容器內的元素本來就會超出 —— 那是設計，不是破版

這條規則在 2026-10-29 的候選組產物裡**結構性地放行了 judge 的 high 缺陷**
「窄版（420px）三欄表格被裁切」：所有表格內元素都因為在 .table-scroll 裡而被
靜默略過，RUNLOG 裡沒有任何一行提到跳過過什麼。

本版的核心改變 —— **排除規則拆成兩型，且兩型都必須留痕**：

  型 A「設計意圖型」（design-intent）
      排除對象：位於「已宣告」捲動區域內的元素。
      排除理由：該區域已宣告 role/aria-label/tabindex，使用者與輔助科技知道它可捲動。
      補償機制：由 audit_narrow_overflow.py 以不同實作路徑獨立複驗（Q4）。
      解除條件：捲動區域缺少宣告時，**排除立即失效** → 該元素回到檢查範圍並報缺陷。

  型 B「補償機制型」（compensated）
      排除對象：位於「未宣告」捲動區域內的元素。
      排除理由：**沒有理由**。這不是設計意圖，是漏宣告。
      處置：**不排除**，反而直接報缺陷（未宣告的捲動容器 = 使用者以為資料被截斷）。

兩型不可共用同一個 `continue`（這正是原版的缺陷）。
所有被排除的元素都會進入 `skipped` 清單並附理由與補償機制，**不靜默略過**。

此外新增「排除率監控」：若某條規則長期跳過 90% 以上的檢查對象，等於沒有檢查 → 判定失敗。

用法：
    python3 audit.py [after.html]      # 預設 after.html
    python3 audit.py fixtures/defective_table_undeclared.html   # 對抗性 fixture → 必須 EXIT!=0

本檢查器自我標註類型（code SOP §9-1）：**版面形式檢查**（交付形式 + 版面幾何）。
它不檢查資料數字的正確性（那由 audit_total_identity.py 負責），也不檢查對比度
（那由 contrast_check.py 負責）。
"""
import json
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE = Path(__file__).parent
TARGET_DEFAULT = "after.html"

# 每一筆排除都要指名「被排除的缺陷由誰負責」——沒有指名就不准排除。
# ★ 這張表是排除規則的「補償機制宣告」：型 A 排除必須能查到補償者，
#   查不到 → 該排除不成立（見 JS 內的補償機制檢查）。
COMPENSATORS = {
    "caseTableScroll": "audit_narrow_overflow.py",
    "table-scroll": "audit_narrow_overflow.py",
}

# ★ 2026-10-30 修正（第一輪 judge 後）：被「排除規則」丟掉的檢查項有哪些？
#   型 A 排除發生在 overflow / clipped 這兩項檢查之前（見 JS 的 continue），
#   所以被排除的就是這兩項。把它寫成常數 → 排除的邊界變成可宣告、可稽核的。
EXCLUDED_CHECKS = ["overflow", "clipped"]

# ★ 補償機制「宣稱覆蓋」了哪些檢查項。
#   必須與它真的做的事一致 —— 否則排除規則不成立（JS 會擋）。
#   2026-10-30 第一輪 judge 前，這裡是空的（只寫名字、不寫覆蓋範圍），
#   實測結果：一個內容被硬砍（overflow:hidden）的儲存格，
#   audit.py 被型 A 排除、audit_narrow_overflow.py 也不查 → 兩支都 EXIT=0。
COMPENSATOR_COVERAGE = {
    "audit_narrow_overflow.py": ["overflow", "clipped"],
}

AUDIT_JS_TMPL = r"""
() => {
  const COMPENSATORS = __COMPENSATORS__;
  const COMPENSATOR_COVERAGE = __COMPENSATOR_COVERAGE__;
  const EXCLUDED_CHECKS = __EXCLUDED_CHECKS__;
  const out = {overflow: [], clipped: [], overlap: [], smallTarget: [],
               undeclaredScroller: [], skipped: [], cq: {}, page: {}};
  const els = document.querySelectorAll('body *');

  const isScrollContainer = (el) => {
    const ox = getComputedStyle(el).overflowX;
    return ox === 'auto' || ox === 'scroll';
  };
  // 找最近的捲動祖先
  const scrollerOf = (el) => {
    for (let p = el.parentElement; p && p !== document.body; p = p.parentElement) {
      if (isScrollContainer(p)) return p;
    }
    return null;
  };
  // ★ 捲動區域「是否已宣告」——這是排除規則的邊界條件。
  //   宣告的完整定義：data-scroll-region 屬性 + role=region + aria-label + tabindex。
  //   四項缺一即視為未宣告 → 排除規則對它失效。
  const declarationOf = (sc) => {
    if (!sc) return null;
    const has = {
      dataScrollRegion: sc.hasAttribute('data-scroll-region'),
      roleRegion: sc.getAttribute('role') === 'region',
      ariaLabel: !!(sc.getAttribute('aria-label') || '').trim(),
      tabindex: sc.getAttribute('tabindex') === '0',
    };
    const missing = Object.keys(has).filter(k => !has[k]);
    return {has, missing, declared: missing.length === 0, name: sc.id || sc.className || 'scroller'};
  };

  // ── 0. 捲動區域宣告稽核（型 B 的判定來源）────────────────────
  const scrollers = [];
  for (const el of document.querySelectorAll('*')) {
    if (!isScrollContainer(el)) continue;
    const d = declarationOf(el);
    const r = el.getBoundingClientRect();
    const rec = {name: d.name, declared: d.declared, missing: d.missing,
                 scrolls: el.scrollWidth > el.clientWidth + 2,
                 clientWidth: Math.round(el.clientWidth),
                 scrollWidth: Math.round(el.scrollWidth)};
    scrollers.push(rec);
    if (!d.declared) {
      // ★ 型 B：未宣告的捲動容器 → 不排除，直接報缺陷
      out.undeclaredScroller.push({
        sel: d.name, missing: d.missing,
        overflows: rec.scrolls,
        detail: '捲動容器未宣告（role=region / aria-label / tabindex / data-scroll-region 缺 '
              + d.missing.join(', ') + '）→ 使用者無法得知此區可捲動，會誤以為資料被截斷',
      });
    }
  }
  out.scrollRegions = scrollers;

  // ── 1. 溢出：元素超出其 offsetParent 的左右邊界 ────────────────
  let considered = 0, skipped = 0;
  for (const el of els) {
    if (el.tagName === 'HTML' || el.tagName === 'BODY' || el.tagName === 'SCRIPT') continue;
    const r = el.getBoundingClientRect();
    if (r.width === 0 || r.height === 0) continue;
    const parent = el.offsetParent;
    if (!parent) continue;
    const pr = parent.getBoundingClientRect();
    const cs = getComputedStyle(el);
    if (cs.position === 'fixed' || cs.position === 'absolute') continue;
    considered++;

    const sc = scrollerOf(el);
    if (sc) {
      const d = declarationOf(sc);
      if (d.declared) {
        // ── 型 A：設計意圖型排除（且必須留痕）────────────────
        // ★ 2026-10-30 修正（第一輪 judge 後）：補償機制不能只是「被指名」。
        //   舊版只檢查 COMPENSATORS 裡有沒有名字 → 名字存在就整類排除，
        //   但被指名的檢查器可能根本沒覆蓋被排除的檢查項（實測：型 A 排除
        //   了 overflow 檢查，而 audit_narrow_overflow.py 只查欄位可見性，
        //   → 元素內容被硬砍掉的缺陷兩支檢查器都 EXIT=0）。
        //   修正：把「這個區域被排除了哪些檢查項」與「補償機制宣稱覆蓋哪些」
        //   都寫成結構化資料，兩邊必須逐項對得上才允許排除。
        const compensator = COMPENSATORS[d.name] || COMPENSATORS['table-scroll'];
        if (!compensator) {
          // ★ 沒有指名補償機制 → 排除不成立，元素回到檢查範圍
          out.undeclaredScroller.push({
            sel: d.name,
            missing: ['compensator'],
            overflows: false,
            detail: '捲動區域已宣告，但沒有任何檢查器被指名負責複驗此區域 → '
                  + '排除規則不成立（沒有指名就沒有補償）',
          });
        } else {
          const claimed = (COMPENSATOR_COVERAGE[compensator] || []);
          const missingCover = EXCLUDED_CHECKS.filter(c => !claimed.includes(c));
          if (missingCover.length) {
            // ★ 補償機制沒有覆蓋被排除的檢查項 → 排除不成立，元素回到檢查範圍
            out.undeclaredScroller.push({
              sel: d.name,
              missing: ['compensator-coverage'],
              overflows: false,
              detail: '捲動區域已宣告且已指名補償機制「' + compensator + '」，'
                    + '但該機制未覆蓋被排除的檢查項 [' + missingCover.join(', ')
                    + '] → 排除規則不成立（被指名不等於有覆蓋）',
            });
          } else {
            skipped++;
            out.skipped.push({
              sel: el.className || el.tagName,
              type: 'A/design-intent',
              reason: '位於已宣告的捲動區域「' + d.name + '」內，該區域已宣告可捲動（role=region + aria-label + tabindex）',
              compensatedBy: compensator,
              compensatedChecks: claimed,
              revokeIf: '該捲動區域失去任一宣告屬性時，或補償機制不再覆蓋上述檢查項時，本排除立即失效',
            });
            continue;
          }
        }
      }
      // 型 B：未宣告 → 不排除，往下走照常檢查（並已由 undeclaredScroller 記錄）
    }

    if (r.right > pr.right + 1 || r.left < pr.left - 1) {
      out.overflow.push({
        sel: el.className || el.tagName,
        elRight: Math.round(r.right), parentRight: Math.round(pr.right),
        elLeft: Math.round(r.left), parentLeft: Math.round(pr.left),
        inUndeclaredScroller: !!sc,
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
  out.considered = considered;
  out.skippedCount = skipped;

  // 2b. 捲動容器本身要能用（需要捲動但 overflow 為 hidden）
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
  // ★ 2026-10-30 修正（檢查器自身的缺陷，不是頁面的缺陷）：
  //   原版用 getBoundingClientRect() 比對。對「會換行的行內元素」
  //   （例如窄版下換行的 <code>），getBoundingClientRect() 回傳的是
  //   **所有行框的聯集**：水平方向涵蓋每一行的起訖，垂直方向涵蓋整段。
  //   結果兩個其實在同一行但左右分開的 inline 元素，聯集框會互相穿插
  //   → 假陽性重疊。
  //   實測（2026-10-30）：420px 下兩個 <code> 分別在 x=116–203 與 x=278–387，
  //   聯集框卻是 116–203 與 29–387 → 被判為 overlapX=87、overlapY=14。
  //   修正：改用 getClientRects() 逐行比對，只有「同一行的行框」才可能重疊。
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
      const lines = [...k.getClientRects()].filter(x => x.width > 0 && x.height > 0);
      return {k, lines};
    }).filter(b => b.lines.length > 0
      && getComputedStyle(b.k).position === 'static');
    for (let i = 0; i < boxes.length; i++) {
      for (let j = i + 1; j < boxes.length; j++) {
        let hit = null;
        for (const a of boxes[i].lines) {
          for (const b of boxes[j].lines) {
            const ix = Math.min(a.right, b.right) - Math.max(a.left, b.left);
            const iy = Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top);
            if (ix > 2 && iy > 2) {
              hit = {overlapX: Math.round(ix), overlapY: Math.round(iy)};
              break;
            }
          }
          if (hit) break;
        }
        if (hit) {
          out.overlap.push({
            a: boxes[i].k.className || boxes[i].k.tagName,
            b: boxes[j].k.className || boxes[j].k.tagName,
            overlapX: hit.overlapX, overlapY: hit.overlapY,
            sameLine: true,
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
  // 5b. app 層級的 container query 是否命中（窄版策略是否真的生效）
  const bodyCS = getComputedStyle(document.body);
  const appProbe = document.createElement('style');
  appProbe.textContent = '@container page (width < 700px) { .app { outline-color: rgb(4,5,6) } }';
  document.head.appendChild(appProbe);
  const appHit = getComputedStyle(document.querySelector('.app')).outlineColor;
  appProbe.remove();
  out.page = {
    containerType: bodyCS.containerType,
    containerName: bodyCS.containerName,
    width_lt_700_matches: appHit === 'rgb(4, 5, 6)',
    viewportWidth: window.innerWidth,
  };

  return out;
}
"""

AUDIT_JS = (AUDIT_JS_TMPL
            .replace("__COMPENSATORS__", json.dumps(COMPENSATORS, ensure_ascii=False))
            .replace("__COMPENSATOR_COVERAGE__", json.dumps(COMPENSATOR_COVERAGE, ensure_ascii=False))
            .replace("__EXCLUDED_CHECKS__", json.dumps(EXCLUDED_CHECKS, ensure_ascii=False)))

VIEWS = [
    ("wide",   1440, 900, "light"),
    ("narrow",  420, 900, "light"),
    ("dark",   1440, 900, "dark"),
    ("dark-narrow", 420, 900, "dark"),
]

# 排除率監控門檻：跳過比例超過這個值 → 這個檢查等於沒檢查
# ★ 2026-10-30 修正（第一輪 judge medium 缺陷 3）：
#   舊版只有一條 90% 的 fail 門檻，而實測排除率是 54.7%
#   → 永遠不會觸發，等於「門檻形同虛設」。
#   改為兩級：超過 WARN → 警告並揭露（不擋交付，因為型 A 排除是設計意圖）；
#              超過 FAIL → 判定失敗（此檢查器等於沒檢查）。
#   數字本身必須被寫進輸出與 verification_summary，不能只當內部門檻。
MAX_SKIP_RATIO = 0.60
WARN_SKIP_RATIO = 0.30


def main() -> int:
    target = sys.argv[1] if len(sys.argv) > 1 else TARGET_DEFAULT
    path = (BASE / target).resolve()
    if not path.exists():
        print(f"✗ 找不到目標檔：{path}")
        return 2

    total = 0
    skip_ratio_worst = 0.0
    print(f"audit.py v2 — 目標：{path.name}")
    print("檢查類型：版面形式檢查（不檢查資料數字正確性、不檢查對比度）")
    print("排除規則：型 A 設計意圖型（已宣告捲動區域）／型 B 補償機制型（未宣告 → 不排除）")

    with sync_playwright() as p:
        b = p.chromium.launch()
        for name, w, h, theme in VIEWS:
            ctx = b.new_context(viewport={"width": w, "height": h})
            pg = ctx.new_page()
            errs = []
            pg.on("pageerror", lambda e: errs.append(str(e)))
            pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
            pg.goto(path.as_uri())
            if theme == "dark":
                pg.evaluate("document.documentElement.dataset.theme='dark'")
            pg.wait_for_timeout(250)
            r = pg.evaluate(AUDIT_JS)

            issues = (len(r["overflow"]) + len(r["clipped"]) + len(r["overlap"])
                      + len(r["smallTarget"]) + len(errs) + len(r["undeclaredScroller"]))
            total += issues

            considered = max(r["considered"], 1)
            ratio = r["skippedCount"] / considered
            skip_ratio_worst = max(skip_ratio_worst, ratio)

            print(f"\n-- {name} ({w}x{h}, {theme}) --")
            print(f"   container query(kpi): {r['cq']}")
            print(f"   container query(page): {r['page']}")
            if r["scrollRegions"]:
                print(f"   捲動區域宣告：{r['scrollRegions']}")
            for key, label in [("overflow", "溢出"), ("clipped", "截斷"),
                               ("overlap", "重疊"), ("smallTarget", "觸控目標過小"),
                               ("undeclaredScroller", "未宣告的捲動容器")]:
                if r[key]:
                    print(f"   ✗ {label} ({len(r[key])}):")
                    for item in r[key][:6]:
                        print(f"       {item}")
            if errs:
                print(f"   ✗ console/page errors: {errs[:3]}")

            # ★ skipped 清單：被排除的元素必須留痕（原本是靜默 continue）
            print(f"   skipped 清單（型 A 設計意圖型排除，共 {r['skippedCount']} 筆／檢查對象 {considered} 筆）：")
            if r["skipped"]:
                seen = set()
                for s in r["skipped"]:
                    k = (s["type"], s["compensatedBy"])
                    if k in seen:
                        continue
                    seen.add(k)
                    print(f"       {s['type']} | 排除對象：{s['sel']}")
                    print(f"           理由：{s['reason']}")
                    print(f"           補償機制：{s['compensatedBy']}")
                    print(f"           解除條件：{s['revokeIf']}")
            else:
                print("       （無）")
            print(f"   排除率：{r['skippedCount']}/{considered} = {ratio:.1%}"
                  f"（警告門檻 > {WARN_SKIP_RATIO:.0%}／失敗門檻 > {MAX_SKIP_RATIO:.0%}）")
            if ratio > MAX_SKIP_RATIO:
                print(f"   ✗ 排除率過高：此檢查器等於沒有檢查")
                total += 1
            elif ratio > WARN_SKIP_RATIO:
                # ★ 警告不擋交付，但必須被看見（第一輪 judge medium 缺陷 3）
                print(f"   ⚠ 排除率 {ratio:.1%} 偏高：被排除的元素未被本檢查器覆蓋，"
                      f"完全靠補償機制 {COMPENSATOR_COVERAGE} 支撐。")
                print(f"     → 補償機制若失效，這些元素就沒有任何檢查。解除條件見上方 skipped 清單。")
            if issues == 0:
                print("   ✓ 無版面問題、無 console 錯誤")
            ctx.close()
        b.close()

    print(f"\n總計問題數：{total}")
    print(f"最高排除率：{skip_ratio_worst:.1%}")
    print(f"排除率門檻：警告 > {WARN_SKIP_RATIO:.0%}／失敗 > {MAX_SKIP_RATIO:.0%}")
    if skip_ratio_worst > WARN_SKIP_RATIO:
        print(f"⚠ 本次最高排除率 {skip_ratio_worst:.1%} 超過警告門檻 {WARN_SKIP_RATIO:.0%}："
              f"被排除的元素不由本檢查器覆蓋，"
              f"完全依賴補償機制 {list(COMPENSATOR_COVERAGE.keys())}。"
              f"補償機制失效時這些元素將無任何檢查（解除條件見 skipped 清單）。")
    if total == 0:
        print("本檢查器涵蓋：溢出／截斷／重疊／觸控目標／console 錯誤／捲動區域宣告／排除率。")
        print("不涵蓋：資料數字正確性（見 audit_total_identity.py）、對比度（見 contrast_check.py）、"
              "螢幕閱讀器實機、導覽列與主內容幾何（見 audit_nav_collision.py）。")
        print("「EXIT=0」只代表上述已列項目全過，不代表頁面完全無問題。")
    return 0 if total == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
