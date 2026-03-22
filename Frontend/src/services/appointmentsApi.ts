import { apiRequest } from './api';

export interface CreateAppointmentRequest {
  agencyId: string;
  serviceCode: string;
  date: string; // YYYY-MM-DD
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

export const appointmentsAPI = {
  create: (payload: CreateAppointmentRequest) =>
    apiRequest<ApiResponse<Appointment>>('/appointments', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  getByDate: (agencyId: string, date: string) => {
    const params = new URLSearchParams({ agencyId, date });
    return apiRequest<ApiResponse<{ appointments: Appointment[] }>>(`/appointments/by-date?${params}`);
  },

  getAll: () =>
    apiRequest<ApiResponse<{ appointments: Appointment[] }>>('/appointments/all'),

  getUpcoming: () =>
    apiRequest<ApiResponse<{ appointments: Appointment[] }>>('/appointments/upcoming'),
};
