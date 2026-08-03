# Advanced Asyncio Task Management

## Overview
This advanced micro-skill focuses on managing asynchronous tasks using `asyncio`, including implementing retry mechanisms with exponential backoff, managing task scheduling with bounded queues and worker pools, and building an event-driven web crawler framework.

---

## 1. Retry with Exponential Backoff

### Description
Implement a robust retry mechanism for network requests using exponential backoff to enhance the success rate of requests in the face of transient failures.

### Key Code Snippet
```python
import asyncio
import random

async def fetch_with_retry(url, retries=3, backoff_factor=0.5):
    for attempt in range(1, retries + 1):
        try:
            return await fetch(url)
        except Exception as e:
            wait_time = backoff_factor * (2 ** (attempt - 1)) + random.uniform(0, 0.1)
            print(f'Retry {attempt} for {url} in {wait_time} seconds due to {e}')
            await asyncio.sleep(wait_time)
    raise Exception(f'All retries failed for {url}')

async def main():
    urls = [...]
    tasks = [asyncio.create_task(fetch_with_retry(url)) for url in urls]
    results = await asyncio.gather(*tasks)
    return results

asyncio.run(main())
```

### Common Errors and Prevention
1. **Infinite Retries**: Always set a maximum number of retries to prevent exhausting system resources.
2. **Insufficient Backoff Time**: Adjust the backoff time based on the specific use case to avoid excessively short or long wait times.

---

## 2. Bounded Asyncio Queue Worker Pool

### Description
Utilize bounded queues and worker pools to manage concurrent tasks efficiently, ensuring optimal resource utilization and stable task execution.

### Key Code Snippet
```python
import asyncio

async def worker(name, queue, results):
    while True:
        try:
            url = await queue.get()
            content = await fetch(url)
            results.append(content)
        except Exception as e:
            print(f'Error fetching {url}: {e}')
        finally:
            queue.task_done()

async def main():
    queue = asyncio.Queue(maxsize=100)  # Bounded queue to prevent memory overload
    results = []
    for url in urls:
        await queue.put(url)
    num_workers = 10  # Number of worker tasks
    workers = [asyncio.create_task(worker(f'worker-{i}', queue, results)) for i in range(num_workers)]
    await queue.join()  # Wait until all tasks are processed
    for worker_task in workers:
        worker_task.cancel()
    await asyncio.gather(*workers, return_exceptions=True)
    return results

asyncio.run(main())
```

### Common Errors and Prevention
1. **Improper Queue Closure**: Ensure the queue is properly closed after tasks are completed to prevent workers from entering an infinite wait state.
2. **Resource Contention**: Use locks or semaphores to control access to shared resources and prevent race conditions.

---

## 3. Asyncio Event-Driven Crawler

### Description
Build an event-driven web crawler using `asyncio`, featuring non-blocking HTTP request handling, event-driven task scheduling, error handling with retries, rate limiting, and JSONL-formatted output.

### Key Code Snippet
```python
import asyncio
from urllib.request import urlopen

async def fetch(url):
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(None, urlopen, url)
    return response.read()

async def main():
    urls = [...]
    tasks = [asyncio.create_task(fetch(url)) for url in urls]
    results = await asyncio.gather(*tasks)
    for content in results:
        print(content)

asyncio.run(main())
```

### Enhanced Features
1. **Non-blocking HTTP Requests**: Use `asyncio` and executors to prevent blocking the event loop.
2. **Event-Driven Task Scheduling**: Schedule tasks based on events, such as task completion or new URL discovery.
3. **Error Handling and Retries**: Implement comprehensive exception handling and retry mechanisms to manage network errors or request failures.
4. **Rate Limiting**: Control the rate of requests to avoid overwhelming the target server and to comply with usage policies.
5. **JSONL Output**: Format the results as JSON Lines for easy processing and storage.

### Common Errors and Prevention
1. **Blocking the Event Loop**: Always wrap blocking operations using `asyncio.to_thread` or `run_in_executor` to prevent blocking the event loop.
2. **Resource Leaks**: Ensure all connections and resources are properly closed or released after task completion.
3. **Insufficient Error Handling**: Implement thorough exception handling and retry logic to gracefully handle unexpected issues.

---

## Summary
This advanced `asyncio` task management micro-skill equips you with the tools to build efficient, resilient, and scalable asynchronous applications. By mastering retry mechanisms, worker pools, and event-driven frameworks, you can manage complex tasks and handle real-world challenges in network-dependent applications.