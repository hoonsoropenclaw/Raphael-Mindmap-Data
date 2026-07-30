# Document and Calendar Integration Micro-Skill

## Overview

This micro-skill combines advanced PDF and OCR processing with Google Calendar integration, enabling the extraction of data from various PDF documents and scheduling events directly into Google Calendar. It leverages multiple technologies, including PyMuPDF, Tesseract, PDF.js, Tesseract.js, Playwright, and the Google Calendar API, to provide a robust solution for document processing and event management.

---

## 1. Advanced PDF and OCR Processing

### 1.1 PDF Text Extraction and OCR Processing

#### Purpose
Extract text from PDF files, including text-based PDFs and scanned/image-based PDFs using OCR.

#### Key Code Snippets and Patterns

##### Text Extraction with PyMuPDF (Python)
```python
import pymupdf

def extract_text_pymupdf(pdf_path):
    """
    Extracts text from a PDF using PyMuPDF.

    :param pdf_path: Path to the PDF file.
    :return: A list of strings, each representing the text of a page.
    """
    doc = pymupdf.open(pdf_path)
    pages_text = [page.get_text('text') for page in doc]
    return pages_text
```

##### OCR Processing with Tesseract (Python)
```python
from PIL import Image
import pytesseract

def extract_text_via_ocr(pdf_path):
    """
    Extracts text from a PDF using OCR with Tesseract.

    :param pdf_path: Path to the PDF file.
    :return: A list of strings, each representing the OCR-processed text of a page.
    """
    doc = pymupdf.open(pdf_path)
    pages_text = []
    for page in doc:
        pix = page.get_pixmap()
        img = Image.frombytes('RGB', [pix.width, pix.height], pix.samples)
        text = pytesseract.image_to_string(img, lang='chi_tra+eng')
        pages_text.append(text)
    return pages_text
```

#### Common Errors and Solutions
- **OCR Accuracy Issues**: Low-quality scans or non-standard fonts can reduce OCR accuracy.
  - **Solution**: Preprocess images by increasing contrast, resizing, or applying filters. Use language-specific OCR models.
- **Inefficient Processing of Large PDFs**: Large files can slow down processing.
  - **Solution**: Implement multithreading or multiprocessing to handle multiple pages in parallel.

### 1.2 Regex-Based Data Extraction

#### Purpose
Extract specific data fields (e.g., dates, IDs, amounts) from unstructured text using regular expressions.

#### Key Code Snippets and Patterns
```python
import re

def extract_key_data(text):
    """
    Extracts key data from unstructured text using regex patterns.

    :param text: The text to extract data from.
    :return: A dictionary containing extracted data fields.
    """
    patterns = {
        'document_number': r'發文字號[:：]\s*(府授文號字第\d+號)',
        'roc_date': r'中華民國(\d{1,3})年(\d{1,2})月(\d{1,2})日',
        'iso_date': r'\d{4}[-/]\d{1,2}[-/]\d{1,2}',
        'amount': r'NT\$\s*\d{1,3}(,\d{3})*',
        'email': r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+',
        'phone': r'\(?\d{2,4}\)?[- \.]?\d{6,8}',
        'address': r'[台灣市縣鄉鎮區路號樓]\s*\d{1,5}[巷弄號樓]?',
    }
    extracted_data = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, text)
        if match:
            extracted_data[key] = match.group(1)
    return extracted_data
```

#### Common Errors and Solutions
- **Rigid Patterns**: Regex patterns that are too strict may fail to match variations in data formats.
  - **Solution**: Use more flexible patterns with optional groups and alternative delimiters.
- **Overlapping Patterns**: Overlapping patterns can lead to incorrect extractions.
  - **Solution**: Prioritize patterns based on specificity and order them accordingly.

### 1.3 Frontend UI with PDF.js and Tesseract.js

#### Purpose
Create a user-friendly interface for uploading and processing PDFs, utilizing PDF.js for rendering and Tesseract.js for in-browser OCR.

