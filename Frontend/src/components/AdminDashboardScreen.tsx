/**
 * AdminDashboardScreen — Panel quản trị
 * Tab: Tổng quan | Tài khoản | Địa điểm | Thủ tục
 */
import React, { useState, useEffect, useCallback } from 'react';
import {
  ChevronLeft, Users, MapPin, FileText, BarChart3,
  Plus, Pencil, Trash2, Search, RefreshCw, AlertCircle,
  CheckCircle, X, Save, Eye, EyeOff, Calendar, ClipboardList,
  ThumbsUp, ThumbsDown, MessageSquare,
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
  { value: 'under_review',     label: 'Đang xét' },
  { value: 'need_more_info',   label: 'Cần bổ sung' },
  { value: 'approved',         label: 'Đã duyệt' },
  { value: 'rejected',         label: 'Từ chối' },
];
const APP_STATUS_COLOR: Record<string, string> = {
  submitted:      'bg-blue-100 text-blue-700',
  under_review:   'bg-yellow-100 text-yellow-700',
  need_more_info: 'bg-orange-100 text-orange-700',
  approved:       'bg-green-100 text-green-700',
  rejected:       'bg-red-100 text-red-700',
};
const APP_STATUS_LABEL: Record<string, string> = {
  submitted:      'Đã nộp',
  under_review:   'Đang xét',
  need_more_info: 'Cần bổ sung',
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
          <TabsList className="grid grid-cols-6 w-full h-10 mb-4">
            <TabsTrigger value="overview"      className="text-[10px] px-1">Tổng quan</TabsTrigger>
            <TabsTrigger value="users"         className="text-[10px] px-1">Tài khoản</TabsTrigger>
            <TabsTrigger value="locations"     className="text-[10px] px-1">Địa điểm</TabsTrigger>
            <TabsTrigger value="procedures"    className="text-[10px] px-1">Thủ tục</TabsTrigger>
            <TabsTrigger value="applications"  className="text-[10px] px-1">Hồ sơ</TabsTrigger>
            <TabsTrigger value="appointments"  className="text-[10px] px-1">Lịch hẹn</TabsTrigger>
          </TabsList>

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
        </Tabs>
      </div>
    </div>
  );
}
