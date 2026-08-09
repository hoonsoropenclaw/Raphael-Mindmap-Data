# Full-Stack Data Management

## Overview
The **full_stack_data_management** micro-skill is designed to manage and test data across the entire application stack, encompassing database design, optimization, integration with backend and frontend systems, and comprehensive automated testing. This skill integrates advanced database management techniques with FastAPI, intelligent data crawling, secure data extraction, dynamic visualization, efficient file handling, and robust automated testing to ensure data integrity, accurate analysis, and reliable application performance.

## Key Components

### 1. Full-Stack Database Management with FastAPI

#### 1.1 Asynchronous Database Initialization
Efficiently initializing database connections is crucial for the smooth operation of asynchronous applications.

##### Example Implementation with `aiosqlite`
```python
import asyncio
import aiosqlite

async def init_db():
    try:
        db = await aiosqlite.connect('test.db')
        await db.execute('CREATE TABLE IF NOT EXISTS test (id INTEGER PRIMARY KEY, name TEXT)')
        await db.commit()
    except aiosqlite.Error as e:
        print(f"Database initialization error: {e}")
    finally:
        await db.close()

async def main():
    await init_db()
    # Proceed with other asynchronous operations

asyncio.run(main())
```

#### 1.2 Error Prevention and Handling
Effective error handling ensures that the application can gracefully handle issues related to database initialization and connection.

##### Common Errors and Solutions
- **Error**: Database connection is not properly initialized, leading to failed queries.
  - **Solution**: Always ensure that `init_db()` is called before performing any database operations. Incorporate try-except blocks to catch and handle initialization errors.
  
  ```python
  async def perform_query():
      try:
          await init_db()
          db = await aiosqlite.connect('test.db')
          cursor = await db.execute('SELECT * FROM test')
          results = await cursor.fetchall()
          await db.close()
          return results
      except aiosqlite.Error as e:
          print(f"Query failed: {e}")
  ```

- **Error**: In a testing environment, the database connection is not correctly set up, causing tests to fail.
  - **Solution**: In tests, manually call `init_db()` or use a test-specific database configuration. Utilize mocking frameworks to simulate database interactions without relying on a physical database.

  ```python
  from unittest.mock import AsyncMock, patch

  async def test_init_db():
      with patch('aiosqlite.connect') as mock_connect:
          mock_db = AsyncMock()
          mock_connect.return_value = mock_db
          await init_db()
          mock_connect.assert_called_with('test.db')
          mock_db.execute.assert_called_with('CREATE TABLE IF NOT EXISTS test (id INTEGER PRIMARY KEY, name TEXT)')
          mock_db.commit.assert_called_once()
          mock_db.close.assert_called_once()
  ```

#### 1.3 Performance Optimization
Efficient database connection management can significantly improve the performance of asynchronous applications.

##### Tips for Optimization
- **Connection Pooling**: Implement connection pooling to reuse existing connections instead of creating new ones for each operation. Libraries like `aiopg` for PostgreSQL offer built-in support for connection pooling.

  ```python
  import aiopg

  async def get_pool():
      pool = await aiopg.create_pool(user='user', password='password',
                                     dbname='test', host='127.0.0.1')
      return pool

  async def main():
      pool = await get_pool()
      async with pool.acquire() as conn:
          async with conn.cursor() as cur:
              await cur.execute('SELECT 1')
              await cur.fetchone()
      pool.close()
      await pool.wait_closed()
  ```

- **Lazy Initialization**: Delay the initialization of the database connection until it is actually needed. This can prevent unnecessary overhead during application startup.

  ```python
  import asyncio
  import aiosqlite

  db = None

  async def get_db():
      global db
      if db is None:
          db = await aiosqlite.connect('test.db')
          await db.execute('CREATE TABLE IF NOT EXISTS test (id INTEGER PRIMARY KEY, name TEXT)')
          await db.commit()
      return db

  async def main():
      db = await get_db()
      # Proceed with database operations
  ```

