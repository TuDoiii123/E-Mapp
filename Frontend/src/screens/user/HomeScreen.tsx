import {
  Search, FileText, Plus, MapPin, Star, Bell, Calendar, Hash,
  MonitorPlay, ShieldCheck, TrendingUp, Clock, CheckCircle2,
  FolderOpen, CreditCard, ArrowRight, Eye, Download, ChevronRight,
  RefreshCw,
} from 'lucide-react';
import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import * as adminSvc from '../../services/adminService';

interface HomeScreenProps {
  onNavigate: (screen: string, params?: any) => void;
}

const STATUS_LABEL: Record<string, string> = {
  draft: 'Bản nháp', submitted: 'Đã nộp', in_review: 'Đang xem xét',
  approved: 'Đã duyệt', rejected: 'Từ chối', more_info: 'Cần bổ sung', withdraw: 'Đã rút',
};
const STATUS_COLOR: Record<string, string> = {
  draft: 'bg-gray-50 text-gray-600', submitted: 'bg-blue-50 text-blue-600',
  in_review: 'bg-yellow-50 text-yellow-700', approved: 'bg-green-50 text-green-700',
  rejected: 'bg-red-50 text-red-700', more_info: 'bg-orange-50 text-orange-700',
};

export function HomeScreen({ onNavigate }: HomeScreenProps) {
  const { user } = useAuth();
  const role = (user as any)?.role || 'citizen';
  const [recentApps,    setRecentApps]    = useState<any[]>([]);
  const [loadingApps,   setLoadingApps]   = useState(true);
  const [searchQuery,   setSearchQuery]   = useState('');
  const [sysStats,      setSysStats]      = useState<{totalApplications:number; pendingApplications:number; ticketsToday:number} | null>(null);

  useEffect(() => {
    adminSvc.getMyApplications()
      .then(r => setRecentApps(Array.isArray(r.data) ? r.data.slice(0, 3) : []))
      .catch(() => setRecentApps([]))
      .finally(() => setLoadingApps(false));
    adminSvc.getStats()
      .then(r => setSysStats(r.data || null))
      .catch(() => {});
  }, []);

  const handleSearch = () => {
    if (searchQuery.trim()) onNavigate('search');
  };

  const shortcuts = [
    {
      id: 'search',
      title: 'Tra cứu hồ sơ',
      icon: FileText,
      color: 'bg-red-500',
      description: 'Kiểm tra trạng thái hồ sơ'
    },
    {
      id: 'submit',
      title: 'Nộp hồ sơ mới',
      icon: Plus,
      color: 'bg-red-600',
      description: 'Nộp hồ sơ trực tuyến'
    },
    {
      id: 'appointment',
      title: 'Đặt lịch hẹn',
      icon: Calendar,
      color: 'bg-red-600',
      description: 'Chọn ngày giờ làm thủ tục'
    },
    {
      id: 'map',
      title: 'Bản đồ dịch vụ',
      icon: MapPin,
      color: 'bg-red-400',
      description: 'Tìm cơ quan gần nhất'
    },
    {
      id: 'evaluation',
      title: 'Đánh giá cơ quan',
      icon: Star,
      color: 'bg-red-700',
      description: 'Góp ý chất lượng dịch vụ'
    }
    ,{
      id: 'document-catalog',
      title: 'Tổng hợp giấy tờ',
      icon: FileText,
      color: 'bg-indigo-600',
      description: 'Xem các loại giấy tờ và tìm kiếm'
    },
    {
      id: 'queue',
      title: 'Lấy số thứ tự',
      icon: Hash,
      color: 'bg-emerald-600',
      description: 'Lấy số và theo dõi hàng chờ'
    },
    {
      id: 'queue-display',
      title: 'Bảng hàng chờ',
      icon: MonitorPlay,
      color: 'bg-slate-700',
      description: 'Màn hình hiển thị realtime'
    },
    // Chỉ hiển thị cho nhân viên / admin
    ...(role === 'staff' || role === 'admin' ? [{
      id: 'queue-staff',
      title: 'Quầy phục vụ',
      icon: Hash,
      color: 'bg-teal-600',
      description: 'Gọi vé và phục vụ khách'
    }] : []),
    ...(role === 'admin' ? [{
      id: 'admin',
      title: 'Quản trị',
      icon: ShieldCheck,
      color: 'bg-gray-800',
      description: 'Quản lý hệ thống'
    }] : []),
  ];

  // Vietnam dot pattern via inline style
  const patternStyle: React.CSSProperties = {
    backgroundImage:
      'radial-gradient(#a17d00 0.5px, transparent 0.5px), radial-gradient(#a17d00 0.5px, #8f000d 0.5px)',
    backgroundSize: '20px 20px',
    backgroundPosition: '0 0, 10px 10px',
    opacity: 0.07,
  };


  return (
    <div className="min-h-screen bg-[#f8f9fa] pb-24">

      {/* ── Top App Bar ── */}
      <header className="sticky top-0 z-30 bg-white border-b border-neutral-100 shadow-sm">
        <div className="flex items-center justify-between px-4 sm:px-6 h-14 sm:h-16 max-w-screen-xl mx-auto">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 bg-[#8f000d] rounded-full flex items-center justify-center shrink-0">
              <ShieldCheck className="w-4 h-4 text-white" />
            </div>
            <span className="text-xs sm:text-sm font-extrabold text-[#8f000d] uppercase tracking-tight">Cổng Dịch vụ công</span>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => onNavigate('notifications')}
              className="relative w-9 h-9 flex items-center justify-center text-neutral-500 hover:text-[#8f000d] rounded-full hover:bg-neutral-50 transition-colors"
              aria-label="Thông báo"
            >
              <Bell className="w-5 h-5" />
              <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full border-2 border-white" />
            </button>
            <button
              onClick={() => onNavigate('account-detail')}
              className="w-9 h-9 bg-neutral-100 rounded-full flex items-center justify-center hover:bg-neutral-200 transition-colors"
              aria-label="Tài khoản"
            >
              <span className="text-sm font-bold text-neutral-600">{(user?.fullName || 'U')[0].toUpperCase()}</span>
            </button>
          </div>
        </div>
      </header>

      <div className="px-3 sm:px-6 lg:px-8 py-4 sm:py-6 space-y-6 sm:space-y-8 max-w-screen-xl mx-auto">

        {/* ── Hero ── */}
        <section
          className="relative rounded-2xl sm:rounded-3xl overflow-hidden shadow-lg"
          style={{ background: 'linear-gradient(135deg, #8f000d 0%, #3d0006 100%)' }}
        >
          <div className="absolute inset-0" style={patternStyle} />
          <div className="absolute -right-6 -bottom-6 opacity-5 pointer-events-none">
            <FileText className="w-36 h-36 sm:w-48 sm:h-48 text-white" />
          </div>
          <div className="relative z-10 px-4 sm:px-6 py-6 sm:py-8 flex flex-col gap-4">
            <div>
              <p className="text-white/70 text-xs sm:text-sm">Xin chào,</p>
              <h1 className="text-white font-black text-xl sm:text-2xl leading-tight mt-0.5">{user?.fullName || 'bạn'}</h1>
              <p className="text-white/60 text-xs mt-1">Chào mừng đến với Cổng Dịch vụ công</p>
            </div>
            <div className="w-full relative">
              <input
                value={searchQuery}
                onChange={e => setSearchQuery(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && handleSearch()}
                placeholder="Tìm thủ tục, cơ quan, số CCCD..."
                className="w-full h-11 sm:h-12 pl-4 pr-24 sm:pr-28 rounded-full bg-white text-sm text-neutral-800 shadow-xl border-none outline-none focus:ring-2 focus:ring-[#a17d00]/40"
              />
              <button
                onClick={handleSearch}
                className="absolute right-1.5 top-1/2 -translate-y-1/2 h-8 sm:h-9 px-4 sm:px-5 bg-[#8f000d] text-white rounded-full flex items-center gap-1.5 text-xs font-bold uppercase tracking-wide hover:bg-[#a17d00] transition-colors active:scale-95"
              >
                <Search className="w-3 h-3 sm:w-3.5 sm:h-3.5" />
                <span>Tìm</span>
              </button>
            </div>
          </div>
        </section>

        {/* ── Service Grid ── */}
        <section>
          <div className="flex items-center justify-between mb-3 sm:mb-4">
            <div>
              <h2 className="text-base sm:text-lg font-black text-neutral-800 tracking-tight">Danh mục dịch vụ</h2>
              <div className="w-10 sm:w-14 h-1 bg-[#a17d00] rounded-full mt-1" />
            </div>
            <button onClick={() => onNavigate('search')} className="text-xs font-bold text-neutral-500 bg-neutral-100 hover:bg-neutral-200 px-3 py-1.5 rounded-full transition-colors">
              Xem toàn bộ
            </button>
          </div>

          <div className="grid grid-cols-3 sm:grid-cols-3 lg:grid-cols-6 gap-2 sm:gap-3">

            {/* Featured banner — full width */}
            <button
              onClick={() => onNavigate('submit')}
              className="col-span-3 lg:col-span-6 relative overflow-hidden rounded-2xl text-left shadow-md active:scale-[0.98] transition-transform"
              style={{ background: 'linear-gradient(135deg, #8f000d 0%, #3d0006 100%)' }}
            >
              <div className="absolute inset-0" style={patternStyle} />
              <div className="absolute right-3 bottom-1 opacity-5 pointer-events-none">
                <Plus className="w-24 h-24 sm:w-32 sm:h-32 text-white" />
              </div>
              <div className="relative z-10 px-4 sm:px-6 py-4 sm:py-5 flex items-center justify-between gap-4">
                <div className="flex items-center gap-3 sm:gap-4">
                  <div className="w-10 h-10 sm:w-12 sm:h-12 bg-[#a17d00] rounded-xl flex items-center justify-center shrink-0 shadow-lg">
                    <Plus className="w-5 h-5 sm:w-6 sm:h-6 text-white" />
                  </div>
                  <div>
                    <h3 className="text-sm sm:text-base font-black text-white leading-snug">Nộp hồ sơ trực tuyến mới</h3>
                    <p className="text-white/60 text-[10px] sm:text-xs mt-0.5 hidden sm:block">Khởi tạo quy trình hành chính công nhanh chóng, bảo mật cao</p>
                  </div>
                </div>
                <div className="flex items-center gap-1 text-[#a17d00] font-black text-xs shrink-0">
                  <span className="hidden sm:inline">BẮT ĐẦU</span>
                  <ArrowRight className="w-4 h-4" />
                </div>
              </div>
            </button>

            {/* Shortcut cards — 3 cols mobile, 3 cols tablet, 6 cols desktop */}
            {[
              { id: 'search',           title: 'Tra cứu hồ sơ',    icon: Search,     iconBg: 'bg-red-50',    iconColor: 'text-[#8f000d]',  desc: 'Theo dõi tiến độ' },
              { id: 'appointment',      title: 'Đặt lịch hẹn',     icon: Calendar,   iconBg: 'bg-yellow-50', iconColor: 'text-[#a17d00]',  desc: 'Tiết kiệm thời gian' },
              { id: 'document-catalog', title: 'Kho tài liệu',     icon: FolderOpen, iconBg: 'bg-indigo-50', iconColor: 'text-indigo-600',  desc: 'Giấy tờ định danh' },
              { id: 'evaluation',       title: 'Đánh giá dịch vụ', icon: Star,       iconBg: 'bg-amber-50',  iconColor: 'text-amber-600',   desc: 'Góp ý chất lượng' },
              { id: 'map',              title: 'Bản đồ cơ quan',   icon: MapPin,     iconBg: 'bg-green-50',  iconColor: 'text-green-600',   desc: 'Tìm nơi gần nhất' },
              { id: 'queue',            title: 'Lấy số thứ tự',    icon: Hash,       iconBg: 'bg-sky-50',    iconColor: 'text-sky-600',     desc: 'Hàng chờ trực tuyến' },
            ].map((s) => (
              <button
                key={s.id}
                onClick={() => onNavigate(s.id)}
                className="bg-white rounded-2xl p-2.5 sm:p-4 border border-neutral-100 shadow-sm hover:shadow-md hover:-translate-y-0.5 transition-all active:scale-[0.97] flex flex-col items-center text-center gap-1.5 sm:gap-2 py-3 sm:py-4"
              >
                <div className={`w-9 h-9 sm:w-11 sm:h-11 ${s.iconBg} rounded-xl flex items-center justify-center shrink-0`}>
                  <s.icon className={`w-4 h-4 sm:w-5 sm:h-5 ${s.iconColor}`} />
                </div>
                <p className="text-[10px] sm:text-xs font-bold text-neutral-800 leading-tight w-full">{s.title}</p>
                <p className="text-[9px] sm:text-[10px] text-neutral-400 leading-snug hidden sm:block w-full">{s.desc}</p>
              </button>
            ))}

            {/* Wide card: Tổng hợp giấy tờ số — full width */}
            <button
              onClick={() => onNavigate('document-catalog')}
              className="col-span-3 lg:col-span-6 bg-[#a17d00]/10 hover:bg-[#a17d00] rounded-2xl p-3.5 sm:p-5 flex items-center gap-3 sm:gap-4 group transition-all active:scale-[0.98] shadow-sm hover:shadow-lg"
            >
              <div className="w-11 h-11 sm:w-14 sm:h-14 bg-[#a17d00] rounded-xl flex items-center justify-center shrink-0 shadow-lg group-hover:bg-white transition-colors">
                <FolderOpen className="w-5 h-5 sm:w-7 sm:h-7 text-white group-hover:text-[#a17d00] transition-colors" />
              </div>
              <div className="flex-1 text-left min-w-0">
                <p className="text-sm sm:text-base font-bold text-neutral-800 group-hover:text-white transition-colors">Tổng hợp giấy tờ số</p>
                <p className="text-[10px] sm:text-xs text-neutral-500 group-hover:text-white/80 mt-0.5 transition-colors truncate">Kho lưu trữ an toàn cho mọi giấy tờ cá nhân đã được định danh</p>
              </div>
              <div className="w-8 h-8 sm:w-9 sm:h-9 rounded-full bg-[#a17d00]/20 group-hover:bg-white/20 flex items-center justify-center shrink-0 transition-colors">
                <ChevronRight className="w-4 h-4 text-[#a17d00] group-hover:text-white transition-colors" />
              </div>
            </button>
          </div>
        </section>

        {/* ── Stats ── */}
        <section className="grid grid-cols-3 gap-2 sm:gap-3">
          {[
            {
              label: 'Tổng hồ sơ',
              value: sysStats ? sysStats.totalApplications.toLocaleString('vi-VN') : '—',
              icon: FileText, iconBg: 'bg-red-50', iconColor: 'text-[#8f000d]', trendColor: 'text-green-600',
              trend: 'Hệ thống',
            },
            {
              label: 'Đang xử lý',
              value: sysStats ? sysStats.pendingApplications.toLocaleString('vi-VN') : '—',
              icon: Clock, iconBg: 'bg-yellow-50', iconColor: 'text-[#a17d00]', trendColor: 'text-[#a17d00]',
              trend: 'Chờ duyệt',
            },
            {
              label: 'Vé hôm nay',
              value: sysStats ? sysStats.ticketsToday.toLocaleString('vi-VN') : '—',
              icon: CheckCircle2, iconBg: 'bg-green-50', iconColor: 'text-green-600', trendColor: 'text-neutral-500',
              trend: 'Hàng chờ',
            },
          ].map((s) => (
            <div key={s.label} className="bg-white rounded-2xl p-3 sm:p-4 border border-neutral-100 shadow-sm hover:shadow-md hover:-translate-y-0.5 transition-all">
              <div className={`w-8 h-8 sm:w-10 sm:h-10 ${s.iconBg} rounded-xl flex items-center justify-center mb-2`}>
                <s.icon className={`w-4 h-4 sm:w-5 sm:h-5 ${s.iconColor}`} />
              </div>
              <p className="text-sm sm:text-xl font-black text-neutral-800 leading-none">{s.value}</p>
              <p className="text-[8px] sm:text-[10px] font-black text-neutral-400 uppercase tracking-wider mt-1 leading-tight">{s.label}</p>
              <p className={`text-[8px] sm:text-[10px] font-bold mt-1.5 ${s.trendColor} flex items-center gap-0.5`}>
                <TrendingUp className="w-2.5 h-2.5 sm:w-3 sm:h-3 shrink-0" /><span className="truncate">{s.trend}</span>
              </p>
            </div>
          ))}
        </section>

        {/* ── Recent Records ── */}
        <section className="pb-4">
          <div className="flex items-center justify-between mb-3 sm:mb-4">
            <div>
              <h2 className="text-base sm:text-lg font-black text-neutral-800 tracking-tight">Hồ sơ gần đây</h2>
              <div className="w-10 sm:w-14 h-1 bg-[#8f000d] rounded-full mt-1" />
            </div>
            <button
              onClick={() => onNavigate('search')}
              className="text-xs font-bold text-[#8f000d] flex items-center gap-1 hover:gap-2 transition-all"
            >
              Xem tất cả <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="bg-white rounded-2xl border border-neutral-100 shadow-sm overflow-hidden">
            <div className="hidden sm:grid grid-cols-[1fr_auto_auto_auto] gap-4 px-5 py-3 bg-neutral-50 border-b border-neutral-100 text-[10px] font-black text-neutral-400 uppercase tracking-widest">
              <span>Nội dung hồ sơ</span>
              <span>Ngày nộp</span>
              <span>Trạng thái</span>
              <span className="text-right">Thao tác</span>
            </div>

            <div className="divide-y divide-neutral-50">
              {loadingApps ? (
                <div className="flex justify-center py-8"><RefreshCw className="w-5 h-5 animate-spin text-neutral-300" /></div>
              ) : recentApps.length === 0 ? (
                <p className="text-center text-neutral-400 text-sm py-8">Chưa có hồ sơ nào</p>
              ) : recentApps.map((app) => (
                <div key={app.id} className="flex items-center gap-2.5 sm:gap-3 px-3 sm:px-4 py-3 sm:py-4 hover:bg-neutral-50/60 transition-colors group">
                  <div className="w-9 h-9 sm:w-11 sm:h-11 bg-red-50 rounded-xl flex items-center justify-center shrink-0 group-hover:scale-110 transition-transform">
                    <FileText className="w-4 h-4 sm:w-5 sm:h-5 text-[#8f000d]" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-xs sm:text-sm font-bold text-neutral-800 truncate">
                      {app.procedureName || app.serviceId || 'Hồ sơ'}
                    </p>
                    <p className="text-[9px] sm:text-[10px] font-mono text-neutral-400 mt-0.5 truncate">
                      {app.id.slice(0, 8).toUpperCase()} · {app.createdAt ? new Date(app.createdAt).toLocaleDateString('vi-VN') : ''}
                    </p>
                  </div>
                  <span className={`shrink-0 text-[9px] sm:text-[10px] font-black uppercase tracking-wide px-2 sm:px-2.5 py-1 rounded-full whitespace-nowrap ${STATUS_COLOR[app.status] || 'bg-gray-50 text-gray-600'}`}>
                    {STATUS_LABEL[app.status] || app.status}
                  </span>
                  <button
                    onClick={() => onNavigate('search')}
                    className="shrink-0 w-8 h-8 sm:w-9 sm:h-9 rounded-full border border-neutral-200 flex items-center justify-center text-neutral-400 hover:bg-[#8f000d] hover:text-white hover:border-[#8f000d] transition-all"
                    aria-label="Xem chi tiết"
                  >
                    <Eye className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
                  </button>
                </div>
              ))}
            </div>
          </div>
        </section>

      </div>
    </div>
  );
}