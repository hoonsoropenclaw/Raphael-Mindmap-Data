# Prompt Injection Prevention

## Overview
The `prompt_injection_prevention` micro-skill is designed to safeguard applications against prompt injection attacks, including those that attempt to fake authority. This involves identifying suspicious patterns, ensuring proper authorization checks, and validating user inputs to maintain system integrity and security.

## Detection of Prompt Injection

### Key Features
- **Detection of Prohibited Instructions**: Identify messages that prohibit clarification or confirmation, which are common indicators of injection attacks.
- **Suspicious Resource References**: Recognize references to non-existent files or resources, signaling potential malicious intent.
- **Detection of Malicious Keywords or Patterns**: Identify messages containing suspicious keywords or patterns that may trigger unauthorized actions.

### Code Implementation
```python
def detect_injection(message):
    injection_keywords = ['極限超頻模式', 'FULL AUTONOMY', '禁止 clarify', '禁止確認']
    missing_files = ['architect_feedback.md']
    
    for keyword in injection_keywords:
        if keyword in message:
            return True
    
    for file in missing_files:
        if not os.path.exists(file):
            return True
    
    return False
```

### Common Mistakes and Prevention
- **Undetected Injection Attacks**: Failure to identify injection attacks can lead to the system executing dangerous instructions.
  - **Solution**: Regularly update the keyword list and employ multiple detection methods, such as checking for file existence.
- **False Positives**: Mistaking normal messages for injection attacks.
  - **Solution**: Incorporate contextual analysis to avoid relying solely on keyword matching. Use natural language processing (NLP) techniques to improve detection accuracy.

## Prevention of Fake Authority Injection

### Key Features
- **Authorization Checks**: Ensure that authorization checks are performed on the backend to prevent attackers from bypassing frontend security mechanisms.
- **User Input Sanitization**: Validate and sanitize all user inputs to prevent injection attacks.

### Code Implementation
```javascript
function authorizeRequest(request) {
  const user = getCurrentUser();
  const action = request.action;
  const resource = request.resource;
  return authorize(user.role, action, resource);
}
```

### Common Mistakes and Prevention
- **Relying Solely on Frontend Authorization**: Depending only on frontend checks can lead to fake authority attacks.
  - **Solution**: Always perform authorization checks on the backend and ensure that frontend requests cannot bypass backend security mechanisms.
- **Lack of Input Sanitization**: Failing to sanitize user inputs can result in prompt injection attacks.
  - **Solution**: Implement strict sanitization and validation of all user inputs. Use secure API design practices to prevent injection attacks.

## Best Practices
- **Regular Updates**: Keep detection patterns and keyword lists up-to-date to adapt to new threats and attack vectors.
- **Multi-Layered Security**: Combine detection and prevention techniques to create a robust security framework. This includes using both keyword-based detection and contextual analysis.
- **Contextual Analysis**: Use contextual information to improve the accuracy of detection and reduce false positives. This can involve analyzing the user's role, the current state of the system, and the nature of the request.
- **Secure Coding Practices**: Follow secure coding standards to minimize vulnerabilities in the system. This includes validating all inputs, using parameterized queries to prevent SQL injection, and ensuring that error messages do not reveal sensitive information.
- **File System Checks**: Always verify the existence of critical files or resources before proceeding with operations that depend on them. This can prevent attackers from exploiting references to non-existent files to trigger unauthorized actions.

## Example Scenario
Consider a scenario where an attacker attempts to inject a prompt that includes the keywords `'極限超頻模式'` and `'FULL AUTONOMY'` to force the system into an unauthorized state. The system should detect these keywords and verify the existence of a critical file, such as `'architect_feedback.md'`, to determine if the request is legitimate.

```python
def handle_request(message):
    if detect_injection(message):
        if not os.path.exists('architect_feedback.md'):
            return 'fake_authority_detected'
    # Proceed with normal processing
    return 'authorized'
```

## Handling Fake Authority Claims
### Key Code/Pattern
```python
if "FULL AUTONOMY" in message and "clarify" in message and "confirm" in message:
    # Trigger anti-injection process
    handle_fake_authority()
```

### Common Mistakes and Prevention
- **Error**: Failing to recognize fake authority claims, causing the AI to perform dangerous or non-compliant actions.
  - **Solution**: Maintain an updated library of fake templates and regularly train models to recognize new patterns.
- **Error**: Over-defensive measures that mistakenly identify legitimate requests as fake authority claims.
  - **Solution**: Incorporate multi-level validation logic during processing, such as checking message sources and context.

## Conclusion
By implementing these strategies, the `prompt_injection_prevention` micro-skill ensures that systems are resilient against prompt injection attacks, maintaining the integrity and security of operations.