import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

from models.db import db
from flask import Flask

app = Flask(__name__)
db_url = 'postgresql://{}:{}@{}:{}/{}'.format(
    os.environ['DB_USER'], os.environ['DB_PASSWORD'],
    os.environ['DB_HOST'], os.environ['DB_PORT'], os.environ['DB_NAME']
)
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    from sqlalchemy import text

    # Check columns
    res = db.session.execute(text(
        "SELECT column_name, data_type FROM information_schema.columns WHERE table_name='ds_dichvucong' ORDER BY ordinal_position"
    ))
    cols = res.fetchall()
    print('=== ds_dichvucong columns ===')
    for c in cols:
        print(f'  {c[0]} ({c[1]})')

    # Test fixed SQL
    print('\n=== Testing fixed SQL ===')
    try:
        sql = text('''
            SELECT d.id, d.name
            FROM ds_dichvucong d
            LEFT JOIN ds_theloai t ON d.category_id = t.id
            WHERE d.name ILIKE :q
            LIMIT 5
        ''')
        res2 = db.session.execute(sql, {'q': '%UBND%'})
        rows = res2.fetchall()
        print(f'UBND results: {len(rows)}')
        for r in rows:
            print(f'  {r[0]} | {r[1]}')
    except Exception as e:
        print(f'SQL error: {e}')

    # Count total
    cnt = db.session.execute(text("SELECT COUNT(*) FROM ds_dichvucong")).scalar()
    print(f'\nTotal ds_dichvucong: {cnt}')

    hn_cnt = db.session.execute(text("SELECT COUNT(*) FROM ds_dichvucong WHERE id LIKE 'hn-%'")).scalar()
    print(f'HN records: {hn_cnt}')
