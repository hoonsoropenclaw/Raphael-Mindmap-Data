# Process and JavaScript Optimization

## Overview
This micro-skill focuses on enhancing system performance and reliability by optimizing process management, input/output (I/O) operations, runtime middleware integration, and JavaScript compilation strategies. It provides detailed guidance on managing processes, handling asynchronous I/O, integrating essential runtime features, and addressing common issues in Babel standalone modules and JSX compilation.

---

## 1. Process Management and I/O Optimization

### 1.1 Preventing Zombie Processes

#### Description
Zombie processes are child processes that have completed execution but still retain an entry in the process table, preventing the parent process from recognizing their termination. Proper management is essential to prevent resource leaks and terminal blocking.

#### Key Techniques and Patterns

##### Using `disown` to Detach Processes
The `disown` command removes jobs from the shell's active job table, allowing them to continue running in the background even after the terminal is closed.

```bash
# Start a background process and detach it from the terminal
python -m http.server & disown
```

##### Using `nohup` with Output Redirection
The `nohup` command allows a process to ignore the hangup signal, enabling it to continue running after the terminal is closed. Combining it with output redirection prevents log files from growing excessively large.

```bash
# Start a process with nohup and redirect both stdout and stderr to a log file
nohup python script.py > output.log 2>&1 &
```

#### Common Mistakes and Prevention

- **Mistake**: Using `&` to background a process without `disown`, causing the process to terminate when the terminal closes.
  - **Solution**: Always use `disown` after placing a process in the background to detach it from the terminal.
  
    ```bash
    # Incorrect
    python script.py &
    
    # Correct
    python script.py & disown
    ```

- **Mistake**: Using `nohup` without proper output redirection, leading to oversized log files.
  - **Solution**: Always redirect both `stdout` and `stderr` to a log file when using `nohup`.
  
    ```bash
    # Incorrect
    nohup python script.py &
    
    # Correct
    nohup python script.py > output.log 2>&1 &
    ```

### 1.2 Optimizing I/O in Asynchronous Applications

#### Description
In asynchronous applications, blocking I/O operations like `time.sleep()` or synchronous database queries can halt the event loop, degrading performance. Utilizing non-blocking I/O operations is crucial for maintaining responsiveness and scalability.

#### Key Techniques and Patterns

##### Replacing Blocking with Non-Blocking I/O

###### Blocking I/O Example
Using `time.sleep()` in an asynchronous function blocks the event loop, preventing other tasks from running.

```python
import time

async def blocking_task():
    time.sleep(5)  # Blocks the event loop
```

###### Non-Blocking I/O Example
Using `asyncio.sleep()` allows other tasks to run while waiting, preventing the event loop from being blocked.

```python
import asyncio

async def non_blocking_task():
    await asyncio.sleep(5)  # Non-blocking wait
```

#### Common Mistakes and Prevention

- **Mistake**: Using `time.sleep()` in asynchronous functions.
  - **Solution**: Replace `time.sleep()` with `asyncio.sleep()` to prevent blocking the event loop.
  
    ```python
    # Incorrect
    import time

    async def example():
        time.sleep(2)
    
    # Correct
    import asyncio

    async def example():
        await asyncio.sleep(2)
    ```

- **Mistake**: Performing synchronous database queries in asynchronous functions.
  - **Solution**: Use asynchronous database drivers (e.g., `asyncpg` for PostgreSQL) and `await` the queries to maintain non-blocking behavior.
  
    ```python
    # Incorrect
    import sqlite3

    async def sync_db_query():
        conn = sqlite3.connect('example.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM table')
        results = cursor.fetchall()
        conn.close()
        return results
    
    # Correct
    import asyncpg

    async def async_db_query():
        conn = await asyncpg.connect(user='user', password='password',
                                     database='library', host='127.0.0.1')
        results = await conn.fetch('SELECT * FROM table')
        await conn.close()
        return results
    ```

---

## 2. Runtime Middleware Integration

### Description
Integrate essential runtime features such as UUID request ID generation, body size limiting, timeout handling, rate limiting, security headers, and metrics into a single `RuntimeMiddleware` to enhance application functionality and maintainability.

### Key Techniques and Patterns

#### Example Implementation

