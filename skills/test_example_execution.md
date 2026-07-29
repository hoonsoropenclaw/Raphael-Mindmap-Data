# Test Example Execution

## 說明...
### 目的
- 驗證 `playwright_dynamic_scraper.py` 的功能是否正常。
- 確保所有模式（基本抓取、進階抽取、網絡監聽）均能正確執行。

### 關鍵代碼片段或模式
- 使用 `subprocess.run` 執行測試命令，例如：
  ```python
  result = subprocess.run(ex['cmd'], capture_output=True, text=True, timeout=60)
  ```
- 檢查退出代碼並輸出結果，例如：
  ```python
  if result.returncode == 0:
      print("✅ 成功")
  else:
      print("❌ 失敗")
  ```
- 驗證 JSON 輸出內容，例如：
  ```python
  import json
  d = json.load(open('result.json'))
  print(f'URL: {d["url"]}')
  ```

### 常見錯誤及避免方法
- **錯誤**: 測試腳本執行超時。
  **避免方法**: 增加超時時間或優化測試腳本以加快執行速度。
- **錯誤**: 測試結果與預期不符。
  **避免方法**: 檢查目標網站結構是否發生變化，並更新選擇器或提取邏輯。