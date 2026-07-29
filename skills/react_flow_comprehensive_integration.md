# React Flow Comprehensive Integration

## 說明...
### 目的
將 React Flow 框架整合到應用中，實現自訂節點類型、Inspector 元件和 JSON 匯出功能。

### 關鍵代碼片段
```javascript
// 初始化 React Flow
const reactFlowInstance = useReactFlow();

// 自訂節點類型
const CustomNodeComponent = ({ data }) => {
  return <div>{data.label}</div>;
};

// Inspector 元件
const Inspector = () => {
  const [selectedNodes, setSelectedNodes] = useState([]);
  return (
    <div>
      {selectedNodes.map(node => (
        <div key={node.id}>
          <input
            value={node.data.label}
            onChange={(e) => {
              reactFlowInstance.setNodes(
                reactFlowInstance
                  .getNodes()
                  .map(n => (n.id === node.id ? { ...n, data: { ...n.data, label: e.target.value } } : n))
              );
            }}
          />
        </div>
      ))}
    </div>
  );
}

// JSON 匯出功能
const exportToJson = () => {
  const flow = reactFlowInstance.toObject();
  const json = JSON.stringify(flow);
  console.log(json);
}
```

### 常見錯誤及避免方法
- **錯誤**：自訂節點無法正確渲染。
  **解決方法**：確保自訂節點組件符合 React Flow 的要求，並正確傳遞必要的 props。
- **錯誤**：Inspector 無法獲取選中的節點。
  **解決方法**：使用 React Flow 提供的 hooks（如 `useNodesState`）來獲取當前選中的節點。
- **錯誤**：JSON 匯出後無法正確導入。
  **解決方法**：確保匯出的 JSON 結構符合 React Flow 的要求，並在導入時進行必要的驗證。