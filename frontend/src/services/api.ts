import axios from "axios";

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export const api = axios.create({
  baseURL: BASE_URL,
  timeout: 30_000,
});

// Attach auth token from localStorage
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("rift_token");
  if (token) {
    config.headers["Authorization"] = `Bearer ${token}`;
  }
  return config;
});

// Clear token on 401 and dispatch an event so the app can redirect
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("rift_token");
      // Dispatch a custom event; the AuthProvider listens and redirects via React Router
      window.dispatchEvent(new CustomEvent("rift:auth:expired"));
    }
    return Promise.reject(error);
  }
);
