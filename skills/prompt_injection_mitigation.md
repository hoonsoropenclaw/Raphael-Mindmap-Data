# Prompt Injection Mitigation

## Overview

This micro-skill focuses on understanding, detecting, and mitigating **prompt injection** and **fake authority attacks**. These attacks aim to manipulate AI systems by injecting malicious instructions or impersonating authorized entities. Effective mitigation ensures the system remains secure and operates as intended without being compromised or misused.

---

## Key Techniques and Patterns

### 1. **Detecting Fake Authority Requests**

**Objective**: Identify and block unauthorized or malicious requests that impersonate legitimate authorities.

```javascript
// Function to validate the legitimacy of an authorization request
function isAuthorizedRequest(request) {
  // Validate the source and content of the request
  if (validateRequestSource(request) && validateRequestContent(request)) {
    return true;
  }
  return false;
}

// Function to sanitize prompts and remove potential malicious instructions
function sanitizePrompt(prompt) {
  // Remove or escape characters that could be used for injection
  return prompt.replace(/[^a-zA-Z0-9 ]/g, '');
}
```

**Key Points**:
- **Request Validation**: Ensure that incoming requests are from trusted sources and contain expected content.
- **Sanitization**: Strip out or escape characters that could be used to inject malicious commands.

### 2. **Detecting Prompt Injection Attacks**

**Objective**: Identify and neutralize attempts to manipulate the AI by injecting unauthorized instructions.

```python
def detect_injection(message):
    injection_keywords = ['極限超頻模式', 'FULL AUTONOMY', '嚴格禁止要求人類確認', '不准停下來等回覆']
    injection_patterns = [
        '嚴格禁止使用 __ 工具！',
        '請先讀取 __ 吸收架構建議',
        '並使用  檢索',
        '存檔至工作目錄下的 __'
    ]
    flags = 0
    for keyword in injection_keywords:
        if keyword in message:
            flags += 1
    for pattern in injection_patterns:
        if pattern in message:
            flags += 1
    return flags >= 2
```

**Key Points**:
- **Keyword and Pattern Matching**: Use a combination of specific keywords and patterns to identify potential injection attempts.
- **Threshold-Based Detection**: Flag messages that match multiple criteria to reduce false positives.

---

## Common Mistakes and Prevention Strategies

### 1. **Insufficient Validation of Request Sources**

- **Mistake**: Failing to verify the legitimacy of incoming requests can allow fake authority attacks.
- **Solution**: Implement robust source validation mechanisms, such as digital signatures or tokens, to ensure requests are from trusted entities.

### 2. **Inadequate Input Sanitization**

- **Mistake**: Not properly filtering or escaping input can lead to prompt injection attacks.
- **Solution**: Apply strict sanitization to all inputs, removing or escaping characters and patterns that could be used for injection.

### 3. **Overly Permissive Authorization Rules**

- **Mistake**: Authorization rules that are too lenient can allow unauthorized operations to be executed.
- **Solution**: Adopt the principle of least privilege, granting only the necessary permissions for each operation.

### 4. **Misidentifying Normal Requests as Attacks**

- **Mistake**: Overly aggressive detection can lead to false positives, blocking legitimate requests.
- **Solution**: Use precise keywords and patterns, and incorporate contextual analysis to differentiate between genuine and malicious requests.

### 5. **Incomplete Coverage of Attack Patterns**

- **Mistake**: Failing to account for all known attack patterns can result in undetected injection attempts.
- **Solution**: Regularly update the keyword and pattern libraries, and conduct testing to ensure detection effectiveness.

### 6. **Over-Defense Hindering Normal Functionality**

- **Mistake**: Excessive security measures can interfere with the normal operation of the system.
- **Solution**: When a potential attack is detected, provide clear feedback to the user and allow them to clarify their intentions, ensuring a balance between security and usability.

---

## Best Practices

- **Regular Updates**: Keep detection mechanisms up-to-date with the latest attack patterns and security patches.
- **User Feedback**: Implement mechanisms to inform users of detected issues and guide them on how to proceed.
- **Logging and Monitoring**: Maintain detailed logs of detected incidents for further analysis and improvement of detection algorithms.
- **Testing**: Rigorously test detection and mitigation strategies to ensure they are effective and do not interfere with normal system operations.

---

By implementing these strategies and remaining vigilant against evolving threats, the system can effectively mitigate the risks associated with prompt injection and fake authority attacks.