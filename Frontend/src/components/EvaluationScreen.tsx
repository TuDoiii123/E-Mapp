import { useState } from 'react';
import { Star, Send, CheckCircle, Building, Calendar } from 'lucide-react';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Textarea } from './ui/textarea';
import { Label } from './ui/label';
import React from 'react';
interface EvaluationScreenProps {
  onNavigate: (screen: string) => void;
}

export function EvaluationScreen({ onNavigate }: EvaluationScreenProps) {
  const [selectedOffice, setSelectedOffice] = useState<any>(null);
  const [ratings, setRatings] = useState({
    attitude: 0,
    speed: 0,
    quality: 0
  });
  const [comment, setComment] = useState('');
  const [submitted, setSubmitted] = useState(false);

  const offices = [
    {
      id: 1,
      name: 'UBND Quận 1',
      address: '86 Lê Thánh Tôn, Quận 1, TP.HCM',
      lastVisit: '2024-01-20',
      services: ['Đăng ký kết hôn'],
      completed: true,
      rated: false
    },
    {
      id: 2,
      name: 'Sở GTVT TP.HCM',
      address: '63 Lý Tự Trọng, Quận 1, TP.HCM',
      lastVisit: '2024-01-22',
      services: ['Giấy phép lái xe'],
      completed: false,
      rated: false
    },
    {
      id: 3,
      name: 'Sở Tài nguyên Môi trường',
      address: '123 Lê Lợi, Quận 1, TP.HCM',
      lastVisit: '2024-01-10',
      services: ['Giấy phép môi trường'],
      completed: true,
      rated: true,
      rating: 4.5
    }
  ];

  const StarRating = ({ value, onChange, label }: { value: number; onChange: (rating: number) => void; label: string }) => {
    return (
      <div className="space-y-2">
        <Label>{label}</Label>
        <div className="flex gap-1">
          {[1, 2, 3, 4, 5].map((star) => (
            <button
              key={star}
              type="button"
              onClick={() => onChange(star)}
              className={`p-1 ${star <= value ? 'text-yellow-400' : 'text-gray-300'} hover:text-yellow-400 transition-colors`}
            >
              <Star className="w-6 h-6 fill-current" />
            </button>
          ))}
        </div>
        <p className="text-sm text-gray-600">
          {value === 0 ? 'Chưa đánh giá' :
           value === 1 ? 'Rất không hài lòng' :
           value === 2 ? 'Không hài lòng' :
           value === 3 ? 'Bình thường' :
           value === 4 ? 'Hài lòng' : 'Rất hài lòng'}
        </p>
      </div>
    );
  };

  const handleSubmitEvaluation = () => {
    if (ratings.attitude > 0 && ratings.speed > 0 && ratings.quality > 0) {
      setSubmitted(true);
      setTimeout(() => {
        setSelectedOffice(null);
        setSubmitted(false);
        setRatings({ attitude: 0, speed: 0, quality: 0 });
        setComment('');
      }, 2000);
    }
  };

  if (submitted) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <Card className="w-full max-w-md text-center">
          <CardContent className="p-6">
            <CheckCircle className="w-16 h-16 text-green-600 mx-auto mb-4" />
            <h2 className="mb-2">Cảm ơn bạn!</h2>
            <p className="text-gray-600 mb-4">
              Đánh giá của bạn đã được gửi thành công. Những góp ý này sẽ giúp cải thiện chất lượng dịch vụ công.
            </p>
            <Button onClick={() => setSubmitted(false)} className="w-full">
              Tiếp tục đánh giá
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* iOS Status Bar Space */}
      
      {/* iOS Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="px-4 py-4">
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Đánh giá cơ quan</h1>
          <p className="text-gray-600">Góp ý chất lượng dịch vụ công</p>
        </div>
      </div>

      <div className="px-4 pb-6">
        {selectedOffice ? (
          // Evaluation form
          <div className="space-y-6">
            <Button 
              variant="ghost" 
              onClick={() => setSelectedOffice(null)}
              className="mb-4"
            >
              ← Quay lại
            </Button>

            <Card>
              <CardHeader>
                <CardTitle>Đánh giá dịch vụ</CardTitle>
                <div className="text-sm text-gray-600">
                  <p>{selectedOffice.name}</p>
                  <p>{selectedOffice.address}</p>
                </div>
              </CardHeader>
              <CardContent className="space-y-6">
                <StarRating
                  value={ratings.attitude}
                  onChange={(rating) => setRatings({ ...ratings, attitude: rating })}
                  label="Thái độ phục vụ"
                />

                <StarRating
                  value={ratings.speed}
                  onChange={(rating) => setRatings({ ...ratings, speed: rating })}
                  label="Tốc độ xử lý"
                />

                <StarRating
                  value={ratings.quality}
                  onChange={(rating) => setRatings({ ...ratings, quality: rating })}
                  label="Chất lượng kết quả"
                />

                <div className="space-y-2">
                  <Label>Nhận xét chi tiết (không bắt buộc)</Label>
                  <Textarea
                    placeholder="Chia sẻ trải nghiệm của bạn..."
                    value={comment}
                    onChange={(e) => setComment(e.target.value)}
                    rows={4}
                  />
                </div>

                <div className="bg-blue-50 p-4 rounded-lg">
                  <h4 className="mb-2">Tổng đánh giá</h4>
                  <div className="flex items-center gap-2">
                    <div className="flex">
                      {[1, 2, 3, 4, 5].map((star) => (
                        <Star 
                          key={star}
                          className={`w-5 h-5 ${
                            star <= Math.round((ratings.attitude + ratings.speed + ratings.quality) / 3)
                              ? 'text-yellow-400 fill-current' 
                              : 'text-gray-300'
                          }`}
                        />
                      ))}
                    </div>
                    <span>
                      {((ratings.attitude + ratings.speed + ratings.quality) / 3).toFixed(1)}/5
                    </span>
                  </div>
                </div>

                <Button 
                  onClick={handleSubmitEvaluation}
                  disabled={!ratings.attitude || !ratings.speed || !ratings.quality}
                  className="w-full"
                >
                  <Send className="w-4 h-4 mr-2" />
                  Gửi đánh giá
                </Button>
              </CardContent>
            </Card>
          </div>
        ) : (
          // Offices list
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h2>Cơ quan đã từng tiếp xúc</h2>
              <Badge variant="outline">{offices.length} cơ quan</Badge>
            </div>

            <div className="space-y-3">
              {offices.map((office) => (
                <Card 
                  key={office.id}
                  className={`cursor-pointer transition-all ${
                    office.completed && !office.rated ? 'ring-2 ring-blue-200' : ''
                  }`}
                  onClick={() => {
                    if (office.completed && !office.rated) {
                      setSelectedOffice(office);
                    }
                  }}
                >
                  <CardContent className="p-4">
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex-1">
                        <h3>{office.name}</h3>
                        <p className="text-sm text-gray-600">{office.address}</p>
                      </div>
                      
                      <div className="text-right">
                        {office.rated ? (
                          <div className="flex items-center gap-1">
                            <Star className="w-4 h-4 text-yellow-400 fill-current" />
                            <span className="text-sm">{office.rating}</span>
                          </div>
                        ) : office.completed ? (
                          <Badge className="bg-blue-100 text-blue-800">
                            Có thể đánh giá
                          </Badge>
                        ) : (
                          <Badge variant="outline">
                            Đang xử lý
                          </Badge>
                        )}
                      </div>
                    </div>

                    <div className="flex items-center gap-4 text-sm text-gray-600">
                      <div className="flex items-center gap-1">
                        <Calendar className="w-4 h-4" />
                        {office.lastVisit}
                      </div>
                      <div className="flex items-center gap-1">
                        <Building className="w-4 h-4" />
                        {office.services.join(', ')}
                      </div>
                    </div>

                    {office.completed && !office.rated && (
                      <div className="mt-3 p-2 bg-blue-50 rounded text-sm text-blue-700">
                        💡 Bấm để đánh giá chất lượng dịch vụ
                      </div>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>

            <Card>
              <CardContent className="p-4 text-center">
                <p className="text-gray-600 mb-3">
                  Đánh giá của bạn giúp cải thiện chất lượng dịch vụ công
                </p>
                <div className="grid grid-cols-3 gap-4 text-sm">
                  <div>
                    <div className="text-lg">4.2</div>
                    <div>Điểm TB</div>
                  </div>
                  <div>
                    <div className="text-lg">1,245</div>
                    <div>Đánh giá</div>
                  </div>
                  <div>
                    <div className="text-lg">89%</div>
                    <div>Hài lòng</div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
}