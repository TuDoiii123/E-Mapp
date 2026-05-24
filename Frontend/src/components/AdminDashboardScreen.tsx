/**
 * AdminDashboardScreen — Panel quản trị  ✦ Redesigned
 * Aesthetic: Command-Centre editorial — bold numbers, accent-bar rows,
 * custom tab-pills, warm burgundy palette, staggered entrance animations.
 */
import React, { useState, useEffect, useCallback } from 'react';
import {
  ChevronLeft, Users, MapPin, FileText, BarChart3,
  Plus, Pencil, Trash2, Search, RefreshCw, AlertCircle,
  CheckCircle, X, Save, Eye, EyeOff, ClipboardList,
  ThumbsUp, ThumbsDown, MessageSquare, Bot, Zap, ShieldAlert,
  Building2, Timer, CalendarCheck, TrendingUp,
} from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Badge } from './ui/badge';
import * as adminSvc from '../services/adminService';

interface Props { onNavigate: (screen: string, params?: any) => void; hideHeader?: boolean; }

const P    = '#8f000d';
const GOLD = '#fcd400';

/* ── CSS animations injected once ─────────────────────────────────────────── */
const ANIM_CSS = `
@keyframes _fsu{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
.a0{animation:_fsu .26s ease-out both}
.a1{animation:_fsu .26s .05s ease-out both}
.a2{animation:_fsu .26s .10s ease-out both}
.a3{animation:_fsu .26s .15s ease-out both}
.a4{animation:_fsu .26s .20s ease-out both}
.a5{animation:_fsu .26s .25s ease-out both}
`;

/* ── Shared form-field styles ──────────────────────────────────────────────── */
const fLabel = 'text-[11px] font-semibold text-[#4d2128]/60 uppercase tracking-wide';
const fInput = 'mt-1 w-full h-10 border border-[#de9ca4]/30 rounded-xl px-3 text-sm bg-white focus:outline-none focus:border-[#8f000d] transition-colors placeholder:text-gray-300';
const fSelect = `${fInput} appearance-none cursor-pointer`;
const fTextarea = 'mt-1 w-full border border-[#de9ca4]/30 rounded-xl px-3 py-2.5 text-sm bg-white resize-none focus:outline-none focus:border-[#8f000d] transition-colors';

/* ── ConfirmDialog ─────────────────────────────────────────────────────────── */
function ConfirmDialog({ msg, onYes, onNo }: { msg: string; onYes(): void; onNo(): void }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-6">
      <div className="bg-white rounded-2xl p-6 w-full max-w-xs shadow-2xl text-center">
        <div className="w-11 h-11 rounded-2xl bg-red-50 flex items-center justify-center mx-auto mb-3">
          <AlertCircle className="w-5 h-5 text-red-600" />
        </div>
        <p className="text-sm font-medium text-gray-700 mb-5">{msg}</p>
        <div className="flex gap-3">
          <button onClick={onNo}
            className="flex-1 h-10 rounded-xl border border-[#de9ca4]/30 text-sm font-medium
              text-[#4d2128]/70 hover:bg-[#fff4f4] transition-colors">Hủy</button>
          <button onClick={onYes}
            className="flex-1 h-10 rounded-xl text-sm font-semibold text-white transition-opacity hover:opacity-90"
            style={{ backgroundColor: P }}>Xác nhận</button>
        </div>
      </div>
    </div>
  );
}

/* ── Toast ─────────────────────────────────────────────────────────────────── */
function Toast({ text, ok }: { text: string; ok: boolean }) {
  return (
    <div className={`fixed bottom-24 left-1/2 -translate-x-1/2 z-50 px-4 py-2.5 rounded-full
      shadow-lg text-sm font-medium text-white flex items-center gap-2 whitespace-nowrap
      ${ok ? 'bg-green-600' : 'bg-red-700'}`}>
      {ok ? <CheckCircle className="w-4 h-4 flex-shrink-0" /> : <AlertCircle className="w-4 h-4 flex-shrink-0" />}
      {text}
    </div>
  );
}

/* ── Custom Tab Bar ────────────────────────────────────────────────────────── */
type DashTab = 'overview' | 'locations' | 'procedures' | 'chatbot';

const DASH_TABS: { key: DashTab; label: string; Icon: any }[] = [
  { key: 'overview',   label: 'Tổng quan', Icon: BarChart3 },
  { key: 'locations',  label: 'Địa điểm',  Icon: MapPin    },
  { key: 'procedures', label: 'Thủ tục',   Icon: FileText  },
  { key: 'chatbot',    label: 'Chatbot',   Icon: Bot       },
];

function DashTabBar({ active, onChange }: { active: DashTab; onChange(t: DashTab): void }) {
  return (
    <div className="flex gap-1.5 overflow-x-auto no-scrollbar px-4 pt-3 pb-2">
      {DASH_TABS.map(({ key, label, Icon }) => {
        const on = active === key;
        return (
          <button key={key} onClick={() => onChange(key)}
            className={`flex-shrink-0 flex items-center gap-1.5 px-3 py-2 rounded-xl
              text-xs font-semibold transition-all
              ${on ? 'text-white shadow-sm' : 'text-[#4d2128]/55 hover:text-[#4d2128] hover:bg-[#de9ca4]/10'}`}
            style={on ? { backgroundColor: P } : {}}>
            <Icon className="w-3.5 h-3.5" />
            {label}
          </button>
        );
      })}
    </div>
  );
}

/* ── Section Header ────────────────────────────────────────────────────────── */
function SectionLabel({ text }: { text: string }) {
  return (
    <p className="text-[10px] font-bold uppercase tracking-[.16em] text-[#9f364c]/50 mb-1.5 px-4 pt-1">
      {text}
    </p>
  );
}

/* ── Empty State ───────────────────────────────────────────────────────────── */
function EmptyState({ text = 'Không có dữ liệu' }: { text?: string }) {
  return (
    <div className="flex flex-col items-center justify-center py-14 gap-3">
      <div className="w-14 h-14 rounded-2xl bg-[#fff4f4] flex items-center justify-center">
        <FileText className="w-7 h-7 text-[#de9ca4]/50" />
      </div>
      <p className="text-sm font-medium text-gray-400">{text}</p>
    </div>
  );
}

