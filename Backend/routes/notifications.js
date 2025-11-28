const express = require('express');
const { authenticateToken, authorizeRole } = require('../middleware/auth');
const Notification = require('../models/Notification');
const { body, validationResult } = require('express-validator');

const router = express.Router();

// @route   GET /api/notifications
// @desc    Get notifications for the logged-in user (Citizen)
// @access  Private (Citizen)
router.get('/', authenticateToken, async (req, res) => {
  try {
    const notifications = await Notification.findByUserId(req.userId);
    res.json({ 
      success: true, 
      message: 'Lấy thông báo thành công',
      data: notifications 
    });
  } catch (error) {
    console.error('Get notifications error:', error);
    res.status(500).json({ 
      success: false, 
      message: 'Lỗi khi lấy thông báo' 
    });
  }
});

// @route   POST /api/notifications
// @desc    Create a notification (Agency Staff to Citizen)
// @access  Private (Official, Admin)
router.post('/', [
    authenticateToken,
    authorizeRole(['admin']),
    body('toUserId').notEmpty().withMessage('Người nhận là bắt buộc'),
    body('title').notEmpty().withMessage('Tiêu đề là bắt buộc'),
    body('message').notEmpty().withMessage('Nội dung là bắt buộc'),
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

        const { toUserId, title, message, type = 'system', relatedId } = req.body;
        
        const notification = await Notification.create({
            toUserId,
            fromAgencyId: req.user.agencyId || 'SYSTEM', // Fallback if no agency
            title,
            message,
            type,
            relatedId
        });
        res.status(201).json({ 
          success: true, 
          message: 'Gửi thông báo thành công',
          data: notification 
        });
    } catch (error) {
        console.error('Create notification error:', error);
        res.status(500).json({ 
          success: false, 
          message: 'Lỗi khi tạo thông báo' 
        });
    }
});

// @route   PUT /api/notifications/:id/read
// @desc    Mark a notification as read
// @access  Private (Citizen)
router.put('/:id/read', authenticateToken, async (req, res) => {
    try {
        const notification = await Notification.markAsRead(req.params.id, req.userId);
        if (!notification) {
            return res.status(404).json({ 
              success: false, 
              message: 'Không tìm thấy thông báo' 
            });
        }
        res.json({ 
          success: true, 
          message: 'Đánh dấu đã đọc thành công',
          data: notification 
        });
    } catch (error) {
        console.error('Mark notification as read error:', error);
        res.status(500).json({ 
          success: false, 
          message: 'Lỗi khi đánh dấu đã đọc' 
        });
    }
});

// THÊM ROUTE ĐỂ GET NOTIFICATIONS CHO DEMO USER (KHÔNG CẦN AUTH)
router.get('/demo-user', async (req, res) => {
  try {
    // Lấy tất cả notifications cho demo users
    const fs = require('fs').promises;
    const path = require('path');
    const DATA_FILE = path.join(__dirname, '../data/notifications.json');
    
    const data = await fs.readFile(DATA_FILE, 'utf8');
    const allNotifications = JSON.parse(data);
    
    // Lọc notifications cho demo users
    const demoNotifications = allNotifications.filter(n => 
      n.toUserId && n.toUserId.toString().startsWith('demo-user')
    );
    
    res.json({ 
      success: true, 
      message: 'Lấy thông báo thành công',
      data: demoNotifications.sort((a, b) => 
        new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
      )
    });
  } catch (error) {
    console.error('Get demo notifications error:', error);
    res.status(500).json({ 
      success: false, 
      message: 'Lỗi khi lấy thông báo',
      data: []
    });
  }
});

// @route   DELETE /api/notifications/:id
// @desc    Delete a notification
// @access  Public (for demo)
router.delete('/:id', async (req, res) => {
  try {
    const fs = require('fs').promises;
    const path = require('path');
    const DATA_FILE = path.join(__dirname, '../data/notifications.json');
    
    const data = await fs.readFile(DATA_FILE, 'utf8');
    let notifications = JSON.parse(data);
    
    const initialLength = notifications.length;
    notifications = notifications.filter(n => n.id !== req.params.id);
    
    if (notifications.length === initialLength) {
      return res.status(404).json({ 
        success: false, 
        message: 'Không tìm thấy thông báo' 
      });
    }
    
    await fs.writeFile(DATA_FILE, JSON.stringify(notifications, null, 2), 'utf8');
    
    res.json({ 
      success: true, 
      message: 'Xóa thông báo thành công'
    });
  } catch (error) {
    console.error('Delete notification error:', error);
    res.status(500).json({ 
      success: false, 
      message: 'Lỗi khi xóa thông báo'
    });
  }
});

// @route   DELETE /api/notifications/demo-user/all
// @desc    Delete all demo user notifications
// @access  Public (for demo)
router.delete('/demo-user/all', async (req, res) => {
  try {
    const fs = require('fs').promises;
    const path = require('path');
    const DATA_FILE = path.join(__dirname, '../data/notifications.json');
    
    const data = await fs.readFile(DATA_FILE, 'utf8');
    let notifications = JSON.parse(data);
    
    // Giữ lại notifications không phải của demo users
    notifications = notifications.filter(n => 
      !n.toUserId || !n.toUserId.toString().startsWith('demo-user')
    );
    
    await fs.writeFile(DATA_FILE, JSON.stringify(notifications, null, 2), 'utf8');
    
    res.json({ 
      success: true, 
      message: 'Xóa tất cả thông báo thành công'
    });
  } catch (error) {
    console.error('Delete all notifications error:', error);
    res.status(500).json({ 
      success: false, 
      message: 'Lỗi khi xóa thông báo'
    });
  }
});

module.exports = router;
