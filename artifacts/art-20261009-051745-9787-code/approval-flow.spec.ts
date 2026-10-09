// tests/e2e/approval-flow.spec.ts
// Playwright e2e covering the two end-to-end paths required by the project goal:
// 1. 員工提交 (employee submits a flow) — sees submit, no delete, no approve buttons
// 2. 校長核准 (principal approves) — sees approve button on principal node, can click
// 3. 組長核准 (manager approves) — same for manager node
//
// Day-2 change: the AuthProvider now reads ?as=<role> from the URL to prefill the
// signed-in user, so the e2e tests can deep-link to /flows?as=role and avoid the
// sign-in-picker flow entirely. This also means the picker remains reachable via /
// for manual QA.
import { test, expect } from "@playwright/test";

const FLOWS = "http://localhost:4173/flows";
const FLOWS_AS = (role: string) => `${FLOWS}?as=${role}`;

test("employee can submit, cannot see approve buttons or delete", async ({ page }) => {
  await page.goto(FLOWS_AS("employee"));
  await expect(page.getByTestId("flow-editor")).toBeVisible();

  // Path 1: employee should see Submit but NOT Delete.
  await expect(page.getByTestId("btn-submit")).toBeVisible();
  await expect(page.getByTestId("btn-delete")).toHaveCount(0);

  // Path 1 (extended): employee should NOT see any 核准/駁回 buttons on the
  // manager/director/principal nodes, because:
  //   - <Can I="flow:approve"> hides them (employee lacks the perm)
  await expect(page.getByTestId("btn-approve-2")).toHaveCount(0);
  await expect(page.getByTestId("btn-approve-3")).toHaveCount(0);
  await expect(page.getByTestId("btn-approve-4")).toHaveCount(0);
  await expect(page.getByTestId("btn-reject-2")).toHaveCount(0);

  // Path 1 (negative): employee cannot reach /admin → /403
  // Use the SPA's <Link> via the editor's "帳號管理" anchor so React context survives.
  await page.getByRole("link", { name: "帳號管理" }).click();
  await expect(page).toHaveURL(/\/403$/);
});

test("principal can approve the principal node", async ({ page }) => {
  await page.goto(FLOWS_AS("principal"));
  await expect(page.getByTestId("flow-editor")).toBeVisible();

  // Path 2: principal can NOT submit (read-only approver) but CAN see the editor
  await expect(page.getByTestId("btn-submit")).toHaveCount(0);
  await expect(page.getByTestId("btn-delete")).toHaveCount(0);

  // Path 2: principal node (id="4") shows the 核准 button (assigned approver + flow:approve perm)
  const approvePrincipal = page.getByTestId("btn-approve-4");
  await expect(approvePrincipal).toBeVisible();

  // Click it → node state should flip to "approved" via the state badge.
  await approvePrincipal.click();
  await expect(page.getByTestId("state-badge-4")).toHaveText("核准");

  // Path 2 (negative): principal CANNOT approve the manager node (id="2"),
  // because principal is not the manager. The button should never render.
  await expect(page.getByTestId("btn-approve-2")).toHaveCount(0);
});

test("manager can approve the manager node; subsequent approve button hides", async ({ page }) => {
  await page.goto(FLOWS_AS("manager"));
  await expect(page.getByTestId("flow-editor")).toBeVisible();

  const approveManager = page.getByTestId("btn-approve-2");
  await expect(approveManager).toBeVisible();

  await approveManager.click();
  await expect(page.getByTestId("state-badge-2")).toHaveText("核准");

  // After acting, the buttons should disappear (acted=true && !pending).
  await expect(page.getByTestId("btn-approve-2")).toHaveCount(0);
  await expect(page.getByTestId("btn-reject-2")).toHaveCount(0);

  // Manager cannot reach the principal node's approve button.
  await expect(page.getByTestId("btn-approve-4")).toHaveCount(0);
});
