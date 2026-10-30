#!/usr/bin/env python3
"""build.py — 產生截圖與機器可讀摘要（code SOP §8：數字必須機器回算）。

這支腳本是**唯一**的數字來源：
- 截圖：4 張視窗 × 主題（亮/暗 × 寬/窄）
- verification_summary.json：每支檢查器的 exit code、關鍵計數、對帳等式三個數字
- manifest.json：由**交付集合反推**（10-29 Q2 卡的實作），不是掃工作目錄

RUNLOG.md 與 artifact notes 一律引用本檔產出的欄位，不手抄（§8-2）。
"""
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE = Path(__file__).parent
TARGET = BASE / "after.html"

CHECKERS = [
    ("audit.py", 240),
    ("audit_narrow_overflow.py", 240),
    ("audit_nav_collision.py", 240),
    ("audit_total_identity.py", 200),
    ("a11y_check.py", 200),
    ("contrast_check.py", 200),
]

SHOTS = [
    ("after-wide.png", 1440, 900, "light"),
    ("after-narrow.png", 420, 900, "light"),
    ("after-dark.png", 1440, 900, "dark"),
    ("after-dark-narrow.png", 420, 900, "dark"),
]


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def run_checkers():
    results = {}
    for name, tmo in CHECKERS:
        cmd = ["python3", name, "after.html"]
        try:
            r = subprocess.run(cmd, cwd=BASE, capture_output=True, text=True, timeout=tmo)
            rc, out = r.returncode, (r.stdout + r.stderr)
        except subprocess.TimeoutExpired:
            rc, out = 124, "TIMEOUT"
        entry = {"exit_code": rc}
        # 各檢查器的關鍵計數（全部由程式解析，不手抄）
        m = re.search(r"總計問題數：(\d+)", out)
        if m:
            entry["issues"] = int(m.group(1))
        m = re.search(r"最高排除率：([\d.]+)%", out)
        if m:
            entry["max_skip_ratio_pct"] = float(m.group(1))
        m = re.search(r"被抓住：(\d+) 筆　漏抓：(\d+) 筆", out)
        if m:
            entry["fixtures_caught"] = int(m.group(1))
            entry["fixtures_missed"] = int(m.group(2))
        m = re.search(r"雙向通過：(\d+) 組　失敗：(\d+) 組", out)
        if m:
            entry["bidi_passed"] = int(m.group(1))
            entry["bidi_failed"] = int(m.group(2))
        m = re.search(r"發現 (\d+) 項（阻擋 (\d+)／建議 (\d+)）", out)
        if m:
            entry["a11y_findings"] = int(m.group(1))
            entry["a11y_blocking"] = int(m.group(2))
            entry["a11y_suggestions"] = int(m.group(3))
        m = re.search(r"(\d+)/(\d+) 通過", out)
        if m:
            entry["contrast_passed"] = int(m.group(1))
            entry["contrast_total"] = int(m.group(2))
        m = re.search(r"✓ 對帳等式成立：總計 ([\d,]+) = Σ 分組合計 ([\d,]+) = Σ 明細值 ([\d,]+)", out)
        if m:
            entry["total_identity"] = {
                "declared_total": int(m.group(1).replace(",", "")),
                "sum_of_groups": int(m.group(2).replace(",", "")),
                "sum_of_details": int(m.group(3).replace(",", "")),
            }
        m = re.search(r"排除對象：(\S+)", out)
        if m:
            entry["excluded_sample"] = m.group(1)
        m = re.search(r"補償機制：(\S+)", out)
        if m:
            entry["compensated_by"] = m.group(1)
        results[name] = entry
    return results


