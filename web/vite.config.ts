import { defineConfig } from "vite";
import solid from "vite-plugin-solid";

export default defineConfig({
  base: "/",
  plugins: [solid()],
  publicDir: "public",
  server: { port: 5173, open: false },
});
