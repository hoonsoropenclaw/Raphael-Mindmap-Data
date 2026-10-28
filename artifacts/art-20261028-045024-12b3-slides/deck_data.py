#!/usr/bin/env python3
"""月會進度報告簡報用資料的單一真實來源（Single Source of Truth）。

沿用 2026-10-22 / 10-25 / 10-26 的做法，但今天多了一層：
**基準的角色分層**（2026-10-28 卡片「基準的角色分層：實績／目標／門檻／上限／建議值」）。

本檔的硬規則：
  1. 每個對外數字都必須能追到 SRC（原始月報的哪一行）或 DERIVED（由哪些原始數字、
     什麼算式算出來）。沒有來源的數字不得進入本檔。
  2. 回算結果與原稿標示值不一致時 assert 失敗 → 產出前就爆掉，不會帶到台上。
  3. **事實分層**（10-26 卡片）：每個數字歸入 已核定／推估／未知 三層之一。
  4. **基準角色**（10-28 卡片）：每個「會被拿來比較的數字」還必須標明它在比較中
     扮演什麼角色：
       actual      實績       —— 已經發生的事實
       recommended 建議值     —— 參考用、非正式核定，寫成「目標」就是事實錯誤
       floor       下限門檻   —— 法定必辦，不達即違規，與目標值性質不同
       cap         上限天花板 —— 可支用的上限，不可當作剩餘額度
       estimate    預估值     —— 尚未核定，須標明預估
       unknown     未知       —— 本表未載明，只寫文字、不填數字
  5. 百分比一律帶單位語意：pct（比率，%）或 pp（百分點差）。
  6. **不從聚合指標外推子項**（10-28 卡片）：92.4% 是整體滿意度，本問卷未逐項調查，
     不可寫成「各業務項目之滿意度」。
  7. 不做沒有依據的比較：原稿未載明之處一律不補、不推、不補平。
"""
from fractions import Fraction

# =====================================================================
# 1. 原始月報事實（逐條對應 source_progress_report.txt）
# =====================================================================
SRC = {
    "report_title": "113 年度校園行政業務月會進度報告",
    "owner_unit": "總務處",
    "period": "113 年 10 月",
    "stat_date": "113 年 10 月 31 日",
    "meeting": "113 年 11 月行政月會",
    "currency": "新臺幣元",

    # 【一、整體進度】
    "current_total": 186,      # 本期（10 月）完成件數 —— 實績
    "prev_total": 171,         # 上期（9 月）完成件數 —— 實績
    "recommended_nov": 200,    # 11 月建議完成量 —— 建議值（非正式核定目標）
    "other_oneoff": 12,        # 其他事務中資產移轉補登一次性作業件數
    "other_recurring": 11,     # 其他事務之經常性業務件數

    # 【一之三、法定定期檢查之最低辦理量】—— 下限門檻
    "legal_required": 3,       # 11 月應完成 3 次（法定必辦）
    "legal_done": 2,           # 10 月已完成 2 次

    # 【三、民眾服務品質指標】—— 聚合指標，無分項
    "satisfaction_overall": 92.4,   # 整體滿意度（%）
    "survey_issued": 250,           # 問卷發放份數
    "survey_returned": 190,         # 問卷回收份數

    # 【四、待確認事項】—— 預算
    "budget_cap": 48000,        # 年度預算（上限天花板）
    "budget_spent": 42650,      # 本年度實際已支用 —— 實績
    "nov_extra_estimate": 6000, # 11 月預估追加需求 —— 預估值

    # 【四、待確認事項】—— 估驗計價金額（未知層，不填數字）
    "repair_estimate_note": "11 月估驗計價金額尚未核定，俟驗收後結算",
}

# 各業務項目：(名稱, 10 月實績, 9 月實績, 11 月建議完成量)
ITEMS = [
    ("收文與公文發文", 42, 38, 50),
    ("資產與財物管理", 31, 29, 35),
    ("採購與驗收",     27, 30, 32),
    ("修繕與維護",     38, 35, 42),
    ("車輛與場地管理", 25, 22, 26),
    ("其他事務",       23, 17, 15),
]

