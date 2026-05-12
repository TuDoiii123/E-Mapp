import React, { useState, useRef, useEffect } from 'react';
import {
  Star, BarChart3, ArrowRight, CheckCircle, Upload,
  Info, CheckCircle2, FileImage, ArrowLeft, Building2,
  UserCheck, Clock, RefreshCw,
} from 'lucide-react';
import * as adminSvc from '../services/adminService';

interface EvaluationScreenProps {
  onNavigate: (screen: string) => void;
}

type TxStatus = 'evaluatable' | 'processing' | 'done';

interface Transaction {
  id:            string;
  applicationId: string;
  agency:        string;
  agencyShort:   string;
  service:       string;
  status:        TxStatus;
  code:          string;
  rating?:       number;
  updatedAt?:    string | null;
}

/* ── Star rating row ── */
function StarRow({
  value, onChange, size = 'md',
}: { value: number; onChange: (v: number) => void; size?: 'sm' | 'md' }) {
  return (
    <div className="flex gap-1">
      {[1, 2, 3, 4, 5].map((s) => (
        <button
          key={s}
          type="button"
          aria-label={`${s} sao`}
          onClick={() => onChange(s)}
          className={`transition-transform hover:scale-110 ${
            s <= value ? 'text-[#fdc003]' : 'text-[#de9ca4]'
          }`}
        >
          <Star className={`fill-current ${size === 'sm' ? 'w-5 h-5' : 'w-6 h-6'}`} />
        </button>
      ))}
    </div>
  );
}

