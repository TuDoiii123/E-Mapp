import React, { useEffect, useState } from 'react';
import {
  ArrowLeft, RefreshCw, Phone, MessageCircle,
  Clock, Banknote, Building2, CheckCircle2,
  FileText, Copy, Shield, CircleDot, Send,
} from 'lucide-react';
import { proceduresAPI, type Procedure, type Requirement } from '../../services/proceduresService';

interface DocumentDetailProps {
  onNavigate: (screen: string, params?: any) => void;
  serviceId?: string;
  params?: any;
}

const CATEGORY_META: Record<string, { label: string; icon: string; color: string }> = {
  civil:        { label: 'Hộ tịch & Cư trú',  icon: '👤', color: '#3b82f6' },
  land:         { label: 'Đất đai',             icon: '🏠', color: '#10b981' },
  construction: { label: 'Xây dựng',            icon: '🏗️', color: '#f59e0b' },
  business:     { label: 'Kinh doanh',           icon: '🏢', color: '#8b5cf6' },
  transport:    { label: 'Giao thông',           icon: '🚗', color: '#06b6d4' },
  justice:      { label: 'Tư pháp',             icon: '⚖️', color: '#ef4444' },
  tax:          { label: 'Thuế',                 icon: '💰', color: '#f97316' },
  insurance:    { label: 'BHXH & Bảo hiểm',    icon: '🛡️', color: '#84cc16' },
  health:       { label: 'Y tế',                 icon: '⚕️', color: '#ec4899' },
  education:    { label: 'Giáo dục',             icon: '🎓', color: '#a855f7' },
  environment:  { label: 'Môi trường',           icon: '🌿', color: '#22c55e' },
};

const LEVEL_AGENCY: Record<string, { name: string; desc: string; phone: string }[]> = {
  ward: [
    { name: 'UBND phường Điện Biên, TP Thanh Hóa',   desc: 'Tiếp nhận và giải quyết hồ sơ hộ tịch, cư trú cấp phường', phone: '0237.3852.111' },
    { name: 'UBND phường Ba Đình, TP Thanh Hóa',      desc: 'Tiếp nhận và giải quyết hồ sơ hộ tịch, cư trú cấp phường', phone: '0237.3855.222' },
    { name: 'UBND phường Tân Sơn, TP Thanh Hóa',      desc: 'Tiếp nhận và giải quyết hồ sơ hộ tịch, cư trú cấp phường', phone: '0237.3851.333' },
    { name: 'UBND xã Thiệu Hóa, huyện Thiệu Hóa',    desc: 'Tiếp nhận và giải quyết hồ sơ hộ tịch cấp xã',            phone: '0237.3861.444' },
  ],
  district: [
    { name: 'UBND TP Thanh Hóa — Phòng Tư pháp',     desc: 'Giải quyết hồ sơ cấp huyện/thành phố, có thể ủy quyền cho xã', phone: '0237.3852.011' },
    { name: 'UBND huyện Đông Sơn — Phòng QL Đô thị',  desc: 'Tiếp nhận hồ sơ xây dựng, đất đai cấp huyện',               phone: '0237.3853.022' },
    { name: 'UBND huyện Quảng Xương — Phòng TNMT',    desc: 'Giải quyết thủ tục đất đai, môi trường cấp huyện',           phone: '0237.3854.033' },
  ],
  province: [
    { name: 'Trung tâm Phục vụ Hành chính công tỉnh', desc: '25A Đại lộ Lê Lợi, Ba Đình, TP Thanh Hóa. Một cửa tập trung 19 Sở/ngành', phone: '0237.3753.888' },
    { name: 'Sở Tư pháp Thanh Hóa',                   desc: '34 Đại lộ Lê Lợi, TP Thanh Hóa. Lý lịch tư pháp, công chứng, hộ tịch', phone: '0237.3852.573' },
    { name: 'Sở Tài nguyên & Môi trường Thanh Hóa',   desc: '33 Đại lộ Lê Lợi, TP Thanh Hóa. Đất đai, tài nguyên, môi trường',      phone: '0237.3752.262' },
    { name: 'Công an tỉnh Thanh Hóa (PA06)',           desc: '4 Trần Phú, Hàm Rồng, TP Thanh Hóa. CCCD, cư trú, đăng ký xe',        phone: '069.2587.018' },
    { name: 'Sở Giao thông Vận tải Thanh Hóa',         desc: '09 Đại lộ Hùng Vương, TP Thanh Hóa. Giấy phép lái xe, đăng kiểm',    phone: '0237.3850.397' },
    { name: 'Sở Kế hoạch & Đầu tư Thanh Hóa',         desc: '24 Hải Thượng Lãn Ông, TP Thanh Hóa. Đăng ký doanh nghiệp, đầu tư', phone: '0237.3852.349' },
    { name: 'Sở Xây dựng Thanh Hóa',                   desc: '22 Đào Duy Từ, TP Thanh Hóa. Cấp phép xây dựng, quy hoạch',          phone: '0237.3852.601' },
  ],
};

