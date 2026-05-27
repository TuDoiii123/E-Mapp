import React, { useEffect, useMemo, useState, useCallback } from 'react';
import { appointmentsAPI, Appointment, CreateAppointmentRequest } from '../../services/appointmentsApi';
import { servicesAPI } from '../../services/servicesApi';
import {
  ArrowLeft, ChevronLeft, ChevronRight, Plus, X,
  CalendarX2, CheckCircle, AlertCircle, CalendarDays,
  MessageSquarePlus, Search, Image, CalendarCheck,
  Bell, User, Phone, Headphones,
} from 'lucide-react';

interface AppointmentCalendarScreenProps {
  onNavigate: (screen: string, params?: any) => void;
}

const VI_MONTHS = [
  'Tháng 01', 'Tháng 02', 'Tháng 03', 'Tháng 04', 'Tháng 05', 'Tháng 06',
  'Tháng 07', 'Tháng 08', 'Tháng 09', 'Tháng 10', 'Tháng 11', 'Tháng 12',
];
const DOW_LABELS = ['Th 2', 'Th 3', 'Th 4', 'Th 5', 'Th 6', 'Th 7', 'CN'];

function buildCalendarDays(year: number, month: number) {
  const firstDow = new Date(year, month, 1).getDay();
  const offset = firstDow === 0 ? 6 : firstDow - 1;
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  const daysInPrev  = new Date(year, month, 0).getDate();

  const days: { day: number; current: boolean }[] = [];
  for (let i = offset - 1; i >= 0; i--)
    days.push({ day: daysInPrev - i, current: false });
  for (let i = 1; i <= daysInMonth; i++)
    days.push({ day: i, current: true });
  const rem = 42 - days.length;
  for (let i = 1; i <= rem; i++)
    days.push({ day: i, current: false });
  return days;
}

const statusBadge: Record<string, { bg: string; text: string; label: string }> = {
  pending:   { bg: 'bg-amber-100',   text: 'text-amber-800',   label: 'Chờ duyệt'    },
  confirmed: { bg: 'bg-blue-100',    text: 'text-blue-800',    label: 'Đã xác nhận'  },
  approved:  { bg: 'bg-blue-100',    text: 'text-blue-800',    label: 'Đã duyệt'     },
  completed: { bg: 'bg-emerald-100', text: 'text-emerald-800', label: 'Hoàn thành'   },
  cancelled: { bg: 'bg-red-100',     text: 'text-red-800',     label: 'Đã hủy'       },
};

