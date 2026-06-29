/**
 * Forecast Service — dự báo cao điểm hàng chờ (weekly heatmap + short-term forecast)
 * Uses the shared apiRequest helper from ./api (inherits auth, primary→fallback URL logic).
 * API_BASE_URL already includes /api, so endpoints here are /queue/forecast…
 */
import { apiRequest } from './api';

export type ForecastLevel = 'low' | 'medium' | 'high';

export interface WeeklyProfileCell {
  weekday: number; // 0 = Mon .. 6 = Sun
  hour: number;    // 7..17
  avg: number;
  level: ForecastLevel;
  peak: boolean;
}

export interface ShortTermForecastItem {
  time: string; // ISO 'YYYY-MM-DDTHH'
  count: number;
  level: ForecastLevel;
  peak: boolean;
}

export interface ShortTermWarning {
  time: string;
  level: ForecastLevel;
}

export interface WeeklyForecastResponse {
  success?: boolean;
  agency?: string;
  profile: WeeklyProfileCell[];
  peakHours: WeeklyProfileCell[];
}

export interface ShortTermForecastResponse {
  success?: boolean;
  agency?: string;
  source: 'lstm' | 'stats';
  forecast: ShortTermForecastItem[];
  warnings: ShortTermWarning[];
}

/** GET /queue/forecast/weekly?agency=<id> */
export async function weekly(agency: string): Promise<WeeklyForecastResponse> {
  try {
    const res = await apiRequest<WeeklyForecastResponse>(
      `/queue/forecast/weekly?agency=${encodeURIComponent(agency)}`
    );
    return {
      ...res,
      profile: res.profile ?? [],
      peakHours: res.peakHours ?? [],
    };
  } catch {
    return { profile: [], peakHours: [] };
  }
}

/** GET /queue/forecast?agency=<id>&hours=<N> */
export async function shortTerm(agency: string, hours = 8): Promise<ShortTermForecastResponse> {
  try {
    const res = await apiRequest<ShortTermForecastResponse>(
      `/queue/forecast?agency=${encodeURIComponent(agency)}&hours=${encodeURIComponent(String(hours))}`
    );
    return {
      ...res,
      source: res.source ?? 'stats',
      forecast: res.forecast ?? [],
      warnings: res.warnings ?? [],
    };
  } catch {
    return { source: 'stats', forecast: [], warnings: [] };
  }
}
