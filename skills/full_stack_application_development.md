# Full-Stack Application Development with RBAC and SPA in Next.js

## Overview
This comprehensive micro-skill focuses on building secure, scalable, and efficient full-stack applications using Next.js. It encompasses both **Role-Based Access Control (RBAC)** and **Single Page Application (SPA)** development. The guide covers essential aspects such as middleware-based route protection, API route permission checks, UI-level permission enforcement, strict TypeScript configurations, server-side rendering (SSR) optimization, and best practices for maintaining a robust and maintainable codebase.

## Key Components

### 1. Role and Permission Definitions

Centralizing role and permission definitions is crucial for maintaining consistency across the application.

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

### 4. UI-Level Permission Enforcement in React Flow

Enforce RBAC at the UI level by conditionally rendering components and disabling unauthorized actions.

```javascript
// Role Definitions
const ROLES = {
  guest: { name: 'Guest', permissions: [] },
  sysadmin: { name: 'System Administrator', permissions: ['read', 'write', 'approve', 'reject', 'reset'] },
  // Other roles...
};

// Node Permission Matrix
const NODE_PERMS = {
  'submit_request': { write: ['sysadmin', 'dept_officer'], approve: ['sysadmin'], reject: ['sysadmin'] },
  // Other nodes...
};

// Permission Check Functions
const canWrite = (role, nodeId) => NODE_PERMS[nodeId].write.includes(role);
const canApprove = (role, nodeId) => NODE_PERMS[nodeId].approve.includes(role);

// Custom Node Component
const FlowStepNode = ({ id, data, selected }) => (
  <div className={`flow-node ${data.status}`}>
    <div className="fn-title">{data.label}</div>
    <div className="fn-meta">
      {canWrite(currentRole, id) ? 'Editable' : 'Read-Only'}
    </div>
    {/* Other content... */}
  </div>
);

// Dynamic State Engine
const computedEdges = useMemo(() => {
  return edges.map(edge => ({
    ...edge,
    className: edgeStatusMapping[edge.status],
  }));
}, [edges]);

// Operation Controller
const handleSubmit = (nodeId) => {
  if (canWrite(currentRole, nodeId)) {
    // Execute submission logic
  }
};
```

## Best Practices for RBAC Implementation

- **Centralize RBAC Logic**: Maintain all RBAC-related logic in a centralized module to ensure consistency and ease of maintenance.
- **Least Privilege Principle**: Grant users the minimum permissions necessary to perform their tasks.
- **Regular Audits**: Conduct regular security audits to verify RBAC implementation and identify vulnerabilities.
- **Error Handling**: Provide clear and consistent error messages for unauthorized access attempts without revealing sensitive information.
- **Secure Token Handling**: Ensure that tokens are securely stored and transmitted, using HTTPS and secure cookie settings.

## Additional Recommendations for RBAC

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

## Best Practices for SPA Development with Next.js

### 1. Strict TypeScript Configuration

Enforce strict TypeScript rules to catch potential type-related errors during development.

```json
// tsconfig.json
{
  "strict": true,
  "noEmit": true,
  "compilerOptions": {
    // Additional compiler options can be added here
  }
}
```

- **File Extensions**: Use `.tsx` for files containing JSX and `.ts` for other TypeScript files.
- **Type Sharing**: Utilize the `@/lib/data` directory and `import type` to share types between server and client, ensuring zero-cost type imports.

### 2. Implementing API Routes

Create backend endpoints within your Next.js application to handle various HTTP requests.

```tsx
// pages/api/health.ts
export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const status = searchParams.get("status");
  const role = searchParams.get("role");
  // ... additional logic
  return NextResponse.json({ /* response data */ }, { status: 200 });
}

// pages/api/users.ts
export async function POST(request: Request) {
  let body: CreateUserPayload = {};
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ ok: false, error: "Invalid JSON body" }, { status: 400 });
  }
  // ... additional logic, such as creating a user
  return NextResponse.json({ ok: true, user: created, note: "Echo only — not persisted in this demo" }, { status: 201 });
}
```

### 3. Optimizing Server-Side Rendering (SSR)

Leverage SSR to render pages on the server, enhancing initial load times and SEO performance.

```tsx
// pages/index.tsx
export default function Home() {
  return (
    <div>
      {/* Page content */}
    </div>
  );
}

// components/ServerComponent.tsx
"use server";
import { /* imports */ } from "...";

const ServerComponent = () => {
  // Server-only logic
  return <div>Server Component</div>;
};

export default ServerComponent;
```

### 4. Component Organization

Organize components within the `src/components/` directory, prioritizing server-rendered components and marking interactive components with `use client`.

```tsx
// Example of a server-first component
const Navbar = () => {
  return <nav>...</nav>;
};

export default Navbar;

//