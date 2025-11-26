const fs = require('fs');
const path = require('path');

// ĐỌC DỮ LIỆU TỪ 3 FILE JSON
function loadAgencyData(filePath) {
  try {
    const content = fs.readFileSync(filePath, 'utf8');
    const data = JSON.parse(content);
    
    if (!Array.isArray(data) || data.length === 0) {
      console.warn(`⚠️  File ${path.basename(filePath)} is empty or invalid`);
      return [];
    }
    
    // Lấy tỉnh từ tên file hoặc từ data
    const fileName = path.basename(filePath, '.json');
    let province = 'Unknown';
    
    if (fileName.includes('hatinh')) province = 'Hà Tĩnh';
    else if (fileName.includes('quangninh')) province = 'Quảng Ninh';
    else if (fileName.includes('thanhhoa')) province = 'Thanh Hóa';
    
    // Nếu data có trường Province, ưu tiên dùng nó
    if (data[0] && data[0].Province) {
      province = data[0].Province;
    }
    
    console.log(`   Found ${data.length} entries for ${province}`);
    
    return data.map(item => ({
      ...item,
      Province: province
    }));
  } catch (error) {
    console.error(`❌ Error reading ${filePath}:`, error.message);
    return [];
  }
}

console.log('📖 Reading JSON files...\n');

const haTinhData = loadAgencyData(path.join(__dirname, '../data/agency_data_hatinh.json'));
const quangNinhData = loadAgencyData(path.join(__dirname, '../data/agency_data_quangninh.json'));
const thanhHoaData = loadAgencyData(path.join(__dirname, '../data/agency_data_thanhhoa.json'));

console.log(`\n📊 Data summary:`);
console.log(`   Hà Tĩnh: ${haTinhData.length} entries`);
console.log(`   Quảng Ninh: ${quangNinhData.length} entries`);
console.log(`   Thanh Hóa: ${thanhHoaData.length} entries`);

// KIỂM TRA DỮ LIỆU
const allData = [...haTinhData, ...quangNinhData, ...thanhHoaData];
if (allData.length === 0) {
  console.error('\n❌ ERROR: No data found in any JSON file!');
  process.exit(1);
}

// TẠO DANH SÁCH AGENCIES VÀ SERVICES TỪ DỮ LIỆU THỰC
const agenciesMap = new Map();
const servicesMap = new Map();

allData.forEach(row => {
  const agencyName = row.AGENCY_NAME || row.Province; // Fallback to Province if no AGENCY_NAME
  const serviceName = row.NAME || 'Dịch vụ hành chính';
  const province = row.Province;
  
  if (agencyName && !agenciesMap.has(agencyName)) {
    agenciesMap.set(agencyName, {
      id: `AGC-${agenciesMap.size + 1}`,
      name: agencyName,
      province: province
    });
  }
  
  if (serviceName && !servicesMap.has(serviceName)) {
    servicesMap.set(serviceName, {
      name: serviceName,
      field: row.FIELD || 'Dịch vụ hành chính',
      agency: agencyName,
      province: province
    });
  }
});

const agencies = Array.from(agenciesMap.values());
const services = Array.from(servicesMap.values());

console.log(`\n🏢 Unique agencies: ${agencies.length}`);
console.log(`📋 Unique services: ${services.length}`);

if (agencies.length === 0 || services.length === 0) {
  console.error('\n❌ ERROR: No agencies or services extracted!');
  process.exit(1);
}

console.log('\n📝 Sample data:');
console.log('   Agencies:', agencies.slice(0, 3).map(a => `${a.name} (${a.province})`));
console.log('   Services:', services.slice(0, 3).map(s => `${s.name} (${s.province})`));

const channels = ['Trực tiếp', 'Trực tuyến'];

const vietnameseNames = [
  'Nguyễn Văn Anh', 'Trần Thị Lan', 'Lê Hoàng Nam', 'Phạm Thị Thu', 'Võ Minh Tuấn',
  'Đinh Thu Hương', 'Ngô Quốc Bảo', 'Bùi Thị Mai', 'Hoàng Văn Cường', 'Lương Hữu Đức',
  'Đỗ Thị Ngọc', 'Phan Văn Hải', 'Vũ Thị Hồng', 'Đặng Minh Khôi', 'Mai Thanh Phong',
  'Trương Thị Linh', 'Đoàn Văn Sơn', 'Nguyễn Thị Hoa', 'Lý Quang Vinh', 'Tôn Thất An'
];

