# CLI and Output Generation Tools

## Overview
This micro-skill focuses on building command-line interfaces (CLI) and generating HTML output for automation and reporting purposes using Python. It covers using the `argparse` module for CLI development and techniques for dynamically generating and saving HTML content.

## Building Command-Line Interfaces with argparse

### Description
Utilize Python's `argparse` module to parse command-line arguments, construct CLIs with subcommands, options, and help information.

### Key Code Snippet
```python
import argparse

parser = argparse.ArgumentParser(
    prog="smartcrawler",
    description="智慧網頁爬蟲 — BeautifulSoup + Selenium,自動選最佳策略",
)
parser.add_argument("--urls", required=True, help="逗號分隔的起始 URL")
parser.add_argument("--output", default="output.json", help="輸出檔路徑(預設 output.json)")
parser.add_argument(
    "--format",
    default="",
    choices=["", "json", "csv", "sqlite"],
    help="輸出格式(預設依副檔名判斷)",
)
# ... 其他參數
```

### Common Errors and Prevention
- **Parameter Conflicts**: Ensure that different options do not conflict and clearly explain each option's purpose in the help information.
  - **Prevention**: Thoroughly test the CLI with various combinations of options and provide clear documentation.
- **Type Conversion Errors**: Use `argparse`'s type checking features, such as `type=int`, to prevent users from entering invalid types.
  - **Prevention**: Always specify the expected type for each argument and handle exceptions gracefully.
- **Missing Required Parameters**: Use `required=True` to mark required parameters and provide clear error messages when they are missing.
  - **Prevention**: Always mark required parameters and provide informative error messages guiding the user to correct usage.

## Generating HTML Output

### Description
This skill involves dynamically generating HTML content and saving it to a specified file for reporting and automation tasks.

### Key Code Snippet or Pattern
```python
html_content = """<html>
<head><title>測試頁面</title></head>
<body>
<h1>Hello, World!</h1>
</body>
</html>"""
with open('web_output.html', 'w') as f:
    f.write(html_content)
```

### Common Errors and Prevention
- **File Writing Errors**: The file may not be writable due to permission issues.
  - **Solution**: Ensure that the user running the script has write permissions for the target directory or choose a directory with appropriate permissions.
  - **Prevention**: Implement error handling to catch and inform the user of permission issues.
- **HTML Content Formatting Errors**: The generated HTML may contain syntax errors or be improperly structured.
  - **Solution**: Use HTML validation tools to check the generated HTML code or employ template engines like Jinja2 to generate structured and error-free HTML.
  - **Prevention**: Validate HTML content before saving and consider using templates for more complex HTML generation.

## Best Practices

### For CLI Development
- **Modular Design**: Structure your CLI code in a modular way, separating argument parsing, logic, and output generation.
- **Comprehensive Help**: Provide detailed help messages and usage examples to guide users.
- **Input Validation**: Always validate and sanitize user inputs to prevent errors and security issues.

### For HTML Generation
- **Use Templates**: Leverage template engines to manage complex HTML structures and ensure consistency.
- **Maintain Readability**: Keep the generated HTML clean and readable to facilitate debugging and maintenance.
- **Automate Testing**: Implement automated tests to verify the correctness of the generated HTML output.

By following these guidelines and utilizing the provided code snippets, you can effectively build robust command-line tools and generate accurate HTML reports for your automation and reporting needs.