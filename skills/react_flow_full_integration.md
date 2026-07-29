# React Flow Full Integration

## 說明...
此技能涵蓋如何在 React Flow 中建立角色權限管理系統，包括角色和資源的 CRUD 操作、三態權限矩陣（允許/拒絕/繼承）、角色繼承圖的動態渲染，以及循環繼承的偵測與阻擋。

## 關鍵程式碼片段或模式
```javascript
// 角色繼承圖的渲染邏輯
const onNodesChange = useCallback((changes) => {
  setNodes((nds) => applyNodeChanges(changes, nds));
  // 更新角色狀態
}, []);

const onEdgesChange = useCallback((changes) => {
  setEdges((eds) => applyEdgeChanges(changes, eds));
  // 更新邊線狀態
}, []);

// 權限計算邏輯
const resolvePermissions = useCallback(() => {
  // 計算有效權限，考慮繼承與拒絕優先
}, []);
```

## 常見錯誤及避免方法
1. **循環繼承問題**：未正確實現循環繼承的偵測與阻擋，可能導致無限迴圈。
   - **解決方法**：在新增邊線時檢查是否會產生循環，並在偵測到循環時阻擋操作。
2. **React Flow 版本衝突**：使用不同版本的 React Flow 可能導致 API 不兼容。
   - **解決方法**：確保使用與樣板相容的 React Flow 版本，例如 11.11.4。
3. **Controls 和 MiniMap 樣式衝突**：Controls 或 MiniMap 可能會遮擋主要節點。
   - **解決方法**：使用絕對定位並設置固定尺寸和 z-index 以避免遮擋。