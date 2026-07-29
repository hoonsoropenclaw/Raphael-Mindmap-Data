# playwright_web_testing_and_automation

## Overview

### Purpose
The `playwright_web_testing_and_automation` micro-skill is designed to master advanced web automation and smoke testing techniques using Playwright. It enables comprehensive testing and automation by:
- Rendering dynamic web pages and extracting structured data.
- Monitoring network requests for API reverse engineering.
- Automating frontend application interactions to verify functionalities such as AI recommendations, node insertion, template application, process execution, and LLM script generation.
- Performing smoke testing to ensure application stability across different scenarios.
- Outputting results in a structured JSON format for easy integration and analysis.

### Key Features and Techniques
- **Dynamic Page Rendering**: Utilize Playwright to render JavaScript-heavy pages and wait for dynamic content to load.
- **Network Request Monitoring**: Intercept and log network requests to understand API interactions and reverse engineer endpoints.
- **Automated Testing**: Simulate user interactions and verify frontend functionalities through automated test scripts.
- **Smoke Testing**: Conduct quick, high-level tests to ensure basic application functionality and stability.
- **Data Extraction and Output**: Extract relevant data from web pages and format it into JSON for further processing or storage.

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

## Best Practices
- **Use Robust Selectors**: Prefer `data-testid` attributes or other unique identifiers over fragile selectors based on HTML structure.
- **Implement Retry Logic**: For flaky tests or network-dependent operations, implement retry logic to handle transient issues.
- **Monitor Performance**: Keep an eye on the performance implications of your automation scripts, especially when dealing with large or complex web pages.
- **Maintain Test Data**: Use separate test data sets and environments to ensure that tests are consistent and do not interfere with production data.
- **Regularly Review and Update Tests**: As the application evolves, ensure that tests are updated to reflect changes and maintain relevance.

By adhering to these guidelines and utilizing the provided code snippets, you can effectively employ Playwright for advanced web automation and comprehensive testing tasks, including smoke testing for application stability.