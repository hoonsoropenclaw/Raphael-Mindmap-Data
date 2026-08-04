# React Flow Integration

## 說明...

### 目的
將 React Flow 套件整合到 React 應用中，以實現拖放式流程圖編輯功能。

### 關鍵代碼片段
```javascript
import ReactFlow from '@xyflow/react';
import { ReactFlowProvider } from '@xyflow/react';

function App() {
  return (
    <ReactFlowProvider>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onInit={setRf}
        onDrop={drop}
        onDragOver={onDragOver}
        nodeTypes={nodeTypes}
      />
    </ReactFlowProvider>
  );
}
```

### 常見錯誤及避免方法
- **錯誤**：無法渲染流程圖。
  **解決方法**：確保已正確引入 React Flow 的 CSS 樣式和依賴套件。
- **錯誤**：拖放功能失效。
  **解決方法**：檢查 `onDrop` 和 `onDragOver` 事件處理函數是否正確實現，並確保 `dataTransfer` 資料格式正確。