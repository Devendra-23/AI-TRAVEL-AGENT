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
    temperature=0.1 # Lower temperature for precision parsing
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
    content = re.sub(r'```json\s*|\s*```', '', content).strip()
    start = content.find('{')
    end = content.rfind('}')
    if start != -1 and end != -1:
        return content[start:end+1]
    return content

# --- 1. PARSE INPUT (UPGRADED TO LLM) ---
def parse_input_node(state: TripState) -> dict:
    text = state['user_prompt']
    print(f"🧠 [AI BRAIN] Analyzing Prompt: {text}")
    
    # SYSTEM PROMPT: Forces the LLM to extract entities correctly
    sys_msg = """You are a Travel Data Extractor. 
    Extract 'origin', 'destination', and 'duration' from the user prompt.
    - If the user mentions a country (e.g., Ireland), pick its capital or major city (e.g., Dublin).
    - If no duration is found, default to 3.
    - Return ONLY valid JSON: {"origin": "City", "destination": "City", "duration": 3}"""
    
    try:
        response = llm.invoke([("system", sys_msg), ("user", text)])
        data = json.loads(clean_json_response(response.content))
        origin = data.get("origin", "London")
        dest = data.get("destination", "Paris")
        duration = int(data.get("duration", 3))
    except Exception as e:
        print(f"⚠️ [PARSER FAIL] Falling back to Regex/Defaults: {e}")
        origin, dest, duration = "London", "Paris", 3

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

# --- 6. PLANNER ---
def planner_node(state: TripState) -> dict:
    dest = state['destination']
    days_count = int(state.get('duration_days', 1))
    real_pois = state.get('pois', [])
    
    found_flights = state.get('flights', [])
    selected_flight = found_flights[0] if found_flights else {
        "airline": "Global Carrier", "price_eur": 450, "outbound_price": 225, "return_price": 225, "type": "Market Estimate"
    }
    
    selected_hotel = state.get('hotels')[0] if state.get('hotels') else None
    poi_list = [p['name'] for p in real_pois] if real_pois else [f"{dest} Center", f"{dest} Old Town"]

    try:
        sys_msg = f"You are a Travel API. Return JSON with 'days' array of EXACTLY {days_count} elements."
        user_msg = f"Plan a {days_count}-day trip to {dest} using: {', '.join(poi_list[:6])}."
        response = llm.invoke([("system", sys_msg), ("user", user_msg)])
        plan = json.loads(clean_json_response(response.content))
    except:
        manual_days = []
        for i in range(days_count):
            day_pois = poi_list[i*2 : (i*2)+2] if i*2 < len(poi_list) else [poi_list[0]]
            manual_days.append({
                "day": i + 1,
                "theme": f"Exploring {dest} - Day {i+1}",
                "activities": [
                    {"name": f"Morning visit to {day_pois[0]}", "time": "09:30 AM", "cost_eur": 25},
                    {"name": f"Lunch in {dest}", "time": "01:00 PM", "cost_eur": 30},
                    {"name": f"Evening dinner near {day_pois[-1] if len(day_pois)>1 else dest}", "time": "07:30 PM", "cost_eur": 40}
                ]
            })
        plan = {"days": manual_days}

    return {"itinerary": plan, "selected_flight": selected_flight, "selected_hotel": selected_hotel}

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
        "selected_hotel": state.get("selected_hotel"),
        "total_cost_eur": state.get("total_cost_eur"), 
        "within_budget": state.get("within_budget"),
        "cost_breakdown": state.get("cost_breakdown"),
        "buffer_applied": state.get("buffer_applied"),
        "start_date": state.get("start_date"),
        "end_date": state.get("end_date"),
        "current_step": "final_itinerary"
    }