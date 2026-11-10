"""宣告 ↔ 後果對帳的**宣告側**資料（code SOP §25-6）。

為什麼這份資料要存在
--------------------
§25 的病根是：「檢查器宣稱自己做了什麼，這個宣稱本身就是證據」——
但 11-06 的實測顯示這個前提在多個獨立作品上不成立：
宣告寫在 docstring 裡，卻沒有任何一處綁定「什麼條件下這件事會讓 exit≠0」。
於是「宣告」變成免費的：宣告得越詳細，綠燈越沒有被約束。

§25-6 要求產出一支「宣告 ↔ 後果對帳」檢查器，輸出三個數字：

    N = 宣告條數
    M = 有可執行後果的條數
    K = 宣告了但無後果的條數（K > 0 即 exit≠0）

本模組只放**宣告側**（規則、母體、不看的維度、後果綁定、探針名）；
探針的實作放在 `checks/check_population_boundary.py`（放這裡是因為
探針需要執行交付集合裡的其他檢查器，會造成 import 循環）。

**為什麼宣告要分三層寫**（每一層都可被推翻）：
    rule          這條規則宣稱管什麼
    population    它實際看的母體（機械可核：探針必須真的讓它變紅）
    not_covered   它明確不看的維度（誠實揭露，不得用沉默代替）
    consequence   哪支檢查器、在什麼條件下 exit≠0（可 grep）
    probe         對抗性探針名（探針找不到 → 這條計入 K）

`not_covered` 是**必填**而非選填：
一個只寫「我管 X」卻不寫「我不管 Y」的宣告，使用者無從判斷
那個綠燈的適用範圍——這正是 11-08 的失效形狀
（檢查器只宣告頁面層，缺陷卻落在圖內層，檢查器不會紅，
但它給的是一個讓人以為已蓋住整個維度的綠燈）。
"""
from __future__ import annotations

from dataclasses import dataclass

__all__ = ["Declaration", "DECLARATIONS",
           "EXCLUDED_RATIO_LIMIT", "EXCLUDED_RATIO_MIN_ROWS"]

#: 被排除列的**比例上限**（宣告側提供，engine 只讀不訂）。
#:
#: 為什麼需要這個常數（11-11 的實測結論）：
#: 「等式成立」與「等式有意義」是兩個不同的命題。
#: 原本的實作只驗了前者：把無法解析／空值／百分比／小計列排除在加總母體之外並留痕，
#: 是對的做法；但**沒有任何規則檢查「排除得太多」**——
#: 如果 90% 的列被排除，等式依然成立、依然綠燈，因為它在一個幾乎空的母體上成立。
#:
#: 門檻值取 0.30 的理由（實測基礎，11-11）：
#: 乾淨測資的**整體**排除比例 = 3/28 = 0.107；各檔最高是 h2_異常.xlsx 的 3/7 = 0.4286
#: （那一檔本來就是「金額異常」對抗性 fixture，是刻意做出來要抓異常的）。
#: → 0.30 對整體母體不會誤報，且能抓到「大多數列無法解析」的真缺陷。
#:
#: 門檻寫在**宣告側**（這裡）而不是檢查器裡：
#: 門檻若由檢查器自己自訂，等同沒有門檻（11-03 已實證）。
EXCLUDED_RATIO_LIMIT = 0.30

#: 比例判準的**最小分母**：某一檔的明細列少於這個數時，比例不具資訊量，不判。
#:
#: 為什麼需要：乾淨測資的 h2_異常.xlsx 只有 7 列、其中 3 列刻意是異常值，
#: 比例 0.4286 > 0.30。但那一檔**本來就是**要展示「金額異常被排除並留痕」的 fixture
#: ——它是對抗性樣本，不是「資料品質壞掉的來源檔」。
#: 沒有分母下限，門檻就會對刻意設計的 fixture 誤報，而誤報會讓門檻被無視。
#: 8 列是實測選定的值：乾淨測資所有檔案的明細列數都 <= 7（h2_異常 = 7 最多），
#: 而「大多數列無法解析」的真缺陷 fixture 會有 10 列以上 → 分母下限擋得住前者、擋不住後者。
EXCLUDED_RATIO_MIN_ROWS = 8


@dataclass(frozen=True)
class Declaration:
    """一條被宣告的規則。欄位全部必填——空值視為宣告不完整。"""

    id: str
    rule: str
    population: str
    not_covered: str
    consequence: str
    probe: str

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "rule": self.rule,
            "population": self.population,
            "not_covered": self.not_covered,
            "consequence": self.consequence,
            "probe": self.probe,
        }


