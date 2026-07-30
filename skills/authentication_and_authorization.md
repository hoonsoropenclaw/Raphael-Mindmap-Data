# Authentication and Authorization

## Overview
This document outlines a comprehensive micro-skill for managing access control, authentication mechanisms, and OAuth security integration. The goal is to ensure secure access to resources, provide detailed auditing of access control decisions, and allow administrators to modify policies in real-time without requiring system restarts or code changes.

---

## 1. Role-Based Access Control (RBAC) System

### 1.1 RBAC Permission Check

#### Purpose
Develop a robust permission-checking engine that supports various types of permission handling logic based on roles.

#### Key Features and Code Patterns

1. **Boolean-Type Permissions**
   - **Description**: Simple allow or deny permissions.
   - **Example**: `canEdit: true` or `canDelete: false`.
   - **Implementation**:
     ```javascript
     const permissions = {
       canEdit: true,
       canDelete: false
     };
     ```

2. **Function-Type Permissions**
   - **Description**: Dynamic permission evaluation based on context.
   - **Example**: `canEdit(user, resource) => resource.ownerId === user.id`.
   - **Implementation**:
     ```javascript
     const permissions = {
       canEdit: (user, resource) => resource.ownerId === user.id
     };
     ```

3. **Array-Type Permissions**
   - **Description**: Permission based on membership in a value collection.
   - **Example**: `canViewDept(user) => ['teaching', 'general'].includes(user.dept)`.
   - **Implementation**:
     ```javascript
     const permissions = {
       canViewDept: (user) => ['teaching', 'general'].includes(user.dept)
     };
     ```

4. **Role Inheritance**
   - **Description**: Roles can inherit permissions from other roles.
   - **Example**: `manager` inherits all permissions from `employee`.
   - **Implementation**:
     ```javascript
     const roles = {
       employee: {
         canView: true,
         canEdit: false
       },
       manager: {
         inherits: ['employee'],
         canEdit: true
       }
     };
     ```

#### Common Errors and Prevention

- **Error**: Incorrect handling of role inheritance leading to incorrect permission assignments.
  - **Solution**: Recursively expand the inheritance chain during permission checks to ensure all inherited roles' permissions are correctly evaluated.
    ```javascript
    function getAllPermissions(role) {
      let permissions = { ...roles[role] };
      if (permissions.inherits) {
        permissions.inherits.forEach(inheritedRole => {
          const inheritedPermissions = getAllPermissions(inheritedRole);
          permissions = { ...permissions, ...inheritedPermissions };
        });
        delete permissions.inherits;
      }
      return permissions;
    }
    ```

- **Error**: Function-type permissions not correctly handling context, resulting in inaccurate permission judgments.
  - **Solution**: Ensure that function permissions receive the complete context object and use it correctly within the function for evaluation.
    ```javascript
    const permissions = {
      canEdit: (user, resource) => {
        return resource.ownerId === user.id;
      }
    };
    ```

### 1.2 Audit Logging

#### Purpose
Maintain detailed logs of each permission decision for auditing and tracking purposes.

#### Key Features and Code Patterns

1. **Log Recording**
   - **Description**: Capture decision details such as timestamp, user information, permission type, and decision outcome.
   - **Implementation**:
     ```javascript
     function logPermissionDecision(user, permission, result, resource) {
       const logEntry = {
         timestamp: new Date(),
         user: user.id,
         permission: permission,
         result: result,
         resource: resource.id
       };
       // Store logEntry in desired storage medium
     }
     ```

2. **Log Storage**
   - **Description**: Store logs in local files, databases, or remote servers via API.
   - **Implementation**:
     ```javascript
     function storeLog(logEntry) {
       // Example: Store in local file
       fs.appendFileSync('audit_logs.txt', JSON.stringify(logEntry) + '\n');
       
       // Alternatively, store in a database or send via API
     }
     ```

3. **Log Presentation**
   - **Description**: Provide a user interface to view and export audit logs.
   - **Implementation**:
     ```javascript
     function displayLogs() {
       // Fetch logs from storage
       const logs = fetchLogsFromStorage();
       // Render logs in UI
       renderLogsInUI(logs);
     }
     ```

#### Common Errors and Prevention

- **Error**: Incomplete or incorrectly formatted log records.
  - **Solution**: Ensure all necessary information is correctly captured during logging and use a standardized log format.
    ```javascript
    function logPermissionDecision(user, permission, result, resource) {
      const requiredFields = ['timestamp', 'user', 'permission', 'result', 'resource'];
      const logEntry = {
        timestamp: new Date(),
        user: user.id,
        permission: permission,
        result: result,
        resource: resource.id
      };
      if (Object.keys(logEntry).length === requiredFields.length) {
        // Proceed to store logEntry
      } else {
        // Handle missing fields
      }
    }
    ```

