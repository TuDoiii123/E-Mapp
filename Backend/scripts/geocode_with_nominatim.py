import os, sys, time, json
from pathlib import Path

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_file = os.path.join(root, 'data', 'public_services.json')
backup_dir = os.path.join(root, 'data', 'backups')

if not os.path.exists(data_file):
    print('public_services.json not found at', data_file)
    sys.exit(1)

with open(data_file, 'r', encoding='utf-8') as f:
    services = json.load(f)

# find targets: address contains 'thanh hoa' variants and missing lat/lng
targets = []
for i, s in enumerate(services):
    addr = (s.get('address') or '').lower()
    if ('thanh hoa' in addr or 'thanh hoá' in addr or 'thanh-ho' in addr or 'thanh-hoá' in addr) and not s.get('latitude') and not s.get('longitude'):
        targets.append((i, s))

print('Found', len(targets), 'services matching Thanh Hóa without coordinates')
if not targets:
    sys.exit(0)

# backup
os.makedirs(backup_dir, exist_ok=True)
from datetime import datetime
ts = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
backup_path = os.path.join(backup_dir, f'public_services_before_nominatim_{ts}.json')
with open(backup_path, 'w', encoding='utf-8') as b:
    json.dump(services, b, ensure_ascii=False, indent=2)
print('Backup written to', backup_path)

import requests

NOMINATIM = 'https://nominatim.openstreetmap.org/search'
headers = {'User-Agent': 'E-Map-Geocoder/1.0 (your-email@example.com)'}

updated = 0
for idx, svc in targets:
    address = svc.get('address')
    if not address:
        continue
    params = {
        'q': address + ', Viet Nam',
        'format': 'json',
        'limit': 1,
        'addressdetails': 0,
    }
    try:
        resp = requests.get(NOMINATIM, params=params, headers=headers, timeout=10)
        data = resp.json()
        if data:
            loc = data[0]
            lat = float(loc.get('lat'))
            lon = float(loc.get('lon'))
            services[idx]['latitude'] = lat
            services[idx]['longitude'] = lon
            updated += 1
            print(f'Geocoded (Nominatim) idx {idx}: {address} -> {lat},{lon}')
        else:
            print('Nominatim no result for:', address)
    except Exception as e:
        print('Nominatim request failed for', address, e)
    time.sleep(1)

if updated > 0:
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(services, f, ensure_ascii=False, indent=2)
    print('Wrote updated public_services.json, updated', updated, 'records')
else:
    print('No updates applied')
