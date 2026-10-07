// tests/permissions.test.ts
// Unit tests for the RBAC model. Covers normal, empty, and edge cases.
import { describe, expect, it } from "vitest";
import {
  permissionsFor,
  can,
  canAny,
  requirePermission,
  PermissionDeniedError,
  type User,
} from "../src/permissions/model";

const employee: User = { id: "1", name: "員工", roles: ["employee"] };
const manager: User = { id: "2", name: "組長", roles: ["manager"] };
const multi: User = { id: "3", name: "雙重身分", roles: ["employee", "manager"] };
const principal: User = { id: "4", name: "校長", roles: ["principal"] };
const admin: User = { id: "5", name: "管理員", roles: ["admin"] };

describe("RBAC: permissionsFor", () => {
  it("employee has read/create/submit but not approve", () => {
    const p = permissionsFor(employee);
    expect(p.has("flow:read")).toBe(true);
    expect(p.has("flow:approve")).toBe(false);
  });

  it("manager has approve but not delete", () => {
    expect(can(manager, "flow:approve")).toBe(true);
    expect(can(manager, "flow:delete")).toBe(false);
  });

  it("multi-role user is UNION (not first-wins)", () => {
    expect(can(multi, "flow:approve")).toBe(true); // from manager
    expect(can(multi, "flow:submit")).toBe(true); // from employee
  });

  it("admin has all permissions", () => {
    expect(can(admin, "flow:delete")).toBe(true);
    expect(can(admin, "user:manage")).toBe(true);
  });

  it("canAny returns true if ANY perm is present", () => {
    expect(canAny(principal, ["flow:approve", "user:manage"])).toBe(true);
  });

  it("requirePermission throws on denial", () => {
    expect(() => requirePermission(employee, "flow:delete")).toThrow(PermissionDeniedError);
  });

  it("requirePermission does not throw on grant", () => {
    expect(() => requirePermission(admin, "flow:delete")).not.toThrow();
  });

  it("edge: empty roles = no perms", () => {
    const ghost: User = { id: "0", name: "ghost", roles: [] };
    expect(permissionsFor(ghost).size).toBe(0);
    expect(can(ghost, "flow:read")).toBe(false);
  });

  it("edge: principal has approve but not submit (read-only approver)", () => {
    expect(can(principal, "flow:approve")).toBe(true);
    expect(can(principal, "flow:submit")).toBe(false);
  });
});
