# Real-Time Data Visualization and Event Handling

## Overview
This micro-skill focuses on handling real-time events and generating dynamic outputs for monitoring and analysis, including creating real-time data visualization dashboards. It combines backend event monitoring using inotify with real-time dashboard updates via Server-Sent Events (SSE) and dynamic webpage generation for interactive data visualization.

---

## 1. Inotify Backend Event Handling

### Purpose
Monitor filesystem events in real-time using inotify and convert them into internal event objects for further processing and visualization.

### Key Implementation Details
- **Initialization**: Use `inotify_simple.init()` to set up inotify and add watches on the target directory.
- **Event Monitoring**: Continuously listen for events such as file modifications, creations, and deletions.
- **Event Processing**: Convert inotify events into internal event objects for downstream processing and dashboard updates.

### Code Example
```python
import ctypes
import inotify_simple

def watch_directory(path):
    fd = inotify_simple.init()
    inotify_simple.add_watch(fd, path, inotify_simple.IN_MODIFY | inotify_simple.IN_CREATE | inotify_simple.IN_DELETE)
    try:
        while True:
            events = inotify_simple.read(fd)
            for event in events:
                # Convert inotify event to internal event object
                internal_event = {
                    "mask": event.mask,
                    "name": event.name.decode().replace('\x00', ''),
                    "cookie": event.cookie,
                    "wd": event.wd
                }
                # Process the internal event
                process_event(internal_event)
    except KeyboardInterrupt:
        print("Stopping inotify event monitoring.")
    finally:
        inotify_simple.close(fd)

def process_event(event):
    # Implement your event processing logic here
    print(f"Event received: {event}")
```

### Common Errors and Prevention
1. **NUL Characters in Event Names**
   - **Issue**: Event names may contain NUL characters, causing string processing errors.
   - **Solution**: Strip NUL characters when processing event names.
     ```python
     event_name = event.name.decode().replace('\x00', '')
     ```

2. **File Descriptor Leakage**
   - **Issue**: Failure to close inotify file descriptors can lead to resource leaks over time.
   - **Solution**: Use context managers or ensure proper cleanup on program termination.
     ```python
     import contextlib

     def watch_directory(path):
         with inotify_simple.INotify() as fd:
             fd.add_watch(path, inotify_simple.IN_MODIFY | inotify_simple.IN_CREATE | inotify_simple.IN_DELETE)
             while True:
                 events = fd.read()
                 for event in events:
                     # Process events
                     ...
     ```

---

## 2. Web Dashboard Real-Time Streaming

### Purpose
Implement a real-time event stream dashboard using SSE to reflect backend events instantly on a web interface.

### Key Implementation Details
- **Server-Sent Events (SSE)**: Use SSE to push events from the server to the client over a single HTTP connection.
- **HTTP Server Setup**: Set up an HTTP server to handle SSE connections and serve the dashboard HTML.
- **Event Broadcasting**: Continuously send events to connected clients as they occur.

### Code Example
```python
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import threading
import time

INDEX_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Real-Time Dashboard</title>
</head>
<body>
    <h1>Real-Time Events</h1>
    <div id="events"></div>
    <script>
        const eventSource = new EventSource("/events");
        eventSource.onmessage = function(event) {
            const eventsDiv = document.getElementById("events");
            const newEvent = document.createElement("div");
            newEvent.textContent = event.data;
            eventsDiv.prepend(newEvent);
        };
    </script>
</body>
</html>
"""

class SSEHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/events':
            self.send_response(200)
            self.send_header('Content-Type', 'text/event-stream')
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()
            try:
                while True:
                    # Replace with actual event data
                    event = {"message": "Event occurred"}
                    self.wfile.write(f'data: {json.dumps(event)}\n\n'.encode())
                    self.wfile.flush()
                    time.sleep(1)  # Adjust as needed
            except BrokenPipeError:
                # Client disconnected
                pass
        else:
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(INDEX_HTML.encode())

def start_server():
    server = HTTPServer(('127.0.0.1', 8765), SSEHandler)
    server.serve_forever()

if __name__ == "__main__":
    server_thread = threading.Thread(target=start_server)
    server_thread.daemon = True
    server_thread.start()
    print("Server started on http://127.0.0.1:8765")
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        print("Shutting down server.")
        exit(0)
```

