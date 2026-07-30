# React Flow Integration

## 說明
React Flow 是一個用於構建自定義流程圖的 React 庫。此技能涵蓋如何將 React Flow 整合到 React 應用程式中，包括初始化、節點和邊的渲染以及與應用程式的交互。

## 關鍵代碼片段
```javascript
import React from 'react';
import ReactDOM from 'react-dom';
import ReactFlow, { Background, Controls, MiniMap } from 'reactflow';

const nodes = [/* 節點數據 */];
const edges = [/* 邊數據 */];

function FlowComponent() {
  return (
    <ReactFlow
      nodes={nodes}
      edges={edges}
      onNodesChange={onNodesChange}
      onEdgesChange={onEdgesChange}
      fitView
      fitViewOptions={{ padding: 0.22 }}
    >
      <Background gap={22} size={1} />
      <Controls />
      <MiniMap nodeColor={(n) => (n.id === 'policy' ? '#c9aa62' : '#d97757')} maskColor='#101315aa' />
    </ReactFlow>
  );
}
```

## 常見錯誤及避免方法
1. **ReactFlow 命名空間錯誤**：ReactFlow UMD 版本中，ReactFlow 是物件命名空間而非函式。應使用 `RF.ReactFlow` 而非 `RF.ReactFlow()`。
2. **節點和邊的數據格式錯誤**：確保節點和邊的數據格式符合 React Flow 的要求，否則可能導致渲染失敗。
3. **缺少必要的依賴**：確保所有必要的 React Flow 組件（如 `Background`, `Controls`, `MiniMap`）都已正確導入。