const detailedComments = {
  5: [
    'Cán bộ rất nhiệt tình, hướng dẫn tận tình từng bước. Thủ tục đơn giản, nhanh chóng. Rất hài lòng!',
    'Phục vụ xuất sắc, không phải chờ đợi lâu. Nhân viên giải thích rõ ràng, dễ hiểu. 5 sao xứng đáng!',
    'Quy trình minh bạch, nhân viên chuyên nghiệp. Hồ sơ được xử lý đúng hẹn. Tôi rất ấn tượng.',
    'Cơ sở vật chất hiện đại, sạch sẽ. Cán bộ làm việc hiệu quả, giải quyết nhanh. Đánh giá cao!'
  ],
  4: [
    'Nhân viên nhiệt tình nhưng có lúc hơi đông người chờ. Nhìn chung vẫn tốt.',
    'Hồ sơ được giải quyết đúng thời hạn, thái độ phục vụ tốt. Chỉ cần cải thiện thêm về cơ sở vật chất.',
    'Tốt, chỉ có điều phải chờ hơi lâu một chút do nhiều người. Nhưng nhân viên rất có trách nhiệm.',
    'Thủ tục rõ ràng, cán bộ hướng dẫn chi tiết. Mong cải thiện thêm về tốc độ xử lý.'
  ],
  3: [
    'Bình thường, thái độ cán bộ ổn nhưng tốc độ xử lý chưa nhanh. Có thể cải thiện thêm.',
    'Thủ tục hơi phức tạp, phải bổ sung giấy tờ nhiều lần. Nhân viên cũng chưa hướng dẫn rõ lắm.',
    'Trung bình, mong cải thiện về thời gian chờ và sự rõ ràng trong quy trình.',
    'Hồ sơ được giải quyết nhưng mất nhiều thời gian hơn dự kiến. Cần tối ưu quy trình.'
  ],
  2: [
    'Thái độ phục vụ chưa tốt, cán bộ thiếu kiên nhẫn khi giải thích. Tốc độ xử lý chậm.',
    'Phải đến nhiều lần vì thiếu hướng dẫn rõ ràng ngay từ đầu. Rất mất thời gian.',
    'Không hài lòng về tốc độ, hồ sơ bị trễ hẹn mà không có thông báo gì.',
    'Cơ sở vật chất kém, chỗ ngồi chờ không đủ. Nhân viên làm việc thiếu nhiệt tình.'
  ],
  1: [
    'Rất tệ! Thái độ cán bộ lạnh lùng, không giải thích gì. Hồ sơ chậm mà không rõ lý do.',
    'Tôi rất thất vọng. Phải đến 3 lần mới nộp được vì mỗi lần yêu cầu giấy tờ khác nhau.',
    'Cần cải cách ngay! Quy trình lộn xộn, cán bộ thiếu chuyên môn. Tôi đã lãng phí cả tuần.',
    'Quá tệ, không có sự hỗ trợ nào. Hồ sơ bị thất lạc mà không ai chịu trách nhiệm.'
  ]
};

const officers = [
  'Nguyễn Thị Lan', 'Trần Văn Hùng', 'Lê Minh Phương', 'Phạm Thu Hà',
  'Võ Đức Anh', 'Đinh Thị Mai', 'Hoàng Văn Nam', 'Bùi Thị Hương'
];

function randomElement(arr) {
  return arr[Math.floor(Math.random() * arr.length)];
}

function analyzeSentiment(rating, comment) {
  if (rating >= 4.5) return { score: 0.9, label: 'Rất tích cực' };
  if (rating >= 4.0) return { score: 0.7, label: 'Tích cực' };
  if (rating >= 3.0) return { score: 0.5, label: 'Trung lập' };
  if (rating >= 2.0) return { score: 0.3, label: 'Tiêu cực' };
  return { score: 0.1, label: 'Rất tiêu cực' };
}

function extractKeywords(comment) {
  const positiveWords = ['tốt', 'nhanh', 'nhiệt tình', 'chuyên nghiệp', 'hài lòng', 'xuất sắc', 'tận tình'];
  const negativeWords = ['chậm', 'kém', 'tệ', 'thiếu', 'không', 'lạnh lùng', 'mất thời gian'];
  
  const keywords = [];
  positiveWords.forEach(word => {
    if (comment.toLowerCase().includes(word)) keywords.push(word);
  });
  negativeWords.forEach(word => {
    if (comment.toLowerCase().includes(word)) keywords.push(word);
  });
  
  return keywords.slice(0, 3);
}

