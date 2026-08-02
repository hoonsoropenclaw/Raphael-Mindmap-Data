# Event-Driven Application Development

## Overview
This document provides a comprehensive guide to building scalable, reactive applications using an event-driven architecture. It covers implementing an asynchronous publish-subscribe pattern with an event bus, monitoring filesystem events, handling events in real-time, and simulating filesystem operations for testing purposes.

## Event Bus for Asynchronous Publish-Subscribe

### Description
Implement an event bus based on `asyncio` to support multiple subscribers, event fan-out, and historical snapshots of events.

### Key Code Snippets
```python
from collections import deque
from typing import AsyncGenerator

class BusEvent:
    def __init__(self, type: str, data: dict):
        self.type = type
        self.data = data

    def to_dict(self):
        return {'type': self.type, 'data': self.data}

class EventBus:
    def __init__(self):
        self._subscribers = []
        self._history = deque(maxlen=100)

    async def subscribe(self) -> AsyncGenerator[BusEvent, None]:
        queue = asyncio.Queue()
        self._subscribers.append(queue)
        try:
            async for event in self._process_events(queue):
                yield event
        finally:
            self._subscribers.remove(queue)

    async def _process_events(self, queue: asyncio.Queue):
        while True:
            event = await queue.get()
            yield event

    def publish(self, event: BusEvent):
        self._history.append(event)
        for subscriber in self._subscribers:
            subscriber.put_nowait(event)

    def history_snapshot(self, n: int = 10) -> list[BusEvent]:
        return list(self._history)[-n:]
```

### Common Errors and Prevention
- **Memory Leaks Due to Improper Subscriber Cleanup**: 
  - **Issue**: Subscribers may not be properly removed, leading to memory leaks.
  - **Solution**: Use a `try...finally` block to ensure that the subscriber queue is removed when the subscriber disconnects.
  
- **Blocking I/O Operations Affecting Event Bus Performance**: 
  - **Issue**: Blocking operations can degrade the performance of the event bus.
  - **Solution**: Avoid blocking operations within event handlers. If necessary, use `asyncio.to_thread` to offload blocking tasks to a thread pool.

## Filesystem Monitoring and Event Handling

### Filesystem Monitoring Setup

#### Description
Utilize the `watchdog` library to monitor filesystem events such as file creation, modification, and deletion.

#### Key Code Snippets
```python
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time

class DebouncedHandler(FileSystemEventHandler):
    def __init__(self, debounce_ms=200):
        super().__init__()
        self.debounce_ms = debounce_ms
        self.last_event_time = {}  # path -> timestamp

    def on_any_event(self, event):
        path = event.src_path
        current_time = time.time()
        if path in self.last_event_time:
            if current_time - self.last_event_time[path] < self.debounce_ms / 1000:
                return
        self.last_event_time[path] = current_time
        # Handle the event, e.g., broadcast it
```

#### Common Errors and Solutions
- **Excessive Event Triggering**: 
  - **Issue**: Frequent events can overwhelm the rule engine, causing performance issues.
  - **Solution**: Implement a debouncing mechanism in the `DebouncedHandler` to filter events within a specified time interval.
  
- **Cross-Platform Compatibility Issues**: 
  - **Issue**: Different operating systems may handle filesystem events differently.
  - **Solution**: Use `watchdog`'s cross-platform API to ensure consistent behavior across operating systems.

### WebSocket Event Broadcasting

#### Description
Use `Flask-SocketIO` to broadcast filesystem events to the frontend in real-time, enabling instant monitoring and feedback.

#### Key Code Snippets
```python
from flask import Flask
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

@socketio.on('connect')
def on_connect():
    print('Client connected')

def broadcast_event(event):
    socketio.emit('fs:event', event.to_dict())

def broadcast_action(action):
    socketio.emit('fs:action', action.to_dict())
```

#### Common Errors and Solutions
- **WebSocket Connection Interruptions or Delays**: 
  - **Issue**: Network issues can cause interruptions or delays in the WebSocket connection, affecting real-time performance.
  - **Solution**: Implement a reconnection mechanism and handle reconnection scenarios on the frontend to ensure connection stability.
  
- **Event Data Serialization Issues**: 
  - **Issue**: Non-serializable data can cause broadcasting failures.
  - **Solution**: Ensure all event data is serializable, for example, by using the `to_dict()` method to convert `dataclass` instances to dictionaries.

## Simulating Filesystem Operations

### Description
Implement a set of simulated filesystem operations, such as creating, modifying, moving, and deleting files, to test the filesystem monitoring and rule engine functionalities.

### Key Code Snippets
```python
import os
import shutil
import time

SANDBOX = '/path/to/sandbox'  # Replace with the actual sandbox path

def sim_create(name: str = 'hello.txt') -> dict:
    path = os.path.join(SANDBOX, name)
    with open(path, 'w') as f:
        f.write(f'# created at {time.time()}\nhello world\n')
    return {'ok': True, 'path': path}

def sim_modify(name: str = 'hello.txt') -> dict:
    path = os.path.join(SANDBOX, name)
    with open(path, 'a') as f:
        f.write(f'# modified at {time.time()}\n')
    return {'ok': True, 'path': path}

def sim_move(name: str = 'hello.txt') -> dict:
    src = os.path.join(SANDBOX, name)
    dst = os.path.join(SANDBOX, f'{name}_moved_{int(time.time())}')
    os.rename(src, dst)
    return {'ok': True, 'src': src, 'dst': dst}

def sim_delete(name: str = 'hello.txt') -> dict:
    path = os.path.join(SANDBOX, name)
    os.remove(path)
    return {'ok': True, 'path': path}
```

### Common Errors and Solutions
- **Mismatch Between Simulated and Actual Filesystem Operations**: 
  - **Issue**: Simulated operations may not fully replicate real-world scenarios, leading to inaccurate test results.
  - **Solution**: Ensure that simulated operations closely mimic actual operations, including handling cases where files already exist and simulating more complex sequences of operations.
  
- **Simulated Operations Not Triggering Expected Monitoring Events**: 
  - **Issue**: Some simulated operations may not correctly trigger filesystem events, causing monitoring to fail.
  - **Solution**: Verify the `watchdog` event triggering mechanism and use logging or debugging tools to ensure that events are correctly processed.

## Summary
This document provides a detailed guide on setting up filesystem monitoring, broadcasting events via WebSocket, and simulating filesystem operations. It also covers common errors and their solutions to ensure stable and efficient implementation of filesystem monitoring and event handling in real-world applications.