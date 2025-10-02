import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/chat": {
        target: "http://185.185.142.249:8000",
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/chat/, "/chat"),
      },
      "/api": {
        target: "http://185.185.142.249:8000",
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/chat/, "/chat"),
      },
    },
  },
});
