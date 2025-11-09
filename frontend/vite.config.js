import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5000,
    host: "0.0.0.0",
    strictPort: true,
    hmr: {
      protocol: 'wss',
      host: '53f5c5e1-daad-4912-baf8-3021b0947944-00-2ke9oz9rxh47x.sisko.replit.dev',
      port: 443,
      clientPort: 443
    },
    allowedHosts: [
      "53f5c5e1-daad-4912-baf8-3021b0947944-00-2ke9oz9rxh47x.sisko.replit.dev",
      ".replit.dev"
    ]
  }
});
