/**
 * AdminForecastScreen — Dự báo cao điểm hàng chờ
 *
 * Layout:
 *   • Header (agency selector)
 *   • Heatmap tuần (7 ngày × giờ làm việc) theo mức độ đông (low/medium/high)
 *   • Dự báo ngắn hạn (N giờ tới) — nguồn AI/LSTM hoặc thống kê
 *   • Cảnh báo cao điểm
 *
 * Data: forecastSvc.weekly(agencyId) + forecastSvc.shortTerm(agencyId, 8)
 */
import React, { useState, useEffect, useCallback } from 'react';
import {
  RefreshCw, TrendingUp, AlertTriangle, Calendar, BarChart2,
} from 'lucide-react';
import * as forecastSvc from '../../services/forecastService';
import type {
  WeeklyForecastResponse, ShortTermForecastResponse, ForecastLevel,
} from '../../services/forecastService';

interface Props { onNavigate: (s: string, p?: any) => void }

const PRIMARY = '#8f000d';

const AGENCIES = [
  { id: 'ubnd-tp-thanhhoa', name: 'UBND TP Thanh Hóa' },
  { id: 'ubnd-quangxuong',  name: 'UBND huyện Quảng Xương' },
  { id: 'ubnd-samson',      name: 'UBND TP Sầm Sơn' },
  { id: 'ubnd-bimson',      name: 'UBND thị xã Bỉm Sơn' },
  { id: 'ubnd-nghison',     name: 'UBND thị xã Nghi Sơn' },
  { id: 'ubnd-dongson',     name: 'UBND huyện Đông Sơn' },
  { id: 'congan-thanhhoa',  name: 'Công an tỉnh Thanh Hóa' },
  { id: 'bhxh-thanhhoa',    name: 'BHXH tỉnh Thanh Hóa' },
];

