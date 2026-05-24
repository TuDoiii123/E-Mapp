import React, { useState } from 'react';
import {
  ShieldCheck, ChevronLeft, CreditCard, Phone, Mail,
  Lock, Eye, EyeOff, Check, AlertCircle, ArrowRight, KeyRound,
} from 'lucide-react';

interface Props { onNavigate: (screen: string) => void }

const P = '#8f000d';

const patternStyle: React.CSSProperties = {
  backgroundImage: 'radial-gradient(rgba(255,255,255,0.15) 0.5px, transparent 0.5px)',
  backgroundSize: '18px 18px',
};

const STEPS = ['Xác thực', 'Nhận mã', 'OTP', 'Mật khẩu mới'];

export function ForgotPasswordScreen({ onNavigate }: Props) {
  const [step, setStep]               = useState(1);
  const [cccd, setCccd]               = useState('');
  const [method, setMethod]           = useState<'sms' | 'email' | ''>('');
  const [otp, setOtp]                 = useState('');
  const [newPwd, setNewPwd]           = useState('');
  const [confirmPwd, setConfirmPwd]   = useState('');
  const [showPwd, setShowPwd]         = useState(false);
  const [showCPwd, setShowCPwd]       = useState(false);
  const [error, setError]             = useState('');

  const pwReq = {
    length:  newPwd.length >= 8,
    upper:   /[A-Z]/.test(newPwd),
    number:  /\d/.test(newPwd),
    special: /[!@#$%^&*(),.?":{}|<>]/.test(newPwd),
  };
  const pwValid = Object.values(pwReq).every(Boolean);

  const handleNext = () => {
    setError('');
    if (step === 1) {
      if (cccd.length !== 12) { setError('Số CCCD phải đủ 12 chữ số'); return; }
      setStep(2);
    } else if (step === 2) {
      if (!method) { setError('Vui lòng chọn phương thức'); return; }
      setStep(3);
    } else if (step === 3) {
      if (otp.length !== 6) { setError('Vui lòng nhập mã 6 số'); return; }
      setStep(4);
    } else {
      if (!pwValid)              { setError('Mật khẩu chưa đủ mạnh'); return; }
      if (newPwd !== confirmPwd) { setError('Mật khẩu xác nhận không khớp'); return; }
      onNavigate('login');
    }
  };

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
            <KeyRound className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-lg font-black text-white leading-tight">Quên mật khẩu</h1>
            <p className="text-white/50 text-xs">Khôi phục tài khoản</p>
          </div>
        </div>

        {/* Step pills */}
        <div className="flex items-center gap-1.5 mt-5">
          {STEPS.map((label, i) => {
            const idx  = i + 1;
            const done = idx < step;
            const cur  = idx === step;
            return (
              <React.Fragment key={idx}>
                <div className={`flex items-center gap-1 px-2.5 py-1 rounded-full text-[9px] font-bold transition-all
                  ${cur  ? 'bg-white text-[#8f000d]'
                  : done ? 'bg-white/20 text-white'
                  :        'bg-white/10 text-white/40'}`}>
                  {done
                    ? <Check className="w-2.5 h-2.5" />
                    : <span className="w-2.5 h-2.5 rounded-full border border-current flex items-center justify-center text-[7px] font-black">{idx}</span>}
                  <span>{label}</span>
                </div>
                {i < 3 && <div className={`flex-1 h-px ${idx < step ? 'bg-white/40' : 'bg-white/10'}`} />}
              </React.Fragment>
            );
          })}
        </div>
      </div>

      {/* ── Form card ─────────────────────────────────────────────────────── */}
      <div className="relative z-10 flex-1 bg-white rounded-t-[2rem] px-6 pt-7 pb-10 shadow-2xl">

        {error && (
          <div className="flex items-center gap-2.5 bg-red-50 border border-red-200 rounded-2xl
            px-4 py-3 mb-5 text-sm text-red-700">
            <AlertCircle className="w-4 h-4 shrink-0" /> {error}
          </div>
        )}

        {/* ── Step 1: CCCD ─────────────────────────────────────────────── */}
        {step === 1 && (
          <div className="space-y-6">
            <div>
              <h2 className="text-xl font-black text-gray-900">Xác thực danh tính</h2>
              <p className="text-sm text-gray-400 mt-1">Nhập số CCCD để tìm tài khoản</p>
            </div>

            <div>
              <label className="text-[10px] font-bold uppercase tracking-widest text-gray-400 mb-1.5 block">
                Số CCCD
              </label>
              <div className="flex items-center gap-3 bg-gray-50 rounded-2xl px-4 h-14
                border border-gray-100 focus-within:border-[#8f000d] transition-colors">
                <CreditCard className="w-4 h-4 text-gray-300 shrink-0" />
                <input
                  type="text"
                  inputMode="numeric"
                  placeholder="12 chữ số CCCD"
                  value={cccd}
                  maxLength={12}
                  onChange={e => { setCccd(e.target.value.replace(/\D/g, '')); setError(''); }}
                  className="flex-1 bg-transparent text-sm text-gray-800 outline-none placeholder:text-gray-300 font-mono tracking-wide"
                />
              </div>
            </div>

            <button onClick={handleNext} disabled={cccd.length !== 12}
              className="w-full h-14 rounded-2xl text-white font-bold text-sm flex items-center
                justify-center gap-2 hover:opacity-90 active:scale-[.98] transition-all
                disabled:opacity-40 shadow-lg shadow-red-900/30"
              style={{ background: `linear-gradient(135deg, ${P} 0%, #c0392b 100%)` }}>
              Tiếp tục <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        )}

        {/* ── Step 2: Method ───────────────────────────────────────────── */}
        {step === 2 && (
          <div className="space-y-6">
            <div>
              <h2 className="text-xl font-black text-gray-900">Nhận mã xác thực</h2>
              <p className="text-sm text-gray-400 mt-1">Chọn phương thức nhận OTP</p>
            </div>

            <div className="space-y-3">
              {[
                { id: 'sms' as const,   Icon: Phone, label: 'SMS',   desc: 'Gửi mã đến số điện thoại ****1234' },
                { id: 'email' as const, Icon: Mail,  label: 'Email', desc: 'Gửi mã đến email n****@example.com' },
              ].map(m => (
                <button
                  key={m.id}
                  onClick={() => setMethod(m.id)}
                  className={`w-full flex items-center gap-4 p-4 rounded-2xl border-2 text-left transition-all
                    ${method === m.id
                      ? 'border-[#8f000d] bg-[#fff4f4]'
                      : 'border-gray-100 bg-gray-50 hover:border-gray-200'}`}
                >
                  <div className={`w-10 h-10 rounded-xl flex items-center justify-center shrink-0
                    ${method === m.id ? 'bg-[#8f000d]' : 'bg-white border border-gray-200'}`}>
                    <m.Icon className={`w-4 h-4 ${method === m.id ? 'text-white' : 'text-gray-400'}`} />
                  </div>
                  <div>
                    <p className={`text-sm font-bold ${method === m.id ? 'text-[#8f000d]' : 'text-gray-800'}`}>
                      {m.label}
                    </p>
                    <p className="text-xs text-gray-400 mt-0.5">{m.desc}</p>
                  </div>
                  {method === m.id && (
                    <div className="ml-auto w-5 h-5 rounded-full bg-[#8f000d] flex items-center justify-center">
                      <Check className="w-3 h-3 text-white" />
                    </div>
                  )}
                </button>
              ))}
            </div>

            <button onClick={handleNext} disabled={!method}
              className="w-full h-14 rounded-2xl text-white font-bold text-sm flex items-center
                justify-center gap-2 hover:opacity-90 active:scale-[.98] transition-all
                disabled:opacity-40 shadow-lg shadow-red-900/30"
              style={{ background: `linear-gradient(135deg, ${P} 0%, #c0392b 100%)` }}>
              Gửi mã xác thực <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        )}

        {/* ── Step 3: OTP ──────────────────────────────────────────────── */}
        {step === 3 && (
          <div className="space-y-6">
            <div className="text-center">
              <div className="w-16 h-16 rounded-2xl mx-auto mb-4 flex items-center justify-center"
                style={{ backgroundColor: P + '18' }}>
                {method === 'sms'
                  ? <Phone className="w-8 h-8" style={{ color: P }} />
                  : <Mail className="w-8 h-8"  style={{ color: P }} />}
              </div>
              <h2 className="text-xl font-black text-gray-900">Nhập mã OTP</h2>
              <p className="text-sm text-gray-400 mt-1">
                Mã đã gửi qua {method === 'sms' ? 'SMS ****1234' : 'email n****@example.com'}
              </p>
              <span className="inline-block mt-2 px-3 py-1 bg-amber-50 text-amber-700 text-xs font-bold rounded-full">
                Hết hạn sau 5 phút
              </span>
            </div>

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

            <button onClick={handleNext} disabled={otp.length !== 6}
              className="w-full h-14 rounded-2xl text-white font-bold text-sm flex items-center
                justify-center gap-2 hover:opacity-90 active:scale-[.98] transition-all
                disabled:opacity-40 shadow-lg shadow-red-900/30"
              style={{ background: `linear-gradient(135deg, ${P} 0%, #c0392b 100%)` }}>
              Xác thực <ArrowRight className="w-4 h-4" />
            </button>

            <button className="w-full text-sm text-gray-400 hover:text-gray-600 transition-colors py-2">
              Gửi lại mã
            </button>
          </div>
        )}

        {/* ── Step 4: New password ─────────────────────────────────────── */}
        {step === 4 && (
          <div className="space-y-5">
            <div>
              <h2 className="text-xl font-black text-gray-900">Mật khẩu mới</h2>
              <p className="text-sm text-gray-400 mt-1">Đặt mật khẩu mới cho tài khoản</p>
            </div>

            {/* New password */}
            <div>
              <label className="text-[10px] font-bold uppercase tracking-widest text-gray-400 mb-1.5 block">
                Mật khẩu mới
              </label>
              <div className="flex items-center gap-3 bg-gray-50 rounded-2xl px-4 h-14
                border border-gray-100 focus-within:border-[#8f000d] transition-colors">
                <Lock className="w-4 h-4 text-gray-300 shrink-0" />
                <input
                  type={showPwd ? 'text' : 'password'}
                  placeholder="Ít nhất 8 ký tự"
                  value={newPwd}
                  onChange={e => { setNewPwd(e.target.value); setError(''); }}
                  className="flex-1 bg-transparent text-sm text-gray-800 outline-none placeholder:text-gray-300"
                />
                <button onClick={() => setShowPwd(v => !v)} className="text-gray-300 hover:text-gray-500">
                  {showPwd ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
              {newPwd && (
                <div className="grid grid-cols-2 gap-1 mt-2 px-1">
                  {[
                    { ok: pwReq.length,  t: '≥ 8 ký tự' },
                    { ok: pwReq.upper,   t: 'Chữ hoa' },
                    { ok: pwReq.number,  t: 'Chữ số' },
                    { ok: pwReq.special, t: 'Ký tự đặc biệt' },
                  ].map(r => (
                    <div key={r.t} className={`flex items-center gap-1.5 text-[11px] ${r.ok ? 'text-green-600' : 'text-gray-400'}`}>
                      <Check className={`w-3 h-3 ${r.ok ? '' : 'opacity-30'}`} /> {r.t}
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Confirm */}
            <div>
              <label className="text-[10px] font-bold uppercase tracking-widest text-gray-400 mb-1.5 block">
                Xác nhận mật khẩu
              </label>
              <div className="flex items-center gap-3 bg-gray-50 rounded-2xl px-4 h-14
                border border-gray-100 focus-within:border-[#8f000d] transition-colors">
                <Lock className="w-4 h-4 text-gray-300 shrink-0" />
                <input
                  type={showCPwd ? 'text' : 'password'}
                  placeholder="Nhập lại mật khẩu"
                  value={confirmPwd}
                  onChange={e => { setConfirmPwd(e.target.value); setError(''); }}
                  className="flex-1 bg-transparent text-sm text-gray-800 outline-none placeholder:text-gray-300"
                />
                <button onClick={() => setShowCPwd(v => !v)} className="text-gray-300 hover:text-gray-500">
                  {showCPwd ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
              {confirmPwd && newPwd !== confirmPwd && (
                <p className="text-xs text-red-500 mt-1.5 px-1">Mật khẩu không khớp</p>
              )}
            </div>

            <button onClick={handleNext} disabled={!pwValid || newPwd !== confirmPwd}
              className="w-full h-14 rounded-2xl text-white font-bold text-sm flex items-center
                justify-center gap-2 hover:opacity-90 active:scale-[.98] transition-all
                disabled:opacity-40 shadow-lg shadow-red-900/30"
              style={{ background: `linear-gradient(135deg, ${P} 0%, #c0392b 100%)` }}>
              Đặt lại mật khẩu <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
