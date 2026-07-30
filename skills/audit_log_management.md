# Audit Log Management

## 說明...
記錄用戶的關鍵操作和事件，以便後續審計和監控。

## 關鍵代碼片段或模式
```javascript
// 將審計日誌掛載到 window 以便在測試中訪問
if (typeof window !== 'undefined') {
  window.__auditLog = auditLog;
  window.__stats = stats;
}

// 記錄審計日誌
function logAudit(entry) {
  auditLog.unshift({ ...entry, timestamp: new Date().toLocaleTimeString() });
}
```

## 常見錯誤及避免方法
- **錯誤**：在審計日誌中未包含足夠的上下文信息，導致無法準確追蹤操作。
  **解決方法**：在記錄審計日誌時包含詳細的操作信息、執行者信息和時間戳。
- **錯誤**：在客戶端和服務器端對審計日誌的實現不一致，導致數據不一致。
  **解決方法**：在服務器端進行統一的審計日誌管理，並確保所有關鍵操作都經過服務器端的記錄。