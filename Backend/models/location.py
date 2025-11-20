import json
from pathlib import Path
from datetime import datetime
from models.user import FileStorage


class Location:
    """Location model - file-based storage"""
    
    def __init__(self, data):
        self.id = data.get('id', str(int(datetime.now().timestamp() * 1000)))
        self.name = data.get('name')
        self.address = data.get('address')
        self.ward = data.get('ward', '')  # Phường/Xã
        self.district = data.get('district', '')  # Quận/Huyện
        self.province = data.get('province', '')  # Tỉnh/Thành phố
        self.latitude = data.get('latitude')
        self.longitude = data.get('longitude')
        self.level = data.get('level', 'district')  # ward, district, province
        self.createdAt = data.get('createdAt', datetime.now().isoformat())
        self.updatedAt = data.get('updatedAt', datetime.now().isoformat())
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'ward': self.ward,
            'district': self.district,
            'province': self.province,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'level': self.level,
            'createdAt': self.createdAt,
            'updatedAt': self.updatedAt
        }
    
    @staticmethod
    def find_all():
        """Find all locations"""
        return FileStorage.read_json('locations.json')
    
    @staticmethod
    def find_by_id(location_id):
        """Find location by ID"""
        locations = FileStorage.read_json('locations.json')
        for l in locations:
            if l['id'] == location_id:
                return l
        return None
    
    @staticmethod
    def find_by_province(province):
        """Find locations by province"""
        locations = FileStorage.read_json('locations.json')
        return [l for l in locations if l.get('province') == province]
    
    @staticmethod
    def find_by_district(district):
        """Find locations by district"""
        locations = FileStorage.read_json('locations.json')
        return [l for l in locations if l.get('district') == district]
    
    @staticmethod
    def create(data):
        """Create new location"""
        locations = FileStorage.read_json('locations.json')
        location = Location(data)
        locations.append(location.to_dict())
        FileStorage.write_json('locations.json', locations)
        
        return location.to_dict()
