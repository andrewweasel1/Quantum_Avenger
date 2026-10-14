import { fileURLToPath, URL } from "node:url";

import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

// The dev server proxies /api to the FastAPI backend (uvicorn on :8000), so the
// React app and the engine API share an origin in development. The production
// build is emitted to dist/ and served by FastAPI itself (see api/app.py).
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: { "@": fileURLToPath(new URL("./src", import.meta.url)) },
  },
  server: {
    port: 5173,
    proxy: {
      "/api": { target: "http://127.0.0.1:8000", changeOrigin: true },
    },
  },
  build: {
    outDir: "dist",
    sourcemap: false,
    chunkSizeWarningLimit: 600, // recharts is a single ~520KB lib; nothing to split further
    rollupOptions: {
      output: {
        // Split heavy, rarely-changing vendors so the app chunk stays small and
        // the charting lib is cached independently of feature work.
        manualChunks: {
          react: ["react", "react-dom"],
          charts: ["recharts"],
          query: ["@tanstack/react-query"],
        },
      },
    },
  },
});
