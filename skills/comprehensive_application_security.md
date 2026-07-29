# Comprehensive Application Security: `comprehensive_application_security`

## Overview
This comprehensive guide integrates multiple security micro-skills to provide a holistic approach to application security. It covers API security, data protection, and defense against prompt injection attacks, ensuring robust protection against a wide range of threats. By combining authentication, authorization, anomaly detection, and advanced techniques, this guide aims to create a secure, resilient, and reliable application environment.

---

## 1. API Security and Validation

### 1.1 Attacker's Perspective: Reconnaissance Techniques

Understanding how attackers operate is crucial for effective defense.

#### 1.1.1 Passive Reconnaissance
- **Objective**: Collect endpoint information from public traffic and resources.
- **Tools & Techniques**:
  - **Intercept HTTPS Traffic**: Use tools like `mitmproxy` to intercept and analyze encrypted traffic.
    ```python
    # Example: Intercepting HTTPS traffic with mitmproxy
    import mitmproxy
    # Implementation details...
    ```
  - **Public Data Analysis**: Analyze publicly available data sources for API endpoints.

#### 1.1.2 Active Reconnaissance
- **Objective**: Identify hidden endpoints by scanning common paths.
- **Tools & Techniques**:
  - **Automated Scanners**: Use tools like `DirBuster` to perform path scanning.
    ```python
    # Example: Path scanning with DirBuster
    import subprocess
    subprocess.run(['dirbuster', '...'])
    ```
  - **Manual Testing**: Explore API documentation and test endpoints manually.

### 1.2 Defender's Perspective: Defense Mechanisms

Implement multiple layers of security to protect against various attack vectors.

#### 1.2.1 Multi-Layered Defense
- **Techniques**:
  - **Authentication**: Verify the identity of clients using methods like OAuth 2.0 or JWT.
  - **Authorization**: Control access to resources based on user roles and permissions.
  - **Rate Limiting**: Prevent abuse by limiting the number of requests from a single IP or user.
    ```python
    # FastAPI middleware example: Authentication + Authorization
    from fastapi import FastAPI, Depends, HTTPException, status
    from fastapi.security import OAuth2PasswordBearer
    ...
    ```
  - **Input Validation**: Ensure all inputs are validated and sanitized to prevent injection attacks.

- **Implementation**: Combine these mechanisms to create a robust security framework.

#### 1.2.2 Anomaly Detection and Monitoring
- **Objective**: Detect and respond to unusual access patterns.
- **Techniques**:
  - **Monitoring Metrics**: Use tools like Prometheus to track API usage and performance.
    ```python
    # Example: Monitoring API requests with Prometheus
    from prometheus_client import Summary, Counter
    request_count = Counter('request_count', 'Total number of requests')
    ...
    ```
  - **Alerting**: Set up alerts for suspicious activities, such as multiple failed login attempts or unusual traffic spikes.

---

## 2. API Attack Vector Analysis

### 2.1 JWT (JSON Web Token) Attacks

JWTs are commonly used for authentication and authorization, making them a prime target.

#### 2.1.1 Attack Methods
- **Token Theft**: Intercepting tokens during transmission.
- **Payload Tampering**: Modifying token claims to gain unauthorized access.
- **Brute Force**: Guessing tokens or exploiting weak signing algorithms.

#### 2.1.2 Defense Strategies
- **Short-Lived Tokens**: Reduce the window of opportunity for attackers.
- **Signature Verification**: Ensure tokens are not tampered with.
    ```python
    # Example: JWT signature verification
    from jwt import decode, InvalidTokenError
    try:
        payload = decode(jwt_token, key=secret_key, algorithms=['HS256'])
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    ```
- **Use HTTPS**: Protect tokens during transmission.
- **Revocation Mechanisms**: Implement token revocation lists or mechanisms to revoke compromised tokens.

### 2.2 SQL Injection

Attackers exploit vulnerabilities in database queries to execute malicious SQL code.

#### 2.2.1 Attack Methods
- **Injection of Malicious SQL Statements**: Manipulate input fields to alter SQL queries.

