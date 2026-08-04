# Workflow and Minutes Management

## Overview
This micro-skill focuses on managing workflows using React Flow for visual process representation and implementing a structured pattern for organizing and managing meeting minutes and notes.

## React Flow Workflow Management

### Purpose
Utilize the React Flow library to render and manage workflow diagrams, including custom node types, connection logic, and user interaction features.

### Key Code Snippets and Patterns
- **Initialize the Canvas**: Use the `ReactFlow` component to set up the workflow canvas.
  ```javascript
  import React from 'react';
  import ReactFlow from 'react-flow-renderer';

  const initialNodes = [];
  const initialEdges = [];

  function WorkflowCanvas() {
      return <ReactFlow nodes={initialNodes} edges={initialEdges} />;
  }

  export default WorkflowCanvas;
  ```
- **Custom Node Types**: Define custom node types, such as `WorkflowNode`, and inject them via the `nodeTypes` property.
  ```javascript
  import ReactFlow, { MiniMap, Controls } from 'react-flow-renderer';
  import WorkflowNode from './WorkflowNode';

  const nodeTypes = { workflowNode: WorkflowNode };

  function WorkflowCanvas() {
      return (
          <ReactFlow 
              nodeTypes={nodeTypes} 
              nodes={initialNodes} 
              edges={initialEdges} 
              >
              <Controls />
              <MiniMap />
          </ReactFlow>
      );
  }
  ```
- **State Management**: Use `useNodesState` and `useEdgesState` hooks to manage the state of nodes and edges.
  ```javascript
  import React from 'react';
  import { useNodesState, useEdgesState } from 'reactflow';

  function WorkflowCanvas() {
      const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
      const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

      return (
          <ReactFlow 
              nodes={nodes} 
              edges={edges} 
              onNodesChange={onNodesChange} 
              onEdgesChange={onEdgesChange}
              >
              <Controls />
              <MiniMap />
          </ReactFlow>
      );
  }
  ```
- **User Interactions**: Implement drag-and-drop, selection, and editing functionalities for nodes.
  ```javascript
  // Example: Adding a new node on drag end
  function onDragOver(event) {
      event.preventDefault();
      event.dataTransfer.dropEffect = 'move';
  }

  function onDrop(event) {
      const position = getPosition(event);
      const newNode = { id: 'new-id', position, type: 'workflowNode', data: { label: 'New Node' } };
      setNodes((nodes) => [...nodes, newNode]);
  }
  ```

### Common Errors and How to Avoid Them
- **Error**: Custom nodes do not correctly receive data.
  - **Solution**: Ensure that custom nodes receive data through the `data` attribute rather than props.
- **Error**: Node icons or styles are not displaying correctly.
  - **Solution**: Verify that the `nodeTypes` definition is correct and that the data structure matches expectations.

## Minutes Pattern

### Purpose
This micro-skill outlines the architecture pattern for a real-time meeting minutes system, including recording, transcription, scheduling, concurrency management, API calls, timeline rendering, and export functionalities.

### Key Code Snippets and Patterns
- **MediaRecorder with Chunk Scheduling**: Implement `MediaRecorder` to handle audio chunks and scheduling.
  ```javascript
  const mediaRecorder = new MediaRecorder(stream);
  const chunks = [];

  mediaRecorder.ondataavailable = (e) => {
      chunks.push(e.data);
      if (recording) {
          setTimeout(() => requestData(), chunkInterval);
      }
  };

  mediaRecorder.start();

  function requestData() {
      mediaRecorder.requestData();
  }
  ```
- **Error Handling**: Use asynchronous error handling to manage transcription failures.
  ```javascript
  async function transcribeAudio() {
      try {
          const transcription = await transcribe(chunks);
          updateTranscript(transcription);
      } catch (error) {
          console.error('Transcription failed:', error);
          handleTranscriptionError(error);
      }
  }
  ```

### Common Errors and How to Avoid Them
- **Error**: Recording interruptions or pauses are not handled, leading to data loss.
  - **Solution**: Save the current state when recording is paused and resume from the saved state when recording resumes.
- **Error**: Transcription failures are not properly handled, causing the system to crash.
  - **Solution**: Implement asynchronous error handling to capture and manage transcription errors gracefully.

## Summary
By integrating React Flow for workflow visualization and adopting a structured pattern for managing meeting minutes, this micro-skill ensures efficient workflow management and reliable meeting documentation. Careful attention to error handling and state management is crucial for maintaining system stability and data integrity.