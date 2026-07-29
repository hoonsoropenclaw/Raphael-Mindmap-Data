# Automated Browser Testing with Playwright

## Overview

### Purpose
The `automated_browser_testing_with_playwright` micro-skill focuses on implementing comprehensive automated testing strategies for web applications using Playwright. This includes simulating browser-level security tests such as Cross-Site Scripting (XSS) attacks, as well as performing end-to-end (E2E) testing, smoke testing, and other essential testing tasks to ensure the robustness and reliability of web applications.

### Key Features and Techniques
- **Dynamic Page Rendering**: Utilize Playwright to render JavaScript-heavy pages and wait for dynamic content to load, ensuring that all elements are properly rendered before testing.
- **Network Request Monitoring**: Intercept and log network requests to understand API interactions, reverse engineer endpoints, and verify that network calls are functioning as expected.
- **Automated Testing**: Simulate user interactions and verify frontend functionalities through automated test scripts, including clicking buttons, filling forms, and navigating through application workflows.
- **End-to-End (E2E) Testing**: Validate the complete workflow and functionality of the application from start to finish, ensuring that all components work together seamlessly.
- **Smoke Testing**: Conduct quick, high-level tests to ensure basic application functionality and stability across different scenarios.
- **Security Testing**: Simulate browser-level attacks such as XSS to test the application's security mechanisms and ensure that vulnerabilities are mitigated.
- **Screenshot Capture**: Capture and save screenshots of rendered pages for visual verification and debugging, aiding in the identification of visual regressions or rendering issues.
- **Data Extraction and JSON Output**: Extract relevant data from web pages and format it into structured JSON files for further processing, analysis, or integration with other systems.

## Technical Implementation

### Initialization and Browser Setup
Initialize Playwright and launch a headless browser instance:
```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
```

### Navigation and Selector Waiting
Navigate to the target URL and wait for specific elements to load:
```python
page.goto(args.url)
page.wait_for_selector(args.selector, timeout=args.timeout)
```

### Screenshot Capture
Capture and save screenshots of the rendered page:
```python
page.screenshot(path=args.screenshot)
```

### Network Request Monitoring
Listen to network requests to capture API endpoints and payloads:
```python
network_requests = []
page.on("request", lambda request: network_requests.append(request.url))
```

### Data Extraction and JSON Output
Extract data using selectors and output it as a structured JSON file:
```python
data = page.evaluate(f"document.querySelector('{args.selector}').innerText")
with open(args.output, 'w', encoding='utf-8') as f:
    json.dump({'url': args.url, 'data': data}, f, ensure_ascii=False, indent=2)
```

### Automated Testing with Playwright (JavaScript Example)
Example of using Playwright for automated testing in a JavaScript environment:
```javascript
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  
  // Set up listeners or mocks if needed
  // Example: Mocking network requests
  await page.route('**/api/**', route => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ mocked: 'response' }),
    });
  });

  await page.goto('http://127.0.0.1:8766/index.html', { waitUntil: 'networkidle', timeout: 45000 });
  
  // Execute test steps
  // Example: Interact with the page
  await page.click('button#start');
  await page.fill('input#username', 'testUser');
  await page.fill('input#password', 'testPass');
  await page.click('button#submit');

  // Verify results
  const result = await page.evaluate(() => ({
    elementCount: document.querySelectorAll('*').length,
    // Add more evaluation logic as needed
  }));
  
  console.log(JSON.stringify(result, null, 2));

  await browser.close();
})();
```

### E2E Testing with Playwright (JavaScript Example)
Example of using Playwright for E2E testing in a JavaScript environment:
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

### Smoke Testing with Playwright (Python Example)
Example of using Playwright for smoke testing in a Python environment:
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

### XSS Testing with Playwright (Python Example)
Example of using Playwright to simulate an XSS attack:
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

## Common Errors and Prevention

### Dynamic Scraper Errors
- **Selector Timeout**: The specified selector is not found within the given timeout.
  - **Prevention**: Increase the `timeout` value or use more robust selectors that account for dynamic content loading.
  
- **Network Request Monitoring Failure**: Network requests are not captured as expected.
  - **Prevention**: Ensure that the event listener is set up before navigating to the page. Check the browser console for any JavaScript errors that might prevent network requests from being sent.

- **JSON Formatting Issues**: The output JSON is malformed or not properly encoded.
  - **Prevention**: Use `json.dump` with `ensure_ascii=False` and `indent=2` to ensure the JSON is well-formatted and readable.

### Headless Browser Testing Errors
- **Playwright Installation or Environment Issues**: Playwright is not installed correctly or the environment is not configured properly.
  - **Prevention**: Verify Playwright installation using `pip list | grep playwright` for Python or `npm list playwright` for JavaScript. Ensure that the Node.js environment is correctly set up.

- **Page Load Timeout**: The page takes too long to load, causing the test to fail.
  - **Prevention**: Increase the `timeout` value or optimize the page load time by reducing unnecessary resources or optimizing network requests.

- **Element Interaction Failures**: The test is unable to interact with page elements as expected.
  - **Prevention**: Ensure that selectors are accurate and that elements are present and visible before interaction. Use explicit waits or retries if necessary.

### Smoke Testing Errors
- **Selector Errors**: The test script uses incorrect selectors, leading to element location failures.
  - **Prevention**: Use browser developer tools to verify selector accuracy and include appropriate wait times for dynamic content.

- **Environment Mismatch**: The test environment does not match the application environment, causing test failures.
  - **Prevention**: Ensure that the test environment mirrors the application environment, including database state and API dependencies.

- **Insufficient Test Coverage**: Key functionalities are not tested, leading to potential issues going unnoticed.
  - **Prevention**: Follow a test case writing approach that covers critical paths and edge cases, and regularly review test coverage.

### E2E Testing Errors
- **Error in Test Script**: The test script contains errors or does not accurately reflect the application's workflow.
  - **Prevention**: Review and validate the test script against the application's workflow, ensuring that all steps are correctly implemented.

- **Environment Configuration Issues**: The test environment is not properly configured, leading to test failures.
  - **Prevention**: Ensure that the test environment is correctly configured and that all necessary dependencies are in place.

- **Flaky Tests**: Tests are inconsistent due to network issues or other transient problems.
  - **Prevention**: Implement retry logic for flaky tests and ensure that the test environment is stable.

### XSS Testing Errors
- **Cross-Domain Issues**: The browser page and the test target are not in the same origin, leading to test failures.
  - **Prevention**: Ensure that the browser page and the test target are in the same origin to avoid cross-domain problems.

- **X