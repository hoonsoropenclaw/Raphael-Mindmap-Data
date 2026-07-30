# Real-Time Data Synchronization

## Target Skill Name
real_time_data_synchronization

## Target Summary
Implement real-time data extraction, synchronization, and output within applications, ensuring data integrity, security, and efficient handling across diverse sources and formats.

---

## 1. Data Extraction and Security

### 1.1 Advanced Site Parsing Framework

#### Purpose
Develop a flexible and extensible website parsing framework with an abstract interface, a lightweight CSS selector engine, and hybrid data extraction techniques to handle diverse website structures.

#### Site Parser Abstract Interface
- **Purpose**: Provide an abstract interface for developers to implement custom parsing logic without altering the core framework.
- **Key Code and Patterns**
  ```python
  from abc import ABC, abstractmethod
  from typing import List

  class SiteParser(ABC):
      @abstractmethod
      def parse_api(self, data: dict) -> List[ExtractedItem]:
          """Parse data from API response."""
          pass

      @abstractmethod
      def parse_html(self, html: str) -> List[ExtractedItem]:
          """Parse data from HTML content."""
          pass
  ```
- **Common Errors and Prevention**
  - **Error**: Tight coupling between parsing logic and the core framework.
    - **Prevention**: Use abstract interfaces to decouple parsing logic.
  - **Error**: Lack of adaptability to different website structures.
    - **Prevention**: Implement flexible parsing strategies (e.g., regular expressions) in the `parse_html` method.

#### Mini Soup CSS Selector
- **Purpose**: Offer a lightweight CSS selector engine for HTML parsing in constrained environments.
- **Key Code and Patterns**
  ```python
  class MiniSoup:
      def __init__(self, html: str):
          self.html = html

      def select(self, selector: str) -> list:
          """Select elements based on CSS selector."""
          # Simple CSS selector parsing logic
          ...
  ```
- **Common Errors and Prevention**
  - **Error**: Overly complex selectors leading to degraded performance.
    - **Prevention**: Use simple selectors and avoid complex syntax.
  - **Error**: Lack of adaptability to changes in HTML structure.
    - **Prevention**: Design selectors to account for potential changes and use flexible parsing strategies.

#### Hybrid Extractor Framework
- **Purpose**: Create a reusable data extraction framework that prioritizes API-based data extraction, falls back to HTML parsing when necessary, and cross-validates data from both sources.
- **Key Code and Patterns**
  ```python
  class HybridExtractor:
      def __init__(self, site_parser: SiteParser):
          self.site_parser = site_parser
          self.http_client = HttpClient()

      def extract(self) -> list[ExtractedItem]:
          api_data = self._fetch_api()
          html_data = self._fetch_html()
          if api_data and html_data:
              return self._merge_and_validate(api_data, html_data)
          elif api_data:
              return api_data
          elif html_data:
              return html_data
          else:
              return []

      def _fetch_api(self) -> list[ExtractedItem]:
          """Fetch data from API."""
          # Implementation
          ...

      def _fetch_html(self) -> list[ExtractedItem]:
          """Fetch and parse HTML."""
          # Implementation
          ...

      def _merge_and_validate(self, api_data: list[ExtractedItem], html_data: list[ExtractedItem]) -> list[ExtractedItem]:
          """Merge and cross-validate data from both sources."""
          # Implementation
          ...
  ```
- **Common Errors and Prevention**
  - **Error**: Lack of consistency between API and HTML parsing.
    - **Prevention**: Use unique identifiers for cross-validation and prioritize the more reliable data source.
  - **Error**: Over-reliance on third-party libraries.
    - **Prevention**: Use standard libraries (e.g., `urllib` and `re`) for data extraction and parsing.

### 1.2 BeautifulSoup Dynamic Scraper

#### Purpose
Utilize BeautifulSoup to scrape dynamic web data and store it in CSV, JSON, and SQLite formats.

