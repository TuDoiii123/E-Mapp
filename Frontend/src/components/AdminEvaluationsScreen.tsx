/**
 * AdminEvaluationsScreen — Quản lý đánh giá  (Desktop redesign)
 *
 * Layout matching HTML design:
 *   • Hero banner + large headline
 *   • 3-col bento stats (Điểm TB | Tỷ lệ hài lòng | Cần phản hồi)
 *   • Feedback list with inline reply
 *   • Pagination
 *
 * API:
 *   GET  /api/evaluations/stats         → avgRating, totalEvaluations, satisfactionRate
 *   GET  /api/admin/evaluations?page&limit&minRating
 *   POST /api/admin/evaluations/:id/reply
 */
import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  RefreshCw, Star, ChevronLeft, ChevronRight,
  Inbox, Send, SlidersHorizontal, ArrowUpDown,
  MessageSquare, ArrowRight, Pencil, TrendingUp,
} from 'lucide-react';
import * as adminSvc from '../services/adminService';

interface Props { onNavigate: (s: string, p?: any) => void }

const PRIMARY = '#8f000d';
const GOLD    = '#e9c400';   // secondary-fixed-dim  ≈ star color

// ── Helpers ───────────────────────────────────────────────────────────────────
function fmtDate(iso?: string) {
  if (!iso) return '–';
  const d = new Date(iso);
  return `${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}, ${d.toLocaleDateString('vi-VN')}`;
}

// ── Stars ─────────────────────────────────────────────────────────────────────
function Stars({ rating, size = 'md' }: { rating: number; size?: 'sm' | 'md' | 'lg' }) {
  const px = size === 'lg' ? 'w-6 h-6' : size === 'sm' ? 'w-3 h-3' : 'w-4 h-4';
  return (
    <div className="flex items-center gap-0.5">
      {Array.from({ length: 5 }).map((_, i) => (
        <Star
          key={i}
          className={`${px} ${i < Math.round(rating)
            ? 'fill-yellow-400 text-yellow-400'
            : 'text-gray-200'}`}
        />
      ))}
    </div>
  );
}

// ── Rating progress bar ───────────────────────────────────────────────────────
function RatingBar({ label, value }: { label: string; value: number }) {
  return (
    <div className="flex items-center gap-2">
      <span className="text-[10px] text-gray-500 w-20 flex-shrink-0">{label}</span>
      <div className="flex-1 h-1 bg-[#de9ca4]/20 rounded-full overflow-hidden">
        <div className="h-full rounded-full transition-all duration-700"
          style={{ width: `${(value / 5) * 100}%`, backgroundColor: GOLD }} />
      </div>
      <span className="text-[11px] font-bold text-gray-700 w-6 text-right">{value.toFixed(1)}</span>
    </div>
  );
}

