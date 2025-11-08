import { Search, FileText, Plus, MapPin, Star, Bell } from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import React from 'react';
interface HomeScreenProps {
  onNavigate: (screen: string) => void;
}

export function HomeScreen({ onNavigate }: HomeScreenProps) {
  const shortcuts = [
    {
      id: 'search',
      title: 'Tra cứu hồ sơ',
      icon: FileText,
      color: 'bg-red-500',
      description: 'Kiểm tra trạng thái hồ sơ'
    },
    {
      id: 'submit',
      title: 'Nộp hồ sơ mới',
      icon: Plus,
      color: 'bg-red-600',
      description: 'Nộp hồ sơ trực tuyến'
    },
    {
      id: 'map',
      title: 'Bản đồ dịch vụ',
      icon: MapPin,
      color: 'bg-red-400',
      description: 'Tìm cơ quan gần nhất'
    },
    {
      id: 'evaluation',
      title: 'Đánh giá cơ quan',
      icon: Star,
      color: 'bg-red-700',
      description: 'Góp ý chất lượng dịch vụ'
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* iOS Status Bar Space */}
      <div className="h-11 bg-white"></div>
      
      {/* iOS Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="px-4 py-4">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Chào bạn!</h1>
              <p className="text-lg text-gray-600 mt-1">Nguyễn Văn A</p>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onNavigate('notifications')}
              className="w-10 h-10 rounded-full relative"
            >
              <Bell className="w-6 h-6" />
              <Badge variant="destructive" className="absolute -top-1 -right-1 w-5 h-5 text-xs p-0 flex items-center justify-center">3</Badge>
            </Button>
          </div>

          {/* iOS Search Bar */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <Input
              placeholder="Tìm thủ tục, cơ quan, hoặc nhập số CCCD"
              className="pl-11 h-12 bg-gray-100 border-0 rounded-xl text-base"
            />
          </div>
        </div>
      </div>

      <div className="px-4 py-6 space-y-8">
        {/* Shortcuts */}
        <div>
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Dịch vụ chính</h2>
          <div className="grid grid-cols-2 gap-4">
            {shortcuts.map((shortcut) => (
              <Card 
                key={shortcut.id}
                className="cursor-pointer hover:scale-[0.98] transition-transform border-0 shadow-lg bg-white"
                onClick={() => onNavigate(shortcut.id)}
              >
                <CardContent className="p-5 text-center">
                  <div className={`w-14 h-14 ${shortcut.color} rounded-2xl flex items-center justify-center mx-auto mb-4`}>
                    <shortcut.icon className="w-7 h-7 text-white" />
                  </div>
                  <h3 className="text-base font-medium text-gray-900 mb-2">{shortcut.title}</h3>
                  <p className="text-sm text-gray-600 leading-relaxed">{shortcut.description}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* Thông báo trạng thái hồ sơ */}
        <Card className="border-0 shadow-lg bg-white">
          <CardHeader className="pb-4">
            <CardTitle className="text-lg font-semibold text-gray-900">Trạng thái hồ sơ gần nhất</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 bg-red-50 rounded-2xl">
                <div>
                  <p className="font-medium text-gray-900">Giấy phép lái xe</p>
                  <p className="text-sm text-gray-600 mt-1">Đã tiếp nhận</p>
                </div>
                <Badge variant="secondary" className="bg-orange-100 text-orange-800 px-3 py-1 rounded-full">Đang xử lý</Badge>
              </div>
              
              <div className="flex items-center justify-between p-4 bg-green-50 rounded-2xl">
                <div>
                  <p className="font-medium text-gray-900">Đăng ký kết hôn</p>
                  <p className="text-sm text-gray-600 mt-1">Hoàn tất</p>
                </div>
                <Badge className="bg-green-100 text-green-800 px-3 py-1 rounded-full">Xong</Badge>
              </div>
            </div>
            
            <Button 
              variant="outline" 
              className="w-full mt-6 h-12 rounded-xl border-red-200 text-red-600 hover:bg-red-50"
              onClick={() => onNavigate('search')}
            >
              Xem tất cả hồ sơ
            </Button>
          </CardContent>
        </Card>

        {/* Thống kê nhanh */}
        <div className="grid grid-cols-3 gap-4">
          <Card className="text-center border-0 shadow-lg bg-white">
            <CardContent className="p-5">
              <div className="text-3xl font-bold text-red-600 mb-2">5</div>
              <div className="text-sm text-gray-600">Hồ sơ đã nộp</div>
            </CardContent>
          </Card>
          <Card className="text-center border-0 shadow-lg bg-white">
            <CardContent className="p-5">
              <div className="text-3xl font-bold text-orange-600 mb-2">2</div>
              <div className="text-sm text-gray-600">Đang xử lý</div>
            </CardContent>
          </Card>
          <Card className="text-center border-0 shadow-lg bg-white">
            <CardContent className="p-5">
              <div className="text-3xl font-bold text-green-600 mb-2">3</div>
              <div className="text-sm text-gray-600">Hoàn thành</div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}