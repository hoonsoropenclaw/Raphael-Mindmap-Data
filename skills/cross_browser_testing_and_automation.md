# Cross-Browser Testing and Automation

## Overview
The **cross_browser_testing_and_automation** micro-skill provides a comprehensive framework for automating testing, monitoring, and reporting across various browsers and devices. This includes configuring browser-specific launch parameters, executing automated tests, performing visual regression analysis, and generating detailed reports to ensure software quality, reliability, and consistency.

## Key Components

### 1. Cross-Browser Testing Matrix

#### Purpose
- **Versatility**: Ensure consistent functionality and appearance across multiple browsers (Chromium, Firefox, WebKit) and device viewports (desktop, tablet, mobile).

#### Setup and Configuration
- **Configuration Management**: Maintain a centralized configuration for active browsers and viewports.
  ```python
  from framework.config import active_browsers, active_viewports
  ```
- **Parameterized Testing**: Utilize pytest's parametrization to iterate through all browser and viewport combinations.
  ```python
  @pytest.mark.parametrize("browser, viewport", [(b, v) for b in active_browsers for v in active_viewports])
  def test_cross_browser_visual_regression(browser, viewport):
      # Launch the browser in headless mode
      context = browser.launch(headless=True)
      # Create a new page with specified viewport dimensions
      page = context.new_page(viewport={"width": viewport.width, "height": viewport.height})
      # Execute test logic
      ...
  ```

#### Common Errors and Solutions
- **Test Failures**: 
  - **Issue**: Certain browser or viewport combinations cause test failures.
  - **Solution**: Log detailed failure reports, including browser and viewport details, to facilitate targeted debugging.
- **Layout Inconsistencies**: 
  - **Issue**: Incorrect viewport settings lead to inconsistent page layouts.
  - **Solution**: Use standardized viewport configurations and validate them before testing.

### 2. Comprehensive System Monitoring and Testing

#### Pytest Smoke Tests
- **Purpose**: Verify critical system functionalities such as data validation, provider behaviors, service methods, and FastAPI endpoints.
- **Setup**: 
  ```bash
  pip install pytest
  ```
- **Example Test**:
  ```python
  import pytest
  from fastapi.testclient import TestClient
  from your_app import app

  client = TestClient(app)

  def test_api_endpoint():
      response = client.get("/api/endpoint")
      assert response.status_code == 200
      assert response.json() == {"key": "value"}
  ```
- **Error Prevention**: 
  - **Test Failures**: Ensure assertions accurately reflect expected outcomes.
  - **Dependency Issues**: Use virtual environments to manage dependencies and avoid conflicts.

#### Comprehensive Playwright Integration
- **Key Features**: 
  - Automated testing across multiple browsers
  - Web scraping and data extraction
  - Visual regression testing
  - Asynchronous crawling with relative URL handling
  - Robust error handling

- **Setup and Configuration**:
  ```bash
  npm install playwright
  ```
  or for Python:
  ```bash
  pip install playwright
  python -m playwright install
  ```

- **Browser Initialization**:
  ```javascript
  import { chromium, firefox, webkit } from 'playwright';

  const browsers = { chromium, firefox, webkit };
  for (const [name, type] of Object.entries(browsers)) {
    const browser = await type.launch({ headless: true });
    // Further configuration and testing
  }
  ```

- **Common Errors and Solutions**:
  - **Browser Not Launching**: Ensure browsers are installed using `npx playwright install`.
  - **Permission Issues in Headless Mode**: For Chromium, add the `--no-sandbox` flag:
    ```javascript
    const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
    ```

- **Page Interaction**:
  ```python
  from playwright.sync_api import sync_playwright
  import os

  with sync_playwright() as p:
      browser = p.chromium.launch(headless=True)
      page = browser.new_page(viewport={"width": 1280, "height": 800})
      page.goto(f"file://{os.path.abspath('web_output.html')}")
      page.wait_for_timeout(800)
      page.locator('.lang-btn[data-lang="ja"]').click()
      page.wait_for_timeout(200)
      page.locator('.sample-btn[data-sample="recipe"]').click()
      page.wait_for_timeout(1800)
      panel = page.locator("#demo .panel").nth(1)
      panel.screenshot(path="/tmp/sim_v4.png")
      print(f"Saved {os.path.getsize('/tmp/sim_v4.png')} bytes")
      browser.close()
  ```

