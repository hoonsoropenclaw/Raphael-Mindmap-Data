# Playwright Visual Regression Testing

## Overview
This micro-skill focuses on using Playwright for visual regression testing, encompassing pixel-level image comparison, freezing dynamic content, and generating self-contained HTML test reports.

---

## 1. Pixel-Level Image Comparison with Pixelmatch

### Explanation
Pixelmatch is a lightweight and efficient library for comparing two images pixel by pixel. It is used to detect visual differences between screenshots taken during tests.

### Key Code Snippets
```javascript
const pixelmatch = require('pixelmatch');
const fs = require('fs');
const PNG = require('pngjs').PNG;

const compareImages = async (img1, img2, diffImg) => {
  const img1Data = fs.readFileSync(img1);
  const img2Data = fs.readFileSync(img2);

  const img1PNG = PNG.sync.read(img1Data);
  const img2PNG = PNG.sync.read(img2Data);

  const { width, height } = img1PNG;
  const diffPNG = new PNG({ width, height });

  const numDiffPixels = pixelmatch(
    img1PNG.data,
    img2PNG.data,
    diffPNG.data,
    width,
    height,
    { threshold: 0.1 }
  );

  fs.writeFileSync(diffImg, PNG.sync.write(diffPNG));
  return numDiffPixels;
};
```

### Common Errors and Prevention
- **Error**: Incorrect image paths leading to comparison failure.
  - **Prevention**: Ensure that the paths to the images are correct and that the images exist at the specified locations.
- **Error**: Mismatch in image dimensions causing comparison errors.
  - **Prevention**: Verify that both images have the same dimensions before comparison.

---

## 2. Freezing Dynamic Content

### Explanation
Dynamic content can cause false positives in visual regression tests. Freezing dynamic content involves capturing screenshots when the content is in a stable state.

### Key Code Snippets
```javascript
const { chromium } = require('playwright');

const freezeDynamicContent = async (page) => {
  // Wait for network idle to ensure dynamic content is loaded
  await page.waitForLoadState('networkidle');

  // Optionally, wait for specific elements to load
  await page.waitForSelector('.dynamic-content');

  // Take screenshot
  await page.screenshot({ path: 'screenshot.png' });
};
```

### Common Errors and Prevention
- **Error**: Screenshot taken before dynamic content is fully loaded.
  - **Prevention**: Use appropriate wait mechanisms (`waitForLoadState`, `waitForSelector`) to ensure content is loaded before taking the screenshot.
- **Error**: Dynamic content continues to change after the screenshot is taken.
  - **Prevention**: Implement additional logic to pause or freeze the content if necessary.

---

## 3. Generating Self-Contained HTML Test Reports

### Explanation
The HTML report includes test results, screenshots, and difference images. It uses data-URI to embed images, ensuring the report is self-contained and can be viewed offline.

### Key Code Snippets
```javascript
const fs = require('fs');
const generateReport = async (results) => {
  const reportTemplate = fs.readFileSync('report-template.html', 'utf8');
  let reportContent = reportTemplate;
  results.forEach(result => {
    const diffImageDataURI = fs.readFileSync(result.diffImage, 'base64');
    reportContent = reportContent.replace('{{test-name}}', result.name);
    reportContent = reportContent.replace('{{status}}', result.ok ? 'passed' : 'failed');
    reportContent = reportContent.replace('{{diff-image}}', `data:image/png;base64,${diffImageDataURI}`);
    // Other replacements
  });
  fs.writeFileSync('report.html', reportContent);
};
```

### Common Errors and Prevention
- **Error**: Image data not correctly converted to data-URI, causing images to not display in the report.
  - **Prevention**: Ensure that images are read as base64 and properly embedded using the data-URI scheme.
- **Error**: Placeholder tokens in the report template not matching the replacement logic.
  - **Prevention**: Verify that the placeholder tokens in the report template exactly match those used in the code for replacement.

---

## Summary
This micro-skill integrates pixel-level image comparison, dynamic content freezing, and HTML report generation to provide a comprehensive visual regression testing solution using Playwright. By following the provided code snippets and error prevention tips, you can ensure reliable and accurate visual regression testing.