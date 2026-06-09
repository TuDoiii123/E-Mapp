/**
 * AdminAnalyticsScreen — Phân tích & Báo cáo  (Desktop redesign)
 *
 * Layout:
 *   • Hero banner gradient
 *   • 4 KPI cards  (totalUsers | totalApps | on-time rate | avg time)
 *   • Charts bento (2/3 bar + 1/3 donut)
 *   • Detailed analysis (image/quote + top-categories progress bars)
 *
 * Data: adminSvc.getStats()  +  adminSvc.getEvaluationStats()
 */
import React, { useState, useEffect, useCallback } from 'react';
import {
  RefreshCw, TrendingUp, TrendingDown, Users,
  FileText, Clock, CheckCircle2, BarChart2, AlertCircle,
} from 'lucide-react';
import * as adminSvc from '../../services/adminService';

interface Props { onNavigate: (s: string, p?: any) => void }

const PRIMARY = '#8f000d';
const GOLD    = '#fcd400';

// ── Time-series bar chart (real data from /api/admin/stats) ───────────────────
interface TsPoint { date: string; applications: number; appointments: number }
const WD = ['CN', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7'];

/** Gắn nhãn cho mỗi điểm dữ liệu: thứ trong tuần (≤7 ngày) hoặc dd/MM (dài hơn). */
function labelFor(dateStr: string, compact: boolean): string {
  const d = new Date(dateStr + 'T00:00:00');
  if (Number.isNaN(d.getTime())) return dateStr;
  return compact ? WD[d.getDay()] : `${d.getDate()}/${d.getMonth() + 1}`;
}

function TimeSeriesChart({ data }: { data: TsPoint[] }) {
  const [view, setView] = useState<'week' | 'all'>('week');
  const points = view === 'week' ? data.slice(-7) : data;
  const compact = points.length <= 7;
  const maxVal = Math.max(...points.map(p => p.applications + p.appointments), 1);

  return (
    <div className="bg-white p-5 rounded-2xl shadow-sm">
      <div className="flex justify-between items-center mb-2">
        <h2 className="text-base font-bold text-gray-900">Lưu lượng hồ sơ theo thời gian</h2>
        <div className="flex gap-1">
          {(['week', 'all'] as const).map(v => (
            <button
              key={v}
              onClick={() => setView(v)}
              className={`px-3 py-1 text-xs font-bold transition-all
                ${view === v
                  ? 'border-b-2 bg-[#fff4f4] text-[#4d2128] rounded-t-lg'
                  : 'text-[#9f364c]/50 hover:text-[#9f364c]'}`}
              style={view === v ? { borderBottomColor: PRIMARY } : undefined}
            >
              {v === 'week' ? '7 NGÀY' : 'TẤT CẢ'}
            </button>
          ))}
        </div>
      </div>

      {/* Legend */}
      <div className="flex items-center gap-4 mb-4 text-[11px] text-gray-500">
        <span className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-sm" style={{ backgroundColor: PRIMARY }} /> Hồ sơ
        </span>
        <span className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-sm" style={{ backgroundColor: GOLD }} /> Lịch hẹn
        </span>
      </div>

      {points.length === 0 ? (
        <div className="h-[180px] flex items-center justify-center text-sm text-gray-400">
          Chưa có dữ liệu trong khoảng thời gian này
        </div>
      ) : (
        <div className="flex items-end justify-between gap-1.5" style={{ height: 180 }}>
          {points.map((p) => {
            const bgH = 140;
            const appH  = Math.round((p.applications / maxVal) * bgH);
            const apptH = Math.round((p.appointments / maxVal) * bgH);
            return (
              <div key={p.date} className="flex flex-col items-center gap-2 flex-1 min-w-0">
                <div className="w-full relative flex flex-col justify-end overflow-hidden group"
                  style={{ height: bgH, backgroundColor: `${PRIMARY}10`, borderRadius: 8 }}>
                  <div className="w-full transition-all duration-700 group-hover:opacity-80"
                    style={{ height: apptH, backgroundColor: GOLD }}
                    title={`${labelFor(p.date, false)} — ${p.appointments} lịch hẹn`} />
                  <div className="w-full transition-all duration-700 group-hover:opacity-80"
                    style={{ height: appH, backgroundColor: PRIMARY, borderRadius: '8px 8px 0 0' }}
                    title={`${labelFor(p.date, false)} — ${p.applications} hồ sơ`} />
                </div>
                <span className="text-[10px] font-bold text-gray-500 truncate w-full text-center">
                  {labelFor(p.date, compact)}
                </span>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

// ── CSS conic-gradient donut chart ────────────────────────────────────────────
function ApprovalDonut({
  approved, pending, rejected,
}: {
  approved: number; pending: number; rejected: number;
}) {
  const total    = approved + pending + rejected || 1;
  const pctApp   = approved / total;
  const pctPend  = pending  / total;
  const deg1     = Math.round(pctApp  * 360);
  const deg2     = Math.round((pctApp + pctPend) * 360);

  const conicGradient =
    `conic-gradient(${PRIMARY} 0deg ${deg1}deg, ${GOLD} ${deg1}deg ${deg2}deg, #e2e2e2 ${deg2}deg 360deg)`;

  const items = [
    { color: PRIMARY, label: 'Đã phê duyệt',   pct: Math.round(pctApp  * 100) },
    { color: GOLD,    label: 'Đang chờ xử lý', pct: Math.round(pctPend * 100) },
    { color: '#e2e2e2', label: 'Từ chối',       pct: Math.round((rejected / total) * 100) },
  ];

  return (
    <div className="bg-white p-5 rounded-2xl shadow-sm flex flex-col items-center">
      <h2 className="text-base font-bold text-gray-900 w-full mb-5">Tỷ lệ phê duyệt hồ sơ</h2>

      {/* Donut */}
      <div className="relative flex items-center justify-center mb-5"
        style={{ width: 160, height: 160, background: conicGradient, borderRadius: '50%' }}>
        <div className="flex flex-col items-center justify-center bg-white rounded-full"
          style={{ width: 108, height: 108 }}>
          <span className="text-2xl font-black text-gray-900">{items[0].pct}%</span>
          <span className="text-[9px] uppercase font-bold text-gray-500 tracking-wider">Đã Duyệt</span>
        </div>
      </div>

      {/* Legend */}
      <div className="w-full space-y-3">
        {items.map(({ color, label, pct }) => (
          <div key={label} className="flex justify-between items-center">
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-sm flex-shrink-0" style={{ backgroundColor: color }} />
              <span className="text-sm font-medium text-gray-700">{label}</span>
            </div>
            <span className="text-sm font-bold text-gray-900">{pct}%</span>
          </div>
        ))}
      </div>
    </div>
  );
}

// ── KPI card ──────────────────────────────────────────────────────────────────
function KpiCard({
  label, value, delta, deltaLabel, accentColor, up,
}: {
  label: string; value: string; delta?: string; deltaLabel?: string;
  accentColor: string; up?: boolean;
}) {
  return (
    <div className="bg-white rounded-2xl p-4 shadow-sm overflow-hidden relative">
      {/* accent line */}
      <div className="absolute top-0 left-0 right-0 h-1 rounded-t-2xl"
        style={{ backgroundColor: accentColor }} />
      <p className="text-[10px] font-semibold uppercase tracking-widest text-gray-400 mb-2 mt-1">{label}</p>
      <div className="flex items-baseline gap-2">
        <span className="text-3xl font-bold text-gray-900">{value}</span>
        {delta && (
          <span
            className="text-xs font-bold flex items-center gap-0.5"
            style={{ color: up === false ? '#ba1a1a' : accentColor }}
          >
            {up !== undefined && (
              up
                ? <TrendingUp className="w-3 h-3" />
                : <TrendingDown className="w-3 h-3" />
            )}
            {delta}
          </span>
        )}
      </div>
      {deltaLabel && <p className="text-xs text-gray-400 mt-1">{deltaLabel}</p>}
    </div>
  );
}

// ── Main ──────────────────────────────────────────────────────────────────────
export function AdminAnalyticsScreen({ onNavigate }: Props) {
  const [stats,     setStats]     = useState<any>(null);
  const [evalStats, setEvalStats] = useState<any>(null);
  const [loading,   setLoading]   = useState(true);
  const [error,     setError]     = useState('');

  const load = useCallback(async () => {
    setLoading(true);
    setError('');
    const [sR, eR] = await Promise.allSettled([
      adminSvc.getStats(),
      adminSvc.getEvaluationStats(),
    ]);
    if (sR.status === 'fulfilled') setStats(sR.value.data ?? sR.value);
    else setError('Không tải được thống kê hệ thống');
    if (eR.status === 'fulfilled') setEvalStats(eR.value.data ?? eR.value);
    setLoading(false);
  }, []);

  useEffect(() => { load(); }, [load]);

  // ── Derived numbers (dữ liệu thật từ backend) ──────────────────────────────
  const totalUsers = stats?.totalUsers     ?? 0;
  const totalApps  = stats?.totalApplications ?? 0;
  const pending    = stats?.pendingApplications ?? 0;
  const approved   = stats?.approvedApplications ?? Math.max(0, totalApps - pending);
  const rejected   = stats?.rejectedApplications ?? 0;
  const pendingAdj = pending;

  const timeseries: TsPoint[] = stats?.timeseries ?? [];
  const categories: { label: string; pct: number }[] =
    (stats?.categoryBreakdown ?? []).map((c: any) => ({ label: c.label, pct: c.pct }));

  const avgDays   = stats?.avgProcessingDays;
  const avgValue  = (avgDays !== null && avgDays !== undefined) ? String(avgDays) : '–';

  // Tỷ lệ xử lý đúng hạn = (đã duyệt) / (đã duyệt + từ chối) trong số hồ sơ đã xử lý xong
  const resolved   = approved + rejected;
  const onTimeRate = resolved > 0
    ? `${((approved / resolved) * 100).toFixed(1)}%`
    : '–';

  return (
    <div className="min-h-full bg-transparent">
      <div className="px-4 py-4 pb-6">

        {/* ── Hero banner ───────────────────────────────────────────────── */}
        <div className="relative mb-6 rounded-3xl overflow-hidden flex items-end"
          style={{
            height: 192,
            background: `linear-gradient(135deg, ${PRIMARY} 0%, #b22222 50%, #c0392b 80%, #e8867a 100%)`,
          }}>
          {/* Grid overlay */}
          <div className="absolute inset-0 opacity-10"
            style={{
              backgroundImage:
                'repeating-linear-gradient(0deg,transparent,transparent 39px,rgba(255,255,255,0.6) 39px,rgba(255,255,255,0.6) 40px),' +
                'repeating-linear-gradient(90deg,transparent,transparent 39px,rgba(255,255,255,0.6) 39px,rgba(255,255,255,0.6) 40px)',
            }} />
          <div className="absolute inset-0 bg-gradient-to-t from-black/30 to-transparent" />
          <div className="relative z-10 p-8 flex items-end justify-between w-full">
            <div>
              <h1 className="font-extrabold text-white text-4xl leading-tight tracking-tight">
                Phân tích &amp; Báo cáo
              </h1>
              <p className="text-white/80 font-medium mt-1 text-sm">
                Hệ thống giám sát hiệu năng dịch vụ công theo thời gian thực
              </p>
            </div>
            <button
              onClick={load}
              className="bg-white/20 hover:bg-white/30 text-white p-2 rounded-full transition-colors"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            </button>
          </div>
        </div>

        {/* ── Error ─────────────────────────────────────────────────────── */}
        {error && !stats && (
          <div className="flex items-center gap-3 bg-red-50 border border-red-200 rounded-2xl p-4 mb-6">
            <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0" />
            <p className="text-sm text-red-700">{error}</p>
            <button onClick={load} className="ml-auto text-sm font-bold text-red-700 underline">
              Thử lại
            </button>
          </div>
        )}

        {/* ── Loading skeleton ───────────────────────────────────────────── */}
        {loading ? (
          <div className="flex items-center justify-center py-20">
            <RefreshCw className="w-7 h-7 animate-spin" style={{ color: PRIMARY }} />
          </div>
        ) : (
          <>
            {/* spacer from hero */}
            {/* ── KPI Cards ─────────────────────────────────────────────── */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-6">
              <KpiCard
                label="Tổng người dùng"
                value={totalUsers.toLocaleString('vi-VN')}
                deltaLabel="Tài khoản đã đăng ký"
                accentColor={PRIMARY}
              />
              <KpiCard
                label="Tổng hồ sơ tiếp nhận"
                value={totalApps.toLocaleString('vi-VN')}
                deltaLabel={`${pending.toLocaleString('vi-VN')} đang xử lý`}
                accentColor="#705d00"
              />
              <KpiCard
                label="Tỷ lệ xử lý đúng hạn"
                value={onTimeRate}
                deltaLabel={resolved > 0 ? `${approved}/${resolved} hồ sơ đã duyệt` : 'Chưa có dữ liệu'}
                accentColor={PRIMARY}
              />
              <KpiCard
                label="Thời gian xử lý TB"
                value={avgValue === '–' ? '–' : `${avgValue}đ`}
                deltaLabel={avgValue === '–' ? 'Chưa đủ dữ liệu' : 'ngày / hồ sơ'}
                accentColor="#705d00"
              />
            </div>

            {/* ── Charts bento ──────────────────────────────────────────── */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
              {/* Bar chart — 2 / 3 */}
              <div className="md:col-span-2">
                <TimeSeriesChart data={timeseries} />
              </div>

              {/* Donut — 1 / 3 */}
              <ApprovalDonut
                approved={approved}
                pending={pendingAdj}
                rejected={rejected}
              />
            </div>

            {/* ── Detailed analysis ─────────────────────────────────────── */}
            <div className="bg-white p-5 shadow-sm rounded-2xl border border-gray-100">
              <div className="flex justify-between items-start mb-5">
                <div>
                  <h3 className="text-lg font-bold text-gray-900">Báo cáo phân tích chuyên sâu</h3>
                  <p className="text-sm text-gray-400 mt-0.5">
                    Tổng hợp từ {totalApps.toLocaleString('vi-VN')} hồ sơ trên toàn hệ thống
                  </p>
                </div>
                <button
                  className="flex items-center gap-1.5 text-sm font-bold hover:underline"
                  style={{ color: PRIMARY }}
                >
                  Xem chi tiết
                </button>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Left — image + quote */}
                <div className="space-y-5">
                  {/* Top 5 thủ tục được nộp nhiều nhất */}
                  <div className="rounded-2xl bg-gradient-to-br from-[#fff4f4] to-[#ffe9ea] p-4">
                    <p className="text-[10px] uppercase font-semibold text-[#9f364c]/70 tracking-widest mb-3">
                      Top thủ tục được nộp nhiều nhất
                    </p>
                    {(stats?.topProcedures ?? []).length === 0 ? (
                      <p className="text-xs text-gray-400">Chưa có hồ sơ.</p>
                    ) : (
                      <ol className="space-y-2">
                        {(stats?.topProcedures ?? []).map((p: any, i: number) => (
                          <li key={p.id} className="flex items-center gap-3">
                            <span className="flex-shrink-0 w-5 h-5 rounded-full text-[10px] font-bold
                              flex items-center justify-center text-white"
                              style={{ backgroundColor: PRIMARY }}>{i + 1}</span>
                            <span className="text-xs text-gray-700 flex-1 truncate" title={p.name}>{p.name}</span>
                            <span className="text-xs font-bold" style={{ color: PRIMARY }}>{p.count}</span>
                          </li>
                        ))}
                      </ol>
                    )}
                  </div>
                  <p className="text-sm text-gray-500 leading-relaxed italic border-l-2 border-yellow-400 pl-4">
                    {avgValue === '–'
                      ? 'Hệ thống đang tổng hợp dữ liệu xử lý hồ sơ để đưa ra phân tích thời gian.'
                      : `Thời gian xử lý trung bình mỗi hồ sơ là ${avgValue} ngày, với tỷ lệ duyệt đúng hạn đạt ${onTimeRate}.`}
                  </p>
                </div>

                {/* Right — category bars */}
                <div>
                  <h4 className="font-bold text-gray-900 text-xs uppercase tracking-widest mb-5">
                    Top lĩnh vực tiếp nhận
                  </h4>
                  <div className="space-y-4">
                    {categories.length === 0 ? (
                      <p className="text-xs text-gray-400 py-4">Chưa có hồ sơ để thống kê theo lĩnh vực.</p>
                    ) : categories.map(({ label, pct }) => (
                      <div key={label} className="space-y-1">
                        <div className="flex justify-between text-xs font-bold text-gray-700 mb-1">
                          <span>{label}</span>
                          <span>{pct}%</span>
                        </div>
                        <div className="w-full h-1.5 bg-[#de9ca4]/20 rounded-full">
                          <div
                            className="h-full rounded-full transition-all duration-1000"
                            style={{ width: `${pct}%`, backgroundColor: PRIMARY }}
                          />
                        </div>
                      </div>
                    ))}
                  </div>

                  {/* Evaluation summary */}
                  {evalStats && (
                    <div className="mt-6 pt-6 border-t border-gray-100 space-y-2">
                      <p className="text-[10px] uppercase font-semibold text-gray-400 tracking-widest mb-3">
                        Mức độ hài lòng
                      </p>
                      {[
                        {
                          label: 'Điểm trung bình',
                          value: `${evalStats.avgRating} ★`,
                          Icon: CheckCircle2,
                          color: '#e9c400',
                        },
                        {
                          label: 'Tỷ lệ hài lòng',
                          value: `${evalStats.satisfactionRate ?? '–'}%`,
                          Icon: TrendingUp,
                          color: '#16a34a',
                        },
                        {
                          label: 'Tổng đánh giá',
                          value: (evalStats.totalEvaluations ?? 0).toLocaleString(),
                          Icon: Users,
                          color: '#2563eb',
                        },
                      ].map(({ label, value, Icon, color }) => (
                        <div key={label} className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <Icon className="w-3.5 h-3.5 flex-shrink-0" style={{ color }} />
                            <span className="text-xs text-gray-600">{label}</span>
                          </div>
                          <span className="text-xs font-bold text-gray-900">{value}</span>
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Queue quick stats */}
                  {stats && (
                    <div className="mt-4 pt-4 border-t border-gray-100 grid grid-cols-2 gap-3">
                      {[
                        { label: 'Địa điểm',    value: stats.totalLocations  ?? '–', Icon: Clock },
                        { label: 'Thủ tục',     value: stats.totalProcedures ?? '–', Icon: FileText },
                        { label: 'Vé hôm nay',  value: stats.ticketsToday    ?? '–', Icon: BarChart2 },
                        { label: 'Đang chờ',    value: stats.waitingToday    ?? '–', Icon: AlertCircle },
                      ].map(({ label, value, Icon }) => (
                        <div key={label} className="flex items-center gap-2">
                          <Icon className="w-3.5 h-3.5 text-gray-400 flex-shrink-0" />
                          <div>
                            <p className="text-base font-bold text-gray-900 leading-none">{value}</p>
                            <p className="text-[9px] text-gray-400">{label}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* ── Pending alert ─────────────────────────────────────────── */}
            {pending > 0 && (
              <div className="mt-4 bg-amber-50 border border-amber-200 rounded-2xl p-4 flex items-center gap-3">
                <AlertCircle className="w-5 h-5 text-amber-600 flex-shrink-0" />
                <p className="text-sm text-amber-800 font-medium">
                  <strong>{pending}</strong> hồ sơ đang chờ duyệt —
                  vào tab <em>Hồ sơ</em> để xử lý
                </p>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