- **Error**: Insufficient log storage space.
  - **Solution**: Regularly clean or archive old logs or use rolling log files.
    ```javascript
    function archiveOldLogs() {
      // Logic to archive logs older than a certain date
    }
    ```

### 1.3 Dynamic Policy Management

#### Purpose
Enable administrators to modify permission policies at runtime without restarting the system or changing the codebase.

#### Key Features and Code Patterns

1. **Policy Storage**
   - **Description**: Store policies in `localStorage` or other persistent storage mechanisms.
   - **Implementation**:
     ```javascript
     function savePolicy(policy) {
       localStorage.setItem('policy', JSON.stringify(policy));
     }
     ```

2. **Policy Loading**
   - **Description**: Load policies during system startup and reload them after any modifications.
   - **Implementation**:
     ```javascript
     function loadPolicy() {
       const policy = JSON.parse(localStorage.getItem('policy'));
       // Apply policy to permission engine
     }
     ```

3. **Policy Application**
   - **Description**: Ensure that the latest policies are applied during permission checks.
   - **Implementation**:
     ```javascript
     function checkPermission(user, permission, resource) {
       const policy = loadPolicy();
       // Use policy to evaluate permission
     }
     ```

4. **User Interface**
   - **Description**: Provide an admin interface for editing policies and triggering hot-reloading.
   - **Implementation**:
     ```javascript
     function showAdminUI() {
       // Render UI for editing policies
     }
     
     function triggerPolicyReload() {
       // Reload policy and notify permission engine
     }
     ```

#### Common Errors and Prevention

- **Error**: Policies not taking effect immediately after modification.
  - **Solution**: After policy modification, immediately trigger a policy reload and notify the permission-checking engine to use the new policy.
    ```javascript
    function updatePolicy(newPolicy) {
      savePolicy(newPolicy);
      loadPolicy();
      notifyPermissionEngine();
    }
    ```

- **Error**: Incorrect policy storage format leading to parsing failures.
  - **Solution**: Validate the policy format and syntax before saving and implement error handling during loading.
    ```javascript
    function savePolicy(policy) {
      if (isValidPolicy(policy)) {
        localStorage.setItem('policy', JSON.stringify(policy));
      } else {
        // Handle invalid policy format
      }
    }
    
    function loadPolicy() {
      try {
        const policy = JSON.parse(localStorage.getItem('policy'));
        if (isValidPolicy(policy)) {
          // Apply policy
        } else {
          // Handle invalid policy
        }
      } catch (e) {
        // Handle parsing errors
      }
    }
    ```

---

## 2. Authentication System Integration and Security

### 2.1 Auth Middleware Protection

#### Description
Protect routes using Next.js middleware to ensure only authenticated users can access protected routes.

#### Key Code Snippets and Patterns
```typescript
// middleware.ts
import { NextResponse } from 'next/server';
import { auth } from '@/auth';

export default auth((req) => {
  const { nextUrl } = req;
  const isLoggedIn = !!req.auth?.user;

  if (nextUrl.pathname.startsWith('/api/auth')) {
    return NextResponse.next();
  }

  if (PUBLIC_PATHS.has(nextUrl.pathname)) {
    if (isLoggedIn && nextUrl.pathname === '/') {
      return NextResponse.redirect(new URL('/dashboard', nextUrl));
    }
    return NextResponse.next();
  }

  if (!isLoggedIn) {
    const loginUrl = new URL('/login', nextUrl);
    loginUrl.searchParams.set('callbackUrl', nextUrl.pathname + nextUrl.search);
    return NextResponse.redirect(loginUrl);
  }

  return NextResponse.next();
});
```

#### Common Errors and Prevention
- **Error**: Forgetting to whitelist `/api/auth/*` paths, blocking OAuth callbacks.
  - **Solution**: Explicitly allow `/api/auth/*` paths in the middleware.
- **Error**: Incorrectly setting public paths, preventing unauthenticated users from accessing the homepage.
  - **Solution**: Ensure public paths (e.g., `/` and `/login`) are correctly added to the `PUBLIC_PATHS` set.

### 2.2 Server-Side Session Handling

#### Description
Handle sessions on the server side using NextAuth to ensure sensitive operations are performed securely.

#### Key Code Snippets and Patterns
```typescript
// session.ts
import { NextApiRequest, NextApi