#### Key Code Snippets and Patterns
```html
<!DOCTYPE html>
<html lang="zh-Hant">
<head>
    <meta charset="UTF-8">
    <title>PDF OCR Processing</title>
    <script type="module">
        import { getDocument, GlobalWorkerOptions } from 'https://cdn.jsdelivr.net/npm/pdfjs-dist@4.0.379/build/pdf.min.mjs';
        import Tesseract from 'https://cdn.jsdelivr.net/npm/tesseract.js@5/dist/tesseract.min.js';
    </script>
</head>
<body>
    <input type="file" id="pdf-upload" accept="application/pdf">
    <canvas id="pdf-render"></canvas>
    <script>
        const upload = document.getElementById('pdf-upload');
        upload.addEventListener('change', (e) => {
            const file = e.target.files[0];
            const loadingTask = getDocument({ url: URL.createObjectURL(file) });
            loadingTask.promise.then(pdf => {
                // Render PDF
                pdf.getPage(1).then(page => {
                    const viewport = page.getViewport({ scale: 1.5 });
                    const canvas = document.getElementById('pdf-render');
                    canvas.height = viewport.height;
                    canvas.width = viewport.width;
                    const renderContext = {
                        canvasContext: canvas.getContext('2d'),
                        viewport: viewport
                    };
                    page.render(renderContext);
                    // Perform OCR
                    Tesseract.recognize(canvas, 'chi_tra+eng').then(({ data: { text } }) => {
                        console.log(text);
                    });
                });
            });
        });
    </script>
</body>
</html>
```

#### Common Errors and Solutions
- **CORS Issues**: Loading PDFs from external sources can lead to CORS errors.
  - **Solution**: Ensure PDFs are served with appropriate CORS headers or use local file uploads.
- **Performance Issues with Large PDFs**: Large files can cause rendering and OCR processing delays.
  - **Solution**: Implement pagination or lazy loading for rendering and OCR processing.

### 1.4 Playwright Automation for PDF OCR Workflow

#### Purpose
Automate the process of uploading PDFs, extracting text, performing OCR, extracting specific fields, and exporting the results using Playwright.

#### Key Code Snippets and Patterns
```javascript
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('http://localhost:8000');
  
  // Upload PDF
  const [fileChooser] = await Promise.all([
    page.waitForEvent('filechooser'),
    page.click('#uploadButton')
  ]);
  await fileChooser.setFiles(['/path/to/sample.pdf']);
  
  // Wait for OCR to complete
  await page.waitForSelector('#ocrResult', { timeout: 60000 });
  
  // Extract text
  const text = await page.$eval('#ocrResult', el => el.value);
  console.log('Extracted Text:', text);
  
  await browser.close();
})();
```

#### Common Errors and Solutions
- **File Upload Failure**: File upload may fail due to incorrect file paths or permissions.
  - **Solution**: Ensure file paths are correct and file permissions are set appropriately.
- **OCR Processing Timeout**: OCR processing may take longer than expected.
  - **Solution**: Increase the timeout duration, optimize the OCR processing logic, or limit the size of the files being processed.

---

## 2. Google Calendar Integration

### 2.1 Google Calendar OAuth Device Flow

#### Purpose
To authenticate and authorize access to the Google Calendar API using the OAuth Device Flow, which is suitable for devices with limited input capabilities.

#### Key Steps

1. **Create OAuth Credentials**:
   - Navigate to the [Google Cloud Console](https://console.cloud.google.com/).
   - Create a new project or select an existing one.
   - Go to **APIs & Services > Credentials**.
   - Click **Create Credentials > OAuth client ID**.
   - Select **TV and limited input devices** as the application type.
   - Download the `client_secret_*.json` file and rename it to `calendar_client.json`.

2. **Authenticate Using Device Flow**:
   - Use the provided Python script to initiate the device flow.
   - Run the command: `python3 src/calendar_client.py auth`.
   - The script will display a `user_code` and a `verification_url`.
   - Open a browser, navigate to the `verification_url`, and enter the `user_code` to complete the authentication process.

#### Key Code Snippet
```python
from google_auth_oauthlib.flow import InstalledAppFlow

def authenticate_device_flow(client_secret_path):
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    flow = InstalledAppFlow.from_client_secrets_file(client_secret_path, SCOPES)
    device_flow_info = flow.device_flow()
    print(f"Visit the URL: {device_flow_info['verification_url']}")
    print(f"Enter the code: {device_flow_info['user_code']}")
    flow.fetch_token(device