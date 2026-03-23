/**
 * QueueDisplayScreen — Màn hình bảng hiển thị hàng chờ realtime (public display)
 * Tối ưu độ trễ: WebSocket với heartbeat + exponential backoff reconnect
 */
import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
  MonitorPlay, Wifi, WifiOff, RefreshCw,
  Users, CheckCircle, Clock, ChevronLeft,
} from 'lucide-react';
import { Button } from './ui/button';
import {
  QueueWebSocket, getQueueSummary,
  QueueSummary, formatWaitTime,
} from '../services/queueService';

interface QueueDisplayScreenProps {
  onNavigate: (screen: string) => void;
  agencyId?:  string;
  agencyName?:string;
}

export function QueueDisplayScreen({
  onNavigate,
  agencyId  = 'default',
  agencyName = 'Trung tâm Hành chính công tỉnh Thanh Hóa',
}: QueueDisplayScreenProps) {
  const [summary,   setSummary]   = useState<QueueSummary | null>(null);
  const [connected, setConnected] = useState(false);
  const [lastUpdate,setLastUpdate]= useState<Date | null>(null);
  const [tick,      setTick]      = useState(0); // đồng hồ làm mới
  const wsRef = useRef<QueueWebSocket | null>(null);

  // Callback khi nhận update từ WebSocket
  const handleUpdate = useCallback((data: QueueSummary) => {
    setSummary(data);
    setConnected(true);
    setLastUpdate(new Date());
  }, []);

  // Khởi tạo WebSocket
  useEffect(() => {
    // Tải snapshot ban đầu qua REST (đảm bảo hiển thị ngay cả khi WS chưa ready)
    getQueueSummary(agencyId).then(setSummary).catch(() => {});

    // Kết nối WebSocket
    const ws = new QueueWebSocket(agencyId, handleUpdate);
    wsRef.current = ws;

    // Theo dõi trạng thái kết nối
    const healthCheck = setInterval(() => {
      const age = lastUpdate ? Date.now() - lastUpdate.getTime() : Infinity;
      setConnected(age < 20_000); // coi là mất kết nối nếu > 20s không có dữ liệu
    }, 5_000);

    return () => {
      ws.destroy();
      clearInterval(healthCheck);
    };
  }, [agencyId]);

  // Đồng hồ giây — cập nhật thời gian hiển thị
  useEffect(() => {
    const t = setInterval(() => setTick(n => n + 1), 1_000);
    return () => clearInterval(t);
  }, []);

  const now = new Date();

  // Màu sắc theo tải hàng chờ
  const waitLevel = !summary
    ? 'green'
    : summary.totalWaiting === 0
      ? 'green'
      : summary.totalWaiting < 10
        ? 'yellow'
        : 'red';

  const waitColors = {
    green:  { bg: 'bg-green-500',  text: 'text-green-700',  light: 'bg-green-50' },
    yellow: { bg: 'bg-yellow-500', text: 'text-yellow-700', light: 'bg-yellow-50' },
    red:    { bg: 'bg-red-500',    text: 'text-red-700',    light: 'bg-red-50' },
  };
  const wc = waitColors[waitLevel];

  return (
    <div className="min-h-screen bg-gray-900 text-white flex flex-col">
      {/* Header */}
      <div className="bg-red-700 px-4 py-3 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Button variant="ghost" size="sm" className="text-white hover:bg-red-800 p-1.5"
            onClick={() => onNavigate('home')}>
            <ChevronLeft className="w-5 h-5" />
          </Button>
          <MonitorPlay className="w-5 h-5 text-red-200" />
          <div>
            <h1 className="text-sm font-bold leading-tight">{agencyName}</h1>
            <p className="text-xs text-red-200">Bảng hiển thị hàng chờ</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {connected
            ? <Wifi className="w-4 h-4 text-green-400" />
            : <WifiOff className="w-4 h-4 text-red-300 animate-pulse" />}
          <span className="text-xs text-red-200">
            {now.toLocaleTimeString('vi-VN')}
          </span>
          <Button variant="ghost" size="sm" className="text-white hover:bg-red-800 p-1.5"
            onClick={() => wsRef.current?.refresh()}>
            <RefreshCw className="w-4 h-4" />
          </Button>
        </div>
      </div>

      {/* Nội dung chính */}
      {!summary ? (
        <div className="flex-1 flex items-center justify-center">
          <RefreshCw className="w-10 h-10 text-gray-400 animate-spin" />
        </div>
      ) : (
        <div className="flex-1 flex flex-col gap-3 p-4 overflow-auto">

          {/* Đang phục vụ — ô lớn nổi bật */}
          <div>
            <p className="text-xs text-gray-400 uppercase tracking-wider mb-2">Đang phục vụ</p>
            {summary.nowServing.length === 0 ? (
              <div className="bg-gray-800 rounded-xl p-6 text-center text-gray-500">
                <Users className="w-8 h-8 mx-auto mb-2 opacity-40" />
                <p className="text-sm">Chưa có quầy nào đang phục vụ</p>
              </div>
            ) : (
              <div className="grid grid-cols-2 gap-3">
                {summary.nowServing.map(s => (
                  <div key={s.counterNo}
                    className="bg-green-600 rounded-xl p-4 text-center shadow-lg
                      ring-2 ring-green-400 ring-opacity-60">
                    <p className="text-xs text-green-200 font-medium">QUẦY {s.counterNo}</p>
                    <p className="text-5xl font-black text-white tracking-wider mt-1 mb-1">
                      {s.ticketCode}
                    </p>
                    <p className="text-xs text-green-200 truncate">{s.serviceName}</p>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Thống kê nhanh */}
          <div className="grid grid-cols-2 gap-3">
            <div className={`rounded-xl p-4 ${wc.light} border border-opacity-30`}>
              <div className="flex items-center justify-between mb-1">
                <p className="text-xs text-gray-500 font-medium">Đang chờ</p>
                <Clock className={`w-4 h-4 ${wc.text}`} />
              </div>
              <p className={`text-4xl font-black ${wc.text}`}>{summary.totalWaiting}</p>
              <p className="text-xs text-gray-500 mt-1">người trong hàng</p>
            </div>

            <div className="rounded-xl p-4 bg-blue-50 border border-blue-100">
              <div className="flex items-center justify-between mb-1">
                <p className="text-xs text-gray-500 font-medium">Hoàn thành</p>
                <CheckCircle className="w-4 h-4 text-blue-600" />
              </div>
              <p className="text-4xl font-black text-blue-700">{summary.totalDone}</p>
              <p className="text-xs text-gray-500 mt-1">hôm nay</p>
            </div>
          </div>

          {/* Ước tính thời gian chờ */}
          {summary.totalWaiting > 0 && (
            <div className={`rounded-xl p-4 ${wc.light} border`}>
              <p className="text-xs text-gray-500 font-medium mb-1">Ước tính thời gian chờ</p>
              <p className={`text-2xl font-bold ${wc.text}`}>
                {formatWaitTime(
                  Math.ceil(summary.totalWaiting / Math.max(summary.activeCounters, 1))
                  * (summary.avgServiceTimeSec || 420)
                )}
              </p>
              <p className="text-xs text-gray-400 mt-1">
                {summary.activeCounters} quầy đang mở •
                {summary.peakFactor > 1
                  ? ` giờ cao điểm (×${summary.peakFactor})`
                  : ' bình thường'}
              </p>
            </div>
          )}

          {/* Thông tin quầy */}
          <div>
            <p className="text-xs text-gray-400 uppercase tracking-wider mb-2">
              Quầy phục vụ ({summary.activeCounters} đang mở)
            </p>
            <div className="grid grid-cols-4 gap-2">
              {Array.from({ length: Math.max(summary.activeCounters, 1) }, (_, i) => i + 1).map(n => {
                const serving = summary.nowServing.find(s => s.counterNo === n);
                return (
                  <div key={n}
                    className={`rounded-lg p-2 text-center text-xs ${
                      serving
                        ? 'bg-green-600 text-white'
                        : 'bg-gray-700 text-gray-400'
                    }`}>
                    <p className="font-bold">Q{n}</p>
                    <p className="mt-0.5 truncate">
                      {serving ? serving.ticketCode : '—'}
                    </p>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Footer */}
          <div className="text-center text-xs text-gray-600 pt-2 border-t border-gray-800">
            {connected ? (
              <span className="flex items-center justify-center gap-1 text-green-500">
                <Wifi className="w-3 h-3" /> Cập nhật realtime
                {lastUpdate && ` • ${lastUpdate.toLocaleTimeString('vi-VN')}`}
              </span>
            ) : (
              <span className="flex items-center justify-center gap-1 text-yellow-500">
                <WifiOff className="w-3 h-3" /> Đang kết nối lại...
              </span>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
