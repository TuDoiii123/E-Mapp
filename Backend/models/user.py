import json
from pathlib import Path
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


# Try to detect SQLAlchemy DB from models.db
try:
    from models.db import db
    from sqlalchemy import text
    HAS_DB = True
except Exception:
    db = None
    text = None
    HAS_DB = False


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
    """User model - file-based storage with optional Postgres backing"""
    
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
        """Find user by CCCD. Use DB if available, otherwise file storage."""
        if HAS_DB and db is not None:
            try:
                res = db.session.execute(
                    text("SELECT * FROM users WHERE cccd_number = :cccd LIMIT 1"),
                    {'cccd': cccd_number}
                ).mappings().first()
                if res:
                    row = dict(res)
                    # map DB columns to expected keys
                    return {
                        'id': row.get('id'),
                        'cccdNumber': row.get('cccd_number'),
                        'fullName': row.get('full_name'),
                        'dateOfBirth': row.get('date_of_birth'),
                        'phone': row.get('phone'),
                        'email': row.get('email'),
                        'password': row.get('password'),
                        'role': row.get('role'),
                        'isVNeIDVerified': row.get('is_vneid_verified'),
                        'vneidId': row.get('vneid_id'),
                        'createdAt': row.get('created_at'),
                        'updatedAt': row.get('updated_at')
                    }
            except Exception:
                pass

        users = FileStorage.read_json('users.json')
        for u in users:
            if u.get('cccdNumber') == cccd_number:
                return u
        return None
    
    @staticmethod
    def find_by_id(user_id):
        """Find user by ID. Use DB if available, otherwise file storage."""
        if HAS_DB and db is not None:
            try:
                res = db.session.execute(
                    text("SELECT * FROM users WHERE id = :id LIMIT 1"),
                    {'id': user_id}
                ).mappings().first()
                if res:
                    row = dict(res)
                    # sanitize
                    row.pop('password', None)
                    return {
                        'id': row.get('id'),
                        'cccdNumber': row.get('cccd_number'),
                        'fullName': row.get('full_name'),
                        'dateOfBirth': row.get('date_of_birth'),
                        'phone': row.get('phone'),
                        'email': row.get('email'),
                        'role': row.get('role'),
                        'isVNeIDVerified': row.get('is_vneid_verified'),
                        'vneidId': row.get('vneid_id'),
                        'createdAt': row.get('created_at'),
                        'updatedAt': row.get('updated_at')
                    }
            except Exception:
                pass

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
        """Find user by email. Use DB if available, otherwise file storage."""
        if HAS_DB and db is not None:
            try:
                res = db.session.execute(
                    text("SELECT * FROM users WHERE email = :email LIMIT 1"),
                    {'email': email}
                ).mappings().first()
                if res:
                    return dict(res)
            except Exception:
                pass

        users = FileStorage.read_json('users.json')
        for u in users:
            if u.get('email') == email:
                return u
        return None
    
    @staticmethod
    def create(user_data):
        """Create new user. Writes to DB if available, otherwise file storage."""
        # Use DB if available
        if HAS_DB and db is not None:
            try:
                # check existing
                exists = db.session.execute(
                    text("SELECT id FROM users WHERE cccd_number = :cccd OR email = :email LIMIT 1"),
                    {'cccd': user_data.get('cccdNumber'), 'email': user_data.get('email')}
                ).first()
                if exists:
                    raise ValueError('CCCD hoặc Email đã được đăng ký')

                hashed = generate_password_hash(user_data.get('password', ''), method='pbkdf2:sha256')
                now = datetime.utcnow().isoformat()
                ins = db.session.execute(
                    text('''INSERT INTO users (id, cccd_number, full_name, date_of_birth, phone, email, password, role, is_vneid_verified, vneid_id, created_at, updated_at)
                                  VALUES (:id, :cccd, :full_name, :dob, :phone, :email, :password, :role, :is_vneid, :vneid_id, :created_at, :updated_at)'''),
                    {
                        'id': user_data.get('id', str(int(datetime.now().timestamp() * 1000))),
                        'cccd': user_data.get('cccdNumber'),
                        'full_name': user_data.get('fullName'),
                        'dob': user_data.get('dateOfBirth'),
                        'phone': user_data.get('phone'),
                        'email': user_data.get('email'),
                        'password': hashed,
                        'role': user_data.get('role', 'citizen'),
                        'is_vneid': bool(user_data.get('isVNeIDVerified', False)),
                        'vneid_id': user_data.get('vneidId'),
                        'created_at': now,
                        'updated_at': now
                    }
                )
                db.session.commit()
                return {
                    'id': user_data.get('id'),
                    'cccdNumber': user_data.get('cccdNumber'),
                    'fullName': user_data.get('fullName'),
                    'dateOfBirth': user_data.get('dateOfBirth'),
                    'phone': user_data.get('phone'),
                    'email': user_data.get('email'),
                    'role': user_data.get('role', 'citizen'),
                    'isVNeIDVerified': bool(user_data.get('isVNeIDVerified', False)),
                    'vneidId': user_data.get('vneidId'),
                    'createdAt': now,
                    'updatedAt': now
                }
            except ValueError:
                raise
            except Exception as e:
                # If DB is available but insert fails, surface the error
                # so caller (route) can decide. Do NOT silently fallback to file.
                print('DB user create failed:', e)
                raise

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
        # Try DB update
        if HAS_DB and db is not None:
            try:
                # build set clauses
                set_parts = []
                params = {'id': user_id}
                for k, v in updates.items():
                    col = k
                    # map camelCase to snake_case
                    if k == 'fullName':
                        col = 'full_name'
                    elif k == 'dateOfBirth':
                        col = 'date_of_birth'
                    elif k == 'isVNeIDVerified':
                        col = 'is_vneid_verified'
                    elif k == 'vneidId':
                        col = 'vneid_id'
                    params[col] = v
                    set_parts.append(f"{col} = :{col}")

                if set_parts:
                    sql = text(f"UPDATE users SET {', '.join(set_parts)}, updated_at = :updated_at WHERE id = :id")
                    params['updated_at'] = datetime.utcnow().isoformat()
                    db.session.execute(sql, params)
                    db.session.commit()
                    return User.find_by_id(user_id)
            except Exception as e:
                print('DB user update failed, falling back to file:', e)

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
