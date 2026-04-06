/**
 * SubmitDocumentScreen — Nộp hồ sơ trực tuyến
 * Design: Heritage Bordeaux Red #8f000d + Gold #a17d00
 * Layout: Horizontal stepper + Bento grid cards + Sticky action bar
 */
import { useState, useRef } from 'react';
import React from 'react';
import { API_BASE_URL, getToken } from '../services/api';
import {
  ArrowLeft, CheckCircle, Upload, FileText, Clock, CreditCard,
  ShieldCheck, Phone, X, Building2, FolderOpen, Download,
  ChevronRight, MessageCircle, Info, Eye, Trash2, CloudUpload,
  Paperclip, Smartphone, HardDrive, Send, ShieldAlert, Image,
} from 'lucide-react';

interface SubmitDocumentScreenProps {
  onNavigate: (screen: string) => void;
}

interface DocItem {
  name: string;
  description: string;
  hasTemplate?: boolean;
  actionLabel?: string;
}

const SERVICES = [
  {
    id: 'marriage',
    name: 'Đăng ký kết hôn',
    category: 'Hộ tịch',
    icon: '❤️',
    time: '5-7 ngày làm việc',
    fee: '0 VNĐ',
    feeColor: true,
    docs: [
      { name: 'Tờ khai đăng ký kết hôn', description: 'Cần có chữ ký của cả hai bên nam và nữ. Đầy đủ thông tin theo mẫu quy định.', hasTemplate: true },
      { name: 'CCCD/Hộ chiếu/Giấy tờ định danh', description: 'Bản chính hoặc bản sao có chứng thực của cả hai bên để đối chiếu thông tin.', actionLabel: 'Xem quy định' },
      { name: 'Giấy xác nhận tình trạng hôn nhân', description: 'Do UBND cấp xã nơi cư trú cấp. Có giá trị trong vòng 06 tháng kể từ ngày cấp.', actionLabel: 'Liên kết trực tuyến' },
      { name: 'Ảnh 4x6 (4 tấm)', description: 'Ảnh chân dung nền trắng, chụp trong vòng 06 tháng gần nhất.' },
    ] as DocItem[],
  },
  {
    id: 'license',
    name: 'Giấy phép kinh doanh',
    category: 'Kinh doanh',
    icon: '💼',
    time: '15 ngày làm việc',
    fee: '100,000 VNĐ',
    feeColor: false,
    docs: [
      { name: 'Đơn đăng ký kinh doanh', description: 'Theo mẫu quy định của Bộ Kế hoạch và Đầu tư. Phải có chữ ký và dấu của người đại diện.', hasTemplate: true },
      { name: 'CCCD gốc của chủ hộ kinh doanh', description: 'Bản chính để đối chiếu, bản sao có công chứng để nộp hồ sơ.', actionLabel: 'Xem quy định' },
      { name: 'Hợp đồng/Giấy tờ địa điểm kinh doanh', description: 'Hợp đồng thuê mặt bằng hoặc giấy tờ chứng minh quyền sử dụng địa điểm.', actionLabel: 'Hướng dẫn' },
      { name: 'Ảnh 3x4 (2 tấm)', description: 'Ảnh chân dung nền trắng của người đại diện.' },
    ] as DocItem[],
  },
  {
    id: 'cccd',
    name: 'Cấp lại CCCD',
    category: 'Hành chính',
    icon: '🪪',
    time: '7-10 ngày làm việc',
    fee: '50,000 VNĐ',
    feeColor: false,
    docs: [
      { name: 'Đơn đề nghị cấp lại CCCD', description: 'Theo mẫu CC02 hoặc điền trực tiếp tại cơ quan công an. Ghi rõ lý do cấp lại.', hasTemplate: true },
      { name: 'CCCD cũ (nếu có)', description: 'Nộp lại thẻ CCCD cũ hoặc bản tường trình lý do mất/hỏng có xác nhận.', actionLabel: 'Xem quy định' },
      { name: 'Ảnh 3x4 (2 tấm)', description: 'Ảnh chân dung nền trắng, chụp trong vòng 06 tháng gần nhất.' },
    ] as DocItem[],
  },
];

const STEPS = ['Chọn loại hồ sơ', 'Chuẩn bị tài liệu', 'Upload hồ sơ', 'Xác nhận & Ký số'];

