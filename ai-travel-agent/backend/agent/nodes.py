import json
import os
import re
import requests
from datetime import datetime
from langchain_google_genai import ChatGoogleGenerativeAI
from agent.state import TripState
from tools.flights import search_flights
from tools.hotels import search_hotels
from tools.weather import check_weather
from tools.maps import get_pois
from dotenv import load_dotenv

load_dotenv()

today_str = datetime.now().strftime("%Y-%m-%d")

# Initialize Gemini 1.5 Flash 
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash", 
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.2
)

# --- UTILITY: DYNAMIC GEOCODING ---
def get_coords(city_name: str):
    """Fetches real lat/lng for ANY city using OpenStreetMap."""
    try:
        url = f"https://nominatim.openstreetmap.org/search?q={city_name}&format=json&limit=1"
        headers = {'User-Agent': 'TravelDev-Agent-Project'}
        resp = requests.get(url, headers=headers).json()
        if resp:
            return float(resp[0]['lat']), float(resp[0]['lon'])
    except Exception as e:
        print(f"🌍 Geocoding error for {city_name}: {e}")
    return 0.0, 0.0

def clean_json_response(content):
    """Cleans AI responses to ensure valid JSON parsing."""
    content = str(content)
    # Remove markdown code block wrappers
    content = re.sub(r'```json\s*|\s*```', '', content).strip()
    # Find the outermost curly braces
    start = content.find('{')
    end = content.rfind('}')
    if start != -1 and end != -1:
        return content[start:end+1]
    return content

# --- 1. PARSE INPUT ---
def parse_input_node(state: TripState) -> dict:
    text = state['user_prompt']
    print(f"🧠 [AI BRAIN] Reasoning: {text}")
    
    match = re.search(r"to\s+([a-zA-Z\s]+?)(?:\s+for|$)", text, re.IGNORECASE)
    dest = match.group(1).strip() if match else "France"
    
    match_origin = re.search(r"(?:From\s+)?([a-zA-Z\s]+?)\s+to", text, re.IGNORECASE)
    origin = match_origin.group(1).strip() if match_origin else "Norway"

    dur_match = re.search(r"for\s+(\d+)\s+days", text, re.IGNORECASE)
    duration = int(dur_match.group(1)) if dur_match else 3

    o_lat, o_lng = get_coords(origin)
    d_lat, d_lng = get_coords(dest)

    return {
        "destination": dest,
        "origin_city": origin,
        "origin_lat": o_lat,
        "origin_lng": o_lng,
        "destination_lat": d_lat,
        "destination_lng": d_lng,
        "duration_days": duration,
        "start_date": state.get('start_date') or today_str,
        "end_date": state.get('end_date') or today_str,
        "current_step": "parsed"
    }

# --- 2. SEARCH FLIGHTS ---
def search_flights_node(state: TripState) -> dict:
    flights = search_flights(state['origin_city'], state['destination'], state['start_date'], state['end_date'])
    return {"flights": flights}

# --- 3. SEARCH HOTELS ---
def search_hotels_node(state: TripState) -> dict:
    hotels = search_hotels(state['destination'], state['duration_days'], state['start_date'], state['end_date'])
    return {"hotels": hotels}

# --- 4. WEATHER & POIs ---
def check_weather_node(state: TripState) -> dict:
    return {"weather": check_weather(state['destination'])}

def get_pois_node(state: TripState) -> dict:
    return {"pois": get_pois(state['destination'])}


# --- 6. PLANNER (HIGH-VIBE TOURIST REALISM) ---
def planner_node(state: TripState) -> dict:
    dest = state['destination']
    days_count = int(state.get('duration_days', 1))
    real_pois = state.get('pois', [])
    
    found_flights = state.get('flights', [])
    selected_flight = found_flights[0] if found_flights else {"airline": "Global Carrier", "price_eur": 450}
    selected_hotel = state.get('hotels')[0] if state.get('hotels') else None

    print(f"📝 [PLANNER] Forcing {days_count} days for {dest}...")

    # Data Anchor: Ensure we have landmarks to show even in fallback
    poi_list = [p['name'] for p in real_pois] if real_pois else [f"{dest} Old Town", f"{dest} Central Park", f"{dest} Museum"]

    try:
        sys_msg = f"You are a Travel API. You MUST return a JSON object with a 'days' array containing EXACTLY {days_count} elements."
        user_msg = f"""Plan a {days_count}-day trip to {dest}.
        Use these landmarks: {', '.join(poi_list[:6])}.
        
        Return ONLY this JSON format:
        {{
          "days": [
            {{
              "day": 1,
              "theme": "Historical Exploration",
              "activities": [
                {{ "name": "Visit the local landmarks", "time": "10:00 AM", "cost_eur": 20 }},
                {{ "name": "Lunch at a traditional bistro", "time": "01:00 PM", "cost_eur": 30 }},
                {{ "name": "Evening city views", "time": "07:00 PM", "cost_eur": 0 }}
              ]
            }}
          ]
        }}
        (Add more days until you reach {days_count} days).
        """
        
        response = llm.invoke([("system", sys_msg), ("user", user_msg)])
        clean_json = clean_json_response(response.content if hasattr(response, 'content') else str(response))
        plan = json.loads(clean_json)

        # Ensure the AI didn't short-change us on days
        if len(plan.get("days", [])) < days_count:
            raise ValueError("AI under-delivered day count")

    except Exception as e:
        print(f"🚨 [PLANNER AI FAIL] {e}. Building manual itinerary from POIs...")
        # REALISTIC FALLBACK: If AI fails, we build it ourselves using the real POIs
        manual_days = []
        for i in range(days_count):
            # Pick 2-3 POIs for this specific day
            day_pois = poi_list[i*2 : (i*2)+2] if i*2 < len(poi_list) else [poi_list[0]]
            manual_days.append({
                "day": i + 1,
                "theme": f"Exploring {dest} -  Day {i+1}",
                "activities": [
                    {"name": f"Morning visit to {day_pois[0]}", "time": "09:30 AM", "cost_eur": 25},
                    {"name": f"Afternoon discovery of {day_pois[1] if len(day_pois)>1 else dest}", "time": "02:00 PM", "cost_eur": 30},
                    {"name": f"Evening dinner in central {dest}", "time": "07:30 PM", "cost_eur": 40}
                ]
            })
        plan = {"days": manual_days}

    return {
        "itinerary": plan,
        "selected_flight": selected_flight,
        "selected_hotel": selected_hotel
    }

# --- 7. BUDGET & COMPILATION ---
def budget_check_node(state: TripState) -> dict:
    from utils.budget import calculate_total_cost
    return calculate_total_cost(state)

def compile_itinerary_node(state: TripState) -> dict:
    return {
        "destination_lat": state.get("destination_lat"),
        "destination_lng": state.get("destination_lng"),
        "origin_lat": state.get("origin_lat"),
        "origin_lng": state.get("origin_lng"),
        "destination": state.get("destination"),
        "itinerary": state.get("itinerary"),  
        "selected_flight": state.get("selected_flight"),
        "hotels": state.get("hotels", []),
        "total_cost_eur": state.get("total_cost_eur"), 
        "start_date": state.get("start_date"),
        "end_date": state.get("end_date"),
        "current_step": "final_itinerary"
    }