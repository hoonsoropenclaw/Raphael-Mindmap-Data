# Micro-Skill: Data Cleaning and Information Management

## Overview
The `data_cleaning_and_information_management` micro-skill is designed to streamline data processing, ensure data integrity, and facilitate efficient information management. This involves using class tokens for data cleaning and type conversion, deduplicating and normalizing data such as URLs, handling asynchronous environments, clarifying missing or ambiguous information, and adhering to Standard Operating Procedures (SOPs).

## Key Functionalities

### 1. Data Cleaning with Class Tokens

#### 1.1 Purpose
This functionality leverages HTML class tokens to clean and convert data types, such as transforming star ratings from class names into numerical values.

#### 1.2 Implementation
```python
from bs4 import BeautifulSoup
from spider import DataCleaner, FieldSpec

soup = BeautifulSoup('<p class="star-rating Three"></p>', 'html.parser')
cleaner = DataCleaner([
    FieldSpec('rating', '.star-rating', type='rating', class_token_index=1)
])
result = cleaner.clean_one(soup, 'u', 't')
print(result.data['rating'])  # Output: 3
```

#### 1.3 Common Errors and Prevention
- **Class Name and Selector Mismatch**: Ensure selectors precisely match HTML class names (e.g., use `.star-rating` instead of `.r`).
- **Missing Tokens**: Incorporate default values or error handling to manage cases where expected tokens are absent.

### 2. URL Deduplication and Normalization

#### 2.1 URL Normalization
Normalization standardizes URLs to eliminate redundancies.

- **Removing Fragments**: Fragments (e.g., `#section`) are stripped as they don't affect page content.
- **Sorting Query Parameters**: Parameters are sorted alphabetically for consistency.
- **Case Normalization**: URLs are converted to lowercase to prevent case-sensitive duplicates.

##### Code Example
```python
from urllib.parse import urlparse, urlunparse

def normalize_url(url: str) -> str:
    parsed = urlparse(url)
    normalized = parsed._replace(fragment='')
    if parsed.query:
        query_params = sorted(parsed.query.split('&'))
        normalized = normalized._replace(query='&'.join(query_params))
    return urlunparse(normalized).lower()
```

#### 2.2 URL Deduplication
Deduplication ensures each URL is processed only once.

##### Code Example
```python
from typing import Set

class Deduper:
    def __init__(self):
        self.seen: Set[str] = set()

    def add(self, url: str) -> bool:
        normalized = normalize_url(url)
        if normalized in self.seen:
            return False
        self.seen.add(normalized)
        return True
```

### 3. Handling Asynchronous and Multi-threaded Environments

In multi-threaded or asynchronous contexts, thread safety is essential to prevent race conditions.

#### Enhanced Implementation with Thread Safety
```python
import asyncio
from asyncio.locks import Lock

class Deduper:
    def __init__(self):
        self.seen: Set[str] = set()
        self.lock: Lock = asyncio.Lock()

    async def add(self, url: str) -> bool:
        normalized = normalize_url(url)
        async with self.lock:
            if normalized in self.seen:
                return False
            self.seen.add(normalized)
            return True
```

### 4. Clarifying Missing Information

#### 4.1 Identifying Missing Data
```python
def list_missing_information(task_info: dict) -> list:
    missing_items = []
    required_fields = ['architect_feedback', 'workflow_trigger_list', 'node_types']
    for field in required_fields:
        if field not in task_info:
            missing_items.append(field)
    return missing_items
```

#### 4.2 Executing Clarification
```python
def execute_clarify(missing_items: list) -> str:
    clarification = ""
    for item in missing_items:
        clarification += f"Please provide detailed information for {item}.\n"
    return clarification
```

### 5. Information Management and SOP Adherence

#### 5.1 Standard Operating Procedure (SOP) Adherence

##### 5.1.1 Loading and Executing SOPs
```python
# Load the SOP from a predefined source
sop = load_sop('prompt_injection_fake_authority')

# Execute each step in the SOP sequentially
for step in sop.steps:
    execute_step(step)

# Verify that the SOP has been fully executed
if not sop.is_complete():
    handle_sop_incomplete()
```

