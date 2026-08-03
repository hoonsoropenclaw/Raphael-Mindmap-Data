# Browser Navigate

## 說明
此技能用於在瀏覽器中導航到指定的URL，並等待頁面加載完成。

## 關鍵代碼片段
```python
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto('https://example.com')
    browser.close()
```

## 常見錯誤及避免方法
- **錯誤**：URL無效或無法訪問。
  **解決方法**：在導航前驗證URL的有效性。

- **錯誤**：瀏覽器無法啟動。
  **解決方法**：確保瀏覽器驅動程序已正確安裝並配置。