```python
# middleware.py
import asyncio
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from prometheus_client import Summary
import uuid

REQUEST_TIME = Summary('request_processing_seconds', 'Time spent processing request')

class RuntimeMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Generate or retrieve request ID
        request_id = request.headers.get('X-Request-Id', uuid.uuid4().hex)
        
        # Set request ID in headers
        request.headers.__setitem__('X-Request-Id', request_id)
        
        # Start timing the request
        with REQUEST_TIME.time():
            response = await call_next(request)
        
        # Attach request ID to response headers
        response.headers['X-Request-Id'] = request_id
        return response
```

### Common Mistakes and Prevention

- **Mistake**: Including too many metrics labels, leading to cardinality explosion.
  - **Solution**: Limit metrics labels to essential fields such as method, route template, and status to avoid high cardinality.
  
    ```python
    # Incorrect
    REQUEST_TIME = Summary('request_processing_seconds', 'Time spent processing request', ['method', 'route', 'status', 'user_id'])
    
    # Correct
    REQUEST_TIME = Summary('request_processing_seconds', 'Time spent processing request', ['method', 'route', 'status'])
    ```

---

## 3. JavaScript Compilation and Module Optimization

### 3.1 Babel Standalone Module Fix

#### Issue
Babel-standalone version 8 automatically treats `<script type="text/babel" data-type="module">` as an ES module. This behavior can cause syntax errors when using non-module syntax (e.g., `const`) within the script.

#### Solution
To resolve this, remove the `data-type="module"` attribute and use `data-presets="react"` to handle JSX transformation.

#### Key Code Snippets
**Problematic Script Tag:**
```html
<script type="text/babel" data-presets="react" data-type="module">
  // JSX code
</script>
```

**Corrected Script Tag:**
```html
<script type="text/babel" data-presets="react">
  // JSX code
</script>
```

#### Common Errors and Prevention
- **Error**: Using `data-type="module"` causes Babel-standalone to attempt processing the code as a module, leading to syntax errors.
- **Prevention**: Remove `data-type="module"` and rely solely on `data-presets="react"` for JSX transformation.

### 3.2 JSX Runtime Classic Compilation

#### Issue
In certain environments, React's development runtime (e.g., `jsxDEV`) may be unavailable. This can prevent the proper compilation and rendering of JSX code.

#### Solution
To address this, compile JSX code to use the classic runtime (`React.createElement`) instead of the development runtime.

#### Key Code Snippets
**Compilation Process:**
```javascript
const Babel = require('@babel/core');
const fs = require('fs');

// Read the source file
let src = fs.readFileSync('index.html', 'utf8');

// Locate the inlined script containing JSX
const m = src.match(/<script>\s*\nimport \{ jsxDEV[\s\S]*?<\/script>/);
if (!m) { 
  console.error('No inlined script to replace'); 
  process.exit(1); 
}

// Extract and clean the compiled JSX code
let compiled = m[0].slice(8, -9).trim();
compiled = compiled.replace(/^import \{[^}]*\} from "react\/jsx-dev-runtime";\s*/m, '');

// Define the classic runtime stub
const stub = `
var _jsxDEV = function(type, props, key) { return React.createElement(type, Object.assign({}, props, key != null ? {key: key} : {})); };
var _jsx = _jsxDEV;
var _jsxs = _jsxDEV;
var _Fragment = React.Fragment;
`;

// Replace the inlined script with the classic runtime version
const newScript = '<script>\n' + stub + compiled + '\n</script>';
src = src.replace(m[0], newScript);

// Write the updated content back to the file
fs.writeFileSync('index.html', src);
console.log('Rewrote, file now', src.length, 'chars');
```

#### Common Errors and Prevention
- **Error**: Compiled code still contains calls to `jsxDEV`, causing runtime errors.
- **Prevention**: During the compilation process, replace `jsxDEV` with `React.createElement` and ensure that `React.Fragment` is properly declared.

---

## Summary
By effectively managing processes, optimizing I/O operations, integrating runtime middleware, and correctly handling JavaScript compilation and module optimization, you can significantly enhance the stability, performance, and functionality of your applications. Always ensure that background processes are properly detached, asynchronous functions utilize non-blocking I/O, middleware is thoughtfully implemented