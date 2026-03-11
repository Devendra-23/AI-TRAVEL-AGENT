# tools/mock_data.py [cite: 83]
MOCK_FLIGHTS = [
    {'airline': 'ANA', 'price_usd': 650, 'departure': '2026-06-01T10:00', 'duration_hours': 14.5, 'stops': 0},
    {'airline': 'Japan Airlines', 'price_usd': 580, 'departure': '2026-06-01T14:00', 'duration_hours': 15.0, 'stops': 1},
]

MOCK_HOTELS = [
    {'name': 'Shinjuku Granbell', 'price_per_night_usd': 120, 'rating': 4.3, 'location': 'Shinjuku', 'amenities': ['WiFi', 'Breakfast']},
    {'name': 'Asakusa Culture Hostel', 'price_per_night_usd': 45, 'rating': 4.6, 'location': 'Asakusa', 'amenities': ['WiFi']},
]

MOCK_WEATHER = [
    {'date': '2026-06-01', 'condition': 'sunny',  'temp_high_c': 26, 'temp_low_c': 18},
]

MOCK_POIS = [
    {'name': 'Senso-ji Temple', 'category': 'temple', 'rating': 4.8, 'visit_duration_hours': 2.0, 'admission_usd': 0},
]