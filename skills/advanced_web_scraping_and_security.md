# Advanced Web Scraping and Security

## Overview
This micro-skill focuses on implementing a multi-tiered scraping architecture while managing network security and scraping activities. It ensures protection against Server-Side Request Forgery (SSRF) attacks and compliance with `robots.txt` policies.

---

## Tiered Scraping with Fallback

### Description
This micro-skill implements a multi-tiered scraping architecture with three tiers:
1. **Tier1Static**: Uses `requests` and `BeautifulSoup` for static page scraping.
2. **Tier2Dynamic**: Utilizes `Selenium` or `Playwright` for dynamic content scraping.
3. **Tier3Adaptive**: Employs a pool of fuzzy selectors for content extraction, suitable for complex or frequently changing page structures.

The system automatically switches to the next tier if the current one fails.

### Key Code Snippet
```python
from spider import Tier1Static, Tier2Dynamic, Tier3Adaptive, SpiderController

class SpiderController:
    def __init__(self, schema, mode='list', use_dynamic=False):
        self.schema = schema
        self.mode = mode
        self.use_dynamic = use_dynamic
        self.tier1 = Tier1Static()
        self.tier2 = Tier2Dynamic()
        self.tier3 = Tier3Adaptive(self.tier1)

    def crawl_one(self, url):
        try:
            record = self.tier1.fetch(url, self.schema)
            return {'ok': True, 'tier': 'tier1-static', 'record': record}
        except Exception as e:
            if self.use_dynamic:
                try:
                    record = self.tier2.fetch(url, self.schema)
                    return {'ok': True, 'tier': 'tier2-dynamic', 'record': record}
                except Exception as e:
                    try:
                        record = self.tier3.fetch(url, self.schema)
                        return {'ok': True, 'tier': 'tier3-adaptive', 'record': record}
                    except Exception as e:
                        return {'ok': False, 'tier': 'failed', 'error': str(e)}
            else:
                return {'ok': False, 'tier': 'failed', 'error': str(e)}
```

### Common Errors and Prevention Methods
- **Tier Switching Logic Errors**: Ensure each tier's exceptions are caught and trigger the next tier's scraping when necessary.
- **Fuzzy Selector Pool Coverage**: Design the selector pool to include multiple alternatives for each critical field to prevent data loss.

---

## Web Security and Scraping Management

### SSRF Guard

#### Purpose
Protects web applications from SSRF attacks by enforcing strict controls over outbound HTTP requests.

#### Key Features
1. **Protocol Restriction**
   - **Allowed Protocols**: Only HTTP and HTTPS are permitted.
   - **Blocked Protocols**: All other protocols (e.g., FTP, FILE) are blocked.

2. **IP Address Filtering**
   - **Private IP Ranges**: Blocks requests to private IP ranges (e.g., 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16).
   - **Localhost and .local Domains**: Blocks requests to `localhost`, `127.0.0.1`, and domains ending with `.local`.
   - **CGNAT and ULA**: Blocks requests to Carrier-Grade NAT (CGNAT) and Unique Local Address (ULA) ranges.

3. **DNS Public-Host Verification**
   - **Initial URL Check**: Verifies that the initial URL resolves to a public IP address.
   - **Redirection and Subresource Checks**: Ensures all redirected and subresource URLs also resolve to public IP addresses.

4. **Request-Level Enforcement**
   - **Redirection Handling**: Applies security checks to all redirection URLs.
   - **Subresource Protection**: Ensures all subresources (e.g., images, scripts) are subject to the same security checks.

5. **Performance Optimization**
   - **Caching Mechanism**: Caches DNS resolution results and security checks to improve performance.

#### Error Prevention
- **Input Validation**: Ensures all URLs are properly formatted.
- **Exception Handling**: Gracefully handles exceptions related to DNS resolution and network requests.
- **Logging**: Logs all blocked requests and security violations for auditing.

