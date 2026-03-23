/**
 * SearchDocumentScreen — Tra cứu hồ sơ
 * Kết nối API thật: GET /api/applications/search và /api/applications/my
 */
import React, { useState, useEffect, useCallback } from 'react';
import {
  Search, FileText, Clock, CheckCircle, AlertCircle,
  Phone, MessageCircle, ChevronLeft, RefreshCw,
  X, ChevronRight, ArrowLeft,
} from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';

const BASE = 'http://localhost:8888/api';

function authH() {
  const token = localStorage.getItem('token');
  return token ? { Authorization: `Bearer ${token}` } : {};
}

interface AppRecord {
  id:            string;
  applicantId:   string;
  serviceId:     string;
  currentStatus: string;
  createdAt:     string;
  updatedAt:     string;
  data:          Record<string, any>;
  statusHistory: { status: string; note: string; createdAt: string }[];
}

interface SearchDocumentScreenProps {
  onNavigate: (screen: string, params?: any) => void;
}

// ── Helper ────────────────────────────────────────────────────────────────────
const STATUS_META: Record<string, { label: string; color: string; progress: number }> = {
  submitted:   { label: 'Đã nộp',        color: 'bg-blue-100 text-blue-700',    progress: 25 },
  in_review:   { label: 'Đang xử lý',    color: 'bg-yellow-100 text-yellow-700',progress: 60 },
  more_info:   { label: 'Cần bổ sung',   color: 'bg-orange-100 text-orange-700',progress: 40 },
  approved:    { label: 'Đã duyệt',      color: 'bg-green-100 text-green-700',  progress: 100 },
  rejected:    { label: 'Từ chối',       color: 'bg-red-100 text-red-700',      progress: 100 },
};

function statusMeta(s: string) {
  return STATUS_META[s] || { label: s, color: 'bg-gray-100 text-gray-600', progress: 0 };
}

function fmtDate(iso: string) {
  if (!iso) return '–';
  return new Date(iso).toLocaleDateString('vi-VN', {
    day: '2-digit', month: '2-digit', year: 'numeric',
  });
}

