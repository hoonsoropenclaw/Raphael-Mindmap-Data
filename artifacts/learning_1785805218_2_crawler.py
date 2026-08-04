"""
BeautifulSoup + Playwright 動態網頁抓取與解析工具組 (v1.0)
============================================================
模組架構（對應《總工程師審查回饋 v58》核准的爬蟲技能藍圖）:

    1. StaticCrawler      —— BeautifulSoup + urllib;無 JS、輕量
    2. DynamicCrawler     —— Playwright sync API;處理 JS 渲染
    3. AsyncDynamicCrawler—— Playwright async API;並行抓取多頁
    4. HybridSmartCrawler —— 啟發式判斷「靜態 or 動態」並自動派工
    5. DataExtractor      —— BeautifulSoup 解析為結構化 records
    6. RetryPolicy        —— 指數退避 (exponential backoff) 含 Jitter
    7. CrawlResult        —— 統一資料結構(static / dynamic / hybrid 結果一致)

規範來源（已內化為本模組的設計原則）:
- skills/data_crawling_extraction_and_visualization.md
- skills/headless_browser_management.md
- skills/playwright_browser_lifecycle.md
- skills/trial-and-error/references/by-category/browser-automation.md
- 總工程師審查回饋 v58: "爬蟲與資料抓取模組必須設計得夠強健,具備重試機制"

使用範例:
    python crawler.py                  # 執行內建 demo
    python crawler.py --target URL     # 對單一 URL 進行 hybrid 抓取
    python crawler.py --urls U1,U2     # 並行抓取多個 URL
"""

from __future__ import annotations

import asyncio
import json
import random
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Iterable

# ---------------------------------------------------------------------------
# 第三方套件
# ---------------------------------------------------------------------------
try:
    from bs4 import BeautifulSoup, Tag
except ImportError as e:  # pragma: no cover
    raise SystemExit(
        "缺少 beautifulsoup4。請先執行: pip install beautifulsoup4 lxml"
    ) from e

try:
    from playwright.sync_api import (
        Page,
        TimeoutError as PWTimeoutError,
        sync_playwright,
    )
    from playwright.async_api import async_playwright
    _PLAYWRIGHT_READY = True
except Exception:  # chromium binaries not installed etc.
    _PLAYWRIGHT_READY = False

# ---------------------------------------------------------------------------
# 常數
# ---------------------------------------------------------------------------
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 "
    "RaphaelCrawler/1.0"
)
DEFAULT_TIMEOUT_S = 25
DEMO_URLS: list[str] = [
    "https://quotes.toscrape.com/",                      # 靜態 SSR
    "https://en.wikipedia.org/wiki/Web_scraping",       # 靜態 SSR
    "https://httpbin.org/html",                          # 純 HTML
]


# ===========================================================================
# 0. CrawlResult —— 統一結果結構
# ===========================================================================
@dataclass
class CrawlResult:
    """所有爬取模式的統一結果容器。"""
    url: str
    mode: str                          # static | dynamic | hybrid
    status: str                        # ok | fail
    http_code: int | None = None
    title: str = ""
    fetched_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    elapsed_ms: float = 0.0
    attempt: int = 1
    final_url: str = ""                # 重定向後的 URL
    html: str = ""
    text: str = ""
    records: list[dict[str, Any]] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        # 別把整份 HTML 序列化到 JSON,僅留長度與前 500 char 預覽
        if len(d.get("html", "")) > 500:
            d["html_preview"] = d["html"][:500]
            d["html_len"] = len(d["html"])
            del d["html"]
        return d


# ===========================================================================
# 1. RetryPolicy —— 指數退避 + Jitter（抵擋 thundering herd）
# ===========================================================================
@dataclass
class RetryPolicy:
    """指數退避策略;每次失敗時 sleep = min(cap, base * 2^attempt) ± jitter。"""
    max_attempts: int = 3
    base_delay_s: float = 0.4
    cap_delay_s: float = 4.0
    jitter_ratio: float = 0.25

    def sleep_for(self, attempt: int) -> float:
        # attempt: 第幾次失敗(1-based)
        delay = min(self.cap_delay_s, self.base_delay_s * (2 ** (attempt - 1)))
        jitter = delay * self.jitter_ratio
        return max(0.0, delay + random.uniform(-jitter, jitter))

    def run(self, fn: Callable[[], CrawlResult]) -> CrawlResult:
        last: CrawlResult | None = None
        for attempt in range(1, self.max_attempts + 1):
            result = fn()
            result.attempt = attempt
            if result.status == "ok":
                return result
            last = result
            if attempt < self.max_attempts:
                wait = self.sleep_for(attempt)
                time.sleep(wait)
        # exhausted
        assert last is not None
        return last


