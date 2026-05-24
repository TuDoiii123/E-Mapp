/**
 * AdminUsersScreen — Quản lý Tài khoản  (Desktop redesign)
 *
 * Layout (matches HTML design):
 *   • Hero: headline "Quản lý Tài khoản" + 2-col stats grid
 *   • Search / filter bar (plinth underline-input style)
 *   • Data table: Thông tin | CCCD | Vai trò | Trạng thái + hover actions
 *   • Pagination
 *   • Image anchor section
 */
import React, {
  useState, useEffect, useCallback, useRef,
} from 'react';
import {
  RefreshCw, Search, Plus, X, Save, Pencil, Trash2,
  Eye, EyeOff, MoreVertical, CheckCircle, AlertCircle,
  KeyRound, Users, ShieldCheck,
} from 'lucide-react';
import * as adminSvc from '../services/adminService';

interface Props { onNavigate: (s: string, p?: any) => void }

const PRIMARY = '#8f000d';
const GOLD    = '#fcd400';

// ── Helpers ───────────────────────────────────────────────────────────────────
function initials(name?: string) {
  if (!name) return '?';
  const parts = name.trim().split(' ');
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
  return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
}

const ROLE_LABEL: Record<string, string> = {
  admin:   'Quản trị viên',
  staff:   'Cán bộ',
  citizen: 'Công dân',
};
const ROLE_BADGE: Record<string, React.CSSProperties> = {
  admin:   { backgroundColor: PRIMARY,   color: '#fff' },
  staff:   { backgroundColor: GOLD,      color: '#221b00' },
  citizen: { backgroundColor: '#e8e8e8', color: '#5a403e' },
};
const ISSUED_BY: Record<string, string> = {
  admin:   'Cấp bởi Bộ Công An',
  staff:   'Cấp bởi Bộ Công An',
  citizen: 'Thẻ căn cước công dân',
};

// ── Toast ─────────────────────────────────────────────────────────────────────
function Toast({ msg, ok }: { msg: string; ok: boolean }) {
  return (
    <div className={`fixed bottom-6 right-6 z-50 px-4 py-2.5 rounded-xl shadow-lg text-sm font-medium
      text-white flex items-center gap-2 max-w-xs
      ${ok ? 'bg-green-600' : 'bg-red-700'}`}>
      {ok ? <CheckCircle className="w-4 h-4 flex-shrink-0" /> : <AlertCircle className="w-4 h-4 flex-shrink-0" />}
      {msg}
    </div>
  );
}

// ── Confirm Dialog ────────────────────────────────────────────────────────────
function ConfirmDialog({ msg, onYes, onNo }: { msg: string; onYes(): void; onNo(): void }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 px-6">
      <div className="bg-white rounded-2xl p-6 w-full max-w-sm shadow-2xl">
        <p className="text-sm text-gray-700 mb-6 text-center">{msg}</p>
        <div className="flex gap-3">
          <button onClick={onNo}
            className="flex-1 py-2.5 rounded-xl border border-[#de9ca4]/30 text-sm font-bold text-[#4d2128]/70
              hover:bg-[#fff4f4] transition-colors">
            Hủy
          </button>
          <button onClick={onYes}
            className="flex-1 py-2.5 rounded-xl text-white text-sm font-bold hover:opacity-90 transition-opacity"
            style={{ backgroundColor: PRIMARY }}>
            Xác nhận xóa
          </button>
        </div>
      </div>
    </div>
  );
}

