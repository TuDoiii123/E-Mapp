/**
 * AdminApplicationsScreen — Quản lý hồ sơ
 * Hero header + plinth search + status filter chips
 * Application cards with accent-bar, status badge, review actions
 * Bottom stats row + ReviewModal
 */
import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  Search, RefreshCw, ChevronLeft, ChevronRight,
  Eye, ClipboardList, FileText, CheckCircle,
  AlertCircle, ThumbsUp, ThumbsDown, MessageSquare,
  X, Clock, TrendingUp, FolderOpen,
  Download, ImageIcon, FileIcon, History, ChevronDown, ChevronUp,
} from 'lucide-react';
import * as adminSvc from '../../services/adminService';
import { API_BASE_URL, getToken } from '../../services/api';

/**
 * Fetch a protected file with the JWT Bearer token, return a blob URL.
 * The blob URL is revoked automatically when the component unmounts.
 */
function useAuthedBlobUrl(apiUrl: string | null): { blobUrl: string | null; loading: boolean; error: boolean } {
  const [blobUrl, setBlobUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error,   setError]   = useState(false);

  useEffect(() => {
    if (!apiUrl) return;
    let revoke: string | null = null;
    let cancelled = false;
    setLoading(true);
    setError(false);

    const token = getToken();
    fetch(apiUrl, { headers: token ? { Authorization: `Bearer ${token}` } : {} })
      .then(r => {
        if (!r.ok) throw new Error(`${r.status}`);
        return r.blob();
      })
      .then(blob => {
        if (cancelled) return;
        revoke = URL.createObjectURL(blob);
        setBlobUrl(revoke);
      })
      .catch(() => { if (!cancelled) setError(true); })
      .finally(() => { if (!cancelled) setLoading(false); });

    return () => {
      cancelled = true;
      if (revoke) URL.revokeObjectURL(revoke);
      setBlobUrl(null);
    };
  }, [apiUrl]);

  return { blobUrl, loading, error };
}

interface Props { onNavigate: (screen: string, params?: any) => void }

const PRIMARY = '#8f000d';
const GOLD    = '#fcd400';

// ── Status config ──────────────────────────────────────────────────────────────
const STATUS_CFG: Record<string, {
  label: string;
  badge: string;           // badge classes
  accent: string;          // left-bar color (inline style)
}> = {
  submitted: {
    label:  'Đã nộp',
    badge:  'bg-blue-100 text-blue-700',
    accent: '#3b82f6',
  },
  in_review: {
    label:  'Đang xét duyệt',
    badge:  'bg-[#fcd400] text-[#6e5c00]',
    accent: PRIMARY,
  },
  more_info: {
    label:  'Cần bổ sung',
    badge:  'bg-[#b22222] text-[#ffc8c2]',
    accent: GOLD,
  },
  approved: {
    label:  'Đã duyệt',
    badge:  'bg-[#e2e2e2] text-[#1a1c1c]',
    accent: '#6b7280',
  },
  rejected: {
    label:  'Từ chối',
    badge:  'bg-red-700 text-red-100',
    accent: '#dc2626',
  },
};

const FILTER_OPTS = [
  { value: '',           label: 'Tất cả'     },
  { value: 'submitted',  label: 'Đã nộp'     },
  { value: 'in_review',  label: 'Đang xét'   },
  { value: 'more_info',  label: 'Cần bổ sung'},
  { value: 'approved',   label: 'Đã duyệt'   },
  { value: 'rejected',   label: 'Từ chối'    },
];

const PAGE_SIZE = 12;

// ── Toast ──────────────────────────────────────────────────────────────────────
function Toast({ text, ok }: { text: string; ok: boolean }) {
  return (
    <div className={`fixed bottom-24 left-1/2 -translate-x-1/2 z-50 px-4 py-2.5 rounded-full
      shadow-lg text-sm font-medium text-white flex items-center gap-2 whitespace-nowrap
      ${ok ? 'bg-green-600' : 'bg-red-700'}`}>
      {ok
        ? <CheckCircle className="w-4 h-4 flex-shrink-0" />
        : <AlertCircle className="w-4 h-4 flex-shrink-0" />}
      {text}
    </div>
  );
}

