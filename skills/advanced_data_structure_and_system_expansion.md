# Advanced Data Structure and System Expansion

## Target Skill Name
advanced_data_structure_and_system_expansion

## Target Summary
Implement and optimize graph algorithms and traversal techniques, and propose and implement strategies for system domain or feature expansion.

---

## 1. Graph Algorithm and Traversal

### 1.1 Frontier Strategy (BFS/DFS)

#### Description
Control the traversal order of graph-based algorithms using Breadth-First Search (BFS) and Depth-First Search (DFS) strategies. These strategies are fundamental for tasks like crawling, pathfinding, and data processing.

#### BFS (Breadth-First Search) Frontier

##### Key Concepts
- Utilizes a queue to explore neighbors level by level.
- Suitable for finding the shortest path in unweighted graphs.

##### Implementation (Python)
```python
from asyncio import Queue

class BFSFrontier:
    def __init__(self):
        self._q = Queue()

    async def put(self, item):
        await self._q.put(item)

    async def get(self):
        return await self._q.get()

    async def join(self):
        await self._q.join()
```

#### DFS (Depth-First Search) Frontier

##### Key Concepts
- Utilizes a stack to explore as far as possible along each branch before backtracking.
- Useful for tasks like topological sorting and cycle detection.

##### Implementation (Python)
```python
from asyncio import Queue

class DFSFrontier:
    def __init__(self):
        self._stack = []

    async def put(self, item):
        self._stack.append(item)

    async def get(self):
        return self._stack.pop()

    async def join(self):
        pass
```

##### Common Errors and Prevention
- **Error**: Improper stack management in DFS leading to infinite recursion or data loss.
  - **Solution**: Use a list to simulate a stack and ensure the last element is correctly popped in the `get` method.
  
- **Error**: Improper queue handling in BFS causing tasks to remain incomplete.
  - **Solution**: Use `asyncio.Queue` and call `task_done()` upon task completion to ensure `join()` waits for all tasks to finish.

### 1.2 Graph Algorithm Implementation

#### 1.2.1 Kahn's Topological Sorting

##### Description
Kahn's algorithm is used to perform topological sorting on Directed Acyclic Graphs (DAGs). It detects cycles by ensuring all nodes are processed in a valid order.

##### Steps
1. **Initialize In-Degree of Each Node**:
   - Create a data structure (e.g., array or hash map) to store the in-degree of each node.
   - Iterate through all edges to populate the in-degree values.

2. **Initialize Queue**:
   - Enqueue all nodes with an in-degree of 0.

3. **Process Nodes**:
   - While the queue is not empty:
     - Dequeue a node and add it to the topological order.
     - For each neighbor of the dequeued node:
       - Decrement its in-degree by 1.
       - If the in-degree becomes 0, enqueue the neighbor.

4. **Check for Cycles**:
   - If the topological order includes all nodes, the graph is a DAG.
   - Otherwise, the graph contains at least one cycle.

##### Code Snippet (Python)
```python
from collections import defaultdict, deque

def kahn_topological_sort(graph):
    in_degree = defaultdict(int)
    for u in graph:
        for v in graph[u]:
            in_degree[v] += 1

    queue = deque([u for u in graph if in_degree[u] == 0])
    topo_order = []

    while queue:
        u = queue.popleft()
        topo_order.append(u)
        for v in graph[u]:
            in_degree[v] -= 1
            if in_degree[v] == 0:
                queue.append(v)

    if len(topo_order) == len(graph):
        return topo_order
    else:
        raise ValueError("Graph has at least one cycle")

# Example usage:
graph = {
    'A': ['C'],
    'B': ['C', 'D'],
    'C': ['E'],
    'D': ['E'],
    'E': []
}

print(kahn_topological_sort(graph))
```

##### Error Prevention
- **Cycle Detection**: If the topological order does not include all nodes, a cycle exists in the graph.
- **Graph Validation**: Ensure the input graph is a valid DAG before attempting to sort.

#### 1.2.2 DFS Cycle Detection

