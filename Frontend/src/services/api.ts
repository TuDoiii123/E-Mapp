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
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://192.168.1.231:8888/api';
const API_BASE_URL_FALLBACK = 'http://localhost:8888/api';

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
    return await apiRequest<ProfileResponse>('/auth/profile');
  },

  updateProfile: async (updates: Partial<User>): Promise<ProfileResponse> => {
    return await apiRequest<ProfileResponse>('/auth/profile', {
      method: 'PUT',
      body: JSON.stringify(updates),
    });
  },
};

