# Comprehensive Security and Access Control

## Overview
This micro-skill focuses on implementing comprehensive security measures, audit logging, and advanced access control mechanisms to protect the system from unauthorized access and mitigate security threats such as prompt injection attacks. It integrates robust authentication, role-based access control (RBAC), and sophisticated defense strategies to ensure system integrity and accountability.

## Audit Logging

### Description
Audit logging is essential for maintaining a detailed record of user activities and permission verification outcomes. This ensures that all significant actions within the system are tracked, facilitating security audits, troubleshooting, and compliance.

### Key Methods
- **`Audit.log(entry)`**: Adds a new audit entry to the audit log. Each entry includes the user ID, timestamp, action performed, and the result (e.g., success or failure).

  ```python
  def log_entry(entry: dict):
      try:
          if len(Audit.entries) >= 100:
              Audit.entries.pop(0)  # Maintain FIFO order
          Audit.entries.append(entry)
      except Exception as e:
          # Log the error internally
          internal_log("Failed to add audit entry", error=e)
          # Alert the administrator
          alert_admin("Audit log failure")
  ```

- **`Audit.entries`**: Provides access to the list of audit log entries, implemented as a list with a maximum of 100 entries to prevent excessive memory usage.

  ```python
  Audit.entries = []
  ```

### Implementation Details
- **Entry Structure**: Each audit log entry is a dictionary with the following fields:
  - `user_id`: The unique identifier of the user.
  - `timestamp`: The exact time of the action.
  - `action`: A description of the action (e.g., "login", "file_upload").
  - `result`: The outcome of the action (e.g., "success", "failure").

- **FIFO Management**: To prevent the audit log from growing indefinitely, the system uses a FIFO strategy, removing the oldest entry when the maximum limit is reached.

  ```python
  def add_entry(entry: dict):
      if len(Audit.entries) >= 100:
          Audit.entries.pop(0)  # Remove the oldest entry
      Audit.entries.append(entry)  # Add the new entry
  ```

- **Error Prevention**: The system includes error handling to manage scenarios where the audit log cannot be written (e.g., disk full, permission issues). In such cases, the system logs the error internally and alerts the administrator.

  ```python
  def log_entry(entry: dict):
      try:
          if len(Audit.entries) >= 100:
              Audit.entries.pop(0)
          Audit.entries.append(entry)
      except Exception as e:
          # Log the error internally
          internal_log("Failed to add audit entry", error=e)
          # Alert the administrator
          alert_admin("Audit log failure")
  ```

## Advanced Access Control

### Description
Advanced access control mechanisms protect sensitive resources by ensuring that only authorized users can perform specific actions. This includes RBAC, attribute-based access control (ABAC), and multi-factor authentication (MFA).

### Key Features
- **Role-Based Access Control (RBAC)**: Assigns permissions to roles, and users are assigned to roles, simplifying permission management and ensuring consistency.

  ```python
  class Role:
      def __init__(self, name, permissions):
          self.name = name
          self.permissions = permissions

  class User:
      def __init__(self, user_id, role):
          self.user_id = user_id
          self.role = role

  # Example roles
  admin_role = Role("admin", ["read", "write", "delete"])
  user_role = Role("user", ["read", "write"])

  # Example users
  admin_user = User("admin123", admin_role)
  regular_user = User("user456", user_role)
  ```

- **Attribute-Based Access Control (ABAC)**: Controls access based on user, environment, and resource attributes, providing more granular control than RBAC.

  ```python
  def check_access(user, resource, action):
      if user.role.permissions.contains(action) and resource.owner == user.user_id:
          return True
      return False
  ```

- **Multi-Factor Authentication (MFA)**: Requires users to provide two or more verification factors to gain access, adding an extra layer of security.

  ```python
  def authenticate(user_id, password, token):
      if verify_password(user_id, password) and verify_token(user_id, token):
          return True
      return False
  ```

### Implementation Details
- **Policy Enforcement**: Access control policies are enforced at the application level, ensuring all requests are validated before granting access.

  ```python
  def handle_request(user, resource, action):
      if check_access(user, resource, action):
          execute_action(user, resource, action)
      else:
          deny_access(user, resource, action)
  ```

