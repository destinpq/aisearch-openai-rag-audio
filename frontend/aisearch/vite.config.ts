import path from "path";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [react()],
    build: {
        outDir: "/home/azureuser/aisearch-openai-rag-audio/app/backend/static-aisearch",
        emptyOutDir: true,
        sourcemap: true
    },
    resolve: {
        preserveSymlinks: true,
        alias: {
            "@": path.resolve(__dirname, "./src")
        }
    },
    server: {
        proxy: {
            "/realtime": {
                target: "ws://localhost:8765",
                ws: true,
                rewriteWsOrigin: true
            },
            "/api": {
                target: "http://localhost:8765",
                changeOrigin: true
            },
            "/process-pdf": {
                target: "http://localhost:8765",
                changeOrigin: true
            },
            "/document": {
                target: "http://localhost:8765",
                changeOrigin: true
            },
            "/documents": {
                target: "http://localhost:8765",
                changeOrigin: true
            }
        }
    }
});
