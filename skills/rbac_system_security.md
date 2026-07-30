# RBAC System Security

## 說明
此微技能旨在實現基於角色的存取控制 (RBAC) 系統，以保護敏感數據的安全。

## 關鍵代碼片段
```javascript
// 授權函數範例
function authorize(subject, action, resource) {
    const policy = POLICIES.find(p => p.role === subject.role && p.action === action && p.resource === resource);
    return policy ? { allowed: true } : { allowed: false };
}
```

## 常見錯誤及避免方法
1. **錯誤：未授權的資源被訪問**
   - **解決方法**：確保所有資源訪問都經過 `authorize` 函數的檢查，並且默認情況下拒絕訪問 (`deny-by-default`)。
2. **錯誤：角色權限過大導致越權**
   - **解決方法**：細化角色權限，確保每個角色僅擁有完成其任務所需的最小權限。
3. **錯誤：未處理未知角色或操作**
   - **解決方法**：在授權函數中加入對未知角色或操作的處理，默認拒絕這些請求。