const WEEKDAY_LABELS = ['T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'CN'];
const HOURS = Array.from({ length: 11 }, (_, i) => i + 7); // 7..17

const LEVEL_STYLE: Record<ForecastLevel, { bg: string; text: string; label: string }> = {
  low:    { bg: '#dcfce7', text: '#166534', label: 'Thấp' },
  medium: { bg: '#fde68a', text: '#92400e', label: 'Trung bình' },
  high:   { bg: '#fecaca', text: '#991b1b', label: 'Cao' },
};

const EMPTY_CELL_BG = '#f3f4f6';

/* ── Heatmap card ──────────────────────────────────────────────────────────── */
function WeeklyHeatmap({ profile }: { profile: WeeklyForecastResponse['profile'] }) {
  const map = new Map<number, WeeklyForecastResponse['profile'][number]>();
  for (const cell of profile) {
    map.set(cell.weekday * 100 + cell.hour, cell);
  }

  return (
    <div className="bg-white p-5 rounded-2xl shadow-sm mb-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Calendar className="w-4 h-4" style={{ color: PRIMARY }} />
          <h2 className="text-base font-bold text-gray-900">Bản đồ nhiệt cao điểm theo tuần</h2>
        </div>
      </div>

      {profile.length === 0 ? (
        <div className="h-[160px] flex items-center justify-center text-sm text-gray-400">
          Chưa có dữ liệu dự báo cho cơ quan này.
        </div>
      ) : (
        <>
          <div className="overflow-x-auto">
            <table className="border-separate" style={{ borderSpacing: 4 }}>
              <thead>
                <tr>
                  <th className="w-10" />
                  {HOURS.map(h => (
                    <th key={h} className="text-[10px] font-bold text-gray-400 px-1">
                      {h}h
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {WEEKDAY_LABELS.map((label, weekday) => (
                  <tr key={weekday}>
                    <td className="text-[11px] font-bold text-gray-500 pr-2 text-right">{label}</td>
                    {HOURS.map(hour => {
                      const cell = map.get(weekday * 100 + hour);
                      const style = cell ? LEVEL_STYLE[cell.level] : null;
                      return (
                        <td key={hour}>
                          <div
                            className={`w-9 h-9 rounded-lg flex items-center justify-center text-[10px] font-bold
                              ${cell?.peak ? 'ring-2 ring-offset-1' : ''}`}
                            style={{
                              backgroundColor: style ? style.bg : EMPTY_CELL_BG,
                              color: style ? style.text : '#9ca3af',
                              ...(cell?.peak ? { boxShadow: `0 0 0 2px ${PRIMARY}` } : {}),
                            }}
                            title={cell
                              ? `${label} ${hour}h — TB ${Math.round(cell.avg)} khách${cell.peak ? ' (cao điểm)' : ''}`
                              : `${label} ${hour}h — chưa có dữ liệu`}
                          >
                            {cell ? Math.round(cell.avg) : '–'}
                          </div>
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Legend */}
          <div className="flex items-center gap-4 mt-4 text-[11px] text-gray-500">
            {(['low', 'medium', 'high'] as ForecastLevel[]).map(lvl => (
              <span key={lvl} className="flex items-center gap-1.5">
                <span className="w-3 h-3 rounded-sm" style={{ backgroundColor: LEVEL_STYLE[lvl].bg }} />
                {LEVEL_STYLE[lvl].label}
              </span>
            ))}
            <span className="flex items-center gap-1.5">
              <span className="w-3 h-3 rounded-sm border-2" style={{ borderColor: PRIMARY }} />
              Giờ cao điểm
            </span>
          </div>
        </>
      )}
    </div>
  );
}

/* ── Short-term forecast card ─────────────────────────────────────────────── */
function ShortTermForecastCard({ data }: { data: ShortTermForecastResponse }) {
  const isLstm = data.source === 'lstm';

  return (
    <div className="bg-white p-5 rounded-2xl shadow-sm mb-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <TrendingUp className="w-4 h-4" style={{ color: PRIMARY }} />
          <h2 className="text-base font-bold text-gray-900">Dự báo 8 giờ tới</h2>
        </div>
        <span
          className="text-[10px] font-bold uppercase tracking-wide px-2.5 py-1 rounded-full"
          style={isLstm
            ? { backgroundColor: `${PRIMARY}15`, color: PRIMARY }
            : { backgroundColor: '#f3f4f6', color: '#6b7280' }}
        >
          {isLstm ? 'AI / LSTM' : 'Thống kê'}
        </span>
      </div>

      {data.forecast.length === 0 ? (
        <div className="h-[100px] flex items-center justify-center text-sm text-gray-400">
          Chưa có dữ liệu dự báo ngắn hạn.
        </div>
      ) : (
        <div className="flex gap-2 overflow-x-auto pb-1">
          {data.forecast.map((item, i) => {
            const style = LEVEL_STYLE[item.level];
            const hourLabel = (item.time.split('T')[1] || '').padStart(2, '0');
            return (
              <div
                key={`${item.time}-${i}`}
                className={`flex-shrink-0 w-[72px] rounded-xl p-2.5 flex flex-col items-center gap-1
                  ${item.peak ? 'ring-2' : ''}`}
                style={{
                  backgroundColor: style.bg,
                  ...(item.peak ? { boxShadow: `0 0 0 2px ${PRIMARY}` } : {}),
                }}
                title={`${hourLabel}h — ${item.count} khách dự kiến${item.peak ? ' (cao điểm)' : ''}`}
              >
                <span className="text-[10px] font-bold" style={{ color: style.text }}>
                  {hourLabel}h
                </span>
                <span className="text-lg font-black" style={{ color: style.text }}>
                  {item.count}
                </span>
                <span className="text-[9px] font-semibold uppercase" style={{ color: style.text }}>
                  {style.label}
                </span>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

/* ── Warnings card ─────────────────────────────────────────────────────────── */
function WarningsCard({ warnings }: { warnings: ShortTermForecastResponse['warnings'] }) {
  return (
    <div className="bg-white p-5 rounded-2xl shadow-sm">
      <div className="flex items-center gap-2 mb-3">
        <AlertTriangle className="w-4 h-4" style={{ color: PRIMARY }} />
        <h2 className="text-base font-bold text-gray-900">Cảnh báo cao điểm</h2>
      </div>

      {warnings.length === 0 ? (
        <p className="text-sm text-gray-400">Không có khung giờ quá tải dự kiến.</p>
      ) : (
        <ul className="space-y-2">
          {warnings.map((w, i) => {
            const hourLabel = (w.time.split('T')[1] || '').padStart(2, '0');
            const dateLabel = w.time.split('T')[0];
            const style = LEVEL_STYLE[w.level];
            return (
              <li
                key={`${w.time}-${i}`}
                className="flex items-center gap-3 bg-red-50 border border-red-200 rounded-xl px-3 py-2"
              >
                <AlertTriangle className="w-4 h-4 text-red-500 flex-shrink-0" />
                <span className="text-sm text-red-800 font-medium flex-1">
                  {dateLabel} — {hourLabel}h
                </span>
                <span
                  className="text-[10px] font-bold uppercase px-2 py-0.5 rounded-full"
                  style={{ backgroundColor: style.bg, color: style.text }}
                >
                  {style.label}
                </span>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}

/* ── Main ──────────────────────────────────────────────────────────────────── */
export function AdminForecastScreen({ onNavigate }: Props) {
  const [agencyId, setAgencyId] = useState(AGENCIES[0].id);
  const [weekly, setWeekly]     = useState<WeeklyForecastResponse>({ profile: [], peakHours: [] });
  const [short, setShort]       = useState<ShortTermForecastResponse>({ source: 'stats', forecast: [], warnings: [] });
  const [loading, setLoading]   = useState(true);

  const load = useCallback(async (agency: string) => {
    setLoading(true);
    const [w, s] = await Promise.all([
      forecastSvc.weekly(agency),
      forecastSvc.shortTerm(agency, 8),
    ]);
    setWeekly(w);
    setShort(s);
    setLoading(false);
  }, []);

  useEffect(() => { load(agencyId); }, [agencyId, load]);

  return (
    <div className="min-h-full bg-transparent">
      <div className="px-4 py-4 pb-6">

        {/* ── Header ────────────────────────────────────────────────────── */}
        <div className="flex items-center justify-between mb-6 flex-wrap gap-3">
          <div>
            <h1 className="text-xl font-extrabold text-gray-900 flex items-center gap-2">
              <BarChart2 className="w-5 h-5" style={{ color: PRIMARY }} />
              Dự báo cao điểm hàng chờ
            </h1>
            <p className="text-sm text-gray-400 mt-0.5">
              Phân tích lưu lượng theo giờ để chủ động bố trí nhân sự quầy
            </p>
          </div>

          <div className="flex items-center gap-2">
            <select
              value={agencyId}
              onChange={e => setAgencyId(e.target.value)}
              className="text-sm font-medium text-gray-700 bg-white border border-gray-200 rounded-xl
                px-3 py-2 shadow-sm focus:outline-none focus:ring-2 focus:ring-[#8f000d]/30"
            >
              {AGENCIES.map(a => (
                <option key={a.id} value={a.id}>{a.name}</option>
              ))}
            </select>
            <button
              onClick={() => load(agencyId)}
              className="p-2 rounded-full hover:bg-gray-100 transition-colors"
              title="Làm mới"
            >
              <RefreshCw className={`w-4 h-4 text-gray-500 ${loading ? 'animate-spin' : ''}`} style={loading ? { color: PRIMARY } : undefined} />
            </button>
          </div>
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-20">
            <RefreshCw className="w-7 h-7 animate-spin" style={{ color: PRIMARY }} />
          </div>
        ) : (
          <>
            <WeeklyHeatmap profile={weekly.profile} />
            <ShortTermForecastCard data={short} />
            <WarningsCard warnings={short.warnings} />
          </>
        )}
      </div>
    </div>
  );
}
