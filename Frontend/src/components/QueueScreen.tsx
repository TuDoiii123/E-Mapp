/**
 * QueueScreen — Người dùng lấy số thứ tự & theo dõi vé của mình
 */
import React, { useState, useEffect, useCallback } from 'react';
import {
  Hash, Clock, CheckCircle, XCircle, RefreshCw,
  ChevronLeft, Users, Ticket, AlertCircle,
} from 'lucide-react';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import {
  takeTicket, getMyTickets, cancelTicket, getQueueSummary,
  formatWaitTime, QueueTicket, QueueSummary,
} from '../services/queueService';
import { useAuth } from '../contexts/AuthContext';

interface QueueScreenProps {
  onNavigate: (screen: string, params?: any) => void;
  agencyId?:  string;
  agencyName?:string;
}

const STATUS_LABELS: Record<string, { label: string; color: string }> = {
  waiting:   { label: 'Đang chờ',     color: 'bg-yellow-100 text-yellow-800' },
  called:    { label: 'Đã được gọi',  color: 'bg-blue-100 text-blue-800' },
  serving:   { label: 'Đang phục vụ', color: 'bg-green-100 text-green-800' },
  done:      { label: 'Hoàn thành',   color: 'bg-gray-100 text-gray-600' },
  absent:    { label: 'Vắng mặt',     color: 'bg-orange-100 text-orange-800' },
  cancelled: { label: 'Đã hủy',       color: 'bg-red-100 text-red-600' },
};