#### Key Code and Patterns
```python
from bs4 import BeautifulSoup
import requests
import csv
import json
import sqlite3

def fetch_html(url: str) -> str:
    response = requests.get(url)
    return response.text

def parse_html(html: str) -> dict:
    soup = BeautifulSoup(html, 'lxml')
    data = {}
    data['title'] = soup.title.string if soup.title else ''
    data['headings'] = [h.text for h in soup.find_all(['h1', 'h2', 'h3'])]
    data['paragraphs'] = [p.text for p in soup.find_all('p')]
    return data

def store_data(data: dict, filename_csv: str, filename_json: str, db_path: str):
    # Store as CSV
    with open(filename_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=data.keys())
        writer.writeheader()
        writer.writerow(data)
    # Store as JSON
    with open(filename_json, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    # Store as SQLite
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS pages (url TEXT, title TEXT, headings TEXT, paragraphs TEXT)')
    c.execute('INSERT INTO pages (url, title, headings, paragraphs) VALUES (?, ?, ?, ?)', (url, data['title'], json.dumps(data['headings']), json.dumps(data['paragraphs'])))
    conn.commit()
    conn.close()
```

#### Common Errors and Prevention
- **Dynamic Content Scraping Failure**: BeautifulSoup cannot execute JavaScript, leading to failure in scraping dynamically generated content.
  - **Solution**: Use Selenium or Playwright for dynamic content scraping.
- **Parsing Errors**: Different websites have varying HTML structures, causing parsing failures.
  - **Solution**: Use more robust parsing logic or customize parsing for specific websites.

### 1.3 Prompt Injection Handling

#### Overview
This skill involves handling prompt injection attacks to ensure system security. By validating and sanitizing input data, we can prevent malicious code execution.

#### Key Code Snippets and Patterns
```javascript
function sanitizeInput(input) {
  return input.replace(/[^a-zA-Z0-9 ]/g, '');
}

function handlePrompt(prompt) {
  const sanitizedPrompt = sanitizeInput(prompt);
  // Further process sanitizedPrompt
}
```

#### Common Errors and Prevention
- **Error**: Failure to validate and sanitize user input, leading to prompt injection attacks.
  - **Solution**: Use regular expressions or other methods to validate and sanitize input, removing potential malicious code.
- **Error**: Over-sanitizing input, resulting in the removal of legitimate data.
  - **Solution**: Carefully design sanitization rules to ensure only malicious code is removed without affecting legitimate data.
- **Error**: Lack of subsequent validation on sanitized data, leading to security vulnerabilities.
  - **Solution**: Perform subsequent validation on sanitized data to ensure its integrity and security.

---

## 2. PDF Data Extraction and Excel Output

### 2.1 Extracting Tables from Digital PDFs with `pdfplumber`

#### Description
The `pdfplumber` library is used to parse and extract tables from digitally created PDF files. The `extract_tables()` method identifies and extracts table structures based on the PDF's text layout.

#### Key Code Snippet
```python
import pdfplumber

def extract_tables_with_pdfplumber(pdf_path):
    tables = []
    with pdfplumber.open(pdf_path) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            extracted_tables = page.extract_tables()
            if extracted_tables:
                for table in extracted_tables:
                    tables.append({'page': page_number, 'data': table})
    return tables
```

#### Common Errors and Solutions
- **Issue**: Incorrect table boundary detection or merged cells not recognized.
  - **Solution**: Adjust the `table_settings` parameters, such as increasing the sensitivity of `vertical_strategy` or `horizontal_strategy`.
- **Issue**: Poor performance with large PDF files.
  - **Solution**: Implement pagination or use multithreading to speed up the processing.

### 2.2 OCR Processing for Scanned PDFs with `pytesseract`

#### Description
For scanned or image-based PDFs, `pytesseract` is employed to perform OCR (Optical Character Recognition) to convert images into text. The `PyMuPDF` library (`fitz`) is used to convert PDF pages into images.

#### Key Code Snippet
```python
import pytesseract
from PIL import Image
import fitz  # PyMuPDF

def ocr_with_pytesseract(pdf_path):
    text = ""
    doc = fitz.open(pdf_path)
    for page_number in range(len(doc)):
        page = doc.load_page(page_number)
        pix = page.get_pixmap(dpi=300)
        image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        ocr_text = pytesseract.image_to_string(image, lang='chi_tra+eng')
        text += ocr_text + "\n"
    return text
```

#### Common Errors and Solutions
- **Issue**: Low OCR recognition accuracy.
  - **Solution**: Ensure the image resolution is high enough (recommended 300 DPI) and use appropriate language packs (e.g., `chi_tra.traineddata`).
- **Issue**: High memory consumption with large PDF files.
  - **Solution**: Implement pagination or use memory-optimized processing techniques.

---

## 3. Real-Time Data Synchronization with WebSockets