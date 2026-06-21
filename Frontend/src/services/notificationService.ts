/**
 * Notification Service — list, mark-read, unread-count, push-token registration
 * Uses the shared apiRequest helper from ./api (inherits auth, primary→fallback URL logic).
 * API_BASE_URL already includes /api, so endpoints here are /notifications/…
 */
import { apiRequest } from './api';

export interface NotificationDTO {
  id: string;
  type: string;
  title: string;
  content: string;
  link?: string;
  refId?: string;
  priority: string;
  read: boolean;
  time: string;
}

interface ListResponse {
  success: boolean;
  data: NotificationDTO[];
  total: number;
}

interface CountResponse {
  success: boolean;
  count: number;
}

/** GET /api/notifications?unread=0|1&limit=N */
export async function list(unread = false, limit = 50): Promise<NotificationDTO[]> {
  try {
    const params = new URLSearchParams({
      unread: unread ? '1' : '0',
      limit: String(limit),
    });
    const res = await apiRequest<ListResponse>(`/notifications?${params.toString()}`);
    return res.data ?? [];
  } catch {
    return [];
  }
}

/** GET /api/notifications/unread-count */
export async function unreadCount(): Promise<number> {
  try {
    const res = await apiRequest<CountResponse>('/notifications/unread-count');
    return res.count ?? 0;
  } catch {
    return 0;
  }
}

/** POST /api/notifications/{id}/read */
export async function markRead(id: string): Promise<void> {
  await apiRequest(`/notifications/${encodeURIComponent(id)}/read`, { method: 'POST' });
}

/** POST /api/notifications/read-all */
export async function markAllRead(): Promise<void> {
  await apiRequest('/notifications/read-all', { method: 'POST' });
}

/** POST /api/notifications/push-token  body: { token, platform: 'web' } */
export async function registerPushToken(token: string): Promise<void> {
  await apiRequest('/notifications/push-token', {
    method: 'POST',
    body: JSON.stringify({ token, platform: 'web' }),
  });
}
