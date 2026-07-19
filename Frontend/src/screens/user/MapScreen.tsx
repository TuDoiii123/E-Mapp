import React, { useState, useEffect, useRef, useCallback } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import {
  Loader2, AlertCircle, CalendarDays, Navigation, Clock,
  Sparkles, Users, MapPin, Car, PersonStanding, Bike,
  Trophy, Search, X, ArrowLeft, Phone, Globe, Star, Route,
  LayoutGrid, IdCard, Home, Baby, Heart, Landmark, Briefcase, Stethoscope,
} from 'lucide-react';
import { servicesAPI, PublicService } from '../../services/servicesApi';
import { getMapOverview, AgencyQueueStatus } from '../../services/queueService';
import { mapAPI, DirectionsResult, RouteStep, SmartRecommendation } from '../../services/mapApi';
import { adminDivisionsAPI, AdminDivision } from '../../services/adminDivisionsApi';

interface MapScreenProps { onNavigate: (screen: string, params?: any) => void; }

const DEFAULT_LAT  = 21.0285;  // Hà Nội — Hồ Hoàn Kiếm
const DEFAULT_LNG  = 105.8542;
const DEFAULT_ZOOM = 12;
// Mặc định chỉ tải cơ quan quanh vị trí trong bán kính này; muốn xa hơn thì
// chọn tỉnh (toàn tỉnh) hoặc gõ tìm kiếm (quét toàn bộ DB)
const NEARBY_RADIUS_KM = 5;

const CATEGORY_CHIPS = [
  { key: 'all',       label: 'Tất cả' },
  { key: 'ubnd',      label: 'UBND' },
  { key: 'police',    label: 'Công an' },
  { key: 'health',    label: 'Y tế' },
  { key: 'bhxh',      label: 'BHXH' },
  { key: 'tax',       label: 'Thuế' },
  { key: 'so-nganh',  label: 'Sở ngành' },
];

const SMART_SERVICES = [
  { id: 'all',          label: 'Tất cả thủ tục',    Icon: LayoutGrid },
  { id: 'cccd',         label: 'CCCD / Căn cước',   Icon: IdCard },
  { id: 'ho_khau',      label: 'Hộ khẩu / Cư trú',  Icon: Home },
  { id: 'khai_sinh',    label: 'Khai sinh',          Icon: Baby },
  { id: 'ket_hon',      label: 'Đăng ký kết hôn',   Icon: Heart },
  { id: 'dat_dai',      label: 'Đất đai / Nhà ở',   Icon: Landmark },
  { id: 'doanh_nghiep', label: 'Doanh nghiệp',       Icon: Briefcase },
  { id: 'y_te',         label: 'Y tế / Khám bệnh',  Icon: Stethoscope },
  { id: 'gplx',         label: 'Giấy phép lái xe',  Icon: Car },
];

const LOAD_COLOR: Record<string, string> = { low: '#22c55e', medium: '#f59e0b', high: '#ef4444' };
const LOAD_BG:    Record<string, string> = { low: 'bg-green-500', medium: 'bg-amber-500', high: 'bg-red-500' };
const LOAD_TEXT:  Record<string, string> = { low: 'text-green-600', medium: 'text-amber-600', high: 'text-red-600' };
const LOAD_LABEL: Record<string, string> = { low: 'Vắng', medium: 'Trung bình', high: 'Đông' };

// ── Marker builders ───────────────────────────────────────────────────────────
function buildAgencyIcon(waiting: number, loadLevel: string, selected = false, dimmed = false): L.DivIcon {
  const color   = selected ? '#3B82F6' : (loadLevel === 'high' ? '#ef4444' : loadLevel === 'medium' ? '#f59e0b' : '#22c55e');
  const size    = selected ? 50 : 44;
  const opacity = dimmed ? 0.35 : 1;
  const ring    = selected ? `<circle cx="22" cy="21" r="22" fill="none" stroke="#93C5FD" stroke-width="3" opacity="0.7"/>` : '';
  const label   = waiting > 99 ? '99+' : String(waiting);
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size * 1.23}" viewBox="0 0 44 54" style="opacity:${opacity}">
    ${ring}
    <ellipse cx="22" cy="21" rx="18" ry="18" fill="${color}" stroke="white" stroke-width="${selected ? 3 : 2.5}"/>
    <polygon points="14,37 30,37 22,54" fill="${color}"/>
    <text x="22" y="27" text-anchor="middle" font-size="${label.length > 2 ? 10 : 13}"
      font-weight="bold" fill="white" font-family="Arial,sans-serif">${label}</text>
  </svg>`;
  return L.divIcon({ html: svg, className: '', iconSize: [size, size * 1.23] as any, iconAnchor: [size / 2, size * 1.23] as any });
}

function buildUserIcon(): L.DivIcon {
  return L.divIcon({
    html: `<div style="width:18px;height:18px;background:#3B82F6;border:3px solid white;border-radius:50%;box-shadow:0 2px 8px rgba(59,130,246,.7)"></div>`,
    className: '', iconSize: [18, 18] as any, iconAnchor: [9, 9] as any,
  });
}

// Các ký hiệu Unicode dùng trong step marker
const STEP_ARROWS: Record<string, string> = {
  'depart':       '▶',
  'arrive':       '⚑',
  'turn-left':    '↰',
  'turn-right':   '↱',
  'slight-left':  '↖',
  'slight-right': '↗',
  'straight':     '↑',
  'uturn':        '↺',
  'roundabout':   '↻',
};

function buildStepMarkerIcon(iconType: string, active = false): L.DivIcon {
  const arrow = STEP_ARROWS[iconType] ?? '↑';
  const bg    = active ? '#1e40af' : '#3b82f6';
  const html  = `<div style="width:22px;height:22px;background:${bg};border:2.5px solid white;`
    + `border-radius:50%;box-shadow:0 1px 5px rgba(0,0,0,.35);display:flex;align-items:center;`
    + `justify-content:center;color:white;font-size:12px;line-height:1">${arrow}</div>`;
  return L.divIcon({ html, className: '', iconSize: [22, 22] as any, iconAnchor: [11, 11] as any });
}

function buildEndpointIcon(label: string, color: string): L.DivIcon {
  const html = `<div style="width:28px;height:28px;background:${color};border:3px solid white;`
    + `border-radius:50%;box-shadow:0 2px 8px rgba(0,0,0,.3);display:flex;align-items:center;`
    + `justify-content:center;color:white;font-weight:bold;font-size:13px;font-family:Arial">${label}</div>`;
  return L.divIcon({ html, className: '', iconSize: [28, 28] as any, iconAnchor: [14, 14] as any });
}

const fmtDist = (d?: number | null) =>
  !d ? 'N/A' : d < 1 ? `${Math.round(d * 1000)} m` : `${d.toFixed(1)} km`;

/** Haversine km — fallback tính khoảng cách phía client khi backend không trả
 *  (chế độ xem theo tỉnh không gửi lat/lng lên server). */
const haversineKm = (lat1: number, lng1: number, lat2: number, lng2: number) => {
  const rad = (deg: number) => deg * (Math.PI / 180);
  const dLat = rad(lat2 - lat1), dLng = rad(lng2 - lng1);
  const a = Math.sin(dLat / 2) ** 2 +
    Math.cos(rad(lat1)) * Math.cos(rad(lat2)) * Math.sin(dLng / 2) ** 2;
  return 6371 * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
};

