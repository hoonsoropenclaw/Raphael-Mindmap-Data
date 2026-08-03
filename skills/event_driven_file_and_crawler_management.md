# Event-Driven File and Crawler Management

## Overview

The `event_driven_file_and_crawler_management` system integrates robust file monitoring and crawler orchestration using event-driven architectures. This comprehensive solution ensures efficient handling of file system changes and seamless coordination of crawler tasks. The system leverages both Python's `watchdog` library for event-driven file monitoring and Godot's polling mechanism for environments where event-driven approaches are not feasible. Additionally, it incorporates an event-driven crawler orchestration system to manage crawling tasks effectively.

## Key Features

### File Monitoring

- **Directory and File Monitoring**: Continuously monitor specified directories and files for creation, modification, and deletion events.
- **Event Handling**: Trigger custom actions in response to file system events.
- **Logging**: Record all file system events with timestamps for auditing and debugging.
- **File Archiving**: Automatically archive modified or created files for backup purposes.
- **Polling Mechanism**: Support for environments where event-driven monitoring is not feasible by using periodic polling.

### Crawler Orchestration

- **Task Queueing**: Efficiently queue crawling tasks for processing.
- **Task Execution**: Manage the execution of crawling tasks across multiple workers.
- **Event Monitoring**: Monitor crawler events such as task completion, failure, and item discovery.
- **Statistics Tracking**: Maintain statistics on crawler performance, including successful and failed tasks, and items found.

## Implementation Details

### 1. Python Watchdog-Based File Monitoring

#### Explanation

The Python implementation uses the `watchdog` library to monitor file system events. It includes event handlers for creation, modification, and deletion of files and directories.

#### Key Code Snippets

##### Event Handler
```python
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import shutil
import os
import json

class AutoIndexHandler(FileSystemEventHandler):
    def __init__(self, watch_dir, archive_dir, log_path, enable_archive=True, enable_staging=False):
        self.watch_dir = watch_dir
        self.archive_dir = archive_dir
        self.log_path = log_path
        self.enable_archive = enable_archive
        self.enable_staging = enable_staging

    def on_created(self, event):
        self._record("CREATED", event.src_path)
        if self.enable_archive:
            self._archive(event.src_path)
        if self.enable_staging:
            self._stage(event.src_path)

    def on_modified(self, event):
        self._record("MODIFIED", event.src_path)
        if self.enable_archive:
            self._archive(event.src_path)

    def on_deleted(self, event):
        self._record("DELETED", event.src_path)

    def _record(self, event_type, src_path, dest_path=""):
        payload = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "type": event_type,
            "path": src_path,
            "dest": dest_path,
        }
        self._rotate_if_needed()
        with self.log_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(payload, ensure_ascii=False) + "\n")
        print(f"[{payload['ts']}] {event_type:9s} {src_path}", flush=True)

    def _archive(self, src_path):
        dest_path = self.archive_dir / os.path.basename(src_path)
        if dest_path.exists():
            timestamp = time.strftime("%Y%m%d%H%M%S")
            dest_path = self.archive_dir / (os.path.basename(src_path) + "_" + timestamp)
        shutil.copy2(src_path, dest_path)

    def _stage(self, src_path):
        # Implement staging logic if needed
        pass

    def _rotate_if_needed(self):
        # Implement log rotation logic if needed
        pass

observer = Observer()
event_handler = AutoIndexHandler(watch_dir='./watch_test', archive_dir='./archive', log_path='./log.json')
observer.schedule(event_handler, path='./watch_test', recursive=True)
observer.start()
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()
observer.join()
```

##### Error Prevention

- **Issue**: Monitoring directory does not exist when the observer starts.
  - **Solution**: Ensure the directory exists before scheduling the observer by calling `os.makedirs` with `exist_ok=True`.
  
- **Issue**: Blocking I/O operations causing the main loop to stall.
  - **Solution**: Use asynchronous I/O or a thread pool to handle file operations without blocking the main loop.
  
- **Issue**: Infinite loop preventing the program from exiting gracefully.
  - **Solution**: Handle `KeyboardInterrupt` to catch SIGINT signals and shut down the observer cleanly.

### 2. Godot Polling-Based File Watcher

#### Explanation

In Godot, where event-driven monitoring is not natively supported, a polling mechanism is implemented to periodically check for file system changes. This approach involves periodically scanning the directory and comparing file metadata to detect changes.

#### Key Code Snippets

##### Polling Logic
```gdscript
func _wait_for_polling(seconds: float) -> void:
    var elapsed := 0.0
    var slice := 0.05
    while elapsed < seconds:
        await create_timer(slice).timeout
        elapsed += slice
```

##### File Metadata Capture
```gdscript
func _meta_for(path: String, is_dir: bool) -> Dictionary:
    var file := FileAccess.open(path, FileAccess.READ)
    var mtime := 0.0
    var size := 0
    if file != null:
        mtime = FileAccess.get_modified_time(path)
        size = file.get_length()
        file.close()
    return {"mtime": float(mtime), "size": size, "is_directory": is_dir}
```

##### Event Trigger Conditions
```gdscript
if not new_meta.get("is_directory", false) and \
        (absf(new_mtime - old_mtime) > 0.0001 or new_size != old_size):
    _emit_event(EventType.MODIFIED, new_path, false, "")
```

##### Error Prevention

1. **Issue**: In headless mode, `process_frame` signal does not trigger, causing polling to fail.
   - **Solution**: Use `OS.delay_msec` or `create_timer().timeout` to simulate the polling loop.
   
2. **Issue**: `FileAccess.get_modified_time()` cannot distinguish modifications within the same second, leading to missed events.
   - **Solution**: Compare file sizes (`size`) alongside modification times to compensate for the lack of higher resolution in time tracking.
   
3. **Issue**: Testing in headless mode is challenging due to the absence of GUI elements.
   - **Solution**: Write headless end-to-end test scripts (`smoke_test.gd`) to verify functionality.

### 3. Crawler Event-Driven Orchestration

#### Explanation

This component uses an event-driven architecture to coordinate crawler tasks, including task dispatching, execution, monitoring, and completion.

#### Key Code Snippets
```python
class Crawler:
    def __init__(self, workers: int, extractor: Extractor):
        self.bus = EventBus()
        self.pool = WorkerPool(workers)
        self.extractor = extractor
        
    async def run(self, urls: List[str]) -> Dict[str, Any]:
        self.bus.subscribe(self._observer)
        self.pool.start()
        for url in urls:
            self.bus.publish(Event(EventType.JOB_DISPATCHED, {"url": url}))
        await self._wait_for_idle(idle_s=1.0, max_wait_s=120.0)
        
    async def _observer(self, event: Event):
        if event.type == EventType.JOB_COMPLETED:
            self._stats["ok"] += 1
        elif event.type == EventType.JOB_FAILED:
            self._stats["fail"] += 1
        elif event.type == EventType.ITEM_FOUND:
            self._stats["items"] += len(event.payload.get("items", []))
```

#### Common Errors and Prevention

- **Error**: In event handling functions, failure to correctly update the state leads to incorrect statistics.
  - **Solution**: Ensure that all event types have corresponding handling logic and that the state is updated accurately.
  
- **Error**: Waiting for idle state fails due to different time bases.
  - **Solution**: Use the same time base for comparison, such as using `time.time()` for both.

## Conclusion

The `event_driven_file_and_crawler_management` system offers a robust and versatile solution for managing file system changes and crawler tasks. By integrating event-driven architectures and polling mechanisms, it ensures efficient and reliable operation across various environments. The included error-prevention strategies and code snippets provide a solid foundation for building resilient and scalable applications.