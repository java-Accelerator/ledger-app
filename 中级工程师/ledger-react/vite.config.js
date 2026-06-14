import react from "@vitejs/plugin-react";

export default {
  base: "./",
  plugins: [react()],
  server: {
    proxy: {
      "/login": "http://127.0.0.1:8000",
      "/register": "http://127.0.0.1:8000",
      "/records": "http://127.0.0.1:8000",
      "/me": "http://127.0.0.1:8000"
    }
  }
};
