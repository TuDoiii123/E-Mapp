/**
 * AdminSystemScreen — Cấu hình hệ thống
 *
 * Tabs:
 *  1. Cài đặt   — feature toggles, chế độ hệ thống, banner, thông tin app
 *  2. Nhật ký   — audit log với filter + pagination
 *
 * Backend:
 *   GET  /api/admin/settings        → load settings
 *   PUT  /api/admin/settings/:key   → toggle boolean setting
 *   PUT  /api/admin/settings        → save batch (appInfo + banner)
 *   GET  /api/admin/audit-logs      → audit log list
 */
import React, { useState, useEffect, useCallback } from 'react';
import {
  RefreshCw, Settings, ScrollText, Bell, Shield,
  Globe, ChevronLeft, ChevronRight,
  User, AlertCircle, CheckCircle2, Inbox,
  Megaphone, Phone, Mail, MapPin, Save,
  Loader2, Mic, BotMessageSquare, Server, LogOut,
} from 'lucide-react';
import * as adminSvc from '../../services/adminService';
import { useAuth } from '../../contexts/AuthContext';

const P = '#8f000d';

interface Props { onNavigate: (s: string, p?: any) => void }

/* ── Toast ─────────────────────────────────────────────────────────────────── */
function Toast({ text, ok }: { text: string; ok: boolean }) {
  return (
    <div className={`fixed bottom-24 left-1/2 -translate-x-1/2 z-50 px-4 py-2.5 rounded-full
      shadow-lg text-sm font-medium text-white flex items-center gap-2 whitespace-nowrap
      ${ok ? 'bg-green-600' : 'bg-red-700'}`}>
      {ok ? <CheckCircle2 className="w-4 h-4 flex-shrink-0" /> : <AlertCircle className="w-4 h-4 flex-shrink-0" />}
      {text}
    </div>
  );
}

