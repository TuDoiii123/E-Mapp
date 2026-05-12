import React, { useState } from 'react';
import { appointmentsAPI } from '../services/appointmentsApi';
import {
  ArrowLeft, ArrowRight, Building2, Clock, Info,
  CheckCircle, FileText, QrCode, XCircle,
  Phone, AlertCircle, ChevronLeft, ChevronRight,
  CalendarDays, Folder,
  ShieldCheck, ClipboardList, Printer, Download, HelpCircle,
} from 'lucide-react';

interface AppointmentScreenProps {
  onNavigate: (screen: string, params?: any) => void;
  defaultAgencyId?: string;
  defaultServiceCode?: string;
}

/* ── Static data ── */
const PROVINCES = ['Thành phố Hà Nội', 'Thành phố Hồ Chí Minh', 'Thành phố Đà Nẵng'];
const DISTRICTS: Record<string, string[]> = {
  'Thành phố Hà Nội':       ['Quận Hoàn Kiếm', 'Quận Ba Đình', 'Quận Hai Bà Trưng'],
  'Thành phố Hồ Chí Minh':  ['Quận 1', 'Quận 3', 'Quận Bình Thạnh'],
  'Thành phố Đà Nẵng':      ['Quận Hải Châu', 'Quận Thanh Khê'],
};
const AGENCIES: Record<string, string[]> = {
  /* Hà Nội */
  'Quận Hoàn Kiếm':    ['UBND Phường Hàng Mã', 'UBND Phường Phan Chu Trinh', 'Công an Quận Hoàn Kiếm'],
  'Quận Ba Đình':      ['UBND Phường Điện Biên', 'UBND Phường Đội Cấn'],
  'Quận Hai Bà Trưng': ['UBND Phường Bạch Đằng', 'UBND Phường Bùi Thị Xuân'],
  /* TP.HCM */
  'Quận 1':            ['UBND Phường Bến Nghé', 'UBND Phường Bến Thành', 'Công an Quận 1'],
  'Quận 3':            ['UBND Phường Võ Thị Sáu', 'UBND Phường 9'],
  'Quận Bình Thạnh':   ['UBND Phường 1', 'UBND Phường 13', 'Công an Quận Bình Thạnh'],
  /* Đà Nẵng */
  'Quận Hải Châu':     ['UBND Phường Hải Châu 1', 'UBND Phường Thạch Thang', 'Công an Quận Hải Châu'],
  'Quận Thanh Khê':    ['UBND Phường Thanh Khê Đông', 'UBND Phường Xuân Hà'],
};
const SERVICES = [
  { code: 'MARRIAGE',  label: 'Đăng ký kết hôn' },
  { code: 'BIRTH',     label: 'Đăng ký khai sinh' },
  { code: 'NOTARIZE',  label: 'Chứng thực bản sao từ bản chính' },
  { code: 'CCCD',      label: 'Cấp lại thẻ Căn cước công dân' },
];
const MORNING_SLOTS   = ['08:00', '09:00', '10:00', '11:00'];
const AFTERNOON_SLOTS = ['13:30', '14:30', '15:30', '16:30'];
const BOOKED_SLOTS    = ['11:00', '15:30'];

const VI_MONTHS = [
  'Tháng 01','Tháng 02','Tháng 03','Tháng 04','Tháng 05','Tháng 06',
  'Tháng 07','Tháng 08','Tháng 09','Tháng 10','Tháng 11','Tháng 12',
];
const DOW_LABELS = ['Thứ 2','Thứ 3','Thứ 4','Thứ 5','Thứ 6','Thứ 7','CN'];

function buildCalDays(year: number, month: number) {
  const firstDow = new Date(year, month, 1).getDay();
  const offset   = firstDow === 0 ? 6 : firstDow - 1;
  const dim      = new Date(year, month + 1, 0).getDate();
  const prevDim  = new Date(year, month, 0).getDate();
  const days: { day: number; cur: boolean }[] = [];
  for (let i = offset - 1; i >= 0; i--) days.push({ day: prevDim - i, cur: false });
  for (let i = 1; i <= dim; i++)         days.push({ day: i,           cur: true  });
  const rem = 42 - days.length;
  for (let i = 1; i <= rem; i++)         days.push({ day: i,           cur: false });
  return days;
}

const STEPS = ['Thông tin hồ sơ', 'Chọn ngày & Giờ', 'Hoàn tất'];

const selectCls = "w-full bg-white border-0 border-b-2 border-[#8e706d] focus:border-[#705d00] focus:ring-0 transition-all py-3 text-sm text-[#1a1c1c] outline-none";
const labelCls  = "block text-[10px] font-bold text-[#5a403e] uppercase tracking-wider mb-1";
const inputCls  = "w-full border border-[#e2beba] bg-white px-3 py-2.5 text-sm text-[#1a1c1c] outline-none focus:border-[#8f000d] focus:ring-1 focus:ring-[#8f000d] transition-colors placeholder:text-[#8e706d]";

