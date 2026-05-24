import { apiRequest } from './api';

// ── Types ─────────────────────────────────────────────────────────────────────

export interface MapConfig {
  defaultCenter: { lat: number; lng: number };
  defaultZoom: number;
  tileUrl: string;
  attribution: string;
  maxZoom: number;
  region: string;
  language: string;
}

export interface GeocodeResult {
  lat: number;
  lng: number;
  formattedAddress: string;
  placeId: string;
  ward?: string;
  district?: string;
  province?: string;
}

export interface ReverseGeocodeResult {
  formattedAddress: string;
  ward: string;
  district: string;
  province: string;
  placeId: string;
}

export interface AutocompletePrediction {
  placeId: string;
  description: string;
  mainText: string;
  secondaryText: string;
  lat: number;
  lng: number;
}

export interface PlaceDetail {
  name: string;
  formattedAddress: string;
  lat: number | null;
  lng: number | null;
  phone: string;
  website: string;
  rating: number | null;
  openNow: boolean | null;
  weekdayText: string[];
}

export interface RouteStep {
  instruction:  string;
  iconType:     'depart' | 'arrive' | 'turn-left' | 'turn-right' |
                'slight-left' | 'slight-right' | 'straight' | 'uturn' | 'roundabout';
  roadName:     string;
  distance:     string;
  distanceM:    number;
  duration:     string;
  location:     [number, number] | null;   // [lat, lng]
  maneuverType: string;
  modifier:     string;
  bearingAfter: number;
}

export interface DirectionsResult {
  distance: { text: string; meters: number | null };
  duration: { text: string; seconds: number | null };
  summary: string;
  osmUrl: string;
  googleMapsUrl: string;
  coordinates?: [number, number][];
  steps?: RouteStep[];
  note?: string;
}

export interface SmartRecommendation {
  rank:    number;
  tag:     'recommended' | 'nearest' | 'least_busy' | null;
  reason:  string;
  score:   number;
  agency: {
    id: string; name: string; address: string;
    phone: string; latitude: number | null; longitude: number | null; status: string;
  };
  distance: { text: string; km: number };
  duration: { text: string; minutes: number };
  queue: {
    waiting: number; serving: number; loadLevel: string;
    estWaitMin: number; estWaitText: string;
  };
  navigation: { osmUrl: string; googleMapsUrl: string };
}

export interface SmartRouteResponse {
  success: boolean;
  data: {
    recommendations: SmartRecommendation[];
    total: number;
    message?: string;
    searchParams: { lat: number; lng: number; serviceId: string | null; radius: number; mode: string };
  };
}

// ── API ───────────────────────────────────────────────────────────────────────

export const mapAPI = {
  getConfig: () =>
    apiRequest<{ success: boolean; data: MapConfig }>('/map/config'),

  geocode: (address: string) =>
    apiRequest<{ success: boolean; data: GeocodeResult }>(
      `/map/geocode?${new URLSearchParams({ address })}`,
    ),

  reverseGeocode: (lat: number, lng: number) =>
    apiRequest<{ success: boolean; data: ReverseGeocodeResult }>(
      `/map/reverse-geocode?lat=${lat}&lng=${lng}`,
    ),

  autocomplete: (input: string, lat?: number, lng?: number) => {
    const p: Record<string, string> = { input };
    if (lat != null && lng != null) { p.lat = String(lat); p.lng = String(lng); }
    return apiRequest<{ success: boolean; data: { predictions: AutocompletePrediction[] } }>(
      `/map/autocomplete?${new URLSearchParams(p)}`,
    );
  },

  getPlace: (placeId: string) =>
    apiRequest<{ success: boolean; data: PlaceDetail }>(
      `/map/place?${new URLSearchParams({ place_id: placeId })}`,
    ),

  getDirections: (
    origin: { lat: number; lng: number },
    dest: { lat: number; lng: number },
    mode: 'driving' | 'walking' | 'cycling' = 'driving',
  ) => {
    const p = new URLSearchParams({
      olat: String(origin.lat), olng: String(origin.lng),
      dlat: String(dest.lat),   dlng: String(dest.lng),
      mode,
    });
    return apiRequest<{ success: boolean; data: DirectionsResult }>(`/map/directions?${p}`);
  },

  smartRoute: (
    lat: number,
    lng: number,
    serviceId = 'all',
    mode: 'driving' | 'walking' | 'cycling' = 'driving',
    radius = 20,
    limit = 5,
  ) => {
    const p = new URLSearchParams({
      lat: String(lat), lng: String(lng),
      serviceId, mode,
      radius: String(radius),
      limit:  String(limit),
    });
    return apiRequest<SmartRouteResponse>(`/map/smart-route?${p}`);
  },
};