/* ── Toggle Switch ─────────────────────────────────────────────────────────── */
function Toggle({ checked, onChange, disabled }: {
  checked: boolean; onChange(v: boolean): void; disabled?: boolean;
}) {
  return (
    <button
      role="switch"
      aria-checked={checked}
      disabled={disabled}
      onClick={() => !disabled && onChange(!checked)}
      className={`relative w-11 h-6 rounded-full transition-colors duration-200 flex-shrink-0
        focus:outline-none ${checked ? '' : 'bg-gray-300'} ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
      style={checked ? { backgroundColor: P } : undefined}
    >
      <span
        className={`absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full shadow transition-transform duration-200
          ${checked ? 'translate-x-5' : 'translate-x-0'}`}
      />
    </button>
  );
}

/* ── Section Card ──────────────────────────────────────────────────────────── */
function SectionCard({ title, icon, accentColor = P, children }: {
  title: string; icon: React.ReactNode; accentColor?: string; children: React.ReactNode;
}) {
  return (
    <div className="bg-white rounded-2xl shadow-sm overflow-hidden">
      <div className="h-0.5 w-full" style={{ backgroundColor: accentColor }} />
      <div className="px-4 pt-4 pb-1 flex items-center gap-2.5">
        <div className="w-7 h-7 rounded-lg flex items-center justify-center flex-shrink-0"
          style={{ backgroundColor: accentColor + '18' }}>
          <span style={{ color: accentColor }}>{icon}</span>
        </div>
        <h3 className="text-xs font-bold uppercase tracking-widest text-[#4d2128]">{title}</h3>
      </div>
      <div className="px-4 pb-4 pt-3">{children}</div>
    </div>
  );
}

/* ── Feature Toggle Row ────────────────────────────────────────────────────── */
function ToggleRow({ label, desc, checked, saving, onChange }: {
  label: string; desc: string; checked: boolean; saving?: boolean; onChange(v: boolean): void;
}) {
  return (
    <div className="flex items-center justify-between py-3 border-b border-[#de9ca4]/10 last:border-0">
      <div className="flex-1 min-w-0 pr-4">
        <p className="text-sm font-semibold text-gray-800 leading-tight">{label}</p>
        <p className="text-[11px] text-gray-400 mt-0.5 leading-snug">{desc}</p>
      </div>
      {saving
        ? <Loader2 className="w-4 h-4 animate-spin text-gray-400 flex-shrink-0" />
        : <Toggle checked={checked} onChange={onChange} />}
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════════════════
   TAB: CÀI ĐẶT
═══════════════════════════════════════════════════════════════════════════ */
function SettingsTab({ onNavigate }: { onNavigate: (s: string) => void }) {
  const { logout } = useAuth();
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
    setTimeout(() => setToast(null), 3000);
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

  const toggle = async (key: string, newVal: boolean) => {
    setSaving(s => ({ ...s, [key]: true }));
    setRaw(prev => ({ ...prev, [key]: { ...prev[key], value: newVal } }));
    try {
      await adminSvc.updateSystemSetting(key, newVal);
      showToast(newVal ? `Đã bật` : `Đã tắt`, true);
    } catch (e: any) {
      setRaw(prev => ({ ...prev, [key]: { ...prev[key], value: !newVal } }));
      showToast(e.message || 'Lỗi cập nhật', false);
    } finally {
      setSaving(s => ({ ...s, [key]: false }));
    }
  };

  const saveAll = async () => {
    setSavingAll(true);
    try {
      await adminSvc.updateSystemSettings({
        ...appInfo,
        announcementText: banner.announcementText,
        announcementType: banner.announcementType,
      });
      showToast('Đã lưu cấu hình', true);
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
      <div className="flex flex-col items-center justify-center py-20 gap-3">
        <Loader2 className="w-6 h-6 animate-spin" style={{ color: P }} />
        <p className="text-xs text-gray-400">Đang tải cài đặt...</p>
      </div>
    );
  }

  const BANNER_TYPES = [
    { value: 'info',    label: 'Thông tin' },
    { value: 'warning', label: 'Cảnh báo'  },
    { value: 'error',   label: 'Khẩn cấp'  },
    { value: 'success', label: 'Thành công'},
  ];

  const APP_FIELDS: { Icon: any; label: string; key: keyof typeof appInfo; placeholder: string }[] = [
    { Icon: Globe,  label: 'Tên ứng dụng', key: 'appName',        placeholder: 'E-Mapp Dịch vụ công' },
    { Icon: Mail,   label: 'Email hỗ trợ', key: 'contactEmail',   placeholder: 'support@emapp.vn'     },
    { Icon: Phone,  label: 'Hotline',       key: 'contactPhone',   placeholder: '1800 xxxx'            },
    { Icon: MapPin, label: 'Địa chỉ',       key: 'contactAddress', placeholder: 'Số xx, đường...'      },
  ];

  return (
    <div className="space-y-3">
      {toast && <Toast text={toast.text} ok={toast.ok} />}

      {/* ── Tính năng ────────────────────────────────────────────────────── */}
      <SectionCard title="Tính năng" icon={<Settings className="w-4 h-4" />}>
        <ToggleRow
          label="Trợ lý Chatbot AI"
          desc="Bật/tắt chatbot hỗ trợ tự động trên toàn hệ thống"
          checked={getBool('enableChatbot', true)}
          saving={saving.enableChatbot}
          onChange={v => toggle('enableChatbot', v)}
        />
        <ToggleRow
          label="Hàng đợi trực tuyến"
          desc="Người dân đăng ký lấy số thứ tự qua ứng dụng"
          checked={getBool('enableQueue', true)}
          saving={saving.enableQueue}
          onChange={v => toggle('enableQueue', v)}
        />
        <ToggleRow
          label="Đặt lịch bằng giọng nói"
          desc="Voice AI hội thoại để đặt lịch hẹn cán bộ"
          checked={getBool('enableVoice', false)}
          saving={saving.enableVoice}
          onChange={v => toggle('enableVoice', v)}
        />
        <ToggleRow
          label="Push notification"
          desc="Gửi thông báo đẩy tới điện thoại người dùng"
          checked={getBool('enableNotifications', true)}
          saving={saving.enableNotifications}
          onChange={v => toggle('enableNotifications', v)}
        />
      </SectionCard>

      {/* ── Chế độ hệ thống ──────────────────────────────────────────────── */}
      <SectionCard title="Chế độ hệ thống" icon={<Shield className="w-4 h-4" />} accentColor="#705d00">
        <ToggleRow
          label="Chế độ bảo trì"
          desc="Tạm dừng ứng dụng cho người dùng thường để cập nhật"
          checked={getBool('maintenanceMode', false)}
          saving={saving.maintenanceMode}
          onChange={v => toggle('maintenanceMode', v)}
        />
        <ToggleRow
          label="Debug mode"
          desc="In log chi tiết ra console cho đội ngũ kỹ thuật"
          checked={getBool('debugMode', false)}
          saving={saving.debugMode}
          onChange={v => toggle('debugMode', v)}
        />
      </SectionCard>

      {/* ── Banner thông báo ─────────────────────────────────────────────── */}
      <SectionCard title="Banner thông báo" icon={<Megaphone className="w-4 h-4" />} accentColor="#b45309">
        {/* Bật/tắt */}
        <ToggleRow
          label="Hiện banner trang chủ"
          desc="Hiển thị thông báo nổi bật ở đầu trang chủ"
          checked={getBool('announcementActive', false)}
          saving={saving.announcementActive}
          onChange={v => toggle('announcementActive', v)}
        />

        {/* Loại */}
        <div className="mt-3">
          <p className="text-[10px] font-bold uppercase tracking-widest text-gray-400 mb-2">Loại thông báo</p>
          <div className="flex gap-1.5 flex-wrap">
            {BANNER_TYPES.map(t => (
              <button
                key={t.value}
                onClick={() => setBanner(b => ({ ...b, announcementType: t.value }))}
                className={`px-3 py-1 text-xs font-semibold rounded-full transition-all
                  ${banner.announcementType === t.value
                    ? 'text-white'
                    : 'bg-[#fff4f4] text-[#9f364c]/70 hover:bg-[#de9ca4]/20'}`}
                style={banner.announcementType === t.value ? { backgroundColor: P } : undefined}
              >
                {t.label}
              </button>
            ))}
          </div>
        </div>

        {/* Nội dung */}
        <div className="mt-3">
          <p className="text-[10px] font-bold uppercase tracking-widest text-gray-400 mb-2">Nội dung</p>
          <textarea
            value={banner.announcementText}
            onChange={e => setBanner(b => ({ ...b, announcementText: e.target.value }))}
            rows={3}
            placeholder="Nhập nội dung hiển thị trên banner..."
            className="w-full border border-[#de9ca4]/30 rounded-xl px-3 py-2.5 text-sm
              bg-white resize-none focus:outline-none focus:border-[#8f000d] transition-colors"
          />
        </div>
      </SectionCard>

      {/* ── Thông tin ứng dụng ───────────────────────────────────────────── */}
      <SectionCard title="Thông tin ứng dụng" icon={<Server className="w-4 h-4" />} accentColor="#2563eb">
        <div className="space-y-3">
          {APP_FIELDS.map(({ Icon, label, key, placeholder }) => (
            <div key={key} className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-blue-50 flex items-center justify-center flex-shrink-0">
                <Icon className="w-3.5 h-3.5 text-blue-500" />
              </div>
              <div className="flex-1 min-w-0">
                <label className="text-[10px] font-bold uppercase tracking-widest text-gray-400">{label}</label>
                <input
                  type="text"
                  value={appInfo[key]}
                  onChange={e => setAppInfo(a => ({ ...a, [key]: e.target.value }))}
                  placeholder={placeholder}
                  className="block w-full mt-0.5 border-b border-[#de9ca4]/30 focus:border-[#8f000d]
                    bg-transparent outline-none text-sm text-[#4d2128] py-1 transition-colors
                    placeholder:text-gray-300"
                />
              </div>
            </div>
          ))}
        </div>
      </SectionCard>

      {/* ── Save ─────────────────────────────────────────────────────────── */}
      <button
        onClick={saveAll}
        disabled={savingAll}
        className="w-full h-12 rounded-2xl text-sm font-bold text-white flex items-center justify-center
          gap-2 hover:opacity-90 active:scale-[.98] transition-all disabled:opacity-50 shadow-sm"
        style={{ backgroundColor: P }}
      >
        {savingAll ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
        Lưu cấu hình
      </button>

      {/* ── Logout ───────────────────────────────────────────────────────── */}
      <button
        onClick={async () => { await logout(); onNavigate('login'); }}
        className="w-full h-11 rounded-2xl text-sm font-semibold text-red-600 flex items-center justify-center
          gap-2 border border-red-200 hover:bg-red-50 active:scale-[.98] transition-all"
      >
        <LogOut className="w-4 h-4" />
        Đăng xuất
      </button>
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════════════════
   TAB: NHẬT KÝ HÀNH ĐỘNG
═══════════════════════════════════════════════════════════════════════════ */
const ACTION_BADGE: Record<string, string> = {
  CREATE: 'bg-green-100 text-green-700',
  UPDATE: 'bg-blue-100 text-blue-700',
  DELETE: 'bg-red-100 text-red-700',
  REVIEW: 'bg-purple-100 text-purple-700',
  REPLY:  'bg-yellow-100 text-yellow-700',
  LOGIN:  'bg-gray-100 text-gray-600',
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
    } catch { }
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
    <div className="space-y-3">
      {/* Filter bar */}
      <div className="bg-white rounded-2xl px-4 py-3 shadow-sm flex items-center gap-2">
        <div className="flex gap-1.5 flex-wrap flex-1">
          {FILTERS.map(o => (
            <button
              key={o.value}
              onClick={() => { setResource(o.value); setPage(1); }}
              className={`px-2.5 py-1 text-xs font-semibold rounded-full transition-all
                ${resource === o.value
                  ? 'text-white'
                  : 'bg-[#fff4f4] text-[#9f364c]/70 hover:bg-[#de9ca4]/20'}`}
              style={resource === o.value ? { backgroundColor: P } : undefined}
            >
              {o.label}
            </button>
          ))}
        </div>
        <button
          onClick={load}
          className="w-8 h-8 flex items-center justify-center rounded-xl bg-[#fff4f4] text-[#9f364c]/60
            hover:text-[#8f000d] transition-colors flex-shrink-0"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {/* Log list */}
      {loading ? (
        <div className="flex justify-center py-12">
          <Loader2 className="w-5 h-5 animate-spin" style={{ color: P }} />
        </div>
      ) : items.length === 0 ? (
        <div className="flex flex-col items-center py-14 gap-3 bg-white rounded-2xl">
          <Inbox className="w-10 h-10 text-[#de9ca4]/40" />
          <p className="text-sm text-gray-400">Chưa có nhật ký</p>
        </div>
      ) : (
        <div className="space-y-2">
          {items.map(log => {
            const IconComp = RESOURCE_ICON[log.resource] ?? Shield;
            const dateStr  = log.createdAt
              ? new Date(log.createdAt).toLocaleString('vi-VN', {
                  day: '2-digit', month: '2-digit',
                  hour: '2-digit', minute: '2-digit',
                })
              : '–';
            return (
              <div key={log.id}
                className="bg-white rounded-2xl px-4 py-3 flex items-start gap-3 shadow-sm">
                <div className="w-8 h-8 bg-[#fff4f4] rounded-xl flex items-center justify-center flex-shrink-0 mt-0.5">
                  <IconComp className="w-3.5 h-3.5 text-[#9f364c]/60" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-1.5 flex-wrap">
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full
                      ${ACTION_BADGE[log.action] ?? 'bg-gray-100 text-gray-600'}`}>
                      {log.action}
                    </span>
                    <span className="text-xs text-[#4d2128]/70">
                      {log.resource}{log.resourceId ? ` #${String(log.resourceId).slice(0, 6)}` : ''}
                    </span>
                  </div>
                  <p className="text-[10px] text-gray-400 mt-0.5">
                    {log.actorRole === 'admin' ? 'Admin' : (log.actorRole ?? '–')}
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
        <div className="flex justify-center items-center gap-4 py-2">
          <button
            disabled={page === 1}
            onClick={() => setPage(p => p - 1)}
            className="w-9 h-9 flex items-center justify-center bg-white rounded-xl shadow-sm
              border border-[#de9ca4]/20 disabled:opacity-40 hover:border-[#8f000d] transition-colors"
          >
            <ChevronLeft className="w-4 h-4 text-[#4d2128]" />
          </button>
          <span className="text-xs font-medium text-[#4d2128]/70">
            {page} / {totalPages}
          </span>
          <button
            disabled={page >= totalPages}
            onClick={() => setPage(p => p + 1)}
            className="w-9 h-9 flex items-center justify-center bg-white rounded-xl shadow-sm
              border border-[#de9ca4]/20 disabled:opacity-40 hover:border-[#8f000d] transition-colors"
          >
            <ChevronRight className="w-4 h-4 text-[#4d2128]" />
          </button>
        </div>
      )}
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════════════════
   MAIN
═══════════════════════════════════════════════════════════════════════════ */
export function AdminSystemScreen({ onNavigate }: Props) {
  const [tab, setTab] = useState<'settings' | 'auditlog'>('settings');

  const TABS = [
    { key: 'settings', label: 'Cài đặt' },
    { key: 'auditlog', label: 'Nhật ký' },
  ] as const;

  return (
    <div className="min-h-full">
      {/* Header */}
      <div className="px-4 pt-4 pb-2">
        <h2 className="text-lg font-bold text-[#1c0003]">Hệ thống</h2>
        <p className="text-xs text-[#9f364c]/60 mt-0.5">Cấu hình & nhật ký hoạt động</p>
      </div>

      {/* Tab bar */}
      <div className="flex gap-1 px-4 mb-3">
        {TABS.map(t => (
          <button
            key={t.key}
            onClick={() => setTab(t.key)}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition-all
              ${tab === t.key ? 'text-white shadow-sm' : 'text-[#4d2128]/50 hover:text-[#4d2128] hover:bg-[#de9ca4]/10'}`}
            style={tab === t.key ? { backgroundColor: P } : undefined}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="px-4 pb-6">
        {tab === 'settings' && <SettingsTab onNavigate={onNavigate} />}
        {tab === 'auditlog' && <AuditLogTab />}
      </div>
    </div>
  );
}
