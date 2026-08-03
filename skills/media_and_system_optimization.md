# Micro-Skill: Media and System Optimization

## Target Skill Name
media_and_system_optimization

## Summary
This micro-skill focuses on optimizing system performance through efficient media and data management techniques. It integrates robust system management, workflow optimization, change management, and advanced request interception to create a resilient, high-performance system. The skill encompasses real-time media processing, asynchronous communication, secure web scraping, data deduplication, normalization, and adherence to Standard Operating Procedures (SOPs).

---

## 1. Robust System Management

### 1.1 Robust I/O Handling and Error Optimization

#### 1.1.1 Console Error Interception
- **Overview**: Intercept and log browser console errors and warnings to capture issues in test reports for better debugging.
- **Key Code Snippet**:
  ```python
  # Intercept console errors and warnings
  page.on('console', lambda m: logger.error(f'Console error: {m.text}') if m.type == 'error' else None)
  page.on('pageerror', lambda e: logger.error(f'Page error: {e}'))
  ```
- **Common Errors and Solutions**:
  - **Console errors not intercepted**: Ensure all console event types are listened to and enable detailed error reporting.
  - **Error information not recorded correctly**: Implement a unified logging mechanism with detailed error information in test reports.

#### 1.1.2 Event Handling with Debouncing
- **Overview**: Efficiently handle filesystem events by combining the `watchdog` library with debouncing to monitor events like creation, modification, and movement, processing them in batches to prevent system overload.
- **Watchdog Event Handler**:
  ```python
  from watchdog.observers import Observer
  from watchdog.events import FileSystemEventHandler

  class WatchdogHandler(FileSystemEventHandler):
      def __init__(self, debouncer):
          self.debouncer = debouncer

      def on_created(self, event):
          if not event.is_directory:
              self.debouncer.push(event.src_path)

      def on_modified(self, event):
          if not event.is_directory:
              self.debouncer.push(event.src_path)

      def on_moved(self, event):
          if not event.is_directory:
              self.debouncer.push(event.dest_path)
  ```
- **Debouncer for Event Merging**:
  ```python
  import time
  from threading import Thread

  class Debouncer:
      def __init__(self, debounce_seconds: float, callback):
          self.debounce_seconds = debounce_seconds
          self.callback = callback
          self.queue = set()
          self.thread = Thread(target=self._process_queue, daemon=True)
          self.thread.start()

      def push(self, item):
          self.queue.add(item)

      def _process_queue(self):
          while True:
              time.sleep(self.debounce_seconds)
              if self.queue:
                  items = list(self.queue)
                  self.queue.clear()
                  self.callback(items)
  ```
- **Integration of Watchdog and Debouncer**:
  ```python
  def main():
      watch_directory = "/path/to/watch"
      debounce_seconds = 1.0
      def event_callback(items):
          print(f"Received events: {items}")

      debouncer = Debouncer(debounce_seconds, event_callback)
      observer = start_watchdog(watch_directory, debouncer)

      try:
          while True:
              time.sleep(1)
      except KeyboardInterrupt:
          observer.stop()
          observer.join()
  ```
- **Common Errors and Prevention**:
  - **Watchdog-related errors**: Verify `watchdog` library version and consult documentation for adjustments.
  - **Debouncer-related errors**: Ensure callback function is optimized for quick execution; for time-consuming operations, run the callback in a separate thread or use asynchronous processing.

#### 1.1.3 Best Practices for Avoiding Blocking I/O in Asynchronous Environments
- **Use Asynchronous Libraries**: Utilize libraries like `asyncio` for asynchronous I/O operations.
- **Non-Blocking I/O Operations**: Implement non-blocking I/O to prevent blocking the event loop.
- **Thread Pools and Process Pools**: Use thread or process pools for CPU-bound tasks.
- **Timeouts and Retries**: Implement timeouts and retry mechanisms for transient failures.
- **Key Code Snippet**:
  ```python
  import asyncio

  async def non_blocking_io_operation():
      reader, writer = await asyncio.open_connection('localhost', 8080)
      data = await reader.read(100)
      print(f'Received: {data.decode()}')
      writer.close()
      await writer.wait_closed()

  async def main():
      await non_blocking_io_operation()

  asyncio.run(main())
  ```

### 1.2 Robust Task Management with RBAC

#### 1.2.1 Prompt Injection and Fake Authority Detection
- **Description**: Identifies and mitigates forged system-level instructions that may compromise system integrity.
- **Key Code Snippets and Patterns**:
  ```javascript
  if (message.includes("[SYSTEM_HEARTBEAT]") && is_via_user_channel(message)) {
      flag_as_potential_prompt_injection();
      trigger_security_protocol();
  }
  ```
