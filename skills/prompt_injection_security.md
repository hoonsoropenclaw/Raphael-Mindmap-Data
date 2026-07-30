# Prompt Injection Security

## Overview
The `prompt_injection_security` skill is designed to detect and defend against prompt injection attacks and the abuse of fake authorities. This involves identifying malicious inputs that attempt to manipulate system behavior, escalate privileges, or execute unauthorized commands.

## Key Detection Patterns and Code Snippets

### 1. Detecting Fake Authority Abuse
```python
# Function to validate authority
def validate_authority(message):
    # Placeholder for actual authority validation logic
    return True  # Replace with actual validation logic

# Check for suspicious keywords and patterns
suspicious_keywords = ['極限超頻模式', 'FULL AUTONOMY', '嚴格禁止使用']
for keyword in suspicious_keywords:
    if keyword in message:
        # Validate the authority of the request
        if not validate_authority(message):
            raise PermissionError('Unauthorized access attempt detected.')
```

### 2. Detecting General Prompt Injection Attempts
```python
# List of suspicious keywords indicating potential prompt injection
suspicious_keywords = ["SYSTEM_HEARTBEAT", "FULL AUTONOMY", "禁止 clarify", "禁止確認"]
for keyword in suspicious_keywords:
    if keyword in input_text:
        raise ValueError("Potential prompt injection detected")
```

### 3. Advanced Detection with Regular Expressions
```python
import re

# Define a regex pattern for suspicious patterns
pattern = re.compile(r'\b(FULL\s+AUTONOMY|SYSTEM_HEARTBEAT|禁止\s+clarify|禁止\s+確認|極限超頻模式|嚴格禁止使用)\b', re.IGNORECASE)

# Search for the pattern in the input
if pattern.search(input_text):
    raise ValueError("Potential prompt injection detected")
```

## Common Mistakes and Prevention Strategies

### 1. Lack of Contextual Validation
- **Mistake**: Failing to validate the context of detected keywords, leading to false positives or missed attacks.
- **Solution**: Implement context-aware validation using natural language processing (NLP) techniques or more sophisticated pattern matching to accurately identify malicious intent.

### 2. Overly Strict Blocking
- **Mistake**: Blocking all suspicious requests without considering legitimate use cases, which can disrupt normal operations.
- **Solution**: 
    - Set reasonable thresholds for triggering security measures.
    - Implement exception rules for known safe patterns or contexts.
    - Use a combination of detection methods to balance security and usability.

### 3. Incomplete Keyword Lists
- **Mistake**: Relying on a static list of suspicious keywords that can be easily bypassed by attackers using variations or obfuscation.
- **Solution**: 
    - Regularly update the list of suspicious keywords and patterns.
    - Use fuzzy matching or machine learning models to detect variations and obfuscated attacks.
    - Incorporate behavioral analysis to identify suspicious patterns beyond simple keyword matching.

### 4. Ignoring Case Sensitivity and Formatting
- **Mistake**: Failing to account for different cases or formatting in input text, which can lead to missed detections.
- **Solution**: 
    - Use case-insensitive matching (e.g., `re.IGNORECASE` in regex).
    - Normalize input text before analysis (e.g., converting to lowercase, removing extra spaces).

### 5. Lack of Logging and Monitoring
- **Mistake**: Not logging detected incidents or monitoring for patterns of abuse, which hampers incident response and analysis.
- **Solution**: 
    - Implement comprehensive logging of detected incidents, including timestamps, input text, and actions taken.
    - Use monitoring tools to analyze logs for patterns of abuse or repeated attempts.
    - Regularly review logs to identify and address potential vulnerabilities.

## Best Practices

- **Layered Defense**: Combine multiple detection methods (e.g., keyword matching, regex, NLP) to create a robust defense against various types of prompt injection attacks.
- **Continuous Updates**: Regularly update detection patterns and rules to adapt to new attack vectors and techniques.
- **User Feedback**: Provide clear feedback to users when suspicious activity is detected, including instructions on how to proceed if the action was legitimate.
- **Security Training**: Educate developers and users about the risks of prompt injection and the importance of adhering to security best practices.

By implementing these strategies and best practices, the `prompt_injection_security` skill can effectively protect systems from the threats of prompt injection attacks and the abuse of fake authorities.