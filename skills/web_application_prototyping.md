# Web Application Prototyping

## Overview
Web Application Prototyping focuses on developing self-contained prototypes and mock websites to support the design and testing process. This involves creating standalone web applications, building system integration prototypes, developing minimal executable prototypes, and establishing mock websites for various testing purposes such as crawling and frontend functionality validation.

## Key Techniques and Tools

### 1. Standalone Web Application Development

#### Description
Build fully independent web applications using React and Babel, packaged into a single HTML file containing all necessary JavaScript, CSS, and simulated persistence (e.g., localStorage). These applications run directly in the browser without external dependencies.

#### Key Technologies and Tools
- **React**: For building user interfaces.
- **Babel Standalone**: For in-browser compilation of React JSX code.
- **HTML/CSS/JavaScript**: Core technologies for application development.
- **localStorage**: For simulating persistent data storage.

#### Implementation Steps

##### a. Setting Up a Single HTML File Application
Embed all necessary resources into a single HTML file to ensure the application is completely self-contained.

```html
<!DOCTYPE html>
<html lang="zh-Hant">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Standalone Web Application</title>
  <style>
    /* Embedded CSS Styles */
    body {
      font-family: Arial, sans-serif;
      margin: 0;
      padding: 0;
      background-color: #f0f0f0;
    }
    /* Additional Styles */
  </style>
</head>
<body>
  <div id="root"></div>

  <!-- React 18 + Babel Standalone -->
  <script crossorigin src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
  <script crossorigin src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
  <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>

  <!-- Application JSX Code -->
  <script type="text/babel">
    const { useState, useEffect } = React;

    const App = () => {
      const [count, setCount] = useState(() => {
        // Using localStorage for simulated persistence
        const storedCount = localStorage.getItem('count');
        return storedCount ? parseInt(storedCount, 10) : 0;
      });

      useEffect(() => {
        localStorage.setItem('count', count);
      }, [count]);

      return (
        <div style={{ textAlign: 'center', marginTop: '50px' }}>
          <h1>Counter</h1>
          <p>Current Count: {count}</p>
          <button onClick={() => setCount(count + 1)}>Increase</button>
          <button onClick={() => setCount(count - 1)}>Decrease</button>
        </div>
      );
    };

    ReactDOM.render(<App />, document.getElementById('root'));
  </script>
</body>
</html>
```

##### b. Using Babel Standalone for JSX Compilation
Include Babel Standalone in the HTML file to compile JSX code in the browser.

```html
<!-- React 18 + Babel Standalone -->
<script crossorigin src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
<script crossorigin src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
<script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
```

##### c. Handling Common Errors and Performance Optimization
- **Error**: React code not compiling correctly.
  - **Solution**: Ensure the Babel script is correctly included and set the `<script>` tag's `type` attribute to `text/babel`.
- **Error**: Performance issues.
  - **Solution**: Use Babel Standalone only in development environments. For production, use pre-compiled code via build tools like Webpack or Parcel.

##### d. Simulating Persistent Storage
Use `localStorage` to simulate data persistence.

```javascript
const localStorage = {
  _s: {},
  getItem(k) { return this._s[k] || null; },
  setItem(k, v) { this._s[k] = String(v); },
  removeItem(k) { delete this._s[k]; }
};

// Usage Example
localStorage.setItem('key', 'value');
const value = localStorage.getItem('key');
```

##### e. Cross-Browser Compatibility
Conduct cross-browser testing during development and use polyfills or fallback solutions to handle incompatibilities. For example, use Babel to transpile modern JavaScript syntax for older browsers.

### 2. System Integration Prototype

#### Description
Design a prototype that integrates multiple systems or services, such as linking Google Calendar with a personnel case system.

#### Example Code Snippet
```html
<!-- Simple Integration Prototype Example -->
<!DOCTYPE html>
<html>
<head>
    <title>Integration Prototype</title>
</head>
<body>
    <h1>Personnel Cases & Google Calendar Integration</h1>
    <div id="timeline">
        <!-- Timeline content -->
    </div>
    <div id="reminders">
        <!-- Reminders content -->
    </div>
    <script>
        // Mock data
        const cases = [
            // Personnel case data
        ];
        const calendarEvents = [
            // Calendar event data
        ];
        
        // Merge logic
        const timelineData = mergeData(cases, calendarEvents);
        
        // Render timeline
        renderTimeline(timelineData);
        
        // Function definitions
        function mergeData(cases, calendarEvents) {
            // Merging logic
        }
        
        function renderTimeline(data) {
            // Rendering logic
        }
    </script>
</body>
</html>
```

#### Common Mistakes and Prevention
- **Mistake**: Integration logic is too simplistic and cannot handle the complexities of real-world applications.
  - **Prevention**: Simulate multiple scenarios in the prototype and design corresponding handling mechanisms.
- **Mistake**: Ignoring security considerations.
  - **Prevention**: Incorporate basic authentication and authorization mechanisms during the prototype design phase.

### 3. Minimal Executable Prototype

#### Description
Build a minimal but executable prototype to demonstrate core functionalities when complete specifications are unavailable.

#### Example Code Snippet
```python
def build_minimal_prototype(specs):
    # Identify key features
    key_features = identify_key_features(specs)
    
    # Use mock data
    mock_data = generate_mock_data(key_features)
    
    # Build a simple UI or interface
    prototype = create_prototype_ui(mock_data)
    
    return prototype

def identify_key_features(specs):
    # Logic to identify key features
    pass

def generate_mock_data(features):
    # Logic to generate mock data
    pass

def create_prototype_ui(data):
    # Logic to create a simple UI
    pass
```

#### Common Mistakes and Prevention
- **Mistake**: The prototype is too simple and fails to demonstrate actual application scenarios.
  - **Prevention**: Ensure the prototype includes core logic and data flow, not just static pages.
- **Mistake**: Over-reliance on mock data, causing the prototype to diverge from the actual application.
  - **Prevention**: Clearly mark the use of mock data in the prototype and gradually replace it with real data in subsequent stages.

### 4. Mock Site Creation

#### Description
Establish a local mock website with multiple static HTML pages for testing crawlers and frontend functionality.

#### Key Code Snippet
```html
<!DOCTYPE html>
<html lang="zh-Hant">
<head>
    <meta charset="UTF-8">
    <title>P001 - 藍牙降噪耳機</title>
</head>
<body>
    ...
</body>
</html>
```

#### Common Mistakes and Prevention
- **Mistake**: Mock site lacks necessary pages, causing the crawler to malfunction.
  - **Prevention**: Ensure all target pages (e.g., list pages, detail pages) are created and accessible.
- **Mistake**: The URL structure of the mock site does not match the actual target website, leading to crawler path errors.
  - **Prevention**: Design the mock site with a URL structure that strictly adheres to the target website's structure.

## Best Practices
- **Iterative Development**: Start with a simple prototype and gradually increase complexity as needed.
- **Clear Documentation**: Document the purpose, functionality, and limitations of the prototype to ensure clarity for all stakeholders.
- **User Feedback**: Incorporate user feedback early and often to refine the prototype and align it with user needs.
- **Technical Feasibility**: Regularly assess the technical feasibility of the prototype to ensure it can be developed into a fully functional system.
- **Comprehensive Testing**: Test the mock site thoroughly to ensure it accurately represents the target website and supports the intended testing scenarios.

By following these guidelines and techniques, you can effectively develop and optimize prototypes and mock sites that accurately represent the intended system and facilitate the validation of core concepts and functionalities.