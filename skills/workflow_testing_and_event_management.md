# Workflow Testing and Event Management

## Overview
The **Workflow Testing and Event Management** micro-skill is designed to ensure the efficiency, stability, and reliability of projects and systems. This skill integrates comprehensive testing, workflow optimization, event handling, synchronization, deduplication, and simulation execution. It leverages automation tools, session management, and structured methodologies to enhance productivity, consistency, and quality assurance.

## Key Components

### 1. Comprehensive Testing and Workflow Management

#### 1.1 End-to-End Testing and Bug Resolution

##### 1.1.1 Session-Aware End-to-End Testing

###### **Purpose**
Manage the `currentSession` context within a sandboxed environment to ensure session information is correctly read and updated across multiple functions and scopes.

###### **Key Techniques and Patterns**

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

###### **Common Errors and Prevention**

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

##### 1.1.2 jsdom-Based E2E Testing

###### **Purpose**
Utilize jsdom to simulate a browser environment for end-to-end interaction testing of frontend applications, verifying UI rendering and user operations.

###### **Key Techniques and Patterns**

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

###### **Common Errors and Prevention**

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

##### 1.1.3 Integration of Session Management and E2E Testing

###### **Ensuring Session Consistency in Tests**

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

###### **Error Prevention in Integrated Testing**

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

#### 1.2 Bug Tracking and Resolution

##### **Explanation**
This skill involves tracking and resolving errors in the code to ensure the system runs smoothly. It includes debugging and testing to identify and fix issues.

##### **Key Code Snippets and Patterns**
```javascript
function debugError(error) {
  console.error(error);
  // Further debugging and handling of the error
}

function testFunction() {
  // Test code
  assert.equal(result, expected, 'Result does not match expected value');
}
```

##### **Common Errors and Prevention Methods**

- **Error:** Error messages are not detailed enough, making it difficult to locate the problem.
  **Solution:** Use detailed error messages, including error type, location, and cause.
- **Error:** Insufficient testing, leading to errors not being detected in a timely manner.
  **Solution:** Write unit tests and integration tests to ensure code correctness and stability.
- **Error:** After fixing an error, regression testing is not performed, leading to new issues.
  **Solution:** Perform regression testing after fixing errors to ensure that the fix does not introduce new problems.

### 2. Audit and Testing Management

#### 2.1 Audit Log Management

##### **Purpose**
- To record critical user operations and events for subsequent auditing and monitoring.

##### **Key Techniques and Patterns**

1. **Mounting Audit Logs for Testing**:
   - Expose audit logs and statistics to the global scope for easy access during testing.
     ```javascript
     if (typeof window !== 'undefined') {
       window.__auditLog = auditLog;
       window.__stats = stats;
     }
     ```

2. **Logging Audit Entries**:
   - Record audit entries with detailed information, including a timestamp.
     ```javascript
     function logAuditEntry(entry) {
       auditLog.unshift({ ...entry, timestamp: new Date().toLocaleTimeString() });
     }
     ```

##### **Common Mistakes and Prevention**

- **Insufficient Context in Logs**:
  - **Issue**: Lack of detailed context makes it difficult to trace user actions.
  - **Prevention**: Include comprehensive operation details, executor information, and timestamps when logging.

- **Inconsistent Log Implementation**:
  - **Issue**: Discrepancies between client-side and server-side logging lead to data inconsistencies.
  - **Prevention**: Centralize audit logging on the server side and ensure all critical operations are recorded there.

#### 2.2 Structured Refusal Handling

##### **Purpose**
- To decline non-compliant or potentially harmful requests in a clear and structured manner, while offering alternative solutions.

##### **Key Techniques and Patterns**

1. **3-Strike Progressive Refusal Pattern**:
   - **First Strike**: Refuse the request and provide a reason.
     ```plaintext
     "I'm sorry, but we cannot process your request as it does not meet our security standards."
     ```
   - **Second Strike**: Specify the exact limitations or issues.
     ```plaintext
     "The request exceeds the maximum allowed data size of 10MB."
     ```
   - **Third Strike**: Offer alternative options or suggestions.
     ```plaintext
     "Consider splitting the data into smaller chunks or using our API to upload the data securely."
     ```

2. **Referencing User Documentation**:
   - Cite principles from USER.md or other relevant documents to justify the refusal.
     ```plaintext
     "As stated in our USER.md under 'Data Handling Guidelines', we cannot process requests that contain sensitive information without proper encryption."
     ```

3. **Providing Specific Options**:
   - List different task directions or specific steps for the user to choose from.