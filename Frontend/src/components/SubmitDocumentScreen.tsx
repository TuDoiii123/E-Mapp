import { useState } from 'react';
import { Upload, Camera, FileText, CheckCircle, Info, Plus, ArrowLeft } from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Textarea } from './ui/textarea';
import { Checkbox } from './ui/checkbox';
import { Progress } from './ui/progress';
import React from 'react';
interface SubmitDocumentScreenProps {
  onNavigate: (screen: string) => void;
}

export function SubmitDocumentScreen({ onNavigate }: SubmitDocumentScreenProps) {
  const [currentStep, setCurrentStep] = useState(1);
  const [selectedService, setSelectedService] = useState('');
  const [uploadedFiles, setUploadedFiles] = useState<string[]>([]);
  const [agreed, setAgreed] = useState(false);

  const services = [
    {
      id: 'marriage',
      name: 'Đăng ký kết hôn',
      category: 'Hộ tịch',
      time: '5-7 ngày',
      fee: '0 VNĐ',
      documents: ['CCCD gốc 2 bên', 'Đơn đăng ký', 'Giấy khám sức khỏe', 'Ảnh 4x6 (4 tấm)']
    },
    {
      id: 'license',
      name: 'Giấy phép kinh doanh',
      category: 'Kinh doanh',
      time: '15 ngày',
      fee: '100,000 VNĐ',
      documents: ['CCCD gốc', 'Đơn đăng ký', 'Giấy thuê mặt bằng', 'Ảnh 3x4 (2 tấm)']
    },
    {
      id: 'cccd',
      name: 'Cấp lại CCCD',
      category: 'Hành chính',
      time: '7-10 ngày',
      fee: '50,000 VNĐ',
      documents: ['CCCD cũ (nếu có)', 'Đơn đăng ký', 'Ảnh 3x4 (2 tấm)']
    }
  ];

  const requiredDocuments = selectedService ? 
    services.find(s => s.id === selectedService)?.documents || [] : [];

  const steps = [
    'Chọn loại hồ sơ',
    'Chuẩn bị tài liệu',
    'Upload hồ sơ',
    'Xác nhận & ký số'
  ];

  const handleFileUpload = (fileName: string) => {
    if (!uploadedFiles.includes(fileName)) {
      setUploadedFiles([...uploadedFiles, fileName]);
    }
  };

  const handleNext = () => {
    if (currentStep < 4) {
      setCurrentStep(currentStep + 1);
    }
  };

  const handleSubmit = () => {
    // Simulate submission
    alert('Nộp hồ sơ thành công! Mã hồ sơ: HS2024001');
    onNavigate('home');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* iOS Status Bar Space */}
      <div className="h-11 bg-white"></div>
      
      {/* iOS Header with progress */}
      <div className="bg-white border-b border-gray-200">
        <div className="px-4 py-4">
          <div className="flex items-center space-x-3 mb-6">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onNavigate('home')}
              className="w-10 h-10 rounded-full"
            >
              <ArrowLeft className="w-5 h-5" />
            </Button>
            <h1 className="text-2xl font-bold text-gray-900">Nộp hồ sơ trực tuyến</h1>
          </div>
          
          <div className="space-y-3">
            <div className="flex justify-between text-sm font-medium">
              <span className="text-gray-700">Bước {currentStep}/4</span>
              <span className="text-red-600">{Math.round((currentStep / 4) * 100)}%</span>
            </div>
            <Progress value={(currentStep / 4) * 100} className="h-2" />
          </div>

          <div className="flex justify-between mt-6">
            {steps.map((step, index) => (
              <div 
                key={index}
                className={`text-xs text-center flex-1 ${
                  index + 1 <= currentStep ? 'text-red-600' : 'text-gray-400'
                }`}
              >
                <div className={`w-8 h-8 rounded-full mx-auto mb-2 flex items-center justify-center ${
                  index + 1 <= currentStep ? 'bg-red-600 text-white' : 'bg-gray-200'
                }`}>
                  {index + 1 < currentStep ? <CheckCircle className="w-4 h-4" /> : index + 1}
                </div>
                <p className="font-medium">{step}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="px-4 pb-6">
        {currentStep === 1 && (
          <div className="space-y-6">
            <h2 className="text-xl font-semibold text-gray-900">Chọn loại hồ sơ</h2>
            
            <div className="space-y-4">
              {services.map((service) => (
                <Card 
                  key={service.id}
                  className={`cursor-pointer transition-all border-0 shadow-lg hover:scale-[0.98] ${
                    selectedService === service.id ? 'ring-2 ring-red-500' : ''
                  }`}
                  onClick={() => setSelectedService(service.id)}
                >
                  <CardContent className="p-5">
                    <div className="flex justify-between items-start mb-3">
                      <h3 className="font-semibold text-gray-900">{service.name}</h3>
                      <Badge variant="outline" className="px-3 py-1 rounded-full border-gray-300">{service.category}</Badge>
                    </div>
                    <div className="grid grid-cols-2 gap-4 text-sm text-gray-600">
                      <div>
                        <p>Thời gian: <span className="font-medium text-gray-900">{service.time}</span></p>
                      </div>
                      <div>
                        <p>Lệ phí: <span className="font-medium text-gray-900">{service.fee}</span></p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            <Button 
              onClick={handleNext}
              disabled={!selectedService}
              className="w-full h-12 rounded-xl bg-red-600 hover:bg-red-700"
            >
              Tiếp tục
            </Button>
          </div>
        )}

        {currentStep === 2 && (
          <div className="space-y-4">
            <h2>Chuẩn bị tài liệu</h2>
            
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Info className="w-5 h-5" />
                  Giấy tờ cần chuẩn bị
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2">
                  {requiredDocuments.map((doc, index) => (
                    <li key={index} className="flex items-center gap-2">
                      <div className="w-2 h-2 bg-blue-600 rounded-full" />
                      {doc}
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Lưu ý quan trọng</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2 text-sm">
                <p>• Ảnh ch��p phải rõ nét, đủ ánh sáng</p>
                <p>• File không quá 5MB</p>
                <p>• Chấp nhận định dạng: JPG, PNG, PDF</p>
                <p>• Không được chỉnh sửa hoặc photoshop</p>
              </CardContent>
            </Card>

            <Button onClick={handleNext} className="w-full">
              Đã chuẩn bị xong
            </Button>
          </div>
        )}

        {currentStep === 3 && (
          <div className="space-y-4">
            <h2>Upload hồ sơ</h2>
            
            {requiredDocuments.map((doc, index) => (
              <Card key={index}>
                <CardContent className="p-4">
                  <div className="flex items-center justify-between mb-3">
                    <h3>{doc}</h3>
                    {uploadedFiles.includes(doc) ? (
                      <CheckCircle className="w-5 h-5 text-green-600" />
                    ) : (
                      <Badge variant="outline">Bắt buộc</Badge>
                    )}
                  </div>
                  
                  {uploadedFiles.includes(doc) ? (
                    <div className="bg-green-50 p-3 rounded-lg">
                      <p className="text-sm text-green-700">✓ Đã upload thành công</p>
                    </div>
                  ) : (
                    <div className="space-y-2">
                      <Button 
                        variant="outline" 
                        className="w-full"
                        onClick={() => handleFileUpload(doc)}
                      >
                        <Upload className="w-4 h-4 mr-2" />
                        Chọn file
                      </Button>
                      <Button 
                        variant="outline" 
                        className="w-full"
                        onClick={() => handleFileUpload(doc)}
                      >
                        <Camera className="w-4 h-4 mr-2" />
                        Chụp ảnh
                      </Button>
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}

            <Button 
              onClick={handleNext}
              disabled={uploadedFiles.length !== requiredDocuments.length}
              className="w-full"
            >
              Tiếp tục
            </Button>
          </div>
        )}

        {currentStep === 4 && (
          <div className="space-y-4">
            <h2>Xác nhận & ký số</h2>
            
            <Card>
              <CardHeader>
                <CardTitle>Thông tin hồ sơ</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div>
                  <Label>Loại hồ sơ</Label>
                  <p>{services.find(s => s.id === selectedService)?.name}</p>
                </div>
                <div>
                  <Label>Số tài liệu đã upload</Label>
                  <p>{uploadedFiles.length} file</p>
                </div>
                <div>
                  <Label>Lệ phí</Label>
                  <p>{services.find(s => s.id === selectedService)?.fee}</p>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Ghi chú bổ sung</CardTitle>
              </CardHeader>
              <CardContent>
                <Textarea 
                  placeholder="Nhập ghi chú nếu có (không bắt buộc)"
                  rows={3}
                />
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-4">
                <div className="flex items-start space-x-2">
                  <Checkbox 
                    id="agree" 
                    checked={agreed}
                    onCheckedChange={(checked: boolean | 'indeterminate') => setAgreed(checked === true)}
                  />
                  <Label htmlFor="agree" className="text-sm">
                    Tôi xác nhận các thông tin trên là chính xác và chịu trách nhiệm về tính xác thực của hồ sơ đã nộp.
                  </Label>
                </div>
              </CardContent>
            </Card>

            <div className="space-y-2">
              <Button 
                onClick={handleSubmit}
                disabled={!agreed}
                className="w-full"
              >
                Ký số & Nộp hồ sơ
              </Button>
              <p className="text-xs text-gray-600 text-center">
                Hồ sơ sẽ được xử lý trong vòng {services.find(s => s.id === selectedService)?.time}
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}