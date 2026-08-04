# Playwright Visual Validation

## 說明...
透過 Playwright 的 `page.locator` 和 `evaluate` 方法，可以檢查特定 UI 元素是否存在、可見，以及其布局是否符合預期。

## 關鍵程式碼片段
```javascript
const checks = {
  'hero title exists': await page.locator('.hero__title').count() > 0,
  '6 demo cards': await page.locator('.demo-card').count() === 6,
};
```

## 常見錯誤及避免方法
- **錯誤**: 元素選擇器錯誤，導致檢查失敗。
  **解決方法**: 確認選擇器正確，並使用瀏覽器的開發者工具進行測試。
- **錯誤**: 元素尚未加載完成，導致檢查失敗。
  **解決方法**: 在檢查前使用 `await page.waitForSelector` 或類似的等待方法，確保元素已加載。