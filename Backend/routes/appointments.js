const express = require('express');
const cors = require('cors');
const { body, validationResult } = require('express-validator');
const { authenticateToken, authorizeRole } = require('../middleware/auth');
const Appointment = require('../models/Appointment');
const Notification = require('../models/Notification');
const Procedure = require('../models/Procedure');

const router = express.Router();

// Router-level CORS to ensure consistent headers for all endpoints
router.use(cors({
  origin: (origin, callback) => {
    const allowed = ['http://localhost:5173', 'http://localhost:3000', 'http://localhost:3001'];
    if (!origin || allowed.includes(origin)) return callback(null, true);
    if (/^http:\/\/localhost:\d{2,5}$/.test(origin)) return callback(null, true);
    return callback(null, true);
  },
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization'],
  credentials: true,
  optionsSuccessStatus: 204,
}));

// Ensure all responses include CORS headers
router.use((req, res, next) => {
  const origin = req.headers.origin || 'http://localhost:3001';
  res.header('Access-Control-Allow-Origin', origin);
  res.header('Access-Control-Allow-Credentials', 'true');
  res.header('Vary', 'Origin');
  next();
});

// Explicit CORS preflight handler for this router (OPTIONS /api/appointments)
router.options('/', (req, res) => {
  res.header('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS');
  res.header('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  return res.sendStatus(204);
});

// Allow preflight for any sub-path (e.g. /api/appointments/by-date)
router.options('*', (req, res) => {
  res.header('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS');
  res.header('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  return res.sendStatus(204);
});

// Specific preflight for upcoming endpoint
router.options('/upcoming', (req, res) => {
  res.header('Access-Control-Allow-Methods', 'GET,OPTIONS');
  res.header('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  return res.sendStatus(204);
});

// @route   POST /api/appointments
// @desc    Create a new appointment (Citizen) - DEMO MODE (No Auth Required)
// @access  Public
router.post('/', [
  body('fullName').trim().isLength({ min: 2 }).withMessage('Họ tên phải >= 2 ký tự'),
  body('phone').matches(/^(0[0-9]{9,10})$/).withMessage('Số điện thoại không hợp lệ'),
  body('agencyId').notEmpty().withMessage('Cơ quan là bắt buộc'),
  body('serviceCode').notEmpty().withMessage('Dịch vụ là bắt buộc'),
  body('info').optional().isLength({ max: 500 }).withMessage('Thông tin cuộc hẹn quá dài'),
  body('date').isISO8601().withMessage('Ngày không hợp lệ'),
  body('time').matches(/^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$/).withMessage('Thời gian không hợp lệ (HH:mm)'),
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ 
        success: false, 
        message: 'Dữ liệu không hợp lệ',
        errors: errors.array()
      });
    }

    const { agencyId, serviceCode, date, time, fullName, phone, info } = req.body;
    
    const appointmentDate = new Date(`${date}T${time}`);
    if (appointmentDate < new Date()) {
      return res.status(400).json({
        success: false,
        message: 'Không thể đặt lịch trong quá khứ'
      });
    }

    const demoUserId = req.userId || 'demo-user-' + Date.now();

    const appointment = await Appointment.create({
      userId: demoUserId,
      agencyId,
      serviceCode,
      date,
      time,
      fullName,
      phone,
      info,
      status: 'pending'
    });

    // TẠO THÔNG BÁO CHO USER SAU KHI ĐẶT LỊCH THÀNH CÔNG
    try {
      await Notification.create({
        toUserId: demoUserId,
        fromAgencyId: agencyId,
        title: 'Đặt lịch hẹn thành công',
        message: `Bạn đã đặt lịch hẹn dịch vụ "${serviceCode}" vào lúc ${time} ngày ${date}. Mã lịch hẹn: ${appointment.id}`,
        type: 'appointment_created',
        relatedId: appointment.id,
      });
      console.log('✅ Created notification for user:', demoUserId);
    } catch (notifError) {
      console.error('⚠️  Failed to create notification:', notifError);
      // Không throw error để không ảnh hưởng đến việc tạo appointment
    }

    res.status(201).json({ 
      success: true, 
      message: 'Đặt lịch hẹn thành công',
      data: appointment 
    });
  } catch (error) {
    console.error('Create appointment error:', error);
    if (error.message && error.message.includes('đầy')) {
      return res.status(409).json({ 
        success: false, 
        message: error.message
      });
    }
    res.status(500).json({ 
      success: false, 
      message: 'Lỗi khi tạo lịch hẹn: ' + error.message
    });
  }
});

