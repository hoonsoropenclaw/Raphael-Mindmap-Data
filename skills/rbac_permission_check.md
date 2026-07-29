# RBAC Permission Check

## 說明...

### 目的
實現一個基於角色的權限檢查系統，支持不同角色（如管理員、主管、員工、檢視者）的權限驗證。

### 關鍵代碼片段
```javascript
const ROLES = {
  admin: { can: { createNode: true, editNode: true, deleteNode: true } },
  manager: { can: { createNode: true, editNode: true, deleteNode: false } },
  employee: { can: { createNode: false, editNode: true, deleteNode: false } },
  viewer: { can: { createNode: false, editNode: false, deleteNode: false } }
};

function checkPermission(role, action, context) {
  const perm = ROLES[role]?.can[action];
  if (perm === undefined || perm === null) return false;
  if (typeof perm === 'boolean') return perm;
  if (typeof perm === 'function') return perm(context);
  if (Array.isArray(perm)) return perm.includes(context);
  return false;
}
```

### 常見錯誤及避免方法
- **錯誤**：權限檢查函數未正確處理不同類型的權限定義。
  - **解決方法**：確保函數能夠處理布爾值、函數和數組類型的權限定義。
- **錯誤**：角色或動作名稱拼寫錯誤導致權限檢查失敗。
  - **解決方法**：使用常量或枚舉來定義角色和動作名稱，避免拼寫錯誤。