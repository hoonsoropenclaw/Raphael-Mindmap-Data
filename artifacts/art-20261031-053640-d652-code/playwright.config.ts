// playwright.config.ts
import { defineConfig } from "@playwright/test";

// 2026-10-31 (Q4): the e2e ports are configurable, and the webServer is NOT
// reused blindly.
//
// Two real problems this fixes (both found by actually running the suite on
// 2026-10-31, not by reading the config):
//
//   (a) Port 4173 was already occupied by an unrelated long-running project
//       (capstone-procedure-decision-ledger). With `reuseExistingServer: true`
//       Playwright silently reused THAT server, so every spec failed with
//       "flow-editor element not found" — the app under test was never
//       loaded. The failure message looked like an app bug; the cause was a
//       port collision.
//
//   (b) A stale server on the same port serves a *different* application.
//       `reuseExistingServer: true` turns "port busy" into "silently testing
//       the wrong thing", which is the worst failure mode: a green run that
//       proves nothing.
//
// So: the port comes from the environment (E2E_PORT), default 4180; and
// reuseExistingServer is false, so Playwright always starts the server from
// THIS project. If the port is busy, the suite fails loudly instead of
// testing someone else's app.
//
// 2026-10-31 (second revision): the default moved off 4173 → 4180 because
// 4173 was permanently occupied on this machine by an unrelated long-running
// project (capstone-procedure-decision-ledger). A default that collides with
// a known occupant just guarantees the suite can never run unattended.
//
// API_PORT is exported by scripts/run_all.sh so the vite preview proxy
// (vite.config.ts reads API_PORT) points at the SAME backend the rest of
// the checks hit.
const E2E_PORT = Number(process.env.E2E_PORT || "4180");
const BASE_URL = process.env.E2E_BASE_URL || `http://127.0.0.1:${E2E_PORT}`;

export default defineConfig({
  testDir: "./tests/e2e",
  // Day-3: the e2e specs share a single SQLite-backed flow (flow-default).
  // Running with 2 workers causes test A's reset to race with test B's
  // assertions. Serialise via workers: 1 to make the suite deterministic.
  workers: 1,
  webServer: {
    command: `node node_modules/vite/bin/vite.js preview --port ${E2E_PORT} --host 127.0.0.1 --strictPort`,
    port: E2E_PORT,
    // 2026-10-31: never reuse. See (b) above — reusing can silently point the
    // suite at a completely different application.
    reuseExistingServer: false,
    timeout: 60_000,
  },
  use: { baseURL: BASE_URL },
});
