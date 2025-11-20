import json
from pathlib import Path
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class FileStorage:
    """Utility class for file-based JSON storage"""
    
    @staticmethod
    def get_data_dir():
        """Get or create data directory"""
        data_dir = Path(__file__).parent.parent / 'data'
        data_dir.mkdir(exist_ok=True)
        return data_dir
    
    @staticmethod
    def read_json(filename):
        """Read JSON file"""
        filepath = FileStorage.get_data_dir() / filename
        try:
            if filepath.exists():
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error reading {filename}: {e}")
        return []
    
    @staticmethod
    def write_json(filename, data):
        """Write JSON file"""
        filepath = FileStorage.get_data_dir() / filename
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error writing {filename}: {e}")
            return False


class User:
    """User model - file-based storage"""
    
    def __init__(self, data):
        self.id = data.get('id', str(int(datetime.now().timestamp() * 1000)))
        self.cccdNumber = data.get('cccdNumber')
        self.fullName = data.get('fullName')
        self.dateOfBirth = data.get('dateOfBirth')
        self.phone = data.get('phone')
        self.email = data.get('email')
        self.password = data.get('password')  # Hashed
        self.role = data.get('role', 'citizen')  # 'citizen' or 'admin'
        self.isVNeIDVerified = data.get('isVNeIDVerified', False)
        self.vneidId = data.get('vneidId')
        self.createdAt = data.get('createdAt', datetime.now().isoformat())
        self.updatedAt = data.get('updatedAt', datetime.now().isoformat())
    
    def to_dict(self, include_password=False):
        """Convert to dictionary"""
        result = {
            'id': self.id,
            'cccdNumber': self.cccdNumber,
            'fullName': self.fullName,
            'dateOfBirth': self.dateOfBirth,
            'phone': self.phone,
            'email': self.email,
            'role': self.role,
            'isVNeIDVerified': self.isVNeIDVerified,
            'vneidId': self.vneidId,
            'createdAt': self.createdAt,
            'updatedAt': self.updatedAt
        }
        if include_password:
            result['password'] = self.password
        return result
    
    @staticmethod
    def find_by_cccd(cccd_number):
        """Find user by CCCD"""
        users = FileStorage.read_json('users.json')
        for u in users:
            if u.get('cccdNumber') == cccd_number:
                return u
        return None
    
    @staticmethod
    def find_by_id(user_id):
        """Find user by ID"""
        users = FileStorage.read_json('users.json')
        for u in users:
            if u.get('id') == user_id:
                # Return sanitized dict without password
                u_copy = dict(u)
                if 'password' in u_copy:
                    del u_copy['password']
                return u_copy
        return None
    
    @staticmethod
    def find_by_email(email):
        """Find user by email"""
        users = FileStorage.read_json('users.json')
        for u in users:
            if u.get('email') == email:
                return u
        return None
    
    @staticmethod
    def create(user_data):
        """Create new user"""
        users = FileStorage.read_json('users.json')
        
        # Check if CCCD exists
        if any(u.get('cccdNumber') == user_data.get('cccdNumber') for u in users):
            raise ValueError('Số CCCD đã được đăng ký')
        
        # Check if email exists
        if any(u.get('email') == user_data.get('email') for u in users):
            raise ValueError('Email đã được đăng ký')
        
        # Hash password before storing
        hashed = generate_password_hash(user_data.get('password', ''), method='pbkdf2:sha256')
        user_data['password'] = hashed
        new_user = User(user_data)
        users.append(new_user.to_dict(include_password=True))
        FileStorage.write_json('users.json', users)
        
        # Return sanitized dict (without password)
        return new_user.to_dict()
    @staticmethod
    def update(user_id, updates):
        """Update user by id (static)"""
        users = FileStorage.read_json('users.json')

        for i, u in enumerate(users):
            if u['id'] == user_id:
                u.update(updates)
                u['updatedAt'] = datetime.now().isoformat()
                FileStorage.write_json('users.json', users)
                # Return sanitized dict
                u_copy = dict(u)
                if 'password' in u_copy:
                    del u_copy['password']
                return u_copy

        raise ValueError('User not found')

    @staticmethod
    def verify_password(raw_password, hashed_password):
        """Verify a plaintext password against stored hash"""
        if not hashed_password:
            return False
        try:
            return check_password_hash(hashed_password, raw_password)
        except Exception:
            return False