def measure_geometry():
    """窄版與寬版的實際幾何（來自 probe，不手抄）"""
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
      const sr = sc.getBoundingClientRect();
      const cells = [...t.querySelectorAll('thead th')].map(th => {
        const b = th.getBoundingClientRect();
        return {label: th.textContent.trim(),
                visible: b.right <= sr.right + 1 && b.left >= sr.left - 1};
      });
      const hint = document.getElementById('caseTableScrollHint');
      return {
        viewportWidth: window.innerWidth,
        sidebar: r('.sidebar'), main: r('.main'),
        mainRatio: +(document.querySelector('.main').getBoundingClientRect().width
                     / window.innerWidth).toFixed(3),
        scrollerClientWidth: sc.clientWidth, scrollerScrollWidth: sc.scrollWidth,
        tableWidth: Math.round(t.getBoundingClientRect().width),
        columnsTotal: cells.length,
        columnsVisible: cells.filter(c => c.visible).length,
        columnsHidden: cells.filter(c => !c.visible).map(c => c.label),
        scrollHintVisible: !!hint && !hint.hidden,
        scrollHintText: hint ? hint.textContent.trim().replace(/\s+/g,' ') : null,
        scrollerDeclared: sc.hasAttribute('data-scroll-region')
          && sc.getAttribute('role') === 'region'
          && !!sc.getAttribute('aria-label')
          && sc.getAttribute('tabindex') === '0',
        pageHorizontalScroll: document.documentElement.scrollWidth > window.innerWidth + 1,
      };
    }
    """
    out = {}
    with sync_playwright() as p:
        b = p.chromium.launch()
        for name, w, h, theme in SHOTS:
            ctx = b.new_context(viewport={"width": w, "height": h})
            pg = ctx.new_page()
            pg.goto(TARGET.as_uri())
            if theme == "dark":
                pg.evaluate("document.documentElement.dataset.theme='dark'")
            pg.wait_for_timeout(300)
            out[f"{name.replace('.png','')}"] = pg.evaluate(JS)
            ctx.close()
        b.close()
    return out


def take_screenshots():
    files = []
    with sync_playwright() as p:
        b = p.chromium.launch()
        for fname, w, h, theme in SHOTS:
            ctx = b.new_context(viewport={"width": w, "height": h},
                                device_scale_factor=2)
            pg = ctx.new_page()
            pg.goto(TARGET.as_uri())
            if theme == "dark":
                pg.evaluate("document.documentElement.dataset.theme='dark'")
            pg.wait_for_timeout(400)
            out = BASE / fname
            pg.screenshot(path=str(out), full_page=True)
            files.append(fname)
            print(f"  截圖：{fname}  ({w}x{h}, {theme})  {out.stat().st_size} bytes")
            ctx.close()
        b.close()
    return files


def main() -> int:
    print("── 1. 產生截圖 ──")
    shots = take_screenshots()

    print("\n── 2. 執行全部檢查器 ──")
    checkers = run_checkers()
    for k, v in checkers.items():
        print(f"  {k}: EXIT={v['exit_code']}")

    print("\n── 3. 量測幾何 ──")
    geom = measure_geometry()
    for k, v in geom.items():
        print(f"  {k}: main={v['main']['width']}px ({v['mainRatio']:.1%})  "
              f"欄位可見={v['columnsVisible']}/{v['columnsTotal']}")

    print("\n── 4. 對抗性 fixture 與雙向回歸 ──")
    r = subprocess.run(["bash", "run_checks.sh", "after.html"],
                       cwd=BASE, capture_output=True, timeout=1800)
    # ★ 不用 text=True：run_checks.sh 裡的 `cut -c1-160` 會把 UTF-8 字元切成
    #   不完整位元組 → decode 失敗（UnicodeDecodeError）。改用 errors="replace"。
    out = r.stdout.decode("utf-8", errors="replace")
    m = re.search(r"被抓住：(\d+) 筆　漏抓：(\d+) 筆", out)
    fixtures = {"caught": int(m.group(1)), "missed": int(m.group(2))} if m else {}
    m = re.search(r"雙向通過：(\d+) 組　失敗：(\d+) 組", out)
    bidi = {"passed": int(m.group(1)), "failed": int(m.group(2))} if m else {}
    m = re.search(r"殘留旗標數：(\d+)", out)
    flags = int(m.group(1)) if m else None
    print(f"  fixture 被抓住 {fixtures.get('caught')}／漏抓 {fixtures.get('missed')}")
    print(f"  雙向通過 {bidi.get('passed')}／失敗 {bidi.get('failed')}")
    print(f"  §6 殘留旗標數 {flags}")

    # ── 交付集合（manifest 由交付集合反推，不是掃工作目錄）──
    DELIVERABLES = [
        "after.html", "after-wide.png", "after-narrow.png",
        "after-dark.png", "after-dark-narrow.png",
        "audit.py", "audit_narrow_overflow.py", "audit_nav_collision.py",
        "audit_total_identity.py", "a11y_check.py", "contrast_check.py",
        "run_checks.sh", "build.py",
        "RUNLOG.md", "verification_summary.json", "manifest.json",
        "fixtures/defective_undeclared_scroller.html",
        "fixtures/defective_total_mismatch.html",
        "fixtures/defective_subtotal_double_count.html",
        "fixtures/defective_subtotal_huizong_label.html",
        "fixtures/defective_subtotal_unknown_label.html",
        "fixtures/defective_nav_squeeze.html",
    ]

    html = TARGET.read_text(encoding="utf-8")
    summary = {
        "generated_by": "build.py",
        "target": "after.html",
        "html_sha256": sha256_file(TARGET),
        "checkers": checkers,
        "geometry": geom,
        "adversarial_fixtures": fixtures,
        "bidirectional_regression": bidi,
        "section6_grep": {"forbidden_flag_residue": flags},
        "screenshots": shots,
        "counts": {
            "n_checkers": len(checkers),
            "n_screenshots": len(shots),
            "n_fixtures": len([f for f in DELIVERABLES if f.startswith("fixtures/")]),
            "n_deliverable_files": len(DELIVERABLES),
            "all_checkers_exit_zero": all(v["exit_code"] == 0 for v in checkers.values()),
        },
    }
    (BASE / "verification_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")
    print("\n→ verification_summary.json 已產生")

    manifest = {
        "generated_by": "build.py",
        "note": "由交付集合反推（每筆列出 sha256 與大小），不是掃工作目錄",
        "files": [],
    }
    for f in DELIVERABLES:
        p = BASE / f
        if not p.exists():
            manifest["files"].append({"path": f, "exists": False})
            continue
        manifest["files"].append({"path": f, "sha256": sha256_file(p),
                                  "bytes": p.stat().st_size, "exists": True})
    (BASE / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
    print("→ manifest.json 已產生")
    return 0


if __name__ == "__main__":
    sys.exit(main())
