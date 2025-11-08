# Public Services Backend API

Backend API cho ứng dụng Dịch vụ công số với hệ thống xác thực JWT và phân quyền.

## Cài đặt

1. Cài đặt dependencies:
```bash
npm install
```

2. Tạo file `.env` (đã có sẵn template):
```env
PORT=8888
JWT_SECRET=your-super-secret-jwt-key-change-in-production
JWT_EXPIRES_IN=7d
NODE_ENV=development
```

3. Chạy server:
```bash
npm run dev
```

Hoặc sử dụng file `start-server.bat` trên Windows.

## API Endpoints

### Authentication

- `POST /api/auth/register` - Đăng ký tài khoản mới
- `POST /api/auth/login` - Đăng nhập
- `POST /api/auth/logout` - Đăng xuất
- `GET /api/auth/profile` - Lấy thông tin người dùng (yêu cầu authentication)
- `PUT /api/auth/profile` - Cập nhật thông tin người dùng (yêu cầu authentication)

### Health Check

- `GET /api/health` - Kiểm tra trạng thái server

## Cấu trúc dự án

```
Backend/
├── server.js              # Entry point
├── routes/
│   └── auth.js           # Auth routes
├── middleware/
│   └── auth.js            # JWT authentication & role-based middleware
├── models/
│   └── User.js            # User model với file-based storage
├── services/
│   └── vneid.js           # VNeID mock service
└── data/
    └── users.json         # User database (tự động tạo)
```

## Tính năng

### Authentication
- JWT-based authentication
- Password hashing với bcrypt
- Token expiration (mặc định 7 ngày)

### User Roles
- `citizen`: Người dân
- `admin`: Cán bộ hành chính

### Middleware
- `authenticateToken`: Xác thực JWT token
- `requireRole(...roles)`: Kiểm tra quyền truy cập theo role
- `requireAdmin`: Yêu cầu quyền admin
- `requireCitizen`: Yêu cầu quyền citizen

### VNeID Integration
- Mock VNeID service cho demo
- Có thể tích hợp với VNeID API thật trong production

## Tài khoản mặc định

Khi server khởi động lần đầu, sẽ tự động tạo tài khoản admin:
- Email: `admin@publicservices.gov.vn`
- CCCD: `000000000000`
- Password: `admin123`

## Ví dụ sử dụng

### Đăng ký
```bash
POST /api/auth/register
Content-Type: application/json

{
  "cccdNumber": "123456789012",
  "fullName": "Nguyễn Văn A",
  "dateOfBirth": "1990-01-01",
  "phone": "0123456789",
  "email": "user@example.com",
  "password": "Password123!",
  "confirmPassword": "Password123!",
  "otp": "123456"
}
```

### Đăng nhập
```bash
POST /api/auth/login
Content-Type: application/json

{
  "cccdNumber": "123456789012",
  "password": "Password123!"
}
```

### Lấy profile (yêu cầu token)
```bash
GET /api/auth/profile
Authorization: Bearer <token>
```

## Bảo mật

- Passwords được hash với bcrypt (10 rounds)
- JWT tokens với expiration
- Input validation với express-validator
- CORS enabled (cấu hình trong production)

## Lưu ý

- Database sử dụng file JSON cho demo. Trong production nên dùng database thật (MongoDB, PostgreSQL, etc.)
- VNeID service hiện tại là mock. Cần tích hợp với API thật trong production
- OTP verification hiện chấp nhận mã `123456` cho demo. Cần tích hợp SMS service thật trong production

