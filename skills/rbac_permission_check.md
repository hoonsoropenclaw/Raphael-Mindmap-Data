# RBAC Permission Check

## 說明...

### 關鍵代碼片段
- 定義角色權限
  ```javascript
  const ROLES = {
    admin: { can: { editNode: true, deleteNode: true, ... } },
    employee: { can: { editNode: (node) => node.type === 'employee_submit', ... } },
    // 其他角色
  }
  ```
- 檢查權限
  ```javascript
  const checkPermission = (role, permission, context) => {
    const perm = ROLES[role]?.can[permission];
    if (typeof perm === 'function') return perm(context);
    if (typeof perm === 'boolean') return perm;
    return false;
  }
  ```

### 常見錯誤及避免方法
- **錯誤**：權限檢查函數未正確處理不同類型的權限定義（函數型、布爾型、陣列型）。
  **解決方法**：在檢查權限時，先確定權限定義的類型，然後根據類型進行相應的處理。
- **錯誤**：權限檢查結果與預期不符。
  **解決方法**：檢查角色權限定義是否正確，並確保傳遞給權限檢查函數的參數與定義相符。