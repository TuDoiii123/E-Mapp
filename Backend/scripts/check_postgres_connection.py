import os
import sys
from sqlalchemy import create_engine, text

# Ensure Backend folder is on path so we can import models.db
here = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(here)
backend_path = os.path.join(project_root)
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Try to import get_db_url from models.db if available
try:
    from models.db import get_db_url
    url = get_db_url()
except Exception:
    # Fall back to environment variables
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '5432')
    db_name = os.getenv('DB_NAME', 'postgres')
    db_user = os.getenv('DB_USER', 'postgres')
    db_password = os.getenv('DB_PASSWORD', '')
    url = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'

print('\n[check_postgres_connection] Using DB URL:')
print(url)

# Try to connect
try:
    engine = create_engine(url)
    with engine.connect() as conn:
        print('\n[check_postgres_connection] Connection successful. Running tests...')
        try:
            r = conn.execute(text('SELECT 1'))
            print('[check_postgres_connection] SELECT 1 ->', r.scalar())
        except Exception as e:
            print('[check_postgres_connection] Failed to run SELECT 1:', e)

        # Try to get sample rows from dichvucong_thanhhoa
        try:
            res = conn.execute(text('SELECT * FROM dichvucong_thanhhoa LIMIT 5'))
            rows = res.mappings().all()
            if not rows:
                print('[check_postgres_connection] Table `dichvucong_thanhhoa` returned no rows or does not exist.')
            else:
                print('[check_postgres_connection] Sample rows (up to 5):')
                for r in rows:
                    # Print keys and a short view
                    d = dict(r)
                    print(dict(list(d.items())[:10]))
        except Exception as e:
            print('[check_postgres_connection] Could not query `dichvucong_thanhhoa`:', e)
except ModuleNotFoundError as e:
    print('\n[check_postgres_connection] Missing dependency:', e)
    print('Install requirements: pip install sqlalchemy psycopg2-binary')
except Exception as e:
    print('\n[check_postgres_connection] Connection failed:', e)
    print('Check your .env or environment variables for DB_HOST/DB_PORT/DB_NAME/DB_USER/DB_PASSWORD')
