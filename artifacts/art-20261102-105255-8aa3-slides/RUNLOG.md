# RUNLOG — 20261102-教職員工時數與進用結構

> 依 slides SOP v1.6.0 §4（自我視覺檢查）與 §1.8（交付紀錄的數字不得手抄）：
> 本檔所有計數均由 `build_verification_summary.py` 實跑產生並寫入
> `verification_summary.json`，此處只引用該檔欄位，**無任何手抄數字**。
> 工作目錄：`workspace/practice-20261102-hr-hours/`
>
> ⚠️ **素材性質揭露**：本簡報的月報資料為本次練習**自擬之示範素材**，
> 不是任何機關的實際資料，數字為虛構，不可對外引用。

## 1. 產出物

| 檔案 | 說明 | 大小（bytes） |
|---|---|---:|
| `20261102-教職員工時數與進用結構.pptx` | 本簡報（6 頁，含講者備註） | 857306 |
| `20261102-教職員工時數與進用結構.pdf` | PDF 版本 | 613683 |
| `人事時數與進用結構自檢表.docx` | A4 可列印、3 欄之人事時數與進用結構自檢表 | 39044 |
| `人事時數與進用結構自檢表.pdf` | A4 可列印、3 欄之人事時數與進用結構自檢表（PDF 版） | 154076 |
| `manifest.json` | 交付清單與檔案雜湊值 | — |
| `RUNLOG.md` | 驗證紀錄（每支檢查器的 exit code 與修法） | — |
| `build.sh` | 一鍵重現全部流程（fail fast） | 5960 |
| `verification_summary.json` | 機器可讀驗證摘要（每支檢查器的 exit code 與計數，禁止手抄） | 10119 |
| `audit_aggregate_claims.py` | 機械檢查器（隨產出物交付，使用者可重跑） | — |
| `audit_baseline_roles.py` | 機械檢查器（隨產出物交付，使用者可重跑） | — |
| `audit_caliber_pledge.py` | 機械檢查器（隨產出物交付，使用者可重跑） | — |
| `audit_chart_encoding.py` | 機械檢查器（隨產出物交付，使用者可重跑） | — |
| `audit_decision_pages.py` | 機械檢查器（隨產出物交付，使用者可重跑） | — |
| `audit_delivery_manifest.py` | 機械檢查器（隨產出物交付，使用者可重跑） | — |
| `audit_fact_layers.py` | 機械檢查器（隨產出物交付，使用者可重跑） | — |
| `audit_notes_claims.py` | 機械檢查器（隨產出物交付，使用者可重跑） | — |
| `audit_number_style.py` | 機械檢查器（隨產出物交付，使用者可重跑） | — |
| `audit_numbers.py` | 機械檢查器（隨產出物交付，使用者可重跑） | — |
| `audit_page_order.py` | 機械檢查器（隨產出物交付，使用者可重跑） | — |
| `audit_page_refs.py` | 機械檢查器（隨產出物交付，使用者可重跑） | — |
| `audit_text_fit.py` | 機械檢查器（隨產出物交付，使用者可重跑） | — |
| `audit_visual_semantics.py` | 機械檢查器（隨產出物交付，使用者可重跑） | — |
| `source_hr_report.txt` | 原始月報（本次練習的唯一事實來源） | 3870 |
| `deck_data.py` | 單一真實來源（所有對外數字的回算與事實分層登記） | 25784 |
| `page-1.png` … `page-6.png` | 逐頁渲染預覽（70 dpi） | — |

簡報頁數：**6** 頁（每頁皆有講者備註：6 頁）。
附件本體自證：**3 欄**、**21.0×29.7 cm**、表格 **18 列**（含表頭），且已驗證內含宣稱中的數字：1,260,000、15,308、13,868、630,000、97。

## 2. 機械檢查結果

共 **14** 支檢查器，**14** 支 EXIT=0，**0** 支不通過。

> **綠燈的命題形式**：EXIT=0 只能讀成「在我宣告的範圍內、這一輪的輸入、這個集合裡，沒有發現問題」；不代表涵蓋全部可能缺陷。

