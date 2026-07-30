# Session-Aware End-to-End Testing

## Overview
Session-aware end-to-end (E2E) testing ensures the consistency and reliability of applications across different scopes and contexts by managing session information and simulating realistic browser environments. This micro-skill combines session context management with jsdom-based E2E testing to provide a comprehensive approach to testing that accounts for session-specific behaviors and user interactions.

## Session Context Management

### Purpose
Manage the `currentSession` context within a sandboxed environment to ensure session information is correctly read and updated across multiple functions and scopes.

### Key Techniques and Patterns
- **Binding `currentSession` to `window` for Cross-Scope Access:**
  ```javascript
  // Bind currentSession to window to allow access across different scopes
  const patchedCode = mainCode.replace(/let currentSession = null;/, 'let currentSession = window.currentSession;');
  ```
  
- **Ensuring All Assignments Update `window.currentSession`:**
  ```javascript
  // Update window.currentSession whenever currentSession is assigned
  patchedCode = patchedCode.replace(/currentSession = user;/g, 'window.currentSession = user; currentSession = user;');
  ```

### Common Errors and Prevention
- **Error:** Initializing `currentSession` only once within a function, causing subsequent updates to not reflect globally.
  **Prevention:** Bind `currentSession` to `window.currentSession` to ensure all updates are reflected in the global context.
  ```javascript
  // Incorrect
  function initializeSession(user) {
    let currentSession = user;
  }

  // Correct
  function initializeSession(user) {
    window.currentSession = user;
    let currentSession = window.currentSession;
  }
  ```

- **Error:** Incorrectly comparing `window.currentSession` with a string in conditional statements, leading to logical errors.
  **Prevention:** Use parentheses to clarify operator precedence.
  ```javascript
  // Incorrect
  if (window.currentSession && window.currentSession.role == 'viewer') { ... }

  // Correct
  if ((window.currentSession && window.currentSession.role) === 'viewer') { ... }
  ```

## jsdom-Based E2E Testing

### Purpose
Utilize jsdom to simulate a browser environment for end-to-end interaction testing of frontend applications, verifying UI rendering and user operations.

### Key Techniques and Patterns
- **Simulating the Browser Environment with jsdom:**
  ```javascript
  // Create a new jsdom instance to simulate the browser environment
  const dom = new JSDOM(patched, {
    url: 'http://localhost:3000/',
    runScripts: 'dangerously',
    pretendToBeVisual: true,
    beforeParse(window) {
      window.zod = z;
    },
  });
  ```

- **Waiting for DOM to Load:**
  ```javascript
  // Wait for the DOM to load completely before proceeding with tests
  await new Promise((resolve) => {
    if (document.readyState === 'complete') resolve();
    else window.addEventListener('load', () => resolve());
  });
  ```

### Common Errors and Prevention
- **Error:** Failing to properly simulate external resources such as CDN scripts, leading to test failures.
  **Prevention:** Replace external resources with local stubs or mocks within the simulated environment.
  ```javascript
  // Example of replacing an external script with a mock
  beforeParse(window) {
    window.externalScript = mockExternalScript;
  },
  ```

- **Error:** Not accounting for asynchronous operations in tests, resulting in inaccurate test results.
  **Prevention:** Use appropriate asynchronous control mechanisms such as `async/await` to handle asynchronous operations and wait for related actions to complete.
  ```javascript
  // Example of using async/await to handle asynchronous operations
  test('should perform user action and wait for result', async () => {
    const result = await performUserAction();
    expect(result).toBe(expectedResult);
  });
  ```

## Integration of Session Management and E2E Testing

### Ensuring Session Consistency in Tests
- **Injecting Session Information:**
  When setting up the jsdom environment, inject the `currentSession` into the `window` object to simulate a real user session.
  ```javascript
  beforeParse(window) {
    window.currentSession = mockCurrentSession;
  },
  ```

- **Verifying Session-Dependent Behaviors:**
  After simulating user interactions, verify that the application behaves correctly based on the injected session information.
  ```javascript
  test('should display user-specific content based on session', async () => {
    // Simulate user action
    await simulateUserAction();

    // Verify that the content is specific to the session
    const content = dom.window.document.querySelector('#user-content').textContent;
    expect(content).toBe(mockCurrentSession.userContent);
  });
  ```

### Error Prevention in Integrated Testing
- **Error:** Session information not correctly propagated during tests, causing inconsistent behavior.
  **Prevention:** Ensure that the `currentSession` is properly bound to the `window` object and that all updates to `currentSession` are reflected in the simulated environment.
  ```javascript
  // Example of ensuring session propagation
  beforeParse(window) {
    window.currentSession = mockCurrentSession;
    window.currentSession.update = function(newData) {
      window.currentSession = newData;
    };
  },
  ```

- **Error:** Asynchronous session updates not handled correctly, leading to test flakiness.
  **Prevention:** Use `async/await` to handle asynchronous session updates and ensure that tests wait for these updates to complete before making assertions.
  ```javascript
  test('should update session and reflect changes in UI', async () => {
    // Perform action that updates session
    await updateSession();

    // Wait for UI to reflect session changes
    await waitForUIUpdate();

    // Verify that UI reflects session changes
    const content = dom.window.document.querySelector('#session-dependent-content').textContent;
    expect(content).toBe(mockCurrentSession.updatedContent);
  });
  ```

## Conclusion
By integrating session context management with jsdom-based E2E testing, this micro-skill provides a robust framework for testing applications that rely on session-specific behaviors. Proper management of session information and simulation of realistic browser environments are crucial for ensuring the reliability and consistency of frontend applications.