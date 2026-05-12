/**
 * SubmitDocumentScreen — Nộp hồ sơ trực tuyến
 * Design: Heritage Bordeaux Red #8f000d + Gold #a17d00
 * Layout: Horizontal stepper + Bento grid cards + Sticky action bar
 *
 * Flow:
 *   Step 1 → chọn thủ tục
 *   Step 2 → xem danh sách giấy tờ (fetch từ API)
 *   Step 3 → tạo draft + upload từng file per-requirement
 *   Step 4 → xác nhận & ký số → submit
 */
import { useState, useRef, useCallback, useEffect } from 'react';
import React from 'react';
import { API_BASE_URL, getToken } from '../services/api';
import { proceduresAPI, Procedure as ProcedureData } from '../services/proceduresService';
import {
  ArrowLeft, CheckCircle, Upload, FileText,
  ShieldCheck, Phone, X, FolderOpen,
  Trash2, CloudUpload,
  Paperclip, Smartphone, HardDrive, Image,
  RefreshCw, AlertCircle,
} from 'lucide-react';

interface SubmitDocumentScreenProps {
  onNavigate: (screen: string) => void;
}

interface Requirement {
  id: string;
  docName: string;
  docDescription: string;
  isRequired: boolean;
  docType: string;
  orderIndex: number;
}

interface UploadedDoc {
  file: File;
  docId: string;
}

interface Service {
  id: string;
  name: string;
  category: string;
  icon: string;
  time: string;
  fee: string;
  feeColor: boolean;
  description: string;
  agency?: string;
  legalBasis?: string[];
}

function procToService(p: ProcedureData): Service {
  return {
    id:         p.id,
    name:       p.name,
    category:   p.categoryLabel || p.category,
    icon:       p.icon,
    time:       p.timeFormatted,
    fee:        p.feeFormatted,
    feeColor:   p.feeColor,
    description: p.agency || p.processingNote || '',
    agency:     p.agency,
    legalBasis: p.legalBasis,
  };
}

const STEPS = ['Chọn loại hồ sơ', 'Chuẩn bị tài liệu', 'Upload hồ sơ', 'Xác nhận & Ký số'];

