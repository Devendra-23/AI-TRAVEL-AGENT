import json
import os
import re
import requests
from datetime import datetime
from agent.state import TripState
from tools.flights import search_flights
from tools.hotels import search_hotels
from tools.weather import check_weather
from tools.maps import get_pois
from dotenv import load_dotenv

load_dotenv()

today_str = datetime.now().strftime("%Y-%m-%d")

# --- 1. DIRECT REST API PROXY ---
class DirectGemini:
    """Uses standard requests to hit the stable V1 production endpoint directly."""
    def invoke(self, messages):
        system_instr = messages[0][1] if messages[0][0] == "system" else ""
        user_prompt = messages[-1][1]
        
        api_key = os.getenv("GOOGLE_API_KEY")
        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"
        
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": f"INSTRUCTIONS: {system_instr}\n\nUSER REQUEST: {user_prompt}"}]
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 4096,
                "responseMimeType": "application/json" 
            }
        }

        try:
            response = requests.post(url, json=payload, timeout=90)
            if response.status_code != 200:
                print(f"❌ API Error: {response.text}")
                return type('obj', (object,), {'content': "{}"})
            
            data = response.json()
            ai_text = data['candidates'][0]['content']['parts'][0]['text']
            return type('obj', (object,), {'content': ai_text})
        except Exception as e:
            print(f"❌ REST Request Failed: {e}")
            return type('obj', (object,), {'content': "{}"})

llm = DirectGemini()

# --- UTILITIES ---
def get_coords(city_name: str):
    try:
        url = f"https://nominatim.openstreetmap.org/search?q={city_name}&format=json&limit=1"
        headers = {'User-Agent': 'TravelDev-Agent-Project'}
        resp = requests.get(url, headers=headers).json()
        if resp:
            return float(resp[0]['lat']), float(resp[0]['lon'])
    except: pass
    return 0.0, 0.0

def clean_json_response(content):
    content = str(content)
    content = re.sub(r'```json\s*|\s*```', '', content).strip()
    start = content.find('{')
    end = content.rfind('}')
    if start != -1 and end != -1:
        return content[start:end+1]
    return content

# --- 2. NODES ---

def parse_input_node(state: TripState) -> dict:
    text = state['user_prompt']
    sys_msg = "Extract origin, destination, and duration. Return ONLY JSON: {\"origin\": \"City\", \"destination\": \"City\", \"duration\": 3}"
    try:
        response = llm.invoke([("system", sys_msg), ("user", text)])
        data = json.loads(clean_json_response(response.content))
        origin = data.get("origin", "London")
        dest = data.get("destination", "")
        duration = int(data.get("duration", 3))
        
        if not dest:
            words = text.strip().split()
            dest = words[-1].replace('?', '').capitalize() if words else ""

        o_lat, o_lng = get_coords(origin)
        d_lat, d_lng = get_coords(dest)

        return {
            "destination": dest, "origin_city": origin,
            "origin_lat": o_lat, "origin_lng": o_lng,
            "destination_lat": d_lat, "destination_lng": d_lng,
            "duration_days": duration, "start_date": state.get('start_date') or today_str,
            "end_date": state.get('end_date') or today_str, "current_step": "parsed", "errors": [] 
        }
    except Exception as e:
        return {"errors": [str(e)], "current_step": "error"}

def search_flights_node(state: TripState) -> dict:
    return {"flights": search_flights(state['origin_city'], state['destination'], state['start_date'], state['end_date'])}

def search_hotels_node(state: TripState) -> dict:
    return {"hotels": search_hotels(state['destination'], state['duration_days'], state['start_date'], state['end_date'])}

def check_weather_node(state: TripState) -> dict:
    return {"weather": check_weather(state['destination'])}

def get_pois_node(state: TripState) -> dict:
    return {"pois": get_pois(state['destination'])}

def planner_node(state: TripState) -> dict:
    dest = state['destination']
    days_count = int(state.get('duration_days', 1))
    
    flights = state.get('flights', [])
    hotels = state.get('hotels', [])
    pois = state.get('pois', [])
    
    # Critical: Use existing selection if present, otherwise grab first result
    top_flight = state.get('selected_flight') or (flights[0] if flights else {"airline": "Global Carrier", "price_eur": 450, "booking_url": "#"})
    top_hotel = state.get('selected_hotel') or (hotels[0] if hotels else {"name": "Local Stay", "price_per_night_eur": 120, "booking_url": "#"})

    poi_list = ", ".join([p['name'] for p in pois[:10]]) if pois else "Main attractions"

    sys_msg = f"""You are Atlas, a travel AI. Create a {days_count}-day itinerary for {dest}.
    Landmarks to use: {poi_list}
    
    Return ONLY a JSON object.
    SCHEMA:
    {{
      "days": [
        {{
          "day": 1,
          "theme": "Creative title",
          "activities": [
            {{ "name": "...", "description": "...", "cost_eur": 15, "search_link": "..." }}
          ]
        }}
      ]
    }}"""
    
    user_msg = f"JSON Itinerary for {dest}, {days_count} days."

    try:
        response = llm.invoke([("system", sys_msg), ("user", user_msg)])
        raw_plan = json.loads(clean_json_response(response.content))
        
        # FORCED STANDARDIZATION:
        # We ensure 'days' is always the top-level key inside the dictionary
        if isinstance(raw_plan, dict):
            if "itinerary" in raw_plan:
                plan = raw_plan["itinerary"]
            elif "days" in raw_plan:
                plan = raw_plan
            else:
                plan = {"days": []}
        else:
            plan = {"days": []}

    except Exception as e:
        plan = {"days": [{"day": 1, "theme": "Arrival", "activities": []}]}

    return {
        "itinerary": plan, # This matches TripState
        "selected_flight": top_flight, 
        "selected_hotel": top_hotel,
        "current_step": "planned"
    }

    # PERSISTENCE: Returning the selected items ensures budget calculation works
    return {
        "itinerary": plan, 
        "selected_flight": top_flight, 
        "selected_hotel": top_hotel,
        "current_step": "planned"
    }

def budget_check_node(state: TripState) -> dict:
    import utils.budget as budget_module
    return budget_module.calculate_total_cost(state)

def compile_itinerary_node(state: TripState) -> dict:
    return {**state, "current_step": "final_itinerary"}