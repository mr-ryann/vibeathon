import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 20000
});

export function getHealth() {
  return api.get("/health");
}

export function fetchTrends(payload) {
  return api.post("/api/trends/fetch", payload);
}

export function generateScript(payload) {
  return api.post("/api/script/generate", payload);
}

export function processVideo(formData) {
  return api.post("/api/upload/process", formData, {
    headers: { "Content-Type": "multipart/form-data" }
  });
}

export function getAnalytics() {
  return api.get("/api/analytics");
}

export default api;
