/**
 * AdminAppointmentsScreen — Quản lý lịch hẹn
 *
 * Hai chế độ:
 *  - Danh sách : timeline nhóm theo ngày, card accent-bar theo trạng thái
 *  - Lịch       : mini calendar tháng + dots hiển thị số lịch, click ngày xem chi tiết
 *
 * API:
 *  GET  /api/appointments/all          → danh sách tất cả lịch hẹn (admin)
 *  PATCH /api/appointments/:id/status  → cập nhật trạng thái
 */
import React, { useState, useEffect, useCallback, useMemo } from 'react';
import {
  CalendarDays, List, Search, RefreshCw, Clock, Phone,
  MapPin, User, CheckCircle2, XCircle, AlertCircle,
  ChevronLeft, ChevronRight, Inbox, Calendar, Building2,
  Hash, FileText,
} from 'lucide-react';
import * as adminSvc from '../services/adminService';

interface Props { onNavigate: (s: string, p?: any) => void }

const PRIMARY = '#8f000d';
const GOLD    = '#fcd400';

// ── Status config ──────────────────────────────────────────────────────────────
const S: Record<string, { label: string; bar: string; chip: string }> = {
  pending:   { label: 'Chờ đến',  bar: '#d97706', chip: 'bg-amber-100 text-amber-700'           },
  completed: { label: 'Đã đến',   bar: '#16a34a', chip: 'bg-green-100 text-green-700'           },
  cancelled: { label: 'Đã hủy',   bar: '#c8a0a8', chip: 'bg-[#fff4f4] text-[#9f364c]/60'       },
};

