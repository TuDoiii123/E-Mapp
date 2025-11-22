"""
Import data from Postgres table `dichvucong_thanhhoa` into Backend/data/public_services.json.
Creates a timestamped backup of the existing JSON before overwriting.

Usage:
  python Backend/scripts/import_dichvu_to_public_services.py

Requirements: sqlalchemy, psycopg2-binary
"""
import os
import sys
import json
from datetime import datetime

# Ensure Backend is on path
here = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(here)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from models.db import get_db_url
from sqlalchemy import create_engine, text

# import the mapper from models.public_service
from models.public_service import _map_db_row_to_service

DATA_DIR = os.path.join(project_root, 'data')
OUT_FILE = os.path.join(DATA_DIR, 'public_services.json')
BACKUP_DIR = os.path.join(DATA_DIR, 'backups')


def ensure_dirs():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(BACKUP_DIR, exist_ok=True)


def backup_existing():
    if os.path.exists(OUT_FILE):
        ts = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
        backup_name = f'public_services_{ts}.json'
        backup_path = os.path.join(BACKUP_DIR, backup_name)
        with open(OUT_FILE, 'rb') as r, open(backup_path, 'wb') as w:
            w.write(r.read())
        print('Backup created:', backup_path)
    else:
        print('No existing public_services.json to backup.')


def fetch_and_map():
    url = get_db_url()
    print('Connecting to DB at', url)
    engine = create_engine(url)
    mapped = []
    with engine.connect() as conn:
        res = conn.execute(text('SELECT * FROM dichvucong_thanhhoa'))
        rows = res.mappings().all()
        for r in rows:
            try:
                svc = _map_db_row_to_service(r)
                mapped.append(svc)
            except Exception as e:
                print('Failed to map row:', e)
    return mapped


def write_out(mapped):
    # write pretty JSON
    with open(OUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(mapped, f, ensure_ascii=False, indent=2)
    print('Wrote', len(mapped), 'services to', OUT_FILE)


def main():
    ensure_dirs()
    backup_existing()
    mapped = fetch_and_map()
    if not mapped:
        print('No mapped rows, aborting write.')
        return
    write_out(mapped)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print('Import failed:', e)
