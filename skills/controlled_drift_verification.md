# Controlled Drift Verification

## 說明
此技能涉及故意改變 UI 的某些屬性（例如顏色或佈局），以驗證視覺回歸測試是否能夠捕捉到這些變更。

## 關鍵代碼片段
```javascript
// 臨時修改 CSS 變量以引入 drift
await page.addStyleTag({ content: 'body { --accent: #ff4d6d; }' });
```

## 常見錯誤及避免方法
- **錯誤**：引入的 drift 未被視覺測試捕獲。
  **解決方法**：檢查視覺測試的配置，確保 `maxDiffPixelRatio` 和 `threshold` 設置合理，並確認測試腳本正確運行。
- **錯誤**：drift 引入後無法恢復。
  **解決方法**：在測試前後備份和恢復 UI 狀態，例如使用文件備份或版本控制。