#### Example Code Snippet
```python
def is_allowed_url(url):
    # Check protocol
    if not url.startswith(('http://', 'https://')):
        return False

    # Resolve DNS
    try:
        hostname = url.split('//')[-1].split('/')[0]
        resolved_ips = socket.gethostbyname_ex(hostname)[-1]
    except socket.gaierror:
        return False

    # Check for public IP
    for ip in resolved_ips:
        if not is_public_ip(ip):
            return False

    return True

def is_public_ip(ip):
    # Check for private, local, CGNAT, and ULA IPs
    private_ip_ranges = [
        '10.0.0.0/8',
        '172.16.0.0/12',
        '192.168.0.0/16',
        '127.0.0.0/8',
        '169.254.0.0/16',
        '100.64.0.0/10',
        '192.0.0.0/24',
        '192.0.2.0/24',
        '198.51.100.0/24',
        '203.0.113.0/24',
        '::1',
        'fe80::/10',
        'fc00::/7'
    ]
    for ip_range in private_ip_ranges:
        if IPAddress(ip) in IPNetwork(ip_range):
            return False
    return True
```

### Robots.txt Parser

#### Purpose
Parses and enforces the rules defined in `robots.txt` files to manage web crawling activities.

#### Key Features
1. **Robots.txt Parsing**
   - **File Retrieval**: Fetches the `robots.txt` file from the target website.
   - **Syntax Parsing**: Parses the file to extract rules for different user agents.

2. **Rule Handling**
   - **Allow/Disallow Rules**: Processes `Allow` and `Disallow` directives to determine which URLs are permitted or blocked.
   - **Wildcard Support**: Supports the use of wildcards (`*`) in rules to match multiple URLs.
   - **Priority Enforcement**: Ensures that more specific rules take precedence over more general ones.

3. **Security Enforcement**
   - **Private Address Blocking**: Prevents crawling of URLs that redirect to private IP addresses or internal network resources.

#### Error Prevention
- **Robots.txt Retrieval**: Handles cases where the `robots.txt` file is unavailable or malformed.
- **Rule Validation**: Validates the syntax and structure of `robots.txt` rules to prevent parsing errors.
- **Redirection Handling**: Ensures that any redirects from the `robots.txt` file do not point to private or restricted addresses.

#### Example Code Snippet
```python
from urllib.parse import urlparse, urljoin
import re

def parse_robots_txt(content, base_url):
    rules = {}
    for line in content.splitlines():
        if line.startswith('User-agent:'):
            user_agent = line.split(':', 1)[1].strip()
            rules[user_agent] = {'Allow': [], 'Disallow': []}
        elif line.startswith('Allow:'):
            path = line.split(':', 1)[1].strip()
            rules[user_agent]['Allow'].append(path)
        elif line.startswith('Disallow:'):
            path = line.split(':', 1)[1].strip()
            rules[user_agent]['Disallow'].append(path)
    return rules

def is_url_allowed(url, rules, user_agent='*'):
    parsed_url = urlparse(url)
    path = parsed_url.path
    if user_agent in rules:
        for pattern in rules[user_agent]['Disallow']:
            if re.match(pattern.replace('*', '.*'), path):
                return False
        for pattern in rules[user_agent]['Allow']:
            if re.match(pattern.replace('*', '.*'), path):
                return True
    return True
```

---

## Tiered Scraping Strategy

### 1. Tier 1: Pure SSR Page Scraping
For pure Server-Side Rendered (SSR) web pages, use `requests` and `BeautifulSoup` for quick scraping.

#### Key Code Snippet
```python
import requests
from bs4 import BeautifulSoup

# Send HTTP request
resp = requests.get(url, timeout=15)

# Parse HTML content
soup = BeautifulSoup(resp.text, "html.parser")

# Extract required data
for article in soup.select("article.product_pod"):
    title = article.h3.a.get("title")
    price = parse_price(article.select_one(".price_color").get_text())
    rating = parse_rating(article.select_one(".star-rating").get("class"))
    # Further data processing...
```

### 2. Tier 2: Dynamic Rendering Page Scraping
For dynamic pages that require JavaScript rendering, use `Scrapling DynamicFetcher` (based on Playwright) for scraping.

#### Key Code Snippet
```python
from scrapling import DynamicFetcher

# Fetch dynamic content
page = DynamicFetcher.fetch(product_url, headless=True, network_idle=True)

# Extract required data
# Assuming hydrated DOM contains title, price, availability fields
title = page.css("h1.product_title::text").get()
price = page.css(".price_color::text").get()
availability = page.css(".availability::text").get()
# Further data processing...
```

### 3. Tier 3: Adaptive Relocation