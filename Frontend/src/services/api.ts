// Provide type declarations for Vite's import.meta.env so TypeScript recognizes it
declare global {
  interface ImportMetaEnv {
    readonly VITE_API_URL?: string;
  }
  interface ImportMeta {
    readonly env: ImportMetaEnv;
  }
}

// Try to use the configured IP, fallback to localhost for development
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8888/api';
export const API_BASE_URL_FALLBACK = 'http://localhost:8888/api';

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

// API request helper with fallback
async function apiRequest<T>(
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
    // Try primary URL first
    response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers,
    });
    data = await response.json();
  } catch (error: any) {
    // If primary URL fails, try fallback (localhost)
    if (API_BASE_URL !== API_BASE_URL_FALLBACK) {
      try {
        console.warn(`Primary API URL failed, trying fallback: ${API_BASE_URL_FALLBACK}`);
        response = await fetch(`${API_BASE_URL_FALLBACK}${endpoint}`, {
          ...options,
          headers,
        });
        data = await response.json();
      } catch (fallbackError: any) {
        throw new Error(
          `Không thể kết nối đến server. Vui lòng kiểm tra:\n` +
          `1. Backend server đã chạy chưa?\n` +
          `2. Đã cài đặt dependencies: cd Backend && npm install\n` +
          `3. Server đang chạy trên port 8888?\n\n` +
          `Lỗi: ${error.message || 'Network error'}`
        );
      }
    } else {
      throw new Error(
        `Không thể kết nối đến server. Vui lòng kiểm tra:\n` +
        `1. Backend server đã chạy chưa?\n` +
        `2. Đã cài đặt dependencies: cd Backend && npm install\n` +
        `3. Server đang chạy trên port 8888?\n\n` +
        `Lỗi: ${error.message || 'Network error'}`
      );
    }
  }

  if (!response.ok) {
    throw new Error(data.message || data.error || `Lỗi ${response.status}: ${response.statusText}`);
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
      await apiRequest('/auth/logout', {
        method: 'POST',
      });
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      removeToken();
    }
    return { success: true, message: 'Đăng xuất thành công' };
  },

  getProfile: async (): Promise<ProfileResponse> => {
    // Temporarily disabled. Callers should avoid using this until re-enabled.
    return Promise.reject(new Error('getProfile temporarily disabled'));
  },

  updateProfile: async (updates: Partial<User>): Promise<ProfileResponse> => {
    return Promise.reject(new Error('updateProfile temporarily disabled'));
  },
};

export interface ChatRequestPayload {
  message: string;
  sessionId?: string;
  intent?: string; // optional intent e.g. 'administrative_qa'
  speak?: boolean; // request audio response
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
    data?: { suggestions: Array<{ procedure_internal_id: number; procedure_name: string; procedure_code?: string | null; label?: number | null; similarity_score: number; source?: string; link?: string }>; explanation: string; totalCandidates: number; latencyMs: number; sessionId?: string };
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

// Voice API
export const voiceAPI = {
  stt: async (blob: Blob): Promise<{ status: string; text?: string; message?: string }> => {
    const form = new FormData();
    form.append('file', blob, 'audio.webm');
    const token = getToken();
    const headers: Record<string, string> = token ? { Authorization: `Bearer ${token}` } : {};
    // Try primary then fallback
    let res: Response;
    try {
      res = await fetch(`${API_BASE_URL}/voice/stt`, { method: 'POST', headers, body: form as any });
    } catch {
      res = await fetch(`${API_BASE_URL_FALLBACK}/voice/stt`, { method: 'POST', headers, body: form as any });
    }
    const data = await res.json();
    if (!res.ok) throw new Error(data?.message || 'STT error');
    return data;
  },

  tts: async (text: string): Promise<Blob> => {
    const token = getToken();
    const headers: Record<string, string> = { 'Content-Type': 'application/json' };
    if (token) headers['Authorization'] = `Bearer ${token}`;
    let res: Response;
    try {
      res = await fetch(`${API_BASE_URL}/voice/tts`, { method: 'POST', headers, body: JSON.stringify({ text }) });
    } catch {
      res = await fetch(`${API_BASE_URL_FALLBACK}/voice/tts`, { method: 'POST', headers, body: JSON.stringify({ text }) });
    }
    if (!res.ok) {
      const msg = await res.text();
      throw new Error(msg || 'TTS error');
    }
    return await res.blob();
  },

  autoCreate: async (text: string, phone?: string): Promise<{ status: string; message: string; missing?: string[]; appointment?: any }> => {
    const token = getToken();
    const headers: Record<string, string> = { 'Content-Type': 'application/json' };
    if (token) headers['Authorization'] = `Bearer ${token}`;
    let res: Response;
    const body = JSON.stringify({ text, phone });
    try {
      res = await fetch(`${API_BASE_URL}/voice/appointments/auto-create`, { method: 'POST', headers, body });
    } catch {
      res = await fetch(`${API_BASE_URL_FALLBACK}/voice/appointments/auto-create`, { method: 'POST', headers, body });
    }
    const data = await res.json();
    if (!res.ok) throw new Error(data?.message || 'Voice booking error');
    return data;
  },
};

