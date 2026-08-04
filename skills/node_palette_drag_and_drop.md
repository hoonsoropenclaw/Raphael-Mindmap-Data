# Node Palette Drag and Drop

## 說明...

### 目的
實現流程節點的拖放功能，使用戶能夠從側邊欄拖動節點到畫布上。

### 關鍵代碼片段
```javascript
const dragStart = (e, kind) => {
  e.dataTransfer.setData('application/xyflow', kind);
  e.dataTransfer.effectAllowed = 'move';
};

const drop = useCallback(e => {
  e.preventDefault();
  const kind = e.dataTransfer.getData('application/xyflow');
  if (!kind || !rf) return;
  snapshot();
  const pos = rf.screenToFlowPosition({ x: e.clientX, y: e.clientY });
  const t = TYPES[kind];
  setNodes(ns => ns.concat({
    id: crypto.randomUUID(),
    type: 'workflow',
    position: pos,
    data: { kind, label: t.label, description: t.desc }
  }));
}, [rf, setNodes, snapshot]);
```

### 常見錯誤及避免方法
- **錯誤**：拖放後節點未出現在畫布上。
  **解決方法**：檢查 `drop` 事件處理函數是否正確調用了 `setNodes` 更新狀態，並確保 `dataTransfer` 資料格式正確。
- **錯誤**：節點位置不正確。
  **解決方法**：確認 `screenToFlowPosition` 方法的實現是否正確，並檢查畫布的坐標系統設置。