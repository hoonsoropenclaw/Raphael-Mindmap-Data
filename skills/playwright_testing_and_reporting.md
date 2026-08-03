# Playwright Testing and Reporting

## Overview
This micro-skill covers the foundational configuration for cross-browser automation testing using Playwright and the generation of self-contained HTML test reports. It includes setting up the test environment, configuring devices, generating test reports, and embedding images for comprehensive and portable test results.

## Key Components

### 1. Playwright Test Setup

#### Explanation
Configure Playwright for cross-browser automation testing, including setting up the test directory, device configurations, and test report generation.

#### Key Code Snippets
```javascript
const { defineConfig, devices } = require('@playwright/test');

module.exports = defineConfig({
  testDir: './tests',
  /* Additional configurations such as timeout, retries, and reporter can be added here */
  reporter: 'html', // Specifies the reporter to generate HTML reports
});
```

#### Common Errors and Prevention
- **Error**: Test environment port is in use, preventing the test service from starting.
  - **Solution**: Use dynamic port configuration or ensure the desired port is free before starting the test service.
    ```javascript
    // Example of dynamic port configuration
    const { createServer } = require('http');
    const PORT = process.env.PORT || 3000;

    createServer().listen(PORT, () => {
      console.log(`Test server running on port ${PORT}`);
    });
    ```
- **Error**: Cross-browser configuration uses browser-specific launch arguments, causing other browsers to fail.
  - **Solution**: Utilize `perProject` configuration or conditionally apply browser-specific launch arguments.
    ```javascript
    // Example of conditional browser configuration
    const browserConfig = {
      ...devices['Desktop Chrome'],
      // Add browser-specific configurations here
    };

    // Apply configurations based on the browser being used
    ```

### 2. HTML Report Generation

#### Explanation
Generate self-contained HTML test reports that include test results, screenshots, and diff images. Embed images using data-URI to ensure the report is portable and does not rely on external resources.

#### Key Code Snippets
```javascript
const fs = require('fs');
const generateReport = async (results) => {
  const reportTemplate = fs.readFileSync('report-template.html', 'utf8');
  let reportContent = reportTemplate;
  
  results.forEach(result => {
    reportContent = reportContent.replace('{{test-name}}', result.name);
    reportContent = reportContent.replace('{{status}}', result.ok ? 'passed' : 'failed');
    reportContent = reportContent.replace('{{diff-image}}', result.diffImage);
    // Replace other placeholders as needed
  });
  
  fs.writeFileSync('report.html', reportContent);
};
```

#### Common Errors and Prevention
- **Error**: Image embedding fails, causing the report to not display images correctly.
  - **Solution**: Ensure that image data is correctly converted to data-URI and properly referenced in the report template.
    ```javascript
    // Example of converting an image to data-URI
    const imageBuffer = fs.readFileSync('path/to/image.png');
    const base64Image = imageBuffer.toString('base64');
    const dataUri = `data:image/png;base64,${base64Image}`;
    ```
- **Error**: Report template placeholders are not correctly replaced, leading to incorrect report content.
  - **Solution**: Verify that the placeholders in the report template match the replacement logic in the code.
    ```html
    <!-- Example of report template with placeholders -->
    <html>
      <head>
        <title>Test Report</title>
      </head>
      <body>
        <h1>Test Results</h1>
        <p>Test Name: {{test-name}}</p>
        <p>Status: {{status}}</p>
        <img src="{{diff-image}}" alt="Diff Image"/>
      </body>
    </html>
    ```

## Best Practices

- **Modular Configuration**: Keep configuration files modular and organized to easily manage different environments and test scenarios.
- **Dynamic Port Allocation**: Use dynamic port allocation to avoid port conflicts, especially in CI/CD pipelines.
- **Consistent Reporting**: Use a consistent reporting format to ensure that all team members can easily interpret test results.
- **Image Management**: Manage images efficiently by compressing them and using data-URI to keep the report self-contained without significantly increasing its size.

## Conclusion
By following the guidelines and utilizing the provided code snippets, you can effectively set up Playwright for cross-browser automation testing and generate comprehensive, self-contained HTML reports. This setup ensures that your test results are accurate, accessible, and easy to share with stakeholders.