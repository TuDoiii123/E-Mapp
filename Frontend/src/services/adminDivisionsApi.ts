import { apiRequest } from './api';

// Danh mục hành chính VN (mô hình 2025: tỉnh → xã, bỏ cấp huyện).
export interface AdminDivision {
  code: string;
  name: string;
  fullName: string;
}

export const adminDivisionsAPI = {
  /** 34 tỉnh/thành, đã sắp theo tên. */
  async provinces(): Promise<AdminDivision[]> {
    const res = await apiRequest<{ success: boolean; data: AdminDivision[] }>(
      '/admin-divisions/provinces'
    );
    return res.data || [];
  },

  /** Xã/phường theo mã tỉnh. */
  async wards(provinceCode: string): Promise<AdminDivision[]> {
    if (!provinceCode) return [];
    const res = await apiRequest<{ success: boolean; data: AdminDivision[] }>(
      `/admin-divisions/wards?province_code=${encodeURIComponent(provinceCode)}`
    );
    return res.data || [];
  },
};