# ===========================================================================
# 2. StaticCrawler —— BeautifulSoup + urllib（無 JS 開銷）
# ===========================================================================
class StaticCrawler:
    """無 JS 渲染頁面用,使用 urllib + BeautifulSoup。

    適合:server-side rendering 的網頁,如 Wikipedia、quotes.toscrape、新聞網站等。
    優點:資源開銷極低,單次請求 < 200ms,適合大規模並行抓取。
    限制:無法處理 React/Vue SPA 等需 JS 觸發的內容。
    """

    def __init__(self, timeout_s: float = DEFAULT_TIMEOUT_S, retry: RetryPolicy | None = None):
        self.timeout_s = timeout_s
        self.retry = retry or RetryPolicy()

    def _http_get(self, url: str) -> tuple[int, str, str]:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept-Language": "en-US,en;q=0.9,zh-TW;q=0.8"})
        with urllib.request.urlopen(req, timeout=self.timeout_s) as resp:
            body = resp.read()
            charset = resp.headers.get_content_charset() or "utf-8"
            try:
                html = body.decode(charset, errors="replace")
            except LookupError:
                html = body.decode("utf-8", errors="replace")
            return resp.status, html, resp.geturl()

    def fetch(self, url: str) -> CrawlResult:
        """同步抓取靜態頁面;回傳統一 CrawlResult。"""
        start = time.perf_counter()
        try:
            code, html, final = self._http_get(url)
            soup = BeautifulSoup(html, "lxml")
            title = (soup.title.string if soup.title and soup.title.string else "").strip()
            return CrawlResult(
                url=url, mode="static", status="ok",
                http_code=code, title=title,
                elapsed_ms=(time.perf_counter() - start) * 1000,
                final_url=final,
                html=html, text=soup.get_text(" ", strip=True),
                metrics={
                    "html_len": len(html),
                    "tag_count": len(soup.find_all()),
                    "link_count": len(soup.find_all("a", href=True)),
                    "image_count": len(soup.find_all("img", src=True)),
                    "h1": [h.get_text(strip=True) for h in soup.find_all("h1")][:5],
                },
            )
        except (urllib.error.HTTPError, urllib.error.URLError) as e:
            err_msg = f"{type(e).__name__}: {getattr(e, 'reason', e)}"
            return CrawlResult(
                url=url, mode="static", status="fail",
                elapsed_ms=(time.perf_counter() - start) * 1000,
                errors=[err_msg],
            )
        except Exception as e:  # 防呆:任何未預期錯誤
            return CrawlResult(
                url=url, mode="static", status="fail",
                elapsed_ms=(time.perf_counter() - start) * 1000,
                errors=[f"{type(e).__name__}: {e}"],
            )


