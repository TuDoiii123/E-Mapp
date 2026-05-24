import { useState, useRef } from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Avatar, AvatarFallback, AvatarImage } from './ui/avatar';
import {
  ArrowLeft, Camera, Edit3, Save, X, Eye, EyeOff, Loader2,
  CheckCircle, AlertCircle, LogOut,
} from 'lucide-react';
import { Badge } from './ui/badge';
import { Separator } from './ui/separator';
import { useAuth } from '../contexts/AuthContext';
import { authAPI, apiRequest, API_BASE_URL } from '../services/api';
import React from 'react';

interface AccountDetailScreenProps {
  onNavigate: (screen: string) => void;
}

type Toast = { type: 'success' | 'error'; msg: string };

export function AccountDetailScreen({ onNavigate }: AccountDetailScreenProps) {
  const { user, refreshProfile } = useAuth();

  /* ── form state ─────────────────────────────────── */
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving,  setIsSaving]  = useState(false);
  const [toast,     setToast]     = useState<Toast | null>(null);

  const initInfo = () => ({
    cccdNumber:  user?.cccdNumber  || '',
    fullName:    user?.fullName    || '',
    dateOfBirth: user?.dateOfBirth || '',
    phone:       user?.phone       || '',
    email:       user?.email       || '',
    address:     user?.address     || '',
    avatarUrl:   user?.avatarUrl   || '',
  });

  const [displayInfo, setDisplayInfo] = useState(initInfo);
  const [editForm,    setEditForm]    = useState(initInfo);

  /* ── password state ─────────────────────────────── */
  const [isChangingPassword, setIsChangingPassword] = useState(false);
  const [pwSaving, setPwSaving]   = useState(false);
  const [pwError,  setPwError]    = useState('');
  const [showPw, setShowPw] = useState({ current: false, new: false, confirm: false });
  const [passwordForm, setPasswordForm] = useState({
    currentPassword: '', newPassword: '', confirmPassword: '',
  });

  /* ── avatar state ───────────────────────────────── */
  const [avatarUploading, setAvatarUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  /* ── helpers ────────────────────────────────────── */
  const showToast = (type: Toast['type'], msg: string) => {
    setToast({ type, msg });
    setTimeout(() => setToast(null), 3500);
  };

  const avatarSrc = displayInfo.avatarUrl
    ? (displayInfo.avatarUrl.startsWith('http')
        ? displayInfo.avatarUrl
        : `${API_BASE_URL.replace('/api', '')}${displayInfo.avatarUrl}`)
    : '';

  const initials = displayInfo.fullName
    .split(' ')
    .filter(Boolean)
    .map(n => n[0])
    .join('')
    .slice(0, 2)
    .toUpperCase();

  /* ── actions ────────────────────────────────────── */
  const handleEdit = () => {
    setEditForm({
      cccdNumber:  user?.cccdNumber  || '',
      fullName:    user?.fullName    || '',
      dateOfBirth: user?.dateOfBirth || '',
      phone:       user?.phone       || '',
      email:       user?.email       || '',
      address:     user?.address     || '',
      avatarUrl:   user?.avatarUrl   || '',
    });
    setIsEditing(true);
  };

  const handleCancel = () => {
    setEditForm(displayInfo);
    setIsEditing(false);
  };

  const handleSave = async () => {
    setIsSaving(true);
    try {
      await authAPI.updateProfile({
        fullName:    editForm.fullName,
        phone:       editForm.phone,
        email:       editForm.email,
        dateOfBirth: editForm.dateOfBirth,
        address:     editForm.address,
      });
      setDisplayInfo({ ...editForm });
      setIsEditing(false);
      await refreshProfile();
      showToast('success', 'Cập nhật thông tin thành công');
    } catch (err: any) {
      showToast('error', err.message || 'Cập nhật thất bại. Vui lòng thử lại.');
    } finally {
      setIsSaving(false);
    }
  };

  const handleAvatarClick = () => {
    if (fileInputRef.current) fileInputRef.current.click();
  };

  const handleAvatarChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setAvatarUploading(true);
    try {
      const res = await authAPI.uploadAvatar(file);
      const newUrl = res.data.avatarUrl;
      setDisplayInfo(prev => ({ ...prev, avatarUrl: newUrl }));
      setEditForm(prev  => ({ ...prev, avatarUrl: newUrl }));
      await refreshProfile();
      showToast('success', 'Cập nhật ảnh đại diện thành công');
    } catch (err: any) {
      showToast('error', err.message || 'Tải ảnh thất bại');
    } finally {
      setAvatarUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const handlePasswordChange = async () => {
    setPwError('');
    if (passwordForm.newPassword !== passwordForm.confirmPassword) {
      setPwError('Mật khẩu xác nhận không khớp');
      return;
    }
    if (passwordForm.newPassword.length < 8) {
      setPwError('Mật khẩu mới phải có ít nhất 8 ký tự');
      return;
    }
    setPwSaving(true);
    try {
      await apiRequest('/auth/change-password', {
        method: 'POST',
        body: JSON.stringify({
          currentPassword: passwordForm.currentPassword,
          newPassword:     passwordForm.newPassword,
        }),
      });
      setPasswordForm({ currentPassword: '', newPassword: '', confirmPassword: '' });
      setIsChangingPassword(false);
      showToast('success', 'Đổi mật khẩu thành công');
    } catch (err: any) {
      setPwError(err.message || 'Đổi mật khẩu thất bại');
    } finally {
      setPwSaving(false);
    }
  };

  /* ── render ─────────────────────────────────────── */
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hidden file input */}
      <input
        ref={fileInputRef}
        type="file"
        accept="image/jpeg,image/png,image/gif,image/webp"
        className="hidden"
        onChange={handleAvatarChange}
      />

      {/* Toast */}
      {toast && (
        <div className={`fixed top-4 left-1/2 -translate-x-1/2 z-50 flex items-center gap-2 px-4 py-3 rounded-xl shadow-lg text-white text-sm font-medium transition-all
          ${toast.type === 'success' ? 'bg-green-600' : 'bg-red-600'}`}>
          {toast.type === 'success'
            ? <CheckCircle className="w-4 h-4 shrink-0" />
            : <AlertCircle className="w-4 h-4 shrink-0" />}
          {toast.msg}
        </div>
      )}

      {/* Header */}
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
          <div className="flex items-center gap-1">
            {!isEditing && !isChangingPassword && (
              <Button variant="ghost" size="sm" onClick={handleEdit}>
                <Edit3 className="w-4 h-4" />
              </Button>
            )}
            <Button
              variant="ghost"
              size="sm"
              className="text-red-600 hover:text-red-700 hover:bg-red-50"
              onClick={async () => { await logout(); onNavigate('login'); }}
              title="Đăng xuất"
            >
              <LogOut className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </div>

      <div className="p-4 space-y-6">
        {/* Avatar Section */}
        <Card>
          <CardContent className="p-6">
            <div className="flex flex-col items-center space-y-4">
              <div className="relative">
                <Avatar className="w-24 h-24">
                  <AvatarImage src={avatarSrc} />
                  <AvatarFallback className="text-xl bg-red-100 text-red-600">
                    {initials || '?'}
                  </AvatarFallback>
                </Avatar>

                {/* Upload overlay */}
                <button
                  type="button"
                  onClick={handleAvatarClick}
                  disabled={avatarUploading}
                  className="absolute -bottom-2 -right-2 w-8 h-8 rounded-full bg-red-600 hover:bg-red-700 text-white flex items-center justify-center shadow-md disabled:opacity-60"
                >
                  {avatarUploading
                    ? <Loader2 className="w-4 h-4 animate-spin" />
                    : <Camera className="w-4 h-4" />}
                </button>
              </div>

              <div className="text-center">
                <h2 className="text-lg font-semibold">{displayInfo.fullName}</h2>
                <p className="text-sm text-gray-600">CCCD: {displayInfo.cccdNumber}</p>
                <Badge className="mt-2 bg-green-100 text-green-800 hover:bg-green-100">
                  {user?.isVNeIDVerified ? '✓ Đã xác thực VNeID' : 'Chưa xác thực VNeID'}
                </Badge>
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
                  <Button size="sm" variant="outline" onClick={handleCancel} disabled={isSaving}>
                    <X className="w-4 h-4" />
                  </Button>
                  <Button
                    size="sm"
                    onClick={handleSave}
                    disabled={isSaving}
                    className="bg-red-600 hover:bg-red-700 min-w-[72px]"
                  >
                    {isSaving ? <Loader2 className="w-4 h-4 animate-spin" /> : <><Save className="w-4 h-4 mr-1" />Lưu</>}
                  </Button>
                </div>
              )}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Họ tên */}
            <div className="space-y-1">
              <Label>Họ và tên</Label>
              {isEditing
                ? <Input value={editForm.fullName} onChange={e => setEditForm(p => ({ ...p, fullName: e.target.value }))} />
                : <p className="text-gray-900 py-1">{displayInfo.fullName || '—'}</p>}
            </div>

            {/* Ngày sinh */}
            <div className="space-y-1">
              <Label>Ngày sinh</Label>
              {isEditing
                ? <Input type="date" value={editForm.dateOfBirth} onChange={e => setEditForm(p => ({ ...p, dateOfBirth: e.target.value }))} />
                : <p className="text-gray-900 py-1">
                    {displayInfo.dateOfBirth
                      ? (() => { try { return new Date(displayInfo.dateOfBirth).toLocaleDateString('vi-VN'); } catch { return displayInfo.dateOfBirth; } })()
                      : '—'}
                  </p>}
            </div>

            {/* SĐT */}
            <div className="space-y-1">
              <Label>Số điện thoại</Label>
              {isEditing
                ? <Input value={editForm.phone} onChange={e => setEditForm(p => ({ ...p, phone: e.target.value }))} inputMode="tel" />
                : <p className="text-gray-900 py-1">{displayInfo.phone || '—'}</p>}
            </div>

            {/* Email */}
            <div className="space-y-1">
              <Label>Email</Label>
              {isEditing
                ? <Input type="email" value={editForm.email} onChange={e => setEditForm(p => ({ ...p, email: e.target.value }))} />
                : <p className="text-gray-900 py-1">{displayInfo.email || '—'}</p>}
            </div>

            {/* Địa chỉ */}
            <div className="space-y-1">
              <Label>Địa chỉ</Label>
              {isEditing
                ? <Input value={editForm.address} placeholder="Số nhà, đường, phường/xã, quận/huyện, tỉnh/thành" onChange={e => setEditForm(p => ({ ...p, address: e.target.value }))} />
                : <p className="text-gray-900 py-1">{displayInfo.address || '—'}</p>}
            </div>

            {/* CCCD (read-only) */}
            <div className="space-y-1">
              <Label className="text-gray-500">Số CCCD</Label>
              <p className="text-gray-500 py-1 text-sm">{displayInfo.cccdNumber} (không thể thay đổi)</p>
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
              <>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">Mật khẩu</p>
                    <p className="text-sm text-gray-600">Đổi mật khẩu định kỳ để bảo mật tài khoản</p>
                  </div>
                  <Button variant="outline" size="sm" onClick={() => setIsChangingPassword(true)}>
                    Đổi mật khẩu
                  </Button>
                </div>

                <Separator />

                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">Xác thực 2 lớp</p>
                    <p className="text-sm text-gray-600">Tăng cường bảo mật với OTP</p>
                  </div>
                  <Badge className="bg-green-100 text-green-800 hover:bg-green-100">Đã bật</Badge>
                </div>
              </>
            ) : (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="font-medium">Đổi mật khẩu</h3>
                  <Button variant="ghost" size="sm" onClick={() => { setIsChangingPassword(false); setPwError(''); }}>
                    <X className="w-4 h-4" />
                  </Button>
                </div>

                {/* Current pw */}
                <div className="space-y-2">
                  <Label>Mật khẩu hiện tại</Label>
                  <div className="relative">
                    <Input
                      type={showPw.current ? 'text' : 'password'}
                      value={passwordForm.currentPassword}
                      onChange={e => setPasswordForm(p => ({ ...p, currentPassword: e.target.value }))}
                    />
                    <Button type="button" variant="ghost" size="sm"
                      className="absolute right-0 top-0 h-full px-3 hover:bg-transparent"
                      onClick={() => setShowPw(p => ({ ...p, current: !p.current }))}>
                      {showPw.current ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </Button>
                  </div>
                </div>

                {/* New pw */}
                <div className="space-y-2">
                  <Label>Mật khẩu mới</Label>
                  <div className="relative">
                    <Input
                      type={showPw.new ? 'text' : 'password'}
                      value={passwordForm.newPassword}
                      onChange={e => setPasswordForm(p => ({ ...p, newPassword: e.target.value }))}
                    />
                    <Button type="button" variant="ghost" size="sm"
                      className="absolute right-0 top-0 h-full px-3 hover:bg-transparent"
                      onClick={() => setShowPw(p => ({ ...p, new: !p.new }))}>
                      {showPw.new ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </Button>
                  </div>
                  <p className="text-xs text-gray-500">Tối thiểu 8 ký tự</p>
                </div>

                {/* Confirm pw */}
                <div className="space-y-2">
                  <Label>Xác nhận mật khẩu mới</Label>
                  <div className="relative">
                    <Input
                      type={showPw.confirm ? 'text' : 'password'}
                      value={passwordForm.confirmPassword}
                      onChange={e => setPasswordForm(p => ({ ...p, confirmPassword: e.target.value }))}
                    />
                    <Button type="button" variant="ghost" size="sm"
                      className="absolute right-0 top-0 h-full px-3 hover:bg-transparent"
                      onClick={() => setShowPw(p => ({ ...p, confirm: !p.confirm }))}>
                      {showPw.confirm ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </Button>
                  </div>
                </div>

                {pwError && (
                  <div className="flex items-center gap-2 text-sm text-red-600 bg-red-50 p-3 rounded-lg">
                    <AlertCircle className="w-4 h-4 shrink-0" />
                    {pwError}
                  </div>
                )}

                <Button
                  onClick={handlePasswordChange}
                  className="w-full bg-red-600 hover:bg-red-700"
                  disabled={pwSaving || !passwordForm.currentPassword || !passwordForm.newPassword || !passwordForm.confirmPassword}
                >
                  {pwSaving ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : null}
                  Cập nhật mật khẩu
                </Button>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Recent Activity — placeholder */}
        <Card>
          <CardHeader>
            <CardTitle>Hoạt động gần đây</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div>
                  <p className="font-medium text-sm">Đăng nhập</p>
                  <p className="text-xs text-gray-500">{new Date().toLocaleDateString('vi-VN')}</p>
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
