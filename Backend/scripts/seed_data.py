from logger import get_logger
log = get_logger("seed_data")

from models.service_category import ServiceCategory
from models.public_service import PublicService

categories = [
    { 'name': 'Hộ tịch',   'nameEn': 'Civil Status',   'code': 'civil',        'icon': 'file-text', 'description': 'Dịch vụ hộ tịch, đăng ký khai sinh, kết hôn, ly hôn' },
    { 'name': 'Đất đai',   'nameEn': 'Land',            'code': 'land',         'icon': 'map',       'description': 'Dịch vụ về đất đai, cấp giấy chứng nhận quyền sử dụng đất' },
    { 'name': 'Tư pháp',   'nameEn': 'Justice',         'code': 'justice',      'icon': 'scale',     'description': 'Dịch vụ tư pháp, công chứng, chứng thực' },
    { 'name': 'Môi trường','nameEn': 'Environment',     'code': 'environment',  'icon': 'leaf',      'description': 'Dịch vụ về môi trường, xử lý chất thải' },
    { 'name': 'Y tế',      'nameEn': 'Health',          'code': 'health',       'icon': 'heart',     'description': 'Dịch vụ y tế, cấp giấy chứng nhận sức khỏe' },
    { 'name': 'Giáo dục',  'nameEn': 'Education',       'code': 'education',    'icon': 'book',      'description': 'Dịch vụ giáo dục, cấp bằng, chứng chỉ' },
    { 'name': 'Thuế',      'nameEn': 'Tax',             'code': 'tax',          'icon': 'dollar-sign','description': 'Dịch vụ thuế, kê khai thuế' },
    { 'name': 'Lao động',  'nameEn': 'Labor',           'code': 'labor',        'icon': 'briefcase', 'description': 'Dịch vụ lao động, bảo hiểm xã hội' },
    { 'name': 'Xây dựng',  'nameEn': 'Construction',    'code': 'construction', 'icon': 'hammer',    'description': 'Dịch vụ xây dựng, cấp phép xây dựng' },
    { 'name': 'Kinh doanh','nameEn': 'Business',        'code': 'business',     'icon': 'store',     'description': 'Dịch vụ đăng ký kinh doanh, giấy phép kinh doanh' },
]