// ── ReviewModal ────────────────────────────────────────────────────────────────
function ReviewModal({ app, onClose, onDone }: {
  app: any; onClose(): void; onDone(action: string, note: string): void;
}) {
  const [action, setAction] = useState('');
  const [note,   setNote]   = useState('');

  const OPTIONS = [
    { val: 'approve',           label: 'Duyệt',            Icon: ThumbsUp,      cls: 'border-green-400 text-green-700 bg-green-50'   },
    { val: 'reject',            label: 'Từ chối',           Icon: ThumbsDown,    cls: 'border-red-400 text-red-700 bg-red-50'         },
    { val: 'request_more_info', label: 'Yêu cầu\nbổ sung', Icon: MessageSquare, cls: 'border-amber-400 text-amber-700 bg-amber-50'   },
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 px-4">
      <div className="bg-white rounded-2xl w-full max-w-lg p-5 space-y-4 max-h-[88vh] overflow-y-auto shadow-2xl">
        <div className="flex items-center justify-between">
          <h3 className="font-bold text-gray-800 text-base">Xét duyệt hồ sơ</h3>
          <button onClick={onClose} className="p-1 rounded-lg hover:bg-[#fff4f4] transition-colors">
            <X className="w-5 h-5 text-gray-400" />
          </button>
        </div>

        {/* Thông tin hồ sơ */}
        <div className="bg-[#fff4f4] rounded-xl p-3.5 space-y-1.5 border-l-4" style={{ borderColor: PRIMARY }}>
          <p className="text-sm font-semibold text-gray-800 leading-snug">
            {app.procedureName || app.procedureId || 'Thủ tục hành chính'}
          </p>
          <p className="text-xs text-gray-500">Người nộp: <span className="font-medium text-gray-700">{app.applicantName || app.applicantId}</span></p>
          <p className="text-xs text-gray-500 font-mono">Mã: {app.id}</p>
        </div>

        {/* Lựa chọn hành động */}
        <div className="grid grid-cols-3 gap-2">
          {OPTIONS.map(o => (
            <button key={o.val}
              className={`border-2 rounded-xl p-3 flex flex-col items-center gap-1.5 text-xs font-medium
                transition-all leading-tight text-center
                ${action === o.val ? o.cls + ' ring-2 ring-offset-1 ring-current' : 'border-[#de9ca4]/30 text-[#4d2128]/70 hover:border-[#de9ca4]'}`}
              onClick={() => setAction(o.val)}>
              <o.Icon className="w-5 h-5" />
              {o.label}
            </button>
          ))}
        </div>

        {/* Ghi chú */}
        <div>
          <label className="text-xs text-gray-500 font-medium">Ghi chú</label>
          <textarea value={note} onChange={e => setNote(e.target.value)}
            rows={3} placeholder="Nhập ghi chú (nếu có)..."
            className="mt-1.5 w-full border border-[#de9ca4]/30 rounded-xl px-3 py-2.5 text-sm
              resize-none focus:outline-none focus:border-[#8f000d] transition-colors bg-white" />
        </div>

        <div className="flex gap-3 pt-1">
          <button onClick={onClose}
            className="flex-1 h-11 rounded-xl border border-[#de9ca4]/30 text-sm font-medium
              text-[#4d2128]/70 hover:bg-[#fff4f4] transition-colors">
            Hủy
          </button>
          <button
            disabled={!action}
            onClick={() => action && onDone(action, note)}
            className="flex-1 h-11 rounded-xl text-sm font-semibold text-white transition-colors
              disabled:opacity-40 disabled:cursor-not-allowed"
            style={{ backgroundColor: action ? PRIMARY : '#ccc' }}>
            Xác nhận
          </button>
        </div>
      </div>
    </div>
  );
}

// ── File helpers ──────────────────────────────────────────────────────────────
function fileUrl(filename: string): string {
  // Route: GET /api/applications/uploads/<filename>
  return `${API_BASE_URL}/applications/uploads/${filename}`;
}

function formatSize(bytes: number | null | undefined): string {
  if (!bytes) return '—';
  if (bytes < 1024)       return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function FileTypeIcon({ mimeType }: { mimeType?: string }) {
  const m = (mimeType || '').toLowerCase();
  if (m.startsWith('image/'))
    return <ImageIcon className="w-4 h-4 text-blue-500" />;
  if (m === 'application/pdf')
    return <FileText className="w-4 h-4 text-red-600" />;
  return <FileIcon className="w-4 h-4 text-gray-400" />;
}

// ── DocPreviewPanel ────────────────────────────────────────────────────────────
function DocPreviewPanel({ doc, onClose }: { doc: any; onClose(): void }) {
  const apiUrl = fileUrl(doc.filename);
  const mime   = (doc.mimeType || '').toLowerCase();
  const isImage = mime.startsWith('image/');
  const isPdf   = mime === 'application/pdf';
  const isWord  = mime.includes('word') || mime.includes('openxmlformats');

  // Fetch with auth headers → blob URL (fixes 401 for img/iframe/download)
  const { blobUrl, loading, error } = useAuthedBlobUrl(
    isImage || isPdf ? apiUrl : null
  );
  // For Word + other: provide a download function via blob
  const { blobUrl: wordBlobUrl } = useAuthedBlobUrl(
    isWord && !isImage && !isPdf ? apiUrl : null
  );

  const handleDownload = () => {
    const src = blobUrl || wordBlobUrl;
    if (!src) return;
    const a = document.createElement('a');
    a.href = src;
    a.download = doc.originalName || doc.filename;
    a.click();
  };

  return (
    <div className="fixed inset-0 z-[60] bg-black/80 flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 bg-[#1a0003] text-white flex-shrink-0">
        <p className="text-sm font-semibold truncate max-w-xs">{doc.originalName || doc.filename}</p>
        <div className="flex items-center gap-2">
          <button
            onClick={handleDownload}
            disabled={!blobUrl && !wordBlobUrl}
            className="flex items-center gap-1.5 text-xs px-3 py-1.5 bg-white/10 hover:bg-white/20 rounded-lg transition-colors disabled:opacity-40">
            <Download className="w-3.5 h-3.5" /> Tải xuống
          </button>
          <button onClick={onClose} className="p-1.5 hover:bg-white/10 rounded-lg transition-colors">
            <X className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Body */}
      <div className="flex-1 overflow-auto bg-[#111] flex items-center justify-center">
        {/* Loading state */}
        {loading && (
          <div className="flex flex-col items-center gap-3 text-white/60">
            <RefreshCw className="w-8 h-8 animate-spin" />
            <p className="text-sm">Đang tải file…</p>
          </div>
        )}

        {/* Error state */}
        {error && (
          <div className="text-center text-white space-y-3 p-8">
            <AlertCircle className="w-12 h-12 text-red-400 mx-auto" />
            <p className="text-sm text-gray-300">Không thể tải file. Vui lòng thử lại.</p>
          </div>
        )}

        {/* Image */}
        {isImage && blobUrl && (
          <img src={blobUrl} alt={doc.originalName} className="max-w-full max-h-full object-contain" />
        )}

        {/* PDF */}
        {isPdf && blobUrl && (
          <iframe src={blobUrl} className="w-full h-full border-0" title={doc.originalName} />
        )}

        {/* Word — no inline viewer; prompt download */}
        {isWord && !loading && (
          <div className="text-center text-white space-y-4 p-8">
            <FileText className="w-16 h-16 text-blue-300 mx-auto" />
            <p className="text-sm text-gray-300 font-medium">{doc.originalName || doc.filename}</p>
            <p className="text-xs text-gray-500 max-w-xs mx-auto">
              File Word không thể xem trực tiếp trong trình duyệt. Tải về máy để mở.
            </p>
            <button
              onClick={handleDownload}
              disabled={!wordBlobUrl}
              className="inline-flex items-center gap-2 px-5 py-2.5 bg-blue-600 text-white rounded-xl
                hover:bg-blue-700 transition-colors text-sm font-medium disabled:opacity-40">
              <Download className="w-4 h-4" />
              {wordBlobUrl ? 'Tải về máy' : 'Đang tải…'}
            </button>
          </div>
        )}

        {/* Unknown type */}
        {!isImage && !isPdf && !isWord && !loading && (
          <div className="text-center text-white space-y-3 p-8">
            <FileIcon className="w-12 h-12 text-gray-400 mx-auto" />
            <p className="text-sm text-gray-400">Không hỗ trợ xem định dạng này.</p>
          </div>
        )}
      </div>
    </div>
  );
}

// ── ApplicationDetailModal ─────────────────────────────────────────────────────
function ApplicationDetailModal({ app, onClose, onReview }: {
  app: any;
  onClose(): void;
  onReview(): void;
}) {
  const [detail,     setDetail]     = useState<any>(null);
  const [loading,    setLoading]    = useState(true);
  const [error,      setError]      = useState('');
  const [showHist,   setShowHist]   = useState(false);
  const [previewDoc, setPreviewDoc] = useState<any>(null);

  useEffect(() => {
    setLoading(true);
    setError('');
    adminSvc.getApplicationDetail(app.id)
      .then(r => setDetail(r.data))
      .catch(e => setError(e.message || 'Không tải được chi tiết'))
      .finally(() => setLoading(false));
  }, [app.id]);

  const application  = detail?.application  ?? app;
  const documents    = detail?.documents    ?? [];
  const history      = detail?.statusHistory ?? [];

  const cfg    = STATUS_CFG[application.currentStatus ?? application.status]
              ?? { label: application.currentStatus ?? '—', badge: 'bg-[#fff4f4] text-[#9f364c]/70', accent: '#9ca3af' };
  const codeStr = `HS-${String(application.id).slice(0, 13).toUpperCase()}`;

  const dateLabel = (iso?: string) =>
    iso ? new Date(iso).toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' }) : '—';

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 px-4">
      <div className="bg-white rounded-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto shadow-2xl flex flex-col">

        {/* ── Header ──────────────────────────────────────────────────────── */}
        <div className="relative flex items-center justify-between px-5 pt-5 pb-4 flex-shrink-0">
          {/* top accent bar */}
          <div className="absolute top-0 left-0 right-0 h-1 rounded-t-2xl"
            style={{ backgroundColor: cfg.accent }} />
          <div className="mt-1">
            <h3 className="font-bold text-[#1c0003] text-base">Chi tiết hồ sơ</h3>
            <p className="text-[11px] text-gray-400 font-mono mt-0.5">{codeStr}</p>
          </div>
          <button onClick={onClose}
            className="p-1.5 rounded-xl hover:bg-[#fff4f4] transition-colors flex-shrink-0">
            <X className="w-4 h-4 text-gray-400" />
          </button>
        </div>

        {loading ? (
          <div className="flex flex-col items-center justify-center py-12 gap-3">
            <RefreshCw className="w-6 h-6 animate-spin" style={{ color: PRIMARY }} />
            <p className="text-sm text-gray-400">Đang tải…</p>
          </div>
        ) : error ? (
          <div className="px-5 pb-5 flex flex-col items-center gap-2">
            <AlertCircle className="w-8 h-8 text-red-400" />
            <p className="text-sm text-red-500 text-center">{error}</p>
          </div>
        ) : (
          <div className="px-5 pb-5 space-y-4 overflow-y-auto">

            {/* ── Thông tin hồ sơ ──────────────────────────────────────── */}
            <section>
              <p className="text-[10px] font-bold uppercase tracking-widest text-[#9f364c]/60 mb-2">
                Thông tin hồ sơ
              </p>
              <div className="rounded-2xl border border-[#de9ca4]/20 overflow-hidden">
                {[
                  { label: 'Trạng thái',   value: <span className={`text-xs font-semibold px-2.5 py-0.5 rounded-full ${cfg.badge}`}>{cfg.label}</span> },
                  { label: 'Thủ tục',      value: application.procedureName || application.serviceId || '—' },
                  { label: 'Người nộp',    value: application.applicantName || (application.data?.applicantName) || '—' },
                  { label: 'CCCD',         value: application.applicantCccd || (application.data?.cccdNumber) || '—', mono: true },
                  { label: 'Ngày nộp',     value: dateLabel(application.submittedAt || application.createdAt) },
                  { label: 'Cập nhật',     value: dateLabel(application.updatedAt) },
                ].map((row, i) => (
                  <div key={i}
                    className={`flex items-center justify-between px-4 py-2.5 gap-3
                      ${i % 2 === 0 ? 'bg-[#fff4f4]/40' : 'bg-white'}`}>
                    <span className="text-xs text-gray-400 flex-shrink-0 w-24">{row.label}</span>
                    {typeof row.value === 'string'
                      ? <span className={`text-xs font-medium text-gray-800 text-right flex-1 ${(row as any).mono ? 'font-mono' : ''}`}>{row.value}</span>
                      : <div className="flex-1 flex justify-end">{row.value}</div>
                    }
                  </div>
                ))}
              </div>
            </section>

            {/* ── Tài liệu đính kèm ────────────────────────────────────── */}
            <section>
              <p className="text-[10px] font-bold uppercase tracking-widest text-[#9f364c]/60 mb-2">
                Tài liệu đính kèm ({documents.length})
              </p>
              {documents.length === 0 ? (
                <div className="rounded-2xl border border-dashed border-[#de9ca4]/30 py-6
                  flex flex-col items-center gap-2">
                  <FileIcon className="w-7 h-7 text-[#de9ca4]/40" />
                  <p className="text-xs text-gray-400">Không có tài liệu đính kèm</p>
                </div>
              ) : (
                <>
                  <div className="rounded-2xl border border-[#de9ca4]/20 overflow-hidden divide-y divide-[#de9ca4]/10">
                    {documents.map((doc: any, i: number) => {
                      const mime = (doc.mimeType || '').toLowerCase();
                      const canPreview = mime.startsWith('image/') || mime === 'application/pdf'
                        || mime.includes('word') || mime.includes('openxmlformats');
                      return (
                        <div key={doc.id ?? i}
                          className={`flex items-center gap-3 px-4 py-3
                            ${i % 2 === 0 ? 'bg-white' : 'bg-[#fff4f4]/30'}`}>
                          {/* icon */}
                          <div className="w-8 h-8 rounded-lg bg-[#fff4f4] flex items-center justify-center flex-shrink-0">
                            <FileTypeIcon mimeType={doc.mimeType} />
                          </div>
                          {/* info */}
                          <div className="flex-1 min-w-0">
                            <p className="text-xs font-semibold text-gray-800 truncate">
                              {doc.originalName || doc.filename}
                            </p>
                            <p className="text-[10px] text-gray-400 mt-0.5">
                              {doc.mimeType || '—'} · {formatSize(doc.size)}
                            </p>
                          </div>
                          {/* view inline */}
                          {canPreview && (
                            <button
                              onClick={() => setPreviewDoc(doc)}
                              className="w-8 h-8 rounded-lg border border-[#de9ca4]/30 flex items-center justify-center
                                hover:border-[#8f000d] hover:bg-red-50 transition-colors flex-shrink-0"
                              title="Xem trước">
                              <Eye className="w-3.5 h-3.5 text-[#9f364c]" />
                            </button>
                          )}
                          {/* download — open DocPreviewPanel which handles auth */}
                          <button
                            onClick={() => setPreviewDoc(doc)}
                            className="w-8 h-8 rounded-lg border border-[#de9ca4]/30 flex items-center justify-center
                              hover:border-[#8f000d] hover:bg-red-50 transition-colors flex-shrink-0"
                            title="Tải xuống / Xem">
                            <Download className="w-3.5 h-3.5 text-[#9f364c]" />
                          </button>
                        </div>
                      );
                    })}
                  </div>
                  {previewDoc && <DocPreviewPanel doc={previewDoc} onClose={() => setPreviewDoc(null)} />}
                </>
              )}
            </section>

            {/* ── Lịch sử trạng thái ───────────────────────────────────── */}
            {history.length > 0 && (
              <section>
                <button
                  className="flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-widest
                    text-[#9f364c]/60 mb-2 hover:text-[#9f364c] transition-colors"
                  onClick={() => setShowHist(h => !h)}>
                  <History className="w-3 h-3" />
                  Lịch sử trạng thái ({history.length})
                  {showHist ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
                </button>

                {showHist && (
                  <div className="relative pl-4 space-y-3 border-l-2 border-[#de9ca4]/20 ml-2">
                    {history.map((h: any, i: number) => {
                      const hcfg = STATUS_CFG[h.status] ?? { label: h.statusLabel || h.status, badge: 'bg-gray-100 text-gray-600', accent: '#9ca3af' };
                      return (
                        <div key={h.id ?? i} className="relative">
                          {/* dot */}
                          <span className="absolute -left-[21px] top-1.5 w-3 h-3 rounded-full border-2 border-white"
                            style={{ backgroundColor: hcfg.accent }} />
                          <div className="bg-[#fff4f4]/50 rounded-xl px-3 py-2.5 border border-[#de9ca4]/10">
                            <div className="flex items-center gap-2 mb-1">
                              <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full ${hcfg.badge}`}>
                                {hcfg.label}
                              </span>
                              <span className="text-[10px] text-gray-400">
                                {dateLabel(h.createdAt)}
                              </span>
                            </div>
                            {h.note && (
                              <p className="text-xs text-gray-600 leading-snug">{h.note}</p>
                            )}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </section>
            )}
          </div>
        )}

        {/* ── Footer actions ────────────────────────────────────────────────── */}
        <div className="px-5 pb-5 pt-2 flex gap-3 flex-shrink-0 border-t border-[#de9ca4]/10 mt-1">
          <button onClick={onClose}
            className="flex-1 h-11 rounded-xl border border-[#de9ca4]/30 text-sm font-medium
              text-[#4d2128]/70 hover:bg-[#fff4f4] transition-colors">
            Đóng
          </button>
          <button
            onClick={() => { onClose(); onReview(); }}
            className="flex-1 h-11 rounded-xl text-sm font-semibold text-white transition-colors"
            style={{ backgroundColor: PRIMARY }}>
            <span className="flex items-center justify-center gap-1.5">
              <ClipboardList className="w-4 h-4" />
              Xét duyệt
            </span>
          </button>
        </div>
      </div>
    </div>
  );
}

// ── ApplicationCard ────────────────────────────────────────────────────────────
function ApplicationCard({
  app,
  onView,
  onReview,
}: {
  app: any;
  onView(app: any): void;
  onReview(app: any): void;
}) {
  const cfg    = STATUS_CFG[app.currentStatus] ?? { label: app.currentStatus, badge: 'bg-[#fff4f4] text-[#9f364c]/70', accent: '#9ca3af' };
  const dateStr = app.createdAt
    ? new Date(app.createdAt).toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit', year: 'numeric' })
    : '—';
  const codeStr = app.id
    ? `HS-${String(app.id).slice(0, 13).toUpperCase()}`
    : 'HS-—';

  return (
    <div
      className="relative bg-white rounded-2xl shadow-sm overflow-hidden
        transition-transform duration-200 hover:-translate-y-0.5 hover:shadow-md"
      style={{ willChange: 'transform' }}
    >
      {/* Left accent bar */}
      <div className="absolute top-0 left-0 w-1 h-full rounded-l-2xl"
        style={{ backgroundColor: cfg.accent }} />

      <div className="pl-4 pr-4 py-4">
        {/* Row 1 — code + date + badge */}
        <div className="flex items-start justify-between gap-2 mb-2">
          <div className="flex items-center gap-1.5 text-[11px] text-gray-400 font-mono flex-wrap">
            <span>Mã: {codeStr}</span>
            <span className="text-gray-300">•</span>
            <span>{dateStr}</span>
          </div>
          {/* Status badge */}
          <span className={`flex-shrink-0 text-[11px] font-semibold px-2.5 py-0.5 rounded-full ${cfg.badge}`}>
            {cfg.label}
          </span>
        </div>

        {/* Row 2 — procedure name */}
        <p className="text-base font-bold text-gray-900 leading-snug line-clamp-2 mb-2">
          {app.procedureName || app.procedureId || 'Thủ tục hành chính'}
        </p>

        {/* Row 3 — applicant info */}
        <div className="flex items-center gap-1.5 text-xs text-gray-500 mb-3">
          <span className="font-medium text-gray-700">
            {app.applicantName || app.applicantId || 'Không rõ'}
          </span>
          {app.applicantCccd && (
            <>
              <span className="text-gray-300">·</span>
              <span className="font-mono text-gray-400">{app.applicantCccd}</span>
            </>
          )}
        </div>

        {/* Row 4 — actions */}
        <div className="flex gap-2">
          <button
            onClick={() => onView(app)}
            className="flex-1 h-9 flex items-center justify-center gap-1.5 rounded-xl
              border border-[#de9ca4]/30 text-xs font-medium text-[#4d2128]/70
              hover:border-[#8f000d] hover:text-[#8f000d] transition-colors group">
            <Eye className="w-3.5 h-3.5" />
            Xem chi tiết
          </button>
          <button
            onClick={() => onReview(app)}
            className="flex-1 h-9 flex items-center justify-center gap-1.5 rounded-xl
              text-xs font-semibold text-white transition-colors"
            style={{ backgroundColor: PRIMARY }}>
            <ClipboardList className="w-3.5 h-3.5" />
            Xét duyệt
          </button>
        </div>
      </div>
    </div>
  );
}

// ── Pagination ─────────────────────────────────────────────────────────────────
function Pagination({ page, total, pageSize, onChange }: {
  page: number; total: number; pageSize: number; onChange(p: number): void;
}) {
  const totalPages = Math.ceil(total / pageSize);
  if (totalPages <= 1) return null;

  const pages: (number | '…')[] = [];
  if (totalPages <= 7) {
    for (let i = 1; i <= totalPages; i++) pages.push(i);
  } else {
    pages.push(1);
    if (page > 3)        pages.push('…');
    for (let i = Math.max(2, page - 1); i <= Math.min(totalPages - 1, page + 1); i++) pages.push(i);
    if (page < totalPages - 2) pages.push('…');
    pages.push(totalPages);
  }

  return (
    <div className="flex items-center justify-center gap-1.5 py-4">
      <button
        disabled={page === 1}
        onClick={() => onChange(page - 1)}
        className="w-8 h-8 flex items-center justify-center rounded-lg border border-[#de9ca4]/30
          text-[#9f364c]/50 hover:border-[#8f000d] hover:text-[#8f000d] disabled:opacity-30
          disabled:cursor-not-allowed transition-colors">
        <ChevronLeft className="w-4 h-4" />
      </button>

      {pages.map((p, i) =>
        p === '…'
          ? <span key={`ellipsis-${i}`} className="w-8 text-center text-gray-400 text-sm">…</span>
          : (
            <button key={p}
              onClick={() => onChange(p as number)}
              className={`w-8 h-8 flex items-center justify-center rounded-lg text-sm font-medium
                transition-colors
                ${page === p
                  ? 'text-white'
                  : 'border border-[#de9ca4]/30 text-[#4d2128]/70 hover:border-[#8f000d] hover:text-[#8f000d]'}`}
              style={page === p ? { backgroundColor: PRIMARY } : {}}>
              {p}
            </button>
          )
      )}

      <button
        disabled={page >= totalPages}
        onClick={() => onChange(page + 1)}
        className="w-8 h-8 flex items-center justify-center rounded-lg border border-[#de9ca4]/30
          text-[#9f364c]/50 hover:border-[#8f000d] hover:text-[#8f000d] disabled:opacity-30
          disabled:cursor-not-allowed transition-colors">
        <ChevronRight className="w-4 h-4" />
      </button>
    </div>
  );
}

// ════════════════════════════════════════════════════════════════════════════════
// MAIN COMPONENT
// ════════════════════════════════════════════════════════════════════════════════
export function AdminApplicationsScreen({ onNavigate }: Props) {
  const [items,     setItems]     = useState<any[]>([]);
  const [loading,   setLoading]   = useState(true);
  const [q,         setQ]         = useState('');
  const [status,    setStatus]    = useState('');
  const [page,      setPage]      = useState(1);
  const [total,     setTotal]     = useState(0);
  const [stats,     setStats]     = useState<any>(null);
  const [reviewing, setReviewing] = useState<any>(null);
  const [viewing,   setViewing]   = useState<any>(null);
  const [toast,     setToast]     = useState<{ msg: string; ok: boolean } | null>(null);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const showToast = useCallback((msg: string, ok: boolean) => {
    setToast({ msg, ok });
    setTimeout(() => setToast(null), 3000);
  }, []);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const params: Record<string, string> = { page: String(page), limit: String(PAGE_SIZE) };
      if (q)      params.q      = q;
      if (status) params.status = status;
      const r = await adminSvc.getApplications(params);
      // /applications/admin/list trả về { data: { items, total, ... } }
      const payload = r.data;
      setItems(payload?.items ?? payload ?? []);
      setTotal(payload?.total ?? r.pagination?.total ?? r.total ?? 0);
    } catch { /* silent */ }
    finally { setLoading(false); }
  }, [q, status, page]);

  // Load stats once
  useEffect(() => {
    adminSvc.getStats()
      .then(r => setStats(r.data))
      .catch(() => {});
  }, []);

  useEffect(() => { load(); }, [load]);

  // Debounce search
  const handleSearch = (val: string) => {
    setQ(val);
    setPage(1);
    if (debounceRef.current) clearTimeout(debounceRef.current);
  };

  const handleReview = async (action: string, note: string) => {
    if (!reviewing) return;
    try {
      await adminSvc.reviewApplication(reviewing.id, action, note);
      showToast('Đã cập nhật trạng thái hồ sơ', true);
      setReviewing(null);
      load();
    } catch (e: any) { showToast(e.message || 'Có lỗi xảy ra', false); }
  };

  // Stats derived values
  const totalMonth       = stats?.totalApplications ?? 0;
  const pendingCount     = stats?.pendingApplications ?? 0;
  const approvedPercent  = totalMonth > 0
    ? Math.round(((totalMonth - pendingCount) / totalMonth) * 100)
    : 0;

  return (
    <div className="min-h-screen bg-transparent pb-6">
      {toast && <Toast text={toast.msg} ok={toast.ok} />}
      {viewing && !reviewing && (
        <ApplicationDetailModal
          app={viewing}
          onClose={() => setViewing(null)}
          onReview={() => { setReviewing(viewing); setViewing(null); }}
        />
      )}
      {reviewing && (
        <ReviewModal
          app={reviewing}
          onClose={() => setReviewing(null)}
          onDone={handleReview}
        />
      )}

      {/* ── Hero Header ───────────────────────────────────────────────────── */}
      <div className="relative overflow-hidden px-4 pt-5 pb-6"
        style={{ background: `linear-gradient(135deg, ${PRIMARY} 0%, #6b0009 100%)` }}>
        {/* grid overlay */}
        <div className="absolute inset-0 opacity-[0.07]"
          style={{
            backgroundImage: 'linear-gradient(rgba(255,255,255,.6) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.6) 1px,transparent 1px)',
            backgroundSize: '28px 28px',
          }} />

        <div className="relative">
          <div className="flex items-start justify-between mb-1">
            <div>
              <p className="text-[11px] font-semibold text-red-200 uppercase tracking-widest mb-0.5">
                Quản trị · Hồ sơ
              </p>
              <h1 className="text-2xl font-black text-white leading-tight">
                Quản lý hồ sơ<span style={{ color: GOLD }}>.</span>
              </h1>
              <p className="text-red-200 text-xs mt-1">
                Xét duyệt, theo dõi và xử lý hồ sơ người dân
              </p>
            </div>
            <div className="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0"
              style={{ backgroundColor: 'rgba(255,255,255,0.12)' }}>
              <FolderOpen className="w-5 h-5 text-white" />
            </div>
          </div>

          {/* Quick stats strip */}
          <div className="flex gap-3 mt-4">
            {[
              { label: 'Tổng hồ sơ',   value: stats?.totalApplications ?? '—' },
              { label: 'Chờ duyệt',     value: stats?.pendingApplications ?? '—' },
              { label: 'Tháng này',     value: totalMonth },
            ].map(s => (
              <div key={s.label}
                className="flex-1 rounded-xl px-3 py-2.5 text-center"
                style={{ backgroundColor: 'rgba(255,255,255,0.12)' }}>
                <p className="text-base font-black text-white leading-none">{s.value}</p>
                <p className="text-[10px] text-red-200 mt-0.5">{s.label}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* ── Search + Filters ──────────────────────────────────────────────── */}
      <div className="px-4 -mt-3 relative z-10">
        {/* Plinth search */}
        <div className="bg-white rounded-2xl shadow-md flex items-center gap-2 px-4 py-0 h-12 mb-3">
          <Search className="w-4 h-4 flex-shrink-0" style={{ color: PRIMARY }} />
          <input
            value={q}
            onChange={e => handleSearch(e.target.value)}
            placeholder="Tìm mã hồ sơ, tên người nộp, CCCD…"
            className="flex-1 text-sm text-gray-800 bg-transparent border-none outline-none
              placeholder:text-gray-400"
          />
          {q && (
            <button onClick={() => { setQ(''); setPage(1); }}
              className="text-gray-300 hover:text-gray-500 transition-colors">
              <X className="w-4 h-4" />
            </button>
          )}
        </div>

        {/* Status filter chips */}
        <div className="flex gap-1.5 overflow-x-auto pb-1 no-scrollbar">
          {FILTER_OPTS.map(o => {
            const active = status === o.value;
            return (
              <button key={o.value}
                onClick={() => { setStatus(o.value); setPage(1); }}
                className={`flex-shrink-0 px-3 py-1.5 rounded-full text-xs font-semibold
                  transition-all border
                  ${active
                    ? 'text-white border-transparent'
                    : 'bg-white text-[#4d2128]/70 border-[#de9ca4]/30 hover:border-[#de9ca4]'}`}
                style={active ? { backgroundColor: PRIMARY, borderColor: PRIMARY } : {}}>
                {o.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* ── Content ───────────────────────────────────────────────────────── */}
      <div className="px-4 mt-3">
        {/* Count label */}
        <div className="flex items-center justify-between mb-3">
          <p className="text-xs text-gray-400 font-medium">
            {loading ? 'Đang tải…' : `${total} hồ sơ`}
          </p>
          <button onClick={() => load()}
            className="text-xs flex items-center gap-1 text-gray-400 hover:text-gray-600 transition-colors">
            <RefreshCw className={`w-3 h-3 ${loading ? 'animate-spin' : ''}`} />
            Làm mới
          </button>
        </div>

        {loading ? (
          <div className="flex flex-col items-center justify-center py-16 gap-3">
            <RefreshCw className="w-7 h-7 animate-spin" style={{ color: PRIMARY }} />
            <p className="text-sm text-gray-400">Đang tải hồ sơ…</p>
          </div>
        ) : items.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-16 gap-3">
            <div className="w-16 h-16 rounded-2xl flex items-center justify-center bg-[#fff4f4]">
              <FileText className="w-8 h-8 text-[#de9ca4]/50" />
            </div>
            <p className="text-sm text-gray-400 font-medium">Không có hồ sơ nào</p>
            <p className="text-xs text-gray-300">Thử thay đổi bộ lọc hoặc từ khoá tìm kiếm</p>
          </div>
        ) : (
          <div className="space-y-3">
            {items.map(app => (
              <ApplicationCard
                key={app.id}
                app={app}
                onView={a => setViewing(a)}
                onReview={a => setReviewing(a)}
              />
            ))}
          </div>
        )}

        <Pagination
          page={page}
          total={total}
          pageSize={PAGE_SIZE}
          onChange={p => { setPage(p); window.scrollTo({ top: 0, behavior: 'smooth' }); }}
        />
      </div>

      {/* ── Bottom Stats Row ──────────────────────────────────────────────── */}
      <div className="px-4 mt-4 grid grid-cols-2 gap-3">
        <div className="rounded-2xl p-3.5 relative overflow-hidden" style={{ backgroundColor: '#fef2f2' }}>
          <FileText className="w-5 h-5 mb-2" style={{ color: PRIMARY }} />
          <p className="text-xl font-black leading-none" style={{ color: PRIMARY }}>{totalMonth}</p>
          <p className="text-[10px] mt-1 font-medium" style={{ color: '#b91c1c' }}>Hồ sơ tháng này</p>
        </div>
        <div className="rounded-2xl p-3.5 relative overflow-hidden" style={{ backgroundColor: '#fffde7' }}>
          <TrendingUp className="w-5 h-5 mb-2" style={{ color: '#92400e' }} />
          <p className="text-xl font-black leading-none" style={{ color: '#78350f' }}>{approvedPercent}%</p>
          <p className="text-[10px] mt-1 font-medium" style={{ color: '#92400e' }}>Tỷ lệ đã xử lý</p>
        </div>
      </div>

      {/* ── Pending alert banner ──────────────────────────────────────────── */}
      {(stats?.pendingApplications ?? 0) > 0 && (
        <div className="mx-4 mt-4 rounded-2xl px-4 py-3 flex items-center gap-3"
          style={{ backgroundColor: '#fff3cd', border: `1px solid ${GOLD}` }}>
          <Clock className="w-5 h-5 flex-shrink-0" style={{ color: '#856404' }} />
          <div className="flex-1 min-w-0">
            <p className="text-xs font-semibold" style={{ color: '#533f03' }}>
              {stats.pendingApplications} hồ sơ đang chờ xét duyệt
            </p>
            <p className="text-[10px] text-amber-600">Vui lòng xem xét sớm để tránh trễ hạn</p>
          </div>
          <button
            onClick={() => { setStatus('in_review'); setPage(1); }}
            className="flex-shrink-0 text-xs font-semibold px-3 py-1.5 rounded-lg text-white transition-colors"
            style={{ backgroundColor: '#856404' }}>
            Xem ngay
          </button>
        </div>
      )}
    </div>
  );
}
