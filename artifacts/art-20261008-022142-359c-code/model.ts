// src/permissions/model.ts
// RBAC model: users → roles → permissions (resource:action)
// Pure data + functions, no React. Easy to unit test.

export type Permission =
  | "flow:read"
  | "flow:create"
  | "flow:edit"
  | "flow:delete"
  | "flow:submit"
  | "flow:approve"
  | "user:manage";

export type Role = "employee" | "manager" | "director" | "principal" | "admin";

export const ROLE_PERMISSIONS: Record<Role, Permission[]> = {
  employee: ["flow:read", "flow:create", "flow:submit"],
  manager: ["flow:read", "flow:create", "flow:edit", "flow:submit", "flow:approve"],
  director: ["flow:read", "flow:create", "flow:edit", "flow:submit", "flow:approve"],
  principal: ["flow:read", "flow:approve"],
  admin: [
    "flow:read",
    "flow:create",
    "flow:edit",
    "flow:delete",
    "flow:submit",
    "flow:approve",
    "user:manage",
  ],
};

export interface User {
  id: string;
  name: string;
  roles: Role[]; // multi-role: union permissions
}

export function permissionsFor(user: User): Set<Permission> {
  const out = new Set<Permission>();
  for (const r of user.roles) {
    for (const p of ROLE_PERMISSIONS[r] ?? []) out.add(p);
  }
  return out;
}

export function can(user: User, perm: Permission): boolean {
  return permissionsFor(user).has(perm);
}

export function canAny(user: User, perms: Permission[]): boolean {
  const set = permissionsFor(user);
  return perms.some((p) => set.has(p));
}

// Throws a structured error so the API middleware / server can return 403.
export class PermissionDeniedError extends Error {
  constructor(public user: User, public perm: Permission) {
    super(`Permission denied: user ${user.id} lacks ${perm}`);
  }
}

// Server-side guard. NEVER trust the client; always re-check on API.
export function requirePermission(user: User, perm: Permission): void {
  if (!can(user, perm)) throw new PermissionDeniedError(user, perm);
}
