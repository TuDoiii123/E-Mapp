from flask import Blueprint, request, jsonify
from functools import wraps
import jwt
import json
from datetime import datetime, timedelta
import re
import os
from models.user import User
from services.vneid import verify_vneid

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

JWT_SECRET = os.getenv('JWT_SECRET', 'default-secret-key-change-in-production')
JWT_EXPIRES_IN = os.getenv('JWT_EXPIRES_IN', '7d')

if JWT_SECRET == 'default-secret-key-change-in-production':
    print('⚠️  WARNING: Using default JWT_SECRET. Please set JWT_SECRET in .env file for production!')


def generate_token(user):
    """Generate JWT token for user"""
    payload = {
        'userId': user.get('id'),
        'role': user.get('role'),
        'cccdNumber': user.get('cccdNumber')
    }
    
    # Parse expiration time
    expires_in = JWT_EXPIRES_IN
    if expires_in.endswith('d'):
        days = int(expires_in[:-1])
        exp = datetime.utcnow() + timedelta(days=days)
    else:
        exp = datetime.utcnow() + timedelta(hours=24)
    
    payload['exp'] = exp
    token = jwt.encode(payload, JWT_SECRET, algorithm='HS256')
    return token


def validate_register_input(data):
    """Validate registration input"""
    errors = []
    
    # Validate CCCD
    cccd = data.get('cccdNumber', '').strip()
    if not cccd:
        errors.append('Số CCCD là bắt buộc')
    elif len(cccd) != 12:
        errors.append('Số CCCD phải có 12 chữ số')
    elif not cccd.isdigit():
        errors.append('Số CCCD chỉ được chứa số')
    
    # Validate full name
    full_name = data.get('fullName', '').strip()
    if not full_name:
        errors.append('Họ và tên là bắt buộc')
    elif len(full_name) < 2:
        errors.append('Họ và tên phải có ít nhất 2 ký tự')
    
    # Validate date of birth
    if not data.get('dateOfBirth'):
        errors.append('Ngày sinh là bắt buộc')
    
    # Validate phone
    phone = data.get('phone', '').strip()
    if not phone:
        errors.append('Số điện thoại là bắt buộc')
    elif not re.match(r'^[0-9]{10,11}$', phone):
        errors.append('Số điện thoại không hợp lệ')
    
    # Validate email
    email = data.get('email', '').strip()
    if not email:
        errors.append('Email là bắt buộc')
    elif not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
        errors.append('Email không hợp lệ')
    
    # Validate password
    password = data.get('password', '')
    if not password:
        errors.append('Mật khẩu là bắt buộc')
    elif len(password) < 8:
        errors.append('Mật khẩu phải có ít nhất 8 ký tự')
    elif not re.search(r'[A-Z]', password):
        errors.append('Mật khẩu phải có ít nhất 1 chữ hoa')
    elif not re.search(r'[0-9]', password):
        errors.append('Mật khẩu phải có ít nhất 1 chữ số')
    elif not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append('Mật khẩu phải có ít nhất 1 ký tự đặc biệt')
    
    # Validate password confirmation
    confirm_password = data.get('confirmPassword', '')
    if password != confirm_password:
        errors.append('Mật khẩu xác nhận không khớp')
    
    # Validate OTP (optional)
    otp = data.get('otp')
    if otp and (len(str(otp)) != 6 or not str(otp).isdigit()):
        errors.append('Mã OTP phải có 6 chữ số')
    
    return errors


