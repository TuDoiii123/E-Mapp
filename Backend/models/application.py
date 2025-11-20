import json
from pathlib import Path
from datetime import datetime
from models.user import FileStorage


class Application:
    """Application model - file-based storage"""
    
    def __init__(self, data):
        self.id = data.get('id', str(int(datetime.now().timestamp() * 1000)))
        self.applicantId = data.get('applicantId')  # user id (cccd id)
        self.serviceId = data.get('serviceId')  # which public service / service type
        self.data = data.get('data', {})  # form fields
        self.documents = data.get('documents', [])  # document ids
        self.currentStatus = data.get('currentStatus', 'submitted')
        self.createdAt = data.get('createdAt', datetime.now().isoformat())
        self.updatedAt = data.get('updatedAt', datetime.now().isoformat())
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'applicantId': self.applicantId,
            'serviceId': self.serviceId,
            'data': self.data,
            'documents': self.documents,
            'currentStatus': self.currentStatus,
            'createdAt': self.createdAt,
            'updatedAt': self.updatedAt
        }
    
    @staticmethod
    def create(app_data):
        """Create new application"""
        from models.status_tracking import StatusTracking
        
        all_apps = FileStorage.read_json('applications.json')
        app = Application(app_data)
        all_apps.append(app.to_dict())
        FileStorage.write_json('applications.json', all_apps)
        
        # Create initial status tracking
        StatusTracking.create({
            'applicationId': app.id,
            'status': app.currentStatus,
            'note': 'Nộp hồ sơ',
            'by': app.applicantId
        })
        
        return app.to_dict()
    
    @staticmethod
    def find_by_id(app_id):
        """Find application by ID"""
        all_apps = FileStorage.read_json('applications.json')
        for app in all_apps:
            if app['id'] == app_id:
                return app
        return None
    
    @staticmethod
    def update(app_id, updates):
        """Update application"""
        all_apps = FileStorage.read_json('applications.json')
        
        for i, app in enumerate(all_apps):
            if app['id'] == app_id:
                all_apps[i].update(updates)
                all_apps[i]['updatedAt'] = datetime.now().isoformat()
                FileStorage.write_json('applications.json', all_apps)
                return all_apps[i]
        
        raise ValueError('Application not found')
    
    @staticmethod
    def find_all_by_applicant(applicant_id):
        """Find all applications by applicant ID"""
        all_apps = FileStorage.read_json('applications.json')
        return [app for app in all_apps if app['applicantId'] == applicant_id]
    
    def attach_document(self, doc_id):
        """Attach document to application"""
        if 'documents' not in self.__dict__:
            self.documents = []
        self.documents.append(doc_id)
        Application.update(self.id, {'documents': self.documents})
        return self
    
    def get_documents(self):
        """Get all documents for this application"""
        from models.document import Document
        
        docs = []
        for doc_id in self.documents:
            doc = Document.find_by_id(doc_id)
            if doc:
                docs.append(doc)
        return docs
    
    def get_status_history(self):
        """Get status history for this application"""
        from models.status_tracking import StatusTracking
        
        return StatusTracking.find_by_application_id(self.id)

    # Static helper wrappers expected by routes (operate on dicts)
    @staticmethod
    def attach_document(app_id, doc):
        """Attach a document (dict) to an application by id"""
        app = Application.find_by_id(app_id)
        if not app:
            raise ValueError('Application not found')

        doc_id = doc.get('id') if isinstance(doc, dict) else getattr(doc, 'id', None)
        if not doc_id:
            raise ValueError('Invalid document')

        docs = app.get('documents', [])
        docs.append(doc_id)
        Application.update(app_id, {'documents': docs})
        # return updated application dict
        return Application.find_by_id(app_id)

    @staticmethod
    def get_documents(app_id):
        from models.document import Document
        docs = Document.find_by_application_id(app_id)
        return docs

    @staticmethod
    def get_status_history(app_id):
        from models.status_tracking import StatusTracking
        return StatusTracking.find_by_application_id(app_id)