# ===========================================================================
# 3. DynamicCrawler —— Playwright sync API（JS 渲染頁面專用）
# ===========================================================================
class DynamicCrawler:
    """用 Playwright 觸發 JS 渲染後再回傳完整 DOM。

    適合:SPA / 動態載入 / 需 scroll-to-load / 需 cookie 的網站。
    啟發式觸發條件(見 HybridSmartCrawler):
      - <body> 內文字少於閾值
      - 含有 angular / react / vue / next-data 等 script
      - 含有<div id="root"> / <div id="app"> 之類 SPA 容器
    """

    def __init__(self, headless: bool = True, timeout_ms: int = 25_000):
        if not _PLAYWRIGHT_READY:
            raise RuntimeError("Playwright Python bindings not available")
        self.headless = headless
        self.timeout_ms = timeout_ms

    def _launch_options(self) -> dict[str, Any]:
        # 從 trial-and-error/browser-automation.md:chromium 在 headless 容器需 --no-sandbox
        return {
            "headless": self.headless,
            "args": [
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
            ],
        }

    def fetch(self, url: str, wait_selector: str | None = None, scroll: bool = False) -> CrawlResult:
        start = time.perf_counter()
        if not _PLAYWRIGHT_READY:
            return CrawlResult(url=url, mode="dynamic", status="fail", errors=["Playwright not installed"])
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(**self._launch_options())
                try:
                    ctx = browser.new_context(
                        user_agent=USER_AGENT,
                        viewport={"width": 1366, "height": 900},
                        ignore_https_errors=True,
                    )
                    page: Page = ctx.new_page()
                    page.set_default_timeout(self.timeout_ms)
                    page.goto(url, wait_until="domcontentloaded", timeout=self.timeout_ms)
                    # 等到指定的關鍵選擇器(若有),或 networkidle(預設)等 JS 收尾
                    try:
                        page.wait_for_load_state("networkidle", timeout=self.timeout_ms)
                    except PWTimeoutError:
                        # 動態站常駐 long-poll,允許繼續
                        pass
                    if wait_selector:
                        try:
                            page.wait_for_selector(wait_selector, timeout=self.timeout_ms)
                        except PWTimeoutError as e:
                            return CrawlResult(
                                url=url, mode="dynamic", status="fail",
                                elapsed_ms=(time.perf_counter() - start) * 1000,
                                errors=[f"Selector timeout: {wait_selector} ({e})"],
                            )
                    if scroll:
                        # 無限滾動式載入:逐段 scroll 直到 scrollHeight 不再增加
                        self._infinite_scroll(page)
                    html = page.content()
                    final = page.url
                    title = page.title()
                    browser.close()  # 放 ctx 之前 close,browser 也會清掉所有 context
                    return self._build_result(url, html, final, title, start)
                finally:
                    # try/finally 防資源洩漏(from playwright_browser_lifecycle)
                    try:
                        browser.close()
                    except Exception:
                        pass
        except Exception as e:
            return CrawlResult(
                url=url, mode="dynamic", status="fail",
                elapsed_ms=(time.perf_counter() - start) * 1000,
                errors=[f"{type(e).__name__}: {e}"],
            )

    @staticmethod
    def _infinite_scroll(page: Page, max_steps: int = 8, pause_ms: int = 700) -> None:
        prev = 0
        for _ in range(max_steps):
            page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
            page.wait_for_timeout(pause_ms)
            cur = page.evaluate("document.body.scrollHeight")
            if cur == prev:
                break
            prev = cur

    @staticmethod
    def _build_result(url: str, html: str, final: str, title: str, start: float) -> CrawlResult:
        soup = BeautifulSoup(html, "lxml")
        return CrawlResult(
            url=url, mode="dynamic", status="ok",
            title=title, final_url=final,
            elapsed_ms=(time.perf_counter() - start) * 1000,
            html=html,
            text=soup.get_text(" ", strip=True),
            metrics={
                "html_len": len(html),
                "tag_count": len(soup.find_all()),
                "link_count": len(soup.find_all("a", href=True)),
                "image_count": len(soup.find_all("img", src=True)),
                "h1": [h.get_text(strip=True) for h in soup.find_all("h1")][:5],
            },
        )


# ===========================================================================
# 4. AsyncDynamicCrawler —— Playwright async API;並行多頁
# ===========================================================================
class AsyncDynamicCrawler:
    """並行版本:用單一 browser 跑多 page context(資源復用)。

    為什麼需要這個?當需要對 20~100 個子頁面並行抓取時,每個 page 各開一個
    browser 太貴;共一個 browser + 多 context 是最佳實踐。
    """

    def __init__(self, headless: bool = True, timeout_ms: int = 25_000, concurrency: int = 4):
        if not _PLAYWRIGHT_READY:
            raise RuntimeError("Playwright Python bindings not available")
        self.headless = headless
        self.timeout_ms = timeout_ms
        self.concurrency = concurrency

    async def _fetch_one(self, browser, url: str, semaphore: asyncio.Semaphore) -> CrawlResult:
        start = time.perf_counter()
        async with semaphore:
            ctx = await browser.new_context(user_agent=USER_AGENT, viewport={"width": 1366, "height": 900})
            try:
                page = await ctx.new_page()
                page.set_default_timeout(self.timeout_ms)
                try:
                    await page.goto(url, wait_until="domcontentloaded", timeout=self.timeout_ms)
                    try:
                        await page.wait_for_load_state("networkidle", timeout=self.timeout_ms)
                    except Exception:
                        pass
                    html = await page.content()
                    title = await page.title()
                    final = page.url
                    soup = BeautifulSoup(html, "lxml")
                    return CrawlResult(
                        url=url, mode="dynamic", status="ok",
                        title=title, final_url=final,
                        elapsed_ms=(time.perf_counter() - start) * 1000,
                        html=html, text=soup.get_text(" ", strip=True),
                        metrics={
                            "html_len": len(html),
                            "tag_count": len(soup.find_all()),
                            "link_count": len(soup.find_all("a", href=True)),
                        },
                    )
                except Exception as e:
                    return CrawlResult(
                        url=url, mode="dynamic", status="fail",
                        elapsed_ms=(time.perf_counter() - start) * 1000,
                        errors=[f"{type(e).__name__}: {e}"],
                    )
            finally:
                await ctx.close()

    async def fetch_many(self, urls: list[str]) -> list[CrawlResult]:
        if not _PLAYWRIGHT_READY:
            return [CrawlResult(url=u, mode="dynamic", status="fail", errors=["Playwright not installed"]) for u in urls]
        launch_opts = {
            "headless": self.headless,
            "args": ["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage", "--disable-gpu"],
        }
        sem = asyncio.Semaphore(self.concurrency)
        async with async_playwright() as p:
            browser = await p.chromium.launch(**launch_opts)
            try:
                tasks = [self._fetch_one(browser, u, sem) for u in urls]
                return await asyncio.gather(*tasks)
            finally:
                await browser.close()

    def fetch_sync(self, urls: list[str]) -> list[CrawlResult]:
        return asyncio.run(self.fetch_many(urls))


