/**
 * AdminQueueManagementScreen — Quản lý hàng đợi (Desktop redesign)
 *
 * Layout: Left 2/3 = 2×2 counter cards + summary strip
 *          Right 1/3 = ticket queue list + hourly bar chart
 *
 * API bindings (unchanged):
 *   GET  /api/queue/summary/:agencyId  → totalWaiting, totalCalled, totalServing, totalDone, total
 *   GET  /api/queue/list/:agencyId     → { data: ticket[] }
 *   POST /api/queue/call-next          → { agencyId, counterNo }   ← per-counter int
 *   PUT  /api/queue/ticket/:id/status  → serving | done | absent | cancelled
 *   GET  /api/queue/counters/:agencyId → { counterNo, isActive, operatorName }
 */
import React, { useState, useEffect, useCallback } from 'react';
import {
  RefreshCw, ChevronDown, Clock, CheckCircle2,
  AlertCircle, Inbox, BellRing, XCircle, Users,
  Wifi, WifiOff, BarChart2,
} from 'lucide-react';
import * as adminSvc from '../services/adminService';

interface Props { onNavigate: (s: string, p?: any) => void }

// ── Constants ─────────────────────────────────────────────────────────────────
const PRIMARY = '#8f000d';

const AGENCIES = [
  { id: 'ubnd-thanhhoa',    name: 'UBND tỉnh Thanh Hóa' },
  { id: 'ubnd-tp-thanhhoa', name: 'UBND TP Thanh Hóa' },
  { id: 'bql-nghi-son',     name: 'Ban Quản lý KKT Nghi Sơn' },
  { id: 'so-tu-phap',       name: 'Sở Tư pháp Thanh Hóa' },
  { id: 'so-tttt-thanhhoa', name: 'Sở TT&TT Thanh Hóa' },
];

// Fallback 4 counters when API returns nothing
const DEFAULT_COUNTERS = [
  { counterNo: 1, isActive: true,  operatorName: '',  serviceName: 'Đăng ký dân sự' },
  { counterNo: 2, isActive: true,  operatorName: '',  serviceName: 'Cấp phép xây dựng' },
  { counterNo: 3, isActive: true,  operatorName: '',  serviceName: 'Giải quyết khiếu nại' },
  { counterNo: 4, isActive: false, operatorName: '',  serviceName: 'Dịch vụ hành chính' },
];

const STATUS_COLOR: Record<string, string> = {
  waiting:   'bg-yellow-50 text-yellow-700 border-yellow-200',
  called:    'bg-blue-50 text-blue-700 border-blue-200',
  serving:   'bg-purple-50 text-purple-700 border-purple-200',
  done:      'bg-green-50 text-green-700 border-green-200',
  absent:    'bg-gray-100 text-gray-500 border-gray-200',
  cancelled: 'bg-red-50 text-red-400 border-red-100',
};
const STATUS_LABEL: Record<string, string> = {
  waiting:   'Đang chờ',
  called:    'Đã gọi',
  serving:   'Đang phục vụ',
  done:      'Hoàn thành',
  absent:    'Vắng mặt',
  cancelled: 'Đã hủy',
};

