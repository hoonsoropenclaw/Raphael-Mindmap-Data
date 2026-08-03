# React Flow Integration and Custom Node Design

## Overview
This micro-skill focuses on integrating the React Flow library into an HTML page to create a flowchart editor and designing custom nodes with specific styles and metadata.

## Integration of React Flow

### Explanation
React Flow is a powerful library for building interactive node-based editors and flowcharts. This section covers the steps to integrate React Flow into an HTML page using ESM importmaps, ensuring all dependencies are correctly loaded and initialized.

### Key Code Snippets and Patterns
```html
<!-- React Flow v11 + React 18 via ESM importmap -->
<script type="module">
  import React, { useState, useCallback, useMemo, useEffect, useRef } from 'https://esm.sh/react@18.3.1';
  import { createRoot } from 'https://esm.sh/react-dom@18.3.1/client';
  import ReactFlow, { Controls, MiniMap, Background } from 'https://esm.sh/reactflow@11.11.4?external=react,react-dom';

  const initialNodes = [
    {
      id: '1',
      type: 'start',
      position: { x: 250, y: 5 },
      data: { description: 'Start node' },
    },
    // ...其他初始節點
  ];

  const initialEdges = [
    { id: 'e1-2', source: '1', target: '2' },
    // ...其他初始邊
  ];

  const FlowEditor = () => {
    const [nodes, setNodes] = useState(initialNodes);
    const [edges, setEdges] = useState(initialEdges);

    const onNodesChange = useCallback((changes) => setNodes((nds) => changes.map((change) => ({ ...nds.find((n) => n.id === change.id), ...change }))), []);
    const onEdgesChange = useCallback((changes) => setEdges((eds) => changes.map((change) => ({ ...eds.find((e) => e.id === change.id), ...change }))), []);

    return (
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        fitView
      >
        <Controls />
        <MiniMap />
        <Background />
      </ReactFlow>
    );
  };

  const root = createRoot(document.getElementById('flow-root'));
  root.render(<FlowEditor />);
</script>
```

### Common Errors and Prevention
- **Error**: React Flow components are not rendering correctly.
  - **Solution**: Ensure all dependencies (React, ReactDOM, and React Flow) are loaded via the correct ESM URLs and that their versions are compatible with each other.
- **Error**: Module resolution errors in the browser console.
  - **Solution**: Verify that the importmap is correctly configured and that all module aliases match the actual loaded paths.

## Custom Node Design

### Explanation
Custom node design involves creating different types of nodes (e.g., START, TASK, APPROVAL, END) with distinct styles and metadata using React Flow's custom rendering capabilities.

### Key Code Snippets and Patterns
```javascript
const nodeTypes = {
  start: (props) => (
    <div style={{ border: '2px solid green', padding: '10px', borderRadius: '8px' }}>
      <div>START</div>
      <div>{props.data.description}</div>
    </div>
  ),
  task: (props) => (
    <div style={{ border: '2px solid blue', padding: '10px', borderRadius: '8px' }}>
      <div>TASK</div>
      <div>{props.data.title}</div>
    </div>
  ),
  approval: (props) => (
    <div style={{ border: '2px solid orange', padding: '10px', borderRadius: '8px' }}>
      <div>APPROVAL</div>
      <div>{props.data.status}</div>
    </div>
  ),
  end: (props) => (
    <div style={{ border: '2px solid red', padding: '10px', borderRadius: '8px' }}>
      <div>END</div>
      <div>{props.data.result}</div>
    </div>
  ),
  // 其他節點類型...
};

const FlowEditor = () => {
  // ...之前的代碼

  return (
    <ReactFlow
      nodes={nodes}
      edges={edges}
      onNodesChange={onNodesChange}
      onEdgesChange={onEdgesChange}
      nodeTypes={nodeTypes}
      fitView
    >
      <Controls />
      <MiniMap />
      <Background />
    </ReactFlow>
  );
};
```

### Common Errors and Prevention
- **Error**: Custom nodes are not displaying correctly.
  - **Solution**: Ensure that the keys in the `nodeTypes` object match the node types used in React Flow, and that each custom rendering function returns a valid React element.
- **Error**: Metadata is not displaying.
  - **Solution**: Confirm that the `data` property of the node contains the necessary metadata and that the custom rendering function correctly accesses this data.

## Summary
By following the guidelines and code snippets provided in this micro-skill, you can successfully integrate React Flow into your HTML page and design custom nodes with unique styles and metadata, enabling the creation of dynamic and interactive flowchart editors.