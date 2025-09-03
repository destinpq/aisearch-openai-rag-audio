import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";
import path from "path";

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [react()],
    build: {
        outDir: "../backend/static",
        emptyOutDir: true,
        sourcemap: false,
        minify: "terser"
    },
    resolve: {
        preserveSymlinks: true,
        alias: {
            "@": path.resolve(__dirname, "./src")
        }
    },
    server: {
        host: "0.0.0.0",
        port: 5173,
        proxy: {
            "/realtime": {
                target: "wss://converse-api.destinpq.com",
                ws: true,
                rewriteWsOrigin: true
            },
            "/register": {
                target: "https://converse-api.destinpq.com",
                changeOrigin: true
            },
            "/login": {
                target: "https://converse-api.destinpq.com",
                changeOrigin: true
            },
            "/upload": {
                target: "https://converse-api.destinpq.com",
                changeOrigin: true
            },
            "/analyze": {
                target: "https://converse-api.destinpq.com",
                changeOrigin: true
            },
            "/call": {
                target: "https://converse-api.destinpq.com",
                changeOrigin: true
            }
        }
    }
});