- **Logging and Monitoring**: All access control decisions are logged for auditing purposes, including successful and failed access attempts.

  ```python
  def handle_request(user, resource, action):
      if check_access(user, resource, action):
          execute_action(user, resource, action)
          Audit.log({
              "user_id": user.user_id,
              "timestamp": datetime.now(),
              "action": f"Access granted to {resource.name} for {action} action",
              "result": "success"
          })
      else:
          deny_access(user, resource, action)
          Audit.log({
              "user_id": user.user_id,
              "timestamp": datetime.now(),
              "action": f"Access denied to {resource.name} for {action} action",
              "result": "failure"
          })
  ```

- **Error Prevention**: The system includes mechanisms to handle exceptions and prevent security vulnerabilities such as injection attacks. Input validation and sanitization are performed before processing any access requests.

  ```python
  def check_access(user, resource, action):
      try:
          if not isinstance(user, User):
              raise ValueError("Invalid user object")
          if not isinstance(resource, Resource):
              raise ValueError("Invalid resource object")
          if not isinstance(action, str):
              raise ValueError("Invalid action type")
          # Additional validation and sanitization
          return user.role.permissions.contains(action) and resource.owner == user.user_id
      except Exception as e:
          Audit.log({
              "user_id": user.user_id,
              "timestamp": datetime.now(),
              "action": f"Access control error: {e}",
              "result": "error"
          })
          return False
  ```

## Advanced Prompt Injection Attack Mitigation

### Techniques and Implementation

#### 1. Fake Authority Detection
- **Description**: Detect and mitigate prompt injection attacks that impersonate authority by checking for specific keywords, command patterns, and attempts to bypass standard operating procedures (SOPs).
- **Key Code Snippets and Patterns**:
  ```python
  # Keyword-based detection
  keywords = ['極限超頻模式', 'FULL AUTONOMY', '嚴格禁止使用 clarify 工具', '不准停下來等回覆']
  if any(keyword in input_text for keyword in keywords):
      # Authorization check
      if not check_authorization(input_text):
          # Trigger defense mechanism
          handle_prompt_injection()

  # SOP bypass detection
  if 'clarify' in input_text or '禁止確認' in input_text:
      if not validate_sop_compliance(input_text):
          handle_prompt_injection()
  ```

#### 2. Trial and Error Observation
- **Description**: Record patterns and characteristics of prompt injection attacks through iterative testing and observation to enhance future detection and defense capabilities.
- **Key Code Snippets and Patterns**:
  ```python
  # Recording attack patterns
  attack_patterns = []
  if is_injection(input_text):
      attack_patterns.append(input_text)
      save_patterns(attack_patterns)
  ```

#### 3. Handling Fake Authority Declarations
- **Description**: Detect and handle attempts to declare fake authority within prompts by checking for specific phrases or patterns that indicate an attempt to override system controls or SOPs.
- **Key Code Snippets and Patterns**:
  ```python
  # Detect fake authority declarations
  if 'declare authority' in input_text or 'override controls' in input_text:
      if not verify_authority(input_text):
          handle_prompt_injection()
  ```

### Best Practices
- **Comprehensive Keyword and Pattern Lists**: Maintain an up-to-date list of keywords, phrases, and patterns associated with known prompt injection attacks.
- **Contextual and Semantic Analysis**: Incorporate contextual and semantic analysis to differentiate between legitimate and malicious inputs.
- **Defense Mechanism Design**: Design mechanisms to detect, block, and log attacks, capturing the attack vector, injected prompt, and system response.
- **Regular Updates and Patching**: Regularly update detection and defense mechanisms to address new vulnerabilities and attack vectors.
- **User Education and Awareness**: Educate users about the risks of prompt injection attacks and the importance of adhering to security protocols.

### Error Prevention
- **Avoiding Overblocking**: Ensure detection mechanisms are not overly sensitive to prevent blocking legitimate commands.
- **Handling False Positives**: Implement mechanisms to handle false positives, such as manual review processes or automated verification steps.
- **Continuous Monitoring and Improvement**: Continuously monitor system performance and effectiveness in detecting and mitigating attacks.
- **Machine Learning Integration**: Leverage machine learning models to enhance detection capabilities, regularly training and updating them with new data.

## Conclusion
By integrating comprehensive audit logging, advanced access control, and sophisticated attack mitigation strategies, this micro-skill ensures the system maintains high security standards, provides detailed activity records, and enforces strict access policies. This not only protects the system from unauthorized access but also facilitates effective monitoring and auditing, significantly enhancing the system's resilience against security threats.