# ===========================================================================
# 5. HybridSmartCrawler —— 啟發式自動派工
# ===========================================================================
class HybridSmartCrawler:
    """先以輕量靜態抓取試探;若頁面疑似 SPA / JS-only,就 upgrade 到動態。

    啟發式條件(任何一項成立 → 升級為 dynamic):
      - 靜態 HTML < 12 KB 且 <body> 內文字 < 800 字
      - 包含 'ng-app' / 'data-reactroot' / 'id="root"' / 'id="app"' / '__NEXT_DATA__'
      - <noscript> 內容遠大於 <body> 文字(SSR fallback 很大)
    """

    def __init__(self, headless: bool = True, timeout_ms: int = 25_000,
                 upgrade_threshold_chars: int = 800, upgrade_threshold_bytes: int = 12_000):
        self.static = StaticCrawler()
        self.dynamic = DynamicCrawler(headless=headless, timeout_ms=timeout_ms)
        self.upgrade_threshold_chars = upgrade_threshold_chars
        self.upgrade_threshold_bytes = upgrade_threshold_bytes

    @staticmethod
    def _looks_like_spa(soup: BeautifulSoup, html: str) -> tuple[bool, list[str]]:
        reasons: list[str] = []
        body_text = soup.body.get_text(" ", strip=True) if soup.body else ""
        if len(html) < 12_000 and len(body_text) < 800:
            reasons.append(f"small_payload(html={len(html)},text={len(body_text)})")
        low = html.lower()
        spa_markers = [
            ("ng-app", "ng-app"),
            ("data-reactroot", "react"),
            ('id="root"', "react#root"),
            ('id="app"', "vue#/app"),
            ("__next_data__", "next.js"),
            ("window.__nuxt__", "nuxt.js"),
            ("window.__remixContext", "remix"),
        ]
        for marker, label in spa_markers:
            if marker in low:
                reasons.append(label)
                break  # 一個就夠
        if soup.find("noscript"):
            ns_text = soup.noscript.get_text(" ", strip=True)
            if len(ns_text) > len(body_text) + 500:
                reasons.append("noscript>body")
        return (len(reasons) > 0, reasons)

    def fetch(self, url: str) -> CrawlResult:
        # 1) 嘗試 static
        sres = self.static.fetch(url)
        if sres.status == "fail":
            # 連不上 → 試 dynamic(說不定是因為 user-agent / cookie)
            dres = self.dynamic.fetch(url)
            dres.mode = "hybrid"
            dres.errors.insert(0, f"static_failed:{sres.errors}")
            dres.metrics["dispatch_log"] = ["static_fail", "dynamic_ok"]
            return dres
        soup = BeautifulSoup(sres.html, "lxml")
        is_spa, reasons = self._looks_like_spa(soup, sres.html)
        if not is_spa:
            sres.mode = "hybrid"
            sres.metrics["dispatch_log"] = ["static_ok"]
            sres.metrics["dispatch_reasons"] = []
            return sres
        # 2) 升級 dynamic
        dres = self.dynamic.fetch(url)
        dres.mode = "hybrid"
        dres.metrics["dispatch_log"] = ["static_ok_suspect", "dynamic_ok"]
        dres.metrics["dispatch_reasons"] = reasons
        if dres.status == "ok":
            return dres
        # 3) dynamic 也掛了 → 至少回靜態結果 + 警告
        sres.mode = "hybrid"
        sres.metrics["dispatch_log"] = ["static_ok", "dynamic_fail"]
        sres.metrics["dispatch_reasons"] = reasons
        sres.metrics["dispatch_dyn_errors"] = dres.errors
        sres.errors.extend(dres.errors)
        return sres


