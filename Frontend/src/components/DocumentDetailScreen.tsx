import React, { useEffect, useState } from 'react';
import { API_BASE_URL } from '../services/api';
import { ArrowLeft } from 'lucide-react';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';

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
      // fetch list of services (locations) for this category
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
  }, [serviceId, params]);

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white border-b border-gray-200">
        <div className="px-4 py-4 flex items-center gap-3">
          <Button variant="ghost" size="icon" onClick={() => onNavigate('document-catalog')} className="w-10 h-10">
            <ArrowLeft className="w-5 h-5" />
          </Button>
          <div>
            <h1 className="text-xl font-semibold">Chi tiết giấy tờ</h1>
            <p className="text-sm text-gray-600">Thông tin chi tiết dịch vụ</p>
          </div>
        </div>
      </div>

      <div className="px-4 py-6">
        {loading ? (
          <div className="text-center text-gray-600">Đang tải...</div>
        ) : !service ? (
          <Card className="p-6">
            <CardContent>
              <div className="text-gray-600">Không tìm thấy thông tin dịch vụ.</div>
            </CardContent>
          </Card>
        ) : locations && locations.length !== 0 ? (
          <div className="space-y-4">
            <Card className="p-4">
              <CardContent>
                <div className="text-2xl font-bold">{service?.name || 'Danh mục'}</div>
                <div className="text-sm text-gray-600">Danh sách các nơi thực hiện ({locations.length})</div>
              </CardContent>
            </Card>

            <div className="grid grid-cols-1 gap-3">
              {locations.map((loc: any, idx: number) => (
                <Card key={`${loc.id || loc.code || loc.name || 'loc'}-${idx}`} className="p-4">
                  <CardContent>
                    <div className="font-medium text-gray-900">{loc.name || loc.ten || loc.serviceName}</div>
                    <div className="text-sm text-gray-600">{loc.address || loc.diachi || ''}</div>
                    <div className="text-sm text-gray-700 mt-2">{loc.phone || loc.sdt || loc.contact || ''}</div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            <Card className="p-4">
              <CardContent>
                <div className="text-2xl font-bold">{service.name}</div>
                <div className="text-sm text-gray-600">{service.categoryId ? `Thể loại: ${service.categoryId}` : ''}</div>
                <div className="mt-3 text-gray-700">{service.description}</div>
              </CardContent>
            </Card>

            <Card className="p-4">
              <CardHeader>
                <CardTitle>Thông tin liên hệ</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-sm text-gray-700">Địa chỉ: {service.address || '—'}</div>
                <div className="text-sm text-gray-700">Điện thoại: {service.phone || '—'}</div>
                <div className="text-sm text-gray-700">Email: {service.email || '—'}</div>
                <div className="text-sm text-gray-700">Website: {service.website || '—'}</div>
              </CardContent>
            </Card>

            <Card className="p-4">
              <CardHeader>
                <CardTitle>Chi tiết thêm</CardTitle>
              </CardHeader>
              <CardContent>
                <pre className="text-xs text-gray-700 whitespace-pre-wrap">{JSON.stringify(service, null, 2)}</pre>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
}

export default DocumentDetailScreen;
