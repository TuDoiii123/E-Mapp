/**
 * Admin Service — CRUD users, locations, procedures + stats + applications + appointments
 */
const BASE       = 'http://localhost:8888/api/admin';
const COMMON_BASE = 'http://localhost:8888/api';

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

async function apiFull(path: string, opts: RequestInit = {}) {
  const res  = await fetch(`${COMMON_BASE}${path}`, { headers: authH(), ...opts });
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

// ── Applications ──────────────────────────────────────────────────────────────
export const getApplications = (params: Record<string, string> = {}) => {
  const q = new URLSearchParams(params).toString();
  return apiFull(`/applications/search${q ? '?' + q : ''}`);
};
export const getMyApplications = (params: Record<string, string> = {}) => {
  const q = new URLSearchParams(params).toString();
  return apiFull(`/applications/my${q ? '?' + q : ''}`);
};
export const reviewApplication = (applicationId: string, action: string, note = '') =>
  api('/applications/review', { method: 'POST', body: JSON.stringify({ applicationId, action, note }) });

// ── Appointments ──────────────────────────────────────────────────────────────
export const getAppointments = () => apiFull('/appointments/all');
