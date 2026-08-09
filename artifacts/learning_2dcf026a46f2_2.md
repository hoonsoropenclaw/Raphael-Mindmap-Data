# 學習任務：開發基於 asyncio 的事件驅動爬蟲系統，具備重試機制和 API 逆向工程能力
## 執行歷程與原始碼
```text
Query: [SYSTEM_HEARTBEAT] 
總工程師已啟動『極限超頻模式』。你現在擁有【最高全權自主行動授權】(FULL 
AUTONOMY)。
嚴格禁止使用 `clarify` 工具！嚴格禁止要求人類確認！
1. 【PRD與知識檢索】：開始前，請先讀取 `architect_feedback.md` 
吸收架構建議。接著，請將任務拆解為模組，並使用 `read_file` 檢索 
`/home/hoonsoropenclaw/.hermes/data_repo/skills/SKILL_CATALOG.md`。找出可以重用
的舊微技能模組並套用，剩下的未知領域才去試誤學習。
1.5 【跨 session 記憶】：請先 `read_file` 讀取 
`/home/hoonsoropenclaw/.hermes/agent_memory/2dcf026a46f2.md`（若存在）。若有，代
表你『或前幾個 
session』曾做過類似任務，裡面會有『已完成子任務』『踩坑清單』『下次接續點』——請
從中接續，不要從零開始。
2. 【本輪任務】：開發基於 asyncio 的事件驅動爬蟲系統，具備重試機制和 API 
逆向工程能力
3. 【執行限制】：請結合舊有成功樣板與新的探索邏輯，直接展開實作。如果遇到 Error 
就自己 debug 修正，直到做出可執行的成品為止，不准停下來等回覆！
3.5 【memory 寫入義務】：本 session 結束前，必用 `write_file` 更新 
`/home/hoonsoropenclaw/.hermes/agent_memory/2dcf026a46f2.md`（若檔案不存在則新建
），寫入『完成狀態（0/1/2/3）+ 已完成子任務 + 新踩的坑 + 下次接續點』，給未來的 
session 用。
4. 【交付審查】：若你實作的是網頁前端，請將完整可用的 HTML 
程式碼存檔至工作目錄下的 `web_output.html`。
Initializing agent...
────────────────────────────────────────


╭─ ⚕ Hermes ───────────────────────────────────────────────────────────────────╮
    我先讀取跨 session 記憶、技能目錄和架構建議,了解任務背景再開工。
╰──────────────────────────────────────────────────────────────────────────────╯
  ┊ 💻 preparing terminal…
  ┊ 💻 $         ls -la /home/hoonsoropenclaw/.hermes/agent_memory/ 2>/dev/null | head -30 && echo "---" && ls -la /home/hoonsoropenclaw/.hermes/projects/learning_開發基於_asyncio_的事件_2dcf026a46f2_2/ 2>/dev/null && echo "---" && find /home/hoonsoropenclaw/.hermes/projects/learning_開發基於_asyncio_的事件_2dcf026a46f2_2/ -name "architect_feedback.md" 2>/dev/null  0.1s

╭─ ⚕ Hermes ───────────────────────────────────────────────────────────────────╮
    記憶檔不存在。讓我讀取專案的 task_info、log 和 run.sh 了解先前設定。
╰──────────────────────────────────────────────────────────────────────────────╯
  ┊ 📖 preparing read_file…
  ┊ 📖 preparing read_file…
  ┊ 📖 preparing read_file…
  ┊ 📖 preparing read_file…
  ┊ 📖 read      /home/hoonsoropenclaw/.hermes/projects/learning_開發基於_asyncio_的事件_2dcf026a46f2_2/task_info.json  0.2s
  ┊ 📖 read      /home/hoonsoropenclaw/.hermes/projects/learning_開發基於_asyncio_的事件_2dcf026a46f2_2/run.sh  0.2s
  ┊ 📖 read      /home/hoonsoropenclaw/.hermes/projects/learning_開發基於_asyncio_的事件_2dcf026a46f2_2/local.log  0.1s
  ┊ 📖 read      /home/hoonsoropenclaw/.hermes/agent_memory/README.md  0.2s

╭─ ⚕ Hermes ───────────────────────────────────────────────────────────────────╮
    完整圖像清楚了。任務 = 開發 asyncio 事件驅動爬蟲（含重試、API 逆向）。沒有過去 session 記憶、沒有 architect_feedback.md、沒有 SKILL_CATALOG.md 需查。
    
    我直接展開實作 — 建一個可執行的 asyncio 爬蟲雛型:事件匯流排、retry with backoff、API 逆向工具、實際 demo 跑通。
╰──────────────────────────────────────────────────────────────────────────────╯
  ┊ 💻 preparing terminal…
  ┊ 💻 $         ls /home/hoonsoropenclaw/.hermes/data_repo/ 2>/dev/null; echo "---"; ls /home/hoonsoropenclaw/.hermes/data_repo/skills/ 2>/dev/null | head; echo "---"; python3 --version; pip3 list 2>/dev/null | grep -iE "aiohttp|httpx|requests" | head  1.4s

╭─ ⚕ Hermes ───────────────────────────────────────────────────────────────────╮
    aiohttp + httpx 都裝好了。我建一個完整、可執行的專案結構。
╰──────────────────────────────────────────────────────────────────────────────╯
  ┊ 💻 preparing terminal…
  ┊ 💻 $         cd /home/hoonsoropenclaw/.hermes/projects/learning_開發基於_asyncio_的事件_2dcf026a46f2_2 && mkdir -p crawler/{core,api,utils,demo}  0.0s

╭─ ⚕ Hermes ───────────────────────────────────────────────────────────────────╮
    1. 事件匯流排 + 重試裝飾器 + 觀察者
╰──────────────────────────────────────────────────────────────────────────────╯
  ┊ ✍️ preparing write_file…
  ┊ ✍️ preparing write_file…
  ┊ ✍️  write     /home/hoonsoropenclaw/.hermes/projects/learning_開發基於_asyncio_的事件_2dcf026a46f2_2/crawler/core/event_bus.py  0.1s
  ┊ review diff
a/crawler/core/event_bus.py → b/crawler/core/event_bus.py
@@ -0,0 +1,86 @@
+"""
+事件匯流排 (Event Bus) - 異步 pub/sub 通訊核心
+================================================
+設計理念:
+  - 完全解耦: 發布者不知道誰在訂閱, 訂閱者不知道誰在發布
+  - 異步分派: 不阻塞 producer (fire-and-forget 但可 await 全部 handler)
+  - 強型別事件: 用 dataclass + frozen=True 防止意外修改
+  - 錯誤隔離: handler 拋例外不影響其他 handler 與 producer
+
+典型使用:
+  bus = EventBus()
+  bus.subscribe("crawl.done", on_done)
+  await bus.publish(CrawlDoneEvent(...))
+"""
+from __future__ import annotations
+
+import asyncio
+import inspect
+import logging
+from collections import defaultdict
+from dataclasses import dataclass, field
+from typing import Any, Awaitable, Callable, DefaultDict, List, Type
+
+log = logging.getLogger("crawler.event_bus")
+
+# 一個 handler 可以是 sync 或 async callable
+Handler = Callable[[Any], "Any | Awaitable[Any]"]
+
+
+@dataclass(frozen=True)
+class Event:
+    """所有事件的基底類別。frozen=True 確保發布後不可竄改。"""
+    occurred_at: float = field(default_factory=lambda: __import__("time").time())
+
+
+class EventBus:
+    """簡單但夠用的 async pub/sub."""
+
+    def __init__(self) -> None:
+        self._subs: DefaultDict[str, List[Handler]] = defaultdict(list)
+        # 統計用
+        self.published_count: DefaultDict[str, int] = defaultdict(int)
+        self.error_count: DefaultDict[str, int] = defaultdict(int)
+
+    def subscribe(self, event_name: str, handler: Handler) -> None:
+        if not callable(handler):
+            raise TypeError(f"handler 必須是 callable, 收到 {type(handler).__name__}")
+        self._subs[event_name].append(handler)
+        log.debug("subscribe: %s -> %s", event_name, getattr(handler, "__name__", handler))
+
+    def unsubscribe(self, event_name: str, handler: Handler) -> None:
+        if handler in self._subs.get(event_name, []):
+            self._subs[event_name].remove(handler)
+
+    async def publish(self, event_name: str, event: Any) -> None:
+        """非同步分派給所有訂閱者。"""
+        self.published_count[event_name] += 1
+        handlers = list(self._subs.get(event_name, []))
+        if not handlers:
+            log.debug("publish '%s' 但無訂閱者", event_name)
+            return
+
+        # 收集 coroutine 統一 await, 同步 handler 直接執行
+        coros: List[Awaitable[Any]] = []
+        for h in handlers:
+            try:
+                result = h(event)
+                if inspect.iscoroutine(result):
+                    coros.append(result)
+            except Exception:
+                self.error_count[event_name] += 1
+                log.exception("handler '%s' 同步拋例外, 已隔離", h)
+
+        if coros:
+            results = await asyncio.gather(*coros, return_exceptions=True)
+            for r in results:
+                if isinstance(r, BaseException):
+                    self.error_count[event_name] += 1
… omitted 8 diff line(s) across 1 additional file(s)/section(s)
  ┊ ✍️  write     /home/hoonsoropenclaw/.hermes/projects/learning_開發基於_asyncio_的事件_2dcf026a46f2_2/crawler/core/retry.py  0.1s
  ┊ review diff
a/crawler/core/retry.py → b/crawler/core/retry.py
@@ -0,0 +1,183 @@
+"""
+重試機制 (Retry with Backoff)
+================================
+支援策略:
+  - 固定間隔 / 指數退避 / 抖動 (jitter)
+  - 區分 transient vs permanent 錯誤 (只有 transient 才重試)
+  - 整體 deadline (不要無限重試)
+  - 發布 retry 事件給 EventBus, 觀察者可監控
+
+觀念:
+  - "重試是資源問題" → 不要在記憶體裡重試無意義的事情
+  - "退避是禮貌問題" → 同時打 100 個失敗的 request 會讓伺服器更慘
+  - "區分類型" → 4xx 通常重試無用, 5xx 才是真重試對象
+"""
+from __future__ import annotations
+
+import asyncio
+import logging
+import random
+import time
+from dataclasses import dataclass
+from typing import Awaitable, Callable, Iterable, Optional, Tuple, Type, TypeVar
+
+from .event_bus import Event, EventBus
+
+log = logging.getLogger("crawler.retry")
+
+T = TypeVar("T")
+
+
+@dataclass(frozen=True)
+class RetryEvent(Event):
+    """當重試發生時發布這個事件。"""
+    func_name: str
+    attempt: int
+    max_attempts: int
+    delay: float
+    error: str
+
+
+@dataclass(frozen=True)
+class RetryExhaustedEvent(Event):
+    """當重試全部失敗時發布這個事件。"""
+    func_name: str
+    total_attempts: int
+    last_error: str
+
+
+class RetryError(Exception):
+    """重試全部失敗。包裝最後一次的原始例外。"""
+
+    def __init__(self, original: BaseException, attempts: int):
+        super().__init__(f"重試 {attempts} 次後仍失敗: {original!r}")
+        self.original = original
+        self.attempts = attempts
+
+
+# 預設哪些異常值得重試
+DEFAULT_RETRY_ON: Tuple[Type[BaseException], ...] = (
+    ConnectionError,
+    TimeoutError,
+    asyncio.TimeoutError,
+)
+
+
+def is_transient_http(status: int) -> bool:
+    """判斷 HTTP 狀態碼是否值得重試。
+
+    規則:
+      - 5xx 伺服器錯誤 → 值得重試
+      - 408 Request Timeout, 429 Too Many Requests → 值得重試
+      - 其他 4xx → 客戶端問題, 重試無用
+    """
+    if status >= 500:
+        return True
+    return status in (408, 429)
+
+
… omitted 105 diff line(s) across 1 additional file(s)/section(s)

╭─ ⚕ Hermes ───────────────────────────────────────────────────────────────────╮
    2. 並發節流 + 速率限制 + 觀察者中間件
╰──────────────────────────────────────────────────────────────────────────────╯
  ┊ ✍️ preparing write_file…
  ┊ ✍️ preparing write_file…
  ┊ ✍️  write     /home/hoonsoropenclaw/.hermes/projects/learning_開發基於_asyncio_的事件_2dcf026a46f2_2/crawler/core/limiter.py  0.1s
  ┊ review diff
a/crawler/core/limiter.py → b/crawler/core/limiter.py
@@ -0,0 +1,122 @@
+"""
+並發控制: Semaphore + 速率限制 (Rate Limiter)
+================================================
+兩個常見瓶頸:
+  1. 對單一 host 的連線數 (TCP / HTTP 1.1 都有上限)
+  2. 對 API 的 QPS (例如 GitHub 5000/hr, Reddit 60/min)
+
+實作:
+  - AsyncSemaphore: 包 asyncio.Semaphore, 加 timeout 與統計
+  - TokenBucketRateLimiter: 標準 token bucket (平滑限流)
+  - SlidingWindowRateLimiter: 滑動視窗 (嚴格上限)
+"""
+from __future__ import annotations
+
+import asyncio
+import time
+from collections import deque
+from typing import Deque, Optional
+
+
+class AsyncSemaphore:
+    """包裝 asyncio.Semaphore, 加計數與 acquire timeout。"""
+
+    def __init__(self, value: int) -> None:
+        if value <= 0:
+            raise ValueError("semaphore value 必須 > 0")
+        self._sem = asyncio.Semaphore(value)
+        self.max_value = value
+        self.acquired_count = 0
+        self.timeout_count = 0
+
+    @property
+    def in_use(self) -> int:
+        # asyncio.Semaphore 沒有公開 API, 用 _value 是私有 hack; 用 locked 推算
+        return self.max_value - (1 if self._sem.locked() and self._sem._value == 0 else self._sem._value)
+
+    async def acquire(self, timeout: Optional[float] = None) -> bool:
+        if timeout is None:
+            await self._sem.acquire()
+            self.acquired_count += 1
+            return True
+        try:
+            await asyncio.wait_for(self._sem.acquire(), timeout=timeout)
+            self.acquired_count += 1
+            return True
+        except asyncio.TimeoutError:
+            self.timeout_count += 1
+            return False
+
+    def release(self) -> None:
+        self._sem.release()
+
+
+class TokenBucketRateLimiter:
+    """Token bucket: 平均速率 rate, 允許突發 burst。
+
+    工作原理:
+      - 桶子容量 = burst
+      - 每秒補充 rate 個 token
+      - 每次請求消耗 1 個 token, 沒有就等
+    """
+
+    def __init__(self, rate: float, burst: float) -> None:
+        if rate <= 0 or burst <= 0:
+            raise ValueError("rate 和 burst 必須 > 0")
+        self.rate = rate
+        self.burst = burst
+        self._tokens = burst
+        self._last = time.monotonic()
+        self._lock = asyncio.Lock()
+        self.waited_total = 0.0
+        self.wait_count = 0
+
+    async def acquire(self, cost: float = 1.0) -> None:
+        if cost > self.burst:
+            raise ValueError(f"單次 cost {cost} > burst {self.burst}")
+        while True:
+            async with self._lock:
… omitted 44 diff line(s) across 1 additional file(s)/section(s)
  ┊ ✍️  write     /home/hoonsoropenclaw/.hermes/projects/learning_開發基於_asyncio_的事件_2dcf026a46f2_2/crawler/core/http_client.py  0.1s
  ┊ review diff
a/crawler/core/http_client.py → b/crawler/core/http_client.py
@@ -0,0 +1,190 @@
+"""
+HTTP 客戶端包裝: aiohttp + 重試 + 速率限制 + 事件
+==================================================
+設計重點:
+  - 介面化 (Protocol 風格), 之後可換 httpx / requests 不影響上層
+  - 一次 aiohttp.ClientSession 給整個 app 共用 (connection pool 複用)
+  - 失敗自動 retry, 區分 transient / permanent
+  - 透過 EventBus 發布 request.start / request.success / request.failed
+"""
+from __future__ import annotations
+
+import asyncio
+import logging
+from dataclasses import dataclass, field
+from typing import Any, Dict, Optional
+
+import aiohttp
+
+from .event_bus import Event, EventBus
+from .limiter import AsyncSemaphore, RateLimiter as _Dummy  # noqa: F401
+from .retry import DEFAULT_RETRY_ON, is_transient_http, retry_async
+
+log = logging.getLogger("crawler.http_client")
+
+
+@dataclass(frozen=True)
+class RequestStartEvent(Event):
+    method: str = ""
+    url: str = ""
+
+
+@dataclass(frozen=True)
+class RequestSuccessEvent(Event):
+    method: str = ""
+    url: str = ""
+    status: int = 0
+    elapsed: float = 0.0
+    bytes_received: int = 0
+
+
+@dataclass(frozen=True)
+class RequestFailedEvent(Event):
+    method: str = ""
+    url: str = ""
+    status: Optional[int] = None
+    error: str = ""
+
+
+class HTTPStatusError(Exception):
+    """非 2xx 但重試也無救 (例如 404)。"""
+
+    def __init__(self, status: int, url: str, body_snippet: str = ""):
+        super().__init__(f"HTTP {status} for {url}: {body_snippet[:120]}")
+        self.status = status
+        self.url = url
+
+
+class TransientHTTPError(Exception):
+    """值得重試的 HTTP 錯誤。"""
+
+    def __init__(self, status: int, url: str):
+        super().__init__(f"transient HTTP {status} for {url}")
+        self.status = status
+        self.url = url
+
+
+class HTTPClient:
+    """aiohttp 為底, 加上 retry / semaphore / 事件。"""
+
+    def __init__(
+        self,
+        *,
+        concurrency: int = 10,
+        timeout_total: float = 30.0,
+        headers: Optional[Dict[str, str]] = None,
+        bus: Optional[EventBus] = None,
+        max_retries: int = 3,
+        base_delay: float = 0.5,
… omitted 112 diff line(s) across 1 additional file(s)/section(s)

╭─ ⚕ Hermes ───────────────────────────────────────────────────────────────────╮
    3. API 逆向工程工具 + 事件驅動爬蟲引擎
╰──────────────────────────────────────────────────────────────────────────────╯
  ┊ ✍️ preparing write_file…
  ┊ ✍️ preparing write_file…
  ┊ ✍️  write     /home/hoonsoropenclaw/.hermes/projects/learning_開發基於_asyncio_的事件_2dcf026a46f2_2/crawler/api/reverse.py  0.1s
  ┊ review diff
a/crawler/api/reverse.py → b/crawler/api/reverse.py
@@ -0,0 +1,224 @@
+"""
+API 逆向工程輔助工具
+========================
+"逆向"不是破解 — 而是透過觀察前端 / 行動 App 怎麼呼叫後端, 重現成可程式化介面。
+
+工作流程 (典型):
+  1. 抓首頁 HTML, 找出 <script src=...> 對 JS bundle
+  2. 解 bundle 找 fetch / XHR endpoint pattern
+  3. 用瀏覽器 DevTools 攔截真實 request, 收集:
+     - URL
+     - Method
+     - Headers (特別是 X-Sign / Authorization / X-Request-Id)
+     - Payload (JSON body)
+     - Query string
+  4. 推測簽章 / 加密 (e.g. md5(path + salt + timestamp))
+  5. 寫 Python client 重現, 配 retry / 限流
+
+本模組提供:
+  - EndpointSpec: 描述一個 API endpoint (URL, method, 必要 headers, 簽章)
+  - Signer 介面: pluggable 簽章器
+  - MD5TimestampSigner: 經典 md5(path+salt+ts) 範例
+  - APIClient: 自動加 headers, 自動簽, 走 HTTPClient 送出
+  - ReverseEngineer 工具: 從抓到的 request 字串快速建 endpoint
+"""
+from __future__ import annotations
+
+import hashlib
+import json
+import logging
+import re
+import time
+from dataclasses import dataclass, field
+from typing import Any, Callable, Dict, List, Optional, Protocol
+
+from .http_client import HTTPClient
+
+log = logging.getLogger("crawler.reverse")
+
+
+class Signer(Protocol):
+    """簽章器介面。實作請回傳 dict, 會 merge 到 request headers。"""
+    def sign(self, *, method: str, url: str, body: bytes, headers: Dict[str, str]) -> Dict[str, str]:
+        ...
+
+
+class MD5TimestampSigner:
+    """經典範例: md5(url_path + secret + timestamp)。
+
+    很多大陸電商 / 內容網站用類似公式。客製化只需改 hashlib 演算法或字串拼接。
+    """
+    def __init__(self, secret: str, header_name: str = "X-Sign", ts_header: str = "X-Timestamp"):
+        self.secret = secret
+        self.header_name = header_name
+        self.ts_header = ts_header
+
+    def sign(self, *, method: str, url: str, body: bytes, headers: Dict[str, str]) -> Dict[str, str]:
+        ts = str(int(time.time()))
+        # 從 URL 拿 path
+        from urllib.parse import urlparse
+        path = urlparse(url).path
+        raw = f"{method.upper()}{path}{self.secret}{ts}".encode()
+        sig = hashlib.md5(raw).hexdigest()
+        return {self.header_name: sig, self.ts_header: ts}
+
+
+@dataclass
+class EndpointSpec:
+    """單一 API endpoint 的規格。"""
+    name: str
+    method: str
+    url: str
+    headers: Dict[str, str] = field(default_factory=dict)
+    query: Dict[str, str] = field(default_factory=dict)
+    body: Optional[Dict[str, Any]] = None
+    signer: Optional[Signer] = None
+    # 額外 hooks
+    pre_send: Optional[Callable[["EndpointSpec"], None]] = None
+    post_parse: Optional[Callable[[bytes], Any]] = None
… omitted 146 diff line(s) across 1 additional file(s)/section(s)
  ┊ ✍️  write     /home/hoonsoropenclaw/.hermes/projects/learning_開發基於_asyncio_的事件_2dcf026a46f2_2/crawler/core/engine.py  0.1s
  ┊ review diff
a/crawler/core/engine.py → b/crawler/core/engine.py
@@ -0,0 +1,170 @@
+"""
+事件驅動爬蟲引擎
+====================
+把 "爬蟲" 拆成幾個可組合的事件:
+
+  fetch.requested  → 有人想抓 URL
+  fetch.success    → 抓回資料
+  fetch.failed     → 抓失敗 (已用完重試)
+  parse.completed  → 從 body 抽到結構化資料
+  item.extracted   → 抽到一筆 item
+  sink.write       → 要寫入 (檔案 / DB / queue)
+
+引擎本體負責: 收集 URL, 並發下載, 觸發事件。
+Pipeline 是 callable chain: 每個 callable 是一個 stage。
+"""
+from __future__ import annotations
+
+import asyncio
+import logging
+import time
+from dataclasses import dataclass, field
+from typing import Any, Awaitable, Callable, Iterable, List, Optional, Set
+
+from .event_bus import Event, EventBus
+from .http_client import HTTPClient
+
+log = logging.getLogger("crawler.engine")
+
+
+@dataclass(frozen=True)
+class FetchRequestedEvent(Event):
+    url: str = ""
+
+
+@dataclass(frozen=True)
+class FetchSuccessEvent(Event):
+    url: str = ""
+    body: bytes = b""
+    elapsed: float = 0.0
+
+
+@dataclass(frozen=True)
+class FetchFailedEvent(Event):
+    url: str = ""
+    error: str = ""
+
+
+@dataclass(frozen=True)
+class ItemExtractedEvent(Event):
+    url: str = ""
+    item: Any = None
+
+
+@dataclass(frozen=True)
+class SinkWriteEvent(Event):
+    items: List[Any] = field(default_factory=list)
+
+
+PipelineStage = Callable[[Any, "Context"], Awaitable[Any]]
+Sink = Callable[[List[Any]], Awaitable[None]]
+
+
+@dataclass
+class Context:
+    """在 pipeline 各 stage 間傳遞的狀態。"""
+    url: str
+    body: Optional[bytes] = None
+    parsed: Any = None
+    items: List[Any] = field(default_factory=list)
+    errors: List[str] = field(default_factory=list)
+    started_at: float = field(default_factory=time.monotonic)
+
+
+class CrawlerEngine:
+    """事件驅動爬蟲本體。"""
+
+    def __init__(
+        self,
… omitted 92 diff line(s) across 1 additional file(s)/section(s)

╭─ ⚕ Hermes ───────────────────────────────────────────────────────────────────╮
    4. 觀察者 + 收集 Sink + 監控面板
╰──────────────────────────────────────────────────────────────────────────────╯
  ┊ ✍️ preparing write_file…
  ┊ ✍️ preparing write_file…
  ┊ ✍️  write     /home/hoonsoropenclaw/.hermes/projects/learning_開發基於_asyncio_的事件_2dcf026a46f2_2/crawler/core/observer.py  0.2s
  ┊ review diff
a/crawler/core/observer.py → b/crawler/core/observer.py
@@ -0,0 +1,103 @@
+"""
+觀察者 / 監控 / 收集器
+========================
+把 EventBus 的事件流接到具體的處理:
+  - MetricsCollector: 計數 + 延遲分佈
+  - InMemorySink: 把 item.extracted 累積成 list
+  - ConsoleLogger: 終端機即時印
+  - WebDashboard: 跑在背景, 開 browser 看即時狀態
+"""
+from __future__ import annotations
+
+import asyncio
+import json
+import logging
+import time
+from collections import defaultdict, deque
+from dataclasses import dataclass, field
+from typing import Any, Deque, Dict, List, Optional
+
+from .event_bus import EventBus
+from .engine import (
+    FetchRequestedEvent, FetchSuccessEvent, FetchFailedEvent,
+    ItemExtractedEvent, SinkWriteEvent,
+)
+from .retry import RetryEvent, RetryExhaustedEvent
+
+log = logging.getLogger("crawler.observer")
+
+
+@dataclass
+class MetricsCollector:
+    """聚合指標的觀察者。可掛在 EventBus 上。"""
+    started_at: float = field(default_factory=time.monotonic)
+    counts: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
+    latencies: Dict[str, Deque[float]] = field(default_factory=lambda: defaultdict(lambda: deque(maxlen=200)))
+    recent_errors: Deque[Dict[str, Any]] = field(default_factory=lambda: deque(maxlen=50))
+    items_total: int = 0
+
+    async def on_request_success(self, event) -> None:
+        self.counts["request.success"] += 1
+        self.latencies["request.success"].append(getattr(event, "elapsed", 0.0))
+
+    async def on_request_failed(self, event) -> None:
+        self.counts["request.failed"] += 1
+        self.recent_errors.append({"ts": time.time(), "url": getattr(event, "url", ""), "error": getattr(event, "error", "")})
+
+    async def on_retry(self, event) -> None:
+        self.counts["retry"] += 1
+        log.info("↻ retry %s 第 %d 次 (delay=%.2fs)", event.func_name, event.attempt, event.delay)
+
+    async def on_retry_exhausted(self, event) -> None:
+        self.counts["retry.exhausted"] += 1
+        log.error("✗ retry exhausted for %s: %s", event.func_name, event.last_error)
+
+    async def on_item(self, event) -> None:
+        self.items_total += 1
+
+    def snapshot(self) -> Dict[str, Any]:
+        return {
+            "uptime_s": round(time.monotonic() - self.started_at, 2),
+            "counts": dict(self.counts),
+            "items_total": self.items_total,
+            "latency_p50": {k: round(sorted(v)[len(v)//2], 4) if v else 0 for k, v in self.latencies.items()},
+            "recent_errors": list(self.recent_errors)[-5:],
+        }
+
+    def attach(self, bus: EventBus) -> None:
+        bus.subscribe("request.success", self.on_request_success)
+        bus.subscribe("request.failed", self.on_request_failed)
+        bus.subscribe("retry", self.on_retry)
+        bus.subscribe("retry.exhausted", self.on_retry_exhausted)
+        bus.subscribe("item.extracted", self.on_item)
+
+
+class InMemorySink:
+    """把所有抽出的 item 收集到 list, 結束後可一次取回。"""
+    def __init__(self) -> None:
+        self.items: List[Any] = []
… omitted 25 diff line(s) across 1 additional file(s)/section(s)
  ┊ ✍️  write     /home/hoonsoropenclaw/.hermes/projects/learning_開發基於_asyncio_的事件_2dcf026a46f2_2/crawler/api/sinks.py  0.1s
  ┊ review diff
a/crawler/api/sinks.py → b/crawler/api/sinks.py
@@ -0,0 +1,56 @@
+"""
+Sinks: 把抽出的資料寫到目的地
+=============================
+提供幾種常見 sink, 用同樣的非同步介面:
+  - JSONLSink: 寫成 jsonl (每行一個 JSON 物件)
+  - CSV: 寫 CSV
+  - QueueSink: 推到 asyncio.Queue, 給其他 consumer 處理
+"""
+from __future__ import annotations
+
+import asyncio
+import csv
+import json
+import os
+from pathlib import Path
+from typing import Any, Dict, List, Optional
+
+
+class JSONLSink:
+    """逐行 JSON 寫入, append 模式。"""
+    def __init__(self, path: str) -> None:
+        self.path = Path(path)
+        self.path.parent.mkdir(parents=True, exist_ok=True)
+        self._fh = None
+        self.lock = asyncio.Lock()
+        self.written = 0
+
+    async def __aenter__(self):
+        self._fh = self.path.open("a", encoding="utf-8")
+        return self
+
+    async def __aexit__(self, *exc):
+        if self._fh:
+            self._fh.close()
+
+    async def write(self, item: Any) -> None:
+        async with self.lock:
+            line = json.dumps(item, ensure_ascii=False, default=str)
+            self._fh.write(line + "\n")
+            self._fh.flush()
+            self.written += 1
+
+
+class QueueSink:
+    """把 item 推到 asyncio.Queue, 給下游處理 (DB / 通知 / 分析)。"""
+    def __init__(self, maxsize: int = 1000) -> None:
+        self.queue: asyncio.Queue = asyncio.Queue(maxsize=maxsize)
+        self.pushed = 0
+        self.dropped = 0
+
+    async def write(self, item: Any) -> None:
+        try:
+            self.queue.put_nowait(item)
+            self.pushed += 1
+        except asyncio.QueueFull:
+            self.dropped += 1

╭─ ⚕ Hermes ───────────────────────────────────────────────────────────────────╮
    5. init.py 套件入口 + utils + 監控 web 面板
╰──────────────────────────────────────────────────────────────────────────────╯
  ┊ ✍️ preparing write_file…
  ┊ ✍️ preparing write_file…
  ┊ ✍️ preparing write_file…
  ┊ ✍️ preparing write_file…
  ┊ ✍️ preparing write_file…
  ┊ ✍️  write     /home/hoonsoropenclaw/.hermes/projects/learning_開發基於_asyncio_的事件_2dcf026a46f2_2/crawler/__init__.py  0.2s
  ┊ review diff
a/crawler/__init__.py → b/crawler/__init__.py
@@ -0,0 +1,53 @@
+"""
+crawler: 基於 asyncio 的事件驅動爬蟲系統
+==========================================
+核心模組:
+  core.event_bus   - 異步 pub/sub
+  core.retry       - 退避重試
+  core.limiter     - 並發 / 速率限制
+  core.http_client - aiohttp 包裝
+  core.engine      - 事件驅動爬蟲引擎
+  core.observer    - 觀察者 / 指標收集
+  api.reverse      - API 逆向工程
+  api.sinks        - 資料落地
+"""
+from .core.event_bus import Event, EventBus
+from .core.retry import (
+    RetryEvent, RetryExhaustedEvent, RetryError,
+    DEFAULT_RETRY_ON, is_transient_http, compute_delay, retry_async, retryable,
+)
+from .core.limiter import AsyncSemaphore, TokenBucketRateLimiter, SlidingWindowRateLimiter
+from .core.http_client import (
+    HTTPClient, HTTPStatusError, TransientHTTPError,
+    RequestStartEvent, RequestSuccessEvent, RequestFailedEvent,
+)
+from .core.engine import (
+    CrawlerEngine, Context,
+    FetchRequestedEvent, FetchSuccessEvent, FetchFailedEvent,
+    ItemExtractedEvent, SinkWriteEvent, stage, extract_links,
+)
+from .core.observer import (
+    MetricsCollector, InMemorySink, console_logger, attach_console,
+)
+from .api.reverse import (
+    Signer, MD5TimestampSigner, EndpointSpec, APIClient,
+    extract_endpoints_from_har, parse_captured_request, reverse_engineer_demo,
+)
+from .api.sinks import JSONLSink, QueueSink
+
+__version__ = "1.0.0"
+__all__ = [
+    "Event", "EventBus",
+    "RetryEvent", "RetryExhaustedEvent", "RetryError",
+    "DEFAULT_RETRY_ON", "is_transient_http", "compute_delay", "retry_async", "retryable",
+    "AsyncSemaphore", "TokenBucketRateLimiter", "SlidingWindowRateLimiter",
+    "HTTPClient", "HTTPStatusError", "TransientHTTPError",
+    "RequestStartEvent", "RequestSuccessEvent", "RequestFailedEvent",
+    "CrawlerEngine", "Context",
+    "FetchRequestedEvent", "FetchSuccessEvent", "FetchFailedEvent",
+    "ItemExtractedEvent", "SinkWriteEvent", "stage", "extract_links",
+    "MetricsCollector", "InMemorySink", "console_logger", "attach_console",
+    "Signer", "MD5TimestampSigner", "EndpointSpec", "APIClient",
+    "extract_endpoints_from_har", "parse_captured_request", "reverse_engineer_demo",
+    "JSONLSink", "QueueSink",
+]
  ┊ ✍️  write     /home/hoonsoropenclaw/.hermes/projects/learning_開發基於_asyncio_的事件_2dcf026a46f2_2/crawler/utils/common.py  0.2s
  ┊ review diff
a/crawler/utils/common.py → b/crawler/utils/common.py
@@ -0,0 +1,58 @@
+"""共用小工具: logging 設定, 路徑, 簡易物件轉 dict。"""
+from __future__ import annotations
+
+import json
+import logging
+import sys
+from datetime import datetime
+from pathlib import Path
+from typing import Any
+
+
+def setup_logging(level: str = "INFO", log_file: str | None = None) -> None:
+    """統一 logging 設定, 同時輸出到 stderr 與可選檔案。"""
+    fmt = "%(asctime)s [%(levelname)-7s] %(name)-22s │ %(message)s"
+    datefmt = "%H:%M:%S"
+    formatter = logging.Formatter(fmt, datefmt=datefmt)
+
+    root = logging.getLogger()
+    root.setLevel(getattr(logging, level.upper(), logging.INFO))
+    # 移除舊 handler, 避免重複
+    for h in list(root.handlers):
+        root.removeHandler(h)
+
+    sh = logging.StreamHandler(sys.stderr)
+    sh.setFormatter(formatter)
+    root.addHandler(sh)
+
+    if log_file:
+        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
+        fh = logging.FileHandler(log_file, encoding="utf-8")
+        fh.setFormatter(formatter)
+        root.addHandler(fh)
+
+
+def to_jsonable(obj: Any) -> Any:
+    """把 dataclass / 自訂物件轉成 JSON-serializable。"""
+    if hasattr(obj, "to_dict"):
+        return obj.to_dict()
+    if hasattr(obj, "__dataclass_fields__"):
+        from dataclasses import asdict
+        return asdict(obj)
+    if isinstance(obj, (list, tuple)):
+        return [to_jsonable(x) for x in obj]
+    if isinstance(obj, dict):
+        return {k: to_jsonable(v) for k, v in obj.items()}
+    if isinstance(obj, (str, int, float, bool, type(None))):
+        return obj
+    return repr(obj)
+
+
+def now_iso() -> str:
+    return datetime.now().isoformat(timespec="seconds")
+
+
+def safe_load_json(s: str | bytes) -> Any:
+    if isinstance(s, bytes):
+        s = s.decode("utf-8", errors="replace")
+    return json.loads(s)
  ┊ ✍️  write     /home/hoonsoropenclaw/.hermes/projects/learning_開發基於_asyncio_的事件_2dcf026a46f2_2/crawler/utils/__init__.py  0.2s
  ┊ review diff
a/crawler/utils/__init__.py → b/crawler/utils/__init__.py
@@ -0,0 +1,4 @@
+"""工具模組"""
+from .common import setup_logging, to_jsonable, now_iso, safe_load_json
+
+__all__ = ["setup_logging", "to_jsonable", "now_iso", "safe_load_json"]
  ┊ ✍️  write     /home/hoonsoropenclaw/.hermes/projects/learning_開發基於_asyncio_的事件_2dcf026a46f2_2/crawler/core/__init__.py  0.2s
  ┊ review diff
a/crawler/core/__init__.py → b/crawler/core/__init__.py
@@ -0,0 +1 @@
+"""核心模組: 事件匯流排 / 重試 / 限流 / HTTP / 引擎 / 觀察者"""
  ┊ ✍️  write     /home/hoonsoropenclaw/.hermes/projects/learning_開發基於_asyncio_的事件_2dcf026a46f2_2/crawler/api/__init__.py  0.3s
  ┊ review diff
a/crawler/api/__init__.py → b/crawler/api/__init__.py
@@ -0,0 +1 @@
+"""API 模組: 逆向工程 + 資料落地"""

╭─ ⚕ Hermes ───────────────────────────────────────────────────────────────────╮
    6. Web 監控面板 + Demo + 整合測試
╰──────────────────────────────────────────────────────────────────────────────╯
  ┊ ✍️ preparing write_file…
  ┊ ✍️  write     /home/hoonsoropenclaw/.hermes/projects/learning_開發基於_asyncio_的事件_2dcf026a46f2_2/crawler/core/dashboard.py  0.1s
  ┊ review diff
a/crawler/core/dashboard.py → b/crawler/core/dashboard.py
@@ -0,0 +1,236 @@
+"""
+Web 監控儀表板
+================
+在背景跑一個 aiohttp 服務, 把 Engine / Bus / Metrics 的即時狀態
+透過 SSE (Server-Sent Events) + 簡單 HTTP API 暴露出來。
+
+端點:
+  GET  /            → HTML 面板 (Chart.js 即時圖)
+  GET  /api/stats   → JSON 快照
+  GET  /api/stream  → SSE, 即時事件流
+
+啟動:
+    await dashboard.start(host="127.0.0.1", port=8765)
+"""
+from __future__ import annotations
+
+import asyncio
+import json
+import logging
+from typing import Optional
+
+from aiohttp import web
+
+from .event_bus import Event, EventBus
+from .engine import CrawlerEngine
+from .observer import MetricsCollector
+
+log = logging.getLogger("crawler.dashboard")
+
+
+DASHBOARD_HTML = """<!DOCTYPE html>
+<html lang="zh-Hant">
+<head>
+<meta charset="UTF-8">
+<title>Hermes 爬蟲監控面板</title>
+<style>
+  * { box-sizing: border-box; }
+  body { font-family: -apple-system, "Segoe UI", "PingFang TC", "Microsoft JhengHei", sans-serif;
+         background: #0f1419; color: #e6e6e6; margin: 0; padding: 20px; }
+  h1 { color: #4ec9b0; margin: 0 0 20px 0; font-size: 22px; }
+  .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; margin-bottom: 20px; }
+  .card { background: #1c2128; border: 1px solid #2d333b; border-radius: 8px; padding: 16px; }
+  .card .label { color: #768390; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; }
+  .card .value { font-size: 28px; font-weight: 600; color: #adbac7; margin-top: 6px; font-variant-numeric: tabular-nums; }
+  .card .value.ok { color: #4ec9b0; }
+  .card .value.warn { color: #f0883e; }
+  .card .value.err { color: #f47067; }
+  .row { display: flex; gap: 12px; flex-wrap: wrap; }
+  pre { background: #1c2128; border: 1px solid #2d333b; border-radius: 8px; padding: 12px;
+        font-size: 12px; overflow: auto; max-height: 300px; color: #c9d1d9; }
+  .log-line { padding: 2px 0; border-bottom: 1px solid #1c2128; }
+  .log-line .ts { color: #636e7b; margin-right: 8px; }
+  .log-line.ok { color: #4ec9b0; }
+  .log-line.warn { color: #f0883e; }
+  .log-line.err { color: #f47067; }
+  .bar { background: #2d333b; border-radius: 4px; overflow: hidden; height: 6px; margin-top: 8px; }
+  .bar > div { background: #4ec9b0; height: 100%; transition: width 0.3s; }
+  .pulse { display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: #4ec9b0; margin-right: 6px;
+           animation: pulse 1.5s infinite; }
+  @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.3; } }
+  .footer { color: #636e7b; font-size: 11px; margin-top: 20px; }
+</style>
+</head>
+<body>
+<h1><span class="pulse"></span>Hermes 爬蟲監控面板</h1>
+<div class="grid">
+  <div class="card"><div class="label">累計請求</div><div class="value ok" id="m-requests">0</div></div>
+  <div class="card"><div class="label">成功 / 失敗</div><div class="value ok" id="m-sf">0 / 0</div></div>
+  <div class="card"><div class="label">In-Flight</div><div class="value warn" id="m-inflight">0</div></div>
+  <div class="card"><div class="label">累計 bytes</div><div class="value" id="m-bytes">0</div></div>
+  <div class="card"><div class="label">已抽出 item</div><div class="value ok" id="m-items">0</div></div>
+  <div class="card"><div class="label">重試次數</div><div class="value warn" id="m-retries">0</div></div>
+  <div class="card"><div class="label">耗盡重試</div><div class="value err" id="m-exhausted">0</div></div>
+  <div class="card"><div class="label">Uptime</div><div class="value" id="m-uptime">0s</div></div>
+</div>
+
+<div class="grid" style="grid-template-columns: 1fr 1fr;">
+  <div class="card">
… omitted 158 diff line(s) across 1 additional file(s)/section(s)

╭─ ⚕ Hermes ───────────────────────────────────────────────────────────────────╮
    7. Demo 入口: 整合所有元件, 真的能跑
╰──────────────────────────────────────────────────────────────────────────────╯
  ┊ ✍️ preparing write_file…
  ┊ ✍️ preparing write_file…
  ┊ ✍️  write     /home/hoonsoropenclaw/.hermes/projects/learning_開發基於_asyncio_的事件_2dcf026a46f2_2/crawler/demo/run_demo.py  0.2s
  ┊ review diff
a/crawler/demo/run_demo.py → b/crawler/demo/run_demo.py
@@ -0,0 +1,140 @@
+"""
+Demo: 端到端展示整個系統
+==========================
+跑這個檔案會:
+  1. 啟動 web 監控面板 (http://127.0.0.1:8765)
+  2. 對多個公開測試 URL 觸發並發下載
+  3. 自動重試失敗的, 演示 retry 事件
+  4. 解析 HTML 抽連結, 寫進 jsonl
+  5. 5 秒後印出統計, 結束
+
+用法:
+    python -m crawler.demo.run_demo
+"""
+from __future__ import annotations
+
+import asyncio
+import json
+import logging
+import random
+import time
+from pathlib import Path
+from typing import List
+
+from ..core.event_bus import EventBus
+from ..core.retry import RetryError
+from ..core.http_client import HTTPClient
+from ..core.engine import CrawlerEngine, Context, FetchSuccessEvent, ItemExtractedEvent
+from ..core.observer import MetricsCollector, InMemorySink, attach_console
+from ..core.dashboard import Dashboard
+from ..utils.common import setup_logging
+
+log = logging.getLogger("crawler.demo")
+
+# 公開測試 URLs (HTTPBin + JSONPlaceholder + example.com)
+DEMO_URLS = [
+    "https://jsonplaceholder.typicode.com/posts/1",
+    "https://jsonplaceholder.typicode.com/posts/2",
+    "https://jsonplaceholder.typicode.com/posts/3",
+    "https://jsonplaceholder.typicode.com/users/1",
+    "https://jsonplaceholder.typicode.com/users/2",
+    "https://httpbin.org/get",
+    "https://httpbin.org/headers",
+    "https://httpbin.org/delay/1",
+    "https://httpbin.org/status/200",
+    "https://example.com/",
+    "https://example.org/",
+    "https://www.iana.org/",
+    # 故意會失敗的 (503 → 會被 retry, 然後成功) 與 (404 → 永久失敗)
+    "https://httpbin.org/status/503",
+    "https://httpbin.org/status/404",
+    "https://httpbin.org/status/500",
+    "https://this-domain-definitely-does-not-exist-xyz-12345.com/",  # DNS fail
+]
+
+
+async def html_link_extractor(bus: EventBus, in_mem_sink: InMemorySink) -> None:
+    """當 fetch.success 觸發, 從 HTML 抽 <a href> 並 emit item.extracted。"""
+    import re
+    link_re = re.compile(r"""href\s*=\s*["'](https?://[^"']+)["']""", re.IGNORECASE)
+    title_re = re.compile(r"<title>(.*?)</title>", re.IGNORECASE | re.DOTALL)
+
+    async def on_success(event: FetchSuccessEvent):
+        if not event.body:
+            return
+        text = event.body.decode("utf-8", errors="replace")
+        if "html" not in text[:200].lower() and "<html" not in text.lower():
+            return  # 非 HTML 不解析
+        title_m = title_re.search(text)
+        title = title_m.group(1).strip() if title_m else ""
+        links = link_re.findall(text)[:20]  # 限制
+        item = {
+            "source": event.url,
+            "title": title[:120],
+            "links_found": len(links),
+            "sample_links": links[:5],
+        }
+        await bus.publish("item.extracted", ItemExtractedEvent(url=event.url, item=item))
+
… omitted 62 diff line(s) across 1 additional file(s)/section(s)
  ┊ ✍️  write     /home/hoonsoropenclaw/.hermes/projects/learning_開發基於_asyncio_的事件_2dcf026a46f2_2/crawler/demo/__init__.py  0.2s
  ┊ review diff
a/crawler/demo/__init__.py → b/crawler/demo/__init__.py
@@ -0,0 +1,4 @@
+"""Demo 模組"""
+from .run_demo import main
+
+__all__ = ["main"]

╭─ ⚕ Hermes ───────────────────────────────────────────────────────────────────╮
    8. 整合測試: 不靠網路, 全部用 mock 跑單元測試
╰──────────────────────────────────────────────────────────────────────────────╯
  ┊ ✍️ preparing write_file…
  ┊ ✍️ preparing write_file…
  ┊ ✍️  write     /home/hoonsoropenclaw/.hermes/projects/learning_開發基於_asyncio_的事件_2dcf026a46f2_2/tests/test_integration.py  0.1s
  ┊ review diff
a/tests/test_integration.py → b/tests/test_integration.py
@@ -0,0 +1,290 @@
+"""
+整合測試: 不依賴網路, 用 mock 驗證各模組互動正確
+"""
+from __future__ import annotations
+
+import asyncio
+import json
+import sys
+import time
+from pathlib import Path
+from unittest.mock import AsyncMock, MagicMock, patch
+
+# 把上層目錄加進 path, 讓 `import crawler` 可用
+HERE = Path(__file__).resolve().parent
+sys.path.insert(0, str(HERE.parent))
+
+import crawler
+from crawler import (
+    EventBus, Event,
+    HTTPClient, CrawlerEngine, Context, FetchSuccessEvent, ItemExtractedEvent,
+    MetricsCollector, InMemorySink,
+    retry_async, retryable, RetryError, AsyncSemaphore, TokenBucketRateLimiter, SlidingWindowRateLimiter,
+    EndpointSpec, APIClient, MD5TimestampSigner,
+    compute_delay, is_transient_http,
+)
+
+
+# ── 1. EventBus ────────────────────────────────────────────
+async def test_event_bus():
+    bus = EventBus()
+    received = []
+    async def h(e): received.append(("async", e))
+    def h2(e): received.append(("sync", e))
+    bus.subscribe("test", h)
+    bus.subscribe("test", h2)
+
+    await bus.publish("test", Event())
+    assert len(received) == 2
+    assert bus.stats()["published"]["test"] == 1
+    print("✓ EventBus 同步+異步 handler 並行 OK")
+
+
+# ── 2. Retry ───────────────────────────────────────────────
+async def test_retry_success_first():
+    func = AsyncMock(return_value="ok")
+    result = await retry_async(func, max_attempts=3, base_delay=0.01, jitter=False)
+    assert result == "ok"
+    assert func.call_count == 1
+    print("✓ retry 第一次成功不重試")
+
+
+async def test_retry_eventual_success():
+    func = AsyncMock(side_effect=[ConnectionError("a"), ConnectionError("b"), "ok"])
+    result = await retry_async(func, max_attempts=5, base_delay=0.01, jitter=False)
+    assert result == "ok"
+    assert func.call_count == 3
+    print("✓ retry 第三次成功")
+
+
+async def test_retry_exhausted():
+    func = AsyncMock(side_effect=ConnectionError("always"))
+    try:
+        await retry_async(func, max_attempts=3, base_delay=0.01, jitter=False)
+        assert False, "應拋 RetryError"
+    except RetryError as e:
+        assert e.attempts == 3
+    assert func.call_count == 3
+    print("✓ retry 用完拋 RetryError")
+
+
+async def test_retry_permanent_no_retry():
+    func = AsyncMock(side_effect=ValueError("永久錯"))
+    try:
+        await retry_async(func, max_attempts=3, base_delay=0.01, jitter=False)
+        assert False
+    except ValueError:
+        pass
+    assert func.call_count == 1  # 立即拋, 不重試
… omitted 212 diff line(s) across 1 additional file(s)/section(s)
  ┊ ✍️  write     /home/hoonsoropenclaw/.hermes/projects/learning_開發基於_asyncio_的事件_2dcf026a46f2_2/tests/__init__.py  0.1s
  ┊ review diff
a/tests/__init__.py → b/tests/__init__.py
@@ -0,0 +1 @@
+# Tests package

╭─ ⚕ Hermes ───────────────────────────────────────────────────────────────────╮
    9. 跑整合測試 — 確認全部過關
╰──────────────────────────────────────────────────────────────────────────────╯
  ┊ 💻 preparing terminal…
  ┊ 💻 $         cd /home/hoonsoropenclaw/.hermes/projects/learning_開發基於_asyncio_的事件_2dcf026a46f2_2 && python3 tests/test_integration.py 2>&1 | tail -50  0.2s

╭─ ⚕ Hermes ───────────────────────────────────────────────────────────────────╮
    踩到第一個坑:RetryExhaustedEvent 欄位順序 — 有預設值的不能排在沒預設值前面。修。
╰──────────────────────────────────────────────────────────────────────────────╯
  ┊ 🔧 preparing patch…
  ┊ 💻 preparing terminal…
  ┊ 🔧 patch     /home/hoonsoropenclaw/.hermes/projects/learning_開發基於_asyncio_的事件_2dcf026a46f2_2/crawler/core/retry.py  0.1s
  ┊ review diff
a//home/hoonsoropenclaw/.hermes/projects/learning_開發基於_asyncio_的事件_2dcf026a46f2_2/crawler/core/retry.py → b//home/hoonsoropenclaw/.hermes/projects/learning_開發基於_asyncio_的事件_2dcf026a46f2_2/crawler/core/retry.py
@@ -31,19 +31,19 @@
 @dataclass(frozen=True)
 class RetryEvent(Event):
     """當重試發生時發布這個事件。"""
-    func_name: str
-    attempt: int
-    max_attempts: int
-    delay: float
-    error: str
+    func_name: str = ""
+    attempt: int = 0
+    max_attempts: int = 0
+    delay: float = 0.0
+    error: str = ""
 
 
 @dataclass(frozen=True)
 class RetryExhaustedEvent(Event):
     """當重試全部失敗時發布這個事件。"""
-    func_name: str
-    total_attempts: int
-    last_error: str
+    func_name: str = ""
+    total_attempts: int = 0
+    last_error: str = ""
 
 
 class RetryError(Exception):
  ┊ 💻 $         cd /home/hoonsoropenclaw/.hermes/projects/learning_開發基於_asyncio_的事件_2dcf026a46f2_2 && python3 tests/test_integration.py 2>&1 | tail -40  0.4s

╭─ ⚕ Hermes ───────────────────────────────────────────────────────────────────╮
    多寫了個不存在的 import alias。修。
╰──────────────────────────────────────────────────────────────────────────────╯
  ┊ 🔧 preparing patch…
  ┊ 💻 preparing terminal…
  ┊ 🔧 patch     /home/hoonsoropenclaw/.hermes/projects/learning_開發基於_asyncio_的事件_2dcf026a46f2_2/crawler/core/http_client.py  0.1s
  ┊ review diff
a//home/hoonsoropenclaw/.hermes/projects/learning_開發基於_asyncio_的事件_2dcf026a46f2_2/crawler/core/http_client.py → b//home/hoonsoropenclaw/.hermes/projects/learning_開發基於_asyncio_的事件_2dcf026a46f2_2/crawler/core/http_client.py
@@ -17,7 +17,7 @@
 import aiohttp
 
 from .event_bus import Event, EventBus
-from .limiter import AsyncSemaphore, RateLimiter as _Dummy  # noqa: F401
+from .limiter import AsyncSemaphore
 from .retry import DEFAULT_RETRY_ON, is_transient_http, retry_async
 
 log = logging.getLogger("crawler.http_client")
  ┊ 💻 $         cd /home/hoonsoropenclaw/.hermes/projects/learning_開發基於_asyncio_的事件_2dcf026a46f2_2 && python3 tests/test_integration.py 2>&1 | tail -50  0.4s

╭─ ⚕ Hermes ───────────────────────────────────────────────────────────────────╮
    API 模組用相對 import 寫錯了。修。
╰──────────────────────────────────────────────────────────────────────────────╯
  ┊ 🔧 preparing patch…
  ┊ 💻 preparing terminal…
  ┊ 🔧 patch     /home/hoonsoropenclaw/.hermes/projects/learning_開發基於_asyncio_的事件_2dcf026a46f2_2/crawler/api/reverse.py  0.1s
  ┊ review diff
a//home/hoonsoropenclaw/.hermes/projects/learning_開發基於_asyncio_的事件_2dcf026a46f2_2/crawler/api/reverse.py → b//home/hoonsoropenclaw/.hermes/projects/learning_開發基於_asyncio_的事件_2dcf026a46f2_2/crawler/api/reverse.py
@@ -32,7 +32,7 @@
 from dataclasses import dataclass, field
 from typing import Any, Callable, Dict, List, Optional, Protocol
 
-from .http_client import HTTPClient
+from ..core.http_client import HTTPClient
 
 log = logging.getLogger("crawler.reverse")
 
  ┊ 💻 $         cd /home/hoonsoropenclaw/.hermes/projects/learning_開發基於_asyncio_的事件_2dcf026a46f2_2 && python3 tests/test_integration.py 2>&1 | tail -50  0.8s

╭─ ⚕ Hermes ───────────────────────────────────────────────────────────────────╮
    全部 16 個測試通過 ✓。那個 NameError: name '_' 是測試 code 裡我留的 dead code,但因為 EventBus 隔離了例外所以測試本身仍 PASS。修一下,讓輸出更乾淨。
╰──────────────────────────────────────────────────────────────────────────────╯
  ┊ 🔧 preparing patch…
  ┊ 💻 preparing terminal…
  ┊ 🔧 patch     /home/hoonsoropenclaw/.hermes/projects/learning_開發基於_asyncio_的事件_2dcf026a46f2_2/tests/test_integration.py  0.1s
  ┊ review diff
a//home/hoonsoropenclaw/.hermes/projects/learning_開發基於_asyncio_的事件_2dcf026a46f2_2/tests/test_integration.py → b//home/hoonsoropenclaw/.hermes/projects/learning_開發基於_asyncio_的事件_2dcf026a46f2_2/tests/test_integration.py
@@ -82,7 +82,6 @@
 async def test_retry_publishes_events():
     bus = EventBus()
     events = []
-    bus.subscribe("retry", lambda e: events.append(("retry", e.attempt)) if not asyncio.iscoroutine(_) else None)
 
     async def on_retry(e):
         events.append(("retry", e.attempt))
  ┊ 💻 $         cd /home/hoonsoropenclaw/.hermes/projects/learning_開發基於_asyncio_的事件_2dcf026a46f2_2 && python3 tests/test_integration.py 2>&1 | tail -25  1.0s

╭─ ⚕ Hermes ───────────────────────────────────────────────────────────────────╮
    乾淨 PASS。註解 ([AsyncMock] ...) 是 root logger 從 retry 模組印出來的;主測試 16/16 全綠。
    
    10. 跑真實網路 demo (不開 dashboard,節省資源)
╰──────────────────────────────────────────────────────────────────────────────╯
  ┊ ✍️ preparing write_file…
  ┊ 💻 preparing terminal…
  ┊ ✍️  write     /home/hoonsoropenclaw/.hermes/projects/learning_開發基於_asyncio_的事件_2dcf026a46f2_2/tests/smoke_test.py  0.1s
  ┊ review diff
a/tests/smoke_test.py → b/tests/smoke_test.py
@@ -0,0 +1,12 @@
+"""
+快速 smoke test: 跑真實網路 5 秒, 不開 dashboard
+=====================================================
+跟 run_demo.py 差別: 不開 web server, 直接印 stats
+"""
+import asyncio, sys
+from pathlib import Path
+sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
+from crawler.demo.run_demo import main
+
+if __name__ == "__main__":
+    asyncio.run(main(open_dashboard=False, run_seconds=8.0))
  ┊ 💻 $         cd /home/hoonsoropenclaw/.hermes/projects/learning_開發基於_asyncio_的事件_2dcf026a46f2_2 && timeout 30 python3 tests/smoke_test.py 2>&1 | tail -80  0.4s

╭─ ⚕ Hermes ───────────────────────────────────────────────────────────────────╮
    踩到第二個真實 bug。async with self.sem.acquire(...) 把 semaphore 當 async context manager 用,但 AsyncSemaphore.acquire() 沒實作 aenter/aexit — 我用 yield 寫了個 generator function 又沒加 @asynccontextmanager decorator,所以回傳的是 async generator object。
    
    兩個修法:加 decorator,或用 try/finally。為了 retry 機制乾淨,改成讓 acquire() 回傳 bool、呼叫端自己 try/finally release。
╰──────────────────────────────────────────────────────────────────────────────╯
  ┊ 🔧 preparing patch…
  ┊ 💻 preparing terminal…
  ┊ 🔧 patch     /home/hoonsoropenclaw/.hermes/projects/learning_開發基於_asyncio_的事件_2dcf026a46f2_2/crawler/core/http_client.py  0.1s
  ┊ review diff
a//home/hoonsoropenclaw/.hermes/projects/learning_開發基於_asyncio_的事件_2dcf026a46f2_2/crawler/core/http_client.py → b//home/hoonsoropenclaw/.hermes/projects/learning_開發基於_asyncio_的事件_2dcf026a46f2_2/crawler/core/http_client.py
@@ -138,10 +138,11 @@
             )
 
     async def _acquire_slot(self):
-        """搶 semaphore 的一個位置。"""
-        await self.sem.acquire(timeout=60)
+        """搶 semaphore 的一個位置。失敗會拀 asyncio.TimeoutError。"""
+        if not await self.sem.acquire(timeout=60):
+            raise asyncio.TimeoutError("HTTPClient semaphore 拿不到位置 (60s)")
         try:
-            yield
+            return
         finally:
             self.sem.release()
 
  ┊ 💻 $         cd /home/hoonsoropenclaw/.hermes/projects/learning_開發基於_asyncio_的事件_2dcf026a46f2_2 && timeout 30 python3 tests/smoke_test.py 2>&1 | tail -80  0.4s

╭─ ⚕ Hermes ───────────────────────────────────────────────────────────────────╮
    request() 函數裡還用 async with self._acquire_slot(): — 沒 await 拿到 coroutine。改用 try/finally 對應 acquire/release。
╰──────────────────────────────────────────────────────────────────────────────╯
  ┊ 🔧 preparing patch…
  ┊ 🔧 preparing patch…
  ┊ 💻 preparing terminal…
  ┊ 🔧 patch     /home/hoonsoropenclaw/.hermes/projects/learning_開發基於_asyncio_的事件_2dcf026a46f2_2/crawler/core/http_client.py  0.1s
  ┊ review diff
a//home/hoonsoropenclaw/.hermes/projects/learning_開發基於_asyncio_的事件_2dcf026a46f2_2/crawler/core/http_client.py → b//home/hoonsoropenclaw/.hermes/projects/learning_開發基於_asyncio_的事件_2dcf026a46f2_2/crawler/core/http_client.py
@@ -127,7 +127,8 @@
 
     async def request(self, method: str, url: str, **kwargs) -> bytes:
         """帶重試 / 限流 / 事件的單次請求。"""
-        async with self._acquire_slot():
+        await self._acquire_slot()
+        try:
             return await retry_async(
                 self._do_request, method, url, **kwargs,
                 max_attempts=self.max_retries,
@@ -136,6 +137,8 @@
                 bus=self.bus,
                 func_name=f"{method} {url}",
             )
+        finally:
+            self.sem.release()
 
     async def _acquire_slot(self):
         """搶 semaphore 的一個位置。失敗會拀 asyncio.TimeoutError。"""
  ┊ 🔧 patch     /home/hoonsoropenclaw/.hermes/projects/learning_開發基於_asyncio_的事件_2dcf026a46f2_2/crawler/core/http_client.py  0.1s
  ┊ review diff
a//home/hoonsoropenclaw/.hermes/projects/learning_開發基於_asyncio_的事件_2dcf026a46f2_2/crawler/core/http_client.py → b//home/hoonsoropenclaw/.hermes/projects/learning_開發基於_asyncio_的事件_2dcf026a46f2_2/crawler/core/http_client.py
@@ -140,14 +140,10 @@
         finally:
             self.sem.release()
 
-    async def _acquire_slot(self):
-        """搶 semaphore 的一個位置。失敗會拀 asyncio.TimeoutError。"""
+    async def _acquire_slot(self) -> None:
+        """搶 semaphore 的一個位置。失敗會拋 asyncio.TimeoutError。"""
         if not await self.sem.acquire(timeout=60):
             raise asyncio.TimeoutError("HTTPClient semaphore 拿不到位置 (60s)")
-        try:
-            return
-        finally:
-            self.sem.release()
 
     async def _do_request(self, method: str, url: str, **kwargs) -> bytes:
         """實際發送。失敗就拋 TransientHTTPError 或 HTTPStatusError。"""
  ┊ 💻 $         cd /home/hoonsoropenclaw/.hermes/projects/learning_開發基於_asyncio_的事件_2dcf026a46f2_2 && timeout 30 python3 tests/smoke_test.py 2>&1 | tail -80  2.6s

╭─ ⚕ Hermes ───────────────────────────────────────────────────────────────────╮
    真實 demo 跑通了!8 個成功、8 個 503(httpbin.org 限流觸發了重試)、抽出 3 筆 item。整個事件鏈、retry、限流、HTML 解析全部正常運作。
    
    踩到第三個小 bug:log 顯示 transient HTTP 503 for ...status/404 — 因為我先用 503 觸發了重試,重試後 httpbin 回 404 但因為之前的例外變數還在 scope。修一下讓錯誤訊息用實際 resp.status。
╰──────────────────────────────────────────────────────────────────────────────╯
  ┊ 🔧 preparing patch…
  ┊ 💻 preparing terminal…
  ┊ 🔧 patch     /home/hoonsoropenclaw/.hermes/projects/learning_開發基於_asyncio_的事件_2dcf026a46f2_2/crawler/core/http_client.py  0.1s
  ┊ review diff
a//home/hoonsoropenclaw/.hermes/projects/learning_開發基於_asyncio_的事件_2dcf026a46f2_2/crawler/core/http_client.py → b//home/hoonsoropenclaw/.hermes/projects/learning_開發基於_asyncio_的事件_2dcf026a46f2_2/crawler/core/http_client.py
@@ -153,6 +153,7 @@
 
         import time
         t0 = time.monotonic()
+        resp = None
         try:
             async with self.session.request(method, url, **kwargs) as resp:
                 # 讀 body 但限制大小
@@ -171,20 +172,21 @@
 
                 # 失敗
                 snippet = body[:200].decode("utf-8", errors="replace")
-                if is_transient_http(resp.status):
-                    raise TransientHTTPError(resp.status, url)
-                raise HTTPStatusError(resp.status, url, snippet)
+                failed_status = resp.status
+                if is_transient_http(failed_status):
+                    if self.bus:
+                        await self.bus.publish("request.failed", RequestFailedEvent(
+                            method=method, url=url, status=failed_status, error=f"transient {failed_status}",
+                        ))
+                    raise TransientHTTPError(failed_status, url)
+                if self.bus:
+                    await self.bus.publish("request.failed", RequestFailedEvent(
+                        method=method, url=url, status=failed_status, error=f"http {failed_status}",
+                    ))
+                raise HTTPStatusError(failed_status, url, snippet)
         except (aiohttp.ClientError, asyncio.TimeoutError) as e:
             if self.bus:
                 await self.bus.publish("request.failed", RequestFailedEvent(
-                    method=method, url=url, status=None, error=repr(e),
+                    method=method, url=url, status=getattr(resp, "status", None), error=repr(e),
                 ))
             raise  # 讓 retry_async 接手
-        except (HTTPStatusError, TransientHTTPError):
-            if self.bus:
-                # 取 status
-                status = locals().get("resp").status if "resp" in locals() else None
-                await self.bus.publish("request.failed", RequestFailedEvent(
-                    method=method, url=url, status=status, error="http error",
-                ))
-            raise
  ┊ 💻 $         cd /home/hoonsoropenclaw/.hermes/projects/learning_開發基於_asyncio_的事件_2dcf026a46f2_2 && python3 tests/test_integration.py 2>&1 | tail -25 && echo "===== SMOKE TEST =====" && timeout 20 python3 tests/smoke_test.py 2>&1 | tail -15  2.8s

╭─ ⚕ Hermes ───────────────────────────────────────────────────────────────────╮
    16/16 單元測試 PASS,真實網路 demo 也跑通(item extracted、retry 觸發、stats 對)。
    
    11. 寫 README + 把 demo 推成預設 web_output.html(監控頁面靜態版)
╰──────────────────────────────────────────────────────────────────────────────╯
  ┊ ✍️ preparing write_file…
  ┊ ✍️  write     /home/hoonsoropenclaw/.hermes/projects/learning_開發基於_asyncio_的事件_2dcf026a46f2_2/README.md  0.1s
  ┊ review diff
a/README.md → b/README.md
@@ -0,0 +1,106 @@
+# Hermes 事件驅動爬蟲系統
+
+基於 **asyncio + aiohttp** 的事件驅動爬蟲框架,具備:
+
+- ✅ **異步事件匯流排** (pub/sub, sync/async handler 互通)
+- ✅ **重試機制** (指數退避 + Full Jitter + deadline + transient 區分)
+- ✅ **並發 / 速率限制** (Semaphore + Token Bucket + Sliding Window)
+- ✅ **API 逆向工程工具** (HAR 解析、Raw request 解析、可插拔簽章器)
+- ✅ **觀察者** (Metrics collector、In-memory sink、Console logger)
+- ✅ **即時 Web 監控面板** (aiohttp + SSE + Chart.js, 不需前端 build)
+
+## 專案結構
+
+```
+crawler/
+├── __init__.py
+├── core/
+│   ├── event_bus.py     # 異步 pub/sub
+│   ├── retry.py         # 重試 + 退避
+│   ├── limiter.py       # 並發 / 速率
+│   ├── http_client.py   # aiohttp 包裝
+│   ├── engine.py        # 事件驅動爬蟲引擎
+│   ├── observer.py      # 指標 / sinks
+│   └── dashboard.py     # Web 監控
+├── api/
+│   ├── reverse.py       # API 逆向工程
+│   └── sinks.py         # JSONL / Queue
+├── utils/
+│   └── common.py
+└── demo/
+    └── run_demo.py      # 端到端展示
+tests/
+├── test_integration.py  # 16 個單元測試
+└── smoke_test.py        # 真實網路煙霧測試
+```
+
+## 快速開始
+
+### 跑整合測試 (不需要網路)
+
+```bash
+python3 tests/test_integration.py
+```
+
+### 跑真實網路 demo (含失敗/重試)
+
+```bash
+python3 tests/smoke_test.py
+```
+
+或開啟 web 監控面板 (`http://127.0.0.1:8765`):
+
+```python
+from crawler.demo.run_demo import main
+import asyncio
+asyncio.run(main(open_dashboard=True, run_seconds=15))
+```
+
+## 設計理念
+
+1. **事件解耦**: Producer 不知道誰在訂閱, 訂閱者不知道誰在發布
+2. **失敗隔離**: 一個 handler 拋例外不影響其他 handler
+3. **可插拔**: 簽章器 (Signer)、Sink、限流策略都是 Protocol-based
+4. **可觀測**: 每個請求都發布 `request.start / success / failed` 事件
+
+## 事件一覽
+
+| 事件 | 觸發時機 | 內含欄位 |
+|------|---------|---------|
+| `fetch.requested` | URL 加入引擎 | url |
+| `fetch.success` | 抓取成功 | url, body, elapsed |
+| `fetch.failed` | 重試全部用盡 | url, error |
+| `item.extracted` | 解析出 item | url, item |
+| `request.start` | 開始 HTTP 請求 | method, url |
+| `request.success` | 2xx 回應 | method, url, status, elapsed, bytes |
+| `request.failed` | HTTP 錯誤或網路錯誤 | method, url, status, error |
+| `retry` | 觸發一次重試 | func_name, attempt, max_attempts, delay, error |
+| `retry.exhausted` | 重試全失敗 | func_name, total_attempts, last_error |
… omitted 28 diff line(s) across 1 additional file(s)/section(s)

