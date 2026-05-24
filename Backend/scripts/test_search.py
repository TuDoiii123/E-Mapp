import urllib.request, json, sys

url = "http://localhost:8888/api/services/search?q=UBND&limit=20"
try:
    with urllib.request.urlopen(url) as resp:
        d = json.load(resp)
    svcs = d.get('data', {}).get('services', [])
    print(f"Total: {len(svcs)}")
    hn = [s for s in svcs if s['id'].startswith('hn-')]
    th = [s for s in svcs if s['id'].startswith('th-')]
    print(f"  HN: {len(hn)} | TH: {len(th)} | Other: {len(svcs)-len(hn)-len(th)}")
    print("First 5 results:")
    for s in svcs[:5]:
        print(f"  {s['id']} | {s['name']}")
except Exception as e:
    print(f"Error: {e}")
