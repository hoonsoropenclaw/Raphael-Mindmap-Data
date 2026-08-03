# Playwright Skill

## 說明...
Playwright 是一個用於自動化瀏覽器操作的工具，適用於 Chromium、Firefox 和 WebKit 等主流瀏覽器。本技能涵蓋了如何初始化 Playwright、啟動瀏覽器實例、導航到目標頁面、執行操作以及截取屏幕截圖。

## 關鍵代碼片段或模式
```javascript
const { chromium, firefox, webkit } = require('playwright');

(async () => {
  for (const browserType of [chromium, firefox, webkit]) {
    const browser = await browserType.launch();
    const page = await browser.newPage();
    await page.goto('https://example.com');
    // 執行操作，例如截圖
    await page.screenshot({ path: `example-${browserType.name()}.png` });
    await browser.close();
  }
})();
```

## 常見錯誤及避免方法
- **錯誤**：瀏覽器無法啟動。
  **解決方法**：檢查是否已安裝對應的瀏覽器，並確保 Playwright 的瀏覽器二進制文件是最新的。
- **錯誤**：導航超時。
  **解決方法**：增加 `page.goto` 的超時時間，或檢查目標頁面是否可訪問。