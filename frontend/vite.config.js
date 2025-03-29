import { defineConfig, loadEnv } from "vite";
import vue from "@vitejs/plugin-vue";
import AutoImport from "unplugin-auto-import/vite";
import path from "node:path";  // ✅ Так правильно
import fs from 'node:fs'



export default defineConfig(({ mode }) => {
  // ✅ Загружаем `.env` и сохраняем в `env`
  const env = loadEnv(mode, process.cwd());
  console.log("📌 Загруженные переменные .env:", env); // 🔥 Выведем в терминал

  return {
    define: {
      "import.meta.env.VITE_API_URL": JSON.stringify(env.VITE_API_URL),
      "import.meta.env.VITE_WS_URL": JSON.stringify(env.VITE_WS_URL), // ✅ Теперь переменная будет в браузере!
    }, // ✅ Тут закрылся `define`!

    plugins: [
      vue(),
      AutoImport({
        imports: ["vue", "vue-router", "pinia", "@vueuse/core"],
        dts: "src/auto-imports.d.ts",
      }),
    ], // ✅ `plugins` теперь в правильном месте!

    server: {
      https: {
        cert: fs.readFileSync('localhost+2.pem'),
        key: fs.readFileSync('localhost+2-key.pem'),
      },
      host: true,
      port: 5174,
      strictPort: true,
      open: false,
      cors: {
        origin: "https://localhost:5174",
        credentials: true,
      },
      proxy: {
        "/api": {
          target: 'https://localhost:5002', // "http://localhost:5000/api"
          changeOrigin: true,
          secure: true,
          ws: true,
        },
        '/socket.io': {
        target: 'https://localhost:5002',
        ws: true,
        changeOrigin: true,
        secure: true,
        },
        "/static": {
          target: "https://localhost:5002",
          ws: true, // 🔥 Включаем WebSocket
          changeOrigin: true,
          secure: true,
          // Для /static обычно не нужен rewrite. Можно просто убрать его или оставить "пустую" функцию:
          // rewrite: (path) => path,
        }
      },
      watch: {
        usePolling: true,
      },
    },
    build: {
      target: "esnext",
      minify: "esbuild",
      sourcemap: false,
      outDir: path.resolve(__dirname, "../backend/static/dist"),
      emptyOutDir: true,
    },
    resolve: {
      alias: {
        "@": path.resolve(__dirname, "src"),
        "store": path.resolve(__dirname, "src/store"),
      },
    },
  };
});





