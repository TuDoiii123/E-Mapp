import { useState } from 'react';
import { Settings, Globe, Bell, Shield, User, ChevronRight, Moon, Sun, Volume2, VolumeX, ArrowLeft } from 'lucide-react';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Switch } from './ui/switch';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Label } from './ui/label';
import { Avatar, AvatarFallback } from './ui/avatar';
import { useAuth } from '../contexts/AuthContext';
import React from 'react';
interface SettingsScreenProps {
  onNavigate: (screen: string) => void;
}

export function SettingsScreen({ onNavigate }: SettingsScreenProps) {
  const { user, logout } = useAuth();
  const [language, setLanguage] = useState('vi');
  const [darkMode, setDarkMode] = useState(false);
  const [notifications, setNotifications] = useState({
    push: true,
    sms: true,
    email: false,
    sound: true
  });

  const languages = [
    { code: 'vi', name: 'Tiếng Việt', flag: '🇻🇳' },
    { code: 'en', name: 'English', flag: '🇺🇸' },
    { code: 'km', name: 'ភាសាខ្មែរ', flag: '🇰🇭' },
    { code: 'zh', name: '中文', flag: '🇨🇳' }
  ];

  const vneidStatus = user?.isVNeIDVerified ? 'Đã kết nối' : 'Chưa kết nối';

  const settingSections = [
    {
      title: 'Tài khoản',
      icon: User,
      items: [
        { label: 'Thông tin cá nhân', value: user?.fullName || '—', action: () => {} },
        { label: 'Số CCCD', value: user?.cccdNumber || '—', action: () => {} },
        { label: 'Số điện thoại', value: user?.phone || '—', action: () => {} },
        { label: 'Email', value: user?.email || '—', action: () => {} }
      ]
    },
    {
      title: 'VNeID',
      icon: Shield,
      items: [
        { label: 'Trạng thái kết nối', value: vneidStatus, action: () => {} },
        { label: 'Quản lý chữ ký số', value: 'Xem chi tiết', action: () => {} },
        { label: 'Bảo mật tài khoản', value: 'Cấu hình', action: () => {} }
      ]
    }
  ];

  const handleLogout = async () => {
    await logout();
    onNavigate('login');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      
      {/* iOS Header */}  
      <div className="bg-white border-b border-gray-200">
        <div className="px-4 py-4">
          <div className="flex items-center space-x-3">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onNavigate('home')}
              className="w-10 h-10 rounded-full"
            >
              <ArrowLeft className="w-5 h-5" />
            </Button>
            <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-3">
              <Settings className="w-7 h-7" />
              Cài đặt
            </h1>
          </div>
        </div>
      </div>

      <div className="px-4 py-6 space-y-8">
        {/* User Profile */}
        <Card 
          className="cursor-pointer hover:shadow-md transition-shadow"
          onClick={() => onNavigate('account-detail')}
        >
          <CardContent className="p-4">
            <div className="flex items-center gap-4">
              <Avatar className="w-16 h-16">
                <AvatarFallback>
                  <User className="w-8 h-8" />
                </AvatarFallback>
              </Avatar>
              <div className="flex-1">
                <h3>{user?.fullName || '—'}</h3>
                <p className="text-sm text-gray-600">CCCD: {user?.cccdNumber || '—'}</p>
                <p className="text-sm text-green-600">✓ Tài khoản đã xác thực</p>
              </div>
              <ChevronRight className="w-5 h-5 text-gray-400" />
            </div>
          </CardContent>
        </Card>

        {/* Account & Security Settings */}
        {settingSections.map((section) => (
          <Card key={section.title}>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <section.icon className="w-5 h-5" />
                {section.title}
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {section.items.map((item, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between p-2 rounded-lg hover:bg-gray-50 cursor-pointer"
                  onClick={item.action}
                >
                  <Label className="cursor-pointer">{item.label}</Label>
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-gray-600">{item.value}</span>
                    <ChevronRight className="w-4 h-4 text-gray-400" />
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        ))}

        {/* Language Settings */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Globe className="w-5 h-5" />
              Ngôn ngữ & Hiển thị
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label>Ngôn ngữ giao diện</Label>
              <Select value={language} onValueChange={setLanguage}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {languages.map((lang) => (
                    <SelectItem key={lang.code} value={lang.code}>
                      <div className="flex items-center gap-2">
                        <span>{lang.flag}</span>
                        <span>{lang.name}</span>
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                {darkMode ? <Moon className="w-4 h-4" /> : <Sun className="w-4 h-4" />}
                <Label>Chế độ tối</Label>
              </div>
              <Switch
                checked={darkMode}
                onCheckedChange={setDarkMode}
              />
            </div>
          </CardContent>
        </Card>

        {/* Notification Settings */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Bell className="w-5 h-5" />
              Thông báo
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <Label>Thông báo đẩy</Label>
              <Switch
                checked={notifications.push}
                onCheckedChange={(checked : boolean) => 
                  setNotifications(prev => ({ ...prev, push: checked }))
                }
              />
            </div>

            <div className="flex items-center justify-between">
              <Label>SMS</Label>
              <Switch
                checked={notifications.sms}
                onCheckedChange={(checked : boolean) => 
                  setNotifications(prev => ({ ...prev, sms: checked }))
                }
              />
            </div>

            <div className="flex items-center justify-between">
              <Label>Email</Label>
              <Switch
                checked={notifications.email}
                onCheckedChange={(checked : boolean) => 
                  setNotifications(prev => ({ ...prev, email: checked }))
                }
              />
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                {notifications.sound ? <Volume2 className="w-4 h-4" /> : <VolumeX className="w-4 h-4" />}
                <Label>Âm thanh thông báo</Label>
              </div>
              <Switch
                checked={notifications.sound}
                onCheckedChange={(checked : boolean) => 
                  setNotifications(prev => ({ ...prev, sound: checked }))
                }
              />
            </div>
          </CardContent>
        </Card>

        {/* App Info */}
        <Card>
          <CardContent className="p-4 space-y-3">
            <div className="flex justify-between items-center">
              <Label>Phiên bản ứng dụng</Label>
              <span className="text-sm text-gray-600">v2.1.0</span>
            </div>
            <div className="flex justify-between items-center">
              <Label>Cập nhật lần cuối</Label>
              <span className="text-sm text-gray-600">24/01/2024</span>
            </div>
            <Button variant="outline" className="w-full">
              Kiểm tra cập nhật
            </Button>
          </CardContent>
        </Card>

        {/* Support & Legal */}
        <Card>
          <CardContent className="p-4 space-y-3">
            <Button variant="ghost" className="w-full justify-between">
              <span>Trung tâm trợ giúp</span>
              <ChevronRight className="w-4 h-4" />
            </Button>
            <Button variant="ghost" className="w-full justify-between">
              <span>Điều khoản sử dụng</span>
              <ChevronRight className="w-4 h-4" />
            </Button>
            <Button variant="ghost" className="w-full justify-between">
              <span>Chính sách bảo mật</span>
              <ChevronRight className="w-4 h-4" />
            </Button>
            <Button variant="ghost" className="w-full justify-between">
              <span>Liên hệ hỗ trợ</span>
              <ChevronRight className="w-4 h-4" />
            </Button>
          </CardContent>
        </Card>

        {/* Logout */}
        <Button 
          variant="destructive" 
          className="w-full"
          onClick={handleLogout}
        >
          Đăng xuất
        </Button>

        {/* App Credits */}
        <div className="text-center text-sm text-gray-500 pb-4">
          <p>Dịch vụ công số</p>
        </div>
      </div>
    </div>
  );
}