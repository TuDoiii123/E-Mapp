const fs = require('fs');
const path = require('path');

const reviewsPath = path.join(__dirname, '../data/review.json');

// Load existing reviews
let reviews = JSON.parse(fs.readFileSync(reviewsPath, 'utf8'));
let nextId = reviews.length + 1;

console.log('🚀 Real-time review simulation started');
console.log(`📊 Current reviews: ${reviews.length}`);
console.log('⏱️  New review every 10-30 seconds\n');

function generateRealtimeReview() {
  const agencies = [
    { id: 'Q1-UBND', name: 'UBND Quận 1', district: 'Quận 1' },
    { id: 'Q3-UBND', name: 'UBND Quận 3', district: 'Quận 3' },
    { id: 'BTN-UBND', name: 'UBND Quận Bình Thạnh', district: 'Bình Thạnh' }
  ];
  
  const services = ['Chứng thực', 'Cấp phép kinh doanh', 'Đăng ký khai sinh'];
  const departments = ['Bộ phận Một cửa', 'TN&MT', 'Kinh tế'];
  const channels = ['Trực tiếp', 'Trực tuyến'];
  
  const randomElement = (arr) => arr[Math.floor(Math.random() * arr.length)];
  const randomRating = () => 3 + Math.random() * 2; // Bias 3-5
  
  const agency = randomElement(agencies);
  const attitudeRating = Math.round(randomRating());
  const speedRating = Math.round(randomRating());
  const qualityRating = Math.round(randomRating());
  const overallRating = (attitudeRating + speedRating + qualityRating) / 3;
  
  return {
    review_id: `R-${String(nextId).padStart(4, '0')}`,
    user_name: `User ${nextId}`,
    agency_id: agency.id,
    agency_name: agency.name,
    department: randomElement(departments),
    service_type: randomElement(services),
    ward: `Phường ${Math.floor(Math.random() * 20) + 1}`,
    district: agency.district,
    attitude_rating: attitudeRating,
    speed_rating: speedRating,
    quality_rating: qualityRating,
    overall_rating: parseFloat(overallRating.toFixed(1)),
    comment: 'Đánh giá thời gian thực',
    channel: randomElement(channels),
    processing_time_days: Math.floor(Math.random() * 5) + 1,
    created_at: new Date().toISOString().split('T')[0]
  };
}

function addReview() {
  const newReview = generateRealtimeReview();
  reviews.unshift(newReview);
  
  if (reviews.length > 1000) {
    reviews = reviews.slice(0, 1000);
  }
  
  fs.writeFileSync(reviewsPath, JSON.stringify(reviews, null, 2));
  
  const timestamp = new Date().toLocaleTimeString();
  console.log(`✅ [${timestamp}] Review ${newReview.review_id}`);
  console.log(`   Agency: ${newReview.agency_name}`);
  console.log(`   Rating: ${newReview.overall_rating}⭐`);
  console.log(`   Total: ${reviews.length} reviews`);
  console.log('   ───────────────────────────────────');
  
  nextId++;
}

// Add review every 10-30 seconds
function scheduleNext() {
  const delay = 10000 + Math.random() * 20000; // 10-30s
  setTimeout(() => {
    addReview();
    scheduleNext();
  }, delay);
}

// Start simulation
addReview(); // First review immediately
scheduleNext();

// Keep process alive
process.on('SIGINT', () => {
  console.log('\n🛑 Simulation stopped');
  console.log(`📊 Total reviews: ${reviews.length}`);
  process.exit();
});
