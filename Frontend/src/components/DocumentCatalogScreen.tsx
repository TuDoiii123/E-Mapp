import React, { useState, useMemo, useEffect } from 'react';
import { API_BASE_URL } from '../services/api';
import { ArrowLeft, RefreshCw, FolderX } from 'lucide-react';

interface DocumentCatalogProps {
  onNavigate: (screen: string, params?: any) => void;
}

const FALLBACK_DOC_TYPES = [
  'Giấy phép lái xe',
  'Chứng minh nhân dân / CCCD',
  'Hộ chiếu',
];

export function DocumentCatalogScreen({ onNavigate }: DocumentCatalogProps) {
  const [query, setQuery] = useState('');
  const [services, setServices] = useState<any[] | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    fetch(`${API_BASE_URL}/services?limit=500`)
      .then((r) => r.json())
      .then((d) => {
        if (d && d.success && d.data && Array.isArray(d.data.services)) {
          setServices(d.data.services);
        } else {
          setServices(null);
        }
      })
      .catch(() => setServices(null))
      .finally(() => setLoading(false));
  }, []);

  const categories = useMemo(() => {
    const map: Record<string, { id: string; name: string; count: number }> = {};
    const list =
      services && services.length
        ? services
        : FALLBACK_DOC_TYPES.map((t) => ({ id: t, name: t, categoryId: t }));
    for (const s of list) {
      const cid = s.categoryId || s.theloai_id || s.category || s.name || 'uncategorized';
      const cname =
        s.categoryName || s.theloai_name || s.category_name || s.category || s.name || 'Khác';
      if (!map[cid]) map[cid] = { id: cid, name: cname, count: 0 };
      map[cid].count += 1;
    }
    const q = query.trim().toLowerCase();
    return Object.values(map).filter((c) => (q ? c.name.toLowerCase().includes(q) : true));
  }, [query, services]);

  return (
    <div
      className="bg-[#fff4f4] text-[#4d2128] min-h-screen flex flex-col"
      style={{ fontFamily: "'Manrope', sans-serif" }}
    >
      {/* ── TopNavBar ── */}
      <header className="flex justify-between items-center w-full px-6 md:px-10 py-4 bg-[#fff4f4]/80 backdrop-blur-md sticky top-0 z-40 border-b border-[#de9ca4]/20">
        <div className="flex items-center gap-6 flex-1">
          <div className="relative w-full max-w-md">
            <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-[#9f364c] text-xl">
              search
            </span>
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 bg-white border-none rounded-xl text-sm focus:ring-2 focus:ring-[#b7131a] outline-none placeholder:text-[#9f364c]/50"
              placeholder="Tìm kiếm tài liệu..."
            />
          </div>
        </div>
        <div className="flex items-center gap-3 ml-4">
          <div className="hidden sm:flex items-center gap-2 px-4 py-2 bg-[#ffeced] rounded-full">
            <span className="w-2 h-2 rounded-full bg-green-500" />
            <span className="text-sm font-bold text-[#4d2128]">Synthesis Hub</span>
          </div>
          <button
            onClick={() => onNavigate('notifications')}
            className="w-10 h-10 flex items-center justify-center rounded-full hover:bg-[#ffd9dd] transition-all text-[#9f364c]"
          >
            <span className="material-symbols-outlined">notifications</span>
          </button>
          <button className="w-10 h-10 flex items-center justify-center rounded-full hover:bg-[#ffd9dd] transition-all text-[#9f364c]">
            <span className="material-symbols-outlined">settings</span>
          </button>
        </div>
      </header>

      {/* ── Main ── */}
      <main className="flex-1 px-6 md:px-10 py-10 max-w-6xl mx-auto w-full">

        {/* Hero */}
        <section className="mb-12">
          <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
            <div>
              <button
                onClick={() => onNavigate('home')}
                className="flex items-center gap-1.5 text-sm text-[#9f364c] hover:text-[#b7131a] transition-colors mb-3"
              >
                <ArrowLeft className="w-4 h-4" /> Trang chủ
              </button>
              <h2 className="text-4xl font-extrabold tracking-tight text-[#4d2128] mb-2">
                Tổng hợp giấy tờ
              </h2>
              <p className="text-lg text-[#9f364c] font-medium">
                Tìm và xem các loại giấy tờ thủ tục hành chính công
              </p>
            </div>
            <div className="flex items-center gap-3">
              <span className="px-4 py-2 bg-[#b7131a]/10 text-[#b7131a] rounded-full text-sm font-bold">
                Hệ thống E-Mapp
              </span>
              <span className="px-4 py-2 bg-[#fdc003]/20 text-[#755700] rounded-full text-sm font-bold">
                Cập nhật 24/7
              </span>
            </div>
          </div>
        </section>

        {/* Search Bento Box */}
        <section className="mb-16">
          <div className="bg-white rounded-3xl p-8 shadow-sm relative overflow-hidden border border-[#de9ca4]/10">
            <div className="absolute top-0 right-0 w-64 h-64 bg-[#b7131a]/5 rounded-full -mr-20 -mt-20 blur-3xl pointer-events-none" />
            <div className="relative z-10">
              <label className="block text-sm font-bold text-[#4d2128] mb-4">
                Tra cứu nguồn dữ liệu
              </label>
              <div className="flex flex-col md:flex-row gap-4">
                <div className="flex-1 relative">
                  <span className="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-[#b7131a]">
                    description
                  </span>
                  <input
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="Nhập tên cơ quan, đơn vị hoặc loại giấy tờ..."
                    className="w-full pl-12 pr-4 py-4 bg-[#ffeced] border-none rounded-2xl text-base focus:ring-2 focus:ring-[#b7131a] outline-none placeholder:text-[#de9ca4]"
                  />
                </div>
                <button className="px-8 py-4 bg-gradient-to-br from-[#b7131a] to-[#ff766b] text-white font-bold rounded-2xl flex items-center justify-center gap-2 shadow-lg shadow-[#b7131a]/20 hover:scale-105 transition-transform">
                  <span className="material-symbols-outlined">search</span>
                  <span>Tìm kiếm</span>
                </button>
              </div>
            </div>
          </div>
        </section>

        {/* Agency List */}
        <section>
          <div className="flex items-center justify-between mb-8">
            <h3 className="text-2xl font-bold text-[#4d2128]">Danh sách cơ quan</h3>
            <div className="flex items-center gap-1 text-[#9f364c] text-sm font-semibold cursor-pointer hover:text-[#b7131a] transition-colors">
              <span>Sắp xếp: Mặc định</span>
              <span className="material-symbols-outlined text-sm">expand_more</span>
            </div>
          </div>

          {loading ? (
            <div className="flex flex-col items-center justify-center py-24 bg-white rounded-3xl border border-[#de9ca4]/20">
              <RefreshCw className="w-10 h-10 text-[#de9ca4] animate-spin mb-3" />
              <p className="text-sm text-[#9f364c] font-medium">Đang tải...</p>
            </div>
          ) : categories.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-24 bg-white rounded-3xl border border-[#de9ca4]/20">
              <div className="w-20 h-20 mb-5 bg-[#ffeced] rounded-2xl flex items-center justify-center">
                <FolderX className="w-10 h-10 text-[#de9ca4]" strokeWidth={1.5} />
              </div>
              <h3 className="text-xl font-bold text-[#4d2128] mb-2">Không tìm thấy giấy tờ phù hợp</h3>
              <p className="text-[#824c54] text-center max-w-sm text-sm">
                Vui lòng thử tìm kiếm với từ khóa khác.
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 gap-6">
              {categories.map((c) => (
                <div
                  key={c.id}
                  onClick={() =>
                    onNavigate('document-detail', { categoryId: c.id, categoryName: c.name })
                  }
                  className="group bg-white rounded-2xl p-6 flex flex-col md:flex-row items-center justify-between transition-all hover:shadow-xl hover:shadow-[#b7131a]/5 border border-transparent hover:border-[#de9ca4]/20 cursor-pointer"
                >
                  <div className="flex items-center gap-6 mb-4 md:mb-0">
                    <div className="w-16 h-16 rounded-2xl bg-[#ffd9dd] flex items-center justify-center text-[#b7131a] shrink-0">
                      <span
                        className="material-symbols-outlined text-3xl"
                        style={{ fontVariationSettings: "'FILL' 1" }}
                      >
                        account_balance
                      </span>
                    </div>
                    <div>
                      <h4 className="text-xl font-bold text-[#4d2128] group-hover:text-[#b7131a] transition-colors">
                        {c.name}
                      </h4>
                      <div className="flex items-center gap-4 mt-1">
                        <span className="flex items-center gap-1 text-sm text-[#9f364c]">
                          <span className="material-symbols-outlined text-xs">location_on</span>
                          Hà Nội
                        </span>
                        <span className="flex items-center gap-1 text-sm text-[#9f364c] font-bold">
                          <span className="material-symbols-outlined text-xs">list_alt</span>
                          Số nơi thực hiện: {c.count}
                        </span>
                      </div>
                    </div>
                  </div>
                  <button className="w-full md:w-auto px-10 py-3 bg-[#ffeced] text-[#b7131a] font-extrabold rounded-xl hover:bg-[#b7131a] hover:text-white transition-all flex items-center justify-center gap-2 shrink-0">
                    <span>Xem</span>
                    <span className="material-symbols-outlined text-sm">arrow_forward_ios</span>
                  </button>
                </div>
              ))}
            </div>
          )}
        </section>

        {/* Featured Categories */}
        <section className="mt-20">
          <div className="flex flex-col md:flex-row gap-8">
            <div className="flex-1 bg-gradient-to-br from-[#b7131a] to-[#ff766b] rounded-[2rem] p-10 text-white relative overflow-hidden group">
              <div className="absolute bottom-0 right-0 p-4 opacity-20 translate-y-4 group-hover:translate-y-0 transition-transform pointer-events-none">
                <span className="material-symbols-outlined text-[120px]">verified_user</span>
              </div>
              <h5 className="text-2xl font-bold mb-4">Thủ tục nhanh chóng</h5>
              <p className="text-white/80 max-w-xs mb-8 text-sm leading-relaxed">
                Tra cứu và xử lý các loại hồ sơ đất đai, hộ khẩu và tư pháp chỉ trong vài phút.
              </p>
              <button
                onClick={() => onNavigate('submit')}
                className="px-6 py-3 bg-white text-[#b7131a] font-bold rounded-xl shadow-lg hover:bg-[#ffefed] transition-colors text-sm"
              >
                Khám phá ngay
              </button>
            </div>
            <div className="md:w-1/3 flex flex-col gap-8">
              <div className="bg-[#ffd9dd] rounded-[2rem] p-8">
                <div className="w-12 h-12 bg-[#fdc003] rounded-full flex items-center justify-center mb-4">
                  <span className="material-symbols-outlined text-[#3d2b00]">history</span>
                </div>
                <h6 className="text-xl font-bold text-[#4d2128] mb-2">Lịch sử tra cứu</h6>
                <p className="text-sm text-[#9f364c]">Xem lại các cơ quan bạn đã truy cập gần đây.</p>
              </div>
              <div className="bg-white border border-[#de9ca4]/10 rounded-[2rem] p-8">
                <div className="w-12 h-12 bg-[#ffc2c9] rounded-full flex items-center justify-center mb-4">
                  <span className="material-symbols-outlined text-[#852139]">help</span>
                </div>
                <h6 className="text-xl font-bold text-[#4d2128] mb-2">Trung tâm hỗ trợ</h6>
                <p className="text-sm text-[#9f364c]">Hướng dẫn chi tiết về các loại giấy tờ.</p>
              </div>
            </div>
          </div>
        </section>

      </main>

      {/* ── Footer ── */}
      <footer className="mt-auto py-8 px-10 border-t border-[#de9ca4]/10 flex flex-col md:flex-row justify-between items-center text-xs text-[#9f364c] font-medium opacity-60">
        <p>© 2024 Cổng dịch vụ công Quốc gia. All rights reserved.</p>
        <div className="flex gap-6 mt-4 md:mt-0">
          {['Điều khoản sử dụng', 'Chính sách bảo mật', 'Liên hệ hỗ trợ'].map((t) => (
            <button key={t} className="hover:text-[#b7131a] transition-colors">
              {t}
            </button>
          ))}
        </div>
      </footer>

      {/* ── Mobile Bottom Nav ── */}
      <nav className="md:hidden fixed bottom-0 left-0 w-full bg-[#fff4f4]/90 backdrop-blur-md border-t border-[#ffeced] flex justify-around items-center py-3 px-2 z-50">
        {(
          [
            { label: 'Trang chủ', icon: 'home',          active: false, action: () => onNavigate('home')   },
            { label: 'Tài liệu',  icon: 'manage_search', active: true,  action: () => {}                   },
            { label: 'Hồ sơ',     icon: 'description',   active: false, action: () => onNavigate('submit') },
            { label: 'Cá nhân',   icon: 'person',         active: false, action: () => {}                   },
          ] as const
        ).map(({ label, icon, active, action }) => (
          <button
            key={label}
            onClick={action}
            className={`flex flex-col items-center gap-1 transition-colors ${
              active ? 'text-[#b7131a]' : 'text-[#4d2128]/60'
            }`}
          >
            <span
              className="material-symbols-outlined text-[22px]"
              style={{ fontVariationSettings: active ? "'FILL' 1" : "'FILL' 0" }}
            >
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
