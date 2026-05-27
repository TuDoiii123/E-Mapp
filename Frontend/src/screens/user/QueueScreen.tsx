/**
 * QueueScreen — Người dùng lấy số thứ tự & theo dõi vé của mình
 */
import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { RefreshCw, XCircle, CheckCircle, Clock, Users } from 'lucide-react';
import {
  takeTicket, getMyTickets, cancelTicket, getQueueSummary,
  formatWaitTime, QueueTicket, QueueSummary,
} from '../../services/queueService';
import { useAuth } from '../../contexts/AuthContext';

interface QueueScreenProps {
  onNavigate: (screen: string, params?: any) => void;
  agencyId?:  string;
  agencyName?:string;
}

const STATUS_LABELS: Record<string, { label: string; color: string }> = {
  waiting:   { label: 'Đang chờ',     color: 'bg-yellow-100 text-yellow-800' },
  called:    { label: 'Đã được gọi',  color: 'bg-blue-100   text-blue-800'   },
  serving:   { label: 'Đang phục vụ', color: 'bg-green-100  text-green-800'  },
  done:      { label: 'Hoàn thành',   color: 'bg-gray-100   text-gray-600'   },
  absent:    { label: 'Vắng mặt',     color: 'bg-orange-100 text-orange-800' },
  cancelled: { label: 'Đã hủy',       color: 'bg-red-100    text-red-600'    },
};

// Nhóm thủ tục thành 5 nhóm để lấy số hàng chờ
const QUEUE_SERVICE_GROUPS = [
  { id: 'svc-cccd',    name: 'Cấp CCCD / Hộ chiếu',        desc: 'CCCD, hộ chiếu, cư trú',                                      prefix: 'A', icon: 'fingerprint',   span: false },
  { id: 'svc-datdai',  name: 'Thủ tục đất đai',             desc: 'Sổ đỏ, chuyển nhượng, tách thửa, môi trường',                 prefix: 'B', icon: 'foundation',    span: false },
  { id: 'svc-hotich',  name: 'Hộ tịch & Kinh doanh',        desc: 'Khai sinh, kết hôn, khai tử, đăng ký doanh nghiệp',          prefix: 'C', icon: 'family_history', span: false },
  { id: 'svc-xacnhan', name: 'Tư pháp & Thuế',              desc: 'Công chứng, lý lịch tư pháp, mã số thuế, BHXH',              prefix: 'D', icon: 'description',   span: false },
  { id: 'svc-other',   name: 'Thủ tục khác',                desc: 'GPLX, xây dựng, y tế, giáo dục và các loại khác',            prefix: 'E', icon: 'more_horiz',    span: true  },
];

