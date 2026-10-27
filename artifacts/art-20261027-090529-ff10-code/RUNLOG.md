# scout A/B 執行紀錄 — nolze/msoffcrypto-tool（2026-10-27）

> 這份 RUNLOG 回應跨模型評審（minimax-m3-ab）對前一版交付的每一條缺失：
> 程式碼不可審、執行紀錄不可稽核、測試覆蓋數字說不準、負向路徑沒證據。
> 每一條判斷都可以在這個資料夾裡重跑驗證。

## 1. 這個 A/B 在比什麼

| 項目 | 內容 |
|---|---|
| 唯一變因 | 「密碼保護的活頁簿能不能被讀進來」 |
| 基準 | 現行 SOP 的 `merge_xlsx.py`（無解密能力） |
| 候選 | 同一支 `merge_xlsx.py` + 解密流程（`nolze/msoffcrypto-tool`, MIT） |
| 工具版本 | commit SHA `1f7925e388ac5a661b553adc97541a0972a8a80e`（vet 記錄於 `state/tools/registry.json`） |
| 執行環境 | harness Docker 沙盒（`raphael-sandbox:1`）——容器內無主機金鑰、執行階段斷網、`--cap-drop ALL`、獨立 venv |
| 套件版本 | openpyxl 3.1.5、msoffcrypto-tool 6.0.0、Python 3.12.15 |

**程式碼差異**：`evidence/shared/variant_diff.patch`（共 91 行 diff）——只有 1 個 hunk、
新增 3 個函式（`is_protected_office_file` / `decrypt_to_temp` / `_read_raw_file_plain`）、
其餘程式碼逐行相同。

- 基準版：`evidence/baseline/merge_xlsx.py`
- 候選版：`evidence/candidate/merge_xlsx.py`

## 2. 測試資料（fixture）— 修正上一版的數字錯誤

**這裡要更正一個錯誤**：前一版交付把測試集說成「10 個 Excel 檔」，實際是
**9 個不重複的來源檔案**。摘要之所以有 10 筆資料列，是因為 `h_多分頁.xlsx`
含兩個分頁（第一季、第二季），各佔一列。

實際組成（9 個來源檔 / 10 個分頁）：

| 檔案 | 測的情境 | 基準 | 候選 |
|---|---|---|---|
| `a_正常.xlsx` | 正常經費表 | 成功 | 成功 |
| `b_有說明列.xlsx` | 標題列下方有說明列 → 表頭在第 1 列 | 成功 | 成功 |
| `c_文字型數字.xlsx` | 文字型數字需轉型 | 成功 | 成功 |
| `d_無法解析.xlsx` | 表頭列模稜兩可 → 需人工指定 | **失敗**（要求 `--header-row N`） | **失敗**（同基準，行為一致） |
| `e_合併儲存格.xlsx` | 合併儲存格造成欄名借名 | 成功 | 成功 |
| `f_百分比語意.xlsx` | 百分比語意 | 成功 | 成功 |
| `g_只有表頭.xlsx` | 只有表頭無資料列 | 成功 | 成功 |
| `h_多分頁.xlsx` | 兩個分頁（第一季、第二季） | 成功 | 成功 |
| `j_密碼保護.xlsx` | **ECMA-376 加密活頁簿** | **失敗（跳過）** | **成功（解密後讀入）** |

fixture 的 SHA256 全部列在 `evidence/shared/fixture_sha256.txt`。
`~$j_鎖檔.xlsx`（Excel 鎖檔）兩邊都跳過，是預期行為。

### 加密 fixture 本身的有效性驗證

不是「做出來就算數」——`ab_result.json` 的 `fixture` 段記錄了實測：

```
openpyxl_can_open: false          ← openpyxl 確實開不起
openpyxl_error: "BadZipFile"
msoffcrypto_test_encrypted_exit: 0 ← msoffcrypto 確認它被加密
msoffcrypto_test_plain_exit: 1     ← 對照組：明文檔回 1
fixture_valid: true
```

⚠️ 該專案 README 第 54 行寫「returns 1 if the file is encrypted, 0 if not」，
**與實作相反**。以程式碼（`msoffcrypto/__main__.py`）與自家 `tests/test_cli.sh` 為準：
**已加密 = exit 0、未加密 = exit 1**。這是採用時必須記下來給使用者的坑。

## 3. 實測結果

| 指標 | 基準 | 候選 | 差 |
|---|---|---|---|
| 解析成功檔案／分頁 | 8 / 8 | 9 / 9 | +1 |
| 合併資料列數 | 15 | 18 | +3 |
| 加密檔的資料列 | 0 | 3 | +3 |
| 金額總和（非彙總列） | 1,953,968.5 | 2,653,968.5 | +700,000 |
| exit code | 5 | 5 | 相同 |

exit code 兩邊都是 5，原因是 `d_無法解析.xlsx` 需要人工指定表頭列 ——
這與解密無關，兩邊行為一致。

## 4. 對帳守門：證明「+3 列」不是重複計算

這是本次 A/B 最關鍵的一段。第一版跑完時 **delta 看起來是 +3，但那是假的**：
明文原檔 `j_密碼保護_原始.xlsx` 還留在輸入資料夾裡，候選把它「解密後再合併一次」
→ 同一筆金額被算兩次。

