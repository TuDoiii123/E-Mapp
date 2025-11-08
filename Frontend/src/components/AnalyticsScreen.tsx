import { TrendingUp, Clock, AlertTriangle, CheckCircle, Users, FileText, MapPin, Lightbulb, ArrowLeft } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { Button } from './ui/button';
import React from 'react';
interface AnalyticsScreenProps {
  onNavigate: (screen: string) => void;
}

export function AnalyticsScreen({ onNavigate }: AnalyticsScreenProps) {
  const personalStats = {
    totalDocuments: 5,
    completed: 3,
    inProgress: 2,
    avgProcessingTime: 8,
    successRate: 95
  };

  const aiSuggestions = [
    {
      id: 1,
      type: 'office',
      title: 'Cơ quan ít tải',
      content: 'UBND Quận 7 hiện tại ít quá tải hơn Quận 1. Thời gian xử lý nhanh hơn 2-3 ngày.',
      action: 'Xem bản đồ',
      icon: MapPin,
      priority: 'high'
    },
    {
      id: 2,
      type: 'online',
      title: 'Nộp trực tuyến',
      content: 'Thủ tục "Giấy phép kinh doanh" nộp online sẽ nhanh hơn 5 ngày so với nộp trực tiếp.',
      action: 'Nộp ngay',
      icon: FileText,
      priority: 'medium'
    },
    {
      id: 3,
      type: 'timing',
      title: 'Thời điểm tốt nhất',
      content: 'Nộp hồ sơ vào thứ 3-4 sẽ được xử lý nhanh hơn. Tránh thứ 2 và cuối tuần.',
      action: 'Đặt lịnh báo',
      icon: Clock,
      priority: 'low'
    }
  ];

  const processWarnings = [
    {
      id: 1,
      title: 'Hồ sơ chậm tiến độ',
      content: 'Giấy phép lái xe đã 5 ngày chưa có phản hồi. Bình thường là 3-4 ngày.',
      severity: 'warning',
      documentId: 'HS002'
    },
    {
      id: 2,
      title: 'Sắp hết hạn bổ sung',
      content: 'Hồ sơ CCCD cần bổ sung trong 3 ngày nữa.',
      severity: 'urgent',
      documentId: 'HS003'
    }
  ];

  const systemStats = [
    { label: 'Hồ sơ được xử lý hôm nay', value: '1,234', change: '+12%', positive: true },
    { label: 'Thời gian xử lý trung bình', value: '6.5 ngày', change: '-1.2 ngày', positive: true },
    { label: 'Tỷ lệ hài lòng', value: '94.2%', change: '+2.1%', positive: true },
    { label: 'Cơ quan hoạt động', value: '98/102', change: '4 bảo trì', positive: false }
  ];

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
      {/* iOS Status Bar Space */}
      <div className="h-11 bg-white"></div>
      
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
          <div className="ml-13">
            <p className="text-gray-600">Thông tin thông minh để tối ưu trải nghiệm</p>
          </div>
        </div>
      </div>

      <div className="px-4 py-6 space-y-8">
        {/* Personal Statistics */}
        <div>
          <h2 className="mb-4">Thống kê cá nhân</h2>
          <div className="grid grid-cols-2 gap-4 mb-4">
            <Card>
              <CardContent className="p-4 text-center">
                <div className="text-2xl mb-1">{personalStats.completed}</div>
                <div className="text-sm text-gray-600">Hồ sơ hoàn thành</div>
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
                <span>{Math.round((personalStats.completed / personalStats.totalDocuments) * 100)}%</span>
              </div>
              <Progress value={(personalStats.completed / personalStats.totalDocuments) * 100} />
              <div className="flex justify-between text-sm text-gray-600 mt-2">
                <span>{personalStats.completed}/{personalStats.totalDocuments} hồ sơ</span>
                <span>Thời gian TB: {personalStats.avgProcessingTime} ngày</span>
              </div>
            </CardContent>
          </Card>
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
          <div className="grid grid-cols-1 gap-3">
            {systemStats.map((stat, index) => (
              <Card key={index}>
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <p className="text-sm text-gray-600">{stat.label}</p>
                      <p className="text-lg">{stat.value}</p>
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