# ===========================================================================
# 6. DataExtractor —— BeautifulSoup 解析為結構化 records
# ===========================================================================
class DataExtractor:
    """把已抓回的 HTML 轉成結構化 records。

    抽出 4 種通用 schema:
      - schema='generic'   : 純粹的 link/image/heading 蒐集(預設)
      - schema='article'   : 標題 + 段落
      - schema='quote'     : 經典 quote/author(quotes.toscrape 風格)
      - schema='product'   : 標題 + 連結 + 圖片 + 描述(可調)
    """

    @staticmethod
    def _base_metrics(soup: BeautifulSoup) -> dict[str, Any]:
        return {
            "title": soup.title.string.strip() if soup.title and soup.title.string else "",
            "description": (soup.find("meta", attrs={"name": "description"}) or {}).get("content", "") if soup.find("meta", attrs={"name": "description"}) else "",
            "lang": (soup.html.get("lang") if soup.html else "") or "",
        }

    @classmethod
    def extract(cls, html: str, schema: str = "generic") -> list[dict[str, Any]]:
        soup = BeautifulSoup(html, "lxml")
        base = cls._base_metrics(soup)
        if schema == "generic":
            return cls._extract_generic(soup, base)
        if schema == "article":
            return cls._extract_article(soup, base)
        if schema == "quote":
            return cls._extract_quote(soup, base)
        if schema == "product":
            return cls._extract_product(soup, base)
        return []

    @classmethod
    def _extract_generic(cls, soup: BeautifulSoup, base: dict[str, Any]) -> list[dict[str, Any]]:
        records: list[dict[str, Any]] = []
        # 把每個 <a> 當作 record,text + href + 內含第一張圖
        for a in soup.find_all("a", href=True):
            text = a.get_text(" ", strip=True)
            if not text:
                continue
            img = a.find("img", src=True)
            records.append({
                **base,
                "kind": "link",
                "text": text,
                "href": a["href"],
                "img": img["src"] if img else None,
            })
        # 補抓無 anchor 的圖片
        for img in soup.find_all("img", src=True):
            records.append({**base, "kind": "image", "text": img.get("alt", ""), "href": img["src"], "img": img["src"]})
        return records

    @classmethod
    def _extract_article(cls, soup: BeautifulSoup, base: dict[str, Any]) -> list[dict[str, Any]]:
        paragraphs = [p.get_text(" ", strip=True) for p in soup.find_all("p") if len(p.get_text(strip=True)) > 30]
        return [{**base, "kind": "article", "paragraph": p} for p in paragraphs[:50]]

    @classmethod
    def _extract_quote(cls, soup: BeautifulSoup, base: dict[str, Any]) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        # 標準 quote.toscrape selectors
        for q in soup.select(".quote"):
            text_el = q.select_one(".text")
            author_el = q.select_one(".author")
            tags = [t.get_text(strip=True) for t in q.select(".tag")]
            out.append({
                **base,
                "kind": "quote",
                "text": text_el.get_text(" ", strip=True) if text_el else "",
                "author": author_el.get_text(strip=True) if author_el else "",
                "tags": tags,
            })
        if out:
            return out
        # fallback:抓所有 <blockquote>
        for bq in soup.find_all("blockquote"):
            out.append({
                **base, "kind": "quote",
                "text": bq.get_text(" ", strip=True),
                "author": "", "tags": [],
            })
        return out

    @classmethod
    def _extract_product(cls, soup: BeautifulSoup, base: dict[str, Any]) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        for card in soup.select(".product, .card, article"):
            title_el = card.select_one("h1, h2, h3, .title, .name")
            price_el = card.select_one(".price, .cost")
            link_el = card.select_one("a[href]")
            img_el = card.select_one("img[src]")
            out.append({
                **base, "kind": "product",
                "title": title_el.get_text(strip=True) if title_el else "",
                "price": price_el.get_text(strip=True) if price_el else "",
                "url": link_el["href"] if link_el else "",
                "img": img_el["src"] if img_el else "",
            })
        return out


