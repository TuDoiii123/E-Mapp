import { useState } from 'react';
import { Search, FileText, Clock, CheckCircle, AlertCircle, Phone, MessageCircle } from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import React from 'react';
interface SearchDocumentScreenProps {
  onNavigate: (screen: string) => void;
}

export function SearchDocumentScreen({ onNavigate }: SearchDocumentScreenProps) {
  const [searchValue, setSearchValue] = useState('');
  const [selectedDocument, setSelectedDocument] = useState<any>(null);

  const recentSearches = [
    '012345678901',
    '098765432109',
    'Giấy phép lái xe'
  ];

  const documents = [
    {
      id: 'HS001',
      title: 'Đăng ký kết hôn',
      status: 'Hoàn thành',
      submitDate: '2024-01-15',
      completedDate: '2024-01-20',
      office: 'UBND Quận 1',
      progress: 100,
      steps: [
        { name: 'Tiếp nhận', date: '2024-01-15 09:30', completed: true },
        { name: 'Đang xử lý', date: '2024-01-16 14:20', completed: true },
        { name: 'Hoàn tất', date: '2024-01-20 16:45', completed: true }
      ]
    },
    {
      id: 'HS002',
      title: 'Giấy phép lái xe',
      status: 'Đang xử lý',
      submitDate: '2024-01-22',
      office: 'Sở GTVT TP.HCM',
      progress: 60,
      steps: [
        { name: 'Tiếp nhận', date: '2024-01-22 10:15', completed: true },
        { name: 'Đang xử lý', date: '2024-01-23 11:30', completed: true },
        { name: 'Hoàn tất', date: '', completed: false }
      ]
    },
    {
      id: 'HS003',
      title: 'Cấp lại CCCD',
      status: 'Cần bổ sung',
      submitDate: '2024-01-25',
      office: 'Công an Quận 3',
      progress: 40,
      needSupplementary: true,
      steps: [
        { name: 'Tiếp nhận', date: '2024-01-25 08:45', completed: true },
        { name: 'Cần bổ sung', date: '2024-01-26 14:00', completed: false, note: 'Thiếu ảnh 4x6' },
        { name: 'Hoàn tất', date: '', completed: false }
      ]
    }
  ];

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

  return (
    <div className="min-h-screen bg-gray-50">
      
      {/* iOS Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="px-4 py-4">
          <h1 className="text-2xl font-bold text-gray-900 mb-6">Tra cứu hồ sơ</h1>
          
          {/* iOS Search */}
          <div className="relative mb-6">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <Input
              placeholder="Nhập số CCCD hoặc mã hồ sơ"
              value={searchValue}
              onChange={(e) => setSearchValue(e.target.value)}
              className="pl-11 h-12 bg-gray-100 border-0 rounded-xl text-base"
            />
        </div>

          {/* Recent searches */}
          <div>
            <p className="text-sm font-medium text-gray-700 mb-3">Tìm kiếm gần đây:</p>
            <div className="flex gap-2 flex-wrap">
              {recentSearches.map((search, index) => (
                <Button
                  key={index}
                  variant="outline"
                  size="sm"
                  onClick={() => setSearchValue(search)}
                  className="h-10 px-4 rounded-full border-gray-300 text-gray-700"
                >
                  {search}
                </Button>
              ))}
            </div>
          </div>
        </div>
      </div>

      <div className="px-4 pb-6">
        {selectedDocument ? (
          // Document detail
          <div>
            <Button 
              variant="ghost" 
              className="mb-6 h-10 px-3 rounded-xl"
              onClick={() => setSelectedDocument(null)}
            >
              ← Quay lại
            </Button>

            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>{selectedDocument.title}</CardTitle>
                    <p className="text-gray-600">Mã hồ sơ: {selectedDocument.id}</p>
                  </div>
                  <Badge className={getStatusColor(selectedDocument.status)}>
                    {selectedDocument.status}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <p className="text-gray-600">Ngày nộp</p>
                      <p>{selectedDocument.submitDate}</p>
                    </div>
                    <div>
                      <p className="text-gray-600">Cơ quan xử lý</p>
                      <p>{selectedDocument.office}</p>
                    </div>
                  </div>

                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <p>Tiến trình xử lý</p>
                      <p className="text-sm text-gray-600">{selectedDocument.progress}%</p>
                    </div>
                    <Progress value={selectedDocument.progress} className="mb-4" />
                  </div>

                  {/* Timeline */}
                  <div className="space-y-3">
                    {selectedDocument.steps.map((step: any, index: number) => (
                      <div key={index} className="flex items-start gap-3">
                        <div className={`w-6 h-6 rounded-full flex items-center justify-center ${
                          step.completed ? 'bg-green-100' : 'bg-gray-100'
                        }`}>
                          {step.completed ? (
                            <CheckCircle className="w-4 h-4 text-green-600" />
                          ) : (
                            <div className="w-2 h-2 bg-gray-400 rounded-full" />
                          )}
                        </div>
                        <div className="flex-1">
                          <p className={step.completed ? '' : 'text-gray-500'}>{step.name}</p>
                          {step.date && (
                            <p className="text-sm text-gray-600">{step.date}</p>
                          )}
                          {step.note && (
                            <p className="text-sm text-orange-600">{step.note}</p>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>

                  {selectedDocument.needSupplementary && (
                    <div className="bg-orange-50 p-4 rounded-lg">
                      <h4 className="flex items-center gap-2 mb-2">
                        <AlertCircle className="w-4 h-4 text-orange-600" />
                        Cần bổ sung hồ sơ
                      </h4>
                      <p className="text-sm">Vui lòng bổ sung ảnh 4x6 và nộp lại trong vòng 15 ngày.</p>
                    </div>
                  )}

                  <div className="flex gap-2">
                    <Button className="flex-1">
                      <Phone className="w-4 h-4 mr-2" />
                      Gọi hotline
                    </Button>
                    <Button variant="outline" className="flex-1" onClick={() => onNavigate('chatbot')}>
                      <MessageCircle className="w-4 h-4 mr-2" />
                      Chat hỗ trợ
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        ) : (
          // Documents list
          <div>
            <div className="flex items-center justify-between mb-4">
              <h2>Hồ sơ của bạn ({documents.length})</h2>
              <Button variant="outline" size="sm">
                Lọc
              </Button>
            </div>

            <div className="space-y-3">
              {documents.map((doc) => (
                <Card 
                  key={doc.id}
                  className="cursor-pointer hover:shadow-md transition-shadow"
                  onClick={() => setSelectedDocument(doc)}
                >
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between mb-2">
                      <h3>{doc.title}</h3>
                      <Badge className={getStatusColor(doc.status)}>
                        {doc.status}
                      </Badge>
                    </div>
                    
                    <div className="flex items-center justify-between text-sm text-gray-600 mb-3">
                      <span>Mã: {doc.id}</span>
                      <span>{doc.submitDate}</span>
                    </div>

                    <div className="flex items-center gap-2">
                      {getStatusIcon(doc.status)}
                      <span className="text-sm">{doc.office}</span>
                    </div>

                    <Progress value={doc.progress} className="mt-3" />
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}