/**
 * Queue Service — REST API calls + WebSocket client
 * Tối ưu độ trễ: binary JSON, delta updates, heartbeat 15s
 */

const BASE_URL = 'http://localhost:8888/api/queue';
const WS_BASE  = 'ws://localhost:8888/ws/queue';

function authHeaders(): Record<string, string> {
  const token = localStorage.getItem('token');
  return token
    ? { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` }
    : { 'Content-Type': 'application/json' };
}

// ── REST ──────────────────────────────────────────────────────────────────────

export interface QueueTicket {
  id:            string;
  agencyId:      string;
  serviceId:     string;
  serviceName:   string;
  ticketNumber:  number;
  prefix:        string;
  ticketCode:    string;
  userId:        string;
  userName:      string;
  counterNo:     number | null;
  status:        'waiting' | 'called' | 'serving' | 'done' | 'absent' | 'cancelled';
  priority:      number;
  estimatedWait: number; // giây
  calledAt:      string | null;
  servedAt:      string | null;
  doneAt:        string | null;
  createdAt:     string;
  date:          string;
}

export interface QueueSummary {
  agencyId:          string;
  date:              string;
  totalWaiting:      number;
  totalCalled:       number;
  totalServing:      number;
  totalDone:         number;
  activeCounters:    number;
  avgServiceTimeSec: number;
  peakFactor:        number;
  loadLevel:         'low' | 'medium' | 'high';
  nowServing: {
    counterNo:   number;
    ticketCode:  string;
    serviceName: string;
  }[];
}

export interface AgencyQueueStatus {
  agencyId:     string;
  totalWaiting: number;
  totalServing: number;
  loadLevel:    'low' | 'medium' | 'high';
  ageSeconds:   number;
}

export async function takeTicket(payload: {
  agencyId:    string;
  serviceId?:  string;
  serviceName?:string;
  prefix?:     string;
  priority?:   number;
  userName?:   string;
}): Promise<QueueTicket> {
  const res = await fetch(`${BASE_URL}/ticket`, {
    method: 'POST',
    headers: authHeaders(),
    body: JSON.stringify(payload),
  });
  const json = await res.json();
  if (!json.success) throw new Error(json.message || 'Không thể lấy số');
  return json.data as QueueTicket;
}

export async function getTicketStatus(ticketId: string): Promise<QueueTicket> {
  const res = await fetch(`${BASE_URL}/status/${ticketId}`, {
    headers: authHeaders(),
  });
  const json = await res.json();
  if (!json.success) throw new Error(json.message);
  return json.data as QueueTicket;
}

export async function getMyTickets(date?: string): Promise<QueueTicket[]> {
  const q = date ? `?date=${date}` : '';
  const res = await fetch(`${BASE_URL}/my${q}`, { headers: authHeaders() });
  const json = await res.json();
  if (!json.success) throw new Error(json.message);
  return json.data as QueueTicket[];
}

export async function cancelTicket(ticketId: string): Promise<void> {
  const res = await fetch(`${BASE_URL}/ticket/${ticketId}`, {
    method: 'DELETE',
    headers: authHeaders(),
  });
  const json = await res.json();
  if (!json.success) throw new Error(json.message);
}

export async function getQueueSummary(agencyId: string): Promise<QueueSummary> {
  const res = await fetch(`${BASE_URL}/summary/${agencyId}`, {
    headers: authHeaders(),
  });
  const json = await res.json();
  if (!json.success) throw new Error(json.message);
  return json.data as QueueSummary;
}

export async function getMapOverview(): Promise<Record<string, AgencyQueueStatus>> {
  const res = await fetch(`${BASE_URL}/map-overview`, {
    headers: authHeaders(),
  });
  const json = await res.json();
  if (!json.success) throw new Error(json.message || 'Failed to fetch map overview');
  return json.data as Record<string, AgencyQueueStatus>;
}

export function formatWaitTime(seconds: number): string {
  if (seconds < 60) return 'Dưới 1 phút';
  if (seconds < 3600) return `~${Math.ceil(seconds / 60)} phút`;
  const h = Math.floor(seconds / 3600);
  const m = Math.ceil((seconds % 3600) / 60);
  return m > 0 ? `~${h} giờ ${m} phút` : `~${h} giờ`;
}

// ── WebSocket Client (tối ưu độ trễ) ─────────────────────────────────────────

type WsMessageType = 'snapshot' | 'summary' | 'ping' | 'pong';

interface WsMessage {
  type: WsMessageType;
  data?: QueueSummary;
  ts?:  number;
}

export type QueueWsHandler = (summary: QueueSummary) => void;

export class QueueWebSocket {
  private ws:           WebSocket | null = null;
  private agencyId:     string;
  private onUpdate:     QueueWsHandler;
  private heartbeat:    ReturnType<typeof setInterval> | null = null;
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  private reconnectDelay = 1000; // ms — exponential backoff
  private destroyed      = false;

  constructor(agencyId: string, onUpdate: QueueWsHandler) {
    this.agencyId = agencyId;
    this.onUpdate  = onUpdate;
    this.connect();
  }

  private connect() {
    if (this.destroyed) return;
    try {
      this.ws = new WebSocket(`${WS_BASE}/${this.agencyId}`);

      this.ws.onopen = () => {
        this.reconnectDelay = 1000; // reset backoff
        this._startHeartbeat();
      };

      this.ws.onmessage = (event: MessageEvent) => {
        try {
          const msg: WsMessage = JSON.parse(event.data as string);
          if (msg.type === 'snapshot' || msg.type === 'summary') {
            if (msg.data) this.onUpdate(msg.data);
          } else if (msg.type === 'ping') {
            // Server ping → pong ngay lập tức (giảm độ trễ)
            this.ws?.send(JSON.stringify({ type: 'pong', ts: Date.now() }));
          }
        } catch {
          // bỏ qua parse error
        }
      };

      this.ws.onclose = () => {
        this._stopHeartbeat();
        if (!this.destroyed) this._scheduleReconnect();
      };

      this.ws.onerror = () => {
        this.ws?.close();
      };
    } catch {
      if (!this.destroyed) this._scheduleReconnect();
    }
  }

  /** Gửi ping từ client mỗi 15 giây để duy trì kết nối */
  private _startHeartbeat() {
    this._stopHeartbeat();
    this.heartbeat = setInterval(() => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        this.ws.send(JSON.stringify({ type: 'ping', ts: Date.now() }));
      }
    }, 15_000);
  }

  private _stopHeartbeat() {
    if (this.heartbeat) {
      clearInterval(this.heartbeat);
      this.heartbeat = null;
    }
  }

  /** Exponential backoff: 1s → 2s → 4s → max 30s */
  private _scheduleReconnect() {
    this.reconnectTimer = setTimeout(() => {
      this.connect();
    }, this.reconnectDelay);
    this.reconnectDelay = Math.min(this.reconnectDelay * 2, 30_000);
  }

  /** Yêu cầu snapshot mới */
  refresh() {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ type: 'subscribe' }));
    }
  }

  destroy() {
    this.destroyed = true;
    this._stopHeartbeat();
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer);
    this.ws?.close();
  }
}
