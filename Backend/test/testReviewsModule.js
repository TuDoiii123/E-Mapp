console.log('Testing reviews module...\n');

try {
  const reviewRoutes = require('../routes/reviews');
  console.log('✅ Module loaded successfully');
  console.log('Type:', typeof reviewRoutes);
  console.log('Keys:', Object.keys(reviewRoutes));
  console.log('Stack:', reviewRoutes.stack ? `${reviewRoutes.stack.length} routes` : 'No stack');
  
  // Kiểm tra routes
  if (reviewRoutes.stack) {
    console.log('\nRegistered routes:');
    reviewRoutes.stack.forEach((layer, i) => {
      if (layer.route) {
        console.log(`  ${i}: ${Object.keys(layer.route.methods)} ${layer.route.path}`);
      }
    });
  }
} catch (error) {
  console.error('❌ Error:', error.message);
  console.error(error.stack);
}
