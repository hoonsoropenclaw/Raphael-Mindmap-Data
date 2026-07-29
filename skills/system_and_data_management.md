# System and Data Management

## Overview
The **system_and_data_management** micro-skill encompasses the management of middleware, system infrastructure, and data persistence. This includes handling middleware event processing, system monitoring, audit logging, and utilizing localStorage for application state management. The goal is to ensure robust system stability, efficient performance tracking, secure operations, and reliable data persistence.

---

## 1. Middleware Event and Redirect Handling

### 1.1 Middleware Redirect Handling

#### Description
Redirect handling within middleware is essential for maintaining application flow, especially in scenarios like authentication failures or access control issues. Proper management ensures users are directed to appropriate pages without encountering errors or unintended behavior.

#### Key Code Snippet (TypeScript)
```typescript
// Middleware Implementation
export function middleware(req: NextRequest) {
  const { pathname } = req.nextUrl;
  const policy = findPolicy(pathname);
  if (!policy) {
    return NextResponse.next();
  }
  const user = getCurrentUser();
  if (!user || !hasPermissions(user, policy.requires)) {
    return NextResponse.redirect(new URL('/403', req.url));
  }
  return NextResponse.next();
}
```

#### Common Errors and Prevention

1. **Incorrect Redirect Path**
   - **Issue**: Redirecting to an incorrect path, causing users to be unable to access the intended error page.
   - **Solution**: Ensure the redirect path is correct and configure the appropriate error handling pages within the application.

2. **Loss of User Information During Redirect**
   - **Issue**: Redirecting without preserving necessary user information, leading to a poor user experience.
   - **Solution**: Retain essential user information during redirection, such as through query parameters or session storage.

3. **Redirect Loop**
   - **Issue**: Creating a loop where the redirect target triggers another redirect, potentially crashing the application.
   - **Solution**: Review the redirect logic to prevent the redirect target from triggering additional redirects. Implement checks to break the loop if necessary.

#### Best Practices

- **Consistent Redirect Strategy**: Maintain a consistent strategy for handling redirects across different parts of the application to ensure predictability and reliability.
- **Logging and Monitoring**: Implement logging for redirect events to monitor and troubleshoot issues related to redirection.
- **Security Considerations**: Ensure that redirects do not expose sensitive information and are protected against open redirect vulnerabilities.

### 1.2 Python urllib Redirect Handling

#### Description
Properly handling redirects when using Python's `urllib` for HTTP requests is crucial for accurate response processing and avoiding unintended behavior.

#### Key Code Snippet
```python
import urllib.request

# Disable automatic redirects
class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None

opener = urllib.request.build_opener(NoRedirect)
response = opener.open('http://example.com')
print(response.status)
```

#### Common Errors and Prevention

1. **Automatic Redirection by Default**
   - **Issue**: `urllib` automatically follows redirects by default, which can lead to inaccurate testing results.
   - **Solution**: Use a custom redirect handler to control redirection behavior, such as disabling automatic redirects.

2. **Ignoring Important Redirect Information**
   - **Issue**: Overlooking critical information in redirect responses, such as the `Location` header.
   - **Solution**: When handling redirects, inspect and record the `Location` header for any necessary subsequent processing.

3. **Redirect Loop Handling**
   - **Issue**: Failing to manage redirect loops, which can cause the application to crash.
   - **Solution**: Set a maximum limit on the number of redirects and terminate the request when this limit is reached.

### 1.3 Signal-Based Event Handling

#### Description
Signal-based event handling involves using signals to manage events such as progress updates, completion notifications, and error messages. This approach is particularly useful in applications that require real-time updates and responsive user interfaces.

#### Key Code Snippets (GDScript)
```gdscript
signal scan_progress(value: float, phase: String)
signal scan_completed(text: String, confidence: float)
signal scan_failed(message: String)

func _ready() -> void:
    ocr.scan_progress.connect(_on_scan_progress)
    ocr.scan_completed.connect(_on_scan_completed)
    ocr.scan_failed.connect(_on_scan_failed)

func _on_scan_progress(value: float, phase: String) -> void:
    # Update UI progress bar
    progress_bar.value = value * 100
    status_label.text = phase

func _on_scan_completed(text: String, confidence: float) -> void:
    result_label.text = text
    status_label.text = "OCR COMPLETED"
```

#### Common Errors and Prevention

1. **Signal Connection Errors**
   - **Issue**: Signals are not connected correctly, leading to events not being triggered.
   - **Solution**: Verify signal names and connection methods, and use Godot's built-in signal inspection tools for validation.

