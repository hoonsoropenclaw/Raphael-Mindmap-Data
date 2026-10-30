#!/usr/bin/env python3
"""audit_total_identity.py — 對帳等式：總計 = Σ 分組合計 = Σ 明細值。

對應 Q3（office-automation / Excel 處理）與 code SOP §11。

為什麼這支檢查器在 dev-ui-design 的產出裡：
§9-2 要求「必須有至少一組對抗性實測」，§11 要求「任何輸出含小計／合計的表，
都必須滿足加總等式」。本儀表板的表格有「各處室案件數」明細與「合計 4,812 件」
的總計列 —— 這就是一個分組合計的結構，必須能對帳。

★ 母體明寫（code SOP §11-4）：本檔回報的每一個數字都標明母體：
    - 明細層母體 = <table> tbody 中所有 <tr> 的「案件數」欄（每個 <tr> 算 1 筆）
    - 分組層母體 = 同上（本表只有一個分組維度：處室；每一列自成一組）
    - 總計層母體 = .panel-sub 中「合計 N 件」的 N
    - 被排除者：不含表頭列（thead）、不含 tfoot、不含任何小計列（本表沒有小計列，
      但偵測器必須多寫法並列 —— 見 SUBTOTAL_LABELS）
    - 單位：件（不含百分比欄、不含平均天數欄 —— 這兩者不可加總）

★ 三個數字必須由同一個函式回算（§11-1），不得各自手寫。

檢查類型（code SOP §9-1）：**核心正確性檢查**。
這是本組檢查器中唯一一支能支持「資料是對的」宣稱的。

用法：
    python3 audit_total_identity.py                    # 預設 after.html
    python3 audit_total_identity.py fixtures/xxx.html  # 對抗性 fixture
"""
import re
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE = Path(__file__).parent

# ★ 小計列的多寫法並列（code SOP §11-2：不得只認一種寫法）
# ★ 多寫法並列（code SOP §11-2：不得只認一種寫法）。
#   「彙總」是 2026-10-30 對抗性實測新增的寫法：
#   原本的清單漏了它 → 該列被當成明細 → 合計靜默加倍（差額 4,812）而檢查器回綠。
#   教訓：這正是「小計列偵測漏接常見寫法，合計靜默加倍」的 web 版。
SUBTOTAL_LABELS = ["合計", "小計", "總計", "累計", "彙總", "彙計", "總合",
                   "subtotal", "sub total", "total", "sum"]
# 百分比／比率欄：不可加總（§11-6 交界）
NON_ADDITIVE_HEADERS = ["率", "%", "平均", "天數", "ratio", "rate", "avg", "average"]
# 純數字（可加總）欄的表頭關鍵字
ADDITIVE_HEADER = "案件數"

JS = r"""
() => {
  const out = {rows: [], subtotalRows: [], totalTexts: [], headers: []};
  for (const t of document.querySelectorAll('table')) {
    const ths = [...t.querySelectorAll('thead th')];
    out.headers = ths.map(th => th.textContent.trim());
    const trs = [...t.querySelectorAll('tbody tr')];
    out.rows = trs.map(tr => {
      const tds = [...tr.children];
      return {
        label: tds[0] ? tds[0].textContent.trim() : '',
        cells: tds.map(td => td.textContent.trim()),
      };
    });
  }
  // 找出宣告「合計 N 件」的敘述列
  const subs = [];
  for (const p of document.querySelectorAll('.panel-sub, .scroll-hint, p')) {
    const txt = (p.textContent || '').trim();
    if (/合計|總計|小計/.test(txt)) subs.push({cls: p.className, text: txt});
  }
  out.totalTexts = subs;
  return out;
}
"""


def parse_num(s):
    """把 '1,204' / '4,812' / '87.2%' / '3.4' 轉成可加總的數。
    回傳 None 代表這個欄位不可加總（百分比、平均值）。"""
    t = s.strip().replace(",", "").replace("，", "")
    if not t:
        return None
    if "%" in t:
        return None            # 百分比欄位不得直接加總
    if not re.fullmatch(r"-?\d+(\.\d+)?", t):
        return None
    return float(t)


def is_subtotal(label):
    """小計列偵測：多寫法並列，且大小寫不敏感。

    ★ 邊界說明（誠實揭露）：這是**標籤比對**，不是語意判斷。
      一個寫法沒列到的標籤（例如「總計數」）會被當成明細 → 合計靜默加倍。
      所以等式這條線是「標籤偵測漏接」的最後一道防線：
      標籤漏接時，等式會因為「總計 ≠ Σ明細」而報出來（差額 = 小計列的量）。
      兩道防線互補：標籤偵測擋常見寫法，等式擋所有漏接。
    """
    low = label.lower().strip()
    return any(lab in low for lab in SUBTOTAL_LABELS)


