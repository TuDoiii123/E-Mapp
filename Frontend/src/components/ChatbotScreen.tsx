import { useState, useEffect, useRef, useCallback, type KeyboardEvent } from 'react';
import { Send, Bot, User, Paperclip, Mic, MoreVertical, ArrowLeft, Plus, Search as SearchIcon } from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Card, CardContent } from './ui/card';
import { Avatar, AvatarFallback } from './ui/avatar';
import { chatbotAPI, type ChatSessionSummary } from '../services/api';
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

interface Conversation {
  id: string; // sessionId or '__local__'
  title?: string;
  lastUpdated: number; // epoch ms
  messages: Message[];
}

export function ChatbotScreen({ onNavigate }: ChatbotScreenProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [inputText, setInputText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [mode, setMode] = useState<'default' | 'administrative_qa' | 'document_suggestion' | 'booking'>('default');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const messageRefs = useRef<Record<string, HTMLDivElement | null>>({});
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [recentSessions, setRecentSessions] = useState<ChatSessionSummary[]>([]);
  const [loadingSessions, setLoadingSessions] = useState<boolean>(false);
  const [showSearch, setShowSearch] = useState<boolean>(false);
  const [searchTerm, setSearchTerm] = useState<string>('');

  const activeConversationId = sessionId ?? '__local__';

  const STORAGE_KEY = 'chat_conversations_v1';

  const loadConversations = useCallback(() => {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return [] as Conversation[];
      const parsed = JSON.parse(raw) as {
        id: string; title?: string; lastUpdated: number; messages: Array<Omit<Message, 'timestamp'> & { timestamp: string }>
      }[];
      return parsed.map((c) => ({
        id: c.id,
        title: c.title,
        lastUpdated: c.lastUpdated,
        messages: c.messages.map((m) => ({ ...m, timestamp: new Date(m.timestamp) })),
      }));
    } catch {
      return [] as Conversation[];
    }
  }, []);

  const saveConversations = useCallback((items: Conversation[]) => {
    const payload = items.map((c) => ({
      id: c.id,
      title: c.title,
      lastUpdated: c.lastUpdated,
      messages: c.messages.map((m) => ({
        id: m.id,
        text: m.text,
        isBot: m.isBot,
        // strip actions because functions are not serializable
        timestamp: m.timestamp.toISOString(),
      })),
    }));
    localStorage.setItem(STORAGE_KEY, JSON.stringify(payload));
  }, []);

  const createMessageId = useCallback((prefix: string) => {
    return `${prefix}-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
  }, []);

  const appendBotMessage = useCallback((text: string, actions?: Message['actions']) => {
    const msg: Message = {
      id: createMessageId('bot'),
      text,
      isBot: true,
      timestamp: new Date(),
      actions,
    };
    setMessages((prev) => [...prev, msg]);
    setConversations((prev) => {
      const id = activeConversationId;
      const next = [...prev];
      const idx = next.findIndex((c) => c.id === id);
      if (idx === -1) {
        next.push({ id, lastUpdated: Date.now(), messages: [msg] });
      } else {
        next[idx] = {
          ...next[idx],
          lastUpdated: Date.now(),
          messages: [...next[idx].messages, msg],
        };
      }
      // keep everything but we will display only 10 most recent
      saveConversations(next);
      return next;
    });
  }, [createMessageId, activeConversationId, saveConversations]);

  const appendUserMessage = useCallback((text: string) => {
    const msg: Message = {
      id: createMessageId('user'),
      text,
      isBot: false,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, msg]);
    setConversations((prev) => {
      const id = activeConversationId;
      const next = [...prev];
      const idx = next.findIndex((c) => c.id === id);
      if (idx === -1) {
        next.push({ id, lastUpdated: Date.now(), messages: [msg] });
      } else {
        next[idx] = {
          ...next[idx],
          lastUpdated: Date.now(),
          messages: [...next[idx].messages, msg],
        };
      }
      saveConversations(next);
      return next;
    });
  }, [createMessageId, activeConversationId, saveConversations]);

  // Ensure CSS class for pre-wrap in container (added inline style later in JSX)

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

    // Only show greeting if there's no data at all
    if (recentSessions.length > 0 || conversations.length > 0) return;

    appendBotMessage('Xin chào! Tôi là trợ lý AI của Dịch vụ công số. Tôi có thể giúp bạn:', [
      {
        label: 'Hỏi đáp hành chính',
        action: () => appendBotMessage('Bạn có thể hỏi tôi về thủ tục, thời hạn, lệ phí hoặc cơ quan phụ trách. Hãy nhập câu hỏi cụ thể.'),
      },
      {
        label: 'Gợi ý các giấy tờ liên quan',
        action: () => appendBotMessage('Vui lòng cho biết loại thủ tục hoặc mục đích (ví dụ: đăng ký kinh doanh, cấp lại CMND...) để tôi gợi ý bộ giấy tờ cần chuẩn bị.'),
      },
      {
        label: 'Đặt lịch',
        action: () => appendBotMessage('Để đặt lịch, vui lòng cho tôi biết loại dịch vụ và khoảng thời gian mong muốn. Tôi sẽ hỗ trợ bạn tạo yêu cầu.'),
      },
    ]);
  }, [appendBotMessage, messages.length, onNavigate, recentSessions.length, conversations.length]);

  // Load conversations from storage and initialize messages of active conversation
  useEffect(() => {
    const loaded = loadConversations();
    setConversations(loaded);
    const active = loaded.find((c) => c.id === activeConversationId);
    if (active) {
      setMessages(active.messages);
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Fetch 10 most recent sessions from backend (if available)
  useEffect(() => {
    let cancelled = false;
    const run = async () => {
      setLoadingSessions(true);
      try {
        const resp = await chatbotAPI.getRecentSessions(10);
        if (!cancelled && resp?.success && Array.isArray(resp.data?.sessions)) {
          setRecentSessions(resp.data.sessions);
        }
      } catch (e) {
        // Silently ignore and rely on local fallback
        console.warn('getRecentSessions failed; using local fallback');
      } finally {
        if (!cancelled) setLoadingSessions(false);
      }
    };
    run();
    return () => { cancelled = true; };
  }, []);

  const normalizedQuery = searchTerm.trim().toLowerCase();

  const handleSend = useCallback(async () => {
    const trimmed = inputText.trim();
    if (!trimmed || isTyping) {
      return;
    }

    setInputText('');
    appendUserMessage(trimmed);
    setIsTyping(true);

    try {
      if (mode === 'document_suggestion') {
        const resp = await chatbotAPI.suggestProcedure(trimmed, { topK: 4, threshold: 0.5, sessionId: sessionId ?? undefined });
        if (resp.success && resp.data) {
          const { explanation, suggestions, sessionId: newSid } = resp.data;
          const normalizedSessionId = newSid && newSid.trim().length > 0 ? newSid : sessionId;
          if (!sessionId && normalizedSessionId) {
            // migrate local conversation id similar to RAG branch
            setConversations((prev) => {
              const localId = '__local__';
              const idxLocal = prev.findIndex((c) => c.id === localId);
              let next = [...prev];
              if (idxLocal !== -1) {
                const idxTarget = next.findIndex((c) => c.id === normalizedSessionId!);
                if (idxTarget === -1) {
                  next[idxLocal] = { ...next[idxLocal], id: normalizedSessionId!, lastUpdated: Date.now() };
                } else {
                  next[idxTarget] = {
                    ...next[idxTarget],
                    lastUpdated: Math.max(next[idxTarget].lastUpdated, next[idxLocal].lastUpdated),
                    messages: [...next[idxTarget].messages, ...next[idxLocal].messages],
                  };
                  next = next.filter((c, i) => i !== idxLocal);
                }
                saveConversations(next);
              }
              return next;
            });
          }
          setSessionId(normalizedSessionId ?? null);
          const explanationText = explanation || 'Các thủ tục liên quan được đề xuất gồm:';
          if (suggestions && suggestions.length > 0) {
            const header = explanationText;
            const block = suggestions.map((s, idx) => {
              let name = s.procedure_name || 'Không rõ tên thủ tục';
              name = name.trim();
              if (!/[\.?!…]$/.test(name)) {
                name = name + '.'; // đảm bảo dấu chấm cuối câu
              }
              return ` ${idx + 1}. ${name}`; // một khoảng trắng đầu dòng như yêu cầu mẫu
            }).join('\n');
            appendBotMessage(`${header}\n${block}`);
          } else {
            appendBotMessage('Không tìm thấy thủ tục phù hợp.');
          }
        } else {
          appendBotMessage(resp.message || 'Không thể lấy gợi ý giấy tờ.');
        }
      } else {
        const response = await chatbotAPI.sendMessage({
          message: trimmed,
          sessionId: sessionId ?? undefined,
          intent: mode === 'administrative_qa' ? 'administrative_qa' : undefined,
        });

      if (response.warnings?.length) {
        console.warn('[chatbotAPI]', response.warnings.join(' | '));
      }

        const nextSessionId = response.data?.sessionId ?? sessionId;
        const normalizedSessionId = nextSessionId && nextSessionId.trim().length > 0 ? nextSessionId : null;

      // If session just got assigned, migrate '__local__' conversation to real id
      if (sessionId == null && normalizedSessionId) {
        setConversations((prev) => {
          const localId = '__local__';
          const idxLocal = prev.findIndex((c) => c.id === localId);
          if (idxLocal === -1) return prev;
          const idxTarget = prev.findIndex((c) => c.id === normalizedSessionId);
          let next = [...prev];
          if (idxTarget === -1) {
            // rename
            next[idxLocal] = { ...next[idxLocal], id: normalizedSessionId };
          } else {
            // merge
            next[idxTarget] = {
              ...next[idxTarget],
              lastUpdated: Math.max(next[idxTarget].lastUpdated, next[idxLocal].lastUpdated),
              messages: [...next[idxTarget].messages, ...next[idxLocal].messages],
            };
            next = next.filter((c, i) => i !== idxLocal);
          }
          saveConversations(next);
          return next;
        });
      }

        setSessionId(normalizedSessionId);

        const responseText = response.data?.response ?? 'Xin lỗi, hệ thống chưa có phản hồi phù hợp.';
        appendBotMessage(responseText);
      }
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
  }, [appendBotMessage, appendUserMessage, inputText, isTyping, sessionId, mode]);

  const startNewConversation = useCallback(() => {
    setSessionId(null);
    setMessages([]);
    setConversations((prev) => {
      let next = [...prev];
      const now = Date.now();
      const idxLocal = next.findIndex((c) => c.id === '__local__');
      if (idxLocal !== -1 && next[idxLocal].messages.length > 0) {
        // Preserve old local by renaming it to a unique id
        const preservedId = `draft-${now}`;
        next[idxLocal] = { ...next[idxLocal], id: preservedId, lastUpdated: now };
        // Insert a fresh empty local conversation at the front for visibility
        next.unshift({ id: '__local__', lastUpdated: now, messages: [] });
      } else if (idxLocal === -1) {
        next.unshift({ id: '__local__', lastUpdated: now, messages: [] });
      } else {
        // Existing local is empty, just update its timestamp
        next[idxLocal] = { ...next[idxLocal], lastUpdated: now, messages: [] };
      }
      saveConversations(next);
      return next;
    });
  }, [saveConversations]);

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

  const handleSelectConversation = useCallback(async (id: string) => {
    // Try local first
    const conv = conversations.find((c) => c.id === id);
    if (conv) {
      setMessages(conv.messages);
      setSessionId(id === '__local__' ? null : id);
      return;
    }

    // Fallback to backend fetch
    try {
      const resp = await chatbotAPI.getSessionMessages(id);
      if (resp?.success && resp.data?.messages) {
        const mapped: Message[] = resp.data.messages.map((m) => ({
          id: createMessageId(m.role === 'assistant' ? 'bot' : 'user'),
          text: m.content,
          isBot: m.role === 'assistant',
          timestamp: m.timestamp ? new Date(m.timestamp) : new Date(),
        }));
        setMessages(mapped);
        setSessionId(id);

        // Cache in local conversations for preview/persistence
        setConversations((prev) => {
          const next = [...prev];
          const idx = next.findIndex((c) => c.id === id);
          const lastUpdated = mapped.length ? mapped[mapped.length - 1].timestamp.getTime() : Date.now();
          if (idx === -1) {
            next.push({ id, lastUpdated, messages: mapped });
          } else {
            next[idx] = { ...next[idx], lastUpdated, messages: mapped };
          }
          saveConversations(next);
          return next;
        });
      }
    } catch (e) {
      console.error('Failed to load session messages', e);
    }
  }, [conversations, createMessageId, saveConversations]);

  const startModeConversation = useCallback((newMode: 'administrative_qa' | 'document_suggestion' | 'booking', greeting: string) => {
    // Kết thúc cuộc trò chuyện hiện tại và bắt đầu cuộc trò chuyện mới với mode tương ứng
    startNewConversation();
    setMode(newMode);
    appendBotMessage(greeting);
  }, [appendBotMessage, startNewConversation]);

  const startAdministrativeQA = useCallback(() => {
    startModeConversation(
      'administrative_qa',
      'Chào bạn, tôi là Trợ lý hành chính của E-Map. Bạn hãy nhập câu hỏi về thủ tục, lệ phí, thời hạn xử lý hoặc cơ quan phụ trách để tôi hỗ trợ.'
    );
  }, [startModeConversation]);

  const startDocumentSuggestion = useCallback(() => {
    startModeConversation(
      'document_suggestion',
      'Chào bạn, tôi sẽ gợi ý các giấy tờ liên quan. Vui lòng nhập loại thủ tục hoặc mục đích (ví dụ: đăng ký kinh doanh, cấp lại CMND, chuyển hộ khẩu...) để tôi liệt kê giấy tờ cần chuẩn bị.'
    );
  }, [startModeConversation]);

  const startBooking = useCallback(() => {
    startModeConversation(
      'booking',
      'Bạn đang bắt đầu yêu cầu Đặt lịch. Vui lòng nhập loại dịch vụ và thời điểm mong muốn (ví dụ: “Đặt lịch nộp hồ sơ cấp CCCD vào sáng thứ 3 tuần sau”).'
    );
  }, [startModeConversation]);

  return (
    <div className="chatbot-screen-wrapper bg-gray-50">

      {/* Chatbot framed container centered with fixed size (scrollable) */}
      <div className="chatbot-frame mb-4 border border-gray-200 rounded-xl shadow-sm bg-white relative flex flex-col">

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
          <div className="horizontal-divider" aria-hidden="true" />

      <div className="flex flex-2 min-h-0 gap-0">
        {/* Sidebar: Lịch sử chat (10 cuộc trò chuyện gần nhất) */}
        <aside className="hidden md:flex md:w-56 lg:w-64 flex-col bg-gray min-h-0 relative overflow-y-auto">
          <div className="px-4 py-3 sticky top-0 bg-white z-10">
            {/* Actions placed ABOVE both the title and the history list (inside sticky header) */}
            <div className="space-y-2">
              <Button variant="ghost" className="w-full justify-start gap-3 mx-2 border-0 shadow-none hover:bg-gray-50" onClick={startNewConversation}>
                <Plus className="w-5 h-5" />
                <span>Đoạn chat mới</span>
              </Button>
              <Button variant="ghost" className="w-full justify-start gap-3 border-0 shadow-none hover:bg-gray-50" onClick={() => setShowSearch((v) => !v)}>
                <SearchIcon className="w-5 h-5" />
                <span>Tìm kiếm đoạn chat</span>
              </Button>
              {showSearch && (
                <Input
                  placeholder="Nhập từ khóa..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="h-9"
                />
              )}
            </div>
            <div className="flex items-center gap-2 mt-2">
              <div className="flex-1 min-w-0">
                <h2 className="text-base font-semibold text-gray-900 truncate">Lịch sử chat</h2>
              </div>
            </div>
            <div className="horizontal-divider mt-2" aria-hidden="true" />
          </div>
          <div className="flex-1 min-h-0">
            <ul className="divide-y">
              {/* Loading skeletons */}
              {loadingSessions && recentSessions.length === 0 && (
                <>
                  {Array.from({ length: 5 }).map((_, i) => (
                    <li key={`skeleton-${i}`} className="px-4 py-3">
                      <div className="animate-pulse">
                        <div className="h-12 rounded-lg bg-gray-100" />
                      </div>
                    </li>
                  ))}
                </>
              )}

              {/* Prefer backend sessions if available */}
              {recentSessions.length > 0 && (
                <>
                  {recentSessions
                    .filter((s) =>
                      normalizedQuery.length === 0 ||
                      s.summary?.toLowerCase().includes(normalizedQuery) ||
                      s.sessionId.toLowerCase().includes(normalizedQuery)
                    )
                    .slice(0, 10)
                    .map((s) => (
                    <li key={`remote-${s.sessionId}`}>
                      <button
                        type="button"
                        onClick={() => handleSelectConversation(s.sessionId)}
                        className="w-full px-4 py-2 text-left"
                        title={s.summary}
                      >
                        <div className={`group rounded-lg border ${s.sessionId === activeConversationId ? 'border-blue-200 bg-blue-50' : 'border-gray-200 bg-white'} p-3 hover:shadow-sm transition` }>
                          <div className="flex items-start gap-3">
                            <span className="mt-0.5 inline-flex items-center justify-center w-7 h-7 rounded-full bg-gradient-to-br from-blue-50 to-blue-100 text-blue-700 ring-1 ring-blue-200">
                              <Bot className="w-4 h-4" />
                            </span>
                            <span className="flex-1 min-w-0">
                              <span className="flex items-center justify-between gap-3">
                                <span className="text-sm font-medium text-gray-900 truncate">
                                  {s.summary || 'Không có tiêu đề'}
                                </span>
                                <span className="text-[11px] text-gray-500 shrink-0">
                                  {s.createdAt ? new Date(s.createdAt).toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' }) : ''}
                                </span>
                              </span>
                            </span>
                          </div>
                        </div>
                      </button>
                    </li>
                  ))}
                </>
              )}

              {/* Fallback to local cached conversations */}
              {recentSessions.length === 0 && conversations.length === 0 && !loadingSessions && (
                <li className="px-4 py-3 text-sm text-gray-500">Chưa có cuộc trò chuyện</li>
              )}

              {recentSessions.length === 0 && conversations.length > 0 && (
                <>
                  {[...conversations]
                    .sort((a, b) => b.lastUpdated - a.lastUpdated)
                    .filter((c) => {
                      if (normalizedQuery.length === 0) return true;
                      const last = c.messages[c.messages.length - 1];
                      const preview = last?.text?.toLowerCase() || '';
                      return c.id.toLowerCase().includes(normalizedQuery) || preview.includes(normalizedQuery);
                    })
                    .slice(0, 10)
                    .map((c) => {
                      const last = c.messages[c.messages.length - 1];
                      const preview = last?.text ?? 'Trống';
                      const time = last ? formatTime(last.timestamp) : '';
                      const isActive = c.id === activeConversationId;
                      const firstUser = c.messages.find((m) => !m.isBot);
                      let titleText = (firstUser?.text || '').trim();
                      if (!titleText) {
                        if (c.messages.length === 0 && c.id === '__local__') titleText = 'Cuộc trò chuyện mới';
                        else titleText = preview || 'Không có tiêu đề';
                      }
                      return (
                        <li key={`conv-${c.id}`}>
                          <button
                            type="button"
                            onClick={() => handleSelectConversation(c.id)}
                            className="w-full px-4 py-2 text-left"
                            title={titleText}
                          >
                            <div className={`group rounded-lg border ${isActive ? 'border-blue-200 bg-blue-50' : 'border-gray-200 bg-white'} p-3 hover:shadow-sm transition` }>
                              <div className="flex items-start gap-3">
                                <span className="mt-0.5 inline-flex items-center justify-center w-7 h-7 rounded-full bg-gradient-to-br from-blue-50 to-blue-100 text-blue-700 ring-1 ring-blue-200">
                                  <Bot className="w-4 h-4" />
                                </span>
                                <span className="flex-1 min-w-0">
                                  <span className="flex items-center justify-between gap-3">
                                    <span className="text-sm font-medium text-gray-900 truncate">
                                      {titleText}
                                    </span>
                                    <span className="text-[11px] text-gray-500 shrink-0">{time}</span>
                                  </span>
                                </span>
                              </div>
                            </div>
                          </button>
                        </li>
                      );
                    })}
                </>
              )}
            </ul>
          </div>
        </aside>

        {/* Vertical divider between history and chat */}
        <div className="hidden md:block vertical-divider" aria-hidden="true" />

        {/* Main chat area */}
        <div className="flex-1 flex flex-col min-h-0">
          <div className="flex-1 p-4 pb-24 space-y-4 chat-messages-scroll">
            {/* Quick action buttons always visible at top */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2 mb-2">
              <Button
                variant={mode === 'administrative_qa' ? 'default' : 'outline'}
                size="sm"
                className="justify-start"
                onClick={startAdministrativeQA}
              >
                Hỏi đáp hành chính
              </Button>
              <Button
                variant={mode === 'document_suggestion' ? 'default' : 'outline'}
                size="sm"
                className="justify-start"
                onClick={startDocumentSuggestion}
              >
                Gợi ý các giấy tờ liên quan
              </Button>
              <Button
                variant={mode === 'booking' ? 'default' : 'outline'}
                size="sm"
                className="justify-start"
                onClick={startBooking}
              >
                Đặt lịch
              </Button>
            </div>
            {messages.map((message) => (
              <div
                key={message.id}
                ref={(el) => { messageRefs.current[message.id] = el; }}
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
                      {message.text.includes('\n') ? (
                        <div className="leading-relaxed text-sm whitespace-pre-wrap">
                          {message.text.split(/\n/).map((line, i) => (
                            <p key={i} className="m-0">
                              {line.trim() === '' ? '\u00A0' : line}
                            </p>
                          ))}
                        </div>
                      ) : (
                        <p className="leading-relaxed text-sm whitespace-pre-wrap">{message.text}</p>
                      )}

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

          <div className="bg-white border-t p-4 chat-input-bar">
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
      </div>
      </div>
    </div>
  );
}