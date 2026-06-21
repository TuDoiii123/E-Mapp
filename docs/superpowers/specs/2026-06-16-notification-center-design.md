# Thiết kế: Trung tâm Thông báo (Notification Center) cho E-Mapp

- **Ngày**: 2026-06-16
- **Phạm vi**: Backend `Backend/` + Frontend `frontend/`
- **Bối cảnh**: Audit đối chiếu đồ án nghiên cứu với code phát hiện báo cáo mô tả Trung tâm
  Thông báo (mục "(h) Đánh giá và thông báo": danh sách thông báo trạng thái hồ sơ / nhắc lịch
  hẹn / thông báo hệ thống, đánh dấu đã đọc, push Firebase) nhưng thực tế `NotificationScreen.tsx`
  chỉ **suy ra phía client từ danh sách hồ sơ**, không có backend, đánh dấu đã đọc không bền,
  thiếu nhắc lịch hẹn / thông báo hệ thống / push. Đây là gap thật cần đóng.

## Quyết định đã chốt
1. Phạm vi v1 = **đầy đủ báo cáo**: hồ sơ + nhắc lịch hẹn + thông báo hệ thống + **push Firebase**.
2. Triển khai cả push ngay; push viết **config-driven + degrade an toàn** (thiếu Firebase credentials
   thì app vẫn chạy, chỉ không đẩy push). Credentials do người dùng cấp để kích hoạt — không tự lấy được.
3. Kiến trúc: **Hướng A** — bảng `notifications` materialized + service `emit()`; push gửi trong `emit`.

## Nguyên tắc cốt lõi
Tách: **in-app notification luôn hoạt động (lõi)**; **push là best-effort** bọc ngoài, lỗi/thiếu
config không ảnh hưởng nghiệp vụ. Mọi điểm sinh thông báo bọc try/except — notify hỏng không làm
hỏng nghiệp vụ chính (đổi trạng thái hồ sơ, đặt lịch…).

## Kiến trúc

```
Sự kiện (đổi trạng thái hồ sơ / rút hồ sơ / tạo lịch hẹn / scheduler nhắc lịch / admin broadcast)
        │
        ▼
notification_service.emit(user_id, type, title, content, link, ref_id, priority)
        │  1) Notification.create() → ghi bảng notifications (in-app, luôn chạy)
        │  2) push_service.send()   → FCM best-effort (degrade nếu thiếu Firebase)
        ▼
GET /api/notifications  ←  NotificationScreen.tsx (frontend)
```

## Data model (thêm vào `models/db.py`, pattern CREATE TABLE IF NOT EXISTS)

```sql
CREATE TABLE public.notifications (
  id         VARCHAR(80) PRIMARY KEY DEFAULT gen_random_uuid()::text,
  user_id    VARCHAR(80) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  type       VARCHAR(30) NOT NULL,          -- document | appointment | system | evaluation
  title      VARCHAR(255) NOT NULL,
  content    TEXT NOT NULL DEFAULT '',
  link       VARCHAR(60),                   -- screen key cho FE điều hướng
  ref_id     VARCHAR(80),                   -- id hồ sơ/lịch hẹn liên quan
  priority   VARCHAR(10) NOT NULL DEFAULT 'low',   -- low|medium|high
  read_at    TIMESTAMPTZ,                   -- NULL = chưa đọc
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_notif_user   ON notifications(user_id, created_at DESC);
CREATE INDEX idx_notif_unread ON notifications(user_id, read_at);

CREATE TABLE public.push_tokens (
  token      VARCHAR(255) PRIMARY KEY,
  user_id    VARCHAR(80) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  platform   VARCHAR(20) NOT NULL DEFAULT 'web',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_pushtok_user ON push_tokens(user_id);

ALTER TABLE public.appointments ADD COLUMN IF NOT EXISTS reminder_sent BOOLEAN NOT NULL DEFAULT FALSE;
```

## Model layer — `models/notification.py` (mới, SQL qua db.session)
- `Notification.create(user_id, type, title, content, link=None, ref_id=None, priority='low') -> dict`
- `Notification.list_for(user_id, only_unread=False, limit=50) -> list[dict]`
- `Notification.unread_count(user_id) -> int`
- `Notification.mark_read(notif_id, user_id) -> bool` (chỉ của chính user)
- `Notification.mark_all_read(user_id) -> int`
- `PushToken.register(user_id, token, platform='web')` / `PushToken.list_tokens(user_id) -> list[str]` / `PushToken.remove(token)`

## API — `routes/notification_routes.py` (`notification_bp`, prefix `/api/notifications`, đăng ký server.py)
| Method · Path | Việc | Auth |
|---|---|---|
| `GET /api/notifications?unread=&limit=` | Danh sách user hiện tại (shape: id,type,title,content,time,read,priority,link,ref_id) | user |
| `GET /api/notifications/unread-count` | `{count}` | user |
| `POST /api/notifications/<id>/read` | Đánh dấu 1 đã đọc | user |
| `POST /api/notifications/read-all` | Đánh dấu tất cả đã đọc | user |
| `POST /api/notifications/push-token` | Đăng ký FCM token `{token,platform}` | user |
| `DELETE /api/notifications/push-token` | Gỡ token | user |
| `POST /api/notifications/broadcast` | Gửi thông báo hệ thống tới tất cả user | admin |

Dùng `request.user_id` (401 nếu thiếu) như các route khác; broadcast yêu cầu `request.role == 'admin'`.

## Service — `services/notification_service.py` (mới)
- `emit(user_id, type, title, content, link=None, ref_id=None, priority='low') -> dict`:
  tạo `Notification` rồi `push_service.send(...)` best-effort (nuốt lỗi).
