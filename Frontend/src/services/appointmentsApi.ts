const API_BASE_URL = (import.meta as any).env?.VITE_API_URL || 'http://localhost:8888/api';
const API_BASE_URL_FALLBACK = 'http://localhost:8888/api';

export interface CreateAppointmentRequest {
  agencyId: string;
  serviceCode: string;
  date: string; // ISO date: YYYY-MM-DD
  time: string; // HH:mm
  fullName: string;
  phone: string;
  info?: string;
}

export interface Appointment {
  id: string;
  userId: string;
  agencyId: string;
  serviceCode: string;
  date: string;
  time: string;
  status: 'pending' | 'completed' | 'cancelled';
  fullName?: string;
  phone?: string;
  info?: string;
}

export interface ApiResponse<T> {
  success: boolean;
  message: string;
  data: T;
}

async function apiRequest<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  let response: Response;
  let data: any;

  try {
    response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });
    data = await response.json();
  } catch (error: any) {
    if (API_BASE_URL !== API_BASE_URL_FALLBACK) {
      try {
        response = await fetch(`${API_BASE_URL_FALLBACK}${endpoint}`, {
          ...options,
          headers: {
            'Content-Type': 'application/json',
            ...options.headers,
          },
        });
        data = await response.json();
      } catch (fallbackError: any) {
        throw new Error(`Không thể kết nối đến server: ${error.message}`);
      }
    } else {
      throw new Error(`Không thể kết nối đến server: ${error.message}`);
    }
  }

  if (!response.ok) {
    throw new Error(data?.message || `Lỗi ${response.status}`);
  }

  return data as T;
}

export const appointmentsAPI = {
  create: async (payload: CreateAppointmentRequest): Promise<ApiResponse<Appointment>> => {
    return await apiRequest<ApiResponse<Appointment>>('/appointments', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },
  getByDate: async (agencyId: string, date: string): Promise<ApiResponse<{ appointments: Appointment[] }>> => {
    const params = new URLSearchParams({ agencyId, date });
    return await apiRequest<ApiResponse<{ appointments: Appointment[] }>>(`/appointments/by-date?${params.toString()}`);
  },
  getAll: async (): Promise<ApiResponse<{ appointments: Appointment[] }>> => {
    return await apiRequest<ApiResponse<{ appointments: Appointment[] }>>('/appointments/all');
  },
  getUpcoming: async (): Promise<ApiResponse<{ appointments: Appointment[] }>> => {
    return await apiRequest<ApiResponse<{ appointments: Appointment[] }>>('/appointments/upcoming');
  },
};
