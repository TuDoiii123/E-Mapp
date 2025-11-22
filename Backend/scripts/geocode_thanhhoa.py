import os, sys, time, json
from pathlib import Path

# Try to obtain Google API key from environment first, then Frontend/.env
GM_KEY = os.getenv('GOOGLE_MAPS_API_KEY') or os.getenv('VITE_GOOGLE_MAPS_API_KEY')
if not GM_KEY:
    # try to read Frontend/.env
    frontend_env = Path(os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'Frontend', '.env')).resolve()
    if frontend_env.exists():
        with open(frontend_env, 'r', encoding='utf-8') as f:
            for ln in f:
                if ln.strip().startswith('VITE_GOOGLE_MAPS_API_KEY='):
                    GM_KEY = ln.strip().split('=',1)[1]
                    break

if not GM_KEY:
    print('Google Maps API key not found. Set environment variable GOOGLE_MAPS_API_KEY or VITE_GOOGLE_MAPS_API_KEY or add to Frontend/.env')
    sys.exit(1)

import requests
from datetime import datetime

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
ts = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
backup_path = os.path.join(backup_dir, f'public_services_before_geocode_{ts}.json')
with open(backup_path, 'w', encoding='utf-8') as b:
    json.dump(services, b, ensure_ascii=False, indent=2)
print('Backup written to', backup_path)

GEOCODE_URL = 'https://maps.googleapis.com/maps/api/geocode/json'

updated = 0
for idx, svc in targets:
    address = svc.get('address')
    if not address:
        continue
    params = {
        'address': address,
        'key': GM_KEY,
        'region': 'vn'
    }
    try:
        resp = requests.get(GEOCODE_URL, params=params, timeout=10)
        data = resp.json()
        if data.get('status') == 'OK' and data.get('results'):
            loc = data['results'][0]['geometry']['location']
            services[idx]['latitude'] = loc.get('lat')
            services[idx]['longitude'] = loc.get('lng')
            updated += 1
            print(f"Geocoded index {idx}: {address} -> {loc.get('lat')},{loc.get('lng')}")
        else:
            print(f"No geocode result for: {address} - status {data.get('status')}")
    except Exception as e:
        print('Request failed for', address, e)
    time.sleep(0.2)  # small delay

# write back if updated
if updated > 0:
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(services, f, ensure_ascii=False, indent=2)
    print('Wrote updated public_services.json, updated', updated, 'records')
else:
    print('No updates applied')
