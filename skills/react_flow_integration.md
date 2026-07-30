# React Flow Integration

## 說明...

### 目的
將 React Flow 集成到 React 應用中，實現可拖拽、可連接的流程圖功能。

### 關鍵代碼片段
```javascript
import ReactFlow from 'reactflow';
import 'reactflow/dist/style.css';

function App() {
  return (
    <ReactFlowProvider>
      <ReactFlow
        nodes={initialNodes}
        edges={initialEdges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
      >
        <Controls />
        <MiniMap />
      </ReactFlow>
    </ReactFlowProvider>
  );
}
```

### 常見錯誤及避免方法
- **錯誤**：節點無法拖拽或連接失敗。
  **解決方法**：確保 `ReactFlowProvider` 包裹了 `ReactFlow` 組件，並正確設置 `nodes` 和 `edges` 狀態。
- **錯誤**：樣式問題，導致流程圖顯示異常。
  **解決方法**：確認已正確引入 React Flow 的 CSS 文件。