/* ── Search Row ────────────────────────────────────────────────────────────── */
function SearchRow({
  value, onChange, placeholder, onAdd,
}: {
  value: string; onChange(v: string): void; placeholder?: string; onAdd?(): void;
}) {
  return (
    <div className="flex gap-2 px-4">
      <div className="relative flex-1">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#9f364c]/40" />
        <input value={value} onChange={e => onChange(e.target.value)}
          placeholder={placeholder || 'Tìm kiếm...'}
          className="w-full h-10 pl-9 pr-3 bg-white border border-[#de9ca4]/20 rounded-xl text-sm
            text-gray-800 placeholder:text-gray-300 focus:outline-none focus:border-[#8f000d] transition-colors shadow-sm" />
      </div>
      {onAdd && (
        <button onClick={onAdd}
          className="w-10 h-10 rounded-xl flex items-center justify-center text-white flex-shrink-0
            hover:opacity-90 transition-opacity shadow-sm"
          style={{ backgroundColor: P }}>
          <Plus className="w-4 h-4" />
        </button>
      )}
    </div>
  );
}

/* ── Pagination strip ──────────────────────────────────────────────────────── */
function PaginationRow({
  page, total, pageSize, onChange,
}: { page: number; total: number; pageSize: number; onChange(p: number): void }) {
  const pages = Math.ceil(total / pageSize);
  if (pages <= 1) return null;
  return (
    <div className="flex items-center justify-center gap-3 pt-2 pb-1">
      <button disabled={page === 1} onClick={() => onChange(page - 1)}
        className="px-3 h-8 rounded-lg border border-[#de9ca4]/30 text-xs font-medium text-[#4d2128]/60
          disabled:opacity-30 disabled:cursor-not-allowed hover:border-[#8f000d] hover:text-[#8f000d] transition-colors">
        ← Trước
      </button>
      <span className="text-xs text-gray-400 font-medium">{page} / {pages}</span>
      <button disabled={page >= pages} onClick={() => onChange(page + 1)}
        className="px-3 h-8 rounded-lg border border-[#de9ca4]/30 text-xs font-medium text-[#4d2128]/60
          disabled:opacity-30 disabled:cursor-not-allowed hover:border-[#8f000d] hover:text-[#8f000d] transition-colors">
        Sau →
      </button>
    </div>
  );
}

/* ──────────────────────────────────────────────────────────────────────────── */
/*  TAB: TỔNG QUAN                                                             */
/* ──────────────────────────────────────────────────────────────────────────── */
function OverviewTab() {
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  const load = useCallback(() => {
    setLoading(true);
    adminSvc.getStats()
      .then(r => setStats(r.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);
  useEffect(() => { load(); }, [load]);

  const today = new Date().toLocaleDateString('vi-VN', {
    weekday: 'long', day: 'numeric', month: 'long', year: 'numeric',
  });

  const CARDS = [
    { label: 'Người dùng',  v: stats?.totalUsers,          Icon: Users,       ac: '#2563eb', bg: '#dbeafe' },
    { label: 'Địa điểm',   v: stats?.totalLocations,       Icon: Building2,   ac: '#16a34a', bg: '#dcfce7' },
    { label: 'Thủ tục',    v: stats?.totalProcedures,      Icon: FileText,    ac: '#7c3aed', bg: '#ede9fe' },
    { label: 'Hồ sơ',      v: stats?.totalApplications,    Icon: BarChart3,   ac: P,         bg: '#fce7e7' },
    { label: 'Chờ duyệt',  v: stats?.pendingApplications,  Icon: AlertCircle, ac: '#d97706', bg: '#fef3c7' },
    { label: 'Vé hôm nay', v: stats?.ticketsToday,         Icon: Timer,       ac: '#0891b2', bg: '#cffafe' },
  ];

  return (
    <div className="pb-4">
      <style>{ANIM_CSS}</style>

      {/* ── Hero banner ──────────────────────────────────────────────────── */}
      <div className="mx-4 mt-2 relative overflow-hidden rounded-2xl"
        style={{ background: `linear-gradient(135deg, #1c0003 0%, ${P} 60%, #6b0009 100%)` }}>
        {/* crosshatch overlay */}
        <div className="absolute inset-0 opacity-[0.055]"
          style={{
            backgroundImage: 'repeating-linear-gradient(45deg,rgba(255,255,255,.6) 0,rgba(255,255,255,.6) 1px,transparent 0,transparent 50%)',
            backgroundSize: '12px 12px',
          }} />
        <div className="relative px-5 py-5 flex items-start justify-between">
          <div>
            <p className="text-[9px] font-black uppercase tracking-[.22em] text-red-300 mb-1.5">
              E-Mapp · Admin
            </p>
            <h2 className="text-[22px] font-black text-white leading-tight">
              Tổng quan<span style={{ color: GOLD }}>.</span>
            </h2>
            <p className="text-[11px] text-red-300/70 mt-1 capitalize">{today}</p>
          </div>
          <button onClick={load}
            className="w-9 h-9 rounded-xl flex items-center justify-center mt-1 transition-colors hover:bg-white/10"
            style={{ backgroundColor: 'rgba(255,255,255,0.13)' }}>
            <RefreshCw className={`w-4 h-4 text-white ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>

        {/* Sparkline strip */}
        {stats && (
          <div className="flex border-t border-white/10 divide-x divide-white/10">
            {[
              { label: 'Users',  v: stats.totalUsers },
              { label: 'Hồ sơ', v: stats.totalApplications },
              { label: 'Chờ',   v: stats.pendingApplications },
            ].map(s => (
              <div key={s.label} className="flex-1 text-center py-2.5">
                <p className="text-base font-black text-white leading-none">{s.v ?? '—'}</p>
                <p className="text-[9px] text-red-300/70 mt-0.5 uppercase tracking-wide">{s.label}</p>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* ── Stat grid ────────────────────────────────────────────────────── */}
      {loading ? (
        <div className="flex justify-center py-12">
          <RefreshCw className="w-6 h-6 animate-spin" style={{ color: P }} />
        </div>
      ) : (
        <div className="px-4 mt-3 grid grid-cols-2 gap-3">
          {CARDS.map((c, i) => (
            <div key={c.label} className={`bg-white rounded-2xl shadow-sm overflow-hidden a${i}`}>
              <div className="h-[3px]" style={{ backgroundColor: c.ac }} />
              <div className="px-4 py-4">
                <div className="w-9 h-9 rounded-xl flex items-center justify-center mb-3"
                  style={{ backgroundColor: c.bg }}>
                  <c.Icon className="w-[18px] h-[18px]" style={{ color: c.ac }} />
                </div>
                <p className="text-[28px] font-black leading-none text-[#1c0003] mb-1">
                  {c.v ?? '—'}
                </p>
                <p className="text-[11px] font-bold" style={{ color: c.ac }}>{c.label}</p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

/* ──────────────────────────────────────────────────────────────────────────── */
/*  TAB: TÀI KHOẢN                                                             */
/* ──────────────────────────────────────────────────────────────────────────── */
function UserForm({ initial, onSave, onClose }: {
  initial?: any; onSave(data: any): void; onClose(): void;
}) {
  const [form, setForm] = useState({
    cccdNumber: initial?.cccdNumber || '',
    fullName:   initial?.fullName   || '',
    email:      initial?.email      || '',
    phone:      initial?.phone      || '',
    role:       initial?.role       || 'citizen',
    password:   '',
  });
  const [showPwd, setShowPwd] = useState(false);
  const set = (k: string) => (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) =>
    setForm(f => ({ ...f, [k]: e.target.value }));

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 px-4">
      <div className="bg-white rounded-2xl w-full max-w-lg p-5 space-y-3 max-h-[88vh] overflow-y-auto shadow-2xl">
        <div className="flex items-center justify-between mb-1">
          <h3 className="font-bold text-[#1c0003]">{initial ? 'Sửa tài khoản' : 'Thêm tài khoản'}</h3>
          <button onClick={onClose} className="p-1.5 rounded-xl hover:bg-[#fff4f4] transition-colors">
            <X className="w-4 h-4 text-gray-400" />
          </button>
        </div>
        {[
          { label: 'Số CCCD *',  key: 'cccdNumber', type: 'text' },
          { label: 'Họ và tên *', key: 'fullName',  type: 'text' },
          { label: 'Email',       key: 'email',     type: 'email' },
          { label: 'Điện thoại',  key: 'phone',     type: 'tel' },
        ].map(f => (
          <div key={f.key}>
            <label className={fLabel}>{f.label}</label>
            <input type={f.type} value={(form as any)[f.key]} onChange={set(f.key)} className={fInput} />
          </div>
        ))}
        <div>
          <label className={fLabel}>Vai trò</label>
          <select value={form.role} onChange={set('role')} className={fSelect}>
            <option value="citizen">Công dân</option>
            <option value="staff">Nhân viên</option>
            <option value="admin">Quản trị</option>
          </select>
        </div>
        {!initial && (
          <div>
            <label className={fLabel}>Mật khẩu *</label>
            <div className="relative mt-1">
              <input type={showPwd ? 'text' : 'password'} value={form.password}
                onChange={set('password')}
                className="w-full h-10 border border-[#de9ca4]/30 rounded-xl px-3 pr-10 text-sm bg-white
                  focus:outline-none focus:border-[#8f000d] transition-colors" />
              <button onClick={() => setShowPwd(v => !v)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600">
                {showPwd ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
          </div>
        )}
        <div className="flex gap-3 pt-2">
          <button onClick={onClose}
            className="flex-1 h-11 rounded-xl border border-[#de9ca4]/30 text-sm font-medium
              text-[#4d2128]/70 hover:bg-[#fff4f4] transition-colors">Hủy</button>
          <button onClick={() => onSave(form)}
            className="flex-1 h-11 rounded-xl text-sm font-semibold text-white flex items-center
              justify-center gap-1.5 hover:opacity-90 transition-opacity"
            style={{ backgroundColor: P }}>
            <Save className="w-4 h-4" /> Lưu
          </button>
        </div>
      </div>
    </div>
  );
}

function UsersTab({ onToast }: { onToast(msg: string, ok: boolean): void }) {
  const [items,   setItems]   = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [q,       setQ]       = useState('');
  const [page,    setPage]    = useState(1);
  const [total,   setTotal]   = useState(0);
  const [editing, setEditing] = useState<any>(null);
  const [adding,  setAdding]  = useState(false);
  const [confirm, setConfirm] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const r = await adminSvc.getUsers({ q, page: String(page), limit: '15' });
      setItems(r.data || []);
      setTotal(r.pagination?.total || 0);
    } catch { }
    finally { setLoading(false); }
  }, [q, page]);
  useEffect(() => { load(); }, [load]);

  const handleSave = async (data: any) => {
    try {
      if (editing) { await adminSvc.updateUser(editing.id, data); onToast('Đã cập nhật tài khoản', true); }
      else         { await adminSvc.createUser(data);             onToast('Đã tạo tài khoản', true); }
      setEditing(null); setAdding(false); load();
    } catch (e: any) { onToast(e.message, false); }
  };
  const handleDelete = async (id: string) => {
    try { await adminSvc.deleteUser(id); onToast('Đã xóa tài khoản', true); load(); }
    catch (e: any) { onToast(e.message, false); }
    finally { setConfirm(null); }
  };

  const ROLE_CFG: Record<string, { label: string; cls: string; ac: string }> = {
    admin:   { label: 'Quản trị', cls: 'bg-red-100 text-red-700',          ac: P        },
    staff:   { label: 'Nhân viên',cls: 'bg-blue-100 text-blue-700',        ac: '#2563eb' },
    citizen: { label: 'Công dân', cls: 'bg-[#fff4f4] text-[#9f364c]/70',  ac: '#c8a0a8' },
  };

  function initials(name = ''): string {
    const parts = name.trim().split(' ');
    if (parts.length >= 2) return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
    return (name.slice(0, 2)).toUpperCase();
  }

  return (
    <div className="space-y-3 pb-4">
      {(editing || adding) && (
        <UserForm initial={editing} onSave={handleSave}
          onClose={() => { setEditing(null); setAdding(false); }} />
      )}
      {confirm && (
        <ConfirmDialog msg="Xóa tài khoản này?"
          onYes={() => handleDelete(confirm)} onNo={() => setConfirm(null)} />
      )}

      <SearchRow value={q} onChange={v => { setQ(v); setPage(1); }}
        placeholder="Tìm tên, CCCD, email..." onAdd={() => setAdding(true)} />

      <SectionLabel text={`${total} tài khoản`} />

      {loading ? (
        <div className="flex justify-center py-10">
          <RefreshCw className="w-5 h-5 animate-spin" style={{ color: P }} />
        </div>
      ) : items.length === 0 ? <EmptyState /> : (
        <div className="space-y-2 px-4">
          {items.map(u => {
            const cfg = ROLE_CFG[u.role] ?? ROLE_CFG.citizen;
            return (
              <div key={u.id}
                className="relative bg-white rounded-2xl overflow-hidden shadow-sm
                  hover:-translate-y-0.5 hover:shadow-md transition-all">
                <div className="absolute top-0 left-0 w-1 h-full rounded-l-2xl"
                  style={{ backgroundColor: cfg.ac }} />
                <div className="pl-5 pr-3 py-3 flex items-center gap-3">
                  {/* Avatar */}
                  <div className="w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0
                    text-xs font-black"
                    style={{ backgroundColor: cfg.ac + '18', color: cfg.ac }}>
                    {initials(u.fullName)}
                  </div>
                  {/* Info */}
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-semibold text-gray-800 truncate">{u.fullName}</p>
                    <p className="text-[11px] text-gray-400 truncate font-mono">
                      {u.cccdNumber}{u.email ? ` · ${u.email}` : ''}
                    </p>
                  </div>
                  {/* Role + actions */}
                  <div className="flex items-center gap-1 flex-shrink-0">
                    <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full ${cfg.cls}`}>
                      {cfg.label}
                    </span>
                    <button onClick={() => setEditing(u)}
                      className="p-1.5 rounded-lg text-gray-400 hover:text-blue-600 hover:bg-blue-50 transition-colors">
                      <Pencil className="w-3.5 h-3.5" />
                    </button>
                    <button onClick={() => setConfirm(u.id)}
                      className="p-1.5 rounded-lg text-gray-400 hover:text-red-500 hover:bg-red-50 transition-colors">
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
      <PaginationRow page={page} total={total} pageSize={15} onChange={p => setPage(p)} />
    </div>
  );
}

/* ──────────────────────────────────────────────────────────────────────────── */
/*  TAB: ĐỊA ĐIỂM                                                              */
/* ──────────────────────────────────────────────────────────────────────────── */
function LocationForm({ initial, onSave, onClose }: {
  initial?: any; onSave(data: any): void; onClose(): void;
}) {
  const [form, setForm] = useState({
    name:      initial?.name      || '',
    address:   initial?.address   || '',
    ward:      initial?.ward      || '',
    district:  initial?.district  || '',
    province:  initial?.province  || 'Thanh Hóa',
    latitude:  initial?.latitude  || '',
    longitude: initial?.longitude || '',
    level:     initial?.level     || 'district',
  });
  const set = (k: string) => (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) =>
    setForm(f => ({ ...f, [k]: e.target.value }));

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 px-4">
      <div className="bg-white rounded-2xl w-full max-w-lg p-5 space-y-3 max-h-[88vh] overflow-y-auto shadow-2xl">
        <div className="flex items-center justify-between mb-1">
          <h3 className="font-bold text-[#1c0003]">{initial ? 'Sửa địa điểm' : 'Thêm địa điểm'}</h3>
          <button onClick={onClose} className="p-1.5 rounded-xl hover:bg-[#fff4f4] transition-colors">
            <X className="w-4 h-4 text-gray-400" />
          </button>
        </div>
        {[
          { label: 'Tên *',          key: 'name' },
          { label: 'Địa chỉ',        key: 'address' },
          { label: 'Phường/Xã',      key: 'ward' },
          { label: 'Quận/Huyện',     key: 'district' },
          { label: 'Tỉnh/TP',        key: 'province' },
          { label: 'Vĩ độ (lat)',    key: 'latitude' },
          { label: 'Kinh độ (lng)',   key: 'longitude' },
        ].map(f => (
          <div key={f.key}>
            <label className={fLabel}>{f.label}</label>
            <input value={(form as any)[f.key]} onChange={set(f.key)} className={fInput} />
          </div>
        ))}
        <div>
          <label className={fLabel}>Cấp</label>
          <select value={form.level} onChange={set('level')} className={fSelect}>
            <option value="ward">Phường/Xã</option>
            <option value="district">Quận/Huyện</option>
            <option value="province">Tỉnh/TP</option>
          </select>
        </div>
        <div className="flex gap-3 pt-2">
          <button onClick={onClose}
            className="flex-1 h-11 rounded-xl border border-[#de9ca4]/30 text-sm font-medium
              text-[#4d2128]/70 hover:bg-[#fff4f4] transition-colors">Hủy</button>
          <button onClick={() => onSave(form)}
            className="flex-1 h-11 rounded-xl text-sm font-semibold text-white flex items-center
              justify-center gap-1.5 hover:opacity-90 transition-opacity"
            style={{ backgroundColor: P }}>
            <Save className="w-4 h-4" /> Lưu
          </button>
        </div>
      </div>
    </div>
  );
}

function LocationsTab({ onToast }: { onToast(msg: string, ok: boolean): void }) {
  const [items,   setItems]   = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [q,       setQ]       = useState('');
  const [editing, setEditing] = useState<any>(null);
  const [adding,  setAdding]  = useState(false);
  const [confirm, setConfirm] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    try { const r = await adminSvc.getLocations({ q, limit: '30' }); setItems(r.data || []); }
    catch { }
    finally { setLoading(false); }
  }, [q]);
  useEffect(() => { load(); }, [load]);

  const handleSave = async (data: any) => {
    try {
      if (editing) { await adminSvc.updateLocation(editing.id, data); onToast('Đã cập nhật địa điểm', true); }
      else         { await adminSvc.createLocation(data);             onToast('Đã thêm địa điểm', true); }
      setEditing(null); setAdding(false); load();
    } catch (e: any) { onToast(e.message, false); }
  };
  const handleDelete = async (id: string) => {
    try { await adminSvc.deleteLocation(id); onToast('Đã xóa địa điểm', true); load(); }
    catch (e: any) { onToast(e.message, false); }
    finally { setConfirm(null); }
  };

  const LEVEL_CFG: Record<string, { label: string; cls: string; ac: string }> = {
    ward:     { label: 'Phường/Xã',  cls: 'bg-green-100 text-green-700',  ac: '#16a34a' },
    district: { label: 'Quận/Huyện', cls: 'bg-teal-100 text-teal-700',    ac: '#0d9488' },
    province: { label: 'Tỉnh/TP',    cls: 'bg-blue-100 text-blue-700',    ac: '#2563eb' },
  };

  return (
    <div className="space-y-3 pb-4">
      {(editing || adding) && (
        <LocationForm initial={editing} onSave={handleSave}
          onClose={() => { setEditing(null); setAdding(false); }} />
      )}
      {confirm && (
        <ConfirmDialog msg="Xóa địa điểm này?"
          onYes={() => handleDelete(confirm)} onNo={() => setConfirm(null)} />
      )}
      <SearchRow value={q} onChange={setQ}
        placeholder="Tìm tên, địa chỉ..." onAdd={() => setAdding(true)} />
      <SectionLabel text={`${items.length} địa điểm`} />
      {loading ? (
        <div className="flex justify-center py-10">
          <RefreshCw className="w-5 h-5 animate-spin" style={{ color: P }} />
        </div>
      ) : items.length === 0 ? <EmptyState /> : (
        <div className="space-y-2 px-4">
          {items.map(l => {
            const cfg = LEVEL_CFG[l.level] ?? LEVEL_CFG.district;
            return (
              <div key={l.id}
                className="relative bg-white rounded-2xl overflow-hidden shadow-sm
                  hover:-translate-y-0.5 hover:shadow-md transition-all">
                <div className="absolute top-0 left-0 w-1 h-full" style={{ backgroundColor: cfg.ac }} />
                <div className="pl-5 pr-3 py-3 flex items-center gap-3">
                  <div className="w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0"
                    style={{ backgroundColor: cfg.ac + '18' }}>
                    <MapPin className="w-4 h-4" style={{ color: cfg.ac }} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-semibold text-gray-800 truncate">{l.name}</p>
                    <p className="text-[11px] text-gray-400 truncate">{l.address || l.district || '—'}</p>
                  </div>
                  <div className="flex items-center gap-1 flex-shrink-0">
                    <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full ${cfg.cls}`}>
                      {cfg.label}
                    </span>
                    <button onClick={() => setEditing(l)}
                      className="p-1.5 rounded-lg text-gray-400 hover:text-blue-600 hover:bg-blue-50 transition-colors">
                      <Pencil className="w-3.5 h-3.5" />
                    </button>
                    <button onClick={() => setConfirm(l.id)}
                      className="p-1.5 rounded-lg text-gray-400 hover:text-red-500 hover:bg-red-50 transition-colors">
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

/* ──────────────────────────────────────────────────────────────────────────── */
/*  TAB: THỦ TỤC                                                               */
/* ──────────────────────────────────────────────────────────────────────────── */
function ProcedureForm({ initial, onSave, onClose }: {
  initial?: any; onSave(data: any): void; onClose(): void;
}) {
  const [form, setForm] = useState({
    name:           initial?.name           || '',
    description:    initial?.description    || '',
    category:       initial?.category       || '',
    province:       initial?.province       || 'Thanh Hóa',
    processingTime: initial?.processingTime || '',
    fee:            initial?.fee            || '',
    status:         initial?.status         || 'active',
  });
  const set = (k: string) => (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) =>
    setForm(f => ({ ...f, [k]: e.target.value }));

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 px-4">
      <div className="bg-white rounded-2xl w-full max-w-lg p-5 space-y-3 max-h-[88vh] overflow-y-auto shadow-2xl">
        <div className="flex items-center justify-between mb-1">
          <h3 className="font-bold text-[#1c0003]">{initial ? 'Sửa thủ tục' : 'Thêm thủ tục'}</h3>
          <button onClick={onClose} className="p-1.5 rounded-xl hover:bg-[#fff4f4] transition-colors">
            <X className="w-4 h-4 text-gray-400" />
          </button>
        </div>
        <div>
          <label className={fLabel}>Tên thủ tục *</label>
          <input value={form.name} onChange={set('name')} className={fInput} />
        </div>
        <div>
          <label className={fLabel}>Mô tả</label>
          <textarea value={form.description} onChange={set('description')} rows={3} className={fTextarea} />
        </div>
        {[
          { label: 'Lĩnh vực',          key: 'category' },
          { label: 'Tỉnh/TP',           key: 'province' },
          { label: 'Thời gian xử lý',   key: 'processingTime' },
          { label: 'Lệ phí (VNĐ)',      key: 'fee' },
        ].map(f => (
          <div key={f.key}>
            <label className={fLabel}>{f.label}</label>
            <input value={(form as any)[f.key]} onChange={set(f.key)} className={fInput} />
          </div>
        ))}
        <div>
          <label className={fLabel}>Trạng thái</label>
          <select value={form.status} onChange={set('status')} className={fSelect}>
            <option value="active">Đang áp dụng</option>
            <option value="inactive">Tạm dừng</option>
          </select>
        </div>
        <div className="flex gap-3 pt-2">
          <button onClick={onClose}
            className="flex-1 h-11 rounded-xl border border-[#de9ca4]/30 text-sm font-medium
              text-[#4d2128]/70 hover:bg-[#fff4f4] transition-colors">Hủy</button>
          <button onClick={() => onSave(form)}
            className="flex-1 h-11 rounded-xl text-sm font-semibold text-white flex items-center
              justify-center gap-1.5 hover:opacity-90 transition-opacity"
            style={{ backgroundColor: P }}>
            <Save className="w-4 h-4" /> Lưu
          </button>
        </div>
      </div>
    </div>
  );
}

function ProceduresTab({ onToast }: { onToast(msg: string, ok: boolean): void }) {
  const [items,   setItems]   = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [q,       setQ]       = useState('');
  const [editing, setEditing] = useState<any>(null);
  const [adding,  setAdding]  = useState(false);
  const [confirm, setConfirm] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    try { const r = await adminSvc.getProcedures({ q, limit: '20' }); setItems(r.data || []); }
    catch { }
    finally { setLoading(false); }
  }, [q]);
  useEffect(() => { load(); }, [load]);

  const handleSave = async (data: any) => {
    try {
      if (editing) { await adminSvc.updateProcedure(editing.id, data); onToast('Đã cập nhật thủ tục', true); }
      else         { await adminSvc.createProcedure(data);             onToast('Đã thêm thủ tục', true); }
      setEditing(null); setAdding(false); load();
    } catch (e: any) { onToast(e.message, false); }
  };
  const handleDelete = async (id: string) => {
    try { await adminSvc.deleteProcedure(id); onToast('Đã xóa thủ tục', true); load(); }
    catch (e: any) { onToast(e.message, false); }
    finally { setConfirm(null); }
  };

  return (
    <div className="space-y-3 pb-4">
      {(editing || adding) && (
        <ProcedureForm initial={editing} onSave={handleSave}
          onClose={() => { setEditing(null); setAdding(false); }} />
      )}
      {confirm && (
        <ConfirmDialog msg="Xóa thủ tục này?"
          onYes={() => handleDelete(confirm)} onNo={() => setConfirm(null)} />
      )}
      <SearchRow value={q} onChange={setQ} placeholder="Tìm thủ tục..." onAdd={() => setAdding(true)} />
      <SectionLabel text={`${items.length} thủ tục`} />
      {loading ? (
        <div className="flex justify-center py-10">
          <RefreshCw className="w-5 h-5 animate-spin" style={{ color: P }} />
        </div>
      ) : items.length === 0 ? <EmptyState /> : (
        <div className="space-y-2 px-4">
          {items.map(p => (
            <div key={p.id}
              className="relative bg-white rounded-2xl overflow-hidden shadow-sm
                hover:-translate-y-0.5 hover:shadow-md transition-all">
              <div className="absolute top-0 left-0 w-1 h-full"
                style={{ backgroundColor: p.status === 'active' ? '#7c3aed' : '#c8a0a8' }} />
              <div className="pl-5 pr-3 py-3 flex items-center gap-3">
                <div className="w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0"
                  style={{ backgroundColor: p.status === 'active' ? '#ede9fe' : '#f3f4f6' }}>
                  <FileText className="w-4 h-4" style={{ color: p.status === 'active' ? '#7c3aed' : '#9ca3af' }} />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-semibold text-gray-800 truncate">{p.name}</p>
                  <p className="text-[11px] text-gray-400 truncate">
                    {[p.category, p.processingTime, p.fee ? `${Number(p.fee).toLocaleString()}đ` : '']
                      .filter(Boolean).join(' · ')}
                  </p>
                </div>
                <div className="flex items-center gap-1 flex-shrink-0">
                  <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full
                    ${p.status === 'active' ? 'bg-green-100 text-green-700' : 'bg-[#fff4f4] text-[#9f364c]/50'}`}>
                    {p.status === 'active' ? 'Đang áp dụng' : 'Tạm dừng'}
                  </span>
                  <button onClick={() => setEditing(p)}
                    className="p-1.5 rounded-lg text-gray-400 hover:text-blue-600 hover:bg-blue-50 transition-colors">
                    <Pencil className="w-3.5 h-3.5" />
                  </button>
                  <button onClick={() => setConfirm(p.id)}
                    className="p-1.5 rounded-lg text-gray-400 hover:text-red-500 hover:bg-red-50 transition-colors">
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

/* ──────────────────────────────────────────────────────────────────────────── */
/*  TAB: HỒ SƠ                                                                 */
/* ──────────────────────────────────────────────────────────────────────────── */
const APP_FILTER_OPTS = [
  { value: '',           label: 'Tất cả'     },
  { value: 'submitted',  label: 'Đã nộp'     },
  { value: 'in_review',  label: 'Đang xét'   },
  { value: 'more_info',  label: 'Cần bổ sung'},
  { value: 'approved',   label: 'Đã duyệt'   },
  { value: 'rejected',   label: 'Từ chối'    },
];
const APP_S_CFG: Record<string, { label: string; cls: string; ac: string }> = {
  submitted: { label: 'Đã nộp',      cls: 'bg-blue-100 text-blue-700',   ac: '#3b82f6' },
  in_review: { label: 'Đang xét',    cls: 'bg-amber-100 text-amber-700', ac: P         },
  more_info: { label: 'Bổ sung',     cls: 'bg-orange-100 text-orange-700', ac: '#f97316'},
  approved:  { label: 'Đã duyệt',   cls: 'bg-green-100 text-green-700', ac: '#16a34a' },
  rejected:  { label: 'Từ chối',    cls: 'bg-red-100 text-red-700',     ac: '#dc2626' },
};

function ReviewModal({ app, onClose, onDone }: {
  app: any; onClose(): void; onDone(action: string, note: string): void;
}) {
  const [action, setAction] = useState('');
  const [note,   setNote]   = useState('');
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 px-4">
      <div className="bg-white rounded-2xl w-full max-w-lg p-5 space-y-4 max-h-[88vh] overflow-y-auto shadow-2xl">
        <div className="flex items-center justify-between">
          <h3 className="font-bold text-[#1c0003]">Xét duyệt hồ sơ</h3>
          <button onClick={onClose} className="p-1.5 rounded-xl hover:bg-[#fff4f4] transition-colors">
            <X className="w-4 h-4 text-gray-400" />
          </button>
        </div>
        <div className="bg-[#fff4f4] rounded-xl p-3.5 space-y-1 border-l-4" style={{ borderColor: P }}>
          <p className="text-sm font-semibold text-gray-800 leading-snug line-clamp-2">
            {app.procedureName || app.procedureId || 'Thủ tục hành chính'}
          </p>
          <p className="text-xs text-gray-500">Người nộp: <span className="font-medium text-gray-700">{app.applicantName || app.applicantId}</span></p>
          <p className="text-[10px] text-gray-400 font-mono">Mã: {app.id}</p>
        </div>
        <div className="grid grid-cols-3 gap-2">
          {[
            { val: 'approve',            label: 'Duyệt',    Icon: ThumbsUp,      cls: 'border-green-400 text-green-700 bg-green-50' },
            { val: 'reject',             label: 'Từ chối',  Icon: ThumbsDown,    cls: 'border-red-400 text-red-700 bg-red-50' },
            { val: 'request_more_info',  label: 'Yêu cầu\nbổ sung', Icon: MessageSquare, cls: 'border-amber-400 text-amber-700 bg-amber-50' },
          ].map(o => (
            <button key={o.val}
              className={`border-2 rounded-xl p-3 flex flex-col items-center gap-1.5 text-xs font-medium
                transition-all leading-tight text-center
                ${action === o.val ? o.cls + ' ring-2 ring-offset-1 ring-current' : 'border-[#de9ca4]/30 text-[#4d2128]/70 hover:border-[#de9ca4]'}`}
              onClick={() => setAction(o.val)}>
              <o.Icon className="w-5 h-5" />
              {o.label}
            </button>
          ))}
        </div>
        <div>
          <label className={fLabel}>Ghi chú</label>
          <textarea value={note} onChange={e => setNote(e.target.value)}
            rows={3} placeholder="Nhập ghi chú (nếu có)..." className={fTextarea} />
        </div>
        <div className="flex gap-3">
          <button onClick={onClose}
            className="flex-1 h-11 rounded-xl border border-[#de9ca4]/30 text-sm font-medium
              text-[#4d2128]/70 hover:bg-[#fff4f4] transition-colors">Hủy</button>
          <button disabled={!action} onClick={() => action && onDone(action, note)}
            className="flex-1 h-11 rounded-xl text-sm font-semibold text-white transition-all
              disabled:opacity-40 disabled:cursor-not-allowed hover:opacity-90"
            style={{ backgroundColor: action ? P : '#ccc' }}>
            Xác nhận
          </button>
        </div>
      </div>
    </div>
  );
}

function ApplicationsTab({ onToast }: { onToast(msg: string, ok: boolean): void }) {
  const [items,     setItems]     = useState<any[]>([]);
  const [loading,   setLoading]   = useState(true);
  const [q,         setQ]         = useState('');
  const [status,    setStatus]    = useState('');
  const [page,      setPage]      = useState(1);
  const [total,     setTotal]     = useState(0);
  const [reviewing, setReviewing] = useState<any>(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const params: Record<string, string> = { page: String(page), limit: '15' };
      if (q)      params.q      = q;
      if (status) params.status = status;
      const r = await adminSvc.getApplications(params);
      setItems(r.data || []);
      setTotal(r.pagination?.total || r.total || 0);
    } catch { }
    finally { setLoading(false); }
  }, [q, status, page]);
  useEffect(() => { load(); }, [load]);

  const handleReview = async (action: string, note: string) => {
    if (!reviewing) return;
    try {
      await adminSvc.reviewApplication(reviewing.id, action, note);
      onToast('Đã cập nhật trạng thái hồ sơ', true);
      setReviewing(null); load();
    } catch (e: any) { onToast(e.message, false); }
  };

  return (
    <div className="space-y-3 pb-4">
      {reviewing && (
        <ReviewModal app={reviewing} onClose={() => setReviewing(null)} onDone={handleReview} />
      )}
      <SearchRow value={q} onChange={v => { setQ(v); setPage(1); }} placeholder="Tìm mã, tên, CCCD..." />

      {/* Filter chips */}
      <div className="flex gap-1.5 overflow-x-auto no-scrollbar px-4 pb-0.5">
        {APP_FILTER_OPTS.map(o => {
          const on = status === o.value;
          return (
            <button key={o.value} onClick={() => { setStatus(o.value); setPage(1); }}
              className={`flex-shrink-0 px-3 py-1.5 rounded-full text-xs font-semibold transition-all border
                ${on ? 'text-white border-transparent' : 'bg-white text-[#4d2128]/70 border-[#de9ca4]/30 hover:border-[#de9ca4]'}`}
              style={on ? { backgroundColor: P } : {}}>
              {o.label}
            </button>
          );
        })}
      </div>

      <SectionLabel text={`${total} hồ sơ`} />
      {loading ? (
        <div className="flex justify-center py-10">
          <RefreshCw className="w-5 h-5 animate-spin" style={{ color: P }} />
        </div>
      ) : items.length === 0 ? <EmptyState text="Không có hồ sơ" /> : (
        <div className="space-y-2 px-4">
          {items.map(app => {
            const cfg = APP_S_CFG[app.currentStatus] ?? { label: app.currentStatus, cls: 'bg-gray-100 text-gray-600', ac: '#9ca3af' };
            const dateStr = app.createdAt
              ? new Date(app.createdAt).toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit', year: '2-digit' })
              : '—';
            return (
              <div key={app.id}
                className="relative bg-white rounded-2xl overflow-hidden shadow-sm
                  hover:-translate-y-0.5 hover:shadow-md transition-all">
                <div className="absolute top-0 left-0 w-1 h-full" style={{ backgroundColor: cfg.ac }} />
                <div className="pl-5 pr-3 py-3 flex items-start gap-3">
                  <div className="w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0 mt-0.5"
                    style={{ backgroundColor: cfg.ac + '18' }}>
                    <ClipboardList className="w-4 h-4" style={{ color: cfg.ac }} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-semibold text-gray-800 truncate">
                      {app.procedureName || app.procedureId || 'Thủ tục hành chính'}
                    </p>
                    <p className="text-[11px] text-gray-400 truncate">
                      {app.applicantName || app.applicantId} · {dateStr}
                    </p>
                  </div>
                  <div className="flex items-center gap-1.5 flex-shrink-0">
                    <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full ${cfg.cls}`}>
                      {cfg.label}
                    </span>
                    <button onClick={() => setReviewing(app)}
                      className="p-1.5 rounded-lg text-gray-400 hover:text-[#8f000d] hover:bg-[#fff4f4] transition-colors"
                      title="Xét duyệt">
                      <ClipboardList className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
      <PaginationRow page={page} total={total} pageSize={15} onChange={p => setPage(p)} />
    </div>
  );
}

/* ──────────────────────────────────────────────────────────────────────────── */
/*  TAB: LỊCH HẸN                                                              */
/* ──────────────────────────────────────────────────────────────────────────── */
const APT_CFG: Record<string, { label: string; cls: string; ac: string }> = {
  pending:   { label: 'Chờ đến', cls: 'bg-amber-100 text-amber-700', ac: '#d97706' },
  completed: { label: 'Đã đến',  cls: 'bg-green-100 text-green-700', ac: '#16a34a' },
  cancelled: { label: 'Đã hủy',  cls: 'bg-[#fff4f4] text-[#9f364c]/60', ac: '#c8a0a8' },
};

function AppointmentsTab() {
  const [items,   setItems]   = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter,  setFilter]  = useState('');
  const [q,       setQ]       = useState('');

  useEffect(() => {
    adminSvc.getAppointments()
      .then(r => setItems(r.data?.appointments || r.appointments || r.data || []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const displayed = items.filter(a => {
    if (filter && a.status !== filter) return false;
    if (q) {
      const kw = q.toLowerCase();
      return (a.fullName || '').toLowerCase().includes(kw)
          || (a.phone || '').includes(kw)
          || (a.id || '').toLowerCase().includes(kw);
    }
    return true;
  });

  return (
    <div className="space-y-3 pb-4">
      <SearchRow value={q} onChange={setQ} placeholder="Tìm tên, SĐT, mã lịch hẹn..." />
      <div className="flex gap-1.5 overflow-x-auto no-scrollbar px-4 pb-0.5">
        {[
          { value: '',          label: 'Tất cả' },
          { value: 'pending',   label: 'Chờ đến' },
          { value: 'completed', label: 'Đã đến' },
          { value: 'cancelled', label: 'Đã hủy' },
        ].map(o => {
          const on = filter === o.value;
          return (
            <button key={o.value} onClick={() => setFilter(o.value)}
              className={`flex-shrink-0 px-3 py-1.5 rounded-full text-xs font-semibold transition-all border
                ${on ? 'text-white border-transparent' : 'bg-white text-[#4d2128]/70 border-[#de9ca4]/30 hover:border-[#de9ca4]'}`}
              style={on ? { backgroundColor: P } : {}}>
              {o.label}
            </button>
          );
        })}
      </div>
      <SectionLabel text={`${displayed.length} lịch hẹn`} />
      {loading ? (
        <div className="flex justify-center py-10">
          <RefreshCw className="w-5 h-5 animate-spin" style={{ color: P }} />
        </div>
      ) : displayed.length === 0 ? <EmptyState text="Không có lịch hẹn" /> : (
        <div className="space-y-2 px-4">
          {displayed.map(a => {
            const cfg = APT_CFG[a.status] ?? APT_CFG.pending;
            return (
              <div key={a.id}
                className="relative bg-white rounded-2xl overflow-hidden shadow-sm
                  hover:-translate-y-0.5 hover:shadow-md transition-all">
                <div className="absolute top-0 left-0 w-1 h-full" style={{ backgroundColor: cfg.ac }} />
                <div className="pl-5 pr-3 py-3 flex items-center gap-3">
                  <div className="w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0"
                    style={{ backgroundColor: cfg.ac + '18' }}>
                    <CalendarCheck className="w-4 h-4" style={{ color: cfg.ac }} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-semibold text-gray-800 truncate">{a.fullName || 'Không rõ'}</p>
                    <p className="text-[11px] text-gray-400 truncate">
                      {a.phone} · {a.date} {a.time}
                    </p>
                  </div>
                  <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full flex-shrink-0 ${cfg.cls}`}>
                    {cfg.label}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

/* ──────────────────────────────────────────────────────────────────────────── */
/*  TAB: CHATBOT CONFIG                                                         */
/* ──────────────────────────────────────────────────────────────────────────── */
function PersonaForm({ initial, onSave, onClose }: {
  initial?: any; onSave(data: any): void; onClose(): void;
}) {
  const [form, setForm] = useState({
    name:        initial?.name        || '',
    description: initial?.description || '',
    tone:        initial?.tone        || 'formal',
    greeting:    initial?.greeting    || '',
    farewell:    initial?.farewell    || '',
    language:    initial?.language    || 'vi',
  });
  const set = (k: string) => (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) =>
    setForm(f => ({ ...f, [k]: e.target.value }));
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 px-4">
      <div className="bg-white rounded-2xl w-full max-w-lg p-5 space-y-3 max-h-[88vh] overflow-y-auto shadow-2xl">
        <div className="flex items-center justify-between mb-1">
          <h3 className="font-bold text-[#1c0003]">{initial ? 'Sửa Persona' : 'Thêm Persona'}</h3>
          <button onClick={onClose} className="p-1.5 rounded-xl hover:bg-[#fff4f4] transition-colors">
            <X className="w-4 h-4 text-gray-400" />
          </button>
        </div>
        <div><label className={fLabel}>Tên *</label><input value={form.name} onChange={set('name')} className={fInput} placeholder="VD: Trợ lý Dịch vụ Công" /></div>
        <div><label className={fLabel}>Mô tả</label><input value={form.description} onChange={set('description')} className={fInput} /></div>
        <div>
          <label className={fLabel}>Phong cách</label>
          <select value={form.tone} onChange={set('tone')} className={fSelect}>
            <option value="formal">Trang trọng</option>
            <option value="friendly">Thân thiện</option>
            <option value="neutral">Trung lập</option>
          </select>
        </div>
        <div><label className={fLabel}>Lời chào mở đầu</label><textarea value={form.greeting} onChange={set('greeting')} rows={3} className={fTextarea} /></div>
        <div><label className={fLabel}>Lời tạm biệt</label><input value={form.farewell} onChange={set('farewell')} className={fInput} /></div>
        <div className="flex gap-3 pt-2">
          <button onClick={onClose} className="flex-1 h-11 rounded-xl border border-[#de9ca4]/30 text-sm font-medium text-[#4d2128]/70 hover:bg-[#fff4f4] transition-colors">Hủy</button>
          <button onClick={() => onSave(form)} className="flex-1 h-11 rounded-xl text-sm font-semibold text-white flex items-center justify-center gap-1.5 hover:opacity-90" style={{ backgroundColor: P }}>
            <Save className="w-4 h-4" /> Lưu
          </button>
        </div>
      </div>
    </div>
  );
}

function PersonasSection({ onToast }: { onToast(msg: string, ok: boolean): void }) {
  const [items,   setItems]   = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState<any>(null);
  const [adding,  setAdding]  = useState(false);
  const [confirm, setConfirm] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    try { const r = await adminSvc.getChatbotPersonas(); setItems(r.data || []); }
    catch { } finally { setLoading(false); }
  }, []);
  useEffect(() => { load(); }, [load]);

  const handleSave = async (data: any) => {
    try {
      if (editing) { await adminSvc.updateChatbotPersona(editing.id, data); onToast('Đã cập nhật persona', true); }
      else         { await adminSvc.createChatbotPersona(data);             onToast('Đã thêm persona', true); }
      setEditing(null); setAdding(false); load();
    } catch (e: any) { onToast(e.message, false); }
  };
  const handleActivate = async (id: string) => {
    try { await adminSvc.activateChatbotPersona(id); onToast('Đã kích hoạt', true); load(); }
    catch (e: any) { onToast(e.message, false); }
  };
  const handleDelete = async (id: string) => {
    try { await adminSvc.deleteChatbotPersona(id); onToast('Đã xóa', true); load(); }
    catch (e: any) { onToast(e.message, false); }
    finally { setConfirm(null); }
  };
  const handleSeed = async () => {
    try { await adminSvc.seedChatbotDefaults(); onToast('Đã seed mặc định', true); load(); }
    catch (e: any) { onToast(e.message, false); }
  };

  return (
    <div className="space-y-2">
      {(editing || adding) && (<PersonaForm initial={editing} onSave={handleSave} onClose={() => { setEditing(null); setAdding(false); }} />)}
      {confirm && (<ConfirmDialog msg="Xóa persona?" onYes={() => handleDelete(confirm)} onNo={() => setConfirm(null)} />)}
      <div className="flex gap-2">
        <button onClick={() => setAdding(true)}
          className="flex-1 h-9 rounded-xl text-xs font-semibold text-white flex items-center justify-center gap-1.5 hover:opacity-90"
          style={{ backgroundColor: P }}>
          <Plus className="w-3.5 h-3.5" /> Thêm Persona
        </button>
        <button onClick={handleSeed}
          className="h-9 px-3 rounded-xl text-xs font-medium border border-[#de9ca4]/30 text-[#4d2128]/70
            hover:bg-[#fff4f4] transition-colors flex items-center gap-1">
          <Zap className="w-3.5 h-3.5" /> Seed
        </button>
      </div>
      {loading ? (
        <div className="flex justify-center py-6"><RefreshCw className="w-4 h-4 animate-spin" style={{ color: P }} /></div>
      ) : items.length === 0 ? <EmptyState text="Chưa có persona" /> : (
        <div className="space-y-2">
          {items.map(p => (
            <div key={p.id}
              className="relative bg-white rounded-2xl overflow-hidden shadow-sm">
              <div className="absolute top-0 left-0 w-1 h-full"
                style={{ backgroundColor: p.is_active ? '#16a34a' : '#e5e7eb' }} />
              <div className="pl-5 pr-3 py-3 flex items-center gap-3">
                <div className="w-8 h-8 rounded-xl flex items-center justify-center flex-shrink-0"
                  style={{ backgroundColor: p.is_active ? '#dcfce7' : '#f3f4f6' }}>
                  <Bot className="w-4 h-4" style={{ color: p.is_active ? '#16a34a' : '#9ca3af' }} />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <p className="text-sm font-semibold text-gray-800 truncate">{p.name}</p>
                    {p.is_active && <span className="text-[9px] font-bold px-1.5 py-0.5 rounded-full bg-green-100 text-green-700">ACTIVE</span>}
                  </div>
                  <p className="text-[11px] text-gray-400 truncate">{p.description || p.tone}</p>
                </div>
                <div className="flex items-center gap-1 flex-shrink-0">
                  {!p.is_active && (
                    <button onClick={() => handleActivate(p.id)}
                      className="text-[10px] font-semibold text-green-600 px-2 py-1 rounded-lg hover:bg-green-50 transition-colors">
                      Kích hoạt
                    </button>
                  )}
                  <button onClick={() => setEditing(p)} className="p-1.5 rounded-lg text-gray-400 hover:text-blue-600 hover:bg-blue-50 transition-colors"><Pencil className="w-3.5 h-3.5" /></button>
                  <button onClick={() => setConfirm(p.id)} className="p-1.5 rounded-lg text-gray-400 hover:text-red-500 hover:bg-red-50 transition-colors"><Trash2 className="w-3.5 h-3.5" /></button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

/* ── Prompts ──────────────────────────────────────────────────────────────── */
const PROMPT_TYPES = [
  { value: '',               label: 'Tất cả'  },
  { value: 'system',         label: 'System'  },
  { value: 'nlu',            label: 'NLU'     },
  { value: 'rag_answer',     label: 'RAG'     },
  { value: 'dialog_confirm', label: 'Xác nhận'},
  { value: 'error_fallback', label: 'Fallback'},
];

function PromptForm({ initial, onSave, onClose }: {
  initial?: any; onSave(data: any): void; onClose(): void;
}) {
  const [form, setForm] = useState({
    type:        initial?.type        || 'system',
    name:        initial?.name        || '',
    content:     initial?.content     || '',
    description: initial?.description || '',
  });
  const set = (k: string) => (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) =>
    setForm(f => ({ ...f, [k]: e.target.value }));
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 px-4">
      <div className="bg-white rounded-2xl w-full max-w-lg p-5 space-y-3 max-h-[90vh] overflow-y-auto shadow-2xl">
        <div className="flex items-center justify-between mb-1">
          <h3 className="font-bold text-[#1c0003]">{initial ? 'Sửa Prompt' : 'Thêm Prompt'}</h3>
          <button onClick={onClose} className="p-1.5 rounded-xl hover:bg-[#fff4f4] transition-colors"><X className="w-4 h-4 text-gray-400" /></button>
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className={fLabel}>Loại *</label>
            <select value={form.type} onChange={set('type')} className={fSelect}>
              {PROMPT_TYPES.slice(1).map(t => <option key={t.value} value={t.value}>{t.label}</option>)}
            </select>
          </div>
          <div><label className={fLabel}>Tên *</label><input value={form.name} onChange={set('name')} className={fInput} /></div>
        </div>
        <div>
          <label className={fLabel}>Nội dung prompt *</label>
          <textarea value={form.content} onChange={set('content')} rows={10}
            className="mt-1 w-full border border-[#de9ca4]/30 rounded-xl px-3 py-2.5 text-xs font-mono bg-white resize-y focus:outline-none focus:border-[#8f000d] transition-colors" />
        </div>
        <div><label className={fLabel}>Mô tả</label><input value={form.description} onChange={set('description')} className={fInput} /></div>
        <div className="flex gap-3 pt-2">
          <button onClick={onClose} className="flex-1 h-11 rounded-xl border border-[#de9ca4]/30 text-sm font-medium text-[#4d2128]/70 hover:bg-[#fff4f4] transition-colors">Hủy</button>
          <button onClick={() => onSave(form)} className="flex-1 h-11 rounded-xl text-sm font-semibold text-white flex items-center justify-center gap-1.5 hover:opacity-90" style={{ backgroundColor: P }}>
            <Save className="w-4 h-4" /> Lưu
          </button>
        </div>
      </div>
    </div>
  );
}

const PTYPE_COLOR: Record<string, string> = {
  system:         'bg-purple-100 text-purple-700',
  nlu:            'bg-blue-100 text-blue-700',
  rag_answer:     'bg-indigo-100 text-indigo-700',
  dialog_confirm: 'bg-amber-100 text-amber-700',
  error_fallback: 'bg-red-100 text-red-700',
};

function PromptsSection({ onToast }: { onToast(msg: string, ok: boolean): void }) {
  const [items,    setItems]    = useState<any[]>([]);
  const [loading,  setLoading]  = useState(true);
  const [typeF,    setTypeF]    = useState('');
  const [editing,  setEditing]  = useState<any>(null);
  const [adding,   setAdding]   = useState(false);
  const [confirm,  setConfirm]  = useState<string | null>(null);
  const [expanded, setExpanded] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    try { const r = await adminSvc.getChatbotPrompts(typeF || undefined); setItems(r.data || []); }
    catch { } finally { setLoading(false); }
  }, [typeF]);
  useEffect(() => { load(); }, [load]);

  const handleSave = async (data: any) => {
    try {
      if (editing) { await adminSvc.updateChatbotPrompt(editing.id, data); onToast('Đã cập nhật prompt', true); }
      else         { await adminSvc.createChatbotPrompt(data);             onToast('Đã thêm prompt', true); }
      setEditing(null); setAdding(false); load();
    } catch (e: any) { onToast(e.message, false); }
  };
  const handleDelete = async (id: string) => {
    try { await adminSvc.deleteChatbotPrompt(id); onToast('Đã xóa prompt', true); load(); }
    catch (e: any) { onToast(e.message, false); }
    finally { setConfirm(null); }
  };

  return (
    <div className="space-y-2">
      {(editing || adding) && (<PromptForm initial={editing} onSave={handleSave} onClose={() => { setEditing(null); setAdding(false); }} />)}
      {confirm && (<ConfirmDialog msg="Xóa prompt này?" onYes={() => handleDelete(confirm)} onNo={() => setConfirm(null)} />)}
      <div className="flex items-center gap-2">
        <div className="flex gap-1 overflow-x-auto flex-1 pb-0.5 no-scrollbar">
          {PROMPT_TYPES.map(t => (
            <button key={t.value} onClick={() => setTypeF(t.value)}
              className={`flex-shrink-0 px-2.5 py-1 rounded-full text-[10px] font-semibold transition-all
                ${typeF === t.value ? 'text-white' : 'bg-white text-[#4d2128]/60 border border-[#de9ca4]/30 hover:border-[#de9ca4]'}`}
              style={typeF === t.value ? { backgroundColor: P } : {}}>
              {t.label}
            </button>
          ))}
        </div>
        <button onClick={() => setAdding(true)}
          className="w-8 h-8 rounded-xl flex items-center justify-center text-white flex-shrink-0 hover:opacity-90"
          style={{ backgroundColor: P }}>
          <Plus className="w-3.5 h-3.5" />
        </button>
      </div>
      {loading ? <div className="flex justify-center py-6"><RefreshCw className="w-4 h-4 animate-spin" style={{ color: P }} /></div>
        : items.length === 0 ? <EmptyState text="Chưa có prompt" /> : (
        <div className="space-y-2">
          {items.map(p => (
            <div key={p.id} className="bg-white rounded-2xl shadow-sm overflow-hidden">
              <div className="flex items-center gap-3 px-4 py-3">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-1.5 flex-wrap">
                    <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded-full ${PTYPE_COLOR[p.type] || 'bg-gray-100 text-gray-600'}`}>{p.type}</span>
                    <p className="text-sm font-semibold text-gray-800 truncate">{p.name}</p>
                  </div>
                  {p.description && <p className="text-[10px] text-gray-400 mt-0.5 truncate">{p.description}</p>}
                </div>
                <div className="flex items-center gap-1 flex-shrink-0">
                  <button onClick={() => setExpanded(expanded === p.id ? null : p.id)} className="p-1.5 rounded-lg text-gray-400 hover:text-gray-600 hover:bg-gray-50 transition-colors"><Eye className="w-3.5 h-3.5" /></button>
                  <button onClick={() => setEditing(p)} className="p-1.5 rounded-lg text-gray-400 hover:text-blue-600 hover:bg-blue-50 transition-colors"><Pencil className="w-3.5 h-3.5" /></button>
                  <button onClick={() => setConfirm(p.id)} className="p-1.5 rounded-lg text-gray-400 hover:text-red-500 hover:bg-red-50 transition-colors"><Trash2 className="w-3.5 h-3.5" /></button>
                </div>
              </div>
              {expanded === p.id && (
                <div className="px-4 pb-3 border-t border-[#de9ca4]/10">
                  <pre className="text-[10px] text-gray-600 bg-[#fff4f4]/60 rounded-xl p-3 mt-2
                    whitespace-pre-wrap font-mono overflow-x-auto max-h-48">{p.content}</pre>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

/* ── Rules ──────────────────────────────────────────────────────────────────── */
const RULE_CATS = [
  { value: '',             label: 'Tất cả'  },
  { value: 'behavior',    label: 'Hành vi'  },
  { value: 'restriction', label: 'Giới hạn' },
  { value: 'format',      label: 'Định dạng'},
  { value: 'greeting',    label: 'Lời chào' },
  { value: 'escalation',  label: 'Chuyển'   },
];

function RuleForm({ initial, onSave, onClose }: {
  initial?: any; onSave(data: any): void; onClose(): void;
}) {
  const [form, setForm] = useState({
    category:  initial?.category  || 'behavior',
    rule_text: initial?.rule_text || '',
    priority:  initial?.priority  || 0,
  });
  const set = (k: string) => (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) =>
    setForm(f => ({ ...f, [k]: k === 'priority' ? Number(e.target.value) : e.target.value }));
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 px-4">
      <div className="bg-white rounded-2xl w-full max-w-lg p-5 space-y-3 max-h-[88vh] overflow-y-auto shadow-2xl">
        <div className="flex items-center justify-between mb-1">
          <h3 className="font-bold text-[#1c0003]">{initial ? 'Sửa Rule' : 'Thêm Rule'}</h3>
          <button onClick={onClose} className="p-1.5 rounded-xl hover:bg-[#fff4f4] transition-colors"><X className="w-4 h-4 text-gray-400" /></button>
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className={fLabel}>Loại</label>
            <select value={form.category} onChange={set('category')} className={fSelect}>
              {RULE_CATS.slice(1).map(c => <option key={c.value} value={c.value}>{c.label}</option>)}
            </select>
          </div>
          <div><label className={fLabel}>Độ ưu tiên</label><input type="number" value={form.priority} onChange={set('priority')} className={fInput} /></div>
        </div>
        <div>
          <label className={fLabel}>Nội dung rule *</label>
          <textarea value={form.rule_text} onChange={set('rule_text')} rows={4} className={fTextarea}
            placeholder="VD: Chỉ trả lời các câu hỏi liên quan đến dịch vụ công." />
        </div>
        <div className="flex gap-3 pt-2">
          <button onClick={onClose} className="flex-1 h-11 rounded-xl border border-[#de9ca4]/30 text-sm font-medium text-[#4d2128]/70 hover:bg-[#fff4f4] transition-colors">Hủy</button>
          <button onClick={() => onSave(form)} className="flex-1 h-11 rounded-xl text-sm font-semibold text-white flex items-center justify-center gap-1.5 hover:opacity-90" style={{ backgroundColor: P }}>
            <Save className="w-4 h-4" /> Lưu
          </button>
        </div>
      </div>
    </div>
  );
}

const RCAT_COLOR: Record<string, string> = {
  behavior:    'bg-blue-100 text-blue-700',
  restriction: 'bg-red-100 text-red-700',
  format:      'bg-amber-100 text-amber-700',
  greeting:    'bg-green-100 text-green-700',
  escalation:  'bg-orange-100 text-orange-700',
};

function RulesSection({ onToast }: { onToast(msg: string, ok: boolean): void }) {
  const [items,   setItems]   = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [catF,    setCatF]    = useState('');
  const [editing, setEditing] = useState<any>(null);
  const [adding,  setAdding]  = useState(false);
  const [confirm, setConfirm] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    try { const r = await adminSvc.getChatbotRules(catF || undefined); setItems(r.data || []); }
    catch { } finally { setLoading(false); }
  }, [catF]);
  useEffect(() => { load(); }, [load]);

  const handleSave = async (data: any) => {
    try {
      if (editing) { await adminSvc.updateChatbotRule(editing.id, data); onToast('Đã cập nhật rule', true); }
      else         { await adminSvc.createChatbotRule(data);             onToast('Đã thêm rule', true); }
      setEditing(null); setAdding(false); load();
    } catch (e: any) { onToast(e.message, false); }
  };
  const handleDelete = async (id: string) => {
    try { await adminSvc.deleteChatbotRule(id); onToast('Đã xóa rule', true); load(); }
    catch (e: any) { onToast(e.message, false); }
    finally { setConfirm(null); }
  };
  const handleToggle = async (rule: any) => {
    try { await adminSvc.updateChatbotRule(rule.id, { is_active: !rule.is_active }); onToast(rule.is_active ? 'Đã tắt rule' : 'Đã bật rule', true); load(); }
    catch (e: any) { onToast(e.message, false); }
  };

  return (
    <div className="space-y-2">
      {(editing || adding) && (<RuleForm initial={editing} onSave={handleSave} onClose={() => { setEditing(null); setAdding(false); }} />)}
      {confirm && (<ConfirmDialog msg="Xóa rule này?" onYes={() => handleDelete(confirm)} onNo={() => setConfirm(null)} />)}
      <div className="flex items-center gap-2">
        <div className="flex gap-1 overflow-x-auto flex-1 pb-0.5 no-scrollbar">
          {RULE_CATS.map(c => (
            <button key={c.value} onClick={() => setCatF(c.value)}
              className={`flex-shrink-0 px-2.5 py-1 rounded-full text-[10px] font-semibold transition-all
                ${catF === c.value ? 'text-white' : 'bg-white text-[#4d2128]/60 border border-[#de9ca4]/30 hover:border-[#de9ca4]'}`}
              style={catF === c.value ? { backgroundColor: P } : {}}>
              {c.label}
            </button>
          ))}
        </div>
        <button onClick={() => setAdding(true)}
          className="w-8 h-8 rounded-xl flex items-center justify-center text-white flex-shrink-0 hover:opacity-90"
          style={{ backgroundColor: P }}>
          <Plus className="w-3.5 h-3.5" />
        </button>
      </div>
      {loading ? <div className="flex justify-center py-6"><RefreshCw className="w-4 h-4 animate-spin" style={{ color: P }} /></div>
        : items.length === 0 ? <EmptyState text="Chưa có rule" /> : (
        <div className="space-y-2">
          {items.map(r => (
            <div key={r.id}
              className={`bg-white rounded-2xl shadow-sm px-4 py-3 transition-opacity ${!r.is_active ? 'opacity-50' : ''}`}>
              <div className="flex items-start gap-2">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-1.5 mb-1 flex-wrap">
                    <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded-full ${RCAT_COLOR[r.category] || 'bg-gray-100 text-gray-600'}`}>{r.category}</span>
                    <span className="text-[9px] text-gray-400 font-mono">p={r.priority}</span>
                    {!r.is_active && <span className="text-[9px] text-gray-400 italic">off</span>}
                  </div>
                  <p className="text-xs text-gray-700 leading-relaxed">{r.rule_text}</p>
                </div>
                <div className="flex items-center gap-1 flex-shrink-0">
                  <button onClick={() => handleToggle(r)} title={r.is_active ? 'Tắt' : 'Bật'}
                    className={`p-1.5 rounded-lg transition-colors ${r.is_active ? 'text-green-500 hover:bg-green-50' : 'text-gray-300 hover:bg-gray-50'}`}>
                    <ShieldAlert className="w-3.5 h-3.5" />
                  </button>
                  <button onClick={() => setEditing(r)} className="p-1.5 rounded-lg text-gray-400 hover:text-blue-600 hover:bg-blue-50 transition-colors"><Pencil className="w-3.5 h-3.5" /></button>
                  <button onClick={() => setConfirm(r.id)} className="p-1.5 rounded-lg text-gray-400 hover:text-red-500 hover:bg-red-50 transition-colors"><Trash2 className="w-3.5 h-3.5" /></button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function ChatbotTab({ onToast }: { onToast(msg: string, ok: boolean): void }) {
  const [section, setSection] = useState<'personas' | 'prompts' | 'rules'>('personas');

  const handleInvalidate = async () => {
    try { await adminSvc.invalidateChatbotCache(); onToast('Cache NLU đã được xóa', true); }
    catch (e: any) { onToast(e.message, false); }
  };

  return (
    <div className="space-y-3 pb-4 px-4">
      <div className="flex items-center justify-between pt-1">
        <div className="flex gap-1.5">
          {(['personas', 'prompts', 'rules'] as const).map(s => (
            <button key={s} onClick={() => setSection(s)}
              className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition-all
                ${section === s ? 'text-white shadow-sm' : 'text-[#4d2128]/55 hover:text-[#4d2128] hover:bg-[#de9ca4]/10'}`}
              style={section === s ? { backgroundColor: P } : {}}>
              {s === 'personas' ? 'Persona' : s === 'prompts' ? 'Prompts' : 'Rules'}
            </button>
          ))}
        </div>
        <button onClick={handleInvalidate}
          className="text-[10px] text-gray-400 hover:text-amber-600 flex items-center gap-1 transition-colors">
          <RefreshCw className="w-3 h-3" /> Cache
        </button>
      </div>
      {section === 'personas' && <PersonasSection onToast={onToast} />}
      {section === 'prompts'  && <PromptsSection  onToast={onToast} />}
      {section === 'rules'    && <RulesSection    onToast={onToast} />}
    </div>
  );
}

/* ══════════════════════════════════════════════════════════════════════════════
   MAIN COMPONENT
══════════════════════════════════════════════════════════════════════════════ */
export function AdminDashboardScreen({ onNavigate, hideHeader = false }: Props) {
  const [tab,   setTab]   = useState<DashTab>('overview');
  const [toast, setToast] = useState<{ msg: string; ok: boolean } | null>(null);

  const showToast = useCallback((msg: string, ok: boolean) => {
    setToast({ msg, ok });
    setTimeout(() => setToast(null), 3000);
  }, []);

  return (
    <div className={hideHeader ? 'bg-transparent pb-6' : 'min-h-screen bg-[#fff4f4] pb-6'}>
      {toast && <Toast text={toast.msg} ok={toast.ok} />}

      {/* Standalone header (hidden when inside AdminShell) */}
      {!hideHeader && (
        <div className="bg-[#1c0003] text-white px-4 pt-12 pb-3 flex items-center gap-3">
          <button onClick={() => onNavigate('home')}
            className="p-2 rounded-xl text-white hover:bg-white/10 transition-colors">
            <ChevronLeft className="w-5 h-5" />
          </button>
          <div>
            <h1 className="text-base font-bold">Quản trị hệ thống</h1>
            <p className="text-[11px] text-red-300">Admin Dashboard</p>
          </div>
        </div>
      )}

      {/* Tab bar */}
      <DashTabBar active={tab} onChange={t => setTab(t)} />

      {/* Tab divider */}
      <div className="mx-4 h-px bg-[#de9ca4]/15 mb-1" />

      {/* Content */}
      {tab === 'overview'   && <OverviewTab />}
      {tab === 'locations'  && <LocationsTab  onToast={showToast} />}
      {tab === 'procedures' && <ProceduresTab onToast={showToast} />}
      {tab === 'chatbot'    && <ChatbotTab    onToast={showToast} />}
    </div>
  );
}