### Common Errors and Prevention
1. **Unclosed SSE Connections**
   - **Issue**: SSE connections may not close properly, leading to resource leaks.
   - **Solution**: Ensure the server closes the response stream when the client disconnects.
     ```python
     except BrokenPipeError:
         # Client disconnected
         pass
     ```

2. **Resource Exhaustion from Long-Running Connections**
   - **Issue**: Long-running SSE connections can consume significant server resources.
   - **Solution**: Implement a timeout mechanism and close idle connections.
     ```python
     import socket

     class SSEHandler(BaseHTTPRequestHandler):
         def do_GET(self):
             if self.path == '/events':
                 ...
                 try:
                     while True:
                         ...
                         if self.connection.sock:
                             self.connection.sock.settimeout(10)  # Timeout after 10 seconds
                 except socket.timeout:
                     self.wfile.close()
     ```

3. **Client-Side Reconnection Logic**
   - **Issue**: Clients may not handle reconnection gracefully after a disconnection.
   - **Solution**: Implement reconnection logic on the client side using JavaScript.
     ```javascript
     const eventSource = new EventSource("/events");
     eventSource.onerror = function() {
         console.log("EventSource failed, attempting to reconnect...");
         setTimeout(() => {
             eventSource.close();
             eventSource = new EventSource("/events");
         }, 5000);
     };
     ```

---

## 3. Dynamic Web Output Generation and Visualization

### Purpose
Create interactive, dynamic web content and visualize data for real-time monitoring and analysis.

### Key Implementation Details
- **HTML Structure**: Design a structured HTML layout with interactive elements.
- **CSS Styling**: Apply styles to ensure the webpage is visually appealing and responsive.
- **JavaScript Logic**: Implement dynamic behaviors, such as handling user input, processing data, and updating the UI in real-time.

### Code Example
```html
<!DOCTYPE html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8">
  <title>动态网页输出示例</title>
  <!-- 引入必要的库和样式 -->
  <script src="https://cdn.jsdelivr.net/npm/pdfjs-dist@4.0.379/build/pdf.min.mjs" type="module"></script>
  <script src="https://cdn.jsdelivr.net/npm/tesseract.js@5/dist/tesseract.min.js"></script>
  <style>
    /* 基本样式 */
    body {
      font-family: Arial, sans-serif;
      margin: 20px;
    }
    .app {
      max-width: 800px;
      margin: auto;
    }
    canvas {
      border: 1px solid #ccc;
    }
  </style>
</head>
<body>
  <div class="app">
    <!-- 用户界面元素 -->
    <h1>PDF OCR → 结构化数据处理工具</h1>
    <input type="file" id="file-input" accept="application/pdf" />
    <canvas id="pdf-canvas"></canvas>
    <pre id="extracted-data"></pre>
    <button id="redact-button">遮罩敏感信息</button>
    <button id="download-button">下载结果</button>
  </div>

  <script>
    // JavaScript 逻辑

    // 处理 PDF 文件
    document.getElementById('file-input').addEventListener('change', function(event) {
      const file = event.target.files[0];
      if (file) {
        const loadingTask = pdfjsLib.getDocument({ url: URL.createObjectURL(file) });
        loadingTask.promise.then(function(pdf) {
          // 渲染 PDF 页面
          pdf.getPage(1).then(function(page) {
            const scale = 1.5;
            const viewport = page.getViewport({ scale: scale });
            const canvas = document.getElementById('pdf-canvas');
            const context = canvas.getContext('2d');
            canvas.height = viewport.height;
            canvas.width = viewport.width;

            const renderContext = {
              canvasContext: context,
              viewport: viewport
            };
            page.render(renderContext).promise.then(function() {
              // OCR 和数据提取逻辑
              Tesseract.recognize(canvas, 'eng', { logger: m => console.log(m) })
                .then(({