"""欄位正規化與金額解析。

本模組只做「字串 → 值」的轉換，不碰檔案 I/O，方便單獨測試。

三個設計重點（都是踩過的坑）：
1. 金額解析必須能區分「空值」與「無法解析」，兩者對加總母體的意義不同。
2. 小計列的偵測必須檢查**每一個**欄位，不能只挑第一欄（10-27 v5/v6 的缺陷家族）。
3. 小計標籤的寫法很多，必須多寫法並列，且要能回報是「哪一欄」判斷出來的。
"""
from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation

__all__ = [
    "AMOUNT_ALIASES",
    "CANONICAL_COLUMNS",
    "normalize_header",
    "map_columns",
    "parse_amount",
    "detect_subtotal",
    "SUBTOTAL_LABELS",
]


# ---------- 欄位對映 ----------

#: 正規化後的欄位順序
CANONICAL_COLUMNS = ("日期", "類別", "說明", "單號", "金額")

#: 每個正規欄位可接受的原始表頭寫法（比對前會先跑 normalize_header）
AMOUNT_ALIASES = {
    "日期": ["日期", "date", "交易日期", "時間", "occured_at", "occurred_at"],
    "類別": ["類別", "category", "項目", "分類", "科目", "type"],
    "說明": ["說明", "description", "備註", "remark", "remarks", "摘要", "memo"],
    "單號": ["單號", "id", "編號", "流水號", "no", "number", "key", "ticket"],
    "金額": ["金額", "amount", "數額", "價額", "金額(元)", "金額（元）", "小計金額", "total"],
}

_FULLWIDTH_MAP = str.maketrans(
    "０１２３４５６７８９．，－（）［］：；％"
    "ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ"
    "ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ",
    "0123456789.,-()[]:;%"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "abcdefghijklmnopqrstuvwxyz",
)
# 常見的金額前後綴噪音
_CURRENCY_PREFIX = re.compile(
    r"^(?:nt\$|nt\s|us\$|usd\$|rmb|cny|￥|¥|\$|€|£|新台幣|人民幣|美金|元整)\s*",
    re.IGNORECASE,
)
_CURRENCY_SUFFIX = re.compile(
    r"\s*(?:元整|元|圓|塊|新台幣|人民幣|nt\$|rmb|cny|usd|us\$)\s*$",
    re.IGNORECASE,
)
_UNIT_SUFFIX = re.compile(r"\s*\(?\s*(?:元|nt\$|rmb|cny)\s*\)?\s*$", re.IGNORECASE)


def normalize_header(raw: object) -> str:
    """把表頭文字正規化成比對用的 key：全形轉半形、去空白、轉小寫。

    >>> normalize_header("金額（元）")
    '金額(元)'
    """
    if raw is None:
        return ""
    s = str(raw).translate(_FULLWIDTH_MAP)
    s = s.replace("　", " ")
    s = re.sub(r"\s+", "", s)
    return s.strip().lower()


_ALIAS_INDEX_CACHE: dict[str, str] | None = None


def _alias_index() -> dict[str, str]:
    """反向索引：正規化表頭 → 正規欄位（延遲建立，避免定義順序問題）。"""
    global _ALIAS_INDEX_CACHE
    if _ALIAS_INDEX_CACHE is None:
        index: dict[str, str] = {}
        for canon, aliases in AMOUNT_ALIASES.items():
            for alias in aliases:
                index.setdefault(normalize_header(alias), canon)
        _ALIAS_INDEX_CACHE = index
    return _ALIAS_INDEX_CACHE


def _canonical_of(header: str) -> str | None:
    """單一表頭 → 正規欄位名；認不出來回 None。"""
    n = normalize_header(header)
    if not n:
        return None
    index = _alias_index()
    if n in index:
        return index[n]
    # 去掉單位後綴再試一次（金額(元) → 金額）
    stripped = _UNIT_SUFFIX.sub("", n)
    if stripped in index:
        return index[stripped]
    # 包含式比對（最長別名優先，避免 "金額小計" 蓋掉 "金額"）
    best: tuple[int, str] | None = None
    for alias_norm, canon in index.items():
        if alias_norm and alias_norm in n:
            if best is None or len(alias_norm) > best[0]:
                best = (len(alias_norm), canon)
    return best[1] if best else None


