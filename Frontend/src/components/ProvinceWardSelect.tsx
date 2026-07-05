import React, { useEffect, useState } from 'react';
import { adminDivisionsAPI, AdminDivision } from '../services/adminDivisionsApi';

export interface ProvinceWardValue {
  provinceCode: string;
  provinceName: string;
  wardCode: string;
  wardName: string;
}

interface Props {
  value: ProvinceWardValue;
  onChange: (v: ProvinceWardValue) => void;
  required?: boolean;
  disabled?: boolean;
  className?: string;
  labels?: { province?: string; ward?: string };
}

const EMPTY: ProvinceWardValue = { provinceCode: '', provinceName: '', wardCode: '', wardName: '' };

const selectCls =
  'w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm ' +
  'focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 ' +
  'disabled:cursor-not-allowed disabled:bg-gray-100';

/**
 * Chọn Tỉnh/Thành → Xã/Phường (mô hình hành chính 2025). Hai select phụ thuộc:
 * đổi tỉnh sẽ nạp lại danh sách xã và reset xã đang chọn.
 */
export default function ProvinceWardSelect({
  value, onChange, required, disabled, className, labels,
}: Props) {
  const [provinces, setProvinces] = useState<AdminDivision[]>([]);
  const [wards, setWards] = useState<AdminDivision[]>([]);
  const [loadingWards, setLoadingWards] = useState(false);

  // Nạp tỉnh 1 lần
  useEffect(() => {
    adminDivisionsAPI.provinces().then(setProvinces).catch(() => setProvinces([]));
  }, []);

  // Nạp xã mỗi khi đổi tỉnh
  useEffect(() => {
    if (!value.provinceCode) { setWards([]); return; }
    setLoadingWards(true);
    adminDivisionsAPI.wards(value.provinceCode)
      .then(setWards)
      .catch(() => setWards([]))
      .finally(() => setLoadingWards(false));
  }, [value.provinceCode]);

  const onProvince = (code: string) => {
    const p = provinces.find((x) => x.code === code);
    // đổi tỉnh → reset xã
    onChange({ ...EMPTY, provinceCode: code, provinceName: p?.name || '' });
  };

  const onWard = (code: string) => {
    const w = wards.find((x) => x.code === code);
    onChange({ ...value, wardCode: code, wardName: w?.name || '' });
  };

  return (
    <div className={`grid grid-cols-1 gap-3 sm:grid-cols-2 ${className || ''}`}>
      <div>
        <label className="mb-1 block text-sm font-medium text-gray-700">
          {labels?.province || 'Tỉnh / Thành phố'}{required && <span className="text-red-500"> *</span>}
        </label>
        <select
          className={selectCls}
          value={value.provinceCode}
          disabled={disabled}
          required={required}
          onChange={(e) => onProvince(e.target.value)}
        >
          <option value="">-- Chọn tỉnh/thành --</option>
          {provinces.map((p) => (
            <option key={p.code} value={p.code}>{p.name}</option>
          ))}
        </select>
      </div>

      <div>
        <label className="mb-1 block text-sm font-medium text-gray-700">
          {labels?.ward || 'Xã / Phường'}{required && <span className="text-red-500"> *</span>}
        </label>
        <select
          className={selectCls}
          value={value.wardCode}
          disabled={disabled || !value.provinceCode || loadingWards}
          required={required}
          onChange={(e) => onWard(e.target.value)}
        >
          <option value="">
            {!value.provinceCode ? '-- Chọn tỉnh trước --' : loadingWards ? 'Đang tải...' : '-- Chọn xã/phường --'}
          </option>
          {wards.map((w) => (
            <option key={w.code} value={w.code}>{w.name}</option>
          ))}
        </select>
      </div>
    </div>
  );
}
