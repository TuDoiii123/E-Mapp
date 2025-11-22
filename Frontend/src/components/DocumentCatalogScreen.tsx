import React, { useState, useMemo, useEffect } from 'react';
import { API_BASE_URL } from '../services/api';
import { ArrowLeft, Search } from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';

interface DocumentCatalogProps {
  onNavigate: (screen: string, params?: any) => void;
}

// We'll fetch service list from backend. As a fallback keep a short list.
const FALLBACK_DOC_TYPES = [
  'Giấy phép lái xe',
  'Chứng minh nhân dân / CCCD',
  'Hộ chiếu'
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

  // Build categories map from services: { categoryId: { id, name, count } }
  const categories = useMemo(() => {
    const map: Record<string, { id: string; name: string; count: number }> = {};
    const list = services && services.length ? services : FALLBACK_DOC_TYPES.map((t) => ({ id: t, name: t, categoryId: t }));
    for (const s of list) {
      const cid = s.categoryId || s.theloai_id || s.category || s.name || 'uncategorized';
      const cname = s.categoryName || s.theloai_name || s.category_name || s.category || s.name || 'Khác';
      if (!map[cid]) map[cid] = { id: cid, name: cname, count: 0 };
      map[cid].count += 1;
    }
    // Convert to array and filter by query
    const q = query.trim().toLowerCase();
    return Object.values(map).filter((c) => (q ? c.name.toLowerCase().includes(q) : true));
  }, [query, services]);

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="h-11 bg-white"></div>
      <div className="bg-white border-b border-gray-200">
        <div className="px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Button variant="ghost" size="icon" onClick={() => onNavigate('home')} className="w-10 h-10">
              <ArrowLeft className="w-5 h-5" />
            </Button>
            <div>
              <h1 className="text-xl font-semibold">Tổng hợp giấy tờ</h1>
              <p className="text-sm text-gray-600">Tìm và xem các loại giấy tờ thủ tục</p>
            </div>
          </div>
        </div>

        <div className="px-4 pb-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <Input
              placeholder="Tìm giấy tờ..."
              className="pl-11 h-12 bg-gray-100 border-0 rounded-xl text-base"
              value={query}
              onChange={(e: any) => setQuery(e.target.value)}
            />
          </div>
        </div>
      </div>

      <div className="px-4 py-6 space-y-4">
        {loading ? (
          <Card className="border-0 shadow-lg bg-white p-6 text-center">
            <p className="text-gray-600">Đang tải danh sách giấy tờ...</p>
          </Card>
        ) : categories.length === 0 ? (
          <Card className="border-0 shadow-lg bg-white p-6 text-center">
            <p className="text-gray-600">Không tìm thấy giấy tờ phù hợp.</p>
          </Card>
        ) : (
          <div className="grid grid-cols-1 gap-3">
            {categories.map((c) => (
              <Card key={c.id} className="border-0 shadow-sm bg-white cursor-pointer" onClick={() => onNavigate('document-detail', { categoryId: c.id, categoryName: c.name })}>
                <CardContent className="p-4 flex items-center justify-between">
                  <div>
                    <div className="font-medium text-gray-900">{c.name}</div>
                    <div className="text-sm text-gray-600 mt-1">Số nơi thực hiện: {c.count}</div>
                  </div>
                  <Badge className="bg-slate-100 text-slate-800 px-3 py-1 rounded-full">Xem</Badge>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default DocumentCatalogScreen;
