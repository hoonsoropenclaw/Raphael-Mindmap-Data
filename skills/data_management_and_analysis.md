# Data Management and Analysis (data_management_and_analysis)

## Overview
The **data_management_and_analysis** micro-skill is designed to equip you with the expertise to efficiently manage and organize data and images, as well as perform data extraction and analysis to gain valuable insights. This comprehensive guide covers a range of techniques, including command-line data processing, advanced data extraction methods, image comparison, screenshot management, and data persistence. Emphasis is placed on robust data handling, comprehensive error management, and efficient processing to ensure reliable and accurate results.

---

## 1. Command Line Data Processing

### 1.1. Sending HTTP Requests with `curl`

#### 1.1.1. Description
The `curl` command is a powerful tool for sending HTTP requests, saving response content, and retrieving metadata such as HTTP status codes and download sizes.

#### 1.1.2. Key Command Pattern
```bash
curl -sS -o /path/to/output_file -w "HTTP=%{http_code} BYTES=%{size_download}\n" http://example.com/page.html
```
- `-sS`: Runs `curl` in silent mode, suppressing progress meters and error messages but allowing error codes to be displayed.
- `-o /path/to/output_file`: Specifies the file path where the response content will be saved.
- `-w "FORMAT"`: Defines the format for the output metadata. In this case, it outputs the HTTP status code and the number of bytes downloaded.
- `http://example.com/page.html`: The URL to which the HTTP request is sent.

#### 1.1.3. Example Usage
```bash
curl -sS -o /tmp/served.html -w "HTTP=%{http_code} BYTES=%{size_download}\n" http://127.0.0.1:8766/web_output.html
```
This command sends an HTTP GET request to `http://127.0.0.1:8766/web_output.html`, saves the response to `/tmp/served.html`, and outputs the HTTP status code and the number of bytes downloaded.

#### 1.1.4. Common Errors and Prevention
- **CORS Issues**: 
  - **Problem**: The request may be blocked by the browser's CORS policy if the server does not have the appropriate CORS headers.
  - **Solution**: 
    - Ensure the server is configured with the correct CORS headers.
    - Use a CDN or proxy that supports CORS.
    - When using `curl` from the command line, CORS is generally not an issue as it bypasses browser restrictions.
- **Network Timeouts**:
  - **Problem**: The request may take too long to complete, resulting in a timeout.
  - **Solution**: Use the `--max-time` parameter to set a timeout limit (in seconds).
    ```bash
    curl -sS -o /tmp/served.html -w "HTTP=%{http_code} BYTES=%{size_download}\n" http://127.0.0.1:8766/web_output.html --max-time 10
    ```
    This sets the timeout to 10 seconds.

### 1.2. Counting Keyword Occurrences with `grep`

#### 1.2.1. Description
The `grep` command is used to search for specific keywords within a file and count the number of times each keyword appears.

#### 1.2.2. Key Command Pattern
```bash
for kw in 'ReactFlow' 'authorize' 'RBAC_MATRIX'; do
  n=$(grep -F "$kw" /path/to/input_file | wc -l)
  printf "%s %d\n" "$kw" "$n"
done
```
- `for kw in 'keyword1' 'keyword2' ...; do`: Iterates over a list of keywords.
- `grep -F "$kw" /path/to/input_file`: Searches for the exact keyword (`-F` for fixed strings) in the specified file.
- `wc -l`: Counts the number of lines where the keyword appears.
- `printf "%s %d\n" "$kw" "$n"`: Prints the keyword and the count in a formatted manner.

#### 1.2.3. Example Usage
```bash
for kw in 'ReactFlow' 'authorize' 'RBAC_MATRIX'; do
  n=$(grep -F "$kw" /tmp/served.html | wc -l)
  printf "%s %d\n" "$kw" "$n"
done
```
This command searches for the keywords `ReactFlow`, `authorize`, and `RBAC_MATRIX` in the file `/tmp/served.html` and prints the number of occurrences for each.