| # | 檢查器 | 對應條款 | EXIT | 結果 |
|---|---|---|---:|---|
| 1 | `audit_numbers.py` | rubric accuracy 硬性失敗「捏造數據」 | 0 | ✅ 數字可追溯到原稿或回算式 |
| 2 | `audit_page_refs.py` | SOP §1.5-1 | 0 | ✅ 備註／內文禁用頁碼引用 |
| 3 | `audit_text_fit.py` | SOP §4-2 | 0 | ✅ 文字溢出／頁尾碰撞／疊字 |
| 4 | `audit_notes_claims.py` | SOP §1.6、§4-6 | 0 | ✅ 備註↔正文說法一致、決策後果條件式 |
| 5 | `audit_fact_layers.py` | 2026-10-26 卡片 | 0 | ✅ 事實分層四層 |
| 6 | `audit_number_style.py` | 2026-10-26 卡片 | 0 | ✅ 繁中數字寫法 |
| 7 | `audit_visual_semantics.py` | SOP §1.7、2026-10-26 卡片 | 0 | ✅ 上下文綁定：敘述數值 ≡ 計算值、口徑未混用 |
| 8 | `audit_baseline_roles.py` | 2026-10-28 卡片 Q1 | 0 | ✅ 基準角色分層（建議值／門檻／上限）、編制與現職分別標示 |
| 9 | `audit_aggregate_claims.py` | 2026-10-28 卡片 Q3 | 0 | ✅ 聚合指標不外推子項 |
| 10 | `audit_caliber_pledge.py` | 2026-11-02 卡片 Q1 | 0 | ✅ 並列宣告的兌現義務：每一處使用位置皆帶口徑標註 |
| 11 | `audit_chart_encoding.py` | 2026-11-02 卡片 Q2 | 0 | ✅ 通道↔量綱一致、0 值不畫底、待核定不借用實數通道 |
| 12 | `audit_page_order.py` | 2026-11-02 卡片 Q3 | 0 | ✅ 主線頁序失效判定：封面層級配比、自我否定頁、決策頁位置 |
| 13 | `audit_decision_pages.py` | SOP §1.11 | 0 | ✅ 決策頁四要素、後果條件式、密度合規、圖表頁標出重點 |
| 14 | `verify_fonts.py` | rubric deliverability | 0 | ✅ 字型嵌入與字元覆蓋驗證 |

`build.sh` 整條流程 EXIT=0（fail fast，任一步失敗即停）。

### 2b. 交付閘門（交付宣稱 ↔ 交付實體）

（交付閘門尚未執行；build.sh 最後一步會產生 `delivery_gate.json`）

各檢查器的關鍵計數（機器可讀原始值見 `verification_summary.json`）：

- `audit_notes_claims.py`：投影片頁數 6
- `audit_fact_layers.py`：投影片頁數 6、受檢層數 12
- `audit_visual_semantics.py`：投影片頁數 6、受檢層數 12
- `audit_baseline_roles.py`：投影片頁數 6、受檢層數 12
- `audit_aggregate_claims.py`：投影片頁數 6、受檢層數 12
- `audit_caliber_pledge.py`：投影片頁數 6、受檢層數 12、受檢的使用位置數 6
- `audit_page_order.py`：投影片頁數 6、受檢層數 12
- `audit_decision_pages.py`：投影片頁數 6
- `verify_fonts.py`：字元覆蓋數 449

## 3. 視覺驗證（逐頁看渲染圖，非看程式碼）

（尚未進行視覺驗證）

## 4. 新檢查器的雙向驗證

依 2026-10-25／10-26 教訓：只寫「已驗證」卻交不出驗證用的檔案 = 宣稱沒有證據。
每一支新檢查器都必須有**缺陷版**（EXIT≠0）與**修好版**（EXIT=0）兩組可重跑的檔案，
缺陷版與修好版都隨產出物交付。

缺陷版是「把缺陷注入回產出物」的合法複本，置於 `defect_fixtures/` 子目錄，
不含正式交付物，僅作為驗證證據。


## 5. 素材性質揭露（三處一致）

| 位置 | 揭露句 |
|---|---|
| `artifact add --notes` | 本簡報為自主學習練習自擬之示範素材，非任何機關之實際資料。 |
| 本 RUNLOG | 同上（見檔頭警示） |
| 簡報附錄頁（資料來源說明列） | 「本簡報為示範素材，數字均為虛構，不可對外引用。」 |

刻意不寫在封面（會毀掉「拿到即用」的觀感），但不可省略。

## 6. 交付清單雜湊

完整清單（含每個檔案的 sha256）見 `manifest.json`。
`manifest.json` 自身無法包含自己的 sha256（自含悖論），
其一致性由 `audit_delivery_manifest.py` 規則 D 以「manifest 記載的檔案集合 == 磁碟檔案集合」驗證。

檔案數請直接查 `manifest.json`（本檔刻意不抄這個數字：
manifest 在本檔之後才定稿，抄進來會是過時值）。