def main() -> int:
    target = sys.argv[1] if len(sys.argv) > 1 else "after.html"
    path = (BASE / target).resolve()
    if not path.exists():
        print(f"✗ 找不到目標檔：{path}")
        return 2

    print(f"audit_total_identity.py — 目標：{path.name}")
    print("檢查類型：★ 核心正確性檢查（本組唯一一支）")

    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(viewport={"width": 1440, "height": 900})
        pg = ctx.new_page()
        pg.goto(path.as_uri())
        pg.wait_for_timeout(250)
        d = pg.evaluate(JS)
        ctx.close()
        b.close()

    print(f"\n表頭：{d['headers']}")
    print(f"母體：tbody 全部 {len(d['rows'])} 列（不含 thead、不含小計列）")

    # ── 找出可加總欄位 ─────────────────────────────────────────
    additive_idx = None
    for i, h in enumerate(d["headers"]):
        if ADDITIVE_HEADER in h:
            additive_idx = i
            break
    if additive_idx is None:
        print(f"✗ 找不到可加總欄位「{ADDITIVE_HEADER}」")
        return 1
    print(f"可加總欄位：第 {additive_idx + 1} 欄「{d['headers'][additive_idx]}」")

    # 確認其他欄位不可加總（並在報告中列出，避免「每個欄位都加一遍」的誤解）
    non_add = [d["headers"][i] for i in range(len(d["headers"]))
               if i != additive_idx and any(k in d["headers"][i].lower() for k in NON_ADDITIVE_HEADERS)]
    print(f"不可加總欄位（排除於母體之外）：{non_add}")

    # ── 三層計算（同一個函式回算，§11-1）───────────────────────
    detail_rows = []     # 明細層
    subtotal_rows = []   # 被偵測為小計者
    for r in d["rows"]:
        if is_subtotal(r["label"]):
            subtotal_rows.append(r)
            continue
        detail_rows.append(r)

    # 明細值之和
    print(f"小計列偵測標籤集合（多寫法並列）：{SUBTOTAL_LABELS}")
    detail_sum = 0.0
    detail_count = 0
    for r in detail_rows:
        v = parse_num(r["cells"][additive_idx]) if additive_idx < len(r["cells"]) else None
        if v is None:
            print(f"✗ 明細列「{r['label']}」的第 {additive_idx+1} 欄不是純數字："
                  f"{r['cells'][additive_idx] if additive_idx < len(r['cells']) else '(缺)'}")
            return 1
        detail_sum += v
        detail_count += 1

    # 分組合計之和（本表只有一個分組維度：處室 → 每一列自成一組，
    # 所以分組和 == 明細和；但仍必須獨立回算，不能直接賦值）
    group_sum = 0.0
    group_count = 0
    for r in detail_rows:
        v = parse_num(r["cells"][additive_idx]) if additive_idx < len(r["cells"]) else None
        if v is None:
            return 1
        group_sum += v
        group_count += 1

    # 總計：從頁面敘述列解析出「合計 N 件」
    total_value = None
    total_source = None
    for t in d["totalTexts"]:
        m = re.search(r"合計\s*([\d,]+)\s*件", t["text"])
        if m:
            total_value = float(m.group(1).replace(",", ""))
            total_source = t["text"][:60]
            break
    if total_value is None:
        print("✗ 找不到宣告的總計（『合計 N 件』）")
        return 1

    print("\n── 三層回算（同一函式）──")
    print(f"  明細層：Σ {detail_count} 筆明細值        = {detail_sum:,.0f}")
    print(f"  分組層：Σ {group_count} 個分組合計        = {group_sum:,.0f}")
    print(f"  總計層：頁面宣告的合計                 = {total_value:,.0f}"
          f"  （來源：{total_source}）")
    if subtotal_rows:
        print(f"  被偵測為小計列並排除：{[r['label'] for r in subtotal_rows]}")
        print(f"  被當成明細的列：{[r['label'] for r in detail_rows]}")
    else:
        print(f"  被當成明細的列：{[r['label'] for r in detail_rows]}")

    diff_detail = total_value - detail_sum
    diff_group = total_value - group_sum
    print(f"  差額（總計 − 明細）= {diff_detail:,.0f}")
    print(f"  差額（總計 − 分組）= {diff_group:,.0f}")

    total = 0
    if abs(diff_detail) > 0.5:
        print(f"✗ 對帳等式不成立：總計 {total_value:,.0f} ≠ Σ 明細 {detail_sum:,.0f}"
              f"（差 {diff_detail:,.0f}）")
        print(f"   可能原因：漏接某列 / 小計列被當成明細重複計算 / 總計數字手寫錯誤")
        total += 1
    if abs(diff_group) > 0.5:
        print(f"✗ 對帳等式不成立：總計 {total_value:,.0f} ≠ Σ 分組 {group_sum:,.0f}"
              f"（差 {diff_group:,.0f}）")
        total += 1
    if total == 0:
        print(f"✓ 對帳等式成立：總計 {total_value:,.0f} = Σ 分組合計 {group_sum:,.0f}"
              f" = Σ 明細值 {detail_sum:,.0f}")

    print(f"\n總計問題數：{total}")
    if total == 0:
        print("本檢查器涵蓋：總計＝Σ分組＝Σ明細的三層等式、小計列偵測與排除、"
              "不可加總欄位排除。")
        print("不涵蓋：版面（見 audit.py）、欄位可見性（見 audit_narrow_overflow.py）、"
              "對比度（見 contrast_check.py）。")
        print("「EXIT=0」只代表上述已列項目全過，不代表頁面完全無問題。")
    return 0 if total == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
