const jwt = require('jsonwebtoken');
const User = require('../models/User');

// Middleware kiểm tra token
const authenticateToken = async (req, res, next) => {
  try {
    const authHeader = req.headers['authorization'];
    const token = authHeader && authHeader.split(' ')[1]; // Lấy token sau "Bearer"

    if (!token) {
      return res.status(401).json({
        success: false,
        message: 'Không có token xác thực. Vui lòng đăng nhập lại.'
      });
    }

    const secret = process.env.JWT_SECRET || 'default-secret-key-change-in-production';

    jwt.verify(token, secret, async (err, decoded) => {
      if (err) {
        console.error('JWT lỗi:', err);
        return res.status(401).json({
          success: false,
          message: err.name === 'TokenExpiredError' 
            ? 'Token đã hết hạn. Vui lòng đăng nhập lại.' 
            : 'Token không hợp lệ. Vui lòng đăng nhập lại.'
        });
      }

      // Get user from database
      const user = await User.findById(decoded.userId);
      if (!user) {
        return res.status(401).json({
          success: false,
          message: 'Người dùng không tồn tại'
        });
      }

      req.user = user.toJSON();
      req.userId = decoded.userId;
      req.role = decoded.role; // Gắn role để kiểm tra quyền
      next();
    });
  } catch (error) {
    console.error('Lỗi xác thực token:', error);
    res.status(500).json({
      success: false,
      message: 'Lỗi xác thực. Vui lòng thử lại.'
    });
  }
};

// Role-based access control middleware
const requireRole = (...allowedRoles) => {
  return (req, res, next) => {
    if (!req.user) {
      return res.status(401).json({
        success: false,
        message: 'Chưa xác thực'
      });
    }

    if (!allowedRoles.includes(req.user.role)) {
      return res.status(403).json({
        success: false,
        message: 'Bạn không có quyền truy cập tài nguyên này'
      });
    }

    next();
  };
};

// Check if user is admin
const requireAdmin = requireRole('admin');

// Check if user is citizen
const requireCitizen = requireRole('citizen');

// HÀM MỚI: Middleware để phân quyền dựa trên vai trò
const authorizeRole = (allowedRoles) => {
  return (req, res, next) => {
    if (!req.role || !allowedRoles.includes(req.role)) {
      return res.status(403).json({
        success: false,
        message: 'Không có quyền truy cập tài nguyên này'
      });
    }
    next();
  };
};

module.exports = {
  authenticateToken,
  requireRole,
  requireAdmin,
  requireCitizen,
  authorizeRole // Export hàm mới
};

