from models.service_category import ServiceCategory
from models.public_service import PublicService

categories = [
    { 'name': 'Hộ tịch', 'nameEn': 'Civil Status', 'code': 'civil', 'icon': 'file-text', 'description': 'Dịch vụ hộ tịch, đăng ký khai sinh, kết hôn, ly hôn' },
    { 'name': 'Đất đai', 'nameEn': 'Land', 'code': 'land', 'icon': 'map', 'description': 'Dịch vụ về đất đai, cấp giấy chứng nhận quyền sử dụng đất' },
    { 'name': 'Tư pháp', 'nameEn': 'Justice', 'code': 'justice', 'icon': 'scale', 'description': 'Dịch vụ tư pháp, công chứng, chứng thực' },
    { 'name': 'Môi trường', 'nameEn': 'Environment', 'code': 'environment', 'icon': 'leaf', 'description': 'Dịch vụ về môi trường, xử lý chất thải' },
    { 'name': 'Y tế', 'nameEn': 'Health', 'code': 'health', 'icon': 'heart', 'description': 'Dịch vụ y tế, cấp giấy chứng nhận sức khỏe' },
    { 'name': 'Giáo dục', 'nameEn': 'Education', 'code': 'education', 'icon': 'book', 'description': 'Dịch vụ giáo dục, cấp bằng, chứng chỉ' },
    { 'name': 'Thuế', 'nameEn': 'Tax', 'code': 'tax', 'icon': 'dollar-sign', 'description': 'Dịch vụ thuế, kê khai thuế' },
    { 'name': 'Lao động', 'nameEn': 'Labor', 'code': 'labor', 'icon': 'briefcase', 'description': 'Dịch vụ lao động, bảo hiểm xã hội' },
    { 'name': 'Xây dựng', 'nameEn': 'Construction', 'code': 'construction', 'icon': 'hammer', 'description': 'Dịch vụ xây dựng, cấp phép xây dựng' },
    { 'name': 'Kinh doanh', 'nameEn': 'Business', 'code': 'business', 'icon': 'store', 'description': 'Dịch vụ đăng ký kinh doanh, giấy phép kinh doanh' }
]

services = [
  {
    'name': 'UBND Quận Hoàn Kiếm',
    'description': 'Ủy ban nhân dân Quận Hoàn Kiếm',
    'categoryId': 'civil',
    'address': '12 Lý Thái Tổ, Hoàn Kiếm, Hà Nội',
    'latitude': 21.0285,
    'longitude': 105.8542,
    'phone': '024.3825.4321',
    'email': 'ubnd@hoankiem.hanoi.gov.vn',
    'level': 'district',
    'services': ['Hộ tịch', 'Đất đai', 'Tư pháp'],
    'rating': 4.5,
    'status': 'available',
    'workingHours': {
      'monday': '7:30-17:30', 'tuesday': '7:30-17:30', 'wednesday': '7:30-17:30',
      'thursday': '7:30-17:30', 'friday': '7:30-17:30', 'saturday': '7:30-12:00', 'sunday': 'Closed'
    }
  },
  {
    'name': 'UBND Quận Ba Đình',
    'description': 'Ủy ban nhân dân Quận Ba Đình',
    'categoryId': 'civil',
    'address': '61 Điện Biên Phủ, Ba Đình, Hà Nội',
    'latitude': 21.0333,
    'longitude': 105.8342,
    'phone': '024.3734.5678',
    'email': 'ubnd@badinh.hanoi.gov.vn',
    'level': 'district',
    'services': ['Hộ tịch', 'Y tế', 'Giáo dục'],
    'rating': 4.3,
    'status': 'normal',
    'workingHours': { 'monday': '7:30-17:00', 'tuesday': '7:30-17:00', 'wednesday': '7:30-17:00', 'thursday': '7:30-17:00', 'friday': '7:30-17:00', 'saturday': '7:30-12:00', 'sunday': 'Closed' }
  },
  {
    'name': 'Sở Tài nguyên và Môi trường Hà Nội',
    'description': 'Sở Tài nguyên và Môi trường thành phố Hà Nội',
    'categoryId': 'land',
    'address': '83A Lý Thường Kiệt, Hoàn Kiếm, Hà Nội',
    'latitude': 21.0245,
    'longitude': 105.8412,
    'phone': '024.3826.1234',
    'email': 'stnmt@hanoi.gov.vn',
    'level': 'province',
    'services': ['Đất đai', 'Môi trường', 'Xây dựng'],
    'rating': 4.2,
    'status': 'busy',
    'workingHours': { 'monday': '7:30-17:30', 'tuesday': '7:30-17:30', 'wednesday': '7:30-17:30', 'thursday': '7:30-17:30', 'friday': '7:30-17:30', 'saturday': '7:30-12:00', 'sunday': 'Closed' }
  }
]


def seed_data():
    print('🌱 Starting to seed data...')

    # Seed categories
    print('📁 Seeding categories...')
    for cat in categories:
        existing = ServiceCategory.find_by_code(cat['code'])
        if not existing:
            ServiceCategory.create(cat)
            print(f"  ✓ Created category: {cat['name']}")
        else:
            print(f"  - Category already exists: {cat['name']}")

    # Map category codes to IDs
    all_cats = ServiceCategory.find_all()
    code_map = {c['code']: c['id'] for c in all_cats}

    print('🏢 Seeding public services...')
    for s in services:
        category_code = s['categoryId']
        category_id = code_map.get(category_code)
        if not category_id:
            print(f"  ⚠ Category not found for {s['name']}: {category_code}")
            continue

        service_payload = dict(s)
        service_payload['categoryId'] = category_id

        existing = PublicService.find_all()
        duplicate = next((x for x in existing if x.get('name') == service_payload.get('name') and x.get('address') == service_payload.get('address')), None)
        if not duplicate:
            PublicService.create(service_payload)
            print(f"  ✓ Created service: {service_payload.get('name')}")
        else:
            print(f"  - Service already exists: {service_payload.get('name')}")

    print('✅ Seeding completed!')


if __name__ == '__main__':
    seed_data()
