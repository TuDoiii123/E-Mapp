/**
 * AdminSystemScreen — Cấu hình hệ thống
 *
 * Redesigned to match desktop Heritage design:
 *  - Hero header + breadcrumb
 *  - Tính năng ứng dụng (4 feature toggles with left accent bar)
 *  - 2-col grid: Chế độ hệ thống + Banner thông báo
 *  - Thông tin ứng dụng (plinth inputs)
 *  - Thông tin kỹ thuật (read-only grid)
 *  - Save button
 *  - Nhật ký hành động tab (audit log)
 *
 * Backend:
 *   GET  /api/admin/settings        → load tất cả settings
 *   PUT  /api/admin/settings/:key   → toggle từng setting
 *   PUT  /api/admin/settings        → save nhóm (batch)
 *   GET  /api/admin/audit-logs      → danh sách hành động admin
 */
import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  RefreshCw, Settings, ScrollText, Bell, Shield, Server,
  Globe, ChevronLeft, ChevronRight,
  User, AlertCircle, CheckCircle2, Info, Inbox,
  Megaphone, Phone, Mail, MapPin, Save,
  Loader2, Mic, BotMessageSquare, Home, Bug,
} from 'lucide-react';
import * as adminSvc from '../services/adminService';

const PRIMARY = '#8f000d';

interface Props { onNavigate: (s: string, p?: any) => void }

// ── Toast ─────────────────────────────────────────────────────────────────────
function Toast({ text, ok }: { text: string; ok: boolean }) {
  return (
    <div className={`fixed bottom-24 left-1/2 -translate-x-1/2 z-50 px-5 py-3 rounded-full
      shadow-xl text-sm font-semibold text-white flex items-center gap-2 max-w-sm
      ${ok ? 'bg-green-600' : 'bg-red-700'}`}>
      {ok
        ? <CheckCircle2 className="w-4 h-4 flex-shrink-0" />
        : <AlertCircle  className="w-4 h-4 flex-shrink-0" />}
      {text}
    </div>
  );
}

// ── CSS Toggle Switch (peer pattern) ─────────────────────────────────────────
function Switch({
  checked, onChange, disabled,
}: {
  checked: boolean; onChange: (v: boolean) => void; disabled?: boolean;
}) {
  return (
    <label className="relative inline-flex items-center cursor-pointer flex-shrink-0">
      <input
        type="checkbox"
        checked={checked}
        onChange={e => !disabled && onChange(e.target.checked)}
        disabled={disabled}
        className="sr-only peer"
      />
      <div
        className={[
          'w-11 h-6 rounded-full relative transition-colors duration-200',
          'after:content-[\'\'] after:absolute after:top-[2px] after:left-[2px]',
          'after:bg-white after:border after:border-gray-300 after:rounded-full',
          'after:h-5 after:w-5 after:transition-all after:duration-200',
          'peer-checked:after:translate-x-5',
          checked ? 'bg-[#8f000d]' : 'bg-gray-300',
          disabled ? 'opacity-50 cursor-not-allowed' : '',
        ].join(' ')}
      />
    </label>
  );
}

// ── Feature Row ───────────────────────────────────────────────────────────────
function FeatureRow({
  icon, label, desc, value, saving, onChange,
}: {
  icon: React.ReactNode; label: string; desc?: string;
  value: boolean; saving?: boolean; onChange(v: boolean): void;
}) {
  return (
    <div className="flex items-center justify-between py-5 border-b border-[#de9ca4]/15 last:border-0">
      <div className="flex items-center gap-5">
        <div className="w-12 h-12 flex items-center justify-center bg-white flex-shrink-0 shadow-sm">
          {icon}
        </div>
        <div className="min-w-0">
          <h4 className="text-sm font-bold text-gray-900 leading-tight">{label}</h4>
          {desc && <p className="text-gray-500 text-xs mt-0.5 leading-snug">{desc}</p>}
        </div>
      </div>
      <div className="ml-6 flex-shrink-0">
        {saving
          ? <Loader2 className="w-5 h-5 animate-spin text-gray-400" />
          : <Switch checked={value} onChange={onChange} />}
      </div>
    </div>
  );
}

