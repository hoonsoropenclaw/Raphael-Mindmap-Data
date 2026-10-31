#!/usr/bin/env python3
"""audit_swiss_tokens.py — 機械化檢查「guizang Swiss 設計系統」的核心規則是否成立。

這支檢查器是 2026-10-31 scout A/B 的**量測工具**，兩組（baseline / 候選組）使用
**同一份檔案**（md5 相同），因此它測到的是組版方法本身的差異，不是「檢查器不同」
造成的假差異 —— 這是 2026-10-29 hyperui A/B 已驗證過的做法。

檢查的規則全部來自 op7418/guizang-ppt-skill 的 references/：
  1. themes-swiss.md「❌ 不要做的事」
     - 不允許混搭多個高亮色 → 全份只允許 **1 個** 有彩度色系（單一錨點色）
     - 不要用漸變 → 所有填色必須是純色（無 gradient fill）
     - 不要給 accent 加陰影/圓角/透明度 → 形狀不得有陰影、不得是圓角矩形
     - 不要改成純白（#fff）或純黑（#000）→ 不得出現純白/純黑
  2. themes-swiss.md「正文對比度」與 `--paper` / `--ink` 校色灰階
     - 底色與文字都必須是「校色過」的灰階，不是極端值
  3. checklist.md「0-S-4 瑞士風演示字号不能小到看不清」
     - 以 1280×720 CSS px 為座標系（13.333in × 7.5in 投影片），
       1pt = 96/72 px。字級下限：meta/頁尾 ≥ 14px、caption/說明 ≥ 16px、正文 ≥ 18px。
       判斷依「該 run 在投影片上的角色」難以機械判定，故採保守且可辯護的規則：
       **任何 run 的字級不得低於 11pt（= 14.67px，meta 下限）**；
       且落在頁尾列（bottom > 6.9in）的 run 不得低於 11pt。

用法：audit_swiss_tokens.py <deck.pptx>
結束碼：0 = 全部通過；1 = 有違規（逐條列出）；2 = 執行失敗（找不到檔案等）
"""
from __future__ import annotations

import sys
from math import atan2, degrees
from pathlib import Path

from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE

# ---- guizang themes-swiss.md 的語意變數：允許的「有彩度」錨點色 ----
# 判定方式：把顏色轉成 HSL，飽和度 S < 0.12 視為中性灰階（不算彩色錨點），
# S >= 0.12 且落在同一色相區間（±30°）算同一個色系。
CHROMA_THRESHOLD = 0.02   # OKLCH 彩度：校色過的暖灰 < 0.02；有彩度錨點色 > 0.15
HUE_BUCKET_DEG = 30
PURE_WHITE = (255, 255, 255)
PURE_BLACK = (0, 0, 0)
MIN_PT = 11.0          # = 14.67 CSS px（meta 下限）
FOOTER_BOTTOM_IN = 6.90  # 頁尾列起點（英寸）
EMU_PER_IN = 914400


def rgb_of(color_format) -> tuple[int, int, int] | None:
    """取得 RGB；沒有顏色（繼承主題／無填充）回 None。"""
    try:
        if color_format.type is None:
            return None
        rgb = color_format.rgb
        return (rgb[0], rgb[1], rgb[2])
    except Exception:  # noqa: BLE001 — 讀不到就當「沒有這個顏色」
        return None


# ---- OKLab / OKLCH（與 guizang-ppt-skill scripts/gz-theme.mjs 同一套數學）----
# 2026-10-31 第一版用 HSL 飽和度判定「有無彩度」，結果 guizang 自己的 --paper #fafaf8
# （極淺暖白，HSL S≈3.8% 剛好過關）與基準組的暖橘 #E8A33D（HSL S≈74%）被混為一談，
# 造成「全份 4 個色系」這種**測量工具自身的假陽性**。
# → 改用 OKLCH 彩度 C：知覺上等距，且與 guizang 生成主題用的是同一套函式。
#    校準點（實測 guizang 自己的 token）：#fafaf8 C=0.004（灰階）、#002FA7 C=0.187（彩色）、
#    #FF6B35 C=0.19（彩色）、#737373 C=0.0（灰階）、#525252 C=0.0（灰階）。
#    因此 CHROMA_THRESHOLD = 0.02 可正確區分「校色過的暖灰」與「有彩度的錨點色」。


def _srgb_to_linear(c: float) -> float:
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _linear_to_srgb(c: float) -> float:
    return c * 12.92 if c <= 0.0031308 else 1.055 * (c ** (1 / 2.4)) - 0.055


def rgb_to_oklab(rgb: tuple[int, int, int]) -> tuple[float, float, float]:
    r, g, b = (_srgb_to_linear(c / 255.0) for c in rgb)
    l = (0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b) ** (1 / 3)
    m = (0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b) ** (1 / 3)
    s = (0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b) ** (1 / 3)
    return (
        0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s,
        1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s,
        0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s,
    )


def oklch(rgb: tuple[int, int, int]) -> tuple[float, float, float]:
    L, a, b = rgb_to_oklab(rgb)
    C = (a * a + b * b) ** 0.5
    H = (degrees(atan2(b, a)) % 360) if C > 1e-6 else 0.0
    return (L, C, H)


