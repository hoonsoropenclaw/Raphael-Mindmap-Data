# Playwright Visual Regression Testing

## Overview
This micro-skill focuses on using Playwright for visual regression testing, including pixel-level image comparison with `pixelmatch` and dynamic content freezing techniques to ensure test stability.

## Key Features

### 1. **Playwright Test Environment Setup**
   - **Configuration**: Set up the Playwright test environment with multiple browser configurations.
     ```javascript
     // playwright.config.js
     const { devices } = require('@playwright/test');
     module.exports = {
       projects: [
         {
           name: 'chromium-desktop',
           use: devices['Desktop Chrome']
         },
         // Additional browser configurations can be added here
       ]
     };
     ```
   - **Visual Testing Fixture**: Create a fixture for visual tests that captures screenshots and compares them against baseline images.
     ```javascript
     // helpers/visual-fixture.js
     export const test = base.extend({
       visual: async ({ page, browserName }, use, testInfo) => {
         const helper = {
           async snapshot(name, opts = {}) {
             await page.waitForSelector('[data-app-ready="1"]', { timeout: 5000 }).catch(() => {});
             const buf = await page.screenshot({ fullPage: true, type: 'png' });
             // Save the screenshot and attach it to the report
             const actualPath = attachmentPathFor(testInfo, `${name}__actual`);
             fs.mkdirSync(path.dirname(actualPath), { recursive: true });
             fs.writeFileSync(actualPath, buf);
             testInfo.attachments.push({
               name: `visual-${name}-${result.status}`, path: actualPath, contentType: 'image/png' });
             // Compare against the baseline
             const result = compareAgainstBaseline(baselinePathFor(testInfo, name), buf, opts);
             // Handle the result
           }
         };
         await use(helper);
       }
     });
     ```
   - **Custom Reporter**: Implement a custom reporter to process and report visual test results.
     ```javascript
     // helpers/custom-reporter.js
     class VisualReporter {
       onTestEnd(test, result) {
         const visualStatuses = [];
         for (const att of result.attachments) {
           const m = att.name.match(/^visual-(.+?)(?:-element)?-(created|matched|regressed|updated)$/);
           if (m) {
             visualStatuses.push({ name: m[1], status: m[2], path: att.path });
           }
         }
         // Process visual statuses and write to a JSON report
       }
     }
     module.exports = VisualReporter;
     ```

### 2. **Pixel-Level Image Comparison with Pixelmatch**
   - **Purpose**: Compare actual screenshots with baseline images at the pixel level to detect visual changes.
   - **Implementation**:
     ```javascript
     const pixelmatch = require('pixelmatch').default;
     const fs = require('fs');
     const PNG = require('pngjs').PNG;

     async function compareImages(baselinePath, actualPath, diffPath, width, height) {
       const img1 = fs.createReadStream(baselinePath).pipe(new PNG()).on('parsed', doneReading);
       const img2 = fs.createReadStream(actualPath).pipe(new PNG()).on('parsed', doneReading);
       let img3;

       function doneReading() {
         if (img1 && img2) {
           img3 = new PNG({ width, height });
           pixelmatch(img1.data, img2.data, img3.data, width, height, { threshold: 0.1 });
           img3.pack().pipe(fs.createWriteStream(diffPath));
         }
       }
     }
     ```
   - **Error Prevention**:
     - **Import Error**: Ensure `pixelmatch` is correctly imported using `require('pixelmatch').default` due to ESM module changes in version 6.
     - **Baseline Image Missing**: Handle cases where the baseline image does not exist by either generating it automatically or providing it manually before the test run.

### 3. **Dynamic Content Freezing**
   - **Purpose**: Freeze dynamic content such as timers, animations, and font loading to ensure consistent screenshots and reliable test results.
   - **Implementation**:
     ```javascript
     const freezeDynamicContent = async (page, options) => {
       await page.addInitScript(() => {
         // Freeze time
         const frozenAt = new Date('2026-01-01T00:00:00Z');
         window.Date = class extends Date {
           constructor() {
             super(frozenAt);
           }
         };
         // Stop CSS animations
         document.body.style.animation = 'none';
         // Hide dynamic elements
         const dynamicElements = document.querySelectorAll('[data-dynamic]');
         dynamicElements.forEach(el => el.style.display = 'none');
         // Wait for fonts to load
         document.fonts.ready.then(() => {
           // Further processing can be done here
         });
       });
     };
     ```
   - **Error Prevention**:
     - **Incorrect Freezing**: Ensure all dynamic content is correctly identified and frozen by verifying the freezing logic and running the freezing script before the test starts.
     - **Interference with Test Flow**: Only freeze the necessary dynamic content to avoid disrupting the normal flow of the test.

## Best Practices and Error Prevention

- **Attachment Path Undefined**: Always ensure that the buffer is written to disk and the file path is attached, rather than attaching the buffer directly.
- **Visual Tests Running on Unexpected Browsers**: Use conditional skips to restrict visual tests to specific browsers, such as Chromium, to prevent unexpected failures.
  ```javascript
  test.skip(({ browserName }) => browserName !== 'chromium', 'Skipping visual test on non-Chromium browsers');
  ```
- **Missing Visual Status in Reports**: Verify that the regular expression used to parse attachment names is correct and that the reporter can handle all expected visual statuses.

## Conclusion
By following the guidelines and utilizing the provided code snippets, you can effectively set up and execute visual regression testing using Playwright, ensuring your application's visual integrity and stability.