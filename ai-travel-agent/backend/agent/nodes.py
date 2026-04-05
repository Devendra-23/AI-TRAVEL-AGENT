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

# --- 1. DIRECT REST API PROXY (BYPASSES ALL LIBRARY ERRORS) ---
class DirectGemini:
    """Uses standard requests to ensure we hit the stable V1 production endpoint."""
    def invoke(self, messages):
        # Extract prompts from the list format
        system_instr = messages[0][1] if messages[0][0] == "system" else ""
        user_prompt = messages[-1][1]
        
        api_key = os.getenv("GOOGLE_API_KEY")
        # FORCE the stable v1 URL - no library can change this
        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"
        
        payload = {
            "contents": [{
                "parts": [{"text": f"SYSTEM INSTRUCTIONS:\n{system_instr}\n\nUSER REQUEST:\n{user_prompt}"}]
            }],
            "generationConfig": {
                "temperature": 0.1,
                "maxOutputTokens": 4096,
                "responseMimeType": "application/json" # Ensures Gemini returns clean JSON
            }
        }

        try:
            response = requests.post(url, json=payload, timeout=90)
            if response.status_code != 200:
                print(f"❌ API Error: {response.text}")
                return type('obj', (object,), {'content': "{}"})
            
            data = response.json()
            ai_text = data['candidates'][0]['content']['parts'][0]['text']
            
            # Return an object that has a .content attribute to keep the nodes working
            return type('obj', (object,), {'content': ai_text})
        except Exception as e:
            print(f"❌ REST Request Failed: {e}")
            return type('obj', (object,), {'content': "{}"})

# Initialize the REST proxy
llm = DirectGemini()

# --- UTILITY FUNCTIONS ---
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
    sys_msg = """You are a Travel Intelligence Engine. 
    Map countries to capital cities. Return ONLY JSON: {"origin": "City", "destination": "City", "duration": 3}"""
    
    try:
        response = llm.invoke([("system", sys_msg), ("user", text)])
        data = json.loads(clean_json_response(response.content))
        origin, dest = data.get("origin", ""), data.get("destination", "")
        duration = int(data.get("duration", 3))

        if not dest: return {"errors": ["No destination found."], "current_step": "error"}

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
    
    top_flight = flights[0] if flights else {"airline": "Global Carrier", "price_eur": 450, "booking_url": "#"}
    top_hotel = hotels[0] if hotels else {"name": "Local Stay", "price_per_night_eur": 120, "booking_url": "#"}

    sys_msg = f"""You are 'Atlas', an elite AI Travel Concierge specialized in {dest}.
    
    ### OBJECTIVE:
    Create a highly logical, {days_count}-day itinerary. Group activities by proximity.
    
    ### CONTEXT DATA:
    - FLIGHT: {top_flight['airline']} at €{top_flight['price_eur']}.
    - HOTEL: {top_hotel['name']} at €{top_hotel['price_per_night_eur']}/night.
    - LOCAL SIGHTS: {', '.join([p['name'] for p in pois[:5]])}.

    ### OUTPUT RULES:
    1. Return ONLY valid JSON. 
    2. For every activity, include 'name', 'description', 'cost_eur' (int), and 'search_link'.
    
    ### JSON STRUCTURE:
    {{
      "days": [
        {{
          "day": 1,
          "theme": "Title for the day's vibe",
          "activities": [
            {{ "name": "...", "description": "...", "cost_eur": 0, "search_link": "..." }}
          ]
        }}
      ]
    }}
    """
    
    user_msg = f"Create a {days_count}-day itinerary for {dest}. Use real prices from context."

    try:
        response = llm.invoke([("system", sys_msg), ("user", user_msg)])
        plan = json.loads(clean_json_response(response.content))
    except:
        plan = {"days": [{"day": 1, "activities": [{"name": f"Explore {dest}", "cost_eur": 0, "search_link": "#"}]}]}

    return {
        "itinerary": plan, 
        "selected_flight": top_flight, 
        "selected_hotel": top_hotel
    }

def budget_check_node(state: TripState) -> dict:
    import utils.budget as budget_module
    return budget_module.calculate_total_cost(state)

def compile_itinerary_node(state: TripState) -> dict:
    return {**state, "current_step": "final_itinerary"}