export function QueueScreen({ onNavigate, agencyId = 'default', agencyName = 'Cơ quan hành chính' }: QueueScreenProps) {
  const { user } = useAuth();
  const [myTickets,    setMyTickets]   = useState<QueueTicket[]>([]);
  const [summary,      setSummary]     = useState<QueueSummary | null>(null);
  const [loading,      setLoading]     = useState(false);
  const [taking,       setTaking]      = useState(false);
  const [error,        setError]       = useState('');
  const [selectedSvc,  setSelectedSvc] = useState('');
  const [svcName,      setSvcName]     = useState('');
  const [newTicket,    setNewTicket]   = useState<QueueTicket | null>(null);

  const loadData = useCallback(async () => {
    try {
      const [tickets, sum] = await Promise.all([getMyTickets(), getQueueSummary(agencyId)]);
      setMyTickets(tickets);
      setSummary(sum);
    } catch { /* ignore */ }
  }, [agencyId]);

  useEffect(() => {
    loadData();
    const id = setInterval(loadData, 30_000);
    return () => clearInterval(id);
  }, [loadData]);

  const handleTakeTicket = async () => {
    if (!selectedSvc) { setError('Vui lòng chọn thủ tục trước khi lấy số'); return; }
    setTaking(true); setError('');
    try {
      const svc    = QUEUE_SERVICE_GROUPS.find(s => s.id === selectedSvc);
      const ticket = await takeTicket({
        agencyId,
        serviceId:   selectedSvc,
        serviceName: svcName,
        prefix:      svc?.prefix || 'A',
        userName:    user?.fullName || '',
      });
      setMyTickets(prev => [ticket, ...prev]);
      setNewTicket(ticket);
      await loadData();
    } catch (e: any) {
      setError(e.message || 'Không thể lấy số, vui lòng thử lại');
    } finally {
      setTaking(false);
    }
  };

  const handleCancel = async (ticketId: string) => {
    try {
      await cancelTicket(ticketId);
      setMyTickets(prev => prev.map(t => t.id === ticketId ? { ...t, status: 'cancelled' } : t));
    } catch (e: any) {
      setError(e.message || 'Không thể hủy vé');
    }
  };

  const activeTicket = myTickets.find(t => ['waiting', 'called', 'serving'].includes(t.status));
  const historyTickets = myTickets.filter(t => ['done', 'absent', 'cancelled'].includes(t.status));

  return (
    <div className="bg-surface text-on-surface min-h-screen" style={{ fontFamily: "'Manrope', sans-serif" }}>

      {/* TopAppBar */}
      <header className="fixed top-0 right-0 left-0 h-20 flex items-center justify-between px-8 md:px-12 w-full bg-[#fff4f4]/80 backdrop-blur-xl shadow-[0px_20px_40px_rgba(77,33,40,0.04)] z-40">
        <div className="flex items-center gap-4">
          <button onClick={() => onNavigate('home')} className="text-xl font-bold text-on-surface tracking-tighter hover:opacity-70 transition-opacity">
            Dịch Vụ Công
          </button>
          <div className="h-6 w-[1px] bg-outline-variant/30 hidden md:block" />
          <span className="font-bold text-lg text-primary hidden md:block">Thủ tục Hành chính</span>
        </div>
        <div className="flex items-center gap-6">
          <button
            onClick={() => { setLoading(true); loadData().finally(() => setLoading(false)); }}
            className="text-on-surface hover:opacity-70 transition-opacity"
            aria-label="Làm mới"
          >
            <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
          </button>
          <button onClick={() => onNavigate('notification')} className="relative text-on-surface hover:opacity-70 transition-opacity">
            <span className="material-symbols-outlined">notifications</span>
            <span className="absolute top-0 right-0 w-2 h-2 bg-primary rounded-full" />
          </button>
          <button className="text-on-surface hover:opacity-70 transition-opacity">
            <span className="material-symbols-outlined">account_circle</span>
          </button>
        </div>
      </header>

      {/* Page content */}
      <main className="relative pt-32 pb-20 px-6 md:px-12 max-w-5xl mx-auto">

        {/* ── Active ticket banner ── */}
        {activeTicket && (
          <div className={`mb-8 rounded-xl p-6 border-2 ${
            activeTicket.status === 'called'
              ? 'border-blue-400 bg-blue-50 animate-pulse'
              : 'border-primary/30 bg-surface-container-low'
          }`}>
            <div className="flex items-center justify-between flex-wrap gap-4">
              <div>
                <p className="text-xs font-bold text-outline uppercase tracking-widest mb-1">Số của bạn</p>
                <p className="text-6xl font-black text-primary leading-none">{activeTicket.ticketCode}</p>
                <p className="text-sm text-on-surface-variant mt-2">{activeTicket.serviceName}</p>
                <span className={`inline-block mt-2 px-3 py-1 rounded-full text-xs font-bold ${STATUS_LABELS[activeTicket.status]?.color}`}>
                  {STATUS_LABELS[activeTicket.status]?.label}
                </span>
              </div>
              <div className="text-right space-y-2">
                {activeTicket.status === 'waiting' && (
                  <div>
                    <p className="text-xs text-on-surface-variant">Ước tính chờ</p>
                    <p className="text-lg font-bold text-secondary flex items-center gap-1 justify-end">
                      <Clock className="w-4 h-4" />
                      {formatWaitTime(activeTicket.estimatedWait)}
                    </p>
                  </div>
                )}
                {activeTicket.counterNo && (
                  <p className="text-sm font-semibold text-on-surface">Quầy {activeTicket.counterNo}</p>
                )}
                {activeTicket.status === 'called' && (
                  <p className="text-base font-black text-blue-700">Đến quầy {activeTicket.counterNo} ngay!</p>
                )}
                {activeTicket.status === 'waiting' && (
                  <button
                    onClick={() => handleCancel(activeTicket.id)}
                    className="flex items-center gap-1 text-sm text-error border border-error/40 px-3 py-1.5 rounded-lg hover:bg-error-container/20 transition-colors"
                  >
                    <XCircle className="w-4 h-4" /> Hủy vé
                  </button>
                )}
              </div>
            </div>
          </div>
        )}

        {/* ── Queue summary ── */}
        {summary && (
          <div className="grid grid-cols-3 gap-4 mb-8">
            {[
              { label: 'Đang chờ',     value: summary.totalWaiting,                            color: 'text-yellow-600' },
              { label: 'Đang phục vụ', value: summary.totalServing + summary.totalCalled,        color: 'text-blue-600'   },
              { label: 'Xong hôm nay', value: summary.totalDone,                               color: 'text-green-600'  },
            ].map(item => (
              <div key={item.label} className="bg-surface-container-lowest rounded-xl p-4 text-center shadow-sm">
                <p className={`text-3xl font-black ${item.color}`}>{item.value}</p>
                <p className="text-xs text-on-surface-variant mt-1 font-medium">{item.label}</p>
              </div>
            ))}
          </div>
        )}

        {/* ── Now serving ── */}
        {summary && summary.nowServing.length > 0 && (
          <div className="mb-8 bg-surface-container-lowest rounded-xl p-5 shadow-sm">
            <p className="text-xs font-black text-on-surface-variant uppercase tracking-widest mb-3 flex items-center gap-2">
              <Users className="w-4 h-4 text-green-500" /> Đang phục vụ
            </p>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              {summary.nowServing.map(s => (
                <div key={s.counterNo} className="bg-green-50 border border-green-200 rounded-lg p-3 text-center">
                  <p className="text-xs text-on-surface-variant">Quầy {s.counterNo}</p>
                  <p className="text-2xl font-black text-green-700">{s.ticketCode}</p>
                  <p className="text-xs text-on-surface-variant truncate">{s.serviceName}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* ── Heading ── */}
        <div className="mb-12 text-center">
          <h2 className="text-4xl font-extrabold tracking-tight text-on-surface mb-2">Lấy số thứ tự mới</h2>
          <p className="text-secondary font-medium opacity-80">
            Vui lòng chọn loại thủ tục bạn cần thực hiện tại trung tâm.
          </p>
        </div>

        {/* ── Procedure cards ── */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-16">
          {QUEUE_SERVICE_GROUPS.map(svc => {
            const isSelected = selectedSvc === svc.id;
            return (
              <div
                key={svc.id}
                onClick={() => { setSelectedSvc(svc.id); setSvcName(svc.name); setError(''); }}
                className={`group relative p-6 rounded-lg flex items-center gap-6 cursor-pointer transition-all duration-300
                  ${svc.span ? 'md:col-span-2' : ''}
                  ${isSelected
                    ? 'bg-primary shadow-[0px_12px_32px_rgba(183,19,26,0.2)] scale-[1.01]'
                    : 'bg-surface-container-lowest hover:bg-surface-container-highest'
                  }`}
              >
                {/* Letter badge */}
                <div className={`flex-shrink-0 w-16 h-16 rounded-lg flex items-center justify-center font-black text-2xl transition-colors
                  ${isSelected
                    ? 'bg-on-primary/20 text-on-primary'
                    : 'bg-surface-container-low text-primary group-hover:bg-primary group-hover:text-on-primary'
                  }`}>
                  {svc.prefix}
                </div>

                {/* Text */}
                <div className="flex-1">
                  <h3 className={`text-xl font-bold mb-1 ${isSelected ? 'text-on-primary' : 'text-on-surface'}`}>
                    {svc.name}
                  </h3>
                  <p className={`text-sm ${isSelected ? 'text-on-primary/80' : 'text-secondary opacity-80'}`}>
                    {svc.desc}
                  </p>
                </div>

                {/* Icon */}
                <span className={`material-symbols-outlined ${isSelected ? 'text-on-primary/60' : 'text-outline-variant'}`}>
                  {svc.icon}
                </span>

                {/* Selected checkmark */}
                {isSelected && (
                  <span className="absolute top-3 right-3 w-6 h-6 bg-on-primary/20 rounded-full flex items-center justify-center">
                    <span className="material-symbols-outlined text-on-primary text-[16px]">check</span>
                  </span>
                )}
              </div>
            );
          })}
        </div>

        {/* ── Error ── */}
        {error && (
          <div className="mb-6 flex items-center gap-2 p-4 bg-error-container/20 border-l-4 border-error rounded-lg text-sm text-error">
            <span className="material-symbols-outlined text-[18px]">error</span>
            {error}
          </div>
        )}

        {/* ── CTA button ── */}
        <div className="flex flex-col items-center gap-6">
          <button
            onClick={handleTakeTicket}
            disabled={taking}
            className="w-full max-w-md bg-gradient-to-br from-primary to-primary-container text-on-primary py-6 rounded-xl font-black text-2xl uppercase tracking-widest shadow-[0px_20px_40px_rgba(183,19,26,0.2)] hover:scale-[1.02] active:scale-95 transition-all duration-300 disabled:opacity-60 disabled:cursor-not-allowed disabled:scale-100 flex items-center justify-center gap-3"
          >
            {taking ? (
              <>
                <RefreshCw className="w-6 h-6 animate-spin" />
                Đang lấy số...
              </>
            ) : 'Lấy số thứ tự'}
          </button>

          <div className="flex items-center gap-2 text-on-surface-variant text-sm italic opacity-70">
            <span className="material-symbols-outlined text-base">info</span>
            <span>Vui lòng kiểm tra lại thông tin trước khi nhấn lấy số</span>
          </div>

          {summary && summary.totalWaiting > 0 && (
            <p className="text-sm text-center text-on-surface-variant">
              Hiện có <strong className="text-primary">{summary.totalWaiting}</strong> người đang chờ —
              ước tính <strong className="text-secondary">{formatWaitTime(
                summary.totalWaiting * (summary.avgServiceTimeSec || 420) / Math.max(summary.activeCounters, 1)
              )}</strong>
            </p>
          )}
        </div>

        {/* ── Ticket history ── */}
        {historyTickets.length > 0 && (
          <div className="mt-16">
            <p className="text-xs font-black text-on-surface-variant uppercase tracking-widest mb-4">Lịch sử hôm nay</p>
            <div className="bg-surface-container-lowest rounded-xl overflow-hidden shadow-sm divide-y divide-outline-variant/10">
              {historyTickets.map(t => (
                <div key={t.id} className="flex items-center justify-between px-5 py-4">
                  <div className="flex items-center gap-3">
                    {t.status === 'done'
                      ? <CheckCircle className="w-4 h-4 text-green-500 flex-shrink-0" />
                      : <XCircle    className="w-4 h-4 text-error flex-shrink-0" />}
                    <div>
                      <p className="text-sm font-bold text-on-surface">{t.ticketCode}</p>
                      <p className="text-xs text-on-surface-variant">{t.serviceName}</p>
                    </div>
                  </div>
                  <span className={`text-xs font-bold px-3 py-1 rounded-full ${STATUS_LABELS[t.status]?.color}`}>
                    {STATUS_LABELS[t.status]?.label}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>

      {/* Decorative background */}
      <div className="fixed bottom-0 right-0 w-1/3 h-1/2 -z-10 opacity-10 pointer-events-none"
        style={{ maskImage: 'linear-gradient(to top left, black, transparent)', WebkitMaskImage: 'linear-gradient(to top left, black, transparent)' }}>
        <div className="w-full h-full bg-gradient-to-tl from-primary to-transparent" />
      </div>

      {/* ── Success Modal ── */}
      {newTicket && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          {/* Backdrop */}
          <div
            className="absolute inset-0 bg-neutral-900/60 backdrop-blur-sm"
            onClick={() => setNewTicket(null)}
          />
          {/* Modal */}
          <div className="relative bg-surface-container-lowest w-full max-w-md rounded-xl shadow-2xl p-8 text-center">
            {/* Icon */}
            <div className="mb-6 flex justify-center">
              <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center">
                <span className="material-symbols-outlined text-green-600 text-5xl"
                  style={{ fontVariationSettings: "'FILL' 1" }}>
                  check_circle
                </span>
              </div>
            </div>

            {/* Content */}
            <h3 className="text-2xl font-extrabold text-on-surface mb-2">Lấy số thành công!</h3>
            <div className="text-lg text-on-surface-variant mb-4">
              Số thứ tự của bạn là:
              <span className="text-primary font-black text-4xl block mt-2 tracking-widest">
                {newTicket.ticketCode}
              </span>
            </div>
            <p className="text-sm text-secondary opacity-80 leading-relaxed mb-2">
              Thủ tục: <strong>{newTicket.serviceName}</strong>
            </p>
            {newTicket.estimatedWait != null && newTicket.estimatedWait > 0 && (
              <p className="text-sm text-on-surface-variant mb-2">
                Thời gian chờ ước tính: <strong className="text-secondary">{formatWaitTime(newTicket.estimatedWait)}</strong>
              </p>
            )}
            <p className="text-sm text-on-surface-variant leading-relaxed mb-8">
              Vui lòng theo dõi bảng điện tử tại sảnh chờ. Chúng tôi sẽ thông báo khi đến lượt bạn.
            </p>

            {/* Actions */}
            <div className="space-y-3">
              <button
                onClick={() => setNewTicket(null)}
                className="w-full bg-primary hover:opacity-90 active:scale-95 text-on-primary py-4 rounded-lg font-bold transition-all shadow-lg shadow-primary/20"
              >
                Đóng
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
