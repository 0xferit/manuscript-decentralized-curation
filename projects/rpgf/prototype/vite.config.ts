/// <reference types="vitest" />
import { defineConfig, type UserConfig } from "vite";
import react from "@vitejs/plugin-react";

const config: UserConfig & { test?: Record<string, unknown> } = {
  plugins: [react()],
  server: {
    port: 5173,
    strictPort: false,
  },
  test: {
    globals: true,
    environment: "node",
    include: ["tests/**/*.test.ts"],
  },
};

export default defineConfig(config);
