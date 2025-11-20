from flask import Blueprint, request, jsonify
from models.public_service import PublicService
from models.service_category import ServiceCategory
from services.distance import find_nearby, calculate_distance

services_bp = Blueprint('services', __name__, url_prefix='/api/services')


@services_bp.route('/nearby', methods=['GET'])
def get_nearby_services():
    """Get nearby public services"""
    try:
        lat = request.args.get('lat')
        lng = request.args.get('lng')
        radius = request.args.get('radius', 10)
        category = request.args.get('category')
        level = request.args.get('level')
        limit = request.args.get('limit', 20)
        
        if not lat or not lng:
            return jsonify({
                'success': False,
                'message': 'Latitude và longitude là bắt buộc'
            }), 400
        
        try:
            user_lat = float(lat)
            user_lng = float(lng)
            radius_km = float(radius)
            limit_num = int(limit)
        except:
            return jsonify({
                'success': False,
                'message': 'Latitude và longitude không hợp lệ'
            }), 400
        
        # Get all services
        services = PublicService.find_all()
        
        # Filter by category
        if category:
            services = [s for s in services if s.get('categoryId') == category]
        
        # Filter by level
        if level:
            services = [s for s in services if s.get('level') == level]
        
        # Find nearby services
        nearby = find_nearby(services, user_lat, user_lng, radius_km)
        nearby = nearby[:limit_num]
        
        return jsonify({
            'success': True,
            'data': {
                'services': nearby,
                'total': len(nearby),
                'userLocation': {
                    'latitude': user_lat,
                    'longitude': user_lng
                },
                'radius': radius_km
            }
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Lỗi khi tìm kiếm dịch vụ gần đây'
        }), 500


@services_bp.route('/search', methods=['GET'])
def search_services():
    """Search public services"""
    try:
        q = request.args.get('q', '')
        category = request.args.get('category')
        level = request.args.get('level')
        province = request.args.get('province')
        district = request.args.get('district')
        lat = request.args.get('lat')
        lng = request.args.get('lng')
        limit = request.args.get('limit', 50)
        
        # Search services
        services = PublicService.search(q, category)
        
        # Filter by level
        if level:
            services = [s for s in services if s.get('level') == level]
        
        # Filter by province
        if province:
            services = [s for s in services if province.lower() in s.get('address', '').lower()]
        
        # Filter by district
        if district:
            services = [s for s in services if district.lower() in s.get('address', '').lower()]
        
        # Calculate distances if user location provided
        if lat and lng:
            try:
                user_lat = float(lat)
                user_lng = float(lng)
                nearby = find_nearby(services, user_lat, user_lng, 100)
                services = nearby
            except:
                pass
        
        # Sort by distance if available, otherwise by name
        services.sort(key=lambda s: (
            s.get('distance', float('inf')),
            s.get('name', '')
        ))
        
        limit_num = int(limit)
        services = services[:limit_num]
        
        return jsonify({
            'success': True,
            'data': {
                'services': services,
                'total': len(services),
                'query': q,
                'filters': {
                    'category': category,
                    'level': level,
                    'province': province,
                    'district': district
                }
            }
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Lỗi khi tìm kiếm dịch vụ'
        }), 500


@services_bp.route('/<id>', methods=['GET'])
def get_service(id):
    """Get service details"""
    try:
        service = PublicService.find_by_id(id)
        
        if not service:
            return jsonify({
                'success': False,
                'message': 'Không tìm thấy dịch vụ'
            }), 404
        
        # Get category info
        category = None
        if service.get('categoryId'):
            category = ServiceCategory.find_by_id(service.get('categoryId'))
        
        # Calculate distance if user location provided
        lat = request.args.get('lat')
        lng = request.args.get('lng')
        if lat and lng:
            try:
                user_lat = float(lat)
                user_lng = float(lng)
                service['distance'] = calculate_distance(
                    user_lat,
                    user_lng,
                    service.get('latitude', 0),
                    service.get('longitude', 0)
                )
            except:
                pass
        
        return jsonify({
            'success': True,
            'data': {
                'service': {
                    **service,
                    'category': category
                }
            }
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Lỗi khi lấy thông tin dịch vụ'
        }), 500


@services_bp.route('/', methods=['GET'])
def get_all_services():
    """Get all services with filters"""
    try:
        category = request.args.get('category')
        level = request.args.get('level')
        province = request.args.get('province')
        lat = request.args.get('lat')
        lng = request.args.get('lng')
        limit = request.args.get('limit', 100)
        
        services = PublicService.find_all()
        
        # Apply filters
        if category:
            services = [s for s in services if s.get('categoryId') == category]
        
        if level:
            services = [s for s in services if s.get('level') == level]
        
        if province:
            services = [s for s in services if province.lower() in s.get('address', '').lower()]
        
        # Calculate distances if user location provided
        if lat and lng:
            try:
                user_lat = float(lat)
                user_lng = float(lng)
                nearby = find_nearby(services, user_lat, user_lng, 100)
                services = nearby
            except:
                pass
        
        limit_num = int(limit)
        services = services[:limit_num]
        
        return jsonify({
            'success': True,
            'data': {
                'services': services,
                'total': len(services)
            }
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Lỗi khi lấy danh sách dịch vụ'
        }), 500


@services_bp.route('/categories/list', methods=['GET'])
def get_categories():
    """Get all service categories"""
    try:
        categories = ServiceCategory.find_all()
        
        return jsonify({
            'success': True,
            'data': {
                'categories': categories
            }
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Lỗi khi lấy danh mục dịch vụ'
        }), 500


@services_bp.route('/popular', methods=['GET'])
def get_popular_services():
    """Get popular services by level"""
    try:
        level = request.args.get('level')
        limit = request.args.get('limit', 10)
        
        services = PublicService.find_all()
        
        # Filter by level
        if level:
            services = [s for s in services if s.get('level') == level]
        
        # Sort by rating and status
        status_order = {'available': 0, 'normal': 1, 'busy': 2}
        services.sort(key=lambda s: (
            -s.get('rating', 0),
            status_order.get(s.get('status', 'normal'), 1)
        ))
        
        limit_num = int(limit)
        popular = services[:limit_num]
        
        return jsonify({
            'success': True,
            'data': {
                'services': popular,
                'level': level or 'all'
            }
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Lỗi khi lấy dịch vụ phổ biến'
        }), 500
