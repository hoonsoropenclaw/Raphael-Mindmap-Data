# Application Logging and Error Management

## Overview
This micro-skill focuses on designing and managing audit logs for recording user actions and system events, as well as implementing a comprehensive error handling strategy to ensure system stability and traceability.

## Audit Log Management

### Purpose
To record user operations and system events for future auditing and troubleshooting.

### Key Implementation Details
- **Initialization**: Create a data structure (e.g., an array) to store audit log entries.
- **Logging Function**: Implement a function to record each event with relevant details such as user ID, action, resource, success status, message, and timestamp.
- **Validation**: Ensure each log entry is correctly recorded and validated.

### Code Example
```javascript
// Initialize audit log
const auditLog = [];

// Function to record audit events
function audit(user, action, resource, success, message) {
  const entry = {
    userId: user ? user.id : 'anonymous',
    action,
    resource,
    success,
    message,
    timestamp: new Date().toISOString()
  };
  auditLog.push(entry);
}

// Validation of audit log entry
assert(auditLog.length === before + 1, 'Audit log entry recorded successfully');
```

### Common Errors and Prevention
- **Incomplete or Incorrect Log Format**:
  - **Cause**: Missing or improperly formatted data in log entries.
  - **Solution**: Define a clear log structure and validate entries during testing.
- **Insufficient Storage**:
  - **Cause**: Running out of storage space for logs.
  - **Solution**: Implement log rotation and regular backups.
- **Insecure Access Control**:
  - **Cause**: Unauthorized access to sensitive log data.
  - **Solution**: Enforce strict access controls, ensuring only authorized personnel can view logs.

## Comprehensive Error Handling

### Device Enumeration and Selection

#### Purpose
To manage audio input devices (e.g., microphones) by enumerating available devices and allowing users to select a specific device.

#### Key Implementation Details
- **Enumeration**: Use `navigator.mediaDevices.enumerateDevices()` to retrieve available media devices.
- **Filtering**: Isolate audio input devices by checking `device.kind === 'audioinput'`.
- **User Interface**: Populate a selection element (e.g., dropdown) with device labels or generic names.

#### Code Example
```javascript
navigator.mediaDevices.enumerateDevices().then(devices => {
  const microphones = devices.filter(device => device.kind === 'audioinput');
  const selectElement = document.getElementById('microphone-select');
  selectElement.innerHTML = ''; // Clear existing options

  microphones.forEach(microphone => {
    const option = document.createElement('option');
    option.value = microphone.deviceId;
    option.text = microphone.label || `Microphone ${microphones.indexOf(microphone) + 1}`;
    selectElement.appendChild(option);
  });

  // Select the first microphone by default if available
  if (microphones.length > 0) {
    selectElement.value = microphones[0].deviceId;
  }
}).catch(error => {
  handleError(error);
});
```

#### Common Errors and Prevention
- **Empty Device List**:
  - **Cause**: Lack of user permission or no devices available.
  - **Solution**: Ensure proper permissions and inform the user if no devices are found.
- **Device Selection Not Applied**:
  - **Cause**: Failure to update audio stream constraints after selection.
  - **Solution**: Update constraints and restart the audio recognition process.

### Error Handling and Feedback

#### Purpose
To manage errors during device management and provide clear feedback to users.

#### Key Implementation Details
- **Error Classification**: Categorize errors based on their `name` property.
- **Feedback Mechanism**: Use a `showFeedback` function to display messages.
- **Default Handling**: Provide generic messages for unclassified errors.

#### Code Example
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
}
```

#### Common Errors and Prevention
- **Incomplete Error Classification**:
  - **Cause**: Missing error types in classification.
  - **Solution**: Refer to API documentation and implement specific handlers.
- **Unclear Feedback**:
  - **Cause**: Generic or confusing messages.
  - **Solution**: Provide specific and actionable messages.

### Error Handling Overlay

#### Purpose
To capture unhandled errors and display an overlay for debugging.

#### Key Implementation Details
- **Event Listeners**: Attach listeners for `error` and `unhandledrejection` events.
- **Overlay Creation**: Create a styled `pre` element to display error information.
- **Error Information**: Include stack traces, messages, and source file details.

#### Code Example
```javascript
window.addEventListener('error', (e) => {
  const overlay = document.createElement('pre');
  overlay.style.cssText = 'position:fixed;inset:0;padding:16px;background:#fee;color:#900;overflow:auto;z-index:9999;font:12px monospace;white-space:pre-wrap;';
  overlay.textContent = '[window.error] ' + (e.error?.stack || e.message || e) + '\n  at ' + e.filename + ':' + e.lineno + ':' + e.colno;
  document.body.appendChild(overlay);
});
window.addEventListener('unhandledrejection', (e) => {
  const overlay = document.createElement('pre');
  overlay.style.cssText = 'position:fixed;inset:0;padding:16px;background:#fef3c7;color:#92400e;overflow:auto;z-index:9999;font:12px monospace;white-space:pre-wrap;';
  overlay.textContent = '[unhandledrejection] ' + (e.reason?.stack || e.reason?.message || String(e.reason));
  document.body.appendChild(overlay);
});
```

#### Common Errors and Prevention
- **Overlay Errors**:
  - **Cause**: The overlay itself encounters errors.
  - **Solution**: Ensure overlay code is robust and minimal.
- **Sensitive Information Exposure**:
  - **Cause**: Detailed error information may expose sensitive data.
  - **Solution**: Simplify error messages in production environments.

## Best Practices for Integration

1. **Permission Management**:
   - Request permissions before device enumeration.
   - Handle permission denial or revocation scenarios.

2. **User Experience**:
   - Disable device selection until devices are enumerated.
   - Provide visual indicators for loading, success, and error states.

3. **Fallback Strategies**:
   - Implement fallback options if no devices are available.
   - Consider using default devices if selection fails.

4. **Security Considerations**:
   - Protect user privacy by handling device information securely.
   - Avoid storing sensitive data unless necessary.

5. **Testing**:
   - Test enumeration and selection across different browsers and devices.
   - Simulate various error conditions for robust handling.

By integrating device management with comprehensive error handling and feedback, this micro-skill ensures a smooth and reliable user experience when working with audio input devices.