#### 1.2.4. Common Errors and Prevention
- **Improper Pattern Escaping**:
  - **Problem**: If the keyword contains special characters, `grep` may interpret them as regular expressions, leading to unexpected results.
  - **Solution**: 
    - Enclose the keyword in quotes or escape special characters.
    - Use the `-F` option to treat the pattern as a fixed string.
      ```bash
      grep -F "$kw" /path/to/input_file
      ```
- **Case Sensitivity**:
  - **Problem**: By default, `grep` is case-sensitive, which may lead to missed occurrences if the case does not match.
  - **Solution**: Use the `-i` option to perform a case-insensitive search.
      ```bash
      grep -Fi "$kw" /path/to/input_file | wc -l
      ```

---

## 2. Data Extraction Techniques

### 2.1. PDF.js for Text Extraction

#### 2.1.1. Description
PDF.js is a JavaScript library that renders and manipulates PDF files within a web environment, enabling the extraction of text content from PDFs that contain a text layer.

#### 2.1.2. Key Code Snippet
```javascript
// Wait for PDF.js to finish rendering
page.wait_for_function("typeof window.__hrPdf === 'object'");

// Upload the PDF file
page.set_input_files("#file", "/path/to/pdf");

// Wait for the extract button to be clickable and click it
page.wait_for_function("document.getElementById('btnExtract').disabled === false", timeout=60000);
page.click("#btnExtract");

// Wait for OCR processing to complete (if applicable)
page.wait_for_function("document.getElementById('eventCount').textContent !== '0'", timeout=120000);

// Extract the text content
const text = page.text_content("#textLayerLabel");
```

#### 2.1.3. Common Errors and Prevention
- **Error**: PDF.js fails to render the PDF correctly, leading to failed text extraction.
  - **Solution**: Ensure the PDF file is valid and that the PDF.js library is correctly loaded.
- **Error**: Extracted text is empty or does not meet expectations.
  - **Solution**: Verify if the PDF contains a text layer; if not, consider using OCR tools for image-based text recognition.

### 2.2. Tesseract.js for OCR Processing

#### 2.2.1. Description
Tesseract.js is a browser-based OCR library that converts image-based text into editable text, suitable for scanned PDFs or image files lacking a text layer.

#### 2.2.2. Key Code Snippet
```javascript
// Upload the image file
page.set_input_files("#file", "/path/to/image");

// Wait for OCR processing to complete
page.wait_for_function("document.getElementById('eventCount').textContent !== '0'", timeout=120000);

// Extract the OCR result
const ocrText = page.text_content("#ocrResult");
```

#### 2.2.3. Common Errors and Prevention
- **Error**: OCR recognition results are inaccurate.
  - **Solution**: Ensure the uploaded image is clear with high contrast. Preprocessing, such as grayscale conversion or binarization, may be necessary.
- **Error**: OCR processing takes too long.
  - **Solution**: Optimize image resolution and avoid uploading excessively large image files.

### 2.3. Regex-Based Field Parsing

#### 2.3.1. Description
Regular expressions (regex) are used to extract structured data, such as names, emails, phone numbers, etc., from unstructured or semi-structured text.

#### 2.3.2. Key Code Snippet
```javascript
// Define regex patterns
const NAME_RE = /(?:員工姓名|應徵者|面試者|Employee\s*Name|Candidate|面试者|Name)\s*[：:]?\s*([A-Za-z\u4e00-\u9fa5][A-Za-z\u4e00-\u9fa5\s]{1,20})/;
const DATE_RE = [{
  type: "到職",
  re: /(到職日期|報到日期|到職日|Start\s*Date|Report\s*Date)\s*[：:]?\s*(\d{3,4}[\/.\\-年]\d{1,2}[\/.\\-月]\d{1,2}日?)/i
}];

// Extract fields
const lines = text.split(/\r?\n/).map(s => s.trim()).filter(Boolean);
const foundNames = [];
for (const ln of lines) {
  const m = ln.match(NAME_RE);
  if (m) foundNames.push([ln, m[1]]);
}
```

#### 2.3.3. Common Errors and Prevention
- **Error**: Regex patterns match incorrectly or incompletely.
  - **Solution**: Thoroughly test regex patterns to ensure they cover all possible text formats.

---

## 3. Image and Data Management

### 3.1. Pixelmatch Image Comparison

#### 3.1.1