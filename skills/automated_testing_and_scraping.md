# Automated Testing and Scraping with Playwright

## Overview

This micro-skill focuses on automating regression testing and data scraping using Playwright for headless browser control. It integrates a hybrid scraper framework that combines the strengths of `httpx` for fast HTTP requests, `BeautifulSoup` for static parsing, and Playwright for dynamic rendering. The framework employs a "light-first, heavy-later" strategy, prioritizing static parsing and resorting to browser-based rendering only when necessary.

## Key Components

### Hybrid Scraper Initialization

The hybrid scraper framework is initialized with configurations for crawling and data extraction. It leverages asynchronous programming to handle multiple URLs concurrently while maintaining efficiency and resource management.

#### Key Code Snippet

```python
from hybrid_scraper import CrawlConfig, ExtractionSchema, HybridCrawler

async def crawl_website(urls, schema_path):
    # Load the extraction schema from a JSON file
    schema = ExtractionSchema.from_dict(json.load(open(schema_path)))
    
    # Initialize the HybridCrawler with the schema and crawling configurations
    crawler = HybridCrawler(
        schema,
        CrawlConfig(
            mode="auto", 
            timeout_ms=5000, 
            concurrency=2, 
            retries=0, 
            allow_private=False
        ),
    )
    
    # Perform crawling and return static and dynamic results
    static, dynamic = await crawler.crawl_many(urls)
    return static, dynamic
```

### Configuration Details

- **CrawlConfig Parameters**:
  - `mode`: Determines the crawling mode (`"auto"`, `"static"`, or `"dynamic"`).
  - `timeout_ms`: Sets the timeout for each request in milliseconds.
  - `concurrency`: Controls the number of concurrent requests.
  - `retries`: Specifies the number of retry attempts for failed requests.
  - `allow_private`: Enables or disables access to private network resources.

- **ExtractionSchema**:
  - Defines the structure and selectors for data extraction from web pages.
  - Loaded from a JSON configuration file to allow flexible and reusable schemas.

## Error Prevention and Troubleshooting

### 1. Static Page Parsing Issues

- **Symptom**: Inability to correctly parse static pages.
- **Cause**: Incorrect `item_selector` or other field selectors in the `ExtractionSchema`.
- **Solution**: 
  - Verify the selectors in the `ExtractionSchema` are accurate.
  - Ensure the target web page's structure aligns with the defined selectors.

### 2. Playwright Rendering Failures

- **Symptom**: Playwright fails to render pages correctly.
- **Cause**: The target web page relies on specific resources or permissions, preventing the browser from loading properly.
- **Solution**: 
  - Check if the web page requires additional permissions or resources.
  - Adjust settings in `CrawlConfig`, such as enabling `allow_private`, to accommodate these requirements.

### 3. Resource Overload

- **Symptom**: Network resource exhaustion due to excessive concurrent requests.
- **Cause**: High `concurrency` settings leading to too many simultaneous requests.
- **Solution**: 
  - Modify the `concurrency` parameter in `CrawlConfig` to limit the number of concurrent requests.
  - Implement rate limiting or backoff strategies to manage resource usage effectively.

## Best Practices

- **Schema Management**: Keep extraction schemas in version control and document their purpose and usage to ensure consistency and ease of maintenance.
- **Configuration Validation**: Validate configurations before initiating crawls to catch potential issues early.
- **Logging and Monitoring**: Implement comprehensive logging and monitoring to track crawler performance and quickly identify and resolve issues.
- **Resource Management**: Regularly monitor system resources and adjust concurrency and timeout settings to optimize performance and prevent overload.

## Conclusion

By integrating Playwright with a hybrid scraper framework, this micro-skill provides a robust solution for automating regression testing and data scraping tasks. Careful configuration and error handling are essential to ensure reliable and efficient operation.