// ── Component ─────────────────────────────────────────────────────────────────
export function MapScreen({ onNavigate }: MapScreenProps) {
  // Map refs
  const mapRef          = useRef<HTMLDivElement>(null);
  const mapInstance     = useRef<L.Map | null>(null);
  const markersMap      = useRef<Map<string, L.Marker>>(new Map());
  const userMarkerRef   = useRef<L.Marker | null>(null);
  const routeLayerRef   = useRef<L.FeatureGroup | null>(null);
  const boundaryLayerRef = useRef<L.GeoJSON | null>(null);
  const stepMarkersRef  = useRef<L.Marker[]>([]);
  const acTimer         = useRef<ReturnType<typeof setTimeout> | null>(null);
  const smartResultsRef = useRef<HTMLDivElement>(null);
  const loadSeqRef      = useRef(0);
  const [mapReady, setMapReady] = useState(false);

  // Data
  const [offices,   setOffices]   = useState<PublicService[]>([]);
  const [loading,   setLoading]   = useState(true);
  const [queueData, setQueueData] = useState<Record<string, AgencyQueueStatus>>({});

  // Location
  const [userLocation,    setUserLocation]    = useState<{ lat: number; lng: number } | null>(null);
  const [locationLoading, setLocationLoading] = useState(false);

  // Khoảng cách: ưu tiên backend trả; thiếu thì tự tính từ vị trí người dùng.
  // null = không xác định được (chưa bật định vị) → nơi render tự ẩn.
  const officeDistance = useCallback((o: { distance?: number | null; latitude?: number | null; longitude?: number | null }): number | null => {
    if (o.distance != null) return o.distance;
    if (!userLocation || o.latitude == null || o.longitude == null) return null;
    return haversineKm(userLocation.lat, userLocation.lng, Number(o.latitude), Number(o.longitude));
  }, [userLocation]);

  // Filters
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [provinces,        setProvinces]        = useState<AdminDivision[]>([]);
  const [selectedProvince, setSelectedProvince] = useState('all'); // tên tỉnh (khớp cột province)
  const [selectedDistrict, setSelectedDistrict] = useState('all');
  const [selectedWard,     setSelectedWard]     = useState('all');
  const [showBoundary,     setShowBoundary]     = useState(false);

  // Search
  const [searchQuery,    setSearchQuery]    = useState('');
  const [suggestions,    setSuggestions]    = useState<PublicService[]>([]);
  const [showSuggestions,setShowSuggestions]= useState(false);
  const [searchLoading,  setSearchLoading]  = useState(false);

  // Sidebar tabs
  const [sidebarTab, setSidebarTab] = useState<'map' | 'smart'>('map');

  // Selected office + detail
  const [selectedOffice, setSelectedOffice] = useState<PublicService | null>(null);
  const [showDetail,     setShowDetail]     = useState(false);

  // Directions
  const [directionsInfo,     setDirectionsInfo]     = useState<DirectionsResult | null>(null);
  const [directionsLoading,  setDirectionsLoading]  = useState(false);
  const [dirMode,            setDirMode]            = useState<'driving' | 'walking' | 'cycling'>('driving');
  const [directionsMode,     setDirectionsMode]     = useState(false);
  const [activeStep,         setActiveStep]         = useState(-1);

  // Smart route
  const [smartService,  setSmartService]  = useState('all');
  const [smartMode,     setSmartMode]     = useState<'driving' | 'walking' | 'cycling'>('driving');
  const [smartResults,  setSmartResults]  = useState<SmartRecommendation[]>([]);
  const [smartLoading,  setSmartLoading]  = useState(false);
  const [smartError,    setSmartError]    = useState('');
  const [smartSearched, setSmartSearched] = useState(false);

  // ── Init Leaflet ─────────────────────────────────────────────────────────────
  useEffect(() => {
    if (!mapRef.current || mapInstance.current) return;
    const map = L.map(mapRef.current, {
      center: [DEFAULT_LAT, DEFAULT_LNG], zoom: DEFAULT_ZOOM, zoomControl: false,
    });
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
      maxZoom: 19,
    }).addTo(map);
    mapInstance.current = map;
    setMapReady(true);
    return () => { map.remove(); mapInstance.current = null; };
  }, []);

  // ── User marker ───────────────────────────────────────────────────────────────
  useEffect(() => {
    if (!mapInstance.current || !userLocation) return;
    const ll: L.LatLngExpression = [userLocation.lat, userLocation.lng];
    if (userMarkerRef.current) { userMarkerRef.current.setLatLng(ll); }
    else {
      userMarkerRef.current = L.marker(ll, { icon: buildUserIcon(), zIndexOffset: 1000 })
        .bindPopup('Vị trí của bạn').addTo(mapInstance.current);
    }
    mapInstance.current.setView(ll, mapInstance.current.getZoom());
  }, [userLocation]);

  // ── Danh sách quận/huyện (từ chính data cơ quan) để lọc theo địa bàn ──────────
  const districtOptions = Array.from(
    new Set(offices.map(o => o.district).filter((d): d is string => !!d))
  ).sort();

  // Xã/phường (2025) trong phạm vi huyện đang chọn
  const wardOptions = Array.from(
    new Set(
      offices
        .filter(o => selectedDistrict === 'all' || o.district === selectedDistrict)
        .map(o => o.ward)
        .filter((w): w is string => !!w)
    )
  ).sort();

  // Huyện/xã đang chọn có thể biến mất khỏi options khi offices đổi (đổi chip
  // category, đổi bán kính...) → tự trả về 'all' thay vì kẹt filter 0 kết quả
  useEffect(() => {
    if (selectedDistrict !== 'all' && !districtOptions.includes(selectedDistrict)) {
      setSelectedDistrict('all');
    }
    if (selectedWard !== 'all' && !wardOptions.includes(selectedWard)) {
      setSelectedWard('all');
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [offices, selectedDistrict, selectedWard]);

  // ── Filtered offices (search + lọc theo địa bàn: huyện + xã) ──────────────────
  const q = searchQuery.trim().toLowerCase();
  const filteredOffices = offices.filter(o => {
    if (selectedDistrict !== 'all' && (o.district || '') !== selectedDistrict) return false;
    if (selectedWard !== 'all' && (o.ward || '') !== selectedWard) return false;
    if (q) {
      return o.name.toLowerCase().includes(q) || (o.address ?? '').toLowerCase().includes(q);
    }
    return true;
  });

  // ── Agency markers — update icons based on search/selected state ──────────────
  useEffect(() => {
    if (!mapInstance.current || !mapReady) return;
    // Chỉ hiển thị marker của các cơ quan khớp bộ lọc (địa bàn + tìm kiếm)
    const shownIds = new Set(filteredOffices.map(o => o.id));

    // Remove markers no longer matching filter
    markersMap.current.forEach((m, id) => {
      if (!shownIds.has(id)) { m.remove(); markersMap.current.delete(id); }
    });

    filteredOffices.forEach(office => {
      if (!office.latitude || !office.longitude) return;
      const qs        = queueData[office.id];
      const waiting   = qs?.totalWaiting ?? 0;
      const loadLevel = qs?.loadLevel ?? 'low';
      const isSelected = selectedOffice?.id === office.id;
      // Chỉ setIcon khi trạng thái đổi — tránh thay 1000 DOM node mỗi lần poll
      const iconKey = `${waiting}|${loadLevel}|${isSelected}`;

      const existing = markersMap.current.get(office.id);
      if (existing) {
        if ((existing as any)._iconKey !== iconKey) {
          existing.setIcon(buildAgencyIcon(waiting, loadLevel, isSelected, false));
          (existing as any)._iconKey = iconKey;
        }
        return;
      }

      const marker = L.marker([office.latitude, office.longitude], {
        icon: buildAgencyIcon(waiting, loadLevel, isSelected, false),
      }).addTo(mapInstance.current!);
      (marker as any)._iconKey = iconKey;
      marker.on('click', () => handleSelectOffice(office));
      markersMap.current.set(office.id, marker);
    });
  }, [offices, queueData, mapReady, selectedOffice?.id, searchQuery, selectedProvince, selectedDistrict, selectedWard]);

  // ── Fit-bounds khi ĐỔI bộ lọc (tách khỏi effect marker: không chạy lại theo
  //    poll queueData 30s → không giật viewport; không fit khi đang tải dở) ─────
  useEffect(() => {
    if (!mapInstance.current || !mapReady || loading) return;
    const filtering = searchQuery.trim().length > 0 || selectedProvince !== 'all'
      || selectedDistrict !== 'all' || selectedWard !== 'all';
    if (!filtering || filteredOffices.length === 0) return;
    const pts = filteredOffices
      .filter(o => o.latitude && o.longitude)
      .map(o => [o.latitude!, o.longitude!] as L.LatLngExpression);
    if (pts.length) {
      mapInstance.current.fitBounds(L.latLngBounds(pts), { padding: [50, 50], maxZoom: 15 });
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [offices, loading, mapReady, searchQuery, selectedProvince, selectedDistrict, selectedWard]);

  // ── Lớp ranh giới hành chính (GeoJSON tỉnh Thanh Hóa) — bật/tắt ──────────────
  useEffect(() => {
    if (!mapInstance.current || !mapReady) return;
    if (showBoundary) {
      if (boundaryLayerRef.current) {
        boundaryLayerRef.current.addTo(mapInstance.current);
      } else {
        fetch('/thanhhoa-province.geojson')
          .then(r => r.json())
          .then(gj => {
            if (!mapInstance.current || !showBoundary) return;
            boundaryLayerRef.current = L.geoJSON(gj, {
              style: { color: '#2563eb', weight: 2, fillColor: '#3b82f6', fillOpacity: 0.06, dashArray: '5 4' },
              interactive: false,
            }).addTo(mapInstance.current);
          })
          .catch(() => {});
      }
    } else if (boundaryLayerRef.current) {
      boundaryLayerRef.current.remove();
    }
  }, [showBoundary, mapReady]);

  // ── Route rendering ───────────────────────────────────────────────────────────
  useEffect(() => {
    // Dọn lớp route cũ
    if (routeLayerRef.current) { routeLayerRef.current.remove(); routeLayerRef.current = null; }
    stepMarkersRef.current = [];

    if (!mapInstance.current || !directionsInfo?.coordinates?.length) return;

    const map    = mapInstance.current;
    const coords = directionsInfo.coordinates as L.LatLngExpression[];

    // Màu theo phương tiện
    const modeColor: Record<string, string> = {
      driving: '#3B82F6',
      walking: '#10b981',
      cycling: '#f59e0b',
    };
    const routeColor = modeColor[dirMode] ?? '#3B82F6';

    // FeatureGroup chứa toàn bộ route layer
    const fg = L.featureGroup().addTo(map);
    routeLayerRef.current = fg;

    // 1. Shadow (lớp bóng phía sau)
    L.polyline(coords, {
      color: '#000', weight: 10, opacity: 0.10, lineCap: 'round', lineJoin: 'round',
    }).addTo(fg);

    // 2. Viền trắng (tạo độ nổi)
    L.polyline(coords, {
      color: '#fff', weight: 7, opacity: 0.80, lineCap: 'round', lineJoin: 'round',
    }).addTo(fg);

    // 3. Đường chính (màu phương tiện)
    L.polyline(coords, {
      color: routeColor, weight: 5, opacity: 0.95, lineCap: 'round', lineJoin: 'round',
    }).addTo(fg);

    // 4. Nét đứt động chạy trên đường (hiệu ứng chuyển động)
    L.polyline(coords, {
      color: '#fff', weight: 3, opacity: 0.45,
      lineCap: 'round', lineJoin: 'round',
      dashArray: '2 14', dashOffset: '0',
    }).addTo(fg);

    // 5. Start marker (A — xanh lá)
    L.marker(coords[0], {
      icon: buildEndpointIcon('A', '#22c55e'),
      zIndexOffset: 900,
    }).bindTooltip('Vị trí của bạn', { permanent: false }).addTo(fg);

    // 6. End marker (B — đỏ)
    L.marker(coords[coords.length - 1], {
      icon: buildEndpointIcon('B', '#ef4444'),
      zIndexOffset: 900,
    }).bindTooltip('Điểm đến', { permanent: false }).addTo(fg);

    // 7. Step markers — chỉ hiển thị các điểm rẽ thực sự (bỏ go-straight)
    const SKIP_ON_MAP = new Set(['depart', 'arrive', 'continue', 'new name',
                                  'notification', 'use lane']);
    if (directionsInfo.steps?.length) {
      directionsInfo.steps.forEach((step, idx) => {
        if (!step.location) return;
        if (SKIP_ON_MAP.has(step.maneuverType)) return;

        const marker = L.marker(step.location as L.LatLngExpression, {
          icon: buildStepMarkerIcon(step.iconType, false),
          zIndexOffset: 800,
        })
          .bindTooltip(
            `<b>${idx + 1}.</b> ${step.instruction}<br/><small>${step.distance}</small>`,
            { permanent: false, direction: 'top', className: 'leaflet-route-tooltip' },
          )
          .addTo(fg);
        stepMarkersRef.current.push(marker);
      });
    }

    // Fit bounds
    map.fitBounds(fg.getBounds(), { padding: [80, 80], maxZoom: 16 });
    setActiveStep(-1);
  }, [directionsInfo, dirMode]);

  // ── Queue polling ─────────────────────────────────────────────────────────────
  useEffect(() => {
    const fetch = async () => { try { setQueueData(await getMapOverview()); } catch {} };
    fetch();
    const id = setInterval(fetch, 30_000);
    return () => clearInterval(id);
  }, []);

  // ── Danh sách 34 tỉnh (mô hình 2025) cho bộ lọc toàn quốc ────────────────────
  useEffect(() => {
    adminDivisionsAPI.provinces().then(setProvinces).catch(() => {});
  }, []);

  // ── Load services ─────────────────────────────────────────────────────────────
  // Debounce nhẹ để gộp các lần đổi filter liên tiếp — chỉ request cuối được chạy
  useEffect(() => {
    const t = setTimeout(loadServices, 250);
    return () => clearTimeout(t);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedCategory, selectedProvince, userLocation]);

  const loadServices = async () => {
    // Sequence guard: response cũ về muộn không được đè dữ liệu mode hiện tại
    const seq = ++loadSeqRef.current;
    setLoading(true);
    try {
      const category = selectedCategory === 'all' ? undefined : selectedCategory;
      // Mặc định: chỉ cơ quan trong 5km quanh vị trí; chọn tỉnh = toàn tỉnh.
      // Tìm kiếm không bị giới hạn — handleSearchInput quét toàn bộ DB.
      const loc = userLocation ?? { lat: DEFAULT_LAT, lng: DEFAULT_LNG };
      const res = selectedProvince !== 'all'
        ? await servicesAPI.getAll(category, undefined, selectedProvince, undefined, undefined, 5000)
        : await servicesAPI.getNearby(loc.lat, loc.lng, NEARBY_RADIUS_KM, category, undefined, 500);
      if (seq === loadSeqRef.current && res.success) setOffices(res.data.services);
    } catch {
      // lỗi mạng: giữ dữ liệu cũ, không treo loading
    } finally {
      if (seq === loadSeqRef.current) setLoading(false);
    }
  };

  // ── Geolocation ───────────────────────────────────────────────────────────────
  const getCurrentLocation = useCallback(() => {
    setLocationLoading(true);
    if (!navigator.geolocation) {
      setUserLocation({ lat: DEFAULT_LAT, lng: DEFAULT_LNG }); setLocationLoading(false); return;
    }
    navigator.geolocation.getCurrentPosition(
      pos => { setUserLocation({ lat: pos.coords.latitude, lng: pos.coords.longitude }); setLocationLoading(false); },
      ()  => { setUserLocation({ lat: DEFAULT_LAT, lng: DEFAULT_LNG }); setLocationLoading(false); },
    );
  }, []);

  // ── Search + agency suggestions (từ DB, không giới hạn radius) ──────────────
  const handleSearchInput = useCallback((value: string) => {
    setSearchQuery(value);
    if (acTimer.current) clearTimeout(acTimer.current);
    if (!value.trim() || value.length < 2) {
      setSuggestions([]); setShowSuggestions(false); return;
    }
    acTimer.current = setTimeout(async () => {
      try {
        setSearchLoading(true);
        // Tìm TOÀN BẢN ĐỒ (không truyền lat/lng — backend sẽ cắt cứng 100km
        // quanh user nếu truyền); đang duyệt tỉnh thì scope theo tỉnh
        const res = await servicesAPI.search(
          value, undefined, undefined,
          selectedProvince !== 'all' ? selectedProvince : undefined,
        );
        if (res.success) {
          const results = res.data.services.slice(0, 8);
          setSuggestions(results);
          setShowSuggestions(results.length > 0);
        }
      } catch {} finally { setSearchLoading(false); }
    }, 300);
  }, [userLocation, selectedProvince]);

  const selectSuggestion = useCallback((office: PublicService) => {
    setSearchQuery(office.name);
    setSuggestions([]); setShowSuggestions(false);
    // Thêm vào offices nếu nằm ngoài radius (để marker xuất hiện trên map)
    setOffices(prev => prev.find(o => o.id === office.id) ? prev : [...prev, office]);
    handleSelectOffice(office);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // ── Select / view office ──────────────────────────────────────────────────────
  const handleSelectOffice = async (office: PublicService) => {
    setSelectedOffice(office);
    setShowDetail(true);
    setDirectionsMode(false);
    setDirectionsInfo(null);
    if (routeLayerRef.current) { routeLayerRef.current.remove(); routeLayerRef.current = null; }

    if (mapInstance.current && office.latitude && office.longitude) {
      mapInstance.current.panTo([office.latitude, office.longitude], { animate: true });
    }

    // Fetch detail
    try {
      const res = await servicesAPI.getById(office.id, userLocation?.lat ?? DEFAULT_LAT, userLocation?.lng ?? DEFAULT_LNG);
      if (res.success) setSelectedOffice(res.data.service);
    } catch {}
  };

  const closeDetail = () => {
    setShowDetail(false); setSelectedOffice(null);
    setDirectionsMode(false); setDirectionsInfo(null);
    if (routeLayerRef.current) { routeLayerRef.current.remove(); routeLayerRef.current = null; }
    setActiveStep(-1);
  };

  // ── Directions ────────────────────────────────────────────────────────────────
  const fetchDirections = async (office: PublicService, mode: typeof dirMode = dirMode) => {
    if (!office.latitude || !office.longitude) return;
    setDirectionsLoading(true); setDirectionsInfo(null);
    try {
      const origin = userLocation ?? { lat: DEFAULT_LAT, lng: DEFAULT_LNG };
      const res = await mapAPI.getDirections(origin, { lat: office.latitude, lng: office.longitude }, mode);
      if (res.success) setDirectionsInfo(res.data);
    } finally { setDirectionsLoading(false); }
  };

  const enterDirectionsMode = (office: PublicService) => {
    setDirectionsMode(true);
    fetchDirections(office);
  };

  // ── Smart Route ───────────────────────────────────────────────────────────────
  const handleSmartRoute = async () => {
    const loc = userLocation ?? { lat: DEFAULT_LAT, lng: DEFAULT_LNG };
    setSmartLoading(true); setSmartError(''); setSmartSearched(false);
    try {
      const res = await mapAPI.smartRoute(loc.lat, loc.lng, smartService, smartMode);
      if (res.success) {
        setSmartResults(res.data.recommendations); setSmartSearched(true);
        if (!res.data.recommendations.length) setSmartError(res.data.message ?? 'Không tìm thấy cơ quan phù hợp.');
        // Bảng điều khiển cao hơn khung nhìn trên màn thấp — cuộn tới kết quả
        else setTimeout(() => smartResultsRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' }), 80);
      }
    } catch (e: any) { setSmartError(e.message ?? 'Lỗi khi tìm gợi ý.'); }
    finally { setSmartLoading(false); }
  };

  const qs = selectedOffice ? queueData[selectedOffice.id] : null;

  // ── Render ────────────────────────────────────────────────────────────────────
  return (
    <div className="h-screen flex overflow-hidden bg-gray-100" style={{ fontFamily: "'Manrope', sans-serif" }}>

      {/* ════════════════════ SIDEBAR ════════════════════ */}
      <aside className="w-[360px] flex-shrink-0 bg-white shadow-2xl z-30 flex flex-col h-full border-r border-gray-200">

        {/* ── Brand header ── */}
        <div className="px-5 py-4 border-b border-gray-100 flex items-center justify-between flex-shrink-0">
          <button onClick={() => onNavigate('home')} className="text-primary font-extrabold text-lg tracking-tight">
            Cổng Dịch vụ Công
          </button>
          <div className="flex items-center gap-2">
            <button onClick={() => onNavigate('notification')} className="p-1.5 text-gray-500 hover:text-primary hover:bg-gray-100 rounded-lg transition-colors">
              <span className="material-symbols-outlined text-[20px]">notifications</span>
            </button>
            <button className="p-1.5 text-gray-500 hover:text-primary hover:bg-gray-100 rounded-lg transition-colors">
              <span className="material-symbols-outlined text-[20px]">account_circle</span>
            </button>
          </div>
        </div>

        {/* ── Tab bar ── */}
        <div className="flex border-b border-gray-100 flex-shrink-0">
          {[
            { key: 'map' as const,   icon: 'map',          label: 'Bản đồ' },
            { key: 'smart' as const, icon: 'auto_awesome', label: 'Gợi ý AI' },
          ].map(({ key, icon, label }) => (
            <button key={key} onClick={() => setSidebarTab(key)}
              className={`flex-1 py-3 text-xs font-bold uppercase tracking-widest flex items-center justify-center gap-1.5 border-b-2 transition-colors ${
                sidebarTab === key
                  ? 'border-primary text-primary bg-blue-50/50'
                  : 'border-transparent text-gray-400 hover:text-gray-700'
              }`}>
              <span className="material-symbols-outlined text-[16px]">{icon}</span>
              {label}
            </button>
          ))}
        </div>

        {/* ════ TAB: BẢN ĐỒ ════ */}
        {sidebarTab === 'map' && (
          <div className="flex flex-col flex-1 overflow-hidden">

            {/* ── Directions mode ── */}
            {directionsMode && selectedOffice ? (
              <div className="flex flex-col flex-1 overflow-hidden">
                {/* Header */}
                <div className="px-4 py-3 border-b border-gray-100 bg-blue-50 flex-shrink-0">
                  <div className="flex items-center gap-2 mb-3">
                    <button onClick={() => { setDirectionsMode(false); setDirectionsInfo(null); if (routeLayerRef.current) { routeLayerRef.current.remove(); routeLayerRef.current = null; } setActiveStep(-1); }}
                      className="p-1.5 rounded-lg hover:bg-white text-gray-600 transition-colors">
                      <ArrowLeft className="w-4 h-4" />
                    </button>
                    <div className="min-w-0 flex-1">
                      <p className="text-[10px] text-gray-500 uppercase font-bold">Chỉ đường đến</p>
                      <p className="text-sm font-bold text-gray-800 truncate">{selectedOffice.name}</p>
                    </div>
                  </div>

                  {/* Transport mode */}
                  <div className="flex gap-2">
                    {([
                      { id: 'driving' as const, Icon: Car,           label: 'Xe' },
                      { id: 'walking' as const, Icon: PersonStanding, label: 'Đi bộ' },
                      { id: 'cycling' as const, Icon: Bike,           label: 'Đạp xe' },
                    ]).map(({ id, Icon, label }) => (
                      <button key={id}
                        onClick={() => { setDirMode(id); fetchDirections(selectedOffice, id); }}
                        className={`flex-1 py-2.5 rounded-xl text-[11px] font-bold flex flex-col items-center gap-1 transition-all ${
                          dirMode === id ? 'bg-blue-600 text-white shadow-md' : 'bg-white text-gray-600 hover:bg-blue-100'
                        }`}>
                        <Icon className="w-4 h-4" />{label}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Route info */}
                <div className="p-4 flex-shrink-0 border-b border-gray-100">
                  {directionsLoading ? (
                    <div className="flex items-center gap-2 py-3">
                      <Loader2 className="w-5 h-5 animate-spin text-blue-600" />
                      <span className="text-sm text-gray-500">Đang tìm đường...</span>
                    </div>
                  ) : directionsInfo ? (
                    <>
                      <div className="flex items-end gap-3 mb-3">
                        <div>
                          <p className="text-3xl font-black text-blue-600">{directionsInfo.duration.text}</p>
                          <p className="text-sm text-gray-500 mt-0.5">
                            {directionsInfo.distance.text}
                            {directionsInfo.steps && directionsInfo.steps.length > 0 && (
                              <span className="ml-2 text-[11px] bg-blue-50 text-blue-600 font-bold px-1.5 py-0.5 rounded-full">
                                {directionsInfo.steps.length} bước
                              </span>
                            )}
                          </p>
                        </div>
                      </div>
                      <div className="flex gap-2">
                        <button onClick={() => directionsInfo.googleMapsUrl && window.open(directionsInfo.googleMapsUrl, '_blank')}
                          className="flex-1 py-2.5 bg-blue-600 text-white rounded-xl text-xs font-bold flex items-center justify-center gap-1.5 hover:bg-blue-700 transition-colors shadow-md">
                          <Navigation className="w-3.5 h-3.5" /> Google Maps
                        </button>
                        <button onClick={() => directionsInfo.osmUrl && window.open(directionsInfo.osmUrl, '_blank')}
                          className="flex-1 py-2.5 bg-gray-100 text-gray-700 rounded-xl text-xs font-bold flex items-center justify-center gap-1.5 hover:bg-gray-200 transition-colors">
                          <Route className="w-3.5 h-3.5" /> Mở OSM
                        </button>
                      </div>
                    </>
                  ) : (
                    <p className="text-sm text-gray-400 py-2">Không tìm được đường đi</p>
                  )}
                </div>

                {/* ── Turn-by-turn steps ─────────────────────────────────── */}
                {directionsInfo?.steps && directionsInfo.steps.length > 0 ? (
                  <div className="flex-1 overflow-y-auto min-h-0">
                    <p className="px-4 pt-2.5 pb-1 text-[10px] font-bold text-gray-400 uppercase tracking-widest flex items-center gap-1.5">
                      <Route className="w-3 h-3" /> Hướng dẫn chi tiết
                    </p>
                    {directionsInfo.steps.map((step, i) => {
                      const arrow = STEP_ARROWS[step.iconType] ?? '↑';
                      const isArrive  = step.maneuverType === 'arrive';
                      const isDepart  = step.maneuverType === 'depart';
                      const isActive  = activeStep === i;
                      return (
                        <button
                          key={i}
                          onClick={() => {
                            setActiveStep(i);
                            if (step.location && mapInstance.current) {
                              mapInstance.current.setView(
                                step.location as L.LatLngExpression, 17, { animate: true });
                            }
                          }}
                          className={`w-full text-left flex items-start gap-3 px-4 py-2.5 border-b border-gray-50 transition-colors last:border-0 ${
                            isActive  ? 'bg-blue-50 border-l-4 border-l-blue-500' :
                            isArrive  ? 'bg-red-50/40' :
                            'hover:bg-gray-50'
                          }`}
                        >
                          {/* Icon */}
                          <div className={`w-7 h-7 rounded-full flex-shrink-0 flex items-center justify-center text-sm mt-0.5 ${
                            isArrive ? 'bg-red-100 text-red-600' :
                            isDepart ? 'bg-green-100 text-green-600' :
                            isActive ? 'bg-blue-600 text-white' :
                            'bg-blue-100 text-blue-700'
                          }`}>
                            {arrow}
                          </div>
                          {/* Text */}
                          <div className="min-w-0 flex-1">
                            <p className="text-xs font-semibold text-gray-800 leading-snug">{step.instruction}</p>
                            {step.roadName && step.roadName !== '(unnamed road)' && step.roadName !== '' && (
                              <p className="text-[10px] text-gray-400 mt-0.5 truncate">{step.roadName}</p>
                            )}
                          </div>
                          {/* Distance */}
                          <span className="text-[10px] font-bold text-gray-400 flex-shrink-0 mt-1 tabular-nums">
                            {step.distance}
                          </span>
                        </button>
                      );
                    })}
                  </div>
                ) : (
                  <div className="flex-1" />
                )}

                {/* Book */}
                <div className="p-4 flex-shrink-0 border-t border-gray-100">
                  <button onClick={() => onNavigate('appointment', { defaultAgencyId: selectedOffice.id })}
                    className="w-full py-3.5 bg-primary text-white rounded-xl font-bold text-sm flex items-center justify-center gap-2 hover:opacity-90 transition-opacity shadow-lg">
                    <CalendarDays className="w-4 h-4" /> Đặt lịch hẹn
                  </button>
                </div>
              </div>

            /* ── Detail panel ── */
            ) : showDetail && selectedOffice ? (
              <div className="flex flex-col flex-1 overflow-hidden">
                {/* Header */}
                <div className="px-5 py-4 border-b border-gray-100 flex-shrink-0">
                  <div className="flex items-start gap-3">
                    <button onClick={closeDetail}
                      className="p-1.5 rounded-lg hover:bg-gray-100 text-gray-500 flex-shrink-0 mt-0.5 transition-colors">
                      <ArrowLeft className="w-4 h-4" />
                    </button>
                    <div className="min-w-0 flex-1">
                      <h2 className="text-base font-extrabold text-gray-900 leading-tight">{selectedOffice.name}</h2>
                      <p className="text-xs text-gray-500 mt-1 flex items-start gap-1">
                        <MapPin className="w-3 h-3 flex-shrink-0 mt-0.5 text-primary" />
                        {selectedOffice.address}
                      </p>
                    </div>
                  </div>
                </div>

                <div className="flex-1 overflow-y-auto">
                  {/* Actions */}
                  <div className="px-5 py-4 flex gap-3 border-b border-gray-100">
                    <button onClick={() => enterDirectionsMode(selectedOffice)}
                      className="flex-1 py-3 bg-blue-600 text-white rounded-2xl text-sm font-bold flex items-center justify-center gap-1.5 hover:bg-blue-700 transition-colors shadow-md">
                      <Navigation className="w-4 h-4" /> Chỉ đường
                    </button>
                    <button onClick={() => onNavigate('appointment', { defaultAgencyId: selectedOffice.id })}
                      className="flex-1 py-3 bg-primary text-white rounded-2xl text-sm font-bold flex items-center justify-center gap-1.5 hover:opacity-90 transition-opacity shadow-md">
                      <CalendarDays className="w-4 h-4" /> Đặt lịch
                    </button>
                  </div>

                  {/* Queue stats */}
                  {qs && (
                    <div className="px-5 py-4 border-b border-gray-100">
                      <p className="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-3">Tình trạng hàng chờ</p>
                      <div className="grid grid-cols-3 gap-3">
                        {[
                          { label: 'Đang chờ', val: qs.totalWaiting, color: LOAD_COLOR[qs.loadLevel] },
                          { label: 'Phục vụ',  val: qs.totalServing, color: '#22c55e' },
                          { label: 'Tải',      val: LOAD_LABEL[qs.loadLevel], color: LOAD_COLOR[qs.loadLevel] },
                        ].map(({ label, val, color }) => (
                          <div key={label} className="bg-gray-50 rounded-xl p-3 text-center">
                            <p className="text-[10px] text-gray-400 mb-1">{label}</p>
                            <p className="text-base font-black" style={{ color }}>{val}</p>
                          </div>
                        ))}
                      </div>
                      <div className="mt-3">
                        <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                          <div className={`h-full rounded-full transition-all ${LOAD_BG[qs.loadLevel]}`}
                            style={{ width: `${Math.max(6, Math.min(100, Math.round((qs.totalWaiting / 30) * 100)))}%` }} />
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Info */}
                  <div className="px-5 py-4 space-y-3">
                    {selectedOffice.phone && (
                      <a href={`tel:${selectedOffice.phone}`}
                        className="flex items-center gap-3 py-2.5 px-3 bg-gray-50 rounded-xl hover:bg-blue-50 transition-colors">
                        <Phone className="w-4 h-4 text-primary flex-shrink-0" />
                        <span className="text-sm text-blue-600 font-medium">{selectedOffice.phone}</span>
                      </a>
                    )}
                    {selectedOffice.website && (
                      <a href={selectedOffice.website} target="_blank" rel="noopener noreferrer"
                        className="flex items-center gap-3 py-2.5 px-3 bg-gray-50 rounded-xl hover:bg-blue-50 transition-colors">
                        <Globe className="w-4 h-4 text-primary flex-shrink-0" />
                        <span className="text-sm text-blue-600 font-medium truncate">{selectedOffice.website}</span>
                      </a>
                    )}
                    {selectedOffice.rating != null && selectedOffice.rating > 0 && (
                      <div className="flex items-center gap-2 px-3 py-2">
                        <Star className="w-4 h-4 text-yellow-400 fill-yellow-400" />
                        <span className="text-sm font-bold text-gray-700">{selectedOffice.rating.toFixed(1)}</span>
                      </div>
                    )}
                    {officeDistance(selectedOffice) != null && (
                      <div className="px-3 py-2">
                        <p className="text-[10px] text-gray-400 uppercase font-bold mb-1">Khoảng cách</p>
                        <p className="text-sm font-bold text-gray-700">{fmtDist(officeDistance(selectedOffice))}</p>
                      </div>
                    )}
                  </div>
                </div>
              </div>

            /* ── Normal list ── */
            ) : (
              <div className="flex flex-col flex-1 overflow-hidden">
                {/* Search bar */}
                <div className="px-4 pt-4 pb-3 flex-shrink-0">
                  <div className="relative">
                    <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 w-4 h-4" />
                    <input
                      value={searchQuery}
                      onChange={e => handleSearchInput(e.target.value)}
                      onFocus={() => suggestions.length && setShowSuggestions(true)}
                      onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
                      placeholder="Tìm tên cơ quan, địa chỉ..."
                      className="w-full h-11 bg-gray-50 border border-gray-200 rounded-2xl pl-11 pr-10 text-sm font-medium text-gray-800 placeholder-gray-400 outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition"
                    />
                    {/* Spinner hoặc nút xóa */}
                    {searchLoading ? (
                      <Loader2 className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 animate-spin text-primary" />
                    ) : searchQuery ? (
                      <button onClick={() => { setSearchQuery(''); setSuggestions([]); setShowSuggestions(false); }}
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-700">
                        <X className="w-4 h-4" />
                      </button>
                    ) : null}

                    {/* Agency suggestions dropdown */}
                    {showSuggestions && suggestions.length > 0 && (
                      <ul className="absolute top-full left-0 right-0 mt-1 bg-white rounded-2xl shadow-2xl border border-gray-100 z-50 overflow-hidden max-h-72 overflow-y-auto">
                        {/* Header */}
                        <li className="px-4 py-1.5 bg-gray-50 border-b border-gray-100">
                          <span className="text-[10px] font-bold text-gray-400 uppercase tracking-widest">
                            🏛 Cơ quan nhà nước · {suggestions.length} kết quả
                          </span>
                        </li>
                        {suggestions.map(office => {
                          const qs  = queueData[office.id];
                          const lv  = qs?.loadLevel ?? 'low';
                          const waiting = qs?.totalWaiting ?? 0;
                          const badgeBg   = lv === 'high' ? 'bg-red-100 text-red-600'
                                          : lv === 'medium' ? 'bg-amber-100 text-amber-700'
                                          : 'bg-green-100 text-green-700';
                          const badgeLabel = lv === 'high'   ? `${waiting} đông`
                                           : lv === 'medium' ? `${waiting} chờ`
                                           : waiting > 0     ? `${waiting} chờ` : 'Vắng';
                          return (
                            <li key={office.id} onMouseDown={() => selectSuggestion(office)}
                              className="px-4 py-3 cursor-pointer hover:bg-blue-50 flex items-center gap-3 transition-colors border-b border-gray-50 last:border-0 group">
                              {/* Icon */}
                              <div className="w-8 h-8 rounded-lg bg-blue-100 flex items-center justify-center flex-shrink-0 group-hover:bg-blue-200 transition-colors">
                                <MapPin className="w-4 h-4 text-primary" />
                              </div>
                              {/* Info */}
                              <div className="min-w-0 flex-1">
                                <p className="text-sm font-bold text-gray-800 truncate leading-tight">{office.name}</p>
                                <p className="text-xs text-gray-400 truncate mt-0.5">
                                  {office.address}
                                  {officeDistance(office) != null && (
                                    <span className="ml-1.5 font-semibold text-primary">· {fmtDist(officeDistance(office))}</span>
                                  )}
                                </p>
                              </div>
                              {/* Queue badge */}
                              <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full flex-shrink-0 ${badgeBg}`}>
                                {badgeLabel}
                              </span>
                            </li>
                          );
                        })}
                      </ul>
                    )}
                  </div>

                  {/* Search result count */}
                  {searchQuery.trim() && (
                    <p className="text-xs text-gray-500 mt-2 px-1">
                      Tìm thấy <span className="font-bold text-primary">{filteredOffices.length}</span> cơ quan
                      {filteredOffices.length > 0 && ' — đã đánh dấu trên bản đồ'}
                    </p>
                  )}
                </div>

                {/* Filters */}
                <div className="px-4 pb-3 space-y-3 flex-shrink-0 border-b border-gray-100">
                  {/* Tỉnh/thành (toàn quốc, mô hình 2025) */}
                  {provinces.length > 0 && (
                    <div className="flex items-center gap-2">
                      <Globe className="w-4 h-4 text-gray-400 shrink-0" />
                      <select
                        value={selectedProvince}
                        onChange={e => {
                          setSelectedProvince(e.target.value);
                          setSelectedDistrict('all');
                          setSelectedWard('all');
                          // Về "Quanh vị trí của tôi": trả viewport về quanh user
                          // (fitBounds chỉ chạy khi đang lọc — không tự recenter)
                          if (e.target.value === 'all' && mapInstance.current) {
                            const c = userLocation ?? { lat: DEFAULT_LAT, lng: DEFAULT_LNG };
                            mapInstance.current.setView([c.lat, c.lng], DEFAULT_ZOOM);
                          }
                        }}
                        className="flex-1 rounded-full border border-gray-200 bg-gray-50 px-3 py-1.5 text-xs font-semibold text-gray-700 focus:border-primary focus:outline-none"
                      >
                        <option value="all">Quanh tôi (5 km)</option>
                        {provinces.map(p => (
                          <option key={p.code} value={p.name}>{p.fullName || p.name}</option>
                        ))}
                      </select>
                    </div>
                  )}

                  {/* Category chips */}
                  <div className="flex flex-wrap gap-2">
                    {CATEGORY_CHIPS.map(({ key, label }) => (
                      <button key={key} onClick={() => setSelectedCategory(key)}
                        className={`px-3.5 py-1.5 rounded-full text-xs font-bold transition-all ${
                          selectedCategory === key
                            ? 'bg-primary text-white shadow-sm'
                            : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                        }`}>
                        {label}
                      </button>
                    ))}
                  </div>

                  {/* Lọc theo địa bàn: quận/huyện (mô hình cũ) + xã/phường (2025) */}
                  {(districtOptions.length > 0 || wardOptions.length > 0) && (
                    <div className="flex items-center gap-2">
                      <MapPin className="w-4 h-4 text-gray-400 shrink-0" />
                      {districtOptions.length > 0 && (
                        <select
                          value={selectedDistrict}
                          onChange={e => { setSelectedDistrict(e.target.value); setSelectedWard('all'); }}
                          className="flex-1 min-w-0 rounded-full border border-gray-200 bg-gray-50 px-3 py-1.5 text-xs font-semibold text-gray-700 focus:border-primary focus:outline-none"
                        >
                          <option value="all">Tất cả huyện ({offices.length})</option>
                          {districtOptions.map(d => (
                            <option key={d} value={d}>{d}</option>
                          ))}
                        </select>
                      )}
                      {wardOptions.length > 0 && (
                        <select
                          value={selectedWard}
                          onChange={e => setSelectedWard(e.target.value)}
                          className="flex-1 min-w-0 rounded-full border border-gray-200 bg-gray-50 px-3 py-1.5 text-xs font-semibold text-gray-700 focus:border-primary focus:outline-none"
                        >
                          <option value="all">Tất cả xã/phường</option>
                          {wardOptions.map(w => (
                            <option key={w} value={w}>{w}</option>
                          ))}
                        </select>
                      )}
                    </div>
                  )}

                  {/* Bật/tắt ranh giới hành chính tỉnh Thanh Hóa */}
                  <button
                    onClick={() => setShowBoundary(v => !v)}
                    className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-full text-xs font-bold transition-all w-fit ${
                      showBoundary ? 'bg-primary text-white shadow-sm' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                    }`}>
                    <MapPin className="w-3.5 h-3.5" />
                    {showBoundary ? 'Đang hiện ranh giới tỉnh' : 'Hiện ranh giới tỉnh'}
                  </button>
                </div>

                {/* Results */}
                <div className="flex-1 overflow-y-auto">
                  {loading ? (
                    <div className="flex justify-center items-center py-16">
                      <Loader2 className="w-6 h-6 animate-spin text-primary" />
                    </div>
                  ) : filteredOffices.length === 0 ? (
                    <div className="flex flex-col items-center py-12 text-center px-6">
                      <MapPin className="w-10 h-10 text-gray-300 mb-3" />
                      <p className="text-sm text-gray-500">
                        {searchQuery.trim()
                          ? `Không tìm thấy kết quả cho "${searchQuery}"`
                          : selectedProvince !== 'all'
                            ? `Chưa có dữ liệu cơ quan tại ${selectedProvince}`
                            : 'Chưa có dữ liệu cơ quan'}
                      </p>
                    </div>
                  ) : (
                    // Cap danh sách render 150 dòng — toàn quốc 3.400+ cơ quan,
                    // đổ hết vào DOM sẽ lag; marker trên map vẫn hiện đầy đủ
                    filteredOffices.slice(0, 150).map(office => {
                      const q  = queueData[office.id];
                      const lc = LOAD_COLOR[q?.loadLevel ?? 'low'];
                      const isSelected = selectedOffice?.id === office.id;
                      return (
                        <button
                          key={office.id}
                          onClick={() => handleSelectOffice(office)}
                          className={`w-full text-left px-5 py-4 border-b border-gray-50 transition-colors hover:bg-gray-50 ${
                            isSelected ? 'bg-blue-50 border-l-4 border-l-blue-500' : ''
                          }`}
                        >
                          <div className="flex items-start justify-between gap-2 mb-1.5">
                            <p className={`text-sm font-bold leading-tight ${isSelected ? 'text-blue-700' : 'text-gray-800'}`}>
                              {office.name}
                            </p>
                            {officeDistance(office) != null && (
                              <span className="text-[11px] font-extrabold text-primary bg-blue-50 px-2 py-0.5 rounded-full flex-shrink-0">
                                {fmtDist(officeDistance(office))}
                              </span>
                            )}
                          </div>

                          <p className="text-xs text-gray-500 flex items-start gap-1 mb-2">
                            <MapPin className="w-3 h-3 flex-shrink-0 mt-0.5 text-gray-400" />
                            {office.address}
                          </p>

                          <div className="flex items-center gap-3">
                            {q ? (
                              <>
                                <span className="w-2 h-2 rounded-full flex-shrink-0" style={{ background: lc }} />
                                <span className="text-[11px] text-gray-500">{LOAD_LABEL[q.loadLevel]}</span>
                                <span className="text-[11px] text-gray-400">·</span>
                                <span className="text-[11px] font-bold" style={{ color: lc }}>{q.totalWaiting} người chờ</span>
                              </>
                            ) : (
                              <span className="w-2 h-2 rounded-full bg-green-400" />
                            )}
                          </div>
                        </button>
                      );
                    })
                  )}
                  {!loading && filteredOffices.length > 150 && (
                    <p className="text-center text-[11px] text-gray-400 py-3">
                      Hiển thị 150/{filteredOffices.length} cơ quan — thu hẹp bằng tìm kiếm hoặc bộ lọc
                    </p>
                  )}
                </div>
              </div>
            )}
          </div>
        )}

        {/* ════ TAB: GỢI Ý AI ════ */}
        {sidebarTab === 'smart' && (
          <div className="flex-1 overflow-y-auto">
            {/* Controls */}
            <div className="p-5 space-y-4 border-b border-gray-100">
              <div>
                <label className="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-1.5 block">Thủ tục cần làm</label>
                <div className="grid grid-cols-2 gap-2">
                  {SMART_SERVICES.map(({ id, label, Icon }) => {
                    const active = smartService === id;
                    return (
                      <button key={id} onClick={() => setSmartService(id)} aria-pressed={active}
                        className={`${id === 'all' ? 'col-span-2' : ''} py-2.5 px-3 rounded-xl text-[11px] font-bold flex items-center gap-2 text-left transition-all ${
                          active
                            ? 'bg-primary text-white shadow-md'
                            : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                        }`}>
                        <Icon className={`w-4 h-4 flex-shrink-0 ${active ? 'text-white' : 'text-gray-400'}`} />
                        <span className="leading-tight">{label}</span>
                      </button>
                    );
                  })}
                </div>
              </div>

              <div>
                <label className="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-1.5 block">Phương tiện</label>
                <div className="flex gap-2">
                  {([
                    { id: 'driving' as const, label: 'Xe máy/Ô tô', Icon: Car },
                    { id: 'walking' as const, label: 'Đi bộ',       Icon: PersonStanding },
                    { id: 'cycling' as const, label: 'Xe đạp',      Icon: Bike },
                  ]).map(({ id, label, Icon }) => (
                    <button key={id} onClick={() => setSmartMode(id)}
                      className={`flex-1 py-2.5 rounded-xl text-[11px] font-bold flex flex-col items-center gap-1 transition-all ${
                        smartMode === id ? 'bg-primary text-white shadow-md' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                      }`}>
                      <Icon className="w-4 h-4" />{label}
                    </button>
                  ))}
                </div>
              </div>

              <button onClick={handleSmartRoute} disabled={smartLoading}
                className="w-full py-3.5 bg-primary text-white rounded-xl font-bold text-sm flex items-center justify-center gap-2 hover:opacity-90 transition-opacity disabled:opacity-60 shadow-lg">
                {smartLoading
                  ? <><Loader2 className="w-4 h-4 animate-spin" /> Đang phân tích...</>
                  : <><Sparkles className="w-4 h-4" /> Tìm cơ quan tốt nhất</>}
              </button>

              {smartError && (
                <div className="flex items-start gap-2 p-3 bg-red-50 rounded-xl text-xs text-red-600">
                  <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />{smartError}
                </div>
              )}
            </div>

            {/* Results */}
            <div ref={smartResultsRef} className="p-4 space-y-3 scroll-mt-2">
              {!smartSearched && !smartLoading && (
                <div className="flex flex-col items-center py-10 text-center">
                  <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mb-3">
                    <Sparkles className="w-8 h-8 text-primary" />
                  </div>
                  <p className="text-sm font-semibold text-gray-600 mb-1">Tìm cơ quan phù hợp nhất</p>
                  <p className="text-xs text-gray-400 max-w-[200px]">
                    Chọn thủ tục và bấm tìm — hệ thống gợi ý cơ quan gần, ít đông nhất
                  </p>
                </div>
              )}

              {smartResults.map(rec => {
                const lc = LOAD_COLOR[rec.queue.loadLevel];
                return (
                  <div key={rec.agency.id}
                    onClick={() => {
                      if (rec.agency.latitude && rec.agency.longitude)
                        mapInstance.current?.setView([rec.agency.latitude, rec.agency.longitude], 16);
                      const found = offices.find(o => o.id === rec.agency.id);
                      if (found) handleSelectOffice(found);
                      setSidebarTab('map');
                    }}
                    className={`rounded-2xl border-2 p-4 cursor-pointer transition-all hover:shadow-md ${
                      rec.tag === 'recommended'
                        ? 'border-primary bg-blue-50/50'
                        : 'border-gray-200 hover:border-gray-300 bg-white'
                    }`}>
                    <div className="flex items-center gap-2 mb-2 flex-wrap">
                      {rec.tag === 'recommended' && (
                        <span className="flex items-center gap-1 bg-primary text-white text-[10px] font-bold px-2 py-0.5 rounded-full">
                          <Trophy className="w-3 h-3" /> KHUYẾN NGHỊ
                        </span>
                      )}
                      {rec.tag === 'nearest' && (
                        <span className="flex items-center gap-1 bg-blue-500 text-white text-[10px] font-bold px-2 py-0.5 rounded-full">
                          <MapPin className="w-3 h-3" /> GẦN NHẤT
                        </span>
                      )}
                      {rec.tag === 'least_busy' && (
                        <span className="flex items-center gap-1 bg-teal-500 text-white text-[10px] font-bold px-2 py-0.5 rounded-full">
                          <Users className="w-3 h-3" /> ÍT ĐỢI NHẤT
                        </span>
                      )}
                      <span className="text-[10px] text-gray-400 font-bold ml-auto">#{rec.rank}</span>
                    </div>

                    <p className="text-sm font-bold text-gray-800 leading-tight mb-1">{rec.agency.name}</p>
                    <p className="text-xs text-gray-500 mb-3 flex items-start gap-1">
                      <MapPin className="w-3 h-3 flex-shrink-0 mt-0.5" />{rec.agency.address}
                    </p>

                    <div className="grid grid-cols-3 gap-2 mb-3">
                      {[
                        { l: 'Cách',     v: rec.distance.text,       c: 'text-blue-600' },
                        { l: 'Di chuyển',v: rec.duration.text,        c: 'text-primary' },
                        { l: 'Chờ ≈',   v: rec.queue.estWaitText,    c: LOAD_TEXT[rec.queue.loadLevel] },
                      ].map(({ l, v, c }) => (
                        <div key={l} className="bg-gray-50 rounded-xl p-2 text-center">
                          <p className="text-[9px] text-gray-400 font-bold uppercase mb-0.5">{l}</p>
                          <p className={`text-xs font-black ${c}`}>{v}</p>
                        </div>
                      ))}
                    </div>

                    <div className="mb-3">
                      <div className="flex justify-between text-[10px] mb-1">
                        <span className="text-gray-400">{rec.queue.waiting} người chờ</span>
                        <span className="font-bold" style={{ color: lc }}>{LOAD_LABEL[rec.queue.loadLevel]}</span>
                      </div>
                      <div className="h-1.5 bg-gray-200 rounded-full overflow-hidden">
                        <div className={`h-full rounded-full ${LOAD_BG[rec.queue.loadLevel]}`}
                          style={{ width: `${Math.max(4, Math.min(100, Math.round((rec.queue.waiting / 30) * 100)))}%` }} />
                      </div>
                    </div>

                    <p className="text-[11px] text-gray-500 italic mb-3">"{rec.reason}"</p>

                    <div className="flex gap-2">
                      <button onClick={e => { e.stopPropagation(); onNavigate('appointment', { defaultAgencyId: rec.agency.id }); }}
                        className="flex-1 py-2 bg-primary text-white rounded-lg text-[11px] font-bold flex items-center justify-center gap-1 hover:opacity-90">
                        <CalendarDays className="w-3 h-3" /> Đặt lịch
                      </button>
                      <button onClick={e => { e.stopPropagation(); rec.navigation.googleMapsUrl && window.open(rec.navigation.googleMapsUrl, '_blank'); }}
                        className="flex-1 py-2 bg-gray-100 text-gray-700 rounded-lg text-[11px] font-bold flex items-center justify-center gap-1 hover:bg-gray-200">
                        <Navigation className="w-3 h-3" /> Chỉ đường
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </aside>

      {/* ════════════════════ MAP ════════════════════ */}
      <div className="flex-1 relative overflow-hidden">
        <div ref={mapRef} className="absolute inset-0 w-full h-full" />

        {/* Floating controls */}
        <div className="absolute right-4 bottom-8 flex flex-col gap-2 z-[400]">
          <button onClick={() => mapInstance.current?.zoomIn()}
            className="w-11 h-11 bg-white rounded-xl shadow-lg flex items-center justify-center text-gray-700 hover:bg-gray-50 transition-colors text-xl font-light border border-gray-200">+</button>
          <button onClick={() => mapInstance.current?.zoomOut()}
            className="w-11 h-11 bg-white rounded-xl shadow-lg flex items-center justify-center text-gray-700 hover:bg-gray-50 transition-colors text-xl font-light border border-gray-200">−</button>
          <button onClick={getCurrentLocation} disabled={locationLoading}
            className="w-11 h-11 bg-white rounded-xl shadow-lg flex items-center justify-center text-blue-600 hover:bg-blue-50 transition-colors disabled:opacity-50 border border-gray-200">
            {locationLoading
              ? <Loader2 className="w-5 h-5 animate-spin" />
              : <span className="material-symbols-outlined text-[20px]">my_location</span>}
          </button>
        </div>

        {/* Route info floating badge — hiện khi đang xem đường đi */}
        {directionsMode && directionsInfo && directionsInfo.duration.text !== 'N/A' && (
          <div className="absolute top-4 left-1/2 -translate-x-1/2 z-[400] bg-white/95 backdrop-blur-sm rounded-full px-4 py-2 shadow-xl border border-gray-200 flex items-center gap-2.5 animate-fade-in">
            {dirMode === 'driving'
              ? <Car            className="w-4 h-4 text-blue-600 flex-shrink-0" />
              : dirMode === 'walking'
              ? <PersonStanding className="w-4 h-4 text-emerald-600 flex-shrink-0" />
              : <Bike           className="w-4 h-4 text-amber-500 flex-shrink-0" />}
            <span className="text-sm font-extrabold text-gray-800">
              {directionsInfo.duration.text}
            </span>
            <span className="text-gray-300">·</span>
            <span className="text-xs font-semibold text-gray-500">
              {directionsInfo.distance.text}
            </span>
            {directionsLoading && <Loader2 className="w-3.5 h-3.5 animate-spin text-primary ml-1" />}
          </div>
        )}

        {/* Search result badge on map */}
        {!directionsMode && searchQuery.trim() && filteredOffices.length > 0 && (
          <div className="absolute top-4 left-1/2 -translate-x-1/2 z-[400] bg-white/90 backdrop-blur-sm rounded-full px-4 py-2 shadow-lg border border-gray-200 flex items-center gap-2">
            <Search className="w-3.5 h-3.5 text-primary" />
            <span className="text-xs font-bold text-gray-700">
              {filteredOffices.length} kết quả cho "{searchQuery}"
            </span>
            <button onClick={() => setSearchQuery('')} className="text-gray-400 hover:text-gray-700 ml-1">
              <X className="w-3.5 h-3.5" />
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