function authHeaders(): HeadersInit {
  const token = getToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export function SubmitDocumentScreen({ onNavigate }: SubmitDocumentScreenProps) {
  const [currentStep,     setCurrentStep]     = useState(1);
  const [selectedService, setSelectedService] = useState('');

  // Danh sách dịch vụ từ API
  const [services,      setServices]      = useState<Service[]>([]);
  const [loadingServices, setLoadingServices] = useState(true);

  useEffect(() => {
    proceduresAPI.list({ limit: 50 })
      .then(r => setServices((r.data || []).map(procToService)))
      .catch(() => setServices([]))
      .finally(() => setLoadingServices(false));
  }, []);

  // API-driven state
  const [requirements,  setRequirements]  = useState<Requirement[]>([]);
  const [loadingReqs,   setLoadingReqs]   = useState(false);
  const [appId,         setAppId]         = useState<string | null>(null);
  const [uploadedDocs,  setUploadedDocs]  = useState<Record<string, UploadedDoc>>({});
  const [uploading,     setUploading]     = useState<Record<string, boolean>>({});

  // Form fields
  const [submitting,     setSubmitting]     = useState(false);
  const [agreed,         setAgreed]         = useState(false);
  const [notes] = useState('');
  const [contactPhone,   setContactPhone]   = useState('');
  const [contactEmail,   setContactEmail]   = useState('');
  const [contactAddress, setContactAddress] = useState('');
  const [signMethod,     setSignMethod]     = useState<'otp' | 'usb' | ''>('');
  const [error,          setError]          = useState('');
  const [submitted,      setSubmitted]      = useState(false);

  const fileInputsRef  = useRef<Record<string, HTMLInputElement | null>>({});
  const MAX_FILE_BYTES = 16 * 1024 * 1024; // 16 MB

  const svc              = services.find(s => s.id === selectedService);
  const uploadedCount    = Object.keys(uploadedDocs).length;
  const requiredCount    = requirements.filter(r => r.isRequired).length;
  const requiredUploaded = requirements.filter(r => r.isRequired).every(r => uploadedDocs[r.id]);

  // ── Step navigation ────────────────────────────────────────────────────────

  const handleBack = async () => {
    setError('');
    // Nếu đang ở Step 3 và có draft → xóa draft trước khi quay về Step 2
    if (currentStep === 3 && appId) {
      try {
        await fetch(`${API_BASE_URL}/applications/${appId}/draft`, {
          method: 'DELETE', headers: authHeaders(),
        });
      } catch { /* non-fatal */ }
      setAppId(null);
      setUploadedDocs({});
    }
    if (currentStep > 1) setCurrentStep(s => s - 1);
    else onNavigate('home');
  };

  const handleNext = useCallback(async () => {
    setError('');

    // Step 1 → 2: fetch requirements
    if (currentStep === 1) {
      if (!selectedService) return;
      setLoadingReqs(true);
      try {
        const resp = await fetch(`${API_BASE_URL}/applications/requirements/${selectedService}`, {
          headers: { 'Content-Type': 'application/json', ...authHeaders() },
        });
        const data = await resp.json();
        if (data.success && Array.isArray(data.requirements)) {
          setRequirements(
            [...data.requirements].sort((a: Requirement, b: Requirement) => a.orderIndex - b.orderIndex)
          );
          setCurrentStep(2);
        } else {
          setError(data.message || 'Không thể tải danh sách giấy tờ');
        }
      } catch {
        setError('Lỗi kết nối. Vui lòng thử lại.');
      } finally {
        setLoadingReqs(false);
      }
      return;
    }

    // Step 2 → 3: create draft application
    if (currentStep === 2) {
      try {
        const resp = await fetch(`${API_BASE_URL}/applications/draft`, {
          method:  'POST',
          headers: { 'Content-Type': 'application/json', ...authHeaders() },
          body: JSON.stringify({
            serviceId: selectedService,
            data: { contactPhone, contactEmail, contactAddress, notes },
          }),
        });
        const data = await resp.json();
        if (data.success && data.data?.application?.id) {
          setAppId(data.data.application.id);
          setCurrentStep(3);
        } else {
          setError(data.message || 'Không thể tạo hồ sơ nháp. Vui lòng đăng nhập để tiếp tục.');
        }
      } catch {
        setError('Lỗi kết nối khi tạo hồ sơ nháp.');
      }
      return;
    }

    // Step 3 → 4: kiểm tra tất cả giấy tờ bắt buộc đã upload
    if (currentStep === 3) {
      if (uploadedCount === 0) { setError('Vui lòng upload ít nhất 1 tài liệu.'); return; }
      if (!requiredUploaded) {
        const missing = requirements.filter(r => r.isRequired && !uploadedDocs[r.id]).map(r => r.docName);
        setError(`Còn thiếu giấy tờ bắt buộc: ${missing.join(', ')}`);
        return;
      }
      setCurrentStep(4);
    }
  }, [currentStep, selectedService, uploadedCount, requiredUploaded, requirements, uploadedDocs, contactPhone, contactEmail, contactAddress, notes]);

  // ── File upload (per requirement) ──────────────────────────────────────────

  const handleFilePick = (reqId: string) => fileInputsRef.current[reqId]?.click();

  const onFileChange = useCallback(async (req: Requirement, e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    // Reset so same file can be picked again after removal
    if (e.target) e.target.value = '';
    if (!file || !appId) return;

    // Kiểm tra kích thước file trước khi upload
    if (file.size > MAX_FILE_BYTES) {
      setError(`File "${file.name}" quá lớn (${(file.size / 1024 / 1024).toFixed(1)} MB). Tối đa 16 MB.`);
      return;
    }

    setUploading(prev => ({ ...prev, [req.id]: true }));
    setError('');

    // If there's an existing doc for this requirement, delete it first
    const existing = uploadedDocs[req.id];
    if (existing?.docId) {
      try {
        await fetch(`${API_BASE_URL}/applications/${appId}/documents/${existing.docId}`, {
          method:  'DELETE',
          headers: authHeaders(),
        });
      } catch {
        // Non-fatal — continue with new upload
      }
    }

    try {
      const form = new FormData();
      form.append('file', file);
      form.append('requirementId', req.id);
      const resp = await fetch(`${API_BASE_URL}/applications/${appId}/documents`, {
        method:  'POST',
        headers: authHeaders(),
        body:    form,
      });
      const data = await resp.json();
      if (data.success && data.data?.document?.id) {
        setUploadedDocs(prev => ({ ...prev, [req.id]: { file, docId: data.data.document.id } }));
      } else {
        setError(data.message || 'Lỗi khi upload file');
      }
    } catch {
      setError('Lỗi upload file. Vui lòng thử lại.');
    } finally {
      setUploading(prev => ({ ...prev, [req.id]: false }));
    }
  }, [appId, uploadedDocs]);

  const removeFile = useCallback(async (reqId: string) => {
    const doc = uploadedDocs[reqId];
    if (!doc || !appId) return;
    try {
      await fetch(`${API_BASE_URL}/applications/${appId}/documents/${doc.docId}`, {
        method:  'DELETE',
        headers: authHeaders(),
      });
    } catch {
      // Non-fatal
    }
    setUploadedDocs(prev => {
      const next = { ...prev };
      delete next[reqId];
      return next;
    });
  }, [appId, uploadedDocs]);

  // ── Final submit ───────────────────────────────────────────────────────────

  const handleSubmit = useCallback(async () => {
    if (!agreed || !appId) return;
    setError('');
    setSubmitting(true);
    try {
      const resp = await fetch(`${API_BASE_URL}/applications/${appId}/submit`, {
        method:  'PUT',
        headers: { 'Content-Type': 'application/json', ...authHeaders() },
        body: JSON.stringify({
          signatureType: signMethod === 'otp' ? 'electronic' : signMethod === 'usb' ? 'usb_token' : undefined,
          data: { contactPhone, contactEmail, contactAddress, notes },
        }),
      });
      const data = await resp.json();
      if (data.success) {
        setSubmitted(true);
      } else {
        if (Array.isArray(data.missing) && data.missing.length > 0) {
          setError(`Còn thiếu giấy tờ bắt buộc: ${data.missing.join(', ')}`);
        } else {
          setError(data.message || 'Lỗi nộp hồ sơ');
        }
      }
    } catch {
      setError('Lỗi kết nối khi nộp hồ sơ.');
    } finally {
      setSubmitting(false);
    }
  }, [agreed, appId, signMethod, contactPhone, contactEmail, contactAddress, notes, onNavigate]);

  const canContinue =
    (currentStep === 1 && !!selectedService) ||
    currentStep === 2 ||
    (currentStep === 3 && uploadedCount > 0 && requiredUploaded) ||
    (currentStep === 4 && agreed && !!signMethod && !submitting);

  /* ── Success screen ── */
  if (submitted) {
    return (
      <div className="bg-[#fff4f4] min-h-screen flex items-center justify-center px-6" style={{ fontFamily: "'Manrope', sans-serif" }}>
        <div className="max-w-md w-full text-center space-y-6">
          <div className="w-20 h-20 rounded-full bg-green-50 flex items-center justify-center mx-auto">
            <CheckCircle className="w-10 h-10 text-green-600" />
          </div>
          <div>
            <h2 className="text-2xl font-black text-on-background mb-2">Nộp hồ sơ thành công!</h2>
            <p className="text-on-surface-variant text-sm">Hồ sơ của bạn đã được tiếp nhận và đang được xử lý.</p>
          </div>
          <div className="bg-surface-container-low rounded-xl p-4 text-left space-y-2">
            <p className="text-[10px] font-black uppercase tracking-widest text-on-surface-variant">Mã hồ sơ</p>
            <p className="font-mono font-bold text-lg text-primary">{appId ? appId.slice(0, 8).toUpperCase() : '—'}</p>
            <p className="text-xs text-on-surface-variant">Lưu mã này để tra cứu trạng thái hồ sơ.</p>
          </div>
          <div className="bg-surface-container-low rounded-xl p-4 text-left space-y-1">
            <p className="text-[10px] font-black uppercase tracking-widest text-on-surface-variant">Thủ tục</p>
            <p className="font-semibold text-on-surface text-sm">{svc?.name}</p>
          </div>
          <div className="flex gap-3 pt-2">
            <button onClick={() => onNavigate('home')}
              className="flex-1 py-3 px-6 bg-primary text-on-primary font-black rounded-xl text-sm hover:opacity-90 transition-opacity">
              Về trang chủ
            </button>
            <button onClick={() => onNavigate('search')}
              className="flex-1 py-3 px-6 bg-surface-container text-on-surface font-bold rounded-xl text-sm hover:bg-surface-container-high transition-colors">
              Tra cứu hồ sơ
            </button>
          </div>
        </div>
      </div>
    );
  }

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
              const done   = n < currentStep;
              const active = n === currentStep;
              return (
                <div key={n} className="relative z-10 flex flex-col items-center gap-1">
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-xs shadow
                    ${done ? 'bg-secondary text-on-secondary' : active ? 'bg-primary text-on-primary' : 'bg-surface-container-high text-on-surface-variant'}`}>
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

      {/* ── Error banner ── */}
      {error && (
        <div className="max-w-5xl mx-auto px-6 md:px-12 pt-4 w-full">
          <div className="flex items-start gap-3 p-4 bg-red-50 border border-red-200 rounded-xl text-sm text-red-700">
            <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
            <span>{error}</span>
            <button onClick={() => setError('')} className="ml-auto shrink-0"><X className="w-4 h-4" /></button>
          </div>
        </div>
      )}

      {/* ── Main ── */}
      <main className="flex-1 px-6 md:px-12 pb-16">
        <div className="max-w-5xl mx-auto space-y-8 pt-8">

        {/* ════════════════════════════
            STEP 1: Chọn loại hồ sơ
        ════════════════════════════ */}
        {currentStep === 1 && (
          <>
            {loadingServices && (
              <div className="flex justify-center py-12">
                <RefreshCw className="w-6 h-6 animate-spin text-primary" />
              </div>
            )}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {services.map(service => {
                const selected = selectedService === service.id;
                return (
                  <button key={service.id} onClick={() => setSelectedService(service.id)}
                    className={`group text-left bg-surface-container-lowest p-6 rounded-xl border transition-all duration-300 flex flex-col h-full
                      ${selected ? 'border-primary/50 shadow-xl ring-2 ring-primary/20' : 'border-outline-variant/20 hover:border-primary/30 hover:shadow-xl'}`}>
                    <div className={`w-14 h-14 rounded-xl flex items-center justify-center mb-6 transition-colors text-3xl
                      ${selected ? 'bg-primary text-on-primary' : 'bg-surface-container-low group-hover:bg-primary group-hover:text-on-primary'}`}>
                      {service.icon}
                    </div>
                    <h3 className="text-xl font-bold mb-2 text-on-surface">{service.name}</h3>
                    <p className="text-on-surface-variant text-sm mb-6 flex-1">{service.description}</p>
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

            <div className="relative overflow-hidden bg-gradient-to-r from-primary to-primary-container rounded-2xl p-8 flex flex-col md:flex-row items-center justify-between gap-6 shadow-xl">
              <div className="relative z-10">
                <h2 className="text-2xl font-black text-on-primary mb-2">Hỗ trợ tư vấn pháp lý trực tuyến</h2>
                <p className="text-on-primary/80 max-w-lg font-medium text-sm">Đội ngũ chuyên gia pháp lý luôn sẵn sàng hỗ trợ bạn hoàn thiện hồ sơ nhanh chóng và chính xác nhất.</p>
              </div>
              <button className="relative z-10 flex items-center gap-2 px-8 py-4 bg-secondary-container text-on-secondary-container font-black rounded-xl hover:scale-105 active:scale-95 transition-transform shadow-lg whitespace-nowrap text-sm">
                <Phone className="w-4 h-4" /> Hỗ trợ ngay
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
                  <p className="font-bold text-on-surface">{requirements.length} tài liệu</p>
                  <p className="text-on-surface-variant">Cần chuẩn bị</p>
                </div>
              </div>
            </div>

            {loadingReqs ? (
              <div className="flex justify-center py-12">
                <RefreshCw className="w-6 h-6 animate-spin text-primary" />
              </div>
            ) : requirements.length === 0 ? (
              <p className="text-center text-on-surface-variant py-8">Không có dữ liệu giấy tờ cho thủ tục này.</p>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                {requirements.map((req, i) => (
                  <div key={req.id}
                    className="group bg-surface-container-lowest p-6 rounded-xl border border-outline-variant/20 hover:border-primary/30 hover:shadow-xl transition-all duration-300 flex flex-col">
                    <div className="flex items-start gap-4 mb-4">
                      <div className="w-10 h-10 rounded-xl bg-surface-container-low group-hover:bg-primary group-hover:text-on-primary flex items-center justify-center font-black text-sm text-primary transition-colors shrink-0">
                        {String(i + 1).padStart(2, '0')}
                      </div>
                      <div className="flex-1 min-w-0">
                        <h4 className="font-bold text-on-surface text-base leading-tight">{req.docName}</h4>
                        {!req.isRequired && (
                          <span className="text-[10px] text-on-surface-variant bg-surface-container px-2 py-0.5 rounded-full">Không bắt buộc</span>
                        )}
                      </div>
                    </div>
                    <p className="text-on-surface-variant text-sm leading-relaxed flex-1">
                      {req.docDescription || `Loại: ${req.docType}`}
                    </p>
                  </div>
                ))}
              </div>
            )}

            <div className="flex items-start gap-4 p-5 bg-surface-container-low rounded-xl border border-outline-variant/20">
              <span className="material-symbols-outlined text-primary text-[22px] shrink-0 mt-0.5">info</span>
              <p className="text-sm text-on-surface-variant leading-relaxed">
                Vui lòng chuẩn bị <span className="font-bold text-on-surface">bản quét (scan) hoặc ảnh chụp rõ nét</span> của các tài liệu trên. Hệ thống hỗ trợ định dạng <span className="font-bold text-primary">.pdf, .jpg, .png</span>.
              </p>
            </div>
          </>
        )}

        {/* ════════════════════════════
            STEP 3: Upload hồ sơ
        ════════════════════════════ */}
        {currentStep === 3 && (
          <>
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl md:text-3xl font-black text-on-background tracking-tight">Upload hồ sơ</h2>
                <p className="text-on-surface-variant font-medium text-sm mt-1">
                  Thủ tục: <span className="font-bold text-primary">{svc?.name}</span>
                </p>
              </div>
              <div className="hidden sm:flex items-center gap-3 bg-surface-container-low px-4 py-2 rounded-xl border border-outline-variant/20">
                <span className={`material-symbols-outlined text-[20px] ${uploadedCount >= requiredCount && requiredCount > 0 ? 'text-green-600' : 'text-primary'}`}
                  style={{ fontVariationSettings: "'FILL' 1" }}>
                  {uploadedCount >= requiredCount && requiredCount > 0 ? 'check_circle' : 'upload_file'}
                </span>
                <div className="text-xs">
                  <p className="font-bold text-on-surface">{uploadedCount}/{requirements.length} tệp</p>
                  <p className="text-on-surface-variant">Đã tải lên</p>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
              {requirements.map((req, i) => {
                const uploaded = uploadedDocs[req.id];
                const isUploading = uploading[req.id];
                const file = uploaded?.file;
                const fileSizeKB = file ? Math.round(file.size / 1024) : 0;
                const fileSizeLabel = fileSizeKB >= 1024 ? `${(fileSizeKB / 1024).toFixed(1)} MB` : `${fileSizeKB} KB`;

                return (
                  <div key={req.id}>
                    <input
                      type="file"
                      accept="image/*,application/pdf"
                      aria-label={`Tải lên: ${req.docName}`}
                      className="hidden"
                      ref={el => { fileInputsRef.current[req.id] = el; }}
                      onChange={e => onFileChange(req, e)}
                    />

                    {isUploading ? (
                      <div className="bg-surface-container-lowest p-6 rounded-xl border border-outline-variant/20 flex items-center gap-3">
                        <RefreshCw className="w-5 h-5 animate-spin text-primary" />
                        <p className="text-sm text-on-surface-variant">Đang tải lên {req.docName}…</p>
                      </div>
                    ) : uploaded ? (
                      <div className="group bg-surface-container-lowest p-6 rounded-xl border border-green-200 hover:shadow-lg transition-all duration-300">
                        <div className="flex items-start gap-4">
                          <div className="w-10 h-10 rounded-xl bg-green-50 flex items-center justify-center shrink-0">
                            <CheckCircle className="w-5 h-5 text-green-600 fill-green-600 stroke-white" />
                          </div>
                          <div className="flex-1 min-w-0">
                            <p className="font-bold text-on-surface text-sm leading-tight mb-1">
                              {String(i + 1).padStart(2, '0')}. {req.docName}
                            </p>
                            <div className="flex items-center gap-2 text-[11px] text-on-surface-variant">
                              <FileText className="w-3 h-3 shrink-0 text-primary" />
                              <span className="truncate max-w-[160px] font-medium text-primary">{file?.name}</span>
                              <span className="shrink-0">({fileSizeLabel})</span>
                            </div>
                          </div>
                          <div className="flex items-center gap-1 shrink-0">
                            <button aria-label="Đổi file" className="p-1.5 text-on-surface-variant hover:text-primary rounded-lg hover:bg-surface-container transition-colors"
                              onClick={() => handleFilePick(req.id)}>
                              <Upload className="w-4 h-4" />
                            </button>
                            <button onClick={() => removeFile(req.id)} aria-label="Xóa" className="p-1.5 text-on-surface-variant hover:text-red-600 rounded-lg hover:bg-surface-container transition-colors">
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </div>
                        </div>
                      </div>
                    ) : (
                      <div onClick={() => handleFilePick(req.id)}
                        onDragOver={e => e.preventDefault()}
                        onDrop={e => {
                          e.preventDefault();
                          const f = e.dataTransfer.files?.[0];
                          if (f) onFileChange(req, { target: { files: e.dataTransfer.files, value: '' } } as any);
                        }}
                        className="group bg-surface-container-lowest p-6 rounded-xl border-2 border-dashed border-outline-variant/40 hover:border-primary/50 hover:shadow-xl transition-all duration-300 cursor-pointer">
                        <div className="flex items-start gap-4 mb-4">
                          <div className="w-10 h-10 rounded-xl bg-surface-container-low group-hover:bg-primary group-hover:text-on-primary flex items-center justify-center text-primary transition-colors shrink-0">
                            <span className="material-symbols-outlined text-[20px]">upload_file</span>
                          </div>
                          <div className="flex-1 min-w-0">
                            <p className="font-bold text-on-surface text-sm leading-tight">
                              {String(i + 1).padStart(2, '0')}. {req.docName}
                              {req.isRequired && <span className="text-red-500 ml-1">*</span>}
                            </p>
                            <p className="text-[11px] text-on-surface-variant mt-0.5">PDF, JPG, PNG — tối đa 16MB</p>
                          </div>
                          <button onClick={e => { e.stopPropagation(); handleFilePick(req.id); }}
                            className="flex items-center gap-1.5 px-4 py-2 bg-primary text-on-primary text-xs font-black uppercase tracking-widest rounded-lg hover:opacity-90 transition-opacity shrink-0">
                            <CloudUpload className="w-3.5 h-3.5" /> Tải lên
                          </button>
                        </div>
                        <div className="flex items-center justify-center gap-2 py-3 border-t border-dashed border-outline-variant/30 text-[11px] text-outline font-medium">
                          <Upload className="w-3.5 h-3.5" /> Kéo và thả file tại đây
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>

            {/* Contact info */}
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
                  { label: 'Số điện thoại *', type: 'tel',   value: contactPhone,   setter: setContactPhone,   placeholder: '09x xxxx xxx' },
                  { label: 'Email nhận thông báo *', type: 'email', value: contactEmail, setter: setContactEmail, placeholder: 'email@example.com' },
                ].map(({ label, type, value, setter, placeholder }) => (
                  <div key={label}>
                    <label className="block text-[10px] font-black uppercase tracking-widest text-on-surface-variant mb-2">{label}</label>
                    <input type={type} value={value} onChange={e => setter(e.target.value)}
                      placeholder={placeholder}
                      className="w-full bg-surface-container-low border-none border-b-2 border-outline focus:border-primary outline-none text-sm font-medium py-2.5 px-3 rounded-lg transition-colors placeholder:text-outline/50" />
                  </div>
                ))}
                <div className="md:col-span-2">
                  <label className="block text-[10px] font-black uppercase tracking-widest text-on-surface-variant mb-2">Địa chỉ thường trú *</label>
                  <textarea rows={2} value={contactAddress} onChange={e => setContactAddress(e.target.value)}
                    placeholder="Số nhà, đường, phường/xã, quận/huyện, tỉnh/thành phố"
                    className="w-full bg-surface-container-low border-none outline-none text-sm font-medium py-2.5 px-3 rounded-lg transition-colors placeholder:text-outline/50 resize-none focus:ring-2 focus:ring-primary" />
                </div>
              </div>
            </div>

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

            <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
              <div className="md:col-span-2 bg-surface-container-lowest rounded-xl border border-outline-variant/20 p-6 flex flex-col gap-5">
                <div className="flex items-center justify-between pb-4 border-b border-outline-variant/20">
                  <h3 className="font-bold text-on-surface text-base">Thông tin hồ sơ</h3>
                  <span className="bg-secondary-container text-on-secondary-container text-[10px] font-black px-3 py-1 rounded-full uppercase tracking-wider">Dự thảo</span>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
                  {[
                    { label: 'Thủ tục',             value: svc?.name ?? '—' },
                    { label: 'Cơ quan tiếp nhận',   value: `UBND Phường, ${svc?.category ?? '—'}` },
                    { label: 'Số điện thoại',        value: contactPhone || '—' },
                    { label: 'Email',                value: contactEmail || '—' },
                    { label: 'Ngày khởi tạo',        value: new Date().toLocaleDateString('vi-VN') },
                    { label: 'Mã hồ sơ',             value: appId ? appId.slice(0, 8).toUpperCase() : '—' },
                  ].map(({ label, value }) => (
                    <div key={label}>
                      <p className="text-[10px] font-black uppercase tracking-widest text-on-surface-variant mb-1">{label}</p>
                      <p className="font-semibold text-on-surface text-sm">{value}</p>
                    </div>
                  ))}
                </div>
              </div>

              <div className="bg-surface-container-lowest rounded-xl border border-outline-variant/20 p-6 flex flex-col justify-between">
                <div>
                  <p className="text-[10px] font-black uppercase tracking-widest text-on-surface-variant mb-4">Tiến độ hoàn thiện</p>
                  <div className="h-2 bg-surface-container-high rounded-full mb-3 overflow-hidden">
                    <div
                      className="h-full bg-primary rounded-full transition-all duration-500"
                      style={{ width: requirements.length > 0 ? `${Math.round((uploadedCount / requirements.length) * 100)}%` : '0%' }}
                    />
                  </div>
                  <div className="flex justify-between text-xs font-bold">
                    <span className="text-on-surface">Hồ sơ: {uploadedCount}/{requirements.length} file</span>
                    <span className={requiredUploaded ? 'text-green-600' : 'text-primary'}>
                      {requiredUploaded ? 'Đầy đủ' : 'Chưa đủ bắt buộc'}
                    </span>
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
                <h3 className="font-bold text-on-surface text-base">Danh mục tệp đính kèm ({uploadedCount} file)</h3>
              </div>
              {uploadedCount === 0 ? (
                <p className="text-sm text-outline italic py-4 text-center">Chưa có tệp đính kèm nào.</p>
              ) : (
                <div className="space-y-3">
                  {Object.entries(uploadedDocs).map(([reqId, doc]) => {
                    const req  = requirements.find(r => r.id === reqId);
                    const file = doc.file;
                    const isImage = /\.(jpg|jpeg|png|webp)$/i.test(file.name);
                    const sizeKB  = Math.round(file.size / 1024);
                    const sizeLabel = sizeKB >= 1024 ? `${(sizeKB / 1024).toFixed(1)} MB` : `${sizeKB} KB`;
                    return (
                      <div key={reqId} className="group flex items-center justify-between p-4 bg-surface-container-low rounded-xl hover:bg-surface-container hover:shadow-md transition-all duration-200">
                        <div className="flex items-center gap-4 min-w-0">
                          <div className="w-10 h-10 rounded-xl bg-surface-container-lowest flex items-center justify-center text-primary shrink-0">
                            {isImage ? <Image className="w-5 h-5" /> : <FileText className="w-5 h-5" />}
                          </div>
                          <div className="min-w-0">
                            <p className="text-sm font-semibold text-on-surface truncate">{file.name}</p>
                            <p className="text-[10px] text-on-surface-variant uppercase tracking-wide">
                              {req?.docName ?? reqId} • {sizeLabel}
                            </p>
                          </div>
                        </div>
                        <CheckCircle className="w-4 h-4 text-green-600 shrink-0 ml-4" />
                      </div>
                    );
                  })}
                </div>
              )}
            </div>

            {/* Digital signature */}
            <div>
              <h3 className="text-xl font-black text-on-background tracking-tight mb-5">Phương thức ký điện tử</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                {[
                  { id: 'otp' as const, icon: Smartphone, title: 'Ký bằng OTP (SmartCA)', desc: 'Dành cho người dùng có ứng dụng định danh và chữ ký số từ xa.' },
                  { id: 'usb' as const, icon: HardDrive,  title: 'Ký bằng USB Token',     desc: 'Cần kết nối thiết bị USB Token chuyên dụng vào máy tính.' },
                ].map(({ id, icon: Icon, title, desc }) => {
                  const selected = signMethod === id;
                  return (
                    <button key={id} onClick={() => setSignMethod(id)}
                      className={`group text-left p-6 rounded-xl border-2 transition-all duration-300 flex flex-col
                        ${selected ? 'border-primary bg-surface-container-lowest shadow-xl ring-2 ring-primary/20' : 'border-outline-variant/20 bg-surface-container-lowest hover:border-primary/30 hover:shadow-xl'}`}>
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

            <label className="flex items-start gap-4 cursor-pointer p-6 bg-secondary-container/30 rounded-xl border border-secondary-container hover:bg-secondary-container/50 transition-colors">
              <input type="checkbox" checked={agreed} onChange={e => setAgreed(e.target.checked)}
                className="mt-1 w-5 h-5 text-primary border-outline focus:ring-primary rounded" />
              <span className="text-sm font-medium text-on-surface leading-relaxed">
                Tôi cam đoan những thông tin trên là đúng sự thật và hoàn toàn chịu trách nhiệm trước pháp luật về tính chính xác của các giấy tờ, tài liệu đã cung cấp.
              </span>
            </label>
          </>
        )}

        </div>
      </main>

      {/* ── Footer Actions Bar ── */}
      <footer className="fixed bottom-0 left-0 right-0 bg-[#fff4f4]/90 backdrop-blur-md border-t border-outline-variant/20 py-2.5 px-6 md:px-12 z-50">
        <div className="max-w-5xl mx-auto flex justify-between items-center">
          <button onClick={handleBack}
            className="flex items-center gap-1.5 px-4 py-2 text-on-surface-variant font-bold hover:text-primary transition-colors text-xs">
            <ArrowLeft className="w-3.5 h-3.5" /> Quay lại
          </button>

          <button
            onClick={currentStep === 4 ? handleSubmit : handleNext}
            disabled={!canContinue || loadingReqs}
            className={`flex items-center gap-1.5 px-6 py-2 rounded-lg font-black uppercase tracking-widest text-[11px] transition-all
              ${canContinue && !loadingReqs
                ? 'bg-primary text-on-primary shadow-md hover:opacity-90 active:scale-95'
                : 'bg-primary/20 text-primary/50 cursor-not-allowed'
              }`}
          >
            {loadingReqs || submitting ? (
              <>
                <span className="w-3.5 h-3.5 border-2 border-current border-t-transparent rounded-full animate-spin" />
                {loadingReqs ? 'Đang tải...' : 'Đang gửi...'}
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