// ── Counter Card ──────────────────────────────────────────────────────────────
function CounterCard({
  counter, servingTicket, waitingCount, onCallNext, isCalling,
}: {
  counter: any;
  servingTicket: any;
  waitingCount: number;
  onCallNext: (n: number) => void;
  isCalling: boolean;
}) {
  const active = counter.isActive !== false;
  const num = String(counter.counterNo).padStart(2, '0');

  return (
    <div
      className={`relative bg-white rounded-2xl shadow-sm border border-[#de9ca4]/20 overflow-hidden
        flex flex-col transition-all duration-200
        ${active ? 'hover:shadow-md' : 'grayscale opacity-60'}`}
    >
      {/* Left accent bar */}
      <div
        className="absolute inset-y-0 left-0 w-1 rounded-l-2xl"
        style={{ backgroundColor: active ? PRIMARY : '#9ca3af' }}
      />

      <div className="pl-5 pr-4 pt-4 pb-4 flex flex-col gap-3">
        {/* ── Header ── */}
        <div className="flex items-start justify-between gap-2">
          <div className="min-w-0">
            <p className="text-[10px] font-semibold tracking-widest text-[#9f364c]/50 uppercase">
              Quầy {num}
            </p>
            <p className="text-sm font-semibold text-gray-700 mt-0.5 leading-tight truncate">
              {counter.serviceName || 'Dịch vụ hành chính'}
            </p>
            {counter.operatorName && (
              <p className="text-[10px] text-gray-400 mt-0.5 truncate">{counter.operatorName}</p>
            )}
          </div>
          <div
            className={`flex items-center gap-1 px-2 py-1 rounded-full text-[10px] font-medium flex-shrink-0
              ${active ? 'bg-green-50 text-green-600' : 'bg-[#fff4f4] text-[#9f364c]/50'}`}
          >
            {active
              ? <Wifi className="w-2.5 h-2.5" />
              : <WifiOff className="w-2.5 h-2.5" />}
            <span>{active ? 'Hoạt động' : 'Tạm dừng'}</span>
          </div>
        </div>

        {/* ── Numbers ── */}
        <div className="flex items-end gap-5">
          <div>
            <p className="text-[10px] text-gray-400 mb-1">Đang phục vụ</p>
            <p
              className="font-black leading-none"
              style={{ fontSize: '3rem', color: active ? PRIMARY : '#9ca3af' }}
            >
              {servingTicket?.ticketNumber ?? '—'}
            </p>
          </div>
          <div className="mb-1">
            <p className="text-[10px] text-gray-400 mb-1">Đang chờ</p>
            <div
              className={`inline-flex items-center gap-1 px-2.5 py-1.5 rounded-xl text-sm font-bold
                ${waitingCount > 0
                  ? 'bg-yellow-50 text-yellow-700 border border-yellow-200'
                  : 'bg-[#fff4f4] text-[#9f364c]/40'}`}
            >
              <Users className="w-3 h-3" />
              <span>{waitingCount}</span>
            </div>
          </div>
        </div>

        {/* ── CTA button ── */}
        <button
          disabled={!active || isCalling}
          onClick={() => onCallNext(counter.counterNo)}
          className={`w-full py-2.5 rounded-xl text-xs font-bold tracking-widest uppercase
            transition-all select-none
            ${active
              ? 'text-white hover:opacity-90 active:scale-[0.98]'
              : 'bg-[#de9ca4]/20 text-[#9f364c]/30 cursor-not-allowed'}`}
          style={active ? { backgroundColor: PRIMARY } : undefined}
        >
          {isCalling
            ? (
              <span className="flex items-center justify-center gap-2">
                <RefreshCw className="w-3 h-3 animate-spin" />
                Đang gọi…
              </span>
            )
            : 'Gọi số tiếp theo'}
        </button>
      </div>
    </div>
  );
}

// ── Hourly bar chart ──────────────────────────────────────────────────────────
function HourlyChart({ tickets }: { tickets: any[] }) {
  const now = new Date();
  const slots = Array.from({ length: 8 }, (_, i) => {
    const h = (now.getHours() - 7 + i + 24) % 24;
    const count = tickets.filter(t => {
      try { return new Date(t.createdAt).getHours() === h; } catch { return false; }
    }).length;
    return { h, count };
  });
  const max = Math.max(...slots.map(s => s.count), 1);

  return (
    <div className="flex items-end gap-1.5" style={{ height: 52 }}>
      {slots.map(({ h, count }) => (
        <div key={h} className="flex-1 flex flex-col items-center gap-1">
          <div className="w-full flex items-end" style={{ height: 40 }}>
            <div
              className="w-full rounded-t transition-all cursor-default"
              style={{
                height: `${Math.max(3, (count / max) * 40)}px`,
                backgroundColor: count > 0 ? PRIMARY : '#fca5a5',
                opacity: count > 0 ? 0.8 : 0.35,
              }}
              title={`${h}h: ${count} vé`}
            />
          </div>
          <span className="text-[9px] text-gray-400">{h}h</span>
        </div>
      ))}
    </div>
  );
}

