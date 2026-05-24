/**
 * AdminShell — Trang chủ quản trị (kiểu HomeScreen)
 * Không có bottom nav — điều hướng qua card grid
 */
import React, { useState, useEffect } from 'react';
import {
  FolderOpen, Users, MapPin, FileText, Bot, Settings,
  ShieldCheck, Bell, TrendingUp, Clock, RefreshCw,
  ChevronLeft, ChevronRight, BarChart3, AlertCircle,
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import * as adminSvc from '../services/adminService';
import { AdminApplicationsScreen }  from './AdminApplicationsScreen';
import { AdminUsersScreen }          from './AdminUsersScreen';
import { AdminLocationsScreen }      from './AdminLocationsScreen';
import { AdminProceduresScreen }     from './AdminProceduresScreen';
import { AdminChatbotScreen }        from './AdminChatbotScreen';
import { AdminSystemScreen }         from './AdminSystemScreen';

interface Props { onNavigate: (screen: string, params?: any) => void }

type AdminPage =
  | 'home'
  | 'applications'
  | 'users'
  | 'locations'
  | 'procedures'
  | 'chatbot'
  | 'system';

const PAGE_META: Record<Exclude<AdminPage, 'home'>, { label: string }> = {
  applications: { label: 'Hồ sơ' },
  users:        { label: 'Thành viên' },
  locations:    { label: 'Địa điểm' },
  procedures:   { label: 'Thủ tục' },
  chatbot:      { label: 'Chatbot AI' },
  system:       { label: 'Hệ thống' },
};

const P = '#8f000d';

/* ── dot pattern (giống HomeScreen) ─────────────────────────────────────── */
const patternStyle: React.CSSProperties = {
  backgroundImage:
    'radial-gradient(#a17d00 0.5px, transparent 0.5px), radial-gradient(#a17d00 0.5px, #8f000d 0.5px)',
  backgroundSize: '20px 20px',
  backgroundPosition: '0 0, 10px 10px',
  opacity: 0.07,
};

/* ═══════════════════════════════════════════════════════════════════════════
   ADMIN HOME VIEW
═══════════════════════════════════════════════════════════════════════════ */
function AdminHomeView({
  onNavigate,
  onGoTo,
}: {
  onNavigate: (s: string, p?: any) => void;
  onGoTo: (p: AdminPage) => void;
}) {
  const { user } = useAuth();
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    adminSvc.getStats()
      .then(r => setStats(r.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const CARDS = [
    {
      page: 'applications' as AdminPage,
      title: 'Hồ sơ',
      desc: 'Xét duyệt & quản lý',
      Icon: FolderOpen,
      iconBg: 'bg-red-50',
      iconColor: 'text-[#8f000d]',
    },
    {
      page: 'users' as AdminPage,
      title: 'Thành viên',
      desc: 'Tài khoản người dùng',
      Icon: Users,
      iconBg: 'bg-blue-50',
      iconColor: 'text-blue-600',
    },
    {
      page: 'locations' as AdminPage,
      title: 'Địa điểm',
      desc: 'Cơ quan hành chính',
      Icon: MapPin,
      iconBg: 'bg-green-50',
      iconColor: 'text-green-600',
    },
    {
      page: 'procedures' as AdminPage,
      title: 'Thủ tục',
      desc: 'Quy trình hành chính',
      Icon: FileText,
      iconBg: 'bg-purple-50',
      iconColor: 'text-purple-600',
    },
    {
      page: 'chatbot' as AdminPage,
      title: 'Chatbot AI',
      desc: 'Persona · Prompts · Rules',
      Icon: Bot,
      iconBg: 'bg-indigo-50',
      iconColor: 'text-indigo-600',
    },
    {
      page: 'system' as AdminPage,
      title: 'Hệ thống',
      desc: 'Cài đặt & nhật ký',
      Icon: Settings,
      iconBg: 'bg-slate-50',
      iconColor: 'text-slate-600',
    },
  ];

  const STAT_CARDS = [
    {
      label: 'Người dùng',
      value: stats?.totalUsers,
      Icon: Users,
      iconBg: 'bg-blue-50',
      iconColor: 'text-blue-600',
      trend: 'Tài khoản',
      trendColor: 'text-blue-500',
    },
    {
      label: 'Hồ sơ',
      value: stats?.totalApplications,
      Icon: FolderOpen,
      iconBg: 'bg-red-50',
      iconColor: 'text-[#8f000d]',
      trend: 'Tổng cộng',
      trendColor: 'text-[#8f000d]',
    },
    {
      label: 'Chờ duyệt',
      value: stats?.pendingApplications,
      Icon: Clock,
      iconBg: 'bg-yellow-50',
      iconColor: 'text-yellow-600',
      trend: 'Cần xử lý',
      trendColor: 'text-yellow-600',
    },
  ];

  return (
    <div className="min-h-screen bg-[#f8f9fa] pb-10">

      {/* ── Top App Bar ─────────────────────────────────────────────────────── */}
      <header className="sticky top-0 z-30 bg-white border-b border-neutral-100 shadow-sm">
        <div className="flex items-center justify-between px-4 h-14">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 bg-[#8f000d] rounded-full flex items-center justify-center shrink-0">
              <ShieldCheck className="w-4 h-4 text-white" />
            </div>
            <span className="text-sm font-extrabold text-[#8f000d] uppercase tracking-tight">
              Quản trị E-Mapp
            </span>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => onNavigate('notifications')}
              className="relative w-9 h-9 flex items-center justify-center text-neutral-500
                hover:text-[#8f000d] rounded-full hover:bg-neutral-50 transition-colors"
            >
              <Bell className="w-5 h-5" />
            </button>
            <button
              onClick={() => onGoTo('system')}
              className="w-9 h-9 bg-neutral-100 rounded-full flex items-center justify-center
                hover:bg-neutral-200 transition-colors"
              title={user?.fullName}
            >
              <span className="text-sm font-bold text-neutral-600">
                {(user?.fullName || 'A')[0].toUpperCase()}
              </span>
            </button>
          </div>
        </div>
      </header>

      <div className="px-4 py-4 space-y-6">

        {/* ── Hero Banner ─────────────────────────────────────────────────────── */}
        <section
          className="relative rounded-2xl overflow-hidden shadow-lg"
          style={{ background: 'linear-gradient(135deg, #8f000d 0%, #3d0006 100%)' }}
        >
          <div className="absolute inset-0" style={patternStyle} />
          <div className="absolute -right-4 -bottom-4 opacity-5 pointer-events-none">
            <BarChart3 className="w-40 h-40 text-white" />
          </div>
          <div className="relative z-10 px-5 py-5">
            <p className="text-white/70 text-xs">Xin chào,</p>
            <h1 className="text-white font-black text-xl leading-tight mt-0.5">
              {user?.fullName || 'Admin'}
            </h1>
            <p className="text-white/50 text-[11px] mt-0.5">{user?.email}</p>

            {/* Quick stats inside hero */}
            {!loading && stats && (
              <div className="flex gap-px mt-4 rounded-xl overflow-hidden border border-white/10">
                {[
                  { label: 'Users',  value: stats.totalUsers },
                  { label: 'Hồ sơ', value: stats.totalApplications },
                  { label: 'Địa điểm', value: stats.totalLocations },
                ].map((s, i) => (
                  <div key={i} className="flex-1 bg-white/10 text-center py-2.5 px-1">
                    <p className="text-base font-black text-white leading-none">{s.value ?? '—'}</p>
                    <p className="text-[9px] text-white/60 mt-0.5 uppercase tracking-wide">{s.label}</p>
                  </div>
                ))}
              </div>
            )}
            {loading && (
              <div className="flex items-center gap-2 mt-4 text-white/50 text-xs">
                <RefreshCw className="w-3.5 h-3.5 animate-spin" /> Đang tải...
              </div>
            )}
          </div>
        </section>

        {/* ── Section Cards ───────────────────────────────────────────────────── */}
        <section>
          <div className="flex items-center justify-between mb-3">
            <div>
              <h2 className="text-base font-black text-neutral-800 tracking-tight">Quản lý hệ thống</h2>
              <div className="w-10 h-1 bg-[#8f000d] rounded-full mt-1" />
            </div>
          </div>

          <div className="grid grid-cols-3 gap-2.5">
            {CARDS.map((c) => (
              <button
                key={c.page}
                onClick={() => onGoTo(c.page)}
                className="bg-white rounded-2xl p-3 border border-neutral-100 shadow-sm
                  hover:shadow-md hover:-translate-y-0.5 transition-all active:scale-[0.97]
                  flex flex-col items-center text-center gap-2 py-4"
              >
                <div className={`w-11 h-11 ${c.iconBg} rounded-xl flex items-center justify-center`}>
                  <c.Icon className={`w-5 h-5 ${c.iconColor}`} />
                </div>
                <p className="text-[11px] font-bold text-neutral-800 leading-tight">{c.title}</p>
                <p className="text-[9px] text-neutral-400 leading-snug">{c.desc}</p>
              </button>
            ))}
          </div>
        </section>

        {/* ── Stats ───────────────────────────────────────────────────────────── */}
        <section>
          <div className="flex items-center justify-between mb-3">
            <div>
              <h2 className="text-base font-black text-neutral-800 tracking-tight">Thống kê nhanh</h2>
              <div className="w-10 h-1 bg-[#a17d00] rounded-full mt-1" />
            </div>
            <button
              onClick={() => {
                setLoading(true);
                adminSvc.getStats()
                  .then(r => setStats(r.data))
                  .catch(() => {})
                  .finally(() => setLoading(false));
              }}
              className="p-2 rounded-xl hover:bg-neutral-100 transition-colors"
            >
              <RefreshCw className={`w-4 h-4 text-neutral-400 ${loading ? 'animate-spin' : ''}`} />
            </button>
          </div>

          <div className="grid grid-cols-3 gap-2">
            {STAT_CARDS.map((s) => (
              <div key={s.label}
                className="bg-white rounded-2xl p-3 border border-neutral-100 shadow-sm
                  hover:shadow-md hover:-translate-y-0.5 transition-all">
                <div className={`w-9 h-9 ${s.iconBg} rounded-xl flex items-center justify-center mb-2`}>
                  <s.Icon className={`w-4 h-4 ${s.iconColor}`} />
                </div>
                <p className="text-xl font-black text-neutral-800 leading-none">
                  {loading ? '—' : (s.value ?? '—')}
                </p>
                <p className="text-[9px] font-black text-neutral-400 uppercase tracking-wider mt-1 leading-tight">
                  {s.label}
                </p>
                <p className={`text-[9px] font-bold mt-1.5 ${s.trendColor} flex items-center gap-0.5`}>
                  <TrendingUp className="w-2.5 h-2.5 shrink-0" />
                  <span className="truncate">{s.trend}</span>
                </p>
              </div>
            ))}
          </div>
        </section>

      </div>
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════════════════
   SHELL
═══════════════════════════════════════════════════════════════════════════ */
export function AdminShell({ onNavigate }: Props) {
  const [page, setPage] = useState<AdminPage>('home');

  const goTo   = (p: AdminPage) => setPage(p);
  const goHome = ()             => setPage('home');

  /* ── Home ─────────────────────────────────────────────────────────────── */
  if (page === 'home') {
    return <AdminHomeView onNavigate={onNavigate} onGoTo={goTo} />;
  }

  /* ── Sub-pages ────────────────────────────────────────────────────────── */
  return (
    <div className="min-h-screen bg-[#f8f9fa] flex flex-col">

      {/* Back bar */}
      <div className="sticky top-0 z-30 bg-white border-b border-neutral-100 shadow-sm
        px-4 h-14 flex items-center gap-3">
        <button
          onClick={goHome}
          className="w-9 h-9 flex items-center justify-center rounded-full hover:bg-neutral-100 transition-colors"
        >
          <ChevronLeft className="w-5 h-5 text-neutral-600" />
        </button>
        <span className="text-sm font-bold text-neutral-800">
          {PAGE_META[page].label}
        </span>
      </div>

      {/* Screen content */}
      <div className="flex-1 overflow-y-auto pb-6">
        {page === 'applications' && <AdminApplicationsScreen onNavigate={onNavigate} />}
        {page === 'users'        && <AdminUsersScreen        onNavigate={onNavigate} />}
        {page === 'locations'    && <AdminLocationsScreen    onNavigate={onNavigate} />}
        {page === 'procedures'   && <AdminProceduresScreen   onNavigate={onNavigate} />}
        {page === 'chatbot'      && <AdminChatbotScreen      onNavigate={onNavigate} />}
        {page === 'system'       && <AdminSystemScreen       onNavigate={onNavigate} />}
      </div>
    </div>
  );
}
