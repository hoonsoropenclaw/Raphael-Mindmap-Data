# Advanced Browser Automation and Testing Framework

## Overview
This micro-skill focuses on implementing comprehensive automation and testing strategies for web applications using headless browsers, Playwright, and tools like Pillow for visual regression and screenshot capture. It also covers report generation for detailed analysis, ensuring robust, reliable, and visually consistent web applications across different browsers and devices.

## Key Techniques and Patterns

### 1. Cross-Browser Test Runner with Playwright
Utilize Playwright to create a cross-browser test runner that supports Chromium, Firefox, and WebKit browsers, ensuring test reliability across different rendering engines.

#### Example Code
```javascript
const { chromium, firefox, webkit } = require('playwright');

const browsers = [chromium, firefox, webkit];
const viewports = [
  { name: 'desktop', width: 1440, height: 900 },
  { name: 'mobile', width: 390, height: 844 }
];

(async () => {
  for (const browserType of browsers) {
    for (const viewport of viewports) {
      const browser = await browserType.launch();
      const page = await browser.newPage({
        viewport: { width: viewport.width, height: viewport.height }
      });
      await page.goto('http://localhost:4173/web_output.html');
      
      // Example test logic
      const title = await page.title();
      console.log(`Title of ${viewport.name} ${browserType.name()} is ${title}`);
      
      await browser.close();
    }
  }
})();
```

### 2. Visual Regression Testing
Implement visual regression tests to detect unintended visual changes by capturing screenshots and comparing them against baseline images.

#### Example Code
```javascript
const { chromium } = require('playwright');
const fs = require('fs');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('http://localhost:4173/web_output.html');

  // Capture screenshot
  const screenshot = await page.screenshot({ fullPage: true });
  fs.writeFileSync('screenshot.png', screenshot);

  // Compare with baseline
  const baseline = fs.readFileSync('baseline.png');
  if (!screenshot.equals(baseline)) {
    console.log('Visual regression detected!');
  }

  await browser.close();
})();
```

### 3. Navigation and Interaction Automation
Automate complex navigation flows and user interactions, such as clicking buttons, filling forms, and navigating through pages.

#### Example Code
```javascript
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('http://localhost:4173/login.html');

  // Interact with the page
  await page.fill('input[name="username"]', 'testuser');
  await page.fill('input[name="password"]', 'password123');
  await page.click('button[type="submit"]');

  // Wait for navigation
  await page.waitForNavigation({ waitUntil: 'networkidle' });

  console.log('Logged in successfully');

  await browser.close();
})();
```

### 4. Multi-Browser Configuration with Playwright
Configure `playwright.config.js` to support multiple browsers (Chromium, Firefox, WebKit) and multiple project types (desktop and mobile).

#### Key Code Snippets
```javascript
// playwright.config.js
module.exports = {
  projects: [
    {
      name: 'chromium',
      use: { 
        // Chromium for desktop
      }
    },
    {
      name: 'firefox',
      use: { 
        // Firefox for desktop
      }
    },
    {
      name: 'webkit',
      use: { 
        // WebKit for desktop
      }
    },
    {
      name: 'mobile-chromium',
      use: { 
        // Chromium for mobile
      }
    },
    {
      name: 'mobile-webkit',
      use: { 
        // WebKit for mobile
      }
    }
  ]
}
```

### 5. Test Case Design with `data-testid`
Utilize the `data-testid` attribute in HTML elements for stable and reliable element selection during testing.

#### Key Code Snippets
```html
<!-- HTML -->
<article class="task-row" data-testid="task-row" data-task-id="1">...</article>
```
```javascript
// Test case
await expect(page.getByTestId('task-row')).toHaveAttribute('data-status', 'completed');
```

### 6. Visual Regression Testing Setup
Set up visual regression testing to capture and compare screenshots of web pages, ensuring consistent visual appearance across different browsers and devices.

#### Key Code Snippets
```javascript
// Test case
await expect(page).toHaveScreenshot('home-chromium.png', {
  fullPage: true,
  animations: 'disabled',
  caret: 'hide',
});
```

### 7. Probe Testing for Visual Drift
Implement probe testing to detect unexpected visual changes in the application, ensuring early identification of visual regressions.

