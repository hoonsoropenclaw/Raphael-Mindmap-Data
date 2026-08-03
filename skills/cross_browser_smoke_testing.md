# Cross-Browser Smoke Testing with Playwright

## Overview
This micro-skill focuses on implementing cross-browser automation testing using Playwright, specifically targeting interactive flows with Smoke Tests. The goal is to ensure functionality and consistency across different browsers by setting up a robust testing environment, defining a browser matrix, writing comprehensive test scripts, and handling common issues that may arise during the testing process.

## Key Components

### 1. Setting Up the Testing Environment

#### Configuration
Configure Playwright to set up the testing environment, including specifying the test directory, timeout settings, parallel execution, reporters, and web server configurations.

```javascript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  timeout: 30000,
  fullyParallel: true,
  reporter: [
    ['list'], 
    ['html', { outputFolder: 'playwright-report', open: 'never' }]
  ],
  use: { 
    baseURL: 'http://127.0.0.1:4173', 
    trace: 'retain-on-failure', 
    screenshot: 'only-on-failure' 
  },
  webServer: {
    command: 'python3 -m http.server 4173 --bind 127.0.0.1',
    url: 'http://127.0.0.1:4173/web_output.html',
    reuseExistingServer: true
  },
  projects: [
    { 
      name: 'chromium-desktop', 
      use: { 
        ...devices['Desktop Chrome'], 
        viewport: { width: 1440, height: 900 } 
      } 
    },
    { 
      name: 'firefox-tablet', 
      use: { 
        ...devices['Desktop Firefox'], 
        viewport: { width: 768, height: 1024 } 
      } 
    },
    { 
      name: 'webkit-mobile', 
      use: { 
        ...devices['iPhone 13'], 
        viewport: { width: 390, height: 844 } 
      } 
    }
  ]
});
```

### 2. Writing Interactive Flow Smoke Tests

#### Test Script
Create test scripts that simulate user interactions, such as button clicks, and verify that the DOM updates accordingly without errors.

```javascript
test('interactive smoke flow updates DOM without errors', async ({ page }) => {
  await page.getByTestId('run-check').click();
  await expect(page.getByTestId('check-status')).toHaveText('Smoke check passed');
  await expect(page.getByTestId('check-status')).toHaveAttribute('data-state', 'passed');
  await page.getByTestId('reset-check').click();
  await expect(page.getByTestId('check-status')).toHaveText('Ready to run');
});
```

### 3. Handling Common Errors and Ensuring Robustness

#### 1. Browser Initialization Failures
- **Error**: Browser fails to launch or the test environment does not initialize correctly.
- **Solution**: 
  - Verify that the `webServer` configuration is accurate.
  - Ensure that the local server is running and accessible.
  - Check for any port conflicts or firewall issues that might prevent the server from starting.

#### 2. Cross-Browser Compatibility Issues
- **Error**: Tests fail due to differences in browser behavior or rendering.
- **Solution**: 
  - Utilize Playwright's device configurations (`devices`) to simulate various browsers and devices.
  - Account for browser-specific differences in the test scripts, such as handling CSS variations or JavaScript implementations.
  - Use conditional logic or separate test cases for different browsers if necessary.

#### 3. DOM State Not Updating After Interactions
- **Error**: Clicking a button does not update the DOM as expected.
- **Solution**: 
  - Confirm that the button has the correct event listener attached.
  - Ensure that the JavaScript code responsible for updating the DOM is correctly loaded and executed in the test environment.
  - Use debugging tools to inspect the state of the DOM before and after the interaction.

#### 4. Error Capture Mechanism Not Working
- **Error**: The error capture mechanism fails to detect or report errors.
- **Solution**: 
  - Verify that `page.on('pageerror')` and `page.on('console')` event listeners are properly set up.
  - Trigger intentional errors within the test to ensure that the listeners are functioning as expected.
  - Check for any asynchronous operations that might delay the reporting of errors.

## Best Practices

- **Consistent Configuration**: Maintain a consistent configuration across different test environments to avoid discrepancies.
- **Modular Test Scripts**: Write modular and reusable test scripts to enhance maintainability and scalability.
- **Comprehensive Reporting**: Utilize reporters to generate detailed reports that can be used for analysis and debugging.
- **Regular Updates**: Keep Playwright and other dependencies up to date to benefit from the latest features and fixes.

## Conclusion
By following the guidelines and best practices outlined in this micro-skill, you can effectively implement cross-browser Smoke Testing using Playwright. This will help ensure that your interactive flows function correctly across different browsers, enhancing the overall quality and reliability of your web applications.