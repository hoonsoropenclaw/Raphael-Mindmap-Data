# Data Redaction

## Overview
The **data_redaction** skill is designed to automatically identify and mask sensitive information within text, such as Personally Identifiable Information (PII), salaries, email addresses, tokens, secrets, passwords, API keys, session IDs, and more. This skill is applicable across various scenarios, including documents, test reports, and other data outputs.

## Key Features and Implementation

### Automatic Redaction of Sensitive Data
Sensitive data is automatically detected and masked to prevent unintended exposure. This is particularly crucial in test reports where failure messages might inadvertently disclose sensitive information.

### Example: Masking Sensitive Data in Test Reports
```python
redacted_key = any(marker in path.lower() for marker in ("token", "secret", "password", "apikey", "api_key", "session_id"))
if redacted_key:
    errors.append(f"{path}: sensitive value mismatch (redacted)")
else:
    errors.append(f"{path}: expected {expected!r}, got {actual!r}")
```
- **Explanation**: This code snippet checks if the path contains any sensitive markers. If a marker is found, it appends a redacted error message; otherwise, it displays the expected and actual values.

### Redacting Errors in Reports
```python
def redact_errors(errors: list) -> list:
    redacted_errors = []
    for error in errors:
        redacted_error = redact_text(error)
        redacted_errors.append(redacted_error)
    return redacted_errors

def generate_report(test_results: list) -> None:
    for result in test_results:
        for step in result.steps:
            step.errors = redact_errors(step.errors)
    # Generate report
    ...
```
- **Explanation**: The `redact_errors` function processes a list of errors, redacting each one. The `generate_report` function ensures that all errors in the test results are redacted before the report is generated.

## Common Errors and Prevention

### 1. Sensitive Data Leakage in Reports
- **Error**: Sensitive data is exposed in the report.
- **Solution**: 
  - Ensure all sensitive markers are correctly identified and masked.
  - Use unit tests to verify the redaction functionality, such as `test_sensitive_json_mismatch_never_echoes_values`.

### 2. Over-Redaction of Non-Sensitive Data
- **Error**: Non-sensitive data is mistakenly masked.
- **Solution**: 
  - Carefully define the list of sensitive markers to avoid over-redaction.
  - Regularly review and update the sensitive markers list to reflect current requirements.

### 3. Redaction Impacting Report Readability
- **Error**: Redacted text affects the readability or structure of the report.
- **Solution**: 
  - Use a consistent redaction identifier (e.g., "REDACTED") to maintain readability.
  - Ensure that the redaction process does not disrupt the overall structure and flow of the report.

## Best Practices

- **Define Clear Redaction Rules**: Clearly define what constitutes sensitive information and establish rules for its identification and masking.
- **Regularly Update Sensitive Markers**: As new types of sensitive data emerge, update the list of sensitive markers to ensure comprehensive protection.
- **Implement Redaction in Multiple Layers**: Apply redaction at different stages of data processing to minimize the risk of accidental exposure.
- **Test Redaction Functionality**: Rigorously test the redaction functionality to ensure it works as intended and does not inadvertently mask non-sensitive data.
- **Maintain Log Integrity**: Ensure that redaction does not interfere with the integrity of logs and reports, preserving their usefulness for debugging and analysis.

By following these guidelines and implementing the provided code patterns, you can effectively safeguard sensitive information while maintaining the utility and readability of your reports and documents.