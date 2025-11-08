import { useState } from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { ArrowLeft, Shield, Eye, EyeOff, Check, AlertCircle } from 'lucide-react';
import { Checkbox } from './ui/checkbox';
import { Alert, AlertDescription } from './ui/alert';
import { useAuth } from '../contexts/AuthContext';
import React from 'react';

interface RegisterScreenProps {
  onNavigate: (screen: string) => void;
}

export function RegisterScreen({ onNavigate }: RegisterScreenProps) {
  const [step, setStep] = useState(1); // 1: thông tin cơ bản, 2: xác thực OTP, 3: hoàn tất
  const [formData, setFormData] = useState({
    cccdNumber: '',
    fullName: '',
    dateOfBirth: '',
    phone: '',
    email: '',
    password: '',
    confirmPassword: '',
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [otp, setOtp] = useState('');
  const [agreeTerms, setAgreeTerms] = useState(false);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { register } = useAuth();

  const handleInputChange = (field: string, value: string) => {
    if (field === 'cccdNumber') {
      value = value.replace(/\D/g, '').slice(0, 12);
    } else if (field === 'phone') {
      value = value.replace(/\D/g, '').slice(0, 11);
    }
    setFormData(prev => ({ ...prev, [field]: value }));
    setError('');
  };

  const handleNext = async () => {
    if (step === 1) {
      // Validate step 1
      if (!formData.cccdNumber || formData.cccdNumber.length !== 12) {
        setError('Số CCCD phải có 12 chữ số');
        return;
      }
      if (!formData.fullName || formData.fullName.length < 2) {
        setError('Họ và tên phải có ít nhất 2 ký tự');
        return;
      }
      if (!formData.dateOfBirth) {
        setError('Vui lòng chọn ngày sinh');
        return;
      }
      if (!formData.phone || formData.phone.length < 10) {
        setError('Số điện thoại không hợp lệ');
        return;
      }
      if (!formData.email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
        setError('Email không hợp lệ');
        return;
      }
      if (!isPasswordValid) {
        setError('Mật khẩu không đáp ứng yêu cầu');
        return;
      }
      if (formData.password !== formData.confirmPassword) {
        setError('Mật khẩu xác nhận không khớp');
        return;
      }
      if (!agreeTerms) {
        setError('Vui lòng đồng ý với điều khoản sử dụng');
        return;
      }
      setError('');
      setStep(2);
    } else if (step === 2) {
      // Validate OTP
      if (!otp || otp.length !== 6) {
        setError('Vui lòng nhập mã OTP 6 chữ số');
        return;
      }
      // For demo, accept 123456 as valid OTP
      if (otp !== '123456') {
        setError('Mã OTP không đúng. Sử dụng 123456 cho demo.');
        return;
      }
      setError('');
      // Proceed to registration
      await handleRegister();
    } else {
      // Step 3 - Navigate to login
      onNavigate('login');
    }
  };

  const handleRegister = async () => {
    setIsLoading(true);
    setError('');

    try {
      await register({
        ...formData,
        otp: otp || '123456', // For demo
        useVNeID: false
      });
      setStep(3);
    } catch (err: any) {
      setError(err.message || 'Đăng ký thất bại. Vui lòng thử lại.');
      // Stay on step 2 if registration fails
    } finally {
      setIsLoading(false);
    }
  };

  const validatePassword = (password: string) => {
    const requirements = {
      length: password.length >= 8,
      uppercase: /[A-Z]/.test(password),
      number: /\d/.test(password),
      special: /[!@#$%^&*(),.?":{}|<>]/.test(password),
    };
    return requirements;
  };

  const passwordRequirements = validatePassword(formData.password);
  const isPasswordValid = Object.values(passwordRequirements).every(Boolean);

  const renderStepContent = () => {
    switch (step) {
      case 1:
        return (
          <div className="space-y-4">
            <div className="text-center mb-4">
              <p className="text-gray-600">Tạo tài khoản dịch vụ công số</p>
            </div>

            {error && (
              <Alert variant="destructive">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="cccd">Số CCCD *</Label>
                <Input
                  id="cccd"
                  type="text"
                  placeholder="Nhập số CCCD"
                  value={formData.cccdNumber}
                  onChange={(e) => handleInputChange('cccdNumber', e.target.value)}
                  maxLength={12}
                  disabled={isLoading}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="fullName">Họ và tên *</Label>
                <Input
                  id="fullName"
                  type="text"
                  placeholder="Nhập họ và tên"
                  value={formData.fullName}
                  onChange={(e) => handleInputChange('fullName', e.target.value)}
                  disabled={isLoading}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="dateOfBirth">Ngày sinh *</Label>
                <Input
                  id="dateOfBirth"
                  type="date"
                  value={formData.dateOfBirth}
                  onChange={(e) => handleInputChange('dateOfBirth', e.target.value)}
                  disabled={isLoading}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="phone">Số điện thoại *</Label>
                <Input
                  id="phone"
                  type="tel"
                  placeholder="Nhập số điện thoại"
                  value={formData.phone}
                  onChange={(e) => handleInputChange('phone', e.target.value)}
                  disabled={isLoading}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="email">Email *</Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="Nhập địa chỉ email"
                  value={formData.email}
                  onChange={(e) => handleInputChange('email', e.target.value)}
                  disabled={isLoading}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="password">Mật khẩu *</Label>
                <div className="relative">
                  <Input
                    id="password"
                    type={showPassword ? 'text' : 'password'}
                    placeholder="Nhập mật khẩu"
                    value={formData.password}
                    onChange={(e) => handleInputChange('password', e.target.value)}
                    disabled={isLoading}
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                    onClick={() => setShowPassword(!showPassword)}
                  >
                    {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </Button>
                </div>
                
                {formData.password && (
                  <div className="text-sm space-y-1">
                    <div className={`flex items-center space-x-2 ${passwordRequirements.length ? 'text-green-600' : 'text-gray-500'}`}>
                      <Check className={`w-3 h-3 ${passwordRequirements.length ? 'opacity-100' : 'opacity-30'}`} />
                      <span>Ít nhất 8 ký tự</span>
                    </div>
                    <div className={`flex items-center space-x-2 ${passwordRequirements.uppercase ? 'text-green-600' : 'text-gray-500'}`}>
                      <Check className={`w-3 h-3 ${passwordRequirements.uppercase ? 'opacity-100' : 'opacity-30'}`} />
                      <span>Ít nhất 1 chữ hoa</span>
                    </div>
                    <div className={`flex items-center space-x-2 ${passwordRequirements.number ? 'text-green-600' : 'text-gray-500'}`}>
                      <Check className={`w-3 h-3 ${passwordRequirements.number ? 'opacity-100' : 'opacity-30'}`} />
                      <span>Ít nhất 1 chữ số</span>
                    </div>
                    <div className={`flex items-center space-x-2 ${passwordRequirements.special ? 'text-green-600' : 'text-gray-500'}`}>
                      <Check className={`w-3 h-3 ${passwordRequirements.special ? 'opacity-100' : 'opacity-30'}`} />
                      <span>Ít nhất 1 ký tự đặc biệt</span>
                    </div>
                  </div>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="confirmPassword">Xác nhận mật khẩu *</Label>
                <div className="relative">
                  <Input
                    id="confirmPassword"
                    type={showConfirmPassword ? 'text' : 'password'}
                    placeholder="Nhập lại mật khẩu"
                    value={formData.confirmPassword}
                    onChange={(e) => handleInputChange('confirmPassword', e.target.value)}
                    disabled={isLoading}
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  >
                    {showConfirmPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </Button>
                </div>
                {formData.confirmPassword && formData.password !== formData.confirmPassword && (
                  <p className="text-sm text-red-600">Mật khẩu không khớp</p>
                )}
              </div>

              <div className="p-4 bg-gray-50 rounded-lg border">
                <div className="flex items-start space-x-3">
                  <Checkbox 
                    id="terms" 
                    checked={agreeTerms}
                    onCheckedChange={(checked : boolean) => setAgreeTerms(checked as boolean)}
                    className="mt-1"
                  />
                  <div className="flex-1">
                    <Label htmlFor="terms" className="text-sm leading-relaxed cursor-pointer">
                      Tôi đã đọc và đồng ý với{' '}
                      <button className="text-red-600 underline font-medium hover:text-red-700">
                        Điều khoản sử dụng
                      </button>
                      {' '}và{' '}
                      <button className="text-red-600 underline font-medium hover:text-red-700">
                        Chính sách bảo mật
                      </button>
                      {' '}của dịch vụ công số
                    </Label>
                    <p className="text-xs text-gray-500 mt-1">
                      Bằng việc tạo tài khoản, bạn xác nhận rằng thông tin cung cấp là chính xác và đầy đủ
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <Button 
              onClick={handleNext}
              className="w-full bg-red-600 hover:bg-red-700"
              disabled={!formData.cccdNumber || !formData.fullName || !formData.phone || 
                       !formData.email || !isPasswordValid || 
                       formData.password !== formData.confirmPassword || !agreeTerms || isLoading}
            >
              {isLoading ? 'Đang xử lý...' : 'Tiếp tục'}
            </Button>
          </div>
        );

      case 2:
        return (
          <div className="space-y-4">
            <div className="text-center mb-4">
              <p className="text-gray-600">Mã xác thực đã được gửi đến số điện thoại {formData.phone}</p>
              <p className="text-sm text-gray-500 mt-2">(Sử dụng mã 123456 cho demo)</p>
            </div>

            {error && (
              <Alert variant="destructive">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}
            
            <div className="space-y-2">
              <Label htmlFor="otp">Mã xác thực (6 số)</Label>
              <Input
                id="otp"
                type="text"
                placeholder="Nhập mã xác thực"
                value={otp}
                onChange={(e) => {
                  setOtp(e.target.value.replace(/\D/g, '').slice(0, 6));
                  setError('');
                }}
                maxLength={6}
                className="text-center text-lg tracking-widest"
                disabled={isLoading}
              />
            </div>

            <Button 
              onClick={handleNext}
              className="w-full bg-red-600 hover:bg-red-700"
              disabled={!otp || otp.length !== 6 || isLoading}
            >
              {isLoading ? 'Đang đăng ký...' : 'Xác thực'}
            </Button>

            <Button 
              variant="ghost" 
              className="w-full"
              onClick={() => {
                setOtp('');
                setError('');
                // In production, this would resend OTP
              }}
              disabled={isLoading}
            >
              Gửi lại mã
            </Button>
          </div>
        );

      case 3:
        return (
          <div className="space-y-4 text-center">
            <div className="mx-auto w-16 h-16 bg-green-100 rounded-full flex items-center justify-center">
              <Check className="w-8 h-8 text-green-600" />
            </div>
            
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Đăng ký thành công!</h3>
              <p className="text-gray-600">Tài khoản của bạn đã được tạo thành công. Bạn có thể đăng nhập ngay bây giờ.</p>
            </div>

            <Button 
              onClick={handleNext}
              className="w-full bg-red-600 hover:bg-red-700"
            >
              Đăng nhập ngay
            </Button>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="w-full max-w-md mx-auto space-y-6 p-4">
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
            <h1 className="text-lg font-semibold text-gray-900">Đăng ký</h1>
            <div className="w-9"></div> {/* Spacer for center alignment */}
          </div>
        </div>

        <div className="px-4 pt-6">
          <div className="text-center mb-6">
            <div className="mx-auto w-16 h-16 bg-red-600 rounded-full flex items-center justify-center mb-4">
              <Shield className="w-8 h-8 text-white" />
            </div>
            <h2 className="text-lg font-medium text-gray-900">Tạo tài khoản mới</h2>
            <p className="text-sm text-gray-600 mt-1">Dịch vụ công số Việt Nam</p>
          </div>
        </div>

        {/* Progress indicator */}
        <div className="px-4 mb-6">
          <div className="flex items-center justify-center space-x-2 mb-3">
            {[1, 2, 3].map((i) => (
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
              Bước {step} / 3: {' '}
              {step === 1 && 'Thông tin cá nhân'}
              {step === 2 && 'Xác thực OTP'}
              {step === 3 && 'Hoàn tất'}
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