function generateReview(id, daysAgo) {
  const agency = randomElement(agencies);
  const service = randomElement(services.filter(s => s.province === agency.province));
  const channel = randomElement(channels);
  
  const department = service.name;
  
  const rand = Math.random();
  let baseRating;
  
  if (rand < 0.05) {
    baseRating = 1 + Math.random() * 0.5;
  } else if (rand < 0.10) {
    baseRating = 1.5 + Math.random() * 0.8;
  } else if (rand < 0.30) {
    baseRating = 2.5 + Math.random() * 0.9;
  } else if (rand < 0.70) {
    baseRating = 3.5 + Math.random() * 0.9;
  } else {
    baseRating = 4.5 + Math.random() * 0.5;
  }
  
  const variance = 0.3;
  const attitudeRating = Math.round(Math.max(1, Math.min(5, baseRating + (Math.random() - 0.5) * variance)));
  const speedRating = Math.round(Math.max(1, Math.min(5, baseRating + (Math.random() - 0.5) * variance)));
  const qualityRating = Math.round(Math.max(1, Math.min(5, baseRating + (Math.random() - 0.5) * variance)));
  const helpfulnessRating = Math.round(Math.max(1, Math.min(5, baseRating + (Math.random() - 0.5) * variance)));
  const facilityRating = Math.round(Math.max(1, Math.min(5, baseRating + (Math.random() - 0.5) * variance)));
  
  const clamp = (val) => Math.max(1, Math.min(5, val));
  
  const overallRating = (
    clamp(attitudeRating) + 
    clamp(speedRating) + 
    clamp(qualityRating) + 
    clamp(helpfulnessRating) + 
    clamp(facilityRating)
  ) / 5;
  
  const roundedRating = Math.round(overallRating);
  const comment = randomElement(detailedComments[roundedRating] || detailedComments[3]);
  
  const processingDays = channel === 'Trực tuyến' 
    ? Math.floor(Math.random() * 3) + 1 
    : Math.floor(Math.random() * 5) + 1;
  
  const actualProcessingDays = processingDays + Math.floor(Math.random() * 3) - 1;
  
  const sentiment = analyzeSentiment(overallRating, comment);
  const keywords = extractKeywords(comment);
  
  const submittedDate = new Date();
  submittedDate.setDate(submittedDate.getDate() - daysAgo);
  const createdDate = new Date(submittedDate);
  createdDate.setDate(createdDate.getDate() - processingDays);
  
  return {
    review_id: `R-${String(id).padStart(4, '0')}`,
    user_name: randomElement(vietnameseNames),
    
    agency_id: agency.id,
    agency_name: agency.name,
    province: agency.province, // THÊM TRƯỜNG PROVINCE
    department,
    service_type: service.name,
    service_code: `DV-${Math.floor(Math.random() * 9000) + 1000}`,
    ward: `Phường ${Math.floor(Math.random() * 20) + 1}`,
    district: agency.province,
    
    attitude_rating: clamp(attitudeRating),
    speed_rating: clamp(speedRating),
    quality_rating: clamp(qualityRating),
    helpfulness_rating: clamp(helpfulnessRating),
    facility_rating: clamp(facilityRating),
    overall_rating: parseFloat(overallRating.toFixed(1)),
    
    comment,
    sentiment_score: sentiment.score,
    sentiment_label: sentiment.label,
    keywords,
    
    channel,
    processing_time_days: processingDays,
    actual_processing_days: actualProcessingDays,
    officer_name: Math.random() > 0.3 ? randomElement(officers) : null,
    
    document_id: `HS-${String(id * 2).padStart(6, '0')}`,
    created_at: createdDate.toISOString().split('T')[0],
    submitted_at: submittedDate.toISOString(),
    verified: Math.random() > 0.1,
    status: Math.random() > 0.05 ? 'approved' : 'pending',
    complaint_category: roundedRating < 3 ? (Math.random() > 0.5 ? 'Chậm tiến độ' : 'Thái độ không tốt') : null,
    response_from_agency: roundedRating < 3 && Math.random() > 0.5 
      ? 'Cảm ơn phản hồi, chúng tôi sẽ cải thiện.' 
      : null
  };
}

function generateReviews(count) {
  const reviews = [];
  const maxDaysAgo = 365;
  
  for (let i = 1; i <= count; i++) {
    const daysAgo = Math.floor(Math.random() * maxDaysAgo);
    reviews.push(generateReview(i, daysAgo));
  }
  
  reviews.sort((a, b) => b.created_at.localeCompare(a.created_at));
  
  return reviews;
}

console.log('\n🔄 Generating reviews...\n');
const reviews = generateReviews(10000);

const outputPath = path.join(__dirname, '../data/review.json');
fs.writeFileSync(outputPath, JSON.stringify(reviews, null, 2));

console.log(`✅ Generated ${reviews.length} reviews`);
console.log(`📁 Saved to: ${outputPath}`);
console.log(`📊 Date range: ${reviews[reviews.length - 1].created_at} to ${reviews[0].created_at}`);
console.log(`⭐ Average rating: ${(reviews.reduce((sum, r) => sum + r.overall_rating, 0) / reviews.length).toFixed(2)}`);
console.log(`🏢 Agencies: ${agencies.length}`);
console.log(`📋 Services: ${services.length}`);

// Thống kê phân bố
const agencyCount = {};
reviews.forEach(r => {
  agencyCount[r.agency_name] = (agencyCount[r.agency_name] || 0) + 1;
});
console.log(`\n📈 Top 5 agencies by review count:`);
Object.entries(agencyCount)
  .sort((a, b) => b[1] - a[1])
  .slice(0, 5)
  .forEach(([name, count]) => {
    console.log(`   ${name}: ${count} reviews`);
  });

// Thống kê theo tỉnh
const provinceCount = {};
reviews.forEach(r => {
  provinceCount[r.province] = (provinceCount[r.province] || 0) + 1;
});
console.log(`\n🗺️  Reviews by Province:`);
Object.entries(provinceCount)
  .sort((a, b) => b[1] - a[1])
  .forEach(([name, count]) => {
    console.log(`   ${name}: ${count} reviews`);
  });

console.log('\n');
