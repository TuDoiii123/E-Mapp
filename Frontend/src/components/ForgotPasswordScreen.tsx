import { useState } from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { ArrowLeft, Shield, Phone, Mail } from 'lucide-react';
import { Badge } from './ui/badge';
import React from 'react';
interface ForgotPasswordScreenProps {
  onNavigate: (screen: string) => void;
}

export function ForgotPasswordScreen({ onNavigate }: ForgotPasswordScreenProps) {
  const [step, setStep] = useState(1); // 1: nhập CCCD, 2: chọn phương thức, 3: nhập OTP, 4: đặt lại mật khẩu
  const [cccdNumber, setCccdNumber] = useState('');
  const [selectedMethod, setSelectedMethod] = useState('');
  const [otp, setOtp] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  const handleNext = () => {
    if (step < 4) {
      setStep(step + 1);
    } else {
      // Hoàn tất đặt lại mật khẩu
      onNavigate('login');
    }
  };

  const renderStepContent = () => {
    switch (step) {
      case 1:
        return (
          <div className="space-y-4">
            <div className="text-center mb-4">
              <p className="text-gray-600">Nhập số CCCD để xác thực danh t��nh</p>
            </div>
            <div className="space-y-2">
              <Label htmlFor="cccd">Số CCCD</Label>
              <Input
                id="cccd"
                type="text"
                placeholder="Nhập số CCCD"
                value={cccdNumber}
                onChange={(e) => setCccdNumber(e.target.value)}
                maxLength={12}
              />
            </div>
            <Button 
              onClick={handleNext}
              className="w-full bg-red-600 hover:bg-red-700"
              disabled={!cccdNumber || cccdNumber.length !== 12}
            >
              Tiếp tục
            </Button>
          </div>
        );

      case 2:
        return (
          <div className="space-y-4">
            <div className="text-center mb-4">
              <p className="text-gray-600">Chọn phương thức nhận mã xác thực</p>
            </div>
            
            <div className="space-y-3">
              <div 
                className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                  selectedMethod === 'sms' ? 'border-red-500 bg-red-50' : 'border-gray-200'
                }`}
                onClick={() => setSelectedMethod('sms')}
              >
                <div className="flex items-center space-x-3">
                  <Phone className="w-5 h-5 text-red-600" />
                  <div>
                    <p className="font-medium">SMS</p>
                    <p className="text-sm text-gray-600">Gửi mã đến số điện thoại ****1234</p>
                  </div>
                </div>
              </div>

              <div 
                className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                  selectedMethod === 'email' ? 'border-red-500 bg-red-50' : 'border-gray-200'
                }`}
                onClick={() => setSelectedMethod('email')}
              >
                <div className="flex items-center space-x-3">
                  <Mail className="w-5 h-5 text-red-600" />
                  <div>
                    <p className="font-medium">Email</p>
                    <p className="text-sm text-gray-600">Gửi mã đến email n****@example.com</p>
                  </div>
                </div>
              </div>
            </div>

            <Button 
              onClick={handleNext}
              className="w-full bg-red-600 hover:bg-red-700"
              disabled={!selectedMethod}
            >
              Gửi mã xác thực
            </Button>
          </div>
        );

      case 3:
        return (
          <div className="space-y-4">
            <div className="text-center mb-4">
              <p className="text-gray-600">
                Nhập mã xác thực đã được gửi đến {selectedMethod === 'sms' ? 'số điện thoại' : 'email'} của bạn
              </p>
              <div className="flex items-center justify-center mt-3">
                <Badge variant="secondary" className="bg-orange-100 text-orange-800">
                  Mã có hiệu lực trong 5 phút
                </Badge>
              </div>
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="otp">Mã xác thực (6 số)</Label>
              <Input
                id="otp"
                type="text"
                placeholder="Nhập mã xác thực"
                value={otp}
                onChange={(e) => setOtp(e.target.value.replace(/\D/g, ''))}
                maxLength={6}
                className="text-center text-lg tracking-widest"
              />
            </div>

            <Button 
              onClick={handleNext}
              className="w-full bg-red-600 hover:bg-red-700"
              disabled={!otp || otp.length !== 6}
            >
              Xác thực
            </Button>

            <Button 
              variant="ghost" 
              className="w-full"
              onClick={() => {/* Gửi lại mã */}}
            >
              Gửi lại mã
            </Button>
          </div>
        );

      case 4:
        return (
          <div className="space-y-4">
            <div className="text-center mb-4">
              <p className="text-gray-600">Đặt mật khẩu mới cho tài khoản của bạn</p>
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="newPassword">Mật khẩu mới</Label>
              <Input
                id="newPassword"
                type="password"
                placeholder="Nhập mật khẩu mới"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="confirmPassword">Xác nhận mật khẩu</Label>
              <Input
                id="confirmPassword"
                type="password"
                placeholder="Nhập lại mật khẩu mới"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
              />
            </div>

            <div className="text-sm text-gray-600 space-y-1">
              <p>Mật khẩu phải có:</p>
              <ul className="list-disc list-inside space-y-1 ml-2">
                <li>Ít nhất 8 ký tự</li>
                <li>Ít nhất 1 chữ hoa</li>
                <li>Ít nhất 1 chữ số</li>
                <li>Ít nhất 1 ký tự đặc biệt</li>
              </ul>
            </div>

            <Button 
              onClick={handleNext}
              className="w-full bg-red-600 hover:bg-red-700"
              disabled={!newPassword || !confirmPassword || newPassword !== confirmPassword}
            >
              Đặt lại mật khẩu
            </Button>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="w-full max-w-md mx-auto space-y-6">
        {/* iOS Style Header */}
        <div className="bg-white shadow-sm sticky top-0 z-10">
          <div className="flex items-center justify-between p-4">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => step === 1 ? onNavigate('login') : setStep(step - 1)}
              className="p-2"
            >
              <ArrowLeft className="w-5 h-5" />
            </Button>
            <h1 className="text-lg font-semibold text-gray-900">Quên mật khẩu</h1>
            <div className="w-9"></div> {/* Spacer for center alignment */}
          </div>
        </div>

        <div className="px-4 pt-6">
          <div className="text-center mb-6">
            <div className="mx-auto w-16 h-16 bg-red-600 rounded-full flex items-center justify-center mb-4">
              <Shield className="w-8 h-8 text-white" />
            </div>
            <h2 className="text-lg font-medium text-gray-900">Khôi phục mật khẩu</h2>
            <p className="text-sm text-gray-600 mt-1">Làm theo hướng dẫn để đặt lại mật khẩu</p>
          </div>
        </div>

        {/* Progress indicator */}
        <div className="px-4 mb-6">
          <div className="flex items-center justify-center space-x-2 mb-3">
            {[1, 2, 3, 4].map((i) => (
              <div
                key={i}
                className={`w-3 h-3 rounded-full transition-colors ${
                  i <= step ? 'bg-red-600' : 'bg-gray-300'
                }`}
              />
            ))}
          </div>
          <div className="text-center">
            <p className="text-sm text-gray-600">
              Bước {step} / 4: {' '}
              {step === 1 && 'Xác thực danh tính'}
              {step === 2 && 'Chọn phương thức'}
              {step === 3 && 'Nhập mã xác thực'}
              {step === 4 && 'Đặt mật khẩu mới'}
            </p>
          </div>
        </div>

        {/* Form */}
        <div className="px-4">
          <Card className="border-0 shadow-lg">
            <CardContent className="p-6">
              {renderStepContent()}
            </CardContent>
          </Card>
        </div>

        {/* Support info */}
        <div className="px-4 pb-8">
          <div className="text-center text-sm text-gray-500 bg-white rounded-lg p-4">
            <p>Cần hỗ trợ? Gọi hotline:</p>
            <p className="font-medium text-red-600">1900 1234</p>
            <p className="text-xs mt-1">Hoạt động 24/7</p>
          </div>
        </div>
      </div>
    </div>
  );
}