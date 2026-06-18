// Shared helpers for the portal pages. JWT is kept in localStorage; every API call
// attaches it as a bearer token. On 401/403 we bounce back to the login page.
const WT = {
  token() { return localStorage.getItem("wt_token"); },
  setToken(t) { localStorage.setItem("wt_token", t); },
  clear() { localStorage.removeItem("wt_token"); },

  async api(method, path, body) {
    const headers = { "Content-Type": "application/json" };
    const t = this.token();
    if (t) headers["Authorization"] = "Bearer " + t;
    const res = await fetch(path, {
      method,
      headers,
      body: body ? JSON.stringify(body) : undefined,
    });
    if (res.status === 401 || res.status === 403) {
      if (path !== "/api/v1/auth/me") { /* allow probing */ }
    }
    let data = null;
    try { data = await res.json(); } catch (e) { /* no body */ }
    if (!res.ok) {
      const detail = (data && data.detail) || ("HTTP " + res.status);
      throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
    }
    return data;
  },

  // multipart form (roster upload)
  async upload(path, formData) {
    const headers = {};
    const t = this.token();
    if (t) headers["Authorization"] = "Bearer " + t;
    const res = await fetch(path, { method: "POST", headers, body: formData });
    const data = await res.json().catch(() => null);
    if (!res.ok) throw new Error((data && data.detail) || ("HTTP " + res.status));
    return data;
  },

  show(id, text, kind) {
    const el = document.getElementById(id);
    if (!el) return;
    el.textContent = text;
    el.className = "msg show " + (kind || "ok");
  },

  requireAuth() {
    if (!this.token()) { window.location = "/app/login"; }
  },

  logout() { this.clear(); window.location = "/app/login"; },

  fmtBytes(b) {
    if (b < 1024) return b + " B";
    if (b < 1024 * 1024) return (b / 1024).toFixed(1) + " KB";
    return (b / (1024 * 1024)).toFixed(1) + " MB";
  },
};
