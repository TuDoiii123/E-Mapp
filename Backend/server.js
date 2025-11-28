const express = require('express');
const cors = require('cors');
const dotenv = require('dotenv');
const path = require('path');

dotenv.config();

const app = express();
const PORT = 8888;

// Middleware
app.use(cors({
  origin: ['http://localhost:5173', 'http://localhost:3000'],
  credentials: true
}));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Request logger
app.use((req, res, next) => {
  console.log(`[${new Date().toISOString()}] ${req.method} ${req.path}`);
  next();
});

// === ROUTES ===

// 1. Health check
app.get('/api/health', (req, res) => {
  res.json({ 
    status: 'OK', 
    port: PORT, 
    timestamp: new Date().toISOString()
  });
});

// 2. Auth routes
const authRouter = require('./routes/auth');
app.use('/api/auth', authRouter);

// 3. Services routes
const servicesRouter = require('./routes/services');
app.use('/api/services', servicesRouter);

// 4. Reviews routes
const reviewsRouter = require('./routes/reviews');
app.use('/api/reviews', reviewsRouter);

// 5. Appointments routes
const appointmentsRouter = require('./routes/appointments');
app.use('/api/appointments', appointmentsRouter);

// 6. Notifications routes
const notificationsRouter = require('./routes/notifications');
app.use('/api/notifications', notificationsRouter);

// 7. Procedures routes - THÊM MỚI
const proceduresRouter = require('./routes/procedures');
app.use('/api/procedures', proceduresRouter);

// === ERROR HANDLERS (PHẢI Ở CUỐI) ===

// Error handling middleware
app.use((err, req, res, next) => {
  console.error('❌ ERROR:', err.stack);
  res.status(err.status || 500).json({
    success: false,
    message: err.message || 'Internal Server Error',
    ...(process.env.NODE_ENV === 'development' && { stack: err.stack })
  });
});

// 404 handler - CUỐI CÙNG
app.use((req, res) => {
  console.log(`❌ 404: ${req.method} ${req.path}`);
  res.status(404).json({
    success: false,
    message: 'Route not found',
    requestedPath: req.path
  });
});

// Start server
app.listen(PORT, '0.0.0.0', () => {
  console.log('\n==========================================');
  console.log('  PUBLIC SERVICES BACKEND SERVER');
  console.log('==========================================');
  console.log(`Port: ${PORT}`);
  console.log('\n📍 Access URLs:');
  console.log(`  Health:  http://localhost:${PORT}/api/health`);
  console.log(`  Auth:    http://localhost:${PORT}/api/auth`);
  console.log(`  Services: http://localhost:${PORT}/api/services`);
  console.log(`  Reviews: http://localhost:${PORT}/api/reviews`);
  console.log(`  Appointments: http://localhost:${PORT}/api/appointments`);
  console.log(`  Notifications: http://localhost:${PORT}/api/notifications`);
  console.log(`  Procedures: http://localhost:${PORT}/api/procedures`);
  console.log('\nEnvironment:', process.env.NODE_ENV || 'development');
  console.log('==========================================\n');
});

module.exports = app;