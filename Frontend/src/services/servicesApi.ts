const API_BASE_URL = (import.meta as any).env?.VITE_API_URL || 'http://localhost:8888/api';
const API_BASE_URL_FALLBACK = 'http://localhost:8888/api';

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
    userLocation: {
      latitude: number;
      longitude: number;
    };
    radius: number;
  };
}

export interface SearchServicesResponse {
  success: boolean;
  data: {
    services: PublicService[];
    total: number;
    query: string;
    filters: {
      category?: string;
      level?: string;
      province?: string;
      district?: string;
    };
  };
}

export interface ServiceDetailResponse {
  success: boolean;
  data: {
    service: PublicService & {
      category?: ServiceCategory;
    };
  };
}

// API request helper
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
    throw new Error(data.message || `Lỗi ${response.status}`);
  }

  return data;
}

export const servicesAPI = {
  // Get nearby services
  getNearby: async (
    lat: number,
    lng: number,
    radius: number = 10,
    category?: string,
    level?: string
  ): Promise<NearbyServicesResponse> => {
    const params = new URLSearchParams({
      lat: lat.toString(),
      lng: lng.toString(),
      radius: radius.toString(),
    });
    if (category) params.append('category', category);
    if (level) params.append('level', level);

    return await apiRequest<NearbyServicesResponse>(`/services/nearby?${params}`);
  },

  // Search services
  search: async (
    query?: string,
    category?: string,
    level?: string,
    province?: string,
    district?: string,
    lat?: number,
    lng?: number
  ): Promise<SearchServicesResponse> => {
    const params = new URLSearchParams();
    if (query) params.append('q', query);
    if (category) params.append('category', category);
    if (level) params.append('level', level);
    if (province) params.append('province', province);
    if (district) params.append('district', district);
    if (lat && lng) {
      params.append('lat', lat.toString());
      params.append('lng', lng.toString());
    }

    return await apiRequest<SearchServicesResponse>(`/services/search?${params}`);
  },

  // Get service detail
  getById: async (id: string, lat?: number, lng?: number): Promise<ServiceDetailResponse> => {
    const params = new URLSearchParams();
    if (lat && lng) {
      params.append('lat', lat.toString());
      params.append('lng', lng.toString());
    }
    const queryString = params.toString() ? `?${params}` : '';
    return await apiRequest<ServiceDetailResponse>(`/services/${id}${queryString}`);
  },

  // Get all services
  getAll: async (
    category?: string,
    level?: string,
    province?: string,
    lat?: number,
    lng?: number,
    limit: number = 100
  ): Promise<{ success: boolean; data: { services: PublicService[]; total: number } }> => {
    const params = new URLSearchParams({ limit: limit.toString() });
    if (category) params.append('category', category);
    if (level) params.append('level', level);
    if (province) params.append('province', province);
    if (lat && lng) {
      params.append('lat', lat.toString());
      params.append('lng', lng.toString());
    }

    return await apiRequest(`/services?${params}`);
  },

  // Get categories
  getCategories: async (): Promise<{ success: boolean; data: { categories: ServiceCategory[] } }> => {
    return await apiRequest('/services/categories/list');
  },

  // Get popular services
  getPopular: async (level?: string, limit: number = 10): Promise<{
    success: boolean;
    data: { services: PublicService[]; level: string };
  }> => {
    const params = new URLSearchParams({ limit: limit.toString() });
    if (level) params.append('level', level);
    return await apiRequest(`/services/popular?${params}`);
  },
};