// ── Queue list item ────────────────────────────────────────────────────────────
function QueueItem({
  ticket, onUpdate,
}: {
  ticket: any;
  onUpdate: (id: string, s: string) => void;
}) {
  const [expanded, setExpanded] = useState(false);
  const canExpand = ['called', 'serving'].includes(ticket.status);

  return (
    <div className="bg-white border border-[#de9ca4]/20 rounded-xl overflow-hidden">
      <div className="flex items-center gap-2.5 px-3 py-2.5">
        {/* Number badge */}
        <div
          className="w-9 h-9 rounded-lg flex flex-col items-center justify-center flex-shrink-0 border"
          style={{ borderColor: '#fca5a5', backgroundColor: '#fff5f5' }}
        >
          <span className="text-[8px] font-semibold text-red-400 leading-none">
            {ticket.prefix ?? 'A'}
          </span>
          <span className="text-xs font-black leading-none" style={{ color: PRIMARY }}>
            {ticket.ticketNumber}
          </span>
        </div>

        {/* Info */}
        <div className="flex-1 min-w-0">
          <p className="text-xs font-semibold text-gray-800 truncate">
            {ticket.userName || 'Khách vãng lai'}
          </p>
          <p className="text-[10px] text-gray-400 truncate">
            {ticket.serviceName || (ticket.counterNo ? `Quầy ${ticket.counterNo}` : '–')}
          </p>
        </div>

        {/* Status + chevron */}
        <div className="flex items-center gap-1.5 flex-shrink-0">
          <span
            className={`px-1.5 py-0.5 rounded-full text-[9px] font-semibold border
              ${STATUS_COLOR[ticket.status] ?? 'bg-gray-100 text-gray-500 border-gray-200'}`}
          >
            {STATUS_LABEL[ticket.status] ?? ticket.status}
          </span>
          {canExpand && (
            <button
              onClick={() => setExpanded(v => !v)}
              className="text-gray-400 hover:text-gray-600 p-0.5"
            >
              <ChevronDown className={`w-3.5 h-3.5 transition-transform ${expanded ? 'rotate-180' : ''}`} />
            </button>
          )}
        </div>
      </div>

      {/* Action row */}
      {expanded && canExpand && (
        <div className="px-3 pb-2.5 pt-2 border-t border-gray-50 flex gap-2">
          {ticket.status === 'called' && (
            <>
              <button
                onClick={() => onUpdate(ticket.id, 'serving')}
                className="flex-1 text-[10px] py-1.5 rounded-lg bg-purple-600 hover:bg-purple-700 text-white font-medium"
              >
                <BellRing className="w-2.5 h-2.5 inline mr-1" />Bắt đầu phục vụ
              </button>
              <button
                onClick={() => onUpdate(ticket.id, 'absent')}
                className="flex-1 text-[10px] py-1.5 rounded-lg border border-orange-200 text-orange-600 hover:bg-orange-50 font-medium"
              >
                Vắng mặt
              </button>
            </>
          )}
          {ticket.status === 'serving' && (
            <>
              <button
                onClick={() => onUpdate(ticket.id, 'done')}
                className="flex-1 text-[10px] py-1.5 rounded-lg bg-green-600 hover:bg-green-700 text-white font-medium"
              >
                <CheckCircle2 className="w-2.5 h-2.5 inline mr-1" />Hoàn thành
              </button>
              <button
                onClick={() => onUpdate(ticket.id, 'cancelled')}
                className="flex-1 text-[10px] py-1.5 rounded-lg border border-red-200 text-red-500 hover:bg-red-50 font-medium"
              >
                <XCircle className="w-2.5 h-2.5 inline mr-1" />Hủy vé
              </button>
            </>
          )}
        </div>
      )}
    </div>
  );
}

