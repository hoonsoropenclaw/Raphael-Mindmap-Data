# End-to-End Browser Testing and Resource Management

## Overview
**Target Skill Name:** `end_to_end_browser_testing`  
**Target Summary:** This micro-skill focuses on establishing a comprehensive environment for end-to-end browser-based testing and efficient resource management. It encompasses setting up local HTTP servers, managing CDN resources, debugging browser interactions, automating tasks, and ensuring robust and reliable web application performance.

---

## 1. Setting Up a Local HTTP Server with Python

### 1.1 Purpose
Utilize Python's built-in `http.server` module to create a local HTTP server for serving files during development and testing.

### 1.2 Key Steps and Code Snippets
1. **Navigate to the Desired Directory**
   ```bash
   cd /path/to/directory
   ```
2. **Start the HTTP Server**
   ```bash
   python3 -m http.server 9090
   ```
   - This command starts the server on port `9090`. Replace `9090` with any available port as needed.

### 1.3 Common Errors and Prevention

- **Port Already in Use**
  - **Error:** The specified port is occupied by another process.
  - **Solution:** Check for existing processes using the port with `lsof -i :9090` (replace `9090` with your port) and choose an alternative port.
    ```bash
    lsof -i :9090
    ```

- **Incorrect Directory Path**
  - **Error:** The server cannot find the specified directory, leading to failed file serving.
  - **Solution:** Ensure the path is correct and that the directory exists. Use absolute paths to avoid confusion.
    ```bash
    cd /absolute/path/to/directory
    ```

- **Firewall Restrictions**
  - **Error:** Firewall settings block access to the local server.
  - **Solution:** Adjust firewall settings to allow traffic on the chosen port. For example, on macOS, you might need to allow Python through the firewall.
    ```bash
    # Example for macOS
    sudo ufw allow 9090
    ```

---

## 2. CDN Reachability Checker

### 2.1 Purpose
Ensure specific CDN resources are reachable to guarantee web applications can correctly load required resources.

### 2.2 Key Code Snippets
```bash
# Use curl to check the reachability of a CDN resource
curl -sI -o /dev/null -w "%{http_code}" https://cdn.jsdelivr.net/npm/tesseract.js@5.1.1/dist/tesseract.min.js
```

### 2.3 Common Errors and Prevention

1. **Network Connection Issues**
   - **Solution:** Verify network connectivity to ensure the device can access the internet.

2. **CDN Service Outages**
   - **Solution:** Regularly monitor CDN service status and opt for reliable CDN providers.

3. **Incorrect Resource Path**
   - **Solution:** Confirm the resource path is accurate to prevent failed resource loading due to path errors.

---

## 3. Browser Console Debugging

### 3.1 Purpose
Leverage the browser console to capture and debug JavaScript errors, implement global error handling, and perform effective logging.

### 3.2 Key Techniques and Code Snippets
```html
<script>
window.addEventListener('error', e => {
  document.getElementById('log').textContent += `[ERROR] ${e.message}\n  at ${e.filename}:${e.lineno}\n  ${e.error?.stack || ''}\n\n`;
});
window.addEventListener('unhandledrejection', e => {
  document.getElementById('log').textContent += `[REJECT] ${e.reason}\n  ${e.reason?.stack || ''}\n\n`;
});
const origLog = console.log;
console.log = (...a) => {
  document.getElementById('log').textContent += `[LOG] ${a.map(x=>String(x)).join(' ')}\n`;
  origLog(...a);
};
console.error = (...a) => {
  document.getElementById('log').textContent += `[ERR] ${a.map(x=>String(x)).join(' ')}\n`;
};
</script>
```

### 3.3 Common Errors and Prevention

- **Global Error Handlers Not Configured**
  - **Error:** Uncaught errors are not handled, leading to silent failures.
  - **Solution:** Ensure `window.addEventListener('error', ...)` and `window.addEventListener('unhandledrejection', ...)` are properly set up.

- **Logging Functions Not Overridden**
  - **Error:** Logs are not captured or displayed as expected.
  - **Solution:** Verify that `console.log` and `console.error` are correctly overridden and that the log element exists in the DOM.

---

## 4. Browser Automation

### 4.1 Environment Setup

#### 4.1.1 Terminal Environment
- **Navigate to Project Directory**
  ```bash
  cd path/to/your/project
  ```
