# Advanced Access Control and Logging

## Overview
This micro-skill focuses on implementing robust security and user management within applications by combining role-based access control (RBAC), session persistence, route guards, audit logging, and demo user setup. These components work together to ensure that users have appropriate access to resources, sessions are maintained across page refreshes, unauthorized access is prevented, and system activities are properly logged.

## Session Persistence with LocalStorage

### Description
This component is responsible for storing user session data, such as email, name, and role, in the browser's `LocalStorage` to maintain data persistence across page refreshes. It includes methods for setting and retrieving session data.

### Implementation
```javascript
class Session {
  static set(data) {
    try {
      localStorage.setItem('session', JSON.stringify(data));
    } catch (error) {
      console.error('Error setting session data:', error);
    }
  }

  static load() {
    try {
      const data = localStorage.getItem('session');
      return data ? JSON.parse(data) : null;
    } catch (error) {
      console.error('Error loading session data:', error);
      return null;
    }
  }

  static clear() {
    try {
      localStorage.removeItem('session');
    } catch (error) {
      console.error('Error clearing session data:', error);
    }
  }
}
```

### Usage
```javascript
// Setting session data
Session.set({ email: 'user@example.com', name: 'John Doe', role: 'admin' });

// Loading session data
const session = Session.load();
console.log(session);

// Clearing session data
Session.clear();
```

### Error Prevention
- **Try-Catch Blocks**: Ensure that any errors during setting, loading, or clearing session data are caught and logged.
- **Data Validation**: Validate the data before storing it in `LocalStorage` to prevent potential security issues.

## RBAC Implementation

### Description
This component defines roles, resources, and actions, and implements the core permission-checking function `can(user, action, resource)`. It also handles permission inheritance, such as an admin inheriting permissions from manager and viewer roles.

### Implementation
```javascript
const roles = {
  admin: ['manager', 'viewer'],
  manager: ['viewer'],
  viewer: []
};

const resources = ['dashboard', 'users', 'settings'];

function can(user, action, resource) {
  if (!user || !user.role) {
    return false;
  }

  const userRoles = getAllRoles(user.role);

  return userRoles.some(role => {
    const permissions = getPermissionsForRole(role);
    return permissions.includes(`${action}:${resource}`);
  });
}

function getAllRoles(role) {
  let rolesList = [role];
  let queue = [role];
  while (queue.length > 0) {
    const current = queue.shift();
    const inherited = roles[current];
    if (inherited) {
      rolesList = rolesList.concat(inherited);
      queue = queue.concat(inherited);
    }
  }
  return Array.from(new Set(rolesList));
}

function getPermissionsForRole(role) {
  // Placeholder for role-based permissions
  // In a real scenario, this would retrieve permissions for the given role
  return [];
}
```

### Usage
```javascript
const user = { role: 'admin' };
console.log(can(user, 'read', 'dashboard')); // true
console.log(can(user, 'write', 'users'));    // true
console.log(can(user, 'delete', 'settings')); // true
```

### Error Prevention
- **User Validation**: Ensure that the user object and its role are defined before checking permissions.
- **Role Inheritance**: Properly handle circular inheritance to avoid infinite loops.

## Route Access Guard

### Description
This component checks if a user has the right to access a specific route. It uses the `canAccessRoute(user, route)` function, which internally calls `can(user, 'read', requiredResource)` to determine if the user has the necessary permissions.

### Implementation
```javascript
function canAccessRoute(user, route) {
  const requiredResource = getRequiredResource(route);
  return can(user, 'read', requiredResource);
}

function getRequiredResource(route) {
  const routePermissions = {
    '/dashboard': 'dashboard',
    '/users': 'users',
    '/settings': 'settings'
    // Add more routes and their required resources
  };
  return routePermissions[route] || null;
}
```

### Usage
```javascript
const user = { role: 'viewer' };
console.log(canAccessRoute(user, '/dashboard')); // true
console.log(canAccessRoute(user, '/users'));    // false
```

### Error Prevention
- **Route Validation**: Ensure that the route exists in the `routePermissions` mapping.
- **User Object**: Validate that the user object is provided and contains a role.

## Demo User Setup

### Description
This component defines a set of default demo users with corresponding roles, such as `admin@nextjs.local`, `manager@nextjs.local`, and `viewer@nextjs.local`. It ensures that these users are available when the application starts and have the correct role permissions.

### Implementation
```javascript
const demoUsers = [
  { email: 'admin@nextjs.local', name: 'Admin User', role: 'admin' },
  { email: 'manager@nextjs.local', name: 'Manager User', role: 'manager' },
  { email: 'viewer@nextjs.local', name: 'Viewer User', role: 'viewer' }
];

function setupDemoUsers() {
  demoUsers.forEach(user => {
    // In a real scenario, this would create the user in the database
    console.log(`Setting up demo user: ${user.email} with role: ${user.role}`);
  });
}

function getDemoUser(email) {
  return demoUsers.find(user => user.email === email) || null;
}
```

### Usage
```javascript
setupDemoUsers();
const adminUser = getDemoUser('admin@nextjs.local');
console.log(adminUser);
```

### Error Prevention
- **User Uniqueness**: Ensure that demo user emails are unique to prevent conflicts.
- **Data Integrity**: Validate that each demo user has a valid role.

## Audit Logging

### Description
This component is responsible for logging all significant actions and access attempts within the application. It helps in monitoring and auditing user activities for security and compliance purposes.

### Implementation
```javascript
function logAction(user, action, resource, timestamp = new Date()) {
  const logEntry = {
    user: user.email,
    action,
    resource,
    timestamp
  };
  console.log('Audit Log:', logEntry);
  // In a real scenario, this would write the log to a file or database
}

function logAccessAttempt(user, route, granted) {
  const status = granted ? 'granted' : 'denied';
  logAction(user, 'access', route, new Date());
  console.log(`Access ${status} for user ${user.email} to route ${route}`);
}
```

### Usage
```javascript
const user = { email: 'user@example.com', role: 'viewer' };
logAccessAttempt(user, '/dashboard', canAccessRoute(user, '/dashboard'));
```

### Error Prevention
- **Logging Errors**: Ensure that any errors during logging are caught and handled gracefully.
- **Data Privacy**: Avoid logging sensitive information such as passwords or personal data.

## Conclusion
By integrating these components, the application achieves a comprehensive access control and logging system. This system not only manages user permissions and sessions effectively but also provides a mechanism for auditing and maintaining security standards.