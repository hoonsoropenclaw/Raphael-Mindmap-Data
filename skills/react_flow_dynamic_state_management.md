# React Flow Dynamic State Management

## 說明...
此技能涉及在 React Flow 中根據節點和邊的狀態動態更新 UI，包括節點的鎖定、解鎖、激活和完成狀態。

## 關鍵代碼片段或模式
```javascript
const computedEdges = useMemo(() => {
  return edges.map(edge => ({
    ...edge,
    className: edgeStatusMapping[edge.status],
  }));
}, [edges]);

const FlowStepNode = ({ id, data, selected }) => (
  <div className={`flow-node ${data.status}`}>
    <div className="fn-title">{data.label}</div>
    <div className="fn-meta">
      {canWrite(currentRole, id) ? '可操作' : '只讀'}
    </div>
    {/* 其他內容... */}
  </div>
);
```

## 常見錯誤及避免方法
- **錯誤**：狀態更新邏輯錯誤，導致 UI 未正確反映狀態。
  **解決方法**：確保狀態更新函式正確處理節點和邊的狀態，並使用 `useMemo` 來優化計算。
- **錯誤**：節點組件未正確接收狀態屬性，導致 UI 渲染錯誤。
  **解決方法**：檢查節點組件的 props 是否正確傳遞，並確保所有必要的狀態屬性都已包含。