import os
import requests
import urllib.parse
from dotenv import load_dotenv

load_dotenv()

def get_pois(destination: str) -> list:
    """
    Fetches real-world tourist landmarks with functional Google Maps links.
    Prioritizes 'Top Sights' and 'Local Results' for high-fidelity data.
    """
    print(f"🔎 [MAPS] Finding real-world attractions in {destination}...")
    
    api_key = os.getenv("SERPAPI_API_KEY")
    if not api_key:
        print("⚠️ [MAPS] SERPAPI_API_KEY missing!")
        return []

    params = {
        "engine": "google",
        "q": f"best things to do in {destination} points of interest",
        "api_key": api_key,
        "hl": "en",
        "gl": "us" 
    }

    try:
        response = requests.get("https://serpapi.com/search", params=params, timeout=15)
        data = response.json()
        sights = []
        
        # 1. PRIORITY: 'Top Sights' Carousel
        if "top_sights" in data:
            for item in data["top_sights"].get("sights", []):
                name = item.get("title")
                # Construct a guaranteed search link if 'link' is missing
                link = item.get("link") or f"https://www.google.com/maps/search/{urllib.parse.quote(name + ' ' + destination)}"
                sights.append({
                    "name": name,
                    "description": item.get("description", "A premier landmark."),
                    "rating": item.get("rating", "4.5"),
                    "search_link": link # <--- CRITICAL FOR FRONTEND
                })
        
        # 2. SECONDARY: 'Local Results'
        if not sights and "local_results" in data:
            for item in data["local_results"]:
                name = item.get("title")
                link = item.get("links", {}).get("directions") or f"https://www.google.com/maps/search/{urllib.parse.quote(name + ' ' + destination)}"
                sights.append({
                    "name": name,
                    "description": item.get("type", "Popular tourist attraction."),
                    "rating": item.get("rating", "4.0"),
                    "search_link": link
                })

        # Deduplicate and limit
        unique_sights = {s['name']: s for s in sights if s['name']}.values()
        final_list = list(unique_sights)[:10]

        if final_list:
            return final_list
            
        # Hard fallback with link
        return [{
            "name": f"{destination} City Center", 
            "description": "The historic heart.", 
            "rating": "4.5",
            "search_link": f"https://www.google.com/maps/search/{urllib.parse.quote(destination + ' City Center')}"
        }]

    except Exception as e:
        print(f"❌ [MAPS ERROR] {e}")
        return []