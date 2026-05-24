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

    # Show first 20 HN records
    res = db.session.execute(text(
        "SELECT id, name FROM ds_dichvucong WHERE id LIKE 'hn-%' ORDER BY id LIMIT 20"
    ))
    rows = res.fetchall()
    print('=== HN records (first 20) ===')
    for r in rows:
        print(f'  {r[0]} | {r[1]}')

    # Search UBND in HN records
    res2 = db.session.execute(text(
        "SELECT id, name FROM ds_dichvucong WHERE id LIKE 'hn-%' AND name ILIKE '%UBND%' LIMIT 10"
    ))
    rows2 = res2.fetchall()
    print(f'\n=== HN + UBND in name ({len(rows2)}) ===')
    for r in rows2:
        print(f'  {r[0]} | {r[1]}')

    # Check full search (what PublicService.search does)
    res3 = db.session.execute(text(
        "SELECT id, name FROM ds_dichvucong WHERE name ILIKE '%UBND%' OR address ILIKE '%UBND%' ORDER BY id LIKE 'hn-%' DESC LIMIT 20"
    ))
    rows3 = res3.fetchall()
    print(f'\n=== All UBND ({len(rows3)}) ===')
    for r in rows3:
        print(f'  {r[0]} | {r[1]}')