// ── Helpers ────────────────────────────────────────────────────────────────────
const toDateStr = (d: Date) =>
  `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;

const todayISO = () => toDateStr(new Date());

function fmtDate(s: string) {
  if (!s) return '–';
  const [y, m, d] = s.split('-');
  return `${d}/${m}/${y}`;
}

function dateSectionLabel(s: string) {
  const today    = todayISO();
  const tomorrow = toDateStr(new Date(Date.now() + 86400000));
  if (s === today)    return { main: 'Hôm nay',   sub: fmtDate(s) };
  if (s === tomorrow) return { main: 'Ngày mai',  sub: fmtDate(s) };
  const d = new Date(s);
  const weekday = d.toLocaleDateString('vi-VN', { weekday: 'long' });
  return { main: weekday.charAt(0).toUpperCase() + weekday.slice(1), sub: fmtDate(s) };
}

function initials(name: string) {
  return (name || '?').trim().split(/\s+/).slice(-2).map(w => w[0]).join('').toUpperCase();
}

// ── Toast ──────────────────────────────────────────────────────────────────────
function Toast({ text, ok }: { text: string; ok: boolean }) {
  return (
    <div className={`fixed bottom-24 left-1/2 -translate-x-1/2 z-50 px-4 py-2.5 rounded-full
      shadow-xl text-sm font-semibold text-white flex items-center gap-2 whitespace-nowrap
      ${ok ? 'bg-green-600' : 'bg-red-700'}`}>
      {ok ? <CheckCircle2 className="w-4 h-4" /> : <AlertCircle className="w-4 h-4" />}
      {text}
    </div>
  );
}

// ── Detail Modal ───────────────────────────────────────────────────────────────
function DetailModal({ apt, onClose, onStatusChange }: {
  apt: any;
  onClose(): void;
  onStatusChange(id: string, s: string): Promise<void>;
}) {
  const cfg     = S[apt.status] ?? S.pending;
  const [busy, setBusy] = useState(false);

  const doChange = async (newStatus: string) => {
    setBusy(true);
    await onStatusChange(apt.id, newStatus);
    setBusy(false);
    onClose();
  };

  const rows = [
    { Icon: Clock,     label: 'Thời gian',       val: `${apt.time || '–'}  ·  ${fmtDate(apt.date)}` },
    { Icon: Phone,     label: 'Số điện thoại',    val: apt.phone      || '–' },
    { Icon: Building2, label: 'Cơ quan',          val: apt.agencyId   || '–' },
    { Icon: FileText,  label: 'Dịch vụ',          val: apt.serviceCode || apt.serviceName || '–' },
    { Icon: Hash,      label: 'Mã lịch hẹn',      val: apt.id ? String(apt.id).slice(0, 14).toUpperCase() : '–' },
    { Icon: User,      label: 'Người đặt',        val: apt.fullName   || '–' },
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 px-4">
      <div className="bg-white rounded-2xl w-full max-w-sm shadow-2xl overflow-hidden">

        {/* Top accent */}
        <div className="h-1.5 w-full" style={{ backgroundColor: cfg.bar }} />

        <div className="p-5">
          {/* Header */}
          <div className="flex items-start justify-between mb-5">
            <div>
              <p className="text-[10px] font-bold tracking-[0.18em] uppercase text-[#9f364c]/40 mb-1">
                Chi tiết lịch hẹn
              </p>
              <h3 className="text-lg font-black text-[#4d2128] leading-tight">
                {apt.fullName || 'Không rõ'}
              </h3>
            </div>
            <span className={`px-2.5 py-1 rounded-full text-[10px] font-bold flex-shrink-0 ml-2 ${cfg.chip}`}>
              {cfg.label}
            </span>
          </div>

          {/* Info rows */}
          <div className="space-y-3 mb-5">
            {rows.map(({ Icon, label, val }) => (
              <div key={label} className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-xl bg-[#fff4f4] flex items-center justify-center flex-shrink-0">
                  <Icon className="w-3.5 h-3.5 text-[#9f364c]/60" />
                </div>
                <div className="min-w-0">
                  <p className="text-[10px] text-[#9f364c]/40 font-medium">{label}</p>
                  <p className="text-sm font-semibold text-[#4d2128] truncate leading-tight">{val}</p>
                </div>
              </div>
            ))}
          </div>

          {/* Note */}
          {apt.note && (
            <div className="bg-[#fff4f4] rounded-xl p-3 border-l-4 border-amber-400 mb-5">
              <p className="text-[10px] text-[#9f364c]/40 font-medium mb-0.5">Ghi chú</p>
              <p className="text-sm text-[#4d2128]">{apt.note}</p>
            </div>
          )}

          {/* Actions (only for pending) */}
          {apt.status === 'pending' && (
            <div className="flex gap-2.5 mb-3">
              <button
                onClick={() => doChange('cancelled')}
                disabled={busy}
                className="flex-1 h-10 rounded-xl border border-[#de9ca4]/30 text-sm font-semibold
                  text-[#4d2128]/70 hover:bg-[#fff4f4] transition-colors flex items-center
                  justify-center gap-1.5 disabled:opacity-50">
                <XCircle className="w-3.5 h-3.5" />
                Hủy lịch
              </button>
              <button
                onClick={() => doChange('completed')}
                disabled={busy}
                className="flex-1 h-10 rounded-xl bg-green-600 text-white text-sm font-semibold
                  hover:bg-green-700 transition-colors flex items-center justify-center gap-1.5
                  disabled:opacity-50">
                <CheckCircle2 className="w-3.5 h-3.5" />
                Xác nhận đến
              </button>
            </div>
          )}

          <button
            onClick={onClose}
            className="w-full h-10 rounded-xl border border-[#de9ca4]/25 text-sm font-semibold
              text-[#4d2128]/60 hover:bg-[#fff4f4] transition-colors">
            Đóng
          </button>
        </div>
      </div>
    </div>
  );
}

// ── Appointment Card ───────────────────────────────────────────────────────────
function AptCard({ apt, onClick }: { apt: any; onClick(): void }) {
  const cfg  = S[apt.status] ?? S.pending;
  const ini  = initials(apt.fullName || '');
  const wday = apt.date
    ? new Date(apt.date).toLocaleDateString('vi-VN', { weekday: 'short' })
    : '';

  return (
    <button
      onClick={onClick}
      className="w-full bg-white rounded-2xl border border-[#de9ca4]/15 shadow-sm
        overflow-hidden flex items-stretch text-left hover:shadow-md transition-all
        active:scale-[0.99] group">
      {/* Accent bar */}
      <div className="w-1 flex-shrink-0 transition-all group-hover:w-1.5"
        style={{ backgroundColor: cfg.bar }} />

      <div className="flex-1 flex items-center gap-3 px-3.5 py-3 min-w-0">
        {/* Time column */}
        <div className="w-12 flex-shrink-0 text-center">
          <p className="text-sm font-black text-[#4d2128] leading-none tabular-nums">
            {apt.time || '–'}
          </p>
          <p className="text-[9px] text-[#9f364c]/40 font-semibold mt-0.5 uppercase tracking-wide">
            {wday}
          </p>
        </div>

        {/* Divider */}
        <div className="w-px h-8 bg-[#de9ca4]/20 flex-shrink-0" />

        {/* Avatar */}
        <div className="w-9 h-9 rounded-xl flex-shrink-0 flex items-center justify-center
          text-[11px] font-black text-white select-none"
          style={{ backgroundColor: cfg.bar }}>
          {ini}
        </div>

        {/* Info */}
        <div className="flex-1 min-w-0">
          <p className="text-sm font-bold text-[#4d2128] truncate leading-tight">
            {apt.fullName || 'Không rõ'}
          </p>
          <p className="text-[11px] text-[#9f364c]/55 truncate mt-0.5">
            {apt.phone || '–'}
            {apt.agencyId ? ` · ${apt.agencyId}` : ''}
          </p>
        </div>

        {/* Badge */}
        <span className={`flex-shrink-0 px-2 py-0.5 rounded-full text-[9px] font-bold
          whitespace-nowrap ${cfg.chip}`}>
          {cfg.label}
        </span>
      </div>
    </button>
  );
}

// ── Mini Calendar ──────────────────────────────────────────────────────────────
function MiniCalendar({
  appointments, selectedDate, onSelect,
}: {
  appointments: any[];
  selectedDate: string;
  onSelect(d: string): void;
}) {
  const now    = new Date();
  const [yr,  setYr]  = useState(now.getFullYear());
  const [mo,  setMo]  = useState(now.getMonth());

  const daysInMonth = new Date(yr, mo + 1, 0).getDate();
  const firstWday   = new Date(yr, mo, 1).getDay(); // 0=Sun
  const offset      = firstWday === 0 ? 6 : firstWday - 1; // Mon=0

  const apptMap = useMemo(() => {
    const m: Record<string, { total: number; pending: number }> = {};
    for (const a of appointments) {
      if (!a.date) continue;
      m[a.date] ??= { total: 0, pending: 0 };
      m[a.date].total++;
      if (a.status === 'pending') m[a.date].pending++;
    }
    return m;
  }, [appointments]);

  const prev = () => mo === 0 ? (setYr(y => y - 1), setMo(11)) : setMo(m => m - 1);
  const next = () => mo === 11 ? (setYr(y => y + 1), setMo(0))  : setMo(m => m + 1);

  const MONTHS = ['Tháng 1','Tháng 2','Tháng 3','Tháng 4','Tháng 5','Tháng 6',
                   'Tháng 7','Tháng 8','Tháng 9','Tháng 10','Tháng 11','Tháng 12'];
  const DAYS   = ['T2','T3','T4','T5','T6','T7','CN'];

  const cells = [
    ...Array<null>(offset).fill(null),
    ...Array.from({ length: daysInMonth }, (_, i) => i + 1),
  ];

  const todayStr = todayISO();

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-[#de9ca4]/15 p-4">
      {/* Month nav */}
      <div className="flex items-center justify-between mb-4">
        <button onClick={prev}
          className="w-8 h-8 rounded-xl hover:bg-[#fff4f4] flex items-center justify-center
            transition-colors text-[#4d2128]">
          <ChevronLeft className="w-4 h-4" />
        </button>
        <span className="text-sm font-bold text-[#4d2128]">{MONTHS[mo]} {yr}</span>
        <button onClick={next}
          className="w-8 h-8 rounded-xl hover:bg-[#fff4f4] flex items-center justify-center
            transition-colors text-[#4d2128]">
          <ChevronRight className="w-4 h-4" />
        </button>
      </div>

      {/* Day-of-week headers */}
      <div className="grid grid-cols-7 mb-1.5">
        {DAYS.map(d => (
          <div key={d} className="text-center text-[9px] font-bold text-[#9f364c]/40 uppercase py-1">
            {d}
          </div>
        ))}
      </div>

      {/* Day cells */}
      <div className="grid grid-cols-7 gap-0.5">
        {cells.map((day, i) => {
          if (!day) return <div key={`e${i}`} />;
          const ds   = `${yr}-${String(mo + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
          const info = apptMap[ds];
          const isSel   = ds === selectedDate;
          const isToday = ds === todayStr;

          return (
            <button
              key={i}
              onClick={() => onSelect(isSel ? '' : ds)}
              className={`relative flex flex-col items-center justify-center h-9 rounded-xl
                text-xs font-semibold transition-all
                ${isSel
                  ? 'text-white shadow-sm'
                  : isToday
                  ? 'bg-[#fff0f0] text-[#8f000d] font-black ring-1 ring-[#8f000d]/20'
                  : 'text-[#4d2128] hover:bg-[#fff4f4]'}`}
              style={isSel ? { backgroundColor: PRIMARY } : undefined}
            >
              {day}
              {/* Dot indicator */}
              {info && (
                <span
                  className="absolute bottom-1 w-1.5 h-1.5 rounded-full"
                  style={{
                    backgroundColor: isSel
                      ? 'rgba(255,255,255,0.7)'
                      : info.pending > 0 ? '#d97706' : '#16a34a',
                  }}
                />
              )}
            </button>
          );
        })}
      </div>

      {/* Legend */}
      <div className="flex items-center gap-4 mt-3 pt-3 border-t border-[#de9ca4]/15">
        <div className="flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-amber-500" />
          <span className="text-[9px] text-[#9f364c]/50 font-medium">Chờ đến</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-green-500" />
          <span className="text-[9px] text-[#9f364c]/50 font-medium">Đã hoàn thành</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full" style={{ backgroundColor: PRIMARY }} />
          <span className="text-[9px] text-[#9f364c]/50 font-medium">Ngày đang chọn</span>
        </div>
      </div>
    </div>
  );
}

