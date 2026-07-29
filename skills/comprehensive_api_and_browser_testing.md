# Comprehensive API and Browser Testing with cURL and Playwright

## Overview

### Target Skill Name: `comprehensive_api_and_browser_testing`

### Target Summary
This micro-skill focuses on implementing comprehensive automated testing strategies for web applications using **cURL** for API testing and **Playwright** for browser automation. It covers end-to-end (E2E) testing, security testing (e.g., simulating Cross-Site Scripting (XSS) attacks), smoke testing, and other essential testing tasks to ensure the robustness and reliability of web applications.

---

## 1. API Testing with cURL

### 1.1 Purpose
Using cURL to simulate different user roles and permissions for testing protected routes and API endpoints.

### 1.2 Key Features and Techniques
- **Role-Based Access Control (RBAC) Simulation**: Generate tokens for various user roles and test API access based on permissions.
- **Automated Testing Scripts**: Create reusable scripts to perform API calls and validate responses.
- **Response Validation**: Verify HTTP status codes, response payloads, and headers to ensure API correctness.

### 1.3 Technical Implementation

#### 1.3.1 Token Generation for RBAC
```bash
#!/usr/bin/env bash
# E2E RBAC 驗收腳本: 模擬 6 種角色的所有關鍵路徑
set -u
URL=http://localhost:3457

make_token() {
  local role_json="$1"
  printf 'demo:'
  printf '%s' "$role_json" | base64 -w0
}

# 各角色 token (base64 of demo:<JSON>)
GUEST=$(make_token '{"id":"u-guest","name":"訪客","email":"guest@demo","role":"guest"}')
ADMIN=$(make_token '{"id":"u-admin","name":"管理員","email":"admin@demo","role":"admin"}')
...
```

#### 1.3.2 Testing Script Structure
```bash
check() {
  local desc="$1" expected="$2" got="$3"
  if [[ "$got" == "$expected" ]]; then
    echo "  ✓ $desc (HTTP $got)"
    PASS=$((PASS+1))
  else
    echo "  ✗ $desc (expected $expected, got $got)"
    FAIL=$((FAIL+1))
  fi
}

# 測試案例
test_api() {
  # Example: Test GET /api/protected
  RESPONSE=$(curl -s -w "%{http_code}" -H "Authorization: Bearer $ADMIN" "$URL/api/protected")
  HTTP_STATUS=${RESPONSE:(-3)}
  RESPONSE_BODY=${RESPONSE%???}
  check "GET /api/protected (admin)" "200" "$HTTP_STATUS"
}
```

### 1.4 Common Errors and Prevention