#### 1.4 Managing Database States for E2E Testing
Managing database states during E2E testing is crucial for ensuring test reliability and consistency.

##### 1.4.1 Resetting the Database Between Tests
To prevent data contamination between test cases, reset the database before each test runs.

###### Key Code Snippet (JavaScript Example)
```javascript
// Reset the database before each test case
beforeEach(async () => {
    DB.announcements = JSON.parse(JSON.stringify(DEMO_ANNOUNCEMENTS));
    DB.auditLog = [];
});
```

###### Common Errors and Prevention
- **Error**: Data contamination between tests leads to inaccurate test results.
- **Prevention**: Reset the database before each test case to ensure test independence.

##### 1.4.2 In-Memory Database Management
Using an in-memory database simulates real database behavior, enabling rapid execution and validation of code in testing environments.

###### Key Code Snippet (JavaScript Example)
```javascript
const inMemoryDB = {
    users: [...],
    announcements: [...],
    auditLog: []
};

// Read data
const user = inMemoryDB.users.find(x => x.username === 'principal');

// Write data
inMemoryDB.announcements.push(newAnnouncement);
```

###### Common Errors and Prevention
- **Error**: The in-memory database state is not correctly reset between tests, leading to inaccurate test results.
- **Prevention**: Reset the in-memory database state before each test case to maintain test integrity.

### 2. Data Management and Testing

#### 2.1 Intelligent Crawler System
The crawler system is designed to handle both static and dynamic web content, ensuring comprehensive data extraction.

##### 2.1.1 Crawler Architecture
- **Static Crawler**: Utilizes `BeautifulSoup` and `urllib` to parse and extract data from static web pages.
- **Dynamic Crawler**: Uses Selenium to handle dynamic content rendered by JavaScript.
- **Smart Crawler**: Automatically detects whether a page requires dynamic rendering and selects the appropriate crawling mode.
- **Dynamic Loaders**: Implements strategies for loading dynamic content such as infinite scroll, click-to-load, and waiting for XHR requests.

##### 2.1.2 Handling Forged Authorization Prompts
- **Identification**: Analyzes page content and behavior to detect potential forged authorization prompts.
- **Handling Strategy**: Marks identified prompts as potential threats but continues with the crawling process to achieve crawling goals.

#### 2.2 Data Extraction Pipeline
The data extraction pipeline manages configuration, visualization, and processing of extracted data.

##### 2.2.1 Crawler Configuration
- **Configuration Validation**: Uses `pydantic` for data validation.
- **Environment Variable Expansion**: Supports dynamic configurations through environment variables.

##### 2.2.2 Data Visualization Tools
Transforms extracted data into visual insights.

###### Key Features
- **Interactive Dashboards**: Enables dynamic exploration and analysis.
- **Customizable Charts**: Supports various chart types (e.g., bar, line, pie).
- **Real-time Data Updates**: Provides real-time visualization updates.

###### Implementation Example
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
The automated testing component ensures the reliability and functionality of web applications.

#### 3.1 Playwright Integration
Implements automated testing for web applications.

###### Key Features
- **Cross-Browser Testing**: Supports multiple browsers (e.g., Chrome, Firefox, WebKit).
- **Headless and Headed Modes**: Can run tests in both headless and headed modes.
- **Parallel Testing**: Enables parallel execution of test cases.

###### Implementation Example
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
The workflow integrates data extraction, processing, testing, and visualization into a cohesive process.

##### Workflow
1. **Configuration Loading**: Load and validate crawler and testing configurations.
2. **Data Extraction**: Extract data using the validated configuration.
3. **Data Processing**: Process and transform the extracted data.
4. **Automated Testing**: Execute automated tests to validate data integrity and application functionality.
5. **Schema Inference**: Infer schema from the processed data.
6. **Visualization Generation**: Generate visualizations from the processed data.
7. **Reporting and Analysis**: Compile visualizations, schema, and test results into reports for analysis.

#### 4.2 Error Handling and Prevention
- **