/// <reference types="../vite-env" />

import React, { useState, useEffect, useRef } from 'react';
import { MapPin, Navigation, Clock, Phone, Loader2, AlertCircle, Map, Search, Hash, X } from 'lucide-react';
import { Button } from './ui/button';
import { Card, CardContent } from './ui/card';
import { Badge } from './ui/badge';
import { Input } from './ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Slider } from './ui/slider';
import { servicesAPI, PublicService, ServiceCategory } from '../services/servicesApi';
import { Alert, AlertDescription } from './ui/alert';
import { getMapOverview, AgencyQueueStatus } from '../services/queueService';

declare global {
  interface Window {
    google: any;
  }
}

interface MapScreenProps {
  onNavigate: (screen: string, params?: any) => void;
}

// Default location (Hoàn Kiếm, Hà Nội)
const DEFAULT_LAT = 21.0285;
const DEFAULT_LNG = 105.8542;

export function MapScreen({ onNavigate }: MapScreenProps) {
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [radius, setRadius] = useState([10]);
  const [searchQuery,     setSearchQuery]     = useState('');
  const [selectedOffice, setSelectedOffice] = useState<PublicService | null>(null);
  const [offices, setOffices] = useState<PublicService[]>([]);
  const [categories, setCategories] = useState<ServiceCategory[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');
  const [userLocation, setUserLocation] = useState<{ lat: number; lng: number } | null>(null);
  const [locationLoading, setLocationLoading] = useState(false);
  const [mapError, setMapError] = useState<string>('');
  const [mapLoaded, setMapLoaded] = useState(false);
  const [queueData, setQueueData] = useState<Record<string, AgencyQueueStatus>>({});
  const mapRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<any>(null);
  const markersRef = useRef<any[]>([]);
  const userMarkerRef = useRef<any>(null);
  const scriptLoadedRef = useRef(false);

  // Load Google Maps script dynamically
  useEffect(() => {
    if (scriptLoadedRef.current) return;

    const apiKey = import.meta.env.VITE_GOOGLE_MAPS_API_KEY || '';
    
    if (!apiKey || apiKey === 'YOUR_GOOGLE_MAPS_API_KEY') {
      setMapError('Google Maps API key chưa được cấu hình. Vui lòng thêm VITE_GOOGLE_MAPS_API_KEY vào file .env');
      scriptLoadedRef.current = true;
      return;
    }

    // Check if script already exists
    if (document.querySelector('script[src*="maps.googleapis.com"]')) {
      scriptLoadedRef.current = true;
      if (window.google) {
        setMapLoaded(true);
      }
      return;
    }

    // Load Google Maps script
    const script = document.createElement('script');
    script.src = `https://maps.googleapis.com/maps/api/js?key=${apiKey}&libraries=places`;
    script.async = true;
    script.defer = true;
    
    script.onload = () => {
      scriptLoadedRef.current = true;
      setMapLoaded(true);
      setMapError('');
    };
    
    script.onerror = () => {
      scriptLoadedRef.current = true;
      setMapError('Không thể tải Google Maps. Vui lòng kiểm tra API key và kết nối internet.');
    };

    document.head.appendChild(script);
  }, []);

  // Initialize Google Map after script loads
  useEffect(() => {
    if (!mapLoaded || !mapRef.current || mapInstanceRef.current) return;

    const initMap = () => {
      try {
        if (mapRef.current && window.google && !mapInstanceRef.current) {
          const center = userLocation || { lat: DEFAULT_LAT, lng: DEFAULT_LNG };
          
          mapInstanceRef.current = new window.google.maps.Map(mapRef.current, {
            center: center,
            zoom: 13,
            mapTypeControl: true,
            streetViewControl: false,
            fullscreenControl: true,
            zoomControl: true,
            styles: [
              {
                featureType: 'poi',
                elementType: 'labels',
                stylers: [{ visibility: 'off' }]
              }
            ]
          });
          setMapError('');
        }
      } catch (err: any) {
        setMapError(`Lỗi khởi tạo bản đồ: ${err.message}`);
        console.error('Map initialization error:', err);
      }
    };

    if (window.google) {
      initMap();
    } else {
      // Wait for Google Maps to load
      let attempts = 0;
      const maxAttempts = 50; // 5 seconds
      
      const checkGoogle = setInterval(() => {
        attempts++;
        if (window.google) {
          clearInterval(checkGoogle);
          initMap();
        } else if (attempts >= maxAttempts) {
          clearInterval(checkGoogle);
          setMapError('Google Maps không tải được sau 5 giây. Vui lòng thử lại.');
        }
      }, 100);
    }
  }, [mapLoaded, userLocation]);

  // Update map center when user location changes
  useEffect(() => {
    if (mapInstanceRef.current && userLocation) {
      mapInstanceRef.current.setCenter(userLocation);
      
      // Add/update user location marker
      if (userMarkerRef.current) {
        userMarkerRef.current.setPosition(userLocation);
      } else if (window.google) {
        userMarkerRef.current = new window.google.maps.Marker({
          position: userLocation,
          map: mapInstanceRef.current,
          icon: {
            path: window.google.maps.SymbolPath.CIRCLE,
            scale: 8,
            fillColor: '#3B82F6',
            fillOpacity: 1,
            strokeColor: '#FFFFFF',
            strokeWeight: 2
          },
          title: 'Vị trí của bạn'
        });
      }
    }
  }, [userLocation]);

  // Update markers when offices or queue data change
  useEffect(() => {
    if (!mapInstanceRef.current || !window.google) return;

    // Clear existing markers
    markersRef.current.forEach(marker => marker.setMap(null));
    markersRef.current = [];

    // Add markers for each office
    offices.forEach((office) => {
      if (office.latitude && office.longitude) {
        const qs = queueData[office.id];
        const loadLevel = qs?.loadLevel ?? 'low';
        const waiting   = qs?.totalWaiting ?? 0;

        const marker = new window.google.maps.Marker({
          position: { lat: office.latitude, lng: office.longitude },
          map: mapInstanceRef.current,
          title: office.name,
          icon: {
            url: buildQueueMarkerSvg(waiting, loadLevel),
            scaledSize: new window.google.maps.Size(44, 54),
            anchor: new window.google.maps.Point(22, 54),
          }
        });

        const loadColor = loadLevel === 'high' ? '#ef4444' : loadLevel === 'medium' ? '#f59e0b' : '#22c55e';
        const loadText  = loadLevel === 'high' ? 'Đông' : loadLevel === 'medium' ? 'Vừa' : 'Ít';
        const queueHtml = qs
          ? `<p style="margin:4px 0 0;font-size:12px;color:${loadColor};font-weight:600;">
               Đang chờ: ${waiting} người &bull; <span>${loadText}</span>
             </p>`
          : '';

        const infoWindow = new window.google.maps.InfoWindow({
          content: `
            <div style="padding:8px;min-width:200px;">
              <h3 style="margin:0 0 6px;font-weight:bold;font-size:14px;">${office.name}</h3>
              <p style="margin:0 0 3px;font-size:12px;color:#555;">${office.address}</p>
              ${office.distance ? `<p style="margin:0 0 3px;font-size:12px;color:#555;">Khoảng cách: ${office.distance.toFixed(1)} km</p>` : ''}
              ${office.phone ? `<p style="margin:0 0 3px;font-size:12px;color:#555;">📞 ${office.phone}</p>` : ''}
              ${queueHtml}
            </div>
          `
        });

        marker.addListener('click', () => {
          infoWindow.open(mapInstanceRef.current, marker);
          setSelectedOffice(office);
        });

        markersRef.current.push(marker);
      }
    });

    // Fit bounds to show all markers
    if (markersRef.current.length > 0) {
      const bounds = new window.google.maps.LatLngBounds();
      markersRef.current.forEach(marker => {
        bounds.extend(marker.getPosition());
      });
      if (userMarkerRef.current) {
        bounds.extend(userMarkerRef.current.getPosition());
      }
      mapInstanceRef.current.fitBounds(bounds);
    }
  }, [offices, queueData]);

  // Poll realtime queue overview for map markers
  useEffect(() => {
    const fetchQueueOverview = async () => {
      try {
        const data = await getMapOverview();
        setQueueData(data);
      } catch {
        // non-fatal: markers will show without queue counts
      }
    };
    fetchQueueOverview();
    const interval = setInterval(fetchQueueOverview, 30_000);
    return () => clearInterval(interval);
  }, []);

  // Load categories on mount
  useEffect(() => {
    loadCategories();
  }, []);

  // Load services when filters change
  useEffect(() => {
    loadServices();
  }, [selectedCategory, radius, userLocation]);

  // Build SVG pin icon with waiting count badge
  const buildQueueMarkerSvg = (waiting: number, loadLevel: 'low' | 'medium' | 'high'): string => {
    const color = loadLevel === 'high' ? '#ef4444' : loadLevel === 'medium' ? '#f59e0b' : '#22c55e';
    const label = waiting > 99 ? '99+' : String(waiting);
    const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="44" height="54" viewBox="0 0 44 54">
      <ellipse cx="22" cy="21" rx="19" ry="19" fill="${color}" stroke="white" stroke-width="2.5"/>
      <polygon points="14,37 30,37 22,54" fill="${color}"/>
      <text x="22" y="27" text-anchor="middle" font-size="${label.length > 2 ? 10 : 13}" font-weight="bold" fill="white" font-family="Arial,sans-serif">${label}</text>
    </svg>`;
    return 'data:image/svg+xml;charset=UTF-8,' + encodeURIComponent(svg);
  };

  const loadCategories = async () => {
    try {
      const response = await servicesAPI.getCategories();
      if (response.success) {
        setCategories(response.data.categories);
      }
    } catch (err: any) {
      console.error('Error loading categories:', err);
    }
  };

  const loadServices = async () => {
    setLoading(true);
    setError('');

    try {
      const lat = userLocation?.lat || DEFAULT_LAT;
      const lng = userLocation?.lng || DEFAULT_LNG;
      const categoryId = selectedCategory === 'all' ? undefined : selectedCategory;

      const response = await servicesAPI.getNearby(
        lat,
        lng,
        radius[0],
        categoryId
      );

      if (response.success) {
        setOffices(response.data.services);
      } else {
        setError('Không thể tải danh sách dịch vụ');
      }
    } catch (err: any) {
      setError(err.message || 'Lỗi khi tải danh sách dịch vụ');
      console.error('Error loading services:', err);
    } finally {
      setLoading(false);
    }
  };

  const getCurrentLocation = () => {
    setLocationLoading(true);
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setUserLocation({
            lat: position.coords.latitude,
            lng: position.coords.longitude
          });
          setLocationLoading(false);
        },
        (error) => {
          console.error('Error getting location:', error);
          setError('Không thể lấy vị trí hiện tại. Sử dụng vị trí mặc định.');
          setUserLocation({ lat: DEFAULT_LAT, lng: DEFAULT_LNG });
          setLocationLoading(false);
        }
      );
    } else {
      setError('Trình duyệt không hỗ trợ định vị GPS');
      setUserLocation({ lat: DEFAULT_LAT, lng: DEFAULT_LNG });
      setLocationLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'available': return 'bg-green-100 text-green-800';
      case 'normal': return 'bg-yellow-100 text-yellow-800';
      case 'busy': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'available': return 'Ít tải';
      case 'normal': return 'Bình thường';
      case 'busy': return 'Quá tải';
      default: return status;
    }
  };

  const formatDistance = (distance?: number) => {
    if (!distance) return 'N/A';
    if (distance < 1) {
      return `${Math.round(distance * 1000)} m`;
    }
    return `${distance.toFixed(1)} km`;
  };

  const formatWorkingHours = (workingHours: any) => {
    if (!workingHours) return 'N/A';
    const today = new Date().toLocaleDateString('en-US', { weekday: 'long' }).toLowerCase();
    return workingHours[today] || workingHours.monday || 'N/A';
  };

  const handleViewDetails = async (office: PublicService) => {
    try {
      const lat = userLocation?.lat || DEFAULT_LAT;
      const lng = userLocation?.lng || DEFAULT_LNG;
      const response = await servicesAPI.getById(office.id, lat, lng);
      if (response.success) {
        setSelectedOffice(response.data.service);
      }
    } catch (err) {
      setSelectedOffice(office);
    }
  };

  const filteredOffices = searchQuery.trim()
    ? offices.filter(o =>
        o.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (o.address || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
        (o.services || []).some(s => s.toLowerCase().includes(searchQuery.toLowerCase()))
      )
    : offices;

  return (
    <div className="min-h-screen bg-white">
      
      {/* iOS Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="px-4 py-4">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Bản đồ dịch vụ công</h1>

          {/* Thanh tìm kiếm */}
          <div className="relative mb-4">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <Input
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
              placeholder="Tìm cơ quan, dịch vụ, địa chỉ..."
              className="pl-10 pr-10 h-11 bg-gray-50 border-gray-200 rounded-xl"
            />
            {searchQuery && (
              <button className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400"
                onClick={() => setSearchQuery('')}>
                <X className="w-4 h-4" />
              </button>
            )}
          </div>

          {error && (
            <Alert variant="destructive" className="mb-4">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}
          
          <div className="space-y-4">
            <div className="flex gap-3">
              <Select value={selectedCategory} onValueChange={setSelectedCategory}>
                <SelectTrigger className="flex-1 h-12 rounded-xl border-gray-300">
                  <SelectValue placeholder="Chọn loại dịch vụ" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Tất cả dịch vụ</SelectItem>
                  {categories.map((cat) => (
                    <SelectItem key={cat.id} value={cat.id}>
                      {cat.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <Button 
                variant="outline" 
                size="sm" 
                className="w-12 h-12 rounded-xl border-gray-300"
                onClick={getCurrentLocation}
                disabled={locationLoading}
              >
                {locationLoading ? (
                  <Loader2 className="w-5 h-5 animate-spin" />
                ) : (
                  <Map className="w-5 h-5" />
                )}
              </Button>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-700">
                Bán kính tìm kiếm: {radius[0]} km
              </label>
              <Slider
                value={radius}
                onValueChange={setRadius}
                max={20}
                min={1}
                step={1}
                className="w-full"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Google Maps */}
      <div className="relative h-72 mx-4 my-4 rounded-2xl overflow-hidden border border-gray-200 shadow-lg">
        <div ref={mapRef} className="w-full h-full rounded-2xl" />
        
        {/* Loading state */}
        {!mapLoaded && !mapError && (
          <div className="absolute inset-0 flex items-center justify-center bg-white/80 backdrop-blur-sm rounded-2xl">
            <div className="text-center">
              <Loader2 className="w-8 h-8 animate-spin text-red-600 mx-auto mb-2" />
              <p className="text-sm text-gray-700 font-medium">Đang tải bản đồ...</p>
            </div>
          </div>
        )}

        {/* Error state */}
        {mapError && (
          <div className="absolute inset-0 flex items-center justify-center bg-white/95 backdrop-blur-sm rounded-2xl">
            <div className="text-center p-4 max-w-sm">
              <AlertCircle className="w-12 h-12 text-red-600 mx-auto mb-3" />
              <p className="text-sm font-medium text-gray-900 mb-2">Không thể tải bản đồ</p>
              <p className="text-xs text-gray-700 mb-4">{mapError}</p>
              <div className="text-xs text-left bg-red-50 p-3 rounded-lg border border-red-200">
                <p className="font-medium mb-2 text-red-900">Hướng dẫn:</p>
                <ol className="list-decimal list-inside space-y-1 text-gray-700">
                  <li>Tạo file <code className="bg-white px-1 rounded border border-red-200">.env</code> trong thư mục Frontend</li>
                  <li>Thêm: <code className="bg-white px-1 rounded border border-red-200">VITE_GOOGLE_MAPS_API_KEY=your_api_key</code></li>
                  <li>Khởi động lại ứng dụng</li>
                </ol>
                <p className="mt-2 text-gray-600">
                  Xem <code className="bg-white px-1 rounded border border-red-200">GOOGLE_MAPS_SETUP.md</code> để biết chi tiết
                </p>
              </div>
            </div>
          </div>
        )}

        {/* GPS Button */}
        {mapLoaded && !mapError && (
          <div className="absolute top-4 right-4 z-10 flex flex-col gap-2 items-end">
            <Button
              variant="outline"
              size="sm"
              className="bg-white/90 backdrop-blur-sm shadow-md"
              onClick={getCurrentLocation}
              disabled={locationLoading}
            >
              {locationLoading ? (
                <Loader2 className="w-4 h-4 animate-spin mr-2" />
              ) : (
                <MapPin className="w-4 h-4 mr-2" />
              )}
              {locationLoading ? 'Đang lấy...' : 'Vị trí của tôi'}
            </Button>
            {/* Queue legend */}
            <div className="bg-white/90 backdrop-blur-sm rounded-xl shadow-md px-3 py-2 text-xs space-y-1">
              <div className="flex items-center gap-1.5"><span className="w-3 h-3 rounded-full bg-green-500 inline-block"/><span>Ít người (≤5)</span></div>
              <div className="flex items-center gap-1.5"><span className="w-3 h-3 rounded-full bg-amber-500 inline-block"/><span>Vừa (6-15)</span></div>
              <div className="flex items-center gap-1.5"><span className="w-3 h-3 rounded-full bg-red-500 inline-block"/><span>Đông (&gt;15)</span></div>
            </div>
          </div>
        )}
      </div>

      {/* AI Route Suggestion */}
      {filteredOffices.length > 0 && (
      <div className="mx-4 mb-4 p-5 bg-red-50 rounded-2xl border border-red-100">
        <div className="flex items-start space-x-4">
          <div className="flex-shrink-0">
            <div className="w-10 h-10 bg-red-600 rounded-xl flex items-center justify-center">
              <span className="text-white font-semibold">AI</span>
            </div>
          </div>
          <div className="flex-1">
            <h3 className="font-semibold text-red-800 mb-2">Gợi ý lộ trình thông minh</h3>
            <p className="text-sm text-red-700 leading-relaxed">
                Dựa trên thời gian tối ưu, bạn nên đến <strong>{filteredOffices[0]?.name}</strong> 
                vào lúc 9:00 sáng để tránh đông đúc. 
                {filteredOffices[0]?.distance && (
                  <> Khoảng cách: {formatDistance(filteredOffices[0].distance)}.</>
                )}
            </p>
          </div>
        </div>
      </div>
      )}

      {/* Offices list */}
      <div className="px-4 pb-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">
          Cơ quan gần bạn tại Hà Nội ({filteredOffices.length})
        </h2>
        
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-8 h-8 animate-spin text-red-600" />
            <span className="ml-3 text-gray-600">Đang tải...</span>
          </div>
        ) : filteredOffices.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-600">Không tìm thấy dịch vụ nào trong bán kính {radius[0]} km</p>
          </div>
        ) : (
        <div className="space-y-4">
          {filteredOffices.map((office) => (
            <Card 
              key={office.id}
              className={`cursor-pointer transition-all border-0 shadow-lg hover:scale-[0.98] ${
                selectedOffice?.id === office.id ? 'ring-2 ring-red-500' : ''
              }`}
                onClick={() => handleViewDetails(office)}
            >
              <CardContent className="p-5">
                <div className="flex justify-between items-start mb-3">
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-900">{office.name}</h3>
                    <p className="text-sm text-gray-600 mt-1">{office.address}</p>
                    {queueData[office.id] && (
                      <p className={`text-xs font-medium mt-1 ${
                        queueData[office.id].loadLevel === 'high' ? 'text-red-600' :
                        queueData[office.id].loadLevel === 'medium' ? 'text-amber-600' : 'text-green-600'
                      }`}>
                        Đang chờ: {queueData[office.id].totalWaiting} người
                      </p>
                    )}
                  </div>
                  <div className="text-right">
                      <p className="text-sm font-medium text-gray-900">
                        {formatDistance(office.distance)}
                      </p>
                    <Badge className={`mt-1 px-3 py-1 rounded-full ${getStatusColor(office.status)}`}>
                        {getStatusText(office.status)}
                    </Badge>
                  </div>
                </div>

                <div className="flex flex-wrap gap-2 mb-4">
                  {office.services.map((service, index) => (
                    <Badge key={index} variant="outline" className="px-3 py-1 rounded-full border-gray-300">
                      {service}
                    </Badge>
                  ))}
                </div>

                <div className="flex items-center gap-4 text-sm text-gray-600">
                  <div className="flex items-center gap-2">
                    <Clock className="w-4 h-4" />
                      {formatWorkingHours(office.workingHours)}
                  </div>
                    {office.phone && (
                  <div className="flex items-center gap-2">
                    <Phone className="w-4 h-4" />
                    {office.phone}
                  </div>
                    )}
                </div>

                {selectedOffice?.id === office.id && (
                  <div className="mt-5 pt-5 border-t border-gray-200 space-y-4">
                    <div>
                        <h4 className="font-medium text-gray-900 mb-2">Dịch vụ hỗ trợ:</h4>
                        <div className="flex flex-wrap gap-2">
                          {office.services.map((service, index) => (
                            <Badge key={index} variant="outline" className="px-3 py-1">
                              {service}
                            </Badge>
                          ))}
                        </div>
                    </div>
                    
                    <div>
                        <h4 className="font-medium text-gray-900 mb-2">Giờ làm việc:</h4>
                        <div className="text-sm text-gray-600 space-y-1">
                          <p>Thứ 2 - Thứ 6: {office.workingHours?.monday || 'N/A'}</p>
                          <p>Thứ 7: {office.workingHours?.saturday || 'N/A'}</p>
                          <p>Chủ nhật: {office.workingHours?.sunday || 'Nghỉ'}</p>
                        </div>
                    </div>

                      {office.phone && (
                        <div>
                          <h4 className="font-medium text-gray-900 mb-2">Liên hệ:</h4>
                          <p className="text-sm text-gray-600">Điện thoại: {office.phone}</p>
                          {office.email && <p className="text-sm text-gray-600">Email: {office.email}</p>}
                        </div>
                      )}

                    {queueData[office.id] && (
                      <div className={`p-4 rounded-2xl ${
                        queueData[office.id].loadLevel === 'high' ? 'bg-red-50 border border-red-100' :
                        queueData[office.id].loadLevel === 'medium' ? 'bg-amber-50 border border-amber-100' :
                        'bg-green-50 border border-green-100'
                      }`}>
                        <h4 className="font-medium text-gray-900 mb-1">Trạng thái hàng chờ</h4>
                        <p className="text-sm text-gray-700">
                          Đang chờ: <strong>{queueData[office.id].totalWaiting}</strong> người &bull; Đang phục vụ: <strong>{queueData[office.id].totalServing}</strong>
                        </p>
                      </div>
                    )}

                    <div className="p-4 bg-blue-50 rounded-2xl">
                      <p className="text-sm text-blue-800">
                        <strong>Lưu ý:</strong> Nên đặt lịch trước qua ứng dụng để tiết kiệm thời gian chờ đợi.
                      </p>
                    </div>

                    <div className="flex gap-2 flex-wrap">
                        <Button
                          className="flex-1 h-11 bg-red-600 hover:bg-red-700 rounded-xl text-sm"
                          onClick={(e) => {
                            e.stopPropagation();
                            if (office.latitude && office.longitude) {
                              window.open(
                                `https://www.google.com/maps/dir/?api=1&destination=${office.latitude},${office.longitude}`,
                                '_blank'
                              );
                            }
                          }}
                        >
                          <Navigation className="w-4 h-4 mr-1.5" />
                          Đường đi
                        </Button>
                        <Button
                          className="flex-1 h-11 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-sm"
                          onClick={(e) => {
                            e.stopPropagation();
                            onNavigate('queue', { agencyId: office.id, agencyName: office.name });
                          }}
                        >
                          <Hash className="w-4 h-4 mr-1.5" />
                          Lấy số
                        </Button>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
        )}
      </div>
    </div>
  );
}
