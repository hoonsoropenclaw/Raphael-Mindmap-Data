# Event Bus Async Pub/Sub

## 說明
實現一個基於 `asyncio` 的事件總線，支持多訂閱者接收事件、事件扇出（fan-out）以及歷史快照功能。

## 關鍵代碼片段
```python
from collections import deque
from typing import AsyncGenerator

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

## 常見錯誤及避免方法
- **訂閱者未正確清理導致內存洩漏**：確保在訂閱者斷開連接時，訂閱隊列被正確移除。使用 `try...finally` 塊來保證清理邏輯的執行。
- **阻塞 I/O 操作影響事件總線性能**：避免在事件處理過程中使用阻塞操作，必要時使用 `asyncio.to_thread` 將阻塞操作移至線程池。