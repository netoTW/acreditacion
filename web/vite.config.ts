import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// En desarrollo /api va contra la API local. En el contenedor se define VITE_API.
export default defineConfig({
  plugins: [react()],
  server: {
    host: "0.0.0.0",
    port: 5180,
    proxy: { "/api": { target: "http://localhost:8010", changeOrigin: true, rewrite: (p) => p.replace(/^\/api/, "") } },
  },
});
