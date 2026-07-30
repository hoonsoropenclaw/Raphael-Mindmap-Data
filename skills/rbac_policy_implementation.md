# RBAC Policy Implementation

## 說明
RBAC 是一種訪問控制機制，根據用戶的角色來管理其對資源的訪問權限。此技能涵蓋如何實現 RBAC 策略，包括身份驗證、角色分配、資源訪問控制和決策邏輯。

## 關鍵代碼片段
```javascript
const users = [
  { id: 'alice', name: 'Alice Chen', role: 'Admin', dept: 'Platform Engineering', color: '#d97757' },
  { id: 'bruno', name: 'Bruno Lin', role: 'Editor', dept: 'Content Operations', color: '#7f9eb0' },
  { id: 'cathy', name: 'Cathy Wu', role: 'Viewer', dept: 'Finance', color: '#c9aa62' }
];

const [user, setUser] = React.useState(users[0]);
const [strict, setStrict] = React.useState(true);
const [logs, setLogs] = React.useState([{ t: now(), msg: 'policy graph initialized', ok: true }]);

const allowed = user.role === 'Admin' || (user.role === 'Editor' && !strict);

function select(u) {
  setUser(u);
}

function reset() {
  setUser(users[0]);
  setStrict(true);
  setLogs([{ t: now(), msg: 'policy graph reset', ok: true }]);
}
```

## 常見錯誤及避免方法
1. **角色權限邏輯錯誤**：確保角色權限邏輯正確，否則可能導致未授權的訪問或過度限制。
2. **狀態管理不當**：使用 React 的 `useState` 和 `useEffect` 來管理用戶狀態和決策日誌，避免狀態不同步或數據丟失。
3. **缺乏審計日誌**：實現審計日誌以記錄所有訪問決策和用戶操作，這對於安全性和合規性至關重要。