// @route   GET /api/appointments
// @desc    Get appointments for an agency (Agency Staff)
// @access  Private (Official, Admin)
router.get('/', [
  authenticateToken,
  authorizeRole(['admin']),
], async (req, res) => {
  try {
    // In a real app, we'd get the agencyId from the logged-in official's profile
    const agencyId = req.query.agencyId || req.user.agencyId; 
    if (!agencyId) {
        return res.status(400).json({ 
          success: false, 
          message: 'Thiếu thông tin cơ quan' 
        });
    }
    
    const appointments = await Appointment.findByAgency(agencyId);
    res.json({ 
      success: true, 
      message: 'Lấy danh sách lịch hẹn thành công',
      data: appointments 
    });
  } catch (error) {
    console.error('Get appointments error:', error);
    res.status(500).json({ 
      success: false, 
      message: 'Lỗi khi lấy danh sách lịch hẹn' 
    });
  }
});

// @route   GET /api/appointments/by-date
// @desc    Get appointments by agency and date
// @access  Public (for checking availability)
router.get('/by-date', async (req, res) => {
  try {
    const { agencyId, date } = req.query;
    
    if (!agencyId || !date) {
      return res.status(400).json({ 
        success: false, 
        message: 'Thiếu thông tin cơ quan hoặc ngày' 
      });
    }
    
    const appointments = await Appointment.findByAgencyAndDate(agencyId, date);
    res.json({ 
      success: true, 
      message: 'Lấy danh sách lịch hẹn thành công',
      data: { appointments } 
    });
  } catch (error) {
    console.error('Get appointments by date error:', error);
    res.status(500).json({ 
      success: false, 
      message: 'Lỗi khi lấy danh sách lịch hẹn: ' + error.message
    });
  }
});

// @route   PUT /api/appointments/:id/status
// @desc    Update appointment status (Agency Staff) - DEMO MODE
// @access  Public (for demo)
router.put('/:id/status', [
  body('status').isIn(['pending', 'completed', 'cancelled']).withMessage('Trạng thái không hợp lệ'),
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ 
        success: false, 
        message: 'Trạng thái không hợp lệ',
        errors: errors.array()
      });
    }

    const appointment = await Appointment.findById(req.params.id);
    if (!appointment) {
      return res.status(404).json({ 
        success: false, 
        message: 'Không tìm thấy lịch hẹn' 
      });
    }

    const { status } = req.body;
    const updatedAppointment = await appointment.update({ status });

    // TẠO THÔNG BÁO VÀ PROCEDURE
    let notificationTitle = '';
    let notificationMessage = '';

    switch (status) {
      case 'completed':
        notificationTitle = 'Lịch hẹn hoàn thành';
        notificationMessage = `Lịch hẹn dịch vụ "${appointment.serviceCode}" đã hoàn thành. Hồ sơ của bạn đã được tiếp nhận.`;
        
        // TẠO PROCEDURE TỰ ĐỘNG
        try {
          const procedure = await Procedure.create({
            userId: appointment.userId,
            appointmentId: appointment.id,
            agencyId: appointment.agencyId,
            serviceCode: appointment.serviceCode,
            title: appointment.serviceCode,
            status: 'received',
            submitDate: new Date().toISOString().split('T')[0],
            office: appointment.agencyId, // Sẽ được map sang tên cơ quan ở frontend
          });
          console.log('✅ Created procedure:', procedure.id);
        } catch (procError) {
          console.error('⚠️  Failed to create procedure:', procError);
        }
        break;
      case 'cancelled':
        notificationTitle = 'Lịch hẹn đã hủy';
        notificationMessage = `Lịch hẹn dịch vụ "${appointment.serviceCode}" vào ${appointment.time} ngày ${appointment.date} đã bị hủy.`;
        break;
      default:
        notificationTitle = 'Cập nhật lịch hẹn';
        notificationMessage = `Trạng thái lịch hẹn "${appointment.serviceCode}" đã được cập nhật.`;
    }

    try {
      await Notification.create({
        toUserId: appointment.userId,
        fromAgencyId: appointment.agencyId,
        title: notificationTitle,
        message: notificationMessage,
        type: 'appointment_update',
        relatedId: appointment.id,
      });
      console.log('✅ Sent notification to user:', appointment.userId);
    } catch (notifError) {
      console.error('⚠️  Failed to create notification:', notifError);
    }

    res.json({ 
      success: true, 
      message: 'Cập nhật trạng thái thành công',
      data: updatedAppointment 
    });
  } catch (error) {
    console.error('Update appointment status error:', error);
    res.status(500).json({ 
      success: false, 
      message: 'Lỗi khi cập nhật trạng thái: ' + error.message
    });
  }
});

