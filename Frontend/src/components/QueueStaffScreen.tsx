/**
 * QueueStaffScreen — Màn hình nhân viên quầy phục vụ
 * - Gọi vé tiếp theo
 * - Cập nhật trạng thái vé (serving → done / absent)
 * - Xem hàng chờ realtime qua WebSocket
 * - Mở/đóng quầy
 */
import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
  ChevronLeft, Bell, CheckCircle2, XCircle, SkipForward,
  Wifi, WifiOff, Users, Hash, RefreshCw, Settings2,
  PhoneCall, AlertCircle, Play, Square,
} from 'lucide-react';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import {
  QueueWebSocket, QueueSummary, QueueTicket,
  getQueueSummary, formatWaitTime,
} from '../services/queueService';
import { useAuth } from '../contexts/AuthContext';

const BASE = 'http://localhost:8888/api/queue';

function authH() {
  const token = localStorage.getItem('token');
  return token
    ? { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` }
    : { 'Content-Type': 'application/json' };
}

interface Props {
  onNavigate: (screen: string, params?: any) => void;
  agencyId?:  string;
  agencyName?:string;
}

const STATUS_LABEL: Record<string, string> = {
  waiting: 'Chờ', called: 'Đã gọi', serving: 'Đang phục vụ',
  done: 'Xong', absent: 'Vắng', cancelled: 'Hủy',
};
const STATUS_COLOR: Record<string, string> = {
  waiting:  'bg-yellow-100 text-yellow-700',
  called:   'bg-blue-100 text-blue-700',
  serving:  'bg-green-100 text-green-700',
  done:     'bg-gray-100 text-gray-500',
  absent:   'bg-orange-100 text-orange-700',
  cancelled:'bg-red-100 text-red-400',
};

export function QueueStaffScreen({
  onNavigate,
  agencyId   = 'default',
  agencyName = 'Trung tâm Hành chính công',
}: Props) {
  const { user } = useAuth();
  const [counterNo, setCounterNo]   = useState(1);
  const [summary,   setSummary]     = useState<QueueSummary | null>(null);
  const [queue,     setQueue]       = useState<QueueTicket[]>([]);
  const [current,   setCurrent]     = useState<QueueTicket | null>(null); // vé đang phục vụ
  const [calling,   setCalling]     = useState(false);
  const [connected, setConnected]   = useState(false);
  const [isOpen,    setIsOpen]      = useState(true);
  const [msg,       setMsg]         = useState('');
  const lastUpdateRef = useRef<number>(Date.now());
  const wsRef = useRef<QueueWebSocket | null>(null);

  const loadQueue = useCallback(async () => {
    try {
      const token = localStorage.getItem('token');
      const res = await fetch(
        `${BASE}/list/${agencyId}?status=waiting`,
        { headers: authH() }
      );
      const json = await res.json();
      if (json.success) setQueue(json.data || []);
    } catch { /* bỏ qua */ }
  }, [agencyId]);

  const loadSummary = useCallback(async () => {
    try {
      const s = await getQueueSummary(agencyId);
      setSummary(s);
    } catch { /* bỏ qua */ }
  }, [agencyId]);

  useEffect(() => {
    loadSummary();
    loadQueue();

    const ws = new QueueWebSocket(agencyId, (s) => {
      setSummary(s);
      setConnected(true);
      lastUpdateRef.current = Date.now();
    });
    wsRef.current = ws;

    const healthCheck = setInterval(() => {
      setConnected(Date.now() - lastUpdateRef.current < 20_000);
    }, 5_000);

    const pollQueue = setInterval(loadQueue, 15_000);

    return () => {
      ws.destroy();
      clearInterval(healthCheck);
      clearInterval(pollQueue);
    };
  }, [agencyId]);

  // Gọi vé tiếp theo
  const callNext = async () => {
    setCalling(true);
    setMsg('');
    try {
      const res = await fetch(`${BASE}/call-next`, {
        method: 'POST',
        headers: authH(),
        body: JSON.stringify({ agencyId, counterNo }),
      });
      const json = await res.json();
      if (!json.success) { setMsg(json.message || 'Lỗi'); return; }
      if (!json.data) { setMsg('Không còn vé chờ'); return; }

      const ticket = json.data as QueueTicket;
      setCurrent(ticket);
      setQueue(prev => prev.filter(t => t.id !== ticket.id));
      await loadSummary();
    } catch (e: any) {
      setMsg(e.message);
    } finally {
      setCalling(false);
    }
  };

  // Cập nhật trạng thái vé đang phục vụ
  const updateStatus = async (status: 'serving' | 'done' | 'absent') => {
    if (!current) return;
    try {
      const res = await fetch(`${BASE}/ticket/${current.id}/status`, {
        method: 'PUT',
        headers: authH(),
        body: JSON.stringify({ status }),
      });
      const json = await res.json();
      if (json.success) {
        if (status === 'done' || status === 'absent') setCurrent(null);
        else setCurrent(json.data);
        await loadSummary();
      }
    } catch (e: any) {
      setMsg(e.message);
    }
  };

  // Mở/đóng quầy
  const toggleCounter = async () => {
    try {
      await fetch(`${BASE}/counters`, {
        method: 'POST',
        headers: authH(),
        body: JSON.stringify({
          agencyId, counterNo,
          isActive:     !isOpen,
          operatorName: user?.fullName || '',
        }),
      });
      setIsOpen(v => !v);
    } catch { /* bỏ qua */ }
  };

  return (
    <div className="min-h-screen bg-gray-50 pb-6">
      {/* Header */}
      <div className="bg-red-700 text-white">
        <div className="flex items-center gap-3 px-4 pt-12 pb-4">
          <Button variant="ghost" size="sm"
            className="text-white hover:bg-red-800 p-2"
            onClick={() => onNavigate('home')}>
            <ChevronLeft className="w-5 h-5" />
          </Button>
          <div className="flex-1">
            <h1 className="text-base font-bold">Quầy phục vụ #{counterNo}</h1>
            <p className="text-xs text-red-200">{agencyName}</p>
          </div>
          <div className="flex items-center gap-2">
            {connected
              ? <Wifi className="w-4 h-4 text-green-400" />
              : <WifiOff className="w-4 h-4 text-red-300 animate-pulse" />}
            <Button variant="ghost" size="sm"
              className={`text-xs px-2 py-1 rounded-full ${isOpen ? 'bg-green-600' : 'bg-gray-600'}`}
              onClick={toggleCounter}>
              {isOpen ? <Play className="w-3 h-3 mr-1" /> : <Square className="w-3 h-3 mr-1" />}
              {isOpen ? 'Mở' : 'Đóng'}
            </Button>
          </div>
        </div>

        {/* Chọn số quầy */}
        <div className="px-4 pb-3 flex gap-2">
          {[1, 2, 3, 4, 5].map(n => (
            <button key={n}
              onClick={() => setCounterNo(n)}
              className={`w-9 h-9 rounded-lg text-sm font-bold transition-all ${
                counterNo === n
                  ? 'bg-white text-red-700'
                  : 'bg-red-600 text-white hover:bg-red-500'
              }`}>
              {n}
            </button>
          ))}
          <span className="text-xs text-red-200 self-center ml-1">← Chọn quầy</span>
        </div>
      </div>

      <div className="px-4 pt-4 space-y-4">
        {/* Thống kê nhanh */}
        {summary && (
          <div className="grid grid-cols-3 gap-2">
            {[
              { label: 'Chờ',    val: summary.totalWaiting,   color: 'text-yellow-600' },
              { label: 'Xong',   val: summary.totalDone,      color: 'text-green-600' },
              { label: 'Quầy',   val: summary.activeCounters, color: 'text-blue-600' },
            ].map(item => (
              <Card key={item.label} className="text-center p-3">
                <p className={`text-2xl font-bold ${item.color}`}>{item.val}</p>
                <p className="text-xs text-gray-400 mt-0.5">{item.label}</p>
              </Card>
            ))}
          </div>
        )}

        {/* Vé đang phục vụ */}
        <Card className={`border-2 ${current ? 'border-green-400 bg-green-50' : 'border-gray-200'}`}>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-semibold text-gray-700 flex items-center gap-2">
              <PhoneCall className="w-4 h-4 text-green-600" /> Đang phục vụ
            </CardTitle>
          </CardHeader>
          <CardContent>
            {!current ? (
              <div className="text-center py-6 text-gray-400">
                <Hash className="w-12 h-12 mx-auto mb-2 opacity-30" />
                <p className="text-sm">Chưa có vé — bấm "Gọi vé tiếp theo"</p>
              </div>
            ) : (
              <div>
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <p className="text-5xl font-black text-green-700 tracking-wider">
                      {current.ticketCode}
                    </p>
                    <p className="text-sm text-gray-600 mt-1">{current.serviceName}</p>
                    <p className="text-xs text-gray-400">{current.userName}</p>
                  </div>
                  <Badge className={`text-xs ${STATUS_COLOR[current.status]}`}>
                    {STATUS_LABEL[current.status]}
                  </Badge>
                </div>

                {/* Nút hành động */}
                <div className="grid grid-cols-3 gap-2">
                  {current.status === 'called' && (
                    <Button className="col-span-3 bg-green-600 hover:bg-green-700 text-white h-11"
                      onClick={() => updateStatus('serving')}>
                      <Play className="w-4 h-4 mr-2" /> Bắt đầu phục vụ
                    </Button>
                  )}
                  {current.status === 'serving' && (
                    <>
                      <Button className="col-span-2 bg-blue-600 hover:bg-blue-700 text-white h-11"
                        onClick={() => updateStatus('done')}>
                        <CheckCircle2 className="w-4 h-4 mr-1.5" /> Hoàn thành
                      </Button>
                      <Button variant="outline"
                        className="border-orange-300 text-orange-600 hover:bg-orange-50 h-11"
                        onClick={() => updateStatus('absent')}>
                        <XCircle className="w-4 h-4 mr-1" /> Vắng
                      </Button>
                    </>
                  )}
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Gọi vé tiếp theo */}
        <Button
          className="w-full h-14 text-base font-bold bg-red-600 hover:bg-red-700 text-white rounded-xl shadow-lg"
          onClick={callNext}
          disabled={calling || !isOpen}>
          {calling ? (
            <RefreshCw className="w-5 h-5 mr-2 animate-spin" />
          ) : (
            <SkipForward className="w-5 h-5 mr-2" />
          )}
          {calling ? 'Đang gọi...' : 'Gọi vé tiếp theo'}
        </Button>

        {msg && (
          <div className="flex items-center gap-2 text-sm text-orange-700 bg-orange-50
            border border-orange-200 rounded-lg px-3 py-2">
            <AlertCircle className="w-4 h-4 flex-shrink-0" /> {msg}
          </div>
        )}

        {/* Danh sách đang chờ */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-semibold text-gray-700 flex items-center justify-between">
              <span className="flex items-center gap-2">
                <Users className="w-4 h-4 text-yellow-500" />
                Hàng chờ ({queue.length})
              </span>
              <Button variant="ghost" size="sm" className="p-1 h-auto"
                onClick={loadQueue}>
                <RefreshCw className="w-3.5 h-3.5 text-gray-400" />
              </Button>
            </CardTitle>
          </CardHeader>
          <CardContent>
            {queue.length === 0 ? (
              <p className="text-sm text-center text-gray-400 py-4">Hàng chờ trống</p>
            ) : (
              <div className="space-y-2 max-h-64 overflow-y-auto">
                {queue.slice(0, 20).map((t, idx) => (
                  <div key={t.id}
                    className="flex items-center justify-between py-2 px-3
                      rounded-lg bg-gray-50 hover:bg-gray-100 transition-colors">
                    <div className="flex items-center gap-3">
                      <span className="text-xs text-gray-400 w-5">{idx + 1}</span>
                      <div>
                        <p className="text-sm font-bold text-gray-800">{t.ticketCode}</p>
                        <p className="text-xs text-gray-500 truncate max-w-[140px]">{t.serviceName}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      {t.priority > 0 && (
                        <Badge className="text-xs bg-purple-100 text-purple-700 mb-1">Ưu tiên</Badge>
                      )}
                      <p className="text-xs text-gray-400">
                        {formatWaitTime(t.estimatedWait)}
                      </p>
                    </div>
                  </div>
                ))}
                {queue.length > 20 && (
                  <p className="text-xs text-center text-gray-400 py-1">
                    ... và {queue.length - 20} vé khác
                  </p>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
