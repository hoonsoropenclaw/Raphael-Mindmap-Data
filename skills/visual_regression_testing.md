# Visual Regression Testing

## 說明
此技能涵蓋如何使用 Playwright 進行視覺回歸測試，包括設置視覺測試腳本、生成視覺 baseline、運行測試並比較快照。

## 關鍵代碼片段
```javascript
// tests/e2e.spec.cjs
const { chromium } = require('playwright');

test('home surface remains stable', async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('http://localhost:4173');
  const screenshot = await page.screenshot();
  expect(screenshot).toMatchSnapshot();
  await browser.close();
});
```

## 常見錯誤及避免方法
- **錯誤**：快照比較失敗由於非預期的 UI 變更。
  **解決方法**：在進行 baseline 更新時，確保 UI 處於穩定狀態，並使用 `npm run baseline` 進行顯式更新。
- **錯誤**：視覺測試不穩定由於動態內容。
  **解決方法**：使用遮罩（masks）或忽略動態區域來減少誤報。