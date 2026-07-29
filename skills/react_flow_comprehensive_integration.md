# React Flow Comprehensive Integration

## Overview
This micro-skill document provides a comprehensive guide for integrating React Flow into your project, including UMD integration, custom node types, Inspector component integration, and JSON export functionality.

## 1. React Flow UMD Integration

### Description
Integrate the UMD version of React Flow 11 into an HTML document. This includes importing the necessary CSS and JS files and setting up the React Flow rendering environment.

### Key Code Snippets and Patterns
```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reactflow@11.11.4/dist/style.css" />
<script crossorigin src="https://unpkg.com/react@18/umd/react.development.js"></script>
<script crossorigin src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>
<script crossorigin src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
<script>
  Babel.registerPreset('react-classic', {
    presets: [[Babel.availablePresets['react'], { runtime: 'classic' }]]
  });
</script>
<script src="https://cdn.jsdelivr.net/npm/reactflow@11.11.4/dist/umd/index.min.js"></script>
```

### Common Errors and Prevention
- **Error**: React Flow rendering fails with the message 'Element type is invalid'.
  - **Solution**: Ensure that the versions of React and ReactDOM are compatible with React Flow, such as using React 18.
- **Error**: Babel automatic JSX runtime causes errors.
  - **Solution**: Switch to the classic JSX runtime by manually registering the preset using `Babel.registerPreset`.
- **Error**: UMD version of React Flow does not support certain features in some environments.
  - **Solution**: Consult the React Flow official documentation to ensure that the desired features are supported in the UMD version.

## 2. Custom Node Types Definition

### Description
Define custom node types (e.g., Trigger, HTTP, Condition, Loop, Output) and integrate them into React Flow to support customized workflow nodes.

### Key Code Snippets and Patterns
```javascript
const NODE_TYPES = {
  trigger: TriggerNode,
  http: HttpNode,
  condition: ConditionNode,
  loop: LoopNode,
  output: OutputNode,
};

function TriggerNode({ id, data, ...props }) {
  return (
    <div data-id={id} style={{ background: '#ff4d4f', color: '#fff', padding: '10px', borderRadius: '5px' }}>
      {data.label}
    </div>
  );
}
```

### Common Errors and Prevention
- **Error**: Custom nodes do not render correctly.
  - **Solution**: Ensure that each node type in the `nodeTypes` object correctly references the corresponding React component.
- **Error**: Node properties are passed incorrectly.
  - **Solution**: Check the props passed to the custom nodes to ensure they include necessary attributes such as `id`, `data`, and `position`.
- **Error**: Node styles do not take effect.
  - **Solution**: Ensure that the style definitions for the custom nodes are correct and check for any CSS conflicts.

## 3. Inspector Component Integration

### Description
Integrate the Inspector component to edit the properties of the selected node, including adding, deleting, and modifying node attributes.

### Key Code Snippets and Patterns
```javascript
function Inspector({ selectedNode, onUpdateNode }) {
  if (!selectedNode) return null;
  return (
    <div className="inspector">
      <h2>Inspector</h2>
      <label>
        Label:
        <input
          type="text"
          value={selectedNode.data.label}
          onChange={(e) => onUpdateNode({ ...selectedNode, data: { ...selectedNode.data, label: e.target.value } })}
        />
      </label>
      {/* Other property edits */}
    </div>
  );
}
```

### Common Errors and Prevention
- **Error**: Inspector does not display the selected node properties correctly.
  - **Solution**: Ensure that `selectedNode` is passed correctly and check the rendering logic of the Inspector component.
- **Error**: Properties do not update after editing.
  - **Solution**: Ensure that the `onUpdateNode` function is correctly implemented and called when properties change.
- **Error**: Inspector styles do not take effect.
  - **Solution**: Check the style definitions of the Inspector component to ensure that style attributes are applied correctly and check for any CSS conflicts.

## 4. JSON Export Functionality

### Description
Implement JSON export functionality for the workflow, serializing the current workflow state to JSON and providing a download option.

### Key Code Snippets and Patterns
```javascript
function exportJson() {
  const workflow = {
    nodes: nodes.map((node) => ({ ...node, position: { x: node.position.x, y: node.position.y } })),
    edges: edges.map((edge) => ({ ...edge, source: edge.source, target: edge.target })),
  };
  const json = JSON.stringify(workflow, null, 2);
  const blob = new Blob([json], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = 'workflow.json';
  link.click();
  URL.revokeObjectURL(url);
}
```

### Common Errors and Prevention
- **Error**: JSON export fails.
  - **Solution**: Check the implementation of the `exportJson` function to ensure that node and edge data are correctly serialized.
- **Error**: The downloaded file content is incorrect.
  - **Solution**: When using `JSON.stringify`, ensure that the second parameter is `null` and the third parameter is `2` to format the output.
- **Error**: The downloaded file cannot be opened.
  - **Solution**: Ensure that the MIME type is set to `application/json` and check that the filename is correct.

## Conclusion
By following this guide, you can effectively integrate React Flow into your project, define and manage custom node types, utilize the Inspector component for node property management, and implement JSON export functionality for workflow serialization.