/* ══════════════════════════════════════════
   Main component
══════════════════════════════════════════ */
export function EvaluationScreen({ onNavigate }: EvaluationScreenProps) {
  const timeoutRef  = useRef<ReturnType<typeof setTimeout> | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    return () => { if (timeoutRef.current) clearTimeout(timeoutRef.current); };
  }, []);

  const [loading,     setLoading]    = useState(true);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [stats, setStats] = useState({ totalEvaluations: 0, avgRating: 0, satisfactionRate: 0 });

  const [activeTab,   setActiveTab]   = useState<'all' | 'pending' | 'done'>('all');
  const [evalTarget,  setEvalTarget]  = useState<Transaction | null>(null);

  const [submitted,     setSubmitted]     = useState(false);
  const [submitting,    setSubmitting]    = useState(false);
  const [submitError,   setSubmitError]   = useState('');
  const [comment,       setComment]       = useState('');
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);
  const [ratings, setRatings] = useState({ attitude: 0, time: 0, facilities: 0 });

  const avgRating = ratings.attitude && ratings.time && ratings.facilities
    ? (ratings.attitude + ratings.time + ratings.facilities) / 3 : 0;

  useEffect(() => {
    Promise.all([
      adminSvc.getEvaluations().catch(() => ({ data: { evaluatable: [], pastEvaluations: [] } })),
      adminSvc.getEvaluationStats().catch(() => ({ data: { totalEvaluations: 0, avgRating: 0, satisfactionRate: 0 } })),
    ]).then(([evalRes, statsRes]) => {
      const items: any[] = evalRes?.data?.evaluatable || [];
      setTransactions(items.map((item: any) => ({
        id:            item.id,
        applicationId: item.applicationId,
        agency:        item.agency || 'Cơ quan hành chính',
        agencyShort:   item.agency ? item.agency.split(',')[0].trim() : 'Cơ quan',
        service:       item.service || 'Thủ tục hành chính',
        status:        item.status as TxStatus,
        code:          item.code || item.id?.slice(0, 8).toUpperCase(),
        rating:        item.rating,
        updatedAt:     item.updatedAt,
      })));
      const sd = statsRes?.data;
      if (sd) setStats(sd);
    }).finally(() => setLoading(false));
  }, []);

  function openEval(tx: Transaction) {
    if (tx.status !== 'evaluatable') return;
    setEvalTarget(tx);
    setSubmitted(false);
    setSubmitError('');
    setRatings({ attitude: 0, time: 0, facilities: 0 });
    setComment('');
    setUploadedFiles([]);
  }

  async function handleSubmit() {
    if (!ratings.attitude || !ratings.time || !ratings.facilities || !evalTarget) return;
    setSubmitting(true);
    setSubmitError('');
    try {
      await adminSvc.submitEvaluation({
        applicationId:    evalTarget.applicationId,
        attitudeRating:   ratings.attitude,
        timeRating:       ratings.time,
        facilitiesRating: ratings.facilities,
        comment,
      });
      setSubmitted(true);
      // Update local state so the card shows 'done'
      setTransactions(prev => prev.map(t =>
        t.id === evalTarget.id
          ? { ...t, status: 'done', rating: Math.round((ratings.attitude + ratings.time + ratings.facilities) / 3) }
          : t
      ));
      timeoutRef.current = setTimeout(() => {
        setEvalTarget(null);
        setSubmitted(false);
        setRatings({ attitude: 0, time: 0, facilities: 0 });
        setComment('');
        setUploadedFiles([]);
      }, 2500);
    } catch (err: any) {
      setSubmitError(err.message || 'Gửi đánh giá thất bại. Vui lòng thử lại.');
    } finally {
      setSubmitting(false);
    }
  }

  function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    if (e.target.files) setUploadedFiles(Array.from(e.target.files));
  }

  const filtered = transactions.filter(tx =>
    activeTab === 'pending' ? tx.status === 'evaluatable' :
    activeTab === 'done'    ? tx.status === 'done' : true
  );

  /* ─────────────────── DETAIL VIEW ─────────────────── */
  if (evalTarget) {
    return (
      <div
        className="bg-[#fff4f4] text-[#4d2128] min-h-screen flex flex-col"
        style={{ fontFamily: "'Manrope', sans-serif" }}
      >
        {/* Header */}
        <header className="flex items-center gap-4 w-full px-6 md:px-10 py-4 bg-[#fff4f4]/80 backdrop-blur-md sticky top-0 z-40 border-b border-[#de9ca4]/20">
          <button
            onClick={() => setEvalTarget(null)}
            className="w-10 h-10 flex items-center justify-center rounded-full hover:bg-[#ffd9dd] transition-all text-[#9f364c]"
            aria-label="Quay lại"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div className="flex-1 min-w-0">
            <h1 className="text-base font-black text-[#4d2128] truncate">{evalTarget.agencyShort}</h1>
          </div>
        </header>

        <main className="flex-1 px-6 md:px-10 py-8 max-w-5xl mx-auto w-full">
          <div className="space-y-6">

            {/* Hero banner */}
            <div className="bg-white rounded-2xl p-6 border border-[#de9ca4]/10 relative overflow-hidden">
              <div className="absolute top-0 right-0 w-40 h-40 bg-[#b7131a]/5 rounded-full -mr-10 -mt-10 blur-3xl pointer-events-none" />
              <div className="relative z-10">
                <span className="text-xs font-black uppercase tracking-widest text-[#9f364c] block mb-1">
                  Đánh giá chất lượng dịch vụ
                </span>
                <h2 className="text-2xl font-extrabold text-[#4d2128] mb-2">{evalTarget.agencyShort}</h2>
                <div className="flex items-center gap-2 text-[#9f364c]">
                  <CheckCircle2 className="w-4 h-4" />
                  <span className="text-sm">
                    Thủ tục: <span className="font-bold text-[#b7131a]">{evalTarget.service}</span>
                  </span>
                </div>
                <div className="mt-2 text-right md:text-left">
                  <span className="text-xs text-[#824c54]/60 font-mono">Mã hồ sơ: {evalTarget.code}</span>
                </div>
              </div>
            </div>

            {/* Success state */}
            {submitted ? (
              <div className="bg-white rounded-2xl p-16 flex flex-col items-center text-center border border-[#de9ca4]/10">
                <div className="w-20 h-20 rounded-full bg-emerald-50 flex items-center justify-center mb-4">
                  <CheckCircle className="w-12 h-12 text-emerald-500" />
                </div>
                <h2 className="text-2xl font-black text-[#4d2128] mb-2">Cảm ơn bạn!</h2>
                <p className="text-[#9f364c] leading-relaxed max-w-md text-sm">
                  Đánh giá của bạn đã được gửi thành công. Những góp ý này sẽ giúp cải thiện chất lượng dịch vụ công.
                </p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">

                {/* Left: criteria + comment */}
                <div className="md:col-span-2 space-y-6">

                  {/* Criteria */}
                  <div className="bg-white rounded-2xl p-6 border border-[#de9ca4]/10">
                    <h3 className="text-base font-bold text-[#4d2128] mb-6 flex items-center gap-2">
                      <BarChart3 className="w-5 h-5 text-[#b7131a]" />
                      Tiêu chí đánh giá chính
                    </h3>
                    <div className="space-y-6">
                      {([
                        { key: 'attitude',   label: 'Thái độ phục vụ', Icon: UserCheck },
                        { key: 'time',       label: 'Thời gian xử lý', Icon: Clock     },
                        { key: 'facilities', label: 'Cơ sở vật chất',  Icon: Building2 },
                      ] as const).map(({ key, label, Icon }) => (
                        <div key={key} className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                          <div className="flex items-center gap-3">
                            <div className="w-10 h-10 bg-[#ffeced] rounded-xl flex items-center justify-center">
                              <Icon className="w-5 h-5 text-[#b7131a]" />
                            </div>
                            <span className="font-bold text-[#4d2128] text-sm">{label}</span>
                          </div>
                          <div className="flex items-center gap-3">
                            <StarRow
                              value={ratings[key]}
                              onChange={(v) => setRatings(r => ({ ...r, [key]: v }))}
                            />
                            {ratings[key] > 0 && (
                              <span className="text-xs text-[#9f364c] whitespace-nowrap hidden sm:block">
                                {['','Rất tệ','Tệ','Bình thường','Tốt','Xuất sắc'][ratings[key]]}
                              </span>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Comment */}
                  <div className="bg-white rounded-2xl p-6 border border-[#de9ca4]/10">
                    <label className="text-base font-bold text-[#4d2128] mb-3 block">
                      Nhận xét chi tiết
                    </label>
                    <textarea
                      rows={4}
                      value={comment}
                      onChange={e => setComment(e.target.value)}
                      placeholder="Vui lòng chia sẻ thêm ý kiến của bạn về quá trình thực hiện thủ tục..."
                      className="w-full bg-[#ffeced] border-none rounded-xl p-4 text-[#4d2128] placeholder:text-[#de9ca4] outline-none focus:ring-2 focus:ring-[#b7131a] resize-none text-sm"
                    />
                  </div>
                </div>

                {/* Right: upload + submit */}
                <div className="space-y-6">

                  {/* Upload evidence */}
                  <div className="bg-white rounded-2xl p-6 border border-[#de9ca4]/10 flex flex-col items-center text-center">
                    <div className="w-14 h-14 bg-[#ffeced] rounded-full flex items-center justify-center mb-3">
                      <Upload className="w-6 h-6 text-[#b7131a]" />
                    </div>
                    <h4 className="font-bold text-[#4d2128] text-sm mb-1">Tải lên bằng chứng</h4>
                    <p className="text-xs text-[#9f364c] mb-4 px-2">
                      Đính kèm ảnh phiếu tiếp nhận hoặc tài liệu liên quan.
                    </p>
                    <input
                      ref={fileInputRef}
                      type="file"
                      multiple
                      accept="image/*,.pdf"
                      aria-label="Tải lên bằng chứng"
                      className="hidden"
                      onChange={handleFileChange}
                    />
                    <button
                      onClick={() => fileInputRef.current?.click()}
                      className="w-full border-2 border-dashed border-[#de9ca4] p-4 rounded-xl bg-[#ffeced]/50 hover:bg-[#ffeced] transition-colors"
                    >
                      <div className="text-[10px] uppercase font-bold text-[#9f364c]">Chọn tệp tin</div>
                    </button>
                    {uploadedFiles.length > 0 && (
                      <div className="w-full mt-3 space-y-1">
                        {uploadedFiles.map((f, i) => (
                          <div key={i} className="flex items-center gap-2 text-xs text-[#9f364c] bg-[#ffeced] px-2 py-1.5 rounded-lg">
                            <FileImage className="w-3.5 h-3.5 text-[#b7131a] flex-shrink-0" />
                            <span className="truncate">{f.name}</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Average preview */}
                  {avgRating > 0 && (
                    <div className="bg-white rounded-2xl p-4 border border-[#de9ca4]/10 flex items-center justify-between">
                      <span className="text-[10px] font-black uppercase tracking-widest text-[#824c54]/60">Điểm TB</span>
                      <div className="flex items-center gap-2">
                        <div className="flex gap-0.5">
                          {[1,2,3,4,5].map(s => (
                            <Star key={s} className={`w-4 h-4 fill-current ${s <= Math.round(avgRating) ? 'text-[#fdc003]' : 'text-[#ffd2d6]'}`} />
                          ))}
                        </div>
                        <span className="text-sm font-bold text-[#4d2128]">{avgRating.toFixed(1)}</span>
                      </div>
                    </div>
                  )}

                  {submitError && (
                    <p className="text-xs text-red-600 text-center">{submitError}</p>
                  )}

                  {/* Submit */}
                  <button
                    onClick={handleSubmit}
                    disabled={!ratings.attitude || !ratings.time || !ratings.facilities || submitting}
                    className="w-full py-4 bg-gradient-to-br from-[#b7131a] to-[#ff766b] hover:opacity-90 text-white font-black uppercase tracking-widest text-sm shadow-lg shadow-[#b7131a]/20 active:scale-95 transition-all flex items-center justify-center gap-2 rounded-2xl disabled:opacity-40 disabled:pointer-events-none"
                  >
                    {submitting ? <RefreshCw className="w-4 h-4 animate-spin" /> : 'GỬI ĐÁNH GIÁ'}
                  </button>

                </div>
              </div>
            )}

            {/* Guidance note */}
            <div className="bg-[#ffeced] rounded-2xl p-5 flex items-start gap-3">
              <Info className="w-5 h-5 text-[#b7131a] flex-shrink-0 mt-0.5" />
              <p className="text-sm text-[#9f364c] leading-relaxed">
                Cảm ơn quý công dân đã đóng góp ý kiến. Thông tin phản hồi của quý vị sẽ được bảo mật và sử dụng để cải thiện chất lượng phục vụ tại các cơ quan hành chính nhà nước.
              </p>
            </div>

          </div>
        </main>
      </div>
    );
  }

  /* ─────────────────── LIST VIEW ─────────────────── */
  return (
    <div
      className="bg-[#fff4f4] text-[#4d2128] min-h-screen flex flex-col"
      style={{ fontFamily: "'Manrope', sans-serif" }}
    >
      {/* ── TopNavBar ── */}
      <header className="flex justify-between items-end w-full px-6 md:px-12 py-6 bg-[#fff4f4]/80 backdrop-blur-md sticky top-0 z-40 border-b border-[#de9ca4]/20">
        <div>
          <button
            onClick={() => onNavigate('home')}
            className="flex items-center gap-1.5 text-sm text-[#9f364c] hover:text-[#b7131a] transition-colors mb-2"
          >
            <ArrowLeft className="w-4 h-4" /> Trang chủ
          </button>
          <h1 className="text-3xl md:text-4xl font-bold text-[#4d2128] tracking-tight">
            Đánh giá cơ quan nhà nước
          </h1>
        </div>
        <div className="flex items-center gap-4">
          <button
            onClick={() => onNavigate('notifications')}
            className="p-2 bg-[#ffeced] rounded-full hover:bg-[#ffd9dd] transition-colors"
          >
            <span className="material-symbols-outlined text-[#4d2128]">notifications</span>
          </button>
        </div>
      </header>

      <main className="flex-1 px-6 md:px-12 py-10 max-w-6xl mx-auto w-full space-y-16">

        {/* ── KPI Cards ── */}
        <section className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* Average Rating */}
          <div className="bg-white p-8 rounded-xl shadow-[0px_20px_40px_rgba(77,33,40,0.06)] relative overflow-hidden group">
            <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
              <span className="material-symbols-outlined text-6xl">stars</span>
            </div>
            <p className="text-sm font-semibold text-[#9f364c] mb-4 uppercase tracking-wider">
              Điểm đánh giá trung bình
            </p>
            <div className="flex items-baseline gap-2">
              <h3 className="text-5xl font-black text-[#4d2128]">
                {loading ? '–' : stats.avgRating.toFixed(1)}
              </h3>
              <span className="text-xl font-medium text-[#9f364c]">/ 5.0</span>
            </div>
            {!loading && stats.avgRating > 0 && (
              <div className="flex mt-4 gap-0.5 text-[#fdc003]">
                {[1,2,3,4,5].map(s => (
                  <Star key={s} className={`w-5 h-5 fill-current ${s <= Math.round(stats.avgRating) ? 'text-[#fdc003]' : 'text-[#ffd2d6]'}`} />
                ))}
              </div>
            )}
          </div>

          {/* Total Evaluations */}
          <div className="bg-white p-8 rounded-xl shadow-[0px_20px_40px_rgba(77,33,40,0.06)] relative overflow-hidden group">
            <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
              <span className="material-symbols-outlined text-6xl">groups</span>
            </div>
            <p className="text-sm font-semibold text-[#9f364c] mb-4 uppercase tracking-wider">
              Tổng số đánh giá
            </p>
            <h3 className="text-5xl font-black text-[#4d2128]">
              {loading ? '–' : stats.totalEvaluations.toLocaleString('vi-VN')}
            </h3>
          </div>

          {/* Satisfaction Rate */}
          <div className="bg-white p-8 rounded-xl shadow-[0px_20px_40px_rgba(77,33,40,0.06)] relative overflow-hidden group">
            <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
              <span className="material-symbols-outlined text-6xl">sentiment_satisfied</span>
            </div>
            <p className="text-sm font-semibold text-[#9f364c] mb-4 uppercase tracking-wider">
              Mức độ hài lòng
            </p>
            <h3 className="text-5xl font-black text-[#4d2128]">
              {loading ? '–' : `${stats.satisfactionRate}%`}
            </h3>
            {!loading && (
              <div className="mt-6">
                <div className="h-2 w-full bg-[#ffd9dd] rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-[#b7131a] to-[#ff766b] rounded-full transition-all"
                    style={{ width: `${stats.satisfactionRate}%` }}
                  />
                </div>
                <div className="flex justify-between mt-2 text-[10px] font-bold text-[#9f364c] uppercase tracking-widest">
                  <span>Cần cải thiện</span>
                  <span>Tuyệt vời</span>
                </div>
              </div>
            )}
          </div>
        </section>

        {/* ── Transaction list ── */}
        <section>
          <div className="flex items-center justify-between mb-8">
            <h2 className="text-2xl font-bold text-[#4d2128] tracking-tight">Hồ sơ đã hoàn tất</h2>
            <div className="flex items-center gap-4">
              {(['all','pending','done'] as const).map((tab, i) => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`text-sm px-1 pb-0.5 transition-colors ${
                    activeTab === tab
                      ? 'font-bold text-[#b7131a] border-b-2 border-[#b7131a]'
                      : 'font-medium text-[#9f364c] hover:text-[#b7131a]'
                  }`}
                >
                  {['Tất cả', 'Chờ đánh giá', 'Đã đánh giá'][i]}
                </button>
              ))}
            </div>
          </div>

          {loading ? (
            <div className="flex justify-center py-12">
              <RefreshCw className="w-6 h-6 animate-spin text-[#9f364c]" />
            </div>
          ) : filtered.length === 0 ? (
            <div className="bg-white rounded-xl p-12 text-center text-[#9f364c]">
              <p className="text-lg font-bold mb-2">Chưa có hồ sơ nào</p>
              <p className="text-sm">Hồ sơ đã được duyệt sẽ xuất hiện ở đây để bạn đánh giá.</p>
              <button
                onClick={() => onNavigate('submit')}
                className="mt-6 px-6 py-3 bg-gradient-to-br from-[#b7131a] to-[#ff766b] text-white rounded-xl font-bold text-sm"
              >
                Nộp hồ sơ mới
              </button>
            </div>
          ) : (
            <div className="bg-[#ffeced] rounded-xl p-2 space-y-2">
              {filtered.map((tx) => (
                <div
                  key={tx.id}
                  className={`bg-white rounded-lg p-6 flex flex-col md:flex-row items-center justify-between transition-all group
                    ${tx.status === 'evaluatable' ? 'hover:bg-[#fff4f4] cursor-pointer' : ''}
                    ${tx.status === 'processing'  ? 'opacity-70' : ''}
                  `}
                  onClick={() => tx.status === 'evaluatable' && openEval(tx)}
                >
                  <div className="flex items-center gap-6 mb-4 md:mb-0">
                    <div className={`w-14 h-14 rounded-xl bg-[#ffd9dd] flex items-center justify-center ${
                      tx.status === 'processing' ? 'text-[#9f364c]/40' : 'text-[#b7131a]'
                    } ${tx.status === 'evaluatable' ? 'group-hover:scale-105' : ''} transition-transform`}>
                      <span className="material-symbols-outlined text-3xl" style={{ fontVariationSettings: "'FILL' 0" }}>
                        assignment
                      </span>
                    </div>
                    <div>
                      <h4 className="text-lg font-bold text-[#4d2128] group-hover:text-[#b7131a] transition-colors">
                        {tx.agency || 'Cơ quan hành chính'}
                      </h4>
                      <p className="text-sm text-[#9f364c] mt-0.5">{tx.service}</p>
                      <div className="flex items-center gap-3 mt-1 flex-wrap">
                        {tx.status === 'evaluatable' && (
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold bg-green-100 text-green-800">
                            Có thể đánh giá
                          </span>
                        )}
                        {tx.status === 'done' && (
                          <>
                            <div className="flex gap-0.5 text-[#fdc003]">
                              {[1,2,3,4,5].map(s => (
                                <Star key={s} className={`w-3.5 h-3.5 fill-current ${s <= (tx.rating ?? 0) ? 'text-[#fdc003]' : 'text-[#ffd2d6]'}`} />
                              ))}
                            </div>
                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold bg-blue-100 text-blue-800">
                              Đã đánh giá
                            </span>
                          </>
                        )}
                      </div>
                    </div>
                  </div>

                  <div className="shrink-0">
                    {tx.status === 'evaluatable' && (
                      <button
                        onClick={e => { e.stopPropagation(); openEval(tx); }}
                        className="px-6 py-3 bg-gradient-to-br from-[#b7131a] to-[#ff766b] text-white rounded-xl font-bold text-sm shadow-md active:scale-95 transition-all"
                      >
                        Đánh giá ngay
                      </button>
                    )}
                    {tx.status === 'done' && (
                      <span className="px-6 py-3 bg-[#ffc2c9] text-[#852139] rounded-xl font-bold text-sm">
                        Đã hoàn tất
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>

        {/* ── CTA Banner ── */}
        <section className="relative rounded-2xl overflow-hidden h-64 flex items-center shadow-2xl">
          <div className="absolute inset-0 bg-gradient-to-r from-[#b7131a] to-[#ff766b]" />
          <div className="absolute inset-0 opacity-10 pointer-events-none"
            style={{ backgroundImage: 'repeating-linear-gradient(45deg,#fff 0,#fff 1px,transparent 0,transparent 50%)', backgroundSize: '20px 20px' }}
          />
          <div className="relative z-10 px-10 md:px-16 w-full flex flex-col md:flex-row justify-between items-center gap-8">
            <div className="text-center md:text-left max-w-lg">
              <h2 className="text-3xl font-black text-white leading-tight mb-3">
                Góp ý của bạn thay đổi diện mạo công sở
              </h2>
              <p className="text-white/80 font-medium italic text-sm">
                Sự hài lòng của người dân là thước đo hiệu quả của chính quyền.
              </p>
            </div>
            <button
              onClick={() => onNavigate('chatbot')}
              className="bg-white text-[#b7131a] px-10 py-4 rounded-xl font-black text-sm tracking-widest uppercase hover:bg-[#fff4f4] transition-all shadow-xl hover:-translate-y-1 active:scale-95 whitespace-nowrap flex items-center gap-2"
            >
              HỎI AI TRỢ LÝ
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </section>

      </main>

      {/* ── Footer ── */}
      <footer className="mt-auto py-8 px-12 border-t border-[#de9ca4]/10 flex flex-col md:flex-row justify-between items-center text-xs text-[#9f364c] font-medium opacity-60">
        <p>© 2024 Cổng dịch vụ công tỉnh Thanh Hóa. All rights reserved.</p>
        <div className="flex gap-6 mt-4 md:mt-0">
          {['Điều khoản sử dụng', 'Chính sách bảo mật', 'Liên hệ hỗ trợ'].map((t) => (
            <button key={t} className="hover:text-[#b7131a] transition-colors">{t}</button>
          ))}
        </div>
      </footer>

    </div>
  );
}
