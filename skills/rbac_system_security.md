# RBAC System Security

## 說明...

### 目的
在應用中實現基於角色的權限管理，確保不同角色擁有不同權限。

### 關鍵代碼片段
```javascript
const ROLE_LABELS = {
  admin: 'Admin：完整管理 / 稽核',
  manager: 'Manager：會辦 / 簽核',
  staff: 'Staff：建立 / 編修 / 通知',
  viewer: 'Viewer：唯讀案件進度',
};

function useStoreAPI() {
  const role = useStore(s => s.role);
  // 根據角色返回不同的權限
  switch (role) {
    case 'admin':
      return { ...adminPermissions };
    case 'manager':
      return { ...managerPermissions };
    case 'staff':
      return { ...staffPermissions };
    case 'viewer':
      return { ...viewerPermissions };
    default:
      return {};
  }
}
```

### 常見錯誤及避免方法
- **錯誤**：權限檢查邏輯錯誤，導致未授權用戶訪問受限資源。
  **解決方法**：在每個受保護的路由或組件中明確檢查用戶角色，並在後端進行二次驗證。
- **錯誤**：角色定義不一致，導致權限混亂。
  **解決方法**：在單獨的配置文件中定義角色和權限，並在整個應用中統一引用。