#: 本交付集合宣告的全部規則。
#:
#: 編號刻意跟 code SOP 條款對齊，方便 grep：
#: D-11→§11（加總等式與母體）、D-23→§23（交付集合清潔度）、
#: D-24→§24（敘述層回算）、D-25→§25（宣告↔後果）、D-28→§28（自足性）。
DECLARATIONS: tuple[Declaration, ...] = (
    Declaration(
        id="D-11",
        rule="每個被偵測為小計的列，其宣稱金額必須等於它所涵蓋區段的明細和",
        population="來源檔中所有被偵測為小計的列（標籤層 + 結構層）",
        not_covered="不驗證來源檔的小計數字本身是否忠實反映原始業務資料",
        consequence=(
            "xlsx_recon/engine.py:reconcile() → equations['declared_subtotal == "
            "running_segment_sum'] 為 false → xlsx_recon/cli.py:main() 回傳 exit≠0"
        ),
        probe="probe_tampered_subtotal",
    ),
    Declaration(
        id="D-11b",
        rule="金額無法解析或為空的列必須被排除在加總母體之外，且必須留下原因",
        population="所有來源檔中金額欄非數值的明細列",
        not_covered="不判斷「無法解析」是否為資料品質問題（只排除並留痕，不回頭要求人修資料）",
        consequence=(
            "xlsx_recon/engine.py:reconcile() → excluded_rows_detail 每筆帶 reason"
            "（unparseable / empty / percent）且金額不進 sum_of_details"
        ),
        probe="probe_unparseable_excluded",
    ),
    Declaration(
        id="D-11c",
        rule="來源檔缺必要欄位必須報錯，但不得拖垮同一批次的其他檔案",
        population="輸入資料夾內所有 .xlsx / .xlsm 的所有工作表",
        not_covered="不驗證欄位的**語意**正確（欄名對上就當對，不判斷「類別」欄裝的內容合不合理）",
        consequence=(
            "xlsx_recon/engine.py:merge_directory() → issues 產生 sheet_failed → "
            "cli.main() 有 issues 時回傳 exit≠0"
        ),
        probe="probe_missing_required_column",
    ),
    Declaration(
        id="D-11d",
        rule=(
            "母體必須自證未被掏空：每個來源檔的被排除列比例不得超過宣告上限，"
            "否則等式雖然成立，但它在一個幾乎空的母體上平凡成立"
        ),
        population=(
            "每個來源檔的明細列（已扣除小計列），按檔分組計算排除比例，"
            "分母低於宣告側下限者不判"
        ),
        not_covered=(
            "不驗證被排除列的**理由**是否正確（每筆仍需有 reason 留痕，那是 D-11b 的責任）；"
            "不驗證『被排除』這個判斷本身對不對（只驗比例，不回頭要求人重做資料）"
        ),
        consequence=(
            "xlsx_recon/engine.py:reconcile() → population_not_hollowed=false → "
            "xlsx_recon/cli.py:main() 回傳 exit≠0"
        ),
        probe="probe_hollow_population",
    ),
    Declaration(
        id="D-25",
        rule="宣告 ↔ 後果對帳：每一條宣告都必須綁定一個可執行後果，K>0 即失敗",
        population="xlsx_recon/declarations.py:DECLARATIONS 的每一條",
        not_covered="不驗證探針是否覆蓋了宣告語意的**所有**可能反例（探針是代表性反例，不是窮舉）",
        consequence=(
            "checks/check_population_boundary.py:main() → K>0 即回傳 exit≠0，"
            "並在 verification_summary.json 的 declaration_reconciliation 記錄 N / M / K"
        ),
        probe="probe_k_gt_zero",
    ),
    Declaration(
        id="D-24",
        rule="敘述層的金額型數字與缺陷描述必須能在產物中找到對應（逐句回算）",
        population="交付集合內的敘述檔（RUNLOG / README）與結構化 claims 檔",
        not_covered=(
            "不驗證敘述的**語意**是否成立（只驗證宣稱存在的東西真的存在，"
            "不判斷那段話寫得好不好、推論對不對）"
        ),
        consequence=(
            "checks/check_selfeval_claims.py:main() → 找不到對應即回傳 exit≠0，"
            "並印出「宣稱存在但產物中不存在」的句子"
        ),
        probe="probe_fake_claim",
    ),
    Declaration(
        id="D-28",
        rule="交付集合必須自足：入口腳本在只含交付集合的空目錄中必須 EXIT=0",
        population="交付集合的全部檔案（逐檔 sha256 記錄於 delivery_manifest.json）",
        not_covered=(
            "不驗證**目標使用環境**的相容性（Windows + Excel 實機行為未驗收，"
            "見 RUNLOG 第 7 節第 1 列）"
        ),
        consequence=(
            "checks/check_delivery.py:check_self_contained() → 複製到空目錄跑入口，"
            "結束碼非 0 即回傳 exit≠0"
        ),
        probe="probe_self_contained_fails",
    ),
    Declaration(
        id="D-28b",
        rule="入口腳本引用的每一支相依檔都必須存在於交付集合內",
        population="交付集合內所有 .py 的 import 關係（含 subprocess 字串呼叫）",
        not_covered="不驗證**第三方相依**（openpyxl）有沒有安裝在目標環境（那是 §19 前提檢查的責任）",
        consequence=(
            "checks/check_delivery.py:check_dependencies() → 缺漏任一項即回傳 exit≠0，"
            "並印出「哪一支引用了不存在的相依」"
        ),
        probe="probe_missing_dependency",
    ),
    Declaration(
        id="D-23",
        rule="交付集合不得含執行期產物（__pycache__ / .pyc / .pytest_cache）",
        population="交付集合內的**所有**檔案（偵測母體不套用收錄清單的排除規則）",
        not_covered="不驗證非 Python 的暫存物（.tmp / .bak 等本工具不產生、也不宣稱涵蓋）",
        consequence=(
            "checks/check_delivery.py:check_cleanliness() → 發現暫存物即回傳 exit≠0"
        ),
        probe="probe_transient_pollution",
    ),
    Declaration(
        id="D-25b",
        rule="每支檢查器都必須揭露它的母體（population）與未涵蓋維度（not_covered）",
        population="交付集合內 checks/ 下的每一支檢查器",
        not_covered="不驗證 not_covered 的**完整性**（聲明自己不看某維度不等於那維度真的沒被檢查）",
        consequence=(
            "checks/check_population_boundary.py:check_checkers_declare_boundary() → "
            "任一檢查器缺欄即回傳 exit≠0"
        ),
        probe="probe_missing_not_covered",
    ),
)
