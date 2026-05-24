import React, { useState, useCallback } from 'react';
import { LocationsTab, Toast } from './AdminDashboardScreen';

interface Props { onNavigate: (screen: string, params?: any) => void }

export function AdminLocationsScreen({ onNavigate }: Props) {
  const [toast, setToast] = useState<{ msg: string; ok: boolean } | null>(null);

  const showToast = useCallback((msg: string, ok: boolean) => {
    setToast({ msg, ok });
    setTimeout(() => setToast(null), 3000);
  }, []);

  return (
    <div className="min-h-full pb-6">
      {toast && <Toast text={toast.msg} ok={toast.ok} />}

      {/* Header */}
      <div className="px-4 pt-4 pb-3">
        <h2 className="text-lg font-bold text-[#1c0003]">Địa điểm</h2>
        <p className="text-xs text-[#9f364c]/60 mt-0.5">Quản lý cơ quan hành chính</p>
      </div>

      <LocationsTab onToast={showToast} />
    </div>
  );
}
