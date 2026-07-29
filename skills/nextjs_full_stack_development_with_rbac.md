# Full-Stack Development with Next.js and Role-Based Access Control (RBAC)

## Overview
This micro-skill focuses on building a full-stack application using the Next.js framework while integrating Role-Based Access Control (RBAC). It covers middleware-based route protection, API route permission checks, UI-level permission enforcement, and best practices for maintaining a secure and scalable RBAC system.

## Key Components

### 1. Role and Permission Definitions
Centralize role and permission definitions to maintain consistency across the application.

```javascript
// lib/rbac.js
export const PERMISSIONS = {
  'document:read': new Set(['admin', 'editor', 'viewer', 'guest']),
  'document:update': new Set(['admin', 'editor']),
  'document:delete': new Set(['admin']),
  // Add other permissions as needed
};

// Function to check if a user has a specific permission
export function can(user, permission, resource) {
  if (!user || !user.role) return { ok: false, message: 'Unauthenticated' };
  
  const rolePermissions = PERMISSIONS[permission] || new Set();
  if (!rolePermissions.has(user.role)) {
    return { ok: false, message: 'Insufficient permissions' };
  }

  // Optional: Resource-level checks for sensitive resources
  if (resource && resource.sensitive && !rolePermissions.has('admin')) {
    return { ok: false, message: 'Access to sensitive resource denied' };
  }

  return { ok: true };
}
```

### 2. Middleware-Based Route Protection
Protect specific routes by implementing middleware that verifies user authentication and role-based access.

```typescript
// middleware.ts
import { NextRequest, NextResponse } from "next/server";

const PROTECTED_PREFIXES = ["/dashboard", "/admin", "/console"];
const PUBLIC_PATHS = ["/login", "/api/login", "/api/audit", "/api/health", "/_next", "/favicon"];

export function middleware(req: NextRequest) {
  const { pathname } = req.nextUrl;
  
  // Allow public paths
  if (PUBLIC_PATHS.some(p => pathname.startsWith(p))) return NextResponse.next();
  
  // Allow unprotected paths
  if (!PROTECTED_PREFIXES.some(p => pathname.startsWith(p))) return NextResponse.next();

  // Extract token from headers or cookies
  const auth = req.headers.get("authorization") ?? "";
  const cookieToken = req.cookies.get("portal_token")?.value;
  const token = auth.replace(/^Bearer\s+/i, "") || cookieToken;
  
  if (!token) {
    const url = req.nextUrl.clone();
    url.pathname = "/login";
    return NextResponse.redirect(url);
  }
  
  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)/"],
};
```

### 3. API Route Permission Checks
Ensure that API routes enforce RBAC by validating user permissions before processing requests.

```typescript
// pages/api/[...slug].ts
import { NextRequest, NextResponse } from "next/server";
import { can, methodToAction, requiredRoleFor } from "@/lib/rbac";

export async function handle(req: NextRequest, platform: string, rest: string[]) {
  // Extract and verify token
  const token = req.headers.get("authorization")?.replace(/^Bearer\s+/i, "") ?? req.cookies.get("portal_token")?.value;
  const user = await verify(token);
  
  if (!user) {
    return withAudit({ status: 401, message: 'Unauthorized' });
  }

  // Map HTTP method to action
  const action = methodToAction(req.method);
  
  // Determine required role for the action
  const requiredRole = requiredRoleFor(platform as Platform, action);
  
  // Check if user has the required role
  const allowed = can(user.role, platform as Platform, action);
  
  if (!allowed) {
    return withAudit({ status: 403, message: 'Forbidden' });
  }

  // Proceed with the request
  return withAudit({ status: 200, data: mockData });
}
```

### 4. UI-Level Permission Enforcement
Enforce RBAC at the UI level by conditionally rendering components and disabling unauthorized actions.

```typescript
// components/ActionButtons.tsx
import { useUser } from "@/lib/auth";

const perms = ROLE_PERMS[user.role][platform as keyof typeof ROLE_PERMS[typeof user.role]];

export default function ActionButtons() {
  return (
    <>
      <button
        formAction={`/api/${platform}${sample}`}
        formMethod="GET"
        disabled={!perms.read}
      >
        List (GET)
      </button>
      <button
        formAction={`/api/${platform}${sample}`}
        formMethod="POST"
        disabled={!perms.write}
      >
        Create (POST)
      </button>
      <button
        formAction={`/api/${platform}${sample}`}
        formMethod="DELETE"
        disabled={!perms.delete}
      >
        Delete (DELETE)
      </button>
    </>
  );
}
```

## Common Errors and Prevention

### 1. Incorrect Permission Logic
- **Error**: Permission checks are flawed, allowing unauthorized access.
- **Prevention**: 
  - Implement thorough unit tests for permission logic.
  - Regularly review and audit permission checks.
  - Use centralized RBAC modules to minimize inconsistencies.

### 2. Incomplete Resource-Level Checks
- **Error**: Sensitive resources lack proper permission checks.
- **Prevention**: 
  - Clearly define which resources require additional checks.
  - Implement resource-level checks consistently across the application.
  - Use middleware or higher-order functions to enforce checks.

### 3. Inconsistent UI and Backend Permissions
- **Error**: UI permissions do not align with backend RBAC policies.
- **Prevention**: 
  - Synchronize permission definitions between frontend and backend.
  - Use shared permission constants or modules.
  - Implement client-side validation based on user roles.

### 4. Improper Matcher Configuration
- **Error**: Middleware matcher incorrectly protects or exposes routes.
- **Prevention**: 
  - Carefully define the `matcher` regex to target specific routes.
  - Test middleware with various routes to ensure correct behavior.
  - Use tools like regex testers to validate matcher patterns.

### 5. Insufficient Audit Logging
- **Error**: Lack of audit logs for RBAC-related events.
- **Prevention**: 
  - Implement audit logging for all permission checks and access attempts.
  - Use centralized logging systems to store and manage audit logs.
  - Regularly review audit logs to detect and respond to potential security issues.

## Best Practices

- **Centralize RBAC Logic**: Keep all RBAC-related logic in a centralized module to ensure consistency and ease of maintenance.
- **Least Privilege Principle**: Grant users the minimum permissions necessary to perform their tasks.
- **Regular Audits**: Conduct regular security audits to verify RBAC implementation and identify vulnerabilities.
- **Error Handling**: Provide clear and consistent error messages for unauthorized access attempts without revealing sensitive information.
- **Secure Token Handling**: Ensure that tokens are securely stored and transmitted, using HTTPS and secure cookie settings.

## Additional Recommendations

### 1. Role Hierarchy
Implement a role hierarchy to simplify permission management. For example, an `admin` role can inherit permissions from `editor` and `viewer` roles.

### 2. Dynamic Permission Assignment
Allow dynamic assignment of permissions to roles or users to accommodate changing business requirements.

### 3. User-Friendly Error Messages
Provide user-friendly error messages that inform users of the actions they can take, such as requesting additional permissions or contacting an administrator.

### 4. Performance Optimization
Optimize RBAC checks for performance by caching permission data and minimizing the number of checks performed per request.

### 5. Integration with Authentication Systems
Integrate RBAC with existing authentication systems to leverage existing user management and authentication mechanisms.

By following these guidelines and implementing the provided code snippets, you can effectively enforce RBAC in your Next.js application, enhancing security and ensuring that users have appropriate access to resources and functionalities.