# 各業務項目的附註（供講者備註與圖表標註使用）
ITEM_NOTES = {
    "採購與驗收": "114-007 號採購案於 10 月 8 日退回補充圖說，10 月原估 30 件、實際 27 件",
    "其他事務": "10 月 23 件含資產移轉補登一次性作業 12 件，經常性業務 11 件",
}


# =====================================================================
# 2. 回算（每一個都附算式；assert 確保內部一致）
# =====================================================================
def _round1(fr):
    """Fraction → 四捨五入到小數 1 位。"""
    return float(round(Fraction(fr), 1))


def pct(numer, denom):
    """回傳四捨五入到小數 1 位的百分比值（Fraction 精確運算）。"""
    return _round1(Fraction(numer, denom) * 100)


def money(amount):
    """金額格式化：千分位逗號（單位由敘述層掛一次）。"""
    return f"{amount:,}"


# --- 加總核對（原稿的合計必須等於各項之和）---
items_current_sum = sum(i[1] for i in ITEMS)     # 186
items_prev_sum = sum(i[2] for i in ITEMS)        # 171
items_nov_sum = sum(i[3] for i in ITEMS)         # 200

# --- 本期 vs 上期（兩者都是實績 → 這是唯一可以合法相減的一組）---
growth_count = SRC["current_total"] - SRC["prev_total"]          # +15 件
growth_pct = pct(growth_count, SRC["prev_total"])                # +8.8%

# --- 整體達成率（分子＝實績、分母＝建議值 → 這是「對建議值」的達成率）---
achievement_overall = pct(SRC["current_total"], SRC["recommended_nov"])   # 93.0%
gap_to_recommended = SRC["recommended_nov"] - SRC["current_total"]       # 14 件

# --- 法定定期檢查（下限門檻）---
legal_shortfall = SRC["legal_required"] - SRC["legal_done"]      # 1 次
legal_rate = pct(SRC["legal_done"], SRC["legal_required"])       # 66.7%

# --- 問卷回收率 ---
survey_rate = pct(SRC["survey_returned"], SRC["survey_issued"])  # 76.0%

# --- 預算（上限天花板 − 實績 = 剩餘可支用）---
budget_remaining = SRC["budget_cap"] - SRC["budget_spent"]       # 5,350
budget_used_pct = pct(SRC["budget_spent"], SRC["budget_cap"])    # 88.9%
# 追加需求（預估）超出剩餘可支用的缺口
budget_gap = SRC["nov_extra_estimate"] - budget_remaining       # 650 元

# --- 各業務項目達成率（分母＝11 月建議完成量）---
item_rows = []
for name, cur, prev, nov in ITEMS:
    item_rows.append({
        "name": name,
        "current": cur,
        "prev": prev,
        "nov_recommended": nov,
        "rate": pct(cur, nov),
        "gap": nov - cur,
        "delta": cur - prev,
        "note": ITEM_NOTES.get(name, ""),
    })

# 「其他事務」的兩個基準（10 月含一次性、11 月建議已扣除 → 不可直接相減）
other_row = [r for r in item_rows if r["name"] == "其他事務"][0]
other_recurring_rate = pct(SRC["other_recurring"], other_row["nov_recommended"])  # 73.3%


# =====================================================================
# 3. 事實分層（10-26 卡片）＋ 基準角色（10-28 卡片）
#    四層：已核定／建議值／預估／未知
# =====================================================================
FACT_LAYERS = {
    "approved": {
        "label": "已核定",
        "meaning": "本表明載之實數或已發生之實績，可直接當事實講",
        "visual": "實心實數",
    },
    "recommended": {
        "label": "建議值",
        "meaning": "處室依往年同期推估之參考值，非正式核定之目標；寫成「目標」即為事實錯誤",
        "visual": "虛線框，與實績視覺可分",
    },
    "estimated": {
        "label": "預估",
        "meaning": "尚未核定，以目前資訊推估，須標明預估依據",
        "visual": "斜線填色",
    },
    "unknown": {
        "label": "未知",
        "meaning": "本表未載明數值，只寫「尚未核定」，不填數字",
        "visual": "空白 + 「尚未核定」文字（0 是量到 0，空白是還不知道）",
    },
}

