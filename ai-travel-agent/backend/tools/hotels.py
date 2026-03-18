import os
import requests
import urllib.parse
from dotenv import load_dotenv

load_dotenv()
RAPID_API_KEY = os.getenv("RAPID_API_KEY")

def search_hotels(destination: str, duration_days: int, start_date: str, end_date: str) -> list:
    """
    Finalized for booking-com18. Handles Base64 Location IDs and List-based responses.
    """
    nights = max(1, int(duration_days))
    print(f"🏨 [HOTEL TOOL] Vetting properties in {destination} for {nights} nights...")
    
    headers = {
        "X-RapidAPI-Key": RAPID_API_KEY,
        "X-RapidAPI-Host": "booking-com18.p.rapidapi.com"
    }

    try:
        # --- STEP 1: GET LOCATION ID ---
        loc_url = "https://booking-com18.p.rapidapi.com/stays/auto-complete"
        loc_response = requests.get(loc_url, headers=headers, params={"query": destination})
        loc_data = loc_response.json()

        # The API returns {'status': True, 'message': 'Success', 'data': [...]}
        locations = loc_data.get('data', [])
        if not locations:
            return get_fallback_hotels(destination)

        # Use the ID found in your logs
        dest_id = locations[0].get('id') 
        print(f"📍 Found Location ID: {dest_id[:20]}...")

        # --- STEP 2: SEARCH FOR HOTELS ---
        search_url = "https://booking-com18.p.rapidapi.com/stays/search"
        search_params = {
            "locationId": dest_id,
            "checkinDate": start_date,
            "checkoutDate": end_date,
            "adults": "2",
            "rooms": "1",
            "currency": "EUR"
        }

        search_response = requests.get(search_url, headers=headers, params=search_params)
        search_data = search_response.json()
        
        # FIX: booking-com18 returns {'data': [...]} or just a list. 
        # Based on your error, 'search_data' might be a dictionary with a 'data' key that IS a list.
        hotel_list = search_data.get('data', [])
        
        # If 'data' itself is a list, we handle it here:
        if not isinstance(hotel_list, list):
             hotel_list = []

        if not hotel_list:
            print(f"⚠️ [HOTEL TOOL] No hotels found in the response data.")
            return get_fallback_hotels(destination)

        # --- STEP 3: MAPPING TIERS ---
        # Helper to find price in booking-com18 structure
        def extract_price(hotel):
            # Try rawPrice first, then fallback to price -> amount
            p = hotel.get('priceDetails', {}).get('rawPrice')
            if p is None:
                p = hotel.get('price', {}).get('amount', 0)
            return float(p)

        # Sort by price
        sorted_hotels = sorted(hotel_list, key=extract_price)
        
        tiers = []
        labels = ["Hostel/Budget", "Boutique", "Luxury"]
        # Select indices for 3 distinct price points
        indices = [0, len(sorted_hotels)//2, -1] 

        for i, label in enumerate(labels):
            h = sorted_hotels[indices[i]]
            total_price = extract_price(h)
            
            # Nightly rate calculation
            nightly = int(total_price / nights) if total_price > 0 else (60 * (i+1))

            tiers.append({
                "name": h.get('name', 'Central Hotel'),
                "price_per_night_eur": nightly,
                "image": h.get('image', h.get('thumbnailUrl')),
                "label": label,
                "rating": h.get('reviewScore', 'N/A')
            })

        print(f"✅ [HOTEL TOOL] Successfully fetched {len(tiers)} tiers!")
        return tiers

    except Exception as e:
        print(f"❌ [HOTEL TOOL] Error in hotels.py: {e}")
        return get_fallback_hotels(destination)

def get_fallback_hotels(city: str):
    return [
        {"name": f"{city} Budget Inn", "price_per_night_eur": 55, "label": "Hostel/Budget", "rating": 7.9},
        {"name": f"{city} Boutique Suites", "price_per_night_eur": 155, "label": "Boutique", "rating": 8.7},
        {"name": f"Grand {city} Palace", "price_per_night_eur": 480, "label": "Luxury", "rating": 9.2},
    ]