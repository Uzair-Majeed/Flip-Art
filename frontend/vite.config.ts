import { defineConfig } from "vite";

// https://vite.dev/config/
export default defineConfig({
  server: {
    port: 5173,
    proxy: {
      // Proxy all /api and /health requests to the Flask backend
      "/api": {
        target: "http://127.0.0.1:5000",
        changeOrigin: true,
      },
      "/health": {
        target: "http://127.0.0.1:5000",
        changeOrigin: true,
      },
    },
  },
});
