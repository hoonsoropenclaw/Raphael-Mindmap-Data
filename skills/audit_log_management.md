# Audit Log Management

## 說明
此技能涉及管理和查詢審計日誌，以跟踪用戶活動並確保系統的安全性。

## 關鍵代碼片段或模式
1. 將事件記錄到 SQLite 數據庫：
   ```typescript
   await db.prepare("INSERT INTO audit_log (event, user, ip, userAgent, outcome, detail) VALUES (?, ?, ?, ?, ?, ?)").run(event, user, ip, userAgent, outcome, detail);
   ```
2. 查詢審計日誌：
   ```typescript
   const rows = await db.prepare("SELECT * FROM audit_log WHERE event = ? AND user = ? LIMIT ?").all(event, user, limit);
   ```
3. 使用 curl 查詢審計日誌：
   ```bash
   curl -s "http://127.0.0.1:3000/api/audit?event=mfa_verify_failure"
   ```

## 常見錯誤及避免方法
- **錯誤**：審計日誌記錄失敗。
  **避免方法**：檢查數據庫連接和查詢語句，並確保所有必要的字段都已提供。
- **錯誤**：查詢審計日誌時出現錯誤。
  **避免方法**：檢查查詢參數和語句，並確保數據庫中存在相應的數據。
- **錯誤**：審計日誌數據洩露。
  **避免方法**：實施適當的訪問控制措施，並限制對審計日誌的訪問權限。