import { apiRequest } from './api';

export interface ServiceCategory {
  id: string;
  name: string;
  nameEn: string;
  code: string;
  description: string;
  icon: string;
}

export interface PublicService {
  id: string;
  name: string;
  description: string;
  categoryId: string;
  address: string;
  latitude: number;
  longitude: number;
  phone: string;
  email: string;
  website: string;
  workingHours: {
    monday: string;
    tuesday: string;
    wednesday: string;
    thursday: string;
    friday: string;
    saturday: string;
    sunday: string;
  };
  services: string[];
  level: 'ward' | 'district' | 'province';
  rating: number;
  status: 'normal' | 'busy' | 'available';
  distance?: number;
}

export interface NearbyServicesResponse {
  success: boolean;
  data: {
    services: PublicService[];
    total: number;
    userLocation: { latitude: number; longitude: number };
    radius: number;
  };
}

export interface SearchServicesResponse {
  success: boolean;
  data: {
    services: PublicService[];
    total: number;
    query: string;
    filters: { category?: string; level?: string; province?: string; district?: string };
  };
}

export interface ServiceDetailResponse {
  success: boolean;
  data: {
    service: PublicService & { category?: ServiceCategory };
  };
}

export const servicesAPI = {
  getNearby: (lat: number, lng: number, radius = 10, category?: string, level?: string) => {
    const params = new URLSearchParams({ lat: String(lat), lng: String(lng), radius: String(radius) });
    if (category) params.append('category', category);
    if (level) params.append('level', level);
    return apiRequest<NearbyServicesResponse>(`/services/nearby?${params}`);
  },

  search: (query?: string, category?: string, level?: string, province?: string, district?: string, lat?: number, lng?: number) => {
    const params = new URLSearchParams();
    if (query) params.append('q', query);
    if (category) params.append('category', category);
    if (level) params.append('level', level);
    if (province) params.append('province', province);
    if (district) params.append('district', district);
    if (lat && lng) { params.append('lat', String(lat)); params.append('lng', String(lng)); }
    return apiRequest<SearchServicesResponse>(`/services/search?${params}`);
  },

  getById: (id: string, lat?: number, lng?: number) => {
    const params = new URLSearchParams();
    if (lat && lng) { params.append('lat', String(lat)); params.append('lng', String(lng)); }
    const qs = params.toString() ? `?${params}` : '';
    return apiRequest<ServiceDetailResponse>(`/services/${id}${qs}`);
  },

  getAll: (category?: string, level?: string, province?: string, lat?: number, lng?: number, limit = 100) => {
    const params = new URLSearchParams({ limit: String(limit) });
    if (category) params.append('category', category);
    if (level) params.append('level', level);
    if (province) params.append('province', province);
    if (lat && lng) { params.append('lat', String(lat)); params.append('lng', String(lng)); }
    return apiRequest<{ success: boolean; data: { services: PublicService[]; total: number } }>(`/services?${params}`);
  },

  getCategories: () =>
    apiRequest<{ success: boolean; data: { categories: ServiceCategory[] } }>('/services/categories/list'),

  getPopular: (level?: string, limit = 10) => {
    const params = new URLSearchParams({ limit: String(limit) });
    if (level) params.append('level', level);
    return apiRequest<{ success: boolean; data: { services: PublicService[]; level: string } }>(`/services/popular?${params}`);
  },
};