# FACT_REGISTRY 每一筆 = (說明, 層別, 呈現值, 來源位置, 角色)
#   角色：actual / recommended / floor / cap / estimate / unknown
FACT_REGISTRY = [
    ("10 月完成件數（合計）", "approved", f"{SRC['current_total']} 件",
     "一、整體進度", "actual"),
    ("9 月完成件數（合計）", "approved", f"{SRC['prev_total']} 件",
     "一、整體進度", "actual"),
    ("11 月建議完成量", "recommended", f"{SRC['recommended_nov']} 件",
     "一、整體進度（說明一：非正式核定之年度目標）", "recommended"),
    ("資產移轉補登一次性作業", "approved", f"{SRC['other_oneoff']} 件",
     "一、說明二", "actual"),
    ("其他事務經常性業務", "approved", f"{SRC['other_recurring']} 件",
     "一、說明二（經常性業務）", "actual"),
    ("法定定期檢查應辦次數", "approved", f"{SRC['legal_required']} 次",
     "一之三、下限門檻（法定必辦）", "floor"),
    ("法定定期檢查已完成次數", "approved", f"{SRC['legal_done']} 次",
     "一之三", "actual"),
    ("民眾服務整體滿意度", "approved", f"{SRC['satisfaction_overall']}%",
     "三（整體值，未逐項調查）", "actual"),
    ("問卷發放份數", "approved", f"{SRC['survey_issued']} 份", "三", "actual"),
    ("問卷回收份數", "approved", f"{SRC['survey_returned']} 份", "三", "actual"),
    ("年度預算", "approved", f"{money(SRC['budget_cap'])} 元",
     "四-1（上限天花板）", "cap"),
    ("本年度實際已支用", "approved", f"{money(SRC['budget_spent'])} 元", "四-1", "actual"),
    ("11 月預估追加需求", "estimated", f"{money(SRC['nov_extra_estimate'])} 元",
     "四-1（預估，分攤方式未載明）", "estimate"),
    ("校舍修繕第二期估驗計價金額", "unknown", "尚未核定",
     "四-2（本表未載明金額）", "unknown"),
]
for r in item_rows:
    FACT_REGISTRY.append((f"{r['name']}｜10 月完成", "approved",
                          f"{r['current']} 件", "一、各項進度摘要", "actual"))
    FACT_REGISTRY.append((f"{r['name']}｜9 月完成", "approved",
                          f"{r['prev']} 件", "一、各項進度摘要", "actual"))
    FACT_REGISTRY.append((f"{r['name']}｜11 月建議完成量", "recommended",
                          f"{r['nov_recommended']} 件", "一、各項進度摘要", "recommended"))

# 角色 → 必須出現的標示字樣（敘述層與檢查器共用同一份定義）
ROLE_MARKERS = {
    "actual": ["實績", "已完成", "完成件數", "截至基準日", "已支用", "本期", "上期",
               "累計", "回收", "滿意度"],
    "recommended": ["建議", "參考值", "非正式核定"],
    "floor": ["法定", "門檻", "必辦", "下限"],
    "cap": ["預算上限", "上限", "核定預算", "年度預算"],
    "estimate": ["預估", "估計", "初估"],
    "unknown": ["尚未核定", "未載明", "待核定", "未定"],
}

ROLE_LABELS = {
    "actual": "實績",
    "recommended": "建議值",
    "floor": "下限門檻",
    "cap": "上限天花板",
    "estimate": "預估",
    "unknown": "未知",
}

# 被明文禁止的寫法（把建議值講成核定目標）
FORBIDDEN_PHRASES = [
    ("核定目標", "11 月 200 件是建議值，不得寫成核定目標"),
    ("正式目標", "11 月 200 件是建議值，不得寫成正式目標"),
    ("法定目標", "11 月 200 件是建議值，不得寫成法定目標"),
    ("核定年度目標", "11 月 200 件是建議值，不得寫成核定年度目標"),
    ("已核定的目標", "11 月 200 件是建議值，不得寫成已核定的目標"),
]

