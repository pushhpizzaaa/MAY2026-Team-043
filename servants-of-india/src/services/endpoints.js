import api, { unwrap } from "./api";

// Thin, typed-ish wrappers grouped by domain. Every call returns the unwrapped
// `data` payload (or throws an Error with the server message).

export const authApi = {
  register: (body) => unwrap(api.post("/auth/register", body)),
  login: (body) => unwrap(api.post("/auth/login", body)),
};

export const userApi = {
  me: () => unwrap(api.get("/users/me")),
  updateMe: (body) => unwrap(api.put("/users/me", body)),
  changePassword: (body) => unwrap(api.put("/users/me/password", body)),
  list: (params) => unwrap(api.get("/users", { params })),
  create: (body) => unwrap(api.post("/users", body)),
  setStatus: (id, status) => unwrap(api.patch(`/users/${id}/status`, { status })),
};

export const categoryApi = {
  list: () => unwrap(api.get("/categories")),
};

export const eventApi = {
  list: (params) => unwrap(api.get("/events", { params })),
  get: (id) => unwrap(api.get(`/events/${id}`)),
  create: (body) => unwrap(api.post("/events", body)),
  update: (id, body) => unwrap(api.put(`/events/${id}`, body)),
  remove: (id) => unwrap(api.delete(`/events/${id}`)),
};

export const submissionApi = {
  create: (formData) =>
    unwrap(
      api.post("/submissions", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      })
    ),
  mine: () => unwrap(api.get("/submissions/me")),
  queue: (status) => unwrap(api.get("/submissions", { params: { status } })),
  get: (id) => unwrap(api.get(`/submissions/${id}`)),
  approve: (id, remarks) => unwrap(api.post(`/submissions/${id}/approve`, { remarks })),
  reject: (id, remarks) => unwrap(api.post(`/submissions/${id}/reject`, { remarks })),
};

export const progressApi = {
  me: () => unwrap(api.get("/progress/me")),
};

export const certificateApi = {
  generate: () => unwrap(api.post("/certificates/generate")),
  me: () => unwrap(api.get("/certificates/me")),
  verify: (code) => unwrap(api.get(`/verify/${code}`)),
  // Super Admin: record of every issued certificate.
  list: () => unwrap(api.get("/certificates")),
};

export const notificationApi = {
  list: () => unwrap(api.get("/notifications")),
  markRead: (id) => unwrap(api.patch(`/notifications/${id}/read`)),
};

export const adminApi = {
  stats: () => unwrap(api.get("/admin/stats")),
};