def hue_family(rgb: tuple[int, int, int]) -> str | None:
    """回色系標籤；校色過的灰階（C < CHROMA_THRESHOLD）回 None。"""
    _, C, H = oklch(rgb)
    if C < CHROMA_THRESHOLD:
        return None
    return f"hue-{int(H // HUE_BUCKET_DEG) * HUE_BUCKET_DEG:03d}"


def walk_shapes(shapes):
    for sh in shapes:
        yield sh
        if sh.shape_type == MSO_SHAPE_TYPE.GROUP:
            yield from walk_shapes(sh.shapes)


def main() -> int:
    if len(sys.argv) < 2:
        print("用法：audit_swiss_tokens.py <deck.pptx>", file=sys.stderr)
        return 2
    deck = Path(sys.argv[1])
    if not deck.exists():
        print(f"找不到檔案：{deck}", file=sys.stderr)
        return 2

    prs = Presentation(str(deck))
    violations: list[str] = []
    color_families: dict[str, set[str]] = {}
    all_colors: dict[str, int] = {}

    def note(rgb, where):
        all_colors[rgb] = all_colors.get(rgb, 0) + 1
        fam = hue_family(rgb)
        if fam:
            color_families.setdefault(fam, set()).add(where)

    for idx, slide in enumerate(prs.slides, 1):
        for sh in walk_shapes(slide.shapes):
            # --- 漸變填色 ---
            try:
                if sh.fill.type is not None and int(sh.fill.type) == 3:  # MSO_FILL.GRADIENT
                    violations.append(f"第 {idx} 頁：形狀 {sh.shape_id} 使用漸層填色（瑞士風禁止漸變）")
            except Exception:  # noqa: BLE001
                pass
            # --- 陰影 ---
            try:
                if sh.shadow.inherit is False:
                    # inherit=False 表示明確關閉陰影 → 合規
                    pass
                else:
                    el = sh._element
                    has_shadow = el.find(
                        ".//{http://schemas.openxmlformats.org/drawingml/2006/main}effectLst"
                    )
                    if has_shadow is not None and len(has_shadow):
                        violations.append(f"第 {idx} 頁：形狀 {sh.shape_id} 帶陰影（瑞士風禁止陰影）")
            except Exception:  # noqa: BLE001
                pass
            # --- 圓角矩形 ---
            try:
                if sh.shape_type == MSO_SHAPE_TYPE.AUTO_SHAPE and "ROUNDED" in str(sh.auto_shape_type):
                    violations.append(f"第 {idx} 頁：形狀 {sh.shape_id} 是圓角矩形（瑞士風要求直角）")
            except Exception:  # noqa: BLE001
                pass
            # --- 填色 ---
            try:
                if sh.fill.type is not None and int(sh.fill.type) == 1:  # SOLID
                    c = rgb_of(sh.fill.fore_color)
                    if c:
                        note(c, f"第{idx}頁 形狀填色")
            except Exception:  # noqa: BLE001
                pass
            # --- 文字 ---
            if sh.has_text_frame:
                for para in sh.text_frame.paragraphs:
                    for run in para.runs:
                        if not run.text.strip():
                            continue
                        try:
                            c = rgb_of(run.font.color)
                            if c:
                                note(c, f"第{idx}頁 文字")
                        except Exception:  # noqa: BLE001
                            pass
                        size = run.font.size.pt if run.font.size else None
                        if size is not None and size < MIN_PT:
                            violations.append(
                                f"第 {idx} 頁：文字 {run.text[:18]!r} 字級 {size}pt "
                                f"< {MIN_PT}pt（= {MIN_PT * 96 / 72:.1f} CSS px，瑞士風 meta 下限）"
                            )
                        bottom_in = (sh.top + sh.height) / EMU_PER_IN
                        if bottom_in > FOOTER_BOTTOM_IN and size is not None and size < MIN_PT:
                            violations.append(
                                f"第 {idx} 頁：頁尾列文字 {run.text[:18]!r} 字級 {size}pt 低於下限"
                            )

    # --- 單一錨點色 ---
    if len(color_families) > 1:
        detail = "；".join(f"{fam}（{len(ws)} 處）" for fam, ws in sorted(color_families.items()))
        violations.append(
            f"全份出現 {len(color_families)} 個有彩度色系，違反「單一高飽和錨點色」：{detail}"
        )

    # --- 純白/純黑 ---
    if PURE_WHITE in all_colors:
        violations.append("全份出現純白 #ffffff（瑞士風要求校色過的灰階，不要純白）")
    if PURE_BLACK in all_colors:
        violations.append("全份出現純黑 #000000（瑞士風要求校色過的灰階，不要純黑）")

    print("=" * 68)
    print("audit_swiss_tokens — guizang Swiss 設計系統機械檢查")
    print("=" * 68)
    print(f"投影片數：{len(prs.slides)}")
    print(f"用到的顏色種類：{len(all_colors)}")
    neutral = sum(1 for c in all_colors if hue_family(c) is None)
    print(f"  中性灰階：{neutral} 種｜有彩度色系：{len(color_families)} 個")
    for fam, ws in sorted(color_families.items()):
        print(f"    {fam}：{len(ws)} 處")
    print()

    if violations:
        print(f"❌ 發現 {len(violations)} 項違規：")
        for v in violations:
            print(f"  • {v}")
        print()
        print("結果：未通過（exit 1）")
        return 1

    print("✅ 全部通過：單一錨點色 / 無漸變 / 無陰影 / 無圓角 / 無純白純黑 / 字級達下限")
    print()
    print("結果：通過（exit 0）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
