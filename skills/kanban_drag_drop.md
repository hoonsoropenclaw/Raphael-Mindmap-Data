# Kanban Drag and Drop

## 說明...
此技能涉及實現 Kanban 看板的拖放功能，包括拖動卡片、將其放置到不同的欄位，以及同步更新應用狀態。

## 關鍵代碼片段或模式
```javascript
// Example: 拖放邏輯
const handleDragEnd = (result) => {
  const { destination, source, draggableId } = result;
  if (!destination) return;
  if (
    destination.droppableId === source.droppableId &&
    destination.index === source.index
  ) {
    return;
  }
  const newCases = Array.from(cases);
  const [removed] = newCases.splice(source.index, 1);
  newCases.splice(destination.index, 0, removed);
  setCases(newCases);
};
```

## 常見錯誤及避免方法
- **錯誤**: 拖放後狀態未更新。
  **解決方法**: 確認 `setCases` 函數正確更新狀態，並檢查是否有其他邏輯干擾狀態更新。
- **錯誤**: 拖放後卡片彈回原位。
  **解決方法**: 檢查 `dragSnapToOrigin` 設置，確保其不會覆蓋拖放後的位置更新。