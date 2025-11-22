import os, sys, json
here = os.path.dirname(os.path.abspath(__file__))
root = os.path.dirname(here)
data_file = os.path.join(root, 'data', 'public_services.json')

if not os.path.exists(data_file):
    print('public_services.json not found at', data_file)
    sys.exit(1)

with open(data_file, 'r', encoding='utf-8') as f:
    arr = json.load(f)

print('Total services:', len(arr))

count_thanhhoa = 0
count_lat = 0
count_lng = 0
count_both = 0
samples = []

for s in arr:
    addr = (s.get('address') or '').lower()
    if 'thanh hoá' in addr or 'thanh hoa' in addr or 'thanh-hóa' in addr or 'thanh-hoá' in addr:
        count_thanhhoa += 1
        samples.append(s)
    lat = s.get('latitude')
    lng = s.get('longitude')
    if lat is not None:
        try:
            float(lat)
            count_lat += 1
        except:
            pass
    if lng is not None:
        try:
            float(lng)
            count_lng += 1
        except:
            pass
    if lat is not None and lng is not None:
        try:
            float(lat); float(lng)
            count_both += 1
        except:
            pass

print('Services with address matching Thanh Hóa:', count_thanhhoa)
print('Services with latitude value:', count_lat)
print('Services with longitude value:', count_lng)
print('Services with both lat & lng:', count_both)

print('\nExamples (up to 5) of Thanh Hóa matches:')
for s in samples[:5]:
    print({k: s.get(k) for k in ('id','name','address','latitude','longitude','level')})