##### Description
Depth First Search (DFS) is used to detect cycles in a graph. The algorithm uses a three-color marking method to identify nodes that are part of a cycle.

##### Steps
1. **Initialize Color Array**:
   - Create a data structure (e.g., array or hash map) to store the color of each node.
   - Initially, all nodes are marked as "white" (unvisited).

2. **DFS Traversal**:
   - For each unvisited node, perform DFS:
     - Mark the current node as "gray" (visited).
     - For each neighbor of the current node:
       - If the neighbor is "gray", a cycle is detected.
       - If the neighbor is "white", recursively perform DFS on it.
     - Mark the current node as "black" (fully processed).

3. **Cycle Detection**:
   - If a "gray" node is encountered during traversal, a cycle exists.

##### Code Snippet (Python)
```python
from collections import defaultdict

def dfs_cycle_detection(graph):
    color = defaultdict(lambda: 'white')
    has_cycle = False

    def dfs(u):
        nonlocal has_cycle
        color[u] = 'gray'
        for v in graph[u]:
            if color[v] == 'gray':
                has_cycle = True
                return
            if color[v] == 'white':
                dfs(v)
        color[u] = 'black'

    for u in graph:
        if color[u] == 'white':
            dfs(u)
            if has_cycle:
                return True

    return False

# Example usage:
graph = {
    'A': ['B'],
    'B': ['C'],
    'C': ['A']
}

print(dfs_cycle_detection(graph))
```

##### Error Prevention
- **Graph Validation**: Ensure the input graph is a valid directed graph.
- **Handling Large Graphs**: For very large graphs, consider using iterative DFS to avoid stack overflow.

---

## 2. Topological Sort with Cycle Detection

### Description
In processing Directed Acyclic Graphs (DAGs), topological sorting is a crucial step. To ensure the graph is free of cycles, cycle detection must be performed during the sorting process.

### Key Code Snippet or Pattern (JavaScript)
```javascript
function topologicalSort(nodes, edges) {
  const inDeg = {};
  const byId = {};
  nodes.forEach(n => { inDeg[n.id] = 0; byId[n.id] = n; });
  edges.forEach(e => {
    if (byId[e.target] && inDeg[e.target] != null) {
      inDeg[e.target]++;
    }
  });
  const queue = nodes.filter(n => inDeg[n.id] === 0);
  const order = [];
  const adj = {};
  nodes.forEach(n => { adj[n.id] = []; });
  edges.forEach(e => {
    if (adj[e.source]) adj[e.source].push(e.target);
  });
  while (queue.length) {
    const n = queue.shift();
    order.push(n);
    (adj[n.id] || []).forEach(t => {
      if (inDeg[t] == null) return;
      inDeg[t]--;
      if (inDeg[t] === 0 && byId[t]) queue.push(byId[t]);
    });
  }
  return order;
}
```

### Common Errors and Prevention
- **Error**: In the topological sorting process, failure to consider isolated nodes or edges leads to ineffective cycle detection.
- **Prevention**: Use the `byId` lookup table to ensure all target nodes exist and consider the existence of the target node during cycle detection.

---

## 3. System Domain or Feature Expansion

### Description
When the current task exceeds the authorized learning domain, propose strategies for expanding the learning domain.

### Key Content
- **Current Task**: Develop high-quality UI animations using Framer Motion and optimize performance.
- **Proposed Expansion Domain**: UI/UX Aesthetics & Design Systems (Framer Motion belongs to this domain).
- **Reason**: The current task involves UI animation and performance optimization, and it is recommended to include Framer Motion and related UI/UX design systems in the learning domain.

---

## Conclusion
By implementing and optimizing graph algorithms and traversal techniques, and by proposing and implementing strategies for system domain or feature expansion, you can effectively manage and analyze complex data structures and systems, ensuring they are free of cycles and can be processed in a valid order. These strategies are essential for efficient data processing and problem-solving in various applications, including network analysis, scheduling, and UI/UX design systems.