- **Token Generation Errors**: Incorrect token generation leads to failed authorization.
  - **Prevention**: Validate token generation logic and use tools like [jwt.io](https://jwt.io/) to verify tokens.
  
- **Insufficient Test Coverage**: Missing critical API endpoints or permission combinations.
  - **Prevention**: Design comprehensive test cases covering all roles, endpoints, and edge cases.

- **Environment Configuration Issues**: Mismatched configurations between test and production environments.
  - **Prevention**: Ensure the test environment mirrors the production environment, including API versions and dependencies.

---

## 2. Browser Testing with Playwright

### 2.1 Purpose
Implementing automated browser tests to simulate user interactions, validate frontend functionalities, and perform security and performance assessments.

### 2.2 Key Features and Techniques
- **Dynamic Page Rendering**: Handle JavaScript-heavy pages and wait for dynamic content to load.
- **Network Request Monitoring**: Intercept and analyze network requests to verify API interactions.
- **Automated Interactions**: Simulate user actions like clicks, form submissions, and navigation.
- **End-to-End (E2E) Testing**: Validate complete workflows from start to finish.
- **Smoke Testing**: Perform quick, high-level tests to ensure basic functionality.
- **Security Testing**: Simulate attacks like XSS to test security mechanisms.
- **Screenshot Capture**: Capture screenshots for visual verification and debugging.
- **Data Extraction and JSON Output**: Extract and format data for further analysis or integration.

### 2.3 Technical Implementation

#### 2.3.1 Initialization and Browser Setup (Python)
```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
```

#### 2.3.2 Navigation and Selector Waiting
```python
page.goto(args.url)
page.wait_for_selector(args.selector, timeout=args.timeout)
```

#### 2.3.3 Screenshot Capture
```python
page.screenshot(path=args.screenshot)
```

#### 2.3.4 Network Request Monitoring
```python
network_requests = []
page.on("request", lambda request: network_requests.append(request.url))
```

#### 2.3.5 Data Extraction and JSON Output
```python
data = page.evaluate(f"document.querySelector('{args.selector}').innerText")
with open(args.output, 'w', encoding='utf-8') as f:
    json.dump({'url': args.url, 'data': data}, f, ensure_ascii=False, indent=2)
```

#### 2.3.6 Automated Testing with Playwright (JavaScript Example)
```javascript
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  
  // Mock network requests
  await page.route('**/api/**', route => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ mocked: 'response' }),
    });
  });

  await page.goto('http://127.0.0.1:8766/index.html', { waitUntil: 'networkidle', timeout: 45000 });
  
  // Interact with the page
  await page.click('button#start');
  await page.fill('input#username', 'testUser');
  await page.fill('input#password', 'testPass');
  await page.click('button#submit');

  // Evaluate results
  const result = await page.evaluate(() => ({
    elementCount: document.querySelectorAll('*').length,
  }));
  
  console.log(JSON.stringify(result, null, 2));

  await browser.close();
})();
```

#### 2.3.7 E2E Testing with Playwright (JavaScript Example)
```javascript
const interactiveTargets = await app.page.evaluate(() =>
  [...document.querySelectorAll('button:not(:disabled), input:not([type="checkbox"]), select, textarea, .check-field')]
    .filter((node) => {
      const style = getComputedStyle(node);
      const rect = node.getBoundingClientRect();
      return style.display !== 'none' && style.visibility !== 'hidden' && rect.width > 0 && rect.height > 0;
    })
    .map((node) => ({
      name: node.getAttribute('aria-label') || node.textContent.trim(),
      width: node.getBoundingClientRect().width,
      height: node.getBoundingClientRect().height,
    })),
);
```

#### 2.3.8 Smoke Testing with Playwright (Python Example)
```python
from playwright.sync_api import sync_playwright
import os

def test_rbac():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto('file://' + os.path.abspath('index.html'))
        page.wait_for_load_state('networkidle')

        # Test login flow
        page.locator('.user-pick', has_text='Bob Wang').click()
        page.wait_for_timeout(300)
        assert page.locator('.panel h2').first.inner_text() == 'welcome'

        # Test permission restrictions
        page.locator('.nav-item', has_text='帳單').click()
        page.wait_for_timeout(200)
        assert page.locator('.toast.deny').count() == 1

        browser.close()
```

#### 2.3.9 XSS Testing with Playwright (Python Example)
```python
def test_xss_via_browser_executes_in_dom(browser_page, server_url: str):
    xss = "<img src=x onerror=\"window.__xss_fired__=true\">"
    browser_page.goto(f"{server_url}/health")
    payload_html = browser_page.evaluate("""
        async ({url, xss}) => {
            const resp = await fetch(url + '/search?q=' + encodeURIComponent(xss));
            return resp.text();
        }
    """, {"url": server_url, "xss": xss})
    assert "__xss_fired__" in browser_page.evaluate("window")
```

### 2.4 Common Errors and Prevention

#### 2.4.1 Dynamic Scraper Errors
- **Selector Timeout**: The specified selector is not found within the given timeout.
  - **Prevention**: Increase the `timeout` value or use more robust selectors that account for dynamic content loading.
  
- **Network Request Monitoring Failure**: Network requests are not captured as expected.
  - **Prevention**: Ensure that the event listener is set up before navigating to the page. Check the browser console for any JavaScript errors that might prevent network requests from being sent.

- **JSON Formatting Issues**: The output JSON is malformed or not properly encoded.
  - **Prevention**: Use `json.dump` with `ensure_ascii=False` and `indent=2` to ensure the JSON is well-formatted and readable.

#### 2.4.2 Headless Browser Testing Errors
-