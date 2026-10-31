import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";

// Day-3: proxy /api requests to the FastAPI backend on :8000 so the front-end
// can fetch("/api/flows/...") without CORS or absolute URLs. In production we
// serve everything from one origin, so this proxy is purely a dev convenience.
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
      },
      "/health": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
      },
    },
  },
  preview: {
    port: 4173,
    proxy: {
      "/api": { target: "http://127.0.0.1:8000", changeOrigin: true },
      "/health": { target: "http://127.0.0.1:8000", changeOrigin: true },
    },
  },
  test: {
    globals: true,
    environment: "jsdom",
    setupFiles: ["./tests/setup.ts"],
    exclude: ["**/node_modules/**", "tests/e2e/**"],
  },
});
