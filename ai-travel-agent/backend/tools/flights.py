import os
import requests
from dotenv import load_dotenv

load_dotenv()

SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")

def get_airport_code(location: str) -> str:
    """
    Precision mapping for GDS. 
    Maps common country names and city names to their primary flight hubs.
    """
    mapping = {
        # UK Hubs
        "london": "LHR", "newcastle": "NCL", "manchester": "MAN",
        "bristol": "BRS", "edinburgh": "EDI", "glasgow": "GLA",
        # Europe Hubs
        "stockholm": "ARN", "sweden": "ARN", 
        "poznan": "POZ", "poland": "WAW", "warsaw": "WAW",
        "paris": "CDG", "france": "CDG",
        "berlin": "BER", "germany": "BER", "munich": "MUC",
        "amsterdam": "AMS", "netherlands": "AMS",
        "madrid": "MAD", "barcelona": "BCN", "spain": "MAD",
        "rome": "FCO", "milan": "MXP", "italy": "FCO",
        "helsinki": "HEL", "finland": "HEL",
        "oslo": "OSL", "norway": "OSL",
        "lisbon": "LIS", "portugal": "LIS",
        # Global
        "mumbai": "BOM", "delhi": "DEL", "india": "BOM",
        "new york": "JFK", "usa": "JFK", "los angeles": "LAX"
    }
    loc = location.lower().strip()
    # Returns mapping or guesses the first 3 letters
    return mapping.get(loc, location.upper()[:3])

def search_flights(origin: str, destination: str, start_date: str, end_date: str) -> list:
    """
    Fetches LIVE GDS fares. Combines 'best' and 'other' flights to 
    capture budget carriers like Ryanair and EasyJet.
    """
    origin_code = get_airport_code(origin)
    dest_code = get_airport_code(destination)
    
    print(f"🛫 [GDS LIVE] Searching: {origin_code} ⟷ {dest_code}")

    params = {
        "engine": "google_flights",
        "departure_id": origin_code,
        "arrival_id": dest_code,
        "outbound_date": start_date,
        "return_date": end_date,
        "currency": "EUR",
        "hl": "en",
        "api_key": SERPAPI_API_KEY,
        "type": "1", # Round Trip
        "deep_search": "true" # Forces loading of all budget carriers
    }

    try:
        response = requests.get("https://serpapi.com/search", params=params, timeout=25)
        data = response.json()
        
        # Combine lists: Budget carriers often land in 'other_flights'
        itineraries = data.get("best_flights", []) + data.get("other_flights", [])

        if not itineraries:
            print(f"📡 [GDS] No live matches for {origin_code}-{dest_code}. Using dynamic estimate.")
            return get_fallback_flights(start_date, end_date, origin_code, dest_code)

        real_flights = []
        # Sort by price to find the actual cheapest deal
        sorted_data = sorted(itineraries, key=lambda x: x.get('price', 9999))

        for flight in sorted_data[:5]:
            segments = flight.get("flights", [])
            airline = segments[0].get("airline", "Real Carrier") if segments else "Carrier"
            price = flight.get("price")

            if price:
                real_flights.append({
                    "airline": airline,
                    "price_eur": int(price),
                    "outbound_price": int(price * 0.48),
                    "return_price": int(price) - int(price * 0.48),
                    "duration": flight.get("total_duration", "N/A"),
                    "is_round_trip": True,
                    "type": "Verified GDS Fare"
                })

        return real_flights

    except Exception as e:
        print(f"❌ [GDS ERROR] {e}")
        return get_fallback_flights(start_date, end_date, origin_code, dest_code)

def get_fallback_flights(s_date, e_date, origin_code, dest_code):
    """
    Smart estimation fallback that predicts the airline based on the route.
    """
    uk_hubs = ["LHR", "LGW", "STN", "LTN", "NCL", "MAN", "EDI", "GLA", "BRS"]
    is_uk_internal = origin_code in uk_hubs and dest_code in uk_hubs
    
    # Route-specific logic
    if dest_code == "POZ": airline = "Ryanair"
    elif dest_code == "ARN": airline = "SAS / Norwegian"
    elif is_uk_internal: airline = "EasyJet"
    else: airline = "Global Carrier"

    price = 85 if (is_uk_internal or dest_code in ["POZ", "ARN"]) else 450
    
    return [{
        "airline": f"{airline} (Market Est.)",
        "price_eur": price,
        "outbound_price": int(price * 0.5),
        "return_price": int(price * 0.5),
        "is_round_trip": True,
        "type": "Market Estimate"
    }]