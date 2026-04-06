import React, { useEffect, useState } from 'react';
import { API_BASE_URL } from '../services/api';
import { ArrowLeft, RefreshCw, Phone, MessageCircle } from 'lucide-react';

interface DocumentDetailProps {
  onNavigate: (screen: string, params?: any) => void;
  serviceId?: string;
  params?: any;
}

export function DocumentDetailScreen({ onNavigate, serviceId, params }: DocumentDetailProps) {
  const [service, setService] = useState<any | null>(null);
  const [loading, setLoading] = useState(false);
  const [locations, setLocations] = useState<any[] | null>(null);

  useEffect(() => {
    const categoryId = params?.categoryId;
    const categoryName = params?.categoryName;
    if (!serviceId && !categoryId) return;
    setLoading(true);
    if (categoryId) {
      fetch(`${API_BASE_URL}/services?category=${encodeURIComponent(categoryId)}&limit=500`)
        .then((r) => r.json())
        .then((d) => {
          const data = d && d.success && d.data ? d.data : d;
          setLocations(Array.isArray(data) ? data : data.services || []);
          setService({ id: categoryId, name: categoryName || 'Danh mục' });
        })
        .catch(() => {
          setLocations([]);
          setService({ id: categoryId, name: categoryName || 'Danh mục' });
        })
        .finally(() => setLoading(false));
    } else {
      fetch(`${API_BASE_URL}/services/${encodeURIComponent(String(serviceId))}`)
        .then((r) => r.json())
        .then((d) => {
          if (d && d.success && d.data && d.data.service) setService(d.data.service);
          else setService(d || null);
        })
        .catch(() => setService(null))
        .finally(() => setLoading(false));
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [serviceId, params?.categoryId, params?.categoryName]);

  return (
    <div
      className="bg-[#fff4f4] text-[#4d2128] min-h-screen flex flex-col"
      style={{ fontFamily: "'Manrope', sans-serif" }}
    >
      {/* ── TopNavBar ── */}
      <header className="flex items-center gap-4 w-full px-6 md:px-10 py-4 bg-[#fff4f4]/80 backdrop-blur-md sticky top-0 z-40 border-b border-[#de9ca4]/20">
        <button
          onClick={() => onNavigate('document-catalog')}
          className="w-10 h-10 flex items-center justify-center rounded-full hover:bg-[#ffd9dd] transition-all text-[#9f364c]"
          aria-label="Quay lại"
        >
          <ArrowLeft className="w-5 h-5" />
        </button>
        <div className="flex-1 min-w-0">
          <p className="text-xs font-bold text-[#9f364c] uppercase tracking-widest">Chi tiết giấy tờ</p>
          <h1 className="text-base font-black text-[#4d2128] truncate">
            {service?.name || 'Đang tải...'}
          </h1>
        </div>
        <div className="hidden sm:flex items-center gap-2 px-4 py-2 bg-[#ffeced] rounded-full">
          <span className="w-2 h-2 rounded-full bg-green-500" />
          <span className="text-sm font-bold text-[#4d2128]">Synthesis Hub</span>
        </div>
      </header>

      {/* ── Main ── */}
      <main className="flex-1 px-6 md:px-10 py-10 max-w-6xl mx-auto w-full">

        {loading ? (
          <div className="flex flex-col items-center justify-center py-32">
            <RefreshCw className="w-10 h-10 text-[#de9ca4] animate-spin mb-3" />
            <p className="text-sm text-[#9f364c] font-medium">Đang tải...</p>
          </div>
        ) : !service ? (
          <div className="flex flex-col items-center justify-center py-32 bg-white rounded-3xl border border-[#de9ca4]/20">
            <span className="material-symbols-outlined text-[60px] text-[#de9ca4] mb-4">search_off</span>
            <h3 className="text-xl font-bold text-[#4d2128] mb-2">Không tìm thấy thông tin</h3>
            <p className="text-sm text-[#824c54]">Vui lòng thử lại hoặc quay về danh sách.</p>
          </div>
        ) : (
          <>
            {/* Hero banner */}
            <section className="mb-10">
              <div className="bg-white rounded-3xl p-8 border border-[#de9ca4]/10 relative overflow-hidden">
                <div className="absolute top-0 right-0 w-48 h-48 bg-[#b7131a]/5 rounded-full -mr-12 -mt-12 blur-3xl pointer-events-none" />
                <div className="relative z-10 flex flex-col md:flex-row md:items-center gap-6">
                  <div className="w-20 h-20 rounded-2xl bg-[#ffd9dd] flex items-center justify-center text-[#b7131a] shrink-0">
                    <span
                      className="material-symbols-outlined text-4xl"
                      style={{ fontVariationSettings: "'FILL' 1" }}
                    >
                      account_balance
                    </span>
                  </div>
                  <div className="flex-1 min-w-0">
                    <h2 className="text-2xl font-extrabold text-[#4d2128] mb-1">{service.name}</h2>
                    {service.categoryId && (
                      <p className="text-sm text-[#9f364c]">Thể loại: {service.categoryId}</p>
                    )}
                    {locations && (
                      <div className="flex items-center gap-2 mt-2">
                        <span className="flex items-center gap-1 text-sm text-[#9f364c] font-bold">
                          <span className="material-symbols-outlined text-xs">list_alt</span>
                          Số nơi thực hiện: {locations.length}
                        </span>
                        <span className="flex items-center gap-1 text-sm text-[#9f364c]">
                          <span className="material-symbols-outlined text-xs">location_on</span>
                          Hà Nội
                        </span>
                      </div>
                    )}
                    {service.description && (
                      <p className="text-sm text-[#824c54] mt-3 leading-relaxed">{service.description}</p>
                    )}
                  </div>
                </div>
              </div>
            </section>

            {/* Location list */}
            {locations && locations.length > 0 ? (
              <section>
                <div className="flex items-center justify-between mb-8">
                  <h3 className="text-2xl font-bold text-[#4d2128]">Danh sách nơi thực hiện</h3>
                  <div className="flex items-center gap-1 text-[#9f364c] text-sm font-semibold cursor-pointer hover:text-[#b7131a] transition-colors">
                    <span>Sắp xếp: Mặc định</span>
                    <span className="material-symbols-outlined text-sm">expand_more</span>
                  </div>
                </div>
                <div className="grid grid-cols-1 gap-6">
                  {locations.map((loc: any, idx: number) => (
                    <div
                      key={`${loc.id || loc.code || loc.name || 'loc'}-${idx}`}
                      className="group bg-white rounded-2xl p-6 flex flex-col md:flex-row items-start md:items-center justify-between transition-all hover:shadow-xl hover:shadow-[#b7131a]/5 border border-transparent hover:border-[#de9ca4]/20"
                    >
                      <div className="flex items-start gap-6 mb-4 md:mb-0 flex-1 min-w-0">
                        <div className="w-14 h-14 rounded-2xl bg-[#ffd9dd] flex items-center justify-center text-[#b7131a] shrink-0">
                          <span
                            className="material-symbols-outlined text-2xl"
                            style={{ fontVariationSettings: "'FILL' 1" }}
                          >
                            domain
                          </span>
                        </div>
                        <div className="flex-1 min-w-0">
                          <h4 className="text-lg font-bold text-[#4d2128] group-hover:text-[#b7131a] transition-colors truncate">
                            {loc.name || loc.ten || loc.serviceName || 'Đơn vị thực hiện'}
                          </h4>
                          {(loc.address || loc.diachi) && (
                            <span className="flex items-center gap-1 text-sm text-[#9f364c] mt-1">
                              <span className="material-symbols-outlined text-xs">location_on</span>
                              {loc.address || loc.diachi}
                            </span>
                          )}
                          {(loc.phone || loc.sdt || loc.contact) && (
                            <span className="flex items-center gap-1 text-sm text-[#9f364c] font-bold mt-0.5">
                              <span className="material-symbols-outlined text-xs">call</span>
                              {loc.phone || loc.sdt || loc.contact}
                            </span>
                          )}
                        </div>
                      </div>
                      <button className="w-full md:w-auto px-8 py-3 bg-[#ffeced] text-[#b7131a] font-extrabold rounded-xl hover:bg-[#b7131a] hover:text-white transition-all flex items-center justify-center gap-2 shrink-0">
                        <span>Xem</span>
                        <span className="material-symbols-outlined text-sm">arrow_forward_ios</span>
                      </button>
                    </div>
                  ))}
                </div>
              </section>
            ) : (
              /* Single service detail */
              <section className="space-y-6">
                {/* Contact info card */}
                <div className="bg-white rounded-2xl p-6 border border-[#de9ca4]/10">
                  <p className="text-xs font-black uppercase tracking-widest text-[#824c54]/60 mb-4">
                    Thông tin liên hệ
                  </p>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {[
                      { icon: 'location_on', label: 'Địa chỉ',    value: service.address  },
                      { icon: 'call',        label: 'Điện thoại', value: service.phone    },
                      { icon: 'mail',        label: 'Email',      value: service.email    },
                      { icon: 'language',    label: 'Website',    value: service.website  },
                    ].map(({ icon, label, value }) => (
                      <div key={label} className="flex items-start gap-3">
                        <div className="w-9 h-9 rounded-xl bg-[#ffeced] flex items-center justify-center text-[#b7131a] shrink-0 mt-0.5">
                          <span className="material-symbols-outlined text-sm">{icon}</span>
                        </div>
                        <div>
                          <p className="text-[10px] font-black uppercase tracking-widest text-[#824c54]/60">
                            {label}
                          </p>
                          <p className="text-sm font-semibold text-[#4d2128]">{value || '—'}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Action buttons */}
                <div className="flex gap-3">
                  <button className="flex-1 h-12 bg-[#b7131a] text-white font-bold text-sm rounded-xl flex items-center justify-center gap-2 hover:bg-[#a40010] active:scale-[0.98] transition-all shadow-lg shadow-[#b7131a]/20">
                    <Phone className="w-4 h-4" /> Gọi hotline
                  </button>
                  <button
                    onClick={() => onNavigate('chatbot')}
                    className="flex-1 h-12 border-2 border-[#b7131a] text-[#b7131a] font-bold text-sm rounded-xl flex items-center justify-center gap-2 hover:bg-[#ffeced] active:scale-[0.98] transition-all"
                  >
                    <MessageCircle className="w-4 h-4" /> Hỏi AI
                  </button>
                </div>
              </section>
            )}
          </>
        )}
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
            { label: 'Trang chủ', icon: 'home',          active: false, action: () => onNavigate('home')            },
            { label: 'Tài liệu',  icon: 'manage_search', active: true,  action: () => onNavigate('document-catalog') },
            { label: 'Hồ sơ',     icon: 'description',   active: false, action: () => onNavigate('submit')          },
            { label: 'Cá nhân',   icon: 'person',         active: false, action: () => {}                            },
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

export default DocumentDetailScreen;
