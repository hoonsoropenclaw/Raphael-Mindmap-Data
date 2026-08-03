# dag_based_application_integration

## Target Skill Name
dag_based_application_integration

## Target Summary
整合 DAG 編輯器與工作流程管理系統到應用程式中，以實現基於 DAG 的應用程式架構。

## 說明
本技能旨在將 DAG（Directed Acyclic Graph）編輯器與工作流程管理系統集成到應用程式中，以實現基於 DAG 的應用程式架構。該架構將支持動態工作流管理，包括節點的展開/收縮、批量操作、深度控制等功能，並與側邊欄藍圖樹實現雙向同步。此外，該技能還涵蓋了 DAG 的拓撲排序、環檢測、任務調度和執行等關鍵組件，以確保工作流程的高效管理和執行。

### 1. DAG 編輯器集成

#### React Flow UMD 設置

為了方便在瀏覽器中直接使用 React Flow，我們將使用其 UMD 版本，通過 CDN 引入並解構 `window.ReactFlow`。

##### 步驟

1. **引入 React Flow UMD 版本**
   在你的 HTML 文件中，通過 CDN 引入 React Flow 的 UMD 版本：
   ```html
   <script src="https://unpkg.com/react-flow@latest/dist/react-flow.umd.js"></script>
   ```

2. **解構 React Flow**
   在你的 JavaScript 文件中，解構 `window.ReactFlow` 以便在代碼中使用：
   ```javascript
   const ReactFlow = window.ReactFlow;
   ```

3. **初始化 React Flow**
   在你的應用中初始化 React Flow：
   ```javascript
   const initialElements = [
     {
       id: '1',
       type: 'input',
       data: { label: '輸入節點' },
       position: { x: 250, y: 5 },
     },
     // 其他節點...
   ];

   function Flow() {
     return (
       <ReactFlow
         elements={initialElements}
         onLoad={reactFlowInstance => console.log('flow loaded:', reactFlowInstance)}
       />
     );
   }

   ReactDOM.render(<Flow />, document.getElementById('root'));
   ```

##### 功能概述

- **節點的展開/收縮**：允許用戶展開或收縮節點以顯示或隱藏詳細信息。
- **批量操作**：支持對多個節點進行批量選擇、移動、刪除等操作。
- **深度控制**：控制節點的層級結構，確保 DAG 的無環特性。
- **雙向同步**：與側邊欄藍圖樹實現雙向同步，確保編輯器與藍圖樹的一致性。

##### 實現細節

1. **節點的展開/收縮**
   使用 React Flow 的節點自定義功能，實現節點的展開和收縮：
   ```javascript
   const nodeTypes = {
     collapsible: (props) => {
       const [isExpanded, setIsExpanded] = useState(false);
       return (
         <div onClick={() => setIsExpanded(!isExpanded)}>
           {isExpanded ? '▼' : '▶'} {props.data.label}
         </div>
       );
     },
   };

   function Flow() {
     return (
       <ReactFlow
         elements={initialElements}
         nodeTypes={nodeTypes}
       />
     );
   }
   ```

2. **批量操作**
   實現批量選擇和操作功能：
   ```javascript
   function Flow() {
     const [selectedElements, setSelectedElements] = useState([]);

     const onSelectionChange = (elements) => {
       setSelectedElements(elements);
     };

     const handleDelete = () => {
       // 刪除選中的節點
       const updatedElements = elements.filter(el => !selectedElements.includes(el));
       setElements(updatedElements);
     };

     return (
       <div>
         <button onClick={handleDelete}>刪除選中節點</button>
         <ReactFlow
           elements={elements}
           onSelectionChange={onSelectionChange}
         />
       </div>
     );
   }
   ```

3. **深度控制**
   通過限制節點的連接，確保 DAG 的無環特性：
   ```javascript
   function Flow() {
     const onConnect = (params) => {
       // 檢查連接是否會導致環
       // 如果會導致環，則拒絕連接
       // 否則，允許連接
       // 這裡需要實現環檢測邏輯
       // 例如，使用拓撲排序檢測環
       // 假設有一個函數 `isCycleDetected`
       if (!isCycleDetected(params)) {
         setElements((els) => addEdge(params, els));
       }
     };

     return (
       <ReactFlow
         elements={elements}
         onConnect={onConnect}
       />
     );
   }
   ```

