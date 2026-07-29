# ReactFlow UMD Integration

## 說明...
整合 ReactFlow 11 的 UMD bundle 需要載入多個子套件（core、background、controls、minimap），並從各自的全局變數中提取所需的組件。

## 關鍵代碼片段或模式
```html
<!-- React Flow 11 (UMD) -->
<script src="https://unpkg.com/@reactflow/core@11.11.4/dist/umd/index.js"></script>
<script src="https://unpkg.com/@reactflow/background@11.11.4/dist/umd/index.js"></script>
<script src="https://unpkg.com/@reactflow/controls@11.11.4/dist/umd/index.js"></script>
<script src="https://unpkg.com/@reactflow/minimap@11.11.4/dist/umd/index.js"></script>

<script type="text/javascript">
  const RF = window.ReactFlowCore;
  const RFB = window.ReactFlowBackground;
  const RFC = window.ReactFlowControls;
  const RFM = window.ReactFlowMinimap;

  if (!RF || !RFB || !RFC || !RFM) {
    document.getElementById('root').innerHTML = '❌ ReactFlow UMD missing';
    throw new Error('ReactFlow UMD missing');
  }

  const {
    ReactFlow, ReactFlowProvider, Handle, Position, Panel,
    useNodesState, useEdgesState, addEdge, useReactFlow,
  } = RF;
  const Background = RFB.Background;
  const Controls = RFC.Controls;
  const MiniMap = RFM.MiniMap;

  // 你的應用程式代碼...
</script>