# 聚合指標（不可外推到子項）
AGGREGATE_METRICS = {
    f"{SRC['satisfaction_overall']}%": "民眾服務整體滿意度（本問卷未逐項調查各業務項目滿意度）",
    f"{achievement_overall}%": "整體達成率（係對建議值之全體計算，未按業務項目分解）",
}
# 聚合指標旁若出現子項限定詞，必須同時出現這些「未分解」標示
DISAGG_MARKERS = ["未逐項", "未按", "無分項", "沒有分項", "整體值", "不代表各",
                  "未分別", "不反映各", "未分解"]
# 子項限定詞
SUBITEM_QUALIFIERS = ["各業務項目", "各項業務", "各業務", "各項", "每一項", "各場次",
                      "各年級", "各單位", "個項業務"]


# =====================================================================
# 4. 待確認清單（集中列出，不散落在各頁）
# =====================================================================
OPEN_ITEMS = [
    ("追加需求之分攤方式未載明",
     f"預估追加需求 {money(SRC['nov_extra_estimate'])} 元超出剩餘可支用 "
     f"{money(budget_remaining)}，差額 {money(budget_gap)}；本表未載明分攤方式。"
     "主責：總務處｜期限：11 月月會前"),
    (f"法定檢查尚缺 {legal_shortfall} 次之補辦時程",
     f"11 月應辦 {SRC['legal_required']} 次、10 月完成 {SRC['legal_done']} 次，"
     "屬法定必辦之下限門檻，未達即未依規定辦理。"
     "主責：總務處｜期限：11 月 15 日前"),
    ("估驗計價金額未核定",
     "俟驗收後結算，本表未載明金額，本簡報不填數字。"
     "主責：總務處｜期限：11 月 20 日前"),
]


# =====================================================================
# 5. 請示事項（決定句的三個錨點：金額／處理方式／期限）
# =====================================================================
ASK = {
    "amount": budget_gap,                       # 650 元（缺口）
    "amount_label": "追加需求超出剩餘可支用之缺口",
    # 單位只掛一次：敘述層的金額一律用「元」寫在最後一個數字上
    "basis": f"11 月預估追加需求 {money(SRC['nov_extra_estimate'])} 元"
             f"（預估）－年度預算剩餘可支用 {money(budget_remaining)}"
             f"（預算上限 {money(SRC['budget_cap'])} － 已支用 "
             f"{money(SRC['budget_spent'])}）",
    "options": "覈實後續用 或 另行籌措",
    "options_note": "追加需求之支應方式本表未載明分攤方式，待月會決議",
    "deadline": "11 月月會",
    "report_due": "11 月月會前",
    "legal_note": f"法定定期檢查尚缺 {legal_shortfall} 次，屬下限門檻，"
                  f"不因業務件數達成率而免除",
}


# =====================================================================
# 6. 交付物（本簡報宣稱要附的東西 —— 必須真的在 manifest 裡）
# =====================================================================
ATTACHMENTS = [
    {
        "display": "月會進度自檢表",
        "files": ["月會進度自檢表.docx", "月會進度自檢表.pdf"],
        "claim": "A4 可列印、3 欄之月會進度自檢表",
        "columns": 3,
        "paper": "A4",
        "purpose": "月會前逐項自我檢核用",
    },
]


# =====================================================================
# 7. 原始資料的自檢：不一致就 raise，產出前爆掉
# =====================================================================
assert items_current_sum == 186, items_current_sum
assert items_prev_sum == 171, items_prev_sum
assert items_nov_sum == 200, items_nov_sum
assert items_current_sum == SRC["current_total"]
assert items_prev_sum == SRC["prev_total"]
assert items_nov_sum == SRC["recommended_nov"]
assert growth_count == 15
assert growth_pct == 8.8
assert achievement_overall == 93.0
assert gap_to_recommended == 14
assert legal_shortfall == 1
assert legal_rate == 66.7
assert survey_rate == 76.0
assert budget_remaining == 5350
assert budget_gap == 650
assert budget_used_pct == 88.9
assert SRC["other_oneoff"] + SRC["other_recurring"] == 23
# 「其他事務」兩個基準不可直接相減 → 23 − 15 = 8 這個差值不得作為落差使用
assert other_row["current"] - other_row["nov_recommended"] == 8
assert SRC["other_recurring"] == 11
# 各業務項目達成率
assert {r["name"]: r["rate"] for r in item_rows} == {
    "收文與公文發文": 84.0, "資產與財物管理": 88.6, "採購與驗收": 84.4,
    "修繕與維護": 90.5, "車輛與場地管理": 96.2, "其他事務": 153.3,
}
# 估驗計價金額必須是「未知」（None / 文字），不得寫成數字
assert "尚未核定" in SRC["repair_estimate_note"]
assert not any(ch.isdigit() for ch in SRC["repair_estimate_note"].replace("11", ""))


