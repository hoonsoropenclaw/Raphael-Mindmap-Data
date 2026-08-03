# Headless Browser Verification

## 說明
使用無頭瀏覽器進行測試驗證，確保應用在無頭環境下的穩定性。包含啟動參數設置（如 `--no-sandbox` 和 `--disable-dev-shm-usage`）以避免資源限制問題。

## 關鍵程式碼片段
```javascript
// playwright.config.js
module.exports = {
  ...
  args: ['--no-sandbox', '--disable-dev-shm-usage'],
  ...
};
```

## 常見錯誤與解決方法
- **錯誤**：無頭瀏覽器因資源限制導致測試失敗。
  **解決方法**：增加啟動參數，如 `--disable-gpu` 和 `--disable-dev-shm-usage`，以減少資源消耗。