2. **Improper Data Handling in Event Handlers**
   - **Issue**: Event handlers do not correctly process incoming data, causing UI updates to fail.
   - **Solution**: Check the data types received in event handlers and use debug mode for testing.

#### Best Practices

- **Consistent Event Strategy**: Maintain a consistent strategy for handling events across different parts of the application to ensure predictability and reliability.
- **Logging and Monitoring**: Implement logging for event triggers and redirects to monitor and troubleshoot issues related to event handling and redirection.
- **Security Considerations**: Ensure that event data and redirects do not expose sensitive information and are protected against potential vulnerabilities.

---

## 2. System Monitoring and Management

### 2.1 Comprehensive Logging and Audit System

#### 2.1.1 Detailed Logging
Implement detailed logging to capture system behavior, errors, and user actions. This aids in debugging, monitoring, and auditing.

##### Key Implementation Details
- **Log Levels**: Use different log levels (e.g., INFO, WARN, ERROR) to categorize log messages.
- **Structured Logging**: Use structured formats (e.g., JSON) to facilitate easier parsing and analysis.
- **Log Rotation**: Implement log rotation to manage log file sizes and ensure logs do not consume excessive disk space.

###### Code Example
```typescript
enum LogLevel {
  INFO,
  WARN,
  ERROR,
}

interface LogEntry {
  timestamp: string;
  level: LogLevel;
  message: string;
  metadata?: Record<string, any>;
}

const logs: LogEntry[] = [];

function log(level: LogLevel, message: string, metadata?: Record<string, any>) {
  const entry: LogEntry = {
    timestamp: new Date().toISOString(),
    level,
    message,
    metadata,
  };
  logs.push(entry);
  console.log(`${entry.timestamp} [${LogLevel[level]}] ${entry.message}`);
}
```

##### Best Practices
- **Consistent Formatting**: Ensure all log entries follow a consistent format for easier analysis.
- **Include Contextual Information**: Add contextual data (e.g., user ID, session ID) to logs to aid in troubleshooting.
- **Secure Logging**: Protect sensitive information by sanitizing log data and restricting access to log files.

#### 2.1.2 Error Handling and Management
Implement comprehensive error handling to manage and respond to errors effectively.

##### Key Implementation Details
- **Centralized Error Handling**: Use centralized error handling mechanisms to manage errors consistently across the application.
- **Error Classification**: Categorize errors based on their type and severity to facilitate targeted responses.
- **Feedback Mechanism**: Provide clear and actionable feedback to users when errors occur.

###### Code Example
```javascript
function handleError(error) {
  switch(error.name) {
    case 'NotAllowedError':
      showFeedback('权限被拒绝，请检查麦克风设置。');
      break;
    case 'NoSpeechError':
      showFeedback('未检测到语音，请重试。');
      break;
    case 'NetworkError':
      showFeedback('网络错误，请检查您的连接。');
      break;
    case 'ServiceNotAllowedError':
      showFeedback('服务未获授权，请检查 API 密钥。');
      break;
    case 'NotFoundError':
      showFeedback('未找到音频输入设备，请连接一个麦克风。');
      break;
    case 'NotReadableError':
      showFeedback('麦克风不可用，请检查设备连接。');
      break;
    default:
      showFeedback('发生错误，请稍后再试。');
      break;
  }
  log(LogLevel.ERROR, error.message, { error });
}
```

##### Best Practices
- **Avoid Silent Failures**: Ensure all errors are logged and handled appropriately to prevent silent failures.
- **Provide Meaningful Messages**: Offer clear and understandable error messages to users to aid in troubleshooting.
- **Retry Mechanisms**: Implement retry mechanisms for transient errors to improve resilience.

### 2.2 Device Management and Error Handling

#### 2.2.1 Device Enumeration and Selection
Enumerate available devices (e.g., microphones) and allow users to select a specific device for use.

##### Key Implementation Details
- **Enumeration Process**: Use `navigator.mediaDevices.enumerateDevices()` to retrieve a list of available media devices.
- **Filtering**: Filter devices based on their type (e.g., `audioinput` for microphones).
- **User Interface Integration**: Populate a selection element (e.g., dropdown menu) with available devices.

###### Code Example
```javascript
navigator.mediaDevices.enumerateDevices().then(devices => {
  const microphones = devices.filter(device => device.kind === 'audioinput');
  const selectElement = document.getElementById('microphone-select');
  selectElement.innerHTML = ''; // Clear existing options

  microphones.forEach(microphone => {
    const option = document.createElement('option');
    option.value = microphone.deviceId;
    option.text = microphone.label || `Microphone ${microphones.indexOf(micro