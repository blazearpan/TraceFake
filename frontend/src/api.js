const API = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

async function request(path, options = {}) {
  const response = await fetch(`${API}${path}`, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options
  });
  if (!response.ok) {
    let message = "Request failed.";
    try {
      const data = await response.json();
      message = data.detail || message;
    } catch {}
    throw new Error(message);
  }
  return response.json();
}

export const api = {
  health: () => request("/api/health"),
  analyze: (url) => request("/api/scans/analyze", {
    method: "POST",
    body: JSON.stringify({ url })
  }),
  history: () => request("/api/scans"),
  scan: (id) => request(`/api/scans/${id}`),
  remove: (id) => request(`/api/scans/${id}`, { method: "DELETE" }),
  analytics: () => request("/api/analytics"),
  models: () => request("/api/models/status"),
  reportUrl: (id) => `${API}/api/scans/${id}/report`
};
