// tests/server-api.test.ts
// Verifies the API boundary ALWAYS re-checks permissions.
// These are the "negative" cases that prove the front-end cannot be trusted.
import { describe, expect, it } from "vitest";
import { apiFlowDelete, apiFlowSubmit, apiFlowApprove, apiFlowCreate } from "../src/server/api";
import type { User } from "../src/permissions/model";

const employee: User = { id: "1", name: "員工", roles: ["employee"] };
const manager: User = { id: "2", name: "組長", roles: ["manager"] };

describe("API permission boundary (server-side re-check)", () => {
  it("employee cannot delete (even if UI was bypassed)", () => {
    const r = apiFlowDelete(employee, "flow-1");
    expect(r.ok).toBe(false);
  });

  it("employee can submit (their own perm)", () => {
    const r = apiFlowSubmit(employee);
    expect(r.ok).toBe(true);
  });

  it("manager can approve", () => {
    const r = apiFlowApprove(manager);
    expect(r.ok).toBe(true);
  });

  it("employee cannot approve (front-end <Can> is not the boundary)", () => {
    const r = apiFlowApprove(employee);
    expect(r.ok).toBe(false);
  });

  it("manager cannot delete (only admin can)", () => {
    const r = apiFlowDelete(manager, "flow-1");
    expect(r.ok).toBe(false);
  });

  it("manager can create", () => {
    expect(apiFlowCreate(manager).ok).toBe(true);
  });
});
