# Coordinate mapping for major supply chain hubs
HUB_COORDS = {
    "Tokyo": {"lat": 35.6762, "lon": 139.6503},
    "Los Angeles": {"lat": 34.0522, "lon": -118.2437},
    "Shanghai": {"lat": 31.2304, "lon": 121.4737},
    "Rotterdam": {"lat": 51.9225, "lon": 4.4792},
    "New York": {"lat": 40.7128, "lon": -74.0060},
    "Veracruz": {"lat": 19.1738, "lon": -96.1342},
    "Houston": {"lat": 29.7604, "lon": -95.3698},
    "Jakarta": {"lat": -6.2088, "lon": 106.8456},
    "Sydney": {"lat": -33.8688, "lon": 151.2093},
    "Mumbai": {"lat": 19.0760, "lon": 72.8777},
    "Busan": {"lat": 35.1796, "lon": 129.0756},
    "Vancouver": {"lat": 49.2827, "lon": -123.1207},
    "Taiwan": {"lat": 23.6978, "lon": 120.9605},
    "Germany": {"lat": 51.1657, "lon": 10.4515},
    "China": {"lat": 35.8617, "lon": 104.1954},
    "USA": {"lat": 37.0902, "lon": -95.7129},
    "India": {"lat": 20.5937, "lon": 78.9629},
    "Brazil": {"lat": -14.2350, "lon": -51.9253},
    "France": {"lat": 46.2276, "lon": 2.2137},
}

def get_coords(name):
    return HUB_COORDS.get(name, {"lat": 0, "lon": 0})
