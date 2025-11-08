const express = require('express');
const jwt = require('jsonwebtoken');
const { body, validationResult } = require('express-validator');
const User = require('../models/User');
const { authenticateToken } = require('../middleware/auth');
const { verifyVNeID } = require('../services/vneid');

const router = express.Router();

// Initialize default users on first load
User.initializeDefaultUsers().catch(console.error);

// Generate JWT token
function generateToken(user) {
  const secret = process.env.JWT_SECRET || 'default-secret-key-change-in-production';
  if (!secret || secret === 'default-secret-key-change-in-production') {
    console.warn('⚠️  WARNING: Using default JWT_SECRET. Please set JWT_SECRET in .env file for production!');
  }
  return jwt.sign(
    { 
      userId: user.id,
      role: user.role,
      cccdNumber: user.cccdNumber
    },
    secret,
    { expiresIn: process.env.JWT_EXPIRES_IN || '7d' }
  );
}

// @route   POST /api/auth/register
// @desc    Register new user
// @access  Public
router.post('/register', [
  body('cccdNumber')
    .trim()
    .isLength({ min: 12, max: 12 })
    .withMessage('Số CCCD phải có 12 chữ số')
    .isNumeric()
    .withMessage('Số CCCD chỉ được chứa số'),
  body('fullName')
    .trim()
    .notEmpty()
    .withMessage('Họ và tên là bắt buộc')
    .isLength({ min: 2 })
    .withMessage('Họ và tên phải có ít nhất 2 ký tự'),
  body('dateOfBirth')
    .notEmpty()
    .withMessage('Ngày sinh là bắt buộc'),
  body('phone')
    .trim()
    .matches(/^[0-9]{10,11}$/)
    .withMessage('Số điện thoại không hợp lệ'),
  body('email')
    .trim()
    .isEmail()
    .withMessage('Email không hợp lệ')
    .normalizeEmail(),
  body('password')
    .isLength({ min: 8 })
    .withMessage('Mật khẩu phải có ít nhất 8 ký tự')
    .matches(/[A-Z]/)
    .withMessage('Mật khẩu phải có ít nhất 1 chữ hoa')
    .matches(/[0-9]/)
    .withMessage('Mật khẩu phải có ít nhất 1 chữ số')
    .matches(/[!@#$%^&*(),.?":{}|<>]/)
    .withMessage('Mật khẩu phải có ít nhất 1 ký tự đặc biệt'),
  body('confirmPassword')
    .custom((value, { req }) => {
      if (value !== req.body.password) {
        throw new Error('Mật khẩu xác nhận không khớp');
      }
      return true;
    }),
  body('otp')
    .optional()
    .isLength({ min: 6, max: 6 })
    .withMessage('Mã OTP phải có 6 chữ số')
], async (req, res) => {
  try {
    // Check validation errors
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        success: false,
        message: 'Dữ liệu không hợp lệ',
        errors: errors.array()
      });
    }

    const { cccdNumber, fullName, dateOfBirth, phone, email, password, otp, useVNeID } = req.body;

    // If using VNeID, verify it first
    let vneidData = null;
    if (useVNeID) {
      try {
        vneidData = await verifyVNeID(cccdNumber);
        if (!vneidData) {
          return res.status(400).json({
            success: false,
            message: 'Xác thực VNeID thất bại'
          });
        }
      } catch (error) {
        return res.status(400).json({
          success: false,
          message: 'Lỗi xác thực VNeID: ' + error.message
        });
      }
    } else {
      // For demo, we'll skip OTP verification but in production this should be verified
      if (!otp || otp !== '123456') {
        // In production, verify OTP from SMS service
        // For demo, accept 123456 as valid OTP
        if (otp !== '123456') {
          return res.status(400).json({
            success: false,
            message: 'Mã OTP không đúng. Sử dụng 123456 cho demo.'
          });
        }
      }
    }

    // Create user
    const userData = {
      cccdNumber,
      fullName,
      dateOfBirth,
      phone,
      email,
      password,
      role: 'citizen',
      isVNeIDVerified: !!vneidData,
      vneidId: vneidData?.id || null
    };

    const user = await User.create(userData);
    const token = generateToken(user);

    res.status(201).json({
      success: true,
      message: 'Đăng ký thành công',
      data: {
        user: user.toJSON(),
        token
      }
    });
  } catch (error) {
    console.error('Register error:', error);
    res.status(400).json({
      success: false,
      message: error.message || 'Đăng ký thất bại'
    });
  }
});

