import axios from "axios";

const baseURL = import.meta.env.VITE_API_BASE_URL || "http://localhost:5000/api";

const api = axios.create({ baseURL });

// Attach JWT from localStorage to every request.
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("sob_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Normalise errors + auto-logout on 401.
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem("sob_token");
      localStorage.removeItem("sob_user");
      if (!window.location.pathname.startsWith("/login")) {
        window.location.href = "/login";
      }
    }
    const message =
      err.response?.data?.error || err.message || "Something went wrong";
    return Promise.reject(new Error(message));
  }
);

// Unwrap the { success, data } envelope.
const unwrap = (p) => p.then((r) => r.data.data);

export default api;
export { unwrap };
