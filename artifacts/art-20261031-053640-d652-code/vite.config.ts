import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";

// The backend port is read from the environment so that the WHOLE chain
// (run_all.sh → uvicorn → vite proxy → vitest → playwright → probe) talks
// to ONE backend instance.
//
// 2026-10-31 (second revision, found by actually running the suite):
//   Every layer used to hardcode :8000. When that port was already taken by
//   a stale server, the proxy silently pointed at the WRONG backend while
//   the tests looked like they were passing/failing for app reasons.
//   That is the same failure family as playwright.config.ts's
//   `reuseExistingServer` bug: a port collision disguised as an app bug.
//
//   API_PORT is now the single source of truth for the backend port.
//   Default is 8010 (not 8000) because 8000 is commonly occupied on a
//   developer box and a collision must be loud, not silent.
const API_PORT = process.env.API_PORT || "8010";
const BACKEND = `http://127.0.0.1:${API_PORT}`;
const PREVIEW_PORT = Number(process.env.E2E_PORT || "4180");

// Day-3: proxy /api requests to the FastAPI backend so the front-end
// can fetch("/api/flows/...") without CORS or absolute URLs. In production we
// serve everything from one origin, so this proxy is purely a dev convenience.
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/api": {
        target: BACKEND,
        changeOrigin: true,
      },
      "/health": {
        target: BACKEND,
        changeOrigin: true,
      },
    },
  },
  preview: {
    port: PREVIEW_PORT,
    proxy: {
      "/api": { target: BACKEND, changeOrigin: true },
      "/health": { target: BACKEND, changeOrigin: true },
    },
  },
  test: {
    globals: true,
    environment: "jsdom",
    setupFiles: ["./tests/setup.ts"],
    exclude: ["**/node_modules/**", "tests/e2e/**"],
  },
});
