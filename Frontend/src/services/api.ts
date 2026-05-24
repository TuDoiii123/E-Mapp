// Provide type declarations for Vite's import.meta.env so TypeScript recognizes it
declare global {
  interface ImportMetaEnv {
    readonly VITE_API_URL?: string;
  }
  interface ImportMeta {
    readonly env: ImportMetaEnv;
  }
}

export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8888/api';
export const API_BASE_URL_FALLBACK = import.meta.env.VITE_API_URL_FALLBACK || 'http://localhost:8889/api';

export interface LoginRequest {
  cccdNumber: string;
  password: string;
}

export interface RegisterRequest {
  cccdNumber: string;
  fullName: string;
  dateOfBirth: string;
  phone: string;
  email: string;
  password: string;
  confirmPassword: string;
  otp?: string;
  useVNeID?: boolean;
}

export interface User {
  id: string;
  cccdNumber: string;
  fullName: string;
  dateOfBirth: string;
  phone: string;
  email: string;
  address?: string;
  avatarUrl?: string;
  role: 'citizen' | 'admin';
  isVNeIDVerified: boolean;
  vneidId: string | null;
  createdAt: string;
  updatedAt: string;
}

export interface AuthResponse {
  success: boolean;
  message: string;
  data: {
    user: User;
    token: string;
  };
}

export interface ProfileResponse {
  success: boolean;
  data: {
    user: User;
  };
}

// Get stored token
export const getToken = (): string | null => {
  return localStorage.getItem('auth_token');
};

// Set token
export const setToken = (token: string): void => {
  localStorage.setItem('auth_token', token);
};

// Remove token
export const removeToken = (): void => {
  localStorage.removeItem('auth_token');
};

// Fetch với fallback URL (dùng cho voice API không qua apiRequest)
async function fetchWithFallback(url: string, opts: RequestInit): Promise<Response> {
  try {
    return await fetch(url, opts);
  } catch {
    if (API_BASE_URL === API_BASE_URL_FALLBACK) throw new Error('Network error');
    const fallbackUrl = url.replace(API_BASE_URL, API_BASE_URL_FALLBACK);
    return fetch(fallbackUrl, opts);
  }
}

// Shared API request helper with primary → fallback URL logic
export async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers instanceof Headers
      ? Object.fromEntries(options.headers.entries())
      : (options.headers as Record<string, string> | undefined)),
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  let response: Response;
  let data: any;

  try {
    response = await fetch(`${API_BASE_URL}${endpoint}`, { ...options, headers });
    data = await response.json();
  } catch (error: any) {
    if (API_BASE_URL !== API_BASE_URL_FALLBACK) {
      try {
        response = await fetch(`${API_BASE_URL_FALLBACK}${endpoint}`, { ...options, headers });
        data = await response.json();
      } catch {
        throw new Error(
          `Không thể kết nối đến server. Vui lòng kiểm tra:\n` +
          `1. Backend server đã chạy chưa?\n` +
          `2. Đã cài đặt dependencies: cd Backend && pip install -r requirements.txt\n` +
          `3. Server đang chạy trên port 8888?\n\n` +
          `Lỗi: ${error.message || 'Network error'}`
        );
      }
    } else {
      throw new Error(
        `Không thể kết nối đến server. Vui lòng kiểm tra:\n` +
        `1. Backend server đã chạy chưa?\n` +
        `2. Đã cài đặt dependencies: cd Backend && pip install -r requirements.txt\n` +
        `3. Server đang chạy trên port 8888?\n\n` +
        `Lỗi: ${error.message || 'Network error'}`
      );
    }
  }

  if (response!.status === 401) {
    // Chỉ kích hoạt session-expiry nếu user đang có token (phân biệt với login sai mật khẩu)
    const hadToken = !!getToken();
    if (hadToken) {
      removeToken();
      window.dispatchEvent(new CustomEvent('auth:logout'));
      throw new Error('Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.');
    }
    // Không có token → 401 bình thường (sai credentials, endpoint public, v.v.)
  }

  if (!response!.ok) {
    throw new Error(data?.message || data?.error || `Lỗi ${response!.status}: ${response!.statusText}`);
  }

  return data;
}

// Auth API
export const authAPI = {
  login: async (credentials: LoginRequest): Promise<AuthResponse> => {
    const response = await apiRequest<AuthResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    });
    if (response.success && response.data.token) {
      setToken(response.data.token);
    }
    return response;
  },

  register: async (userData: RegisterRequest): Promise<AuthResponse> => {
    const response = await apiRequest<AuthResponse>('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
    if (response.success && response.data.token) {
      setToken(response.data.token);
    }
    return response;
  },

  logout: async (): Promise<{ success: boolean; message: string }> => {
    try {
      await apiRequest('/auth/logout', { method: 'POST' });
    } catch {
      // Ignore logout errors — token is cleared regardless
    } finally {
      removeToken();
    }
    return { success: true, message: 'Đăng xuất thành công' };
  },

  getProfile: async (): Promise<ProfileResponse> => {
    return apiRequest<ProfileResponse>('/auth/profile');
  },

  updateProfile: async (updates: Partial<User>): Promise<ProfileResponse> => {
    return apiRequest<ProfileResponse>('/auth/profile', {
      method: 'PUT',
      body: JSON.stringify(updates),
    });
  },

  uploadAvatar: async (file: File): Promise<{ success: boolean; data: { avatarUrl: string } }> => {
    const token = getToken();
    const headers: Record<string, string> = token ? { Authorization: `Bearer ${token}` } : {};
    const form = new FormData();
    form.append('file', file);
    const res = await fetch(`${API_BASE_URL}/auth/profile/avatar`, {
      method: 'POST',
      headers,
      body: form,
    });
    const data = await res.json();
    if (!res.ok || !data.success) throw new Error(data?.message || 'Lỗi tải ảnh lên');
    return data;
  },
};

