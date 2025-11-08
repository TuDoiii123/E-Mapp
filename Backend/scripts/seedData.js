const ServiceCategory = require('../models/ServiceCategory');
const PublicService = require('../models/PublicService');

// Seed categories
const categories = [
  { name: 'Hộ tịch', nameEn: 'Civil Status', code: 'civil', icon: 'file-text', description: 'Dịch vụ hộ tịch, đăng ký khai sinh, kết hôn, ly hôn' },
  { name: 'Đất đai', nameEn: 'Land', code: 'land', icon: 'map', description: 'Dịch vụ về đất đai, cấp giấy chứng nhận quyền sử dụng đất' },
  { name: 'Tư pháp', nameEn: 'Justice', code: 'justice', icon: 'scale', description: 'Dịch vụ tư pháp, công chứng, chứng thực' },
  { name: 'Môi trường', nameEn: 'Environment', code: 'environment', icon: 'leaf', description: 'Dịch vụ về môi trường, xử lý chất thải' },
  { name: 'Y tế', nameEn: 'Health', code: 'health', icon: 'heart', description: 'Dịch vụ y tế, cấp giấy chứng nhận sức khỏe' },
  { name: 'Giáo dục', nameEn: 'Education', code: 'education', icon: 'book', description: 'Dịch vụ giáo dục, cấp bằng, chứng chỉ' },
  { name: 'Thuế', nameEn: 'Tax', code: 'tax', icon: 'dollar-sign', description: 'Dịch vụ thuế, kê khai thuế' },
  { name: 'Lao động', nameEn: 'Labor', code: 'labor', icon: 'briefcase', description: 'Dịch vụ lao động, bảo hiểm xã hội' },
  { name: 'Xây dựng', nameEn: 'Construction', code: 'construction', icon: 'hammer', description: 'Dịch vụ xây dựng, cấp phép xây dựng' },
  { name: 'Kinh doanh', nameEn: 'Business', code: 'business', icon: 'store', description: 'Dịch vụ đăng ký kinh doanh, giấy phép kinh doanh' }
];

// Seed public services (Hà Nội)
const services = [
  {
    name: 'UBND Quận Hoàn Kiếm',
    description: 'Ủy ban nhân dân Quận Hoàn Kiếm',
    categoryId: 'civil',
    address: '12 Lý Thái Tổ, Hoàn Kiếm, Hà Nội',
    latitude: 21.0285,
    longitude: 105.8542,
    phone: '024.3825.4321',
    email: 'ubnd@hoankiem.hanoi.gov.vn',
    level: 'district',
    services: ['Hộ tịch', 'Đất đai', 'Tư pháp'],
    rating: 4.5,
    status: 'available',
    workingHours: {
      monday: '7:30-17:30',
      tuesday: '7:30-17:30',
      wednesday: '7:30-17:30',
      thursday: '7:30-17:30',
      friday: '7:30-17:30',
      saturday: '7:30-12:00',
      sunday: 'Closed'
    }
  },
  {
    name: 'UBND Quận Ba Đình',
    description: 'Ủy ban nhân dân Quận Ba Đình',
    categoryId: 'civil',
    address: '61 Điện Biên Phủ, Ba Đình, Hà Nội',
    latitude: 21.0333,
    longitude: 105.8342,
    phone: '024.3734.5678',
    email: 'ubnd@badinh.hanoi.gov.vn',
    level: 'district',
    services: ['Hộ tịch', 'Y tế', 'Giáo dục'],
    rating: 4.3,
    status: 'normal',
    workingHours: {
      monday: '7:30-17:00',
      tuesday: '7:30-17:00',
      wednesday: '7:30-17:00',
      thursday: '7:30-17:00',
      friday: '7:30-17:00',
      saturday: '7:30-12:00',
      sunday: 'Closed'
    }
  },
  {
    name: 'Sở Tài nguyên và Môi trường Hà Nội',
    description: 'Sở Tài nguyên và Môi trường thành phố Hà Nội',
    categoryId: 'land',
    address: '83A Lý Thường Kiệt, Hoàn Kiếm, Hà Nội',
    latitude: 21.0245,
    longitude: 105.8412,
    phone: '024.3826.1234',
    email: 'stnmt@hanoi.gov.vn',
    level: 'province',
    services: ['Đất đai', 'Môi trường', 'Xây dựng'],
    rating: 4.2,
    status: 'busy',
    workingHours: {
      monday: '7:30-17:30',
      tuesday: '7:30-17:30',
      wednesday: '7:30-17:30',
      thursday: '7:30-17:30',
      friday: '7:30-17:30',
      saturday: '7:30-12:00',
      sunday: 'Closed'
    }
  },
  {
    name: 'Sở Lao động TB&XH Hà Nội',
    description: 'Sở Lao động - Thương binh và Xã hội Hà Nội',
    categoryId: 'labor',
    address: '2 Đinh Lễ, Hoàn Kiếm, Hà Nội',
    latitude: 21.0265,
    longitude: 105.8482,
    phone: '024.3824.9876',
    email: 'sldtbxh@hanoi.gov.vn',
    level: 'province',
    services: ['Lao động', 'Y tế', 'Giáo dục'],
    rating: 4.1,
    status: 'normal',
    workingHours: {
      monday: '7:30-17:00',
      tuesday: '7:30-17:00',
      wednesday: '7:30-17:00',
      thursday: '7:30-17:00',
      friday: '7:30-17:00',
      saturday: '7:30-12:00',
      sunday: 'Closed'
    }
  },
  {
    name: 'Cục Thuế Hà Nội',
    description: 'Cục Thuế thành phố Hà Nội',
    categoryId: 'tax',
    address: '18 Phạm Ngũ Lão, Hoàn Kiếm, Hà Nội',
    latitude: 21.0225,
    longitude: 105.8522,
    phone: '024.3971.5555',
    email: 'cucthue@hanoi.gov.vn',
    level: 'province',
    services: ['Thuế', 'Kinh doanh'],
    rating: 4.0,
    status: 'available',
    workingHours: {
      monday: '7:30-17:30',
      tuesday: '7:30-17:30',
      wednesday: '7:30-17:30',
      thursday: '7:30-17:30',
      friday: '7:30-17:30',
      saturday: '7:30-12:00',
      sunday: 'Closed'
    }
  },
  {
    name: 'Phòng Tư pháp Quận Hoàn Kiếm',
    description: 'Phòng Tư pháp Quận Hoàn Kiếm',
    categoryId: 'justice',
    address: '8 Hàng Trống, Hoàn Kiếm, Hà Nội',
    latitude: 21.0305,
    longitude: 105.8502,
    phone: '024.3828.7890',
    email: 'phongtuphap@hoankiem.hanoi.gov.vn',
    level: 'district',
    services: ['Tư pháp', 'Công chứng', 'Hộ tịch'],
    rating: 4.4,
    status: 'available',
    workingHours: {
      monday: '7:30-17:30',
      tuesday: '7:30-17:30',
      wednesday: '7:30-17:30',
      thursday: '7:30-17:30',
      friday: '7:30-17:30',
      saturday: '7:30-12:00',
      sunday: 'Closed'
    }
  },
  {
    name: 'UBND Phường Tràng Tiền',
    description: 'Ủy ban nhân dân Phường Tràng Tiền',
    categoryId: 'civil',
    address: '15 Tràng Tiền, Hoàn Kiếm, Hà Nội',
    latitude: 21.0255,
    longitude: 105.8562,
    phone: '024.3829.1234',
    email: 'ubnd@trangtien.hanoi.gov.vn',
    level: 'ward',
    services: ['Hộ tịch', 'Công chứng'],
    rating: 4.6,
    status: 'available',
    workingHours: {
      monday: '7:30-17:30',
      tuesday: '7:30-17:30',
      wednesday: '7:30-17:30',
      thursday: '7:30-17:30',
      friday: '7:30-17:30',
      saturday: '7:30-12:00',
      sunday: 'Closed'
    }
  },
  {
    name: 'Sở Y tế Hà Nội',
    description: 'Sở Y tế thành phố Hà Nội',
    categoryId: 'health',
    address: '23 Quang Trung, Hoàn Kiếm, Hà Nội',
    latitude: 21.0275,
    longitude: 105.8442,
    phone: '024.3823.4567',
    email: 'soyte@hanoi.gov.vn',
    level: 'province',
    services: ['Y tế', 'Cấp giấy chứng nhận sức khỏe'],
    rating: 4.3,
    status: 'normal',
    workingHours: {
      monday: '7:30-17:30',
      tuesday: '7:30-17:30',
      wednesday: '7:30-17:30',
      thursday: '7:30-17:30',
      friday: '7:30-17:30',
      saturday: '7:30-12:00',
      sunday: 'Closed'
    }
  }
];

