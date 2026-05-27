import React, { useState } from 'react';
import {
  ShieldCheck, ChevronLeft, CreditCard, User, Calendar,
  Phone, Mail, Lock, Eye, EyeOff, Check, AlertCircle, ArrowRight,
} from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';

interface Props { onNavigate: (screen: string) => void }

const P = '#8f000d';

const patternStyle: React.CSSProperties = {
  backgroundImage: 'radial-gradient(rgba(255,255,255,0.15) 0.5px, transparent 0.5px)',
  backgroundSize: '18px 18px',
};

/* ── Shared field component ─────────────────────────────────────────────── */
function Field({
  label, icon: Icon, type = 'text', placeholder, value, onChange,
  maxLength, disabled, right,
}: {
  label: string; icon: any; type?: string; placeholder: string;
  value: string; onChange: (v: string) => void;
  maxLength?: number; disabled?: boolean; right?: React.ReactNode;
}) {
  return (
    <div>
      <label className="text-[10px] font-bold uppercase tracking-widest text-gray-400 mb-1.5 block">
        {label}
      </label>
      <div className="flex items-center gap-3 bg-gray-50 rounded-2xl px-4 h-13
        border border-gray-100 focus-within:border-[#8f000d] transition-colors">
        <Icon className="w-4 h-4 text-gray-300 shrink-0" />
        <input
          type={type}
          placeholder={placeholder}
          value={value}
          maxLength={maxLength}
          disabled={disabled}
          onChange={e => onChange(e.target.value)}
          className="flex-1 bg-transparent text-sm text-gray-800 outline-none placeholder:text-gray-300 py-3.5"
        />
        {right}
      </div>
    </div>
  );
}

/* ── Password strength dot ──────────────────────────────────────────────── */
function PwdHint({ ok, text }: { ok: boolean; text: string }) {
  return (
    <div className={`flex items-center gap-1.5 text-[11px] ${ok ? 'text-green-600' : 'text-gray-400'}`}>
      <Check className={`w-3 h-3 ${ok ? '' : 'opacity-30'}`} /> {text}
    </div>
  );
}

export function RegisterScreen({ onNavigate }: Props) {
  const [step, setStep] = useState(1);
  const [form, setForm] = useState({
    cccdNumber: '', fullName: '', dateOfBirth: '',
    phone: '', email: '', password: '', confirmPassword: '',
  });
  const [showPwd, setShowPwd]   = useState(false);
  const [showCPwd, setShowCPwd] = useState(false);
  const [otp, setOtp]           = useState('');
  const [agreeTerms, setAgree]  = useState(false);
  const [error, setError]       = useState('');
  const [loading, setLoading]   = useState(false);
  const { register } = useAuth();

  const set = (k: string) => (v: string) => {
    if (k === 'cccdNumber') v = v.replace(/\D/g, '').slice(0, 12);
    if (k === 'phone')      v = v.replace(/\D/g, '').slice(0, 11);
    setForm(f => ({ ...f, [k]: v }));
    setError('');
  };

  const pwReq = {
    length:    form.password.length >= 8,
    upper:     /[A-Z]/.test(form.password),
    number:    /\d/.test(form.password),
    special:   /[!@#$%^&*(),.?":{}|<>]/.test(form.password),
  };
  const pwValid = Object.values(pwReq).every(Boolean);

  const handleNext = async () => {
    if (step === 1) {
      if (form.cccdNumber.length !== 12) { setError('Số CCCD phải có 12 chữ số'); return; }
      if (form.fullName.length < 2)      { setError('Họ và tên phải ít nhất 2 ký tự'); return; }
      if (!form.dateOfBirth)             { setError('Vui lòng chọn ngày sinh'); return; }
      if (form.phone.length < 10)        { setError('Số điện thoại không hợp lệ'); return; }
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) { setError('Email không hợp lệ'); return; }
      if (!pwValid)                      { setError('Mật khẩu chưa đủ mạnh'); return; }
      if (form.password !== form.confirmPassword) { setError('Mật khẩu xác nhận không khớp'); return; }
      if (!agreeTerms)                   { setError('Vui lòng đồng ý điều khoản'); return; }
      setError(''); setStep(2);
    } else if (step === 2) {
      if (otp.length !== 6) { setError('Vui lòng nhập mã OTP 6 số'); return; }
      setError(''); setLoading(true);
      try {
        await register({ ...form, otp, useVNeID: false });
        setStep(3);
      } catch (e: any) { setError(e.message || 'Đăng ký thất bại'); }
      finally { setLoading(false); }
    } else {
      onNavigate('login');
    }
  };

  const STEP_LABELS = ['Thông tin', 'Xác thực OTP', 'Hoàn tất'];

  return (
    <div className="min-h-screen flex flex-col"
      style={{ background: 'linear-gradient(160deg, #1c0003 0%, #8f000d 55%, #c0392b 100%)' }}>

      <div className="absolute inset-0 pointer-events-none" style={patternStyle} />

      {/* ── Brand + back ──────────────────────────────────────────────────── */}
      <div className="relative z-10 px-4 pt-12 pb-8">
        <button
          onClick={() => step === 1 ? onNavigate('login') : setStep(s => s - 1)}
          className="w-9 h-9 rounded-full bg-white/10 flex items-center justify-center mb-6
            hover:bg-white/20 transition-colors"
        >
          <ChevronLeft className="w-5 h-5 text-white" />
        </button>

        <div className="flex items-center gap-3 mb-2">
          <div className="w-10 h-10 rounded-2xl bg-white/10 border border-white/20
            flex items-center justify-center">
            <ShieldCheck className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-lg font-black text-white leading-tight">Tạo tài khoản</h1>
            <p className="text-white/50 text-xs">Cổng Dịch vụ công</p>
          </div>
        </div>

        {/* Step pills */}
        <div className="flex items-center gap-2 mt-5">
          {STEP_LABELS.map((label, i) => {
            const idx = i + 1;
            const done    = idx < step;
            const current = idx === step;
            return (
              <React.Fragment key={idx}>
                <div className={`flex items-center gap-1.5 px-3 py-1 rounded-full text-[10px] font-bold transition-all
                  ${current ? 'bg-white text-[#8f000d]'
                  : done    ? 'bg-white/20 text-white'
                  :           'bg-white/10 text-white/40'}`}>
                  {done
                    ? <Check className="w-3 h-3" />
                    : <span className="w-3 h-3 rounded-full border flex items-center justify-center text-[8px]
                        font-black border-current">{idx}</span>}
                  <span className={done ? '' : ''}>{label}</span>
                </div>
                {i < 2 && <div className={`flex-1 h-px ${idx < step ? 'bg-white/40' : 'bg-white/10'}`} />}
              </React.Fragment>
            );
          })}
        </div>
      </div>

      {/* ── Form card ─────────────────────────────────────────────────────── */}
      <div className="relative z-10 flex-1 bg-white rounded-t-[2rem] px-6 pt-7 pb-10 shadow-2xl
        overflow-y-auto">

        {/* Error */}
        {error && (
          <div className="flex items-center gap-2.5 bg-red-50 border border-red-200 rounded-2xl
            px-4 py-3 mb-5 text-sm text-red-700">
            <AlertCircle className="w-4 h-4 shrink-0" /> {error}
          </div>
        )}

        {/* ── Step 1 ─────────────────────────────────────────────────────── */}
        {step === 1 && (
          <div className="space-y-4">
            <Field label="Số CCCD *" icon={CreditCard} placeholder="12 chữ số"
              value={form.cccdNumber} onChange={set('cccdNumber')} maxLength={12} />
            <Field label="Họ và tên *" icon={User} placeholder="Nguyễn Văn A"
              value={form.fullName} onChange={set('fullName')} />
            <Field label="Ngày sinh *" icon={Calendar} type="date" placeholder=""
              value={form.dateOfBirth} onChange={set('dateOfBirth')} />
            <Field label="Số điện thoại *" icon={Phone} type="tel" placeholder="09xxxxxxxx"
              value={form.phone} onChange={set('phone')} maxLength={11} />
            <Field label="Email *" icon={Mail} type="email" placeholder="example@email.com"
              value={form.email} onChange={set('email')} />

            {/* Password */}
            <Field label="Mật khẩu *" icon={Lock} type={showPwd ? 'text' : 'password'}
              placeholder="Ít nhất 8 ký tự" value={form.password} onChange={set('password')}
              right={
                <button onClick={() => setShowPwd(v => !v)}
                  className="text-gray-300 hover:text-gray-500">
                  {showPwd ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              }
            />
            {form.password && (
              <div className="grid grid-cols-2 gap-1 -mt-1 px-1">
                <PwdHint ok={pwReq.length}  text="≥ 8 ký tự" />
                <PwdHint ok={pwReq.upper}   text="Chữ hoa" />
                <PwdHint ok={pwReq.number}  text="Chữ số" />
                <PwdHint ok={pwReq.special} text="Ký tự đặc biệt" />
              </div>
            )}

            {/* Confirm password */}
            <Field label="Xác nhận mật khẩu *" icon={Lock} type={showCPwd ? 'text' : 'password'}
              placeholder="Nhập lại mật khẩu" value={form.confirmPassword} onChange={set('confirmPassword')}
              right={
                <button onClick={() => setShowCPwd(v => !v)}
                  className="text-gray-300 hover:text-gray-500">
                  {showCPwd ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              }
            />
            {form.confirmPassword && form.password !== form.confirmPassword && (
              <p className="text-xs text-red-500 -mt-1 px-1">Mật khẩu không khớp</p>
            )}

            {/* Terms */}
            <div className="flex items-start gap-3 bg-gray-50 rounded-2xl p-4">
              <button
                onClick={() => setAgree(v => !v)}
                className={`w-5 h-5 rounded-md border-2 flex items-center justify-center shrink-0 mt-0.5 transition-colors
                  ${agreeTerms ? 'border-[#8f000d] bg-[#8f000d]' : 'border-gray-300'}`}
              >
                {agreeTerms && <Check className="w-3 h-3 text-white" />}
              </button>
              <p className="text-xs text-gray-500 leading-relaxed">
                Tôi đồng ý với{' '}
                <span className="text-[#8f000d] font-semibold">Điều khoản sử dụng</span>
                {' '}và{' '}
                <span className="text-[#8f000d] font-semibold">Chính sách bảo mật</span>
              </p>
            </div>

            <button
              onClick={handleNext}
              disabled={!form.cccdNumber || !form.fullName || !form.phone || !form.email
                || !pwValid || form.password !== form.confirmPassword || !agreeTerms}
              className="w-full h-14 rounded-2xl text-white font-bold text-sm flex items-center
                justify-center gap-2 hover:opacity-90 active:scale-[.98] transition-all
                disabled:opacity-40 shadow-lg shadow-red-900/30"
              style={{ background: `linear-gradient(135deg, ${P} 0%, #c0392b 100%)` }}
            >
              Tiếp tục <ArrowRight className="w-4 h-4" />
            </button>

            <p className="text-center text-sm text-gray-400">
              Đã có tài khoản?{' '}
              <button onClick={() => onNavigate('login')}
                className="font-bold" style={{ color: P }}>Đăng nhập</button>
            </p>
          </div>
        )}

        {/* ── Step 2 ─────────────────────────────────────────────────────── */}
        {step === 2 && (
          <div className="space-y-6">
            <div className="text-center">
              <div className="w-16 h-16 rounded-2xl mx-auto mb-4 flex items-center justify-center"
                style={{ backgroundColor: P + '18' }}>
                <Phone className="w-8 h-8" style={{ color: P }} />
              </div>
              <h2 className="text-lg font-black text-gray-900">Xác thực OTP</h2>
              <p className="text-sm text-gray-400 mt-1">
                Mã đã gửi tới <span className="font-semibold text-gray-700">{form.phone}</span>
              </p>
            </div>

            <div>
              <label className="text-[10px] font-bold uppercase tracking-widest text-gray-400 mb-1.5 block">
                Mã OTP (6 chữ số)
              </label>
              <input
                type="text"
                inputMode="numeric"
                placeholder="• • • • • •"
                value={otp}
                maxLength={6}
                onChange={e => { setOtp(e.target.value.replace(/\D/g, '').slice(0, 6)); setError(''); }}
                className="w-full h-16 bg-gray-50 border border-gray-100 rounded-2xl text-center
                  text-2xl font-black tracking-[0.5em] text-gray-800 outline-none
                  focus:border-[#8f000d] transition-colors"
              />
            </div>

            <button
              onClick={handleNext}
              disabled={otp.length !== 6 || loading}
              className="w-full h-14 rounded-2xl text-white font-bold text-sm flex items-center
                justify-center gap-2 hover:opacity-90 active:scale-[.98] transition-all
                disabled:opacity-40 shadow-lg shadow-red-900/30"
              style={{ background: `linear-gradient(135deg, ${P} 0%, #c0392b 100%)` }}
            >
              {loading
                ? <><span className="w-4 h-4 border-2 border-white/40 border-t-white rounded-full animate-spin" /> Đang xử lý...</>
                : <>Xác thực <ArrowRight className="w-4 h-4" /></>}
            </button>

            <button className="w-full text-sm text-gray-400 hover:text-gray-600 transition-colors py-2">
              Gửi lại mã
            </button>
          </div>
        )}

        {/* ── Step 3 ─────────────────────────────────────────────────────── */}
        {step === 3 && (
          <div className="flex flex-col items-center text-center space-y-5 py-6">
            <div className="w-20 h-20 rounded-full bg-green-100 flex items-center justify-center">
              <Check className="w-10 h-10 text-green-600" />
            </div>
            <div>
              <h2 className="text-xl font-black text-gray-900">Đăng ký thành công!</h2>
              <p className="text-sm text-gray-400 mt-2">
                Tài khoản của bạn đã được tạo. Đăng nhập để bắt đầu sử dụng dịch vụ.
              </p>
            </div>
            <button
              onClick={handleNext}
              className="w-full h-14 rounded-2xl text-white font-bold text-sm flex items-center
                justify-center gap-2 hover:opacity-90 active:scale-[.98] transition-all shadow-lg shadow-red-900/30"
              style={{ background: `linear-gradient(135deg, ${P} 0%, #c0392b 100%)` }}
            >
              Đăng nhập ngay <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
