# React Flow Comprehensive Integration

## Overview
The `react_flow_comprehensive_integration` skill focuses on the complete integration of React Flow into a React application. This includes dynamic state management, UMD environment integration, stabilization of custom node types, debugging edge rendering, and adjusting the positioning and styling of views and panels.

## Key Components

### 1. Dynamic State Management
Managing the dynamic states of nodes and edges is crucial for reflecting real-time changes in the UI.

#### Key Code Snippets
```javascript
const computedEdges = useMemo(() => {
  return edges.map(edge => ({
    ...edge,
    className: edgeStatusMapping[edge.status],
  }));
}, [edges]);

const FlowStepNode = ({ id, data, selected }) => (
  <div className={`flow-node ${data.status}`}>
    <div className="fn-title">{data.label}</div>
    <div className="fn-meta">
      {canWrite(currentRole, id) ? '可操作' : '只讀'}
    </div>
    {/* 其他內容... */}
  </div>
);
```

#### Common Errors and Solutions
- **Error**: Incorrect state update logic leading to UI not reflecting the state correctly.
  - **Solution**: Ensure the state update function correctly handles node and edge states and use `useMemo` for optimized computations.
- **Error**: Node components not receiving state properties correctly, causing rendering issues.
  - **Solution**: Verify that node components receive the correct props and include all necessary state attributes.

### 2. UMD Environment Integration
Integrating React Flow in a non-modular HTML environment using UMD involves handling JSX and module dependencies.

#### Key Code Snippets
```javascript
// Using Babel to transform JSX into React.createElement
const transformedCode = Babel.transform(code, { presets: [['react', {runtime: 'classic'}]] }).code;
const run = new Function('React', 'ReactDOM', 'ReactFlow', transformedCode);
run(window.React, window.ReactDOM, window.ReactFlow);
```

#### Common Errors and Solutions
- **Error**: Babel's automatic runtime conflicts with the UMD environment, causing the `jsx` function to be undefined.
  - **Solution**: Use the classic runtime and ensure Babel configuration is correct.
- **Error**: Incorrect UMD entry path for React Flow, leading to loading failures.
  - **Solution**: Use the correct UMD entry path, such as `dist/umd/index.js` instead of `dist/index.umd.min.js`.

### 3. Stabilizing Custom Node Types
When using custom node types, it's essential to ensure that the node type references remain stable to prevent React Flow from resetting internal states.

#### Key Code Snippets
```javascript
const RBACNode = ({ data }) => {
  // Node rendering logic
};

const nodeTypes = useMemo(() => ({ rbac: RBACNode }), []);

// Using nodeTypes in React Flow
<ReactFlow nodeTypes={nodeTypes} ... />
```

#### Common Errors and Solutions
- **Error**: Custom node types are recreated on every render, causing React Flow to think the node type has changed.
  - **Solution**: Use `useMemo` to stabilize the node type references.
- **Error**: Node type definitions are inside the component, leading to recreation on every render.
  - **Solution**: Define node types outside the component or use `useMemo` to stabilize the references.

### 4. Debugging Edge Rendering
Ensuring edges are rendered correctly and connect the intended nodes is vital for the flow's integrity.

#### Key Code Snippets
```javascript
// Check if edge data is correct
console.log('Edges:', edges);

// Inspect React Flow internal state
console.log('Node Internals:', nodeInternals);

// Verify edges are connected to the correct nodes
const sourceNode = nodeInternals.get(edge.source);
const targetNode = nodeInternals.get(edge.target);
console.log('Source Node:', sourceNode, 'Target Node:', targetNode);
```

#### Common Errors and Solutions
- **Error**: The `source` or `target` of an edge points to a non-existent node.
  - **Solution**: Ensure all edges have `source` and `target` that point to existing nodes.
- **Error**: Edge type is not registered or loaded correctly.
  - **Solution**: Confirm that the edge type is registered and loaded, using built-in edge types or ensuring custom edge types are correctly implemented.
- **Error**: `sourceHandle` or `targetHandle` is not set correctly.
  - **Solution**: Verify that `sourceHandle` and `targetHandle` are set correctly or use edge types that do not require handles.

