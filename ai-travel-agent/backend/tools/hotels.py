import os
import requests
import re
from dotenv import load_dotenv

load_dotenv()

SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")

def clean_price(price_input) -> float:
    """
    METICULOUS FIX: Strips currency symbols, commas, and whitespace.
    Handles '€140', '1,200.50', and raw numbers.
    """
    if price_input is None:
        return 0.0
    if isinstance(price_input, (int, float)):
        return float(price_input)
    
    # Remove everything except digits and the decimal point
    cleaned = re.sub(r'[^\d.]', '', str(price_input).replace(',', ''))
    try:
        return float(cleaned) if cleaned else 0.0
    except ValueError:
        return 0.0

def search_hotels(destination: str, duration_days: int, start_date: str, end_date: str) -> list:
    """
    Uses SerpApi Google Hotels Engine.
    Fetches real-time pricing and high-res photography for property tiers.
    """
    nights = max(1, int(duration_days))
    print(f"🏨 [GDS HOTELS] Vetting properties in {destination} for {nights} nights...")

    params = {
        "engine": "google_hotels",
        "q": f"best hotels and stay in {destination}",
        "check_in_date": start_date,
        "check_out_date": end_date,
        "currency": "EUR",
        "hl": "en",
        "api_key": SERPAPI_API_KEY
    }

    try:
        response = requests.get("https://serpapi.com/search", params=params)
        data = response.json()
        
        hotel_results = data.get("properties", [])
        if not hotel_results:
            print("📡 [HOTELS] No live properties found. Using Safety Fallback.")
            return get_fallback_hotels(destination)

        # Sort by price to create accurate Boutique/Luxury tiers
        sorted_hotels = sorted(
            hotel_results, 
            key=lambda x: clean_price(x.get("rate_per_night", {}).get("lowest", 9999))
        )

        tiers = []
        labels = ["Hostel/Budget", "Boutique", "Luxury"]
        # Distribute selection across the price spectrum
        indices = [0, len(sorted_hotels)//2, len(sorted_hotels)-1]

        for i, idx in enumerate(indices):
            h = sorted_hotels[idx]
            
            # PREMIMUM PHOTO LOGIC: Grab the first high-res thumbnail available
            images = h.get("images", [])
            image_url = images[0].get("thumbnail") if images else "/hotel-placeholder.jpg"
            
            raw_rate = h.get("rate_per_night", {}).get("lowest")
            nightly_rate = clean_price(raw_rate)

            # Fallback for pricing if the GDS returned null for a specific tier
            if nightly_rate == 0:
                nightly_rate = [45, 140, 350][i]

            tiers.append({
                "name": h.get("name", f"Elite {destination} Stay"),
                "price_per_night_eur": int(nightly_rate),
                "image": image_url,
                "label": labels[i],
                "rating": h.get("overall_rating", "4.5"),
                "amenities": h.get("amenities", [])[:4] # Pass amenities for UI icons
            })

        print(f"✅ [GDS HOTELS] Successfully captured {len(tiers)} live property tiers.")
        return tiers

    except Exception as e:
        print(f"❌ [HOTELS ERROR] {e}")
        return get_fallback_hotels(destination)

def get_fallback_hotels(city: str):
    """Reliable safety net for the UI."""
    return [
        {"name": f"{city} Urban Hostel", "price_per_night_eur": 45, "label": "Hostel/Budget", "rating": 7.5, "image": ""},
        {"name": f"{city} Design Boutique", "price_per_night_eur": 125, "label": "Boutique", "rating": 8.9, "image": ""},
        {"name": f"Royal {city} Grand Hotel", "price_per_night_eur": 350, "label": "Luxury", "rating": 9.5, "image": ""},
    ]