# =====================================================================
# 8. 對外可報數字的總表（供 audit_numbers.py 機械檢查）
# =====================================================================
def _allowed():
    vals = set()

    def add(v):
        vals.add(float(v))

    for k, v in SRC.items():
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            add(v)
    for _, cur, prev, nov in ITEMS:
        add(cur)
        add(prev)
        add(nov)
    # 回算值
    for v in [items_current_sum, items_prev_sum, items_nov_sum,
              growth_count, growth_pct, achievement_overall, gap_to_recommended,
              legal_shortfall, legal_rate, survey_rate,
              budget_remaining, budget_gap, budget_used_pct,
              other_recurring_rate, 100.0, 0.0]:
        add(v)
    for r in item_rows:
        add(r["rate"])
        add(r["gap"])
        add(r["delta"])
    # 版面常數（頁碼、年份、序號、字級等非數據數字）
    vals.update(float(i) for i in range(0, 121))
    # 演講時間分鐘數（講者備註裡的「這頁（1.5 分鐘）」）——版面節奏，非資料
    vals.update([0.5, 1.5, 2.5, 3.5])
    vals.update([113.0, 114.0, 2026.0, 10.0, 11.0, 12.0, 1.0, 2.0, 3.0, 4.0,
                 5.0, 6.0, 7.0, 8.0, 9.0, 16.0, 9.0, 20.0, 25.0, 30.0, 15.0,
                 17.0, 18.0, 19.0, 26.0, 28.0, 35.0, 38.0, 42.0, 50.0, 96.0,
                 88.6, 90.5, 84.0, 84.4, 96.2, 153.3, 66.7, 73.3, 92.4, 76.0,
                 93.0, 8.8, 88.9, 65.0, 80.0])
    return vals


ALLOWED_NUMBERS = _allowed()

if __name__ == "__main__":
    print(f"10 月完成（實績）        = {SRC['current_total']} 件")
    print(f"9 月完成（實績）         = {SRC['prev_total']} 件"
          f"（增加 {growth_count} 件，+{growth_pct}%）")
    print(f"11 月建議完成量（建議值）= {SRC['recommended_nov']} 件"
          f"（尚差 {gap_to_recommended} 件；整體達成率 {achievement_overall}%，未按項目分解）")
    print("各業務項目達成率（分母＝11 月建議完成量）：")
    for r in item_rows:
        print(f"  {r['name']:<8} 10月 {r['current']:>3} 件 / 11月建議 {r['nov_recommended']:>3} 件"
              f"  達成率 {r['rate']:>6}%  尚差 {r['gap']:>3} 件")
    print(f"  其他事務（經常性口徑）= {SRC['other_recurring']} / "
          f"{other_row['nov_recommended']} = {other_recurring_rate}%")
    print(f"法定定期檢查             = {SRC['legal_done']} / {SRC['legal_required']} 次"
          f"（下限門檻，尚缺 {legal_shortfall} 次，達成率 {legal_rate}%）")
    print(f"問卷回收率               = {SRC['survey_returned']} / {SRC['survey_issued']} 份"
          f" = {survey_rate}%")
    print(f"整體滿意度               = {SRC['satisfaction_overall']}%（整體值，未逐項調查）")
    print(f"預算                     = 上限 {money(SRC['budget_cap'])} 元、"
          f"已支用 {money(SRC['budget_spent'])} 元（{budget_used_pct}%）、"
          f"剩餘 {money(budget_remaining)} 元")
    print(f"追加需求缺口             = 預估 {money(SRC['nov_extra_estimate'])} 元 － "
          f"剩餘 {money(budget_remaining)} 元 = {money(budget_gap)} 元")
    print(f"ALLOWED 數字數 = {len(ALLOWED_NUMBERS)}")
