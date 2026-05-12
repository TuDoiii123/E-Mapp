/**
 * AdminDashboardScreen — Panel quản trị
 * Tab: Tổng quan | Tài khoản | Địa điểm | Thủ tục
 */
import React, { useState, useEffect, useCallback } from 'react';
import {
  ChevronLeft, Users, MapPin, FileText, BarChart3,
  Plus, Pencil, Trash2, Search, RefreshCw, AlertCircle,
  CheckCircle, X, Save, Eye, EyeOff, Calendar, ClipboardList,
  ThumbsUp, ThumbsDown, MessageSquare, Bot, Zap, ShieldAlert,
} from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import * as adminSvc from '../services/adminService';

interface Props { onNavigate: (screen: string, params?: any) => void; }

// ── Reusable confirm dialog ────────────────────────────────────────────────────
function ConfirmDialog({ msg, onYes, onNo }: { msg: string; onYes(): void; onNo(): void }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-6">
      <div className="bg-white rounded-2xl p-6 w-full max-w-sm shadow-2xl">
        <p className="text-sm text-gray-700 mb-5 text-center">{msg}</p>
        <div className="flex gap-3">
          <Button variant="outline" className="flex-1" onClick={onNo}>Hủy</Button>
          <Button className="flex-1 bg-red-600 hover:bg-red-700 text-white" onClick={onYes}>Xác nhận</Button>
        </div>
      </div>
    </div>
  );
}

// ── Toast ─────────────────────────────────────────────────────────────────────
function Toast({ text, ok }: { text: string; ok: boolean }) {
  return (
    <div className={`fixed bottom-24 left-1/2 -translate-x-1/2 z-50 px-4 py-2.5 rounded-full
      shadow-lg text-sm font-medium text-white flex items-center gap-2
      ${ok ? 'bg-green-600' : 'bg-red-600'}`}>
      {ok ? <CheckCircle className="w-4 h-4" /> : <AlertCircle className="w-4 h-4" />}
      {text}
    </div>
  );
}

