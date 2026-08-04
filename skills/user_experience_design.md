# User Experience Design

## Overview

This micro-skill focuses on enhancing the user experience through various techniques, including implementing drag and drop functionality, snapshot management for Undo/Redo operations, and applying Glassmorphism visual design principles. These elements work together to create an intuitive, visually appealing, and interactive user interface.

## Key Features

1. **Drag and Drop Functionality**: Enables users to effortlessly move workflow nodes from a sidebar to the canvas.
2. **Snapshot Management**: Captures the state of the canvas to support Undo/Redo operations, allowing users to revert or repeat actions seamlessly.
3. **Glassmorphism Visual Design**: Applies design principles such as semi-transparent backgrounds, blur effects, and gradients to create modern and visually appealing UI elements.

## Implementation Details

### Drag and Drop Functionality

#### Purpose
To facilitate the seamless movement of workflow nodes from a sidebar to the canvas, enhancing interactivity and user engagement.

#### Key Code Snippets

```javascript
const dragStart = (e, kind) => {
  e.dataTransfer.setData('application/xyflow', kind);
  e.dataTransfer.effectAllowed = 'move';
};

const drop = useCallback(e => {
  e.preventDefault();
  const kind = e.dataTransfer.getData('application/xyflow');
  if (!kind || !rf) return;
  snapshot();
  const pos = rf.screenToFlowPosition({ x: e.clientX, y: e.clientY });
  const t = TYPES[kind];
  setNodes(ns => ns.concat({
    id: crypto.randomUUID(),
    type: 'workflow',
    position: pos,
    data: { kind, label: t.label, description: t.desc }
  }));
}, [rf, setNodes, snapshot]);
```

- **`dragStart` Function**: Initializes the drag operation by setting the data type and the effect allowed.
- **`drop` Function**: Handles the drop event by preventing the default action, retrieving the dropped node type, determining its position on the canvas, and updating the node state.

#### Common Errors and Prevention

- **Error**: Dropped node does not appear on the canvas.
  - **Solution**: Ensure that the `drop` event handler correctly calls `setNodes` to update the state and that the `dataTransfer` data format is correct.

- **Error**: Node position is incorrect.
  - **Solution**: Verify the implementation of the `screenToFlowPosition` method and check the canvas coordinate system settings.

### Snapshot Management for Undo/Redo

#### Purpose
To manage snapshots of the canvas state, enabling users to undo or redo their actions seamlessly, thereby enhancing the application's reliability and user satisfaction.

#### Key Code Snippets

```javascript
const setNodes = useCallback((updater) => {
  _setNodesRaw(prev => {
    const next = typeof updater === 'function' ? updater(prev) : updater;
    const lengthChanged = next.length !== prev.length;
    const sampleChanged = next.length === 0 || prev.length === 0 || next[0] !== prev[0];
    if (lengthChanged || sampleChanged) {
      _history.current.push({
        nodes: JSON.parse(JSON.stringify(prev)),
        edges: JSON.parse(JSON.stringify(_edgesRawRef.current)),
      });
      if (_history.current.length > 50) _history.current.shift();
      _redoStack.current = [];
      bumpHistory();
    }
    return next;
  });
}, [bumpHistory]);
```

- **`setNodes` Function**: Updates the node state and manages the history stack for Undo/Redo operations.
  - **History Management**: Captures a snapshot of the current state before updating and stores it in the history stack. Limits the history stack to 50 snapshots to prevent excessive memory usage.
  - **Redo Stack**: Clears the redo stack whenever a new action is performed.

#### Common Errors and Prevention

- **Error**: Unnecessary snapshots are recorded due to internal React Flow triggers like `onNodesChange`.
  - **Solution**: Differentiate between internal calls and user-initiated actions by using separate setter functions. This prevents internal changes from being recorded as snapshots.

- **Error**: Strict reference comparison in `setNodes` leads to incorrect change detection.
  - **Solution**: Use content-based comparison (e.g., checking the length or the first node's reference) to determine if a significant change has occurred.

### Undo/Redo Functionality

#### Key Code Snippets

```javascript
const undo = useCallback(() => {
  if (_history.current.length === 0) return;
  const lastState = _history.current.pop();
  _redoStack.current.push(lastState);
  setNodes(lastState.nodes);
  setEdges(lastState.edges);
  bumpHistory();
  setLastAction('↶ 已復原');
  showToast('已復原');
}, [bumpHistory]);
```

- **`undo` Function**: Handles the undo operation by popping the last state from the history stack, pushing it to the redo stack, updating the node and edge states, and notifying the user.

#### Common Errors and Prevention

- **Error**: Using `useRef` to manage the history stack prevents re-rendering, causing the button's disabled state to not update.
  - **Solution**: Use `useState` to synchronize the history stack's length and update the state whenever changes occur to trigger re-rendering.

- **Error**: Improper management of `redoStack` and `history` during undo and redo operations.
  - **Solution**: During an undo, push the current state into the redo stack and pop the previous state from the history stack. Conversely, during a redo, push the current state into the history stack and pop the previous state from the redo stack.

### Glassmorphism Visual Design

#### Purpose
To create modern, visually appealing UI elements that enhance the overall aesthetic and user experience of the application.

#### Implementation Details

- **Semi-transparent Backgrounds**: Use CSS to create backgrounds with varying levels of transparency, allowing underlying elements to subtly show through.
- **Blur Effects**: Apply blur filters to create a sense of depth and focus on foreground elements.
- **Gradients**: Utilize CSS gradients to add dynamic and visually interesting color transitions.

#### Key Code Snippets

```css
.glassmorphism {
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 10px;
}
```

- **CSS Variables**: Use CSS variables to manage design tokens, ensuring consistency across different themes and components.

```css
:root {
  --glassmorphism-background: rgba(255, 255, 255, 0.2);
  --glassmorphism-blur: blur(8px);
  --glassmorphism-border: rgba(255, 255, 255, 0.3);
}

.glassmorphism {
  background: var(--glassmorphism-background);
  backdrop-filter: var(--glassmorphism-blur);
  -webkit-backdrop-filter: var(--glassmorphism-blur);
  border: 1px solid var(--glassmorphism-border);
  border-radius: 10px;
}
```

## Summary

By combining drag and drop functionality, snapshot management for Undo/Redo operations, and Glassmorphism visual design principles, this micro-skill provides a comprehensive approach to user experience design. It ensures that users can interact with the application intuitively while enjoying a visually pleasing and modern interface, ultimately leading to a more engaging and satisfying user experience.