##### 5.1.2 Error Handling and Prevention
- **Interrupted or Incomplete SOP Execution**
  - **Issue**: Steps may be skipped or the process may terminate prematurely.
  - **Solution**: Implement state tracking for each step and incorporate rollback or retry mechanisms.
    ```python
    def execute_sop_with_error_handling(sop):
        for step in sop.steps:
            try:
                execute_step(step)
            except Exception as e:
                log_error(e)
                rollback_step(step)
                retry_step(step)
        if not sop.is_complete():
            handle_sop_incomplete()
    ```

- **SOP-Task Mismatch**
  - **Issue**: The SOP does not align with current task requirements.
  - **Solution**: Regularly review and update SOPs to reflect the latest task requirements and industry best practices.

#### 5.2 Best Practices
- **Documentation**: Maintain clear and up-to-date documentation for each SOP.
- **Training**: Ensure all team members are trained on the latest SOPs.
- **Audit Trails**: Keep detailed logs of SOP execution for compliance and quality assurance.

### 6. Data and Information Management

#### 6.1 URL Normalization and Deduplication

##### 6.1.1 URL Normalization
- **Protocol Standardization**: Convert all URLs to a standard protocol (e.g., `http` to `https`).
    ```javascript
    function standardizeProtocol(url) {
      return url.startsWith('http://') ? url.replace('http://', 'https://') : url;
    }
    ```
- **Trailing Slash Consistency**: Ensure all URLs have a consistent use of trailing slashes.
    ```javascript
    function ensureTrailingSlash(url) {
      return url.endsWith('/') ? url : url + '/';
    }
    ```
- **Case Normalization**: Convert URLs to a standard case (e.g., lowercase).
    ```javascript
    function normalizeCase(url) {
      return url.toLowerCase();
    }
    ```

##### 6.1.2 Deduplication
- **Using a Set**: Utilize a `Set` to store unique URLs.
    ```javascript
    const urls = ['https://example.com/', 'https://Example.com', 'https://example.com'];
    const uniqueUrls = [...new Set(urls.map(standardizeProtocol).map(ensureTrailingSlash).map(normalizeCase))];
    ```
- **Using a Hash Map**: For large datasets, a hash map can be more efficient.
    ```javascript
    function deduplicateUrls(urls) {
      const map = {};
      urls.forEach(url => {
        const normalizedUrl = normalizeCase(ensureTrailingSlash(standardizeProtocol(url)));
        map[normalizedUrl] = true;
      });
      return Object.keys(map);
    }
    ```

#### 6.2 ESM Importmap Integration

##### 6.2.1 Description
Using importmap to integrate ESM modules in the browser, resolving module dependency issues.

##### 6.2.2 Key Code Snippets
```html
<script type="importmap">
  {
    "imports": {
      "react": "https://esm.sh/react@18.3.1/",
      "react-dom": "https://esm.sh/react-dom@18.3.1/",
      "@xyflow/react": "https://esm.sh/@xyflow/react@12.11.2/"
    }
  }
</script>

<script type="module">
  import React from 'react';
  import ReactDOM from 'react-dom';
  import { Flow } from '@xyflow/react';
  // Your application code
</script>
```

##### 6.2.3 Error Handling and Prevention
- **Browser Parsing Issues**
  - **Issue**: The browser fails to parse the importmap.
  - **Solution**: Ensure the browser supports importmap and the script tag's type attribute is set correctly.
    ```html
    <!-- Correct importmap script tag -->
    <script type="importmap">
      {
        "imports": {
          // ...
        }
      }
    </script>
    ```
- **Module Loading Failures**
  - **Issue**: Modules fail to load.
  - **Solution**: Verify CDN links and network connectivity. Use browser developer tools to inspect module loading errors.
    ```javascript
    // Checking network connectivity
    if (navigator.onLine) {
      // Proceed with module loading
    } else {
      // Handle offline scenario
    }
    ```

##### 6.2.4 Best Practices
- **Consistent Versioning**: Specify exact module versions to avoid unexpected updates.
- **Caching Strategies**: Implement caching to improve performance and reduce network load.
- **Fallback Mechanisms**: Provide fallback mechanisms for module loading failures to enhance resilience.

### 7. Data Clarification and User Interaction

#### 7.1 Identifying Missing Information
```python
def check_missing_data(data):
    return {key: value for key, value in data.items() if value is None}
```

#### 7.2 Clarification Tools
```html
<form id="data-clarification-form">
  <label for="missing-info">Please provide the missing information:</label>
  <input type="text" id="missing-info" name="missing-info">
  <input type="submit