#### Key Code Snippets
```javascript
// Probe test
test('intentional visual drift is rejected', async ({ page }, testInfo) => {
  test.skip(!process.env.RUN_VISUAL_PROBE, 'opt-in regression probe (set RUN_VISUAL_PROBE=1)');
  // Introduce intentional visual change
  await page.addStyleTag({ content: '[data-testid="hero"] { filter: hue-rotate(120deg) !important; }' });
  // Capture screenshot for comparison
  await expect(page).toHaveScreenshot('home-chromium.png', {
    fullPage: true,
    animations: 'disabled',
    caret: 'hide',
  });
});
```

### 8. CSS Animation Freezing
Ensure visual regression tests are deterministic by eliminating differences caused by animations during screenshot capture.

#### Key Code Snippets
```python
page.add_style_tag(content=""" *,
 *::before,
 *::after {
     animation: none !important;
     transition: none !important;
 }
 .animate-float-slow,
 .animate-pulse-soft,
 .animate-gradient {
     animation: none !important;
 }
""")
page.wait_for_timeout(800)
```

### 9. Pixel Diff Using Pillow
Compare two images pixel by pixel to identify differences for visual regression testing.

#### Key Code Snippets
```python
from PIL import Image, ImageChops

def compare_images(image1_path, image2_path):
    image1 = Image.open(image1_path).convert('RGB')
    image2 = Image.open(image2_path).convert('RGB')
    diff = ImageChops.difference(image1, image2)
    if diff.getbbox():
        return diff
    return None
```

### 10. Screenshot Capture with Playwright
Automate the process of capturing screenshots of web pages across different browsers and devices for visual regression testing.

#### Key Code Snippets
```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto('https://example.com')
    page.screenshot(path='screenshot.png')
    browser.close()
```

### 11. Report Generation with HTML
Create a comprehensive, standalone HTML report that includes captured screenshots and diffs, along with statistics for easy analysis and sharing.

#### Key Code Snippets
```python
import base64
from PIL import Image

def generate_html_report(report_path, images, diffs, stats):
    with open(report_path, 'w') as f:
        f.write('<html><body>\n')
        for image in images:
            with open(image, 'rb') as img_file:
                img_data = base64.b64encode(img_file.read()).decode('utf-8')
                f.write(f'<img src="data:image/png;base64,{img_data}" />\n')
        for diff in diffs:
            with open(diff, 'rb') as diff_file:
                diff_data = base64.b64encode(diff_file.read()).decode('utf-8')
                f.write(f'<img src="data:image/png;base64,{diff_data}" />\n')
        f.write(f'<p>{stats}</p>\n')
        f.write('</body></html>')
```

## Best Practices

- **Modularize Test Scripts**: Break down tests into reusable functions and modules to improve maintainability.
- **Use Page Objects**: Implement the Page Object Model to encapsulate page interactions and selectors.
- **Parallelize Tests**: Run tests in parallel to reduce execution time, especially for large test suites.
- **Continuous Integration**: Integrate tests into CI/CD pipelines to ensure continuous feedback and streamline.
- **Consistent Element Identification**: Use stable and unique `data-testid` values to avoid selector conflicts.
- **Isolated Testing Environments**: Maintain separate configurations and baseline images for different testing scenarios to prevent cross-contamination.
- **Controlled Baseline Updates**: Update baseline images only when necessary and through intentional actions to maintain test integrity.
- **Comprehensive Browser Coverage**: Test across multiple browsers and device types to ensure broad compatibility and identify platform-specific issues.

## Error Prevention and Common Issues

### Browser Launch Failures
- **Issue**: Browser fails to launch or pages do not load.
- **Solution**: 
  - Ensure that the correct Playwright browsers are installed using `npx playwright install`.
  - Verify that the local server is running and accessible.
  - Check for any firewall or network issues that might prevent browser launch.

### Test Execution Slowdowns and Timeouts
- **Issue**: Tests run slowly or timeout unexpectedly.
- **Solution**: 
  - Optimize test scripts by removing unnecessary wait times and using appropriate waiting strategies such as `waitForLoadState` or `waitForSelector`.
  - Use `page.setDefaultTimeout` to set a