// ── User Form Modal ───────────────────────────────────────────────────────────
function UserFormModal({
  initial, onSave, onClose,
}: {
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

  const fields: { label: string; key: keyof typeof form; type: string }[] = [
    { label: 'Số CCCD *',   key: 'cccdNumber', type: 'text' },
    { label: 'Họ và tên *', key: 'fullName',   type: 'text' },
    { label: 'Email',       key: 'email',      type: 'email' },
    { label: 'Điện thoại',  key: 'phone',      type: 'tel' },
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 px-4">
      <div className="bg-white rounded-2xl w-full max-w-md shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-[#de9ca4]/20"
          style={{ borderLeftWidth: 4, borderLeftColor: PRIMARY }}>
          <h3 className="font-bold text-gray-900">
            {initial ? 'Sửa tài khoản' : 'Thêm tài khoản mới'}
          </h3>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600 p-1">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Body */}
        <div className="px-6 py-5 space-y-4">
          {fields.map(f => (
            <div key={f.key}>
              <label className="text-[10px] font-bold uppercase tracking-widest text-gray-400 block mb-1.5">
                {f.label}
              </label>
              <input
                type={f.type}
                value={form[f.key] as string}
                onChange={set(f.key)}
                className="w-full bg-transparent pb-2 border-b-2 border-gray-300 focus:border-yellow-500
                  outline-none text-sm font-medium text-gray-800 transition-colors"
                style={{ borderBottomColor: undefined }}
                onFocus={e => (e.target.style.borderBottomColor = GOLD)}
                onBlur={e => (e.target.style.borderBottomColor = '')}
              />
            </div>
          ))}

          <div>
            <label className="text-[10px] font-bold uppercase tracking-widest text-gray-400 block mb-1.5">
              Vai trò
            </label>
            <select
              value={form.role}
              onChange={set('role')}
              className="w-full bg-transparent pb-2 border-b-2 border-gray-300 outline-none
                text-sm font-medium text-gray-800"
            >
              <option value="citizen">Công dân</option>
              <option value="staff">Cán bộ</option>
              <option value="admin">Quản trị viên</option>
            </select>
          </div>

          {!initial && (
            <div>
              <label className="text-[10px] font-bold uppercase tracking-widest text-gray-400 block mb-1.5">
                Mật khẩu *
              </label>
              <div className="relative">
                <input
                  type={showPwd ? 'text' : 'password'}
                  value={form.password}
                  onChange={set('password')}
                  className="w-full bg-transparent pb-2 border-b-2 border-gray-300 outline-none
                    text-sm font-medium text-gray-800 pr-8"
                />
                <button
                  className="absolute right-0 bottom-2 text-gray-400 hover:text-gray-600"
                  onClick={() => setShowPwd(v => !v)}
                >
                  {showPwd ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-5 py-4 border-t border-[#de9ca4]/20 flex gap-3">
          <button
            onClick={onClose}
            className="flex-1 py-2.5 rounded-xl border border-[#de9ca4]/30 text-sm font-bold text-[#4d2128]/70
              hover:bg-[#fff4f4] transition-colors"
          >
            Hủy
          </button>
          <button
            onClick={() => onSave(form)}
            className="flex-1 py-2.5 rounded-xl text-white text-sm font-bold hover:opacity-90 transition-opacity
              flex items-center justify-center gap-2"
            style={{ backgroundColor: PRIMARY }}
          >
            <Save className="w-4 h-4" />
            {initial ? 'Cập nhật' : 'Tạo tài khoản'}
          </button>
        </div>
      </div>
    </div>
  );
}

// ── Row context menu ──────────────────────────────────────────────────────────
function RowMenu({
  user,
  onEdit, onDelete, onResetPwd,
}: {
  user: any;
  onEdit(): void; onDelete(): void; onResetPwd(): void;
}) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  return (
    <div className="relative" ref={ref}>
      <button
        onClick={() => setOpen(v => !v)}
        className="p-1.5 rounded hover:bg-[#fff4f4] text-[#9f364c]/40 hover:text-[#9f364c] transition-colors"
      >
        <MoreVertical className="w-4 h-4" />
      </button>
      {open && (
        <div className="absolute right-0 top-8 z-30 bg-white rounded-xl shadow-xl border border-[#de9ca4]/20 w-44 py-1 overflow-hidden">
          <button onClick={() => { onEdit(); setOpen(false); }}
            className="w-full flex items-center gap-2.5 px-4 py-2.5 text-sm text-[#4d2128]/80 hover:bg-[#fff4f4]">
            <Pencil className="w-3.5 h-3.5 text-gray-400" /> Sửa thông tin
          </button>
          <button onClick={() => { onResetPwd(); setOpen(false); }}
            className="w-full flex items-center gap-2.5 px-4 py-2.5 text-sm text-[#4d2128]/80 hover:bg-[#fff4f4]">
            <KeyRound className="w-3.5 h-3.5 text-gray-400" /> Đặt lại mật khẩu
          </button>
          <div className="border-t border-[#de9ca4]/20 my-1" />
          <button onClick={() => { onDelete(); setOpen(false); }}
            className="w-full flex items-center gap-2.5 px-4 py-2.5 text-sm hover:bg-red-50"
            style={{ color: PRIMARY }}>
            <Trash2 className="w-3.5 h-3.5" /> Xóa tài khoản
          </button>
        </div>
      )}
    </div>
  );
}

// ── Reset Password Modal ──────────────────────────────────────────────────────
function ResetPwdModal({
  user, onClose, onSave,
}: {
  user: any; onClose(): void; onSave(id: string, pwd: string): void;
}) {
  const [pwd,  setPwd]  = useState('');
  const [show, setShow] = useState(false);
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 px-4">
      <div className="bg-white rounded-2xl w-full max-w-sm shadow-2xl overflow-hidden">
        <div className="flex items-center justify-between px-5 py-4 border-b border-[#de9ca4]/20">
          <h3 className="font-bold text-gray-900 text-sm">Đặt lại mật khẩu</h3>
          <button onClick={onClose}><X className="w-5 h-5 text-gray-400" /></button>
        </div>
        <div className="px-6 py-5">
          <p className="text-xs text-gray-500 mb-4">Tài khoản: <strong>{user.fullName}</strong></p>
          <label className="text-[10px] font-bold uppercase tracking-widest text-gray-400 block mb-1.5">
            Mật khẩu mới
          </label>
          <div className="relative">
            <input
              type={show ? 'text' : 'password'}
              value={pwd}
              onChange={e => setPwd(e.target.value)}
              className="w-full bg-transparent pb-2 border-b-2 border-gray-300 outline-none text-sm pr-8"
            />
            <button className="absolute right-0 bottom-2 text-gray-400 hover:text-gray-600"
              onClick={() => setShow(v => !v)}>
              {show ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
            </button>
          </div>
        </div>
        <div className="px-5 pb-5 flex gap-3">
          <button onClick={onClose}
            className="flex-1 py-2.5 rounded-xl border border-[#de9ca4]/30 text-sm font-bold text-[#4d2128]/70 hover:bg-[#fff4f4]">
            Hủy
          </button>
          <button disabled={!pwd.trim()}
            onClick={() => onSave(user.id, pwd)}
            className="flex-1 py-2.5 rounded-xl text-white text-sm font-bold hover:opacity-90 disabled:opacity-50"
            style={{ backgroundColor: PRIMARY }}>
            Xác nhận
          </button>
        </div>
      </div>
    </div>
  );
}

// ── Main Component ────────────────────────────────────────────────────────────
export function AdminUsersScreen({ onNavigate }: Props) {
  const [stats,      setStats]      = useState<any>(null);
  const [items,      setItems]      = useState<any[]>([]);
  const [loading,    setLoading]    = useState(true);
  const [q,          setQ]          = useState('');
  const [roleFilter, setRoleFilter] = useState('');
  const [page,       setPage]       = useState(1);
  const [total,      setTotal]      = useState(0);
  const [adding,     setAdding]     = useState(false);
  const [editing,    setEditing]    = useState<any>(null);
  const [confirm,    setConfirm]    = useState<string | null>(null);
  const [resetPwd,   setResetPwd]   = useState<any>(null);
  const [toast,      setToast]      = useState<{ msg: string; ok: boolean } | null>(null);
  const LIMIT = 12;

  const showToast = (msg: string, ok: boolean) => {
    setToast({ msg, ok });
    setTimeout(() => setToast(null), 3000);
  };

  const load = useCallback(async () => {
    setLoading(true);
    const params: Record<string, string> = { page: String(page), limit: String(LIMIT) };
    if (q)          params.q    = q;
    if (roleFilter) params.role = roleFilter;

    const [usersR, statsR] = await Promise.allSettled([
      adminSvc.getUsers(params),
      adminSvc.getStats(),
    ]);
    if (usersR.status === 'fulfilled') {
      setItems(usersR.value.data || []);
      setTotal(usersR.value.pagination?.total || 0);
    }
    if (statsR.status === 'fulfilled') setStats(statsR.value.data ?? statsR.value);
    setLoading(false);
  }, [q, roleFilter, page]);

  useEffect(() => { load(); }, [load]);

  const handleSave = async (data: any) => {
    try {
      if (editing) {
        await adminSvc.updateUser(editing.id, data);
        showToast('Đã cập nhật tài khoản', true);
      } else {
        await adminSvc.createUser(data);
        showToast('Đã tạo tài khoản', true);
      }
      setEditing(null); setAdding(false); load();
    } catch (e: any) { showToast(e.message || 'Lỗi lưu tài khoản', false); }
  };

  const handleDelete = async (id: string) => {
    try {
      await adminSvc.deleteUser(id);
      showToast('Đã xóa tài khoản', true); load();
    } catch (e: any) { showToast(e.message || 'Không thể xóa', false); }
    finally { setConfirm(null); }
  };

  const handleResetPwd = async (id: string, pwd: string) => {
    try {
      await adminSvc.resetPassword(id, pwd);
      showToast('Đã đặt lại mật khẩu', true);
    } catch (e: any) { showToast(e.message || 'Lỗi đặt lại mật khẩu', false); }
    finally { setResetPwd(null); }
  };

  const totalPages = Math.max(1, Math.ceil(total / LIMIT));

  // Page numbers
  const pageNums = (() => {
    if (totalPages <= 5) return Array.from({ length: totalPages }, (_, i) => i + 1);
    return [page - 1, page, page + 1].filter(n => n >= 1 && n <= totalPages);
  })();

  return (
    <div className="min-h-full bg-transparent">

      {/* Modals */}
      {(adding || editing) && (
        <UserFormModal initial={editing}
          onSave={handleSave}
          onClose={() => { setAdding(false); setEditing(null); }} />
      )}
      {confirm && (
        <ConfirmDialog msg="Xóa tài khoản này? Hành động không thể hoàn tác."
          onYes={() => handleDelete(confirm)}
          onNo={() => setConfirm(null)} />
      )}
      {resetPwd && (
        <ResetPwdModal user={resetPwd}
          onClose={() => setResetPwd(null)}
          onSave={handleResetPwd} />
      )}
      {toast && <Toast msg={toast.msg} ok={toast.ok} />}

      <div className="px-4 py-4 space-y-4">

        {/* ── Stats row ───────────────────────────────────────────────── */}
        <section className="flex gap-2">
          {[
            { label: 'Tổng tài khoản', value: stats?.totalUsers,        Icon: Users,      bg: 'bg-red-50',  color: 'text-[#8f000d]' },
            { label: 'Hồ sơ đã nộp',  value: stats?.totalApplications, Icon: ShieldCheck, bg: 'bg-blue-50', color: 'text-blue-600'  },
          ].map(s => (
            <div key={s.label} className="flex-1 bg-white rounded-2xl px-4 py-3 shadow-sm flex items-center gap-3">
              <div className={`w-9 h-9 ${s.bg} rounded-xl flex items-center justify-center shrink-0`}>
                <s.Icon className={`w-4 h-4 ${s.color}`} />
              </div>
              <div>
                <p className="text-lg font-black text-gray-900 leading-none">
                  {loading ? '—' : (s.value?.toLocaleString('vi-VN') ?? '—')}
                </p>
                <p className="text-[9px] font-bold uppercase tracking-wide text-gray-400 mt-0.5">{s.label}</p>
              </div>
            </div>
          ))}
          <button onClick={load}
            className="w-11 h-11 bg-white rounded-2xl shadow-sm flex items-center justify-center
              text-gray-400 hover:text-gray-600 transition-colors shrink-0 self-center">
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </section>

        {/* ── Filter bar ──────────────────────────────────────────────── */}
        <section className="bg-white rounded-2xl p-5 shadow-sm flex flex-col md:flex-row gap-5 items-end">
          {/* Search */}
          <div className="flex-1 w-full space-y-1.5">
            <label className="text-[10px] font-bold uppercase tracking-widest text-gray-400">
              Tìm kiếm định danh (Họ tên, CCCD, Email)
            </label>
            <div className="flex items-center gap-2">
              <Search className="w-4 h-4 text-gray-400 flex-shrink-0" />
              <input
                type="text"
                value={q}
                onChange={e => { setQ(e.target.value); setPage(1); }}
                placeholder="Nhập từ khóa tìm kiếm..."
                className="flex-1 bg-transparent pb-2 border-b-2 border-gray-300 outline-none
                  text-sm font-medium text-gray-800 transition-colors
                  focus:border-yellow-400"
              />
            </div>
          </div>

          <div className="flex items-end gap-4 w-full md:w-auto">
            {/* Role filter */}
            <div className="flex-1 md:w-44 space-y-1.5">
              <label className="text-[10px] font-bold uppercase tracking-widest text-gray-400">
                Vai trò
              </label>
              <select
                value={roleFilter}
                onChange={e => { setRoleFilter(e.target.value); setPage(1); }}
                className="w-full bg-transparent pb-2 border-b-2 border-gray-300 outline-none
                  text-sm font-medium text-gray-700"
              >
                <option value="">Tất cả vai trò</option>
                <option value="citizen">Công dân</option>
                <option value="staff">Cán bộ</option>
                <option value="admin">Quản trị viên</option>
              </select>
            </div>

            {/* Add button */}
            <button
              onClick={() => setAdding(true)}
              className="h-11 px-5 rounded-xl text-white text-sm font-bold
                hover:opacity-90 transition-opacity flex items-center gap-2 flex-shrink-0"
              style={{ backgroundColor: PRIMARY }}
            >
              <Plus className="w-4 h-4" />
              Thêm tài khoản
            </button>
          </div>
        </section>

        {/* ── Table ───────────────────────────────────────────────────── */}
        <div className="bg-white rounded-2xl shadow-sm overflow-hidden">
          {loading ? (
            <div className="flex justify-center py-20">
              <RefreshCw className="w-6 h-6 animate-spin" style={{ color: PRIMARY }} />
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left">
                <thead>
                  <tr className="border-b-2 bg-[#fff4f4]" style={{ borderBottomColor: `${PRIMARY}33` }}>
                    {['Thông tin người dùng', 'Số CCCD / Định danh', 'Vai trò', 'Trạng thái'].map(h => (
                      <th key={h}
                        className="px-8 py-5 text-[10px] font-bold uppercase tracking-widest text-gray-500"
                        style={h === 'Trạng thái' ? { textAlign: 'right' } : undefined}>
                        {h}
                      </th>
                    ))}
                  </tr>
                </thead>

                <tbody>
                  {items.length === 0 ? (
                    <tr>
                      <td colSpan={4} className="px-8 py-14 text-center text-gray-400 text-sm">
                        Không có tài khoản nào
                      </td>
                    </tr>
                  ) : (
                    items.map(u => (
                      <tr key={u.id}
                        className="border-b border-[#de9ca4]/10 hover:bg-[#fff4f4]/70 transition-colors group cursor-pointer">
                        {/* Thông tin */}
                        <td className="px-8 py-5">
                          <div className="flex items-center gap-4">
                            <div
                              className="w-10 h-10 flex items-center justify-center flex-shrink-0
                                font-bold text-sm rounded-xl border border-[#de9ca4]/30 bg-[#fff4f4]"
                              style={{ color: PRIMARY }}
                            >
                              {initials(u.fullName)}
                            </div>
                            <div>
                              <p className="font-bold text-gray-900 leading-tight">{u.fullName || '–'}</p>
                              <p className="text-sm text-gray-400 mt-0.5">{u.email || '–'}</p>
                            </div>
                          </div>
                        </td>

                        {/* CCCD */}
                        <td className="px-8 py-5">
                          <p className="font-mono text-sm tracking-widest text-gray-900">
                            {u.cccdNumber || '–'}
                          </p>
                          <p className="text-[10px] font-bold uppercase mt-0.5"
                            style={{ color: ['admin', 'staff'].includes(u.role) ? '#705d00' : '#9ca3af' }}>
                            {ISSUED_BY[u.role] || 'Thẻ căn cước công dân'}
                          </p>
                        </td>

                        {/* Vai trò */}
                        <td className="px-8 py-5">
                          <span
                            className="px-3 py-1 rounded-full text-xs font-bold"
                            style={ROLE_BADGE[u.role] ?? { backgroundColor: '#e8e8e8', color: '#5a403e' }}
                          >
                            {ROLE_LABEL[u.role] || u.role}
                          </span>
                        </td>

                        {/* Trạng thái + actions */}
                        <td className="px-8 py-5">
                          <div className="flex items-center justify-end gap-3">
                            <div className="flex items-center gap-1.5">
                              <div className="w-2 h-2 rounded-full bg-green-500 flex-shrink-0" />
                              <span className="text-xs font-bold text-gray-500 uppercase">Hoạt động</span>
                            </div>
                            <div className="opacity-0 group-hover:opacity-100 transition-opacity">
                              <RowMenu
                                user={u}
                                onEdit={() => setEditing(u)}
                                onDelete={() => setConfirm(u.id)}
                                onResetPwd={() => setResetPwd(u)}
                              />
                            </div>
                          </div>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          )}

          {/* Pagination footer */}
          <div className="px-5 py-4 border-t border-[#de9ca4]/20 flex justify-between items-center bg-white">
            <p className="text-xs text-gray-500 font-medium">
              {Math.min((page - 1) * LIMIT + 1, total)}–{Math.min(page * LIMIT, total)} / {total.toLocaleString('vi-VN')}
            </p>
            <div className="flex gap-1">
              <button
                disabled={page === 1}
                onClick={() => setPage(p => p - 1)}
                className="w-8 h-8 flex items-center justify-center rounded-lg border border-[#de9ca4]/30
                  hover:bg-[#fff4f4] disabled:opacity-40 text-[#4d2128] text-base"
              >
                ‹
              </button>
              {page > 2 && (
                <>
                  <button onClick={() => setPage(1)}
                    className="w-8 h-8 rounded-lg text-sm font-bold text-[#4d2128] border border-[#de9ca4]/30 hover:bg-[#fff4f4]">
                    1
                  </button>
                  {page > 3 && <span className="w-8 h-8 flex items-center justify-center text-gray-400 text-sm">…</span>}
                </>
              )}
              {pageNums.map(n => (
                <button key={n}
                  onClick={() => setPage(n)}
                  className="w-8 h-8 rounded-lg text-sm font-bold transition-all border"
                  style={page === n
                    ? { backgroundColor: PRIMARY, color: '#fff', borderColor: PRIMARY }
                    : { borderColor: '#e5e7eb', color: '#374151' }}
                >
                  {n}
                </button>
              ))}
              {page < totalPages - 1 && (
                <>
                  {page < totalPages - 2 && (
                    <span className="w-8 h-8 flex items-center justify-center text-gray-400 text-sm">…</span>
                  )}
                  <button onClick={() => setPage(totalPages)}
                    className="w-8 h-8 rounded-lg text-sm font-bold text-[#4d2128] border border-[#de9ca4]/30 hover:bg-[#fff4f4]">
                    {totalPages}
                  </button>
                </>
              )}
              <button
                disabled={page >= totalPages}
                onClick={() => setPage(p => p + 1)}
                className="w-8 h-8 flex items-center justify-center rounded-lg border border-[#de9ca4]/30
                  hover:bg-[#fff4f4] disabled:opacity-40 text-[#4d2128] text-base"
              >
                ›
              </button>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}