async function seedData() {
  try {
    console.log('🌱 Starting to seed data...');

    // Seed categories
    console.log('📁 Seeding categories...');
    for (const catData of categories) {
      try {
        const existing = await ServiceCategory.findByCode(catData.code);
        if (!existing) {
          await ServiceCategory.create(catData);
          console.log(`  ✓ Created category: ${catData.name}`);
        } else {
          console.log(`  - Category already exists: ${catData.name}`);
        }
      } catch (error) {
        console.error(`  ✗ Error creating category ${catData.name}:`, error.message);
      }
    }

    // Get all categories to map IDs
    const allCategories = await ServiceCategory.findAll();
    const categoryMap = {};
    allCategories.forEach(cat => {
      categoryMap[cat.code] = cat.id;
    });

    // Seed services
    console.log('🏢 Seeding public services...');
    for (const serviceData of services) {
      try {
        // Map category code to ID
        const categoryId = categoryMap[serviceData.categoryId];
        if (!categoryId) {
          console.warn(`  ⚠ Category not found: ${serviceData.categoryId}`);
          continue;
        }

        const serviceToCreate = {
          ...serviceData,
          categoryId: categoryId
        };

        // Check if service already exists (by name and address)
        const existing = await PublicService.findAll();
        const duplicate = existing.find(s => 
          s.name === serviceToCreate.name && s.address === serviceToCreate.address
        );

        if (!duplicate) {
          await PublicService.create(serviceToCreate);
          console.log(`  ✓ Created service: ${serviceToCreate.name}`);
        } else {
          console.log(`  - Service already exists: ${serviceToCreate.name}`);
        }
      } catch (error) {
        console.error(`  ✗ Error creating service ${serviceData.name}:`, error.message);
      }
    }

    console.log('✅ Seeding completed!');
  } catch (error) {
    console.error('❌ Error seeding data:', error);
    throw error;
  }
}

// Run if called directly
if (require.main === module) {
  seedData()
    .then(() => {
      console.log('Done!');
      process.exit(0);
    })
    .catch(error => {
      console.error('Failed:', error);
      process.exit(1);
    });
}

module.exports = { seedData, categories, services };