- `emit_system_all(title, content, link=None)`: fan-out — lấy mọi user id → `emit` từng người.
- Helper thuần: `status_notification(status) -> (title, content_prefix, priority)` map khớp UI:
  submitted→("Hồ sơ đã được tiếp nhận", low), in_review→("Hồ sơ đang được xem xét", medium),
  more_info→("Cần bổ sung hồ sơ", high), approved→("Hồ sơ đã được duyệt", medium),
  rejected→("Hồ sơ bị từ chối", high), withdraw→("Đã rút hồ sơ", low).

## Điểm sinh thông báo (hook)
| Sự kiện | Vị trí | Action |
|---|---|---|
| Đổi trạng thái hồ sơ | `applications_routes.update_status` (PUT `/<id>/status`) sau commit | `emit(applicant_id,'document', status_notification(...), link='search', ref_id=app_id)` |
| Rút hồ sơ | `applications_routes` `/withdraw` | `emit(... 'Đã rút hồ sơ' ...)` |
| Tạo lịch hẹn | luồng tạo appointment (gồm voice nếu có user_id) | `emit(user_id,'appointment','Đặt lịch thành công', …, link='appointments', ref_id=appt_id)` |
| Nhắc lịch hẹn | scheduler | `emit(... 'Nhắc lịch hẹn ngày mai' …, priority='medium')` |
| Thông báo hệ thống | `POST /broadcast` (admin) | `emit_system_all(...)` |

Mọi hook bọc try/except.

## Scheduler — `services/notification_scheduler.py` (mới)
- `due_reminders(appointments, today) -> list`: lọc `date == today+1`, status ∈ {pending,confirmed},
  `reminder_sent == False`. **Hàm thuần — test không cần DB.**
- `run_reminder_loop(app)`: daemon thread (pattern `_cleanup_rag_sessions`): trong `app.app_context()`
  → quét appointment đến hạn → `emit` nhắc + set `reminder_sent=True` → `sleep(1800)`. Bọc try/except,
  không bao giờ crash. Khởi động trong `server.py`.

## Push FCM — `services/push_service.py` (mới, config-driven + degrade)
- Lazy init `firebase_admin` từ env `FIREBASE_CREDENTIALS` (service-account JSON). Thiếu creds/SDK → no-op.
- `send(user_id, title, body, data=None)`: lấy tokens → gửi FCM multicast; token `UNREGISTERED` → remove.
  **Không bao giờ raise.**
- `requirements.txt`: thêm `firebase-admin`.

## Frontend
- `frontend/src/services/notificationService.ts` (mới): `list()`, `unreadCount()`, `markRead(id)`,
  `markAllRead()`, `registerPushToken(token)`.
- `NotificationScreen.tsx` (sửa): thay `getMyApplications→appToNotification` bằng
  `notificationService.list()`; map row API → shape hiện tại; `handleMarkAllRead` gọi API; click 1
  thông báo → `markRead` + điều hướng theo `link`. Tab "Lịch sử" giữ nguyên (từ applications).
- Push (config-driven): firebase web SDK init từ `VITE_FIREBASE_*`; service worker
  `public/firebase-messaging-sw.js`; util xin quyền + lấy FCM token + POST `/push-token`. Thiếu
  `VITE_FIREBASE_*` → bỏ qua êm.

## Config/env
- Backend: `FIREBASE_CREDENTIALS=path/serviceAccount.json` (push degrade nếu thiếu).
- Frontend: `VITE_FIREBASE_API_KEY/AUTH_DOMAIN/PROJECT_ID/MESSAGING_SENDER_ID/APP_ID/VAPID_KEY`.
- Người dùng cấp các giá trị này để kích hoạt push; in-app không cần.

## Error handling / degradation
- `emit()` luôn ghi notification in-app; push best-effort (swallow). In-app chạy bất kể Firebase.
- Scheduler & hook bọc try/except, không crash app.
- API: thiếu auth → 401; mark-read chỉ tác động notif của chính user.

## Testing (chạy không cần DB/Firebase)
- `status_notification()` mapping — pure.
- `due_reminders()` — pure (lọc đúng cái đến hạn, bỏ `reminder_sent`).
- `notification_service.emit()` — mock `Notification.create` + `push_service.send`: tạo notif + gọi
  push; **push lỗi không làm emit vỡ**.
- `push_service.send()` — thiếu Firebase → no-op, không raise.
- `Notification` model: test thật nếu DB local sẵn, else skip có điều kiện.

## Files
| File | Action |
|---|---|
| `models/db.py` | + DDL notifications/push_tokens + cột reminder_sent |
| `models/notification.py` | mới — Notification + PushToken |
| `services/notification_service.py` | mới — emit / emit_system_all / status_notification |
| `services/push_service.py` | mới — FCM lazy/degrade |
| `services/notification_scheduler.py` | mới — due_reminders + run_reminder_loop |
| `routes/notification_routes.py` | mới — API |
| `server.py` | đăng ký blueprint + start scheduler thread |
| `routes/applications_routes.py` | hook emit (status + withdraw) |
| `routes/appointments_routes.py` | hook emit (tạo lịch) |
| `requirements.txt` | + firebase-admin |
| `frontend/src/services/notificationService.ts` | mới |
| `frontend/src/screens/user/NotificationScreen.tsx` | nối API thật |
| `frontend/public/firebase-messaging-sw.js` + push init util | mới |
| tests | mới (mapping, due_reminders, emit, push degrade) |

## Không làm (YAGNI)
- Không event-sourcing; không realtime websocket cho notif (poll khi mở màn đủ cho v1).
- Không badge chuông toàn cục (để sau).
- Không sửa luồng nghiệp vụ ngoài việc chèn hook emit.
