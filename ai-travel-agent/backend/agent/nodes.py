import json
import time
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

def clean_json_response(response_content):
    content = response_content.content if hasattr(response_content, 'content') else str(response_content)
    start_idx = content.find('{')
    end_idx = content.rfind('}')
    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
        return content[start_idx:end_idx + 1]
    return content.replace('```json', '').replace('```', '').strip()

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
        "end_date": state.get('end_date') or today_str
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
    # We still fetch it for budget/internal logic, but we won't display it if requested
    return {"weather": check_weather(state['destination'])}

def get_pois_node(state: TripState) -> dict:
    return {"pois": get_pois(state['destination'])}

# --- 6. PLANNER (FIXED ITINERARY DISTRIBUTION) ---
def planner_node(state: TripState) -> dict:
    dest = state['destination']
    days_count = int(state.get('duration_days', 3))
    real_pois = state.get('pois', [])
    
    # Selection logic for flight
    found_flights = state.get('flights', [])
    selected_flight = found_flights[0] if found_flights else {"airline": "Global Carrier", "price_eur": 480}

    # STEP 1: Manually Slice POIs to prevent duplication
    # We take 2 landmarks per day to ensure variety
    poi_assignments = []
    for i in range(days_count):
        start = i * 2
        end = start + 2
        day_landmarks = real_pois[start:end]
        if not day_landmarks: # Fallback if we run out of real landmarks
            day_landmarks = [{"name": "Historic City Center", "description": "Local exploration"}]
        poi_assignments.append(day_landmarks)

    print(f"📝 [PLANNER] Generating strict itinerary using {len(real_pois)} real landmarks...")
    
    try:
        # Construct a very explicit context for the AI
        poi_text = ""
        for idx, day_list in enumerate(poi_assignments):
            landmark_names = ", ".join([p['name'] for p in day_list])
            poi_text += f"Day {idx+1} MUST center around: {landmark_names}\n"

        sys_msg = "You are a professional travel guide. You must create a SPECIFIC itinerary using ONLY the landmarks provided. No generic 'Heritage' filler."
        user_msg = f"""Plan a {days_count}-day trip to {dest}. 
        
        MANDATORY ASSIGNMENTS:
        {poi_text}

        RULES:
        1. Every day must have 3 activities: Morning, Mid-day, and Evening.
        2. Activity names MUST contain the landmark name (e.g., 'Guided tour of Belém Tower').
        3. Do NOT use generic names like 'Local heritage discovery' or 'Cultural Exploration'.
        4. Use the description of the landmarks to make activities unique.
        5. Return ONLY clean JSON.

        Format: {{ "days": [ {{ "day": 1, "theme": "Landmark Focus", "activities": [ {{ "name": "...", "time": "10:00 AM", "cost_eur": 15 }} ] }} ] }}
        """
        
        response = llm.invoke([("system", sys_msg), ("user", user_msg)])
        plan = json.loads(clean_json_response(response))
        
        # FINAL GUARD: If AI failed to provide days, use the manual builder
        if not plan.get("days"):
            raise ValueError("Empty days")

    except Exception as e:
        print(f"🚨 [PLANNER AI FAIL] {e}. Using Manual Construction Engine.")
        # MANUAL CONSTRUCTION: If Gemini fails, we build it ourselves using the POIs
        manual_days = []
        for i in range(days_count):
            day_pois = poi_assignments[i]
            main_landmark = day_pois[0]['name']
            manual_days.append({
                "day": i + 1,
                "theme": f"Discovering {main_landmark}",
                "activities": [
                    {"name": f"Comprehensive tour of {main_landmark}", "time": "09:30 AM", "cost_eur": 25},
                    {"name": f"Afternoon stroll around {day_pois[-1]['name']}", "time": "02:00 PM", "cost_eur": 0},
                    {"name": f"Evening dinner near {main_landmark}", "time": "07:30 PM", "cost_eur": 45}
                ]
            })
        plan = {"days": manual_days}

    return {
        "itinerary": plan,
        "selected_flight": selected_flight,
        "destination_lat": state['destination_lat'], 
        "destination_lng": state['destination_lng']
    }

# --- 7. BUDGET & COMPILATION ---
def budget_check_node(state: TripState) -> dict:
    from utils.budget import calculate_total_cost
    return calculate_total_cost(state)

def compile_itinerary_node(state: TripState) -> dict:
    # Weather is fetched in state but not passed to final frontend display bundle
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