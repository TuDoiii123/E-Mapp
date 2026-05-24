/**
 * AdminShell — Khung giao diện admin
 * Bottom navigation 5 tab (không có header)
 */
import React, { useState } from 'react';
import {
  LayoutDashboard, FolderOpen, CalendarDays, Users, Settings,
} from 'lucide-react';
import { AdminDashboardScreen }      from './AdminDashboardScreen';
import { AdminApplicationsScreen }   from './AdminApplicationsScreen';
import { AdminAppointmentsScreen }   from './AdminAppointmentsScreen';
import { AdminUsersScreen }          from './AdminUsersScreen';
import { AdminSystemScreen }         from './AdminSystemScreen';

interface Props { onNavigate: (screen: string, params?: any) => void }

type AdminTab = 'dashboard' | 'applications' | 'appointments' | 'users' | 'system';

const TABS: { key: AdminTab; label: string; Icon: any }[] = [
  { key: 'dashboard',    label: 'Tổng quan',  Icon: LayoutDashboard },
  { key: 'applications', label: 'Hồ sơ',      Icon: FolderOpen      },
  { key: 'appointments', label: 'Lịch hẹn',   Icon: CalendarDays    },
  { key: 'users',        label: 'Thành viên',  Icon: Users           },
  { key: 'system',       label: 'Hệ thống',   Icon: Settings        },
];

export function AdminShell({ onNavigate }: Props) {
  const [activeTab, setActiveTab] = useState<AdminTab>('dashboard');

  return (
    <div className="min-h-screen bg-[#fff4f4] flex flex-col">

      {/* ── Content ────────────────────────────────────────────────────────── */}
      <div className="flex-1 overflow-y-auto pb-20 pt-10">
        {activeTab === 'dashboard'    && <AdminDashboardScreen    onNavigate={onNavigate} hideHeader />}
        {activeTab === 'applications' && <AdminApplicationsScreen onNavigate={onNavigate} />}
        {activeTab === 'appointments' && <AdminAppointmentsScreen onNavigate={onNavigate} />}
        {activeTab === 'users'        && <AdminUsersScreen        onNavigate={onNavigate} />}
        {activeTab === 'system'       && <AdminSystemScreen       onNavigate={onNavigate} />}
      </div>

      {/* ── Bottom Nav ─────────────────────────────────────────────────────── */}
      <nav className="fixed bottom-0 inset-x-0 bg-white border-t border-[#de9ca4]/20 flex z-40
        shadow-[0_-1px_8px_rgba(143,0,13,0.06)]">
        {TABS.map(({ key, label, Icon }) => {
          const active = activeTab === key;
          return (
            <button
              key={key}
              onClick={() => setActiveTab(key)}
              className={`relative flex-1 flex flex-col items-center justify-center py-2.5 gap-0.5 transition-colors
                ${active ? 'text-red-700' : 'text-[#9f364c]/40 hover:text-[#9f364c]'}`}
            >
              {active && (
                <span className="absolute top-0 inset-x-0 h-0.5 bg-red-700 rounded-full" />
              )}
              <Icon className={`w-5 h-5 ${active ? 'scale-110' : ''} transition-transform`} />
              <span className="text-[9px] font-medium leading-none">{label}</span>
            </button>
          );
        })}
      </nav>
    </div>
  );
}
