import os, sys, json
from datetime import datetime

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(root, 'data', 'public_services.json')
BACKUP_DIR = os.path.join(root, 'data', 'backups')

if not os.path.exists(DATA):
    print('public_services.json not found')
    sys.exit(1)

with open(DATA, 'r', encoding='utf-8') as f:
    services = json.load(f)

# province center for Thanh Hóa (approx)
THANHHOA_LAT = 19.8067
THANHHOA_LNG = 105.7758

modified = 0
for s in services:
    addr = (s.get('address') or '').lower()
    if ('thanh hoa' in addr or 'thanh hoá' in addr or 'thanh-ho' in addr) and not s.get('latitude') and not s.get('longitude'):
        s['latitude'] = THANHHOA_LAT
        s['longitude'] = THANHHOA_LNG
        modified += 1

if modified:
    os.makedirs(BACKUP_DIR, exist_ok=True)
    ts = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
    backup = os.path.join(BACKUP_DIR, f'public_services_before_set_thanhhoa_coords_{ts}.json')
    with open(backup, 'w', encoding='utf-8') as b:
        json.dump(services, b, ensure_ascii=False, indent=2)
    with open(DATA, 'w', encoding='utf-8') as f:
        json.dump(services, f, ensure_ascii=False, indent=2)
    print('Set', modified, 'entries to Thanh Hóa coords; backup at', backup)
else:
    print('No entries modified')
