# 動態角色繼承圖

## 說明...

### 目的
使用 React Flow 庫構建動態角色繼承圖，實現節點和邊的動態添加、刪除和更新。

### 關鍵代碼片段
```javascript
function App() {
  const [nodes, setNodes, onNodesChange] = useNodesState([
    { id: '1', position: { x: 0, y: 0 }, data: { label: 'Test Node' } }
  ]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  return (
    <ReactFlowProvider>
      <div style={{ width: '100vw', height: '100vh', background: '#0a0a0a' }}>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          fitView
        >
          <Background color="#ffb800" gap={32} />
          <Controls />
          <MiniMap />
        </ReactFlow>
      </div>
    </ReactFlowProvider>
  );
}
```

### 常見錯誤及解決方法
- **錯誤**: 節點或邊的狀態管理不當，導致圖形無法正確更新。
  **解決方法**: 使用 `useNodesState` 和 `useEdgesState` 來管理節點和邊的狀態，確保每次更新都觸發重新渲染。
- **錯誤**: 圖形佈局混亂，無法自動調整。
  **解決方法**: 使用 `fitView` 屬性來自動調整視圖，或手動設置佈局參數以適應不同節點和邊的數量。