/**
 * Admin Service — CRUD users, locations, procedures + stats + applications + appointments
 */
import { API_BASE_URL, getToken } from './api';

const BASE        = `${API_BASE_URL}/admin`;
const COMMON_BASE = API_BASE_URL;

function authH() {
  const token = getToken();
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
/**
 * Admin — lấy danh sách hồ sơ (có CCCD, docCount, filter nâng cao)
 * Response: { success, data: { items[], total, page, perPage, pages } }
 */
export const getApplications = (params: Record<string, string> = {}) => {
  const q = new URLSearchParams(params).toString();
  return apiFull(`/applications/admin/list${q ? '?' + q : ''}`);
};
export const getApplicationDetail = (id: string) =>
  apiFull(`/applications/${id}/online`);
export const getMyApplications = (params: Record<string, string> = {}) => {
  const q = new URLSearchParams(params).toString();
  return apiFull(`/applications/my${q ? '?' + q : ''}`);
};
export const reviewApplication = (applicationId: string, action: string, note = '') =>
  api('/applications/review', { method: 'POST', body: JSON.stringify({ applicationId, action, note }) });

// ── Appointments ──────────────────────────────────────────────────────────────
export const getAppointments = () => apiFull('/appointments/all');
export const updateAppointmentStatus = (id: string, status: string) =>
  apiFull(`/appointments/${id}/status`, { method: 'PATCH', body: JSON.stringify({ status }) });

// ── Chatbot Config ────────────────────────────────────────────────────────────
export const getChatbotPersonas    = ()                          => apiFull('/chatbot/personas');
export const createChatbotPersona  = (data: object)             => apiFull('/chatbot/personas', { method: 'POST', body: JSON.stringify(data) });
export const updateChatbotPersona  = (id: string, data: object) => apiFull(`/chatbot/personas/${id}`, { method: 'PUT', body: JSON.stringify(data) });
export const deleteChatbotPersona  = (id: string)               => apiFull(`/chatbot/personas/${id}`, { method: 'DELETE' });
export const activateChatbotPersona= (id: string)               => apiFull(`/chatbot/personas/${id}/activate`, { method: 'POST' });

export const getChatbotPrompts    = (type?: string)              => apiFull(`/chatbot/prompts${type ? '?type=' + type : ''}`);
export const createChatbotPrompt  = (data: object)              => apiFull('/chatbot/prompts', { method: 'POST', body: JSON.stringify(data) });
export const updateChatbotPrompt  = (id: string, data: object)  => apiFull(`/chatbot/prompts/${id}`, { method: 'PUT', body: JSON.stringify(data) });
export const deleteChatbotPrompt  = (id: string)                => apiFull(`/chatbot/prompts/${id}`, { method: 'DELETE' });

export const getChatbotRules      = (category?: string)         => apiFull(`/chatbot/rules${category ? '?category=' + category : ''}`);
export const createChatbotRule    = (data: object)              => apiFull('/chatbot/rules', { method: 'POST', body: JSON.stringify(data) });
export const updateChatbotRule    = (id: string, data: object)  => apiFull(`/chatbot/rules/${id}`, { method: 'PUT', body: JSON.stringify(data) });
export const deleteChatbotRule    = (id: string)                => apiFull(`/chatbot/rules/${id}`, { method: 'DELETE' });
export const seedChatbotDefaults  = ()                          => apiFull('/chatbot/seed', { method: 'POST' });
export const invalidateChatbotCache = ()                        => apiFull('/chatbot/invalidate-cache', { method: 'POST' });

// ── Evaluations ───────────────────────────────────────────────────────────────
export const getEvaluations    = ()           => apiFull('/evaluations');
export const getEvaluationStats= ()           => apiFull('/evaluations/stats');
export const submitEvaluation  = (data: object) =>
  apiFull('/evaluations', { method: 'POST', body: JSON.stringify(data) });

// ── Evaluations (Admin — all) ─────────────────────────────────────────────────
export const getAllEvaluations = (params: Record<string, string> = {}) => {
  const q = new URLSearchParams(params).toString();
  return api(`/evaluations${q ? '?' + q : ''}`);
};

/** POST /api/admin/evaluations/:id/reply  — thêm / cập nhật phản hồi */
export const replyToEvaluation = (id: string, replyText: string) =>
  api(`/evaluations/${id}/reply`, { method: 'POST', body: JSON.stringify({ replyText }) });

// ── Audit Logs ────────────────────────────────────────────────────────────────
export const getAuditLogs = (params: Record<string, string> = {}) => {
  const q = new URLSearchParams(params).toString();
  return api(`/audit-logs${q ? '?' + q : ''}`);
};

// ── Queue Management (Admin) ──────────────────────────────────────────────────
export const getQueueSummary = (agencyId: string) =>
  apiFull(`/queue/summary/${agencyId}`);

export const getQueueList = (agencyId: string) =>
  apiFull(`/queue/list/${agencyId}`);

// counterNo là int (1, 2, 3...) — backend: POST /api/queue/call-next { agencyId, counterNo }
export const callNextTicket = (data: { agencyId: string; counterNo?: number; serviceId?: string }) =>
  apiFull('/queue/call-next', { method: 'POST', body: JSON.stringify(data) });

export const updateQueueTicket = (ticketId: string, status: string) =>
  apiFull(`/queue/ticket/${ticketId}/status`, { method: 'PUT', body: JSON.stringify({ status }) });

export const getCounters = (agencyId: string) =>
  apiFull(`/queue/counters/${agencyId}`);

export const upsertCounter = (data: object) =>
  apiFull('/queue/counters', { method: 'POST', body: JSON.stringify(data) });

export const getQueueMapOverview = () =>
  apiFull('/queue/map-overview');

// ── System Settings ───────────────────────────────────────────────────────────
/** Lấy tất cả cài đặt — GET /api/admin/settings */
export const getSystemSettings = () => api('/settings');

/** Cập nhật một cài đặt — PUT /api/admin/settings/:key */
export const updateSystemSetting = (key: string, value: string | boolean | number) =>
  api(`/settings/${key}`, { method: 'PUT', body: JSON.stringify({ value }) });

/** Cập nhật nhiều cài đặt — PUT /api/admin/settings */
export const updateSystemSettings = (settings: Record<string, string | boolean | number>) =>
  api('/settings', { method: 'PUT', body: JSON.stringify({ settings }) });

/** Public settings (không cần auth) — GET /api/admin/settings/public */
export const getPublicSettings = () =>
  apiFull('/admin/settings/public');
