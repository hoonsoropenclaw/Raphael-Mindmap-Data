#!/usr/bin/env python3
"""
合併資料夾內多個 Excel 並產生摘要（v4）
=========================================

用途（admin 軌：辦公自動化，目標環境＝使用者的 Windows；開發環境＝N100 Linux）：
  給定一個資料夾，把裡面所有 .xlsx 合併成單一檔案，並產生摘要工作表：
    - 合併資料（跨檔聯集欄位、缺漏欄位留白、來源追溯欄）
    - 檔案摘要（每檔每分頁的列數、欄位、表頭列判定結果、缺漏／獨有欄位、錯誤訊息）
    - 數值合計（每欄合計 + 非空數值格數；用「正規化後」��值）
    - 型別轉換（每一筆文字→數值的轉換留痕：原值 / 正規化值 / 套用的規則）
    - 無法解析（轉型失敗的值獨立成表，不混在 NaN 裡、不算 0）
    - 退款警示（欄名關鍵字 或 正規化後的數值為負）
    - 輸入集合（每個檔案的納入／排除決定 + 理由 + sha256）
    - 本次執行（時間、輸入、輸出、統計、執行平台）
    - 略過檔案（靜默略過會讓使用者困惑）

v4 相對 v3（2026-10-24，art-20261024-025505-097c-code）的六項差異：
  1. 表頭列自動判定（型別互斥判準 + 欄名唯一性 + 非空比例 + 合併儲存格補欄名）
     ＋ --header-row 手動覆寫 ＋ 判定失敗的可行動錯誤訊息。
     v3 是「第一個非空列就是表頭」，遇到說明列就整批錯。
  2. 欄位型別正規化（去千分位／幣別、全形轉半形、百分比依欄位語意換算、
     會計括號負數、萬／億進位），無法解析的值獨立成表並留痕。
     v3 的 _is_number 只認 int/float，文字型金額 100% 靜默漏算。
  3. 輸入集合界定（宣告式排除規則 + --exclude-glob + 輸入清單 sha256），
     連續跑 3 次輸出資料必須完全一致（回歸測試鎖住）。
  4. Windows 實測揭露（交付紀錄分「實測平台／模擬平台／未驗證項目」三欄）。
  5. 交付閘門機檢（依 code SOP §6／§7／§8）：build 腳本產出機器可讀的
     verification_summary.json，RUNLOG 與 artifact notes 全部引用它、不手抄；
     檢查器雙向驗證（缺陷版 exit≠0、修好版 exit=0）且隨產出物交付。
  6. 移除 --no-backup（code SOP §1.4：不得提供關閉保護的旗標）。
     只保留 --dry-run（預設）/ --apply。

執行環境：
  - Python 3.10+，只依賴 openpyxl（Windows 端 pip install openpyxl 即可）
  - 跨平台（Windows / macOS / Linux）

執行：
  python merge_xlsx.py <input_folder>                     # 預設 dry-run，只預覽不寫檔
  python merge_xlsx.py <input_folder> --apply             # 真的合併並寫出
  python merge_xlsx.py <input_folder> --apply \
      -o out/merged.xlsx --summary-csv out/summary.csv --issues-csv out/issues.csv
  python merge_xlsx.py <input_folder> --apply --header-row 2   # 手動指定表頭列（0-based）

設計原則（sops/code/SOP.md v1.6.0）：
  - 破壞性動作（寫檔/覆寫）預設 dry-run，需 --apply 才真的執行
  - 任何外部 I/O 失敗都要有可行動的錯誤訊息
  - 可重跑不損壞資料（idempotent）
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt_mod
import fnmatch as fnmatch_mod
import hashlib
import io
import os
import re
import shutil
import sys
import tempfile
import unicodedata
import zipfile
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path, PureWindowsPath
from xml.etree import ElementTree as ET

try:
    from openpyxl import Workbook, load_workbook
    from openpyxl.styles import Font, PatternFill
    from openpyxl.utils import get_column_letter
except ImportError:  # pragma: no cover - 環境缺套件時給可行動訊息
    sys.stderr.write(
        "缺少必要套件 openpyxl。請執行：pip install openpyxl\n"
        "（或用 python -m pip install --user openpyxl）\n"
    )
    raise SystemExit(3)


# ---------- 設定 ----------
REFUND_KEYWORDS = ("退款", "退費", "折讓", "溢付", "沖銷", "refund", "credit")
INPUT_SUFFIXES = {".xlsx"}
OTHER_EXCEL_SUFFIXES = {".xls", ".xlsm", ".xlsb"}
SKIP_PREFIXES = ("~$", ".")
CSV_ENCODINGS = ("utf-8-sig", "cp950", "utf-8")
MAX_WINDOWS_PATH = 260
ILLEGAL_WINDOWS_CHARS = set('<>:"/\\|?*')
RESERVED_WINDOWS_NAMES = (
    {"CON", "PRN", "AUX", "NUL"}
    | {f"COM{i}" for i in range(1, 10)}
    | {f"LPT{i}" for i in range(1, 10)}
)

# 百分比語意由「欄位語意」決定，不是由值本身猜（見今日卡片 Q3）。
RATE_KEYWORDS = ("率", "百分比", "佔比", "占比", "比例", "percent", "rate")
# 欄名看起來「應該是數值」的關鍵字：這類欄位裡解析失敗的值一定要進「無法解析」清單，
# 不能因為該分頁的比例低就被當成文字欄位而靜默放過。
NUMERIC_NAME_KEYWORDS = (
    "金額", "數量", "件數", "費用", "預算", "小計", "合計", "總計",
    "總金額", "價格", "單價", "率", "比例", "佔比", "占比", "總數",
    "amount", "price", "cost", "total", "qty", "quantity", "count",
)
# 欄名結尾是這些字 → 多半是「標籤欄」不是「數值欄」。
# 實測教訓：「經費項目」含有關鍵字「經費」，若不排除會把整個文字欄
# 當成數值欄 → 每個值都進「無法解析」清單（15 筆假警報）。
LABEL_SUFFIXES = ("項目", "別", "說明", "類別", "名稱", "單位", "類型", "用途", "方式")
# 幣別／單位符號（正規化時移除；「萬／億」是倍率，另走 scale 規則）
CURRENCY_TOKENS = (
    "NT$", "NT＄", "nt$", "NT＄", "＄", "$", "€", "£", "RMB", "CNY",
    "人民幣", "新台幣", "新臺幣", "元", "圓",
)
SCALE_TOKENS = {"千": 1_000, "萬": 10_000, "萬": 10_000, "億": 100_000_000}

# 表頭列自動判定的門檻（候選列得分低於此值 → 報錯要人指定）
HEADER_DETECT_THRESHOLD = 0.5
# 候選列得分與第二名的差距小於此值 → 視為模稜兩可 → 報錯（不猜）
HEADER_DETECT_MARGIN = 0.05
# 表頭列候選只在前 N 列內找（超過通常是標題／說明區）
HEADER_DETECT_MAX_CANDIDATES = 12
# 表頭列的非空比例下限（低於此值多半是只填一格的說明列）
HEADER_MIN_FILL_RATIO = 0.5

# 數值欄位的判定門檻：非空值中「可解析成數字」的比例達此值 → 該欄視為數值欄
NUMERIC_COLUMN_RATIO = 0.5

_NUM_RE = re.compile(r"^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?$")
_DATE_RE = re.compile(
    r"^\d{4}[-/]\d{1,2}[-/]\d{1,2}(?:[ T]\d{1,2}:\d{2}(?::\d{2})?)?$"
)
_XL_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
_XL_REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"


# ---------- 資料結構 ----------
@dataclass
class SheetRaw:
    """單一檔案單一分頁的「原始結構」（尚未決定表頭列、尚未正規化）。"""

    file_name: str
    sheet_name: str
    rows: list[tuple[int, tuple]] = field(default_factory=list)  # (原始 Excel 列號, 值 tuple)
    merged_ranges: list[str] = field(default_factory=list)
    formula_cells: list[str] = field(default_factory=list)
    # Excel 列號 → 該列因「合併儲存格」而被補值的欄索引（不含左上角那一欄）
    merge_filled: dict[int, list[int]] = field(default_factory=dict)
    error: str | None = None


@dataclass
class HeaderDecision:
    """表頭列判定結果（要寫進輸出摘要，讓使用者能逐檔核對）。"""

    header_index: int | None = None       # 0-based，索引「非空列」序列
    header_excel_row: int | None = None   # 在原 Excel 的列號（1-based）
    score: float = 0.0
    method: str = ""                      # auto / manual
    evidence: list[str] = field(default_factory=list)
    candidates: list[tuple[int, float]] = field(default_factory=list)
    reason: str = ""                      # 失敗原因


@dataclass
class SheetData:
    """解析完成、可直接合併的分頁。"""

    file_name: str
    sheet_name: str
    headers: list[str] = field(default_factory=list)
    rows: list[list] = field(default_factory=list)
    row_numbers: list[int] = field(default_factory=list)
    numeric_sums: dict[str, float] = field(default_factory=dict)
    numeric_counts: dict[str, int] = field(default_factory=dict)
    alerts: list[dict] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    error: str | None = None
    header: HeaderDecision = field(default_factory=HeaderDecision)
    conversions: list[dict] = field(default_factory=list)
    unparsed: list[dict] = field(default_factory=list)
    # 本分頁中被判定為「數值欄」的欄名（每個分頁各自判定，規則跨檔一致）
    numeric_headers: set[str] = field(default_factory=set)
    # 本分頁的欄位級警告（例：率欄位同時有原生值與文字值）
    column_warnings: list[str] = field(default_factory=list)
    # 因合併儲存格而被補值的欄（欄名來自左上角，不是該欄自己的名稱）
    merge_filled_headers: list[str] = field(default_factory=list)
    # 本分頁用到的率欄位尺度（欄名 → 倍率；None = 無法推導、不換算）
    rate_scales: dict[str, float | None] = field(default_factory=dict)
    # 率欄位的值（用來算平均／範圍，不做合計）
    rate_stats: dict[str, list[float]] = field(default_factory=dict)
    # 被判定為小計列的資料列（不重複計入合計，但資料仍保留在合併資料中）
    subtotal_rows: list[dict] = field(default_factory=list)


@dataclass
class FileResult:
    """單一檔案的解析結果（多分頁）。"""

    file_name: str
    sheets: list[SheetData] = field(default_factory=list)
    error: str | None = None
    needs_manual_header: bool = False
    sha256: str = ""
    size: int = 0


@dataclass
class ExclusionRule:
    """宣告式排除規則：符合就排除，並且必須回報原因。"""

    name: str
    pattern: str
    reason: str
    match: str = "glob"  # glob / prefix / suffix


# ---------- Windows 路徑預檢 ----------
def looks_like_windows_path(raw: str) -> bool:
    """判斷字串是否為 Windows 形式的路徑。

    在 Linux 上 Path('C:/x') 只是普通目錄名，所以判斷 Windows 語意必須用 PureWindowsPath。
    """
    if not raw:
        return False
    wp = PureWindowsPath(raw)
    return bool(wp.drive) or raw.startswith("\\\\") or raw.startswith("//")


def validate_windows_component(name: str) -> list[str]:
    """檢查單一檔名/目錄名是否符合 Windows 命名規則。回傳問題清單（空 = 合法）。"""
    problems: list[str] = []
    bad = sorted({c for c in ILLEGAL_WINDOWS_CHARS if c in name})
    if bad:
        problems.append(
            f"檔名「{name}」含 Windows 禁用字元 {' '.join(bad)}"
            "（< > : \" / \\ | ? * 都不能用，請改用全形或底線）"
        )
    stem = name.split(".")[0].upper()
    if stem in RESERVED_WINDOWS_NAMES:
        problems.append(
            f"檔名「{name}」是 Windows 保留裝置名（{stem}），加副檔名也不行，請改名"
        )
    return problems


def validate_windows_path(raw: str) -> list[str]:
    """對 Windows 形式的路徑做完整預檢：各層名稱 + 總長度 260。"""
    problems: list[str] = []
    wp = PureWindowsPath(raw)
    anchor = wp.anchor
    for part in wp.parts:
        if part == anchor or part in (wp.drive, "\\", "/"):
            continue
        if part.startswith("\\\\") or part.startswith("//"):
            continue
        problems.extend(validate_windows_component(part))
    if len(str(wp)) > MAX_WINDOWS_PATH:
        problems.append(
            f"路徑長度 {len(str(wp))} 超過 Windows MAX_PATH {MAX_WINDOWS_PATH}；"
            "解法：改用較短路徑、或開啟 LongPathsEnabled + 程式 manifest 標 longPathAware"
        )
    return problems


def validate_target_path(raw: str) -> list[str]:
    """目標輸出路徑預檢：Windows 形式走 Windows 規則，其他走通用規則。"""
    if looks_like_windows_path(raw):
        problems: list[str] = []
        if os.name != "nt":
            problems.append(
                f"輸出路徑「{raw}」是 Windows 形式，但目前作業系統是 {os.name}（非 Windows）。"
                "在非 Windows 上這會被當成含反斜線的單一檔名、寫進目前目錄，"
                "不是預期的磁碟機位置。請改用本機絕對路徑，"
                "或在 Windows 上執行本程式。"
            )
        problems.extend(validate_windows_path(raw))
        return problems
    problems = []
    for part in Path(raw).parts:
        if part in ("/", "\\"):
            continue
        problems.extend(validate_windows_component(part))
    return problems


# ---------- 原子寫入 ----------
def atomic_write_bytes(target: Path, payload: bytes) -> None:
    """把 payload 原子寫入 target：同目錄暫存檔 → flush+fsync → os.replace。"""
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(dir=str(target.parent), prefix=f".{target.name}.", suffix=".tmp")
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(payload)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp_path, target)
    except BaseException:
        tmp_path.unlink(missing_ok=True)
        raise


def atomic_save_workbook(wb, target: Path, backup: bool = True) -> Path | None:
    """把 openpyxl Workbook 原子寫出；回傳備份路徑（若有備份）。"""
    target.parent.mkdir(parents=True, exist_ok=True)
    backup_path = None
    if backup and target.exists():
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        # 備份副檔名刻意「不」保留 .xlsx：否則它會被 .xlsx 掃描器選中，
        # 造成重跑時把備份檔當成輸入合併 → 資料重複、金額 double。
        backup_path = target.with_name(f"{target.stem}.bak-{stamp}")
        shutil.copy2(target, backup_path)

    fd, tmp_name = tempfile.mkstemp(dir=str(target.parent), prefix=f".{target.stem}.", suffix=".xlsx")
    os.close(fd)
    tmp_path = Path(tmp_name)
    try:
        wb.save(tmp_path)
        # 必須用 "rb+"（可寫 handle）做 fsync：Windows 的 os.fsync() 底層是
        # FlushFileBuffers()，而它要求 handle 具備 GENERIC_WRITE 權限；
        # 用 "rb" 開的 handle 只有 GENERIC_READ → EBADF (OSError [Errno 9])。
        # POSIX 允許對 O_RDONLY fd 做 fsync，所以 Linux CI 抓不到這個 bug。
        with open(tmp_path, "rb+") as fh:
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp_path, target)
    except BaseException:
        tmp_path.unlink(missing_ok=True)
        raise
    return backup_path


# ---------- 型別判定與正規化（今日卡片 Q3） ----------
def _looks_numeric_text(s: str) -> bool:
    t = s.strip()
    if not t:
        return False
    # 允許千分位、幣別符號、括號負數、尾端負號、百分比、萬/億
    t = t.replace(",", "").replace("，", "")
    for tok in CURRENCY_TOKENS:
        t = t.replace(tok, "")
    t = t.replace(" ", "").replace("　", "")
    neg = False
    if t.startswith("(") and t.endswith(")"):
        neg = True
        t = t[1:-1]
    if t.endswith("-"):
        neg = True
        t = t[:-1]
    t = t.rstrip("%")
    for tok in SCALE_TOKENS:
        t = t.replace(tok, "")
    if not t:
        return False
    return bool(_NUM_RE.match(t))


def classify_value(value) -> str:
    """把單一儲存格值分類為：empty / text / num / numlike / datelike / bool。"""
    if value is None:
        return "empty"
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, (int, float)):
        return "num"
    if isinstance(value, (dt_mod.datetime, dt_mod.date, dt_mod.time)):
        return "datelike"
    s = str(value).strip()
    if not s:
        return "empty"
    if _looks_numeric_text(s):
        return "numlike"
    if _DATE_RE.match(s):
        return "datelike"
    return "text"


@dataclass
class ParseOutcome:
    """一次數值解析的完整結果（成功與失敗都要有痕跡）。"""

    ok: bool
    value: float | None = None
    normalized: str = ""
    rule: str = ""
    reason: str = ""


def parse_number(raw, header: str, is_rate_column: bool, rate_scale: float | None = None) -> ParseOutcome:
    """把一個「可能看起來像數字」的值轉成 float。

    rate_scale：率欄位的尺度倍率（由欄位層級推導，見 infer_column_scale）。
        None = 尚未推導（此時文字率值不換算，避免猜錯）。

    正規化順序固定（不可調換）：
      ① 空值判定（用原始值）
      ② NFKC 全形轉半形（'１，２３４．５％' → '1,234.5%'）
      ③ 去千分位與幣別符號
      ④ 會計括號負數 / 尾端負號 → 負值
      ⑤ 百分比處理（是否 /100 由「欄位語意」決定，不是由值本身猜）
      ⑥ 萬／億進位
      ⑦ 嚴格數字格式比對（拒絕 '12abc' 這種部分可解析的垃圾）
    失敗時 reason 說明卡在哪一步，呼叫端負責把值放進「無法解析」清單。
    """
    if raw is None:
        return ParseOutcome(ok=False, reason="空值")
    if isinstance(raw, bool):
        return ParseOutcome(ok=False, reason="布林值不是數值")
    if isinstance(raw, (int, float)):
        return ParseOutcome(
            ok=True, value=float(raw), normalized=str(raw), rule="原生數值"
        )
    if isinstance(raw, (dt_mod.datetime, dt_mod.date, dt_mod.time)):
        return ParseOutcome(ok=False, reason="日期值不視為金額/數量")

    original = str(raw)
    text = unicodedata.normalize("NFKC", original).strip()
    if not text:
        return ParseOutcome(ok=False, reason="空值")

    rules: list[str] = []
    if text != original.strip():
        rules.append("NFKC 全形轉半形")

    # ③ 千分位與空白
    stripped = text.replace(",", "").replace("，", "").replace(" ", "").replace("　", "")
    if stripped != text:
        rules.append("去千分位")
    text = stripped

    # ③ 幣別符號
    for tok in CURRENCY_TOKENS:
        if tok in text:
            text = text.replace(tok, "")
            rules.append(f"去幣別符號 {tok}")
    text = text.strip()

    # ④ 會計括號負數 / 尾端負號
    negative = False
    if text.startswith("(") and text.endswith(")"):
        negative = True
        text = text[1:-1].strip()
        rules.append("會計括號負數 ( )")
    if text.endswith("-"):
        negative = True
        text = text[:-1].strip()
        rules.append("尾端負號 -")

    # ⑤ 百分比
    is_percent = False
    if text.endswith("%"):
        is_percent = True
        text = text[:-1].strip()
        rules.append("百分比符號 %")

    # ⑥ 萬／億倍率
    scale = 1.0
    for tok, factor in SCALE_TOKENS.items():
        if tok in text:
            text = text.replace(tok, "")
            scale *= factor
            rules.append(f"單位進位 {tok}（x{factor:,}）")
    text = text.strip()

    # ⑦ 嚴格比對
    if not _NUM_RE.match(text):
        return ParseOutcome(
            ok=False,
            normalized=text,
            reason=f"正規化後「{text}」不符合數字格式",
        )

    number = float(text)
    if scale != 1.0:
        number *= scale
    if negative:
        number = -number
        rules.append("負號")

    # 百分比語意：欄位語意決定，不能由值本身猜。
    if is_percent:
        if is_rate_column:
            number = number / 100.0
            rules.append("百分比 /100（欄名含率/百分比）")
        else:
            return ParseOutcome(
                ok=False,
                normalized=text,
                reason="百分比值出現在非百分比欄位（欄名未含率/百分比），不猜語意",
            )
    elif is_rate_column and not isinstance(raw, (int, float)):
        # 率欄位裡的「文字型數字」：套用「這個欄位」決定好的 scale。
        # 為什麼不能逐值決定：同一欄裡 '0.5'（文字）與 0.95（原生）若各自決定，
        # 會得到 0.005 與 0.95 —— 同一欄裡兩個尺度，合計直接是垃圾。
        # scale 由欄位層級推導（見 infer_column_scale），這裡只套用。
        scale_factor = rate_scale if rate_scale is not None else 0.01
        number = number * scale_factor
        if scale_factor != 1.0:
            rules.append(
                f"率欄位文字值 x{scale_factor:g}（欄名含率/百分比；本欄尺度由原生值推導）"
            )

    normalized_text = f"{number:.10g}"
    return ParseOutcome(ok=True, value=number, normalized=normalized_text, rule="、".join(rules))


def is_rate_header(header: str) -> bool:
    low = header.lower()
    return any(kw in header or kw in low for kw in RATE_KEYWORDS)


def is_numeric_named_header(header: str) -> bool:
    """欄名看起來應該是數值欄（金額／件數／數量…）。

    先去掉自動去重後綴（_2、_3）再判斷，否則「經費項目_2」會繞過標籤欄排除規則。
    """
    base = re.sub(r"_\d+$", "", header)
    if any(base.endswith(sfx) for sfx in LABEL_SUFFIXES):
        return False
    low = base.lower()
    return any(kw in base or kw in low for kw in NUMERIC_NAME_KEYWORDS)


# 小計列的識別字：這一列是「彙總列」不是「資料列」。
# 實測（2026-10-27）：來源表第 4 列（經費項目='合計'、核定金額=800000）被當成
# 一般資料列再累加一次 → 合計回報 1600000（正確值 800000），金額 double。
# 這個缺陷與「文字型金額靜默漏算」同族：都是把資料形狀的意義弄錯了。
SUBTOTAL_LABEL_KEYWORDS = (
    "合計", "小計", "總計", "累計", "總合", "總額",
    "total", "subtotal", "sum", "grand total",
)


def is_subtotal_label(value) -> bool:
    """判斷某個儲存格的值是不是小計列的標籤（合計／小計／total…）。

    只看「整格剛好就是這些字」——「合計數」這種欄位名不會被誤判，
    因為這裡判斷的是儲存格的值，不是欄名。
    """
    if value is None or isinstance(value, bool):
        return False
    text = str(value).strip()
    if not text:
        return False
    # 去掉常見綴字後再比對（例：「小計(1)」「合計:」）
    normalized = re.sub(r"[\s:：()（）\[\]【】.、_-]+$", "", text)
    if not normalized:
        return False
    low = normalized.lower()
    return any(normalized == kw or low == kw.lower() for kw in SUBTOTAL_LABEL_KEYWORDS)


def pick_subtotal_label_column(sheet: SheetData) -> str | None:
    """挑出「最可能是標籤欄」的那一欄（用來辨識小計列）。

    判斷順序：
      1. 欄名看起來像分類／名稱的欄（經費項目、項目別、類別…）→ 優先
      2. 否則用資料實證：那一欄的非空值是文字的比例最高，且不含數字
      3. 全域都是數值 → 沒有標籤欄 → 回傳 None（不猜）

    回傳 None 代表「這個分頁沒有可用的標籤欄」→ 不做小計列判定，
    而不是把某個數值欄當成標籤欄亂猜。
    """
    if not sheet.headers:
        return None
    # 1. 欄名語意優先：結尾是分類／名稱類關鍵字、且不是數值欄
    named = [
        h for h in sheet.headers
        if h not in sheet.numeric_headers
        and any(h.rstrip("0123456789_ ").endswith(sfx) for sfx in LABEL_SUFFIXES)
    ]
    if named:
        return named[0]

    # 2. 資料實證：文字比例最高且沒有任何數字值的那一欄
    best: tuple[str, float] | None = None
    for h in sheet.headers:
        values = [v for v in (row[sheet.headers.index(h)] for row in sheet.rows)
                  if classify_value(v) != "empty"]
        if not values:
            continue
        text_ratio = sum(
            1 for v in values
            if not isinstance(v, bool) and not isinstance(v, (int, float))
        ) / len(values)
        has_number = any(
            isinstance(v, (int, float)) and not isinstance(v, bool) for v in values
        )
        if has_number:
            continue
        if best is None or text_ratio > best[1]:
            best = (h, text_ratio)
    if best is not None and best[1] >= 0.5:
        return best[0]
    return None


# ---------- 合併儲存格 / 公式 的單次 XML 探測 ----------
def probe_xlsx_structure(path: Path) -> dict[str, dict]:
    """一次讀 xlsx 內部 XML，取出每個 sheet 的合併儲存格範圍與公式儲存格。

    為什麼不用 openpyxl：read_only=True 的 ReadOnlyWorksheet 沒有 merged_cells
    （實測 AttributeError），要拿合併範圍就必須整份載入（慢）。
    為什麼還要抓公式：data_only=True 讀「沒有快取值的公式」會拿到 None，
    等於資料被安靜吃掉——這跟「文字型金額靜默漏算」是同一族錯誤。

    失敗時回傳空 dict（不讓探測問題擋掉主流程，但會有對應警告）。
    """
    out: dict[str, dict] = {}
    try:
        with zipfile.ZipFile(path) as z:
            names = set(z.namelist())
            wb_xml = ET.fromstring(z.read("xl/workbook.xml"))
            rels_xml = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
            rmap = {r.get("Id"): r.get("Target") for r in rels_xml}
            sheets_el = wb_xml.find(f"{{{_XL_NS}}}sheets")
            if sheets_el is None:
                return out
            for sh in sheets_el:
                name = sh.get("name")
                rid = sh.get(f"{{{_XL_REL_NS}}}id")
                target = (rmap.get(rid) or "").lstrip("/")
                if not target:
                    continue
                if target not in names:
                    target = "xl/" + target
                if target not in names:
                    continue
                root = ET.fromstring(z.read(target))
                merges: list[str] = []
                mc = root.find(f"{{{_XL_NS}}}mergeCells")
                if mc is not None:
                    merges = [m.get("ref") for m in mc if m.get("ref")]
                formulas: list[str] = []
                for c in root.iter(f"{{{_XL_NS}}}c"):
                    if c.find(f"{{{_XL_NS}}}f") is not None:
                        ref = c.get("r")
                        if ref:
                            formulas.append(ref)
                out[name] = {"merges": merges, "formulas": sorted(formulas)}
    except (zipfile.BadZipFile, KeyError, ET.ParseError, OSError):
        return out
    return out


def parse_range(ref: str) -> tuple[int, int, int, int] | None:
    """把 'A1:B2' 解析成 (min_col, min_row, max_col, max_row)，1-based。"""
    m = re.match(r"^([A-Z]+)(\d+):([A-Z]+)(\d+)$", ref.replace("$", ""))
    if not m:
        return None

    def col_to_num(col: str) -> int:
        n = 0
        for ch in col:
            n = n * 26 + (ord(ch) - ord("A") + 1)
        return n

    try:
        c1 = col_to_num(m.group(1))
        r1 = int(m.group(2))
        c2 = col_to_num(m.group(3))
        r2 = int(m.group(4))
    except ValueError:
        return None
    return (min(c1, c2), min(r1, r2), max(c1, c2), max(r1, r2))


# ---------- 表頭列自動判定（今日卡片 Q2） ----------
def score_header_candidate(
    rows: list[tuple[int, tuple]],
    idx: int,
    n_cols: int,
    merge_filled: dict[int, list[int]] | None = None,
) -> tuple[float, list[str], str]:
    """評分單一候選表頭列。

    判準（型別互斥）：候選列某欄是文字、而其下整欄的實質型別不是純文字
    → 該欄這列才像欄名。單看「這列全是文字」會誤判（資料列也可能是全文字）。

    回傳 (score 0..1, evidence 逐欄說明, 淘汰理由)。
    """
    header_vals = rows[idx][1]
    below = rows[idx + 1:]
    if not below:
        return 0.0, [], "候選列是最後一列，下方沒有資料列可比對"

    non_empty_cols = 0
    support = 0
    eligible = 0
    evidence: list[str] = []
    numeric_header_cols = 0
    for c in range(n_cols):
        h = header_vals[c] if c < len(header_vals) else None
        ht = classify_value(h)
        if ht == "empty":
            continue
        non_empty_cols += 1
        below_types = set()
        for _, r in below:
            v = r[c] if c < len(r) else None
            bt = classify_value(v)
            if bt != "empty":
                below_types.add(bt)
        if ht == "text":
            eligible += 1
            # 型別互斥：欄名是文字，而下方整欄是「數值型或日期型」→ 這欄這列像欄名。
            # 關鍵細節：下方「全是文字」不算支持 —— 因為資料列本身也可能是全文字
            # （例如 業務費 / 1,234,000 / 98% 三欄都是文字）。
            below_is_specific = bool(below_types) and not (
                below_types <= {"text"}
            )
            if below_is_specific:
                support += 1
                evidence.append(
                    f"欄{c + 1} 表頭為文字、下方為 {'/'.join(sorted(below_types))}（型別互斥成立）"
                )
            else:
                evidence.append(
                    f"欄{c + 1} 表頭為文字、下方也是文字（不構成型別互斥）"
                )
        else:
            # 表頭儲存格本身是數值／日期／布林 → 這比較像資料列不像欄名
            numeric_header_cols += 1
            evidence.append(f"欄{c + 1} 表頭本身是 {ht}（不像欄名）")

    if non_empty_cols == 0:
        return 0.0, [], "候選列沒有任何內容"
    if numeric_header_cols == non_empty_cols:
        return 0.0, evidence, "所有欄位都不是文字型欄名"

    # 欄名唯一性（必要條件）：重複＝多半是資料不是欄名。
    # 例外：合併儲存格補出來的欄名天生就會重複（同一橫列多欄共用一個名稱），
    # 那不是「資料冒充欄名」，要排除掉再檢查唯一性。
    merged_cols = set()
    if merge_filled:
        for excel_row, cols in merge_filled.items():
            if excel_row == rows[idx][0]:
                merged_cols.update(cols)
    names = [
        str(v).strip()
        for c, v in enumerate(header_vals)
        if v is not None and str(v).strip() and c not in merged_cols
    ]
    if names and len(set(names)) != len(names):
        return 0.0, evidence, "欄名有重複（欄名必須唯一）"

    # 非空比例：避免把只有一格有值的說明列當表頭
    fill_ratio = non_empty_cols / n_cols if n_cols else 0.0
    if fill_ratio < HEADER_MIN_FILL_RATIO:
        return 0.0, evidence, f"非空比例 {fill_ratio:.2f} 低於門檻 {HEADER_MIN_FILL_RATIO}"

    ratio_all = support / non_empty_cols
    ratio_eligible = support / eligible if eligible else 0.0
    score = max(ratio_all, ratio_eligible)
    # 欄名含數字/符號（例如「2026 年預算」）仍可能是合法欄名，不做額外懲罰。
    return score, evidence, ""


def detect_header_row(sheet: SheetRaw, n_cols: int) -> HeaderDecision:
    """自動判定表頭列。判定失敗時回傳可行動的錯誤訊息（不猜一個）。"""
    candidates: list[tuple[int, float]] = []
    best: tuple[int, float, list[str]] | None = None
    limit = min(len(sheet.rows) - 1, HEADER_DETECT_MAX_CANDIDATES)
    # 只有表頭、沒有資料列的分頁：無法用「型別互斥」判定，
    # 但「第一個非空列有欄名且欄名唯一」是可以接受的（沒有資料可比對時的合理退路）。
    if len(sheet.rows) == 1:
        header_vals = sheet.rows[0][1]
        names = [
            str(v).strip()
            for c, v in enumerate(header_vals)
            if v is not None and str(v).strip()
        ]
        merged_cols = set()
        for excel_row, cols in (sheet.merge_filled or {}).items():
            if excel_row == sheet.rows[0][0]:
                merged_cols.update(cols)
        real_names = [
            str(v).strip()
            for c, v in enumerate(header_vals)
            if v is not None and str(v).strip() and c not in merged_cols
        ]
        fill_ratio = len(names) / n_cols if n_cols else 0.0
        problems = []
        if not names:
            problems.append("該列沒有任何欄位名稱")
        if real_names and len(set(real_names)) != len(real_names):
            problems.append("欄名有重複（欄名必須唯一）")
        if fill_ratio < HEADER_MIN_FILL_RATIO:
            problems.append(f"非空比例 {fill_ratio:.2f} 低於門檻 {HEADER_MIN_FILL_RATIO}")
        if not problems:
            return HeaderDecision(
                header_index=0,
                score=1.0,
                method="auto",
                evidence=[
                    f"這個分頁只有表頭列、沒有資料列（無型別可比對），"
                    f"但欄名完整且唯一（{len(real_names)} 欄）"
                ],
                candidates=[(0, 1.0)],
            )
        return HeaderDecision(
            method="auto",
            candidates=[(0, 0.0)],
            reason=(
                f"無法判定 {sheet.file_name} / {sheet.sheet_name} 的表頭列："
                f"這個分頁只有 1 個非空列，且{'、'.join(problems)}。"
                f"請用 --header-row N 指定（第幾列為表頭，0-based，索引『非空列』序列）。"
            ),
        )
    for i in range(max(limit, 0)):
        score, evidence, _reason = score_header_candidate(
            sheet.rows, i, n_cols, sheet.merge_filled
        )
        candidates.append((i, score))
        if best is None or score > best[1]:
            best = (i, score, evidence)
    candidates.sort(key=lambda x: (-x[1], x[0]))

    if best is None or best[1] <= 0:
        scores = [f"{s:.2f}" for _, s in candidates[:5]]
        return HeaderDecision(
            method="auto",
            candidates=candidates[:5],
            reason=(
                f"無法判定 {sheet.file_name} / {sheet.sheet_name} 的表頭列："
                f"前 {len(scores)} 個候選列的分數 [{', '.join(scores)}] 全為 0，"
                f"都低於門檻 {HEADER_DETECT_THRESHOLD}。"
                f"請用 --header-row N 指定（第幾列為表頭，0-based，索引『非空列』序列）。"
            ),
        )

    if best[1] < HEADER_DETECT_THRESHOLD:
        scores = [f"{s:.2f}" for _, s in candidates[:5]]
        return HeaderDecision(
            method="auto",
            candidates=candidates[:5],
            reason=(
                f"無法判定 {sheet.file_name} / {sheet.sheet_name} 的表頭列："
                f"前 {len(scores)} 個候選列的分數 [{', '.join(scores)}] 均低於門檻 "
                f"{HEADER_DETECT_THRESHOLD}。請用 --header-row N 指定"
                f"（第幾列為表頭，0-based，索引『非空列』序列）。"
            ),
        )

    if len(candidates) >= 2:
        second = candidates[1][1]
        if second > 0 and (best[1] - second) < HEADER_DETECT_MARGIN:
            # 兩個候選得分幾乎一樣 → 真正的表頭列無法確定。
            # 這裡「不猜」：回報候選與得分，要求使用者用 --header-row 指定。
            scores = [f"{s:.2f}" for _, s in candidates[:5]]
            return HeaderDecision(
                method="auto",
                candidates=candidates[:5],
                reason=(
                    f"無法判定 {sheet.file_name} / {sheet.sheet_name} 的表頭列："
                    f"前兩名候選的分數 [{', '.join(scores)}] 差距小於 "
                    f"{HEADER_DETECT_MARGIN}，模稜兩可。請用 --header-row N 指定"
                    f"（第幾列為表頭，0-based，索引『非空列』序列）。"
                ),
            )

    return HeaderDecision(
        header_index=best[0],
        score=round(best[1], 4),
        method="auto",
        evidence=best[2],
        candidates=candidates[:5],
    )


def build_headers(
    raw_values: tuple, header_row_excel: int, merged_ranges: list[str], file_name: str, sheet_name: str
) -> tuple[list[str], list[str]]:
    """從表頭列建立欄名；處理合併儲存格（補上被吞掉的欄名）與重複欄名。

    回傳 (headers, warnings)。
    """
    warnings: list[str] = []
    values = list(raw_values)
    # 合併儲存格補欄名：範圍左上角以外的欄，其值在 openpyxl 讀出來是 None。
    # 對 header row 做 forward-fill（把左上角的值補給同一橫列的其它欄）。
    for ref in merged_ranges:
        rng = parse_range(ref)
        if not rng:
            continue
        c1, r1, c2, r2 = rng
        if r1 != header_row_excel or r1 != r2:
            continue  # 只處理同一橫列的合併（跨列合併不影響欄名）
        if c2 <= c1:
            continue
        anchor_idx = c1 - 1
        if anchor_idx >= len(values) or values[anchor_idx] is None:
            continue
        anchor_val = values[anchor_idx]
        for c in range(c1, c2 + 1):
            idx = c - 1
            if idx >= len(values):
                values.append(None)
            if values[idx] is None:
                values[idx] = anchor_val
                warnings.append(
                    f"合併儲存格 {ref} 吞掉欄 {c} 的欄名，已補上左上角的值「{anchor_val}」"
                )

    last_named = -1
    for idx, h in enumerate(values):
        if h is not None and str(h).strip():
            last_named = idx
    if last_named < 0:
        return [], warnings + ["表頭列沒有任何欄位名稱"]

    headers: list[str] = []
    used: dict[str, int] = {}
    for idx in range(last_named + 1):
        h = values[idx]
        name = "" if h is None else str(h).strip()
        if not name:
            name = f"欄{idx + 1}"
        if name in used:
            used[name] += 1
            new_name = f"{name}_{used[name]}"
            warnings.append(
                f"表頭有重複欄名「{name}」（第 {idx + 1} 欄），已自動改名為「{new_name}」"
            )
            name = new_name
        else:
            used[name] = 1
        headers.append(name)
    return headers, warnings


# ---------- 讀取 ----------
def _cell_value(value):
    """把 openpyxl 讀到的值轉成可安全寫回的型別。"""
    if value is None:
        return None
    if isinstance(value, (dt_mod.datetime, dt_mod.date, dt_mod.time)):
        return value
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value
    return str(value)


def read_raw_file(path: Path) -> tuple[list[SheetRaw], str | None]:
    """讀單一 Excel 的原始結構（未判定表頭、未正規化）。"""
    structure = probe_xlsx_structure(path)
    result: list[SheetRaw] = []
    try:
        wb = load_workbook(path, read_only=True, data_only=True)
    except Exception as exc:  # noqa: BLE001 - 對外 IO 一律要可行動錯誤
        return [], (
            f"無法開啟 {path.name}：{type(exc).__name__}: {exc}。"
            "常見原因：檔案被 Excel 鎖住（關掉 Excel 再試）、檔案損毀、"
            "或密碼保護（先另存為無密碼版本）。"
        )

    try:
        for sheet_name in wb.sheetnames:
            raw = SheetRaw(file_name=path.name, sheet_name=sheet_name)
            info = structure.get(sheet_name, {})
            raw.merged_ranges = list(info.get("merges", []))
            raw.formula_cells = list(info.get("formulas", []))
            try:
                rows_iter = list(wb[sheet_name].iter_rows(values_only=True))
            except Exception as exc:  # noqa: BLE001
                raw.error = f"讀取分頁失敗：{type(exc).__name__}: {exc}"
                result.append(raw)
                continue
            indexed = [(i, r) for i, r in enumerate(rows_iter, start=1)]
            non_empty = [(i, r) for i, r in indexed if any(v is not None for v in r)]
            if not non_empty:
                raw.error = "分頁是空的"
                result.append(raw)
                continue
            raw.rows = [(i, tuple(r)) for i, r in non_empty]
            _spread_merged_cells(raw)
            result.append(raw)
    finally:
        wb.close()
    return result, None


def _spread_merged_cells(raw: SheetRaw) -> None:
    """把「合併儲存格」左上角的值補到同一橫列的其它欄。

    為什麼要在表頭判定「之前」做：合併 A1:B1 時，openpyxl 讀出來 B1 是 None，
    表頭列看起來只有一格有值 → 非空比例不足 → 判定失敗。
    補完之後判定與輸出才一致（否則判定說「表頭在第 1 列」但輸出欄名對不上）。

    只處理「同一橫列」的合併（跨列合併不影響欄名）。
    垂直合併（欄名跨兩列）不在本版處理範圍，會在警告中揭露。
    """
    for ref in raw.merged_ranges:
        rng = parse_range(ref)
        if not rng:
            continue
        c1, r1, c2, r2 = rng
        if r1 != r2:
            continue  # 跨列合併：不做橫向補值
        if c2 <= c1:
            continue
        for row_idx, (excel_row, values) in enumerate(raw.rows):
            if excel_row != r1:
                continue
            cells = list(values)
            anchor_idx = c1 - 1
            if anchor_idx >= len(cells) or cells[anchor_idx] is None:
                continue
            anchor_val = cells[anchor_idx]
            filled: list[int] = []
            for c in range(c1, c2 + 1):
                idx = c - 1
                while len(cells) <= idx:
                    cells.append(None)
                if cells[idx] is None:
                    cells[idx] = anchor_val
                    filled.append(idx)
            raw.rows[row_idx] = (excel_row, tuple(cells))
            if filled:
                raw.merge_filled.setdefault(excel_row, []).extend(filled)


def parse_sheets(
    raw_sheets: list[SheetRaw], header_override: int | None
) -> list[SheetData]:
    """把原始結構轉成可合併的分頁：判定表頭列 → 建欄名 → 取資料列。"""
    out: list[SheetData] = []
    for raw in raw_sheets:
        sheet = SheetData(file_name=raw.file_name, sheet_name=raw.sheet_name)
        if raw.error:
            sheet.error = raw.error
            out.append(sheet)
            continue

        n_cols = max((len(r) for _, r in raw.rows), default=0)
        if header_override is not None:
            if header_override >= len(raw.rows):
                sheet.error = (
                    f"--header-row {header_override} 超出範圍：這個分頁只有 "
                    f"{len(raw.rows)} 個非空列（可指定 0..{len(raw.rows) - 1}，"
                    f"索引的是「非空列」序列、空列不計入）。"
                )
                out.append(sheet)
                continue
            decision = HeaderDecision(
                header_index=header_override,
                score=1.0,
                method="manual",
                evidence=[
                    f"使用者以 --header-row {header_override} 指定"
                    f"（{header_override + 1} 個非空列，0-based）"
                ],
            )
        else:
            decision = detect_header_row(raw, n_cols)
            if decision.header_index is None:
                sheet.error = decision.reason
                sheet.header = decision
                out.append(sheet)
                continue

        header_idx = decision.header_index
        header_orig_idx, header_values = raw.rows[header_idx]
        decision.header_excel_row = header_orig_idx
        headers, warns = build_headers(
            header_values, header_orig_idx, raw.merged_ranges, raw.file_name, raw.sheet_name
        )
        if not headers:
            sheet.error = "表頭列沒有任何欄位名稱"
            sheet.header = decision
            out.append(sheet)
            continue

        sheet.headers = headers
        sheet.header = decision
        sheet.warnings.extend(warns)

        # 合併儲存格補欄名的後果要揭露：這些欄的名稱是借來的（來自左上角），
        # 使用者要知道自己看到的欄名其實沒有自己的欄名。
        merged_header_cols = raw.merge_filled.get(header_orig_idx, [])
        if merged_header_cols:
            sheet.warnings.append(
                f"這個分頁的表頭列有合併儲存格（欄 "
                f"{', '.join(str(c + 1) for c in merged_header_cols)} 的欄名借自左上角）；"
                "這些欄沒有自己的名稱，已依資料型別重新命名，請確認資料對應是否正確。"
            )
        if decision.method == "auto":
            sheet.warnings.append(
                f"表頭列自動判定：第 {header_idx} 列（0-based，Excel 第 {header_orig_idx} 列），"
                f"分數 {decision.score:.2f}"
            )
        if raw.formula_cells:
            sheet.warnings.append(
                f"這個分頁有 {len(raw.formula_cells)} 個公式儲存格"
                f"（例如 {', '.join(raw.formula_cells[:3])}）。"
                "公式必須由 Excel 計算並存檔後才有快取值；未存檔的公式讀出來是空值。"
            )

        for r_idx, values in raw.rows[header_idx + 1:]:
            cells = [_cell_value(v) for v in values]
            if len(cells) > len(headers):
                sheet.warnings.append(
                    f"資料列比表頭多 {len(cells) - len(headers)} 欄，已截斷"
                )
            cells += [None] * (len(headers) - len(cells))
            cells = cells[: len(headers)]
            sheet.rows.append(cells)
            sheet.row_numbers.append(r_idx)

        # 無原名的欄（合併儲存格借來的）依「該欄的資料型別」重新命名。
        # 實測（2026-10-27）：e_合併儲存格.xlsx 第 2 欄其實是金額（100000/200000），
        # 卻被命名為「經費項目_2」→ 在「合併資料」分頁裡看起來像第二個經費分類，
        # 實際是金額。名稱誤導比沒有名稱更危險。
        if merged_header_cols:
            for idx in merged_header_cols:
                if idx >= len(headers):
                    continue
                col_values = [row[idx] for row in sheet.rows if idx < len(row)]
                numeric = sum(
                    1 for v in col_values
                    if isinstance(v, (int, float)) and not isinstance(v, bool)
                )
                non_empty = [v for v in col_values if classify_value(v) != "empty"]
                if non_empty and numeric >= len(non_empty) * 0.5:
                    suffix = "（數值）"
                else:
                    suffix = "（無原名）"
                old_name = headers[idx]
                new_name = f"欄{idx + 1}{suffix}"
                # 避免撞名
                used = {h for i, h in enumerate(headers) if i != idx}
                candidate = new_name
                n = 2
                while candidate in used:
                    candidate = f"{new_name}_{n}"
                    n += 1
                headers[idx] = candidate
                sheet.merge_filled_headers = [
                    candidate if h == old_name else h for h in sheet.merge_filled_headers
                ]
                if candidate not in sheet.merge_filled_headers:
                    sheet.merge_filled_headers.append(candidate)
                sheet.warnings.append(
                    f"欄 {idx + 1} 沒有自己的欄名（合併儲存格造成），"
                    f"原本借名為「{old_name}」，已改依資料型別命名為「{candidate}」"
                )
        out.append(sheet)
    return out


# ---------- 輸入集合界定 ----------
def default_exclusion_rules(output_path: Path, csv_paths: list[Path]) -> list[ExclusionRule]:
    """工具自己產生的檔案必須排除，否則重跑會自我合併（實測：8 列 → 36 列、金額 double）。"""
    stem = output_path.stem
    rules = [
        ExclusionRule("輸出檔本身", output_path.name, "是本工具的輸出檔，排除以避免自我合併", "suffix"),
        ExclusionRule("輸出檔備份", f"{stem}.bak-*", "是本工具的時間戳備份，排除以避免自我合併", "glob"),
        ExclusionRule("舊版輸出備份", f"{stem}.bak", "是本工具的舊版備份，排除以避免自我合併", "glob"),
        ExclusionRule("隱藏檔", ".*", "隱藏檔不納入", "prefix"),
        ExclusionRule("Excel 鎖檔", "~$*", "Excel 開檔時產生的鎖檔，不納入", "glob"),
    ]
    for csv_path in csv_paths:
        rules.append(
            ExclusionRule(
                f"摘要 CSV {csv_path.name}", csv_path.name, "是本工具的摘要輸出，排除以避免自我合併", "suffix"
            )
        )
        rules.append(
            ExclusionRule(
                f"摘要 CSV 備份 {csv_path.stem}.bak-*",
                f"{csv_path.stem}.bak-*",
                "是本工具的時間戳備份，排除以避免自我合併",
                "glob",
            )
        )
    return rules


def rule_matches(rule: ExclusionRule, path: Path) -> bool:
    name = path.name
    if rule.match == "glob":
        return fnmatch_mod.fnmatch(name, rule.pattern)
    if rule.match == "prefix":
        return name.startswith(rule.pattern)
    if rule.match == "suffix":
        return name.endswith(rule.pattern)
    return False


# 本工具產出的工作簿一定帶有這些分頁 —— 這是「內容指紋」，
# 用來認出「這是本工具的輸出」而不是靠檔名。
# 為什麼不能用檔名判斷：實測（2026-10-27）把舊的 merged.xlsx 放進輸入資料夾、
# 這次 -o 用 merged2.xlsx → 舊輸出被當成來源檔合併進去（資料重複、金額 double）。
# 排除規則綁定「本次輸出的檔名」就會被改名繞過 → 必須用內容判斷。
SELF_OUTPUT_MARKER_SHEETS = ("本次執行", "輸入集合")


def is_self_output_workbook(path: Path) -> bool:
    """判斷這個 .xlsx 是不是本工具自己產出的工作簿（讀分頁名，不讀資料）。

    讀不到（不是 xlsx／損壞／沒有 openpyxl）→ 回 False（交由後續流程回報錯誤），
    不在這裡猜。
    """
    try:
        from openpyxl import load_workbook

        wb = load_workbook(path, read_only=True)
        try:
            names = set(wb.sheetnames)
        finally:
            wb.close()
    except Exception:
        return False
    return all(marker in names for marker in SELF_OUTPUT_MARKER_SHEETS)


def scan_inputs(
    folder: Path, rules: list[ExclusionRule]
) -> tuple[list[Path], list[tuple[str, str]], list[dict]]:
    """列出要合併的 .xlsx。回傳 (要合併的檔案, 被略過[(檔名, 原因)], 輸入集合明細)。

    遞迴掃描子資料夾：使用者的行政資料是按年度／單位分資料夾放的
    （113年度/、114年度/…），只掃一層會直接報「找不到 .xlsx 檔案」。
    來源相對路徑保留在 manifest 的 name 欄（用 / 分隔），讓不同子資料夾的
    同名檔不會在報告裡混淆。
    """
    files: list[Path] = []
    skipped: list[tuple[str, str]] = []
    manifest: list[dict] = []
    for path in sorted(folder.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(folder)
        display_name = rel.as_posix()
        suffix = path.suffix.lower()
        matched = next((r for r in rules if rule_matches(r, path)), None)
        if matched is not None:
            skipped.append((display_name, f"{matched.name}：{matched.reason}"))
            manifest.append({"name": display_name, "decision": "排除", "reason": matched.reason, "sha256": ""})
            continue
        if suffix not in INPUT_SUFFIXES:
            reason = ""
            if suffix in OTHER_EXCEL_SUFFIXES:
                reason = f"副檔名 {suffix} 不支援（{suffix} 舊格式請在 Excel 另存為 .xlsx）"
                skipped.append((display_name, reason))
            manifest.append({"name": display_name, "decision": "略過", "reason": reason or f"副檔名 {suffix} 不是 .xlsx", "sha256": ""})
            continue
        # 內容指紋判斷：這是本工具自己產出的工作簿 → 排除，不論檔名叫什麼。
        # 綁定檔名的排除規則會被改名繞過（實測 2026-10-27）。
        if is_self_output_workbook(path):
            reason = (
                "內容判斷：這是本工具自己產出的合併工作簿（含「本次執行」「輸入集合」分頁）"
                "→ 排除以避免自我合併（資料重複、金額 double）"
            )
            skipped.append((display_name, reason))
            manifest.append({"name": display_name, "decision": "排除", "reason": reason, "sha256": ""})
            continue
        files.append(path)
        manifest.append({"name": display_name, "decision": "納入", "reason": "符合納入條件（.xlsx）", "sha256": ""})
    return files, skipped, manifest


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 256), b""):
            h.update(chunk)
    return h.hexdigest()


# ---------- 正規化與統計（跨檔統一做，因為欄位語意是跨檔一致的） ----------
def infer_column_scale(
    sheets: list[SheetData], header: str
) -> tuple[float | None, str]:
    """推導「率欄位」的尺度倍率（整欄一致，不逐值決定）。

    問題：同一欄裡混了原生值 0.95 與文字值 '0.5'。若逐值決定，
    文字值會被 /100 → 0.005，與原生值 0.95 差 190 倍 → 合計是垃圾。

    規則（看原生值就能定案，不用猜）：
      - 原生值全部 ≤ 1        → 尺度 1（原生值已經是比率，例如 0.95）
      - 原生值全部 > 1 且 ≤ 100 → 尺度 0.01（原生值是百分點數字，例如 95）
      - 原生值有 ≤1 也有 >1    → 尺度無法推導 → 回傳 None + 警告
      - 沒有原生值             → 尺度無法推導 → 回傳 None + 警告

    回傳 (scale, 說明)。scale=None 代表「不換算、並留下警告」。
    """
    native = []
    for sheet in sheets:
        if sheet.error:
            continue
        for row in sheet.rows:
            for h, v in zip(sheet.headers, row):
                if h != header:
                    continue
                if isinstance(v, bool) or not isinstance(v, (int, float)):
                    continue
                native.append(float(v))

    if not native:
        return None, (
            f"率欄位「{header}」沒有任何原生數值可推導尺度（全部是文字）"
            f"→ 文字率值不換算，請人工確認"
        )
    has_le_1 = any(v <= 1.0 for v in native)
    has_gt_1 = any(v > 1.0 for v in native)
    if has_le_1 and has_gt_1:
        return None, (
            f"率欄位「{header}」同時有 ≤1 與 >1 的原生值（{min(native)}..{max(native)}），"
            f"尺度無法推導 → 文字率值不換算，請人工確認"
        )
    if has_gt_1:
        return 0.01, (
            f"率欄位「{header}」的原生值皆 >1（{min(native)}..{max(native)}），"
            f"推導尺度為百分點（文字值 x0.01）"
        )
    return 1.0, (
        f"率欄位「{header}」的原生值皆 ≤1（{min(native)}..{max(native)}），"
        f"推導尺度已是比率（文字值不換算）"
    )


def detect_sheet_numeric_headers(sheet: SheetData) -> set[str]:
    """判定「這個分頁」裡哪些欄位是數值欄。

    規則（每個分頁各自判定，但規則本身跨檔一致）：
      - 非空值中「可解析成數字」的比例 ≥ NUMERIC_COLUMN_RATIO → 數值欄
      - 例外：欄名看起來應該是數值（金額／件數…），即使比例低也要當數值欄 ——
        否則「一個壞值就讓整欄變成文字欄」，壞值會被靜默吞掉（這正是 v3 的盲區）。
    """
    non_empty: dict[str, int] = {}
    parseable: dict[str, int] = {}
    for row in sheet.rows:
        for h, v in zip(sheet.headers, row):
            if classify_value(v) == "empty":
                continue
            non_empty[h] = non_empty.get(h, 0) + 1
            if parse_number(v, h, is_rate_header(h)).ok:
                parseable[h] = parseable.get(h, 0) + 1

    numeric: set[str] = set()
    for h in sheet.headers:
        total = non_empty.get(h, 0)
        if total == 0:
            continue
        ratio = parseable.get(h, 0) / total
        if ratio >= NUMERIC_COLUMN_RATIO:
            numeric.add(h)
        elif is_numeric_named_header(h):
            numeric.add(h)
            sheet.column_warnings.append(
                f"欄位「{h}」有 {total - parseable.get(h, 0)}/{total} 個值無法解析成數字，"
                f"但欄名顯示它應該是數值欄 → 這些值已列入「無法解析」清單"
            )
    return numeric


def normalize_values(
    sheets: list[SheetData], union: list[str]
) -> tuple[dict[str, list[dict]], dict[str, list[dict]], set[str]]:
    """跨檔正規化：同一個欄名在所有檔案裡用同一套規則。

    回傳 (conversions_by_header, unparsed_by_header, numeric_columns)。
    numeric_columns 在這裡算（唯一來源），呼叫端不要再自己算一份 ——
    兩份實作不一致會讓「合計」與「寫回的數值」對不上（code SOP §8 的教訓）。
    """
    conversions: dict[str, list[dict]] = {h: [] for h in union}
    unparsed: dict[str, list[dict]] = {h: [] for h in union}
    numeric_columns: set[str] = set()

    # 率欄位的尺度：整欄一致（先推導一次，再套用到所有分頁的所有值）
    rate_scales: dict[str, float | None] = {}
    for h in union:
        if is_rate_header(h):
            scale, note = infer_column_scale(sheets, h)
            rate_scales[h] = scale
            for sheet in sheets:
                if sheet.error:
                    continue
                if any(sh == h for sh in sheet.headers):
                    sheet.column_warnings.append(note)
                    sheet.rate_scales[h] = scale

    for sheet in sheets:
        if sheet.error:
            continue
        sheet.numeric_headers = detect_sheet_numeric_headers(sheet)
        numeric_columns |= sheet.numeric_headers
        # 小計列要從合計裡排除，但資料本身仍要保留在「合併資料」中
        # （使用者可能想看到原始的合計列；只是不能把它再算一次）。
        label_header = pick_subtotal_label_column(sheet)

        for row_idx, row in enumerate(sheet.rows):
            excel_row = sheet.row_numbers[row_idx] if row_idx < len(sheet.row_numbers) else row_idx + 2
            is_subtotal_row = False
            if label_header is not None:
                try:
                    label_value = row[sheet.headers.index(label_header)]
                except (ValueError, IndexError):
                    label_value = None
                if is_subtotal_label(label_value):
                    is_subtotal_row = True
                    sheet.subtotal_rows.append(
                        {
                            "row": excel_row,
                            "label": str(label_value).strip(),
                            "reason": "標籤欄的值是彙總字（合計／小計／total…）→ 這一列是小計列，"
                                      "不重複計入合計",
                        }
                    )
            for h, v in zip(sheet.headers, row):
                if classify_value(v) == "empty":
                    continue
                if is_subtotal_row:
                    # 小計列：留痕但不累加（否則合計 double）
                    if h in sheet.numeric_headers:
                        outcome = parse_number(
                            v, h, is_rate_header(h), rate_scale=rate_scales.get(h)
                        )
                        if outcome.ok and outcome.rule != "原生數值":
                            conversions[h].append(
                                {
                                    "file": sheet.file_name,
                                    "sheet": sheet.sheet_name,
                                    "row": excel_row,
                                    "col": h,
                                    "raw": str(v),
                                    "normalized": outcome.normalized,
                                    "rule": outcome.rule + "（小計列，已排除於合計）",
                                }
                            )
                    continue
                if h not in sheet.numeric_headers:
                    # 文字欄位：若值含數字卻解析失敗，仍要留痕（可能是型別錯置）
                    s = str(v)
                    if any(ch.isdigit() for ch in s):
                        outcome = parse_number(v, h, is_rate_header(h))
                        if not outcome.ok:
                            unparsed[h].append(
                                {
                                    "file": sheet.file_name,
                                    "sheet": sheet.sheet_name,
                                    "row": excel_row,
                                    "col": h,
                                    "raw": s,
                                    "reason": f"文字欄位含數字但無法解析：{outcome.reason}",
                                }
                            )
                    continue

                outcome = parse_number(
                    v, h, is_rate_header(h), rate_scale=rate_scales.get(h)
                )
                if outcome.ok:
                    if outcome.rule != "原生數值":
                        conversions[h].append(
                            {
                                "file": sheet.file_name,
                                "sheet": sheet.sheet_name,
                                "row": excel_row,
                                "col": h,
                                "raw": str(v),
                                "normalized": outcome.normalized,
                                "rule": outcome.rule,
                            }
                        )
                    sheet.numeric_sums[h] = round(
                        sheet.numeric_sums.get(h, 0.0) + outcome.value, 10
                    )
                    sheet.numeric_counts[h] = sheet.numeric_counts.get(h, 0) + 1
                    if is_rate_header(h):
                        # 比率欄位做「合計」沒有意義（多筆加起來 >1 沒人看得懂），
                        # 改記平均與範圍。這是分析語意，不是技術限制。
                        sheet.rate_stats.setdefault(h, []).append(outcome.value)
                    # 警示要用「正規化後」的數值，文字型金額的負值也必須被抓到
                    reasons: list[str] = []
                    header_lower = h.lower()
                    if any(kw.lower() in header_lower for kw in REFUND_KEYWORDS):
                        reasons.append("退款關鍵欄")
                    if outcome.value < 0:
                        reasons.append("負值")
                    if reasons:
                        sheet.alerts.append(
                            {
                                "file": sheet.file_name,
                                "sheet": sheet.sheet_name,
                                "row": excel_row,
                                "header": h,
                                "value": outcome.value,
                                "raw": str(v),
                                "reason": "、".join(reasons),
                            }
                        )
                else:
                    unparsed[h].append(
                        {
                            "file": sheet.file_name,
                            "sheet": sheet.sheet_name,
                            "row": excel_row,
                            "col": h,
                            "raw": str(v),
                            "reason": outcome.reason,
                        }
                    )
    return conversions, unparsed, numeric_columns


def apply_normalized_values(sheets: list[SheetData], union: list[str], numeric_columns: set[str]) -> None:
    """把正規化後的數值寫回資料列（讓 Excel 直接能加總），同時保留無法解析的原值。

    用「每個分頁自己的 numeric_headers」判斷，而不是全域 union ——
    否則一個分頁的判定結果會蓋掉另一個分頁（跨檔語意一致 ≠ 每個分頁都一樣）。
    """
    for sheet in sheets:
        if sheet.error:
            continue
        for row_idx, row in enumerate(sheet.rows):
            for c, h in enumerate(sheet.headers):
                if h not in sheet.numeric_headers:
                    continue
                v = row[c]
                if classify_value(v) == "empty":
                    continue
                outcome = parse_number(
                    v, h, is_rate_header(h), rate_scale=sheet.rate_scales.get(h)
                )
                if outcome.ok:
                    row[c] = outcome.value


# ---------- 合併 ----------
def union_headers(sheets: list[SheetData]) -> list[str]:
    """跨檔欄位聯集：依首次出現順序。"""
    out: list[str] = []
    seen: set[str] = set()
    for sheet in sheets:
        for h in sheet.headers:
            if h not in seen:
                seen.add(h)
                out.append(h)
    return out


def merge_all(
    folder: Path,
    output_path: Path,
    csv_paths: list[Path],
    user_rules: list[ExclusionRule],
    header_override: int | None = None,
    per_file_header: dict[str, int] | None = None,
) -> tuple[list[FileResult], list[SheetData], list[str], list[tuple[str, str]], list[dict]]:
    """掃描並解析資料夾內所有 Excel。"""
    results: list[FileResult] = []
    usable: list[SheetData] = []
    errors: list[str] = []
    rules = default_exclusion_rules(output_path, csv_paths) + user_rules
    files, skipped, manifest = scan_inputs(folder, rules)

    for path in files:
        # 來源名稱用「相對輸入資料夾的路徑」：遞迴掃描後不同子資料夾可能
        # 有同名檔（113年度/經費.xlsx 與 114年度/經費.xlsx），用 basename
        # 會讓它們在報告裡混成同一個檔案。
        display_name = path.relative_to(folder).as_posix()
        result = FileResult(file_name=display_name)
        try:
            result.sha256 = sha256_of(path)
            result.size = path.stat().st_size
        except OSError as exc:
            result.error = f"無法讀取檔案資訊：{type(exc).__name__}: {exc}"
        for entry in manifest:
            if entry["name"] == display_name:
                entry["sha256"] = result.sha256
        raw_sheets, file_error = read_raw_file(path)
        if file_error:
            result.error = file_error
            errors.append(file_error)
            print(f"  ✗ 略過 {display_name}：{file_error}", file=sys.stderr)
            results.append(result)
            continue
        # 表頭列覆寫可以用相對路徑或單純檔名指定（後者套用到所有同名檔）
        file_override = (per_file_header or {}).get(
            display_name, (per_file_header or {}).get(path.name, header_override)
        )
        result.sheets = parse_sheets(raw_sheets, header_override=file_override)
        # 分頁的 file_name 要用相對路徑（否則不同子資料夾的同名檔會混在一起）
        for sheet in result.sheets:
            sheet.file_name = display_name
        for sheet in result.sheets:
            if sheet.error:
                errors.append(f"{display_name} / {sheet.sheet_name}：{sheet.error}")
                print(f"  ✗ {display_name} / {sheet.sheet_name}：{sheet.error}", file=sys.stderr)
                if "表頭列" in sheet.error:
                    result.needs_manual_header = True
                continue
            usable.append(sheet)
        results.append(result)
    return results, usable, errors, skipped, manifest


# ---------- 寫出 ----------
def _style_header(ws, headers: list[str], fill: str = "D9E1F2") -> None:
    for idx, h in enumerate(headers, start=1):
        cell = ws.cell(row=1, column=idx, value=h)
        cell.font = Font(bold=True)
        cell.fill = PatternFill("solid", fgColor=fill)


def _autosize(ws, widths: list[int]) -> None:
    for idx, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(idx)].width = w


def build_workbook(
    results: list[FileResult],
    usable: list[SheetData],
    union: list[str],
    input_folder: Path,
    output_path: Path,
    csv_paths: list[Path],
    csv_encoding: str,
    skipped: list[tuple[str, str]] | None = None,
    manifest: list[dict] | None = None,
    conversions: dict[str, list[dict]] | None = None,
    unparsed: dict[str, list[dict]] | None = None,
    numeric_columns: set[str] | None = None,
) -> Workbook:
    wb = Workbook()

    # Sheet 1：合併資料
    ws_data = wb.active
    ws_data.title = "合併資料"
    headers = union + ["_來源檔", "_來源分頁", "_來源列號"]
    _style_header(ws_data, headers)
    row_idx = 2
    for sheet in usable:
        for i, values in enumerate(sheet.rows):
            mapping = dict(zip(sheet.headers, values))
            cells = [mapping.get(h) for h in union]
            src_row = sheet.row_numbers[i] if i < len(sheet.row_numbers) else i + 2
            cells += [sheet.file_name, sheet.sheet_name, src_row]
            for c_idx, value in enumerate(cells, start=1):
                ws_data.cell(row=row_idx, column=c_idx, value=value)
            row_idx += 1
    _autosize(ws_data, [18] * len(union) + [24, 16, 10])

    # Sheet 2：檔案摘要（含表頭列判定結果）
    ws_meta = wb.create_sheet("檔案摘要")
    meta_headers = [
        "檔名", "分頁", "資料列數", "欄位數", "狀態", "錯誤訊息",
        "表頭列(0-based非空列)", "表頭列(Excel列號)", "表頭判定", "判定依據",
        "缺漏欄位", "獨有欄位", "警告", "排除的小計列",
    ]
    _style_header(ws_meta, meta_headers)
    row_idx = 2
    for result in results:
        if result.error:
            ws_meta.cell(row=row_idx, column=1, value=result.file_name)
            ws_meta.cell(row=row_idx, column=5, value="失敗")
            ws_meta.cell(row=row_idx, column=6, value=result.error)
            row_idx += 1
            continue
        for sheet in result.sheets:
            others: set[str] = set()
            for other in result.sheets:
                if other is not sheet:
                    others |= set(other.headers)
            for other_result in results:
                if other_result is result:
                    continue
                for other_sheet in other_result.sheets:
                    others |= set(other_sheet.headers)
            missing = [h for h in union if h not in sheet.headers]
            extra = [h for h in sheet.headers if h not in others]
            ws_meta.cell(row=row_idx, column=1, value=result.file_name)
            ws_meta.cell(row=row_idx, column=2, value=sheet.sheet_name)
            ws_meta.cell(row=row_idx, column=3, value=len(sheet.rows))
            ws_meta.cell(row=row_idx, column=4, value=len(sheet.headers))
            status = "失敗" if sheet.error else ("只有表頭" if not sheet.rows else "成功")
            ws_meta.cell(row=row_idx, column=5, value=status)
            ws_meta.cell(row=row_idx, column=6, value=sheet.error or "")
            if sheet.header.header_index is not None:
                ws_meta.cell(row=row_idx, column=7, value=sheet.header.header_index)
            if sheet.header.header_excel_row is not None:
                ws_meta.cell(row=row_idx, column=8, value=sheet.header.header_excel_row)
            ws_meta.cell(row=row_idx, column=9, value=sheet.header.method)
            ws_meta.cell(
                row=row_idx,
                column=10,
                value="；".join(sheet.header.evidence[:4]) if sheet.header.evidence else sheet.header.reason,
            )
            ws_meta.cell(row=row_idx, column=11, value="、".join(missing))
            ws_meta.cell(row=row_idx, column=12, value="、".join(extra))
            ws_meta.cell(row=row_idx, column=13, value="；".join(sheet.warnings))
            if sheet.subtotal_rows:
                ws_meta.cell(
                    row=row_idx,
                    column=14,
                    value="；".join(
                        f"第 {s['row']} 列（{s['label']}）：{s['reason']}"
                        for s in sheet.subtotal_rows
                    ),
                )
            row_idx += 1
    _autosize(ws_meta, [26, 18, 10, 10, 10, 50, 18, 16, 10, 50, 30, 30, 40, 46])

    # Sheet 3：數值合計（用正規化後的數值）
    # 率欄位（執行率、佔比…）不做合計 —— 比率加總沒有意義，改列平均與範圍。
    ws_sum = wb.create_sheet("數值合計")
    _style_header(ws_sum, ["來源檔", "分頁", "欄位", "合計/平均", "非空數值格數", "最小值", "最大值"])
    row_idx = 2
    for sheet in usable:
        for header, total in sheet.numeric_sums.items():
            values = sheet.rate_stats.get(header)
            if values:
                avg = sum(values) / len(values)
                ws_sum.cell(row=row_idx, column=1, value=sheet.file_name)
                ws_sum.cell(row=row_idx, column=2, value=sheet.sheet_name)
                ws_sum.cell(row=row_idx, column=3, value=f"{header}（平均，率欄位不做合計）")
                ws_sum.cell(row=row_idx, column=4, value=round(avg, 10))
                ws_sum.cell(row=row_idx, column=5, value=len(values))
                ws_sum.cell(row=row_idx, column=6, value=min(values))
                ws_sum.cell(row=row_idx, column=7, value=max(values))
            else:
                ws_sum.cell(row=row_idx, column=1, value=sheet.file_name)
                ws_sum.cell(row=row_idx, column=2, value=sheet.sheet_name)
                ws_sum.cell(row=row_idx, column=3, value=header)
                ws_sum.cell(row=row_idx, column=4, value=total)
                ws_sum.cell(row=row_idx, column=5, value=sheet.numeric_counts.get(header, 0))
            row_idx += 1
    _autosize(ws_sum, [26, 18, 30, 16, 14, 12, 12])

    # Sheet 4：型別轉換留痕
    ws_conv = wb.create_sheet("型別轉換")
    _style_header(ws_conv, ["來源檔", "分頁", "列號", "欄位", "原始值", "正規化值", "套用規則"], fill="E2EFDA")
    row_idx = 2
    conv_total = 0
    for h, items in (conversions or {}).items():
        for item in items:
            ws_conv.cell(row=row_idx, column=1, value=item["file"])
            ws_conv.cell(row=row_idx, column=2, value=item["sheet"])
            ws_conv.cell(row=row_idx, column=3, value=item["row"])
            ws_conv.cell(row=row_idx, column=4, value=item["col"])
            ws_conv.cell(row=row_idx, column=5, value=item["raw"])
            ws_conv.cell(row=row_idx, column=6, value=item["normalized"])
            ws_conv.cell(row=row_idx, column=7, value=item["rule"])
            row_idx += 1
            conv_total += 1
    if row_idx == 2:
        ws_conv.cell(row=2, column=1, value="（無型別轉換紀錄）")
    _autosize(ws_conv, [26, 18, 8, 22, 20, 18, 46])

    # Sheet 5：無法解析（獨立成表，不混在空值裡、不算 0）
    ws_unp = wb.create_sheet("無法解析")
    _style_header(ws_unp, ["來源檔", "分頁", "列號", "欄位", "原始值", "無法解析原因"], fill="FCE4D6")
    row_idx = 2
    unp_total = 0
    for h, items in (unparsed or {}).items():
        for item in items:
            ws_unp.cell(row=row_idx, column=1, value=item["file"])
            ws_unp.cell(row=row_idx, column=2, value=item["sheet"])
            ws_unp.cell(row=row_idx, column=3, value=item["row"])
            ws_unp.cell(row=row_idx, column=4, value=item["col"])
            ws_unp.cell(row=row_idx, column=5, value=item["raw"])
            ws_unp.cell(row=row_idx, column=6, value=item["reason"])
            row_idx += 1
            unp_total += 1
    if row_idx == 2:
        ws_unp.cell(row=2, column=1, value="（無無法解析的值）")
    _autosize(ws_unp, [26, 18, 8, 22, 24, 50])

    # Sheet 6：退款/負值警示
    ws_alert = wb.create_sheet("退款警示")
    _style_header(ws_alert, ["來源檔", "分頁", "列號", "欄位", "正規化值", "原始值", "原因"], fill="FCE4D6")
    row_idx = 2
    for sheet in usable:
        for alert in sheet.alerts:
            ws_alert.cell(row=row_idx, column=1, value=alert["file"])
            ws_alert.cell(row=row_idx, column=2, value=alert["sheet"])
            ws_alert.cell(row=row_idx, column=3, value=alert["row"])
            ws_alert.cell(row=row_idx, column=4, value=alert["header"])
            ws_alert.cell(row=row_idx, column=5, value=alert["value"])
            ws_alert.cell(row=row_idx, column=6, value=alert.get("raw", ""))
            ws_alert.cell(row=row_idx, column=7, value=alert["reason"])
            row_idx += 1
    if row_idx == 2:
        ws_alert.cell(row=2, column=1, value="（無退款/負值紀錄）")
    _autosize(ws_alert, [26, 18, 8, 22, 14, 16, 20])

    # Sheet 7：輸入集合（納入／排除決定 + 理由 + sha256）
    ws_in = wb.create_sheet("輸入集合")
    _style_header(ws_in, ["檔名", "決定", "理由", "sha256"], fill="FFF2CC")
    row_idx = 2
    for entry in manifest or []:
        ws_in.cell(row=row_idx, column=1, value=entry["name"])
        ws_in.cell(row=row_idx, column=2, value=entry["decision"])
        ws_in.cell(row=row_idx, column=3, value=entry["reason"])
        ws_in.cell(row=row_idx, column=4, value=entry["sha256"])
        row_idx += 1
    if row_idx == 2:
        ws_in.cell(row=2, column=1, value="（資料夾是空的）")
    _autosize(ws_in, [34, 10, 60, 68])

    # Sheet 8：本次執行
    ws_run = wb.create_sheet("本次執行")
    run_rows = [
        ("執行時間", datetime.now().isoformat(timespec="seconds")),
        ("執行平台", f"{platform_name()}（Python {sys.version.split()[0]}）"),
        ("目標環境", "Windows（使用者實機）"),
        ("輸入資料夾", str(input_folder)),
        ("輸出檔", str(output_path)),
        ("摘要 CSV", "、".join(str(p) for p in csv_paths) if csv_paths else "（未輸出）"),
        ("CSV 編碼", csv_encoding if csv_paths else "-"),
        ("解析檔數", len(results)),
        ("可用分頁數", len(usable)),
        ("合併後總列數", sum(len(s.rows) for s in usable)),
        ("聯集欄位數", len(union)),
        ("數值欄位數", len(numeric_columns or [])),
        ("率欄位（不做合計，改列平均）", "、".join(h for h in union if is_rate_header(h)) or "（無）"),
        ("型別轉換筆數", conv_total),
        ("無法解析筆數", unp_total),
        ("警示筆數", sum(len(s.alerts) for s in usable)),
        ("略過檔案數", len(skipped or [])),
        ("需人工指定表頭列", sum(1 for r in results if r.needs_manual_header)),
    ]
    for r_idx, (k, v) in enumerate(run_rows, start=1):
        ws_run.cell(row=r_idx, column=1, value=k).font = Font(bold=True)
        ws_run.cell(row=r_idx, column=2, value=v)
    _autosize(ws_run, [20, 70])

    # Sheet 9：略過的檔案
    ws_skip = wb.create_sheet("略過檔案")
    _style_header(ws_skip, ["檔名", "略過原因"], fill="FFF2CC")
    row_idx = 2
    for name, reason in (skipped or []):
        ws_skip.cell(row=row_idx, column=1, value=name)
        ws_skip.cell(row=row_idx, column=2, value=reason)
        row_idx += 1
    if row_idx == 2:
        ws_skip.cell(row=2, column=1, value="（無略過檔案）")
    _autosize(ws_skip, [30, 70])

    return wb


def platform_name() -> str:
    import platform

    return f"{platform.system()} {platform.release()} ({platform.machine()})"


def summary_rows(results: list[FileResult], usable: list[SheetData], union: list[str]) -> list[list]:
    """組出 CSV 摘要列（與工作表的「檔案摘要」一致 —— 欄位必須一一對應）。"""
    rows: list[list] = [[
        "檔名", "分頁", "資料列數", "欄位數", "狀態", "錯誤訊息",
        "表頭列(0-based非空列)", "表頭列(Excel列號)", "表頭判定", "判定依據",
        "缺漏欄位", "獨有欄位", "警告", "排除的小計列",
    ]]
    for result in results:
        if result.error:
            rows.append([result.file_name, "", "", "", "失敗", result.error,
                         "", "", "", "", "", "", "", ""])
            continue
        for sheet in result.sheets:
            others: set[str] = set()
            for other in result.sheets:
                if other is not sheet:
                    others |= set(other.headers)
            for other_result in results:
                if other_result is result:
                    continue
                for other_sheet in other_result.sheets:
                    others |= set(other_sheet.headers)
            missing = "、".join(h for h in union if h not in sheet.headers)
            extra = "、".join(h for h in sheet.headers if h not in others)
            status = "失敗" if sheet.error else ("只有表頭" if not sheet.rows else "成功")
            rows.append(
                [
                    result.file_name,
                    sheet.sheet_name,
                    len(sheet.rows),
                    len(sheet.headers),
                    status,
                    sheet.error or "",
                    sheet.header.header_index if sheet.header.header_index is not None else "",
                    sheet.header.header_excel_row if sheet.header.header_excel_row is not None else "",
                    sheet.header.method,
                    "；".join(sheet.header.evidence[:4]) if sheet.header.evidence else sheet.header.reason,
                    missing,
                    extra,
                    "；".join(sheet.warnings),
                    "；".join(
                        f"第 {s['row']} 列（{s['label']}）：{s['reason']}"
                        for s in sheet.subtotal_rows
                    ),
                ]
            )
    return rows


def issues_rows(
    conversions: dict[str, list[dict]], unparsed: dict[str, list[dict]]
) -> list[list]:
    """型別轉換 + 無法解析 的問題清單 CSV。"""
    rows: list[list] = [["類型", "來源檔", "分頁", "列號", "欄位", "原始值", "正規化值/原因", "套用規則"]]
    for h, items in conversions.items():
        for item in items:
            rows.append([
                "型別轉換", item["file"], item["sheet"], item["row"], item["col"],
                item["raw"], item["normalized"], item["rule"],
            ])
    for h, items in unparsed.items():
        for item in items:
            rows.append([
                "無法解析", item["file"], item["sheet"], item["row"], item["col"],
                item["raw"], item["reason"], "",
            ])
    return rows


def atomic_write_csv(target: Path, rows: list[list], encoding: str) -> None:
    """原子寫出 CSV（預設 utf-8-sig，Excel 開不亂碼）。"""
    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer)
    for row in rows:
        writer.writerow(row)
    payload = buffer.getvalue().encode(encoding, errors="replace")
    atomic_write_bytes(target, payload)


# ---------- CLI ----------
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="合併資料夾內多個 Excel 並產生摘要（v4：表頭列自動判定 + 型別正規化 + 輸入集合界定）",
    )
    parser.add_argument("input_folder", type=Path, help="要合併的資料夾")
    parser.add_argument(
        "-o", "--output", type=Path, default=Path("merged.xlsx"), help="輸出 Excel（預設 merged.xlsx）"
    )
    parser.add_argument("--summary-csv", type=Path, default=None, help="另存摘要 CSV 的路徑")
    parser.add_argument("--issues-csv", type=Path, default=None, help="另存型別轉換／無法解析問題清單 CSV")
    parser.add_argument(
        "--csv-encoding", choices=CSV_ENCODINGS, default="utf-8-sig",
        help="CSV 編碼（預設 utf-8-sig：Excel 直接開不亂碼；cp950 給舊系統）",
    )
    parser.add_argument(
        "--header-row", type=int, default=None,
        help=(
            "手動指定表頭列（0-based，索引『非空列』序列、空列不計入；0 = 第一個非空列）。"
            "指定後不做自動判定（套用到所有分頁）。"
        ),
    )
    parser.add_argument(
        "--header-row-for", action="append", default=[], metavar="FILE=N",
        help=(
            "只對特定檔案指定表頭列（可重複），例如 --header-row-for 'd_無法解析.xlsx=0'。"
            "多個分頁表頭列不同時用這個（比 --header-row 精確）。"
        ),
    )
    parser.add_argument(
        "--exclude-glob", action="append", default=[], metavar="PATTERN",
        help="額外排除的檔名樣式（可重複），例如 --exclude-glob '~$*' --exclude-glob '草稿*'",
    )
    parser.add_argument(
        "--apply", action="store_true",
        help="真的寫出檔案（預設 dry-run：只預覽不寫）",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if not args.input_folder.is_dir():
        sys.stderr.write(
            f"錯誤：{args.input_folder} 不是資料夾。請確認路徑是否存在，"
            "Windows 下可用引號包住含空格的路徑。\n"
        )
        return 2

    csv_paths = [p for p in (args.summary_csv, args.issues_csv) if p is not None]
    path_problems = validate_target_path(str(args.output))
    for p in csv_paths:
        path_problems += validate_target_path(str(p))
    if path_problems:
        sys.stderr.write("輸出路徑預檢失敗（先修正再執行，避免在 Windows 上產生無法開啟的檔名）：\n")
        for p in path_problems:
            sys.stderr.write(f"  - {p}\n")
        return 2

    user_rules = [
        ExclusionRule(f"使用者排除 {pat}", pat, "使用者以 --exclude-glob 指定排除", "glob")
        for pat in args.exclude_glob
    ]

    # 逐檔表頭列覆寫：--header-row-for '檔名=N'
    per_file_header: dict[str, int] = {}
    for spec in args.header_row_for:
        if "=" not in spec:
            sys.stderr.write(
                f"錯誤：--header-row-for 的格式是 '檔名=N'，收到「{spec}」。\n"
                "例如：--header-row-for '2026Q3.xlsx=2'\n"
            )
            return 2
        fname, _, num = spec.rpartition("=")
        try:
            per_file_header[fname.strip()] = int(num.strip())
        except ValueError:
            sys.stderr.write(
                f"錯誤：--header-row-for '{spec}' 的 N 不是整數（表頭列索引必須是整數）。\n"
            )
            return 2

    print(f"[merge_xlsx] 輸入資料夾：{args.input_folder}")
    print(f"[merge_xlsx] 輸出 Excel：{args.output}")
    if csv_paths:
        print(f"[merge_xlsx] 摘要 CSV：{'、'.join(str(p) for p in csv_paths)}（編碼 {args.csv_encoding}）")
    print(f"[merge_xlsx] 模式：{'APPLY（會寫檔）' if args.apply else 'dry-run（不寫檔）'}")
    print(f"[merge_xlsx] 執行平台：{platform_name()}")
    if args.header_row is not None:
        print(f"[merge_xlsx] 表頭列：手動指定第 {args.header_row} 列（0-based）")

    results, usable, errors, skipped, manifest = merge_all(
        args.input_folder, args.output, csv_paths, user_rules,
        header_override=args.header_row, per_file_header=per_file_header,
    )

    if not results:
        sys.stderr.write(
            f"錯誤：{args.input_folder} 內找不到 .xlsx 檔案。"
            "請確認資料夾正確、檔案副檔名是 .xlsx（.xls 舊格式請先在 Excel 另存為 .xlsx）。\n"
        )
        return 2
    if not usable:
        sys.stderr.write("錯誤：所有檔案都解析失敗，沒有可合併的資料。\n")
        for e in errors:
            sys.stderr.write(f"  - {e}\n")
        return 4

    union = union_headers(usable)
    conversions, unparsed, numeric_columns = normalize_values(usable, union)
    apply_normalized_values(usable, union, numeric_columns)

    print(f"  解析成功：{sum(1 for r in results if not r.error)} 個檔案 / {len(usable)} 個分頁")
    print(f"  聯集欄位（{len(union)}）：{'、'.join(union)}")
    print(f"  合併後總列數：{sum(len(s.rows) for s in usable)}")
    print(f"  型別轉換：{sum(len(v) for v in conversions.values())} 筆")
    unp_total = sum(len(v) for v in unparsed.values())
    print(f"  無法解析：{unp_total} 筆")
    for h, items in unparsed.items():
        if items:
            print(f"    - 欄位「{h}」：{len(items)} 個值無法解析（見「無法解析」分頁）")
    print(f"  退款/負值警示：{sum(len(s.alerts) for s in usable)} 筆")
    if skipped:
        print(f"  略過 {len(skipped)} 個檔案（原因見輸出檔的「略過檔案」分頁）：")
        for name, reason in skipped:
            print(f"    - {name}：{reason}")

    needs_manual = [r for r in results if r.needs_manual_header]
    if needs_manual:
        sys.stderr.write(
            f"\n注意：{len(needs_manual)} 個檔案需要人工指定表頭列（已合併其他檔案，這些檔案未被計入）：\n"
        )
        for r in needs_manual:
            for sheet in r.sheets:
                if sheet.error and "表頭列" in sheet.error:
                    sys.stderr.write(f"  - {sheet.error}\n")
        sys.stderr.write("  請用 --header-row N 重跑指定（會套用到所有分頁；分頁各自不同時請分批處理）。\n")

    if not args.apply:
        print("\n[dry-run] 沒有寫任何檔案。要真的輸出請加 --apply。")
        return 5 if needs_manual else 0

    wb = build_workbook(
        results, usable, union, args.input_folder, args.output, csv_paths,
        args.csv_encoding, skipped, manifest, conversions, unparsed, numeric_columns,
    )
    try:
        backup = atomic_save_workbook(wb, args.output, backup=True)
    except PermissionError:
        sys.stderr.write(
            f"錯誤：沒有權限寫入「{args.output}」。\n"
            "請改用有寫入權限的資料夾，或用 -o 指定其他輸出路徑。\n"
        )
        return 3
    except OSError as exc:
        sys.stderr.write(
            f"錯誤：寫出「{args.output}」失敗（{type(exc).__name__}: {exc}）。\n"
            "請確認磁碟空間、檔案是否被 Excel 開著鎖住、以及輸出資料夾是否存在。\n"
        )
        return 3
    print(f"  ✓ 寫出 {args.output}")
    if backup:
        print(f"  ↻ 舊檔已備份到 {backup}")

    if args.summary_csv:
        try:
            atomic_write_csv(args.summary_csv, summary_rows(results, usable, union), args.csv_encoding)
        except (PermissionError, OSError) as exc:
            sys.stderr.write(
                f"錯誤：寫出摘要 CSV「{args.summary_csv}」失敗（{type(exc).__name__}: {exc}）。\n"
                "Excel 已輸出完成，但 CSV 摘要未產生。\n"
            )
            return 3
        print(f"  ✓ 寫出 {args.summary_csv}（{args.csv_encoding}）")

    if args.issues_csv:
        try:
            atomic_write_csv(args.issues_csv, issues_rows(conversions, unparsed), args.csv_encoding)
        except (PermissionError, OSError) as exc:
            sys.stderr.write(
                f"錯誤：寫出問題清單 CSV「{args.issues_csv}」失敗（{type(exc).__name__}: {exc}）。\n"
                "Excel 已輸出完成，但問題清單 CSV 未產生。\n"
            )
            return 3
        print(f"  ✓ 寫出 {args.issues_csv}（{args.csv_encoding}）")

    return 5 if needs_manual else 0


if __name__ == "__main__":
    sys.exit(main())
