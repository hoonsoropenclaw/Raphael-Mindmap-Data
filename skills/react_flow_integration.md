# React Flow Integration

## 說明...
React Flow 是一個用於建立可拖曳流程圖的 React 庫。此技能涵蓋如何將 React Flow 引入 React 應用中，包括初始化畫布、定義節點和邊，以及處理用戶交互。

## 關鍵代碼片段或模式
```javascript
import React, { useState } from 'react';
import ReactFlow, { MiniMap, Controls, Background } from 'reactflow';

const initialNodes = [
  { id: '1', type: 'input', position: { x: 250, y: 5 }, data: { label: 'Start' } },
  // 更多節點
];
const initialEdges = [
  { id: 'e1-2', source: '1', target: '2', animated: true },
  // 更多邊
];

function FlowEditor() {
  const [nodes, setNodes] = useState(initialNodes);
  const [edges, setEdges] = useState(initialEdges);

  return (
    <ReactFlow
      nodes={nodes}
      edges={edges}
      onNodesChange={setNodes}
      onEdgesChange={setEdges}
      fitView
    >
      <Controls />
      <MiniMap />
      <Background variant="dots" gap={12} size={1} />
    </ReactFlow>
  );
}
```

## 常見錯誤及避免方法
- **節點或邊未正確初始化**：確保 `initialNodes` 和 `initialEdges` 包含所有必要的屬性，如 `id`、`source` 和 `target`。
- **事件處理不當**：使用 `onNodesChange` 和 `onEdgesChange` 來更新狀態，否則畫布不會反映用戶的更改。
- **性能問題**：對於大型流程圖，考慮使用 `ReactFlow` 的優化選項，如 `zoomOnPinch` 和 `panOnScroll`。