// @route   PUT /api/appointments/:id
// @desc    Update appointment date/time
// @access  Public (for demo)
router.put('/:id', [
  body('date').isISO8601().withMessage('Ngày không hợp lệ'),
  body('time').matches(/^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$/).withMessage('Thời gian không hợp lệ'),
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ 
        success: false, 
        message: 'Dữ liệu không hợp lệ',
        errors: errors.array()
      });
    }

    const appointment = await Appointment.findById(req.params.id);
    if (!appointment) {
      return res.status(404).json({ 
        success: false, 
        message: 'Không tìm thấy lịch hẹn' 
      });
    }

    const { date, time } = req.body;
    
    // Validate date is not in the past
    const appointmentDate = new Date(`${date}T${time}`);
    if (appointmentDate < new Date()) {
      return res.status(400).json({
        success: false,
        message: 'Không thể đặt lịch trong quá khứ'
      });
    }

    const updatedAppointment = await appointment.update({ date, time });

    // Gửi thông báo
    try {
      await Notification.create({
        toUserId: appointment.userId,
        fromAgencyId: appointment.agencyId,
        title: 'Lịch hẹn đã được thay đổi',
        message: `Lịch hẹn dịch vụ "${appointment.serviceCode}" đã được thay đổi sang ${time} ngày ${date}.`,
        type: 'appointment_update',
        relatedId: appointment.id,
      });
    } catch (notifError) {
      console.error('⚠️  Failed to create notification:', notifError);
    }

    res.json({ 
      success: true, 
      message: 'Cập nhật lịch hẹn thành công',
      data: updatedAppointment 
    });
  } catch (error) {
    console.error('Update appointment error:', error);
    res.status(500).json({ 
      success: false, 
      message: 'Lỗi khi cập nhật lịch hẹn: ' + error.message
    });
  }
});

// @route   GET /api/appointments/all
// @desc    Get all appointments (DEMO MODE - No Auth)
// @access  Public
router.get('/all', async (req, res) => {
  try {
    const appointments = await Appointment.findAll();
    res.json({ 
      success: true, 
      message: 'Lấy danh sách lịch hẹn thành công',
      data: { appointments } 
    });
  } catch (error) {
    console.error('Get all appointments error:', error);
    res.status(500).json({ 
      success: false, 
      message: 'Lỗi khi lấy danh sách lịch hẹn: ' + error.message
    });
  }
});

// @route   GET /api/appointments/user/:userId
// @desc    Get appointments by userId
// @access  Public (for demo)
router.get('/user/:userId', async (req, res) => {
  try {
    const fs = require('fs').promises;
    const path = require('path');
    const DATA_FILE = path.join(__dirname, '../data/appointments.json');
    
    const data = await fs.readFile(DATA_FILE, 'utf8');
    const allAppointments = JSON.parse(data);
    
    const userAppointments = allAppointments.filter(apt => 
      apt.userId === req.params.userId
    );
    
    res.json({ 
      success: true, 
      message: 'Lấy danh sách lịch hẹn thành công',
      data: { appointments: userAppointments }
    });
  } catch (error) {
    console.error('Get user appointments error:', error);
    res.status(500).json({ 
      success: false, 
      message: 'Lỗi khi lấy danh sách lịch hẹn',
      data: { appointments: [] }
    });
  }
});

// NEW: Upcoming sorted future appointments
router.get('/upcoming', async (req, res) => {
  try {
    const all = await Appointment.findAll();
    const now = new Date();
    const upcoming = all
      .filter(a => {
        if (!a.date || !a.time) return false;
        const dt = new Date(`${a.date}T${a.time}`);
        return !isNaN(dt.getTime()) && dt >= now;
      })
      .sort((a, b) => new Date(`${a.date}T${a.time}`) - new Date(`${b.date}T${b.time}`));
    res.json({
      success: true,
      message: 'Danh sách lịch hẹn sắp tới',
      data: { appointments: upcoming }
    });
  } catch (e) {
    res.status(500).json({ success: false, message: 'Lỗi khi lấy lịch hẹn sắp tới' });
  }
});

module.exports = router;
