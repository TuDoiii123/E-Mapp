const express = require('express');
const path = require('path');
const fs = require('fs');

console.log('\n========================================');
console.log('  ROUTE DEBUGGING');
console.log('========================================\n');

// 1. Kiểm tra file reviews.js tồn tại
const reviewsPath = path.join(__dirname, '../routes/reviews.js');
console.log('1️⃣  Checking reviews.js file:');
console.log(`   Path: ${reviewsPath}`);
if (fs.existsSync(reviewsPath)) {
  console.log('   ✅ File exists');
} else {
  console.log('   ❌ File NOT found');
  process.exit(1);
}

// 2. Kiểm tra file review.json tồn tại
const dataPath = path.join(__dirname, '../data/review.json');
console.log('\n2️⃣  Checking review.json file:');
console.log(`   Path: ${dataPath}`);
if (fs.existsSync(dataPath)) {
  console.log('   ✅ File exists');
  try {
    const data = JSON.parse(fs.readFileSync(dataPath, 'utf8'));
    console.log(`   ✅ Valid JSON with ${data.length} reviews`);
  } catch (e) {
    console.log(`   ❌ Invalid JSON: ${e.message}`);
  }
} else {
  console.log('   ❌ File NOT found');
}

// 3. Thử load module reviews.js
console.log('\n3️⃣  Loading reviews.js module:');
try {
  const reviewRoutes = require('../routes/reviews');
  console.log('   ✅ Module loaded successfully');
  console.log(`   Type: ${typeof reviewRoutes}`);
} catch (e) {
  console.log(`   ❌ Error loading module: ${e.message}`);
  console.log(e.stack);
  process.exit(1);
}

// 4. Test Express app với route
console.log('\n4️⃣  Testing Express route registration:');
try {
  const app = express();
  const reviewRoutes = require('../routes/reviews');
  
  app.use('/api/reviews', reviewRoutes);
  
  // Lấy danh sách routes
  const routes = [];
  app._router.stack.forEach(middleware => {
    if (middleware.route) {
      routes.push({
        path: middleware.route.path,
        methods: Object.keys(middleware.route.methods)
      });
    } else if (middleware.name === 'router') {
      middleware.handle.stack.forEach(handler => {
        if (handler.route) {
          const basePath = middleware.regexp.source
            .replace('\\/?', '')
            .replace('(?=\\/|$)', '')
            .replace(/\\/g, '');
          routes.push({
            path: basePath + handler.route.path,
            methods: Object.keys(handler.route.methods)
          });
        }
      });
    }
  });
  
  console.log('   ✅ Routes registered:');
  routes.forEach(route => {
    console.log(`      ${route.methods.join(', ').toUpperCase()} ${route.path}`);
  });
  
} catch (e) {
  console.log(`   ❌ Error: ${e.message}`);
  console.log(e.stack);
}

console.log('\n========================================\n');
