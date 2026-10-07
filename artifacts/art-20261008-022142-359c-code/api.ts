// src/server/api.ts
// Mock server. In a real app, this runs in a Node process behind auth middleware.
// Here we expose the same shape so the front-end fetch wrapper can use it,
// AND so we can unit-test the permission boundary directly.
import { requirePermission, type User, type Permission } from "../permissions/model";

export interface ApiResponse<T> {
  ok: boolean;
  data?: T;
  error?: string;
}

export function apiFlowGet(user: User, _id: string): ApiResponse<{ id: string }> {
  try {
    requirePermission(user, "flow:read");
    return { ok: true, data: { id: _id } };
  } catch (e) {
    return { ok: false, error: (e as Error).message };
  }
}

export function apiFlowCreate(user: User): ApiResponse<{ created: true }> {
  try {
    requirePermission(user, "flow:create");
    return { ok: true, data: { created: true } };
  } catch (e) {
    return { ok: false, error: (e as Error).message };
  }
}

export function apiFlowDelete(user: User, _id: string): ApiResponse<{ deleted: true }> {
  try {
    requirePermission(user, "flow:delete");
    return { ok: true, data: { deleted: true } };
  } catch (e) {
    return { ok: false, error: (e as Error).message };
  }
}

export function apiFlowSubmit(user: User): ApiResponse<{ submitted: true }> {
  try {
    requirePermission(user, "flow:submit");
    return { ok: true, data: { submitted: true } };
  } catch (e) {
    return { ok: false, error: (e as Error).message };
  }
}

export function apiFlowApprove(user: User): ApiResponse<{ approved: true }> {
  try {
    requirePermission(user, "flow:approve");
    return { ok: true, data: { approved: true } };
  } catch (e) {
    return { ok: false, error: (e as Error).message };
  }
}

// Generic test helper: confirms a user can/cannot hit any perm
export function assertAllowed(user: User, perm: Permission): boolean {
  try {
    requirePermission(user, perm);
    return true;
  } catch {
    return false;
  }
}