const DOC_TYPE_LABEL: Record<string, { label: string; icon: React.ReactNode; color: string }> = {
  original:        { label: 'Bản chính',           icon: <Shield className="w-3.5 h-3.5" />,    color: '#b7131a' },
  certified_copy:  { label: 'Bản sao có chứng thực', icon: <CheckCircle2 className="w-3.5 h-3.5" />, color: '#059669' },
  copy:            { label: 'Bản sao thường',       icon: <Copy className="w-3.5 h-3.5" />,     color: '#6b7280' },
};

export function DocumentDetailScreen({ onNavigate, serviceId, params }: DocumentDetailProps) {
  const [procedure, setProcedure] = useState<Procedure | null>(null);
  const [loading, setLoading]     = useState(true);

  const procId = params?.procedureId || serviceId;

  useEffect(() => {
    if (!procId) { setLoading(false); return; }
    setLoading(true);
    proceduresAPI.get(procId)
      .then(r => setProcedure(r.success ? r.data : null))
      .catch(() => setProcedure(null))
      .finally(() => setLoading(false));
  }, [procId]);

  const meta = procedure ? (CATEGORY_META[procedure.category] || { label: procedure.category, icon: '📄', color: '#9f364c' }) : null;
  const agencies = procedure ? (LEVEL_AGENCY[procedure.implementingLevel] || LEVEL_AGENCY.province) : [];

  const allReqs: Requirement[] = procedure?.requirements || [];

  // ── Phân loại clean vs raw ────────────────────────────────────────────────
  // Raw IDs có dạng số: "1.000894-req-005", "2.002286-req-003"
  // Clean IDs có dạng tên: "ket_hon-req-003", "cap-doi-cccd-req-001"
  const isRawId = (r: Requirement) => /^\d+\.\d+-req-\d+$/.test(r.id);
  const cleanReqs = allReqs.filter(r => !isRawId(r));
  const rawReqs   = allReqs.filter(r =>  isRawId(r));

  // ── Lọc bỏ rác (áp dụng cho cả clean lẫn raw) ───────────────────────────
  // "Rác" = nhãn tiêu đề, câu điều kiện, hướng dẫn quy trình — không phải giấy tờ
  const isJunkItem = (r: Requirement) => {
    const name   = r.docName.trim();
    const noDesc = !r.docDescription?.trim();
    if (!name) return true;

    // Bảo vệ: tên bắt đầu bằng từ khoá giấy tờ → không bao giờ là rác
    const docPrefixes = [
      'Tờ khai ', 'Đơn đề nghị', 'Đơn xin ', 'Đơn yêu cầu',
      'Giấy chứng ', 'Giấy khai ', 'Phiếu ', 'Bản khai ',
    ];
    if (docPrefixes.some(p => name.startsWith(p))) return false;

    // Nhãn tiêu đề kết thúc ':' hoặc ';' → luôn là rác
    if (name.endsWith(':') || name.endsWith(';')) return true;

    // Bullet point hướng dẫn
    if (name.startsWith('+')) return true;

    // Luôn là rác bất kể có mô tả hay không
    const alwaysJunk = [
      'Trường hợp ',
      'Nếu bên ',
      'Người có yêu cầu ',
      'Công dân Việt Nam đã ',
      'Cá nhân có quyền',
      'Lưu ý',
      'Giấy tờ phải nộp',
      'Giấy tờ phải xuất trình',
      'Người tiếp nhận có trách nhiệm',
    ];
    if (alwaysJunk.some(p => name.startsWith(p))) return true;

    // Tên dài chứa điều kiện nộp trực tuyến
    const nl = name.toLowerCase();
    if (name.length > 100 && (
      nl.includes('(nếu người có yêu cầu') ||
      nl.includes('(do người yêu cầu') ||
      nl.includes('theo hình thức trực tuyến')
    )) return true;

    // Đoạn văn pháp lý dài không có mô tả
    if (noDesc) {
      if (name.length > 120) return true;
      if (['Đối với giấy tờ nộp', 'Đối với giấy tờ xuất', 'Người yêu cầu đăng ký hộ tịch']
          .some(p => name.startsWith(p))) return true;
    }

    return false;
  };

  // ── Chiến lược lấy requirements ──────────────────────────────────────────
  // Ưu tiên bộ clean; nếu sau lọc rác clean còn < 1 item → fallback sang raw.
  const filteredClean = cleanReqs.filter(r => !isJunkItem(r));
  const requirements: Requirement[] = filteredClean.length >= 1
    ? filteredClean
    : rawReqs.filter(r => !isJunkItem(r));

  // ── Phân loại 3 nhóm rõ ràng ────────────────────────────────────────────────
  const isXuatTrinh  = (r: Requirement) => (r.docDescription || '').toLowerCase().startsWith('xuất trình');
  const submitReqs   = requirements.filter(r => r.isRequired && !isXuatTrinh(r));
  const xuatTrinhReqs = requirements.filter(r => isXuatTrinh(r));
  const optionalReqs = requirements.filter(r => !r.isRequired && !isXuatTrinh(r));

  return (
    <div className="bg-[#fff4f4] text-[#4d2128] min-h-screen flex flex-col" style={{ fontFamily: "'Manrope', sans-serif" }}>

      {/* ── Header ── */}
      <header className="sticky top-0 z-40 bg-[#fff4f4]/90 backdrop-blur-md border-b border-[#de9ca4]/20 px-4 md:px-8 py-4 flex items-center gap-3">
        <button onClick={() => onNavigate('document-catalog')}
          className="w-9 h-9 flex items-center justify-center rounded-full hover:bg-[#ffd9dd] transition-colors text-[#9f364c]">
          <ArrowLeft className="w-5 h-5" />
        </button>
        <div className="flex-1 min-w-0">
          <p className="text-[10px] font-bold text-[#9f364c] uppercase tracking-widest">Chi tiết thủ tục</p>
          <h1 className="text-sm font-black text-[#4d2128] truncate leading-tight">
            {procedure?.name || 'Đang tải...'}
          </h1>
        </div>
      </header>

      {/* ── Main ── */}
      <main className="flex-1 max-w-4xl mx-auto w-full px-4 md:px-8 py-6 pb-28 space-y-5">

        {loading ? (
          <div className="flex flex-col items-center justify-center py-32">
            <RefreshCw className="w-8 h-8 text-[#de9ca4] animate-spin mb-3" />
            <p className="text-sm text-[#9f364c]">Đang tải thông tin...</p>
          </div>
        ) : !procedure ? (
          <div className="flex flex-col items-center justify-center py-32 bg-white rounded-2xl border border-[#de9ca4]/20">
            <span className="text-5xl mb-4">😔</span>
            <h3 className="text-lg font-bold mb-1">Không tìm thấy thủ tục</h3>
            <button onClick={() => onNavigate('document-catalog')}
              className="mt-3 px-4 py-2 bg-[#b7131a] text-white rounded-lg text-sm font-bold">
              Quay lại danh sách
            </button>
          </div>
        ) : (
          <>
            {/* ── Hero card ── */}
            <div className="bg-white rounded-2xl p-5 border border-[#de9ca4]/15 shadow-sm overflow-hidden relative">
              <div className="absolute top-0 right-0 w-32 h-32 rounded-full -mr-10 -mt-10 blur-2xl pointer-events-none"
                style={{ backgroundColor: (meta?.color || '#b7131a') + '18' }} />
              <div className="relative z-10 flex items-start gap-4">
                <div className="w-14 h-14 rounded-xl flex items-center justify-center text-3xl flex-shrink-0"
                  style={{ backgroundColor: (meta?.color || '#b7131a') + '18' }}>
                  {procedure.icon || meta?.icon}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1 flex-wrap">
                    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold"
                      style={{ backgroundColor: (meta?.color || '#b7131a') + '18', color: meta?.color || '#b7131a' }}>
                      {meta?.icon} {meta?.label}
                    </span>
                    {procedure.isOnline && (
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-green-50 text-green-700">
                        <CircleDot className="w-2.5 h-2.5" /> Trực tuyến
                      </span>
                    )}
                  </div>
                  <h2 className="font-black text-[#4d2128] text-base leading-snug">{procedure.name}</h2>
                  {procedure.code && (
                    <p className="text-[10px] text-[#9f364c]/60 mt-0.5">Mã: {procedure.code}</p>
                  )}
                </div>
              </div>
            </div>

            {/* ── Thông tin nhanh ── */}
            <div className="grid grid-cols-2 gap-3">
              {[
                { icon: <Clock className="w-4 h-4" />, label: 'Thời gian xử lý', value: procedure.timeFormatted, color: '#3b82f6' },
                { icon: <Banknote className="w-4 h-4" />, label: 'Lệ phí', value: procedure.feeFormatted, color: procedure.feeColor ? '#059669' : '#b7131a' },
                { icon: <Building2 className="w-4 h-4" />, label: 'Cấp thực hiện', value: procedure.implementingLevel === 'ward' ? 'Cấp xã/phường' : procedure.implementingLevel === 'district' ? 'Cấp huyện' : 'Cấp tỉnh', color: '#8b5cf6' },
                { icon: <FileText className="w-4 h-4" />, label: 'Số giấy tờ', value: `${requirements.length} loại (${submitReqs.length} bắt buộc)`, color: '#f59e0b' },
              ].map(({ icon, label, value, color }) => (
                <div key={label} className="bg-white rounded-xl p-4 border border-[#de9ca4]/15 flex items-start gap-3">
                  <div className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0"
                    style={{ backgroundColor: color + '18', color }}>
                    {icon}
                  </div>
                  <div className="min-w-0">
                    <p className="text-[10px] text-[#9f364c] font-bold uppercase tracking-wide">{label}</p>
                    <p className="text-sm font-black text-[#4d2128] leading-tight mt-0.5">{value}</p>
                  </div>
                </div>
              ))}
            </div>

            {/* ── Cơ quan thực hiện ── */}
            {procedure.agency && (
              <div className="bg-white rounded-2xl p-5 border border-[#de9ca4]/15">
                <h3 className="font-black text-[#4d2128] text-sm mb-1 flex items-center gap-2">
                  <Building2 className="w-4 h-4 text-[#b7131a]" /> Cơ quan thực hiện
                </h3>
                <p className="text-sm text-[#824c54] mb-4 leading-relaxed">{procedure.agency}</p>

                <div className="space-y-3">
                  {agencies.map((ag, i) => (
                    <div key={i} className="flex items-start gap-3 p-3 bg-[#ffeced]/50 rounded-xl">
                      <div className="w-9 h-9 rounded-lg bg-[#ffd9dd] flex items-center justify-center text-[#b7131a] flex-shrink-0">
                        <Building2 className="w-4 h-4" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-bold text-[#4d2128] leading-tight">{ag.name}</p>
                        <p className="text-xs text-[#9f364c] mt-0.5 leading-relaxed">{ag.desc}</p>
                        <a href={`tel:${ag.phone}`}
                          className="inline-flex items-center gap-1 text-xs text-[#b7131a] font-bold mt-1">
                          <Phone className="w-3 h-3" /> {ag.phone}
                        </a>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* ── Giấy tờ cần nộp ── */}
            {submitReqs.length > 0 && (
              <div className="bg-white rounded-2xl p-5 border border-[#de9ca4]/15">
                <h3 className="font-black text-[#4d2128] text-sm mb-4 flex items-center gap-2">
                  <FileText className="w-4 h-4 text-[#b7131a]" />
                  Giấy tờ cần chuẩn bị
                  <span className="ml-auto text-[10px] font-black bg-[#b7131a] text-white px-2 py-0.5 rounded-full">
                    {submitReqs.length} loại
                  </span>
                </h3>
                <div className="space-y-2">
                  {submitReqs.map((req, i) => {
                    const typeInfo = DOC_TYPE_LABEL[req.docType] || DOC_TYPE_LABEL.original;
                    return (
                      <div key={req.id} className="flex items-start gap-3 p-3 bg-red-50/50 rounded-xl border border-red-100">
                        <div className="w-6 h-6 rounded-full bg-[#b7131a] text-white flex items-center justify-center text-[10px] font-black flex-shrink-0 mt-0.5">
                          {i + 1}
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-bold text-[#4d2128] leading-snug">{req.docName}</p>
                          {req.docDescription && (
                            <p className="text-xs text-[#824c54] mt-0.5 leading-relaxed">{req.docDescription}</p>
                          )}
                          <div className="flex items-center gap-2 mt-1 flex-wrap">
                            <span className="inline-flex items-center gap-1 text-[10px] font-bold px-2 py-0.5 rounded-full"
                              style={{ backgroundColor: typeInfo.color + '18', color: typeInfo.color }}>
                              {typeInfo.icon} {typeInfo.label}
                            </span>
                            {req.templateFile && (
                              <a href={`/api/templates/download/${req.templateFile}`} target="_blank" rel="noreferrer"
                                className="inline-flex items-center gap-1 text-[10px] font-bold px-2 py-0.5 rounded-full bg-blue-50 text-blue-600">
                                📄 Tải mẫu đơn
                              </a>
                            )}
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* ── Thẻ lưu ý: xuất trình + điều kiện ── */}
            {(xuatTrinhReqs.length > 0 || optionalReqs.length > 0 ||
              (procedure.conditions && procedure.conditions.length > 0)) && (
              <div className="bg-amber-50 rounded-2xl p-5 border border-amber-200">
                <h3 className="font-black text-amber-800 text-sm mb-4 flex items-center gap-2">
                  ℹ️ Lưu ý & Giấy tờ bổ sung
                </h3>

                {/* Giấy tờ xuất trình */}
                {xuatTrinhReqs.length > 0 && (
                  <div className="mb-4">
                    <span className="inline-flex items-center gap-1.5 text-[10px] font-black uppercase tracking-wider text-blue-700 bg-blue-50 border border-blue-200 px-2.5 py-0.5 rounded-full mb-3">
                      👁 Xuất trình tại quầy
                    </span>
                    <div className="space-y-2">
                      {xuatTrinhReqs.map((req) => (
                        <div key={req.id} className="flex items-start gap-2 text-sm text-amber-800">
                          <span className="mt-1.5 w-1.5 h-1.5 rounded-full bg-blue-400 flex-shrink-0" />
                          <div>
                            <span className="font-semibold">{req.docName}</span>
                            {req.docDescription && (
                              <span className="text-xs text-amber-700 ml-1">— {req.docDescription.replace(/^Xuất trình bản gốc\.?\s*/i, '')}</span>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Giấy tờ tùy chọn / điều kiện */}
                {optionalReqs.length > 0 && (
                  <div className="mb-4">
                    <span className="inline-flex items-center gap-1.5 text-[10px] font-black uppercase tracking-wider text-amber-800 bg-amber-100 border border-amber-300 px-2.5 py-0.5 rounded-full mb-3">
                      🎯 Tùy trường hợp
                    </span>
                    <div className="space-y-2">
                      {optionalReqs.map((req) => (
                        <div key={req.id} className="flex items-start gap-2 text-sm text-amber-800">
                          <span className="mt-1.5 w-1.5 h-1.5 rounded-full bg-amber-400 flex-shrink-0" />
                          <div>
                            <span className="font-semibold">{req.docName}</span>
                            {req.docDescription && (
                              <p className="text-xs text-amber-700 mt-0.5 leading-relaxed">{req.docDescription}</p>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Điều kiện từ dữ liệu thủ tục */}
                {procedure.conditions && procedure.conditions.length > 0 && (
                  <div>
                    <span className="inline-flex items-center gap-1.5 text-[10px] font-black uppercase tracking-wider text-orange-800 bg-orange-50 border border-orange-200 px-2.5 py-0.5 rounded-full mb-3">
                      ⚠️ Điều kiện thực hiện
                    </span>
                    <ul className="space-y-1">
                      {procedure.conditions.map((cond, i) => (
                        <li key={i} className="flex items-start gap-2 text-xs text-amber-800">
                          <span className="mt-1 w-1.5 h-1.5 rounded-full bg-amber-600 flex-shrink-0" />
                          <span className="leading-relaxed">{cond}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}

            {/* ── Trình tự thực hiện ── */}
            {procedure.steps && procedure.steps.length > 0 && (
              <div className="bg-white rounded-2xl p-5 border border-[#f0d0d4]">
                <h3 className="font-black text-[#4d2128] text-sm mb-4 flex items-center gap-2">
                  <span className="w-6 h-6 rounded-full bg-[#b7131a] text-white flex items-center justify-center text-[10px] font-black">→</span>
                  Trình tự thực hiện
                </h3>
                <ol className="space-y-3">
                  {procedure.steps.map((step, i) => (
                    <li key={i} className="flex items-start gap-3">
                      <span className="w-5 h-5 rounded-full bg-[#ffeced] text-[#b7131a] flex items-center justify-center text-[10px] font-black flex-shrink-0 mt-0.5">
                        {i + 1}
                      </span>
                      <p className="text-xs text-[#4d2128] leading-relaxed">{step}</p>
                    </li>
                  ))}
                </ol>
              </div>
            )}

            {/* ── Ghi chú thời gian & lệ phí ── */}
            {(procedure.processingNote || procedure.feeNote) && (
              <div className="bg-amber-50 rounded-2xl p-5 border border-amber-100">
                <h3 className="font-black text-amber-800 text-sm mb-3">ℹ️ Lưu ý quan trọng</h3>
                {procedure.processingNote && (
                  <p className="text-xs text-amber-700 leading-relaxed mb-2">⏱ {procedure.processingNote}</p>
                )}
                {procedure.feeNote && (
                  <p className="text-xs text-amber-700 leading-relaxed">💰 {procedure.feeNote}</p>
                )}
              </div>
            )}
          </>
        )}
      </main>

      {/* ── Sticky action bar ── */}
      {procedure && (
        <div className="fixed bottom-0 left-0 right-0 z-50 bg-[#fff4f4]/95 backdrop-blur-md border-t border-[#de9ca4]/20 px-4 py-3">
          <div className="max-w-4xl mx-auto flex gap-3">
            <button
              onClick={() => onNavigate('chatbot')}
              className="flex-1 h-11 flex items-center justify-center gap-2 border-2 border-[#b7131a] text-[#b7131a] font-bold text-sm rounded-xl hover:bg-[#ffeced] transition-colors">
              <MessageCircle className="w-4 h-4" /> Hỏi AI
            </button>
            <button
              onClick={() => onNavigate('submit')}
              className="flex-1 h-11 flex items-center justify-center gap-2 bg-[#b7131a] text-white font-bold text-sm rounded-xl hover:bg-[#a00010] transition-colors shadow-lg shadow-[#b7131a]/20">
              <Send className="w-4 h-4" /> Nộp hồ sơ
            </button>
          </div>
        </div>
      )}

      {/* ── Mobile bottom nav ── */}
      <nav className="md:hidden h-16" /> {/* spacer for fixed nav */}
    </div>
  );
}

export default DocumentDetailScreen;
