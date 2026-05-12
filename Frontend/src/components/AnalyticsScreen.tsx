import { TrendingUp, Clock, AlertTriangle, CheckCircle, Users, FileText, MapPin, Lightbulb, ArrowLeft, RefreshCw } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { Button } from './ui/button';
import React, { useState, useEffect } from 'react';
import * as adminSvc from '../services/adminService';

interface AnalyticsScreenProps {
  onNavigate: (screen: string) => void;
}

export function AnalyticsScreen({ onNavigate }: AnalyticsScreenProps) {
  const [myApps,       setMyApps]       = useState<any[]>([]);
  const [systemData,   setSystemData]   = useState<any>(null);
  const [loadingStats, setLoadingStats] = useState(true);

  useEffect(() => {
    Promise.all([
      adminSvc.getMyApplications().catch(() => ({ data: [] })),
      adminSvc.getStats().catch(() => ({ data: null })),
    ]).then(([myRes, sysRes]) => {
      setMyApps(myRes.data || []);
      setSystemData(sysRes.data || null);
    }).finally(() => setLoadingStats(false));
  }, []);

  const completed   = myApps.filter(a => a.currentStatus === 'approved').length;
  const inProgress  = myApps.filter(a => ['submitted','in_review'].includes(a.currentStatus)).length;
  const needInfo    = myApps.filter(a => a.currentStatus === 'more_info').length;
  const total       = myApps.length;

  // Tính avgProcessingTime từ dữ liệu thực (submitted → approved)
  const avgProcessingTime = (() => {
    const done = myApps.filter(a => a.status === 'approved' && a.createdAt && a.updatedAt);
    if (!done.length) return null;
    const avg = done.reduce((sum, a) => {
      const days = (new Date(a.updatedAt).getTime() - new Date(a.createdAt).getTime()) / 86400000;
      return sum + days;
    }, 0) / done.length;
    return Math.round(avg);
  })();

  const personalStats = {
    totalDocuments:    total,
    completed,
    inProgress,
    avgProcessingTime,
    successRate:       total > 0 ? Math.round((completed / total) * 100) : 0,
  };

  const processWarnings = myApps
    .filter(a => a.status === 'more_info')
    .map(a => ({
      id:         a.id,
      title:      'Cần bổ sung hồ sơ',
      content:    `Hồ sơ "${a.procedureName || a.serviceId || a.id.slice(0, 8)}" yêu cầu bổ sung thêm tài liệu.`,
      severity:   'warning',
      documentId: a.id,
    }));

  // Gợi ý thực tế dựa trên dữ liệu hồ sơ của user
  const aiSuggestions = [
    ...(inProgress > 0 ? [{
      id: 1, type: 'online', title: 'Theo dõi hồ sơ',
      content: `Bạn có ${inProgress} hồ sơ đang xử lý. Kiểm tra thường xuyên để bổ sung kịp thời.`,
      action: 'Xem hồ sơ', icon: FileText, priority: 'high',
    }] : []),
    {
      id: 2, type: 'timing', title: 'Thời điểm tốt nhất',
      content: 'Nộp hồ sơ vào thứ 3-4 sẽ được xử lý nhanh hơn. Tránh thứ 2 và cuối tuần.',
      action: 'Đặt lịch hẹn', icon: Clock, priority: 'low',
    },
    {
      id: 3, type: 'office', title: 'Nộp trực tuyến',
      content: 'Trung tâm Hành chính công Thanh Hóa hỗ trợ nộp hồ sơ trực tuyến 24/7.',
      action: 'Nộp ngay', icon: MapPin, priority: 'medium',
    },
  ];

  const systemStats = systemData ? [
    { label: 'Tổng người dùng',         value: String(systemData.totalUsers ?? '–'),          change: '', positive: true },
    { label: 'Hồ sơ đang chờ duyệt',    value: String(systemData.pendingApplications ?? '–'), change: '', positive: false },
    { label: 'Tổng hồ sơ',              value: String(systemData.totalApplications ?? '–'),   change: '', positive: true },
    { label: 'Vé xếp hàng hôm nay',     value: String(systemData.ticketsToday ?? '–'),        change: '', positive: true },
  ] : [];

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'border-red-200 bg-red-50';
      case 'medium': return 'border-orange-200 bg-orange-50';
      case 'low': return 'border-blue-200 bg-blue-50';
      default: return 'border-gray-200 bg-gray-50';
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'urgent': return 'border-red-500 bg-red-50';
      case 'warning': return 'border-orange-500 bg-orange-50';
      default: return 'border-gray-300 bg-gray-50';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      
      {/* iOS Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="px-4 py-4">
          <div className="flex items-center space-x-3 mb-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onNavigate('home')}
              className="w-10 h-10 rounded-full"
            >
              <ArrowLeft className="w-5 h-5" />
            </Button>
            <h1 className="text-2xl font-bold text-gray-900">Phân tích & Gợi ý</h1>
          </div>
          <div className="ml-[52px]">
            <p className="text-gray-600">Thông tin thông minh để tối ưu trải nghiệm</p>
          </div>
        </div>
      </div>

      <div className="px-4 py-6 space-y-8">
        {/* Personal Statistics */}
        <div>
          <h2 className="mb-4">Thống kê cá nhân</h2>
          {loadingStats ? (
            <div className="flex justify-center py-6"><RefreshCw className="w-5 h-5 animate-spin text-gray-400" /></div>
          ) : (
            <>
              <div className="grid grid-cols-2 gap-4 mb-4">
                <Card>
                  <CardContent className="p-4 text-center">
                    <div className="text-2xl mb-1">{personalStats.completed}</div>
                    <div className="text-sm text-gray-600">Hồ sơ đã duyệt</div>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="p-4 text-center">
                    <div className="text-2xl mb-1">{personalStats.inProgress}</div>
                    <div className="text-sm text-gray-600">Đang xử lý</div>
                  </CardContent>
                </Card>
              </div>

              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span>Tiến độ hoàn thành</span>
                    <span>
                      {personalStats.totalDocuments > 0
                        ? Math.round((personalStats.completed / personalStats.totalDocuments) * 100)
                        : 0}%
                    </span>
                  </div>
                  <Progress value={
                    personalStats.totalDocuments > 0
                      ? (personalStats.completed / personalStats.totalDocuments) * 100
                      : 0
                  } />
                  <div className="flex justify-between text-sm text-gray-600 mt-2">
                    <span>{personalStats.completed}/{personalStats.totalDocuments} hồ sơ</span>
                    {needInfo > 0 && <span className="text-orange-600">{needInfo} cần bổ sung</span>}
                  </div>
                </CardContent>
              </Card>
            </>
          )}
        </div>

        {/* AI Suggestions */}
        <div>
          <h2 className="mb-4 flex items-center gap-2">
            <Lightbulb className="w-5 h-5 text-yellow-600" />
            Gợi ý thông minh
          </h2>
          <div className="space-y-3">
            {aiSuggestions.map((suggestion) => (
              <Card key={suggestion.id} className={`border-l-4 ${getPriorityColor(suggestion.priority)}`}>
                <CardContent className="p-4">
                  <div className="flex items-start gap-3">
                    <div className="p-2 bg-white rounded-full">
                      <suggestion.icon className="w-5 h-5" />
                    </div>
                    <div className="flex-1">
                      <h3 className="mb-1">{suggestion.title}</h3>
                      <p className="text-sm text-gray-600 mb-3">{suggestion.content}</p>
                      <Button 
                        size="sm" 
                        variant="outline"
                        onClick={() => {
                          if (suggestion.type === 'office') onNavigate('map');
                          if (suggestion.type === 'online') onNavigate('submit');
                        }}
                      >
                        {suggestion.action}
                      </Button>
                    </div>
                    <Badge variant="outline" className="text-xs">
                      {suggestion.priority === 'high' ? 'Quan trọng' :
                       suggestion.priority === 'medium' ? 'Trung bình' : 'Thông tin'}
                    </Badge>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* Process Warnings */}
        {processWarnings.length > 0 && (
          <div>
            <h2 className="mb-4 flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-orange-600" />
              Cảnh báo tiến độ
            </h2>
            <div className="space-y-3">
              {processWarnings.map((warning) => (
                <Card key={warning.id} className={`border-l-4 ${getSeverityColor(warning.severity)}`}>
                  <CardContent className="p-4">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h3 className="mb-1">{warning.title}</h3>
                        <p className="text-sm text-gray-600 mb-2">{warning.content}</p>
                        <Badge variant="outline" className="text-xs">
                          {warning.documentId}
                        </Badge>
                      </div>
                      <Button 
                        size="sm" 
                        variant="outline"
                        onClick={() => onNavigate('search')}
                      >
                        Xem chi tiết
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        )}

        {/* System Statistics */}
        <div>
          <h2 className="mb-4">Thống kê hệ thống</h2>
          {loadingStats ? (
            <div className="flex justify-center py-6"><RefreshCw className="w-5 h-5 animate-spin text-gray-400" /></div>
          ) : systemStats.length === 0 ? (
            <p className="text-sm text-gray-400 text-center py-4">Không thể tải thống kê hệ thống</p>
          ) : (
            <div className="grid grid-cols-1 gap-3">
              {systemStats.map((stat, index) => (
                <Card key={index}>
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <p className="text-sm text-gray-600">{stat.label}</p>
                        <p className="text-lg font-semibold text-gray-800">{stat.value}</p>
                      </div>
                      <div className={`text-sm flex items-center gap-1 ${
                        stat.positive ? 'text-green-600' : 'text-orange-600'
                      }`}>
                        {stat.positive ? (
                          <TrendingUp className="w-4 h-4" />
                        ) : (
                          <AlertTriangle className="w-4 h-4" />
                        )}
                        {stat.change}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>

        {/* Quick Actions */}
        <Card>
          <CardHeader>
            <CardTitle>Hành động nhanh</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <Button 
              variant="outline" 
              className="w-full justify-start"
              onClick={() => onNavigate('map')}
            >
              <MapPin className="w-4 h-4 mr-2" />
              Tìm cơ quan ít tải nhất
            </Button>
            <Button 
              variant="outline" 
              className="w-full justify-start"
              onClick={() => onNavigate('submit')}
            >
              <FileText className="w-4 h-4 mr-2" />
              Nộp hồ sơ trực tuyến
            </Button>
            <Button 
              variant="outline" 
              className="w-full justify-start"
              onClick={() => onNavigate('chatbot')}
            >
              <Users className="w-4 h-4 mr-2" />
              Hỏi AI trợ lý
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}