修正做法：明文原檔移到輸入資料夾**外面**（`ab/fixture_plain/`），
並加一道對帳守門 `check_no_double_count()`，三個判準全部要過才放行：

1. **同來源列數不得比基準多** → 沒有任何一個來源被合併兩次
2. **對帳等式**：`候選金額總和 − 基準金額總和 == 新來源非彙總列金額加總`
   → 實測 `2653968.5 − 1953968.5 = 700000.0 == 700000.0` ✅
3. **同一份資料不得出現兩次**（把來源檔名去掉「_原始」這類加密前後綴後比對）
   → 偵測「明文原檔 + 解密後明文同時存在」這個 double count 根因

### 反向對照（negative control）：證明守門不是橡皮章

`neg_control.py` 故意把明文原檔放回輸入資料夾、重現 double count 缺陷，
再餵給同一個守門。實測結果（`evidence/shared/neg_control_result.json`）：

```
caught: true
guard ok: false
twin_sources_same_data: {"j_密碼保護.xlsx": ["j_密碼保護.xlsx", "j_密碼保護_原始.xlsx"]}
```

**守門抓到了。** 這很重要：只做正向測試的守門可能只是「怎麼都回 True」。
（第一次寫的守門只做「相對」比較——基準與候選都用壞 fixture 時兩邊一起漲，
差額仍然對得上、等式會通過——反向對照把這個漏洞抓出來了，
所以最後補上第 3 條「絕對」判準。）

## 5. 負向路徑：解密失敗會怎樣

評審指出前一版「未見密碼缺失、密碼錯誤的案例」。實測（`ab_result.json` 的
`failure_modes` 段）：

| 情境 | exit | 錯誤訊息 | 加密檔資料是否混進輸出 | 密碼是否外洩到 stdout | 密碼是否外洩到輸出檔 |
|---|---|---|---|---|---|
| 密碼錯誤 | 5 | `解密 j_密碼保護.xlsx 失敗：InvalidKeyError: The file could not be decrypted with this password。請確認密碼正確，且該檔是 Excel 的「開啟密碼」（不是「修改權限」或「數位簽章」——那兩種不需要密碼就能讀）。` | 否（0 列） | 否 | 否 |
| 沒給密碼 | 5 | `j_密碼保護.xlsx 是密碼保護的活頁簿，但沒有提供密碼。請設定環境變數 OFFICE_FILE_PASSWORD 後重跑（密碼只從環境變數讀，不會寫進輸出檔或日誌）。` | 否（0 列） | 否 | 否 |

判準是**相對**的，不是絕對的：基準版遇到加密檔也是「略過該檔、其餘照常合併、
仍寫出輸出檔、exit=5」。所以「有寫出檔」本身不是缺陷；真正的判準是
**有明確可行動的錯誤訊息、退出碼非 0、沒有假裝讀到、密碼不外洩**。

密碼在測試中用 `chr()` 組出來，不以明文出現在任何 shell 變數或輸出中。

## 6. 尚未驗證的部分（誠實揭露）

評審指出的以下幾點，**這一輪沒有做到**，採用前要補：

- **Windows 實機未驗**：使用者是 Windows 環境，這裡全程在 Linux 沙盒跑。
  特別是「解密到暫存檔 → 讀完刪除」在 Windows 上遇到檔案句柄未釋放時的行為未驗。
- **暫存檔殘留未驗**：程式走 `finally` 之外的路徑（讀取階段拋例外、行程被中止）
  時，明文暫存檔是否一定被清掉，沒有留下斷言式證據。
- **支援的加密格式範圍未驗**：ECMA-376 Agile/Standard 實測過，
  其他容器（舊式 RC4、加密 OLE2 損壞檔）未測。
- **需要 `pip install msoffcrypto-tool`**：目前是手動安裝步驟，
  尚未寫進 SOP 的安裝段落。

## 7. 怎麼重跑

```bash
cd /home/hoonsoropenclaw/raphael-harness

# A/B 本體（容器內無主機金鑰、執行階段斷網）
python -m harness sandbox run --workdir sandbox/trial-msoffcrypto \
  --cmd "venv/bin/python run_ab.py"

# 反向對照：證明對帳守門抓得到 double count
python -m harness sandbox run --workdir sandbox/trial-msoffcrypto \
  --cmd "venv/bin/python neg_control.py"
```

守門未通過時 `run_ab.py` 會印 `FATAL: 對帳守門未通過 → A/B 結果無效，
不得拿去評審或採用`。

## 8. 檔案對照

| 檔案 | 說明 |
|---|---|
| `run_ab.py` | A/B 執行器（fixture 產生、兩邊跑、對帳守門、負向路徑） |
| `neg_control.py` | 反向對照（證明守門有效） |
| `run_ab_judge.py` | 跨模型評審（寫回 harness eval 紀錄） |
| `evidence/baseline/` | 基準版程式碼 + 輸出 + 執行紀錄 |
| `evidence/candidate/` | 候選版程式碼 + 輸出 + 執行紀錄 |
| `evidence/shared/variant_diff.patch` | 兩版程式碼差異（91 行，1 hunk） |
| `evidence/shared/ab_result.json` | 全部實測數據（fixture / 兩邊輸出 / 守門 / 負向路徑） |
| `evidence/shared/neg_control_result.json` | 反向對照結果 |
| `evidence/shared/fixture_sha256.txt` | 測試資料 SHA256 |
