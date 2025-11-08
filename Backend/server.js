const express = require('express');
const cors = require('cors');
const dotenv = require('dotenv');
const authRoutes = require('./routes/auth');
const servicesRoutes = require('./routes/services');
const { authenticateToken } = require('./middleware/auth');
const { seedData } = require('./scripts/seedData');

dotenv.config();

const app = express();
const PORT = process.env.PORT || 8888;

// Middleware
app.use(cors({
  origin: '*', // In production, specify your frontend URL
  credentials: true
}));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Health check
app.get('/api/health', (req, res) => {
  res.json({ 
    status: 'ok', 
    message: 'Public Services Backend API',
    timestamp: new Date().toISOString()
  });
});

// Auth routes
app.use('/api/auth', authRoutes);

// Services routes
app.use('/api/services', servicesRoutes);

// Protected routes example
app.get('/api/protected', authenticateToken, (req, res) => {
  res.json({ 
    message: 'This is a protected route',
    user: req.user 
  });
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(err.status || 500).json({
    success: false,
    message: err.message || 'Internal Server Error',
    ...(process.env.NODE_ENV === 'development' && { stack: err.stack })
  });
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({
    success: false,
    message: 'Route not found'
  });
});

// Initialize seed data on startup (only in development)
if (process.env.NODE_ENV !== 'production') {
  seedData().catch(err => {
    console.error('Error seeding data:', err);
  });
}

app.listen(PORT, '0.0.0.0', () => {
  console.log(`==========================================`);
  console.log(`  PUBLIC SERVICES BACKEND SERVER`);
  console.log(`==========================================`);
  console.log(`Server running on port ${PORT}`);
  console.log(`Health check: http://192.168.1.231:${PORT}/api/health`);
  console.log(`Environment: ${process.env.NODE_ENV || 'development'}`);
  console.log(`==========================================`);
});

module.exports = app;

