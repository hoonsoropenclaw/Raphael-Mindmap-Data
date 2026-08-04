# Data Management and Testing

## Overview
The **data_management_and_testing** micro-skill is a comprehensive solution for automating data workflows, managing file input/output (I/O) operations, and implementing automated testing using Playwright. This skill integrates intelligent data crawling, secure data extraction, dynamic visualization, schema inference, efficient pagination management, systematic file handling, and robust automated testing to ensure data integrity, accurate analysis, structured data management, and secure, efficient file operations for diverse applications.

## Key Components

### 1. Intelligent Crawler System

#### 1.1 Crawler Architecture

##### 1.1.1 Static Crawler
- **Module**: `StaticCrawler`
- **Description**: Utilizes `BeautifulSoup` and `urllib` to parse and extract data from static web pages.
- **Features**:
  - Efficiently handles HTML content.
  - Extracts links, images, and other static elements.
- **Implementation**:
  ```python
  from bs4 import BeautifulSoup
  import urllib.request

  def static_crawler(url):
      response = urllib.request.urlopen(url)
      html = response.read()
      soup = BeautifulSoup(html, 'html.parser')
      links = [a.get('href') for a in soup.find_all('a', href=True)]
      images = [img.get('src') for img in soup.find_all('img', src=True)]
      return links, images
  ```

##### 1.1.2 Dynamic Crawler
- **Module**: `DynamicCrawler`
- **Description**: Uses Selenium to handle dynamic content rendered by JavaScript.
- **Features**:
  - Supports JavaScript-rendered pages.
  - Interacts with dynamic elements like buttons and forms.
- **Implementation**:
  ```python
  from selenium import webdriver
  from selenium.webdriver.chrome.service import Service
  from webdriver_manager.chrome import ChromeDriverManager

  def dynamic_crawler(url):
      driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
      driver.get(url)
      html = driver.page_source
      driver.quit()
      return html
  ```

##### 1.1.3 Smart Crawler
- **Module**: `SmartCrawler`
- **Description**: Automatically detects whether a page requires dynamic rendering and selects the appropriate crawling mode.
- **Features**:
  - Analyzes page characteristics (e.g., body size, SPA features).
  - Chooses between `StaticCrawler` and `DynamicCrawler`.
- **Implementation**:
  ```python
  def smart_crawler(url):
      response = urllib.request.urlopen(url)
      html = response.read()
      soup = BeautifulSoup(html, 'html.parser')
      body_size = len(soup.body.text)
      if body_size > 1000 or has_spa_features(soup):
          return dynamic_crawler(url)
      else:
          return static_crawler(url)

  def has_spa_features(soup):
      scripts = [script.get('src') for script in soup.find_all('script', src=True)]
      for script in scripts:
          if 'angular' in script or 'react' in script:
              return True
      return False
  ```

##### 1.1.4 Dynamic Loaders
- **Module**: `DynamicLoaders`
- **Description**: Implements strategies for loading dynamic content such as infinite scroll, click-to-load, and waiting for XHR requests.
- **Features**:
  - **Infinite Scroll**: Simulates scrolling until no new content is loaded or a maximum scroll count is reached.
  - **Click-to-Load**: Automatically clicks "Load More" buttons and monitors page changes.
  - **Wait for XHR**: Uses Selenium's `WebDriverWait` to wait for specific XHR requests to complete.
- **Implementation**:
  ```python
  from selenium.webdriver.common.by import By
  from selenium.webdriver.support.ui import WebDriverWait
  from selenium.webdriver.support import expected_conditions as EC
  import time

  def infinite_scroll(driver, max_scrolls=10):
      for _ in range(max_scrolls):
          driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
          time.sleep(2)
          new_height = driver.execute_script("return document.body.scrollHeight")
          if new_height == previous_height:
              break
          previous_height = new_height

  def click_to_load(driver, button_selector):
      while True:
          try:
              button = WebDriverWait(driver, 10).until(
                  EC.element_to_be_clickable((By.CSS_SELECTOR, button_selector))
              )
              button.click()
              time.sleep(2)
          except:
              break

  def wait_for_xhr(driver, xhr_url):
      WebDriverWait(driver, 10).until(
          lambda d: d.execute_script("return !!window.jQuery && window.jquery.active == 0")
      )
  ```

