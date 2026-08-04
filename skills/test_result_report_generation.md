# Test Result Report Generation

## Purpose
Generate a comprehensive HTML report that includes test results, screenshots, and regression analysis. The report should be self-contained and easily shareable, providing a clear and detailed overview of the test outcomes.

## Key Components
- **Test Results**: Summarize the outcomes of the tests, including pass/fail status, execution time, and any error messages.
- **Screenshots**: Embed screenshots of the application under test, highlighting differences or issues identified during the test.
- **Regression Analysis**: Provide an analysis of the test results, identifying trends, anomalies, and potential areas for improvement.

## Key Code Snippets/Patterns

### Embedding Images
```javascript
function embedImage(relPath, siblingDir) {
  const absPath = resolveSibling(siblingDir, relPath);
  const data = fs.readFileSync(absPath);
  return `data:image/png;base64,${data.toString('base64')}`;
}
```
- **Purpose**: Embeds images into the HTML report by converting image files into base64-encoded strings.
- **Usage**: Call this function with the relative path to the image and the directory where the image is located.

### Generating the Report
```javascript
function generateReport(metricsPath, outputPath) {
  const metrics = JSON.parse(fs.readFileSync(metricsPath, 'utf8'));
  const report = `
    <!doctype html>
    <html>
      <head>
        <title>Test Results Report</title>
        <style>
          /* Add CSS styles for the report here */
        </style>
      </head>
      <body>
        <h1>Test Results Report</h1>
        <h2>Metrics</h2>
        <pre>${JSON.stringify(metrics, null, 2)}</pre>
        <h2>Screenshots</h2>
        <div>
          ${metrics.screenshots.map(screenshot => `<img src="${embedImage(screenshot, 'screenshots')}" alt="Screenshot"/>`).join('')}
        </div>
      </body>
    </html>
  `;
  fs.writeFileSync(outputPath, report);
}
```
- **Purpose**: Compiles the test metrics and embedded screenshots into an HTML report.
- **Usage**: Provide the path to the metrics JSON file and the desired output path for the report.

### Generating Matrix JSON
```python
import json

def generate_matrix_json(results):
    with open('report/matrix.json', 'w') as f:
        json.dump(results, f, indent=4)
```
- **Purpose**: Converts test results into a structured JSON format for easy inclusion in the report.
- **Usage**: Pass the test results data to this function to generate the matrix JSON file.

### Generating HTML Report
```python
def generate_html_report(results):
    with open('report/report.html', 'w') as f:
        f.write('<!DOCTYPE html>...')  # 省略具體 HTML 內容
```
- **Purpose**: Generates the HTML report using the structured test data.
- **Usage**: Call this function with the test results data to create the HTML report.

## Common Errors and How to Avoid Them

### Incorrect Paths to Embedded Images
- **Error**: The report may fail to display images if the paths to the screenshots are incorrect.
- **Solution**: 
  - Use explicit paths for baseline and current screenshots.
  - Ensure that the report script correctly resolves the paths to the images.
  - Consider using relative paths and verifying the directory structure.

### Report Format Errors
- **Error**: The report may not display correctly if the HTML structure is incorrect.
- **Solution**: 
  - Use a template engine or pre-defined HTML templates to generate the report.
  - Validate the HTML structure using tools like the W3C Markup Validation Service.
  - Ensure that all necessary HTML tags and attributes are correctly implemented.

### Incomplete Report Data
- **Error**: The report may lack critical information if the test data is not fully included.
- **Solution**: 
  - Ensure that all necessary test data is included in the report.
  - Validate the data before generating the report.
  - Use data validation techniques to ensure completeness and accuracy.

## Best Practices

- **Modular Code**: Break down the report generation process into modular functions for better maintainability.
- **Error Handling**: Implement robust error handling to catch and handle exceptions during the report generation process.
- **Version Control**: Use version control systems to track changes in the report generation scripts and templates.
- **Documentation**: Document the report generation process and the structure of the report for future reference and onboarding of new team members.

## Conclusion
By following the guidelines and best practices outlined in this document, you can generate comprehensive and accurate test result reports that provide valuable insights into the performance and quality of your applications.