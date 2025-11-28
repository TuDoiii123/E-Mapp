import { useState, useEffect, useRef, useCallback, type KeyboardEvent } from 'react';
import { Send, Bot, User, Paperclip, Mic, MoreVertical, ArrowLeft } from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Card, CardContent } from './ui/card';
import { Avatar, AvatarFallback } from './ui/avatar';
import { chatbotAPI } from '../services/api';
interface ChatbotScreenProps {
  onNavigate: (screen: string) => void;
}

interface Message {
  id: string;
  text: string;
  isBot: boolean;
  timestamp: Date;
  actions?: { label: string; action: () => void }[];
}

export function ChatbotScreen({ onNavigate }: ChatbotScreenProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [inputText, setInputText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const createMessageId = useCallback((prefix: string) => {
    return `${prefix}-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
  }, []);

  const appendBotMessage = useCallback((text: string, actions?: Message['actions']) => {
    setMessages(prev => [
      ...prev,
      {
        id: createMessageId('bot'),
        text,
        isBot: true,
        timestamp: new Date(),
        actions,
      },
    ]);
  }, [createMessageId]);

  const appendUserMessage = useCallback((text: string) => {
    setMessages(prev => [
      ...prev,
      {
        id: createMessageId('user'),
        text,
        isBot: false,
        timestamp: new Date(),
      },
    ]);
  }, [createMessageId]);

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  useEffect(() => {
    if (messages.length > 0) {
      return;
    }

    appendBotMessage('Xin chào! Tôi là trợ lý AI của Dịch vụ công số. Tôi có thể giúp bạn:', [
      { label: 'Tra cứu hồ sơ', action: () => onNavigate('search') },
      {
        label: 'Hướng dẫn nộp hồ sơ',
        action: () => appendBotMessage('Để nộp hồ sơ trực tuyến, bạn cần chuẩn bị các giấy tờ sau...'),
      },
      { label: 'Tìm cơ quan gần nhất', action: () => onNavigate('map') },
    ]);
  }, [appendBotMessage, messages.length, onNavigate]);

  const handleSend = useCallback(async () => {
    const trimmed = inputText.trim();
    if (!trimmed || isTyping) {
      return;
    }

    setInputText('');
    appendUserMessage(trimmed);
    setIsTyping(true);

    try {
      const response = await chatbotAPI.sendMessage({
        message: trimmed,
        sessionId: sessionId ?? undefined,
      });

      if (response.warnings?.length) {
        console.warn('[chatbotAPI]', response.warnings.join(' | '));
      }

      const nextSessionId = response.data?.sessionId ?? sessionId;
      const normalizedSessionId = nextSessionId && nextSessionId.trim().length > 0 ? nextSessionId : null;
      setSessionId(normalizedSessionId);

      const responseText = response.data?.response ?? 'Xin lỗi, hệ thống chưa có phản hồi phù hợp.';
      appendBotMessage(responseText);
    } catch (error) {
      console.error('Chatbot sendMessage failed:', error);
      const fallbackText =
        error instanceof Error
          ? error.message
          : 'Rất tiếc, chatbot đang gặp sự cố. Vui lòng thử lại sau.';
      appendBotMessage(fallbackText);
    } finally {
      setIsTyping(false);
    }
  }, [appendBotMessage, appendUserMessage, inputText, isTyping, sessionId]);

  const handleKeyPress = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      void handleSend();
    }
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('vi-VN', {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <div className="h-11 bg-white"></div>

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

      <div className="bg-white border-t p-4">
        <div className="flex gap-2">
          <Button variant="ghost" size="sm" disabled={isTyping}>
            <Paperclip className="w-5 h-5" />
          </Button>

          <Input
            placeholder="Nhập tin nhắn..."
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyPress={handleKeyPress}
            className="flex-1"
            disabled={isTyping}
          />

          <Button variant="ghost" size="sm" disabled={isTyping}>
            <Mic className="w-5 h-5" />
          </Button>

          <Button onClick={handleSend} disabled={!inputText.trim() || isTyping}>
            <Send className="w-4 h-4" />
          </Button>
        </div>
      </div>
    </div>
  );
}