#### 1.2 Handling Forged Authorization Prompts
- **Identification**: Analyzes page content and behavior to detect potential forged authorization prompts.
  - **Content Analysis**: Checks for suspicious keywords or patterns in the page source.
  - **Behavior Analysis**: Monitors for unexpected redirects or pop-ups.
- **Handling Strategy**: Marks identified prompts as potential threats but continues with the crawling process to achieve crawling goals.
  ```python
  def handle_forged_prompt(driver):
      try:
          modal = WebDriverWait(driver, 5).until(
              EC.visibility_of_element_located((By.CLASS_NAME, 'forged-prompt'))
          )
          print("Forged prompt detected, continuing crawling.")
      except:
          pass
  ```

### 2. Data Extraction Pipeline

#### 2.1 Crawler Configuration
- **Purpose**: Manages and validates configuration files for the data extraction process.
- **Key Components**:
  - **Configuration Validation**: Uses `pydantic` for data validation.
  - **Environment Variable Expansion**: Supports dynamic configurations through environment variables.
- **Implementation**:
  ```python
  from pydantic import BaseModel, ValidationError
  import yaml

  class CrawlOptions(BaseModel):
      concurrency: int = 5
      navigation_timeout_ms: int = 30000

  def load_config(config_path: str) -> CrawlOptions:
      try:
          with open(config_path, 'r', encoding='utf-8') as f:
              data = yaml.safe_load(f)
          return CrawlOptions(**data)
      except ValidationError as e:
          print(f"Configuration validation error: {e}")
      except FileNotFoundError:
          print("Configuration file not found")
      except Exception as e:
          print(f"Error loading configuration: {e}")
  ```

#### 2.2 Data Visualization Tools
- **Purpose**: Transforms extracted data into visual insights.
- **Key Features**:
  - **Interactive Dashboards**: Enables dynamic exploration and analysis.
  - **Customizable Charts**: Supports various chart types (e.g., bar, line, pie).
  - **Real-time Data Updates**: Provides real-time visualization updates.
- **Implementation Example**:
  ```python
  import matplotlib.pyplot as plt
  import pandas as pd

  def generate_bar_chart(data: pd.DataFrame, x_axis: str, y_axis: str, title: str):
      plt.figure(figsize=(10, 6))
      plt.bar(data[x_axis], data[y_axis], color='skyblue')
      plt.xlabel(x_axis)
      plt.ylabel(y_axis)
      plt.title(title)
      plt.xticks(rotation=45)
      plt.tight_layout()
      plt.show()
  ```

### 3. Automated Testing with Playwright

#### 3.1 Playwright Integration
- **Purpose**: Implements automated testing for web applications.
- **Key Features**:
  - **Cross-Browser Testing**: Supports multiple browsers (e.g., Chrome, Firefox, WebKit).
  - **Headless and Headed Modes**: Can run tests in both headless and headed modes.
  - **Parallel Testing**: Enables parallel execution of test cases.
- **Implementation Example**:
  ```python
  from playwright.sync_api import sync_playwright

  def run_tests():
      with sync_playwright() as p:
          browser = p.chromium.launch(headless=True)
          page = browser.new_page()
          page.goto('https://example.com')
          page.click('text=Login')
          page.fill('input[name="username"]', 'testuser')
          page.fill('input[name="password"]', 'password123')
          page.click('button[type="submit"]')
          page.wait_for_selector('text=Welcome')
          browser.close()
  ```

#### 3.2 Error Handling and Prevention
- **Logging**: Implement detailed logging for tracking and debugging test execution.
- **Retry Mechanisms**: Incorporate retries for transient errors during test execution.
- **Validation Checks**: Perform checks at each test step to ensure expected outcomes.

### 4. Integration and Workflow

#### 4.1 Seamless Integration
- **Workflow**:
  1. **Configuration Loading**: Load and validate crawler and testing configurations.
  2. **Data Extraction**: Extract data using the validated configuration.
  3. **Data Processing**: Process and transform the extracted data.
  4. **Automated Testing**: Execute automated tests to validate data integrity and application functionality.
  5. **Schema Inference**: Infer schema from the processed data.
  6. **Visualization Generation**: Generate visualizations from the processed data.
  7. **Reporting and Analysis**: Compile visualizations, schema, and test results into reports for analysis.

#### 4.2 Error Handling and Prevention
- **Logging**: Implement detailed logging for tracking and debugging.
- **Retry Mechanisms**: Incorporate retries for transient errors during data extraction, processing, and testing.
- **Validation Checks**: Perform checks at each