### 5. Viewport and Panel Positioning and Styling
Adjusting the positioning and styling of views and panels ensures the UI meets specific design and functional requirements.

#### Key Code Snippets for MiniMap Positioning
```css
.react-flow__panel.react-flow__minimap {
  background: var(--bg-elev) !important;
  border: 1px solid var(--line) !important;
  bottom: 16px !important;
  right: 16px !important;
  width: 200px !important;
  height: 150px !important;
  top: auto !important;
  left: auto !important;
}
.react-flow__panel.react-flow__minimap svg {
  width: 100% !important;
  height: 100% !important;
}
```

#### Key Code Snippets for Control Panel Positioning
```css
.react-flow__panel {
  position: absolute !important;
  z-index: 5;
}
.react-flow__panel.react-flow__controls {
  bottom: 16px !important;
  left: 16px !important;
  top: auto !important;
  right: auto !important;
  flex-direction: column !important;
}
.react-flow__panel.react-flow__controls .react-flow__controls-button {
  border-right: 0 !important;
  border-bottom: 1px solid var(--line) !important;
}
.react-flow__panel.react-flow__controls .react-flow__controls-button:last-child {
  border-bottom: 0 !important;
}
```

#### Common Errors and Solutions
- **Error**: MiniMap or control panel position is incorrect, displaying in the wrong place.
  - **Solution**: Ensure the parent container has `position: relative` and the CSS for MiniMap or control panel sets the correct `top`, `bottom`, `left`, `right` properties.
- **Error**: Width and height of MiniMap or control panel are overridden by other CSS rules.
  - **Solution**: Use the `!important` flag to enforce width and height settings.

### 6. Viewport Centering
Centering the viewport on a specific node or area ensures that the focus is on the intended part of the flow.

#### Key Code Snippets
```javascript
const bbox = { x: 40, y: 80, w: 1180, h: 360 }; // Bounding box of the target area
const padding = 60;
const wrap = reactFlowWrapper.current?.getBoundingClientRect();
if (wrap) {
  const scale = Math.min((wrap.width  - padding*2) / bbox.w, (wrap.height - padding*2) / bbox.h);
  const cx = bbox.x + bbox.w/2, cy = bbox.y + bbox.h/2;
  const tx = wrap.width/2  - cx * scale;
  const ty = wrap.height/2 - cy * scale;
  reactFlow.setViewport({ x: tx, y: ty, zoom: scale }, { duration: 350 });
}
```

#### Common Errors and Solutions
- **Error**: Viewport does not center correctly, nodes are offset.
  - **Solution**: Confirm that the `bbox` calculation is correct and that the `wrap` dimensions are accurately obtained.
- **Error**: Zoom scale causes nodes to be over- or under-scaled.
  - **Solution**: Adjust the `scale` calculation to ensure it stays within a reasonable range.

### 7. Overriding Node Sizes
React Flow has default CSS settings for node sizes, such as `min-width: 150px`. To meet specific needs, these settings must be overridden through custom CSS.

#### Key Code Snippets
```css
.react-flow__node {
  /* Override RF default 150px min-width and avoid width: max-content stretching */
  width: auto !important;
  min-width: 0 !important;
  padding: 0 !important;
  border: 0 !important;
  background: transparent !important;
}
.node {
  background: var(--bg-elev);
  border: 1px solid var(--line-2);
  border-radius: var(--radius);
  padding: 10px 12px;
  min-width: 180px;
  max-width: 240px;
  box-shadow: var(--shadow);
  color: var(--ink);
  font-family: var(--sans);
}
```

#### Common Errors and Solutions
- **Error**: Custom CSS does not override React Flow's default settings.
  - **Solution**: Use more specific selectors or the `!important` flag to enforce custom styles.
- **Error**: Node size settings are unreasonable, causing layout issues.
  - **Solution**: Adjust the `min-width` and `max-width` values according to actual needs to ensure node sizes are appropriate.

### 8. Panel Positioning
The control panels (such as MiniMap and Controls) may not have default positions that meet the requirements, necessitating the use of CSS to enforce their positions.

#### Key Code Snippets
```css
.react-flow__panel {
  position: absolute !important;
  z-index: 5;
}
.react-flow__panel.react-flow__controls {
  bottom: