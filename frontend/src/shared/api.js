import axios from "axios";

export const BASE_URL = "http://localhost:8001/api/v1";

export const api = axios.create({
  baseURL: BASE_URL,
  withCredentials: true,
});

function readCookie(name) {
  const match = document.cookie.match(new RegExp(`(?:^|; )${name}=([^;]*)`));
  return match ? decodeURIComponent(match[1]) : null;
}

api.interceptors.request.use((config) => {
  const method = (config.method || "get").toLowerCase();
  if (["post", "put", "delete", "patch"].includes(method)) {
    const csrf = readCookie("csrf_token");
    if (csrf) config.headers["X-CSRF-Token"] = csrf;
  }
  return config;
});

let refreshInFlight = null;

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const { config, response } = error;
    if (response?.status === 401 && !config._retried && !config.url.includes("/auth/")) {
      config._retried = true;
      try {
        refreshInFlight = refreshInFlight || api.post("/auth/refresh");
        await refreshInFlight;
        refreshInFlight = null;
        return api(config);
      } catch {
        refreshInFlight = null;
      }
    }
    return Promise.reject(error);
  }
);
