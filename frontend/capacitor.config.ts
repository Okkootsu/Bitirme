import type { CapacitorConfig } from "@capacitor/cli";

const config: CapacitorConfig = {
  appId: "com.insülita.app",
  appName: "İnsülita",
  webDir: "dist",
  server: {
    url: "http://192.168.1.102:5173",
    cleartext: true,
  },
};

export default config;
