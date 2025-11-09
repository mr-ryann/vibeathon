import axios from "axios";

// Backend API URL configuration
// In Replit: Use the public domain with port 8000
// The backend runs on port 8000 which is exposed publicly
const getApiUrl = () => {
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL;
  }
  
  // In Replit, construct the backend URL using the current domain
  if (typeof window !== 'undefined') {
    const hostname = window.location.hostname;
    if (hostname.includes('replit.dev')) {
      return `https://${hostname}:8000`;
    }
  }
  
  return "http://localhost:8000";
};

const API_BASE_URL = getApiUrl();

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