// @route   POST /api/auth/login
// @desc    Login user
// @access  Public
router.post('/login', [
  body('cccdNumber')
    .trim()
    .notEmpty()
    .withMessage('Số CCCD là bắt buộc'),
  body('password')
    .notEmpty()
    .withMessage('Mật khẩu là bắt buộc')
], async (req, res) => {
  try {
    // Check validation errors
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        success: false,
        message: 'Dữ liệu không hợp lệ',
        errors: errors.array()
      });
    }

    const { cccdNumber, password } = req.body;

    // Find user
    const user = await User.findByCCCD(cccdNumber);
    if (!user) {
      return res.status(401).json({
        success: false,
        message: 'Số CCCD hoặc mật khẩu không đúng'
      });
    }

    // Verify password
    const isPasswordValid = await user.verifyPassword(password);
    if (!isPasswordValid) {
      return res.status(401).json({
        success: false,
        message: 'Số CCCD hoặc mật khẩu không đúng'
      });
    }

    // Generate token
    const token = generateToken(user);

    res.json({
      success: true,
      message: 'Đăng nhập thành công',
      data: {
        user: user.toJSON(),
        token
      }
    });
  } catch (error) {
    console.error('Login error:', error);
    res.status(500).json({
      success: false,
      message: 'Lỗi đăng nhập'
    });
  }
});

// @route   POST /api/auth/logout
// @desc    Logout user (client-side token removal, server can blacklist token)
// @access  Private
router.post('/logout', authenticateToken, async (req, res) => {
  try {
    // In a production system, you might want to blacklist the token
    // For now, we'll just return success (client removes token)
    res.json({
      success: true,
      message: 'Đăng xuất thành công'
    });
  } catch (error) {
    console.error('Logout error:', error);
    res.status(500).json({
      success: false,
      message: 'Lỗi đăng xuất'
    });
  }
});

// @route   GET /api/auth/profile
// @desc    Get current user profile
// @access  Private
router.get('/profile', authenticateToken, async (req, res) => {
  try {
    const user = await User.findById(req.userId);
    if (!user) {
      return res.status(404).json({
        success: false,
        message: 'Người dùng không tồn tại'
      });
    }

    res.json({
      success: true,
      data: {
        user: user.toJSON()
      }
    });
  } catch (error) {
    console.error('Get profile error:', error);
    res.status(500).json({
      success: false,
      message: 'Lỗi lấy thông tin người dùng'
    });
  }
});

// @route   PUT /api/auth/profile
// @desc    Update user profile
// @access  Private
router.put('/profile', [
  authenticateToken,
  body('fullName')
    .optional()
    .trim()
    .isLength({ min: 2 })
    .withMessage('Họ và tên phải có ít nhất 2 ký tự'),
  body('phone')
    .optional()
    .trim()
    .matches(/^[0-9]{10,11}$/)
    .withMessage('Số điện thoại không hợp lệ'),
  body('email')
    .optional()
    .trim()
    .isEmail()
    .withMessage('Email không hợp lệ')
    .normalizeEmail()
], async (req, res) => {
  try {
    // Check validation errors
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        success: false,
        message: 'Dữ liệu không hợp lệ',
        errors: errors.array()
      });
    }

    const user = await User.findById(req.userId);
    if (!user) {
      return res.status(404).json({
        success: false,
        message: 'Người dùng không tồn tại'
      });
    }

    const updates = {};
    if (req.body.fullName) updates.fullName = req.body.fullName;
    if (req.body.phone) updates.phone = req.body.phone;
    if (req.body.email) updates.email = req.body.email;
    if (req.body.dateOfBirth) updates.dateOfBirth = req.body.dateOfBirth;

    const updatedUser = await user.update(updates);

    res.json({
      success: true,
      message: 'Cập nhật thông tin thành công',
      data: {
        user: updatedUser.toJSON()
      }
    });
  } catch (error) {
    console.error('Update profile error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Lỗi cập nhật thông tin'
    });
  }
});

module.exports = router;