# ── Dữ liệu cơ quan hành chính tỉnh Thanh Hóa ────────────────────────────────
services = [
    {
        'name': 'UBND tỉnh Thanh Hóa',
        'description': 'Ủy ban nhân dân tỉnh Thanh Hóa — cơ quan hành chính cao nhất tỉnh',
        'categoryId': 'civil',
        'address': '45 Đại lộ Lê Lợi, phường Điện Biên, TP Thanh Hóa',
        'latitude': 19.8069,
        'longitude': 105.7852,
        'phone': '0237.3852.428',
        'email': 'ubnd@thanhhoa.gov.vn',
        'website': 'https://thanhhoa.gov.vn',
        'level': 'province',
        'services': ['Hộ tịch', 'Đất đai', 'Tư pháp', 'Xây dựng', 'Kinh doanh'],
        'rating': 4.4,
        'status': 'available',
        'workingHours': {
            'monday': '7:30-17:00', 'tuesday': '7:30-17:00', 'wednesday': '7:30-17:00',
            'thursday': '7:30-17:00', 'friday': '7:30-17:00', 'saturday': '7:30-11:30', 'sunday': 'Closed',
        },
    },
    {
        'name': 'UBND thành phố Thanh Hóa',
        'description': 'Ủy ban nhân dân thành phố Thanh Hóa',
        'categoryId': 'civil',
        'address': '16 Lê Hoàn, phường Lam Sơn, TP Thanh Hóa',
        'latitude': 19.8088,
        'longitude': 105.7767,
        'phone': '0237.3852.666',
        'email': 'ubnd@tpthanhhoa.gov.vn',
        'level': 'district',
        'services': ['Hộ tịch', 'Đất đai', 'Tư pháp'],
        'rating': 4.3,
        'status': 'normal',
        'workingHours': {
            'monday': '7:30-17:00', 'tuesday': '7:30-17:00', 'wednesday': '7:30-17:00',
            'thursday': '7:30-17:00', 'friday': '7:30-17:00', 'saturday': '7:30-11:30', 'sunday': 'Closed',
        },
    },
    {
        'name': 'Sở Tài nguyên và Môi trường Thanh Hóa',
        'description': 'Sở Tài nguyên và Môi trường tỉnh Thanh Hóa — quản lý đất đai, môi trường',
        'categoryId': 'land',
        'address': '33 Đại lộ Lê Lợi, TP Thanh Hóa',
        'latitude': 19.8102,
        'longitude': 105.7831,
        'phone': '0237.3752.262',
        'email': 'stnmt@thanhhoa.gov.vn',
        'level': 'province',
        'services': ['Đất đai', 'Môi trường'],
        'rating': 4.2,
        'status': 'normal',
        'workingHours': {
            'monday': '7:30-17:00', 'tuesday': '7:30-17:00', 'wednesday': '7:30-17:00',
            'thursday': '7:30-17:00', 'friday': '7:30-17:00', 'saturday': '7:30-11:30', 'sunday': 'Closed',
        },
    },
    {
        'name': 'Sở Tư pháp Thanh Hóa',
        'description': 'Sở Tư pháp tỉnh Thanh Hóa — công chứng, chứng thực, hộ tịch',
        'categoryId': 'justice',
        'address': '34 Đại lộ Lê Lợi, TP Thanh Hóa',
        'latitude': 19.8095,
        'longitude': 105.7840,
        'phone': '0237.3852.573',
        'email': 'stp@thanhhoa.gov.vn',
        'level': 'province',
        'services': ['Tư pháp', 'Hộ tịch'],
        'rating': 4.5,
        'status': 'available',
        'workingHours': {
            'monday': '7:30-17:00', 'tuesday': '7:30-17:00', 'wednesday': '7:30-17:00',
            'thursday': '7:30-17:00', 'friday': '7:30-17:00', 'saturday': '7:30-11:30', 'sunday': 'Closed',
        },
    },
    {
        'name': 'Trung tâm Phục vụ Hành chính công tỉnh Thanh Hóa',
        'description': 'Trung tâm giải quyết thủ tục hành chính một cửa tập trung',
        'categoryId': 'civil',
        'address': '25A Đại lộ Lê Lợi, phường Ba Đình, TP Thanh Hóa',
        'latitude': 19.8078,
        'longitude': 105.7858,
        'phone': '0237.3753.888',
        'email': 'trungtam@thanhhoa.gov.vn',
        'level': 'province',
        'services': ['Hộ tịch', 'Đất đai', 'Tư pháp', 'Xây dựng', 'Kinh doanh', 'Thuế', 'Lao động'],
        'rating': 4.6,
        'status': 'available',
        'workingHours': {
            'monday': '7:00-17:30', 'tuesday': '7:00-17:30', 'wednesday': '7:00-17:30',
            'thursday': '7:00-17:30', 'friday': '7:00-17:30', 'saturday': '7:30-12:00', 'sunday': 'Closed',
        },
    },
    {
        'name': 'UBND huyện Quảng Xương',
        'description': 'Ủy ban nhân dân huyện Quảng Xương, tỉnh Thanh Hóa',
        'categoryId': 'civil',
        'address': 'Thị trấn Quảng Xương, huyện Quảng Xương, Thanh Hóa',
        'latitude': 19.6756,
        'longitude': 105.8303,
        'phone': '0237.3871.001',
        'email': 'ubnd@quangxuong.thanhhoa.gov.vn',
        'level': 'district',
        'services': ['Hộ tịch', 'Đất đai', 'Xây dựng'],
        'rating': 4.1,
        'status': 'normal',
        'workingHours': {
            'monday': '7:30-17:00', 'tuesday': '7:30-17:00', 'wednesday': '7:30-17:00',
            'thursday': '7:30-17:00', 'friday': '7:30-17:00', 'saturday': '7:30-11:30', 'sunday': 'Closed',
        },
    },
    {
        'name': 'UBND thị xã Sầm Sơn',
        'description': 'Ủy ban nhân dân thị xã Sầm Sơn, tỉnh Thanh Hóa',
        'categoryId': 'civil',
        'address': 'Đường Trường Sơn, phường Trung Sơn, thị xã Sầm Sơn',
        'latitude': 19.7319,
        'longitude': 105.9032,
        'phone': '0237.3866.286',
        'email': 'ubnd@samson.thanhhoa.gov.vn',
        'level': 'district',
        'services': ['Hộ tịch', 'Đất đai', 'Kinh doanh'],
        'rating': 4.0,
        'status': 'normal',
        'workingHours': {
            'monday': '7:30-17:00', 'tuesday': '7:30-17:00', 'wednesday': '7:30-17:00',
            'thursday': '7:30-17:00', 'friday': '7:30-17:00', 'saturday': '7:30-11:30', 'sunday': 'Closed',
        },
    },
    {
        'name': 'Sở Lao động - Thương binh và Xã hội Thanh Hóa',
        'description': 'Quản lý lao động, việc làm, bảo hiểm xã hội tỉnh Thanh Hóa',
        'categoryId': 'labor',
        'address': '24 Hải Thượng Lãn Ông, TP Thanh Hóa',
        'latitude': 19.8055,
        'longitude': 105.7820,
        'phone': '0237.3852.197',
        'email': 'soldtbxh@thanhhoa.gov.vn',
        'level': 'province',
        'services': ['Lao động'],
        'rating': 4.2,
        'status': 'normal',
        'workingHours': {
            'monday': '7:30-17:00', 'tuesday': '7:30-17:00', 'wednesday': '7:30-17:00',
            'thursday': '7:30-17:00', 'friday': '7:30-17:00', 'saturday': 'Closed', 'sunday': 'Closed',
        },
    },
]


def seed_data():
    log.info('Starting to seed data...')

    # Seed categories
    log.info('Seeding categories...')
    for cat in categories:
        existing = ServiceCategory.find_by_code(cat['code'])
        if not existing:
            ServiceCategory.create(cat)
            log.info(f"  + Created: {cat['name']}")
        else:
            log.debug(f"  - Exists:  {cat['name']}")

    # Map category codes → IDs
    all_cats = ServiceCategory.find_all()
    code_map = {c['code']: c['id'] for c in all_cats}

    log.info('Seeding public services (Thanh Hoa)...')
    existing_services = PublicService.find_all()
    existing_names = {(x.get('name'), x.get('address')) for x in existing_services}

    for s in services:
        category_id = code_map.get(s['categoryId'])
        if not category_id:
            log.warning(f"  ! Category not found: {s['categoryId']}")
            continue
        payload = {**s, 'categoryId': category_id}
        if (payload['name'], payload['address']) not in existing_names:
            PublicService.create(payload)
            log.info(f"  + Created: {payload['name']}")
        else:
            log.debug(f"  - Exists:  {payload['name']}")

    # Seed chatbot config defaults
    log.info('Seeding chatbot config...')
    try:
        from models.chatbot_config import seed_defaults as seed_chatbot
        seed_chatbot()
        log.info('  + Chatbot config seeded')
    except Exception as e:
        log.warning(f'  ! Chatbot seed failed: {e}')

    log.info('Seeding completed.')


if __name__ == '__main__':
    seed_data()
