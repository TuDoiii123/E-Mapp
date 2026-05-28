/**
 * Procedures Service — thủ tục hành chính từ /api/procedures
 */
import { apiRequest } from './api';

export interface Procedure {
  id: string;
  name: string;
  code: string;
  category: string;
  categoryLabel: string;
  icon: string;
  fee: number;
  feeFormatted: string;
  feeNote: string;
  feeColor: boolean;
  processingDays: number;
  processingNote: string;
  timeFormatted: string;
  legalBasis: string[];
  implementingLevel: 'ward' | 'district' | 'province';
  agency: string;
  isOnline: boolean;
  isActive: boolean;
  requirements?: Requirement[];
  requirementCount?: number;
  requiredCount?: number;
  steps?: string[];
  conditions?: string[];
}

export interface Requirement {
  id: string;
  serviceId: string;
  docName: string;
  docDescription: string;
  isRequired: boolean;
  docType: 'original' | 'copy' | 'certified_copy';
  orderIndex: number;
}

export interface ProcedureListResponse {
  success: boolean;
  data: Procedure[];
  total: number;
  source: 'database' | 'fallback';
  pagination: { page: number; limit: number; total: number };
}

export const proceduresAPI = {
  list: (params: { q?: string; category?: string; level?: string; page?: number; limit?: number } = {}) => {
    const p = new URLSearchParams();
    if (params.q)        p.append('q',        params.q);
    if (params.category) p.append('category', params.category);
    if (params.level)    p.append('level',    params.level);
    if (params.page)     p.append('page',     String(params.page));
    if (params.limit)    p.append('limit',    String(params.limit));
    const qs = p.toString() ? `?${p}` : '';
    return apiRequest<ProcedureListResponse>(`/procedures${qs}`);
  },

  get: (id: string) =>
    apiRequest<{ success: boolean; data: Procedure }>(`/procedures/${id}`),

  getRequirements: (id: string) =>
    apiRequest<{ success: boolean; serviceId: string; requirements: Requirement[]; total: number }>(
      `/procedures/${id}/requirements`
    ),
};
