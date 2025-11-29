import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Select } from './ui/select';
import { appointmentsAPI } from '../services/appointmentsApi';

interface AppointmentScreenProps {
  onNavigate: (screen: string, params?: any) => void;
  defaultAgencyId?: string;
  defaultServiceCode?: string;
}

export function AppointmentScreen({ onNavigate, defaultAgencyId, defaultServiceCode }: AppointmentScreenProps) {
  const [agencyId, setAgencyId] = useState(defaultAgencyId || 'agency-001');
  const [serviceCode, setServiceCode] = useState(defaultServiceCode || 'SERVICE_CODE');
  const [date, setDate] = useState<string>('');
  const [time, setTime] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  useEffect(() => {
    const today = new Date();
    const yyyy = today.getFullYear();
    const mm = String(today.getMonth() + 1).padStart(2, '0');
    const dd = String(today.getDate()).padStart(2, '0');
    setDate(`${yyyy}-${mm}-${dd}`);
    setTime('09:00');
  }, []);

  const handleSubmit = async () => {
    setLoading(true);
    setError(null);
    setSuccessMsg(null);
    try {
      const res = await appointmentsAPI.create({ agencyId, serviceCode, date, time });
      setSuccessMsg(res.message || 'Đặt lịch hẹn thành công');
    } catch (e: any) {
      setError(e.message || 'Có lỗi xảy ra');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <Card className="border-0 shadow-lg bg-white">
        <CardHeader>
          <CardTitle className="text-lg font-semibold text-gray-900">Đặt lịch hẹn</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="block text-sm text-gray-700 mb-1">Cơ quan</label>
            <Input value={agencyId} onChange={(e) => setAgencyId(e.target.value)} placeholder="Nhập mã cơ quan" />
          </div>
          <div>
            <label className="block text-sm text-gray-700 mb-1">Dịch vụ</label>
            <Input value={serviceCode} onChange={(e) => setServiceCode(e.target.value)} placeholder="Nhập mã dịch vụ" />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm text-gray-700 mb-1">Ngày</label>
              <Input type="date" value={date} onChange={(e) => setDate(e.target.value)} />
            </div>
            <div>
              <label className="block text-sm text-gray-700 mb-1">Giờ</label>
              <Input type="time" value={time} onChange={(e) => setTime(e.target.value)} />
            </div>
          </div>

          {error && <div className="text-red-600 text-sm">{error}</div>}
          {successMsg && <div className="text-green-600 text-sm">{successMsg}</div>}

          <Button className="w-full h-12 rounded-xl" onClick={handleSubmit} disabled={loading}>
            {loading ? 'Đang đặt lịch...' : 'Đặt lịch'}
          </Button>

          <Button variant="outline" className="w-full h-12 rounded-xl mt-2" onClick={() => onNavigate('home')}>
            Quay lại trang chủ
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
