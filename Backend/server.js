const express = require('express');
const cors = require('cors');
const dotenv = require('dotenv');
const path = require('path');

dotenv.config();

const app = express();
const PORT = 8888;
// Voice backend (FastAPI) base URL
const VOICE_BASE = process.env.VOICE_BASE || 'http://127.0.0.1:8000';

// Lazy import for node-fetch (ESM) in CommonJS
const fetch = (...args) => import('node-fetch').then(({default: fetch}) => fetch(...args));
// Multer for handling multipart/form-data uploads
const multer = require('multer');
const upload = multer({ storage: multer.memoryStorage() });

// Middleware
app.use(cors({
  origin: (origin, callback) => {
    const allowed = ['http://localhost:5173', 'http://localhost:3000', 'http://localhost:3001'];
    if (!origin || allowed.includes(origin)) return callback(null, true);
    // Allow all localhost ports for dev convenience
    if (/^http:\/\/localhost:\d{2,5}$/.test(origin)) return callback(null, true);
    return callback(null, true); // fallback to allow for demo
  },
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization'],
  credentials: true,
  optionsSuccessStatus: 204
}));
// Global preflight handler
app.options('*', cors());
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

// 8. Voice routes proxy → FastAPI
// POST /api/voice/stt → forwards to FastAPI /voice/stt
app.post('/api/voice/stt', upload.single('file'), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ status: 'error', message: 'Missing audio file under field name "file"' });
    }

    // Use Web FormData available in Node.js 18+
    const form = new FormData();
    form.append('file', new Blob([req.file.buffer], { type: req.file.mimetype || 'audio/webm' }), req.file.originalname || 'audio.webm');

    const resp = await fetch(`${VOICE_BASE}/voice/stt`, {
      method: 'POST',
      body: form,
    });
    const data = await resp.json().catch(() => ({ status: 'error', message: 'Invalid JSON from voice backend' }));
    return res.status(resp.status).json(data);
  } catch (err) {
    console.error('Proxy STT error:', err);
    return res.status(500).json({ status: 'error', message: err.message || 'STT proxy error' });
  }
});

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