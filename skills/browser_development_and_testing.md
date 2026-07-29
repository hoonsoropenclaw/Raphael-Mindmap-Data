# Browser Development and Testing

## Overview

### Target Skill Name: `browser_development_and_testing`

### Target Summary
Browser development and testing encompasses a range of activities including browser console debugging, automation of tasks, and comprehensive testing of APIs and browser functionalities. This micro-skill ensures the robustness and reliability of web applications through end-to-end (E2E) testing, security assessments, and performance evaluations.

---

## 1. Browser Console Debugging

### 1.1 Purpose
Utilize the browser console to capture and debug JavaScript errors, implement global error handling, and perform effective logging.

### 1.2 Key Techniques and Code Snippets
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

### 1.3 Common Errors and Prevention

- **Error**: Global error handlers are not correctly set up, leading to uncaught errors.
  - **Solution**: Ensure `window.addEventListener('error', ...)` and `window.addEventListener('unhandledrejection', ...)` are properly configured.

- **Error**: Logging functions are not correctly overridden, resulting in missing logs.
  - **Solution**: Verify that `console.log` and `console.error` are properly overridden and that the log element exists in the DOM.

---

## 2. Browser Automation

### 2.1 Environment Setup

#### 2.1.1 Terminal Environment
- **Navigate to Project Directory**
  ```bash
  cd path/to/your/project
  ```
- **Install Dependencies**
  ```bash
  npm install
  ```
- **Verify Installation**: Ensure no errors occur during installation.

#### 2.1.2 Common Errors and Solutions
- **Missing Dependencies**: Run `npm install` to install required packages.
- **Permission Issues**: Use `sudo` (with caution) if necessary.

### 2.2 Playwright Bridge Setup

#### 2.2.1 Description
Set up a Node.js WebSocket server to facilitate communication between your HTML application and Playwright.

#### 2.2.2 Key Code Snippets
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

#### 2.2.3 Common Errors and Solutions
- **Bridge Failure**: Verify Playwright installation and check firewall settings.
- **Command Execution Errors**: Double-check command syntax and ensure target website allows automation.

### 2.3 Integration of Skills

#### 2.3.1 Step-by-Step Process
1. **Initialize the Terminal Environment**
   - Navigate to your project directory and run `npm install`.
2. **Set Up the Playwright Bridge**
   - Ensure `playwright-bridge.js` is present and start the server with `node playwright-bridge.js`.
3. **Establish Communication**
   - In your HTML application, establish a WebSocket connection and send commands to Playwright.
4. **Error Handling and Prevention**
   - **Dependency Issues**: Run `npm install` before starting the bridge.
   - **Firewall Restrictions**: Check firewall settings for the specified port.
   - **Command Syntax**: Verify command syntax and parameters.
   - **Target Website Permissions**: Ensure the website allows automation and necessary permissions are in place.

### 2.4 Browser Automation Interaction

#### 2.4.1 Description
Use tools like Selenium, Puppeteer, or Playwright to simulate user interactions and perform visual verification.

#### 2.4.2 Key Code Snippets (Python Example)
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

#### 2.4.3 Common Errors and Solutions
- **Element Locating Failures**: Use robust selectors and implement explicit waits.
  ```python
  from selenium.webdriver.support.ui import WebDriverWait
  from selenium.webdriver.support import expected_conditions as EC

  wait = WebDriverWait(driver, 10)
  button = wait.until(EC.element_to_be_clickable((By.ID, 'toast-button')))
  ```
- **Visual Verification Inaccuracies**: Use screenshot and image recognition techniques.
  ```python
  driver.save_screenshot('screenshot.png')
  # Implement image recognition logic here
  ```

---

## 3. Comprehensive API and Browser Testing with cURL and Playwright

### 3.1 API Testing with cURL

#### 3.1.1 Purpose
Simulate different user roles and permissions to test protected routes and API endpoints.

#### 3.1.2 Key Features and Techniques
- **RBAC Simulation**: Generate tokens for various user roles and test API access.
- **Automated Testing Scripts**: Create reusable scripts for API calls and response validation.
- **Response Validation**: Verify HTTP status codes, payloads, and headers.

#### 3.1.3 Technical Implementation

##### 3.1.3.1 Token Generation for RBAC
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

##### 3.1.3.2 Testing Script Structure
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

#### 3.1.4 Common Errors and Prevention

- **Token Generation Errors**: Incorrect token generation leads to failed authorization.
  - **Prevention**: Validate token generation logic and use tools like [jwt.io](https://jwt.io/) to verify tokens.

- **Insufficient Test Coverage**: Missing critical API endpoints or permission combinations.
  - **Prevention**: Design comprehensive test cases covering all roles, endpoints, and edge cases.

- **Environment Configuration Issues**: Mismatched configurations between test and production environments.
  - **Prevention**: Ensure the test environment mirrors the production environment, including API versions and dependencies.

### 3.2 Browser Testing with Playwright

#### 3.2.1 Purpose
Implement automated browser tests to simulate user interactions, validate frontend functionalities, and perform security and performance assessments.

#### 3.2.2 Key Features and Techniques
- **Dynamic Page Rendering**: Handle JavaScript-heavy pages and wait for dynamic content to load.
- **Network Request Monitoring**: Intercept and analyze network requests to verify API interactions.
- **Automated Interactions**: Simulate user actions like clicks, form submissions, and navigation.
- **E2E Testing**: Validate complete workflows from start to finish.
- **Smoke Testing**: Perform quick, high-level tests to ensure basic functionality.
- **Security Testing**: Simulate attacks like XSS to test security mechanisms.
- **Screenshot Capture**: Capture screenshots for visual verification and debugging.
- **Data Extraction and JSON Output**: Extract and format data for further analysis or integration.

#### 3.2.3 Technical Implementation

##### 3.2