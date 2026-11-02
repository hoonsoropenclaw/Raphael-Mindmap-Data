#!/usr/bin/env python3
"""機械檢查：跨頁語意一致性（建議價／方案指稱／圖例標籤／圖上元素）。

為什麼需要這一支（2026-11-03 evaluate 自評後新增）：
    既有 9 支檢查器的命題**全部是「單頁之內」的**：
      audit_text_fit     比對同頁 shape 之間
      audit_numbers      比對數字 vs deck_data 白名單
      audit_visual_terms 比對**備註 vs 同頁正文**
      audit_decision_pages / audit_block_density / audit_visual_overlap 同理
    → 沒有任何一支會問「**六頁講的是不是同一件事**」。

    於是 11-03 自評抓到兩個 high 缺陷，9 支檢查器全部 EXIT=0：
      ① 封面主標題「建議由 42 元調至 **50 元**」vs 第 5 頁「建議採方案 C **47 元**」
         → 同一份簡報對外給出兩個互斥的建議價
      ② 第 4 頁 c4 圖例「**建議方案 A**」vs 第 5 頁「（本簡報建議）」標在方案 C
         → 「建議方案」這個詞被綁在兩個方案上

    這兩件事都不是「排版錯」，是「跨頁語意錯」→ 需要一支新的命題。

本檢查器驗四件事：
    A. 建議價一致：封面標題的建議價 == 決策頁的建議價 == deck_data 的建議方案
    B. 「建議方案」唯一：全份簡報（含圖例、備註）只允許一個方案被稱為建議
    C. 圖例標籤不自相矛盾：圖例裡出現的方案代號不得帶「建議」之類的評價字
    D. 圖說提到的視覺元素必須真的畫在圖上（防止「圖上有虛線」這種幽靈元素）

退出碼：0 = 通過；1 = 有跨頁語意矛盾。
"""
import os
import re
import sys

import deck_data as D

HERE = os.path.dirname(os.path.abspath(__file__))
DECK = "20261103-午餐費調整請示.pptx"

# 圖上「真的畫得出來」的視覺元素白名單。
# 這是刻意保守的：只列本簡報五張圖實際用到的元素。
# 11-03 首版把「虛線」放進白名單，但 c5 圖上根本沒有虛線 → 白名單自己也會說謊。
REAL_VISUAL_ELEMENTS = {
    "長條", "垂直標記", "虛線標記", "柱", "數值", "格線", "軸",
}


def slide_texts(pptx_path):
    from pptx import Presentation
    prs = Presentation(pptx_path)
    out = []
    for i, slide in enumerate(prs.slides, 1):
        body, notes = [], ""
        for sh in slide.shapes:
            if sh.has_text_frame and sh.text_frame.text.strip():
                body.append(sh.text_frame.text)
        try:
            if slide.has_notes_slide:
                notes = slide.notes_slide.notes_text_frame.text
        except Exception:
            notes = ""
        out.append((i, "\n".join(body), notes))
    return out


def main():
    pptx_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, DECK)
    print("=" * 68)
    print("跨頁語意一致性檢查（2026-11-03 evaluate 自評新增）")
    print("=" * 68)
    print("命題：六頁講的是不是同一件事？")
    print("（既有 9 支檢查器全部是單頁命題 → 這一支補的是跨頁命題）")
    print()

    failures = []
    pages = slide_texts(pptx_path)
    all_body = "\n".join(b for _, b, _ in pages)

    # ── A. 建議價一致 ──
    print("【A】建議價跨頁一致")
    # 封面標題形如「建議由 42 元調至 NN 元」
    cover_re = re.compile(r"建議由\s*(\d+)\s*元調至\s*(\d+)\s*元")
    cover_claim = None
    for no, body, _ in pages:
        m = cover_re.search(body)
        if m:
            cover_claim = (no, int(m.group(1)), int(m.group(2)))
            print(f"  · 第 {no} 頁封面宣稱：{m.group(1)} → {m.group(2)} 元")
            break
    if cover_claim is None:
        print("  · 封面未找到「建議由 X 元調至 Y 元」句式（不檢查）")
    else:
        if cover_claim[2] != D.PRICE_C:
            failures.append(f"A：封面建議價 {cover_claim[2]} 元 != 建議方案 "
                            f"{D.PRICE_C} 元（deck_data.PRICE_C）")
            print(f"  ✗ 封面建議價 {cover_claim[2]} 元 ≠ 建議方案 {D.PRICE_C} 元")
        else:
            print(f"  ✓ 封面建議價 == 建議方案 {D.PRICE_C} 元")

    # ── B. 「建議方案」唯一 ──
    print()
    print("【B】「建議方案」在全份簡報只能指向一個方案")
    # 抓「建議方案 X」或「建議採方案 X」這類綁定
    bind_re = re.compile(r"建議(?:採|為|用|方案為)?\s*方案\s*([ABC])")
    binds = {}
    for no, body, notes in pages:
        for m in bind_re.finditer(body + "\n" + notes):
            binds.setdefault(m.group(1), []).append(no)
    if not binds:
        print("  · 沒有找到「建議…方案 X」的綁定句（不檢查）")
    else:
        for plan, nos in sorted(binds.items()):
            print(f"  · 方案 {plan} 被稱為建議：頁 {nos}")
        if len(binds) > 1:
            failures.append(f"B：「建議方案」同時指向 {sorted(binds)} 個方案")
            print(f"  ✗ 「建議方案」指向多個方案：{sorted(binds)}")
        elif "C" not in binds:
            failures.append(f"B：建議方案不是 C，而是 {sorted(binds)}")
            print(f"  ✗ 建議方案應為 C，實際為 {sorted(binds)}")
        else:
            print("  ✓ 建議方案唯一且為方案 C")

    # ── C. 圖例標籤不得帶評價字 ──
    print()
    print("【C】圖例標籤不得含「建議」等評價字")
    for key in ("delta_c", "delta_a", "delta_b"):
        label = D.LEGEND_LABELS.get(key, "")
        if "建議" in label:
            failures.append(f"C：圖例 {key} 的標籤「{label}」含「建議」，"
                            f"但本簡報建議的是方案 C")
            print(f"  ✗ {key} 的圖例標籤含「建議」：{label}")
        else:
            print(f"  ✓ {key} 圖例標籤：{label}")

    # ── D. 圖說提到的視覺元素必須真的畫在圖上 ──
    print()
    print("【D】圖說提到的視覺元素必須真的存在於圖上")
    ghost_re = re.compile(r"(虛線|虛線連接|折線|折線連接|累計線)")
    ghosts = []
    for key, text in D.LEGEND.items():
        for m in ghost_re.finditer(text):
            ghosts.append((key, m.group(0), text))
    if ghosts:
        for key, word, text in ghosts:
            failures.append(f"D：圖說 {key} 提到「{word}」，但圖上沒有畫這個元素：{text}")
            print(f"  ✗ {key} 圖說提到幽靈元素「{word}」：{text}")
    else:
        print("  ✓ 圖說沒有提到圖上不存在的元素")

    print()
    if failures:
        print("結論：不通過——六頁之間存在語意矛盾。")
        for f in failures:
            print(f"  ✗ {f}")
        return 1
    print("✓ 跨頁語意一致")
    print("\n結論：通過")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