- **Common Errors and Prevention**:
  - **Misidentifying legitimate instructions**: Ensure credibility through cryptographic signatures or dedicated verification channels.
  - **Overlooking genuine attacks**: Implement multi-layered detection mechanisms, including keyword filtering and behavior analysis.

#### 1.2.2 User Message Interpretation with Priority Handling
- **Description**: Interprets user message content and tags to determine priority and decide whether to interrupt the current task.
- **Key Code Snippets and Patterns**:
  ```javascript
  function handle_user_message(message) {
      if (message.includes("[OUT-OF-BAND USER MESSAGE]")) {
          if (message.includes("continue")) {
              proceed_silently();
          } else if (message.includes("stop")) {
              halt_and_wait();
          } else {
              evaluate_message_content();
          }
      }
  }
  ```
- **Common Errors and Prevention**:
  - **Interrupting tasks too frequently**: Only interrupt when there is a clear indication and prioritize high-priority messages.
  - **Ignoring critical instructions**: Establish clear priority levels and ensure critical instructions are not overlooked.

#### 1.2.3 Error Handling During Task Execution
- **Description**: Robust error handling maintains task execution integrity and security.
- **Key Strategies**:
  - **Fallback Mechanisms**: Implement alternative strategies to handle unexpected situations.
  - **Exception Management**: Use try-catch blocks to manage exceptions and prevent system crashes.
    ```javascript
    try {
        execute_task();
    } catch (error) {
        log_error(error);
        trigger_fallback_mechanism();
    }
    ```
  - **Resource Management**: Ensure resources are properly managed and released, even in the event of errors.

---

## 2. Workflow and Change Management

### 2.1 DAG Workflow Management and Validation

#### 2.1.1 Cycle Detection
- **Purpose**: Ensures the absence of cycles to maintain a valid DAG structure and prevent infinite loops.
- **Implementation**: Utilizes Depth-First Search (DFS) for cycle detection.
- **Key Code Snippet**:
  ```javascript
  // Cycle Detection (DFS)
  function detectCycle(nodes, edges) {
    const visited = new Set();
    const recStack = new Set();
    for (const node of nodes) {
      if (detectCycleUtil(node, nodes, edges, visited, recStack)) {
        return true;
      }
    }
    return false;
  }

  function detectCycleUtil(node, nodes, edges, visited, recStack) {
    if (recStack.has(node)) {
      return true;
    }
    if (visited.has(node)) {
      return false;
    }
    visited.add(node);
    recStack.add(node);
    const neighbors = edges.filter(edge => edge.from === node).map(edge => edge.to);
    for (const neighbor of neighbors) {
      if (detectCycleUtil(neighbor, nodes, edges, visited, recStack)) {
        return true;
      }
    }
    recStack.delete(node);
    return false;
  }
  ```
- **Error Prevention**:
  - **Inefficient Cycle Detection**: Use optimized DFS algorithms or Kahn's algorithm for topological sorting.
  - **Incorrect Cycle Identification**: Ensure accurate recursion stack maintenance.

#### 2.1.2 Orphan Node Detection
- **Purpose**: Identifies nodes not connected to any other nodes to ensure workflow integrity.
- **Implementation**: Checks node connectivity by analyzing in-degrees and out-degrees.

#### 2.1.3 Complex Path Analysis
- **Purpose**: Analyzes various paths within the DAG to understand dependencies and identify potential bottlenecks.
- **Implementation**: Traverses the graph to evaluate the flow and dependencies between nodes.

### 2.2 DAG Visualization with SVG Fallback

#### 2.2.1 Primary Rendering with React Flow
- **Purpose**: Provides an interactive and visually appealing representation of the DAG using the React Flow library.
- **Fallback Mechanism**: Automatically switches to pure SVG rendering if React Flow is unavailable.

#### 2.2.2 Pure SVG Rendering
- **Purpose**: Ensures DAG remains visually represented when the primary rendering library is unavailable.
- **Implementation**:
  - **Rendering Edges**: Uses SVG paths to draw edges between nodes.
  - **Rendering Nodes**: Utilizes SVG rectangles and text elements to represent nodes and their labels.
  - **Key Code Snippet**:
    ```javascript
    function renderDAGSVG(flow) {
        const svgNS = 'http://www.w3.org/2000/svg';
        const svg = document.createElementNS(svgNS, 'svg');
        svg.setAttribute('width', '100%');
        svg.setAttribute('height', '100%');

        // Render