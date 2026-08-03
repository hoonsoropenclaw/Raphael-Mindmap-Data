# RBAC Implementation

## 說明...
此微技能涉及在應用程序中實現 RBAC，包括定義角色（如 Admin、Editor 和 Viewer）、分配權限以及根據當前角色限制用戶的操作。

## 關鍵代碼片段或模式
```javascript
const ROLES = {
  ADMIN: 'Admin',
  EDITOR: 'Editor',
  VIEWER: 'Viewer',
};

const permissions = {
  [ROLES.ADMIN]: {
    addNode: true,
    deleteNode: true,
    editTitle: true,
    // 其他權限...
  },
  [ROLES.EDITOR]: {
    addNode: true,
    deleteNode: false,
    editTitle: true,
    // 其他權限...
  },
  [ROLES.VIEWER]: {
    addNode: false,
    deleteNode: false,
    editTitle: false,
    // 其他權限...
  },
};

function checkPermission(role, action) {
  return permissions[role][action] || false;
}
```

## 常見錯誤及避免方法
- **錯誤**: 權限檢查邏輯錯誤，導致用戶能夠執行未授權的操作。
  **解決方法**: 仔細檢查 `checkPermission` 函數的實現，確保所有權限檢查都正確執行，並且角色和權限的映射關係正確。
- **錯誤**: 角色切換後權限未及時更新。
  **解決方法**: 確保在角色切換後，所有相關的 UI 組件和功能都重新渲染並應用新的權限設置。