def map_columns(headers: list[object]) -> tuple[dict[str, int | None], list[dict]]:
    """把原始表頭對映到正規欄位。

    回傳 ``(mapping, unmapped)``：
    - mapping: 正規欄位 → 原始欄位索引（0-based）；找不到為 None
    - unmapped: 無法對映的欄位清單（每筆含 index / header / reason）

    對映到同一個正規欄位的後來者（第一個勝出）會被記進 unmapped，理由為 duplicate。
    """
    mapping: dict[str, int | None] = {c: None for c in CANONICAL_COLUMNS}
    unmapped: list[dict] = []
    taken: dict[str, int] = {}

    for idx, raw in enumerate(headers):
        canon = _canonical_of(raw)
        if canon is None:
            unmapped.append(
                {"index": idx, "header": str(raw) if raw is not None else "",
                 "reason": "no_alias_match"}
            )
            continue
        if canon in taken:
            unmapped.append(
                {"index": idx, "header": str(raw) if raw is not None else "",
                 "reason": "duplicate_of", "kept_index": taken[canon]}
            )
            continue
        mapping[canon] = idx
        taken[canon] = idx
    return mapping, unmapped


# ---------- 金額解析 ----------

class AmountParse:
    """金額解析結果。value 為 None 代表這列**不能**進入加總母體。"""

    __slots__ = ("value", "reason", "raw")

    def __init__(self, value: Decimal | None, reason: str = "", raw: object = None):
        self.value = value
        self.reason = reason
        self.raw = raw

    @property
    def ok(self) -> bool:
        return self.value is not None

    def as_dict(self) -> dict:
        return {
            "value": str(self.value) if self.value is not None else None,
            "reason": self.reason,
            "raw": self.raw if isinstance(self.raw, (int, float, str)) else str(self.raw),
        }


def parse_amount(raw: object) -> AmountParse:
    """把一個儲存格解析成 Decimal 金額。

    失敗原因分類（會直接寫進 issues 與母體揭露）：
    - empty: 空值 / None
    - unparseable: 有內容但認不出來
    - percent: 百分比值（語意與金額不同，不進加總）
    """
    if raw is None:
        return AmountParse(None, "empty", raw)

    if isinstance(raw, bool):
        return AmountParse(None, "unparseable", raw)

    if isinstance(raw, (int, float, Decimal)):
        try:
            return AmountParse(Decimal(str(raw)).quantize(Decimal("0.01")), "", raw)
        except (InvalidOperation, ValueError):
            return AmountParse(None, "unparseable", raw)

    text = str(raw).translate(_FULLWIDTH_MAP)
    text = text.replace("　", " ").strip()
    if not text:
        return AmountParse(None, "empty", raw)

    # 百分比：語意不同
    if text.endswith("%"):
        return AmountParse(None, "percent", raw)

    negative = False
    # 會計負數寫法 (1,234) → -1234
    m = re.fullmatch(r"[（(]\s*(.*?)\s*[)）]", text)
    if m:
        negative = True
        text = m.group(1).strip()

    text = _CURRENCY_PREFIX.sub("", text)
    text = _CURRENCY_SUFFIX.sub("", text)
    text = _UNIT_SUFFIX.sub("", text)
    text = text.replace(",", "").replace(" ", "")
    if text.startswith("+"):
        text = text[1:]
    if text.startswith("-"):
        negative = not negative
        text = text[1:]
    if text.startswith("."):
        text = "0" + text

    if not text:
        return AmountParse(None, "empty", raw)

    if not re.fullmatch(r"\d+(?:\.\d+)?", text):
        return AmountParse(None, "unparseable", raw)

    try:
        value = Decimal(text).quantize(Decimal("0.01"))
    except (InvalidOperation, ValueError):
        return AmountParse(None, "unparseable", raw)

    if negative:
        value = -value
    return AmountParse(value, "", raw)


# ---------- 小計列偵測 ----------

#: 小計／合計列的標籤寫法（多寫法並列；每個都要能被使用者看懂）
SUBTOTAL_LABELS = (
    "小計", "小計合計", "合計", "總計", "累計", "本日小計", "月小計", "本日合計",
    "subtotal", "total", "grand total", "sum",
)

#: 第二層偵測用的「彙總性關鍵字」。
#: 為什麼需要第二層：SUBTOTAL_LABELS 是一份**不可能完整**的清單——
#: 來源檔可能寫「本段彙總」「截至本月底」「期初餘額加總」…
#: 只要漏接一種寫法，那一列就會被當成明細，報表金額靜默變兩倍。
#: 而清單式偵測**結構上無法自我驗證**（漏了就是漏了，沒有任何東西會紅）。
#: 因此加入一個**不依賴清單**的結構性訊號作為安全網。
SUMMARY_KEYWORDS = ("計", "總", "彙", "累", "sum", "total", "subtotal")