4. **雙向同步**
   實現編輯器與側邊欄藍圖樹的雙向同步：
   ```javascript
   function Flow() {
     const onElementsChange = (elements) => {
       setElements(elements);
       // 更新藍圖樹
       updateBlueprintTree(elements);
     };

     return (
       <ReactFlow
         elements={elements}
         onElementsChange={onElementsChange}
       />
     );
   }
   ```

### 2. DAG 工作流程管理與執行

#### 概述
DAG 是高效管理和執行工作流程的關鍵，優化了任務調度、資源利用和依賴管理。本節涵蓋了拓撲排序、環檢測、任務調度和執行等關鍵組件。

##### 1. DAG 拓撲排序

###### 描述
拓撲排序將 DAG 的節點排列，使得對於每條從節點 A 到節點 B 的有向邊，節點 A 在排序中位於節點 B 之前。這對於建立有效的任務執行順序至關重要。

###### 關鍵概念與步驟
1. **圖表示**：節點代表任務或實體，邊表示依賴或關係。
2. **入度計算**：計算每個節點的入度（入邊數量）。
3. **隊列初始化**：識別入度為零的節點（無依賴）並將其添加到處理隊列中。
4. **處理節點**：從隊列中移除節點，將其添加到排序列表中，並減少其鄰居的入度。如果任何鄰居的入度降至零，則將其添加到隊列中。
5. **環檢測**：如果隊列為空但並非所有節點都已處理，則存在環，無法進行拓撲排序。
6. **結果編譯**：排序列表代表 DAG 的有效拓撲順序。

###### 關鍵代碼片段（Kahn 算法）
```javascript
function kahnTopologicalSort(graph) {
  const inDegree = {}; // 存儲每個節點的入度
  const queue = [];    // 處理入度為零的節點的隊列
  const sortedOrder = []; // 存儲拓撲順序

  // 將所有節點的入度初始化為零
  graph.nodes.forEach(node => {
    inDegree[node.id] = 0;
  });

  // 計算每個節點的入度
  graph.edges.forEach(edge => {
    inDegree[edge.to] += 1;
  });

  // 將入度為零的節點添加到隊列中
  for (const nodeId in inDegree) {
    if (inDegree[nodeId] === 0) {
      queue.push(nodeId);
    }
  }

  // 處理隊列
  while (queue.length > 0) {
    const currentNodeId = queue.shift();
    sortedOrder.push(currentNodeId);

    graph.edges.forEach(edge => {
      if (edge.from === currentNodeId) {
        inDegree[edge.to] -= 1;
        if (inDegree[edge.to] === 0) {
          queue.push(edge.to);
        }
      }
    });
  }

  // 檢測環
  if (sortedOrder.length !== graph.nodes.length) {
    throw new Error("Cycle detected! Topological sort is not possible.");
  }

  return sortedOrder;
}
```

###### 常見錯誤及預防方法
- **入度計算錯誤**：未能考慮所有邊會導致排序順序不正確。確保每條邊都包含在入度計算中。
- **環檢測失敗**：未檢測到環會導致無限循環或結果不正確。始終將最終排序順序與節點數量進行比較。
- **隊列管理問題**：錯誤處理隊列會導致節點處理順序錯誤或根本未處理。確保只有當節點的入度降至零時才將其添加到隊列中。

##### 2. 任務調度與執行

###### 描述
在確定拓撲順序後，任務被調度並按順序執行，以確保所有依賴關係在任務開始前得到滿足。

###### 關鍵代碼片段
```python
def execute_tasks(sorted_tasks, execute_func):
    for task_id in sorted_tasks:
        execute_func(task_id)

# 示例用法
nodes = [{'id': 'A'}, {'id': 'B'}, {'id': 'C'}, {'id': 'D'}]
edges = [{'source': 'A', 'target': 'B'}, {'source': 'A', 'target': 'C'}, {'source