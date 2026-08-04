# Undo Redo Functionality

## 說明...

### 目的
為流程編輯器添加復原和重做功能，使用戶能夠回滾或重複之前的操作。

### 關鍵代碼片段
```javascript
const history = useRef([]);
const redo = useRef([]);

const snapshot = useCallback(() => {
  history.current.push({
    nodes: JSON.parse(JSON.stringify(nodes)),
    edges: JSON.parse(JSON.stringify(edges))
  });
  if (history.current.length > 30) history.current.shift();
  redo.current = [];
}, [nodes, edges]);

const undo = () => {
  const s = history.current.pop();
  if (!s) return;
  redo.current.push({ nodes, edges });
  setNodes(s.nodes);
  setEdges(s.edges);
  setSelected(null);
};

const redoIt = () => {
  const s = redo.current.pop();
  if (!s) return;
  history.current.push({ nodes, edges });
  setNodes(s.nodes);
  setEdges(s.edges);
};
```

### 常見錯誤及避免方法
- **錯誤**：復原後狀態不一致。
  **解決方法**：確保在每次操作後調用 `snapshot` 方法，並使用深拷貝來存儲歷史狀態。
- **錯誤**：重做功能失效。
  **解決方法**：檢查 `redo` 堆棧的實現是否正確，並確保在每次復原操作後正確更新 `redo` 堆棧。