export function AppointmentScreen({ onNavigate, defaultAgencyId, defaultServiceCode }: AppointmentScreenProps) {
  const today = new Date();

  const [step, setStep] = useState(1);

  /* Step 1 */
  const [province,    setProvince]    = useState(PROVINCES[0]);
  const [district,    setDistrict]    = useState(DISTRICTS[PROVINCES[0]][0]);
  const [agencyName,  setAgencyName]  = useState(defaultAgencyId || (AGENCIES[DISTRICTS[PROVINCES[0]][0]]?.[0] ?? ''));
  const [serviceCode, setServiceCode] = useState(defaultServiceCode || SERVICES[0].code);

  /* Step 2 */
  const [viewYear,  setViewYear]  = useState(today.getFullYear());
  const [viewMonth, setViewMonth] = useState(today.getMonth());
  const [selDate,   setSelDate]   = useState('');
  const [selTime,   setSelTime]   = useState('');

  /* Step 3 */
  const [fullName,     setFullName]     = useState('');
  const [phone,        setPhone]        = useState('');
  const [note,         setNote]         = useState('');
  const [loading,      setLoading]      = useState(false);
  const [error,        setError]        = useState<string | null>(null);
  const [success,      setSuccess]      = useState(false);
  const [confirmCode,  setConfirmCode]  = useState('');

  /* Helpers */
  const prevMonth = () => {
    if (viewMonth === 0) { setViewMonth(11); setViewYear(y => y - 1); }
    else setViewMonth(m => m - 1);
  };
  const nextMonth = () => {
    if (viewMonth === 11) { setViewMonth(0); setViewYear(y => y + 1); }
    else setViewMonth(m => m + 1);
  };
  const dayKey = (day: number) =>
    `${viewYear}-${String(viewMonth + 1).padStart(2,'0')}-${String(day).padStart(2,'0')}`;
  const isToday = (day: number, cur: boolean) =>
    cur && day === today.getDate() && viewMonth === today.getMonth() && viewYear === today.getFullYear();

  const calDays = buildCalDays(viewYear, viewMonth);

  const canStep1 = !!province && !!district && !!agencyName && !!serviceCode;
  const canStep2 = !!selDate && !!selTime;

  const fmtDate = (d: string) => {
    if (!d) return '—';
    const [y, m, dd] = d.split('-');
    return `${dd}/${m}/${y}`;
  };

  const handleSubmit = async () => {
    if (!fullName.trim() || fullName.trim().length < 2) { setError('Họ tên phải >= 2 ký tự'); return; }
    if (!/^(0[0-9]{9,10})$/.test(phone)) { setError('Số điện thoại không hợp lệ'); return; }
    setLoading(true); setError(null);
    try {
      const result = await appointmentsAPI.create({ agencyId: agencyName, serviceCode, date: selDate, time: selTime, fullName, phone, info: note });
      const serverCode = result?.data?.id ?? result?.data?.queueNumber;
      setConfirmCode(serverCode ? String(serverCode).slice(0, 12).toUpperCase() : `HS-${Date.now().toString(36).toUpperCase()}`);
      setSuccess(true);
    } catch (e: any) {
      setError(e.message || 'Có lỗi xảy ra');
    } finally { setLoading(false); }
  };

  /* ── Success (Bước 4) ── */
  if (success) {
    const svcLabel = SERVICES.find(s => s.code === serviceCode)?.label ?? serviceCode;
    return (
      <div className="min-h-screen bg-[#f9f9f9] font-['Public_Sans',sans-serif]">

        {/* TopAppBar */}
        <nav className="fixed top-0 w-full z-50 bg-white/80 backdrop-blur-xl border-b-2 border-amber-600/20 shadow-sm flex justify-between items-center px-4 md:px-6 h-16">
          <div className="flex items-center gap-4">
            <span className="text-sm md:text-lg font-bold tracking-tighter text-[#8f000d] uppercase">Dịch vụ Công Quốc gia</span>
          </div>
          <div className="flex items-center gap-6">
            <div className="hidden md:flex gap-8 text-zinc-600 text-sm">
              <button onClick={() => onNavigate('home')} className="hover:text-[#8f000d] transition-colors">Trang chủ</button>
              <span className="text-[#8f000d] font-bold">Lịch hẹn</span>
            </div>
          </div>
        </nav>

        {/* Sidebar */}
        <aside className="hidden lg:flex flex-col fixed left-0 top-16 bottom-0 w-64 border-r border-zinc-200 bg-zinc-50 z-40">
          <div className="p-6">
            <h2 className="text-xl font-black text-[#8f000d]">Hệ thống Quốc gia</h2>
            <p className="text-[10px] uppercase tracking-widest text-zinc-500">Phụng sự Nhân dân</p>
          </div>
          <nav className="flex-1 px-3 space-y-1">
            {[
              { icon: Building2,    label: 'Trang chủ',           active: false, action: () => onNavigate('home') },
              { icon: FileText,     label: 'Thủ tục hành chính',  active: false, action: () => onNavigate('submit') },
              { icon: CalendarDays, label: 'Lịch hẹn của tôi',    active: true,  action: () => {} },
              { icon: HelpCircle,   label: 'Hỗ trợ',              active: false, action: () => {} },
            ].map(({ icon: Icon, label, active, action }) => (
              <button key={label} onClick={action}
                className={`w-full flex items-center gap-3 px-4 py-3 text-sm font-medium transition-all
                  ${active ? 'bg-red-50 text-[#8f000d] border-r-4 border-[#8f000d]' : 'text-zinc-500 hover:bg-zinc-100'}`}>
                <Icon className="w-5 h-5 shrink-0" />
                {label}
              </button>
            ))}
          </nav>
        </aside>

        {/* Main */}
        <main className="pt-20 pb-20 lg:pl-72 px-3 md:px-6 lg:px-8 max-w-7xl mx-auto min-h-screen">

          {/* Stepper — all done */}
          <div className="mb-12 max-w-2xl mx-auto">
            <div className="flex items-center justify-between relative">
              <div className="absolute top-5 left-0 w-full h-0.5 bg-[#b22222] -z-10" />
              {['Thông tin', 'Chọn lịch', 'Hoàn tất'].map((label, i) => {
                const isLast = i === 2;
                return (
                  <div key={label} className="relative z-10 flex flex-col items-center gap-2 bg-[#f9f9f9] px-3">
                    <div className={`rounded-full flex items-center justify-center shadow-md text-white
                      ${isLast
                        ? 'w-12 h-12 bg-[#8f000d] ring-4 ring-[#ffdad6] shadow-lg'
                        : 'w-10 h-10 bg-[#b22222]'}`}>
                      {isLast
                        ? <ShieldCheck className="w-6 h-6" />
                        : <CheckCircle className="w-5 h-5" />}
                    </div>
                    <span className={`text-[10px] font-bold uppercase tracking-widest
                      ${isLast ? 'text-[#8f000d] font-black' : 'text-[#5a403e]'}`}>
                      {label}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Hero */}
          <div className="text-center mb-10">
            <h1 className="text-3xl md:text-5xl font-black text-[#1a1c1c] tracking-tighter uppercase mb-4">
              ĐẶT LỊCH HẸN THÀNH CÔNG
            </h1>
            <p className="text-[#5a403e] max-w-xl mx-auto font-medium">
              Hệ thống đã ghi nhận lịch hẹn của ông/bà. Vui lòng lưu lại mã số và thông tin dưới đây để thực hiện thủ tục.
            </p>
          </div>

          {/* Confirmation card */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-0 bg-white shadow-[0_12px_40px_rgba(142,112,109,0.08)] border-b-4 border-[#705d00] overflow-hidden">

            {/* Left — identity */}
            <div className="lg:col-span-5 bg-[#8f000d] p-6 md:p-10 flex flex-col justify-between relative overflow-hidden">
              <div className="absolute inset-0 opacity-10 bg-[radial-gradient(circle_at_center,_rgba(255,255,255,0.2)_0%,_transparent_70%)]" />
              <div className="relative z-10">
                <span className="inline-block px-3 py-1 bg-[#705d00] text-[#221b00] font-bold text-[10px] uppercase tracking-widest mb-6">
                  Mã số xác nhận
                </span>
                <h2 className="text-3xl md:text-5xl font-black text-white tracking-tighter mb-2">{confirmCode}</h2>
                <p className="text-[#ffdad6] font-medium">Vui lòng xuất trình mã này khi đến quầy</p>
              </div>
              {/* QR placeholder */}
              <div className="relative z-10 mt-10 p-4 bg-white inline-block self-center lg:self-start">
                <div className="w-40 h-40 bg-[#f3f3f3] flex items-center justify-center">
                  <QrCode className="w-24 h-24 text-[#1a1c1c]" />
                </div>
                <p className="text-center text-[10px] font-bold text-zinc-400 mt-2 uppercase tracking-widest">Quét để check-in</p>
              </div>
            </div>

            {/* Right — details */}
            <div className="lg:col-span-7 p-6 md:p-10 flex flex-col justify-between bg-white">
              <div className="space-y-8">

                <div className="border-l-4 border-[#705d00] pl-6">
                  <p className="text-[10px] uppercase tracking-widest text-[#5a403e] font-bold mb-1">Cơ quan thực hiện</p>
                  <h3 className="text-xl font-bold text-[#1a1c1c]">{agencyName}</h3>
                  <p className="text-sm text-[#5a403e]">{district}, {province}</p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                  <div>
                    <p className="text-[10px] uppercase tracking-widest text-[#5a403e] font-bold mb-1">Thủ tục</p>
                    <p className="text-lg font-semibold text-[#8f000d]">{svcLabel}</p>
                  </div>
                  <div>
                    <p className="text-[10px] uppercase tracking-widest text-[#5a403e] font-bold mb-1">Thời gian hẹn</p>
                    <p className="text-lg font-semibold text-[#1a1c1c]">{selTime}</p>
                    <p className="text-sm font-medium text-[#5a403e]">{fmtDate(selDate)}</p>
                  </div>
                  <div>
                    <p className="text-[10px] uppercase tracking-widest text-[#5a403e] font-bold mb-1">Người đặt lịch</p>
                    <p className="text-lg font-semibold text-[#1a1c1c]">{fullName}</p>
                    <p className="text-sm text-[#5a403e]">{phone}</p>
                  </div>
                </div>

                <div className="bg-[#f3f3f3] p-6 space-y-3 border-l-4 border-[#8e706d]">
                  <div className="flex items-start gap-3">
                    <Info className="w-5 h-5 text-[#705d00] shrink-0 mt-0.5" />
                    <p className="text-sm text-[#5a403e] leading-relaxed">
                      Vui lòng có mặt tại địa điểm hẹn trước ít nhất <strong className="text-[#1a1c1c]">15 phút</strong> để làm thủ tục check-in.
                    </p>
                  </div>
                  <div className="flex items-start gap-3">
                    <FileText className="w-5 h-5 text-[#705d00] shrink-0 mt-0.5" />
                    <p className="text-sm text-[#5a403e] leading-relaxed">
                      Mang theo <strong className="text-[#1a1c1c]">bản gốc</strong> CMND/CCCD và các giấy tờ liên quan đã kê khai trực tuyến.
                    </p>
                  </div>
                </div>
              </div>

              {/* Actions */}
              <div className="mt-10 flex flex-col sm:flex-row gap-4">
                <button
                  onClick={() => window.print()}
                  className="flex-1 bg-[#8f000d] text-white py-4 px-6 flex items-center justify-center gap-2 font-bold uppercase tracking-widest text-sm hover:bg-[#b22222] transition-colors shadow-sm active:scale-95"
                >
                  <Printer className="w-5 h-5" />
                  In phiếu hẹn
                </button>
                <button className="flex-1 bg-[#fcd400] text-[#6e5c00] py-4 px-6 flex items-center justify-center gap-2 font-bold uppercase tracking-widest text-sm hover:brightness-95 transition-all shadow-sm active:scale-95">
                  <Download className="w-5 h-5" />
                  Tải PDF
                </button>
              </div>
            </div>
          </div>

          {/* Back link */}
          <div className="mt-8 text-center">
            <button
              onClick={() => onNavigate('appointment')}
              className="inline-flex items-center gap-2 text-[#8f000d] font-bold uppercase tracking-widest text-sm hover:underline py-2"
            >
              <ArrowLeft className="w-4 h-4" />
              Về trang chủ hệ thống
            </button>
          </div>

        </main>

        {/* Floating decorative ring */}
        <div className="fixed bottom-24 right-8 opacity-20 pointer-events-none hidden xl:block">
          <div className="w-48 h-48 border-[12px] border-[#b22222] rounded-full flex items-center justify-center">
            <div className="w-32 h-32 border-[4px] border-[#705d00] rounded-full" />
          </div>
        </div>
      </div>
    );
  }

  /* ── Main render ── */
  return (
    <div className="min-h-screen bg-[#f9f9f9] font-['Public_Sans',sans-serif]">

      {/* TopAppBar */}
      <header className="bg-white/80 backdrop-blur-md border-b-2 border-stone-100 shadow-sm fixed top-0 w-full z-50 flex justify-between items-center px-4 md:px-8 h-16">
        <div className="flex items-center gap-6">
          <button onClick={() => onNavigate('appointment')} aria-label="Quay lại trang lịch hẹn" className="p-2 hover:bg-[#f3f3f3] transition-colors rounded">
            <ArrowLeft className="w-5 h-5 text-[#1a1c1c]" />
          </button>
          <span className="text-sm md:text-lg font-bold text-[#8f000d] uppercase tracking-tight hidden sm:block">
            CỔNG DỊCH VỤ CÔNG QUỐC GIA
          </span>
          <nav className="hidden md:flex gap-6">
            {['Trang chủ','Thủ tục','Tra cứu'].map(n => (
              <button key={n} className="text-sm text-[#5a403e] font-medium hover:text-[#8f000d] transition-colors">{n}</button>
            ))}
          </nav>
        </div>
      </header>

      {/* Sidebar */}
      <aside className="hidden lg:flex flex-col h-screen w-64 fixed left-0 top-16 bg-stone-50 py-6 border-r border-stone-200 z-40">
        <div className="px-6 mb-8">
          <div className="text-lg font-black text-[#8f000d] uppercase">Trung tâm Điều hành</div>
          <div className="text-[10px] font-semibold text-[#5a403e] uppercase tracking-widest">Quản lý dịch vụ công</div>
        </div>
        <nav className="flex-1 px-3 space-y-1">
          {[
            { icon: Building2,   label: 'Tổng quan',      active: false, action: () => onNavigate('home') },
            { icon: CalendarDays,label: 'Lịch hẹn của tôi',active: true, action: () => {} },
            { icon: Folder,      label: 'Hồ sơ dịch vụ',  active: false, action: () => onNavigate('submit') },
          ].map(({ icon: Icon, label, active, action }) => (
            <button key={label} onClick={action}
              className={`w-full flex items-center gap-3 px-3 py-2 text-sm font-semibold rounded hover:pl-6 transition-all duration-300
                ${active ? 'bg-white text-[#8f000d] border-l-4 border-[#8f000d] shadow-sm' : 'text-[#5a403e] hover:bg-stone-100'}`}>
              <Icon className="w-5 h-5 shrink-0" />
              {label}
            </button>
          ))}
        </nav>
      </aside>

      {/* Main */}
      <main className="pt-20 pb-12 lg:ml-64 px-3 md:px-6 lg:px-8 max-w-7xl mx-auto">

        {/* ── Stepper ── */}
        <div className="mb-12">
          <div className="flex items-center justify-between max-w-2xl mx-auto relative">
            {/* bg line */}
            <div className="absolute top-5 left-0 w-full h-0.5 bg-[#e2e2e2] -z-10 -translate-y-0" />
            {/* progress line */}
            <div
              className="absolute top-5 left-0 h-0.5 bg-[#8f000d] -z-10 transition-all duration-500"
              style={{ width: step === 1 ? '0%' : step === 2 ? '50%' : '100%' }}
            />
            {STEPS.map((label, i) => {
              const n = i + 1;
              const done   = n < step;
              const active = n === step;
              return (
                <div key={n} className="relative z-10 flex flex-col items-center bg-[#f9f9f9] px-3">
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold shadow-lg
                    ${done   ? 'bg-[#8f000d] text-white' :
                      active ? 'bg-[#8f000d] text-white ring-4 ring-[#ffdad6]' :
                               'bg-[#e2e2e2] text-[#5a403e]'}`}>
                    {done ? <CheckCircle className="w-5 h-5" /> : n}
                  </div>
                  <span className={`text-[10px] mt-2 font-bold uppercase tracking-tighter text-center
                    ${active ? 'text-[#8f000d]' : done ? 'text-[#8f000d]' : 'text-[#5a403e]'}`}>
                    {label}
                  </span>
                </div>
              );
            })}
          </div>
        </div>

        {/* ── Content grid ── */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">

          {/* ── Left: Step content (8 cols) ── */}
          <div className="lg:col-span-8 space-y-6">

            {/* ════ STEP 1 ════ */}
            {step === 1 && (
              <section className="bg-[#f3f3f3] p-4 md:p-8 shadow-sm">
                <h2 className="text-base font-bold text-[#1a1c1c] flex items-center gap-2 mb-6">
                  <Building2 className="w-5 h-5 text-[#8f000d]" />
                  Thông tin cơ quan &amp; Thủ tục
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label htmlFor="sel-province" className={labelCls}>Tỉnh/Thành phố</label>
                    <select id="sel-province" className={selectCls} value={province} onChange={e => {
                      setProvince(e.target.value);
                      const d = DISTRICTS[e.target.value]?.[0] ?? '';
                      setDistrict(d);
                      setAgencyName(AGENCIES[d]?.[0] ?? '');
                    }}>
                      {PROVINCES.map(p => <option key={p}>{p}</option>)}
                    </select>
                  </div>
                  <div>
                    <label htmlFor="sel-district" className={labelCls}>Quận/Huyện</label>
                    <select id="sel-district" className={selectCls} value={district} onChange={e => {
                      setDistrict(e.target.value);
                      setAgencyName(AGENCIES[e.target.value]?.[0] ?? '');
                    }}>
                      {(DISTRICTS[province] ?? []).map(d => <option key={d}>{d}</option>)}
                    </select>
                  </div>
                  <div className="md:col-span-2">
                    <label htmlFor="sel-agency" className={labelCls}>Tên cơ quan tiếp nhận</label>
                    <select id="sel-agency" className={selectCls} value={agencyName} onChange={e => setAgencyName(e.target.value)}>
                      {(AGENCIES[district] ?? [agencyName]).map(a => <option key={a}>{a}</option>)}
                    </select>
                  </div>
                  <div className="md:col-span-2">
                    <label htmlFor="sel-service" className={labelCls}>Lĩnh vực / Thủ tục hành chính</label>
                    <select id="sel-service" className={selectCls} value={serviceCode} onChange={e => setServiceCode(e.target.value)}>
                      {SERVICES.map(s => <option key={s.code} value={s.code}>{s.label}</option>)}
                    </select>
                  </div>
                </div>
              </section>
            )}

            {/* ════ STEP 2 ════ */}
            {step === 2 && (
              <>
                {/* ── Calendar ── */}
                <section className="bg-[#f3f3f3] p-3 md:p-6 shadow-sm">
                  <div className="flex items-center justify-between mb-8">
                    <h2 className="text-xl font-extrabold text-[#1a1c1c] uppercase tracking-tight">
                      {VI_MONTHS[viewMonth]}, {viewYear}
                    </h2>
                    <div className="flex gap-2">
                      <button onClick={prevMonth} aria-label="Tháng trước" className="p-2 bg-white hover:bg-[#8f000d] hover:text-white transition-colors">
                        <ChevronLeft className="w-4 h-4" />
                      </button>
                      <button onClick={nextMonth} aria-label="Tháng sau" className="p-2 bg-white hover:bg-[#8f000d] hover:text-white transition-colors">
                        <ChevronRight className="w-4 h-4" />
                      </button>
                    </div>
                  </div>

                  {/* Grid */}
                  <div className="grid grid-cols-7 gap-px bg-[#e2beba]/20 border-t border-l border-[#e2beba]/20">
                    {/* DOW header */}
                    {DOW_LABELS.map((d, i) => (
                      <div key={d}
                        className={`bg-[#eeeeee] py-3 text-center text-[10px] font-black uppercase tracking-widest
                          ${i >= 5 ? 'text-[#705d00]' : 'text-[#5a403e]'}`}>
                        {d}
                      </div>
                    ))}

                    {/* Day cells */}
                    {calDays.map(({ day, cur }, idx) => {
                      const k      = cur ? dayKey(day) : '';
                      const sel    = k === selDate;
                      const tod    = isToday(day, cur);
                      const dow    = idx % 7;
                      const isWknd = dow >= 5;
                      const past   = cur && new Date(k) < new Date(today.toDateString());

                      if (!cur) return (
                        <div key={idx} className="bg-[#f3f3f3] h-12 sm:h-16 md:h-24 opacity-30 pointer-events-none flex items-center justify-center font-bold text-[#5a403e] text-sm">
                          {day}
                        </div>
                      );
                      if (isWknd) return (
                        <div key={idx} className="bg-[#f3f3f3] h-12 sm:h-16 md:h-24 flex items-center justify-center font-bold text-stone-300 text-sm">
                          {day}
                        </div>
                      );
                      if (past) return (
                        <div key={idx} className="bg-white h-12 sm:h-16 md:h-24 flex items-center justify-center font-bold text-stone-300 cursor-not-allowed text-sm">
                          {day}
                        </div>
                      );

                      return sel ? (
                        <div key={idx} className="bg-[#8f000d] h-12 sm:h-16 md:h-24 text-white flex flex-col items-center justify-center font-bold relative overflow-hidden cursor-pointer">
                          <span className="z-10 text-base sm:text-xl md:text-2xl">{String(day).padStart(2,'0')}</span>
                          <span className="z-10 text-[8px] uppercase tracking-widest opacity-80">Đang chọn</span>
                          <div className="absolute bottom-0 right-0 w-8 h-8 bg-[#705d00] rotate-45 translate-x-4 translate-y-4" />
                        </div>
                      ) : (
                        <div
                          key={idx}
                          onClick={() => { setSelDate(k); setSelTime(''); }}
                          className={`h-12 sm:h-16 md:h-24 hover:bg-[#ffdad6] cursor-pointer transition-colors flex items-center justify-center font-bold text-sm md:text-base
                            ${tod ? 'bg-red-50 ring-1 ring-inset ring-[#8f000d]/20 text-[#8f000d]' : 'bg-white'}`}
                        >
                          {day}
                        </div>
                      );
                    })}
                  </div>
                </section>

                {/* ── Time slots ── */}
                <section className="bg-white p-4 md:p-8 shadow-sm border-l-4 border-[#8f000d]">
                  <div className="flex items-center gap-3 mb-6">
                    <Clock className="w-5 h-5 text-[#8f000d]" />
                    <h3 className="text-lg font-bold uppercase tracking-tight">
                      {selDate ? `Khung giờ trống cho ngày ${fmtDate(selDate)}` : 'Chọn ngày để xem khung giờ'}
                    </h3>
                  </div>

                  {!selDate ? (
                    <p className="text-sm text-[#8e706d] italic py-4">Vui lòng chọn ngày trên lịch trước.</p>
                  ) : (
                    <>
                      <div className="space-y-8">
                        {[
                          { label: 'Sáng',   slots: MORNING_SLOTS },
                          { label: 'Chiều',  slots: AFTERNOON_SLOTS },
                        ].map(({ label, slots }) => (
                          <div key={label}>
                            <h4 className="text-xs font-black text-[#5a403e] uppercase tracking-widest mb-4 flex items-center gap-2">
                              <span className="w-2 h-2 bg-[#705d00] inline-block" />
                              {label}
                            </h4>
                            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                              {slots.map(t => {
                                const booked = BOOKED_SLOTS.includes(t);
                                const picked = selTime === t;
                                return (
                                  <button
                                    key={t}
                                    disabled={booked}
                                    onClick={() => setSelTime(t)}
                                    className={`py-3 px-4 font-bold text-sm text-center transition-all relative
                                      ${booked  ? 'bg-[#e8e8e8] text-[#5a403e] cursor-not-allowed opacity-50 line-through' :
                                        picked  ? 'bg-[#8f000d] text-white shadow-md' :
                                                  'border border-[#8f000d] text-[#8f000d] hover:bg-[#8f000d] hover:text-white'}`}
                                  >
                                    {t}
                                    {picked && (
                                      <span className="absolute -top-1 -right-1 flex h-3 w-3">
                                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#705d00] opacity-75" />
                                        <span className="relative inline-flex rounded-full h-3 w-3 bg-[#705d00]" />
                                      </span>
                                    )}
                                  </button>
                                );
                              })}
                            </div>
                          </div>
                        ))}
                      </div>

                      {/* Legend */}
                      <div className="mt-8 pt-6 border-t border-[#e2beba]/30 flex flex-wrap gap-6">
                        {[
                          { cls: 'border border-[#8f000d]',  label: 'Còn trống' },
                          { cls: 'bg-[#8f000d]',             label: 'Đang chọn' },
                          { cls: 'bg-[#e8e8e8]',             label: 'Đã đặt'    },
                        ].map(({ cls, label }) => (
                          <div key={label} className="flex items-center gap-2">
                            <div className={`w-4 h-4 ${cls}`} />
                            <span className="text-[10px] font-bold uppercase text-[#5a403e]">{label}</span>
                          </div>
                        ))}
                      </div>
                    </>
                  )}
                </section>
              </>
            )}

            {/* ════ STEP 3 ════ */}
            {step === 3 && (
              <section className="bg-[#f3f3f3] p-4 md:p-8 shadow-sm space-y-6">
                <h2 className="text-base font-bold text-[#1a1c1c] flex items-center gap-2">
                  <CheckCircle className="w-5 h-5 text-[#8f000d]" />
                  Xác nhận thông tin
                </h2>

                {/* Summary */}
                <div className="bg-white p-6 border-l-4 border-[#8f000d] space-y-3">
                  {[
                    { label: 'Cơ quan',   value: agencyName },
                    { label: 'Dịch vụ',   value: SERVICES.find(s => s.code === serviceCode)?.label ?? serviceCode },
                    { label: 'Ngày hẹn',  value: fmtDate(selDate) },
                    { label: 'Giờ hẹn',   value: selTime },
                  ].map(({ label, value }) => (
                    <div key={label} className="flex items-start gap-4">
                      <span className="text-[10px] font-bold uppercase text-[#5a403e] tracking-wider w-24 shrink-0 pt-0.5">{label}</span>
                      <span className="text-sm font-semibold text-[#1a1c1c]">{value}</span>
                    </div>
                  ))}
                </div>

                {/* Personal info */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                  <div>
                    <label className={labelCls}>Họ và tên <span className="text-[#8f000d]">*</span></label>
                    <input className={inputCls} value={fullName} onChange={e => setFullName(e.target.value)} placeholder="Nguyễn Văn A" />
                  </div>
                  <div>
                    <label className={labelCls}>Số điện thoại <span className="text-[#8f000d]">*</span></label>
                    <input className={inputCls} value={phone} onChange={e => setPhone(e.target.value)} placeholder="0xxxxxxxxx" />
                  </div>
                  <div className="md:col-span-2">
                    <label className={labelCls}>Ghi chú (tùy chọn)</label>
                    <input className={inputCls} value={note} onChange={e => setNote(e.target.value)} placeholder="Thông tin bổ sung..." />
                  </div>
                </div>

                {error && (
                  <div className="p-4 bg-red-50 border-l-4 border-[#8f000d] flex items-center gap-3 text-sm text-[#8f000d]">
                    <AlertCircle className="w-4 h-4 shrink-0" />
                    {error}
                  </div>
                )}
              </section>
            )}

            {/* ── Action footer ── */}
            <footer className="pt-8 border-t border-[#e2beba] flex flex-col sm:flex-row justify-between items-center gap-4">
              <button
                onClick={() => step === 1 ? onNavigate('appointment') : setStep(s => s - 1)}
                className="w-full sm:w-auto px-10 py-4 bg-[#e8e8e8] text-[#1a1c1c] font-black uppercase tracking-widest text-xs hover:bg-[#e2e2e2] transition-all flex items-center justify-center gap-2 group"
              >
                <ArrowLeft className="w-4 h-4 group-hover:-translate-x-1 transition-transform" />
                Quay lại
              </button>
              {step < 3 ? (
                <button
                  onClick={() => setStep(s => s + 1)}
                  disabled={step === 1 ? !canStep1 : !canStep2}
                  className="w-full sm:w-auto px-12 py-4 bg-[#8f000d] text-white font-black uppercase tracking-widest text-xs shadow-lg hover:bg-[#b22222] disabled:opacity-40 active:scale-95 transition-all flex items-center justify-center gap-2 group"
                >
                  Xác nhận &amp; Tiếp tục
                  <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                </button>
              ) : (
                <button
                  onClick={handleSubmit}
                  disabled={loading}
                  className="w-full sm:w-auto px-12 py-4 bg-[#8f000d] text-white font-black uppercase tracking-widest text-xs shadow-lg hover:bg-[#b22222] disabled:opacity-40 active:scale-95 transition-all flex items-center justify-center gap-2"
                >
                  {loading
                    ? <><span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />Đang gửi...</>
                    : <><CheckCircle className="w-4 h-4" />Hoàn tất đặt lịch</>}
                </button>
              )}
            </footer>
          </div>

          {/* ── Right: sticky sidebar ── */}
          <div className="lg:col-span-4 sticky top-24 space-y-6">

            {/* Summary card */}
            <div className="bg-[#f3f3f3] overflow-hidden shadow-sm">
              <div className="bg-[#8f000d] p-4 flex items-center gap-3">
                <ClipboardList className="w-5 h-5 text-[#ffe16d]" />
                <h3 className="text-white font-extrabold uppercase tracking-widest text-sm">Thông tin tóm tắt</h3>
              </div>
              <div className="p-6 space-y-5">
                <div>
                  <label className="text-[10px] font-black text-[#5a403e] uppercase tracking-widest block mb-1">Cơ quan thực hiện</label>
                  <p className="text-sm font-bold text-[#8f000d]">{agencyName || '—'}</p>
                </div>
                <div>
                  <label className="text-[10px] font-black text-[#5a403e] uppercase tracking-widest block mb-1">Thủ tục hành chính</label>
                  <p className="text-sm font-bold text-[#1a1c1c]">{SERVICES.find(s => s.code === serviceCode)?.label ?? '—'}</p>
                </div>
                {(selDate || selTime) && (
                  <div className="pt-5 border-t border-[#e2beba]/50 space-y-4">
                    <div className="flex justify-between items-start">
                      <div>
                        <label className="text-[10px] font-black text-[#5a403e] uppercase tracking-widest block mb-1">Ngày hẹn dự kiến</label>
                        <p className="text-sm font-bold text-[#8f000d]">{selDate ? fmtDate(selDate) : '—'}</p>
                      </div>
                      {step > 2 && <button onClick={() => setStep(2)} className="text-[#8f000d] hover:underline text-[10px] font-black uppercase">Sửa</button>}
                    </div>
                    {selTime && (
                      <div className="flex justify-between items-start">
                        <div>
                          <label className="text-[10px] font-black text-[#5a403e] uppercase tracking-widest block mb-1">Thời gian</label>
                          <p className="text-sm font-bold text-[#8f000d]">{selTime}</p>
                        </div>
                        {step > 2 && <button onClick={() => setStep(2)} className="text-[#8f000d] hover:underline text-[10px] font-black uppercase">Sửa</button>}
                      </div>
                    )}
                  </div>
                )}
                <div className="bg-[#ffe16d]/30 p-4 border-l-2 border-[#705d00]">
                  <p className="text-[11px] leading-relaxed text-[#544600] font-semibold italic">
                    * Vui lòng có mặt trước 15 phút so với giờ hẹn để hoàn tất các thủ tục chuẩn bị.
                  </p>
                </div>
              </div>
              <div className="h-1 bg-gradient-to-r from-[#8f000d] via-[#705d00] to-[#8f000d]" />
            </div>

            {/* Heritage card */}
            <div className="h-32 relative overflow-hidden bg-[#8f000d] shadow-inner flex items-center justify-center">
              <div className="flex flex-col items-center justify-center p-6 text-center">
                <ShieldCheck className="w-8 h-8 text-[#ffe16d] mb-2" />
                <p className="text-white text-[10px] font-bold uppercase tracking-[0.2em]">Dịch vụ công minh bạch</p>
              </div>
            </div>

            {/* Step 1 only: notes + hotline */}
            {step === 1 && (
              <>
                <div className="bg-white p-6 border-l-4 border-[#705d00] shadow-sm">
                  <h3 className="text-sm font-bold text-[#1a1c1c] flex items-center gap-2 mb-4">
                    <Info className="w-4 h-4 text-[#705d00]" />
                    Lưu ý khi đặt lịch
                  </h3>
                  <ul className="space-y-3 text-sm text-[#5a403e]">
                    {[
                      { icon: CheckCircle, text: 'Có mặt ít nhất 15 phút trước giờ hẹn.' },
                      { icon: FileText,    text: 'Chuẩn bị đầy đủ hồ sơ gốc và bản sao.' },
                      { icon: QrCode,      text: 'Mã QR xác nhận sẽ gửi qua SMS/Email.' },
                      { icon: XCircle,     text: 'Hủy/dời lịch ít nhất 02 tiếng trước.' },
                    ].map(({ icon: Icon, text }, i) => (
                      <li key={i} className="flex gap-3">
                        <Icon className="w-4 h-4 text-[#8f000d] shrink-0 mt-0.5" />
                        <span className="text-xs">{text}</span>
                      </li>
                    ))}
                  </ul>
                </div>
                <div className="bg-[#b22222] p-6">
                  <h4 className="text-xs font-black text-[#ffc8c2] uppercase tracking-widest mb-2">Tổng đài hỗ trợ</h4>
                  <div className="text-2xl font-bold text-white flex items-center gap-2">
                    <Phone className="w-6 h-6" />1900 6060
                  </div>
                  <p className="text-xs text-white/80 mt-1">Hỗ trợ kỹ thuật 24/7</p>
                </div>
              </>
            )}
          </div>

        </div>
      </main>
    </div>
  );
}
