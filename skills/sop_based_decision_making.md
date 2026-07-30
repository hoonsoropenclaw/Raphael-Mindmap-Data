# SOP-Based Decision Making

## 說明...
此微技能涉及根據標準作業程序（SOP）來設計決策節點的邏輯，包括條件判斷、分流和路由。

## 關鍵程式碼片段或模式
```javascript
// 定義 SOP 決策邏輯
const advanceWithChoice = (nodeId, choice) => {
  const currentNode = nodes.find((node) => node.id === nodeId);
  const nextNodes = edges.filter((edge) => edge.source === nodeId);
  const chosenEdge = nextNodes.find((edge) => edge.label === choice);
  if (chosenEdge) {
    setNodes((nds) => nds.map((node) => {
      if (node.id === nodeId) {
        node.selected = false;
      }
      return node;
    }));
    setEdges((eds) => eds.map((edge) => {
      if (edge.source === nodeId && edge.label === choice) {
        edge.selected = true;
      } else {
        edge.selected = false;
      }
      return edge;
    }));
    setNodes((nds) => nds.concat(chosenEdge.target));
  }
};
```

## 常見錯誤及避免方法
- **錯誤**：SOP 規則未正確映射到決策節點，導致無法正確分流。
  **解決方法**：確保 SOP 規則在程式碼中正確實現，並在設計節點時與規則對應。
- **錯誤**：條件判斷邏輯錯誤，導致決策結果不正確。
  **解決方法**：在實作前仔細檢查 SOP 規則，並在開發過程中進行充分的測試。