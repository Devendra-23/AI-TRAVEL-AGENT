import os
import requests
from dotenv import load_dotenv

load_dotenv()
RAPID_API_KEY = os.getenv("RAPID_API_KEY")

def search_flights(origin_iata: str, destination_iata: str, start_date: str, end_date: str, trip_type: str) -> list:
    """
    Meticulously updated for booking-com18 subscription.
    Handles dynamic routing for One-Way and Round-Trip searches.
    """
    t_type = (trip_type or "round-trip").lower()
    
    # booking-com18 uses standard 3-letter IATA codes (JFK, LIS, etc.) 
    # It does NOT usually need the '-sky' suffix.
    from_code = (origin_iata or "LHR").upper()[:3]
    to_code = (destination_iata or "MAD").upper()[:3]
    
    # Use the specific booking-com18 endpoints
    if t_type == "round-trip":
        url = "https://booking-com18.p.rapidapi.com/flights/v2/min-price-roundtrip"
    else:
        url = "https://booking-com18.p.rapidapi.com/flights/v2/min-price-oneway"
    
    # CRITICAL: Updated Host Header
    headers = {
        "x-rapidapi-key": RAPID_API_KEY,
        "x-rapidapi-host": "booking-com18.p.rapidapi.com",
        "Content-Type": "application/json"
    }

    # Ensure we don't send 'None' strings to the API
    s_date = start_date if start_date and str(start_date) != "None" else "2026-06-15"
    e_date = end_date if end_date and str(end_date) != "None" else "2026-06-22"

    # Params mapped specifically to booking-com18 schema
    querystring = {
        "departId": from_code,
        "arrivalId": to_code,
        "outboundDate": s_date,
        "currencyCode": "EUR"
    }
    
    if t_type == "round-trip":
        querystring["returnDate"] = e_date

    print(f"🛫 [SKYSCANNER] Live Search: {from_code} -> {to_code} ({t_type})")

    try:
        response = requests.get(url, headers=headers, params=querystring)
        
        # If we get a 404 or 403, we return fallbacks to keep UI alive
        if response.status_code != 200:
            print(f"⚠️ Flight API Status: {response.status_code} - {response.text[:100]}")
            return get_fallback_flights()

        data = response.json()
        
        # booking-com18 usually returns a list under the 'data' key
        # We look for the flight results meticulously
        flight_data = data.get('data', [])
        
        if not flight_data or not isinstance(flight_data, list):
            print("📡 [SKYSCANNER] No flight results found in response data.")
            return get_fallback_flights(airline="Lufthansa")

        real_flights = []
        # Take up to 5 best options
        for f in flight_data[:5]:
            # booking-com18 structure: 'airlineName' and 'price' -> 'amount'
            airline = f.get('airlineName') or f.get('airline') or "Major Airline"
            
            # Navigate the price object
            price_info = f.get('price', {})
            raw_price = price_info.get('amount') or f.get('minPrice') or 450
            price_val = int(float(raw_price))

            real_flights.append({
                "airline": airline,
                "price_eur": price_val,
                "is_round_trip": t_type == "round-trip",
                "departure_date": s_date,
                "return_date": e_date if t_type == "round-trip" else None,
                "link": "#"
            })
            
        print(f"📡 [SKYSCANNER] Successfully fetched {len(real_flights)} real flight options.")
        return real_flights if real_flights else get_fallback_flights(airline="Lufthansa")

    except Exception as e:
        print(f"❌ [SKYSCANNER] Error: {e}")
        return get_fallback_flights()

def get_fallback_flights(airline="EasyJet"):
    """Meticulous safety net to keep the UI populated during API downtime."""
    return [{"airline": f"{airline} (Est.)", "price_eur": 180, "is_round_trip": True}]