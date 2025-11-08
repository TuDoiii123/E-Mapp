import { useState, useEffect, useRef } from 'react';
import { Send, Bot, User, Paperclip, Mic, MoreVertical, ArrowLeft } from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Card, CardContent } from './ui/card';
import { Avatar, AvatarFallback, AvatarImage } from './ui/avatar';
import React from 'react';
interface ChatbotScreenProps {
  onNavigate: (screen: string) => void;
}

interface Message {
  id: number;
  text: string;
  isBot: boolean;
  timestamp: Date;
  actions?: { label: string; action: () => void }[];
}

export function ChatbotScreen({ onNavigate }: ChatbotScreenProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      text: 'Xin chào! Tôi là trợ lý AI của Dịch vụ công số. Tôi có thể giúp bạn:',
      isBot: true,
      timestamp: new Date(),
      actions: [
        { label: 'Tra cứu hồ sơ', action: () => onNavigate('search') },
        { label: 'Hướng dẫn nộp hồ sơ', action: () => addBotMessage('Để nộp hồ sơ trực tuyến, bạn cần chuẩn bị các giấy tờ sau...') },
        { label: 'Tìm cơ quan gần nhất', action: () => onNavigate('map') }
      ]
    }
  ]);
  const [inputText, setInputText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const addBotMessage = (text: string, actions?: { label: string; action: () => void }[]) => {
    setIsTyping(true);
    setTimeout(() => {
      setMessages(prev => [...prev, {
        id: Date.now(),
        text,
        isBot: true,
        timestamp: new Date(),
        actions
      }]);
      setIsTyping(false);
    }, 1000);
  };

  const addUserMessage = (text: string) => {
    const userMessage: Message = {
      id: Date.now(),
      text,
      isBot: false,
      timestamp: new Date()
    };
    
    setMessages(prev => [...prev, userMessage]);
    
    // Simulate bot response
    setTimeout(() => {
      handleBotResponse(text);
    }, 500);
  };

  const handleBotResponse = (userText: string) => {
    const lowerText = userText.toLowerCase();
    
    if (lowerText.includes('hồ sơ') || lowerText.includes('tra cứu')) {
      addBotMessage(
        'Tôi có thể giúp bạn tra cứu hồ sơ. Bạn có thể cung cấp số CCCD hoặc mã hồ sơ không?',
        [
          { label: 'Tra cứu ngay', action: () => onNavigate('search') }
        ]
      );
    } else if (lowerText.includes('nộp') || lowerText.includes('đăng ký')) {
      addBotMessage(
        'Tôi sẽ hướng dẫn bạn nộp hồ sơ trực tuyến. Bạn muốn nộp loại hồ sơ nào?',
        [
          { label: 'Đăng ký kết hôn', action: () => addBotMessage('Để đăng ký kết hôn, bạn cần: CCCD gốc 2 bên, đơn đăng ký, giấy khám sức khỏe...') },
          { label: 'Giấy phép kinh doanh', action: () => addBotMessage('Để xin giấy phép kinh doanh, bạn cần: CCCD gốc, đơn đăng ký, giấy thuê mặt bằng...') },
          { label: 'Nộp hồ sơ ngay', action: () => onNavigate('submit') }
        ]
      );
    } else if (lowerText.includes('bản đồ') || lowerText.includes('cơ quan') || lowerText.includes('địa chỉ')) {
      addBotMessage(
        'Tôi có thể giúp bạn tìm cơ quan gần nhất và thông tin chi tiết.',
        [
          { label: 'Xem bản đồ', action: () => onNavigate('map') }
        ]
      );
    } else if (lowerText.includes('thời gian') || lowerText.includes('bao lâu')) {
      addBotMessage(
        'Thời gian xử lý phụ thuộc vào loại hồ sơ:\n• Hộ tịch: 5-7 ngày\n• Đất đai: 15-20 ngày\n• Kinh doanh: 10-15 ngày\n• Tư pháp: 7-10 ngày'
      );
    } else if (lowerText.includes('phí') || lowerText.includes('tiền')) {
      addBotMessage(
        'Lệ phí dịch vụ công:\n• Hộ tịch: Miễn phí\n• CCCD: 50,000 VNĐ\n• Giấy phép kinh doanh: 100,000 VNĐ\n• Thủ tục đất đai: 100,000-500,000 VNĐ'
      );
    } else {
      addBotMessage(
        'Tôi hiểu bạn đang cần hỗ trợ. Dưới đây là một số câu hỏi phổ biến:',
        [
          { label: 'Tra cứu hồ sơ', action: () => addBotMessage('Để tra cứu hồ sơ, bạn cần số CCCD hoặc mã hồ sơ...') },
          { label: 'Thời gian xử lý', action: () => addBotMessage('Thời gian xử lý trung bình từ 5-20 ngày tùy loại hồ sơ...') },
          { label: 'Lệ phí dịch vụ', action: () => addBotMessage('Lệ phí được quy định theo từng loại dịch vụ...') },
          { label: 'Liên hệ hotline', action: () => addBotMessage('Hotline hỗ trợ: 1900 1234 (24/7)') }
        ]
      );
    }
  };

  const handleSend = () => {
    if (inputText.trim()) {
      addUserMessage(inputText);
      setInputText('');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSend();
    }
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('vi-VN', { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* iOS Status Bar Space */}
      <div className="h-11 bg-white"></div>
      
      {/* iOS Header */}
      <div className="bg-white border-b border-gray-200 px-4 py-4 flex items-center gap-3">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => onNavigate('home')}
          className="w-10 h-10 rounded-full"
        >
          <ArrowLeft className="w-5 h-5" />
        </Button>
        <Avatar className="w-10 h-10">
          <AvatarFallback>
            <Bot className="w-6 h-6" />
          </AvatarFallback>
        </Avatar>
        <div className="flex-1">
          <h1 className="text-lg font-semibold text-gray-900">Trợ lý AI</h1>
          <p className="text-sm text-green-600">Đang hoạt động</p>
        </div>
        <Button variant="ghost" size="sm" className="w-10 h-10 rounded-full">
          <MoreVertical className="w-5 h-5" />
        </Button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex gap-3 ${message.isBot ? 'justify-start' : 'justify-end'}`}
          >
            {message.isBot && (
              <Avatar className="w-8 h-8">
                <AvatarFallback>
                  <Bot className="w-4 h-4" />
                </AvatarFallback>
              </Avatar>
            )}
            
            <div className={`max-w-[70%] ${message.isBot ? '' : 'order-first'}`}>
              <Card className={message.isBot ? 'bg-white' : 'bg-blue-600 text-white'}>
                <CardContent className="p-3">
                  <p className="whitespace-pre-line">{message.text}</p>
                  
                  {message.actions && (
                    <div className="mt-3 space-y-2">
                      {message.actions.map((action, index) => (
                        <Button
                          key={index}
                          variant="outline"
                          size="sm"
                          onClick={action.action}
                          className="w-full justify-start"
                        >
                          {action.label}
                        </Button>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
              
              <p className={`text-xs text-gray-500 mt-1 ${
                message.isBot ? 'text-left' : 'text-right'
              }`}>
                {formatTime(message.timestamp)}
              </p>
            </div>

            {!message.isBot && (
              <Avatar className="w-8 h-8">
                <AvatarFallback>
                  <User className="w-4 h-4" />
                </AvatarFallback>
              </Avatar>
            )}
          </div>
        ))}
        
        {isTyping && (
          <div className="flex gap-3">
            <Avatar className="w-8 h-8">
              <AvatarFallback>
                <Bot className="w-4 h-4" />
              </AvatarFallback>
            </Avatar>
            <Card>
              <CardContent className="p-3">
                <div className="flex gap-1">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-100" />
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-200" />
                </div>
              </CardContent>
            </Card>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="bg-white border-t p-4">
        <div className="flex gap-2">
          <Button variant="ghost" size="sm">
            <Paperclip className="w-5 h-5" />
          </Button>
          
          <Input
            placeholder="Nhập tin nhắn..."
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyPress={handleKeyPress}
            className="flex-1"
          />
          
          <Button variant="ghost" size="sm">
            <Mic className="w-5 h-5" />
          </Button>
          
          <Button onClick={handleSend} disabled={!inputText.trim()}>
            <Send className="w-4 h-4" />
          </Button>
        </div>
      </div>
    </div>
  );
}