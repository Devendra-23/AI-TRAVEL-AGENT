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

class DirectGemini:
    def invoke(self, messages):
        system_instr = messages[0][1] if messages[0][0] == "system" else ""
        user_prompt = messages[-1][1]
        api_key = os.getenv("GOOGLE_API_KEY")
        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"
        
        payload = {
            "contents": [{"role": "user", "parts": [{"text": f"INSTRUCTIONS: {system_instr}\n\nUSER REQUEST: {user_prompt}"}]}],
            "generationConfig": {"temperature": 0.2, "maxOutputTokens": 4096, "responseMimeType": "application/json"}
        }
        try:
            response = requests.post(url, json=payload, timeout=90)
            if response.status_code != 200: return type('obj', (object,), {'content': "{}"})
            data = response.json()
            return type('obj', (object,), {'content': data['candidates'][0]['content']['parts'][0]['text']})
        except: return type('obj', (object,), {'content': "{}"})

llm = DirectGemini()

def get_coords(city_name: str):
    try:
        url = f"https://nominatim.openstreetmap.org/search?q={city_name}&format=json&limit=1"
        resp = requests.get(url, headers={'User-Agent': 'TravelDev'}, timeout=10).json()
        if resp: return float(resp[0]['lat']), float(resp[0]['lon'])
    except: pass
    return 0.0, 0.0

def clean_json_response(content):
    content = str(content)
    content = re.sub(r'```json\s*|\s*```', '', content).strip()
    start, end = content.find('{'), content.rfind('}')
    return content[start:end+1] if start != -1 and end != -1 else content

def parse_input_node(state: TripState) -> dict:
    text = state['user_prompt']
    sys_msg = "Return ONLY JSON: {\"origin\": \"City\", \"destination\": \"City\", \"duration\": 3}"
    try:
        response = llm.invoke([("system", sys_msg), ("user", text)])
        data = json.loads(clean_json_response(response.content))
        origin, dest = data.get("origin", "London"), data.get("destination", "")
        duration = int(data.get("duration", 3))
        if not dest: dest = text.strip().split()[-1].replace('?', '').capitalize()
        o_lat, o_lng = get_coords(origin)
        d_lat, d_lng = get_coords(dest)
        return {
            "destination": dest, "origin_city": origin,
            "origin_lat": o_lat, "origin_lng": o_lng,
            "destination_lat": d_lat, "destination_lng": d_lng,
            "duration_days": duration, "current_step": "parsed"
        }
    except: return {"errors": ["Parsing failed"], "current_step": "error"}

def search_flights_node(state: TripState) -> dict:
    return {"flights": search_flights(state['origin_city'], state['destination'], state['start_date'], state['end_date'])}

def search_hotels_node(state: TripState) -> dict:
    return {"hotels": search_hotels(state['destination'], state['duration_days'], state['start_date'], state['end_date'])}

def get_pois_node(state: TripState) -> dict:
    return {"pois": get_pois(state['destination'])}

def planner_node(state: TripState) -> dict:
    dest, days_count = state['destination'], int(state.get('duration_days', 1))
    flights, hotels, pois = state.get('flights', []), state.get('hotels', []), state.get('pois', [])
    
    top_flight = state.get('selected_flight') or (flights[0] if flights else {"airline": "Global Carrier", "price_eur": 450})
    top_hotel = state.get('selected_hotel') or (hotels[0] if hotels else {"name": "Local Stay", "price_per_night_eur": 120})
    poi_list = ", ".join([p['name'] for p in pois[:10]]) if pois else "Main attractions"

    sys_msg = f"Create a {days_count}-day JSON itinerary for {dest}. Include: {poi_list}. Return JSON with a 'days' array."
    user_msg = f"Itinerary for {dest}"

    try:
        response = llm.invoke([("system", sys_msg), ("user", user_msg)])
        raw_plan = json.loads(clean_json_response(response.content))
        # Standardize structure
        if "itinerary" in raw_plan: plan = raw_plan["itinerary"]
        elif "days" in raw_plan: plan = raw_plan
        else: plan = {"days": raw_plan} if isinstance(raw_plan, list) else {"days": []}
    except:
        plan = {"days": [{"day": 1, "theme": "Arrival", "activities": []}]}

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