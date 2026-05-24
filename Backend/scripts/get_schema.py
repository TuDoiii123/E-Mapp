# -*- coding: utf-8 -*-
import sys, os, io, logging
logging.disable(logging.CRITICAL)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
os.environ['FLASK_ENV'] = 'production'
from dotenv import load_dotenv; load_dotenv()
from flask import Flask; app = Flask(__name__)
u = os.getenv('DB_USER','postgres')
p = os.getenv('DB_PASSWORD','')
h = os.getenv('DB_HOST','localhost')
port = os.getenv('DB_PORT','5432')
db_name = os.getenv('DB_NAME','postgres')
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{u}:{p}@{h}:{port}/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
from flask_sqlalchemy import SQLAlchemy; db = SQLAlchemy(app)

with app.app_context():
    from sqlalchemy import text
    cols = db.session.execute(text(
        "SELECT column_name, data_type FROM information_schema.columns "
        "WHERE table_name='procedures' AND table_schema='public' ORDER BY ordinal_position"
    )).fetchall()
    print('procedures columns:')
    for c in cols:
        print(f'  {c[0]}: {c[1]}')
