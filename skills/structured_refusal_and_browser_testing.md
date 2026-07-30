# Structured Refusal and Browser Testing

## Overview

This micro-skill focuses on handling refusals in a structured and systematic manner while leveraging browser automation tools for testing and verification. It ensures that any request that does not meet the required standards or poses potential risks is handled gracefully, with clear communication and alternative solutions provided. Additionally, it emphasizes the use of automation tools to streamline the testing process and ensure application reliability.

## Structured Refusal Handling

### Purpose
- To decline requests that are non-compliant or potentially harmful in a clear and structured manner, while offering alternative solutions.

### Key Techniques and Patterns

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
     ```plaintext
     "You can either:
     1. Resubmit the request with the required encryption.
     2. Use our secure data upload portal.
     3. Contact our support team for further assistance."
     ```

### Common Mistakes and Prevention

- **Overly Simple or Vague Refusals**: Ensure that the reason for refusal is clear and unambiguous to prevent user confusion.
  - **Prevention**: Use detailed explanations and provide clear context.
  
- **Lack of Alternative Solutions**: Always offer feasible alternatives to demonstrate the system's willingness to assist.
  - **Prevention**: Brainstorm potential solutions beforehand and include them in the refusal response.
  
- **Aggressive or Offensive Tone**: Maintain professionalism and politeness, avoiding negative or accusatory language.
  - **Prevention**: Use empathetic language and focus on the issue rather than blaming the user.

## Trial and Error with Browser Automation

### Purpose
- To use Playwright and Chromium for automating tests, simulating user interactions, and verifying application functionality.

### Key Techniques and Patterns

1. **Automating Common User Actions**:
   - Simulate adding nodes, performing batch operations, and switching visual effects.
     ```javascript
     const { chromium } = require('playwright');

     (async () => {
       const browser = await chromium.launch();
       const page = await browser.newPage();
       await page.goto('https://your-application-url.com');

       // Simulate adding a node
       await page.click('button#add-node');
       await page.fill('input[name="nodeName"]', 'Test Node');
       await page.click('button#submit-node');

       // Perform batch operations
       await page.click('button#batch-operation');
       await page.selectOption('select#operation-type', 'delete');
       await page.click('button#confirm-operation');

       // Switch visual effects
       await page.click('button#toggle-effects');
       await page.waitForSelector('.effect-active');

       await browser.close();
     })();
     ```

2. **Validating Application Behavior**:
   - Verify that all functionalities work as expected by checking for specific elements or behaviors after each action.
     ```javascript
     // After adding a node
     await page.waitForSelector('.node-item');
     const nodeCount = await page.$$eval('.node-item', nodes => nodes.length);
     console.log(`Number of nodes after addition: ${nodeCount}`);
     ```

3. **Handling Errors and Exceptions**:
   - Implement try-catch blocks to handle potential errors during test execution.
     ```javascript
     try {
       await page.click('button#non-existent-button');
     } catch (error) {
       console.error('Error clicking button:', error);
     }
     ```

### Common Mistakes and Prevention

- **Incomplete Test Coverage**: Ensure that all critical user paths are covered in the automation scripts.
  - **Prevention**: Review user stories and application requirements to identify all necessary test cases.
  
- **Ignoring Asynchronous Operations**: Account for asynchronous behaviors in the application to prevent flaky tests.
  - **Prevention**: Use appropriate wait functions and assertions to handle asynchronous operations.
  
- **Lack of Error Handling**: Implement robust error handling to capture and report issues during test execution.
  - **Prevention**: Use try-catch blocks and logging mechanisms to handle and document errors effectively.

## Conclusion

By combining structured refusal handling with browser automation testing, this micro-skill ensures that user requests are managed professionally and that application functionality is thoroughly validated. This approach not only enhances user experience but also contributes to the overall reliability and security of the system.