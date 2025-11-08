import { useState } from 'react';
import { Bell, Filter, FileText, Building, Star, Clock, CheckCircle, AlertCircle, ArrowLeft } from 'lucide-react';
import { Button } from './ui/button';
import { Card, CardContent } from './ui/card';
import { Badge } from './ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import React from 'react';
interface NotificationScreenProps {
  onNavigate: (screen: string) => void;
}

export function NotificationScreen({ onNavigate }: NotificationScreenProps) {
  const [filter, setFilter] = useState('all');

  const notifications = [
    {
      id: 1,
      type: 'document',
      title: 'Hồ sơ đã được xử lý xong',
      content: 'Hồ sơ "Đăng ký kết hôn" của bạn đã được hoàn tất. Vui lòng đến nhận kết quả.',
      time: '2 phút trước',
      read: false,
      priority: 'high',
      documentId: 'HS001'
    },
    {
      id: 2,
      type: 'document',
      title: 'Cần bổ sung hồ sơ',
      content: 'Hồ sơ "Cấp lại CCCD" cần bổ sung ảnh 4x6. Hạn cuối: 28/01/2024',
      time: '1 giờ trước',
      read: false,
      priority: 'high',
      documentId: 'HS003'
    },
    {
      id: 3,
      type: 'office',
      title: 'Thông báo nghỉ lễ',
      content: 'UBND Quận 1 sẽ nghỉ lễ Tết Nguyên đán từ 08/02 - 17/02/2024',
      time: '3 giờ trước',
      read: true,
      priority: 'medium'
    },
    {
      id: 4,
      type: 'evaluation',
      title: 'Đề nghị đánh giá dịch vụ',
      content: 'Bạn đã hoàn thành thủ tục tại Sở Tài nguyên Môi trường. Vui lòng đánh giá chất lượng dịch vụ.',
      time: '1 ngày trước',
      read: true,
      priority: 'low'
    },
    {
      id: 5,
      type: 'document',
      title: 'Hồ sơ được tiếp nhận',
      content: 'Hồ sơ "Giấy phép lái xe" đã được tiếp nhận. Mã hồ sơ: HS002',
      time: '2 ngày trước',
      read: true,
      priority: 'medium',
      documentId: 'HS002'
    }
  ];

  const history = [
    {
      id: 'HS001',
      title: 'Đăng ký kết hôn',
      status: 'Hoàn thành',
      date: '2024-01-20',
      office: 'UBND Quận 1'
    },
    {
      id: 'HS002',
      title: 'Giấy phép lái xe',
      status: 'Đang xử lý',
      date: '2024-01-22',
      office: 'Sở GTVT TP.HCM'
    },
    {
      id: 'HS003',
      title: 'Cấp lại CCCD',
      status: 'Cần bổ sung',
      date: '2024-01-25',
      office: 'Công an Quận 3'
    }
  ];

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case 'document': return <FileText className="w-5 h-5" />;
      case 'office': return <Building className="w-5 h-5" />;
      case 'evaluation': return <Star className="w-5 h-5" />;
      default: return <Bell className="w-5 h-5" />;
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'text-red-600';
      case 'medium': return 'text-orange-600';
      case 'low': return 'text-blue-600';
      default: return 'text-gray-600';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Hoàn thành': return 'bg-green-100 text-green-800';
      case 'Đang xử lý': return 'bg-blue-100 text-blue-800';
      case 'Cần bổ sung': return 'bg-orange-100 text-orange-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'Hoàn thành': return <CheckCircle className="w-4 h-4 text-green-600" />;
      case 'Đang xử lý': return <Clock className="w-4 h-4 text-blue-600" />;
      case 'Cần bổ sung': return <AlertCircle className="w-4 h-4 text-orange-600" />;
      default: return <FileText className="w-4 h-4" />;
    }
  };

  const filteredNotifications = filter === 'all' 
    ? notifications 
    : notifications.filter(n => n.type === filter);

  const unreadCount = notifications.filter(n => !n.read).length;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* iOS Status Bar Space */}
      <div className="h-11 bg-white"></div>
      
      {/* iOS Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="px-4 py-4">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center space-x-3">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => onNavigate('home')}
                className="w-10 h-10 rounded-full"
              >
                <ArrowLeft className="w-5 h-5" />
              </Button>
              <h1 className="text-2xl font-bold text-gray-900">Thông báo & Lịch sử</h1>
            </div>
            <div className="flex items-center gap-3">
              <Badge variant="destructive" className="px-2 py-1 rounded-full">{unreadCount}</Badge>
              <Button variant="ghost" size="sm" className="w-10 h-10 rounded-full">
                <Filter className="w-5 h-5" />
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="px-4 pb-6">
        <Tabs defaultValue="notifications" className="w-full">
          <TabsList className="grid w-full grid-cols-2 h-12 bg-gray-100 rounded-xl p-1">
            <TabsTrigger value="notifications" className="rounded-lg font-medium">
              Thông báo ({unreadCount})
            </TabsTrigger>
            <TabsTrigger value="history" className="rounded-lg font-medium">
              Lịch sử ({history.length})
            </TabsTrigger>
          </TabsList>

          <TabsContent value="notifications" className="space-y-4">
            {/* Filter */}
            <Select value={filter} onValueChange={setFilter}>
              <SelectTrigger>
                <SelectValue placeholder="Lọc thông báo" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Tất cả</SelectItem>
                <SelectItem value="document">Hồ sơ</SelectItem>
                <SelectItem value="office">Cơ quan</SelectItem>
                <SelectItem value="evaluation">Đánh giá</SelectItem>
              </SelectContent>
            </Select>

            {/* Notifications list */}
            <div className="space-y-3">
              {filteredNotifications.map((notification) => (
                <Card 
                  key={notification.id}
                  className={`cursor-pointer transition-all ${
                    !notification.read ? 'bg-blue-50 border-blue-200' : ''
                  }`}
                  onClick={() => {
                    if (notification.documentId) {
                      onNavigate('search');
                    }
                  }}
                >
                  <CardContent className="p-4">
                    <div className="flex items-start gap-3">
                      <div className={`p-2 rounded-full ${
                        !notification.read ? 'bg-blue-100' : 'bg-gray-100'
                      }`}>
                        {getNotificationIcon(notification.type)}
                      </div>
                      
                      <div className="flex-1">
                        <div className="flex items-start justify-between mb-1">
                          <h3 className={!notification.read ? '' : 'text-gray-700'}>
                            {notification.title}
                          </h3>
                          <div className="flex items-center gap-2">
                            {!notification.read && (
                              <div className="w-2 h-2 bg-blue-600 rounded-full" />
                            )}
                            <span className="text-xs text-gray-500">
                              {notification.time}
                            </span>
                          </div>
                        </div>
                        
                        <p className={`text-sm ${
                          !notification.read ? 'text-gray-700' : 'text-gray-600'
                        }`}>
                          {notification.content}
                        </p>
                        
                        <div className="flex items-center gap-2 mt-2">
                          <Badge 
                            variant="outline"
                            className={getPriorityColor(notification.priority)}
                          >
                            {notification.type === 'document' ? 'Hồ sơ' :
                             notification.type === 'office' ? 'Cơ quan' : 'Đánh giá'}
                          </Badge>
                          {notification.documentId && (
                            <Badge variant="secondary">
                              {notification.documentId}
                            </Badge>
                          )}
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            <Button variant="outline" className="w-full">
              Đánh dấu tất cả đã đọc
            </Button>
          </TabsContent>

          <TabsContent value="history" className="space-y-4">
            <div className="space-y-3">
              {history.map((item) => (
                <Card 
                  key={item.id}
                  className="cursor-pointer hover:shadow-md transition-shadow"
                  onClick={() => onNavigate('search')}
                >
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between mb-2">
                      <h3>{item.title}</h3>
                      <Badge className={getStatusColor(item.status)}>
                        {item.status}
                      </Badge>
                    </div>
                    
                    <div className="flex items-center justify-between text-sm text-gray-600 mb-3">
                      <span>Mã: {item.id}</span>
                      <span>{item.date}</span>
                    </div>

                    <div className="flex items-center gap-2">
                      {getStatusIcon(item.status)}
                      <span className="text-sm">{item.office}</span>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            <Button 
              variant="outline" 
              className="w-full"
              onClick={() => onNavigate('submit')}
            >
              Nộp hồ sơ mới
            </Button>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}