import json
from pathlib import Path
from datetime import datetime
from models.user import FileStorage


class ServiceCategory:
    """ServiceCategory model - file-based storage"""
    
    def __init__(self, data):
        self.id = data.get('id', str(int(datetime.now().timestamp() * 1000)))
        self.name = data.get('name')
        self.nameEn = data.get('nameEn', data.get('name', ''))
        self.code = data.get('code')
        self.description = data.get('description', '')
        self.icon = data.get('icon', 'building')
        self.createdAt = data.get('createdAt', datetime.now().isoformat())
        self.updatedAt = data.get('updatedAt', datetime.now().isoformat())
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'nameEn': self.nameEn,
            'code': self.code,
            'description': self.description,
            'icon': self.icon,
            'createdAt': self.createdAt,
            'updatedAt': self.updatedAt
        }
    
    @staticmethod
    def find_all():
        """Find all categories"""
        return FileStorage.read_json('service_categories.json')
    
    @staticmethod
    def find_by_id(category_id):
        """Find category by ID"""
        categories = FileStorage.read_json('service_categories.json')
        for c in categories:
            if c['id'] == category_id:
                return c
        return None
    
    @staticmethod
    def find_by_code(code):
        """Find category by code"""
        categories = FileStorage.read_json('service_categories.json')
        for c in categories:
            if c.get('code') == code:
                return c
        return None
    
    @staticmethod
    def create(data):
        """Create new category"""
        categories = FileStorage.read_json('service_categories.json')
        
        # Check if code exists
        if any(c.get('code') == data.get('code') for c in categories):
            raise ValueError('Category code already exists')
        
        category = ServiceCategory(data)
        categories.append(category.to_dict())
        FileStorage.write_json('service_categories.json', categories)
        
        return category.to_dict()
