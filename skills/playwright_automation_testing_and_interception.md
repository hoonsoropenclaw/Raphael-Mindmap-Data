# playwright_automation_testing_and_interception

## Overview
This micro-skill focuses on using Playwright for automating web application testing and intercepting `fetch` and `XHR` requests within the page, including capturing request and response bodies.

## Key Techniques and Code Patterns

### 1. **Intercepting Fetch and XHR Requests**

To intercept `fetch` and `XHR` requests, inject a script into the page that overrides the native `fetch` and `XMLHttpRequest` methods. This allows you to capture and log requests and responses.

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

### 2. **Handling Binary or Large Data Responses**

When dealing with binary data or large responses, it's important to manage memory usage to prevent potential issues.

- **Issue**: Intercepting large or binary data can lead to high memory consumption.
- **Solution**: Limit the size of the response body being recorded or capture only necessary data.

```javascript
// Example of limiting the response body size
await page.addInitScript(() => {
    const originalFetch = window.fetch;
    window.fetch = async (...args) => {
        const response = await originalFetch(...args);
        const body = await response.clone().text();
        const limitedBody = body.length > 1024 ? body.substring(0, 1024) + '...' : body;
        window._fetchInterceptions = window._fetchInterceptions || [];
        window._fetchInterceptions.push({ url: args[0], body: limitedBody });
        return response;
    };
});
```

### 3. **Ensuring Proper Injection of Interception Logic**

A common mistake is injecting the interception script after the page's scripts have already executed, resulting in missed requests.

- **Issue**: Interception script is not injected early enough.
- **Solution**: Use `addInitScript` to ensure the interception logic is executed before any page scripts run.

```javascript
// Correct usage of addInitScript to inject interception logic early
await page.addInitScript(() => {
    // Interception logic here
});
```

## Error Prevention and Best Practices

- **Error**: Interception script is injected too late, causing some requests to be missed.
  - **Prevention**: Always use `addInitScript` to inject the interception logic before the page loads any scripts.
  
- **Error**: Intercepting large or binary data without handling it properly can lead to memory issues.
  - **Prevention**: Implement logic to limit the size of the response body or capture only necessary data. For example:

    ```javascript
    const limitedBody = body.length > 1024 ? body.substring(0, 1024) + '...' : body;
    ```

- **Error**: Not initializing interception arrays can lead to runtime errors.
  - **Prevention**: Always initialize interception arrays before pushing data to them.

    ```javascript
    window._fetchInterceptions = window._fetchInterceptions || [];
    window._xhrInterceptions = window._xhrInterceptions || [];
    ```

## Summary

By following the techniques and best practices outlined above, you can effectively use Playwright to automate web application testing and intercept `fetch` and `XHR` requests. Proper injection of interception logic and careful handling of response data are crucial for successful and efficient interception.