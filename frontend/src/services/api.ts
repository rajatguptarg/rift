import axios from "axios";

const BASE_URL = (import.meta as Record<string, unknown>).env?.VITE_API_BASE_URL as string | undefined ?? "http://localhost:8000";

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

// Redirect to /login on 401
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("rift_token");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);