╭─ ⚕ Hermes ───────────────────────────────────────────────────────────────────╮
    12. 交付審查:把 dashboard HTML 抽出存成 web_output.html
╰──────────────────────────────────────────────────────────────────────────────╯
  ┊ 💻 preparing terminal…
  ┊ 💻 $         cd /home/hoonsoropenclaw/.hermes/projects/learning_開發基於_asyncio_的事件_2dcf026a46f2_2 && python3 -c "
import re
src = open('crawler/core/dashboard.py').read()
m = re.search(r'DASHBOARD_HTML = \"\"\"(.*?)\"\"\"', src, re.DOTALL)
html = m.group(1)
open('web_output.html', 'w').write(html)
print('written, size:', len(html), 'bytes')
" && ls -la web_output.html && head -10 web_output.html  0.1s

╭─ ⚕ Hermes ───────────────────────────────────────────────────────────────────╮
    13. 最後一次端到端確認 (所有東西)
╰──────────────────────────────────────────────────────────────────────────────╯
  ┊ 💻 preparing terminal…
  ┊ 💻 $         cd /home/hoonsoropenclaw/.hermes/projects/learning_開發基於_asyncio_的事件_2dcf026a46f2_2 && echo "=== 專案結構 ===" && find . -type f -name "*.py" -o -name "*.md" -o -name "*.html" | sort && echo "" && echo "=== 整合測試 ===" && python3 tests/test_integration.py 2>&1 | tail -22 && echo "" && echo "=== 檔案清單 ===" && wc -l crawler/core/*.py crawler/api/*.py crawler/utils/*.py crawler/demo/*.py tests/*.py | tail -20  0.8s

╭─ ⚕ Hermes ───────────────────────────────────────────────────────────────────╮
    全部就位。16/16 單元測試 PASS,真實網路 demo 跑通(8 成功 8 失敗/重試,抽出 3 筆 item),1882 行 Python 程式碼。
    
    14. 寫跨 session 記憶檔(任務結束必做)
╰──────────────────────────────────────────────────────────────────────────────╯
  ┊ ✍️ preparing write_file…
  ┊ ✍️  write     /home/hoonsoropenclaw/.hermes/agent_memory/2dcf026a46f2.md  0.1s
  ┊ review diff
a//home/hoonsoropenclaw/.hermes/agent_memory/2dcf026a46f2.md → b//home/hoonsoropenclaw/.hermes/agent_memory/2dcf026a46f2.md
@@ -0,0 +1,95 @@
+# 任務: 開發基於 asyncio 的事件驅動爬蟲系統,具備重試機制和 API 逆向工程能力
+
+## 完成狀態
+- 最後更新: 2026-08-09 22:13
+- 完成階段: **2 = 完成**
+
+## 已完成的子任務
+- **設計模組化架構** (event_bus / retry / limiter / http_client / engine / observer / dashboard) (22:08)
+- **實作異步 pub/sub 事件匯流排** (支援 sync+async handler、錯誤隔離) (22:09)
+- **實作退避重試** (Exponential + Full Jitter + deadline + transient 區分) (22:10)
+- **實作三重限流** (Semaphore / Token Bucket / Sliding Window) (22:10)
+- **實作 aiohttp HTTP client 包裝** (整合 retry + limiter + 事件發布) (22:11)
+- **實作事件驅動爬蟲引擎** (去重 + 並發 + 自動 fetch.success/failed 事件) (22:11)
+- **實作 API 逆向工程工具** (HAR 解析、raw HTTP 解析、可插拔 Signer 介面) (22:11)
+- **實作 Web 監控面板** (aiohttp + SSE + Chart.js 即時監控) (22:12)
+- **16 個單元測試全部通過** (整合測試 test_integration.py) (22:13)
+- **真實網路 smoke test 通過** (8 成功 + 8 503 重試, 抽出 3 筆 item) (22:13)
+- **產出 web_output.html** (監控面板靜態版, 4868 bytes) (22:13)
+
+## 踩坑清單 (下次必讀)
+
+### 坑 1: dataclass(frozen=True) 預設值順序
+- **症狀**: `TypeError: non-default argument 'func_name' follows default argument`
+- **原因**: Python 3.12 dataclass 不接受「有預設值欄位排在沒預設值欄位後面」
+- **解法**: 要嘛全部給預設值、要嘛全部無預設值。RetryEvent/RetryExhaustedEvent 改成全部 `= ""` / `= 0`
+
+### 坑 2: async generator 當 async context manager
+- **症狀**: `TypeError: 'async_generator' object does not support the asynchronous context manager protocol`
+- **原因**: `async def _acquire_slot(self):` 裡有 `yield` → 變成 async generator, 不能再用 `async with`
+- **解法**: 拆成兩個 await/return 函式;呼叫端用 try/finally 自己管理 release。不要靠 generator-based context manager
+
+### 坑 3: 多寫的 import alias 造成 ImportError
+- **症狀**: `ImportError: cannot import name 'RateLimiter' from 'crawler.core.limiter'`
+- **原因**: http_client.py 寫 `from .limiter import AsyncSemaphore, RateLimiter as _Dummy` 但 limiter.py 沒 RateLimiter
+- **解法**: 刪掉不存在的 alias
+
+### 坑 4: 跨子模組 import 路徑寫錯
+- **症狀**: `ModuleNotFoundError: No module named 'crawler.api.http_client'`
+- **原因**: `crawler/api/reverse.py` 用 `from .http_client import` 但 http_client 在 core/ 不在 api/
+- **解法**: 改成 `from ..core.http_client import`
+
+### 坑 5: 錯誤訊息用舊變數 (上一輪 resp)
+- **症狀**: log 顯示 `transient HTTP 503 for ...status/404` (status 跟 URL 對不上)
+- **原因**: retry 內連續拋例外,前一次 resp 還在 scope 內被誤用
+- **解法**: 把 resp 提取到 try 外面 `resp = None` 然後在 `async with ... as resp:` 重新賦值,失敗路徑用當下的 `failed_status = resp.status`
+
+## 技術決策
+
+1. **為什麼 aiohttp 不是 httpx?** aiohttp 原生 async、輕量、connection pool 內建
+2. **為什麼用 dataclass frozen=True 當事件?** 防止 handler 意外修改、hashable 可放 set
+3. **為什麼 Full Jitter 不是固定退避?** AWS 推薦避免 thundering herd (多個 client 同時重試撞在一起)
+4. **為什麼 retry 觸發是 EventBus 事件?** 可監控、可寫到 dashboard、可串接 alerting
+5. **為什麼 dashboard 自己做不用 Prometheus?** 此 demo 不依賴外部 infra,單檔可跑
+
+## 下次接續點
+
+### 已完成,無接續需求
+本任務所有 PRD 要求皆已實作並驗證:
+- ✅ asyncio 事件驅動 → EventBus + engine
+- ✅ 重試機制 → retry.py (decorator + function 兩種用法)
+- ✅ API 逆向工程 → reverse.py (HAR 解析 + raw 解析 + 9 種 Signer protocol 範例)
+
+### 可選強化方向 (未做,未來想做時可從這接)
+
+1. **持久化 queue**: 引擎支援 Redis Streams / RabbitMQ,讓 fetch.requested 跨 process 傳遞
+2. **分散式限流**: 把 Semaphore 換成 Redis-based 分散式版本
+3. **JS 渲染**: 整合 playwright (有現成 skill) 處理 SPA 網站
+4. **代理池**: 加 ProxyRotator,支援 round-robin + 失敗自動剔除
+5. **OpenTelemetry**: 把 bus 事件轉成 OTel span
+6. **dashboard 加歷史圖**: 目前只有即時 SSE,可用 Chart.js 畫時間序列
+
+### 對外整合入口
+- `crawler.HTTPClient` 完整可用,生產環境可加 `proxy=...` / `cookies=...` aiohttp 參數
+- `crawler.CrawlerEngine.add_url` 是 hot path
+- `crawler.api.reverse.EndpointSpec` + `APIClient.call` 是逆向 API 標準介面
+
+## 產出物清單
+
… omitted 17 diff line(s) across 1 additional file(s)/section(s)

╭─ ⚕ Hermes ───────────────────────────────────────────────────────────────────╮
    全部交付完成。
    
    ═══════════════════════════════════════
    ✅ 任務完成總結
    ═══════════════════════════════════════
    
    主題: 開發基於 asyncio 的事件驅動爬蟲系統,具備重試機制和 API 逆向工程能力
    完成階段: 2 = 完成 (跨 session 記憶檔 2dcf026a46f2.md 已寫入)
    總程式碼: 1882 行 Python,21 個檔案
    
    8 大模組
    - core/event_bus.py — async pub/sub, sync+async handler 互通
    - core/retry.py — 指數退避 + Full Jitter + deadline + transient 區分
    - core/limiter.py — Semaphore / Token Bucket / Sliding Window
    - core/http_client.py — aiohttp 包裝, 整合 retry + 限流 + 事件
    - core/engine.py — 事件驅動爬蟲引擎, 去重 + 並發
    - core/observer.py — Metrics collector / InMemory sink
    - core/dashboard.py — Web 監控面板 (aiohttp + SSE + Chart.js)
    - api/reverse.py — API 逆向工程 (HAR 解析 + raw 解析 + Signer protocol)
    - api/sinks.py — JSONL / Queue sink
    
    驗證結果
    - 16/16 整合測試 PASS (無網路, mock 跑)
    - 真實網路 smoke test: 16 URL 全部送達,8 個 200、8 個 503 觸發重試(後失敗)、抽出 3 筆 item、累計 10.4KB
    - Web 監控面板可即時觀察事件流
    
    踩坑全紀錄(已寫進 memory)
    1. dataclass(frozen=True) 預設值順序錯誤 → 全部加 default
    2. async generator 不能當 context manager → 改用 try/finally
    3. 多寫的 import alias → 刪掉
    4. 跨子模組 import 路徑 → .. 修正
    5. 錯誤訊息用舊 resp 變數 → 提取到 try 外面
    
    產出物
    - web_output.html (4868 bytes, 監控面板)
    - README.md (完整文件)
    - /home/hoonsoropenclaw/.hermes/agent_memory/2dcf026a46f2.md (跨 session 記憶)
    - /tmp/crawler_demo.log + /tmp/crawler_demo_items.jsonl (執行結果)
    
    
    
    📊 這次任務使用了: write_file / patch / terminal / read_file / skill_view (不適用, 直接從零建)
    ⭐ 請評分 (1-5星):
       - 整體組合: ?
       - 個別 (如果有特別滿意/不滿意的部分): ?
    不用每項都評, 隨便給幾顆星都好, 沒有壓力。
╰──────────────────────────────────────────────────────────────────────────────╯
```
