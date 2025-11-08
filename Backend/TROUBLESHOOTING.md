# Khắc phục lỗi "Failed to fetch"

## Các bước kiểm tra:

### 1. Cài đặt Dependencies
Đảm bảo đã cài đặt tất cả dependencies:
```bash
cd Backend
npm install
```

### 2. Tạo file .env (nếu chưa có)
Tạo file `.env` trong thư mục Backend với nội dung:
```
PORT=8888
JWT_SECRET=your-super-secret-jwt-key-change-in-production
JWT_EXPIRES_IN=7d
NODE_ENV=development
```

### 3. Khởi động Backend Server
```bash
cd Backend
npm run dev
```

Server sẽ chạy trên: `http://localhost:8888` hoặc `http://192.168.1.231:8888`

### 4. Kiểm tra Backend đang chạy
Mở trình duyệt và truy cập:
- `http://localhost:8888/api/health`

Nếu thấy response JSON với `status: "ok"` thì backend đã chạy thành công.

### 5. Khởi động Frontend
Mở terminal mới và chạy:
```bash
cd Frontend
npm run dev
```

### 6. Kiểm tra CORS
Nếu vẫn gặp lỗi, kiểm tra:
- Backend đã bật CORS (đã cấu hình trong server.js)
- Frontend đang gọi đúng URL API
- Không có firewall chặn port 8888

### 7. Kiểm tra Network
- Đảm bảo cả Backend và Frontend đang chạy
- Kiểm tra console của trình duyệt để xem lỗi chi tiết
- Kiểm tra Network tab trong DevTools để xem request có được gửi không

## Lỗi thường gặp:

### "Cannot find module 'express-validator'"
**Giải pháp:** Chạy `npm install` trong thư mục Backend

### "EADDRINUSE: address already in use"
**Giải pháp:** Port 8888 đang được sử dụng. Đổi port trong file .env hoặc tắt ứng dụng đang dùng port đó.

### "Failed to fetch" trong Frontend
**Giải pháp:**
1. Kiểm tra Backend đã chạy chưa
2. Kiểm tra URL API trong `Frontend/src/services/api.ts`
3. Thử truy cập `http://localhost:8888/api/health` trực tiếp trong trình duyệt

