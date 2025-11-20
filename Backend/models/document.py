import json
from pathlib import Path
from datetime import datetime
from models.user import FileStorage


class Document:
    """Document model - file-based storage"""
    
    def __init__(self, data):
        self.id = data.get('id', str(int(datetime.now().timestamp() * 1000)))
        self.applicationId = data.get('applicationId')
        self.filename = data.get('filename')
        self.originalName = data.get('originalName')
        self.mimeType = data.get('mimeType')
        self.size = data.get('size')
        self.storagePath = data.get('storagePath')
        self.processedText = data.get('processedText')
        self.createdAt = data.get('createdAt', datetime.now().isoformat())
        self.updatedAt = data.get('updatedAt', datetime.now().isoformat())
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'applicationId': self.applicationId,
            'filename': self.filename,
            'originalName': self.originalName,
            'mimeType': self.mimeType,
            'size': self.size,
            'storagePath': self.storagePath,
            'processedText': self.processedText,
            'createdAt': self.createdAt,
            'updatedAt': self.updatedAt
        }
    
    @staticmethod
    def create(doc_data):
        """Create new document"""
        all_docs = FileStorage.read_json('documents.json')
        doc = Document(doc_data)
        all_docs.append(doc.to_dict())
        FileStorage.write_json('documents.json', all_docs)
        
        return doc.to_dict()
    
    @staticmethod
    def find_by_id(doc_id):
        """Find document by ID"""
        all_docs = FileStorage.read_json('documents.json')
        for doc in all_docs:
            if doc['id'] == doc_id:
                return doc
        return None
    
    @staticmethod
    def find_by_application_id(app_id):
        """Find all documents for an application"""
        all_docs = FileStorage.read_json('documents.json')
        return [doc for doc in all_docs if doc['applicationId'] == app_id]
    
    @staticmethod
    def update(doc_id, updates):
        """Update document"""
        all_docs = FileStorage.read_json('documents.json')
        
        for i, doc in enumerate(all_docs):
            if doc['id'] == doc_id:
                all_docs[i].update(updates)
                all_docs[i]['updatedAt'] = datetime.now().isoformat()
                FileStorage.write_json('documents.json', all_docs)
                return all_docs[i]
        
        raise ValueError('Document not found')
