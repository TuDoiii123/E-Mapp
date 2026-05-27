/**
 * SearchDocumentScreen — Tra cứu hồ sơ
 * Kết nối API thật: GET /api/applications/search và /api/applications/my
 */
import { useState, useEffect, useCallback } from 'react';
import {
  Clock, CheckCircle2, AlertCircle,
  Phone, MessageCircle, RefreshCw, X, ChevronRight, ArrowLeft,
  FolderX,
} from 'lucide-react';

import { API_BASE_URL, getToken } from '../../services/api';

const BASE = API_BASE_URL;

function authH(): HeadersInit { const token = getToken(); return token ? { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` } : {}; }


interface AppRecord {
  id:            string;
  applicantId:   string;
  serviceId:     string;
  currentStatus: string;
  createdAt:     string;
  updatedAt:     string;
  data:          Record<string, any>;
  statusHistory: { status: string; note: string; createdAt: string }[];
}

interface SearchDocumentScreenProps {
  onNavigate: (screen: string, params?: any) => void;
  params?: any;
}

const STATUS_META: Record<string, { label: string; chip: string; progress: number }> = {
  submitted: { label: 'Đã nộp',      chip: 'bg-blue-50 text-blue-700',        progress: 25  },
  in_review: { label: 'Đang xử lý',  chip: 'bg-[#ffeced] text-[#b7131a]',     progress: 60  },
  more_info: { label: 'Cần bổ sung', chip: 'bg-orange-50 text-orange-700',     progress: 40  },
  approved:  { label: 'Đã duyệt',    chip: 'bg-emerald-50 text-emerald-700',   progress: 100 },
  rejected:  { label: 'Từ chối',     chip: 'bg-red-50 text-[#b7131a]',         progress: 100 },
};

function statusMeta(s: string) {
  return STATUS_META[s] || { label: s, chip: 'bg-neutral-100 text-neutral-600', progress: 0 };
}

function fmtDate(iso: string) {
  if (!iso) return '–';
  return new Date(iso).toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit', year: 'numeric' });
}

// ── Detail view ───────────────────────────────────────────────────────────────
function AppDetail({ app, onBack, onNavigate }: {
  app: AppRecord; onBack(): void; onNavigate(s: string, p?: any): void;
}) {
  const meta  = statusMeta(app.currentStatus);
  const steps = [
    { name: 'Tiếp nhận',  done: true },
    { name: 'Đang xử lý', done: ['in_review', 'more_info', 'approved', 'rejected'].includes(app.currentStatus) },
    { name: 'Xét duyệt',  done: ['approved', 'rejected'].includes(app.currentStatus) },
    { name: 'Hoàn tất',   done: app.currentStatus === 'approved' },
  ];

  return (
    <div className="min-h-screen bg-[#fff4f4] pb-20 font-[Manrope,sans-serif]">
      <header className="sticky top-0 z-30 bg-[#fff4f4]/90 backdrop-blur-md border-b border-[#ffeced] shadow-sm">
        <div className="flex items-center gap-3 px-4 h-14 max-w-7xl mx-auto">
          <button
            onClick={onBack}
            aria-label="Quay lại"
            className="w-9 h-9 flex items-center justify-center text-[#9f364c] hover:text-[#b7131a] transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <span className="text-sm font-bold text-[#b7131a] uppercase tracking-wide">Chi tiết hồ sơ</span>
        </div>
      </header>

      <div className="px-4 py-6 max-w-2xl mx-auto space-y-5">

        {/* Status banner */}
        <div className="bg-white rounded-xl shadow-[0_20px_40px_rgba(77,33,40,0.06)] p-6 border-l-4 border-[#b7131a]">
          <div className="flex items-start justify-between gap-3 mb-4">
            <div className="flex-1 min-w-0">
              <p className="font-bold text-[#4d2128] text-base leading-snug">
                {app.data?.serviceName || app.serviceId || 'Hồ sơ hành chính'}
              </p>
              <p className="text-xs font-mono text-[#824c54]/60 mt-1">Mã: {app.id}</p>
            </div>
            <span className={`shrink-0 text-[11px] font-black uppercase tracking-wider px-3 py-1 rounded-full ${meta.chip}`}>
              {meta.label}
            </span>
          </div>
          <div className="grid grid-cols-2 gap-3 text-sm mb-4 border-t border-[#ffeced] pt-4">
            <div>
              <p className="text-[10px] font-black uppercase tracking-widest text-[#824c54]/60 mb-0.5">Ngày nộp</p>
              <p className="font-semibold text-[#4d2128]">{fmtDate(app.createdAt)}</p>
            </div>
            <div>
              <p className="text-[10px] font-black uppercase tracking-widest text-[#824c54]/60 mb-0.5">Cập nhật</p>
              <p className="font-semibold text-[#4d2128]">{fmtDate(app.updatedAt)}</p>
            </div>
          </div>
          <div>
            <div className="flex justify-between text-[10px] font-black uppercase tracking-widest text-[#824c54]/60 mb-2">
              <span>Tiến trình</span><span>{meta.progress}%</span>
            </div>
            <div className="w-full h-1.5 bg-[#ffd2d6] rounded-full">
              <div className="h-1.5 bg-[#b7131a] rounded-full transition-all" style={{ width: `${meta.progress}%` }} />
            </div>
          </div>
        </div>

        {/* Timeline steps */}
        <div className="bg-white rounded-xl shadow-[0_20px_40px_rgba(77,33,40,0.06)] p-6">
          <p className="text-[10px] font-black uppercase tracking-widest text-[#824c54]/60 mb-4">Quy trình xử lý</p>
          <div className="relative">
            <div className="absolute left-3 top-0 bottom-0 w-px bg-[#ffeced]" />
            <div className="space-y-4">
              {steps.map((s, i) => (
                <div key={i} className="flex items-center gap-4 relative">
                  <div className={`w-6 h-6 rounded-full flex items-center justify-center z-10 shrink-0 ${
                    s.done ? 'bg-[#b7131a]' : 'bg-[#ffd2d6]'
                  }`}>
                    {s.done
                      ? <CheckCircle2 className="w-3.5 h-3.5 text-white" />
                      : <div className="w-2 h-2 rounded-full bg-[#de9ca4]" />}
                  </div>
                  <p className={`text-sm font-semibold ${s.done ? 'text-[#4d2128]' : 'text-[#de9ca4]'}`}>
                    {s.name}
                  </p>
                  {s.done && <CheckCircle2 className="w-4 h-4 text-emerald-500 ml-auto" />}
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Lịch sử */}
        {app.statusHistory?.length > 0 && (
          <div className="bg-white rounded-xl shadow-[0_20px_40px_rgba(77,33,40,0.06)] p-6">
            <p className="text-[10px] font-black uppercase tracking-widest text-[#824c54]/60 mb-3">Lịch sử xử lý</p>
            <div className="space-y-2">
              {app.statusHistory.map((h, i) => {
                const hm = statusMeta(h.status);
                return (
                  <div key={i} className="bg-[#fff4f4] px-3 py-2.5 rounded-lg">
                    <div className="flex items-center justify-between mb-1">
                      <span className={`text-[10px] font-black uppercase rounded-full px-2 py-0.5 ${hm.chip}`}>{hm.label}</span>
                      <span className="text-[10px] text-[#824c54]/60">{fmtDate(h.createdAt)}</span>
                    </div>
                    {h.note && <p className="text-xs text-[#9f364c]">{h.note}</p>}
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Cần bổ sung */}
        {app.currentStatus === 'more_info' && (
          <div className="bg-orange-50 rounded-xl border border-orange-200 p-4">
            <div className="flex items-center gap-2 text-orange-700 text-sm font-bold mb-1">
              <AlertCircle className="w-4 h-4" /> Cần bổ sung hồ sơ
            </div>
            <p className="text-xs text-orange-600">
              {app.statusHistory?.slice().reverse().find(h => h.status === 'more_info')?.note
                || 'Vui lòng liên hệ cơ quan để biết thêm chi tiết.'}
            </p>
          </div>
        )}

        {/* Actions */}
        <div className="flex gap-3">
          <button className="flex-1 h-12 bg-[#b7131a] text-white font-bold text-sm rounded-xl flex items-center justify-center gap-2 hover:bg-[#a40010] active:scale-[0.98] transition-all shadow-lg shadow-[#b7131a]/20">
            <Phone className="w-4 h-4" /> Gọi hotline
          </button>
          <button
            onClick={() => onNavigate('chatbot')}
            className="flex-1 h-12 border-2 border-[#b7131a] text-[#b7131a] font-bold text-sm rounded-xl flex items-center justify-center gap-2 hover:bg-[#ffeced] active:scale-[0.98] transition-all"
          >
            <MessageCircle className="w-4 h-4" /> Hỏi AI
          </button>
        </div>
      </div>
    </div>
  );
}


const FILTER_CHIPS = [
  { label: 'TẤT CẢ',      value: '' },
  { label: 'ĐANG XỬ LÝ',  value: 'in_review' },
  { label: 'CẦN BỔ SUNG', value: 'more_info' },
  { label: 'ĐÃ DUYỆT',    value: 'approved' },
];

// ── Main component ────────────────────────────────────────────────────────────
export function SearchDocumentScreen({ onNavigate, params }: SearchDocumentScreenProps) {
  const [searchValue,  setSearchValue]  = useState('');
  const [activeFilter, setActiveFilter] = useState('');
  const [selected,     setSelected]     = useState<AppRecord | null>(params?.selectedApp ?? null);
  const [myApps,       setMyApps]       = useState<AppRecord[]>([]);
  const [searchResult, setSearchResult] = useState<AppRecord[] | null>(null);
  const [loading,      setLoading]      = useState(false);
  const [loadingMy,    setLoadingMy]    = useState(true);
  const [error,        setError]        = useState('');

  const loadMyApps = useCallback(async () => {
    setLoadingMy(true);
    try {
      const res  = await fetch(`${BASE}/applications/my`, { headers: authH() });
      const json = await res.json();
      if (json.success) setMyApps(json.data || []);
    } catch { /* bỏ qua */ }
    finally { setLoadingMy(false); }
  }, []);

  useEffect(() => { loadMyApps(); }, [loadMyApps]);

  const handleSearch = async (q = searchValue) => {
    const trimmed = q.trim();
    if (!trimmed) { setSearchResult(null); return; }
    setLoading(true); setError('');
    try {
      const isCCCD = /^\d{9,12}$/.test(trimmed);
      const url = isCCCD
        ? `${BASE}/applications/search?cccd=${trimmed}`
        : `${BASE}/applications/search?q=${encodeURIComponent(trimmed)}`;
      const res  = await fetch(url, { headers: authH() });
      const json = await res.json();
      if (json.success) setSearchResult(json.data || []);
      else { setError(json.message || 'Lỗi tra cứu'); setSearchResult([]); }
    } catch (e: any) {
      setError(e.message); setSearchResult([]);
    } finally { setLoading(false); }
  };

  const handleFilterChip = async (val: string) => {
    setActiveFilter(val);
    setSearchValue('');
    if (!val) { setSearchResult(null); return; }
    setLoading(true);
    try {
      const res  = await fetch(`${BASE}/applications/my?status=${val}`, { headers: authH() });
      const json = await res.json();
      if (json.success) setSearchResult(json.data || []);
    } catch { /* bỏ qua */ }
    finally { setLoading(false); }
  };

  const clearAll = () => { setSearchResult(null); setSearchValue(''); setActiveFilter(''); };

  const displayList: AppRecord[] = searchResult ?? myApps;

  if (selected) {
    return <AppDetail app={selected} onBack={() => setSelected(null)} onNavigate={onNavigate} />;
  }

  return (
    <div className="bg-[#fff4f4] text-[#4d2128] min-h-screen flex flex-col" style={{ fontFamily: "'Manrope', sans-serif" }}>

      {/* ── TopNavBar ── */}
      <header className="flex justify-between items-center w-full px-6 md:px-10 py-4 bg-[#fff4f4]/80 backdrop-blur-md sticky top-0 z-40 border-b border-[#de9ca4]/20">
        <div className="flex items-center gap-6 flex-1">
          <div className="relative w-full max-w-md">
            <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-[#9f364c] text-xl">search</span>
            <input
              value={searchValue}
              onChange={e => { setSearchValue(e.target.value); if (!e.target.value) clearAll(); }}
              onKeyDown={e => e.key === 'Enter' && handleSearch()}
              className="w-full pl-10 pr-4 py-2 bg-white border-none rounded-xl text-sm focus:ring-2 focus:ring-[#b7131a] outline-none placeholder:text-[#9f364c]/50"
              placeholder="Tìm kiếm hồ sơ, tài liệu..."
            />
          </div>
        </div>
        <div className="flex items-center gap-3 ml-4">
          <div className="hidden sm:flex items-center gap-2 px-4 py-2 bg-[#ffeced] rounded-full">
            <span className="w-2 h-2 rounded-full bg-green-500" />
            <span className="text-sm font-bold text-[#4d2128]">Cổng dịch vụ công</span>
          </div>
          <button onClick={() => onNavigate('notifications')} className="w-10 h-10 flex items-center justify-center rounded-full hover:bg-[#ffd9dd] transition-all text-[#9f364c]">
            <span className="material-symbols-outlined">notifications</span>
          </button>
          <button className="w-10 h-10 flex items-center justify-center rounded-full hover:bg-[#ffd9dd] transition-all text-[#9f364c]">
            <span className="material-symbols-outlined">settings</span>
          </button>
        </div>
      </header>

      {/* ── Main ── */}
      <main className="flex-1 px-6 md:px-10 py-10 max-w-6xl mx-auto w-full">

        {/* Hero Header */}
        <section className="mb-12">
          <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
            <div>
              <button onClick={() => onNavigate('home')} className="flex items-center gap-1.5 text-sm text-[#9f364c] hover:text-[#b7131a] transition-colors mb-3">
                <ArrowLeft className="w-4 h-4" /> Trang chủ
              </button>
              <h2 className="text-4xl font-extrabold tracking-tight text-[#4d2128] mb-2">Tổng hợp giấy tờ</h2>
              <p className="text-lg text-[#9f364c] font-medium">Tìm và xem các loại giấy tờ thủ tục hành chính công</p>
            </div>
            <div className="flex items-center gap-3">
              <span className="px-4 py-2 bg-[#b7131a]/10 text-[#b7131a] rounded-full text-sm font-bold">Hệ thống E-Mapp</span>
              <span className="px-4 py-2 bg-[#fdc003]/20 text-[#755700] rounded-full text-sm font-bold">Cập nhật 24/7</span>
            </div>
          </div>
        </section>

        {/* Search Bento Box */}
        <section className="mb-16">
          <div className="bg-white rounded-3xl p-8 shadow-sm relative overflow-hidden border border-[#de9ca4]/10">
            <div className="absolute top-0 right-0 w-64 h-64 bg-[#b7131a]/5 rounded-full -mr-20 -mt-20 blur-3xl pointer-events-none" />
            <div className="relative z-10">
              <label className="block text-sm font-bold text-[#4d2128] mb-4">Tra cứu hồ sơ</label>
              <div className="flex flex-col md:flex-row gap-4">
                <div className="flex-1 relative">
                  <span className="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-[#b7131a]">description</span>
                  <input
                    value={searchValue}
                    onChange={e => { setSearchValue(e.target.value); if (!e.target.value) clearAll(); }}
                    onKeyDown={e => e.key === 'Enter' && handleSearch()}
                    placeholder="Nhập mã hồ sơ, số CCCD hoặc tên cơ quan..."
                    aria-label="Tìm kiếm hồ sơ"
                    className="w-full pl-12 pr-4 py-4 bg-[#ffeced] border-none rounded-2xl text-base focus:ring-2 focus:ring-[#b7131a] outline-none placeholder:text-[#de9ca4]"
                  />
                </div>
                <button
                  onClick={() => handleSearch()}
                  disabled={loading}
                  className="px-8 py-4 bg-gradient-to-br from-[#b7131a] to-[#ff766b] text-white font-bold rounded-2xl flex items-center justify-center gap-2 shadow-lg shadow-[#b7131a]/20 hover:scale-105 transition-transform disabled:opacity-60 disabled:hover:scale-100"
                >
                  {loading
                    ? <RefreshCw className="w-5 h-5 animate-spin" />
                    : <span className="material-symbols-outlined">search</span>
                  }
                  <span>Tìm kiếm</span>
                </button>
              </div>
              {error && (
                <div className="mt-3 flex items-center gap-2 text-[#b7131a] bg-[#ffeced] border-l-2 border-[#b7131a] px-3 py-2 text-xs font-medium rounded-lg">
                  <AlertCircle className="w-4 h-4 shrink-0" /> {error}
                </div>
              )}
            </div>
          </div>
        </section>

        {/* Filter Chips + List Header */}
        <section>
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-2xl font-bold text-[#4d2128]">
              {searchResult ? `Kết quả tìm kiếm` : `Hồ sơ của bạn`}
            </h3>
            <div className="flex items-center gap-2">
              <div className="flex flex-wrap gap-2">
                {FILTER_CHIPS.map(chip => (
                  <button
                    key={chip.value}
                    onClick={() => handleFilterChip(chip.value)}
                    className={`px-4 py-1.5 rounded-full text-xs font-bold transition-colors ${
                      activeFilter === chip.value
                        ? 'bg-[#b7131a] text-white'
                        : 'bg-[#ffd2d6] text-[#824c54] hover:bg-[#ffc2c9]'
                    }`}
                  >
                    {chip.label}
                  </button>
                ))}
              </div>
              {(searchResult !== null || activeFilter) && (
                <button onClick={clearAll} aria-label="Xóa bộ lọc" className="w-8 h-8 rounded-full border border-[#de9ca4] hover:border-[#b7131a] hover:text-[#b7131a] text-[#824c54] flex items-center justify-center transition-colors">
                  <X className="w-3.5 h-3.5" />
                </button>
              )}
            </div>
          </div>

          {/* Results */}
          {(loading || loadingMy) ? (
            <div className="flex flex-col items-center justify-center py-24 bg-white rounded-3xl border border-[#de9ca4]/20">
              <RefreshCw className="w-10 h-10 text-[#de9ca4] animate-spin mb-3" />
              <p className="text-sm text-[#9f364c] font-medium">Đang tải...</p>
            </div>
          ) : displayList.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-24 bg-white rounded-3xl border border-[#de9ca4]/20">
              <div className="w-20 h-20 mb-5 bg-[#ffeced] rounded-2xl flex items-center justify-center">
                <FolderX className="w-10 h-10 text-[#de9ca4]" strokeWidth={1.5} />
              </div>
              <h3 className="text-xl font-bold text-[#4d2128] mb-2">Không tìm thấy hồ sơ nào</h3>
              <p className="text-[#824c54] text-center max-w-sm text-sm">Vui lòng kiểm tra lại mã hồ sơ hoặc số CCCD.</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 gap-4">
              {displayList.map(app => {
                const meta = statusMeta(app.currentStatus);
                return (
                  <button
                    key={app.id}
                    onClick={() => setSelected(app)}
                    className="group bg-white rounded-2xl p-6 flex flex-col md:flex-row items-center justify-between transition-all hover:shadow-xl hover:shadow-[#b7131a]/5 border border-transparent hover:border-[#de9ca4]/20 text-left"
                  >
                    <div className="flex items-center gap-6 mb-4 md:mb-0 w-full md:w-auto">
                      <div className="w-16 h-16 rounded-2xl bg-[#ffd9dd] flex items-center justify-center text-[#b7131a] shrink-0">
                        <span className="material-symbols-outlined text-3xl" style={{ fontVariationSettings: "'FILL' 1" }}>
                          description
                        </span>
                      </div>
                      <div className="flex-1 min-w-0">
                        <h4 className="text-lg font-bold text-[#4d2128] group-hover:text-[#b7131a] transition-colors truncate">
                          {app.data?.serviceName || app.serviceId || 'Hồ sơ hành chính'}
                        </h4>
                        <div className="flex items-center gap-4 mt-1 flex-wrap">
                          <span className="flex items-center gap-1 text-sm text-[#9f364c]">
                            <Clock className="w-3.5 h-3.5" />
                            Nộp: {fmtDate(app.createdAt)}
                          </span>
                          <span className={`text-xs font-black uppercase tracking-wide px-3 py-0.5 rounded-full ${meta.chip}`}>
                            {meta.label}
                          </span>
                        </div>
                        <div className="mt-2 w-48 h-1.5 bg-[#ffd2d6] rounded-full">
                          <div className="h-1.5 bg-[#b7131a] rounded-full transition-all" style={{ width: `${meta.progress}%` }} />
                        </div>
                      </div>
                    </div>
                    <div className="w-full md:w-auto px-8 py-3 bg-[#ffeced] text-[#b7131a] font-extrabold rounded-xl hover:bg-[#b7131a] hover:text-white transition-all flex items-center justify-center gap-2 shrink-0">
                      <span>Xem</span>
                      <ChevronRight className="w-4 h-4" />
                    </div>
                  </button>
                );
              })}
            </div>
          )}
        </section>

        {/* Featured Categories */}
        <section className="mt-16">
          <div className="flex flex-col md:flex-row gap-6">
            {/* Main CTA card */}
            <div className="flex-1 bg-gradient-to-br from-[#b7131a] to-[#ff766b] rounded-[2rem] p-10 text-white relative overflow-hidden group">
              <div className="absolute bottom-0 right-0 p-4 opacity-20 translate-y-4 group-hover:translate-y-0 transition-transform pointer-events-none">
                <span className="material-symbols-outlined text-[120px]">verified_user</span>
              </div>
              <h5 className="text-2xl font-bold mb-4">Thủ tục nhanh chóng</h5>
              <p className="text-white/80 max-w-xs mb-8 text-sm leading-relaxed">
                Tra cứu và xử lý các loại hồ sơ đất đai, hộ khẩu và tư pháp chỉ trong vài phút.
              </p>
              <button
                onClick={() => onNavigate('submit')}
                className="px-6 py-3 bg-white text-[#b7131a] font-bold rounded-xl shadow-lg hover:bg-[#ffefed] transition-colors text-sm"
              >
                Nộp hồ sơ ngay
              </button>
            </div>

            {/* Side cards */}
            <div className="md:w-72 flex flex-col gap-6">
              <div className="bg-[#ffd9dd] rounded-[2rem] p-8">
                <div className="w-12 h-12 bg-[#fdc003] rounded-full flex items-center justify-center mb-4">
                  <span className="material-symbols-outlined text-[#3d2b00]">history</span>
                </div>
                <h6 className="text-xl font-bold text-[#4d2128] mb-2">Lịch sử tra cứu</h6>
                <p className="text-sm text-[#9f364c]">Xem lại các hồ sơ bạn đã tra cứu gần đây.</p>
              </div>
              <div className="bg-white border border-[#de9ca4]/20 rounded-[2rem] p-8">
                <div className="w-12 h-12 bg-[#ffc2c9] rounded-full flex items-center justify-center mb-4">
                  <span className="material-symbols-outlined text-[#852139]">help</span>
                </div>
                <h6 className="text-xl font-bold text-[#4d2128] mb-2">Trung tâm hỗ trợ</h6>
                <p className="text-sm text-[#9f364c]">Hướng dẫn chi tiết về các loại giấy tờ.</p>
              </div>
            </div>
          </div>
        </section>

      </main>

      {/* ── Footer ── */}
      <footer className="mt-auto py-8 px-10 border-t border-[#de9ca4]/10 flex flex-col md:flex-row justify-between items-center text-xs text-[#9f364c] font-medium opacity-60">
        <p>© 2024 Cổng dịch vụ công Quốc gia. All rights reserved.</p>
        <div className="flex gap-6 mt-4 md:mt-0">
          {['Điều khoản sử dụng', 'Chính sách bảo mật', 'Liên hệ hỗ trợ'].map(t => (
            <button key={t} className="hover:text-[#b7131a] transition-colors">{t}</button>
          ))}
        </div>
      </footer>

      {/* ── Mobile Bottom Nav ── */}
      <nav className="md:hidden fixed bottom-0 left-0 w-full bg-[#fff4f4]/90 backdrop-blur-md border-t border-[#ffeced] flex justify-around items-center py-3 px-2 z-50">
        {([
          { label: 'Trang chủ', icon: 'home',          active: false, action: () => onNavigate('home')   },
          { label: 'Tra cứu',   icon: 'manage_search',  active: true,  action: () => {}                  },
          { label: 'Hồ sơ',     icon: 'description',   active: false, action: () => onNavigate('submit') },
          { label: 'Cá nhân',   icon: 'person',         active: false, action: () => {}                  },
        ]).map(({ label, icon, active, action }) => (
          <button key={label} onClick={action} className={`flex flex-col items-center gap-1 transition-colors ${active ? 'text-[#b7131a]' : 'text-[#4d2128]/60'}`}>
            <span className="material-symbols-outlined text-[22px]" style={{ fontVariationSettings: active ? "'FILL' 1" : "'FILL' 0" }}>{icon}</span>
            <span className="text-[10px] font-bold">{label}</span>
          </button>
        ))}
      </nav>

    </div>
  );
}