// ════════════════════════════════════════════════════════════════════════════════
// TAB: TỔNG QUAN
// ════════════════════════════════════════════════════════════════════════════════
function OverviewTab() {
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    adminSvc.getStats()
      .then(r => setStats(r.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="flex justify-center py-12"><RefreshCw className="w-6 h-6 animate-spin text-gray-400" /></div>;
  if (!stats)  return <p className="text-center text-gray-500 py-8">Không thể tải thống kê</p>;

  const cards = [
    { label: 'Người dùng',   value: stats.totalUsers,          icon: Users,     color: 'bg-blue-100 text-blue-700' },
    { label: 'Địa điểm',     value: stats.totalLocations,      icon: MapPin,    color: 'bg-green-100 text-green-700' },
    { label: 'Thủ tục',      value: stats.totalProcedures,     icon: FileText,  color: 'bg-purple-100 text-purple-700' },
    { label: 'Hồ sơ',        value: stats.totalApplications,   icon: BarChart3, color: 'bg-yellow-100 text-yellow-700' },
    { label: 'Chờ duyệt',    value: stats.pendingApplications, icon: AlertCircle, color: 'bg-orange-100 text-orange-700' },
    { label: 'Vé hôm nay',   value: stats.ticketsToday,        icon: RefreshCw, color: 'bg-red-100 text-red-700' },
  ];

  return (
    <div className="grid grid-cols-2 gap-3 pt-2">
      {cards.map(c => (
        <Card key={c.label}>
          <CardContent className="p-4 flex items-center gap-3">
            <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${c.color}`}>
              <c.icon className="w-5 h-5" />
            </div>
            <div>
              <p className="text-xl font-bold text-gray-800">{c.value ?? '–'}</p>
              <p className="text-xs text-gray-500">{c.label}</p>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}

// ════════════════════════════════════════════════════════════════════════════════
// TAB: TÀI KHOẢN
// ════════════════════════════════════════════════════════════════════════════════
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
    <div className="fixed inset-0 z-50 flex items-end justify-center bg-black/40">
      <div className="bg-white rounded-t-2xl w-full max-w-lg p-5 space-y-3 max-h-[80vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-2">
          <h3 className="font-bold text-gray-800">{initial ? 'Sửa tài khoản' : 'Thêm tài khoản'}</h3>
          <button onClick={onClose}><X className="w-5 h-5 text-gray-400" /></button>
        </div>

        {[
          { label: 'Số CCCD *',  key: 'cccdNumber', type: 'text' },
          { label: 'Họ tên *',   key: 'fullName',   type: 'text' },
          { label: 'Email',      key: 'email',      type: 'email' },
          { label: 'Điện thoại', key: 'phone',      type: 'tel' },
        ].map(f => (
          <div key={f.key}>
            <label className="text-xs text-gray-500">{f.label}</label>
            <Input type={f.type} value={(form as any)[f.key]}
              onChange={set(f.key)} className="mt-1 h-10" />
          </div>
        ))}

        <div>
          <label className="text-xs text-gray-500">Vai trò</label>
          <select value={form.role} onChange={set('role')}
            className="mt-1 w-full h-10 border border-gray-200 rounded-md px-3 text-sm bg-white">
            <option value="citizen">Công dân</option>
            <option value="staff">Nhân viên</option>
            <option value="admin">Quản trị</option>
          </select>
        </div>

        {!initial && (
          <div>
            <label className="text-xs text-gray-500">Mật khẩu *</label>
            <div className="relative mt-1">
              <Input type={showPwd ? 'text' : 'password'}
                value={form.password} onChange={set('password')} className="h-10 pr-10" />
              <button className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400"
                onClick={() => setShowPwd(v => !v)}>
                {showPwd ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
          </div>
        )}

        <div className="flex gap-3 pt-2">
          <Button variant="outline" className="flex-1" onClick={onClose}>Hủy</Button>
          <Button className="flex-1 bg-red-600 hover:bg-red-700 text-white"
            onClick={() => onSave(form)}>
            <Save className="w-4 h-4 mr-1.5" /> Lưu
          </Button>
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
    } catch { /* bỏ qua */ }
    finally { setLoading(false); }
  }, [q, page]);

  useEffect(() => { load(); }, [load]);

  const handleSave = async (data: any) => {
    try {
      if (editing) {
        await adminSvc.updateUser(editing.id, data);
        onToast('Đã cập nhật tài khoản', true);
      } else {
        await adminSvc.createUser(data);
        onToast('Đã tạo tài khoản', true);
      }
      setEditing(null); setAdding(false); load();
    } catch (e: any) { onToast(e.message, false); }
  };

  const handleDelete = async (id: string) => {
    try {
      await adminSvc.deleteUser(id);
      onToast('Đã xóa tài khoản', true);
      load();
    } catch (e: any) { onToast(e.message, false); }
    finally { setConfirm(null); }
  };

  const ROLE_COLOR: Record<string, string> = {
    admin:   'bg-red-100 text-red-700',
    staff:   'bg-blue-100 text-blue-700',
    citizen: 'bg-gray-100 text-gray-600',
  };
  const ROLE_LABEL: Record<string, string> = {
    admin: 'Quản trị', staff: 'Nhân viên', citizen: 'Công dân',
  };

  return (
    <div className="space-y-3 pt-2">
      {(editing || adding) && (
        <UserForm initial={editing} onSave={handleSave}
          onClose={() => { setEditing(null); setAdding(false); }} />
      )}
      {confirm && (
        <ConfirmDialog msg="Xóa tài khoản này?"
          onYes={() => handleDelete(confirm)} onNo={() => setConfirm(null)} />
      )}

      {/* Tìm kiếm + thêm */}
      <div className="flex gap-2">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <Input value={q} onChange={e => { setQ(e.target.value); setPage(1); }}
            placeholder="Tìm tên, CCCD, email..." className="pl-9 h-10" />
        </div>
        <Button className="bg-red-600 hover:bg-red-700 text-white h-10 px-3"
          onClick={() => setAdding(true)}>
          <Plus className="w-4 h-4" />
        </Button>
      </div>

      {loading ? (
        <div className="flex justify-center py-8"><RefreshCw className="w-5 h-5 animate-spin text-gray-400" /></div>
      ) : items.length === 0 ? (
        <p className="text-center text-gray-400 py-8 text-sm">Không có dữ liệu</p>
      ) : (
        <div className="space-y-2">
          {items.map(u => (
            <div key={u.id}
              className="flex items-center justify-between bg-white rounded-xl px-4 py-3 shadow-sm">
              <div className="flex-1 min-w-0 mr-3">
                <p className="text-sm font-medium text-gray-800 truncate">{u.fullName}</p>
                <p className="text-xs text-gray-400 truncate">{u.cccdNumber} • {u.email}</p>
              </div>
              <div className="flex items-center gap-2 flex-shrink-0">
                <Badge className={`text-xs ${ROLE_COLOR[u.role] || 'bg-gray-100 text-gray-600'}`}>
                  {ROLE_LABEL[u.role] || u.role}
                </Badge>
                <button className="text-gray-400 hover:text-blue-600 p-1"
                  onClick={() => setEditing(u)}><Pencil className="w-4 h-4" /></button>
                <button className="text-gray-400 hover:text-red-500 p-1"
                  onClick={() => setConfirm(u.id)}><Trash2 className="w-4 h-4" /></button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Phân trang */}
      {total > 15 && (
        <div className="flex justify-center gap-3 pt-1">
          <Button variant="outline" size="sm" disabled={page === 1}
            onClick={() => setPage(p => p - 1)}>Trước</Button>
          <span className="text-xs text-gray-500 self-center">
            {page} / {Math.ceil(total / 15)}
          </span>
          <Button variant="outline" size="sm" disabled={page >= Math.ceil(total / 15)}
            onClick={() => setPage(p => p + 1)}>Sau</Button>
        </div>
      )}
    </div>
  );
}

// ════════════════════════════════════════════════════════════════════════════════
// TAB: ĐỊA ĐIỂM
// ════════════════════════════════════════════════════════════════════════════════
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
    <div className="fixed inset-0 z-50 flex items-end justify-center bg-black/40">
      <div className="bg-white rounded-t-2xl w-full max-w-lg p-5 space-y-3 max-h-[80vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-2">
          <h3 className="font-bold text-gray-800">{initial ? 'Sửa địa điểm' : 'Thêm địa điểm'}</h3>
          <button onClick={onClose}><X className="w-5 h-5 text-gray-400" /></button>
        </div>
        {[
          { label: 'Tên *',       key: 'name' },
          { label: 'Địa chỉ',    key: 'address' },
          { label: 'Phường/Xã',  key: 'ward' },
          { label: 'Quận/Huyện', key: 'district' },
          { label: 'Tỉnh/TP',    key: 'province' },
          { label: 'Vĩ độ (lat)',key: 'latitude' },
          { label: 'Kinh độ (lng)',key: 'longitude' },
        ].map(f => (
          <div key={f.key}>
            <label className="text-xs text-gray-500">{f.label}</label>
            <Input value={(form as any)[f.key]} onChange={set(f.key)} className="mt-1 h-10" />
          </div>
        ))}
        <div>
          <label className="text-xs text-gray-500">Cấp</label>
          <select value={form.level} onChange={set('level')}
            className="mt-1 w-full h-10 border border-gray-200 rounded-md px-3 text-sm bg-white">
            <option value="ward">Phường/Xã</option>
            <option value="district">Quận/Huyện</option>
            <option value="province">Tỉnh/TP</option>
          </select>
        </div>
        <div className="flex gap-3 pt-2">
          <Button variant="outline" className="flex-1" onClick={onClose}>Hủy</Button>
          <Button className="flex-1 bg-red-600 hover:bg-red-700 text-white"
            onClick={() => onSave(form)}>
            <Save className="w-4 h-4 mr-1.5" /> Lưu
          </Button>
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
    try {
      const r = await adminSvc.getLocations({ q, limit: '30' });
      setItems(r.data || []);
    } catch { /* bỏ qua */ }
    finally { setLoading(false); }
  }, [q]);

  useEffect(() => { load(); }, [load]);

  const handleSave = async (data: any) => {
    try {
      if (editing) {
        await adminSvc.updateLocation(editing.id, data);
        onToast('Đã cập nhật địa điểm', true);
      } else {
        await adminSvc.createLocation(data);
        onToast('Đã thêm địa điểm', true);
      }
      setEditing(null); setAdding(false); load();
    } catch (e: any) { onToast(e.message, false); }
  };

  const handleDelete = async (id: string) => {
    try {
      await adminSvc.deleteLocation(id);
      onToast('Đã xóa địa điểm', true); load();
    } catch (e: any) { onToast(e.message, false); }
    finally { setConfirm(null); }
  };

  const LEVEL_LABEL: Record<string, string> = {
    ward: 'Phường/Xã', district: 'Quận/Huyện', province: 'Tỉnh/TP',
  };

  return (
    <div className="space-y-3 pt-2">
      {(editing || adding) && (
        <LocationForm initial={editing} onSave={handleSave}
          onClose={() => { setEditing(null); setAdding(false); }} />
      )}
      {confirm && (
        <ConfirmDialog msg="Xóa địa điểm này?"
          onYes={() => handleDelete(confirm)} onNo={() => setConfirm(null)} />
      )}

      <div className="flex gap-2">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <Input value={q} onChange={e => setQ(e.target.value)}
            placeholder="Tìm theo tên, địa chỉ..." className="pl-9 h-10" />
        </div>
        <Button className="bg-red-600 hover:bg-red-700 text-white h-10 px-3"
          onClick={() => setAdding(true)}>
          <Plus className="w-4 h-4" />
        </Button>
      </div>

      {loading ? (
        <div className="flex justify-center py-8"><RefreshCw className="w-5 h-5 animate-spin text-gray-400" /></div>
      ) : (
        <div className="space-y-2">
          {items.map(l => (
            <div key={l.id}
              className="flex items-center justify-between bg-white rounded-xl px-4 py-3 shadow-sm">
              <div className="flex-1 min-w-0 mr-3">
                <p className="text-sm font-medium text-gray-800 truncate">{l.name}</p>
                <p className="text-xs text-gray-400 truncate">{l.address || l.district}</p>
              </div>
              <div className="flex items-center gap-2 flex-shrink-0">
                <Badge className="text-xs bg-green-100 text-green-700">
                  {LEVEL_LABEL[l.level] || l.level}
                </Badge>
                <button className="text-gray-400 hover:text-blue-600 p-1"
                  onClick={() => setEditing(l)}><Pencil className="w-4 h-4" /></button>
                <button className="text-gray-400 hover:text-red-500 p-1"
                  onClick={() => setConfirm(l.id)}><Trash2 className="w-4 h-4" /></button>
              </div>
            </div>
          ))}
          {items.length === 0 && (
            <p className="text-center text-gray-400 py-8 text-sm">Không có dữ liệu</p>
          )}
        </div>
      )}
    </div>
  );
}

// ════════════════════════════════════════════════════════════════════════════════
// TAB: THỦ TỤC
// ════════════════════════════════════════════════════════════════════════════════
function ProcedureForm({ initial, onSave, onClose }: {
  initial?: any; onSave(data: any): void; onClose(): void;
}) {
  const [form, setForm] = useState({
    name:        initial?.name        || '',
    description: initial?.description || '',
    category:    initial?.category    || '',
    province:    initial?.province    || 'Thanh Hóa',
    processingTime: initial?.processingTime || '',
    fee:         initial?.fee         || '',
    status:      initial?.status      || 'active',
  });
  const set = (k: string) => (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) =>
    setForm(f => ({ ...f, [k]: e.target.value }));

  return (
    <div className="fixed inset-0 z-50 flex items-end justify-center bg-black/40">
      <div className="bg-white rounded-t-2xl w-full max-w-lg p-5 space-y-3 max-h-[80vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-2">
          <h3 className="font-bold text-gray-800">{initial ? 'Sửa thủ tục' : 'Thêm thủ tục'}</h3>
          <button onClick={onClose}><X className="w-5 h-5 text-gray-400" /></button>
        </div>
        <div>
          <label className="text-xs text-gray-500">Tên thủ tục *</label>
          <Input value={form.name} onChange={set('name')} className="mt-1 h-10" />
        </div>
        <div>
          <label className="text-xs text-gray-500">Mô tả</label>
          <textarea value={form.description} onChange={set('description')}
            rows={3}
            className="mt-1 w-full border border-gray-200 rounded-md px-3 py-2 text-sm resize-none" />
        </div>
        {[
          { label: 'Lĩnh vực',        key: 'category' },
          { label: 'Tỉnh/TP',         key: 'province' },
          { label: 'Thời gian xử lý', key: 'processingTime' },
          { label: 'Lệ phí (VNĐ)',    key: 'fee' },
        ].map(f => (
          <div key={f.key}>
            <label className="text-xs text-gray-500">{f.label}</label>
            <Input value={(form as any)[f.key]} onChange={set(f.key)} className="mt-1 h-10" />
          </div>
        ))}
        <div>
          <label className="text-xs text-gray-500">Trạng thái</label>
          <select value={form.status} onChange={set('status')}
            className="mt-1 w-full h-10 border border-gray-200 rounded-md px-3 text-sm bg-white">
            <option value="active">Đang áp dụng</option>
            <option value="inactive">Tạm dừng</option>
          </select>
        </div>
        <div className="flex gap-3 pt-2">
          <Button variant="outline" className="flex-1" onClick={onClose}>Hủy</Button>
          <Button className="flex-1 bg-red-600 hover:bg-red-700 text-white"
            onClick={() => onSave(form)}>
            <Save className="w-4 h-4 mr-1.5" /> Lưu
          </Button>
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
    try {
      const r = await adminSvc.getProcedures({ q, limit: '20' });
      setItems(r.data || []);
    } catch { /* bỏ qua */ }
    finally { setLoading(false); }
  }, [q]);

  useEffect(() => { load(); }, [load]);

  const handleSave = async (data: any) => {
    try {
      if (editing) {
        await adminSvc.updateProcedure(editing.id, data);
        onToast('Đã cập nhật thủ tục', true);
      } else {
        await adminSvc.createProcedure(data);
        onToast('Đã thêm thủ tục', true);
      }
      setEditing(null); setAdding(false); load();
    } catch (e: any) { onToast(e.message, false); }
  };

  const handleDelete = async (id: string) => {
    try {
      await adminSvc.deleteProcedure(id);
      onToast('Đã xóa thủ tục', true); load();
    } catch (e: any) { onToast(e.message, false); }
    finally { setConfirm(null); }
  };

  return (
    <div className="space-y-3 pt-2">
      {(editing || adding) && (
        <ProcedureForm initial={editing} onSave={handleSave}
          onClose={() => { setEditing(null); setAdding(false); }} />
      )}
      {confirm && (
        <ConfirmDialog msg="Xóa thủ tục này?"
          onYes={() => handleDelete(confirm)} onNo={() => setConfirm(null)} />
      )}

      <div className="flex gap-2">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <Input value={q} onChange={e => setQ(e.target.value)}
            placeholder="Tìm thủ tục..." className="pl-9 h-10" />
        </div>
        <Button className="bg-red-600 hover:bg-red-700 text-white h-10 px-3"
          onClick={() => setAdding(true)}>
          <Plus className="w-4 h-4" />
        </Button>
      </div>

      {loading ? (
        <div className="flex justify-center py-8"><RefreshCw className="w-5 h-5 animate-spin text-gray-400" /></div>
      ) : (
        <div className="space-y-2">
          {items.map(p => (
            <div key={p.id}
              className="flex items-center justify-between bg-white rounded-xl px-4 py-3 shadow-sm">
              <div className="flex-1 min-w-0 mr-3">
                <p className="text-sm font-medium text-gray-800 truncate">{p.name}</p>
                <p className="text-xs text-gray-400 truncate">
                  {p.category}{p.processingTime ? ` • ${p.processingTime}` : ''}
                  {p.fee ? ` • ${Number(p.fee).toLocaleString()}đ` : ''}
                </p>
              </div>
              <div className="flex items-center gap-2 flex-shrink-0">
                <Badge className={`text-xs ${p.status === 'active' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'}`}>
                  {p.status === 'active' ? 'Đang áp dụng' : 'Tạm dừng'}
                </Badge>
                <button className="text-gray-400 hover:text-blue-600 p-1"
                  onClick={() => setEditing(p)}><Pencil className="w-4 h-4" /></button>
                <button className="text-gray-400 hover:text-red-500 p-1"
                  onClick={() => setConfirm(p.id)}><Trash2 className="w-4 h-4" /></button>
              </div>
            </div>
          ))}
          {items.length === 0 && (
            <p className="text-center text-gray-400 py-8 text-sm">Không có dữ liệu</p>
          )}
        </div>
      )}
    </div>
  );
}

// ════════════════════════════════════════════════════════════════════════════════
// TAB: HỒ SƠ
// ════════════════════════════════════════════════════════════════════════════════
const APP_STATUS_OPTIONS = [
  { value: '', label: 'Tất cả' },
  { value: 'submitted',        label: 'Đã nộp' },
  { value: 'in_review',     label: 'Đang xét' },
  { value: 'more_info',   label: 'Cần bổ sung' },
  { value: 'approved',         label: 'Đã duyệt' },
  { value: 'rejected',         label: 'Từ chối' },
];
const APP_STATUS_COLOR: Record<string, string> = {
  submitted:      'bg-blue-100 text-blue-700',
  in_review:   'bg-yellow-100 text-yellow-700',
  more_info: 'bg-orange-100 text-orange-700',
  approved:       'bg-green-100 text-green-700',
  rejected:       'bg-red-100 text-red-700',
};
const APP_STATUS_LABEL: Record<string, string> = {
  submitted:      'Đã nộp',
  in_review:   'Đang xét',
  more_info: 'Cần bổ sung',
  approved:       'Đã duyệt',
  rejected:       'Từ chối',
};

function ReviewModal({ app, onClose, onDone }: {
  app: any; onClose(): void; onDone(action: string, note: string): void;
}) {
  const [action, setAction] = useState('');
  const [note,   setNote]   = useState('');
  return (
    <div className="fixed inset-0 z-50 flex items-end justify-center bg-black/40">
      <div className="bg-white rounded-t-2xl w-full max-w-lg p-5 space-y-4 max-h-[80vh] overflow-y-auto">
        <div className="flex items-center justify-between">
          <h3 className="font-bold text-gray-800">Xét duyệt hồ sơ</h3>
          <button onClick={onClose}><X className="w-5 h-5 text-gray-400" /></button>
        </div>
        <div className="bg-gray-50 rounded-xl p-3 text-sm space-y-1">
          <p className="font-medium text-gray-800">{app.procedureName || app.procedureId}</p>
          <p className="text-gray-500">Người nộp: {app.applicantName || app.applicantId}</p>
          <p className="text-gray-500">Mã: {app.id}</p>
        </div>
        <div className="grid grid-cols-3 gap-2">
          {[
            { val: 'approve',          label: 'Duyệt',       icon: ThumbsUp,       cls: 'border-green-400 text-green-700 bg-green-50' },
            { val: 'reject',           label: 'Từ chối',     icon: ThumbsDown,     cls: 'border-red-400 text-red-700 bg-red-50' },
            { val: 'request_more_info',label: 'Yêu cầu bổ sung', icon: MessageSquare, cls: 'border-orange-400 text-orange-700 bg-orange-50' },
          ].map(o => (
            <button key={o.val}
              className={`border-2 rounded-xl p-3 flex flex-col items-center gap-1 text-xs font-medium transition-all
                ${action === o.val ? o.cls + ' ring-2 ring-offset-1' : 'border-gray-200 text-gray-600'}`}
              onClick={() => setAction(o.val)}>
              <o.icon className="w-5 h-5" />
              {o.label}
            </button>
          ))}
        </div>
        <div>
          <label className="text-xs text-gray-500">Ghi chú</label>
          <textarea value={note} onChange={e => setNote(e.target.value)}
            rows={3} placeholder="Nhập ghi chú (nếu có)..."
            className="mt-1 w-full border border-gray-200 rounded-md px-3 py-2 text-sm resize-none" />
        </div>
        <div className="flex gap-3">
          <Button variant="outline" className="flex-1" onClick={onClose}>Hủy</Button>
          <Button className="flex-1 bg-red-600 hover:bg-red-700 text-white"
            disabled={!action}
            onClick={() => action && onDone(action, note)}>
            Xác nhận
          </Button>
        </div>
      </div>
    </div>
  );
}

function ApplicationsTab({ onToast }: { onToast(msg: string, ok: boolean): void }) {
  const [items,    setItems]    = useState<any[]>([]);
  const [loading,  setLoading]  = useState(true);
  const [q,        setQ]        = useState('');
  const [status,   setStatus]   = useState('');
  const [page,     setPage]     = useState(1);
  const [total,    setTotal]    = useState(0);
  const [reviewing,setReviewing]= useState<any>(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const params: Record<string, string> = { page: String(page), limit: '15' };
      if (q)      params.q      = q;
      if (status) params.status = status;
      const r = await adminSvc.getApplications(params);
      setItems(r.data || []);
      setTotal(r.pagination?.total || r.total || 0);
    } catch { /* bỏ qua */ }
    finally { setLoading(false); }
  }, [q, status, page]);

  useEffect(() => { load(); }, [load]);

  const handleReview = async (action: string, note: string) => {
    if (!reviewing) return;
    try {
      await adminSvc.reviewApplication(reviewing.id, action, note);
      onToast('Đã cập nhật trạng thái hồ sơ', true);
      setReviewing(null);
      load();
    } catch (e: any) { onToast(e.message, false); }
  };

  return (
    <div className="space-y-3 pt-2">
      {reviewing && (
        <ReviewModal app={reviewing}
          onClose={() => setReviewing(null)}
          onDone={handleReview} />
      )}

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
        <input value={q} onChange={e => { setQ(e.target.value); setPage(1); }}
          placeholder="Tìm mã hồ sơ, tên, CCCD..."
          className="w-full pl-9 pr-3 h-10 border border-gray-200 rounded-md text-sm bg-white" />
      </div>

      {/* Status filter */}
      <div className="flex gap-1.5 overflow-x-auto pb-1 no-scrollbar">
        {APP_STATUS_OPTIONS.map(o => (
          <button key={o.value}
            onClick={() => { setStatus(o.value); setPage(1); }}
            className={`flex-shrink-0 px-3 py-1.5 rounded-full text-xs font-medium transition-all
              ${status === o.value
                ? 'bg-red-600 text-white'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'}`}>
            {o.label}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="flex justify-center py-8"><RefreshCw className="w-5 h-5 animate-spin text-gray-400" /></div>
      ) : items.length === 0 ? (
        <p className="text-center text-gray-400 py-8 text-sm">Không có hồ sơ</p>
      ) : (
        <div className="space-y-2">
          {items.map(app => (
            <div key={app.id}
              className="bg-white rounded-xl px-4 py-3 shadow-sm">
              <div className="flex items-start justify-between gap-2">
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-800 truncate">
                    {app.procedureName || app.procedureId || 'Hồ sơ'}
                  </p>
                  <p className="text-xs text-gray-400 truncate mt-0.5">
                    {app.applicantName || app.applicantId} • {app.id}
                  </p>
                  <p className="text-xs text-gray-400 mt-0.5">
                    {app.createdAt ? new Date(app.createdAt).toLocaleDateString('vi-VN') : ''}
                  </p>
                </div>
                <div className="flex items-center gap-2 flex-shrink-0">
                  <Badge className={`text-xs ${APP_STATUS_COLOR[app.currentStatus] || 'bg-gray-100 text-gray-600'}`}>
                    {APP_STATUS_LABEL[app.currentStatus] || app.currentStatus}
                  </Badge>
                  <button className="text-gray-400 hover:text-blue-600 p-1"
                    onClick={() => setReviewing(app)}>
                    <ClipboardList className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {total > 15 && (
        <div className="flex justify-center gap-3 pt-1">
          <Button variant="outline" size="sm" disabled={page === 1}
            onClick={() => setPage(p => p - 1)}>Trước</Button>
          <span className="text-xs text-gray-500 self-center">
            {page} / {Math.ceil(total / 15)}
          </span>
          <Button variant="outline" size="sm" disabled={page >= Math.ceil(total / 15)}
            onClick={() => setPage(p => p + 1)}>Sau</Button>
        </div>
      )}
    </div>
  );
}

// ════════════════════════════════════════════════════════════════════════════════
// TAB: LỊCH HẸN
// ════════════════════════════════════════════════════════════════════════════════
const APT_STATUS_COLOR: Record<string, string> = {
  pending:   'bg-yellow-100 text-yellow-700',
  completed: 'bg-green-100 text-green-700',
  cancelled: 'bg-gray-100 text-gray-500',
};
const APT_STATUS_LABEL: Record<string, string> = {
  pending:   'Chờ đến',
  completed: 'Đã đến',
  cancelled: 'Đã hủy',
};

function AppointmentsTab() {
  const [items,   setItems]   = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter,  setFilter]  = useState('');
  const [q,       setQ]       = useState('');

  useEffect(() => {
    adminSvc.getAppointments()
      .then(r => setItems(r.appointments || r.data || []))
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
    <div className="space-y-3 pt-2">
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
        <input value={q} onChange={e => setQ(e.target.value)}
          placeholder="Tìm tên, SĐT, mã lịch hẹn..."
          className="w-full pl-9 pr-3 h-10 border border-gray-200 rounded-md text-sm bg-white" />
      </div>

      <div className="flex gap-1.5">
        {[
          { value: '',          label: 'Tất cả' },
          { value: 'pending',   label: 'Chờ đến' },
          { value: 'completed', label: 'Đã đến' },
          { value: 'cancelled', label: 'Đã hủy' },
        ].map(o => (
          <button key={o.value}
            onClick={() => setFilter(o.value)}
            className={`px-3 py-1.5 rounded-full text-xs font-medium transition-all
              ${filter === o.value
                ? 'bg-red-600 text-white'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'}`}>
            {o.label}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="flex justify-center py-8"><RefreshCw className="w-5 h-5 animate-spin text-gray-400" /></div>
      ) : displayed.length === 0 ? (
        <p className="text-center text-gray-400 py-8 text-sm">Không có lịch hẹn</p>
      ) : (
        <div className="space-y-2">
          {displayed.map(a => (
            <div key={a.id} className="bg-white rounded-xl px-4 py-3 shadow-sm">
              <div className="flex items-start justify-between gap-2">
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-800 truncate">{a.fullName || 'Không rõ'}</p>
                  <p className="text-xs text-gray-400 mt-0.5">{a.phone} • {a.date} {a.time}</p>
                  <p className="text-xs text-gray-400 mt-0.5 truncate">{a.serviceCode || a.agencyId}</p>
                </div>
                <Badge className={`text-xs flex-shrink-0 ${APT_STATUS_COLOR[a.status] || 'bg-gray-100 text-gray-600'}`}>
                  {APT_STATUS_LABEL[a.status] || a.status}
                </Badge>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// ════════════════════════════════════════════════════════════════════════════════
// TAB: CHATBOT CONFIG
// ════════════════════════════════════════════════════════════════════════════════

// ── Persona ───────────────────────────────────────────────────────────────────
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
    <div className="fixed inset-0 z-50 flex items-end justify-center bg-black/40">
      <div className="bg-white rounded-t-2xl w-full max-w-lg p-5 space-y-3 max-h-[85vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-1">
          <h3 className="font-bold text-gray-800">{initial ? 'Sửa Persona' : 'Thêm Persona'}</h3>
          <button onClick={onClose}><X className="w-5 h-5 text-gray-400" /></button>
        </div>
        <div>
          <label className="text-xs text-gray-500">Tên *</label>
          <Input value={form.name} onChange={set('name')} className="mt-1 h-10" placeholder="VD: Trợ lý Dịch vụ Công" />
        </div>
        <div>
          <label className="text-xs text-gray-500">Mô tả</label>
          <Input value={form.description} onChange={set('description')} className="mt-1 h-10" />
        </div>
        <div>
          <label className="text-xs text-gray-500">Phong cách (tone)</label>
          <select value={form.tone} onChange={set('tone')}
            className="mt-1 w-full h-10 border border-gray-200 rounded-md px-3 text-sm bg-white">
            <option value="formal">Trang trọng (formal)</option>
            <option value="friendly">Thân thiện (friendly)</option>
            <option value="neutral">Trung lập (neutral)</option>
          </select>
        </div>
        <div>
          <label className="text-xs text-gray-500">Lời chào mở đầu</label>
          <textarea value={form.greeting} onChange={set('greeting')} rows={3}
            className="mt-1 w-full border border-gray-200 rounded-md px-3 py-2 text-sm resize-none" />
        </div>
        <div>
          <label className="text-xs text-gray-500">Lời tạm biệt</label>
          <Input value={form.farewell} onChange={set('farewell')} className="mt-1 h-10" />
        </div>
        <div className="flex gap-3 pt-2">
          <Button variant="outline" className="flex-1" onClick={onClose}>Hủy</Button>
          <Button className="flex-1 bg-red-600 hover:bg-red-700 text-white"
            onClick={() => onSave(form)}>
            <Save className="w-4 h-4 mr-1.5" /> Lưu
          </Button>
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
    try {
      const r = await adminSvc.getChatbotPersonas();
      setItems(r.data || []);
    } catch { }
    finally { setLoading(false); }
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
    try {
      await adminSvc.activateChatbotPersona(id);
      onToast('Đã kích hoạt persona', true);
      load();
    } catch (e: any) { onToast(e.message, false); }
  };

  const handleDelete = async (id: string) => {
    try {
      await adminSvc.deleteChatbotPersona(id);
      onToast('Đã xóa persona', true); load();
    } catch (e: any) { onToast(e.message, false); }
    finally { setConfirm(null); }
  };

  const handleSeed = async () => {
    try {
      await adminSvc.seedChatbotDefaults();
      onToast('Đã seed dữ liệu mặc định', true); load();
    } catch (e: any) { onToast(e.message, false); }
  };

  return (
    <div className="space-y-2">
      {(editing || adding) && (
        <PersonaForm initial={editing} onSave={handleSave}
          onClose={() => { setEditing(null); setAdding(false); }} />
      )}
      {confirm && (
        <ConfirmDialog msg="Xóa persona này?"
          onYes={() => handleDelete(confirm)} onNo={() => setConfirm(null)} />
      )}
      <div className="flex gap-2">
        <Button className="bg-red-600 hover:bg-red-700 text-white h-9 px-3 text-xs flex-1"
          onClick={() => setAdding(true)}>
          <Plus className="w-3.5 h-3.5 mr-1" /> Thêm Persona
        </Button>
        <Button variant="outline" className="h-9 px-3 text-xs"
          onClick={handleSeed} title="Tạo data mặc định">
          <Zap className="w-3.5 h-3.5 mr-1" /> Seed mặc định
        </Button>
      </div>
      {loading ? (
        <div className="flex justify-center py-6"><RefreshCw className="w-5 h-5 animate-spin text-gray-400" /></div>
      ) : items.length === 0 ? (
        <p className="text-center text-gray-400 py-6 text-sm">Chưa có persona</p>
      ) : (
        <div className="space-y-2">
          {items.map(p => (
            <div key={p.id}
              className={`bg-white rounded-xl px-4 py-3 shadow-sm border-l-4 ${p.is_active ? 'border-green-500' : 'border-transparent'}`}>
              <div className="flex items-start justify-between gap-2">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <Bot className="w-4 h-4 text-gray-400 flex-shrink-0" />
                    <p className="text-sm font-semibold text-gray-800 truncate">{p.name}</p>
                    {p.is_active && <Badge className="text-[10px] bg-green-100 text-green-700">Active</Badge>}
                  </div>
                  <p className="text-xs text-gray-400 mt-0.5 truncate pl-6">{p.description || p.tone}</p>
                </div>
                <div className="flex items-center gap-1.5 flex-shrink-0">
                  {!p.is_active && (
                    <button className="text-xs text-green-600 font-medium px-2 py-1 rounded-lg hover:bg-green-50 transition-colors"
                      onClick={() => handleActivate(p.id)}>Kích hoạt</button>
                  )}
                  <button className="text-gray-400 hover:text-blue-600 p-1"
                    onClick={() => setEditing(p)}><Pencil className="w-3.5 h-3.5" /></button>
                  <button className="text-gray-400 hover:text-red-500 p-1"
                    onClick={() => setConfirm(p.id)}><Trash2 className="w-3.5 h-3.5" /></button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// ── Prompts ───────────────────────────────────────────────────────────────────
const PROMPT_TYPES = [
  { value: '',               label: 'Tất cả' },
  { value: 'system',         label: 'System' },
  { value: 'nlu',            label: 'NLU' },
  { value: 'rag_answer',     label: 'RAG Answer' },
  { value: 'dialog_confirm', label: 'Xác nhận' },
  { value: 'error_fallback', label: 'Fallback' },
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
    <div className="fixed inset-0 z-50 flex items-end justify-center bg-black/40">
      <div className="bg-white rounded-t-2xl w-full max-w-lg p-5 space-y-3 max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-1">
          <h3 className="font-bold text-gray-800">{initial ? 'Sửa Prompt' : 'Thêm Prompt'}</h3>
          <button onClick={onClose}><X className="w-5 h-5 text-gray-400" /></button>
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="text-xs text-gray-500">Loại *</label>
            <select value={form.type} onChange={set('type')}
              className="mt-1 w-full h-10 border border-gray-200 rounded-md px-3 text-sm bg-white">
              {PROMPT_TYPES.slice(1).map(t => (
                <option key={t.value} value={t.value}>{t.label}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="text-xs text-gray-500">Tên *</label>
            <Input value={form.name} onChange={set('name')} className="mt-1 h-10" />
          </div>
        </div>
        <div>
          <label className="text-xs text-gray-500">Nội dung prompt *</label>
          <textarea value={form.content} onChange={set('content')} rows={10}
            className="mt-1 w-full border border-gray-200 rounded-md px-3 py-2 text-xs font-mono resize-y" />
        </div>
        <div>
          <label className="text-xs text-gray-500">Mô tả</label>
          <Input value={form.description} onChange={set('description')} className="mt-1 h-10" />
        </div>
        <div className="flex gap-3 pt-2">
          <Button variant="outline" className="flex-1" onClick={onClose}>Hủy</Button>
          <Button className="flex-1 bg-red-600 hover:bg-red-700 text-white"
            onClick={() => onSave(form)}>
            <Save className="w-4 h-4 mr-1.5" /> Lưu
          </Button>
        </div>
      </div>
    </div>
  );
}

function PromptsSection({ onToast }: { onToast(msg: string, ok: boolean): void }) {
  const [items,    setItems]    = useState<any[]>([]);
  const [loading,  setLoading]  = useState(true);
  const [typeFilter, setTypeFilter] = useState('');
  const [editing,  setEditing]  = useState<any>(null);
  const [adding,   setAdding]   = useState(false);
  const [confirm,  setConfirm]  = useState<string | null>(null);
  const [expanded, setExpanded] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const r = await adminSvc.getChatbotPrompts(typeFilter || undefined);
      setItems(r.data || []);
    } catch { }
    finally { setLoading(false); }
  }, [typeFilter]);
  useEffect(() => { load(); }, [load]);

  const handleSave = async (data: any) => {
    try {
      if (editing) { await adminSvc.updateChatbotPrompt(editing.id, data); onToast('Đã cập nhật prompt', true); }
      else         { await adminSvc.createChatbotPrompt(data);             onToast('Đã thêm prompt', true); }
      setEditing(null); setAdding(false); load();
    } catch (e: any) { onToast(e.message, false); }
  };

  const handleDelete = async (id: string) => {
    try {
      await adminSvc.deleteChatbotPrompt(id);
      onToast('Đã xóa prompt', true); load();
    } catch (e: any) { onToast(e.message, false); }
    finally { setConfirm(null); }
  };

  const TYPE_COLOR: Record<string, string> = {
    system:         'bg-purple-100 text-purple-700',
    nlu:            'bg-blue-100 text-blue-700',
    rag_answer:     'bg-indigo-100 text-indigo-700',
    dialog_confirm: 'bg-orange-100 text-orange-700',
    error_fallback: 'bg-red-100 text-red-700',
  };

  return (
    <div className="space-y-2">
      {(editing || adding) && (
        <PromptForm initial={editing} onSave={handleSave}
          onClose={() => { setEditing(null); setAdding(false); }} />
      )}
      {confirm && (
        <ConfirmDialog msg="Xóa prompt này?"
          onYes={() => handleDelete(confirm)} onNo={() => setConfirm(null)} />
      )}
      <div className="flex items-center gap-2">
        <div className="flex gap-1 overflow-x-auto flex-1 pb-0.5 no-scrollbar">
          {PROMPT_TYPES.map(t => (
            <button key={t.value}
              onClick={() => setTypeFilter(t.value)}
              className={`flex-shrink-0 px-2.5 py-1 rounded-full text-[10px] font-medium transition-all
                ${typeFilter === t.value ? 'bg-red-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'}`}>
              {t.label}
            </button>
          ))}
        </div>
        <Button className="bg-red-600 hover:bg-red-700 text-white h-8 px-2.5 text-xs flex-shrink-0"
          onClick={() => setAdding(true)}>
          <Plus className="w-3.5 h-3.5" />
        </Button>
      </div>
      {loading ? (
        <div className="flex justify-center py-6"><RefreshCw className="w-5 h-5 animate-spin text-gray-400" /></div>
      ) : items.length === 0 ? (
        <p className="text-center text-gray-400 py-6 text-sm">Chưa có prompt</p>
      ) : (
        <div className="space-y-2">
          {items.map(p => (
            <div key={p.id} className="bg-white rounded-xl shadow-sm overflow-hidden">
              <div className="flex items-center justify-between px-4 py-3">
                <div className="flex-1 min-w-0 mr-2">
                  <div className="flex items-center gap-2 flex-wrap">
                    <Badge className={`text-[10px] ${TYPE_COLOR[p.type] || 'bg-gray-100 text-gray-600'}`}>{p.type}</Badge>
                    <p className="text-sm font-medium text-gray-800 truncate">{p.name}</p>
                  </div>
                  {p.description && <p className="text-xs text-gray-400 mt-0.5 truncate">{p.description}</p>}
                </div>
                <div className="flex items-center gap-1 flex-shrink-0">
                  <button className="text-gray-400 hover:text-gray-600 p-1"
                    onClick={() => setExpanded(expanded === p.id ? null : p.id)}>
                    <Eye className="w-3.5 h-3.5" />
                  </button>
                  <button className="text-gray-400 hover:text-blue-600 p-1"
                    onClick={() => setEditing(p)}><Pencil className="w-3.5 h-3.5" /></button>
                  <button className="text-gray-400 hover:text-red-500 p-1"
                    onClick={() => setConfirm(p.id)}><Trash2 className="w-3.5 h-3.5" /></button>
                </div>
              </div>
              {expanded === p.id && (
                <div className="px-4 pb-3 border-t border-gray-100">
                  <pre className="text-[10px] text-gray-600 bg-gray-50 rounded-lg p-3 mt-2 whitespace-pre-wrap font-mono overflow-x-auto max-h-48">
                    {p.content}
                  </pre>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// ── Rules ─────────────────────────────────────────────────────────────────────
const RULE_CATEGORIES = [
  { value: '',            label: 'Tất cả' },
  { value: 'behavior',   label: 'Hành vi' },
  { value: 'restriction',label: 'Giới hạn' },
  { value: 'format',     label: 'Định dạng' },
  { value: 'greeting',   label: 'Lời chào' },
  { value: 'escalation', label: 'Chuyển tiếp' },
];

function RuleForm({ initial, onSave, onClose }: {
  initial?: any; onSave(data: any): void; onClose(): void;
}) {
  const [form, setForm] = useState({
    category: initial?.category  || 'behavior',
    rule_text: initial?.rule_text || '',
    priority: initial?.priority  || 0,
  });
  const set = (k: string) => (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) =>
    setForm(f => ({ ...f, [k]: k === 'priority' ? Number(e.target.value) : e.target.value }));
  return (
    <div className="fixed inset-0 z-50 flex items-end justify-center bg-black/40">
      <div className="bg-white rounded-t-2xl w-full max-w-lg p-5 space-y-3 max-h-[80vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-1">
          <h3 className="font-bold text-gray-800">{initial ? 'Sửa Rule' : 'Thêm Rule'}</h3>
          <button onClick={onClose}><X className="w-5 h-5 text-gray-400" /></button>
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="text-xs text-gray-500">Loại</label>
            <select value={form.category} onChange={set('category')}
              className="mt-1 w-full h-10 border border-gray-200 rounded-md px-3 text-sm bg-white">
              {RULE_CATEGORIES.slice(1).map(c => (
                <option key={c.value} value={c.value}>{c.label}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="text-xs text-gray-500">Độ ưu tiên</label>
            <Input type="number" value={form.priority} onChange={set('priority')} className="mt-1 h-10" />
          </div>
        </div>
        <div>
          <label className="text-xs text-gray-500">Nội dung rule *</label>
          <textarea value={form.rule_text} onChange={set('rule_text')} rows={4}
            className="mt-1 w-full border border-gray-200 rounded-md px-3 py-2 text-sm resize-none"
            placeholder="VD: Chỉ trả lời các câu hỏi liên quan đến dịch vụ công." />
        </div>
        <div className="flex gap-3 pt-2">
          <Button variant="outline" className="flex-1" onClick={onClose}>Hủy</Button>
          <Button className="flex-1 bg-red-600 hover:bg-red-700 text-white"
            onClick={() => onSave(form)}>
            <Save className="w-4 h-4 mr-1.5" /> Lưu
          </Button>
        </div>
      </div>
    </div>
  );
}

function RulesSection({ onToast }: { onToast(msg: string, ok: boolean): void }) {
  const [items,      setItems]      = useState<any[]>([]);
  const [loading,    setLoading]    = useState(true);
  const [catFilter,  setCatFilter]  = useState('');
  const [editing,    setEditing]    = useState<any>(null);
  const [adding,     setAdding]     = useState(false);
  const [confirm,    setConfirm]    = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const r = await adminSvc.getChatbotRules(catFilter || undefined);
      setItems(r.data || []);
    } catch { }
    finally { setLoading(false); }
  }, [catFilter]);
  useEffect(() => { load(); }, [load]);

  const handleSave = async (data: any) => {
    try {
      if (editing) { await adminSvc.updateChatbotRule(editing.id, data); onToast('Đã cập nhật rule', true); }
      else         { await adminSvc.createChatbotRule(data);             onToast('Đã thêm rule', true); }
      setEditing(null); setAdding(false); load();
    } catch (e: any) { onToast(e.message, false); }
  };

  const handleDelete = async (id: string) => {
    try {
      await adminSvc.deleteChatbotRule(id);
      onToast('Đã xóa rule', true); load();
    } catch (e: any) { onToast(e.message, false); }
    finally { setConfirm(null); }
  };

  const handleToggle = async (rule: any) => {
    try {
      await adminSvc.updateChatbotRule(rule.id, { is_active: !rule.is_active });
      onToast(rule.is_active ? 'Đã tắt rule' : 'Đã bật rule', true);
      load();
    } catch (e: any) { onToast(e.message, false); }
  };

  const CAT_COLOR: Record<string, string> = {
    behavior:    'bg-blue-100 text-blue-700',
    restriction: 'bg-red-100 text-red-700',
    format:      'bg-yellow-100 text-yellow-700',
    greeting:    'bg-green-100 text-green-700',
    escalation:  'bg-orange-100 text-orange-700',
  };

  return (
    <div className="space-y-2">
      {(editing || adding) && (
        <RuleForm initial={editing} onSave={handleSave}
          onClose={() => { setEditing(null); setAdding(false); }} />
      )}
      {confirm && (
        <ConfirmDialog msg="Xóa rule này?"
          onYes={() => handleDelete(confirm)} onNo={() => setConfirm(null)} />
      )}
      <div className="flex items-center gap-2">
        <div className="flex gap-1 overflow-x-auto flex-1 pb-0.5 no-scrollbar">
          {RULE_CATEGORIES.map(c => (
            <button key={c.value}
              onClick={() => setCatFilter(c.value)}
              className={`flex-shrink-0 px-2.5 py-1 rounded-full text-[10px] font-medium transition-all
                ${catFilter === c.value ? 'bg-red-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'}`}>
              {c.label}
            </button>
          ))}
        </div>
        <Button className="bg-red-600 hover:bg-red-700 text-white h-8 px-2.5 text-xs flex-shrink-0"
          onClick={() => setAdding(true)}>
          <Plus className="w-3.5 h-3.5" />
        </Button>
      </div>
      {loading ? (
        <div className="flex justify-center py-6"><RefreshCw className="w-5 h-5 animate-spin text-gray-400" /></div>
      ) : items.length === 0 ? (
        <p className="text-center text-gray-400 py-6 text-sm">Chưa có rule</p>
      ) : (
        <div className="space-y-2">
          {items.map(r => (
            <div key={r.id}
              className={`bg-white rounded-xl px-4 py-3 shadow-sm ${!r.is_active ? 'opacity-50' : ''}`}>
              <div className="flex items-start gap-2">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <Badge className={`text-[10px] ${CAT_COLOR[r.category] || 'bg-gray-100 text-gray-600'}`}>
                      {r.category}
                    </Badge>
                    <span className="text-[10px] text-gray-400">p={r.priority}</span>
                    {!r.is_active && <span className="text-[10px] text-gray-400 italic">off</span>}
                  </div>
                  <p className="text-xs text-gray-700 leading-relaxed">{r.rule_text}</p>
                </div>
                <div className="flex items-center gap-1 flex-shrink-0 ml-1">
                  <button
                    className={`p-1 rounded transition-colors ${r.is_active ? 'text-green-500 hover:text-green-700' : 'text-gray-300 hover:text-gray-500'}`}
                    onClick={() => handleToggle(r)} title={r.is_active ? 'Tắt' : 'Bật'}>
                    <ShieldAlert className="w-3.5 h-3.5" />
                  </button>
                  <button className="text-gray-400 hover:text-blue-600 p-1"
                    onClick={() => setEditing(r)}><Pencil className="w-3.5 h-3.5" /></button>
                  <button className="text-gray-400 hover:text-red-500 p-1"
                    onClick={() => setConfirm(r.id)}><Trash2 className="w-3.5 h-3.5" /></button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// ── ChatbotTab wrapper ────────────────────────────────────────────────────────
function ChatbotTab({ onToast }: { onToast(msg: string, ok: boolean): void }) {
  const [section, setSection] = useState<'personas' | 'prompts' | 'rules'>('personas');

  const handleInvalidateCache = async () => {
    try {
      await adminSvc.invalidateChatbotCache();
      onToast('Cache NLU đã được xóa', true);
    } catch (e: any) { onToast(e.message, false); }
  };

  return (
    <div className="space-y-3 pt-2">
      <div className="flex items-center justify-between">
        <div className="flex gap-1.5">
          {[
            { key: 'personas', label: 'Persona' },
            { key: 'prompts',  label: 'Prompts' },
            { key: 'rules',    label: 'Rules' },
          ].map(s => (
            <button key={s.key}
              onClick={() => setSection(s.key as typeof section)}
              className={`px-3 py-1.5 rounded-full text-xs font-medium transition-all
                ${section === s.key ? 'bg-red-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'}`}>
              {s.label}
            </button>
          ))}
        </div>
        <button
          onClick={handleInvalidateCache}
          className="text-[10px] text-gray-400 hover:text-orange-600 flex items-center gap-1 transition-colors"
          title="Xóa cache prompt NLU">
          <RefreshCw className="w-3 h-3" /> Xóa cache
        </button>
      </div>

      {section === 'personas' && <PersonasSection onToast={onToast} />}
      {section === 'prompts'  && <PromptsSection  onToast={onToast} />}
      {section === 'rules'    && <RulesSection     onToast={onToast} />}
    </div>
  );
}

// ════════════════════════════════════════════════════════════════════════════════
// MAIN COMPONENT
// ════════════════════════════════════════════════════════════════════════════════
export function AdminDashboardScreen({ onNavigate }: Props) {
  const [toast, setToast] = useState<{ msg: string; ok: boolean } | null>(null);

  const showToast = useCallback((msg: string, ok: boolean) => {
    setToast({ msg, ok });
    setTimeout(() => setToast(null), 3000);
  }, []);

  return (
    <div className="min-h-screen bg-gray-50 pb-6">
      {toast && <Toast text={toast.msg} ok={toast.ok} />}

      {/* Header */}
      <div className="bg-red-700 text-white px-4 pt-12 pb-4 flex items-center gap-3">
        <Button variant="ghost" size="sm"
          className="text-white hover:bg-red-800 p-2"
          onClick={() => onNavigate('home')}>
          <ChevronLeft className="w-5 h-5" />
        </Button>
        <div>
          <h1 className="text-base font-bold">Quản trị hệ thống</h1>
          <p className="text-xs text-red-200">Admin Dashboard</p>
        </div>
      </div>

      <div className="px-4 pt-4">
        <Tabs defaultValue="overview">
          <div className="overflow-x-auto no-scrollbar mb-4">
            <TabsList className="flex w-max min-w-full h-10">
              <TabsTrigger value="overview"      className="text-[10px] px-2.5 flex-shrink-0">Tổng quan</TabsTrigger>
              <TabsTrigger value="users"         className="text-[10px] px-2.5 flex-shrink-0">Tài khoản</TabsTrigger>
              <TabsTrigger value="locations"     className="text-[10px] px-2.5 flex-shrink-0">Địa điểm</TabsTrigger>
              <TabsTrigger value="procedures"    className="text-[10px] px-2.5 flex-shrink-0">Thủ tục</TabsTrigger>
              <TabsTrigger value="applications"  className="text-[10px] px-2.5 flex-shrink-0">Hồ sơ</TabsTrigger>
              <TabsTrigger value="appointments"  className="text-[10px] px-2.5 flex-shrink-0">Lịch hẹn</TabsTrigger>
              <TabsTrigger value="chatbot"       className="text-[10px] px-2.5 flex-shrink-0 gap-1">
                <Bot className="w-3 h-3" /> Chatbot
              </TabsTrigger>
            </TabsList>
          </div>

          <TabsContent value="overview">
            <OverviewTab />
          </TabsContent>
          <TabsContent value="users">
            <UsersTab onToast={showToast} />
          </TabsContent>
          <TabsContent value="locations">
            <LocationsTab onToast={showToast} />
          </TabsContent>
          <TabsContent value="procedures">
            <ProceduresTab onToast={showToast} />
          </TabsContent>
          <TabsContent value="applications">
            <ApplicationsTab onToast={showToast} />
          </TabsContent>
          <TabsContent value="appointments">
            <AppointmentsTab />
          </TabsContent>
          <TabsContent value="chatbot">
            <ChatbotTab onToast={showToast} />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
