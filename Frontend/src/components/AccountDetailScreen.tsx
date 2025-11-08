import { useState } from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Avatar, AvatarFallback, AvatarImage } from './ui/avatar';
import { ArrowLeft, Camera, Edit3, Save, X, Eye, EyeOff } from 'lucide-react';
import { Badge } from './ui/badge';
import { Separator } from './ui/separator';
import React from 'react';
interface AccountDetailScreenProps {
  onNavigate: (screen: string) => void;
}

export function AccountDetailScreen({ onNavigate }: AccountDetailScreenProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [isChangingPassword, setIsChangingPassword] = useState(false);
  const [showPasswords, setShowPasswords] = useState({
    current: false,
    new: false,
    confirm: false,
  });

  const [userInfo, setUserInfo] = useState({
    cccdNumber: '001234567890',
    fullName: 'Nguyễn Văn A',
    dateOfBirth: '1990-01-15',
    phone: '0987654321',
    email: 'nguyenvana@gmail.com',
    address: 'Số 1 Trần Hưng Đạo, Hoàn Kiếm, Hà Nội',
    avatar: '',
  });

  const [editForm, setEditForm] = useState({ ...userInfo });
  const [passwordForm, setPasswordForm] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: '',
  });

  const handleEdit = () => {
    setIsEditing(true);
    setEditForm({ ...userInfo });
  };

  const handleSave = () => {
    setUserInfo({ ...editForm });
    setIsEditing(false);
  };

  const handleCancel = () => {
    setEditForm({ ...userInfo });
    setIsEditing(false);
  };

  const handlePasswordChange = () => {
    // Xử lý đổi mật khẩu
    setPasswordForm({
      currentPassword: '',
      newPassword: '',
      confirmPassword: '',
    });
    setIsChangingPassword(false);
  };

  const togglePasswordVisibility = (field: 'current' | 'new' | 'confirm') => {
    setShowPasswords(prev => ({
      ...prev,
      [field]: !prev[field]
    }));
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* iOS Status Bar Space */}
      <div className="h-11 bg-white"></div>
      
      {/* iOS Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="flex items-center justify-between px-4 py-4">
          <div className="flex items-center space-x-3">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onNavigate('settings')}
              className="w-10 h-10 rounded-full"
            >
              <ArrowLeft className="w-5 h-5" />
            </Button>
            <h1 className="text-xl font-semibold text-gray-900">Thông tin tài khoản</h1>
          </div>
          {!isEditing && !isChangingPassword && (
            <Button
              variant="ghost"
              size="sm"
              onClick={handleEdit}
            >
              <Edit3 className="w-4 h-4" />
            </Button>
          )}
        </div>
      </div>

      <div className="p-4 space-y-6">
        {/* Avatar Section */}
        <Card>
          <CardContent className="p-6">
            <div className="flex flex-col items-center space-y-4">
              <div className="relative">
                <Avatar className="w-24 h-24">
                  <AvatarImage src={userInfo.avatar} />
                  <AvatarFallback className="text-xl bg-red-100 text-red-600">
                    {userInfo.fullName.split(' ').map(n => n[0]).join('')}
                  </AvatarFallback>
                </Avatar>
                {isEditing && (
                  <Button
                    size="sm"
                    className="absolute -bottom-2 -right-2 rounded-full w-8 h-8 p-0 bg-red-600 hover:bg-red-700"
                  >
                    <Camera className="w-4 h-4" />
                  </Button>
                )}
              </div>
              <div className="text-center">
                <h2 className="text-lg font-semibold">{userInfo.fullName}</h2>
                <p className="text-sm text-gray-600">CCCD: {userInfo.cccdNumber}</p>
                <Badge className="mt-2 bg-green-100 text-green-800">Đã xác thực</Badge>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Personal Information */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              Thông tin cá nhân
              {isEditing && (
                <div className="flex space-x-2">
                  <Button size="sm" variant="outline" onClick={handleCancel}>
                    <X className="w-4 h-4" />
                  </Button>
                  <Button size="sm" onClick={handleSave} className="bg-red-600 hover:bg-red-700">
                    <Save className="w-4 h-4" />
                  </Button>
                </div>
              )}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-4">
              <div className="space-y-2">
                <Label>Họ và tên</Label>
                {isEditing ? (
                  <Input
                    value={editForm.fullName}
                    onChange={(e) => setEditForm(prev => ({ ...prev, fullName: e.target.value }))}
                  />
                ) : (
                  <p className="text-gray-900">{userInfo.fullName}</p>
                )}
              </div>

              <div className="space-y-2">
                <Label>Ngày sinh</Label>
                {isEditing ? (
                  <Input
                    type="date"
                    value={editForm.dateOfBirth}
                    onChange={(e) => setEditForm(prev => ({ ...prev, dateOfBirth: e.target.value }))}
                  />
                ) : (
                  <p className="text-gray-900">{new Date(userInfo.dateOfBirth).toLocaleDateString('vi-VN')}</p>
                )}
              </div>

              <div className="space-y-2">
                <Label>Số điện thoại</Label>
                {isEditing ? (
                  <Input
                    value={editForm.phone}
                    onChange={(e) => setEditForm(prev => ({ ...prev, phone: e.target.value }))}
                  />
                ) : (
                  <p className="text-gray-900">{userInfo.phone}</p>
                )}
              </div>

              <div className="space-y-2">
                <Label>Email</Label>
                {isEditing ? (
                  <Input
                    type="email"
                    value={editForm.email}
                    onChange={(e) => setEditForm(prev => ({ ...prev, email: e.target.value }))}
                  />
                ) : (
                  <p className="text-gray-900">{userInfo.email}</p>
                )}
              </div>

              <div className="space-y-2">
                <Label>Địa chỉ</Label>
                {isEditing ? (
                  <Input
                    value={editForm.address}
                    onChange={(e) => setEditForm(prev => ({ ...prev, address: e.target.value }))}
                  />
                ) : (
                  <p className="text-gray-900">{userInfo.address}</p>
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Security Section */}
        <Card>
          <CardHeader>
            <CardTitle>Bảo mật</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {!isChangingPassword ? (
              <div>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">Mật khẩu</p>
                    <p className="text-sm text-gray-600">Đổi mật khẩu định kỳ để bảo mật tài khoản</p>
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setIsChangingPassword(true)}
                  >
                    Đổi mật khẩu
                  </Button>
                </div>
                
                <Separator className="my-4" />
                
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">Xác thực 2 lớp</p>
                    <p className="text-sm text-gray-600">Tăng cường bảo mật với OTP</p>
                  </div>
                  <Badge className="bg-green-100 text-green-800">Đã bật</Badge>
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="font-medium">Đổi mật khẩu</h3>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setIsChangingPassword(false)}
                  >
                    <X className="w-4 h-4" />
                  </Button>
                </div>

                <div className="space-y-4">
                  <div className="space-y-2">
                    <Label>Mật khẩu hiện tại</Label>
                    <div className="relative">
                      <Input
                        type={showPasswords.current ? 'text' : 'password'}
                        value={passwordForm.currentPassword}
                        onChange={(e) => setPasswordForm(prev => ({ ...prev, currentPassword: e.target.value }))}
                      />
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                        onClick={() => togglePasswordVisibility('current')}
                      >
                        {showPasswords.current ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                      </Button>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label>Mật khẩu mới</Label>
                    <div className="relative">
                      <Input
                        type={showPasswords.new ? 'text' : 'password'}
                        value={passwordForm.newPassword}
                        onChange={(e) => setPasswordForm(prev => ({ ...prev, newPassword: e.target.value }))}
                      />
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                        onClick={() => togglePasswordVisibility('new')}
                      >
                        {showPasswords.new ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                      </Button>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label>Xác nhận mật khẩu mới</Label>
                    <div className="relative">
                      <Input
                        type={showPasswords.confirm ? 'text' : 'password'}
                        value={passwordForm.confirmPassword}
                        onChange={(e) => setPasswordForm(prev => ({ ...prev, confirmPassword: e.target.value }))}
                      />
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                        onClick={() => togglePasswordVisibility('confirm')}
                      >
                        {showPasswords.confirm ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                      </Button>
                    </div>
                  </div>

                  <Button
                    onClick={handlePasswordChange}
                    className="w-full bg-red-600 hover:bg-red-700"
                    disabled={!passwordForm.currentPassword || !passwordForm.newPassword || 
                             passwordForm.newPassword !== passwordForm.confirmPassword}
                  >
                    Cập nhật mật khẩu
                  </Button>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Activity Section */}
        <Card>
          <CardHeader>
            <CardTitle>Hoạt động gần đây</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div>
                  <p className="font-medium">Đăng nhập</p>
                  <p className="text-sm text-gray-600">25/09/2024 14:30</p>
                </div>
                <Badge variant="secondary">Thành công</Badge>
              </div>
              
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div>
                  <p className="font-medium">Cập nhật thông tin</p>
                  <p className="text-sm text-gray-600">20/09/2024 09:15</p>
                </div>
                <Badge variant="secondary">Thành công</Badge>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}