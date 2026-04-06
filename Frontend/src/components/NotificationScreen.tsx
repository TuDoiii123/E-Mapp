import { useState, useEffect } from 'react';
import { Bell, Filter, FileText, Building, Star, Clock, CheckCircle, AlertCircle, ArrowLeft, RefreshCw } from 'lucide-react';
import { Button } from './ui/button';
import { Card, CardContent } from './ui/card';
import { Badge } from './ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import React from 'react';
import * as adminSvc from '../services/adminService';

interface NotificationScreenProps {
  onNavigate: (screen: string) => void;
}

// Map application status → notification shape
function appToNotification(app: any) {
  const STATUS_TITLE: Record<string, string> = {
    submitted:      'Hồ sơ đã được tiếp nhận',
    under_review:   'Hồ sơ đang được xem xét',
    need_more_info: 'Cần bổ sung hồ sơ',
    approved:       'Hồ sơ đã được duyệt',
    rejected:       'Hồ sơ bị từ chối',
  };
  const PRIORITY: Record<string, string> = {
    need_more_info: 'high',
    rejected:       'high',
    approved:       'medium',
    under_review:   'medium',
    submitted:      'low',
  };
  const st = app.currentStatus || 'submitted';
  return {
    id:         app.id,
    type:       'document',
    title:      STATUS_TITLE[st] || 'Cập nhật hồ sơ',
    content:    `Hồ sơ "${app.procedureName || app.procedureId}" - Mã: ${app.id}`,
    time:       app.updatedAt ? new Date(app.updatedAt).toLocaleDateString('vi-VN') : '',
    read:       st === 'submitted',
    priority:   PRIORITY[st] || 'low',
    documentId: app.id,
  };
}

const STATUS_VI: Record<string, string> = {
  submitted:      'Đã nộp',
  under_review:   'Đang xét',
  need_more_info: 'Cần bổ sung',
  approved:       'Đã duyệt',
  rejected:       'Từ chối',
};
const STATUS_COLOR: Record<string, string> = {
  submitted:      'bg-blue-100 text-blue-800',
  under_review:   'bg-yellow-100 text-yellow-800',
  need_more_info: 'bg-orange-100 text-orange-800',
  approved:       'bg-green-100 text-green-800',
  rejected:       'bg-red-100 text-red-800',
};

export function NotificationScreen({ onNavigate }: NotificationScreenProps) {
  const [filter,       setFilter]       = useState('all');
  const [applications, setApplications] = useState<any[]>([]);
  const [loading,      setLoading]      = useState(true);
  const [readSet,      setReadSet]      = useState<Set<string>>(new Set());

  useEffect(() => {
    adminSvc.getMyApplications()
      .then(r => setApplications(r.data || []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const notifications = applications.map(appToNotification).map(n => ({
    ...n,
    read: readSet.has(String(n.id)) || n.read,
  }));

  const history = applications.map(app => ({
    id:     app.id,
    title:  app.procedureName || app.procedureId || 'Hồ sơ',
    status: STATUS_VI[app.currentStatus] || app.currentStatus,
    statusKey: app.currentStatus,
    date:   app.createdAt ? new Date(app.createdAt).toLocaleDateString('vi-VN') : '',
    office: app.agencyName || app.agencyId || '',
  }));

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

  const getStatusColor = (statusKey: string) =>
    STATUS_COLOR[statusKey] || 'bg-gray-100 text-gray-800';

  const getStatusIcon = (statusKey: string) => {
    switch (statusKey) {
      case 'approved':       return <CheckCircle className="w-4 h-4 text-green-600" />;
      case 'under_review':   return <Clock className="w-4 h-4 text-blue-600" />;
      case 'need_more_info': return <AlertCircle className="w-4 h-4 text-orange-600" />;
      case 'rejected':       return <AlertCircle className="w-4 h-4 text-red-600" />;
      default:               return <FileText className="w-4 h-4 text-gray-400" />;
    }
  };

  const filteredNotifications = filter === 'all'
    ? notifications
    : notifications.filter(n => n.type === filter);

  const handleMarkAllRead = () => {
    setReadSet(new Set(notifications.map(n => String(n.id))));
  };

  return (
    <div className="min-h-screen bg-gray-50">
      
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
            {loading && (
              <div className="flex justify-center py-8">
                <RefreshCw className="w-5 h-5 animate-spin text-gray-400" />
              </div>
            )}
            {!loading && filteredNotifications.length === 0 && (
              <p className="text-center text-gray-400 py-8 text-sm">Không có thông báo</p>
            )}
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

            <Button variant="outline" className="w-full" onClick={handleMarkAllRead}>
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
                      <Badge className={getStatusColor(item.statusKey)}>
                        {item.status}
                      </Badge>
                    </div>

                    <div className="flex items-center justify-between text-sm text-gray-600 mb-3">
                      <span>Mã: {item.id}</span>
                      <span>{item.date}</span>
                    </div>

                    <div className="flex items-center gap-2">
                      {getStatusIcon(item.statusKey)}
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