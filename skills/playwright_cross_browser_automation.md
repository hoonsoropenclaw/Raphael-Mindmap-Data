# Playwright Cross Browser Automation

## 說明
使用 Playwright 進行跨瀏覽器自動化測試，涵蓋 Chromium、Firefox、WebKit 以及其行動版本。透過矩陣測試確保應用在多種瀏覽器上的相容性。

## 關鍵程式碼片段
```javascript
// playwright.config.js
const { devices } = require('playwright');

module.exports = {
  projects: [
    {
      name: 'Chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'Firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'WebKit',
      use: { ...devices['Desktop Safari'] },
    },
    {
      name: 'Mobile-Chromium',
      use: { ...devices['Pixel 5'] },
    },
    {
      name: 'Mobile-WebKit',
      use: { ...devices['iPhone 13'] },
    },
  ],
};
```

## 常見錯誤與解決方法
- **錯誤**：行動裝置測試中滑鼠事件失效。
  **解決方法**：使用 `page.touch` 系列 API 替代滑鼠事件。
- **錯誤**：瀏覽器啟動參數錯誤導致測試失敗。
  **解決方法**：使用 Playwright 提供的 `devices` 設定，避免手動配置錯誤。