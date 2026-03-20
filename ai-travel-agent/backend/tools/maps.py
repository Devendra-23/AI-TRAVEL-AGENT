import os
import requests
from dotenv import load_dotenv

load_dotenv()

def get_pois(destination: str) -> list:
    """
    Fetches real-world tourist landmarks using SerpApi Google Engine.
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
        response = requests.get("https://serpapi.com/search", params=params)
        data = response.json()
        sights = []
        
        # 1. PRIORITY: 'Top Sights' Carousel (The highest quality landmark list)
        if "top_sights" in data:
            for item in data["top_sights"].get("sights", []):
                sights.append({
                    "name": item.get("title"),
                    "description": item.get("description", "A premier landmark."),
                    "rating": item.get("rating", "4.5")
                })
        
        # 2. SECONDARY: 'Local Results' (Google Maps listings)
        if not sights and "local_results" in data:
            for item in data["local_results"]:
                sights.append({
                    "name": item.get("title"),
                    "description": item.get("type", "Popular tourist attraction."),
                    "rating": item.get("rating", "4.0")
                })
        
        # 3. FALLBACK: Knowledge Graph Sights
        if not sights and "knowledge_graph" in data:
            kg_sights = data["knowledge_graph"].get("sights", [])
            for item in kg_sights:
                sights.append({
                    "name": item.get("title"),
                    "description": "Historic point of interest.",
                    "rating": "4.5"
                })

        # Deduplicate results based on name and limit to top 10
        unique_sights = {s['name']: s for s in sights}.values()
        final_list = list(unique_sights)[:10]

        if final_list:
            print(f"✅ [MAPS] Successfully identified {len(final_list)} real POIs.")
            return final_list
            
        return [{"name": "City Center", "description": "The historic heart of the city.", "rating": "4.0"}]

    except Exception as e:
        print(f"❌ [MAPS ERROR] {e}")
        return []