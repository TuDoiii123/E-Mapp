/**
 * Admin Service — CRUD users, locations, procedures + stats
 */
const BASE = 'http://localhost:8888/api/admin';

function authH() {
  const token = localStorage.getItem('token');
  return token
    ? { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` }
    : { 'Content-Type': 'application/json' };
}

async function api(path: string, opts: RequestInit = {}) {
  const res  = await fetch(`${BASE}${path}`, { headers: authH(), ...opts });
  const json = await res.json();
  if (!json.success) throw new Error(json.message || 'Lỗi');
  return json;
}

// ── Stats ─────────────────────────────────────────────────────────────────────
export const getStats = () => api('/stats');

// ── Users ─────────────────────────────────────────────────────────────────────
export const getUsers = (params: Record<string, string> = {}) => {
  const q = new URLSearchParams(params).toString();
  return api(`/users${q ? '?' + q : ''}`);
};
export const getUser        = (id: string)              => api(`/users/${id}`);
export const createUser     = (data: object)            => api('/users', { method: 'POST', body: JSON.stringify(data) });
export const updateUser     = (id: string, data: object)=> api(`/users/${id}`, { method: 'PUT', body: JSON.stringify(data) });
export const deleteUser     = (id: string)              => api(`/users/${id}`, { method: 'DELETE' });
export const resetPassword  = (id: string, newPassword: string) =>
  api(`/users/${id}/reset-password`, { method: 'POST', body: JSON.stringify({ newPassword }) });

// ── Locations ─────────────────────────────────────────────────────────────────
export const getLocations   = (params: Record<string, string> = {}) => {
  const q = new URLSearchParams(params).toString();
  return api(`/locations${q ? '?' + q : ''}`);
};
export const getLocation    = (id: string)              => api(`/locations/${id}`);
export const createLocation = (data: object)            => api('/locations', { method: 'POST', body: JSON.stringify(data) });
export const updateLocation = (id: string, data: object)=> api(`/locations/${id}`, { method: 'PUT', body: JSON.stringify(data) });
export const deleteLocation = (id: string)              => api(`/locations/${id}`, { method: 'DELETE' });

// ── Procedures ────────────────────────────────────────────────────────────────
export const getProcedures   = (params: Record<string, string> = {}) => {
  const q = new URLSearchParams(params).toString();
  return api(`/procedures${q ? '?' + q : ''}`);
};
export const getProcedure    = (id: string)              => api(`/procedures/${id}`);
export const createProcedure = (data: object)            => api('/procedures', { method: 'POST', body: JSON.stringify(data) });
export const updateProcedure = (id: string, data: object)=> api(`/procedures/${id}`, { method: 'PUT', body: JSON.stringify(data) });
export const deleteProcedure = (id: string)              => api(`/procedures/${id}`, { method: 'DELETE' });
