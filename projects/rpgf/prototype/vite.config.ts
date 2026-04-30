/// <reference types="vitest" />
import { fileURLToPath, URL } from "node:url";
import { defineConfig, type UserConfig } from "vite";
import react from "@vitejs/plugin-react";

const r = (p: string) => fileURLToPath(new URL(p, import.meta.url));

const config: UserConfig & { test?: Record<string, unknown> } = {
  plugins: [react()],
  resolve: {
    alias: {
      "@shared": r("./src/engine/shared"),
      "@bootstrap": r("./src/engine/bootstrap"),
      "@curation": r("./src/engine/curation"),
      "@adjudication": r("./src/engine/adjudication"),
      "@allocation": r("./src/engine/allocation"),
      "@reputation": r("./src/engine/reputation"),
      "@lifecycle": r("./src/engine/lifecycle"),
      "@inspector": r("./src/inspector"),
    },
  },
  server: {
    port: 5173,
    strictPort: false,
  },
  test: {
    globals: true,
    environment: "node",
    include: ["src/**/*.test.ts", "src/**/*.test.tsx", "tests/**/*.test.ts"],
  },
};

export default defineConfig(config);
