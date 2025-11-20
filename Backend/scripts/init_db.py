"""
Initialize PostgreSQL database tables from models
"""
import os
import sys

# Add Backend to path so we can import models
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.db import db, init_db, test_connection
from server import app


def main():
    """Initialize database"""
    print('📁 Initializing PostgreSQL database...')
    
    try:
        init_db(app)
        print('✅ Database initialized successfully')
        
        # Test connection
        if test_connection():
            print('✅ Database connection verified')
        else:
            print('⚠️  Could not verify database connection')
    except Exception as e:
        print(f'❌ Error initializing database: {e}')
        return False
    
    return True


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