@auth_bp.route('/register', methods=['POST'])
def register():
    """Register new user"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': 'Dữ liệu không hợp lệ'
            }), 400
        
        # Validate input
        errors = validate_register_input(data)
        if errors:
            return jsonify({
                'success': False,
                'message': 'Dữ liệu không hợp lệ',
                'errors': errors
            }), 400
        
        cccd_number = data.get('cccdNumber').strip()
        full_name = data.get('fullName').strip()
        date_of_birth = data.get('dateOfBirth')
        phone = data.get('phone').strip()
        email = data.get('email').strip()
        password = data.get('password')
        use_vneid = data.get('useVNeID', False)
        otp = data.get('otp')
        
        # If using VNeID, verify it
        vneid_data = None
        if use_vneid:
            try:
                vneid_data = verify_vneid(cccd_number)
                if not vneid_data:
                    return jsonify({
                        'success': False,
                        'message': 'Xác thực VNeID thất bại'
                    }), 400
            except Exception as e:
                return jsonify({
                    'success': False,
                    'message': f'Lỗi xác thực VNeID: {str(e)}'
                }), 400
        else:
            # For demo, accept 123456 as valid OTP
            if otp != '123456':
                return jsonify({
                    'success': False,
                    'message': 'Mã OTP không đúng. Sử dụng 123456 cho demo.'
                }), 400
        
        # Create user
        user_data = {
            'cccdNumber': cccd_number,
            'fullName': full_name,
            'dateOfBirth': date_of_birth,
            'phone': phone,
            'email': email,
            'password': password,
            'role': 'citizen',
            'isVNeIDVerified': bool(vneid_data),
            'vneidId': vneid_data.get('id') if vneid_data else None
        }
        
        user = User.create(user_data)
        token = generate_token(user)
        
        return jsonify({
            'success': True,
            'message': 'Đăng ký thành công',
            'data': {
                'user': user,
                'token': token
            }
        }), 201
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e) or 'Đăng ký thất bại'
        }), 400


@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': 'Dữ liệu không hợp lệ'
            }), 400
        
        cccd_number = data.get('cccdNumber', '').strip()
        password = data.get('password', '')
        
        if not cccd_number:
            return jsonify({
                'success': False,
                'message': 'Số CCCD là bắt buộc'
            }), 400
        
        if not password:
            return jsonify({
                'success': False,
                'message': 'Mật khẩu là bắt buộc'
            }), 400
        
        # Find user
        user = User.find_by_cccd(cccd_number)
        if not user:
            return jsonify({
                'success': False,
                'message': 'Số CCCD hoặc mật khẩu không đúng'
            }), 401
        
        # Verify password
        if not User.verify_password(password, user.get('password')):
            return jsonify({
                'success': False,
                'message': 'Số CCCD hoặc mật khẩu không đúng'
            }), 401
        
        # Generate token
        token = generate_token(user)
        
        return jsonify({
            'success': True,
            'message': 'Đăng nhập thành công',
            'data': {
                'user': user,
                'token': token
            }
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Lỗi đăng nhập'
        }), 500


@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Logout user"""
    try:
        return jsonify({
            'success': True,
            'message': 'Đăng xuất thành công'
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Lỗi đăng xuất'
        }), 500


@auth_bp.route('/profile', methods=['GET'])
def get_profile():
    """Get current user profile"""
    try:
        # request.user_id is set by middleware; handle missing token gracefully
        user_id = getattr(request, 'user_id', None)
        if not user_id:
            return jsonify({'success': False, 'message': 'Chưa xác thực'}), 401

        user = User.find_by_id(user_id)
        if not user:
            return jsonify({
                'success': False,
                'message': 'Người dùng không tồn tại'
            }), 404
        
        return jsonify({
            'success': True,
            'data': {
                'user': user
            }
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Lỗi lấy thông tin người dùng'
        }), 500


@auth_bp.route('/profile', methods=['PUT'])
def update_profile():
    """Update user profile"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': 'Dữ liệu không hợp lệ'
            }), 400
        
        user_id = request.user_id  # Set by middleware
        user = User.find_by_id(user_id)
        
        if not user:
            return jsonify({
                'success': False,
                'message': 'Người dùng không tồn tại'
            }), 404
        
        # Prepare updates
        updates = {}
        
        if 'fullName' in data:
            full_name = data.get('fullName', '').strip()
            if len(full_name) < 2:
                return jsonify({
                    'success': False,
                    'message': 'Họ và tên phải có ít nhất 2 ký tự'
                }), 400
            updates['fullName'] = full_name
        
        if 'phone' in data:
            phone = data.get('phone', '').strip()
            if not re.match(r'^[0-9]{10,11}$', phone):
                return jsonify({
                    'success': False,
                    'message': 'Số điện thoại không hợp lệ'
                }), 400
            updates['phone'] = phone
        
        if 'email' in data:
            email = data.get('email', '').strip()
            if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
                return jsonify({
                    'success': False,
                    'message': 'Email không hợp lệ'
                }), 400
            updates['email'] = email
        
        if 'dateOfBirth' in data:
            updates['dateOfBirth'] = data.get('dateOfBirth')
        
        # Update user
        updated_user = User.update(user_id, updates)
        
        return jsonify({
            'success': True,
            'message': 'Cập nhật thông tin thành công',
            'data': {
                'user': updated_user
            }
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e) or 'Lỗi cập nhật thông tin'
        }), 500
