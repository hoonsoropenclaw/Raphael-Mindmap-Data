# RUNLOG — 20261103-午餐費調整請示

產生時間：2026-11-03T03:54:09.287388

> 本檔的每一個計數都引用 `verification_summary.json` 與 `manifest.json` 的欄位，
> 沒有手抄任何數字（SOP §1.8）。

## 1. 交付集合

- 主簡報：`20261103-午餐費調整請示.pptx`
- 交付集合檔案數：**41**（含 6 張逐頁 PNG）
- manifest 自我指涉欄位：`manifest_sha256` = `None`、`manifest_size_bytes` = `None`
  （自指必然遞迴 → 值必然是上一輪快照 → 必須留白。11-28 的缺陷之一。）

## 2. 內容檢查器

口徑：**內容檢查器**共 **9 支**
（與交付鏈檢查器分開計數；「共 N 支」必須指明是哪一個口徑，見 SOP §1.10-4。）

| 結果 | 檢查器 | EXIT | 檢查內容 |
|---|---|---|---|
| ✓ | `audit_numbers.py` | 0 | 數字可追溯到 deck_data 回算值（accuracy 硬性失敗防線） |
| ✓ | `audit_page_refs.py` | 0 | 備註／內文禁用頁碼引用（SOP §1.5-1） |
| ✓ | `audit_text_fit.py` | 0 | 文字溢出／頁尾碰撞／疊字（SOP §4-2 的機械化） |
| ✓ | `audit_notes_claims.py` | 0 | 備註↔正文說法一致、決策後果條件式（SOP §1.6） |
| ✓ | `audit_decision_pages.py` | 0 | 決策頁四要素、後果條件式（SOP §1.11） |
| ✓ | `audit_block_density.py` | 0 | 語意區塊數 ≤ 預算（2026-11-03 卡片 Q2） |
| ✓ | `audit_visual_terms.py` | 0 | 視覺元素指稱一致性（2026-11-03 卡片 Q3） |
| ✓ | `audit_visual_overlap.py` | 0 | 圖片版面：圖↔圖／圖↔色塊重疊、圖上字級下限 |
| ✓ | `verify_fonts.py` | 0 | 字型嵌入驗證（deliverability） |

集合完整性：`checker_set_closure_ok` = **True**
（預期清單 `9` 支 vs 實際執行 `9` 支；缺一支即 EXIT≠0——這是 11-02 high 缺陷「檢查器集合完整性未封閉」的直接修法。）

## 3. 交付鏈檢查器

口徑：**交付鏈檢查器**共 **0 支**
（時序／集合／閘門類，不進 verification_summary.json 的內容檢查器計數。）

| 結果 | 檢查器 | EXIT | 檢查內容 |
|---|---|---|---|
| ✓ | `audit_delivery_fingerprint.py` | 0 | 被評審物件↔交付集合的指紋綁定（2026-11-03 卡片 Q4）|
| ✓ | `run_delivery_gate.py` | 0 | 交付閘門：交付宣稱 ↔ 交付實體|

> 這兩支必須在 manifest 定稿後才執行（它們要比對 manifest 裡的指紋）；它們的結果寫進自己的機器可讀檔，RUNLOG 只引用，不手抄。

## 4. 數字可追溯性

- 受檢數字 token 數：**163**
- 白名單來源：`deck_data.ALLOWED_NUMBERS`（由 deck_data 自行回算，非手抄）

## 5. 今日三張新卡的落點

| 卡片 | 落點 |
|---|---|
| Q2 語意區塊 | `audit_block_density.py`：以容器／圖表／對齊基線群為單位計區塊，預算在 `deck_data.BLOCK_BUDGET`；字調小不會讓密度通過 |
| Q3 視覺元素指稱一致性 | `audit_visual_terms.py`：屬性詞典挑候選指稱，擋平行的不相容描述；圖例標籤在 `deck_data.LEGEND_LABELS` 單一宣告 |
| Q4 被評審物件的指紋綁定 | `audit_delivery_fingerprint.py` + `run_delivery_gate.py` 規則 D：被評審物件的 sha256 必須 == manifest 的 sha256 |

## 6. 本輪（2026-11-03 第二次嘗試）親眼看渲染圖才發現的三個缺陷

上一次的 `visual_review.md` 是**腳本寫死結論**（每頁都寫「通過」），不是真的看圖 → 這正是 SOP §1.10-2 要防的假綠燈。這一輪逐頁把渲染圖載入看過，才抓到下列真實缺陷：

1. 第 4 頁：c3 圖底 4.48in 與 c4 圖頂 4.36in 重疊 0.12in → c3 的資料來源第二行被切掉。
2. 第 6 頁：c5 圖底 4.63in 被回算等式卡（頂 4.52in）蓋住 0.11in → c5 資料來源第二行被切掉。
3. 第 6 頁：c5 原生 5.70in 卻只放 5.20in → scale 0.912 → 圖內 11pt 標示實際只有 10.04pt。

三個缺陷都**不是**既有 8 支檢查器能抓的：它們只比對文字↔文字／文字↔圖片／文字↔色塊，從未比對圖片↔圖片、圖片↔色塊，也沒有量圖內字級。→ 新增 `audit_visual_overlap.py` 補上這三個命題，並用 `defect_fixtures/20261103-pre-fix-image-overlap.pptx`（修正前的負樣本）實測它**會亮紅**——證明這支檢查器有鑑別力，不是裝飾。

## 7. 視覺檢查

`visual_review.md` 為最終 rebuild 之後的最後一步產出，並在檔頭寫出被檢 pptx 的 sha256（SOP §1.10-1）。


