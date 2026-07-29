# React Flow Role-Based Access Control

## 說明...
此技能涉及在 React Flow 中根據不同角色設置節點和邊的權限，包括讀取、編輯、批准和拒絕操作。

## 關鍵代碼片段或模式
```javascript
// 角色定義
const ROLES = {
  guest: { name: '訪客', permissions: [] },
  sysadmin: { name: '系統管理員', permissions: ['read', 'write', 'approve', 'reject', 'reset'] },
  // 其他角色...
};

// 節點權限矩陣
const NODE_PERMS = {
  'submit_request': { write: ['sysadmin', 'dept_officer'], approve: ['sysadmin'], reject: ['sysadmin'] },
  // 其他節點...
};

// 權限判定函式
const canWrite = (role, nodeId) => NODE_PERMS[nodeId].write.includes(role);
const canApprove = (role, nodeId) => NODE_PERMS[nodeId].approve.includes(role);

// 自訂節點組件
const FlowStepNode = ({ id, data, selected }) => (
  <div className={`flow-node ${data.status}`}>
    <div className="fn-title">{data.label}</div>
    <div className="fn-meta">
      {canWrite(currentRole, id) ? '可操作' : '只讀'}
    </div>
    {/* 其他內容... */}
  </div>
);

// 動態狀態引擎
const computedEdges = useMemo(() => {
  return edges.map(edge => ({
    ...edge,
    className: edgeStatusMapping[edge.status],
  }));
}, [edges]);

// 操作控制器
const handleSubmit = (nodeId) => {
  if (canWrite(currentRole, nodeId)) {
    // 執行送審邏輯
  }
};
```

## 常見錯誤及避免方法
- **錯誤**：在 importmap 環境中無法正確解析 CSS 子路徑。
  **解決方法**：使用 `<link>` 標籤通過 esm.sh 的 CSS endpoint 引入 CSS，或將 CSS 直接內聯到 HTML 中。
- **錯誤**：冗餘的 `setNodes` 調用導致狀態覆蓋。
  **解決方法**：檢查並刪除不必要的 `setNodes` 調用，確保每個狀態更新邏輯只調用一次。
- **錯誤**：權限判定函式未正確實現，導致權限控制失效。
  **解決方法**：確保 `canWrite`、`canApprove` 等函式正確檢查當前角色和節點權限。