- **Error Prevention**:
  - **Element Not Found**: Verify selector correctness and element existence.
  - **Insufficient Wait Time**: Use `wait_for_timeout` or `wait_for_selector` to ensure elements are loaded.
  - **Headless Mode Rendering Issues**: Try non-headless mode for debugging:
    ```python
    browser = p.chromium.launch(headless=False)
    ```

### 3. FastAPI and Playwright Async Integration

#### Explanation
- Integrate Playwright's Async API into FastAPI's async environment to prevent conflicts between synchronous API and event loop.

#### Key Code Snippets
```python
from playwright.async_api import async_playwright

@app.post("/api/extract")
async def extract(req: ExtractRequest):
    async with AsyncPlaywrightCrawler(...) as crawler:
        crawl_result = await crawler.crawl(...)
```

#### Common Errors and Solutions
- **Error**: Event loop is already running (`Event loop is already running`).
- **Solution**: Use `async_playwright` and `await` within FastAPI's async functions.

### 4. Pixelmatch Integration

#### Purpose
- Perform pixel-level image difference detection to ensure visual consistency.

#### Key Code Snippets
```python
from pixelmatch.contrib.PIL import pixelmatch

img_a = Image.open(baseline_path).convert("RGBA")
img_b = Image.open(current_path).convert("RGBA")
w, h = min(img_a.width, img_b.width), min(img_a.height, img_b.height)
img_a = img_a.crop((0, 0, w, h))
img_b = img_b.crop((0, 0, w, h))
diff_buf = bytearray(w * h * 4)
mismatch = pixelmatch(img_a.tobytes(), img_b.tobytes(), w, h, diff_buf, threshold=0.10)
```

#### Common Errors and Solutions
- **Error**: `pixelmatch` module not callable.
  **Solution**: Use `pixelmatch.pixelmatch` to call the function.
- **Error**: `diff_buf` type error.
  **Solution**: `diff_buf` must be of type `bytearray`, not `bytes`. Initialize with `bytearray(w * h * 4)`.

### 5. Pixelmatch ESM Import Fix

#### Explanation
- In pixelmatch's ESM module, the diff buffer must be a mutable `bytearray` to avoid `TypeError: 'bytes' object does not support item assignment`.

#### Key Code Snippets
```python
diff_buf = bytearray(bw * bh * 4)
mismatch = pixelmatch(base_bytes, other_bytes, bw, bh, diff_buf, threshold=threshold)
```

#### Common Errors and Solutions
- **Error**: Using immutable `bytes` type as diff buffer, leading to inability to write difference pixels.
- **Solution**: Use `bytearray` instead of `bytes` to ensure the buffer is mutable.

## Best Practices

- **Consistent Selector Usage**: Use unique and consistent selectors to interact with page elements, reducing test flakiness.
- **Headless vs. Headful Mode**: Use headful mode for debugging and headless mode for faster testing.
- **Error Handling**: Implement robust error handling to manage unexpected issues during test execution.

### Cross Browser Launch Options

#### Explanation
In cross-browser automation testing, different browsers require different launch parameters. For example, Chromium needs `--no-sandbox` and `--disable-dev-shm-usage` to resolve issues in headless environments, while WebKit and Firefox do not accept these parameters.

#### Key Code Snippets
```python
LAUNCH_OPTIONS = {
    "chromium": {
        "headless": True,
        "args": ["--no-sandbox", "--disable-dev-shm-usage"],
    },
    "firefox": {
        "headless": True,
    },
    "webkit": {
        "headless": True,
    },
}

browser_type = p.chromium if browser_name == "chromium" else p.firefox if browser_name == "firefox" else p.webkit
browser = browser_type.launch(**LAUNCH_OPTIONS[browser_name])
```

#### Common Errors and Solutions
- **Error**: WebKit or Firefox crashes due to unrecognized Chromium-specific parameters.
  - **Solution**: Configure launch parameters separately for different browsers to avoid applying Chromium-specific parameters to other browsers.