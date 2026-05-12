import { useState, useRef, useCallback, useEffect } from 'react';
import { Mic, MicOff, X, CheckCircle, Phone, Bot, User } from 'lucide-react';
import { voiceAPI } from '../services/api';

interface Props {
  isOpen: boolean;
  onClose: () => void;
  sessionId?: string | null;
}

interface DialogMessage {
  role: 'bot' | 'user';
  text: string;
}

const GREETING =
  'Xin chào! Tôi sẽ giúp bạn đặt lịch hẹn dịch vụ công. ' +
  'Nhấn giữ nút mic và nói tên dịch vụ bạn muốn đặt lịch ' +
  '(ví dụ: "Tôi muốn đặt lịch làm CCCD", "Đăng ký khai sinh"...).';

export function VoiceBookingModal({ isOpen, onClose, sessionId }: Props) {
  const [messages,     setMessages]     = useState<DialogMessage[]>([]);
  const [isRecording,  setIsRecording]  = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isDone,       setIsDone]       = useState(false);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef        = useRef<BlobPart[]>([]);
  const audioRef         = useRef<HTMLAudioElement | null>(null);
  const messagesEndRef   = useRef<HTMLDivElement>(null);
  const hasInit          = useRef(false);

  /* ── scroll to bottom ── */
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isProcessing]);

  /* ── cleanup on unmount (mic + audio) ── */
  useEffect(() => {
    return () => {
      if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
        mediaRecorderRef.current.stop();
      }
      if (audioRef.current) { audioRef.current.pause(); audioRef.current = null; }
    };
  }, []);

  /* ── init / reset on open/close ── */
  useEffect(() => {
    if (!isOpen) {
      // Stop any active recording when modal closes
      if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
        mediaRecorderRef.current.stop();
      }
      mediaRecorderRef.current = null;
      hasInit.current = false;
      setMessages([]);
      setIsDone(false);
      setIsRecording(false);
      setIsProcessing(false);
      return;
    }
    if (hasInit.current) return;
    hasInit.current = true;
    setMessages([{ role: 'bot', text: GREETING }]);
  }, [isOpen]);

  /* ── audio helper ── */
  const playAudio = useCallback(async (base64: string, mimeType = 'audio/mpeg') => {
    if (audioRef.current) { audioRef.current.pause(); audioRef.current = null; }
    const audio = new Audio(`data:${mimeType};base64,${base64}`);
    audioRef.current = audio;
    try {
      await audio.play();
    } catch {
      // Autoplay blocked hoặc tab không focus — im lặng
    }
  }, []);

  /* ── recording ── */
  const startRecording = useCallback(async () => {
    if (isRecording || isProcessing || isDone) return;
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mr = new MediaRecorder(stream, { mimeType: 'audio/webm' });
      chunksRef.current = [];
      mr.ondataavailable = ev => { if (ev.data?.size > 0) chunksRef.current.push(ev.data); };
      mr.onstop = async () => {
        stream.getTracks().forEach(t => t.stop());
        setIsRecording(false);
        setIsProcessing(true);
        try {
          const blob = new Blob(chunksRef.current, { type: 'audio/webm' });
          const stt = await voiceAPI.stt(blob);
          const userText = stt.status === 'success' && stt.text ? stt.text.trim() : '';
          if (!userText) {
            setMessages(prev => [...prev, { role: 'bot', text: 'Tôi không nghe rõ, bạn có thể nói lại không?' }]);
            return;
          }
          setMessages(prev => [...prev, { role: 'user', text: userText }]);
          const dialog = await voiceAPI.dialog(userText, sessionId ?? undefined, undefined, true);
          setMessages(prev => [...prev, { role: 'bot', text: dialog.reply }]);
          if (dialog.audio?.base64) playAudio(dialog.audio.base64, dialog.audio.mimeType);
          if (dialog.done) setIsDone(true);
        } catch (e: any) {
          setMessages(prev => [...prev, { role: 'bot', text: e?.message?.includes('quota') ? 'Lỗi' : 'Có lỗi xảy ra. Vui lòng thử lại.' }]);
        } finally {
          setIsProcessing(false);
        }
      };
      mr.start();
      mediaRecorderRef.current = mr;
      setIsRecording(true);
    } catch {
      setMessages(prev => [...prev, { role: 'bot', text: 'Không truy cập được micro. Vui lòng cấp quyền.' }]);
    }
  }, [isRecording, isProcessing, isDone, playAudio, sessionId]);

  const stopRecording = useCallback(() => {
    const mr = mediaRecorderRef.current;
    if (mr && mr.state !== 'inactive') mr.stop();
    mediaRecorderRef.current = null;
  }, []);

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-end sm:items-center justify-center"
      style={{ backgroundColor: 'rgba(77,33,40,0.55)', backdropFilter: 'blur(4px)' }}
      onClick={e => { if (e.target === e.currentTarget) onClose(); }}
    >
      <div
        className="w-full sm:max-w-md flex flex-col overflow-hidden"
        style={{
          backgroundColor: '#fff4f4',
          maxHeight: '88vh',
          borderRadius: '1.5rem 1.5rem 0 0',
          boxShadow: '0 -8px 40px rgba(77,33,40,0.2)',
        }}
      >
        {/* ── Header ── */}
        <div
          className="flex items-center justify-between px-5 py-4 flex-shrink-0"
          style={{ borderBottom: '1px solid rgba(222,156,164,0.3)', backgroundColor: '#ffeced', borderRadius: '1.5rem 1.5rem 0 0' }}
        >
          <div className="flex items-center gap-3">
            <div
              className="w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0"
              style={{ background: 'linear-gradient(135deg, #b7131a, #ff766b)' }}
            >
              <Phone className="w-4 h-4 text-white" />
            </div>
            <div>
              <p className="font-black text-sm" style={{ color: '#b7131a' }}>Đặt lịch qua giọng nói</p>
              <p className="text-xs font-medium" style={{ color: '#824c54' }}>
                {isDone ? 'Hoàn thành' : isRecording ? 'Đang ghi âm...' : isProcessing ? 'Đang xử lý...' : 'Nhấn giữ mic để nói'}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-xl transition-colors hover:bg-white active:scale-95"
            style={{ color: '#4d2128' }}
            aria-label="Đóng"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* ── Messages ── */}
        <div className="flex-1 overflow-y-auto px-4 py-4 space-y-3 [scrollbar-width:none] [&::-webkit-scrollbar]:hidden">
          {messages.map((msg, i) => (
            <div key={i} className={`flex items-end gap-2 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
              <div
                className="w-7 h-7 rounded-lg flex items-center justify-center flex-shrink-0 mb-1"
                style={msg.role === 'bot'
                  ? { backgroundColor: '#fdc003', color: '#3d2b00' }
                  : { backgroundColor: '#b7131a', color: '#fff' }}
              >
                {msg.role === 'bot' ? <Bot className="w-3.5 h-3.5" /> : <User className="w-3.5 h-3.5" />}
              </div>
              <div
                className="max-w-[80%] px-4 py-3 text-sm leading-relaxed"
                style={msg.role === 'bot'
                  ? { backgroundColor: '#fff', color: '#4d2128', borderRadius: '0.25rem 1rem 1rem 1rem', boxShadow: '0 2px 8px rgba(183,19,26,0.06)' }
                  : { backgroundColor: '#ffd9dd', color: '#4d2128', borderRadius: '1rem 0.25rem 1rem 1rem' }}
              >
                {msg.text}
              </div>
            </div>
          ))}

          {/* Typing indicator */}
          {isProcessing && (
            <div className="flex items-end gap-2">
              <div className="w-7 h-7 rounded-lg flex items-center justify-center" style={{ backgroundColor: '#fdc003', color: '#3d2b00' }}>
                <Bot className="w-3.5 h-3.5" />
              </div>
              <div className="px-4 py-3" style={{ backgroundColor: '#fff', borderRadius: '0.25rem 1rem 1rem 1rem', boxShadow: '0 2px 8px rgba(183,19,26,0.06)' }}>
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

        {/* ── Bottom: mic or success ── */}
        {isDone ? (
          /* Success */
          <div className="flex-shrink-0 px-5 pb-10 pt-5 flex flex-col items-center gap-3">
            <div
              className="w-16 h-16 rounded-full flex items-center justify-center"
              style={{ backgroundColor: 'rgba(40,167,69,0.12)' }}
            >
              <CheckCircle className="w-8 h-8" style={{ color: '#28a745' }} />
            </div>
            <p className="font-black text-base text-center" style={{ color: '#4d2128' }}>Đặt lịch thành công!</p>
            <button
              onClick={onClose}
              className="mt-1 px-8 py-2.5 rounded-full text-sm font-bold text-white transition-all active:scale-95 shadow-md"
              style={{ background: 'linear-gradient(135deg, #b7131a, #ff766b)' }}
            >
              Đóng
            </button>
          </div>
        ) : (
          /* Mic button */
          <div className="flex-shrink-0 px-5 pb-10 pt-4 flex flex-col items-center gap-3">
            {/* Waveform when recording */}
            <div className="h-8 flex items-center gap-1">
              {isRecording
                ? [0, 80, 160, 240, 320].map(delay => (
                    <div
                      key={delay}
                      className="w-1.5 rounded-full animate-bounce"
                      style={{ backgroundColor: '#b7131a', height: '24px', animationDelay: `${delay}ms` }}
                    />
                  ))
                : <div className="h-6" />
              }
            </div>

            <button
              onMouseDown={startRecording}
              onMouseUp={stopRecording}
              onTouchStart={e => { e.preventDefault(); void startRecording(); }}
              onTouchEnd={stopRecording}
              disabled={isProcessing}
              aria-label={isRecording ? 'Thả để gửi' : 'Nhấn giữ để nói'}
              className="w-20 h-20 rounded-full flex items-center justify-center transition-all active:scale-95 disabled:opacity-40"
              style={{
                background: isRecording
                  ? 'linear-gradient(135deg, #ff3333, #b7131a)'
                  : 'linear-gradient(135deg, #b7131a, #ff766b)',
                boxShadow: isRecording
                  ? '0 0 0 10px rgba(183,19,26,0.15), 0 0 0 20px rgba(183,19,26,0.06), 0 6px 24px rgba(183,19,26,0.35)'
                  : '0 6px 24px rgba(183,19,26,0.3)',
              }}
            >
              {isRecording
                ? <MicOff className="w-8 h-8 text-white" />
                : <Mic    className="w-8 h-8 text-white" />
              }
            </button>

            <p className="text-xs font-semibold" style={{ color: '#824c54' }}>
              {isProcessing ? 'Đang xử lý...' : isRecording ? 'Thả để gửi' : 'Nhấn giữ để nói'}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