// ── Feedback Item ─────────────────────────────────────────────────────────────
function FeedbackItem({
  item, onReply,
}: {
  item: any;
  onReply: (id: string, text: string) => Promise<void>;
}) {
  const [mode,    setMode]    = useState<'idle' | 'replying' | 'editing'>('idle');
  const [text,    setText]    = useState(item.adminReply ?? '');
  const [saving,  setSaving]  = useState(false);
  const taRef = useRef<HTMLTextAreaElement>(null);

  const hasReply = !!item.adminReply;

  const openReply = (edit = false) => {
    setText(edit ? item.adminReply : '');
    setMode(edit ? 'editing' : 'replying');
    setTimeout(() => taRef.current?.focus(), 80);
  };

  const submit = async () => {
    if (!text.trim()) return;
    setSaving(true);
    await onReply(item.id, text.trim());
    setSaving(false);
    setMode('idle');
  };

  return (
    <div
      className="bg-white rounded-2xl p-5 shadow-sm relative group transition-all duration-200
        hover:-translate-y-0.5 hover:shadow-md overflow-hidden"
      style={{ boxShadow: '0 4px 20px rgba(0,0,0,0.06)' }}
    >
      {/* Left accent */}
      <div
        className="absolute left-0 inset-y-0 w-1 rounded-l-2xl"
        style={{ backgroundColor: hasReply ? '#9ca3af' : PRIMARY }}
      />

      {/* Top row */}
      <div className="flex justify-between items-start mb-4 gap-4">
        <div className="flex items-center gap-4">
          {/* Avatar */}
          <div className="w-11 h-11 bg-[#fff4f4] rounded-2xl flex items-center justify-center flex-shrink-0">
            <span className="text-xl font-bold" style={{ color: PRIMARY }}>
              {(item.userName || 'K')[0].toUpperCase()}
            </span>
          </div>
          <div>
            <h4 className="font-bold text-gray-900 text-base leading-tight">
              {item.userName || 'Khách vãng lai'}
            </h4>
            <p className="text-xs text-gray-400 mt-0.5">
              {item.applicationCode
                ? `Mã hồ sơ: ${item.applicationCode} • `
                : ''}
              {fmtDate(item.submittedAt)}
            </p>
          </div>
        </div>
        {/* Stars */}
        <Stars rating={item.avgRating ?? 0} size="md" />
      </div>

      {/* Sub-rating bars (collapsible tooltip effect) */}
      {(item.attitudeRating || item.timeRating || item.facilitiesRating) && (
        <div className="mb-4 space-y-1 pl-1">
          {item.attitudeRating   && <RatingBar label="Thái độ"       value={item.attitudeRating} />}
          {item.timeRating       && <RatingBar label="Thời gian"     value={item.timeRating} />}
          {item.facilitiesRating && <RatingBar label="Cơ sở vật chất" value={item.facilitiesRating} />}
        </div>
      )}

      {/* Comment */}
      {item.comment && (
        <p className="text-gray-700 leading-relaxed mb-5 text-sm">
          {item.comment}
        </p>
      )}

      {/* Admin reply block */}
      {hasReply && mode === 'idle' && (
        <div className="bg-[#fff4f4] rounded-xl p-4 mb-4 border-l-4 border-yellow-400">
          <p className="text-xs font-bold text-gray-500 mb-1">Admin đã phản hồi:</p>
          <p className="text-sm text-gray-600 italic">"{item.adminReply}"</p>
          {item.adminRepliedAt && (
            <p className="text-[10px] text-gray-400 mt-1.5">{fmtDate(item.adminRepliedAt)}</p>
          )}
        </div>
      )}

      {/* Reply textarea */}
      {(mode === 'replying' || mode === 'editing') && (
        <div className="mb-4">
          <textarea
            ref={taRef}
            value={text}
            onChange={e => setText(e.target.value)}
            rows={3}
            placeholder="Nhập phản hồi của bạn…"
            className="w-full border border-[#de9ca4]/30 rounded-xl px-3 py-2.5 text-sm
              focus:outline-none focus:border-[#8f000d]/40 resize-none bg-white"
          />
          <div className="flex justify-end gap-2 mt-2">
            <button
              onClick={() => setMode('idle')}
              className="px-3 py-1.5 text-xs text-gray-500 hover:text-gray-700"
            >
              Hủy
            </button>
            <button
              disabled={saving || !text.trim()}
              onClick={submit}
              className="px-4 py-1.5 text-xs font-bold text-white rounded-lg flex items-center gap-1.5
                disabled:opacity-50 transition-opacity hover:opacity-90"
              style={{ backgroundColor: PRIMARY }}
            >
              {saving
                ? <RefreshCw className="w-3 h-3 animate-spin" />
                : <Send className="w-3 h-3" />}
              {mode === 'editing' ? 'Cập nhật' : 'Gửi phản hồi'}
            </button>
          </div>
        </div>
      )}

      {/* Action buttons */}
      {mode === 'idle' && (
        <div className="flex justify-end gap-2">
          {hasReply ? (
            <>
              <button
                onClick={() => openReply(true)}
                className="flex items-center gap-1.5 px-4 py-2 text-sm font-bold text-gray-500
                  hover:text-gray-700 transition-colors"
              >
                <Pencil className="w-3.5 h-3.5" /> Sửa phản hồi
              </button>
              <button
                className="px-4 py-2 text-sm font-bold transition-colors hover:opacity-80"
                style={{ color: PRIMARY }}
              >
                Xem chi tiết
              </button>
            </>
          ) : (
            <>
              <button
                className="px-4 py-2 text-sm font-bold transition-colors hover:opacity-80"
                style={{ color: PRIMARY }}
              >
                Xem hồ sơ gốc
              </button>
              <button
                onClick={() => openReply(false)}
                className="px-5 py-2 text-sm font-bold text-white rounded-xl shadow-sm hover:opacity-90
                  transition-opacity flex items-center gap-2"
                style={{ backgroundColor: PRIMARY }}
              >
                <MessageSquare className="w-4 h-4" /> Phản hồi
              </button>
            </>
          )}
        </div>
      )}
    </div>
  );
}

// ── Main ──────────────────────────────────────────────────────────────────────
export function AdminEvaluationsScreen({ onNavigate }: Props) {
  const [stats,     setStats]     = useState<any>(null);
  const [items,     setItems]     = useState<any[]>([]);
  const [loading,   setLoading]   = useState(true);
  const [page,      setPage]      = useState(1);
  const [total,     setTotal]     = useState(0);
  const [filter,    setFilter]    = useState('');
  const [sortNew,   setSortNew]   = useState(true);
  const [toast,     setToast]     = useState<{ msg: string; ok: boolean } | null>(null);
  const LIMIT = 8;

  const showToast = (msg: string, ok: boolean) => {
    setToast({ msg, ok });
    setTimeout(() => setToast(null), 3000);
  };

  const load = useCallback(async () => {
    setLoading(true);
    const params: Record<string, string> = {
      page: String(page),
      limit: String(LIMIT),
      ...(filter ? { minRating: filter } : {}),
      sort: sortNew ? 'newest' : 'oldest',
    };
    const [statsRes, listRes] = await Promise.allSettled([
      adminSvc.getEvaluationStats(),
      adminSvc.getAllEvaluations(params),
    ]);
    if (statsRes.status === 'fulfilled') setStats(statsRes.value.data ?? statsRes.value);
    if (listRes.status  === 'fulfilled') {
      setItems(listRes.value.data  ?? []);
      setTotal(listRes.value.pagination?.total ?? listRes.value.total ?? 0);
    }
    setLoading(false);
  }, [page, filter, sortNew]);

  useEffect(() => { load(); }, [load]);

  const handleReply = async (id: string, text: string) => {
    try {
      await adminSvc.replyToEvaluation(id, text);
      showToast('Đã gửi phản hồi thành công', true);
      // Optimistic update
      setItems(prev =>
        prev.map(it => it.id === id
          ? { ...it, adminReply: text, adminRepliedAt: new Date().toISOString() }
          : it,
        ),
      );
    } catch (e: any) {
      showToast(e.message || 'Không thể gửi phản hồi', false);
      throw e;   // re-throw so FeedbackItem can reset saving state
    }
  };

  const totalPages   = Math.max(1, Math.ceil(total / LIMIT));
  const pendingCount = items.filter(it => !it.adminReply).length;
  const avgRating    = stats?.avgRating ?? 0;
  const satRate      = stats?.satisfactionRate ?? 0;
  const totalEvals   = stats?.totalEvaluations ?? 0;

  // Page numbers to display
  const pageNumbers = (() => {
    const pages: (number | '…')[] = [];
    if (totalPages <= 7) {
      for (let i = 1; i <= totalPages; i++) pages.push(i);
    } else {
      pages.push(1);
      if (page > 3) pages.push('…');
      for (let i = Math.max(2, page - 1); i <= Math.min(totalPages - 1, page + 1); i++) pages.push(i);
      if (page < totalPages - 2) pages.push('…');
      pages.push(totalPages);
    }
    return pages;
  })();

  return (
    <div className="min-h-full bg-transparent relative">

      {/* Toast */}
      {toast && (
        <div className={`fixed bottom-24 left-1/2 -translate-x-1/2 z-50 px-4 py-2.5 rounded-full shadow-lg text-sm
          font-medium text-white flex items-center gap-2 max-w-xs whitespace-nowrap
          ${toast.ok ? 'bg-green-600' : 'bg-red-700'}`}>
          {toast.msg}
        </div>
      )}

      {/* ── Hero banner (full-bleed) ──────────────────────────────────────── */}
      <div className="relative overflow-hidden"
        style={{ background: 'linear-gradient(135deg, #8f000d 0%, #b22222 40%, #c0392b 70%, #e8867a 100%)' }}>
          {/* Grid pattern overlay */}
          <div className="absolute inset-0 opacity-10"
            style={{
              backgroundImage: 'repeating-linear-gradient(0deg,transparent,transparent 39px,rgba(255,255,255,0.5) 39px,rgba(255,255,255,0.5) 40px),repeating-linear-gradient(90deg,transparent,transparent 39px,rgba(255,255,255,0.5) 39px,rgba(255,255,255,0.5) 40px)',
            }} />
          <div className="relative flex items-end p-5 pb-6">
            <div className="text-white">
              <p className="text-[10px] font-semibold text-red-200 uppercase tracking-widest mb-0.5">Quản trị · Đánh giá</p>
              <h1 className="text-2xl font-black text-white leading-tight">
                Quản lý Đánh giá<span style={{ color: '#fcd400' }}>.</span>
              </h1>
              <p className="text-red-100 text-xs mt-1 max-w-xs">
                Giám sát mức độ hài lòng và phản hồi trực tiếp từ công dân.
              </p>
            </div>
            {/* Big decorative number + refresh */}
            <div className="ml-auto flex flex-col items-end gap-2">
              <button
                onClick={load}
                className="p-2 rounded-xl bg-white/15 hover:bg-white/25 text-white transition-colors"
              >
                <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
              </button>
              <p className="text-[4rem] font-black text-white/15 leading-none hidden sm:block">
                {avgRating ? avgRating.toFixed(1) : '–'}
              </p>
            </div>
          </div>
        </div>

      <div className="px-4 pb-6">

        {/* ── Bento stats ──────────────────────────────────────────────────── */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mb-6 -mt-3 relative z-10">

          {/* Avg Rating */}
          <div className="bg-white rounded-2xl p-5 shadow-sm overflow-hidden relative">
            <div className="absolute top-0 left-0 right-0 h-1 rounded-t-2xl" style={{ backgroundColor: PRIMARY }} />
            <p className="text-[10px] font-semibold uppercase tracking-widest text-gray-400 mb-3 mt-1">
              Điểm trung bình
            </p>
            <div className="flex items-end gap-3">
              <span className="text-5xl font-extrabold text-gray-900 leading-none">
                {avgRating ? avgRating.toFixed(1) : '–'}
              </span>
              <div className="pb-1 space-y-1">
                <Stars rating={avgRating} size="md" />
                <p className="text-xs text-gray-400">Từ {totalEvals.toLocaleString()} lượt</p>
              </div>
            </div>
          </div>

          {/* Satisfaction Rate */}
          <div className="bg-white rounded-2xl p-5 shadow-sm overflow-hidden relative">
            <div className="absolute top-0 left-0 right-0 h-1 rounded-t-2xl bg-yellow-400" />
            <p className="text-[10px] font-semibold uppercase tracking-widest text-gray-400 mb-3 mt-1">
              Tỷ lệ hài lòng
            </p>
            <div className="flex items-end gap-3 mb-2">
              <span className="text-5xl font-extrabold text-gray-900 leading-none">
                {satRate ? `${satRate}%` : '–'}
              </span>
            </div>
            <div className="w-full h-2 bg-[#de9ca4]/20 rounded-full overflow-hidden mb-2">
              <div
                className="h-full rounded-full transition-all duration-1000"
                style={{ width: `${satRate}%`, backgroundColor: GOLD }}
              />
            </div>
            <div className="flex items-center gap-1 text-green-600">
              <TrendingUp className="w-3.5 h-3.5" />
              <p className="text-xs font-medium">Tăng 2.4% so với tháng trước</p>
            </div>
          </div>

          {/* Pending replies */}
          <div className="bg-white rounded-2xl p-5 shadow-sm overflow-hidden relative">
            <div className="absolute top-0 left-0 right-0 h-1 rounded-t-2xl bg-gray-300" />
            <p className="text-[10px] font-semibold uppercase tracking-widest text-gray-400 mb-3 mt-1">
              Cần phản hồi
            </p>
            <div className="flex items-end gap-3 mb-3">
              <span className="text-5xl font-extrabold leading-none" style={{ color: PRIMARY }}>
                {pendingCount}
              </span>
              <span className="text-gray-500 font-medium pb-1">mới</span>
            </div>
            <button
              onClick={() => setFilter('')}
              className="flex items-center gap-1 text-sm font-bold hover:underline"
              style={{ color: PRIMARY }}
            >
              Xem ngay <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>

        {/* ── List header ──────────────────────────────────────────────────── */}
        <div className="flex flex-wrap justify-between items-center gap-3 mb-4">
          <h3 className="text-base font-bold text-gray-900">Danh sách phản hồi mới nhất</h3>
          <div className="flex items-center gap-2 flex-wrap">
            {/* Rating filter */}
            <div className="flex gap-1.5">
              {[
                { v: '',  l: 'Tất cả' },
                { v: '4', l: '4★+' },
                { v: '3', l: '3★+' },
              ].map(o => (
                <button key={o.v}
                  onClick={() => { setFilter(o.v); setPage(1); }}
                  className={`px-3 py-1.5 rounded-full text-xs font-semibold transition-all
                    ${filter === o.v ? 'text-white shadow-sm' : 'bg-[#fff4f4] text-[#9f364c]/70 hover:bg-[#de9ca4]/20 border border-[#de9ca4]/30'}`}
                  style={filter === o.v ? { backgroundColor: PRIMARY } : undefined}>
                  {o.l}
                </button>
              ))}
            </div>
            <button
              onClick={() => setSortNew(v => !v)}
              className="px-3 py-1.5 rounded-full bg-[#fff4f4] text-[#9f364c]/70 hover:bg-[#de9ca4]/20 text-xs
                font-semibold flex items-center gap-1.5 transition-colors border border-[#de9ca4]/30"
            >
              <ArrowUpDown className="w-3 h-3" />
              {sortNew ? 'Mới nhất' : 'Cũ nhất'}
            </button>
          </div>
        </div>

        {/* ── List ─────────────────────────────────────────────────────────── */}
        {loading ? (
          <div className="flex justify-center py-16">
            <RefreshCw className="w-6 h-6 animate-spin" style={{ color: PRIMARY }} />
          </div>
        ) : items.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-16 gap-3 text-gray-400">
            <Inbox className="w-12 h-12" />
            <p className="text-sm">Chưa có đánh giá nào</p>
          </div>
        ) : (
          <div className="space-y-4">
            {items.map(item => (
              <FeedbackItem key={item.id} item={item} onReply={handleReply} />
            ))}
          </div>
        )}

        {/* ── Pagination ───────────────────────────────────────────────────── */}
        {totalPages > 1 && (
          <div className="flex justify-center items-center gap-1.5 mt-8">
            <button
              disabled={page === 1}
              onClick={() => setPage(p => p - 1)}
              className="w-9 h-9 flex items-center justify-center rounded-xl border border-[#de9ca4]/30
                hover:bg-[#fff4f4] disabled:opacity-40 transition-colors"
            >
              <ChevronLeft className="w-4 h-4 text-gray-600" />
            </button>

            {pageNumbers.map((n, i) =>
              n === '…' ? (
                <span key={`ellipsis-${i}`} className="w-9 text-center text-gray-400 text-sm">…</span>
              ) : (
                <button
                  key={n}
                  onClick={() => setPage(n as number)}
                  className={`w-9 h-9 rounded-xl text-sm font-bold transition-all
                    ${page === n
                      ? 'text-white shadow-sm'
                      : 'border border-[#de9ca4]/30 hover:bg-[#fff4f4] text-[#4d2128]'}`}
                  style={page === n ? { backgroundColor: PRIMARY } : undefined}
                >
                  {n}
                </button>
              ),
            )}

            <button
              disabled={page >= totalPages}
              onClick={() => setPage(p => p + 1)}
              className="w-9 h-9 flex items-center justify-center rounded-xl border border-[#de9ca4]/30
                hover:bg-[#fff4f4] disabled:opacity-40 transition-colors"
            >
              <ChevronRight className="w-4 h-4 text-gray-600" />
            </button>
          </div>
        )}
      </div>{/* close px-4 pb-6 */}
    </div>
  );
}
