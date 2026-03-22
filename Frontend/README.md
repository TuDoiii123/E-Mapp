# E-Mapp Frontend

Giao diện React cho ứng dụng **Dịch vụ công số tỉnh Thanh Hóa** — tìm kiếm dịch vụ công, đặt lịch hẹn, chatbot AI hỏi đáp thủ tục hành chính và trợ lý voice.

---

## Kiến trúc tổng quan

```
Frontend/
├── src/
│   ├── App.tsx                     # Router dạng state + AuthProvider
│   ├── main.tsx                    # Entry point React
│   ├── contexts/
│   │   └── AuthContext.tsx         # Quản lý trạng thái xác thực (JWT)
│   ├── services/                   # API client layer
│   │   ├── api.ts                  # apiRequest() dùng chung + auth/chatbot/voice API
│   │   ├── appointmentsApi.ts      # Đặt lịch hẹn
│   │   └── servicesApi.ts          # Dịch vụ công / bản đồ
│   └── components/
│       ├── *Screen.tsx             # Các màn hình ứng dụng (16 màn hình)
│       ├── BottomNavigation.tsx    # Thanh điều hướng dưới
│       └── ui/                     # Thư viện Shadcn/ui (60+ component)
├── vite.config.ts                  # Vite + React SWC
└── .env                            # Biến môi trường (không commit)
```

---

## Yêu cầu

- Node.js 18+
- Backend đang chạy tại `http://localhost:8888` (xem `../Backend/README.md`)

---

## Cài đặt & chạy

```bash
cd Frontend
npm install
npm run dev
```

Ứng dụng chạy tại: `http://localhost:3000`

---

## Cấu hình `.env`

Tạo file `.env` tại thư mục `Frontend/`:

```env
# URL backend (mặc định: http://localhost:8888/api)
VITE_API_URL=http://localhost:8888/api

# Google Maps API key (tùy chọn — cần để dùng màn hình bản đồ)
VITE_GOOGLE_MAPS_API_KEY=your_google_maps_api_key
```

> Nếu `VITE_GOOGLE_MAPS_API_KEY` không được đặt, màn hình bản đồ hiển thị thông báo lỗi nhưng các chức năng khác vẫn hoạt động bình thường.

---

## Các màn hình

| Màn hình | Route key | Mô tả |
|----------|-----------|-------|
| Đăng nhập | `login` | Xác thực bằng CCCD + mật khẩu |
| Đăng ký | `register` | Tạo tài khoản mới (OTP demo: `123456`) |
| Trang chủ | `home` | Phím tắt dịch vụ, trạng thái hồ sơ |
| Đặt lịch hẹn | `appointment` | Lịch FullCalendar + tạo lịch hẹn |
| Bản đồ dịch vụ | `map` | Google Maps + danh sách DVC gần đây |
| Tra cứu hồ sơ | `search` | Tìm kiếm và theo dõi hồ sơ |
| Nộp hồ sơ | `submit` | Nộp hồ sơ trực tuyến |
| Danh mục giấy tờ | `document-catalog` | Tra cứu loại giấy tờ |
| Chi tiết dịch vụ | `document-detail` | Thông tin chi tiết DVC |
| Chatbot AI | `chatbot` | Hỏi đáp RAG + Voice AI đặt lịch |
| Thông báo | `notifications` | Danh sách thông báo |
| Đánh giá | `evaluation` | Đánh giá cơ quan hành chính |
| Phân tích | `analytics` | Biểu đồ thống kê |
| Cài đặt | `settings` | Cài đặt tài khoản |
| Thông tin tài khoản | `account-detail` | Chi tiết hồ sơ cá nhân |

---

## Xác thực

- Token JWT lưu trong `localStorage` (`auth_token`)
- Khi khởi động, app tự động gọi `/api/auth/profile` để lấy thông tin người dùng
- Nếu token hết hạn, tự động chuyển về màn hình đăng nhập

---

## Chatbot & Voice AI

Màn hình `ChatbotScreen` hỗ trợ hai chế độ:

1. **Chat văn bản** — gửi câu hỏi đến `/api/rag/chat`, nhận câu trả lời từ RAG agent
2. **Voice AI** — ghi âm giọng nói, STT → gửi đến `/api/voice/dialog` để đặt lịch qua hội thoại

Lịch sử hội thoại được lưu local trong `localStorage` (`chat_conversations_v1`) và đồng bộ với SQL Server nếu được cấu hình ở Backend.

---

## Build production

```bash
npm run build
```

Kết quả xuất tại thư mục `build/`.

---

## Lưu ý

- Ứng dụng dùng routing dạng **state-based** (không dùng URL) — phù hợp cho mobile web app dạng SPA.
- Toàn bộ API call đi qua `src/services/api.ts` với cơ chế fallback URL tự động.
- Thư viện UI: [Shadcn/ui](https://ui.shadcn.com/) + Radix UI + Tailwind CSS.