export interface ChatRequestPayload {
  message: string;
  sessionId?: string;
  intent?: string;
  speak?: boolean;
}

export interface ChatResponsePayload {
  success: boolean;
  data: {
    sessionId?: string | null;
    response: string;
    analysis?: unknown;
    toolResults?: unknown;
    latencyMs?: number;
    audio?: { mimeType: string; base64: string };
  };
  warnings?: string[];
  message?: string;
}

export interface ChatSessionSummary {
  sessionId: string;
  summary: string;
  createdAt?: string | null;
}

export interface ChatSessionsResponse {
  success: boolean;
  data: {
    sessions: ChatSessionSummary[];
  };
}

export interface ChatSessionMessagesResponse {
  success: boolean;
  data: {
    sessionId: string;
    messages: Array<{
      role: 'user' | 'assistant';
      content: string;
      timestamp?: string | null;
    }>;
  };
}

export type StreamEvent =
  | { type: 'start' }
  | { type: 'session'; sessionId: string }
  | { type: 'chunk'; text: string }
  | { type: 'done'; sessionId: string; latencyMs: number }
  | { type: 'error'; message: string };

export async function* streamChatMessage(payload: ChatRequestPayload): AsyncGenerator<StreamEvent> {
  const token = getToken();
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };

  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}/rag/chat/stream`, {
      method: 'POST',
      headers,
      body: JSON.stringify(payload),
    });
  } catch {
    yield { type: 'error', message: 'Không thể kết nối đến server.' };
    return;
  }

  if (!response.ok || !response.body) {
    yield { type: 'error', message: `Lỗi ${response.status}: ${response.statusText}` };
    return;
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split('\n');
    buffer = lines.pop() ?? '';
    for (const line of lines) {
      if (!line.startsWith('data: ')) continue;
      try {
        yield JSON.parse(line.slice(6)) as StreamEvent;
      } catch { /* skip malformed */ }
    }
  }
}

export const chatbotAPI = {
  sendMessage: async (payload: ChatRequestPayload): Promise<ChatResponsePayload> => {
    return apiRequest<ChatResponsePayload>('/rag/chat', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  getRecentSessions: async (limit = 5): Promise<ChatSessionsResponse> => {
    const params = new URLSearchParams({ limit: String(limit) });
    return apiRequest<ChatSessionsResponse>(`/rag/sessions?${params.toString()}`);
  },

  getSessionMessages: async (sessionId: string): Promise<ChatSessionMessagesResponse> => {
    return apiRequest<ChatSessionMessagesResponse>(`/rag/sessions/${encodeURIComponent(sessionId)}`);
  },

  suggestProcedure: async (
    query: string,
    options?: { topK?: number; threshold?: number; sessionId?: string }
  ): Promise<{
    success: boolean;
    data?: {
      suggestions: Array<{
        procedure_internal_id: number;
        procedure_name: string;
        procedure_code?: string | null;
        label?: number | null;
        similarity_score: number;
        source?: string;
        link?: string;
      }>;
      explanation: string;
      totalCandidates: number;
      latencyMs: number;
      sessionId?: string;
    };
    message?: string;
    error?: string;
  }> => {
    return apiRequest('/suggest-procedure', {
      method: 'POST',
      body: JSON.stringify({
        query,
        topK: options?.topK ?? 4,
        threshold: options?.threshold ?? 0.5,
        sessionId: options?.sessionId,
      }),
    });
  },
};

function _voiceHeaders(): Record<string, string> {
  const token = getToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

// Voice API
export const voiceAPI = {
  stt: async (blob: Blob): Promise<{ status: string; text?: string; message?: string }> => {
    const form = new FormData();
    form.append('file', blob, 'audio.webm');
    const res = await fetchWithFallback(`${API_BASE_URL}/voice/stt`,
      { method: 'POST', headers: _voiceHeaders(), body: form as any });
    const data = await res.json();
    if (!res.ok) throw new Error(data?.message || 'STT error');
    return data;
  },

  tts: async (text: string): Promise<Blob> => {
    const headers = { 'Content-Type': 'application/json', ..._voiceHeaders() };
    const res = await fetchWithFallback(`${API_BASE_URL}/voice/tts`,
      { method: 'POST', headers, body: JSON.stringify({ text }) });
    if (!res.ok) throw new Error((await res.text()) || 'TTS error');
    return res.blob();
  },

  autoCreate: async (text: string, phone?: string, sessionId?: string): Promise<{
    status: string; message: string; next?: string;
    state?: any; suggestedSlots?: string[]; appointment?: any;
  }> => {
    const headers = { 'Content-Type': 'application/json', ..._voiceHeaders() };
    const res = await fetchWithFallback(`${API_BASE_URL}/voice/appointments/auto-create`,
      { method: 'POST', headers, body: JSON.stringify({ text, phone, sessionId }) });
    const data = await res.json();
    if (!res.ok) throw new Error(data?.message || 'Voice booking error');
    return data;
  },

  dialog: async (text: string, sessionId?: string, phone?: string, speak = true): Promise<{
    reply: string; step: string; done: boolean; state: any;
    appointment?: any; audio?: { mimeType: string; base64: string };
  }> => {
    const headers = { 'Content-Type': 'application/json', ..._voiceHeaders() };
    const body = JSON.stringify({ text, sessionId, phone, speak });
    const res = await fetchWithFallback(`${API_BASE_URL}/voice/dialog`, { method: 'POST', headers, body });
    const data = await res.json();
    if (!res.ok) throw new Error(data?.reply || data?.message || 'Voice dialog error');
    return data;
  },
};
