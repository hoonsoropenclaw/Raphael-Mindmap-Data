# Playwright Dynamic Scraper

## 說明...
### 目的
- 動態渲染網頁並提取結構化數據。
- 監聽網絡請求以進行 API 逆向工程。
- 輸出結果為 JSON 格式。

### 關鍵代碼片段或模式
- 初始化 Playwright 並啟動瀏覽器，例如：
  ```python
  with sync_playwright() as p:
      browser = p.chromium.launch(headless=True)
      page = browser.new_page()
  ```
- 導航到目標 URL 並等待特定選擇器，例如：
  ```python
  page.goto(args.url)
  page.wait_for_selector(args.selector, timeout=args.timeout)
  ```
- 截圖並保存，例如：
  ```python
  page.screenshot(path=args.screenshot)
  ```
- 監聽網絡請求，例如：
  ```python
  page.on("request", lambda request: network_requests.append(request.url))
  ```
- 提取數據並輸出 JSON，例如：
  ```python
  data = page.evaluate(f"document.querySelector('{args.selector}').innerText")
  with open(args.output, 'w', encoding='utf-8') as f:
      json.dump({'url': args.url, 'data': data}, f, ensure_ascii=False, indent=2)
  ```

### 常見錯誤及避免方法
- **錯誤**: 選擇器等待超時。
  **避免方法**: 增加等待時間或使用更穩健的選擇器。
- **錯誤**: 網絡請求未被正確監聽。
  **避免方法**: 確保事件監聽器在網頁加載前設置，並檢查瀏覽器控制台是否有錯誤。
- **錯誤**: 輸出 JSON 格式錯誤。
  **避免方法**: 使用 `json.dump` 並設置 `ensure_ascii=False` 和 `indent=2` 以確保可讀性。