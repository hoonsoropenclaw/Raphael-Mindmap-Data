# Advanced Site Parsing Framework

## Target Skill Name
advanced_site_parsing_framework

## Target Summary
构建一个高级网站解析框架，集成抽象接口、轻量级 CSS 选择器引擎以及混合数据提取技术，以实现对不同网站结构的灵活解析和数据提取。

---

## 1. Site Parser Abstract Interface

### Purpose
提供一个可扩展的抽象接口，允许开发者为不同网站实现自定义的 API 和 HTML 解析逻辑，而无需修改核心提取框架。

### Key Code and Patterns
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

### Common Errors and Prevention
- **Error**: Tight coupling between parsing logic and the core framework, making it difficult to extend.
  - **Prevention**: Use abstract interfaces to decouple parsing logic from the core framework, ensuring that each site's parsing logic is implemented independently.
- **Error**: Lack of adaptability to different website structures, leading to parsing failures.
  - **Prevention**: Implement flexible parsing strategies (e.g., regular expressions or lightweight parsers) in the `parse_html` method to accommodate varying HTML structures.

---

## 2. Mini Soup CSS Selector

### Purpose
Provide a lightweight CSS selector engine for HTML parsing in constrained environments, avoiding reliance on third-party libraries.

### Key Code and Patterns
```python
class MiniSoup:
    def __init__(self, html: str):
        self.html = html

    def select(self, selector: str) -> list:
        """Select elements based on CSS selector."""
        # Simple CSS selector parsing logic
        ...
```

### Common Errors and Prevention
- **Error**: Overly complex selectors leading to degraded parsing performance.
  - **Prevention**: Use simple selectors and avoid complex selector syntax.
- **Error**: Lack of adaptability to changes in HTML structure, causing parsing failures.
  - **Prevention**: Design selectors to account for potential changes in HTML structure and use more flexible parsing strategies (e.g., regular expressions) as a supplement.

---

## 3. Hybrid Extractor Framework

### Purpose
Provide a reusable data extraction framework that prioritizes API-based data extraction when available, falls back to HTML parsing when the API is unavailable, and cross-validates data from both sources to ensure consistency.

### Key Code and Patterns
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

### Common Errors and Prevention
- **Error**: Lack of consistency between API and HTML parsing, leading to data conflicts.
  - **Prevention**: Use unique identifiers (e.g., IDs) for cross-validation and prioritize the more reliable data source.
- **Error**: Over-reliance on third-party libraries, causing issues in constrained environments.
  - **Prevention**: Use standard libraries (e.g., `urllib` and `re`) for data extraction and parsing to ensure framework versatility.

---

## Summary of Best Practices
- **Modularity**: Separate parsing logic from the core framework using abstract interfaces.
- **Flexibility**: Implement flexible parsing strategies to handle varying website structures.
- **Performance**: Optimize CSS selectors for performance and simplicity.
- **Reliability**: Cross-validate data from multiple sources to ensure consistency and accuracy.
- **Portability**: Rely on standard libraries to enhance framework portability and adaptability to different environments.

This comprehensive framework ensures efficient, reliable, and flexible website parsing and data extraction, accommodating the diverse and dynamic nature of modern websites.