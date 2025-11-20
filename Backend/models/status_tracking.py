import json
from pathlib import Path
from datetime import datetime
from models.user import FileStorage


class StatusTracking:
    """Status tracking model - file-based storage"""
    
    def __init__(self, data):
        self.id = data.get('id', str(int(datetime.now().timestamp() * 1000)))
        self.applicationId = data.get('applicationId')
        self.status = data.get('status')  # submitted, in_review, approved, rejected, more_info
        self.note = data.get('note')  # admin note or reason
        self.by = data.get('by')  # user/admin id
        self.createdAt = data.get('createdAt', datetime.now().isoformat())
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'applicationId': self.applicationId,
            'status': self.status,
            'note': self.note,
            'by': self.by,
            'createdAt': self.createdAt
        }
    
    @staticmethod
    def create(data):
        """Create new status tracking entry"""
        all_statuses = FileStorage.read_json('status_tracking.json')
        status = StatusTracking(data)
        all_statuses.append(status.to_dict())
        FileStorage.write_json('status_tracking.json', all_statuses)
        
        return status
    
    @staticmethod
    def find_by_application_id(app_id):
        """Find all status tracking entries for an application"""
        all_statuses = FileStorage.read_json('status_tracking.json')
        return [StatusTracking(s).to_dict() for s in all_statuses if s['applicationId'] == app_id]