- **Install Dependencies**
  ```bash
  npm install
  ```
- **Verify Installation:** Ensure no errors occur during installation.

#### 4.1.2 Common Errors and Solutions
- **Missing Dependencies:** Run `npm install` to install required packages.
- **Permission Issues:** Use `sudo` (with caution) if necessary.

### 4.2 Playwright Bridge Setup

#### 4.2.1 Description
Set up a Node.js WebSocket server to facilitate communication between your HTML application and Playwright.

#### 4.2.2 Key Code Snippets
```javascript
const { spawn } = require('child_process');
const WebSocket = require('ws');

// Start the Playwright bridge script
const bridge = spawn('node', ['playwright-bridge.js'], { stdio: ['ignore', 'pipe', 'pipe'] });

// Establish a WebSocket connection to the bridge
const ws = new WebSocket('ws://localhost:8787');
ws.on('open', async () => {
  // Send automation commands to Playwright via the bridge
  ws.send(JSON.stringify({ type: 'launchBrowser', params: { url: 'http://example.com' } }));
});
```

#### 4.2.3 Common Errors and Solutions
- **Bridge Failure:** Verify Playwright installation and check firewall settings.
- **Command Execution Errors:** Double-check command syntax and ensure target website allows automation.

### 4.3 Integration of Skills

#### 4.3.1 Step-by-Step Process
1. **Initialize the Terminal Environment**
   - Navigate to your project directory and run `npm install`.
2. **Set Up the Playwright Bridge**
   - Ensure `playwright-bridge.js` is present and start the server with `node playwright-bridge.js`.
3. **Establish Communication**
   - In your HTML application, establish a WebSocket connection and send commands to Playwright.
4. **Error Handling and Prevention**
   - **Dependency Issues:** Run `npm install` before starting the bridge.
   - **Firewall Restrictions:** Check firewall settings for the specified port.
   - **Command Syntax:** Verify command syntax and parameters.
   - **Target Website Permissions:** Ensure the website allows automation and necessary permissions are in place.

### 4.4 Browser Automation Interaction

#### 4.4.1 Description
Use tools like Selenium, Puppeteer, or Playwright to simulate user interactions and perform visual verification.

#### 4.4.2 Key Code Snippets (Python Example)
```python
from selenium import webdriver
from selenium.webdriver.common.by import By

# Initialize the WebDriver (e.g., Chrome)
driver = webdriver.Chrome()

# Navigate to the target URL
driver.get('http://127.0.0.1:8767/')

# Locate and click a button
button = driver.find_element(By.ID, 'toast-button')
button.click()

# Verify the presence of an element
assert driver.find_element(By.ID, 'toast-message')

# Close the browser
driver.quit()
```

#### 4.4.3 Common Errors and Solutions
- **Element Locating Failures:** Use robust selectors and implement explicit waits.
  ```python
  from selenium.webdriver.support.ui import WebDriverWait
  from selenium.webdriver.support import expected_conditions as EC

  wait = WebDriverWait(driver, 10)
  button = wait.until(EC.element_to_be_clickable((By.ID, 'toast-button')))
  ```
- **Visual Verification Inaccuracies:** Use screenshot and image recognition techniques.
  ```python
  driver.save_screenshot('screenshot.png')
  # Implement image recognition logic here
  ```

---

## 5. Comprehensive API and Browser Testing with cURL and Playwright

### 5.1 API Testing with cURL

#### 5.1.1 Purpose
Simulate different user roles and permissions to test protected routes and API endpoints.

#### 5.1.2 Key Features and Techniques
- **RBAC Simulation:** Generate tokens for various user roles and test API access.
- **Automated Testing Scripts:** Create reusable scripts for API calls and response validation.
- **Response Validation:** Verify HTTP status codes, payloads, and headers.

#### 5.1.3 Technical Implementation

##### 5.1.3.1 Token Generation for RBAC
```bash
#!/usr/bin/env bash
# E2E RBAC验收脚本: 模拟6种角色的所有关键路径
set -u
URL=http://localhost:3457

make_token() {
  local role_json="$1"
  printf 'demo:'
  printf '%s' "$role_json" | base64 -w0
}

# 各角色token (base64 of demo:<JSON>)
GUEST=$(make_token '{"id":"u-guest","name":"Guest')