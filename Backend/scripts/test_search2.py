import urllib.request, json, sys

def test_query(query, limit=10):
    url = f"http://localhost:8888/api/services/search?q={urllib.parse.quote(query)}&limit={limit}"
    try:
        with urllib.request.urlopen(url) as resp:
            d = json.load(resp)
        svcs = d.get('data', {}).get('services', [])
        hn = [s for s in svcs if s['id'].startswith('hn-')]
        th = [s for s in svcs if s['id'].startswith('th-')]
        print(f"  Q='{query}' -> {len(svcs)} results | HN:{len(hn)} TH:{len(th)}")
        for s in svcs[:3]:
            print(f"    {s['id']}")
    except Exception as e:
        print(f"  Error: {e}")

import urllib.parse

print("=== Search API Tests ===")
test_query("UBND", 20)
test_query("Ba Dinh", 5)
test_query("Cong an", 10)
test_query("BHXH", 5)
test_query("Hai Ba Trung", 5)
