/**
 * AdminShell — Khung giao diện admin
 * Header tối + bottom navigation 5 tab
 * Tự động render trang tương ứng theo tab đang chọn
 */
import React, { useState } from 'react';
import {
  FolderKanban, BarChart3, Hash, Star, Settings, LogOut, Shield, Users, FolderOpen, CalendarDays,
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { AdminDashboardScreen }         from './AdminDashboardScreen';
import { AdminAnalyticsScreen }          from './AdminAnalyticsScreen';
import { AdminQueueManagementScreen }    from './AdminQueueManagementScreen';
import { AdminEvaluationsScreen }        from './AdminEvaluationsScreen';
import { AdminSystemScreen }             from './AdminSystemScreen';
import { AdminUsersScreen }              from './AdminUsersScreen';
import { AdminApplicationsScreen }       from './AdminApplicationsScreen';
import { AdminAppointmentsScreen }       from './AdminAppointmentsScreen';

interface Props { onNavigate: (screen: string, params?: any) => void }

type AdminTab = 'manage' | 'applications' | 'appointments' | 'users' | 'analytics' | 'queue' | 'evaluations' | 'system';

const TABS: { key: AdminTab; label: string; Icon: any }[] = [
  { key: 'manage',       label: 'Quản lý',  Icon: FolderKanban  },
  { key: 'applications', label: 'Hồ sơ',    Icon: FolderOpen    },
  { key: 'appointments', label: 'Lịch hẹn', Icon: CalendarDays  },
  { key: 'users',        label: 'Thành viên', Icon: Users       },
  { key: 'analytics',   label: 'Phân tích',  Icon: BarChart3    },
  { key: 'queue',       label: 'Hàng đợi',   Icon: Hash         },
  { key: 'evaluations', label: 'Đánh giá',   Icon: Star         },
  { key: 'system',      label: 'Hệ thống',   Icon: Settings     },
];

export function AdminShell({ onNavigate }: Props) {
  const [activeTab, setActiveTab] = useState<AdminTab>('manage');
  const { user } = useAuth();

  const handleLogout = () => onNavigate('login');

  return (
    <div className="min-h-screen bg-[#fff4f4] flex flex-col">

      {/* ── Admin Header ───────────────────────────────────────────────────── */}
      <div className="bg-[#1c0003] text-white px-4 pt-10 pb-3 flex items-center justify-between flex-shrink-0 z-10">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 bg-red-600 rounded-lg flex items-center justify-center flex-shrink-0">
            <Shield className="w-4 h-4" />
          </div>
          <div>
            <h1 className="text-sm font-bold leading-tight">Quản trị E-Mapp</h1>
            <p className="text-[10px] text-gray-400 leading-tight">
              {user?.fullName ?? 'Admin'} · {user?.role ?? 'admin'}
            </p>
          </div>
        </div>
        <button
          onClick={handleLogout}
          className="text-gray-400 hover:text-white p-2 rounded-lg hover:bg-gray-700 transition-colors"
          title="Đăng xuất"
        >
          <LogOut className="w-4 h-4" />
        </button>
      </div>

      {/* ── Tab Content ────────────────────────────────────────────────────── */}
      <div className="flex-1 overflow-y-auto pb-20">
        {activeTab === 'manage'       && (
          <AdminDashboardScreen onNavigate={onNavigate} hideHeader />
        )}
        {activeTab === 'applications' && (
          <AdminApplicationsScreen onNavigate={onNavigate} />
        )}
        {activeTab === 'appointments' && (
          <AdminAppointmentsScreen onNavigate={onNavigate} />
        )}
        {activeTab === 'users'        && (
          <AdminUsersScreen onNavigate={onNavigate} />
        )}
        {activeTab === 'analytics'   && (
          <AdminAnalyticsScreen onNavigate={onNavigate} />
        )}
        {activeTab === 'queue'       && (
          <AdminQueueManagementScreen onNavigate={onNavigate} />
        )}
        {activeTab === 'evaluations' && (
          <AdminEvaluationsScreen onNavigate={onNavigate} />
        )}
        {activeTab === 'system'      && (
          <AdminSystemScreen onNavigate={onNavigate} />
        )}
      </div>

      {/* ── Bottom Navigation ──────────────────────────────────────────────── */}
      <nav className="fixed bottom-0 inset-x-0 bg-white border-t border-[#de9ca4]/20 flex z-40
        safe-area-inset-bottom shadow-[0_-1px_8px_rgba(143,0,13,0.06)]">
        {TABS.map(({ key, label, Icon }) => {
          const active = activeTab === key;
          return (
            <button
              key={key}
              onClick={() => setActiveTab(key)}
              className={`flex-1 flex flex-col items-center justify-center py-2.5 gap-0.5 transition-colors
                ${active ? 'text-red-700' : 'text-[#9f364c]/50 hover:text-[#9f364c]'}`}
            >
              <Icon className={`w-5 h-5 transition-transform ${active ? 'scale-110' : ''}`} />
              <span className={`text-[9px] font-medium leading-none ${active ? 'text-red-700' : ''}`}>
                {label}
              </span>
              {active && (
                <span className="absolute top-0 w-8 h-0.5 bg-red-700 rounded-full" />
              )}
            </button>
          );
        })}
      </nav>
    </div>
  );
}