// ════════════════════════════════════════════════════════════════════════════════
// MAIN EXPORT
// ════════════════════════════════════════════════════════════════════════════════
export function AdminAppointmentsScreen({ onNavigate }: Props) {
  const [items,    setItems]    = useState<any[]>([]);
  const [loading,  setLoading]  = useState(true);
  const [view,     setView]     = useState<'list' | 'calendar'>('list');
  const [q,        setQ]        = useState('');
  const [filter,   setFilter]   = useState('');
  const [selDate,  setSelDate]  = useState('');
  const [detail,   setDetail]   = useState<any>(null);
  const [toast,    setToast]    = useState<{ text: string; ok: boolean } | null>(null);

  const showToast = (text: string, ok: boolean) => {
    setToast({ text, ok });
    setTimeout(() => setToast(null), 3200);
  };

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const r    = await adminSvc.getAppointments();
      const data: any[] = r.data?.appointments ?? r.appointments ?? r.data ?? [];
      data.sort((a, b) => {
        const ka = `${a.date ?? ''} ${a.time ?? ''}`;
        const kb = `${b.date ?? ''} ${b.time ?? ''}`;
        return ka < kb ? -1 : ka > kb ? 1 : 0;
      });
      setItems(data);
    } catch {
      showToast('Không tải được lịch hẹn', false);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  // ── KPIs ────────────────────────────────────────────────────────────────────
  const today = todayISO();
  const kpi = useMemo(() => {
    const todayList = items.filter(a => a.date === today);
    return {
      total:        items.length,
      pending:      items.filter(a => a.status === 'pending').length,
      completed:    items.filter(a => a.status === 'completed').length,
      todayTotal:   todayList.length,
      todayPending: todayList.filter(a => a.status === 'pending').length,
    };
  }, [items, today]);

  // ── Filtered list ────────────────────────────────────────────────────────────
  const filtered = useMemo(() => {
    let arr = items;
    if (filter)   arr = arr.filter(a => a.status === filter);
    if (view === 'calendar' && selDate) arr = arr.filter(a => a.date === selDate);
    if (q) {
      const kw = q.toLowerCase();
      arr = arr.filter(a =>
        (a.fullName   || '').toLowerCase().includes(kw) ||
        (a.phone      || '').includes(kw)               ||
        (a.agencyId   || '').toLowerCase().includes(kw) ||
        String(a.id   || '').toLowerCase().includes(kw),
      );
    }
    return arr;
  }, [items, filter, q, view, selDate]);

  // Group by date (list view)
  const grouped = useMemo(() => {
    const map: Record<string, any[]> = {};
    for (const a of filtered) {
      const d = a.date || 'unknown';
      (map[d] ??= []).push(a);
    }
    return Object.entries(map).sort(([a], [b]) => a.localeCompare(b));
  }, [filtered]);

  // ── Status update ────────────────────────────────────────────────────────────
  const handleStatusChange = useCallback(async (id: string, status: string) => {
    setItems(prev => prev.map(a => a.id === id ? { ...a, status } : a));
    try {
      await adminSvc.updateAppointmentStatus(id, status);
      showToast(status === 'completed' ? '✓ Đã xác nhận' : 'Đã hủy lịch hẹn', true);
    } catch {
      load();
      showToast('Không cập nhật được', false);
    }
  }, [load]);

  // ── Render ───────────────────────────────────────────────────────────────────
  return (
    <div className="min-h-full bg-transparent">
      {toast  && <Toast text={toast.text} ok={toast.ok} />}
      {detail && (
        <DetailModal
          apt={detail}
          onClose={() => setDetail(null)}
          onStatusChange={handleStatusChange}
        />
      )}

      {/* ── Hero ──────────────────────────────────────────────────────────── */}
      <div className="relative overflow-hidden"
        style={{ background: 'linear-gradient(140deg, #1c0003 0%, #3d0008 55%, #1c0003 100%)' }}>
        {/* Grid overlay */}
        <div className="absolute inset-0 opacity-[0.04]"
          style={{
            backgroundImage:
              'repeating-linear-gradient(0deg,#fff,#fff 1px,transparent 1px,transparent 32px),' +
              'repeating-linear-gradient(90deg,#fff,#fff 1px,transparent 1px,transparent 32px)',
          }} />
        {/* Radial glow */}
        <div className="absolute -top-10 -right-10 w-52 h-52 rounded-full opacity-[0.06]"
          style={{ background: 'radial-gradient(circle, #fcd400 0%, transparent 70%)' }} />

        <div className="relative px-5 pt-5 pb-6">
          {/* Top row */}
          <div className="flex items-center justify-between mb-3">
            <p className="text-[10px] font-bold uppercase tracking-[0.2em] text-red-300/60">
              Quản trị · Lịch hẹn
            </p>
            <button onClick={load}
              className="p-1.5 rounded-lg text-white/30 hover:text-white/70
                hover:bg-white/10 transition-colors">
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            </button>
          </div>

          <h1 className="text-3xl font-black text-white leading-none mb-5 tracking-tight">
            Lịch hẹn<span style={{ color: GOLD }}>.</span>
          </h1>

          {/* KPI 2×2 grid */}
          <div className="grid grid-cols-2 gap-2">
            {[
              { label: 'Tổng lịch hẹn',   value: kpi.total,        bg: 'bg-white/10',           text: 'text-white'          },
              { label: 'Hôm nay',          value: kpi.todayTotal,   bg: 'bg-[#fcd400]/15',       text: 'text-[#fcd400]'      },
              { label: 'Chờ xác nhận',     value: kpi.pending,      bg: 'bg-amber-500/15',       text: 'text-amber-300'      },
              { label: 'Đã hoàn thành',    value: kpi.completed,    bg: 'bg-emerald-500/15',     text: 'text-emerald-300'    },
            ].map(({ label, value, bg, text }) => (
              <div key={label} className={`${bg} rounded-xl px-3.5 py-3`}>
                <p className={`text-2xl font-black ${text} leading-none tabular-nums`}>{value}</p>
                <p className={`text-[10px] ${text} opacity-60 font-medium mt-1`}>{label}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* ── View toggle ────────────────────────────────────────────────────── */}
      <div className="px-4 pt-4">
        <div className="flex bg-white rounded-2xl shadow-sm border border-[#de9ca4]/15 p-1 gap-1">
          {([
            { key: 'list'     as const, label: 'Danh sách', Icon: List        },
            { key: 'calendar' as const, label: 'Lịch tháng', Icon: CalendarDays },
          ]).map(({ key, label, Icon }) => (
            <button
              key={key}
              onClick={() => setView(key)}
              className={`flex-1 flex items-center justify-center gap-1.5 py-2.5 rounded-xl
                text-xs font-bold transition-all
                ${view === key
                  ? 'text-white shadow-sm'
                  : 'text-[#9f364c]/50 hover:text-[#9f364c]'}`}
              style={view === key ? { backgroundColor: PRIMARY } : undefined}
            >
              <Icon className="w-3.5 h-3.5" />
              {label}
            </button>
          ))}
        </div>
      </div>

      {/* ── Filters ────────────────────────────────────────────────────────── */}
      <div className="px-4 pt-3 space-y-2.5">
        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-[#9f364c]/35" />
          <input
            value={q}
            onChange={e => setQ(e.target.value)}
            placeholder="Tên, SĐT, cơ quan, mã lịch hẹn..."
            className="w-full pl-10 pr-4 h-10 bg-white rounded-xl border border-[#de9ca4]/25
              text-sm text-[#4d2128] placeholder:text-[#9f364c]/30 shadow-sm
              outline-none focus:border-[#8f000d]/40 transition-colors"
          />
        </div>

        {/* Status chips */}
        <div className="flex gap-2 pb-0.5 overflow-x-auto no-scrollbar">
          {[
            { v: '',          l: 'Tất cả' },
            { v: 'pending',   l: 'Chờ đến' },
            { v: 'completed', l: 'Đã đến' },
            { v: 'cancelled', l: 'Đã hủy' },
          ].map(o => (
            <button
              key={o.v}
              onClick={() => setFilter(o.v)}
              className={`flex-shrink-0 px-3 py-1.5 rounded-full text-xs font-semibold
                transition-all ${filter === o.v
                  ? 'text-white shadow-sm'
                  : 'bg-white text-[#9f364c]/70 border border-[#de9ca4]/30 hover:bg-[#de9ca4]/15'}`}
              style={filter === o.v ? { backgroundColor: PRIMARY } : undefined}
            >
              {o.l}
            </button>
          ))}
        </div>
      </div>

      {/* ── Content ────────────────────────────────────────────────────────── */}
      <div className="px-4 pt-4 pb-6">

        {loading ? (
          /* Loading */
          <div className="flex flex-col items-center justify-center py-20 gap-3">
            <RefreshCw className="w-7 h-7 animate-spin text-[#9f364c]/35" />
            <p className="text-sm text-[#9f364c]/50 font-medium">Đang tải...</p>
          </div>

        ) : view === 'list' ? (
          /* ── LIST VIEW ─────────────────────────────────────────────────── */
          <div className="space-y-7">
            {grouped.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-20 gap-3">
                <div className="w-16 h-16 rounded-2xl bg-[#fff4f4] flex items-center justify-center">
                  <Inbox className="w-8 h-8 text-[#de9ca4]/60" />
                </div>
                <p className="text-sm font-semibold text-[#9f364c]/60">Không có lịch hẹn</p>
                <p className="text-[11px] text-[#9f364c]/40">Thử bỏ bộ lọc hoặc tìm kiếm</p>
              </div>
            ) : (
              grouped.map(([date, apts]) => {
                const { main, sub } = dateSectionLabel(date);
                return (
                  <div key={date}>
                    {/* Section header */}
                    <div className="flex items-center gap-3 mb-3">
                      <div className="flex-shrink-0">
                        <p className="text-xs font-black text-[#4d2128] leading-tight">{main}</p>
                        <p className="text-[10px] text-[#9f364c]/45 font-medium">{sub}</p>
                      </div>
                      <div className="flex-1 h-px bg-[#de9ca4]/20" />
                      <span className="flex-shrink-0 text-[9px] font-bold text-[#9f364c]/50
                        bg-white border border-[#de9ca4]/25 rounded-full px-2 py-0.5">
                        {apts.length} lịch
                      </span>
                    </div>

                    {/* Cards */}
                    <div className="space-y-2">
                      {apts.map(a => (
                        <AptCard key={a.id} apt={a} onClick={() => setDetail(a)} />
                      ))}
                    </div>
                  </div>
                );
              })
            )}
          </div>

        ) : (
          /* ── CALENDAR VIEW ──────────────────────────────────────────────── */
          <div className="space-y-4">
            <MiniCalendar
              appointments={items}
              selectedDate={selDate}
              onSelect={setSelDate}
            />

            {selDate ? (
              /* Day detail */
              <div>
                <div className="flex items-center gap-3 mb-3">
                  {(() => {
                    const { main, sub } = dateSectionLabel(selDate);
                    return (
                      <div className="flex-shrink-0">
                        <p className="text-xs font-black text-[#4d2128]">{main}</p>
                        <p className="text-[10px] text-[#9f364c]/45 font-medium">{sub}</p>
                      </div>
                    );
                  })()}
                  <div className="flex-1 h-px bg-[#de9ca4]/20" />
                  <span className="text-[9px] font-bold text-[#9f364c]/50 bg-white
                    border border-[#de9ca4]/25 rounded-full px-2 py-0.5">
                    {filtered.length} lịch
                  </span>
                </div>

                {filtered.length === 0 ? (
                  <div className="flex flex-col items-center py-12 gap-2.5">
                    <Calendar className="w-8 h-8 text-[#de9ca4]/50" />
                    <p className="text-sm font-medium text-[#9f364c]/55">Không có lịch hẹn ngày này</p>
                  </div>
                ) : (
                  <div className="space-y-2">
                    {filtered.map(a => (
                      <AptCard key={a.id} apt={a} onClick={() => setDetail(a)} />
                    ))}
                  </div>
                )}
              </div>
            ) : (
              /* No day selected */
              <div className="flex flex-col items-center py-12 gap-3 text-center">
                <div className="w-14 h-14 rounded-2xl bg-[#fff4f4] flex items-center justify-center">
                  <CalendarDays className="w-7 h-7 text-[#de9ca4]/60" />
                </div>
                <div>
                  <p className="text-sm font-semibold text-[#9f364c]/60">Chọn một ngày</p>
                  <p className="text-[11px] text-[#9f364c]/40 mt-0.5">
                    Ngày có dấu chấm <span className="text-amber-500">●</span> đang có lịch hẹn chờ
                  </p>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
