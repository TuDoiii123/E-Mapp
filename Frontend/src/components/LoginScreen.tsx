import React, { useState } from 'react';
import { Eye, EyeOff, ShieldCheck, CreditCard, Lock, AlertCircle, ArrowRight } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

interface Props {
  onLogin: () => void;
  onNavigate?: (screen: string) => void;
}

const P = '#8f000d';

const patternStyle: React.CSSProperties = {
  backgroundImage:
    'radial-gradient(rgba(255,255,255,0.15) 0.5px, transparent 0.5px)',
  backgroundSize: '18px 18px',
};

export function LoginScreen({ onLogin, onNavigate }: Props) {
  const [cccd, setCccd]           = useState('');
  const [password, setPassword]   = useState('');
  const [showPwd, setShowPwd]     = useState(false);
  const [error, setError]         = useState('');
  const [loading, setLoading]     = useState(false);
  const { login } = useAuth();

  const handleLogin = async () => {
    if (!cccd || !password) { setError('Vui lòng nhập đầy đủ thông tin'); return; }
    setError(''); setLoading(true);
    try {
      await login(cccd, password);
      onLogin();
    } catch (e: any) {
      setError(e.message || 'Đăng nhập thất bại. Vui lòng thử lại.');
    } finally { setLoading(false); }
  };

  return (
    <div className="min-h-screen flex flex-col"
      style={{ background: 'linear-gradient(160deg, #1c0003 0%, #8f000d 55%, #c0392b 100%)' }}>

      {/* Dot overlay */}
      <div className="absolute inset-0 pointer-events-none" style={patternStyle} />

      {/* ── Brand ─────────────────────────────────────────────────────────── */}
      <div className="relative z-10 flex flex-col items-center justify-center pt-16 pb-10 px-6">
        <div className="w-20 h-20 rounded-3xl bg-white/10 border-2 border-white/20 backdrop-blur
          flex items-center justify-center mb-5 shadow-2xl">
          <ShieldCheck className="w-10 h-10 text-white" />
        </div>
        <h1 className="text-2xl font-black text-white tracking-tight">Cổng Dịch vụ công</h1>
        <p className="text-white/60 text-sm mt-1">Đăng nhập bằng Căn cước công dân</p>
      </div>

      {/* ── Form card ─────────────────────────────────────────────────────── */}
      <div className="relative z-10 flex-1 bg-white rounded-t-[2rem] px-6 pt-8 pb-10 shadow-2xl">

        <h2 className="text-xl font-black text-gray-900 mb-1">Đăng nhập</h2>
        <p className="text-sm text-gray-400 mb-7">Chào mừng bạn trở lại 👋</p>

        {/* Error */}
        {error && (
          <div className="flex items-center gap-2.5 bg-red-50 border border-red-200 rounded-2xl
            px-4 py-3 mb-5 text-sm text-red-700">
            <AlertCircle className="w-4 h-4 shrink-0" />
            {error}
          </div>
        )}

        {/* CCCD */}
        <div className="mb-4">
          <label className="text-[10px] font-bold uppercase tracking-widest text-gray-400 mb-1.5 block">
            Số CCCD
          </label>
          <div className="flex items-center gap-3 bg-gray-50 rounded-2xl px-4 h-14
            border border-gray-100 focus-within:border-[#8f000d] transition-colors">
            <CreditCard className="w-4 h-4 text-gray-300 shrink-0" />
            <input
              type="text"
              inputMode="numeric"
              placeholder="Nhập 12 chữ số CCCD"
              value={cccd}
              maxLength={12}
              onChange={e => { setCccd(e.target.value.replace(/\D/g, '')); setError(''); }}
              onKeyDown={e => e.key === 'Enter' && handleLogin()}
              className="flex-1 bg-transparent text-sm text-gray-800 outline-none placeholder:text-gray-300
                font-mono tracking-wide"
            />
          </div>
        </div>

        {/* Password */}
        <div className="mb-7">
          <label className="text-[10px] font-bold uppercase tracking-widest text-gray-400 mb-1.5 block">
            Mật khẩu
          </label>
          <div className="flex items-center gap-3 bg-gray-50 rounded-2xl px-4 h-14
            border border-gray-100 focus-within:border-[#8f000d] transition-colors">
            <Lock className="w-4 h-4 text-gray-300 shrink-0" />
            <input
              type={showPwd ? 'text' : 'password'}
              placeholder="Nhập mật khẩu"
              value={password}
              onChange={e => { setPassword(e.target.value); setError(''); }}
              onKeyDown={e => e.key === 'Enter' && handleLogin()}
              className="flex-1 bg-transparent text-sm text-gray-800 outline-none placeholder:text-gray-300"
            />
            <button onClick={() => setShowPwd(v => !v)}
              className="text-gray-300 hover:text-gray-500 transition-colors">
              {showPwd ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
            </button>
          </div>
        </div>

        {/* Login button */}
        <button
          onClick={handleLogin}
          disabled={!cccd || !password || loading}
          className="w-full h-14 rounded-2xl text-white font-bold text-sm flex items-center
            justify-center gap-2 hover:opacity-90 active:scale-[.98] transition-all
            disabled:opacity-40 shadow-lg shadow-red-900/30"
          style={{ background: `linear-gradient(135deg, ${P} 0%, #c0392b 100%)` }}
        >
          {loading ? (
            <span className="flex items-center gap-2">
              <span className="w-4 h-4 border-2 border-white/40 border-t-white rounded-full animate-spin" />
              Đang đăng nhập...
            </span>
          ) : (
            <>Đăng nhập <ArrowRight className="w-4 h-4" /></>
          )}
        </button>

        {/* Links */}
        <div className="flex items-center justify-between mt-5">
          <button
            onClick={() => onNavigate?.('forgot-password')}
            className="text-sm text-gray-400 hover:text-[#8f000d] transition-colors"
          >
            Quên mật khẩu?
          </button>
          <button
            onClick={() => onNavigate?.('register')}
            className="text-sm font-bold hover:opacity-80 transition-opacity"
            style={{ color: P }}
          >
            Tạo tài khoản
          </button>
        </div>

        {/* Footer */}
        <div className="mt-10 pt-6 border-t border-gray-100 text-center">
          <p className="text-xs text-gray-400">Cần hỗ trợ? Hotline <span className="font-bold text-gray-600">1900 1234</span></p>
        </div>
      </div>
    </div>
  );
}