export function SubmitDocumentScreen({ onNavigate }: SubmitDocumentScreenProps) {
  const [currentStep, setCurrentStep] = useState(1);
  const [selectedService, setSelectedService] = useState('');
  const [uploadedFiles, setUploadedFiles] = useState<string[]>([]);
  const [fileObjects, setFileObjects] = useState<Record<string, File | null>>({});
  const [submitting, setSubmitting] = useState(false);
  const [agreed, setAgreed] = useState(false);
  const [notes, setNotes] = useState('');
  const [contactPhone, setContactPhone] = useState('');
  const [contactEmail, setContactEmail] = useState('');
  const [contactAddress, setContactAddress] = useState('');
  const [signMethod, setSignMethod] = useState<'otp' | 'usb' | ''>('');
  const fileInputsRef = useRef<Record<string, HTMLInputElement | null>>({});

  const svc = SERVICES.find(s => s.id === selectedService);
  const requiredDocs = svc?.docs.map(d => d.name) ?? [];

  const handleBack = () => {
    if (currentStep > 1) setCurrentStep(s => s - 1);
    else onNavigate('home');
  };

  const handleNext = () => {
    if (currentStep < 4) setCurrentStep(s => s + 1);
  };

  const handleFilePick = (key: string) => fileInputsRef.current[key]?.click();

  const onFileChange = (key: string, e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0] ?? null;
    setFileObjects(p => ({ ...p, [key]: f }));
    if (f) setUploadedFiles(p => p.includes(key) ? p : [...p, key]);
  };

  const removeFile = (key: string) => {
    setUploadedFiles(p => p.filter(k => k !== key));
    setFileObjects(p => ({ ...p, [key]: null }));
  };

  const handleSubmit = async () => {
    if (!agreed) return;
    try {
      setSubmitting(true);
      const form = new FormData();
      form.append('serviceId', selectedService);
      form.append('data', JSON.stringify({ notes, contactPhone, contactEmail, contactAddress }));
      const fileKeys = Object.keys(fileObjects).filter(k => fileObjects[k]);
      if (fileKeys.length === 0) {
        alert('Vui lòng chọn ít nhất 1 file/ảnh trước khi nộp hồ sơ');
        return;
      }
      fileKeys.forEach(key => {
        const f = fileObjects[key];
        if (f) form.append('files', f, f.name);
      });
      const token = getToken();
      const resp = await fetch(`${API_BASE_URL}/applications/create`, {
        method: 'POST',
        headers: token ? { Authorization: `Bearer ${token}` } : {},
        body: form,
      });
      const data = await resp.json();
      if (!resp.ok) throw new Error(data.message || 'Lỗi khi nộp hồ sơ');
      alert('Nộp hồ sơ thành công!');
      onNavigate('home');
    } catch (err: any) {
      alert('Lỗi khi nộp hồ sơ: ' + (err.message || err));
    } finally {
      setSubmitting(false);
    }
  };

  const canContinue =
    (currentStep === 1 && !!selectedService) ||
    currentStep === 2 ||
    (currentStep === 3 && uploadedFiles.length > 0) ||
    (currentStep === 4 && agreed && !!signMethod && !submitting);

  /* ── Render ── */
  return (
    <div className="bg-[#fff4f4] text-on-background min-h-screen flex flex-col" style={{ fontFamily: "'Manrope', sans-serif" }}>

      {/* ── Header & Progress Bar ── */}
      <header className="sticky top-0 bg-[#fff4f4]/80 backdrop-blur-md z-40 px-6 md:px-12 py-3 border-b border-outline-variant/20">
        <div className="max-w-5xl mx-auto">
          <div className="flex items-center justify-between mb-3">
            <div>
              <h1 className="text-lg font-black text-on-background tracking-tight">Thủ tục hành chính</h1>
              <p className="text-on-surface-variant font-medium text-xs">Hệ thống dịch vụ công trực tuyến</p>
            </div>
            <div className="hidden sm:flex items-center gap-2 bg-surface-container-low px-3 py-1.5 rounded-xl border border-outline-variant/20">
              <ShieldCheck className="w-4 h-4 text-primary" />
              <div className="text-[11px]">
                <p className="font-bold text-on-surface leading-tight">Bảo mật tuyệt đối</p>
                <p className="text-on-surface-variant leading-tight">Mã hóa 256-bit</p>
              </div>
            </div>
          </div>

          {/* Progress Tracker */}
          <div className="relative flex justify-between items-center px-2">
            <div className="absolute top-4 left-0 w-full h-[2px] bg-surface-container-high -translate-y-1/2 z-0" />
            {STEPS.map((label, i) => {
              const n = i + 1;
              const done = n < currentStep;
              const active = n === currentStep;
              return (
                <div key={n} className="relative z-10 flex flex-col items-center gap-1">
                  <div
                    className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-xs shadow
                      ${done ? 'bg-secondary text-on-secondary' :
                        active ? 'bg-primary text-on-primary' :
                        'bg-surface-container-high text-on-surface-variant'
                      }`}
                  >
                    {done ? <CheckCircle className="w-4 h-4" /> : n}
                  </div>
                  <span className={`text-[9px] font-bold uppercase tracking-tighter text-center max-w-[56px] leading-tight hidden sm:block
                    ${active ? 'text-primary' : done ? 'text-secondary' : 'text-outline'}`}>
                    {label}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      </header>

      {/* ── Main ── */}
      <main className="flex-1 px-6 md:px-12 pb-16">
        <div className="max-w-5xl mx-auto space-y-8 pt-8">

        {/* ════════════════════════════
            STEP 1: Chọn loại hồ sơ
        ════════════════════════════ */}
        {currentStep === 1 && (
          <>
            {/* Service Cards Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {SERVICES.map(service => {
                const selected = selectedService === service.id;
                return (
                  <button
                    key={service.id}
                    onClick={() => setSelectedService(service.id)}
                    className={`group text-left bg-surface-container-lowest p-6 rounded-xl border transition-all duration-300 flex flex-col h-full
                      ${selected
                        ? 'border-primary/50 shadow-xl ring-2 ring-primary/20'
                        : 'border-outline-variant/20 hover:border-primary/30 hover:shadow-xl'
                      }`}
                  >
                    <div className={`w-14 h-14 rounded-xl flex items-center justify-center mb-6 transition-colors text-3xl
                      ${selected ? 'bg-primary text-on-primary' : 'bg-surface-container-low group-hover:bg-primary group-hover:text-on-primary'}`}>
                      {service.icon}
                    </div>
                    <h3 className="text-xl font-bold mb-2 text-on-surface">{service.name}</h3>
                    <p className="text-on-surface-variant text-sm mb-6 flex-1">
                      {service.id === 'marriage' && 'Cấp giấy chứng nhận kết hôn cho công dân Việt Nam cư trú trong nước.'}
                      {service.id === 'license' && 'Đăng ký thành lập hộ kinh doanh cá thể hoặc doanh nghiệp mới.'}
                      {service.id === 'cccd' && 'Thủ tục cấp đổi, cấp lại thẻ Căn cước công dân gắn chíp điện tử.'}
                    </p>
                    <div className="space-y-3 pt-4 border-t border-outline-variant/10">
                      <div className="flex justify-between text-xs">
                        <span className="text-on-surface-variant/70">Thời gian xử lý:</span>
                        <span className="font-bold text-on-surface">{service.time}</span>
                      </div>
                      <div className="flex justify-between text-xs">
                        <span className="text-on-surface-variant/70">Lệ phí:</span>
                        <span className={`font-bold ${service.feeColor ? 'text-primary' : 'text-on-surface'}`}>{service.fee}</span>
                      </div>
                    </div>
                    {selected && (
                      <div className="mt-4 flex items-center gap-2 text-primary">
                        <CheckCircle className="w-4 h-4 fill-primary stroke-white" />
                        <span className="text-[10px] font-black uppercase tracking-widest">Đã chọn</span>
                      </div>
                    )}
                  </button>
                );
              })}
            </div>

            {/* Show More Button */}
            <div className="flex justify-center">
              <button className="flex items-center gap-2 px-8 py-4 bg-surface-container rounded-xl font-bold text-primary hover:bg-surface-container-high transition-colors text-sm">
                <span className="material-symbols-outlined text-[20px]">apps</span>
                Xem thêm các thủ tục khác
              </button>
            </div>

            {/* Legal Support Banner */}
            <div className="relative overflow-hidden bg-gradient-to-r from-primary to-primary-container rounded-2xl p-8 flex flex-col md:flex-row items-center justify-between gap-6 shadow-xl">
              <div className="relative z-10">
                <h2 className="text-2xl font-black text-on-primary mb-2">Hỗ trợ tư vấn pháp lý trực tuyến</h2>
                <p className="text-on-primary/80 max-w-lg font-medium text-sm">
                  Đội ngũ chuyên gia pháp lý luôn sẵn sàng hỗ trợ bạn hoàn thiện hồ sơ nhanh chóng và chính xác nhất.
                </p>
              </div>
              <button className="relative z-10 flex items-center gap-2 px-8 py-4 bg-secondary-container text-on-secondary-container font-black rounded-xl hover:scale-105 active:scale-95 transition-transform shadow-lg whitespace-nowrap text-sm">
                <Phone className="w-4 h-4" />
                Hỗ trợ ngay
              </button>
              <div className="absolute -right-20 -bottom-20 w-64 h-64 bg-white/10 rounded-full blur-3xl pointer-events-none" />
            </div>
          </>
        )}

        {/* ════════════════════════════
            STEP 2: Chuẩn bị tài liệu
        ════════════════════════════ */}
        {currentStep === 2 && (
          <>
            {/* Sub-header */}
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl md:text-3xl font-black text-on-background tracking-tight">Chuẩn bị tài liệu</h2>
                <p className="text-on-surface-variant font-medium text-sm mt-1">
                  Thủ tục: <span className="font-bold text-primary">{svc?.name}</span>
                </p>
              </div>
              <div className="hidden sm:flex items-center gap-3 bg-surface-container-low px-4 py-2 rounded-xl border border-outline-variant/20">
                <FolderOpen className="w-5 h-5 text-primary" />
                <div className="text-xs">
                  <p className="font-bold text-on-surface">{svc?.docs.length ?? 0} tài liệu</p>
                  <p className="text-on-surface-variant">Cần chuẩn bị</p>
                </div>
              </div>
            </div>

            {/* Document cards grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
              {svc?.docs.map((doc, i) => (
                <div
                  key={i}
                  className="group bg-surface-container-lowest p-6 rounded-xl border border-outline-variant/20 hover:border-primary/30 hover:shadow-xl transition-all duration-300 flex flex-col"
                >
                  <div className="flex items-start gap-4 mb-4">
                    {/* Number badge */}
                    <div className="w-10 h-10 rounded-xl bg-surface-container-low group-hover:bg-primary group-hover:text-on-primary flex items-center justify-center font-black text-sm text-primary transition-colors shrink-0">
                      {String(i + 1).padStart(2, '0')}
                    </div>
                    <div className="flex-1 min-w-0">
                      <h4 className="font-bold text-on-surface text-base leading-tight">{doc.name}</h4>
                    </div>
                  </div>

                  <p className="text-on-surface-variant text-sm leading-relaxed flex-1 mb-5">
                    {doc.description}
                  </p>

                  {(doc.hasTemplate || doc.actionLabel) && (
                    <div className="flex items-center gap-2 pt-4 border-t border-outline-variant/10">
                      {doc.hasTemplate && (
                        <button className="flex items-center gap-2 px-4 py-2 bg-secondary-container text-on-secondary-container text-xs font-black uppercase tracking-widest rounded-lg hover:opacity-90 transition-opacity">
                          <Download className="w-3.5 h-3.5" />
                          Tải mẫu
                        </button>
                      )}
                      {doc.actionLabel && (
                        <button className="flex items-center gap-2 px-4 py-2 bg-surface-container text-primary text-xs font-black uppercase tracking-widest rounded-lg hover:bg-surface-container-high transition-colors">
                          <span className="material-symbols-outlined text-[16px]">open_in_new</span>
                          {doc.actionLabel}
                        </button>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>

            {/* Info note */}
            <div className="flex items-start gap-4 p-5 bg-surface-container-low rounded-xl border border-outline-variant/20">
              <span className="material-symbols-outlined text-primary text-[22px] shrink-0 mt-0.5">info</span>
              <p className="text-sm text-on-surface-variant leading-relaxed">
                Vui lòng chuẩn bị <span className="font-bold text-on-surface">bản quét (scan) hoặc ảnh chụp rõ nét</span> của các tài liệu trên để tải lên ở bước tiếp theo. Hệ thống hỗ trợ định dạng <span className="font-bold text-primary">.pdf, .jpg, .png</span>.
              </p>
            </div>

            {/* Legal Support Banner */}
            <div className="relative overflow-hidden bg-gradient-to-r from-primary to-primary-container rounded-2xl p-8 flex flex-col md:flex-row items-center justify-between gap-6 shadow-xl">
              <div className="relative z-10">
                <h2 className="text-2xl font-black text-on-primary mb-2">Hỗ trợ tư vấn pháp lý trực tuyến</h2>
                <p className="text-on-primary/80 max-w-lg font-medium text-sm">
                  Đội ngũ chuyên gia pháp lý luôn sẵn sàng hỗ trợ bạn hoàn thiện hồ sơ nhanh chóng và chính xác nhất.
                </p>
              </div>
              <button className="relative z-10 flex items-center gap-2 px-8 py-4 bg-secondary-container text-on-secondary-container font-black rounded-xl hover:scale-105 active:scale-95 transition-transform shadow-lg whitespace-nowrap text-sm">
                <Phone className="w-4 h-4" />
                Hỗ trợ ngay
              </button>
              <div className="absolute -right-20 -bottom-20 w-64 h-64 bg-white/10 rounded-full blur-3xl pointer-events-none" />
            </div>
          </>
        )}

        {/* ════════════════════════════
            STEP 3: Upload hồ sơ
        ════════════════════════════ */}
        {currentStep === 3 && (
          <>
            {/* Sub-header */}
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl md:text-3xl font-black text-on-background tracking-tight">Upload hồ sơ</h2>
                <p className="text-on-surface-variant font-medium text-sm mt-1">
                  Thủ tục: <span className="font-bold text-primary">{svc?.name}</span>
                </p>
              </div>
              <div className="hidden sm:flex items-center gap-3 bg-surface-container-low px-4 py-2 rounded-xl border border-outline-variant/20">
                <span className={`material-symbols-outlined text-[20px] ${uploadedFiles.length === requiredDocs.length && requiredDocs.length > 0 ? 'text-green-600' : 'text-primary'}`}
                  style={{ fontVariationSettings: "'FILL' 1" }}>
                  {uploadedFiles.length === requiredDocs.length && requiredDocs.length > 0 ? 'check_circle' : 'upload_file'}
                </span>
                <div className="text-xs">
                  <p className="font-bold text-on-surface">{uploadedFiles.length}/{requiredDocs.length} tệp</p>
                  <p className="text-on-surface-variant">Đã tải lên</p>
                </div>
              </div>
            </div>

            {/* Upload cards grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
              {requiredDocs.map((doc, i) => {
                const uploaded = uploadedFiles.includes(doc);
                const file = fileObjects[doc];
                const fileSizeKB = file ? Math.round(file.size / 1024) : 0;
                const fileSizeLabel = fileSizeKB >= 1024 ? `${(fileSizeKB / 1024).toFixed(1)} MB` : `${fileSizeKB} KB`;

                return (
                  <div key={i}>
                    <input
                      type="file"
                      accept="image/*,application/pdf"
                      aria-label={`Tải lên tài liệu: ${doc}`}
                      className="hidden"
                      ref={el => { fileInputsRef.current[doc] = el; }}
                      onChange={e => onFileChange(doc, e)}
                    />

                    {uploaded ? (
                      /* ── Uploaded ── */
                      <div className="group bg-surface-container-lowest p-6 rounded-xl border border-green-200 hover:shadow-lg transition-all duration-300">
                        <div className="flex items-start gap-4">
                          <div className="w-10 h-10 rounded-xl bg-green-50 flex items-center justify-center shrink-0">
                            <CheckCircle className="w-5 h-5 text-green-600 fill-green-600 stroke-white" />
                          </div>
                          <div className="flex-1 min-w-0">
                            <p className="font-bold text-on-surface text-sm leading-tight mb-1">
                              {String(i + 1).padStart(2, '0')}. {doc}
                            </p>
                            <div className="flex items-center gap-2 text-[11px] text-on-surface-variant">
                              <FileText className="w-3 h-3 shrink-0 text-primary" />
                              <span className="truncate max-w-[160px] font-medium text-primary">{file?.name}</span>
                              <span className="shrink-0">({fileSizeLabel})</span>
                            </div>
                          </div>
                          <div className="flex items-center gap-1 shrink-0">
                            <button aria-label="Xem" className="p-1.5 text-on-surface-variant hover:text-primary rounded-lg hover:bg-surface-container transition-colors">
                              <Eye className="w-4 h-4" />
                            </button>
                            <button onClick={() => removeFile(doc)} aria-label="Xóa" className="p-1.5 text-on-surface-variant hover:text-error rounded-lg hover:bg-surface-container transition-colors">
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </div>
                        </div>
                      </div>
                    ) : (
                      /* ── Not uploaded ── */
                      <div
                        onClick={() => handleFilePick(doc)}
                        className="group bg-surface-container-lowest p-6 rounded-xl border-2 border-dashed border-outline-variant/40 hover:border-primary/50 hover:shadow-xl transition-all duration-300 cursor-pointer"
                      >
                        <div className="flex items-start gap-4 mb-4">
                          <div className="w-10 h-10 rounded-xl bg-surface-container-low group-hover:bg-primary group-hover:text-on-primary flex items-center justify-center text-primary transition-colors shrink-0">
                            <span className="material-symbols-outlined text-[20px]">upload_file</span>
                          </div>
                          <div className="flex-1 min-w-0">
                            <p className="font-bold text-on-surface text-sm leading-tight">
                              {String(i + 1).padStart(2, '0')}. {doc}
                            </p>
                            <p className="text-[11px] text-on-surface-variant mt-0.5">PDF, JPG, PNG — tối đa 5MB</p>
                          </div>
                          <button
                            onClick={e => { e.stopPropagation(); handleFilePick(doc); }}
                            className="flex items-center gap-1.5 px-4 py-2 bg-primary text-on-primary text-xs font-black uppercase tracking-widest rounded-lg hover:opacity-90 transition-opacity shrink-0"
                          >
                            <CloudUpload className="w-3.5 h-3.5" />
                            Tải lên
                          </button>
                        </div>
                        <div className="flex items-center justify-center gap-2 py-3 border-t border-dashed border-outline-variant/30 text-[11px] text-outline font-medium">
                          <Upload className="w-3.5 h-3.5" />
                          Kéo và thả file tại đây
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>

            {/* Contact info card */}
            <div className="bg-surface-container-lowest rounded-xl border border-outline-variant/20 p-6">
              <div className="flex items-center gap-3 mb-6">
                <div className="w-10 h-10 rounded-xl bg-surface-container-low flex items-center justify-center">
                  <Phone className="w-5 h-5 text-primary" />
                </div>
                <div>
                  <h3 className="font-bold text-on-surface text-base">Thông tin liên hệ</h3>
                  <p className="text-xs text-on-surface-variant">Dùng để nhận thông báo kết quả hồ sơ</p>
                </div>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {[
                  { label: 'Số điện thoại *', type: 'tel',   value: contactPhone, setter: setContactPhone, placeholder: '09x xxxx xxx' },
                  { label: 'Email nhận thông báo *', type: 'email', value: contactEmail, setter: setContactEmail, placeholder: 'email@example.com' },
                ].map(({ label, type, value, setter, placeholder }) => (
                  <div key={label}>
                    <label className="block text-[10px] font-black uppercase tracking-widest text-on-surface-variant mb-2">{label}</label>
                    <input
                      type={type}
                      value={value}
                      onChange={e => setter(e.target.value)}
                      placeholder={placeholder}
                      className="w-full bg-surface-container-low border-none border-b-2 border-outline focus:border-primary outline-none text-sm font-medium py-2.5 px-3 rounded-lg transition-colors placeholder:text-outline/50"
                    />
                  </div>
                ))}
                <div className="md:col-span-2">
                  <label className="block text-[10px] font-black uppercase tracking-widest text-on-surface-variant mb-2">Địa chỉ thường trú *</label>
                  <textarea
                    rows={2}
                    value={contactAddress}
                    onChange={e => setContactAddress(e.target.value)}
                    placeholder="Số nhà, đường, phường/xã, quận/huyện, tỉnh/thành phố"
                    className="w-full bg-surface-container-low border-none outline-none text-sm font-medium py-2.5 px-3 rounded-lg transition-colors placeholder:text-outline/50 resize-none focus:ring-2 focus:ring-primary"
                  />
                </div>
              </div>
            </div>

            {/* Legal note */}
            <div className="flex items-start gap-4 p-5 bg-surface-container-low rounded-xl border border-outline-variant/20">
              <span className="material-symbols-outlined text-primary text-[22px] shrink-0 mt-0.5">gavel</span>
              <p className="text-sm text-on-surface-variant leading-relaxed">
                Mọi thông tin khai báo sẽ được xác thực qua <span className="font-bold text-on-surface">cơ sở dữ liệu quốc gia về dân cư</span>. Hành vi khai báo gian dối sẽ bị xử lý theo quy định pháp luật.
              </p>
            </div>
          </>
        )}

        {/* ════════════════════════════
            STEP 4: Xác nhận & Ký số
        ════════════════════════════ */}
        {currentStep === 4 && (
          <>
            {/* Sub-header */}
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl md:text-3xl font-black text-on-background tracking-tight">Xác nhận &amp; Ký số</h2>
                <p className="text-on-surface-variant font-medium text-sm mt-1">Kiểm tra kỹ thông tin trước khi ký điện tử và nộp hồ sơ</p>
              </div>
              <div className="hidden sm:flex items-center gap-3 bg-surface-container-low px-4 py-2 rounded-xl border border-outline-variant/20">
                <ShieldCheck className="w-5 h-5 text-primary" />
                <div className="text-xs">
                  <p className="font-bold text-on-surface">Bảo mật quốc gia</p>
                  <p className="text-on-surface-variant">NĐ 13/2023/NĐ-CP</p>
                </div>
              </div>
            </div>

            {/* Thông tin hồ sơ + Tiến độ */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
              {/* Application info */}
              <div className="md:col-span-2 bg-surface-container-lowest rounded-xl border border-outline-variant/20 p-6 flex flex-col gap-5">
                <div className="flex items-center justify-between pb-4 border-b border-outline-variant/20">
                  <h3 className="font-bold text-on-surface text-base">Thông tin hồ sơ</h3>
                  <span className="bg-secondary-container text-on-secondary-container text-[10px] font-black px-3 py-1 rounded-full uppercase tracking-wider">Dự thảo</span>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
                  {[
                    { label: 'Họ và tên',          value: 'Nguyễn Văn A' },
                    { label: 'Số CCCD/Định danh',  value: '001234567890' },
                    { label: 'Ngày khởi tạo',      value: new Date().toLocaleDateString('vi-VN') },
                    { label: 'Cơ quan tiếp nhận',  value: `UBND Phường, ${svc?.category ?? '—'}` },
                  ].map(({ label, value }) => (
                    <div key={label}>
                      <p className="text-[10px] font-black uppercase tracking-widest text-on-surface-variant mb-1">{label}</p>
                      <p className="font-semibold text-on-surface text-sm">{value}</p>
                    </div>
                  ))}
                  <div className="sm:col-span-2">
                    <p className="text-[10px] font-black uppercase tracking-widest text-on-surface-variant mb-1">Tên thủ tục hành chính</p>
                    <p className="font-bold text-primary text-sm">{svc?.name ?? '—'} (Dịch vụ công mức độ 4)</p>
                  </div>
                </div>
              </div>

              {/* Progress card */}
              <div className="bg-surface-container-lowest rounded-xl border border-outline-variant/20 p-6 flex flex-col justify-between">
                <div>
                  <p className="text-[10px] font-black uppercase tracking-widest text-on-surface-variant mb-4">Tiến độ hoàn thiện</p>
                  <div className="h-2 bg-surface-container-high rounded-full mb-3 overflow-hidden">
                    <div className="h-full bg-primary rounded-full w-full" />
                  </div>
                  <div className="flex justify-between text-xs font-bold">
                    <span className="text-on-surface">Hồ sơ: 100%</span>
                    <span className="text-primary">Đã sẵn sàng</span>
                  </div>
                </div>
                <div className="mt-6 pt-6 border-t border-outline-variant/20 flex items-start gap-3">
                  <span className="material-symbols-outlined text-secondary text-[20px] shrink-0" style={{ fontVariationSettings: "'FILL' 1" }}>verified_user</span>
                  <p className="text-[11px] text-on-surface-variant leading-relaxed">
                    Dữ liệu mã hóa theo <span className="font-bold text-on-surface">Nghị định 13/2023/NĐ-CP</span>
                  </p>
                </div>
              </div>
            </div>

            {/* Attached files */}
            <div className="bg-surface-container-lowest rounded-xl border border-outline-variant/20 p-6">
              <div className="flex items-center gap-3 mb-5">
                <div className="w-10 h-10 rounded-xl bg-surface-container-low flex items-center justify-center">
                  <Paperclip className="w-5 h-5 text-primary" />
                </div>
                <h3 className="font-bold text-on-surface text-base">Danh mục tệp đính kèm</h3>
              </div>
              {uploadedFiles.length === 0 ? (
                <p className="text-sm text-outline italic py-4 text-center">Chưa có tệp đính kèm nào.</p>
              ) : (
                <div className="space-y-3">
                  {uploadedFiles.map((docKey, i) => {
                    const file = fileObjects[docKey];
                    const isImage = file && /\.(jpg|jpeg|png|webp)$/i.test(file.name);
                    const sizeKB = file ? Math.round(file.size / 1024) : 0;
                    const sizeLabel = sizeKB >= 1024 ? `${(sizeKB / 1024).toFixed(1)} MB` : `${sizeKB} KB`;
                    return (
                      <div key={i} className="group flex items-center justify-between p-4 bg-surface-container-low rounded-xl hover:bg-surface-container hover:shadow-md transition-all duration-200">
                        <div className="flex items-center gap-4 min-w-0">
                          <div className="w-10 h-10 rounded-xl bg-surface-container-lowest flex items-center justify-center text-primary shrink-0">
                            {isImage ? <Image className="w-5 h-5" /> : <FileText className="w-5 h-5" />}
                          </div>
                          <div className="min-w-0">
                            <p className="text-sm font-semibold text-on-surface truncate">{file?.name ?? docKey}</p>
                            <p className="text-[10px] text-on-surface-variant uppercase tracking-wide">{docKey} • {sizeLabel}</p>
                          </div>
                        </div>
                        <button className="text-primary text-xs font-bold uppercase tracking-widest group-hover:underline shrink-0 ml-4">
                          Xem lại
                        </button>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>

            {/* Digital signature selection */}
            <div>
              <h3 className="text-xl font-black text-on-background tracking-tight mb-5">Phương thức ký điện tử</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                {[
                  { id: 'otp' as const, icon: Smartphone, title: 'Ký bằng OTP (SmartCA)', desc: 'Dành cho người dùng có ứng dụng định danh và chữ ký số từ xa.' },
                  { id: 'usb' as const, icon: HardDrive,  title: 'Ký bằng USB Token',     desc: 'Cần kết nối thiết bị USB Token chuyên dụng vào máy tính.' },
                ].map(({ id, icon: Icon, title, desc }) => {
                  const selected = signMethod === id;
                  return (
                    <button
                      key={id}
                      onClick={() => setSignMethod(id)}
                      className={`group text-left p-6 rounded-xl border-2 transition-all duration-300 flex flex-col
                        ${selected
                          ? 'border-primary bg-surface-container-lowest shadow-xl ring-2 ring-primary/20'
                          : 'border-outline-variant/20 bg-surface-container-lowest hover:border-primary/30 hover:shadow-xl'
                        }`}
                    >
                      <div className={`w-14 h-14 rounded-xl flex items-center justify-center mb-5 transition-colors
                        ${selected ? 'bg-primary text-on-primary' : 'bg-surface-container-low group-hover:bg-primary group-hover:text-on-primary'}`}>
                        <Icon className="w-7 h-7" />
                      </div>
                      <h4 className="font-bold text-on-surface text-base mb-2">{title}</h4>
                      <p className="text-on-surface-variant text-sm flex-1">{desc}</p>
                      {selected && (
                        <div className="mt-4 flex items-center gap-2 text-primary">
                          <CheckCircle className="w-4 h-4 fill-primary stroke-white" />
                          <span className="text-[10px] font-black uppercase tracking-widest">Đã chọn</span>
                        </div>
                      )}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Confirmation checkbox */}
            <label className="flex items-start gap-4 cursor-pointer p-6 bg-secondary-container/30 rounded-xl border border-secondary-container hover:bg-secondary-container/50 transition-colors">
              <input
                type="checkbox"
                checked={agreed}
                onChange={e => setAgreed(e.target.checked)}
                className="mt-1 w-5 h-5 text-primary border-outline focus:ring-primary rounded"
              />
              <span className="text-sm font-medium text-on-surface leading-relaxed">
                Tôi cam đoan những thông tin trên là đúng sự thật và hoàn toàn chịu trách nhiệm trước pháp luật về tính chính xác của các giấy tờ, tài liệu đã cung cấp.
              </span>
            </label>
          </>
        )}

        </div>{/* max-w-5xl */}
      </main>

      {/* ── Footer Actions Bar ── */}
      <footer className="fixed bottom-0 left-0 right-0 bg-[#fff4f4]/90 backdrop-blur-md border-t border-outline-variant/20 py-2.5 px-6 md:px-12 z-50">
        <div className="max-w-5xl mx-auto flex justify-between items-center">

          <button
            onClick={handleBack}
            className="flex items-center gap-1.5 px-4 py-2 text-on-surface-variant font-bold hover:text-primary transition-colors text-xs"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            Quay lại
          </button>

          <button
            onClick={currentStep === 4 ? handleSubmit : handleNext}
            disabled={!canContinue}
            className={`flex items-center gap-1.5 px-6 py-2 rounded-lg font-black uppercase tracking-widest text-[11px] transition-all
              ${canContinue
                ? 'bg-primary text-on-primary shadow-md hover:opacity-90 active:scale-95'
                : 'bg-primary/20 text-primary/50 cursor-not-allowed'
              }`}
          >
            {submitting ? (
              <>
                <span className="w-3.5 h-3.5 border-2 border-current border-t-transparent rounded-full animate-spin" />
                Đang gửi...
              </>
            ) : currentStep === 4 ? (
              <>Ký số &amp; Nộp hồ sơ <span className="material-symbols-outlined text-[16px]">send</span></>
            ) : (
              <>Tiếp tục <span className="material-symbols-outlined text-[16px]">arrow_forward</span></>
            )}
          </button>

        </div>
      </footer>

    </div>
  );
}
