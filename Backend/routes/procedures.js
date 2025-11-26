const express = require('express');
const { body, validationResult } = require('express-validator');
const Procedure = require('../models/Procedure');
const Notification = require('../models/Notification');

const router = express.Router();

// @route   GET /api/procedures/user/:userId
// @desc    Get procedures for a user
// @access  Public (for demo)
router.get('/user/:userId', async (req, res) => {
  try {
    const procedures = await Procedure.findByUserId(req.params.userId);
    res.json({ 
      success: true, 
      message: 'Lấy danh sách thủ tục thành công',
      data: { procedures } 
    });
  } catch (error) {
    console.error('Get procedures error:', error);
    res.status(500).json({ 
      success: false, 
      message: 'Lỗi khi lấy danh sách thủ tục: ' + error.message
    });
  }
});

// @route   GET /api/procedures/all
// @desc    Get all procedures (Admin)
// @access  Public (for demo)
router.get('/all', async (req, res) => {
  try {
    const procedures = await Procedure.findAll();
    res.json({ 
      success: true, 
      message: 'Lấy danh sách thủ tục thành công',
      data: { procedures } 
    });
  } catch (error) {
    console.error('Get all procedures error:', error);
    res.status(500).json({ 
      success: false, 
      message: 'Lỗi khi lấy danh sách thủ tục: ' + error.message
    });
  }
});

// @route   PUT /api/procedures/:id/status
// @desc    Update procedure status (Admin)
// @access  Public (for demo)
router.put('/:id/status', [
  body('status').isIn(['received', 'processing', 'missing_docs', 'completed']).withMessage('Trạng thái không hợp lệ'),
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

    const procedure = await Procedure.findById(req.params.id);
    if (!procedure) {
      return res.status(404).json({ 
        success: false, 
        message: 'Không tìm thấy thủ tục' 
      });
    }

    const { status, note } = req.body;
    const updatedProcedure = await procedure.update({ status, note });

    // GỬI THÔNG BÁO
    let notificationTitle = '';
    let notificationMessage = '';

    switch (status) {
      case 'received':
        notificationTitle = 'Hồ sơ đã được tiếp nhận';
        notificationMessage = `Hồ sơ "${procedure.title}" đã được tiếp nhận và đang chờ xử lý.`;
        break;
      case 'processing':
        notificationTitle = 'Hồ sơ đang được xử lý';
        notificationMessage = `Hồ sơ "${procedure.title}" đang được xử lý. Vui lòng chờ thông báo tiếp theo.`;
        break;
      case 'missing_docs':
        notificationTitle = 'Cần bổ sung hồ sơ';
        notificationMessage = `Hồ sơ "${procedure.title}" cần bổ sung${note ? ': ' + note : ''}. Vui lòng liên hệ cơ quan.`;
        break;
      case 'completed':
        notificationTitle = 'Hồ sơ đã hoàn tất';
        notificationMessage = `Hồ sơ "${procedure.title}" đã hoàn tất. Bạn có thể đến nhận kết quả tại ${procedure.office}.`;
        break;
    }

    try {
      await Notification.create({
        toUserId: procedure.userId,
        fromAgencyId: procedure.agencyId,
        title: notificationTitle,
        message: notificationMessage,
        type: 'procedure_update',
        relatedId: procedure.id,
      });
      console.log('✅ Sent notification for procedure:', procedure.id);
    } catch (notifError) {
      console.error('⚠️  Failed to create notification:', notifError);
    }

    res.json({ 
      success: true, 
      message: 'Cập nhật trạng thái thành công',
      data: updatedProcedure 
    });
  } catch (error) {
    console.error('Update procedure status error:', error);
    res.status(500).json({ 
      success: false, 
      message: 'Lỗi khi cập nhật trạng thái: ' + error.message
    });
  }
});

module.exports = router;
