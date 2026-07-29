# NextAuth.js RBAC Implementation

## 說明...
此微技能涵蓋使用 NextAuth.js 來實現細粒度的權限管理系統，包括角色定義、權限分配、資源級別的權限檢查以及基於用戶角色的訪問控制。

## 關鍵代碼片段或模式
```javascript
// 定義角色和權限
const PERMISSIONS = {
  'document:read': new Set(['admin', 'editor', 'viewer', 'guest']),
  'document:update': new Set(['admin', 'editor']),
  'document:delete': new Set(['admin']),
  // 其他權限定義
};

// 檢查用戶是否有特定權限
function can(user, permission, resource) {
  if (!user || !user.role) return { ok: false, message: '未認證' };
  const rolePermissions = PERMISSIONS[permission] || new Set();
  if (!rolePermissions.has(user.role)) {
    return { ok: false, message: '權限不足' };
  }
  // 資源級別檢查，例如敏感資源
  if (resource && resource.sensitive && !rolePermissions.has('admin')) {
    return { ok: false, message: '敏感資源訪問被拒絕' };
  }
  return { ok: true };
}
```

## 常見錯誤及避免方法
- **錯誤**：權限檢查邏輯錯誤，導致未授權用戶訪問受保護資源。
  **解決方法**：在開發過程中進行全面的單元測試，確保每個權限檢查點都正確實現。
- **錯誤**：資源級別的權限檢查未覆蓋所有敏感資源。
  **解決方法**：在設計權限系統時，清晰地定義哪些資源需要額外的檢查，並在代碼中明確實現這些檢查。
- **錯誤**：用戶角色和權限定義不一致。
  **解決方法**：使用集中化的權限管理模塊，並在系統啟動時進行驗證，確保角色和權限的一致性。