// ── Main ──────────────────────────────────────────────────────────────────────
export function AdminQueueManagementScreen({ onNavigate }: Props) {
  const [agencyId,   setAgencyId]   = useState(AGENCIES[0].id);
  const [showPicker, setShowPicker] = useState(false);
  const [summary,    setSummary]    = useState<any>(null);
  const [tickets,    setTickets]    = useState<any[]>([]);
  const [counters,   setCounters]   = useState<any[]>([]);
  const [loading,    setLoading]    = useState(true);
  const [filter,     setFilter]     = useState('');
  /* per-counter calling state: { [counterNo]: boolean } */
  const [callingMap, setCallingMap] = useState<Record<number, boolean>>({});
  const [toast,      setToast]      = useState<{ msg: string; ok: boolean } | null>(null);

  const showToast = (msg: string, ok: boolean) => {
    setToast({ msg, ok });
    setTimeout(() => setToast(null), 3000);
  };

  const load = useCallback(async () => {
    setLoading(true);
    const [sumR, listR, ctrR] = await Promise.allSettled([
      adminSvc.getQueueSummary(agencyId),
      adminSvc.getQueueList(agencyId),
      adminSvc.getCounters(agencyId),
    ]);
    if (sumR.status  === 'fulfilled') setSummary(sumR.value.data   ?? sumR.value);
    if (listR.status === 'fulfilled') setTickets(listR.value.data  ?? []);
    if (ctrR.status  === 'fulfilled') setCounters(ctrR.value.data  ?? ctrR.value.counters ?? []);
    setLoading(false);
  }, [agencyId]);

  useEffect(() => { load(); }, [load]);

  const handleCallNext = async (counterNo: number) => {
    setCallingMap(m => ({ ...m, [counterNo]: true }));
    try {
      const res = await adminSvc.callNextTicket({ agencyId, counterNo });
      const ticket = res.data;
      showToast(
        ticket
          ? `Quầy ${counterNo}: Gọi số ${ticket.prefix ?? 'A'}${ticket.ticketNumber}`
          : 'Không còn vé đang chờ',
        !!ticket,
      );
      load();
    } catch (e: any) {
      showToast(e.message || 'Không thể gọi số', false);
    } finally {
      setCallingMap(m => ({ ...m, [counterNo]: false }));
    }
  };

  const handleUpdateStatus = async (ticketId: string, status: string) => {
    try {
      await adminSvc.updateQueueTicket(ticketId, status);
      showToast(
        status === 'done'      ? 'Đã hoàn thành vé'
          : status === 'absent'    ? 'Đánh dấu vắng mặt'
          : status === 'cancelled' ? 'Đã hủy vé'
          : 'Đã cập nhật trạng thái',
        true,
      );
      load();
    } catch (e: any) {
      showToast(e.message || 'Lỗi cập nhật', false);
    }
  };

  const displayCounters = counters.length > 0 ? counters : DEFAULT_COUNTERS;
  const filtered        = filter ? tickets.filter(t => t.status === filter) : tickets;
  const agencyName      = AGENCIES.find(a => a.id === agencyId)?.name ?? agencyId;

  // Average wait time display
  const avgMin = summary?.avgWaitMinutes as number | undefined;
  const avgWait = avgMin != null
    ? `${String(Math.floor(avgMin / 60)).padStart(2, '0')}:${String(avgMin % 60).padStart(2, '0')}`
    : '–:––';

  return (
    <div className="flex flex-col min-h-full bg-transparent relative">

      {/* ── Toast ─────────────────────────────────────────────────────────── */}
      {toast && (
        <div
          className={`fixed bottom-20 left-1/2 -translate-x-1/2 z-50 px-4 py-2.5 rounded-full
            shadow-lg text-sm font-medium text-white flex items-center gap-2 whitespace-nowrap max-w-xs
            ${toast.ok ? 'bg-green-600' : 'bg-red-700'}`}
        >
          {toast.ok
            ? <CheckCircle2 className="w-4 h-4 flex-shrink-0" />
            : <AlertCircle  className="w-4 h-4 flex-shrink-0" />}
          {toast.msg}
        </div>
      )}

      {/* ── Top bar ───────────────────────────────────────────────────────── */}
      <div className="bg-white/80 border-b border-[#de9ca4]/20 px-4 py-3 flex items-center gap-3 flex-shrink-0 sticky top-0 z-20">
        {/* Title + Agency picker */}
        <div className="flex-1 min-w-0">
          <h2 className="text-sm font-bold text-[#4d2128] leading-tight">Quản lý hàng đợi</h2>

          <div className="relative mt-0.5 inline-block">
            <button
              onClick={() => setShowPicker(v => !v)}
              className="flex items-center gap-1 text-[11px] text-[#9f364c]/60 hover:text-[#9f364c] transition-colors"
            >
              <span className="truncate max-w-[180px]">{agencyName}</span>
              <ChevronDown className={`w-3 h-3 flex-shrink-0 transition-transform ${showPicker ? 'rotate-180' : ''}`} />
            </button>

            {showPicker && (
              <div className="absolute top-full left-0 z-40 bg-white border border-[#de9ca4]/20 rounded-xl
                shadow-xl mt-1 min-w-[220px] overflow-hidden py-1">
                {AGENCIES.map(a => (
                  <button key={a.id}
                    onClick={() => { setAgencyId(a.id); setShowPicker(false); }}
                    className={`w-full px-3 py-2 text-left text-xs hover:bg-[#fff4f4] transition-colors
                      ${agencyId === a.id ? 'font-semibold bg-[#fff0f0]' : 'text-[#4d2128]/70'}`}
                    style={agencyId === a.id ? { color: PRIMARY } : undefined}
                  >
                    {a.name}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Stat chips + refresh */}
        <div className="flex items-center gap-2 flex-shrink-0">
          <div className="hidden sm:flex items-center gap-1.5 bg-yellow-50 border border-yellow-200 rounded-full px-3 py-1.5">
            <Users className="w-3 h-3 text-yellow-600" />
            <span className="text-xs font-semibold text-yellow-700">
              Tổng chờ:&nbsp;<strong>{summary?.totalWaiting ?? '—'}</strong>
            </span>
          </div>
          <div className="hidden sm:flex items-center gap-1.5 bg-blue-50 border border-blue-200 rounded-full px-3 py-1.5">
            <Clock className="w-3 h-3 text-blue-600" />
            <span className="text-xs font-semibold text-blue-700">
              TB:&nbsp;<strong>{avgWait}</strong>
            </span>
          </div>
          <button
            onClick={load}
            className="p-2 rounded-xl hover:bg-[#fff4f4] text-[#9f364c]/50 hover:text-[#9f364c] transition-colors"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* ── Content ───────────────────────────────────────────────────────── */}
      {loading ? (
        <div className="flex-1 flex items-center justify-center py-16">
          <RefreshCw className="w-6 h-6 animate-spin" style={{ color: PRIMARY }} />
        </div>
      ) : (
        <div className="flex-1 flex flex-col lg:flex-row">

          {/* ── LEFT: Counter grid + summary ─────────────────────────────── */}
          <div className="lg:flex-[2] p-4 lg:p-5 overflow-y-auto">

            {/* 2 × 2 counter grid */}
            <div className="grid grid-cols-2 gap-3 mb-4">
              {displayCounters.slice(0, 4).map(ctr => {
                const serving = tickets.find(
                  t => t.counterNo === ctr.counterNo &&
                       ['serving', 'called'].includes(t.status),
                );
                return (
                  <CounterCard
                    key={ctr.counterNo}
                    counter={ctr}
                    servingTicket={serving}
                    waitingCount={summary?.totalWaiting ?? 0}
                    onCallNext={handleCallNext}
                    isCalling={!!callingMap[ctr.counterNo]}
                  />
                );
              })}
            </div>

            {/* Summary strip */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
              {[
                {
                  label: 'Đang chờ',
                  value: summary?.totalWaiting ?? 0,
                  textCls: 'text-yellow-600',
                  bgCls:   'bg-yellow-50 border-yellow-100',
                },
                {
                  label: 'Đang phục vụ',
                  value: (summary?.totalServing ?? 0) + (summary?.totalCalled ?? 0),
                  textCls: 'text-purple-600',
                  bgCls:   'bg-purple-50 border-purple-100',
                },
                {
                  label: 'Hoàn thành',
                  value: summary?.totalDone ?? 0,
                  textCls: 'text-green-600',
                  bgCls:   'bg-green-50 border-green-100',
                },
                {
                  label: 'Tổng hôm nay',
                  value: summary?.total ?? 0,
                  textCls: 'text-blue-600',
                  bgCls:   'bg-blue-50 border-blue-100',
                },
              ].map(({ label, value, textCls, bgCls }) => (
                <div key={label} className={`${bgCls} border rounded-2xl p-3 text-center`}>
                  <p className={`text-2xl font-black ${textCls}`}>{value}</p>
                  <p className="text-[10px] text-[#4d2128]/60 mt-0.5 leading-tight">{label}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Divider (desktop only) */}
          <div className="hidden lg:block w-px bg-[#de9ca4]/20 flex-shrink-0 my-4" />

          {/* ── RIGHT: Queue list + chart ─────────────────────────────────── */}
          <div className="lg:flex-1 flex flex-col border-t lg:border-t-0 border-[#de9ca4]/20 min-h-0">

            {/* Filter tabs */}
            <div className="px-3 pt-3 pb-2 flex-shrink-0 flex gap-1.5 overflow-x-auto no-scrollbar">
              {[
                { v: '',          l: 'Tất cả' },
                { v: 'waiting',   l: 'Chờ' },
                { v: 'called',    l: 'Đã gọi' },
                { v: 'serving',   l: 'Phục vụ' },
                { v: 'done',      l: 'Xong' },
              ].map(o => {
                const cnt = o.v ? tickets.filter(t => t.status === o.v).length : tickets.length;
                return (
                  <button
                    key={o.v}
                    onClick={() => setFilter(o.v)}
                    className={`flex-shrink-0 px-2.5 py-1 rounded-full text-[10px] font-semibold transition-all
                      ${filter === o.v
                        ? 'text-white shadow-sm'
                        : 'bg-[#fff4f4] text-[#9f364c]/70 hover:bg-[#de9ca4]/20 border border-[#de9ca4]/30'}`}
                    style={filter === o.v ? { backgroundColor: PRIMARY } : undefined}
                  >
                    {o.l}
                    <span className="ml-1 opacity-60">({cnt})</span>
                  </button>
                );
              })}
            </div>

            {/* Ticket list */}
            <div className="flex-1 overflow-y-auto px-3 pb-3 space-y-1.5 min-h-0"
              style={{ maxHeight: 'calc(100vh - 340px)' }}>
              {filtered.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-10 gap-2 text-[#9f364c]/50">
                  <Inbox className="w-8 h-8" />
                  <p className="text-xs">Không có vé nào</p>
                </div>
              ) : (
                filtered.map(t => (
                  <QueueItem key={t.id} ticket={t} onUpdate={handleUpdateStatus} />
                ))
              )}
            </div>

            {/* Hourly chart */}
            <div className="border-t border-[#de9ca4]/20 px-3 py-3 flex-shrink-0 bg-white">
              <div className="flex items-center justify-between mb-2.5">
                <span className="text-[10px] font-semibold text-[#9f364c]/60 flex items-center gap-1.5">
                  <BarChart2 className="w-3 h-3" />
                  Lưu lượng theo giờ
                </span>
                <span className="text-[9px] text-[#9f364c]/40">
                  {new Date().toLocaleDateString('vi-VN')}
                </span>
              </div>
              <HourlyChart tickets={tickets} />
            </div>
          </div>

        </div>
      )}
    </div>
  );
}
