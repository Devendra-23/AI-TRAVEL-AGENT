import json, os, re, requests
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
        payload = {"contents": [{"role": "user", "parts": [{"text": f"INSTRUCTIONS: {system_instr}\n\nUSER REQUEST: {user_prompt}"}]}],
                   "generationConfig": {"temperature": 0.2, "maxOutputTokens": 4096, "responseMimeType": "application/json"}}
        try:
            resp = requests.post(url, json=payload, timeout=60).json()
            return type('obj', (object,), {'content': resp['candidates'][0]['content']['parts'][0]['text']})
        except: return type('obj', (object,), {'content': "{}"})

llm = DirectGemini()

def get_coords(city_name):
    try:
        resp = requests.get(f"https://nominatim.openstreetmap.org/search?q={city_name}&format=json&limit=1", headers={'User-Agent': 'TravelDev'}, timeout=10).json()
        return (float(resp[0]['lat']), float(resp[0]['lon'])) if resp else (0.0, 0.0)
    except: return 0.0, 0.0

def clean_json_response(content):
    content = str(content)
    content = re.sub(r'```json\s*|\s*```', '', content).strip()
    start, end = content.find('{'), content.rfind('}')
    return content[start:end+1] if start != -1 and end != -1 else content

def parse_input_node(state: TripState) -> dict:
    sys_msg = "Return ONLY JSON: {\"origin\": \"City\", \"destination\": \"City\", \"duration\": 3}"
    try:
        resp = llm.invoke([("system", sys_msg), ("user", state['user_prompt'])])
        data = json.loads(clean_json_response(resp.content))
        origin, dest = data.get("origin", "Dublin"), data.get("destination", "Madrid")
        o_lat, o_lng = get_coords(origin)
        d_lat, d_lng = get_coords(dest)
        
        # CRITICAL: Maps variables specifically for the Globe
        return {
            "origin_city": origin, "destination": dest, 
            "origin_lat": o_lat, "origin_lng": o_lng, 
            "destination_lat": d_lat, "destination_lng": d_lng, 
            "duration_days": int(data.get("duration", 2)), 
            "current_step": "parsed"
        }
    except: return {"errors": ["Parsing failed"], "current_step": "error"}

def search_flights_node(state: TripState) -> dict:
    return {"flights": search_flights(state['origin_city'], state['destination'], state['start_date'], state['end_date'])}

def search_hotels_node(state: TripState) -> dict:
    return {"hotels": search_hotels(state['destination'], state['duration_days'], state['start_date'], state['end_date'])}

def check_weather_node(state: TripState) -> dict:
    try: return {"weather": check_weather(state['destination'])}
    except: return {"weather": {"temp": "Mild", "condition": "Clear"}}

def get_pois_node(state: TripState) -> dict:
    return {"pois": get_pois(state['destination'])}

def planner_node(state: TripState) -> dict:
    flights, hotels = state.get('flights', []), state.get('hotels', [])
    top_flight = flights[0] if flights else {"airline": "Carrier", "price_eur": 250}
    top_hotel = hotels[0] if hotels else {"name": "Hotel", "price_per_night_eur": 120}
    
    sys_msg = f"Create a {state['duration_days']}-day JSON itinerary for {state['destination']}. SCHEMA: {{\"days\": [{{\"day\": 1, \"theme\": \"Title\", \"activities\": [{{\"name\": \"...\", \"description\": \"...\", \"cost_eur\": 10}}]}}]}}"
    
    try:
        resp = llm.invoke([("system", sys_msg), ("user", f"Plan {state['destination']}")])
        plan = json.loads(clean_json_response(resp.content))
        if "itinerary" in plan: plan = plan["itinerary"]
        if "days" not in plan: plan = {"days": plan} if isinstance(plan, list) else {"days": []}
    except: plan = {"days": []}
    
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