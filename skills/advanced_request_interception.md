# Advanced Request Interception and Quality Assurance

## Overview
This micro-skill focuses on advanced techniques for intercepting, controlling, and testing HTTP requests within web applications. It combines the use of `aiohttp` for asynchronous HTTP requests with robust error handling and Playwright for in-page `fetch` and `XHR` request interception. This comprehensive approach enhances system flexibility, reliability, and quality assurance.

## Key Techniques and Patterns

### 1. Advanced Request Interception

#### Asynchronous HTTP Requests with `aiohttp`
- **Description**: Utilize the `aiohttp` library to perform asynchronous HTTP requests, incorporating timeout controls to prevent requests from hanging indefinitely.
- **Key Code Snippets and Patterns**:
    ```python
    import aiohttp
    import asyncio

    async def fetch_with_timeout(session, url, timeout=10):
        try:
            async with session.get(url, timeout=timeout) as response:
                return await response.text()
        except asyncio.TimeoutError:
            print(f"Request to {url} timed out.")
            return None
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None

    async def main():
        async with aiohttp.ClientSession() as session:
            html = await fetch_with_timeout(session, 'https://example.com', timeout=5)
            if html:
                print("Fetched HTML content.")
            else:
                print("Failed to fetch HTML content.")
    ```
- **Common Errors and Prevention**:
    - **Error**: Not setting a timeout, causing the request to hang indefinitely.
        - **Solution**: Always set a reasonable timeout using the `timeout` parameter in `aiohttp` requests.
    - **Error**: Not handling exceptions, leading to potential crashes.
        - **Solution**: Use `try-except` blocks to catch and handle possible exceptions, such as `asyncio.TimeoutError` and other unforeseen errors.

#### In-Page Fetch and XHR Interception with Playwright
- **Description**: Use Playwright to intercept and record `fetch` and `XHR` requests within a web page, capturing both request and response bodies.
- **Key Code Snippets and Patterns**:
    ```javascript
    // Inject a script to intercept fetch and XHR
    await page.addInitScript(() => {
        // Intercept fetch requests
        const originalFetch = window.fetch;
        window.fetch = async (...args) => {
            const response = await originalFetch(...args);
            const body = await response.clone().text();
            window._fetchInterceptions = window._fetchInterceptions || [];
            window._fetchInterceptions.push({ url: args[0], body });
            return response;
        };
        
        // Intercept XHR requests
        const originalXHROpen = XMLHttpRequest.prototype.open;
        XMLHttpRequest.prototype.open = function (...args) {
            this.addEventListener('load', () => {
                window._xhrInterceptions = window._xhrInterceptions || [];
                window._xhrInterceptions.push({ url: args[0], body: this.responseText });
            });
            originalXHROpen.apply(this, args);
        };
    });
    ```
- **Common Errors and Prevention**:
    - **Error**: Interception script not injected before page scripts execute, causing requests to bypass interception.
        - **Solution**: Use `addInitScript` to inject the interception logic before any page scripts are executed.
    - **Error**: Not handling binary data or large payloads, leading to memory issues.
        - **Solution**: Limit the size of the intercepted response bodies or only record necessary data to prevent excessive memory consumption.

### 2. Combining Request Interception with Error Handling

#### Key Code Snippets and Patterns
```javascript
app.use(async (req, res, next) => {
    try {
        // Intercept and validate the request
        if (!req.body || !req.body.task) {
            throw new Error('Invalid request payload');
        }

        // Proceed with task execution
        const result = await executeTask(req.body.task);

        // Send the response
        res.status(200).json({ success: true, data: result });
    } catch (error) {
        // Handle errors
        logError(error);
        if (error.isCritical) {
            notifyUser();
            res.status(500).json({ success: false, message: 'Internal Server Error' });
        } else {
            proceedWithAlternateStrategy();
            res.status(400).json({ success: false, message: error.message });
        }
    }
});
```

### 3. Integration and Best Practices

#### Combining `aiohttp` and Playwright
- **Setup Playwright to Intercept Requests**:
    - Launch a browser context and navigate to the target page using Playwright.
    - Inject the interception script using `addInitScript` to capture `fetch` and `XHR` requests.
- **Use `aiohttp` for External Requests**:
    - Perform any external HTTP requests required during the process with `aiohttp`.
    - Implement timeout controls to ensure that external requests do not hang.
- **Record and Handle Intercepted Data**:
    - Collect intercepted data from both `fetch` and `XHR` requests using the injected script.
    - Use `aiohttp` to handle any data processing or storage tasks as needed.

#### Example Workflow
```python
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        # Inject interception script
        await page.add_init_script("""
            window._fetchInterceptions = [];
            window._xhrInterceptions = [];
            // Interception logic as shown above
        """)
        
        // Navigate to the target page
        await page.goto('https://example.com')
        
        // Perform actions that trigger fetch/XHR requests
        await page.click('button#trigger-request')
        
        // Wait for some time to allow requests to be intercepted
        await asyncio.sleep(5)
        
        // Retrieve intercepted data
        fetch_interceptions = await page.evaluate("window._fetchInterceptions")
        xhr_interceptions = await page.evaluate("window._xhrInterceptions")
        
        print("Fetch Interceptions:", fetch_interceptions)
        print("XHR Interceptions:", xhr_interceptions)
        
        await browser.close()

asyncio.run(main())
```

### 4. Error Prevention and Best Practices
- **Always Set Timeouts**: Whether using `aiohttp` or Playwright, always set appropriate timeouts to prevent requests from hanging.
- **Handle Exceptions Gracefully**: Implement robust exception handling to manage unexpected errors without crashing the application.
- **Limit Data Recording**: When intercepting large payloads, limit the amount of data recorded to prevent memory issues.
    - **Example**:
        ```javascript
        const limitedBody = body.length > 1024 ? body.substring(0, 1024) + '...' : body;
        ```
- **Secure Data Handling**: Ensure that intercepted data is handled securely, especially if it contains sensitive information.
- **Resource Management**: Properly manage resources such as network connections and browser instances to avoid leaks and ensure efficient resource utilization.

## Summary
By integrating `aiohttp` for asynchronous HTTP requests with timeout management and Playwright for in-page request interception, you can achieve advanced fetch interception and control. This approach, combined with robust error handling and best practices, ensures a more resilient and secure system, enhancing overall quality assurance.