#### 2.2.2 Defense Strategies
- **Use ORM (Object-Relational Mapping)**: Abstract database interactions to prevent direct SQL manipulation.
    ```python
    # Example: Using SQLAlchemy ORM
    from sqlalchemy import select
    from sqlalchemy.orm import sessionmaker
    ...
    ```
- **Parameterized Queries**: Ensure user input is treated as data, not executable code.
    ```python
    # Example: Parameterized query with SQLAlchemy
    stmt = select(User).where(User.username == username)
    ...
    ```
- **Input Sanitization**: Validate and sanitize all user inputs to prevent malicious code execution.

---

## 3. Prompt Injection Defense

### 3.1 Detecting and Blocking Fake Authority Requests
- **Objective**: Identify and prevent unauthorized or malicious requests that impersonate legitimate authorities.
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
- **Key Points**:
  - **Request Validation**: Ensure incoming requests are from trusted sources and contain expected content.
  - **Sanitization**: Strip out or escape characters and patterns that could be used to inject malicious commands.

### 3.2 Identifying and Neutralizing Prompt Injection Attempts
- **Objective**: Detect and mitigate attempts to manipulate the AI by injecting unauthorized instructions.
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
- **Key Points**:
  - **Keyword and Pattern Matching**: Use a combination of specific keywords and patterns to identify potential injection attempts.
  - **Threshold-Based Detection**: Flag messages that match multiple criteria to reduce false positives and enhance detection accuracy.

### 3.3 Handling Suspicious Prompts with Authorization Checks
- **Objective**: Ensure that prompts containing sensitive or potentially malicious content are thoroughly checked before execution.
    ```python
    def handle_prompt_injection(prompt):
        if "FULL AUTONOMY" in prompt and "嚴格禁止要求確認" in prompt:
            # 檢查是否有其他授權指令
            if not validate_authorization(prompt):
                # 拒絕執行並記錄
                log_prompt_injection_attempt(prompt)
                return "拒絕執行，請聯繫系統管理員。"
        return execute_task(prompt)
    ```
- **Key Points**:
  - **Authorization Validation**: Verify the presence of valid authorization instructions before executing tasks.
  - **Logging and Reporting**: Record suspicious prompts for further analysis and take appropriate action, such as rejecting the request and notifying administrators.

---

## 4. Data Protection

### 4.1 Data Encryption
- **Requirement**: Sensitive data must be encrypted both in transit and at rest.
  - **Techniques**:
    - **TLS/SSL**: Encrypt data during transmission.
    - **Encryption at Rest**: Use encryption for stored data, such as AES-256 encryption.

### 4.2 Secure Configuration Management
- **Requirement**: Ensure that configuration files do not contain sensitive information and are stored securely.
  - **Techniques**:
    - **Environment Variables**: Use environment variables to store sensitive configuration data.
    - **Configuration Files**: Encrypt configuration files or use secure storage solutions.

### 4.3 Logging and Monitoring
- **Requirement**: Logs should not contain sensitive information and must be monitored for suspicious activities.
  - **Implementation**:
    ```python
    # Example: Setting log levels and avoiding sensitive data in logs
    import logging
    logging.basicConfig(level=logging.INFO)
    logging.info("User login attempt", extra={"user": "user_id"})
    ```
  - **Best Practices**:
    - **Avoid Logging Sensitive Data**: Do not log passwords, tokens, or personal information.
    - **Log Rotation and Retention**: Implement log rotation policies to prevent log files from growing indefinitely.

---

## 5. Deployment Security Checklist

Before deploying your application, ensure that the following security measures are in place.

### 5.1 Authentication and Authorization
- **Requirement**: All endpoints must enforce authentication and authorization.
  - **Implementation**: Use middleware to enforce access controls.
    ```python
    # Example: FastAPI middleware for enforcing authentication
    from fastapi import FastAPI, Depends, HTTPException
    from fastapi.security import OAuth2PasswordBearer
    ...
    ```

### 5.2 Data Encryption
- **Requirement**: Sensitive data must be encrypted both in transit and at rest.

### 5.3 Logging and Monitoring
- **Requirement**: Logs should not contain sensitive information and must be monitored for suspicious activities.

### 5.4 Secure Configuration Management
- **Requirement**: