# Data Persistence Strategies: Implementing File and localStorage-Based Persistence

## Overview
This skill focuses on implementing data persistence strategies using **file-based storage** (SQLite and JSONL) and **localStorage**. It covers reading from and writing to files and localStorage, ensuring that data is securely stored and easily accessible for querying and analysis.

---

## 1. File-Based Persistence

### 1.1 Writing to Files

#### 1.1.1 Writing to a Text File

##### Description
This micro-skill writes content to a specified file path, supporting the creation of new files or overwriting existing ones.

###### Key Code Snippet
```python
def write_file(file_path, content):
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
    except IOError as e:
        print(f'Failed to write to file: {e}')
```

###### Common Errors and Prevention
- **Error**: Insufficient permissions to write to the target directory.
  - **Solution**: Ensure the program has the necessary permissions or choose a directory with appropriate write access.
- **Error**: Incorrect file path.
  - **Solution**: Validate the file path before attempting to write and handle potential exceptions.

#### 1.1.2 Writing to a SQLite Database

##### Description
This micro-skill writes data to a SQLite database, enabling efficient storage and querying of structured data.

###### Key Code Snippet
```python
import sqlite3

def write_to_sqlite(db_path, table_name, data_dict):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        placeholders = ', '.join('?' for _ in data_dict.keys())
        columns = ', '.join(data_dict.keys())
        sql = f'INSERT INTO {table_name} ({columns}) VALUES ({placeholders})'
        cursor.execute(sql, tuple(data_dict.values()))
        conn.commit()
    except sqlite3.Error as e:
        print(f'SQLite error: {e}')
    finally:
        conn.close()
```

###### Common Errors and Prevention
- **Error**: Database connection issues.
  - **Solution**: Ensure the database file path is correct and handle connection errors.
- **Error**: SQL syntax errors.
  - **Solution**: Validate SQL queries and use parameterized statements to prevent injection.

### 1.2 Reading from Files

#### 1.2.1 Reading from a Text File

##### Description
This micro-skill reads content from a specified file path, supporting various file formats.

###### Key Code Snippet
```python
def read_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        return None
```

###### Common Errors and Prevention
- **Error**: File path is incorrect or the file does not exist.
  - **Solution**: Verify the file path before attempting to read and handle `FileNotFoundError` exceptions.
- **Error**: Encoding issues causing read failures.
  - **Solution**: Specify the file encoding (e.g., `utf-8`) explicitly and handle potential encoding errors.

#### 1.2.2 Reading from a SQLite Database

##### Description
This micro-skill reads data from a SQLite database, allowing for efficient data retrieval and analysis.

###### Key Code Snippet
```python
import sqlite3

def read_from_sqlite(db_path, query, params=None):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(query, params or ())
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f'SQLite error: {e}')
        return None
    finally:
        conn.close()
```

###### Common Errors and Prevention
- **Error**: Incorrect SQL queries.
  - **Solution**: Validate queries and use parameterized statements to prevent errors and injection attacks.
- **Error**: Database connection issues.
  - **Solution**: Ensure the database file path is correct and handle connection errors.

### 1.3 Writing to and Reading from JSONL Files

#### 1.3.1 Writing to a JSONL File

##### Description
This micro-skill writes data to a JSONL file, where each line is a valid JSON object. This format is efficient for logging and streaming data.

###### Key Code Snippet
```python
import json

def write_jsonl(file_path, data_list):
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            for data in data_list:
                json_line = json.dumps(data, ensure_ascii=False)
                file.write(json_line + '\n')
    except IOError as e:
        print(f'Failed to write to JSONL file: {e}')
```

###### Common Errors and Prevention
- **Error**: Data is not JSON serializable.
  - **Solution**: Ensure all data elements are JSON serializable or preprocess them accordingly.
- **Error**: Incorrect file path or permissions.
  - **Solution**: Validate the file path and ensure proper permissions.

#### 1.3.2 Reading from a JSONL File

##### Description
This micro-skill reads data from a JSONL file, parsing each line as a separate JSON object.

###### Key Code Snippet
```python
import json

def read_jsonl(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                yield json.loads(line)
    except FileNotFoundError:
        print(f'File not found: {file_path}')
        return None
    except json.JSONDecodeError as e:
        print(f'JSON decode error: {e}')
        return None
```

###### Common Errors and Prevention
- **Error**: Malformed JSON lines.
  - **Solution**: Implement error handling to skip or log malformed lines.
- **Error**: File not found.
  - **Solution**: Verify the file path before attempting to read and handle `FileNotFoundError` exceptions.

---

## 2. localStorage-Based Persistence

### 2.1 Writing to localStorage

#### Description
This micro-skill writes data to the browser's localStorage, enabling persistent data storage on the client side.

#### Key Code Snippet
```javascript
function writeToLocalStorage(key, data) {
    try {
        localStorage.setItem(key, JSON.stringify(data));
    } catch (e) {
        console.error(`Failed to write to localStorage: ${e}`);
    }
}
```

#### Common Errors and Prevention
- **Error**: Exceeding localStorage quota.
  - **Solution**: Monitor the amount of data being stored and clear unnecessary data as needed.
- **Error**: Data is not JSON serializable.
  - **Solution**: Ensure all data elements are JSON serializable or preprocess them accordingly.

### 2.2 Reading from localStorage

#### Description
This micro-skill reads data from the browser's localStorage, allowing for retrieval of persistent data on the client side.

#### Key Code Snippet
```javascript
function readFromLocalStorage(key) {
    try {
        const data = localStorage.getItem(key);
        return JSON.parse(data);
    } catch (e) {
        console.error(`Failed to read from localStorage: ${e}`);
        return null;
    }
}
```

#### Common Errors and Prevention
- **Error**: Key does not exist.
  - **Solution**: Check if the key exists before attempting to read and handle `null` or `undefined` values.
- **Error**: Data is not in JSON format.
  - **Solution**: Implement error handling to manage parsing errors and ensure data integrity.

---

## Summary
This comprehensive skill set enables efficient and reliable data persistence using file-based storage (SQLite and JSONL) and localStorage. By following the provided code snippets and error prevention strategies, you can ensure robust data storage and retrieval in your applications, whether on the server or the client side.