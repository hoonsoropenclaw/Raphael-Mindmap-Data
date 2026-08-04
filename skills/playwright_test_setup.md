# Playwright Test Setup

## 說明
此技能涵蓋如何配置 Playwright 以進行跨瀏覽器自動化測試，包括安裝依賴、設置 `playwright.config.cjs` 配置文件，以及初始化測試腳本。

## 關鍵代碼片段
```javascript
// playwright.config.cjs
const { devices } = require('playwright');

module.exports = {
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] }
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] }
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] }
    },
    {
      name: 'mobile-chromium',
      use: { ...devices['Pixel 5'] }
    },
    {
      name: 'mobile-webkit',
      use: { ...devices['iPhone 12'] }
    }
  ],
  /* 其他配置 */
};
```

## 常見錯誤及避免方法
- **錯誤**：依賴安裝失敗或版本衝突。
  **解決方法**：使用 `npm ci` 鎖定依賴版本，並確保 `package-lock.json` 與 `package.json` 同步。
- **錯誤**：瀏覽器版本不兼容。
  **解決方法**：在 `playwright.config.cjs` 中明確指定瀏覽器版本，或使用 Playwright 自動管理的瀏覽器版本。