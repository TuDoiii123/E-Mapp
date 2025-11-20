import json
from pathlib import Path
from datetime import datetime
from models.user import FileStorage


class PublicService:
    """PublicService model - file-based storage"""
    
    def __init__(self, data):
        self.id = data.get('id', str(int(datetime.now().timestamp() * 1000)))
        self.name = data.get('name')
        self.description = data.get('description', '')
        self.categoryId = data.get('categoryId')
        self.locationId = data.get('locationId')
        self.address = data.get('address')
        self.latitude = data.get('latitude')
        self.longitude = data.get('longitude')
        self.phone = data.get('phone', '')
        self.email = data.get('email', '')
        self.website = data.get('website', '')
        self.workingHours = data.get('workingHours', {
            'monday': '7:30-17:30',
            'tuesday': '7:30-17:30',
            'wednesday': '7:30-17:30',
            'thursday': '7:30-17:30',
            'friday': '7:30-17:30',
            'saturday': '7:30-12:00',
            'sunday': 'Closed'
        })
        self.services = data.get('services', [])
        self.level = data.get('level', 'district')  # ward, district, province
        self.rating = data.get('rating', 0)
        self.status = data.get('status', 'normal')  # normal, busy, available
        self.distance = data.get('distance')
        self.createdAt = data.get('createdAt', datetime.now().isoformat())
        self.updatedAt = data.get('updatedAt', datetime.now().isoformat())
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'categoryId': self.categoryId,
            'locationId': self.locationId,
            'address': self.address,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'phone': self.phone,
            'email': self.email,
            'website': self.website,
            'workingHours': self.workingHours,
            'services': self.services,
            'level': self.level,
            'rating': self.rating,
            'status': self.status,
            'distance': self.distance,
            'createdAt': self.createdAt,
            'updatedAt': self.updatedAt
        }
    
    @staticmethod
    def find_all():
        """Find all services"""
        return FileStorage.read_json('public_services.json')
    
    @staticmethod
    def find_by_id(service_id):
        """Find service by ID"""
        services = FileStorage.read_json('public_services.json')
        for s in services:
            if s['id'] == service_id:
                return s
        return None
    
    @staticmethod
    def find_by_category(category_id):
        """Find services by category ID"""
        services = FileStorage.read_json('public_services.json')
        return [s for s in services if s.get('categoryId') == category_id]
    
    @staticmethod
    def find_by_level(level):
        """Find services by level"""
        services = FileStorage.read_json('public_services.json')
        return [s for s in services if s.get('level') == level]
    
    @staticmethod
    def search(query, category_id=None):
        """Search services"""
        services = FileStorage.read_json('public_services.json')
        results = services
        
        if query:
            query_lower = query.lower()
            results = [s for s in results if
                      query_lower in s.get('name', '').lower() or
                      query_lower in s.get('description', '').lower() or
                      query_lower in s.get('address', '').lower() or
                      any(query_lower in svc.lower() for svc in s.get('services', []))]
        
        if category_id:
            results = [s for s in results if s.get('categoryId') == category_id]
        
        return [s for s in results]
    
    @staticmethod
    def create(data):
        """Create new service"""
        services = FileStorage.read_json('public_services.json')
        service = PublicService(data)
        services.append(service.to_dict())
        FileStorage.write_json('public_services.json', services)
        
        return service.to_dict()
    
    @staticmethod
    def update(service_id, updates):
        """Update service"""
        services = FileStorage.read_json('public_services.json')
        
        for i, s in enumerate(services):
            if s['id'] == service_id:
                services[i].update(updates)
                services[i]['updatedAt'] = datetime.now().isoformat()
                FileStorage.write_json('public_services.json', services)
                return services[i]
        
        raise ValueError('Service not found')