_LABEL_PATTERNS = tuple(
    re.compile(r"^" + re.escape(lbl) + r"(?:\s*[（(][^)）]*[)）])?\s*[:：]?\s*$", re.IGNORECASE)
    for lbl in SUBTOTAL_LABELS
)


def _looks_like_summary_word(text: str) -> bool:
    """這個字串看起來像「彙總標籤」嗎。

    只看**整個字串**（或開頭一小段），不做包含式比對——
    「合計系統建置費」是一筆真實交易的說明，不能因為含「合計」就被當成小計。
    """
    t = text.strip()
    if not t:
        return False
    if len(t) <= 12:
        return any(kw in t.lower() for kw in SUMMARY_KEYWORDS)
    # 太長的字串多半是說明文字，只看前 6 個字
    head = t[:6]
    return any(kw in head.lower() for kw in SUMMARY_KEYWORDS)


def detect_subtotal(
    values: list[object],
    *,
    amount_index: int | None = None,
) -> dict:
    """偵測這一列是不是小計／合計列。

    **必須檢查每一個欄位**——小計標籤常出現在第二欄或第三欄而不是第一欄。

    兩層偵測：
    1. **標籤層**（第一層）：整格文字命中 SUBTOTAL_LABELS → 確認是小計列。
    2. **結構層**（第二層，安全網）：金額欄有值、而關鍵識別欄（日期／單號）
       是空的、且有某個文字格看起來像彙總標籤 → **疑似**小計列。
       第二層抓的是「標籤清單漏掉的寫法」——沒有它，清單漏接會靜默讓金額加倍。

    回傳 dict：
    - is_subtotal: bool（第一層命中或第二層疑似都為 True）
    - label: 命中的標籤原文（None 表示不是小計列）
    - column_index: 命中在哪一欄（None 表示不是小計列）
    - kind: 'subtotal' | 'grand_total' | 'suspected' | None
    - detection_layer: 'label' | 'structural' | None
    """
    # --- 第一層：標籤層 ---
    for idx, value in enumerate(values):
        if value is None:
            continue
        if isinstance(value, (int, float, Decimal)):
            continue
        text = str(value).translate(_FULLWIDTH_MAP).strip()
        if not text:
            continue
        for pat in _LABEL_PATTERNS:
            if pat.match(text):
                kind = "grand_total" if text.lower() in {
                    "total", "grand total", "總計", "合計"} else "subtotal"
                return {
                    "is_subtotal": True,
                    "label": text,
                    "column_index": idx,
                    "kind": kind,
                    "detection_layer": "label",
                }

    # --- 第二層：結構層（不依賴標籤清單的安全網）---
    # 結構訊號：**這一列只有一個非空文字格**，而它看起來像彙總標籤。
    # 這個訊號不依賴任何標籤清單，因此清單漏接時它還能抓到。
    # 為什麼是「只有一個非空文字格」而不是「日期與單號都空」：
    #   真實的小計列常常把小計標籤寫在**第一欄**（日期欄的位置），
    #   這時日期欄不是空的、單號欄是空的——用「全部 key 欄都空」會漏接。
    #   而正常明細列至少有兩個非空文字格（日期 + 說明／單號），
    #   因此「非空文字格恰好 1 個」是更穩的結構判準。
    if amount_index is not None and amount_index < len(values):
        amount_cell = values[amount_index]
        has_amount = amount_cell is not None and str(amount_cell).strip() != ""
        if has_amount:
            text_cells: list[tuple[int, str]] = []
            for idx, value in enumerate(values):
                if idx == amount_index or value is None:
                    continue
                if isinstance(value, (int, float, Decimal)):
                    continue
                text = str(value).translate(_FULLWIDTH_MAP).strip()
                if text:
                    text_cells.append((idx, text))
            # 候選訊號：非空文字格恰好一個，且該格看起來像彙總標籤
            if len(text_cells) == 1:
                idx, text = text_cells[0]
                if _looks_like_summary_word(text):
                    return {
                        "is_subtotal": True,
                        "label": text,
                        "column_index": idx,
                        "kind": "suspected",
                        "detection_layer": "structural",
                    }
    return {
        "is_subtotal": False,
        "label": None,
        "column_index": None,
        "kind": None,
        "detection_layer": None,
    }
