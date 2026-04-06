import { useState, useEffect, useRef, useCallback, type KeyboardEvent } from 'react';
import {
  Send, Paperclip, Mic, Settings, HelpCircle,
  User, ArrowLeft, Search as SearchIcon, Calendar, Image,
  Menu, Share2, Bot, Sun, MessageSquarePlus,
} from 'lucide-react';
import { chatbotAPI, voiceAPI, type ChatSessionSummary } from '../services/api';

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
  id: string;
  title?: string;
  lastUpdated: number;
  messages: Message[];
}

export function ChatbotScreen({ onNavigate }: ChatbotScreenProps) {
  const audioRef         = useRef<HTMLAudioElement | null>(null);
  const messagesEndRef   = useRef<HTMLDivElement>(null);
  const messageRefs      = useRef<Record<string, HTMLDivElement | null>>({});
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef        = useRef<BlobPart[]>([]);

  const [messages,        setMessages]        = useState<Message[]>([]);
  const [sessionId,       setSessionId]       = useState<string | null>(null);
  const [inputText,       setInputText]       = useState('');
  const [isTyping,        setIsTyping]        = useState(false);
  const [mode,            setMode]            = useState<'default' | 'administrative_qa' | 'document_suggestion' | 'booking'>('default');
  const [conversations,   setConversations]   = useState<Conversation[]>([]);
  const [recentSessions,  setRecentSessions]  = useState<ChatSessionSummary[]>([]);
  const [loadingSessions, setLoadingSessions] = useState(false);
  const [showSearch,      setShowSearch]      = useState(false);
  const [searchTerm,      setSearchTerm]      = useState('');
  const [isRecording,     setIsRecording]     = useState(false);
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false);

  const activeConversationId = sessionId ?? '__local__';

  /* ── cleanup ── */
  useEffect(() => {
    return () => {
      if (audioRef.current) { audioRef.current.pause(); audioRef.current = null; }
    };
  }, []);

  /* ── persistence ── */
  const STORAGE_KEY = 'chat_conversations_v1';

  const loadConversations = useCallback(() => {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return [] as Conversation[];
      const parsed = JSON.parse(raw) as {
        id: string; title?: string; lastUpdated: number;
        messages: Array<Omit<Message, 'timestamp'> & { timestamp: string }>;
      }[];
      return parsed.map((c) => ({
        id: c.id, title: c.title, lastUpdated: c.lastUpdated,
        messages: c.messages.map((m) => ({ ...m, timestamp: new Date(m.timestamp) })),
      }));
    } catch { return [] as Conversation[]; }
  }, []);

  const saveConversations = useCallback((items: Conversation[]) => {
    const payload = items.map((c) => ({
      id: c.id, title: c.title, lastUpdated: c.lastUpdated,
      messages: c.messages.map((m) => ({ id: m.id, text: m.text, isBot: m.isBot, timestamp: m.timestamp.toISOString() })),
    }));
    localStorage.setItem(STORAGE_KEY, JSON.stringify(payload));
  }, []);

  const createMessageId = useCallback((prefix: string) =>
    `${prefix}-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`, []);

  const appendBotMessage = useCallback((text: string, actions?: Message['actions']) => {
    const msg: Message = { id: createMessageId('bot'), text, isBot: true, timestamp: new Date(), actions };
    setMessages((prev) => [...prev, msg]);
    setConversations((prev) => {
      const id = activeConversationId;
      const next = [...prev];
      const idx = next.findIndex((c) => c.id === id);
      if (idx === -1) { next.push({ id, lastUpdated: Date.now(), messages: [msg] }); }
      else { next[idx] = { ...next[idx], lastUpdated: Date.now(), messages: [...next[idx].messages, msg] }; }
      saveConversations(next);
      return next;
    });
  }, [createMessageId, activeConversationId, saveConversations]);

  const appendUserMessage = useCallback((text: string) => {
    const msg: Message = { id: createMessageId('user'), text, isBot: false, timestamp: new Date() };
    setMessages((prev) => [...prev, msg]);
    setConversations((prev) => {
      const id = activeConversationId;
      const next = [...prev];
      const idx = next.findIndex((c) => c.id === id);
      if (idx === -1) { next.push({ id, lastUpdated: Date.now(), messages: [msg] }); }
      else { next[idx] = { ...next[idx], lastUpdated: Date.now(), messages: [...next[idx].messages, msg] }; }
      saveConversations(next);
      return next;
    });
  }, [createMessageId, activeConversationId, saveConversations]);

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => { scrollToBottom(); }, [messages, scrollToBottom]);

  /* ── greeting ── */
  useEffect(() => {
    if (messages.length > 0) return;
    if (recentSessions.length > 0 || conversations.length > 0) return;
    appendBotMessage('Xin chào ông/bà. Tôi là Trợ lý Số của Cổng Dịch vụ công. Tôi có thể hỗ trợ ông/bà tra cứu thông tin thủ tục, nộp hồ sơ trực tuyến hoặc giải đáp các thắc mắc về hành chính công.\n\nHôm nay ông/bà cần hỗ trợ về thủ tục nào ạ?', [
      { label: 'Hỏi đáp hành chính',         action: () => appendBotMessage('Bạn có thể hỏi tôi về thủ tục, thời hạn, lệ phí hoặc cơ quan phụ trách. Hãy nhập câu hỏi cụ thể.') },
      { label: 'Gợi ý các giấy tờ liên quan', action: () => appendBotMessage('Vui lòng cho biết loại thủ tục hoặc mục đích để tôi gợi ý bộ giấy tờ cần chuẩn bị.') },
      { label: 'Đặt lịch',                    action: () => appendBotMessage('Để đặt lịch, vui lòng cho tôi biết loại dịch vụ và khoảng thời gian mong muốn.') },
    ]);
  }, [appendBotMessage, messages.length, recentSessions.length, conversations.length]);

  /* ── load local ── */
  useEffect(() => {
    const loaded = loadConversations();
    setConversations(loaded);
    const active = loaded.find((c) => c.id === activeConversationId);
    if (active) setMessages(active.messages);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  /* ── fetch sessions ── */
  useEffect(() => {
    let cancelled = false;
    const run = async () => {
      setLoadingSessions(true);
      try {
        const resp = await chatbotAPI.getRecentSessions(10);
        if (!cancelled && resp?.success && Array.isArray(resp.data?.sessions))
          setRecentSessions(resp.data.sessions);
      } catch { console.warn('getRecentSessions failed; using local fallback'); }
      finally { if (!cancelled) setLoadingSessions(false); }
    };
    run();
    return () => { cancelled = true; };
  }, []);

  const normalizedQuery = searchTerm.trim().toLowerCase();

  /* ── send ── */
  const handleSend = useCallback(async () => {
    const trimmed = inputText.trim();
    if (!trimmed || isTyping) return;
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
            setConversations((prev) => {
              const localId = '__local__';
              const idxLocal = prev.findIndex((c) => c.id === localId);
              let next = [...prev];
              if (idxLocal !== -1) {
                const idxTarget = next.findIndex((c) => c.id === normalizedSessionId!);
                if (idxTarget === -1) { next[idxLocal] = { ...next[idxLocal], id: normalizedSessionId!, lastUpdated: Date.now() }; }
                else {
                  next[idxTarget] = { ...next[idxTarget], lastUpdated: Math.max(next[idxTarget].lastUpdated, next[idxLocal].lastUpdated), messages: [...next[idxTarget].messages, ...next[idxLocal].messages] };
                  next = next.filter((_, i) => i !== idxLocal);
                }
                saveConversations(next);
              }
              return next;
            });
          }
          setSessionId(normalizedSessionId ?? null);
          const explanationText = explanation || 'Các thủ tục liên quan được đề xuất gồm:';
          if (suggestions && suggestions.length > 0) {
            const block = suggestions.map((s, idx) => {
              let name = (s.procedure_name || 'Không rõ tên thủ tục').trim();
              if (!/[.?!…]$/.test(name)) name += '.';
              return ` ${idx + 1}. ${name}`;
            }).join('\n');
            appendBotMessage(`${explanationText}\n${block}`);
          } else { appendBotMessage('Không tìm thấy thủ tục phù hợp.'); }
        } else { appendBotMessage(resp.message || 'Không thể lấy gợi ý giấy tờ.'); }

      } else if (mode === 'booking') {
        const dialog = await voiceAPI.dialog(trimmed, sessionId ?? undefined, undefined, true);
        appendBotMessage(dialog.reply);
        if (dialog.audio?.base64) {
          try {
            if (audioRef.current) { audioRef.current.pause(); audioRef.current.currentTime = 0; }
            const audioEl = new Audio(`data:${dialog.audio.mimeType || 'audio/mpeg'};base64,${dialog.audio.base64}`);
            audioRef.current = audioEl;
            void audioEl.play();
          } catch (e) { console.warn('Audio playback failed:', e); }
        }

      } else {
        const response = await chatbotAPI.sendMessage({ message: trimmed, sessionId: sessionId ?? undefined, intent: mode === 'administrative_qa' ? 'administrative_qa' : undefined, speak: true });
        if (response.warnings?.length) console.warn('[chatbotAPI]', response.warnings.join(' | '));
        const nextSessionId = response.data?.sessionId ?? sessionId;
        const normalizedSessionId = nextSessionId && nextSessionId.trim().length > 0 ? nextSessionId : null;
        if (sessionId == null && normalizedSessionId) {
          setConversations((prev) => {
            const localId = '__local__';
            const idxLocal = prev.findIndex((c) => c.id === localId);
            if (idxLocal === -1) return prev;
            const idxTarget = prev.findIndex((c) => c.id === normalizedSessionId);
            let next = [...prev];
            if (idxTarget === -1) { next[idxLocal] = { ...next[idxLocal], id: normalizedSessionId }; }
            else {
              next[idxTarget] = { ...next[idxTarget], lastUpdated: Math.max(next[idxTarget].lastUpdated, next[idxLocal].lastUpdated), messages: [...next[idxTarget].messages, ...next[idxLocal].messages] };
              next = next.filter((_, i) => i !== idxLocal);
            }
            saveConversations(next);
            return next;
          });
        }
        setSessionId(normalizedSessionId);
        appendBotMessage(response.data?.response ?? 'Xin lỗi, hệ thống chưa có phản hồi phù hợp.');
        if (response.data?.audio?.base64) {
          try {
            if (audioRef.current) { audioRef.current.pause(); audioRef.current.currentTime = 0; }
            const audioEl = new Audio(`data:${response.data.audio.mimeType || 'audio/mpeg'};base64,${response.data.audio.base64}`);
            audioRef.current = audioEl;
            void audioEl.play();
          } catch (e) { console.warn('Audio playback failed:', e); }
        }
      }
    } catch (error) {
      console.error('Chatbot sendMessage failed:', error);
      appendBotMessage(error instanceof Error ? error.message : 'Rất tiếc, chatbot đang gặp sự cố. Vui lòng thử lại sau.');
    } finally { setIsTyping(false); }
  }, [appendBotMessage, appendUserMessage, inputText, isTyping, sessionId, mode, saveConversations]);

  /* ── recording ── */
  const startRecording = useCallback(async () => {
    if (isRecording) return;
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mr = new MediaRecorder(stream, { mimeType: 'audio/webm' });
      chunksRef.current = [];
      mr.ondataavailable = (ev) => { if (ev.data && ev.data.size > 0) chunksRef.current.push(ev.data); };
      mr.onstop = async () => {
        try {
          const blob = new Blob(chunksRef.current, { type: 'audio/webm' });
          const stt = await voiceAPI.stt(blob);
          if (stt.status === 'success' && stt.text) {
            if (mode === 'booking') {
              appendUserMessage(stt.text);
              const dialog = await voiceAPI.dialog(stt.text, sessionId ?? undefined, undefined, true);
              appendBotMessage(dialog.reply);
              if (dialog.audio?.base64) {
                try {
                  if (audioRef.current) { audioRef.current.pause(); audioRef.current.currentTime = 0; }
                  const audioEl = new Audio(`data:${dialog.audio.mimeType || 'audio/mpeg'};base64,${dialog.audio.base64}`);
                  audioRef.current = audioEl;
                  void audioEl.play();
                } catch (e) { console.warn('Audio playback failed:', e); }
              }
            } else { setInputText(stt.text); }
          } else { appendBotMessage(stt.message || 'Không nhận diện được giọng nói.'); }
        } catch (e: any) { appendBotMessage(e?.message || 'Lỗi ghi âm/STT.'); }
      };
      mr.start();
      mediaRecorderRef.current = mr;
      setIsRecording(true);
    } catch { appendBotMessage('Không truy cập được micro. Vui lòng cấp quyền.'); }
  }, [appendBotMessage, appendUserMessage, isRecording, mode, sessionId]);

  const stopRecording = useCallback(() => {
    const mr = mediaRecorderRef.current;
    if (!mr) return;
    if (mr.state !== 'inactive') mr.stop();
    setIsRecording(false);
    mediaRecorderRef.current = null;
  }, []);

  /* ── conversation management ── */
  const startNewConversation = useCallback(() => {
    setSessionId(null);
    setMessages([]);
    setConversations((prev) => {
      const next = [...prev];
      const now = Date.now();
      const idxLocal = next.findIndex((c) => c.id === '__local__');
      if (idxLocal !== -1 && next[idxLocal].messages.length > 0) {
        next[idxLocal] = { ...next[idxLocal], id: `draft-${now}`, lastUpdated: now };
        next.unshift({ id: '__local__', lastUpdated: now, messages: [] });
      } else if (idxLocal === -1) {
        next.unshift({ id: '__local__', lastUpdated: now, messages: [] });
      } else {
        next[idxLocal] = { ...next[idxLocal], lastUpdated: now, messages: [] };
      }
      saveConversations(next);
      return next;
    });
  }, [saveConversations]);

  const handleSelectConversation = useCallback(async (id: string) => {
    const conv = conversations.find((c) => c.id === id);
    if (conv) { setMessages(conv.messages); setSessionId(id === '__local__' ? null : id); return; }
    try {
      const resp = await chatbotAPI.getSessionMessages(id);
      if (resp?.success && resp.data?.messages) {
        const mapped: Message[] = resp.data.messages.map((m) => ({
          id: createMessageId(m.role === 'assistant' ? 'bot' : 'user'),
          text: m.content, isBot: m.role === 'assistant',
          timestamp: m.timestamp ? new Date(m.timestamp) : new Date(),
        }));
        setMessages(mapped);
        setSessionId(id);
        setConversations((prev) => {
          const next = [...prev];
          const idx = next.findIndex((c) => c.id === id);
          const lastUpdated = mapped.length ? mapped[mapped.length - 1].timestamp.getTime() : Date.now();
          if (idx === -1) { next.push({ id, lastUpdated, messages: mapped }); }
          else { next[idx] = { ...next[idx], lastUpdated, messages: mapped }; }
          saveConversations(next);
          return next;
        });
      }
    } catch (e) { console.error('Failed to load session messages', e); }
  }, [conversations, createMessageId, saveConversations]);

  const startModeConversation = useCallback((newMode: typeof mode, greeting: string) => {
    startNewConversation();
    setMode(newMode);
    appendBotMessage(greeting);
  }, [appendBotMessage, startNewConversation]);

  const startAdministrativeQA   = useCallback(() => startModeConversation('administrative_qa',   'Chào bạn, tôi là Trợ lý hành chính của E-Map. Bạn hãy nhập câu hỏi về thủ tục, lệ phí, thời hạn xử lý hoặc cơ quan phụ trách để tôi hỗ trợ.'), [startModeConversation]);
  const startDocumentSuggestion = useCallback(() => startModeConversation('document_suggestion', 'Chào bạn, tôi sẽ gợi ý các giấy tờ liên quan. Vui lòng nhập loại thủ tục hoặc mục đích để tôi liệt kê giấy tờ cần chuẩn bị.'), [startModeConversation]);
  const startBooking            = useCallback(() => startModeConversation('booking',             'Bạn đang bắt đầu yêu cầu Đặt lịch. Vui lòng nhập loại dịch vụ và thời điểm mong muốn.'), [startModeConversation]);

  const handleKeyPress = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); void handleSend(); }
  };

  const formatTime = (date: Date) =>
    date.toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' });

  /* ── mode list ── */
  const MODES = [
    { key: 'default'             as const, label: 'Tổng quát',     fn: startNewConversation    },
    { key: 'administrative_qa'   as const, label: 'Hỏi đáp',       fn: startAdministrativeQA  },
    { key: 'document_suggestion' as const, label: 'Gợi ý giấy tờ', fn: startDocumentSuggestion },
    { key: 'booking'             as const, label: 'Đặt lịch',      fn: startBooking            },
  ];

  /* ── sidebar nav items ── */
  const sidebarNavItems = [
    { icon: <MessageSquarePlus className="w-5 h-5 flex-shrink-0" />, label: 'Đoạn chat mới',      onClick: startNewConversation,             active: false },
    { icon: <SearchIcon        className="w-5 h-5 flex-shrink-0" />, label: 'Tìm kiếm đoạn chat', onClick: () => setShowSearch(v => !v),      active: false },
    { icon: <Image             className="w-5 h-5 flex-shrink-0" />, label: 'Ảnh',                 onClick: () => {},                         active: false },
    { icon: <Calendar          className="w-5 h-5 flex-shrink-0" />, label: 'Đặt lịch online',    onClick: startBooking,                     active: false },
  ];

  /* ── session history list shared ── */
  const sessionList = recentSessions.length > 0
    ? recentSessions
        .filter(s => !normalizedQuery || s.summary?.toLowerCase().includes(normalizedQuery) || s.sessionId.toLowerCase().includes(normalizedQuery))
        .slice(0, 8)
        .map(s => ({
          id: s.sessionId,
          title: s.summary || 'Không có tiêu đề',
          time: s.createdAt ? new Date(s.createdAt).toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' }) : '',
          active: s.sessionId === activeConversationId,
        }))
    : [...conversations]
        .sort((a, b) => b.lastUpdated - a.lastUpdated)
        .filter(c => {
          if (!normalizedQuery) return true;
          const last = c.messages[c.messages.length - 1];
          return c.id.toLowerCase().includes(normalizedQuery) || last?.text?.toLowerCase().includes(normalizedQuery);
        })
        .slice(0, 8)
        .map(c => {
          const last = c.messages[c.messages.length - 1];
          const firstUser = c.messages.find(m => !m.isBot);
          return {
            id: c.id,
            title: (firstUser?.text || '').trim() || (c.id === '__local__' ? 'Cuộc trò chuyện mới' : last?.text || 'Không có tiêu đề'),
            time: last ? formatTime(last.timestamp) : '',
            active: c.id === activeConversationId,
          };
        });

  /* ══════════════════════════════════════════
     Render
  ══════════════════════════════════════════ */
  return (
    <div
      className="flex h-screen overflow-hidden"
      style={{ backgroundColor: '#fff4f4', fontFamily: 'Manrope, sans-serif', color: '#4d2128' }}
    >

      {/* ════════════════════════════════════
          DESKTOP SIDEBAR  (md+)
      ════════════════════════════════════ */}
      <aside
        className="hidden md:flex flex-col h-screen p-4 flex-shrink-0"
        style={{ backgroundColor: '#ffeced', width: '17rem' }}
      >
        {/* Logo */}
        <div className="flex items-center gap-3 px-2 mb-5">
          <div className="w-10 h-10 rounded-xl flex items-center justify-center text-white flex-shrink-0" style={{ backgroundColor: '#b7131a' }}>
            <Sun className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-sm font-black leading-tight" style={{ color: '#b7131a' }}>
              Chatbot Dịch vụ<br />Hành chính công
            </h1>
            <p className="text-[11px] font-medium mt-0.5" style={{ color: '#4d2128', opacity: 0.6 }}>
              Trợ lý hành chính thông minh
            </p>
          </div>
        </div>

        {/* Nav */}
        <nav className="space-y-0.5">
          {/* Back to home */}
          <button
            onClick={() => onNavigate('home')}
            className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-200 active:scale-95 hover:bg-white"
            style={{ color: '#4d2128', opacity: 0.7 }}
          >
            <ArrowLeft className="w-4 h-4 flex-shrink-0" />
            <span className="text-sm font-bold">Về trang chủ</span>
          </button>
          {sidebarNavItems.map((item, i) => (
            <button
              key={i}
              onClick={item.onClick}
              className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-200 active:scale-95 hover:bg-white"
              style={{ color: '#4d2128', opacity: 0.7 }}
            >
              {item.icon}
              <span className="text-sm font-bold">{item.label}</span>
            </button>
          ))}
        </nav>

        {/* Search box */}
        {showSearch && (
          <div className="mt-2 px-1">
            <div className="flex items-center gap-2 bg-white border px-3 py-2 rounded-xl" style={{ borderColor: '#de9ca4' }}>
              <SearchIcon className="w-3.5 h-3.5 flex-shrink-0" style={{ color: '#824c54' }} />
              <input
                placeholder="Tìm kiếm..."
                value={searchTerm}
                onChange={e => setSearchTerm(e.target.value)}
                className="flex-1 text-xs outline-none bg-transparent"
                style={{ color: '#4d2128' }}
              />
            </div>
          </div>
        )}

        {/* Session history */}
        <div className="flex-1 overflow-y-auto mt-3 space-y-0.5 [scrollbar-width:none] [&::-webkit-scrollbar]:hidden">
          {loadingSessions && sessionList.length === 0 &&
            Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="animate-pulse h-10 rounded-xl" style={{ backgroundColor: '#ffd9dd' }} />
            ))
          }
          {sessionList.map(s => (
            <button key={s.id} type="button"
              onClick={() => handleSelectConversation(s.id)}
              className="w-full text-left px-3 py-2 rounded-xl transition-all text-xs"
              style={{ backgroundColor: s.active ? '#ffd9dd' : undefined, color: '#4d2128' }}>
              <p className="font-medium truncate">{s.title}</p>
              {s.time && <p className="mt-0.5" style={{ opacity: 0.5 }}>{s.time}</p>}
            </button>
          ))}
        </div>

        {/* Bottom */}
        <div className="mt-3 pt-3 space-y-0.5" style={{ borderTop: '1px solid rgba(222,156,164,0.25)' }}>
          <button className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all hover:bg-white active:scale-95"
            style={{ color: '#4d2128', opacity: 0.7 }}>
            <Settings className="w-4 h-4 flex-shrink-0" />
            <span className="text-sm font-bold">Cài đặt</span>
          </button>
          <button className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all hover:bg-white active:scale-95"
            style={{ color: '#4d2128', opacity: 0.7 }}>
            <HelpCircle className="w-4 h-4 flex-shrink-0" />
            <span className="text-sm font-bold">Trợ giúp</span>
          </button>
        </div>
      </aside>

      {/* ════════════════════════════════════
          MOBILE DRAWER  (< md)
      ════════════════════════════════════ */}
      {mobileSidebarOpen && (
        <div className="md:hidden fixed inset-0 z-50 flex">
          <div className="absolute inset-0 bg-black/50" onClick={() => setMobileSidebarOpen(false)} />
          <aside
            className="relative flex flex-col h-full p-5 w-72 overflow-y-auto"
            style={{ backgroundColor: '#ffeced' }}
          >
            {/* Close + logo */}
            <div className="flex items-center justify-between mb-5">
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-xl flex items-center justify-center text-white" style={{ backgroundColor: '#b7131a' }}>
                  <Sun className="w-4 h-4" />
                </div>
                <span className="text-sm font-black" style={{ color: '#b7131a' }}>Dịch vụ Hành chính</span>
              </div>
              <button onClick={() => setMobileSidebarOpen(false)} aria-label="Đóng menu"
                className="p-2 rounded-xl hover:bg-white transition-colors" style={{ color: '#824c54' }}>
                <ArrowLeft className="w-4 h-4" />
              </button>
            </div>

            <nav className="space-y-0.5">
              <button onClick={() => { onNavigate('home'); setMobileSidebarOpen(false); }}
                className="w-full flex items-center gap-3 px-3 py-3 rounded-xl transition-all hover:bg-white active:scale-95"
                style={{ color: '#4d2128', opacity: 0.75 }}>
                <ArrowLeft className="w-4 h-4 flex-shrink-0" />
                <span className="text-sm font-bold">Về trang chủ</span>
              </button>
              <button onClick={() => { startNewConversation(); setMobileSidebarOpen(false); }}
                className="w-full flex items-center gap-3 px-3 py-3 rounded-xl shadow-sm transition-all active:scale-95"
                style={{ backgroundColor: '#ffffff', color: '#b7131a' }}>
                <MessageSquarePlus className="w-4 h-4 flex-shrink-0" />
                <span className="text-sm font-bold">Đoạn chat mới</span>
              </button>
              {sidebarNavItems.slice(1).map((item, i) => (
                <button key={i} onClick={() => { item.onClick(); setMobileSidebarOpen(false); }}
                  className="w-full flex items-center gap-3 px-3 py-3 rounded-xl transition-all hover:bg-white active:scale-95"
                  style={{ color: '#4d2128', opacity: 0.75 }}>
                  {item.icon}
                  <span className="text-sm font-bold">{item.label}</span>
                </button>
              ))}
            </nav>

            {/* Mode chips in drawer */}
            <div className="mt-4 pt-4" style={{ borderTop: '1px solid rgba(222,156,164,0.25)' }}>
              <p className="text-[10px] font-bold uppercase tracking-wider mb-2" style={{ color: '#824c54', opacity: 0.6 }}>Chế độ</p>
              <div className="grid grid-cols-2 gap-2">
                {MODES.map(m => (
                  <button key={m.key}
                    onClick={() => { m.fn(); setMobileSidebarOpen(false); }}
                    className="px-3 py-2 rounded-xl text-xs font-bold transition-all"
                    style={{
                      backgroundColor: mode === m.key ? '#b7131a' : '#ffffff',
                      color: mode === m.key ? '#ffffff' : '#4d2128',
                    }}>
                    {m.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Sessions */}
            {sessionList.length > 0 && (
              <div className="mt-4 flex-1 overflow-y-auto space-y-0.5 [scrollbar-width:none] [&::-webkit-scrollbar]:hidden">
                <p className="text-[10px] font-bold uppercase tracking-wider mb-2" style={{ color: '#824c54', opacity: 0.6 }}>Lịch sử</p>
                {sessionList.map(s => (
                  <button key={s.id} type="button"
                    onClick={() => { handleSelectConversation(s.id); setMobileSidebarOpen(false); }}
                    className="w-full text-left px-3 py-2 rounded-xl transition-all text-xs"
                    style={{ backgroundColor: s.active ? '#ffd9dd' : undefined, color: '#4d2128' }}>
                    <p className="font-medium truncate">{s.title}</p>
                    {s.time && <p className="mt-0.5" style={{ opacity: 0.5 }}>{s.time}</p>}
                  </button>
                ))}
              </div>
            )}
          </aside>
        </div>
      )}

      {/* ════════════════════════════════════
          MAIN CONTENT AREA
      ════════════════════════════════════ */}
      <main className="flex-1 flex flex-col min-w-0 overflow-hidden" style={{ backgroundColor: '#fff4f4' }}>

        {/* ── Top Header (sticky, not fixed) ── */}
        <header
          className="flex-shrink-0 flex items-center justify-between px-3 md:px-6 py-3 md:py-4 z-40"
          style={{
            backgroundColor: 'rgba(255,244,244,0.92)',
            backdropFilter: 'blur(12px)',
            boxShadow: '0px 4px 24px rgba(77,33,40,0.06)',
          }}
        >
          {/* Left: menu + title */}
          <div className="flex items-center gap-2 min-w-0">
            <button
              className="md:hidden p-2 rounded-xl transition-colors flex-shrink-0"
              style={{ color: '#b7131a' }}
              onClick={() => setMobileSidebarOpen(true)}
              aria-label="Mở menu"
            >
              <Menu className="w-5 h-5" />
            </button>
            {/* Mobile: back arrow */}
            <button
              className="md:hidden p-2 rounded-xl transition-colors flex-shrink-0"
              style={{ color: '#b7131a' }}
              onClick={() => onNavigate('home')}
              aria-label="Về trang chủ"
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
            <span className="font-black tracking-tight truncate text-base md:text-xl" style={{ color: '#b7131a' }}>
              <span className="hidden sm:inline">Chatbot Dịch vụ Hành chính công</span>
              <span className="sm:hidden">Hành chính công</span>
            </span>
          </div>

          {/* Right: desktop mode tabs + actions */}
          <div className="flex items-center gap-2 flex-shrink-0">
            {/* Mode tabs — desktop only */}
            <div className="hidden lg:flex items-center gap-6 mr-2">
              {MODES.map(m => (
                <button key={m.key} onClick={() => m.fn()}
                  className="font-bold text-sm transition-colors active:opacity-70"
                  style={{
                    color: mode === m.key ? '#b7131a' : '#9f364c',
                    opacity: mode === m.key ? 1 : 0.75,
                    borderBottom: mode === m.key ? '2px solid #fdc003' : '2px solid transparent',
                    paddingBottom: '2px',
                  }}>
                  {m.label}
                </button>
              ))}
            </div>
            <button className="hidden sm:flex p-2 rounded-xl transition-colors active:opacity-70" aria-label="Chia sẻ" style={{ color: '#b7131a' }}>
              <Share2 className="w-4 h-4" />
            </button>
            <button className="hidden sm:flex p-2 rounded-xl transition-colors active:opacity-70" aria-label="Cài đặt" style={{ color: '#b7131a' }}>
              <Settings className="w-4 h-4" />
            </button>
            <div className="w-8 h-8 rounded-full flex items-center justify-center border flex-shrink-0"
              style={{ backgroundColor: '#ffd2d6', borderColor: 'rgba(183,19,26,0.1)' }}>
              <User className="w-4 h-4" style={{ color: '#b7131a' }} />
            </div>
          </div>
        </header>

        {/* ── Mode chips row — mobile & tablet (< lg) ── */}
        <div
          className="lg:hidden flex-shrink-0 flex items-center gap-2 px-3 py-2 overflow-x-auto [scrollbar-width:none] [&::-webkit-scrollbar]:hidden"
          style={{ borderBottom: '1px solid rgba(222,156,164,0.15)' }}
        >
          {MODES.map(m => (
            <button key={m.key} onClick={() => m.fn()}
              className="flex-shrink-0 px-3 py-1.5 rounded-full text-xs font-bold transition-all"
              style={{
                backgroundColor: mode === m.key ? '#b7131a' : '#ffffff',
                color: mode === m.key ? '#ffffff' : '#4d2128',
                border: '1px solid',
                borderColor: mode === m.key ? '#b7131a' : '#de9ca4',
              }}>
              {m.label}
            </button>
          ))}
        </div>

        {/* ── Chat Messages ── */}
        <section className="flex-1 overflow-y-auto [scrollbar-width:thin] [scrollbar-color:#de9ca4_transparent]">
          <div
            className="max-w-3xl mx-auto px-3 md:px-4 space-y-6 md:space-y-8"
            style={{ paddingTop: '1.5rem', paddingBottom: '9rem' }}
          >
            {messages.map((msg) => (
              <div
                key={msg.id}
                ref={el => { messageRefs.current[msg.id] = el; }}
                className={`flex items-end gap-2 md:gap-3 ${msg.isBot ? '' : 'flex-row-reverse'}`}
              >
                {/* Avatar */}
                <div
                  className="w-7 h-7 md:w-8 md:h-8 rounded-lg flex items-center justify-center flex-shrink-0 mb-5"
                  style={msg.isBot
                    ? { backgroundColor: '#fdc003', color: '#3d2b00' }
                    : { backgroundColor: '#b7131a', color: '#ffffff' }
                  }
                >
                  {msg.isBot ? <Bot className="w-3.5 h-3.5" /> : <User className="w-3.5 h-3.5" />}
                </div>

                {/* Bubble + meta */}
                <div className={`space-y-1.5 min-w-0 ${msg.isBot ? 'max-w-[88%] md:max-w-[80%]' : 'max-w-[88%] md:max-w-[75%] flex flex-col items-end'}`}>
                  <div
                    className="px-4 py-3 md:px-5 md:py-4 leading-relaxed"
                    style={msg.isBot
                      ? { backgroundColor: '#ffffff', color: '#4d2128', borderRadius: '0.25rem 1rem 1rem 1rem', boxShadow: '0px 4px 16px rgba(183,19,26,0.06)' }
                      : { backgroundColor: '#ffd9dd', color: '#4d2128', borderRadius: '1rem 0.25rem 1rem 1rem', boxShadow: '0 2px 8px rgba(183,19,26,0.08)', border: '1px solid rgba(222,156,164,0.25)' }
                    }
                  >
                    {msg.text.includes('\n') ? (
                      <div className="text-sm leading-relaxed">
                        {msg.text.split('\n').map((line, i) => (
                          <p key={i} className="m-0">{line.trim() === '' ? '\u00A0' : line}</p>
                        ))}
                      </div>
                    ) : (
                      <p className="text-sm leading-relaxed whitespace-pre-wrap">{msg.text}</p>
                    )}
                  </div>

                  {/* Action chips */}
                  {msg.actions && msg.actions.length > 0 && (
                    <div className="flex gap-1.5 flex-wrap">
                      {msg.actions.map((action, i) => (
                        <button key={i} onClick={action.action}
                          className="px-3 py-1.5 rounded-full text-xs font-bold transition-colors"
                          style={{ border: '1px solid #de9ca4', color: '#4d2128', backgroundColor: 'transparent' }}
                          onMouseEnter={e => { (e.currentTarget as HTMLElement).style.backgroundColor = '#ffeced'; }}
                          onMouseLeave={e => { (e.currentTarget as HTMLElement).style.backgroundColor = 'transparent'; }}
                        >
                          {action.label}
                        </button>
                      ))}
                    </div>
                  )}

                  <span className="text-[10px] font-medium px-1" style={{ color: '#824c54', opacity: 0.55 }}>
                    {formatTime(msg.timestamp)}
                  </span>
                </div>
              </div>
            ))}

            {/* Typing indicator */}
            {isTyping && (
              <div className="flex items-end gap-2 md:gap-3">
                <div className="w-7 h-7 md:w-8 md:h-8 rounded-lg flex items-center justify-center flex-shrink-0"
                  style={{ backgroundColor: '#fdc003', color: '#3d2b00' }}>
                  <Bot className="w-3.5 h-3.5" />
                </div>
                <div className="px-5 py-4 rounded-xl" style={{ backgroundColor: '#ffffff', boxShadow: '0px 4px 16px rgba(183,19,26,0.06)', borderRadius: '0.25rem 1rem 1rem 1rem' }}>
                  <div className="flex gap-1.5 items-center h-4">
                    <div className="w-2 h-2 rounded-full animate-bounce" style={{ backgroundColor: '#b7131a', animationDelay: '0ms' }} />
                    <div className="w-2 h-2 rounded-full animate-bounce" style={{ backgroundColor: '#b7131a', animationDelay: '150ms' }} />
                    <div className="w-2 h-2 rounded-full animate-bounce" style={{ backgroundColor: '#b7131a', animationDelay: '300ms' }} />
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        </section>

        {/* ── Input Footer ── */}
        <footer
          className="flex-shrink-0 px-3 md:px-6 pt-3 pb-4 md:pb-6"
          style={{ background: 'linear-gradient(to top, #fff4f4 80%, rgba(255,244,244,0))' }}
        >
          <div className="max-w-3xl mx-auto">
            <div className="relative group">
              {/* Glow */}
              <div className="absolute inset-0 blur-xl rounded-full opacity-0 group-focus-within:opacity-100 transition-opacity pointer-events-none"
                style={{ backgroundColor: 'rgba(253,192,3,0.12)' }} />
              <div
                className="relative flex items-center rounded-full p-1.5 shadow-lg transition-all"
                style={{ backgroundColor: '#ffffff', border: '2px solid rgba(253,192,3,0.25)' }}
              >
                {/* Attach — hidden on very small screens */}
                <button aria-label="Đính kèm tệp" className="hidden sm:flex p-2.5 transition-colors rounded-full" style={{ color: '#824c54' }}>
                  <Paperclip className="w-4 h-4 md:w-5 md:h-5" />
                </button>
                <input
                  type="text"
                  value={inputText}
                  onChange={e => setInputText(e.target.value)}
                  onKeyDown={handleKeyPress}
                  disabled={isTyping}
                  placeholder={isTyping ? 'Đang trả lời...' : 'Nhập yêu cầu của bạn...'}
                  className="flex-1 bg-transparent border-none outline-none focus:ring-0 px-3 font-medium disabled:opacity-60 text-sm"
                  style={{ color: '#4d2128', minWidth: 0 }}
                />
                <button
                  aria-label={isRecording ? 'Dừng ghi âm' : 'Ghi âm giọng nói'}
                  disabled={isTyping}
                  onClick={() => isRecording ? stopRecording() : startRecording()}
                  className="p-2.5 transition-colors rounded-full disabled:opacity-40"
                  style={{ color: isRecording ? '#b7131a' : '#824c54' }}
                >
                  <Mic className={`w-4 h-4 md:w-5 md:h-5 ${isRecording ? 'animate-pulse' : ''}`} />
                </button>
                <button
                  aria-label="Gửi tin nhắn"
                  onClick={() => void handleSend()}
                  disabled={!inputText.trim() || isTyping}
                  className="w-10 h-10 md:w-12 md:h-12 rounded-full flex items-center justify-center text-white shadow-md active:scale-95 transition-transform disabled:opacity-40 disabled:pointer-events-none flex-shrink-0"
                  style={{ background: 'linear-gradient(135deg, #b7131a, #ff766b)' }}
                >
                  <Send className="w-4 h-4 md:w-5 md:h-5" />
                </button>
              </div>
            </div>
            {/* Disclaimer — desktop only */}
            <p className="hidden md:block text-center mt-2 font-medium tracking-wide uppercase"
              style={{ fontSize: '9px', color: '#824c54', opacity: 0.5 }}>
              Thông tin mang tính tham khảo. Hãy kiểm tra văn bản quy phạm pháp luật thực tế.
            </p>
          </div>
        </footer>
      </main>
    </div>
  );
}
