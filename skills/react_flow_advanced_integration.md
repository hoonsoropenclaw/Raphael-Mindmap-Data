# Advanced Integration of React Flow in Single-Page Applications

## Overview

### Target Skill Name
`react_flow_advanced_integration`

### Summary
Integrate the UMD version of React Flow into a single-page application (SPA), develop custom Controls components, and configure a Zustand store to manage application state effectively.

---

## 1. React Flow UMD Integration

### Purpose
Integrate the React Flow library into an SPA using the UMD (Universal Module Definition) version. This approach simplifies the setup by avoiding complex module bundling processes.

### Key Implementation Details

#### HTML Setup
Include the necessary UMD scripts for React, ReactDOM, and React Flow in your HTML file.

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>React Flow UMD Integration</title>
</head>
<body>
  <div id="root"></div>

  <!-- React -->
  <script src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
  <script src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>

  <!-- React Flow -->
  <script src="https://unpkg.com/@reactflow/core@11.11.4/dist/umd/index.js"></script>

  <!-- Your Application Script -->
  <script>
    // Access React Flow from the global scope
    const ReactFlow = window.ReactFlow;

    // Initialize React Flow components here
    const root = document.getElementById('root');

    const elements = {
      nodes: [],
      edges: [],
    };

    const App = () => (
      <ReactFlowProvider>
        <ReactFlow
          elements={elements}
          onNodesChange={(changes) => console.log('Nodes changed', changes)}
          onEdgesChange={(changes) => console.log('Edges changed', changes)}
        />
      </ReactFlowProvider>
    );

    ReactDOM.createRoot(root).render(<App />);
  </script>
</body>
</html>
```

### Common Errors and Prevention

- **Error**: React Flow throws an error stating it cannot find the Zustand provider.
  - **Solution**: Ensure that the versions of React Flow and Zustand are compatible. Verify that the React Flow Provider is correctly wrapping the entire application.

- **Error**: Conflicts between UMD and ESM versions.
  - **Solution**: Avoid mixing UMD and ESM versions within the same application. Choose one approach for integration to prevent conflicts.

---

## 2. Custom Controls Component Development

### Purpose
Develop custom Controls components to extend React Flow's functionality, such as adding nodes, editing properties, or performing other interactive operations.

### Key Implementation Details

#### Creating a Custom Controls Component
Use the `useReactFlow` hook to access the React Flow instance and implement custom logic.

```jsx
import React from 'react';
import { useReactFlow } from 'react-flow';

const CustomControls = () => {
  const reactFlowInstance = useReactFlow();

  // Custom logic to add a node
  const onAddNode = () => {
    const position = reactFlowInstance.project({ x: 0, y: 0 });
    reactFlowInstance.addNodes([{
      id: 'new-node',
      position,
      data: { label: 'New Node' },
    }]);
  };

  return (
    <div style={{ position: 'absolute', right: 10, top: 10, zIndex: 4 }}>
      <button onClick={onAddNode}>Add Node</button>
    </div>
  );
};

export default CustomControls;
```

#### Integrating the Custom Controls Component
Wrap the `CustomControls` component within the `ReactFlowProvider` to ensure it has access to the React Flow instance.

```jsx
import React from 'react';
import ReactDOM from 'react-dom';
import { ReactFlowProvider } from 'react-flow';
import CustomControls from './CustomControls';

const App = () => (
  <ReactFlowProvider>
    <ReactFlow
      elements={elements}
      onNodesChange={(changes) => console.log('Nodes changed', changes)}
      onEdgesChange={(changes) => console.log('Edges changed', changes)}
    />
    <CustomControls />
  </ReactFlowProvider>
);

ReactDOM.createRoot(document.getElementById('root')).render(<App />);
```

### Common Errors and Prevention

- **Error**: The Controls component cannot access the React Flow instance.
  - **Solution**: Use the `useReactFlow` hook to obtain the React Flow instance within the Controls component.

- **Error**: The Controls component is not positioned correctly.
  - **Solution**: Ensure that the Controls component is correctly wrapped within the React Flow Provider and positioned appropriately in the component tree. Use CSS styles to control the placement (e.g., absolute positioning).

---

## 3. Zustand Store Configuration

### Purpose
Configure a Zustand store to manage the state of React Flow, including nodes, edges, and application-level states. This ensures efficient state management and synchronization with React Flow.

### Key Implementation Details

#### Setting Up the Zustand Store
Create a Zustand store to manage nodes and edges.

```javascript
import create from 'zustand';
import { useStore } from 'react-flow';

const useCustomStore = create((set) => ({
  nodes: [],
  edges: [],
  addNode: (node) => set((state) => ({ nodes: [...state.nodes, node] })),
  addEdge: (edge) => set((state) => ({ edges: [...state.edges, edge] })),
}));

// Example usage in a component
const NodesUpdater = () => {
  const nodes = useCustomStore((state) => state.nodes);
  const addNode = useCustomStore((state) => state.addNode);

  const onAddNode = () => {
    const newNode = { id: 'node-1', position: { x: 0, y: 0 }, data: { label: 'Node 1' } };
    addNode(newNode);
  };

  return <button onClick={onAddNode}>Add Node</button>;
};
```

#### Integrating with React Flow
Synchronize the Zustand store with React Flow by passing the store's state and event handlers.

```jsx
import React from 'react';
import ReactDOM from 'react-dom';
import { ReactFlowProvider, ReactFlow } from 'react-flow';
import useCustomStore from './zustandStore';

const App = () => {
  const nodes = useCustomStore((state) => state.nodes);
  const edges = useCustomStore((state) => state.edges);
  const addNode = useCustomStore((state) => state.addNode);
  const addEdge = useCustomStore((state) => state.addEdge);

  const onNodesChange = (changes) => {
    // Update Zustand store based on node changes
    changes.forEach((change) => {
      if (change.type === 'add') {
        addNode(change.node);
      }
      // Handle other types of changes as needed
    });
  };

  const onEdgesChange = (changes) => {
    // Update Zustand store based on edge changes
    changes.forEach((change) => {
      if (change.type === 'add') {
        addEdge(change.edge);
      }
      // Handle other types of changes as needed
    });
  };

  return (
    <ReactFlowProvider>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
      />
    </ReactFlowProvider>
  );
};

ReactDOM.createRoot(document.getElementById('root')).render(<App />);
```

### Common Errors and Prevention

- **Error**: The Zustand store and React Flow states are not synchronized.
  - **Solution**: Ensure that event handlers for React Flow events correctly update the Zustand store. Use the `useCustomStore` hook to access and update the store's state.

- **Error**: The Zustand store is not initialized correctly.
  - **Solution**: Verify that the store is properly configured and initialized before the application starts. Ensure that all necessary state updates are handled within the store.

---

## Summary

By following the above guidelines, you can effectively integrate React Flow's UMD version into your SPA, develop custom Controls components, and configure a Zustand store for robust state management. This setup ensures a seamless and efficient development experience, allowing you to leverage the full power of React Flow in your projects.