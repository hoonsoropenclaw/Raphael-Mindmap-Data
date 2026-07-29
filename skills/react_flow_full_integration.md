# React Flow Full Integration

## Overview

### Purpose
This skill comprehensively integrates React Flow, leveraging both the UMD bundle and advanced features to create dynamic and interactive user interfaces for workflow visualization and management.

### Key Techniques and Patterns

#### Node Type Definition
- **Implementation**: Define various node types using React Flow's node type definition feature to represent different workflow components.
- **Example**:
  ```javascript
  const nodeTypes = {
    input: InputNode,
    output: OutputNode,
    // Add more node types as needed
  };
  ```

#### Execution State Machine
- **Implementation**: Develop a state machine to manage node execution states such as "waiting," "running," and "completed."
- **Example**:
  ```javascript
  const [nodes, setNodes] = useState(initialNodes);
  const [edges, setEdges] = useState(initialEdges);

  const updateNodeState = (id, state) => {
    setNodes((prevNodes) =>
      prevNodes.map((node) =>
        node.id === id ? { ...node, data: { ...node.data, state } } : node
      )
    );
  };
  ```

#### Persistence
- **Implementation**: Save and restore the workflow state using backend databases or local storage to ensure data persistence across sessions.
- **Example**:
  ```javascript
  const saveState = () => {
    localStorage.setItem('workflowState', JSON.stringify({ nodes, edges }));
  };

  const loadState = () => {
    const state = JSON.parse(localStorage.getItem('workflowState'));
    if (state) {
      setNodes(state.nodes);
      setEdges(state.edges);
    }
  };
  ```

### Common Errors and Prevention

- **Node Type Conflicts**: Carefully design and test node types to prevent conflicts that can cause workflow malfunctions.
- **State Machine Errors**: Use clear state transition rules and conduct extensive testing to avoid state machine-related issues such as workflows getting stuck or entering incorrect states.
- **Persistence Failures**: Implement data validation and backup mechanisms to prevent data loss or corruption during the persistence process.

## Viewport Control

### Description
Utilize React Flow's viewport control features to automatically adjust the canvas's zoom and pan, ensuring all nodes are correctly displayed within the viewport.

### Key Code Snippets and Patterns
```javascript
// Automatically adjust the viewport to fit all nodes
const doFit = () => {
  const btns = document.querySelectorAll('.react-flow__controls-fitview');
  if (btns.length > 0) {
    btns[0].click();
    return;
  }
  if (reactFlowRef.current && reactFlowRef.current.setViewport) {
    const zoom = 0.46;
    const tx = (620 - 1140 * zoom) / 2;
    const ty = (521 - 640 * zoom) / 2;
    reactFlowRef.current.setViewport({ x: tx, y: ty, zoom });
  }
};
```

### Common Errors and Prevention

- **Error**: Nodes are still clipped after viewport adjustment.
  - **Solution**: Verify the accuracy of the calculated zoom ratio and displacement values, and consider the actual size of the canvas and the boundaries of the nodes.
- **Error**: Viewport control buttons are not found or cannot be clicked.
  - **Solution**: Use appropriate selectors and ensure that the buttons are loaded before performing operations.

## Node Transformation

### Description
Control the position and animation effects of nodes using CSS transformations to enable custom layouts and interactive effects.

### Key Code Snippets and Patterns
```css
.react-flow__node {
  transform: translate(0, 40px);
}
```

### Common Errors and Prevention

- **Error**: Node positions do not match expectations.
  - **Solution**: Check for transformations on parent elements that may affect child nodes and ensure the correct transformation order.
- **Error**: Node animation effects are not smooth.
  - **Solution**: Use CSS transition or animation properties and ensure that transformation properties are correctly set.

## MiniMap Positioning

### Description
Adjust the position and size of the MiniMap to prevent it from obstructing the main content on the canvas.

### Key Code Snippets and Patterns
```css
.react-flow__minimap {
  position: absolute;
  bottom: 16px;
  right: 16px;
  width: 180px;
  height: 120px;
  z-index: 5;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4);
}
```

### Common Errors and Prevention

- **Error**: MiniMap obstructs important nodes on the canvas.
  - **Solution**: Adjust the position and size of the MiniMap or relocate it to a different area of the canvas.
- **Error**: MiniMap size is too large or too small.
  - **Solution**: Modify the width and height of the MiniMap according to the actual size of the canvas and user requirements.

## Control Panel Styling

### Description
Customize the styling of the React Flow control panel, including its position, size, shadow, and border, to enhance the user experience and interface aesthetics.

### Key Code Snippets and Patterns
```css
.react-flow__controls {
  position: absolute;
  bottom: 16px;
  left: 16px;
  width: 30px;
  height: 120px;
  z-index: 5;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4);
}
```

### Common Errors and Prevention

- **Error**: Control panel position is incorrect or obscured by other elements.
  - **Solution**: Use absolute positioning and set an appropriate z-index.
- **Error**: Control panel size is too large or too small.
  - **Solution**: Adjust the width and height of the control panel according to the size of the canvas and user needs.

## UMD Bundle Integration

### Description
Integrate React Flow into an HTML project using the UMD bundle by loading the script and correctly accessing the global variables.

### Key Code Snippets and Patterns
```html
<!-- React Flow v12 UMD bundle -->
<script src="https://unpkg.com/@xyflow/react@12.3.5/dist/umd/index.js"></script>

<script type="text/babel">
  const _RFNS = (window.ReactFlow && (window.ReactFlow.ReactFlow ? window.ReactFlow : window.ReactFlow.default)) || {};
  const ReactFlow = _RFNS.ReactFlow || (() => null);
  const ReactFlowProvider = _RFNS.ReactFlowProvider || (({children}) => children);
  // ...other destructuring
</script>
```

### Common Errors and Prevention

- **Error**: Attempting to use destructuring directly from `window.ReactFlow` to access submodules, but the UMD bundle actually exposes submodules as `window.ReactFlow.ReactFlow`.
  - **Solution**: First check if `window.ReactFlow` exists, then correctly access submodules, for example, `window.ReactFlow.ReactFlow`.

## Conclusion
By integrating these advanced features and correctly setting up the UMD bundle, you can create a robust and visually appealing React Flow application that offers precise control over the viewport, nodes, MiniMap, and control panel, ensuring a seamless user experience.