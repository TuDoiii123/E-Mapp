import React, { useState, useEffect, useRef, useCallback } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { Loader2, AlertCircle, CalendarDays, Navigation, Clock, Route } from 'lucide-react';
import { servicesAPI, PublicService } from '../services/servicesApi';
import { getMapOverview, AgencyQueueStatus } from '../services/queueService';
import { mapAPI, AutocompletePrediction, DirectionsResult } from '../services/mapApi';

interface MapScreenProps {
  onNavigate: (screen: string, params?: any) => void;
}

const DEFAULT_LAT = 21.0285;
const DEFAULT_LNG = 105.8542;

const CATEGORY_CHIPS = [
  { key: 'all',    label: 'Tất cả' },
  { key: 'ubnd',   label: 'UBND' },
  { key: 'police', label: 'Công an' },
  { key: 'health', label: 'Y tế' },
];

const STATUS_CFG: Record<string, { dot: string; text: string; label: string }> = {
  available: { dot: 'bg-green-500 animate-pulse', text: 'text-green-600', label: 'ĐANG MỞ CỬA' },
  normal:    { dot: 'bg-green-500 animate-pulse', text: 'text-green-600', label: 'ĐANG MỞ CỬA' },
  busy:      { dot: 'bg-error',                   text: 'text-error',     label: 'SẮP ĐÓNG CỬA' },
  closed:    { dot: 'bg-error',                   text: 'text-error',     label: 'ĐÃ ĐÓNG CỬA' },
};

const statusOf = (s: string) => STATUS_CFG[s] ?? STATUS_CFG.available;

