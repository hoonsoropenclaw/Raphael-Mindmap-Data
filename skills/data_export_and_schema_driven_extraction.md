# Data Export and Schema-Driven Extraction

## Overview

This micro-skill focuses on exporting data to JSON format for indexing and implementing schema-driven data extraction methods to handle data flexibly and efficiently. By combining these two techniques, the system ensures versatile data management and seamless integration with frontend interfaces.

## JSON Index Export

### Description

Exporting data from an SQLite database to JSON format facilitates data visualization and search functionalities in frontend Web UIs.

### Key Code Snippet

```python
import json
import sqlite3

def export_index_to_json(db_path: str, json_path: str):
    """
    Exports SQLite database index data to a JSON file.

    :param db_path: Path to the SQLite database.
    :param json_path: Path where the JSON file will be saved.
    """
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.execute("SELECT path, label, kind, score, ocr_used FROM docs ORDER BY indexed_at DESC")
            docs = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
            index_data = {"docs": docs, "stats": {}}
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, ensure_ascii=False, indent=2)
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
    except IOError as e:
        print(f"I/O error({e.errno}): {e.strerror}")
```

### Common Errors and Prevention

- **Error**: Database connection not properly closed, leading to data corruption.
  - **Solution**: Use the `with` statement to manage the database connection, ensuring it closes automatically after operations are completed.

## Schema-Driven Extraction

### Description

This technique leverages the `ExtractionSchema` to define data extraction rules, including selectors, attributes, mandatory fields, and multiple selections. The schema-driven approach allows the crawler to adapt to different website structures without altering the core codebase.

### Key Code Snippet

```python
from hybrid_scraper import ExtractionSchema

def demo_schema() -> ExtractionSchema:
    """
    Demonstrates the creation of an ExtractionSchema for data extraction.

    :return: An ExtractionSchema object configured for demo purposes.
    """
    return ExtractionSchema.from_dict({
        "name": "demo",
        "item_selector": ".product",
        "wait_selector": "#products[data-ready='true'] .product",
        "min_items": 3,
        "fields": {
            "id": {"selector": "", "attr": "data-id", "required": True},
            "name": {"selector": ".name", "required": True},
            "price": {"selector": ".price", "required": True},
            "url": {"selector": "a.detail", "attr": "href", "required": True},
            "tags": {"selector": ".tag", "many": True},
        },
    })
```

### Common Errors and Prevention

1. **Error**: Selector does not match target elements.
   - **Cause**: Incorrect selector syntax or changes in the target element structure.
   - **Solution**: Use browser developer tools to inspect the element structure and adjust the selector to ensure accurate matching.

2. **Error**: Missing required fields.
   - **Cause**: The target page lacks certain required fields.
   - **Solution**: Adjust field properties in the `ExtractionSchema` or handle missing cases in the code.

## Integration and Best Practices

### Combining JSON Export and Schema-Driven Extraction

To achieve seamless data handling and export:

1. **Define Extraction Schema**: Clearly define the extraction schema to match the data structure of the target data source.
2. **Extract Data**: Use the schema to extract data from the source.
3. **Export to JSON**: Once data is extracted, export it to JSON format using the JSON export function.
4. **Error Handling**: Implement robust error handling to manage issues such as connection failures, missing fields, and selector mismatches.

### Example Workflow

```python
def export_and_export(db_path: str, json_path: str):
    """
    Extracts data using a predefined schema and exports it to JSON.

    :param db_path: Path to the SQLite database.
    :param json_path: Path where the JSON file will be saved.
    """
    schema = demo_schema()
    extracted_data = schema.extract(db_path)
    
    try:
        with sqlite3.connect(db_path) as conn:
            # Assuming extracted_data is a list of dictionaries
            docs = extracted_data
            index_data = {"docs": docs, "stats": {}}
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"An error occurred: {e}")
```

### Tips for Robust Implementation

- **Validation**: Validate extracted data against the schema before exporting to ensure data integrity.
- **Logging**: Implement logging to track extraction and export processes, aiding in debugging and monitoring.
- **Scalability**: Design the system to handle large datasets by processing data in chunks and optimizing database queries.

By integrating JSON export and schema-driven extraction, this micro-skill provides a flexible and efficient framework for data handling and export, ensuring adaptability to various data sources and structures.