// ── System Mode Card ──────────────────────────────────────────────────────────
function ModeCard({
  label, desc, value, saving, onChange,
}: {
  label: string; desc: string;
  value: boolean; saving?: boolean; onChange(v: boolean): void;
}) {
  return (
    <div className="p-5 bg-white rounded-2xl border border-[#de9ca4]/20">
      <div className="flex items-center justify-between mb-1.5">
        <h4 className="text-sm font-bold text-gray-900">{label}</h4>
        {saving
          ? <Loader2 className="w-5 h-5 animate-spin text-gray-400 flex-shrink-0" />
          : <Switch checked={value} onChange={onChange} />}
      </div>
      <p className="text-gray-500 text-xs leading-snug">{desc}</p>
    </div>
  );
}

// ════════════════════════════════════════════════════════════════════════════════
// SETTINGS TAB
// ════════════════════════════════════════════════════════════════════════════════
function SettingsTab() {
  const [raw,       setRaw]       = useState<Record<string, any>>({});
  const [loading,   setLoading]   = useState(true);
  const [saving,    setSaving]    = useState<Record<string, boolean>>({});
  const [savingAll, setSavingAll] = useState(false);
  const [toast,     setToast]     = useState<{ text: string; ok: boolean } | null>(null);
  const [appInfo,   setAppInfo]   = useState({
    appName: '', contactEmail: '', contactPhone: '', contactAddress: '',
  });
  const [banner, setBanner] = useState({ announcementText: '', announcementType: 'info' });

  const showToast = (text: string, ok: boolean) => {
    setToast({ text, ok });
    setTimeout(() => setToast(null), 3200);
  };

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const res = await adminSvc.getSystemSettings();
      const data: Record<string, any> = res.data ?? {};
      setRaw(data);
      setAppInfo({
        appName:        data.appName?.rawValue        ?? data.appName?.value        ?? '',
        contactEmail:   data.contactEmail?.rawValue   ?? data.contactEmail?.value   ?? '',
        contactPhone:   data.contactPhone?.rawValue   ?? data.contactPhone?.value   ?? '',
        contactAddress: data.contactAddress?.rawValue ?? data.contactAddress?.value ?? '',
      });
      setBanner({
        announcementText: data.announcementText?.rawValue ?? data.announcementText?.value ?? '',
        announcementType: data.announcementType?.rawValue ?? data.announcementType?.value ?? 'info',
      });
    } catch {
      showToast('Không tải được cài đặt', false);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  // Toggle một setting boolean (optimistic)
  const toggle = async (key: string, newVal: boolean) => {
    setSaving(s => ({ ...s, [key]: true }));
    setRaw(prev => ({ ...prev, [key]: { ...prev[key], value: newVal } }));
    try {
      await adminSvc.updateSystemSetting(key, newVal);
      showToast(
        newVal ? `Đã bật: ${raw[key]?.label ?? key}` : `Đã tắt: ${raw[key]?.label ?? key}`,
        true,
      );
    } catch (e: any) {
      setRaw(prev => ({ ...prev, [key]: { ...prev[key], value: !newVal } }));
      showToast(e.message || 'Lỗi cập nhật', false);
    } finally {
      setSaving(s => ({ ...s, [key]: false }));
    }
  };

  // Lưu toàn bộ cấu hình (batch)
  const saveAll = async () => {
    setSavingAll(true);
    try {
      await adminSvc.updateSystemSettings({
        ...appInfo,
        announcementText: banner.announcementText,
        announcementType: banner.announcementType,
      });
      showToast('Đã lưu cấu hình hệ thống', true);
    } catch (e: any) {
      showToast(e.message || 'Lỗi lưu cài đặt', false);
    } finally {
      setSavingAll(false);
    }
  };

  const getBool = (key: string, fallback = false): boolean =>
    typeof raw[key]?.value === 'boolean' ? raw[key].value : fallback;

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-48 gap-3">
        <Loader2 className="w-6 h-6 animate-spin text-gray-400" />
        <p className="text-xs text-gray-400">Đang tải cài đặt...</p>
      </div>
    );
  }

  const FEATURES = [
    {
      key: 'enableChatbot',
      icon: <BotMessageSquare className="w-6 h-6" style={{ color: PRIMARY }} />,
      label: 'Trợ lý Chatbot AI',
      desc:  'Bật/tắt chatbot hỗ trợ tự động trên toàn hệ thống dịch vụ công.',
      fallback: true,
    },
    {
      key: 'enableQueue',
      icon: <ScrollText className="w-6 h-6" style={{ color: PRIMARY }} />,
      label: 'Hàng đợi trực tuyến',
      desc:  'Cho phép người dân đăng ký lấy số thứ tự giải quyết thủ tục qua ứng dụng.',
      fallback: true,
    },
    {
      key: 'enableVoice',
      icon: <Mic className="w-6 h-6" style={{ color: PRIMARY }} />,
      label: 'Đặt lịch bằng giọng nói',
      desc:  'Tính năng Voice AI cho phép hội thoại để đặt lịch hẹn cán bộ.',
      fallback: false,
    },
    {
      key: 'enableNotifications',
      icon: <Bell className="w-6 h-6" style={{ color: PRIMARY }} />,
      label: 'Push notification',
      desc:  'Gửi thông báo đẩy tức thời tới người dùng điện thoại thông minh.',
      fallback: true,
    },
  ];

  const BANNER_TYPES = [
    { value: 'info',    label: 'Thông tin' },
    { value: 'warning', label: 'Cảnh báo'  },
    { value: 'error',   label: 'Khẩn cấp'  },
    { value: 'success', label: 'Thành công' },
  ];

  const APP_FIELDS: { icon: any; label: string; key: keyof typeof appInfo; placeholder: string }[] = [
    { icon: Globe,  label: 'Tên ứng dụng', key: 'appName',        placeholder: 'E-Mapp Dịch vụ công'    },
    { icon: Mail,   label: 'Email hỗ trợ', key: 'contactEmail',   placeholder: 'support@emapp.vn'        },
    { icon: Phone,  label: 'Hotline',       key: 'contactPhone',   placeholder: '1800 xxxx'               },
    { icon: MapPin, label: 'Địa chỉ',       key: 'contactAddress', placeholder: 'Số xx, đường...'         },
  ];

  return (
    <div className="space-y-4">
      {toast && <Toast text={toast.text} ok={toast.ok} />}

      {/* ── Tính năng ứng dụng ─────────────────────────────────────────── */}
      <section className="bg-white rounded-2xl p-5 shadow-sm overflow-hidden relative">
        <div className="absolute top-0 left-0 right-0 h-1 rounded-t-2xl" style={{ backgroundColor: PRIMARY }} />
        <div className="flex items-center gap-3 mb-5">
          <Settings className="w-5 h-5" style={{ color: PRIMARY }} />
          <h3 className="text-sm font-extrabold uppercase tracking-widest text-[#4d2128]">
            Tính năng ứng dụng
          </h3>
        </div>
        <div>
          {FEATURES.map(f => (
            <FeatureRow
              key={f.key}
              icon={f.icon}
              label={f.label}
              desc={f.desc}
              value={getBool(f.key, f.fallback)}
              saving={saving[f.key]}
              onChange={v => toggle(f.key, v)}
            />
          ))}
        </div>
      </section>

      {/* ── Chế độ hệ thống + Banner thông báo (2-col) ───────────────── */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

        {/* Chế độ hệ thống */}
        <section className="bg-white rounded-2xl p-5 shadow-sm overflow-hidden relative">
          <div className="absolute top-0 left-0 right-0 h-1 rounded-t-2xl bg-[#705d00]" />
          <div className="flex items-center gap-3 mb-5 mt-1">
            <Shield className="w-5 h-5 text-[#705d00]" />
            <h3 className="text-sm font-extrabold uppercase tracking-widest text-[#4d2128]">
              Chế độ hệ thống
            </h3>
          </div>
          <div className="space-y-4">
            <ModeCard
              label="Chế độ bảo trì"
              desc="Tạm dừng ứng dụng cho người dùng thường để cập nhật cơ sở dữ liệu."
              value={getBool('maintenanceMode', false)}
              saving={saving.maintenanceMode}
              onChange={v => toggle('maintenanceMode', v)}
            />
            <ModeCard
              label="Debug mode"
              desc="In log chi tiết ra console cho đội ngũ kỹ thuật giám sát."
              value={getBool('debugMode', false)}
              saving={saving.debugMode}
              onChange={v => toggle('debugMode', v)}
            />
          </div>
        </section>

        {/* Banner thông báo */}
        <section className="bg-white rounded-2xl p-5 shadow-sm overflow-hidden relative">
          <div className="absolute top-0 left-0 right-0 h-1 rounded-t-2xl bg-[#8f0402]" />
          <div className="flex items-center gap-3 mb-5 mt-1">
            <Megaphone className="w-5 h-5 text-[#8f0402]" />
            <h3 className="text-sm font-extrabold uppercase tracking-widest text-[#4d2128]">
              Banner thông báo
            </h3>
          </div>
          <div className="space-y-5">
            {/* Toggle bật/tắt */}
            <div className="flex items-center justify-between">
              <div>
                <h4 className="text-sm font-bold text-gray-900">Hiện banner trang chủ</h4>
                <p className="text-gray-500 text-xs mt-0.5">Hiển thị thông báo nổi bật ở đầu trang chủ.</p>
              </div>
              {saving.announcementActive
                ? <Loader2 className="w-5 h-5 animate-spin text-gray-400 flex-shrink-0 ml-4" />
                : <Switch
                    checked={getBool('announcementActive', false)}
                    onChange={v => toggle('announcementActive', v)}
                  />
              }
            </div>

            {/* Loại thông báo */}
            <div>
              <p className="text-[10px] font-extrabold uppercase tracking-widest text-gray-400 mb-2">
                Loại thông báo
              </p>
              <div className="flex flex-wrap gap-2">
                {BANNER_TYPES.map(t => (
                  <button
                    key={t.value}
                    onClick={() => setBanner(b => ({ ...b, announcementType: t.value }))}
                    className={`px-3 py-1.5 text-xs font-bold rounded-full transition-all
                      ${banner.announcementType === t.value
                        ? 'text-white'
                        : 'bg-[#fff4f4] text-[#9f364c]/70 hover:bg-[#de9ca4]/20'}`}
                    style={banner.announcementType === t.value
                      ? { backgroundColor: PRIMARY }
                      : undefined}
                  >
                    {t.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Nội dung */}
            <div>
              <p className="text-[10px] font-extrabold uppercase tracking-widest text-gray-400 mb-2">
                Nội dung thông báo
              </p>
              <textarea
                value={banner.announcementText}
                onChange={e => setBanner(b => ({ ...b, announcementText: e.target.value }))}
                rows={3}
                placeholder="Nhập nội dung hiển thị trên banner trang chủ..."
                className="w-full bg-white border-none outline-none text-sm p-4 resize-none
                  focus:ring-2 focus:ring-[#8f000d]/20"
              />
            </div>
          </div>
        </section>
      </div>

      {/* ── Thông tin ứng dụng ─────────────────────────────────────────── */}
      <section className="bg-white rounded-2xl p-5 shadow-sm overflow-hidden relative">
        <div className="absolute top-0 left-0 right-0 h-1 rounded-t-2xl bg-blue-500" />
        <div className="flex items-center gap-3 mb-5 mt-1">
          <Server className="w-5 h-5 text-blue-500" />
          <h3 className="text-sm font-extrabold uppercase tracking-widest text-[#4d2128]">
            Thông tin ứng dụng
          </h3>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-8 gap-y-5">
          {APP_FIELDS.map(f => {
            const Icon = f.icon;
            return (
              <div key={f.key}>
                <label className="flex items-center gap-1.5 text-[10px] font-extrabold uppercase tracking-widest text-[#9f364c]/60 mb-2">
                  <Icon className="w-3.5 h-3.5" />
                  {f.label}
                </label>
                <input
                  type="text"
                  value={appInfo[f.key]}
                  onChange={e => setAppInfo(a => ({ ...a, [f.key]: e.target.value }))}
                  placeholder={f.placeholder}
                  className="w-full bg-transparent border-b-2 border-[#de9ca4]/40 focus:border-[#8f000d]
                    outline-none px-1 py-2 text-sm text-[#4d2128] transition-colors"
                />
              </div>
            );
          })}
        </div>
      </section>

      {/* ── Thông tin kỹ thuật (read-only) ────────────────────────────── */}
      <section className="bg-white rounded-2xl p-5 shadow-sm overflow-hidden relative">
        <div className="absolute top-0 left-0 right-0 h-1 rounded-t-2xl bg-[#de9ca4]/50" />
        <div className="flex items-center gap-3 mb-5 mt-1">
          <Info className="w-5 h-5 text-[#9f364c]/60" />
          <h3 className="text-sm font-extrabold uppercase tracking-widest text-[#4d2128]">
            Thông tin kỹ thuật
          </h3>
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-x-8">
          {[
            ['Phiên bản',  'v2.0.0'],
            ['Môi trường', 'Production'],
            ['Backend',    'Flask + PostgreSQL'],
            ['AI Engine',  'Claude (Anthropic)'],
            ['RAG',        'ChromaDB + LangChain'],
            ['Realtime',   'WebSocket (gevent)'],
          ].map(([l, v]) => (
            <div key={String(l)} className="flex justify-between items-center py-2 border-b border-[#de9ca4]/15">
              <span className="text-xs text-[#9f364c]/60">{l}</span>
              <span className="text-xs font-semibold text-[#4d2128]">{v}</span>
            </div>
          ))}
        </div>
      </section>

      {/* ── Save ────────────────────────────────────────────────────────── */}
      <div className="flex justify-end pt-2 pb-6">
        <button
          onClick={saveAll}
          disabled={savingAll}
          className="text-white px-10 py-4 font-bold uppercase tracking-widest
            hover:opacity-90 active:scale-95 transition-all shadow-lg
            flex items-center gap-3 disabled:opacity-60"
          style={{ backgroundColor: PRIMARY }}
        >
          {savingAll
            ? <Loader2 className="w-5 h-5 animate-spin" />
            : <Save    className="w-5 h-5" />}
          Lưu cấu hình hệ thống
        </button>
      </div>
    </div>
  );
}

// ════════════════════════════════════════════════════════════════════════════════
// AUDIT LOG TAB
// ════════════════════════════════════════════════════════════════════════════════
const ACTION_BADGE: Record<string, string> = {
  CREATE: 'bg-green-100 text-green-700 border-green-200',
  UPDATE: 'bg-blue-100  text-blue-700  border-blue-200',
  DELETE: 'bg-red-100   text-red-700   border-red-200',
  REVIEW: 'bg-purple-100 text-purple-700 border-purple-200',
  REPLY:  'bg-yellow-100 text-yellow-700 border-yellow-200',
  LOGIN:  'bg-gray-100  text-gray-600  border-gray-200',
};
const RESOURCE_ICON: Record<string, any> = {
  user:            User,
  location:        Globe,
  procedure:       ScrollText,
  application:     CheckCircle2,
  system_settings: Settings,
  evaluation:      Bell,
};

function AuditLogTab() {
  const [items,    setItems]    = useState<any[]>([]);
  const [loading,  setLoading]  = useState(true);
  const [page,     setPage]     = useState(1);
  const [total,    setTotal]    = useState(0);
  const [resource, setResource] = useState('');
  const LIMIT = 20;

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const params: Record<string, string> = { page: String(page), limit: String(LIMIT) };
      if (resource) params.resource = resource;
      const r = await adminSvc.getAuditLogs(params);
      setItems(r.data ?? []);
      setTotal(r.pagination?.total ?? 0);
    } catch { /* ignore */ }
    finally { setLoading(false); }
  }, [page, resource]);

  useEffect(() => { load(); }, [load]);

  const totalPages = Math.max(1, Math.ceil(total / LIMIT));

  const FILTERS = [
    { value: '',                label: 'Tất cả'    },
    { value: 'user',            label: 'Tài khoản' },
    { value: 'location',        label: 'Địa điểm'  },
    { value: 'procedure',       label: 'Thủ tục'   },
    { value: 'application',     label: 'Hồ sơ'     },
    { value: 'evaluation',      label: 'Đánh giá'  },
    { value: 'system_settings', label: 'Cài đặt'   },
  ];

  return (
    <div className="space-y-4">

      {/* Filter chips + refresh */}
      <div className="flex items-center justify-between bg-white rounded-2xl p-4 shadow-sm">
        <div className="flex gap-2 flex-wrap">
          {FILTERS.map(o => (
            <button
              key={o.value}
              onClick={() => { setResource(o.value); setPage(1); }}
              className={`px-3 py-1.5 text-xs font-bold rounded-full uppercase tracking-wide transition-all
                ${resource === o.value
                  ? 'text-white'
                  : 'bg-[#fff4f4] text-[#9f364c]/70 hover:bg-[#de9ca4]/20 border border-[#de9ca4]/30'}`}
              style={resource === o.value ? { backgroundColor: PRIMARY } : undefined}
            >
              {o.label}
            </button>
          ))}
        </div>
        <button
          onClick={load}
          className="ml-3 p-2 bg-[#fff4f4] rounded-xl border border-[#de9ca4]/30 text-[#9f364c]/60 hover:text-[#8f000d]
            transition-colors flex-shrink-0"
          title="Làm mới"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {loading ? (
        <div className="flex justify-center py-10">
          <Loader2 className="w-6 h-6 animate-spin text-[#9f364c]/60" />
        </div>
      ) : items.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-14 gap-3 bg-white rounded-2xl">
          <Inbox className="w-12 h-12 text-[#de9ca4]/50" />
          <p className="text-sm text-[#9f364c]/60">Chưa có nhật ký</p>
        </div>
      ) : (
        <div className="space-y-2">
          {items.map(log => {
            const IconComp = RESOURCE_ICON[log.resource] || Shield;
            const dateStr = log.createdAt
              ? new Date(log.createdAt).toLocaleString('vi-VN', {
                  day: '2-digit', month: '2-digit',
                  hour: '2-digit', minute: '2-digit',
                })
              : '–';
            return (
              <div key={log.id} className="bg-white rounded-2xl px-4 py-4 border border-[#de9ca4]/20 flex items-start gap-4">
                <div className="w-9 h-9 bg-[#fff4f4] rounded-xl flex items-center justify-center flex-shrink-0 mt-0.5">
                  <IconComp className="w-4 h-4 text-[#9f364c]/60" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold border
                      ${ACTION_BADGE[log.action] ?? 'bg-[#fff4f4] text-[#9f364c]/70 border-[#de9ca4]/30'}`}>
                      {log.action}
                    </span>
                    <span className="text-xs text-[#4d2128]/70 font-medium">
                      {log.resource}
                      {log.resourceId ? ` #${String(log.resourceId).slice(0, 8)}` : ''}
                    </span>
                  </div>
                  <p className="text-[10px] text-[#9f364c]/50 mt-1">
                    {log.actorRole === 'admin' ? '👤 Admin' : (log.actorRole ?? '–')}
                    {' · '}{dateStr}
                    {log.ip ? ` · ${log.ip}` : ''}
                  </p>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Pagination */}
      {total > LIMIT && (
        <div className="flex justify-center items-center gap-4 pt-2 pb-6">
          <button
            disabled={page === 1}
            onClick={() => setPage(p => p - 1)}
            className="w-9 h-9 flex items-center justify-center bg-white rounded-xl border border-[#de9ca4]/30 disabled:opacity-40 hover:border-[#8f000d] transition-colors"
          >
            <ChevronLeft className="w-4 h-4 text-[#4d2128]" />
          </button>
          <span className="text-sm font-medium text-[#4d2128]/70">
            Trang <span className="font-bold text-[#4d2128]">{page}</span> / {totalPages}
          </span>
          <button
            disabled={page >= totalPages}
            onClick={() => setPage(p => p + 1)}
            className="w-9 h-9 flex items-center justify-center bg-white rounded-xl border border-[#de9ca4]/30 disabled:opacity-40 hover:border-[#8f000d] transition-colors"
          >
            <ChevronRight className="w-4 h-4 text-[#4d2128]" />
          </button>
        </div>
      )}
    </div>
  );
}

// ════════════════════════════════════════════════════════════════════════════════
// MAIN COMPONENT
// ════════════════════════════════════════════════════════════════════════════════
export function AdminSystemScreen({ onNavigate }: Props) {
  const [tab, setTab] = useState<'settings' | 'auditlog'>('settings');

  return (
    <div className="min-h-screen bg-transparent">

      {/* ── Page header ──────────────────────────────────────────────── */}
      <div className="bg-white/70 border-b border-[#de9ca4]/20 px-6 pt-8 pb-5">
        <h2 className="text-2xl font-extrabold text-[#4d2128] tracking-tight mb-1.5">
          Cấu hình hệ thống
        </h2>
        <div className="flex items-center gap-2 text-[#9f364c]/60 text-[11px]">
          <Home className="w-3.5 h-3.5" />
          <span className="font-bold uppercase tracking-widest">Trang chủ / Cài đặt hệ thống</span>
        </div>
      </div>

      {/* ── Tab bar ──────────────────────────────────────────────────── */}
      <div className="bg-white/70 border-b border-[#de9ca4]/20 px-6">
        <div className="flex">
          {[
            { key: 'settings',  label: 'Cài đặt'            },
            { key: 'auditlog',  label: 'Nhật ký hành động'   },
          ].map(t => (
            <button
              key={t.key}
              onClick={() => setTab(t.key as any)}
              className={`px-5 py-3.5 text-xs font-bold uppercase tracking-widest border-b-2 transition-colors
                ${tab === t.key
                  ? 'border-[#8f000d] text-[#8f000d]'
                  : 'border-transparent text-[#9f364c]/50 hover:text-[#9f364c]'}`}
            >
              {t.label}
            </button>
          ))}
        </div>
      </div>

      {/* ── Content ──────────────────────────────────────────────────── */}
      <div className="p-4">
        {tab === 'settings' && <SettingsTab />}
        {tab === 'auditlog' && <AuditLogTab />}
      </div>
    </div>
  );
}