export const AppointmentCalendarScreen: React.FC<AppointmentCalendarScreenProps> = ({ onNavigate }) => {
  const today = new Date();
  const [viewYear,  setViewYear]  = useState(today.getFullYear());
  const [viewMonth, setViewMonth] = useState(today.getMonth());
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [loading,   setLoading]   = useState(false);
  const [creating,  setCreating]  = useState(false);
  const [showForm,  setShowForm]  = useState(false);
  const [showDetail,  setShowDetail]  = useState(false);
  const [detailAppt,  setDetailAppt]  = useState<Appointment | null>(null);
  const [selectedDate, setSelectedDate] = useState(() => today.toISOString().split('T')[0]);

  const [fullName,    setFullName]    = useState('');
  const [phone,       setPhone]       = useState('');
  const [info,        setInfo]        = useState('');
  const [agencyId,    setAgencyId]    = useState('');
  const [serviceCode, setServiceCode] = useState('');
  const [time,        setTime]        = useState('09:00');
  const [errors,      setErrors]      = useState<string[]>([]);
  const [agencies,    setAgencies]    = useState<{id:string; name:string}[]>([]);

  const SERVICE_OPTIONS = [
    { code: 'cccd',         label: 'Cấp CCCD / Căn cước công dân' },
    { code: 'ho_khau',      label: 'Đăng ký hộ khẩu / Cư trú' },
    { code: 'khai_sinh',    label: 'Đăng ký khai sinh' },
    { code: 'ket_hon',      label: 'Đăng ký kết hôn' },
    { code: 'dat_dai',      label: 'Thủ tục đất đai / Nhà ở' },
    { code: 'gplx',         label: 'Giấy phép lái xe' },
    { code: 'xac_nhan',     label: 'Công chứng / Xác nhận giấy tờ' },
    { code: 'doanh_nghiep', label: 'Đăng ký doanh nghiệp' },
    { code: 'other',        label: 'Thủ tục khác' },
  ];

  const loadAppointments = async () => {
    setLoading(true);
    try {
      const res = await appointmentsAPI.getUpcoming();
      setAppointments(res.data.appointments || []);
    } catch { /* silently */ }
    finally { setLoading(false); }
  };

  useEffect(() => {
    loadAppointments();
    servicesAPI.getAll(undefined, undefined, undefined, undefined, undefined, 100)
      .then(r => {
        const list = r?.data?.services || [];
        setAgencies(list.map((s: any) => ({ id: s.id, name: s.name })));
        // dùng functional update để không cần agencyId trong dependency array
        setAgencyId(prev => (prev || (list.length > 0 ? list[0].id : '')));
      })
      .catch(() => {});
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const apptDaySet = useMemo(() => {
    const s = new Set<string>();
    appointments.forEach(a => s.add(a.date));
    return s;
  }, [appointments]);

  const calDays = useMemo(() => buildCalendarDays(viewYear, viewMonth), [viewYear, viewMonth]);

  const prevMonth = () => {
    if (viewMonth === 0) { setViewMonth(11); setViewYear(y => y - 1); }
    else setViewMonth(m => m - 1);
  };
  const nextMonth = () => {
    if (viewMonth === 11) { setViewMonth(0); setViewYear(y => y + 1); }
    else setViewMonth(m => m + 1);
  };

  const handleDateClick = (day: number, current: boolean) => {
    if (!current) return;
    const mm = String(viewMonth + 1).padStart(2, '0');
    const dd = String(day).padStart(2, '0');
    setSelectedDate(`${viewYear}-${mm}-${dd}`);
    setShowForm(true);
  };

  const validateForm = (): boolean => {
    const errs: string[] = [];
    if (!fullName.trim() || fullName.trim().length < 2) errs.push('Họ tên phải >= 2 ký tự');
    if (!/^(0[0-9]{9,10})$/.test(phone)) errs.push('Số điện thoại không hợp lệ');
    if (!selectedDate) errs.push('Chưa chọn ngày');
    if (!time) errs.push('Chưa chọn giờ');
    if (new Date(`${selectedDate}T${time}`) < new Date()) errs.push('Thời gian đã qua');
    if (!agencyId) errs.push('Cơ quan bắt buộc');
    if (!serviceCode) errs.push('Dịch vụ bắt buộc');
    setErrors(errs);
    return errs.length === 0;
  };

  const handleCreate = async () => {
    if (!validateForm()) return;
    setCreating(true);
    try {
      const payload: CreateAppointmentRequest = { agencyId, serviceCode, date: selectedDate, time, fullName, phone, info };
      await appointmentsAPI.create(payload);
      setShowForm(false);
      setFullName(''); setPhone(''); setInfo(''); setErrors([]);
      loadAppointments();
    } catch (e: any) {
      setErrors([e.message || 'Lỗi tạo lịch']);
    } finally { setCreating(false); }
  };

  const isToday = (day: number, current: boolean) =>
    current && day === today.getDate() &&
    viewMonth === today.getMonth() && viewYear === today.getFullYear();

  const dayKey = (day: number) => {
    const mm = String(viewMonth + 1).padStart(2, '0');
    const dd = String(day).padStart(2, '0');
    return `${viewYear}-${mm}-${dd}`;
  };

  const inputCls = "w-full border border-[#de9ca4] bg-white rounded-lg px-3 py-2.5 text-sm text-[#4d2128] outline-none focus:border-[#b7131a] focus:ring-1 focus:ring-[#b7131a] transition-colors placeholder:text-[#de9ca4]";
  const labelCls = "block text-[10px] font-bold uppercase text-[#824c54] tracking-wider mb-1";

  return (
    <div className="bg-[#fff4f4] text-[#4d2128] min-h-screen flex overflow-hidden font-[Manrope,sans-serif]">

      {/* ── Sidebar ── */}
      <aside className="h-screen w-72 left-0 top-0 fixed bg-[#ffeced] flex flex-col p-4 gap-2 border-r border-[#de9ca4]/15 z-20">
        <div className="mb-8 px-4 py-2">
          <h2 className="font-bold text-[#b7131a] text-xl">Quản lý</h2>
          <p className="font-medium text-sm text-[#9f364c]">Hệ thống công vụ</p>
        </div>

        <nav className="flex-1 space-y-2">
          {[
            { Icon: MessageSquarePlus, label: 'Đoạn chat mới',       active: false, action: () => onNavigate('chatbot') },
            { Icon: Search,            label: 'Tìm kiếm đoạn chat',  active: false, action: () => onNavigate('search')  },
            { Icon: Image,             label: 'Ảnh',                  active: false, action: () => onNavigate('submit')  },
            { Icon: CalendarCheck,     label: 'Đặt lịch online',      active: true,  action: () => {}                    },
          ].map(({ Icon, label, active, action }) => (
            <button
              key={label}
              onClick={action}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-300 text-sm font-medium ${
                active
                  ? 'bg-white text-[#b7131a] shadow-sm'
                  : 'text-[#9f364c] hover:bg-[#fff4f4]'
              }`}
            >
              <Icon className="w-5 h-5 shrink-0" />
              {label}
            </button>
          ))}
        </nav>

        {/* Back to home */}
        <button
          onClick={() => onNavigate('home')}
          className="flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium text-[#9f364c] hover:bg-[#fff4f4] transition-all duration-300"
        >
          <ArrowLeft className="w-5 h-5 shrink-0" />
          Trang chủ
        </button>

        {/* User card */}
        <div className="p-4 flex items-center gap-3 rounded-xl bg-[#ffeced] border border-[#de9ca4]/10">
          <div className="w-10 h-10 rounded-full bg-[#ff766b]/20 flex items-center justify-center text-[#b7131a] shrink-0">
            <User className="w-5 h-5" />
          </div>
          <div className="flex flex-col min-w-0">
            <span className="text-xs font-bold text-[#4d2128]">Cán bộ xử lý</span>
            <span className="text-[10px] text-[#9f364c]">Hành chính công</span>
          </div>
        </div>
      </aside>

      {/* ── Main ── */}
      <main className="ml-72 flex-1 flex flex-col h-screen overflow-y-auto bg-[#fff4f4]">

        {/* TopAppBar */}
        <header className="flex justify-between items-center px-8 h-16 w-full bg-[#fff4f4] top-0 sticky z-10 border-b border-[#ffeced]">
          <h1 className="font-bold text-lg tracking-tight text-[#b7131a] uppercase">Dịch vụ công Quốc gia</h1>
          <div className="flex items-center gap-6">
            <div className="flex items-center gap-1 text-[#b7131a] border-b-2 border-[#b7131a] px-2 py-1">
              <span className="font-bold text-sm">Hệ thống Đặt lịch Dịch vụ Công</span>
            </div>
            <div className="flex items-center gap-2 text-[#4d2128]">
              <button aria-label="Thông báo" className="hover:bg-[#ffeced] p-2 rounded-full transition-colors">
                <Bell className="w-5 h-5" />
              </button>
              <button aria-label="Tài khoản" className="hover:bg-[#ffeced] p-2 rounded-full transition-colors">
                <User className="w-5 h-5" />
              </button>
            </div>
          </div>
        </header>

        {/* Content grid */}
        <div className="p-8 grid grid-cols-12 gap-8">

          {/* ── Calendar col (8/12) ── */}
          <div className="col-span-12 lg:col-span-8 flex flex-col gap-6">
            <section className="bg-white rounded-xl p-8 shadow-[0px_20px_40px_rgba(77,33,40,0.06)] border border-[#de9ca4]/5">

              {/* Calendar header */}
              <div className="flex justify-between items-center mb-8">
                <div>
                  <h2 className="text-2xl font-bold text-[#4d2128] tracking-tight">
                    {VI_MONTHS[viewMonth]}/{viewYear}
                  </h2>
                  <p className="text-[#9f364c] text-sm mt-0.5">Chọn ngày để xem các khung giờ trống</p>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={prevMonth}
                    aria-label="Tháng trước"
                    className="w-10 h-10 rounded-lg flex items-center justify-center bg-[#ffeced] hover:bg-[#ffd9dd] transition-colors text-[#4d2128]"
                  >
                    <ChevronLeft className="w-5 h-5" />
                  </button>
                  <button
                    onClick={nextMonth}
                    aria-label="Tháng sau"
                    className="w-10 h-10 rounded-lg flex items-center justify-center bg-[#ffeced] hover:bg-[#ffd9dd] transition-colors text-[#4d2128]"
                  >
                    <ChevronRight className="w-5 h-5" />
                  </button>
                </div>
              </div>

              {/* Day-of-week headers */}
              <div className="grid grid-cols-7 text-center font-bold text-xs uppercase tracking-widest text-[#9f364c]/70 mb-4">
                {DOW_LABELS.map((d, i) => (
                  <div key={d} className={i >= 5 ? 'text-[#b7131a]/70' : ''}>
                    {d}
                  </div>
                ))}
              </div>

              {/* Day cells */}
              <div className="grid grid-cols-7 gap-2">
                {calDays.map(({ day, current }, idx) => {
                  const colInWeek = idx % 7; // 0=Mon … 5=Sat, 6=Sun
                  const isWeekend = colInWeek >= 5;
                  const todayCell = isToday(day, current);
                  const hasAppt   = current && apptDaySet.has(dayKey(day));

                  if (todayCell) {
                    return (
                      <div
                        key={idx}
                        onClick={() => handleDateClick(day, current)}
                        className="h-24 bg-[#b7131a] text-white rounded-lg p-2 font-bold shadow-lg shadow-[#b7131a]/20 relative overflow-hidden cursor-pointer group"
                      >
                        <span className="relative z-10 text-sm">{day}</span>
                        <div className="absolute bottom-2 left-2 right-2 bg-white/20 text-[9px] text-center py-1 rounded-md uppercase tracking-tighter z-10">
                          Hôm nay
                        </div>
                        <div className="absolute -right-4 -top-4 w-12 h-12 bg-white/10 rounded-full blur-xl group-hover:bg-white/20 transition-all" />
                      </div>
                    );
                  }

                  if (!current) {
                    return (
                      <div key={idx} className="h-24 bg-[#ffeced]/30 rounded-lg p-2 text-[#4d2128]/30 text-sm font-bold">
                        {day}
                      </div>
                    );
                  }

                  if (isWeekend) {
                    return (
                      <div key={idx} className="h-24 bg-[#ffeced]/50 rounded-lg p-2 font-bold text-[#b7131a] text-sm">
                        {day}
                        {hasAppt && <div className="mt-2 w-1.5 h-1.5 bg-[#b7131a] rounded-full" />}
                      </div>
                    );
                  }

                  return (
                    <div
                      key={idx}
                      onClick={() => handleDateClick(day, current)}
                      className="h-24 bg-white border border-[#de9ca4]/10 rounded-lg p-2 font-bold hover:bg-[#ff766b]/10 transition-colors cursor-pointer group text-sm text-[#4d2128]"
                    >
                      {day}
                      {hasAppt && <div className="mt-2 w-1.5 h-1.5 bg-[#b7131a] rounded-full" />}
                    </div>
                  );
                })}
              </div>
            </section>
          </div>

          {/* ── Right col (4/12) ── */}
          <div className="col-span-12 lg:col-span-4 flex flex-col gap-6">

            {/* CTA */}
            <button
              onClick={() => setShowForm(true)}
              className="w-full bg-gradient-to-br from-[#b7131a] to-[#ff766b] text-white py-6 px-8 rounded-xl flex items-center justify-between shadow-lg shadow-[#b7131a]/20 hover:scale-[1.02] transition-transform active:scale-95 group"
            >
              <div className="flex flex-col items-start">
                <span className="text-xl font-bold tracking-tight">ĐẶT LỊCH MỚI</span>
                <span className="text-xs text-white/80 mt-0.5">Thực hiện thủ tục hành chính</span>
              </div>
              <div className="w-12 h-12 bg-white/20 rounded-full flex items-center justify-center group-hover:rotate-90 transition-transform">
                <Plus className="w-7 h-7" />
              </div>
            </button>

            {/* Upcoming appointments */}
            <section className="bg-white rounded-xl p-6 border border-[#de9ca4]/15 flex flex-col h-[300px]">
              <div className="flex items-center justify-between mb-6">
                <h3 className="font-bold text-[#4d2128]">Lịch hẹn sắp tới</h3>
                <span className="px-2 py-1 bg-[#ffeced] text-[#9f364c] text-[10px] font-bold rounded uppercase">
                  {appointments.length === 0 ? 'Trống' : `${appointments.length} lịch`}
                </span>
              </div>

              {loading ? (
                <div className="flex-1 flex items-center justify-center">
                  <div className="w-6 h-6 border-2 border-[#b7131a] border-t-transparent rounded-full animate-spin" />
                </div>
              ) : appointments.length === 0 ? (
                <div className="flex-1 flex flex-col items-center justify-center text-center p-4">
                  <div className="w-20 h-20 bg-[#ffeced] rounded-full flex items-center justify-center mb-4">
                    <CalendarDays className="w-10 h-10 text-[#de9ca4]" />
                  </div>
                  <p className="font-bold text-[#4d2128] text-sm mb-1">Chưa có lịch hẹn nào</p>
                  <p className="text-[#9f364c] text-xs max-w-[200px] leading-relaxed">
                    Hãy nhấn 'Đặt lịch' để bắt đầu đăng ký lịch làm việc.
                  </p>
                </div>
              ) : (
                <div className="flex-1 overflow-y-auto divide-y divide-[#ffeced]">
                  {appointments.map(a => {
                    const badge = statusBadge[a.status || 'pending'] ?? statusBadge.pending;
                    return (
                      <button
                        key={a.id}
                        onClick={() => { setDetailAppt(a); setShowDetail(true); }}
                        className="w-full text-left px-2 py-3 hover:bg-[#fff4f4] transition-colors"
                      >
                        <div className="flex items-start justify-between gap-2">
                          <div className="min-w-0">
                            <p className="text-sm font-semibold text-[#4d2128] truncate">{a.fullName || 'Không tên'}</p>
                            <p className="text-[11px] text-[#9f364c] mt-0.5">{a.date} • {a.time}</p>
                          </div>
                          <span className={`shrink-0 text-[10px] font-bold px-2 py-0.5 rounded-full uppercase ${badge.bg} ${badge.text}`}>
                            {badge.label}
                          </span>
                        </div>
                      </button>
                    );
                  })}
                </div>
              )}
            </section>

            {/* Support */}
            <section className="bg-[#fdc003]/10 border border-[#fdc003]/20 rounded-xl p-6 relative overflow-hidden">
              <div className="absolute -right-8 -bottom-8 w-24 h-24 bg-[#fdc003]/20 rounded-full blur-2xl" />
              <h3 className="font-bold text-[#3d2b00] mb-4 flex items-center gap-2 text-sm">
                <Headphones className="w-5 h-5 text-[#755700]" />
                Cần hỗ trợ?
              </h3>
              <div className="space-y-4 relative z-10">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-white rounded-lg flex items-center justify-center text-[#755700] shadow-sm shrink-0">
                    <Phone className="w-5 h-5" />
                  </div>
                  <div>
                    <p className="text-[10px] uppercase font-bold text-[#ecb200]">Tổng đài hỗ trợ</p>
                    <p className="text-lg font-extrabold text-[#3d2b00]">1900 1000</p>
                  </div>
                </div>
                <div className="pt-4 border-t border-[#fdc003]/20">
                  <p className="text-xs text-[#604700] leading-relaxed">
                    Quy trình đặt lịch: Chọn ngày trên lịch <strong>→</strong> Chọn dịch vụ <strong>→</strong> Xác nhận thông tin qua SMS.
                  </p>
                </div>
              </div>
            </section>

            {/* Banner */}
            <div className="rounded-xl overflow-hidden h-32 relative group cursor-pointer shadow-sm bg-gradient-to-br from-[#b7131a] to-[#9f364c]">
              <div className="absolute inset-0 bg-gradient-to-r from-[#b7131a]/90 to-transparent flex items-center p-6">
                <p className="text-white font-bold text-sm leading-tight max-w-[180px]">
                  Hướng dẫn sử dụng cổng dịch vụ công trực tuyến mới
                </p>
              </div>
              <div className="absolute bottom-2 right-2 bg-white/20 backdrop-blur-md rounded-full px-2 py-1">
                <ChevronRight className="w-4 h-4 text-white" />
              </div>
            </div>

          </div>
        </div>

        {/* Floating accent */}
        <div className="fixed bottom-8 right-8 pointer-events-none opacity-20 hidden lg:block select-none">
          <span className="font-black text-8xl text-[#ff766b]">{today.getDate()}</span>
        </div>

      </main>

      {/* ══════════════════════
          Modal: Tạo lịch hẹn
      ══════════════════════ */}
      {showForm && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
          <div className="bg-white w-full max-w-lg rounded-xl shadow-2xl">
            <div className="flex items-center justify-between px-8 py-5 border-b border-[#ffeced]">
              <h2 className="text-lg font-black text-[#4d2128] uppercase tracking-tight">Tạo lịch hẹn mới</h2>
              <button
                onClick={() => { setShowForm(false); setErrors([]); }}
                aria-label="Đóng"
                className="p-1 hover:bg-[#ffeced] transition-colors rounded-lg"
              >
                <X className="w-5 h-5 text-[#9f364c]" />
              </button>
            </div>
            <div className="px-8 py-6 space-y-4">
              <div>
                <label className={labelCls}>Họ và tên</label>
                <input className={inputCls} value={fullName} onChange={e => setFullName(e.target.value)} placeholder="Nhập họ tên đầy đủ" />
              </div>
              <div>
                <label className={labelCls}>Số điện thoại</label>
                <input className={inputCls} value={phone} onChange={e => setPhone(e.target.value)} placeholder="0xxxxxxxxx" />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className={labelCls}>Ngày hẹn</label>
                  <input type="date" aria-label="Ngày hẹn" className={inputCls} value={selectedDate} onChange={e => setSelectedDate(e.target.value)} />
                </div>
                <div>
                  <label className={labelCls}>Giờ hẹn</label>
                  <input type="time" aria-label="Giờ hẹn" className={inputCls} value={time} onChange={e => setTime(e.target.value)} />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className={labelCls}>Loại dịch vụ</label>
                  <select
                    className={inputCls}
                    value={serviceCode}
                    onChange={e => setServiceCode(e.target.value)}
                    aria-label="Loại dịch vụ"
                  >
                    <option value="">-- Chọn dịch vụ --</option>
                    {SERVICE_OPTIONS.map(s => (
                      <option key={s.code} value={s.code}>{s.label}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className={labelCls}>Cơ quan</label>
                  <select
                    className={inputCls}
                    value={agencyId}
                    onChange={e => setAgencyId(e.target.value)}
                    aria-label="Cơ quan"
                  >
                    <option value="">-- Chọn cơ quan --</option>
                    {agencies.map(a => (
                      <option key={a.id} value={a.id}>{a.name}</option>
                    ))}
                    {agencies.length === 0 && (
                      <option value="ubnd-thanhhoa">UBND tỉnh Thanh Hóa</option>
                    )}
                  </select>
                </div>
              </div>
              <div>
                <label className={labelCls}>Ghi chú (tùy chọn)</label>
                <input className={inputCls} value={info} onChange={e => setInfo(e.target.value)} placeholder="Thông tin bổ sung..." />
              </div>
              {errors.length > 0 && (
                <div className="p-4 bg-[#ffeced] border-l-4 border-[#b7131a] rounded space-y-1">
                  {errors.map((er, i) => (
                    <div key={i} className="flex items-center gap-2 text-sm text-[#b7131a]">
                      <AlertCircle className="w-4 h-4 shrink-0" />{er}
                    </div>
                  ))}
                </div>
              )}
            </div>
            <div className="flex gap-3 px-8 py-5 border-t border-[#ffeced]">
              <button
                onClick={handleCreate}
                disabled={creating}
                className="flex-1 py-3 bg-[#b7131a] text-white font-bold text-xs uppercase tracking-widest rounded-lg hover:bg-[#a40010] disabled:opacity-40 active:scale-95 transition-all flex items-center justify-center gap-2"
              >
                {creating
                  ? <><span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />Đang lưu...</>
                  : <><CheckCircle className="w-4 h-4" />Xác nhận đặt lịch</>
                }
              </button>
              <button
                onClick={() => { setShowForm(false); setErrors([]); }}
                className="px-6 py-3 border border-[#de9ca4] text-[#9f364c] font-bold text-xs uppercase tracking-widest rounded-lg hover:bg-[#ffeced] transition-colors"
              >
                Hủy
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ══════════════════════
          Modal: Chi tiết
      ══════════════════════ */}
      {showDetail && detailAppt && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
          <div className="bg-white w-full max-w-md rounded-xl shadow-2xl">
            <div className="flex items-center justify-between px-8 py-5 border-b border-[#ffeced]">
              <h2 className="text-base font-black text-[#4d2128] uppercase tracking-tight">Chi tiết lịch hẹn</h2>
              <button
                onClick={() => { setShowDetail(false); setDetailAppt(null); }}
                aria-label="Đóng"
                className="p-1 hover:bg-[#ffeced] transition-colors rounded-lg"
              >
                <X className="w-5 h-5 text-[#9f364c]" />
              </button>
            </div>
            <div className="px-8 py-6 space-y-4">
              {[
                { label: 'Họ và tên',     value: detailAppt.fullName || '—' },
                { label: 'Số điện thoại', value: detailAppt.phone    || '—' },
                { label: 'Dịch vụ',       value: detailAppt.serviceCode     },
                { label: 'Cơ quan',       value: detailAppt.agencyId        },
                { label: 'Thời gian',     value: `${detailAppt.date} • ${detailAppt.time}` },
                { label: 'Ghi chú',       value: detailAppt.info    || '—' },
              ].map(({ label, value }) => (
                <div key={label}>
                  <span className="block text-[10px] font-bold uppercase text-[#824c54] tracking-wider mb-0.5">{label}</span>
                  <span className="text-sm font-medium text-[#4d2128]">{value}</span>
                </div>
              ))}
              <div>
                <span className="block text-[10px] font-bold uppercase text-[#824c54] tracking-wider mb-1">Trạng thái</span>
                {(() => {
                  const b = statusBadge[detailAppt.status || 'pending'] ?? statusBadge.pending;
                  return <span className={`text-xs font-bold px-3 py-1 rounded-full uppercase ${b.bg} ${b.text}`}>{b.label}</span>;
                })()}
              </div>
            </div>
            <div className="px-8 py-5 border-t border-[#ffeced]">
              <button
                onClick={() => { setShowDetail(false); setDetailAppt(null); }}
                className="px-6 py-3 border border-[#de9ca4] text-[#9f364c] font-bold text-xs uppercase tracking-widest rounded-lg hover:bg-[#ffeced] transition-colors"
              >
                Đóng
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
};
