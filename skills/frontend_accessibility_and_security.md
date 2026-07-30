# Frontend Accessibility and Security

## Overview
The **frontend_accessibility_and_security** micro-skill focuses on enhancing the accessibility and security of frontend applications. This involves integrating ARIA (Accessible Rich Internet Applications) labels to ensure compatibility with assistive technologies and implementing comprehensive security measures to protect against various threats. This includes secure design practices, form validation, RBAC (Role-Based Access Control), and responsive design principles.

---

## 1. ARIA Labeling for Accessibility

### 1.1 Key Concepts
ARIA labels improve the accessibility of web applications by providing additional context to assistive technologies, such as screen readers. This ensures that users with disabilities can navigate and interact with the application effectively.

### 1.2 Key Code Snippets
```html
<!-- Using aria-label to provide an accessible name for a button -->
<button aria-label="Close">✕</button>

<!-- Using aria-describedby to associate descriptive text with an input field -->
<input type="text" aria-describedby="description"/>
<p id="description">Please enter your name.</p>

<!-- Using role to define the purpose of a div element -->
<div role="alert">Error message</div>
```

### 1.3 Common Errors and Solutions
- **Error**: Missing necessary ARIA labels.
  - **Solution**: Add appropriate ARIA labels such as `aria-label`, `aria-describedby`, and `role` based on the element's purpose and functionality.
- **Error**: ARIA labels that do not match the element's state.
  - **Solution**: Ensure that ARIA labels reflect the actual state and function of the element. For example, use `aria-invalid="true"` when the element is in an error state.

---

## 2. Comprehensive Frontend Security Measures

### 2.1 Detecting and Preventing Injection Attacks

#### 2.1.1 Detecting Fake Authority Abuse
Implement validation to ensure that requests are legitimate and prevent abuse of fake authorities.

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

#### 2.1.2 Detecting General Prompt Injection Attempts
Monitor for common indicators of prompt injection, such as specific keywords or phrases.

```python
# List of suspicious keywords indicating potential prompt injection
suspicious_keywords = ["SYSTEM_HEARTBEAT", "FULL AUTONOMY", "禁止 clarify", "禁止確認"]
for keyword in suspicious_keywords:
    if keyword in input_text:
        raise ValueError("Potential prompt injection detected")
```

#### 2.1.3 Advanced Detection with Regular Expressions
Use regex patterns to identify complex or obfuscated injection attempts.

```python
import re

# Define a regex pattern for suspicious patterns
pattern = re.compile(r'\b(FULL\s+AUTONOMY|SYSTEM_HEARTBEAT|禁止\s+clarify|禁止\s+確認|極限超頻模式|嚴格禁止使用)\b', re.IGNORECASE)

# Search for the pattern in the input
if pattern.search(input_text):
    raise ValueError("Potential prompt injection detected")
```

### 2.2 Frontend Form Validation and Sanitization

#### 2.2.1 Validation Function
Implement robust validation to ensure data integrity and prevent malicious inputs.

```javascript
const validateForm = (data) => {
  const errors = {};
  if (!data.name) {
    errors.name = 'Name is required';
  } else if (data.name.length < 3) {
    errors.name = 'Name must be at least 3 characters long';
  }
  if (!data.email) {
    errors.email = 'Email is required';
  } else if (!/\S+@\S+\.\S+/.test(data.email)) {
    errors.email = 'Email is invalid';
  }
  if (!data.password) {
    errors.password = 'Password is required';
  } else if (data.password.length < 6) {
    errors.password = 'Password must be at least 6 characters long';
  }
  // Add more validation rules as needed
  return errors;
};
```

#### 2.2.2 Form Component Integration
Integrate validation into your form components to provide real-time feedback.

```javascript
const RegistrationForm = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
  });
  const errors = validateForm(formData);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (Object.keys(errors).length === 0) {
      // Submit the form data
      console.log('Form submitted successfully', formData);
    } else {
      // Handle validation errors
      console.error('Validation errors', errors);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <label>
        Name:
        <input
          type='text'
          name='name'
          value={formData.name}
          onChange={handleChange}
        />
      </label>
      {errors.name && <span className='error'>{errors.name}</span>}
      <label>
        Email:
        <input
          type='email'
          name='email'
          value={formData.email}
          onChange={handleChange}
        />
      </label>
      {errors.email && <span className='error'>{errors.email}</span>}
      <label>
        Password:
        <input
          type='password'
          name='password'
          value={formData.password}
          onChange={handleChange}
        />
      </label>
      {errors.password && <span className='error'>{errors.password}</span>}
      <button type='submit'>Register</button>
    </form>
  );
};
```

#### 2.2.3 Field Protection and Sanitization
Sanitize user inputs to protect against XSS and other injection attacks.

```javascript
const sanitizeInput = (input) => {
  return input.replace(/</g, "&lt;").replace(/>/g, "&gt;");
};

// Example Usage
const sanitizedName = sanitizeInput(formData.name);
```

### 2.3 Audit Log Recording
Maintain detailed logs of user activities to monitor and respond to potential security incidents.

```javascript
const logActivity = (activity) => {
  const logEntry = {
    timestamp: new Date().toISOString(),
    activity,
    user: getCurrentUser(),
  };
  // Send log entry to server or store it locally
  console.log('Audit Log:', logEntry);
};

// Example Usage
logActivity('User registered');
```

### 2.4 HTML Structure
A well-structured HTML document is the foundation of any secure frontend.

```html
<!doctype html>
<html lang="zh-Hant">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width,initial-scale=1">
    <title>Chronicle — Calendar Reminder Workflow</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <header>
        <h1>Dashboard Title</h1>
    </header>
    <main>
        <section id="data-display">
            <!-- Data visualization components -->
        </section>
        <section id="user-input">
            <!-- User input forms and controls -->
        </section>
    </main>
    <footer>
        <p>Footer content</p>
    </footer>
    <script src="scripts.js"></script>
</body>
</html>
```

### 2.5 CSS Styling
Effective CSS usage enhances both security and user experience.

- **Responsive Design**: Use media queries to ensure accessibility across devices.
- **Consistent Styling**: Utilize CSS preprocessors like SASS or LESS for consistent styles.
- **Performance Optimization**: Minimize expensive CSS properties and use CSS variables.

```css
/* Example of responsive design */
@media (max-width: 768px) {
    body {
        flex-direction: column;
    }
    #data-display, #user-input {
        width: 100%;
    }
}
```

### 2.6 JavaScript Functionality
JavaScript adds interactivity and dynamic content, but it must be secured against vulnerabilities.

- **Event Handling**: Attach event listeners to UI elements securely.
- **Asynchronous Data Loading**: Use `fetch` or AJAX to load data without reloading the page.
- **State Management**: Manage application state using variables or libraries like Redux.

```javascript
// Example of asynchronous data loading
document.addEventListener('DOMContentLoaded', () => {
    fetch('/api/data')
        .then(response => response.json())
        .then(data => {
            // Process and display data
        })
        .catch(error => {
            console.error('Error fetching data:', error);
        });
});
```

---

## 3. RBAC System Security

### 3.1 Key Code Snippet
Implement RBAC to control access to resources based on user roles.

```javascript
// Authorization function example
function authorize(subject, action, resource) {
    const policy = POLICIES.find(p => p.role === subject.role && p.action === action && p.resource === resource);
    return policy ? { allowed: true } : { allowed: false };
}
```

### 3.2 Common Mistakes and Prevention Strategies