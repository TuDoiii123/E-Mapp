import React, { useState } from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Eye, EyeOff, Shield, AlertCircle } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { Alert, AlertDescription } from './ui/alert';

interface LoginScreenProps {
  onLogin: () => void;
  onNavigate?: (screen: string) => void;
}

export function LoginScreen({ onLogin, onNavigate }: LoginScreenProps) {
  const [cccdNumber, setCccdNumber] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { login } = useAuth();

  const handleLogin = async () => {
    if (!cccdNumber || !password) {
      setError('Vui lòng nhập đầy đủ thông tin');
      return;
    }

    setError('');
    setIsLoading(true);

    try {
      await login(cccdNumber, password);
      onLogin();
    } catch (err: any) {
      setError(err.message || 'Đăng nhập thất bại. Vui lòng thử lại.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleLogin();
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="w-full max-w-md mx-auto space-y-6 p-4">
        {/* Logo và tiêu đề */}
        <div className="text-center pt-12 pb-8">
          <div className="mx-auto w-20 h-20 bg-red-600 rounded-full flex items-center justify-center mb-6">
            <Shield className="w-10 h-10 text-white" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Dịch vụ công số</h1>
          <p className="text-gray-600">Đăng nhập bằng Căn cước công dân</p>
        </div>

        {/* Form đăng nhập */}
        <Card className="border-0 shadow-lg">
          <CardHeader>
            <CardTitle>Đăng nhập</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {error && (
              <Alert variant="destructive">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            <div className="space-y-2">
              <Label htmlFor="cccd">Số CCCD</Label>
              <Input
                id="cccd"
                type="text"
                placeholder="Nhập số CCCD"
                value={cccdNumber}
                onChange={(e) => {
                  setCccdNumber(e.target.value.replace(/\D/g, ''));
                  setError('');
                }}
                onKeyPress={handleKeyPress}
                maxLength={12}
                disabled={isLoading}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="password">Mật khẩu</Label>
              <div className="relative">
                <Input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  placeholder="Nhập mật khẩu"
                  value={password}
                  onChange={(e) => {
                    setPassword(e.target.value);
                    setError('');
                  }}
                  onKeyPress={handleKeyPress}
                  disabled={isLoading}
                />
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                  onClick={() => setShowPassword(!showPassword)}
                  disabled={isLoading}
                >
                  {showPassword ? (
                    <EyeOff className="h-4 w-4" />
                  ) : (
                    <Eye className="h-4 w-4" />
                  )}
                </Button>
              </div>
            </div>

            <Button 
              onClick={handleLogin}
              className="w-full bg-red-600 hover:bg-red-700"
              disabled={!cccdNumber || !password || isLoading}
            >
              {isLoading ? 'Đang đăng nhập...' : 'Đăng nhập'}
            </Button>

            <div className="space-y-2">
              <Button 
                variant="ghost" 
                className="w-full"
                onClick={() => onNavigate?.('forgot-password')}
              >
                Quên mật khẩu?
              </Button>
              <Button 
                variant="outline" 
                className="w-full"
                onClick={() => onNavigate?.('register')}
              >
                Đăng ký tài khoản
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Thông tin bổ sung */}
        <div className="text-center text-sm text-gray-500">
          <p>Cần hỗ trợ? Gọi hotline: 1900 1234</p>
        </div>
      </div>
    </div>
  );
}