import React, { useState, useMemo, useEffect } from 'react';
import { ArrowLeft, RefreshCw, Search, ChevronRight } from 'lucide-react';
import { proceduresAPI, type Procedure } from '../services/proceduresService';

interface DocumentCatalogProps {
  onNavigate: (screen: string, params?: any) => void;
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

const LEVEL_LABEL: Record<string, string> = {
  ward:     'Cấp xã/phường',
  district: 'Cấp huyện',
  province: 'Cấp tỉnh',
};

export function DocumentCatalogScreen({ onNavigate }: DocumentCatalogProps) {
  const [query, setQuery]         = useState('');
  const [procedures, setProcedures] = useState<Procedure[]>([]);
  const [loading, setLoading]     = useState(true);
  const [activeCategory, setActiveCategory] = useState<string>('all');

  useEffect(() => {
    setLoading(true);
    proceduresAPI.list({ limit: 100 })
      .then(r => setProcedures(r.data || []))
      .catch(() => setProcedures([]))
      .finally(() => setLoading(false));
  }, []);

  // Danh sách category từ procedures thực tế
  const categories = useMemo(() => {
    const map: Record<string, number> = {};
    for (const p of procedures) {
      map[p.category] = (map[p.category] || 0) + 1;
    }
    return Object.entries(map).map(([id, count]) => ({
      id, count,
      ...(CATEGORY_META[id] || { label: id, icon: '📄', color: '#9f364c' }),
    }));
  }, [procedures]);

  const filtered = useMemo(() => {
    let list = procedures;
    if (activeCategory !== 'all') list = list.filter(p => p.category === activeCategory);
    if (query.trim()) {
      const q = query.trim().toLowerCase();
      list = list.filter(p =>
        p.name.toLowerCase().includes(q) ||
        p.agency?.toLowerCase().includes(q) ||
        (CATEGORY_META[p.category]?.label || '').toLowerCase().includes(q)
      );
    }
    return list;
  }, [procedures, activeCategory, query]);

  return (
    <div className="bg-[#fff4f4] text-[#4d2128] min-h-screen flex flex-col" style={{ fontFamily: "'Manrope', sans-serif" }}>

      {/* ── Header ── */}
      <header className="sticky top-0 z-40 bg-[#fff4f4]/90 backdrop-blur-md border-b border-[#de9ca4]/20">
        <div className="max-w-5xl mx-auto px-4 md:px-8 py-4 flex items-center gap-4">
          <button onClick={() => onNavigate('home')}
            className="w-9 h-9 flex items-center justify-center rounded-full hover:bg-[#ffd9dd] transition-colors text-[#9f364c]">
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div className="flex-1">
            <h1 className="text-lg font-black text-[#b7131a] leading-tight">Kho tài liệu hành chính</h1>
            <p className="text-xs text-[#9f364c] font-medium">{procedures.length} thủ tục · Cổng DVC Thanh Hóa</p>
          </div>
        </div>

        {/* Search bar */}
        <div className="max-w-5xl mx-auto px-4 md:px-8 pb-3">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#9f364c]" />
            <input
              value={query}
              onChange={e => setQuery(e.target.value)}
              placeholder="Tìm tên thủ tục, cơ quan..."
              className="w-full pl-10 pr-4 py-2.5 bg-white rounded-xl text-sm border border-[#de9ca4]/30 focus:outline-none focus:ring-2 focus:ring-[#b7131a]/30 placeholder:text-[#9f364c]/40"
            />
          </div>
        </div>

        {/* Category tabs */}
        <div className="max-w-5xl mx-auto px-4 md:px-8 pb-3 flex gap-2 overflow-x-auto [scrollbar-width:none] [&::-webkit-scrollbar]:hidden">
          <button
            onClick={() => setActiveCategory('all')}
            className={`flex-shrink-0 px-3 py-1.5 rounded-full text-xs font-bold transition-all border ${
              activeCategory === 'all'
                ? 'bg-[#b7131a] text-white border-[#b7131a]'
                : 'bg-white text-[#4d2128] border-[#de9ca4]/30 hover:border-[#b7131a]/40'
            }`}>
            Tất cả ({procedures.length})
          </button>
          {categories.map(cat => (
            <button key={cat.id}
              onClick={() => setActiveCategory(cat.id)}
              className={`flex-shrink-0 flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-bold transition-all border ${
                activeCategory === cat.id
                  ? 'bg-[#b7131a] text-white border-[#b7131a]'
                  : 'bg-white text-[#4d2128] border-[#de9ca4]/30 hover:border-[#b7131a]/40'
              }`}>
              <span>{cat.icon}</span>
              {cat.label} ({cat.count})
            </button>
          ))}
        </div>
      </header>

      {/* ── Main ── */}
      <main className="flex-1 max-w-5xl mx-auto w-full px-4 md:px-8 py-6">

        {loading ? (
          <div className="flex flex-col items-center justify-center py-32">
            <RefreshCw className="w-8 h-8 text-[#de9ca4] animate-spin mb-3" />
            <p className="text-sm text-[#9f364c]">Đang tải danh sách thủ tục...</p>
          </div>
        ) : filtered.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-32 bg-white rounded-2xl border border-[#de9ca4]/20">
            <span className="text-5xl mb-4">🔍</span>
            <h3 className="text-lg font-bold text-[#4d2128] mb-1">Không tìm thấy thủ tục</h3>
            <p className="text-sm text-[#824c54]">Thử từ khóa khác hoặc chọn danh mục khác.</p>
          </div>
        ) : (
          <div className="space-y-3">
            {filtered.map(proc => {
              const meta = CATEGORY_META[proc.category] || { icon: '📄', label: proc.category, color: '#9f364c' };
              return (
                <button key={proc.id}
                  onClick={() => onNavigate('document-detail', { procedureId: proc.id })}
                  className="w-full text-left bg-white rounded-2xl p-5 border border-[#de9ca4]/15 hover:border-[#b7131a]/30 hover:shadow-lg hover:shadow-[#b7131a]/5 transition-all group">
                  <div className="flex items-start gap-4">
                    {/* Icon */}
                    <div className="w-12 h-12 rounded-xl flex items-center justify-center text-2xl flex-shrink-0"
                      style={{ backgroundColor: meta.color + '18' }}>
                      {proc.icon || meta.icon}
                    </div>

                    {/* Content */}
                    <div className="flex-1 min-w-0">
                      <h3 className="font-bold text-[#4d2128] text-sm leading-snug group-hover:text-[#b7131a] transition-colors line-clamp-2">
                        {proc.name}
                      </h3>
                      {proc.agency && (
                        <p className="text-xs text-[#9f364c] mt-1 line-clamp-1">{proc.agency}</p>
                      )}
                      <div className="flex flex-wrap items-center gap-2 mt-2">
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold"
                          style={{ backgroundColor: meta.color + '15', color: meta.color }}>
                          {meta.icon} {meta.label}
                        </span>
                        <span className="text-[10px] text-[#9f364c] font-medium">
                          ⏱ {proc.timeFormatted}
                        </span>
                        <span className={`text-[10px] font-bold ${proc.feeColor ? 'text-green-600' : 'text-[#b7131a]'}`}>
                          💰 {proc.feeFormatted}
                        </span>
                        {proc.implementingLevel && (
                          <span className="text-[10px] text-[#9f364c]">
                            🏛 {LEVEL_LABEL[proc.implementingLevel] || proc.implementingLevel}
                          </span>
                        )}
                      </div>
                    </div>

                    <ChevronRight className="w-4 h-4 text-[#de9ca4] group-hover:text-[#b7131a] transition-colors flex-shrink-0 mt-1" />
                  </div>
                </button>
              );
            })}
          </div>
        )}
      </main>

      {/* ── Bottom nav mobile ── */}
      <nav className="md:hidden fixed bottom-0 left-0 w-full bg-[#fff4f4]/90 backdrop-blur-md border-t border-[#ffeced] flex justify-around items-center py-3 px-2 z-50">
        {([
          { label: 'Trang chủ', icon: 'home',          active: false, action: () => onNavigate('home') },
          { label: 'Tài liệu',  icon: 'manage_search', active: true,  action: () => {} },
          { label: 'Hồ sơ',     icon: 'description',   active: false, action: () => onNavigate('submit') },
          { label: 'Cá nhân',   icon: 'person',         active: false, action: () => {} },
        ] as const).map(({ label, icon, active, action }) => (
          <button key={label} onClick={action}
            className={`flex flex-col items-center gap-1 ${active ? 'text-[#b7131a]' : 'text-[#4d2128]/60'}`}>
            <span className="material-symbols-outlined text-[22px]"
              style={{ fontVariationSettings: active ? "'FILL' 1" : "'FILL' 0" }}>
              {icon}
            </span>
            <span className="text-[10px] font-bold">{label}</span>
          </button>
        ))}
      </nav>
    </div>
  );
}

export default DocumentCatalogScreen;
