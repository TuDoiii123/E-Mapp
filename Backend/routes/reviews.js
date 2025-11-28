const express = require('express');
const router = express.Router();
const fs = require('fs');
const path = require('path');

const REVIEWS_FILE = path.join(__dirname, '../data/review.json');

// Cache cho analytics
let analyticsCache = {
  data: null,
  lastUpdated: 0,
  ttl: 5 * 60 * 1000 // 5 phút
};

// Helper function đọc reviews
const getReviews = () => {
  try {
    const data = fs.readFileSync(REVIEWS_FILE, 'utf8');
    return JSON.parse(data);
  } catch (error) {
    console.error('Error reading reviews:', error);
    return [];
  }
};

// GET /api/reviews - Lấy reviews với filter
router.get('/', (req, res) => {
  try {
    let reviews = getReviews();
    
    // Filter theo province
    if (req.query.province && req.query.province !== 'all') {
      reviews = reviews.filter(r => r.province === req.query.province);
    }
    
    // Filter theo agency
    if (req.query.agency && req.query.agency !== 'all') {
      reviews = reviews.filter(r => r.agency_name === req.query.agency);
    }
    
    // Filter theo service
    if (req.query.service && req.query.service !== 'all') {
      reviews = reviews.filter(r => r.service_type === req.query.service);
    }
    
    // LỌC CHỈ LẤY REVIEWS HỢP LỆ
    const validReviews = reviews.filter(r => 
      r && r.review_id && r.agency_name && r.created_at && typeof r.overall_rating === 'number'
    );

    const transformed = validReviews.map(r => ({
      id: r.review_id,
      userId: r.user_name,
      userName: r.user_name,
      agencyId: r.agency_id,
      agencyName: r.agency_name,
      province: r.province,
      department: r.department,
      serviceId: r.service_type,
      serviceName: r.service_type,
      rating: parseFloat(r.overall_rating),
      attitudeRating: r.attitude_rating,
      speedRating: r.speed_rating,
      qualityRating: r.quality_rating,
      comment: r.comment,
      channel: r.channel,
      createdAt: r.created_at,
      sentimentScore: r.sentiment_score || 0.5,
      sentimentLabel: r.sentiment_label || 'Trung lập',
      keywords: r.keywords || []
    }));
    
    res.json({
      success: true,
      data: transformed,
      total: transformed.length,
      message: 'Lấy dữ liệu thành công'
    });
  } catch (error) {
    console.error('[REVIEWS] Error:', error);
    res.status(500).json({
      success: false,
      message: error.message
    });
  }
});

// GET /api/reviews/analytics - Analytics với filter
router.get('/analytics', (req, res) => {
  try {
    let reviews = getReviews();
    
    // Apply filters giống như route chính
    if (req.query.province && req.query.province !== 'all') {
      reviews = reviews.filter(r => r.province === req.query.province);
    }
    
    if (req.query.agency && req.query.agency !== 'all') {
      reviews = reviews.filter(r => r.agency_name === req.query.agency);
    }
    
    if (req.query.service && req.query.service !== 'all') {
      reviews = reviews.filter(r => r.service_type === req.query.service);
    }
    
    const validReviews = reviews.filter(r => 
      r && typeof r.overall_rating === 'number'
    );
    
    const analytics = computeAnalytics(validReviews);
    
    res.json({
      success: true,
      data: analytics
    });
  } catch (error) {
    console.error('[REVIEWS] Error:', error);
    res.status(500).json({
      success: false,
      message: error.message
    });
  }
});

function computeAnalytics(reviews) {
  const stats = {
    total: reviews.length,
    byAgency: {},
    byService: {},
    byChannel: {},
    byMonth: {},
    bySentiment: { 'Tích cực': 0, 'Trung lập': 0, 'Tiêu cực': 0 },
    overallAvg: 0,
    ratingDist: { 1: 0, 2: 0, 3: 0, 4: 0, 5: 0 }
  };
  
  if (reviews.length === 0) return stats;
  
  let totalRating = 0;
  
  reviews.forEach(r => {
    const rating = parseFloat(r.overall_rating);
    totalRating += rating;
    
    // Rating distribution
    const rounded = Math.round(rating);
    if (rounded >= 1 && rounded <= 5) {
      stats.ratingDist[rounded]++;
    }
    
    // By sentiment
    const sentiment = r.sentiment_label || 'Trung lập';
    if (stats.bySentiment[sentiment] !== undefined) {
      stats.bySentiment[sentiment]++;
    }
    
    // By agency
    if (!stats.byAgency[r.agency_name]) {
      stats.byAgency[r.agency_name] = { total: 0, count: 0, avg: 0 };
    }
    stats.byAgency[r.agency_name].total += rating;
    stats.byAgency[r.agency_name].count++;
    
    // By service
    if (!stats.byService[r.service_type]) {
      stats.byService[r.service_type] = { total: 0, count: 0, avg: 0 };
    }
    stats.byService[r.service_type].total += rating;
    stats.byService[r.service_type].count++;
    
    // By channel
    const channel = r.channel || 'Không xác định';
    if (!stats.byChannel[channel]) {
      stats.byChannel[channel] = { total: 0, count: 0, avg: 0 };
    }
    stats.byChannel[channel].total += rating;
    stats.byChannel[channel].count++;
    
    // By month
    const month = r.created_at.substring(0, 7);
    if (!stats.byMonth[month]) {
      stats.byMonth[month] = { total: 0, count: 0, avg: 0 };
    }
    stats.byMonth[month].total += rating;
    stats.byMonth[month].count++;
  });
  
  stats.overallAvg = totalRating / reviews.length;
  
  // Tính avg cho từng category
  Object.keys(stats.byAgency).forEach(key => {
    stats.byAgency[key].avg = stats.byAgency[key].total / stats.byAgency[key].count;
  });
  
  Object.keys(stats.byService).forEach(key => {
    stats.byService[key].avg = stats.byService[key].total / stats.byService[key].count;
  });
  
  Object.keys(stats.byChannel).forEach(key => {
    stats.byChannel[key].avg = stats.byChannel[key].total / stats.byChannel[key].count;
  });
  
  Object.keys(stats.byMonth).forEach(key => {
    stats.byMonth[key].avg = stats.byMonth[key].total / stats.byMonth[key].count;
  });
  
  return stats;
}

module.exports = router;