# Audit Logging

## 說明
此技能涉及實現審計日誌記錄，以跟踪用戶的操作並確保系統的安全性。

## 關鍵代碼片段
```typescript
export interface AuditEntry {
  ts: string;
  user: string;
  role: string;
  method: string;
  platform: string;
  path: string;
  action: string;
  allowed: boolean;
  status: number;
}

export const auditLog: AuditEntry[] = [];

export function withAudit(...): NextResponse {
  // 記錄審計日誌
  auditLog.push(...);
  return response;
}
```

## 常見錯誤及避免方法
- **錯誤**：審計日誌未正確記錄。
  **解決方法**：確保每次用戶操作都調用 `withAudit` 函數。
- **錯誤**：審計日誌存儲在內存中，導致數據丟失。
  **解決方法**：考慮將審計日誌存儲在持久化存儲中，例如數據庫或日誌文件。