// ── Marker SVG helper ─────────────────────────────────────────────────────────
function buildMarkerIcon(waiting: number, loadLevel: string): L.DivIcon {
  const color = loadLevel === 'high' ? '#ef4444' : loadLevel === 'medium' ? '#f59e0b' : '#22c55e';
  const label = waiting > 99 ? '99+' : String(waiting);
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="44" height="54" viewBox="0 0 44 54">
    <ellipse cx="22" cy="21" rx="19" ry="19" fill="${color}" stroke="white" stroke-width="2.5"/>
    <polygon points="14,37 30,37 22,54" fill="${color}"/>
    <text x="22" y="27" text-anchor="middle" font-size="${label.length > 2 ? 10 : 13}"
      font-weight="bold" fill="white" font-family="Arial,sans-serif">${label}</text>
  </svg>`;
  return L.divIcon({
    html: svg,
    className: '',
    iconSize:   [44, 54],
    iconAnchor: [22, 54],
    popupAnchor:[0, -54],
  });
}

function buildUserIcon(): L.DivIcon {
  return L.divIcon({
    html: `<div style="width:16px;height:16px;background:#3B82F6;border:3px solid white;border-radius:50%;box-shadow:0 2px 6px rgba(0,0,0,.4)"></div>`,
    className: '',
    iconSize:   [16, 16],
    iconAnchor: [8, 8],
  });
}

// ── Component ─────────────────────────────────────────────────────────────────
export function MapScreen({ onNavigate }: MapScreenProps) {
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [radius,           setRadius]           = useState(5);
  const [searchQuery,      setSearchQuery]      = useState('');
  const [selectedOffice,   setSelectedOffice]   = useState<PublicService | null>(null);
  const [offices,          setOffices]          = useState<PublicService[]>([]);
  const [loading,          setLoading]          = useState(true);
  const [error,            setError]            = useState('');
  const [userLocation,     setUserLocation]     = useState<{ lat: number; lng: number } | null>(null);
  const [locationLoading,  setLocationLoading]  = useState(false);
  const [mapReady,         setMapReady]         = useState(false);
  const [queueData,        setQueueData]        = useState<Record<string, AgencyQueueStatus>>({});
  const [showDetail,       setShowDetail]       = useState(false);
  const [predictions,      setPredictions]      = useState<AutocompletePrediction[]>([]);
  const [showPredictions,  setShowPredictions]  = useState(false);
  const [directionsInfo,   setDirectionsInfo]   = useState<DirectionsResult | null>(null);
  const [directionsLoading,setDirectionsLoading]= useState(false);

  const mapRef         = useRef<HTMLDivElement>(null);
  const mapInstance    = useRef<L.Map | null>(null);
  const markersRef     = useRef<L.Marker[]>([]);
  const userMarkerRef  = useRef<L.Marker | null>(null);
  const acTimer        = useRef<ReturnType<typeof setTimeout> | null>(null);

  // ── Init Leaflet map ───────────────────────────────────────────────────────
  useEffect(() => {
    if (!mapRef.current || mapInstance.current) return;

    const map = L.map(mapRef.current, {
      center: [DEFAULT_LAT, DEFAULT_LNG],
      zoom:   DEFAULT_ZOOM_LEVEL,
      zoomControl: false,
      attributionControl: true,
    });

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
      maxZoom: 19,
    }).addTo(map);

    mapInstance.current = map;
    setMapReady(true);

    return () => {
      map.remove();
      mapInstance.current = null;
    };
  }, []);

  // ── User location marker ───────────────────────────────────────────────────
  useEffect(() => {
    if (!mapInstance.current || !userLocation) return;
    const latlng: L.LatLngExpression = [userLocation.lat, userLocation.lng];
    mapInstance.current.setView(latlng, mapInstance.current.getZoom());
    if (userMarkerRef.current) {
      userMarkerRef.current.setLatLng(latlng);
    } else {
      userMarkerRef.current = L.marker(latlng, { icon: buildUserIcon(), zIndexOffset: 1000 })
        .addTo(mapInstance.current)
        .bindPopup('Vị trí của bạn');
    }
  }, [userLocation]);

  // ── Office markers ─────────────────────────────────────────────────────────
  useEffect(() => {
    if (!mapInstance.current || !mapReady) return;
    markersRef.current.forEach(m => m.remove());
    markersRef.current = [];

    offices.forEach(office => {
      if (!office.latitude || !office.longitude) return;
      const qs        = queueData[office.id];
      const loadLevel = qs?.loadLevel ?? 'low';
      const waiting   = qs?.totalWaiting ?? 0;
      const color     = loadLevel === 'high' ? '#ef4444' : loadLevel === 'medium' ? '#f59e0b' : '#22c55e';

      const marker = L.marker(
        [office.latitude, office.longitude],
        { icon: buildMarkerIcon(waiting, loadLevel) },
      ).addTo(mapInstance.current!);

      marker.bindPopup(`
        <div style="padding:4px;min-width:180px;font-family:sans-serif">
          <h3 style="margin:0 0 4px;font-weight:bold;font-size:13px">${office.name}</h3>
          <p style="margin:0 0 3px;font-size:11px;color:#555">${office.address}</p>
          ${qs ? `<p style="margin:4px 0 0;font-size:11px;color:${color};font-weight:600">Đang chờ: ${waiting} người</p>` : ''}
        </div>
      `);

      marker.on('click', () => handleViewDetails(office));
      markersRef.current.push(marker);
    });

    if (markersRef.current.length > 0) {
      const group = L.featureGroup(markersRef.current);
      if (userMarkerRef.current) group.addLayer(userMarkerRef.current);
      mapInstance.current.fitBounds(group.getBounds(), { padding: [40, 40] });
    }
  }, [offices, queueData, mapReady]);

  // ── Queue polling ──────────────────────────────────────────────────────────
  useEffect(() => {
    const fetch = async () => { try { setQueueData(await getMapOverview()); } catch {} };
    fetch();
    const id = setInterval(fetch, 30_000);
    return () => clearInterval(id);
  }, []);

  // ── Load services ──────────────────────────────────────────────────────────
  useEffect(() => { loadServices(); }, [selectedCategory, radius, userLocation]);

  const loadServices = async () => {
    setLoading(true); setError('');
    try {
      const res = await servicesAPI.getNearby(
        userLocation?.lat || DEFAULT_LAT,
        userLocation?.lng || DEFAULT_LNG,
        radius,
        selectedCategory === 'all' ? undefined : selectedCategory,
      );
      if (res.success) setOffices(res.data.services);
      else setError('Không thể tải danh sách dịch vụ');
    } catch (e: any) {
      setError(e.message || 'Lỗi khi tải dịch vụ');
    } finally { setLoading(false); }
  };

  // ── Geolocation ────────────────────────────────────────────────────────────
  const getCurrentLocation = () => {
    setLocationLoading(true);
    if (!navigator.geolocation) {
      setError('Trình duyệt không hỗ trợ GPS');
      setUserLocation({ lat: DEFAULT_LAT, lng: DEFAULT_LNG });
      setLocationLoading(false);
      return;
    }
    navigator.geolocation.getCurrentPosition(
      pos => {
        setUserLocation({ lat: pos.coords.latitude, lng: pos.coords.longitude });
        setLocationLoading(false);
      },
      () => {
        setError('Không thể lấy vị trí. Dùng vị trí mặc định.');
        setUserLocation({ lat: DEFAULT_LAT, lng: DEFAULT_LNG });
        setLocationLoading(false);
      },
    );
  };

  // ── Autocomplete ───────────────────────────────────────────────────────────
  const handleSearchInput = useCallback((value: string) => {
    setSearchQuery(value);
    if (acTimer.current) clearTimeout(acTimer.current);
    if (!value.trim() || value.length < 2) {
      setPredictions([]); setShowPredictions(false); return;
    }
    acTimer.current = setTimeout(async () => {
      try {
        const res = await mapAPI.autocomplete(value, userLocation?.lat, userLocation?.lng);
        if (res.success) {
          setPredictions(res.data.predictions);
          setShowPredictions(res.data.predictions.length > 0);
        }
      } catch { /* ignore */ }
    }, 350);
  }, [userLocation]);

  const selectPrediction = (pred: AutocompletePrediction) => {
    setSearchQuery(pred.description);
    setPredictions([]); setShowPredictions(false);
    if (mapInstance.current) {
      mapInstance.current.setView([pred.lat, pred.lng], 16);
    }
  };

  // ── Directions ─────────────────────────────────────────────────────────────
  const fetchDirections = async (office: PublicService) => {
    if (!office.latitude || !office.longitude) return;
    setDirectionsLoading(true); setDirectionsInfo(null);
    try {
      const origin = userLocation || { lat: DEFAULT_LAT, lng: DEFAULT_LNG };
      const res = await mapAPI.getDirections(origin, { lat: office.latitude, lng: office.longitude });
      if (res.success) setDirectionsInfo(res.data);
    } catch { /* ignore */ } finally { setDirectionsLoading(false); }
  };

  // ── View details ───────────────────────────────────────────────────────────
  const handleViewDetails = async (office: PublicService) => {
    setDirectionsInfo(null);
    try {
      const res = await servicesAPI.getById(
        office.id,
        userLocation?.lat || DEFAULT_LAT,
        userLocation?.lng || DEFAULT_LNG,
      );
      setSelectedOffice(res.success ? res.data.service : office);
    } catch { setSelectedOffice(office); }
    setShowDetail(true);
    fetchDirections(office);

    // Pan map to selected office
    if (mapInstance.current && office.latitude && office.longitude) {
      mapInstance.current.panTo([office.latitude, office.longitude]);
    }
  };

  const fmt = (d?: number) => !d ? 'N/A' : d < 1 ? `${Math.round(d * 1000)} m` : `${d.toFixed(1)} km`;

  const filteredOffices = searchQuery.trim()
    ? offices.filter(o =>
        o.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (o.address || '').toLowerCase().includes(searchQuery.toLowerCase()),
      )
    : offices;

  // ── Render ─────────────────────────────────────────────────────────────────
  return (
    <div className="bg-surface text-on-background overflow-hidden h-screen flex" style={{ fontFamily: "'Manrope', sans-serif" }}>

      <main className="flex-1 flex flex-col relative h-full">

        {/* TopNavBar */}
        <header className="bg-surface flex justify-between items-center px-6 py-4 w-full top-0 z-50 border-b border-outline-variant/20">
          <div className="flex items-center gap-8">
            <button onClick={() => onNavigate('home')} className="text-primary font-extrabold text-xl tracking-tighter uppercase">
              Cổng dịch vụ công
            </button>
            <nav className="hidden lg:flex items-center gap-6">
              <span className="text-primary border-b-2 border-primary pb-1 font-bold text-base tracking-tight">Bản đồ</span>
              <button onClick={() => onNavigate('submit')} className="text-on-background opacity-70 hover:text-primary font-bold text-base tracking-tight transition-colors">Thủ tục</button>
              <button onClick={() => onNavigate('home')}   className="text-on-background opacity-70 hover:text-primary font-bold text-base tracking-tight transition-colors">Tin tức</button>
            </nav>
          </div>
          <div className="flex items-center gap-4">
            <div className="relative hidden sm:block">
              <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-outline text-[20px]">search</span>
              <input
                value={searchQuery}
                onChange={e => handleSearchInput(e.target.value)}
                className="pl-10 pr-4 py-2 bg-surface-container-low border-none rounded-full text-sm focus:ring-2 focus:ring-primary w-64 outline-none"
                placeholder="Tìm kiếm dịch vụ..."
              />
            </div>
            <button onClick={() => onNavigate('notification')} className="p-2 text-primary hover:bg-surface-container-high rounded-full transition-colors">
              <span className="material-symbols-outlined">notifications</span>
            </button>
            <button className="p-2 text-primary hover:bg-surface-container-high rounded-full transition-colors">
              <span className="material-symbols-outlined">account_circle</span>
            </button>
          </div>
        </header>

        {/* Content */}
        <div className="flex-1 flex overflow-hidden">

          {/* Sidebar */}
          <div className="w-full max-w-sm bg-surface-container-lowest shadow-xl z-20 flex flex-col h-full border-r border-outline-variant/20">
            <div className="p-5 space-y-5">

              {/* Search + Autocomplete */}
              <div className="relative">
                <input
                  value={searchQuery}
                  onChange={e => handleSearchInput(e.target.value)}
                  onFocus={() => predictions.length > 0 && setShowPredictions(true)}
                  onBlur={() => setTimeout(() => setShowPredictions(false), 200)}
                  className="w-full bg-surface-container-low border-none rounded-xl py-4 pl-12 pr-4 text-on-surface font-semibold focus:ring-2 focus:ring-primary placeholder:text-outline/60 outline-none text-sm"
                  placeholder="Nhập tên cơ quan, địa chỉ..."
                />
                <span className="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-primary text-[20px]">search</span>
                {searchQuery && (
                  <button
                    onClick={() => { setSearchQuery(''); setPredictions([]); setShowPredictions(false); }}
                    className="absolute right-4 top-1/2 -translate-y-1/2 text-outline hover:text-primary"
                  >
                    <span className="material-symbols-outlined text-[18px]">close</span>
                  </button>
                )}
                {showPredictions && predictions.length > 0 && (
                  <ul className="absolute top-full left-0 right-0 mt-1 bg-surface-container-lowest rounded-xl shadow-2xl border border-outline-variant/20 z-50 max-h-64 overflow-y-auto">
                    {predictions.map(p => (
                      <li
                        key={p.placeId}
                        onMouseDown={() => selectPrediction(p)}
                        className="px-4 py-3 cursor-pointer hover:bg-surface-container transition-colors flex items-start gap-3"
                      >
                        <span className="material-symbols-outlined text-primary text-[18px] flex-shrink-0 mt-0.5">location_on</span>
                        <div className="min-w-0">
                          <p className="text-sm font-semibold text-on-surface truncate">{p.mainText}</p>
                          {p.secondaryText && (
                            <p className="text-xs text-on-surface-variant truncate">{p.secondaryText}</p>
                          )}
                        </div>
                      </li>
                    ))}
                  </ul>
                )}
              </div>

              {/* Radius */}
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="font-bold text-on-surface-variant uppercase tracking-widest text-[10px]">Bán kính tìm kiếm</span>
                  <span className="text-primary font-bold text-sm">{radius} km</span>
                </div>
                <input
                  type="range" min={1} max={20} value={radius}
                  onChange={e => setRadius(Number(e.target.value))}
                  className="w-full h-2 bg-surface-container-high rounded-lg appearance-none cursor-pointer accent-primary"
                />
              </div>

              {/* Category chips */}
              <div className="flex flex-wrap gap-2">
                {CATEGORY_CHIPS.map(({ key, label }) => (
                  <button
                    key={key}
                    onClick={() => setSelectedCategory(key)}
                    className={`px-4 py-2 rounded-full text-xs font-bold shadow-sm transition-colors ${
                      selectedCategory === key
                        ? 'bg-primary text-on-primary'
                        : 'bg-surface-container-high text-on-surface-variant hover:bg-primary-container hover:text-on-primary'
                    }`}
                  >
                    {label}
                  </button>
                ))}
              </div>

              {error && (
                <div className="flex items-start gap-2 p-3 bg-error-container/20 border-l-4 border-error rounded-lg text-sm text-error">
                  <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
                  {error}
                </div>
              )}
            </div>

            {/* Results list */}
            <div className="flex-1 overflow-y-auto px-5 pb-5 space-y-4">
              {loading ? (
                <div className="flex items-center justify-center py-10">
                  <Loader2 className="w-6 h-6 animate-spin text-primary" />
                  <span className="ml-2 text-sm text-on-surface-variant">Đang tải...</span>
                </div>
              ) : filteredOffices.length === 0 ? (
                <p className="text-center text-sm text-outline py-10">
                  Không tìm thấy dịch vụ trong bán kính {radius} km
                </p>
              ) : (
                filteredOffices.map(office => {
                  const qs   = queueData[office.id];
                  const st   = statusOf(office.status);
                  const dist = fmt(office.distance);
                  return (
                    <div
                      key={office.id}
                      onClick={() => handleViewDetails(office)}
                      className="p-4 rounded-xl bg-surface-container-low border border-transparent hover:bg-surface-container-lowest hover:shadow-lg transition-all cursor-pointer group"
                    >
                      <div className="flex justify-between items-start mb-2">
                        <h3 className="font-bold text-on-background leading-tight group-hover:text-primary transition-colors text-sm">
                          {office.name}
                        </h3>
                        {dist !== 'N/A' && (
                          <span className="text-[10px] font-extrabold text-secondary px-2 py-0.5 bg-secondary-container rounded-full flex-shrink-0 ml-2">
                            {dist}
                          </span>
                        )}
                      </div>

                      <p className="text-xs text-on-surface-variant mb-3 flex items-start gap-1">
                        <span className="material-symbols-outlined text-[14px] flex-shrink-0 mt-0.5">location_on</span>
                        {office.address}
                      </p>

                      <div className="flex items-center gap-2 mb-4">
                        <span className={`w-2 h-2 rounded-full ${st.dot}`}></span>
                        <span className={`text-[10px] font-bold ${st.text}`}>{st.label}</span>
                        {qs && (
                          <span className="ml-auto text-[10px] font-bold text-outline">
                            {qs.totalWaiting} đang chờ
                          </span>
                        )}
                      </div>

                      <div className="grid grid-cols-2 gap-3">
                        <button
                          onClick={e => { e.stopPropagation(); onNavigate('appointment', { defaultAgencyId: office.id }); }}
                          className="bg-primary text-on-primary py-2.5 rounded-lg text-[11px] font-extrabold uppercase tracking-tighter hover:scale-95 transition-transform flex items-center justify-center gap-1"
                        >
                          <CalendarDays className="w-3 h-3" /> Đặt lịch
                        </button>
                        <button
                          onClick={e => {
                            e.stopPropagation();
                            if (office.latitude && office.longitude) {
                              const origin = userLocation || { lat: DEFAULT_LAT, lng: DEFAULT_LNG };
                              window.open(
                                `https://www.openstreetmap.org/directions?engine=osrm_car&route=${origin.lat},${origin.lng};${office.latitude},${office.longitude}`,
                                '_blank',
                              );
                            }
                          }}
                          className="bg-surface-container-highest text-on-surface-variant py-2.5 rounded-lg text-[11px] font-extrabold uppercase tracking-tighter hover:bg-secondary hover:text-on-secondary transition-colors flex items-center justify-center gap-1"
                        >
                          <Navigation className="w-3 h-3" /> Chỉ đường
                        </button>
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          </div>

          {/* Map area */}
          <div className="flex-1 relative bg-surface-container overflow-hidden">

            {/* Leaflet container */}
            <div ref={mapRef} className="absolute inset-0 w-full h-full" />

            {/* Map controls */}
            <div className="absolute bottom-10 right-10 flex flex-col gap-3 z-[400]">
              <button
                onClick={() => mapInstance.current?.zoomIn()}
                className="w-12 h-12 bg-surface-container-lowest rounded-xl shadow-xl flex items-center justify-center text-primary hover:bg-primary hover:text-on-primary transition-all"
                aria-label="Phóng to"
              >
                <span className="material-symbols-outlined">add</span>
              </button>
              <button
                onClick={() => mapInstance.current?.zoomOut()}
                className="w-12 h-12 bg-surface-container-lowest rounded-xl shadow-xl flex items-center justify-center text-primary hover:bg-primary hover:text-on-primary transition-all"
                aria-label="Thu nhỏ"
              >
                <span className="material-symbols-outlined">remove</span>
              </button>
              <button
                onClick={getCurrentLocation}
                disabled={locationLoading}
                className="w-12 h-12 bg-surface-container-lowest rounded-xl shadow-xl flex items-center justify-center text-primary hover:bg-primary hover:text-on-primary transition-all disabled:opacity-50"
                aria-label="Vị trí hiện tại"
              >
                {locationLoading
                  ? <Loader2 className="w-5 h-5 animate-spin" />
                  : <span className="material-symbols-outlined">my_location</span>
                }
              </button>
            </div>

            {/* Detail panel */}
            {showDetail && selectedOffice && (
              <div className="absolute top-10 right-10 w-80 bg-surface/90 backdrop-blur-xl rounded-2xl shadow-2xl border border-outline-variant/20 p-6 hidden xl:block z-[400] animate-fade-in">
                <div className="flex items-center justify-between mb-4">
                  <span className="text-xs font-black text-on-surface-variant uppercase tracking-[0.2em]">Thông tin chi tiết</span>
                  <button onClick={() => setShowDetail(false)} className="text-outline hover:text-primary transition-colors">
                    <span className="material-symbols-outlined">close</span>
                  </button>
                </div>

                <h2 className="text-lg font-extrabold text-on-background mb-1">{selectedOffice.name}</h2>
                <p className="text-sm text-on-surface-variant mb-4 flex items-start gap-1">
                  <span className="material-symbols-outlined text-[16px] flex-shrink-0 mt-0.5">location_on</span>
                  {selectedOffice.address}
                </p>

                <div className="grid grid-cols-2 gap-2 mb-4">
                  <div className="bg-surface-container p-3 rounded-lg">
                    <p className="text-[10px] font-bold text-outline uppercase mb-1">Trạng thái</p>
                    <div className="flex items-center gap-1.5">
                      <span className={`w-2 h-2 rounded-full ${statusOf(selectedOffice.status).dot}`}></span>
                      <span className={`text-xs font-bold ${statusOf(selectedOffice.status).text}`}>
                        {statusOf(selectedOffice.status).label}
                      </span>
                    </div>
                  </div>

                  <div className="bg-surface-container p-3 rounded-lg">
                    <p className="text-[10px] font-bold text-outline uppercase mb-1">Khoảng cách</p>
                    {directionsLoading
                      ? <Loader2 className="w-4 h-4 animate-spin text-secondary" />
                      : <span className="text-lg font-black text-secondary">
                          {directionsInfo?.distance.text || fmt(selectedOffice.distance)}
                        </span>
                    }
                  </div>

                  {(directionsInfo || directionsLoading) && (
                    <div className="bg-surface-container p-3 rounded-lg">
                      <p className="text-[10px] font-bold text-outline uppercase mb-1 flex items-center gap-1">
                        <Clock className="w-3 h-3" /> Thời gian
                      </p>
                      {directionsLoading
                        ? <Loader2 className="w-4 h-4 animate-spin text-primary" />
                        : <span className="text-lg font-black text-primary">{directionsInfo?.duration.text || 'N/A'}</span>
                      }
                    </div>
                  )}

                  {queueData[selectedOffice.id] && (
                    <>
                      <div className="bg-surface-container p-3 rounded-lg">
                        <p className="text-[10px] font-bold text-outline uppercase mb-1">Đang chờ</p>
                        <span className="text-lg font-black text-primary">{queueData[selectedOffice.id].totalWaiting}</span>
                      </div>
                      <div className="bg-surface-container p-3 rounded-lg">
                        <p className="text-[10px] font-bold text-outline uppercase mb-1">Đang phục vụ</p>
                        <span className="text-lg font-black text-secondary">{queueData[selectedOffice.id].totalServing}</span>
                      </div>
                    </>
                  )}
                </div>

                <div className="space-y-2">
                  <button
                    onClick={() => onNavigate('appointment', { defaultAgencyId: selectedOffice.id })}
                    className="w-full bg-primary text-on-primary py-3.5 rounded-xl font-black text-sm uppercase tracking-widest shadow-lg hover:opacity-90 transition-opacity"
                  >
                    Xác nhận đặt lịch
                  </button>
                  <button
                    onClick={() => {
                      const url = directionsInfo?.osmUrl
                        || (selectedOffice.latitude && selectedOffice.longitude
                          ? `https://www.openstreetmap.org/directions?engine=osrm_car&route=${DEFAULT_LAT},${DEFAULT_LNG};${selectedOffice.latitude},${selectedOffice.longitude}`
                          : null);
                      if (url) window.open(url, '_blank');
                    }}
                    className="w-full bg-surface-container-high text-on-surface-variant py-3 rounded-xl font-bold text-sm hover:bg-secondary-container hover:text-on-secondary-container transition-colors flex items-center justify-center gap-2"
                  >
                    <Route className="w-4 h-4" /> Chỉ đường (OpenStreetMap)
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </main>

      {/* Mobile bottom nav */}
      <nav className="md:hidden fixed bottom-0 left-0 right-0 bg-surface/80 backdrop-blur-md border-t border-outline-variant/20 flex justify-around items-center py-3 z-50">
        <button className="flex flex-col items-center gap-1 text-primary">
          <span className="material-symbols-outlined" style={{ fontVariationSettings: "'FILL' 1" }}>map</span>
          <span className="text-[10px] font-bold uppercase">Bản đồ</span>
        </button>
        <button className="flex flex-col items-center gap-1 text-on-surface-variant opacity-70" onClick={() => onNavigate('submit')}>
          <span className="material-symbols-outlined">description</span>
          <span className="text-[10px] font-bold uppercase">Thủ tục</span>
        </button>
        <button className="flex flex-col items-center gap-1 text-on-surface-variant opacity-70" onClick={() => onNavigate('home')}>
          <span className="material-symbols-outlined">article</span>
          <span className="text-[10px] font-bold uppercase">Tin tức</span>
        </button>
        <button className="flex flex-col items-center gap-1 text-on-surface-variant opacity-70">
          <span className="material-symbols-outlined">person</span>
          <span className="text-[10px] font-bold uppercase">Tôi</span>
        </button>
      </nav>
    </div>
  );
}

const DEFAULT_ZOOM_LEVEL = 13;
