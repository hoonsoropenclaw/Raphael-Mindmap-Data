# Full-Stack Single Page Application (SPA) Development with Next.js

## Overview
This guide focuses on developing full-stack Single Page Applications (SPAs) using Next.js for both frontend and backend development. The emphasis is on simplicity, scalability, and leveraging TypeScript for optimized and component-based development. By adhering to strict TypeScript configurations, implementing API routes, and optimizing server-side rendering (SSR), developers can create efficient, maintainable, and secure applications.

## 1. Strict TypeScript Configuration

### Configuration Details
Enforce strict TypeScript rules in your Next.js project to catch potential type-related errors during development.

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

- **`strict`**: Enables all strict type-checking options.
- **`noEmit`**: Prevents TypeScript from emitting compiled output, relying on Next.js for bundling.

### Best Practices
- **File Extensions**: Use `.tsx` for files containing JSX and `.ts` for other TypeScript files.
- **Type Sharing**: Utilize the `@/lib/data` directory and `import type` to share types between server and client, ensuring zero-cost type imports.

### Common Errors and Prevention
- **Error**: Forgetting to enable strict mode in `tsconfig.json`.
  - **Prevention**: Always set `"strict": true` and monitor build logs for type errors.
- **Error**: Inconsistent type definitions leading to import issues.
  - **Prevention**: Use `import type` for type imports and maintain consistent type definitions in shared directories.

## 2. Implementing API Routes in Next.js

### Overview
Create backend endpoints within your Next.js application to handle various HTTP requests.

### Key Code Snippets
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

### Best Practices
- **Error Handling**: Always use try-catch blocks to handle exceptions, such as JSON parsing failures.
- **Input Validation**: Validate and sanitize all incoming data to prevent security vulnerabilities.

### Common Errors and Prevention
- **Error**: Not handling exceptions, leading to unexpected crashes.
  - **Prevention**: Implement comprehensive error handling with try-catch blocks and return meaningful error messages.
- **Error**: Lack of input validation, leading to potential security issues.
  - **Prevention**: Implement robust validation rules and sanitize all user input before processing.

## 3. Optimizing Server-Side Rendering (SSR) in Next.js

### Overview
Leverage SSR to render pages on the server, enhancing initial load times and SEO performance. Additionally, use React Server Components (RSC) to reduce client-side JavaScript load.

### Key Code Snippets
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

### Best Practices
- **Selective SSR**: Use SSR only for pages that require SEO or need to be rendered on the server. For static content, consider using Static Site Generation (SSG) to cache pages and reduce server load.
- **React Server Components**: Mark components that do not require client-side interaction by adding `"use server";` at the top. This ensures they are rendered on the server and do not increase the client bundle size.

### Common Errors and Prevention
- **Error**: Overusing SSR, leading to increased server load and potential performance bottlenecks.
  - **Prevention**: Analyze which pages benefit from SSR and use SSG for static content to balance performance and server load.
- **Error**: Incorrect use of RSC, leading to unnecessary client-side JavaScript.
  - **Prevention**: Use `"use client";` to differentiate between server and client components, ensuring interactive components are correctly marked.

## 4. Component Organization in Next.js Applications

### Overview
In a Next.js application, components are organized within the `src/components/` directory. By default, server-rendered components are prioritized, and only parts that require interactivity are marked with `use client`.

### Key Code Snippets
```tsx
// Example of a server-first component
const Navbar = () => {
  return <nav>...</nav>;
};

export default Navbar;

// Example of a client component
"use client";
import { useState } from "react";

const ThemeToggle = () => {
  const [theme, setTheme] = useState("light");
  // ...
};

export default ThemeToggle;
```

### Common Errors and Prevention
- **Error**: Marking non-interactive components with `use client`, leading to performance degradation.
  - **Prevention**: Use `use client` only for components that need to use browser APIs or state management.
- **Error**: Inconsistent type definitions between components, leading to type errors.
  - **Prevention**: Use TypeScript and define types in a shared `@/lib/data` directory.

## Conclusion
By following this guide, you can effectively configure a robust TypeScript setup, implement secure and efficient API routes, and optimize SSR to enhance application performance. Adhering to these practices will help create a more maintainable, performant, and secure code base.