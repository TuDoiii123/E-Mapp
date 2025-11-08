const express = require('express');
const PublicService = require('../models/PublicService');
const ServiceCategory = require('../models/ServiceCategory');
const { findNearby } = require('../services/distance');
const { authenticateToken } = require('../middleware/auth');

const router = express.Router();

// @route   GET /api/services/nearby
// @desc    Get nearby public services
// @access  Public
router.get('/nearby', async (req, res) => {
  try {
    const { lat, lng, radius = 10, category, level } = req.query;

    if (!lat || !lng) {
      return res.status(400).json({
        success: false,
        message: 'Latitude và longitude là bắt buộc'
      });
    }

    const userLat = parseFloat(lat);
    const userLng = parseFloat(lng);
    const radiusKm = parseFloat(radius);

    if (isNaN(userLat) || isNaN(userLng)) {
      return res.status(400).json({
        success: false,
        message: 'Latitude và longitude không hợp lệ'
      });
    }

    // Get all services
    let services = await PublicService.findAll();

    // Filter by category if provided
    if (category) {
      services = services.filter(s => s.categoryId === category);
    }

    // Filter by level if provided
    if (level) {
      services = services.filter(s => s.level === level);
    }

    // Find nearby services
    const nearbyServices = findNearby(services, userLat, userLng, radiusKm);

    // Limit results (optional)
    const limit = parseInt(req.query.limit) || 20;
    const limitedResults = nearbyServices.slice(0, limit);

    res.json({
      success: true,
      data: {
        services: limitedResults,
        total: nearbyServices.length,
        userLocation: {
          latitude: userLat,
          longitude: userLng
        },
        radius: radiusKm
      }
    });
  } catch (error) {
    console.error('Nearby services error:', error);
    res.status(500).json({
      success: false,
      message: 'Lỗi khi tìm kiếm dịch vụ gần đây'
    });
  }
});

// @route   GET /api/services/search
// @desc    Search public services
// @access  Public
router.get('/search', async (req, res) => {
  try {
    const { q, category, level, province, district } = req.query;

    let services = await PublicService.search(q || '', category);

    // Filter by level
    if (level) {
      services = services.filter(s => s.level === level);
    }

    // Filter by province
    if (province) {
      services = services.filter(s => 
        s.address.toLowerCase().includes(province.toLowerCase())
      );
    }

    // Filter by district
    if (district) {
      services = services.filter(s => 
        s.address.toLowerCase().includes(district.toLowerCase())
      );
    }

    // If user location provided, calculate distances
    if (req.query.lat && req.query.lng) {
      const userLat = parseFloat(req.query.lat);
      const userLng = parseFloat(req.query.lng);
      if (!isNaN(userLat) && !isNaN(userLng)) {
        const { findNearby } = require('../services/distance');
        const servicesWithDistance = findNearby(services, userLat, userLng, 100);
        services = servicesWithDistance;
      }
    }

    // Sort by distance if available, otherwise by name
    services.sort((a, b) => {
      if (a.distance !== undefined && b.distance !== undefined) {
        return a.distance - b.distance;
      }
      return a.name.localeCompare(b.name);
    });

    const limit = parseInt(req.query.limit) || 50;
    const limitedResults = services.slice(0, limit);

    res.json({
      success: true,
      data: {
        services: limitedResults,
        total: services.length,
        query: q || '',
        filters: {
          category,
          level,
          province,
          district
        }
      }
    });
  } catch (error) {
    console.error('Search services error:', error);
    res.status(500).json({
      success: false,
      message: 'Lỗi khi tìm kiếm dịch vụ'
    });
  }
});

// @route   GET /api/services/:id
// @desc    Get service details
// @access  Public
router.get('/:id', async (req, res) => {
  try {
    const service = await PublicService.findById(req.params.id);

    if (!service) {
      return res.status(404).json({
        success: false,
        message: 'Không tìm thấy dịch vụ'
      });
    }

    // Get category info if available
    let category = null;
    if (service.categoryId) {
      category = await ServiceCategory.findById(service.categoryId);
    }

    // Calculate distance if user location provided
    if (req.query.lat && req.query.lng) {
      const userLat = parseFloat(req.query.lat);
      const userLng = parseFloat(req.query.lng);
      if (!isNaN(userLat) && !isNaN(userLng)) {
        const { calculateDistance } = require('../services/distance');
        service.distance = calculateDistance(
          userLat,
          userLng,
          service.latitude,
          service.longitude
        );
      }
    }

    res.json({
      success: true,
      data: {
        service: {
          ...service,
          category
        }
      }
    });
  } catch (error) {
    console.error('Get service error:', error);
    res.status(500).json({
      success: false,
      message: 'Lỗi khi lấy thông tin dịch vụ'
    });
  }
});

// @route   GET /api/services
// @desc    Get all services with filters
// @access  Public
router.get('/', async (req, res) => {
  try {
    const { category, level, province, limit = 100 } = req.query;

    let services = await PublicService.findAll();

    // Apply filters
    if (category) {
      services = services.filter(s => s.categoryId === category);
    }

    if (level) {
      services = services.filter(s => s.level === level);
    }

    if (province) {
      services = services.filter(s => 
        s.address.toLowerCase().includes(province.toLowerCase())
      );
    }

    // Calculate distances if user location provided
    if (req.query.lat && req.query.lng) {
      const userLat = parseFloat(req.query.lat);
      const userLng = parseFloat(req.query.lng);
      if (!isNaN(userLat) && !isNaN(userLng)) {
        const { findNearby } = require('../services/distance');
        const servicesWithDistance = findNearby(services, userLat, userLng, 100);
        services = servicesWithDistance;
      }
    }

    const limitNum = parseInt(limit);
    const limitedResults = services.slice(0, limitNum);

    res.json({
      success: true,
      data: {
        services: limitedResults,
        total: services.length
      }
    });
  } catch (error) {
    console.error('Get services error:', error);
    res.status(500).json({
      success: false,
      message: 'Lỗi khi lấy danh sách dịch vụ'
    });
  }
});

// @route   GET /api/services/categories/list
// @desc    Get all service categories
// @access  Public
router.get('/categories/list', async (req, res) => {
  try {
    const categories = await ServiceCategory.findAll();
    res.json({
      success: true,
      data: {
        categories
      }
    });
  } catch (error) {
    console.error('Get categories error:', error);
    res.status(500).json({
      success: false,
      message: 'Lỗi khi lấy danh mục dịch vụ'
    });
  }
});

// @route   GET /api/services/popular
// @desc    Get popular services by level
// @access  Public
router.get('/popular', async (req, res) => {
  try {
    const { level } = req.query;
    let services = await PublicService.findAll();

    // Filter by level
    if (level) {
      services = services.filter(s => s.level === level);
    }

    // Sort by rating and status
    services.sort((a, b) => {
      if (a.rating !== b.rating) {
        return b.rating - a.rating;
      }
      // Prefer available services
      const statusOrder = { 'available': 0, 'normal': 1, 'busy': 2 };
      return (statusOrder[a.status] || 1) - (statusOrder[b.status] || 1);
    });

    const limit = parseInt(req.query.limit) || 10;
    const popularServices = services.slice(0, limit);

    res.json({
      success: true,
      data: {
        services: popularServices,
        level: level || 'all'
      }
    });
  } catch (error) {
    console.error('Get popular services error:', error);
    res.status(500).json({
      success: false,
      message: 'Lỗi khi lấy dịch vụ phổ biến'
    });
  }
});

module.exports = router;

