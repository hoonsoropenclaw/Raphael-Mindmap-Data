# audit_contract 契約檢查器規格（SPEC）

本規格是唯一的「真相來源」。檢查器必須**只依本規格實作**，不得針對特定頁面、id 或特定數字寫死比對。

## 1. 輸入

檔案：`deck_fixture.json`，UTF-8 JSON，結構如下：

```json
{
  "slides": [
    {
      "id": "s01",
      "title": "第 1 頁標題",
      "chart": {
        "type": "bar",
        "axis_label": "預算金額（元）",
        "ticks": ["0", "3 億", "6 億"],
        "value_labels": ["8.2 億"],
        "footer": "資料來源：教育部 114/04/21"
      },
      "notes": "講者備註純文字，開頭通常有時間配額，例如「90 秒」。",
      "footer": "資料來源：教育部 114/04/21",
      "fields": {"verified_total": "7.5 億", "disambiguation": "…"}
    }
  ]
}
```

- `chart` 可能為 `null`（無圖頁）。
- `fields` 為任意鍵值，可能沒有 `verified_total` / `verified_by` / `disambiguation`。

## 2. 必查的五類缺陷

每一類都必須有偵測邏輯，且必須能套用到**任意**頁面（不得引用 id）。

| category | 判定條件 |
|---|---|
| `unit_mismatch` | 同一張圖的 `axis_label` 括號內單位 與 `ticks`／`value_labels` 所使用的單位不一致（單位詞如 元/億/萬/千/件/%). |
| `duplicate_source` | 同一頁的 `chart.footer` 與 `slide.footer` 出現**同一個來源字串**（例如同一組「資料來源：…發布」文字），即同一來源被宣告兩次。 |
| `missing_time_budget` | `notes` 沒有任何時間配額樣式（正則需能抓到「90 秒」「2 分鐘」「1.5 分鐘」這類寫法，含中文數字或阿拉伯數字、小數）。 |
| `unverified_claim` | `notes`（或 `title`）出現「已驗算」「已核對」「已確認」這類宣稱，但該頁 `fields` 缺少 `verified_total` 或 `verified_by`。 |
| `terminology_drift` | 同一頁同時出現同一組同義詞的兩種說法，且該頁 `fields` 沒有 `disambiguation` 說明。已知同義詞組：校舍/校園、安東/Anton、資料/數據、公文/文書。 |

## 3. 輸出

- 結果寫成 JSON：`{"findings": [{"slide_id": "...", "category": "...", "evidence": "..."}]}`
- `slide_id` 必須是輸入中的 `id`；`category` 必須是上表五類之一（字串完全相同）。
- `evidence`：簡短的原始文字片段，要能讓人回頭在輸入檔找到該處。
- 同一頁同一類別若有多處，可合併成一筆，`evidence` 串接多個片段。
- stdout 印出同一份 JSON。

## 4. 結束碼

- `0`：沒有任何發現。
- `1`：有發現（至少一筆）。
- `2`：執行錯誤（輸入檔不存在、JSON 解析失敗、必要欄位缺型別錯誤等）。錯誤訊息要可行動（說明是哪個檔、哪個欄位）。

## 5. 限制

- 只准讀取傳入的輸入檔，只准用 Python 標準函式庫。
- 不得連外、不得讀環境變數、不得寫入輸入檔以外的任何路徑（輸出檔由呼叫端指定）。
- 必須可重跑：同樣輸入跑兩次，輸出逐位元相同。
- 不得把乾淨頁報成有問題（誤報）；也不得漏掉乾淨頁（漏報）。
