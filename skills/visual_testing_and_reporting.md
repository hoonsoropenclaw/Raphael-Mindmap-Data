# Visual Testing and Reporting

## Overview
The `visual_testing_and_reporting` micro-skill focuses on performing pixel-level image comparisons using the `pixelmatch` library and generating comprehensive HTML test reports that include screenshots and difference images.

## Pixelmatch Usage

### Description
Pixelmatch is a tool for pixel-level image comparison. It is essential to understand the function signature and parameter passing, such as ensuring that `diff_buf` is a `bytearray` rather than `bytes`, and passing the threshold parameter as a keyword argument.

### Key Code Snippets
```python
import pixelmatch
from PIL import Image

# Define image dimensions
w, h = img_a.width, img_a.height

# Initialize diff buffer as bytearray
diff_buf = bytearray(w * h * 4)

# Perform pixel-level comparison
mismatch = pixelmatch.pixelmatch(
    img_a.tobytes(),
    img_b.tobytes(),
    diff_buf,
    w, h,
    threshold=0.1
)
```

### Common Errors and Prevention
- **Error**: Passing `diff_buf` as a `bytes` type, resulting in `TypeError: 'bytes' object does not support item assignment`.
  - **Solution**: Use a `bytearray` to store the difference data.
    ```python
    diff_buf = bytearray(w * h * 4)
    ```
- **Error**: Passing the threshold parameter as a positional argument, causing a signature mismatch.
  - **Solution**: Pass the threshold as a keyword argument, e.g., `threshold=0.1`.
    ```python
    mismatch = pixelmatch.pixelmatch(
        img_a.tobytes(),
        img_b.tobytes(),
        diff_buf,
        w, h,
        threshold=0.1
    )
    ```

## HTML Report Generation

### Description
In visual regression testing, generating a detailed test report is crucial for analyzing test results. The report should include the current screenshot, the baseline image, and the difference image, presented in an easily readable format.

### Key Code Snippets
```python
def generate_html_report(results, summary):
    # Generate report content
    report_content = """
    <html>
    <head><title>Visual Regression Test Report</title></head>
    <body>
    <h1>Visual Regression Test Report</h1>
    <p>Total Cases: {summary['total']}, Passed: {summary['pass']}, Failed: {summary['fail']}</p>
    <table>
    <tr><th>No.</th><th>Browser</th><th>Viewport</th><th>Status</th><th>Mismatch</th><th>Duration</th></tr>
    {rows_html}
    </table>
    {detail_blocks}
    </body>
    </html>
    """
    
    # Populate dynamic content
    rows_html = ""
    for result in results:
        rows_html += f"""
        <tr>
            <td>{result['id']}</td>
            <td>{result['browser']}</td>
            <td>{result['viewport']}</td>
            <td>{result['status']}</td>
            <td>{result['mismatch']}%</td>
            <td>{result['duration']}</td>
        </tr>
        """
    
    detail_blocks = ""
    for result in results:
        detail_blocks += f"""
        <h2>Test Case {result['id']}</h2>
        <p>Browser: {result['browser']}, Viewport: {result['viewport']}</p>
        <p>Status: {result['status']}, Mismatch: {result['mismatch']}%</p>
        <p>Duration: {result['duration']}</p>
        <img src="data:image/png;base64,{result['current_screenshot']}" alt="Current Screenshot"/>
        <img src="data:image/png;base64,{result['baseline_screenshot']}" alt="Baseline Screenshot"/>
        <img src="data:image/png;base64,{result['diff_image']}" alt="Difference Image"/>
        """
    
    # Write report to file
    with open('reports/latest.html', 'w') as f:
        f.write(report_content.format(rows_html=rows_html, detail_blocks=detail_blocks, summary=summary))
```

### Common Errors and Prevention
- **Error**: Embedding overly large images in the report, causing the file to become excessively large.
  - **Solution**: Use thumbnails or compress images and provide links to view the full images.
    ```python
    # Example of using thumbnails
    detail_blocks += f"""
    <h2>Test Case {result['id']}</h2>
    <p>Browser: {result['browser']}, Viewport: {result['viewport']}</p>
    <p>Status: {result['status']}, Mismatch: {result['mismatch']}%</p>
    <p>Duration: {result['duration']}</p>
    <a href="data:image/png;base64,{result['current_screenshot']}"><img src="data:image/png;base64,{result['current_thumbnail']}" alt="Current Screenshot"/></a>
    <a href="data:image/png;base64,{result['baseline_screenshot']}"><img src="data:image/png;base64,{result['baseline_thumbnail']}" alt="Baseline Screenshot"/></a>
    <a href="data:image/png;base64,{result['diff_image']}"><img src="data:image/png;base64,{result['diff_thumbnail']}" alt="Difference Image"/></a>
    """
    ```
- **Error**: Exceptions occurring during report generation, resulting in an incomplete report.
  - **Solution**: Add exception handling during report generation and ensure the report file is not corrupted in case of errors.
    ```python
    try:
        with open('reports/latest.html', 'w') as f:
            f.write(report_content.format(rows_html=rows_html, detail_blocks=detail_blocks, summary=summary))
    except Exception as e:
        print(f"An error occurred while generating the report: {e}")
    ```

## Conclusion
By following the guidelines and utilizing the provided code snippets, you can effectively perform pixel-level image comparisons and generate detailed HTML reports for your visual regression tests. Always ensure to handle potential errors to maintain the integrity of your test reports.