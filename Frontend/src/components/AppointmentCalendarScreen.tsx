import React, { useEffect, useMemo, useState } from 'react';
import { appointmentsAPI, Appointment, CreateAppointmentRequest } from '../services/appointmentsApi';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Select } from './ui/select';
import FullCalendar from '@fullcalendar/react';
import dayGridPlugin from '@fullcalendar/daygrid';
import interactionPlugin from '@fullcalendar/interaction';
import viLocale from '@fullcalendar/core/locales/vi';

interface AppointmentCalendarScreenProps {
  onNavigate: (screen: string, params?: any) => void;
}

// Color mapping by status
const statusColors: Record<string, string> = {
  pending: '#f59e0b', // amber
  completed: '#10b981', // emerald
  cancelled: '#ef4444', // red
};

export const AppointmentCalendarScreen: React.FC<AppointmentCalendarScreenProps> = ({ onNavigate }) => {
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [loading, setLoading] = useState(false);
  const [creating, setCreating] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [showDetail, setShowDetail] = useState(false);
  const [detailAppointment, setDetailAppointment] = useState<Appointment | null>(null);
  const [selectedDate, setSelectedDate] = useState<string>(() => new Date().toISOString().split('T')[0]);

  // Form fields
  const [fullName, setFullName] = useState('');
  const [phone, setPhone] = useState('');
  const [info, setInfo] = useState('');
  const [agencyId, setAgencyId] = useState('agency-001');
  const [serviceCode, setServiceCode] = useState('SERVICE_CODE');
  const [time, setTime] = useState('09:00');

  const [errors, setErrors] = useState<string[]>([]);
  const phonePattern = /^(0[0-9]{9,10})$/;

  const loadAppointments = async () => {
    setLoading(true);
    try {
      const res = await appointmentsAPI.getUpcoming();
      setAppointments(res.data.appointments || []);
    } catch (e: any) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAppointments();
  }, []);

  // Build FullCalendar events from appointments
  const events = useMemo(() => {
    return (appointments || []).map(a => ({
      id: a.id,
      title: `${a.fullName || 'Không tên'} • ${a.serviceCode}`,
      start: `${a.date}T${a.time}`,
      allDay: false,
      backgroundColor: statusColors[a.status || 'pending'] || '#2563eb',
      borderColor: statusColors[a.status || 'pending'] || '#2563eb',
    }));
  }, [appointments]);

  const validateForm = (): boolean => {
    const errs: string[] = [];
    if (!fullName || fullName.trim().length < 2) errs.push('Họ tên phải >= 2 ký tự');
    if (!phonePattern.test(phone)) errs.push('Số điện thoại không hợp lệ');
    if (!selectedDate) errs.push('Chưa chọn ngày');
    if (!time) errs.push('Chưa chọn giờ');
    const dt = new Date(`${selectedDate}T${time}`);
    if (dt < new Date()) errs.push('Thời gian đã qua, chọn thời gian khác');
    if (!agencyId) errs.push('Cơ quan bắt buộc');
    if (!serviceCode) errs.push('Dịch vụ bắt buộc');
    setErrors(errs);
    return errs.length === 0;
  };

  const handleCreate = async () => {
    if (!validateForm()) return;
    setCreating(true);
    try {
      const payload: CreateAppointmentRequest = {
        agencyId,
        serviceCode,
        date: selectedDate,
        time,
        fullName,
        phone,
        info,
      };
      await appointmentsAPI.create(payload);
      setShowForm(false);
      setFullName('');
      setPhone('');
      setInfo('');
      loadAppointments();
    } catch (e: any) {
      setErrors([e.message || 'Lỗi tạo lịch']);
    } finally {
      setCreating(false);
    }
  };

  const handleDateClick = (arg: { dateStr: string }) => {
    setSelectedDate(arg.dateStr);
    setShowForm(true);
  };

  const handleEventClick = (info: any) => {
    const id = info.event.id as string;
    const apt = appointments.find(a => a.id === id) || null;
    setDetailAppointment(apt);
    setShowDetail(true);
  };

  return (
    <div className="min-h-screen bg-gray-50 p-4 flex flex-col lg:flex-row gap-6">
      {/* Left sidebar: FullCalendar and actions */}
      <div className="lg:w-80 w-full space-y-4">
        <Card className="border-0 shadow-lg bg-white">
          <CardHeader>
            <CardTitle className="text-lg">Lịch tháng</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="fc-wrapper">
              <FullCalendar
                plugins={[dayGridPlugin, interactionPlugin]}
                initialView="dayGridMonth"
                locales={[viLocale]}
                locale="vi"
                firstDay={1}
                height={350}
                headerToolbar={{ left: 'title', center: '', right: 'prev,next' }}
                dayMaxEvents={2}
                events={events}
                dateClick={handleDateClick}
                eventClick={handleEventClick}
              />
            </div>
          </CardContent>
        </Card>
        <Button className="w-full" onClick={() => setShowForm(true)}>Đặt lịch</Button>
        <Button variant="outline" className="w-full" onClick={() => onNavigate('home')}>Về trang chủ</Button>
      </div>
      {/* Right main: upcoming appointments list */}
      <div className="flex-1 space-y-6">
        <Card className="border-0 shadow-lg bg-white">
          <CardHeader>
            <CardTitle className="text-lg">Lịch hẹn sắp tới</CardTitle>
          </CardHeader>
          <CardContent>
            {loading && <div className="text-sm text-gray-500">Đang tải...</div>}
            {!loading && appointments.length === 0 && <div className="text-sm text-gray-500">Chưa có lịch hẹn</div>}
            <div className="space-y-3">
              {appointments.map(a => {
                const dtStr = `${a.date} ${a.time}`;
                return (
                  <div key={a.id} className="p-3 rounded-lg bg-gray-100 flex items-center justify-between">
                    <div>
                      <div className="font-medium text-gray-900">{a.fullName || 'Không tên'} – {a.serviceCode}</div>
                      <div className="text-xs text-gray-600">{dtStr} • {a.agencyId}</div>
                      {a.phone && <div className="text-xs text-gray-500">📞 {a.phone}</div>}
                      {a.info && <div className="text-xs text-gray-500">{a.info}</div>}
                    </div>
                    <span className={`text-xs px-2 py-1 rounded-full ${a.status === 'pending' ? 'bg-yellow-200 text-yellow-800' : a.status === 'completed' ? 'bg-green-200 text-green-800' : 'bg-red-200 text-red-800'}`}>{a.status}</span>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Modal form */}
      {showForm && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl w-full max-w-lg p-6 shadow-xl space-y-5">
            <h2 className="text-lg font-semibold">Tạo lịch hẹn</h2>
            <div className="grid gap-4">
              <div>
                <label className="text-xs font-medium text-gray-600">Họ tên</label>
                <Input value={fullName} onChange={e => setFullName(e.target.value)} placeholder="Nhập họ tên" />
              </div>
              <div>
                <label className="text-xs font-medium text-gray-600">Số điện thoại</label>
                <Input value={phone} onChange={e => setPhone(e.target.value)} placeholder="0xxxxxxxxx" />
              </div>
              <div>
                <label className="text-xs font-medium text-gray-600">Thông tin cuộc hẹn</label>
                <Input value={info} onChange={e => setInfo(e.target.value)} placeholder="Ghi chú ngắn" />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-xs font-medium text-gray-600">Ngày hẹn</label>
                  <Input type="date" value={selectedDate} onChange={e => setSelectedDate(e.target.value)} />
                </div>
                <div>
                  <label className="text-xs font-medium text-gray-600">Giờ hẹn</label>
                  <Input type="time" value={time} onChange={e => setTime(e.target.value)} />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-xs font-medium text-gray-600">Dịch vụ</label>
                  <Input value={serviceCode} onChange={e => setServiceCode(e.target.value)} placeholder="SERVICE_CODE" />
                </div>
                <div>
                  <label className="text-xs font-medium text-gray-600">Cơ quan</label>
                  <Input value={agencyId} onChange={e => setAgencyId(e.target.value)} placeholder="agency-001" />
                </div>
              </div>
            </div>
            {errors.length > 0 && (
              <div className="text-sm text-red-600 space-y-1">
                {errors.map((er,i) => <div key={i}>• {er}</div>)}
              </div>
            )}
            <div className="flex gap-3 pt-2">
              <Button onClick={handleCreate} disabled={creating}>{creating ? 'Đang lưu...' : 'Xác nhận'}</Button>
              <Button variant="outline" onClick={() => { setShowForm(false); setErrors([]); }}>Hủy</Button>
            </div>
          </div>
        </div>
      )}

      {/* Detail modal */}
      {showDetail && detailAppointment && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl w-full max-w-lg p-6 shadow-xl space-y-4">
            <h2 className="text-lg font-semibold">Chi tiết lịch hẹn</h2>
            <div className="space-y-2 text-sm">
              <div><span className="font-medium">Họ tên:</span> {detailAppointment.fullName || 'Không tên'}</div>
              <div><span className="font-medium">SĐT:</span> {detailAppointment.phone || '—'}</div>
              <div><span className="font-medium">Dịch vụ:</span> {detailAppointment.serviceCode}</div>
              <div><span className="font-medium">Cơ quan:</span> {detailAppointment.agencyId}</div>
              <div><span className="font-medium">Thời gian:</span> {detailAppointment.date} {detailAppointment.time}</div>
              <div><span className="font-medium">Trạng thái:</span> {detailAppointment.status}</div>
              {detailAppointment.info && <div><span className="font-medium">Ghi chú:</span> {detailAppointment.info}</div>}
              <div className="flex gap-2 pt-2">
                <Button variant="outline" onClick={() => { setShowDetail(false); setDetailAppointment(null); }}>Đóng</Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