export function QueueScreen({ onNavigate, agencyId = 'default', agencyName = 'Cơ quan hành chính' }: QueueScreenProps) {
  const { user } = useAuth();
  const [myTickets,   setMyTickets]   = useState<QueueTicket[]>([]);
  const [summary,     setSummary]     = useState<QueueSummary | null>(null);
  const [loading,     setLoading]     = useState(false);
  const [taking,      setTaking]      = useState(false);
  const [error,       setError]       = useState('');
  const [selectedSvc, setSelectedSvc] = useState('');
  const [svcName,     setSvcName]     = useState('Dịch vụ hành chính');

  // Danh sách thủ tục mẫu — thực tế lấy từ API services
  const services = [
    { id: 'svc-cccd',    name: 'Cấp CCCD / Hộ chiếu',         prefix: 'A' },
    { id: 'svc-datdai',  name: 'Thủ tục đất đai',              prefix: 'B' },
    { id: 'svc-hotich',  name: 'Đăng ký hộ tịch / Khai sinh',  prefix: 'C' },
    { id: 'svc-xacnhan', name: 'Xác nhận giấy tờ',             prefix: 'D' },
    { id: 'svc-other',   name: 'Thủ tục khác',                 prefix: 'A' },
  ];

  const loadData = useCallback(async () => {
    try {
      const [tickets, sum] = await Promise.all([
        getMyTickets(),
        getQueueSummary(agencyId),
      ]);
      setMyTickets(tickets);
      setSummary(sum);
    } catch {
      // bỏ qua lỗi tải
    }
  }, [agencyId]);

  useEffect(() => {
    loadData();
    // Poll mỗi 30s khi không dùng WebSocket
    const interval = setInterval(loadData, 30_000);
    return () => clearInterval(interval);
  }, [loadData]);

  const handleTakeTicket = async () => {
    if (!selectedSvc) {
      setError('Vui lòng chọn thủ tục');
      return;
    }
    setTaking(true);
    setError('');
    try {
      const svc    = services.find(s => s.id === selectedSvc);
      const ticket = await takeTicket({
        agencyId,
        serviceId:   selectedSvc,
        serviceName: svcName,
        prefix:      svc?.prefix || 'A',
        userName:    user?.fullName || '',
      });
      setMyTickets(prev => [ticket, ...prev]);
      await loadData();
    } catch (e: any) {
      setError(e.message || 'Không thể lấy số');
    } finally {
      setTaking(false);
    }
  };

  const handleCancel = async (ticketId: string) => {
    try {
      await cancelTicket(ticketId);
      setMyTickets(prev => prev.map(t =>
        t.id === ticketId ? { ...t, status: 'cancelled' } : t
      ));
    } catch (e: any) {
      setError(e.message || 'Không thể hủy vé');
    }
  };

  const activeTicket = myTickets.find(t =>
    ['waiting', 'called', 'serving'].includes(t.status)
  );

  return (
    <div className="min-h-screen bg-gray-50 pb-20">
      {/* Header */}
      <div className="bg-red-600 text-white">
        <div className="flex items-center gap-3 px-4 pt-12 pb-4">
          <Button variant="ghost" size="sm" className="text-white hover:bg-red-700 p-2"
            onClick={() => onNavigate('home')}>
            <ChevronLeft className="w-5 h-5" />
          </Button>
          <div>
            <h1 className="text-lg font-bold">Lấy số thứ tự</h1>
            <p className="text-sm text-red-200">{agencyName}</p>
          </div>
          <Button variant="ghost" size="sm" className="ml-auto text-white hover:bg-red-700 p-2"
            onClick={() => { setLoading(true); loadData().finally(() => setLoading(false)); }}>
            <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
          </Button>
        </div>
      </div>

      <div className="px-4 pt-4 space-y-4">
        {/* Tóm tắt hàng chờ */}
        {summary && (
          <div className="grid grid-cols-3 gap-3">
            {[
              { label: 'Đang chờ',    value: summary.totalWaiting,  color: 'text-yellow-600' },
              { label: 'Đang phục vụ',value: summary.totalServing + summary.totalCalled, color: 'text-blue-600' },
              { label: 'Xong hôm nay',value: summary.totalDone,     color: 'text-green-600' },
            ].map(item => (
              <Card key={item.label} className="text-center p-3">
                <p className={`text-2xl font-bold ${item.color}`}>{item.value}</p>
                <p className="text-xs text-gray-500 mt-1">{item.label}</p>
              </Card>
            ))}
          </div>
        )}

        {/* Đang phục vụ tại các quầy */}
        {summary && summary.nowServing.length > 0 && (
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-semibold text-gray-700 flex items-center gap-2">
                <Users className="w-4 h-4 text-green-500" /> Đang phục vụ
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-2">
                {summary.nowServing.map(s => (
                  <div key={s.counterNo}
                    className="bg-green-50 rounded-lg p-2 text-center border border-green-200">
                    <p className="text-xs text-gray-500">Quầy {s.counterNo}</p>
                    <p className="text-xl font-bold text-green-700">{s.ticketCode}</p>
                    <p className="text-xs text-gray-500 truncate">{s.serviceName}</p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Vé hiện tại của tôi */}
        {activeTicket && (
          <Card className="border-2 border-red-200 bg-red-50">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-semibold text-red-700 flex items-center gap-2">
                <Ticket className="w-4 h-4" /> Vé của bạn
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-5xl font-bold text-red-600">{activeTicket.ticketCode}</p>
                  <p className="text-sm text-gray-600 mt-1">{activeTicket.serviceName}</p>
                  <Badge className={`mt-2 text-xs ${STATUS_LABELS[activeTicket.status]?.color}`}>
                    {STATUS_LABELS[activeTicket.status]?.label}
                  </Badge>
                </div>
                <div className="text-right">
                  {activeTicket.status === 'waiting' && (
                    <>
                      <p className="text-xs text-gray-500">Chờ ước tính</p>
                      <p className="text-lg font-semibold text-orange-600 flex items-center gap-1">
                        <Clock className="w-4 h-4" />
                        {formatWaitTime(activeTicket.estimatedWait)}
                      </p>
                    </>
                  )}
                  {activeTicket.counterNo && (
                    <p className="text-sm text-gray-600 mt-1">Quầy {activeTicket.counterNo}</p>
                  )}
                  {activeTicket.status === 'waiting' && (
                    <Button variant="outline" size="sm"
                      className="mt-2 text-red-600 border-red-300 text-xs"
                      onClick={() => handleCancel(activeTicket.id)}>
                      <XCircle className="w-3 h-3 mr-1" /> Hủy vé
                    </Button>
                  )}
                </div>
              </div>
              {activeTicket.status === 'called' && (
                <div className="mt-3 bg-blue-100 rounded-lg p-3 text-center">
                  <p className="text-blue-700 font-semibold animate-pulse">
                    Đến quầy {activeTicket.counterNo} ngay!
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* Form lấy số mới */}
        {!activeTicket && (
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-semibold text-gray-700 flex items-center gap-2">
                <Hash className="w-4 h-4 text-red-500" /> Lấy số thứ tự mới
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div>
                <p className="text-xs text-gray-500 mb-2">Chọn thủ tục</p>
                <div className="space-y-2">
                  {services.map(svc => (
                    <button key={svc.id}
                      className={`w-full text-left px-3 py-2.5 rounded-lg border text-sm transition-all ${
                        selectedSvc === svc.id
                          ? 'border-red-500 bg-red-50 text-red-700 font-medium'
                          : 'border-gray-200 bg-white hover:border-gray-300'
                      }`}
                      onClick={() => { setSelectedSvc(svc.id); setSvcName(svc.name); setError(''); }}>
                      <span className="inline-block w-7 h-5 text-center text-xs font-bold
                        bg-gray-100 rounded mr-2 leading-5">{svc.prefix}</span>
                      {svc.name}
                    </button>
                  ))}
                </div>
              </div>

              {error && (
                <div className="flex items-center gap-2 text-red-600 text-sm bg-red-50 rounded-lg p-2">
                  <AlertCircle className="w-4 h-4 flex-shrink-0" />
                  {error}
                </div>
              )}

              <Button className="w-full bg-red-600 hover:bg-red-700 text-white"
                onClick={handleTakeTicket} disabled={taking || !selectedSvc}>
                {taking ? (
                  <span className="flex items-center gap-2">
                    <RefreshCw className="w-4 h-4 animate-spin" /> Đang lấy số...
                  </span>
                ) : (
                  <span className="flex items-center gap-2">
                    <Ticket className="w-4 h-4" /> Lấy số thứ tự
                  </span>
                )}
              </Button>

              {summary && summary.totalWaiting > 0 && (
                <p className="text-xs text-center text-gray-500">
                  Hiện có <strong>{summary.totalWaiting}</strong> người đang chờ —
                  ước tính <strong>{formatWaitTime(summary.totalWaiting * (summary.avgServiceTimeSec || 420) / Math.max(summary.activeCounters, 1))}</strong>
                </p>
              )}
            </CardContent>
          </Card>
        )}

        {/* Lịch sử vé hôm nay */}
        {myTickets.filter(t => ['done', 'absent', 'cancelled'].includes(t.status)).length > 0 && (
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-semibold text-gray-700">Lịch sử hôm nay</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {myTickets
                  .filter(t => ['done', 'absent', 'cancelled'].includes(t.status))
                  .map(t => (
                    <div key={t.id} className="flex items-center justify-between py-2
                      border-b border-gray-100 last:border-0">
                      <div className="flex items-center gap-3">
                        {t.status === 'done'
                          ? <CheckCircle className="w-4 h-4 text-green-500" />
                          : <XCircle    className="w-4 h-4 text-red-400" />}
                        <div>
                          <p className="text-sm font-medium">{t.ticketCode}</p>
                          <p className="text-xs text-gray-500">{t.serviceName}</p>
                        </div>
                      </div>
                      <Badge className={`text-xs ${STATUS_LABELS[t.status]?.color}`}>
                        {STATUS_LABELS[t.status]?.label}
                      </Badge>
                    </div>
                  ))}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
