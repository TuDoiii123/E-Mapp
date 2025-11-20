import math

R = 6371  # Earth radius in kilometers


def to_rad(degrees):
    return degrees * (math.pi / 180)


def calculate_distance(lat1, lon1, lat2, lon2):
    """Return distance in kilometers between two coordinates (Haversine)."""
    dlat = to_rad(lat2 - lat1)
    dlon = to_rad(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 + math.cos(to_rad(lat1)) * math.cos(to_rad(lat2)) * math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return round(distance, 2)


def find_nearby(services, user_lat, user_lng, radius_km=10):
    try:
        user_lat = float(user_lat)
        user_lng = float(user_lng)
    except Exception:
        return []

    nearby = []
    for s in services:
        lat = s.get('latitude')
        lng = s.get('longitude')
        if lat is None or lng is None:
            continue
        try:
            dist = calculate_distance(user_lat, user_lng, float(lat), float(lng))
        except Exception:
            continue
        new_s = dict(s)
        new_s['distance'] = dist
        if dist <= float(radius_km):
            nearby.append(new_s)

    nearby.sort(key=lambda x: x.get('distance', float('inf')))
    return nearby