// ── Detail view ───────────────────────────────────────────────────────────────
function AppDetail({ app, onBack, onNavigate }: {
  app: AppRecord; onBack(): void; onNavigate(s: string, p?: any): void;
}) {
  const meta = statusMeta(app.currentStatus);
  const steps = [
    { name: 'Tiếp nhận',    done: true },
    { name: 'Đang xử lý',   done: ['in_review', 'more_info', 'approved', 'rejected'].includes(app.currentStatus) },
    { name: 'Xét duyệt',    done: ['approved', 'rejected'].includes(app.currentStatus) },
    { name: 'Hoàn tất',     done: app.currentStatus === 'approved' },
  ];

  return (
    <div className="px-4 pb-6 pt-2">
      <button className="flex items-center gap-1 text-sm text-gray-500 mb-4"
        onClick={onBack}>
        <ArrowLeft className="w-4 h-4" /> Quay lại
      </button>

      <Card>
        <CardHeader>
          <div className="flex items-start justify-between gap-2">
            <div>
              <CardTitle className="text-base">{app.data?.serviceName || app.serviceId}</CardTitle>
              <p className="text-xs text-gray-400 mt-1">Mã: {app.id}</p>
            </div>
            <Badge className={`text-xs flex-shrink-0 ${meta.color}`}>{meta.label}</Badge>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-3 text-sm">
            <div>
              <p className="text-gray-400 text-xs">Ngày nộp</p>
              <p className="font-medium">{fmtDate(app.createdAt)}</p>
            </div>
            <div>
              <p className="text-gray-400 text-xs">Cập nhật</p>
              <p className="font-medium">{fmtDate(app.updatedAt)}</p>
            </div>
          </div>

          {/* Tiến trình */}
          <div>
            <div className="flex justify-between text-xs text-gray-500 mb-1">
              <span>Tiến trình</span>
              <span>{meta.progress}%</span>
            </div>
            <Progress value={meta.progress} />
          </div>

          {/* Timeline */}
          <div className="space-y-3">
            {steps.map((s, i) => (
              <div key={i} className="flex items-start gap-3">
                <div className={`w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0 ${
                  s.done ? 'bg-green-100' : 'bg-gray-100'
                }`}>
                  {s.done
                    ? <CheckCircle className="w-3.5 h-3.5 text-green-600" />
                    : <div className="w-2 h-2 bg-gray-300 rounded-full" />}
                </div>
                <p className={`text-sm pt-0.5 ${s.done ? 'text-gray-800' : 'text-gray-400'}`}>
                  {s.name}
                </p>
              </div>
            ))}
          </div>

          {/* Lịch sử trạng thái */}
          {app.statusHistory?.length > 0 && (
            <div>
              <p className="text-xs font-medium text-gray-500 mb-2">Lịch sử xử lý</p>
              <div className="space-y-2">
                {app.statusHistory.map((h, i) => (
                  <div key={i} className="bg-gray-50 rounded-lg px-3 py-2 text-xs">
                    <div className="flex justify-between">
                      <Badge className={`text-xs ${statusMeta(h.status).color}`}>
                        {statusMeta(h.status).label}
                      </Badge>
                      <span className="text-gray-400">{fmtDate(h.createdAt)}</span>
                    </div>
                    {h.note && <p className="text-gray-600 mt-1">{h.note}</p>}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Cần bổ sung */}
          {app.currentStatus === 'more_info' && (
            <div className="bg-orange-50 border border-orange-200 rounded-xl p-3">
              <div className="flex items-center gap-2 text-orange-700 text-sm font-medium mb-1">
                <AlertCircle className="w-4 h-4" /> Cần bổ sung hồ sơ
              </div>
              <p className="text-xs text-orange-600">
                {app.statusHistory?.slice().reverse().find(h => h.status === 'more_info')?.note
                  || 'Vui lòng liên hệ cơ quan để biết thêm chi tiết.'}
              </p>
            </div>
          )}

          <div className="flex gap-2 pt-1">
            <Button className="flex-1 h-10 bg-red-600 hover:bg-red-700 text-white text-sm">
              <Phone className="w-4 h-4 mr-1.5" /> Gọi hotline
            </Button>
            <Button variant="outline" className="flex-1 h-10 text-sm"
              onClick={() => onNavigate('chatbot')}>
              <MessageCircle className="w-4 h-4 mr-1.5" /> Hỏi AI
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

// ── Main component ────────────────────────────────────────────────────────────
export function SearchDocumentScreen({ onNavigate }: SearchDocumentScreenProps) {
  const [searchValue,  setSearchValue]  = useState('');
  const [selected,     setSelected]     = useState<AppRecord | null>(null);
  const [myApps,       setMyApps]       = useState<AppRecord[]>([]);
  const [searchResult, setSearchResult] = useState<AppRecord[] | null>(null);
  const [loading,      setLoading]      = useState(false);
  const [loadingMy,    setLoadingMy]    = useState(true);
  const [error,        setError]        = useState('');

  // Tải hồ sơ của mình khi mở màn hình
  const loadMyApps = useCallback(async () => {
    setLoadingMy(true);
    try {
      const res  = await fetch(`${BASE}/applications/my`, { headers: authH() });
      const json = await res.json();
      if (json.success) setMyApps(json.data || []);
    } catch { /* bỏ qua */ }
    finally { setLoadingMy(false); }
  }, []);

  useEffect(() => { loadMyApps(); }, [loadMyApps]);

  // Tra cứu theo từ khóa / CCCD
  const handleSearch = async () => {
    const q = searchValue.trim();
    if (!q) { setSearchResult(null); return; }
    setLoading(true);
    setError('');
    try {
      const isCCCD = /^\d{9,12}$/.test(q);
      const url    = isCCCD
        ? `${BASE}/applications/search?cccd=${q}`
        : `${BASE}/applications/search?q=${encodeURIComponent(q)}`;
      const res  = await fetch(url, { headers: authH() });
      const json = await res.json();
      if (json.success) {
        setSearchResult(json.data || []);
      } else {
        setError(json.message || 'Lỗi tra cứu');
        setSearchResult([]);
      }
    } catch (e: any) {
      setError(e.message);
      setSearchResult([]);
    } finally {
      setLoading(false);
    }
  };

  const displayList: AppRecord[] = searchResult ?? myApps;

  if (selected) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="bg-white border-b border-gray-200 px-4 pt-12 pb-4">
          <h1 className="text-xl font-bold text-gray-900">Chi tiết hồ sơ</h1>
        </div>
        <AppDetail app={selected} onBack={() => setSelected(null)} onNavigate={onNavigate} />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="px-4 pt-12 pb-4">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Tra cứu hồ sơ</h1>

          {/* Tìm kiếm */}
          <div className="flex gap-2">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <Input
                value={searchValue}
                onChange={e => { setSearchValue(e.target.value); if (!e.target.value) setSearchResult(null); }}
                onKeyDown={e => e.key === 'Enter' && handleSearch()}
                placeholder="Nhập mã hồ sơ hoặc số CCCD..."
                className="pl-10 pr-10 h-11 bg-gray-50 border-gray-200 rounded-xl"
              />
              {searchValue && (
                <button className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400"
                  onClick={() => { setSearchValue(''); setSearchResult(null); }}>
                  <X className="w-4 h-4" />
                </button>
              )}
            </div>
            <Button className="h-11 px-4 bg-red-600 hover:bg-red-700 text-white rounded-xl"
              onClick={handleSearch} disabled={loading}>
              {loading
                ? <RefreshCw className="w-4 h-4 animate-spin" />
                : <Search className="w-4 h-4" />}
            </Button>
          </div>

          {/* Gợi ý tìm kiếm nhanh */}
          {!searchValue && (
            <div className="flex gap-2 mt-3 flex-wrap">
              {['Đang xử lý', 'Cần bổ sung', 'Đã duyệt'].map(s => (
                <button key={s}
                  className="text-xs px-3 py-1.5 bg-gray-100 rounded-full text-gray-600 hover:bg-gray-200"
                  onClick={async () => {
                    setLoading(true);
                    try {
                      const statusMap: Record<string, string> = {
                        'Đang xử lý': 'in_review',
                        'Cần bổ sung': 'more_info',
                        'Đã duyệt':   'approved',
                      };
                      const res  = await fetch(`${BASE}/applications/my?status=${statusMap[s]}`, { headers: authH() });
                      const json = await res.json();
                      if (json.success) setSearchResult(json.data || []);
                    } catch { /* bỏ qua */ }
                    finally { setLoading(false); }
                  }}>
                  {s}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="mx-4 mt-3 flex items-center gap-2 text-red-600 bg-red-50
          border border-red-200 rounded-lg px-3 py-2 text-sm">
          <AlertCircle className="w-4 h-4 flex-shrink-0" /> {error}
        </div>
      )}

      {/* Danh sách */}
      <div className="px-4 pt-4 pb-6">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-sm font-semibold text-gray-700">
            {searchResult
              ? `Kết quả tra cứu (${displayList.length})`
              : `Hồ sơ của bạn (${myApps.length})`}
          </h2>
          {searchResult && (
            <button className="text-xs text-red-600" onClick={() => { setSearchResult(null); setSearchValue(''); }}>
              Xóa bộ lọc
            </button>
          )}
        </div>

        {(loading || loadingMy) ? (
          <div className="flex justify-center py-12">
            <RefreshCw className="w-6 h-6 animate-spin text-gray-400" />
          </div>
        ) : displayList.length === 0 ? (
          <div className="text-center py-12 text-gray-400">
            <FileText className="w-12 h-12 mx-auto mb-3 opacity-30" />
            <p className="text-sm">Không tìm thấy hồ sơ nào</p>
          </div>
        ) : (
          <div className="space-y-3">
            {displayList.map(app => {
              const meta = statusMeta(app.currentStatus);
              return (
                <Card key={app.id}
                  className="cursor-pointer hover:shadow-md transition-shadow border-0 shadow-sm"
                  onClick={() => setSelected(app)}>
                  <CardContent className="p-4">
                    <div className="flex items-start justify-between gap-2 mb-2">
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-semibold text-gray-800 truncate">
                          {app.data?.serviceName || app.serviceId || 'Hồ sơ hành chính'}
                        </p>
                        <p className="text-xs text-gray-400 mt-0.5">Mã: {app.id.slice(-8).toUpperCase()}</p>
                      </div>
                      <Badge className={`text-xs flex-shrink-0 ${meta.color}`}>{meta.label}</Badge>
                    </div>
                    <div className="flex items-center justify-between text-xs text-gray-400 mb-2">
                      <span>Nộp: {fmtDate(app.createdAt)}</span>
                      <ChevronRight className="w-4 h-4" />
                    </div>
                    <Progress value={meta.progress} className="h-1.5" />
                  </CardContent>
                </Card>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