# ===========================================================================
# 7. 內建 demo & CLI
# ===========================================================================
def _heuristic_pick_schema(url: str) -> str:
    """根據 URL 提示挑選 schema。"""
    u = url.lower()
    if "quote" in u:
        return "quote"
    if "wiki" in u or "article" in u or "blog" in u:
        return "article"
    if "product" in u or "shop" in u or "amazon" in u:
        return "product"
    return "generic"


def _aggregate_summary(results: list[CrawlResult], records_all: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    ok = [r for r in results if r.status == "ok"]
    fails = [r for r in results if r.status == "fail"]
    avg_ms = sum(r.elapsed_ms for r in ok) / max(1, len(ok))
    by_mode: dict[str, int] = {}
    for r in results:
        by_mode[r.mode] = by_mode.get(r.mode, 0) + 1
    total_records = sum(len(v) for v in records_all.values())
    return {
        "total": len(results),
        "ok": len(ok),
        "fail": len(fails),
        "avg_elapsed_ms": round(avg_ms, 1),
        "by_mode": by_mode,
        "total_records_extracted": total_records,
        "domains": sorted({urllib.parse.urlparse(r.url).netloc for r in results}),
    }


def run_demo() -> dict[str, Any]:
    """內建 demo:Hybrid 抓 3 個 URLs,範式=generic。"""
    print("[demo] Initializing HybridSmartCrawler…")
    hybrid = HybridSmartCrawler()
    results: list[CrawlResult] = []
    for url in DEMO_URLS:
        print(f"[demo] crawling: {url}")
        r = hybrid.fetch(url)
        results.append(r)
        schema = _heuristic_pick_schema(url)
        r.records = DataExtractor.extract(r.html, schema=schema)
        print(f"  → mode={r.mode}, status={r.status}, "
              f"elapsed={r.elapsed_ms:.0f}ms, records={len(r.records)}")
    summary = _aggregate_summary(results, {r.url: r.records for r in results})
    print("[demo] summary:", summary)
    return {"results": [r.to_dict() for r in results], "summary": summary}


def run_async_demo() -> dict[str, Any]:
    """並行 demo。"""
    urls = [
        "https://quotes.toscrape.com/page/1/",
        "https://quotes.toscrape.com/page/2/",
        "https://quotes.toscrape.com/tag/inspirational/",
        "https://quotes.toscrape.com/tag/life/",
    ]
    print(f"[async] crawling {len(urls)} URLs concurrently…")
    crawler = AsyncDynamicCrawler(concurrency=3)
    results = crawler.fetch_sync(urls)
    for r in results:
        if r.status == "ok":
            r.records = DataExtractor.extract(r.html, schema="quote")
        print(f"  → {r.url}: status={r.status}, records={len(r.records)}, "
              f"{r.elapsed_ms:.0f}ms")
    summary = _aggregate_summary(results, {r.url: r.records for r in results})
    return {"results": [r.to_dict() for r in results], "summary": summary}


def main(argv: list[str]) -> int:
    if "--target" in argv:
        i = argv.index("--target")
        url = argv[i + 1]
        hybrid = HybridSmartCrawler()
        r = hybrid.fetch(url)
        r.records = DataExtractor.extract(r.html, schema=_heuristic_pick_schema(url))
        out = {"result": r.to_dict(), "records_count": len(r.records)}
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return 0 if r.status == "ok" else 1
    if "--urls" in argv:
        i = argv.index("--urls")
        urls = [u.strip() for u in argv[i + 1].split(",") if u.strip()]
        out = run_async_demo() if False else None  # use explicit async demo
        # simple sync batch
        async_c = AsyncDynamicCrawler(concurrency=4)
        results = async_c.fetch_sync(urls)
        records_all = {}
        for r in results:
            if r.status == "ok":
                r.records = DataExtractor.extract(r.html, schema=_heuristic_pick_schema(r.url))
            records_all[r.url] = r.records
        out = {"results": [r.to_dict() for r in results],
               "summary": _aggregate_summary(results, records_all)}
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return 0
    # default demo
    demo_out = run_demo()
    print(json.dumps({"hybrid_demo_summary": demo_out["summary"]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
