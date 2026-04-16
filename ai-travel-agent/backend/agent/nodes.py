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
    prompt_text = state.get('user_prompt', '')
    
    # Stronger Prompt: Tell Gemini explicitly to ignore the duration text
    sys_msg = """Extract the origin and destination cities. Ignore numbers, dates, or durations.
    Example 1: 'Dublin to Oslo for 2 days' -> {"origin": "Dublin", "destination": "Oslo"}
    Example 2: 'Flights from Paris to Rome' -> {"origin": "Paris", "destination": "Rome"}
    Return ONLY JSON."""
    
    try:
        resp = llm.invoke([("system", sys_msg), ("user", prompt_text)])
        data = json.loads(clean_json_response(resp.content))
        
        origin = data.get("origin", "").strip()
        dest = data.get("destination", "").strip()
        
        # Python Fallback: Smarter cleanup
        if origin.lower() in ["city", "", "unknown"] or dest.lower() in ["city", "", "unknown"]:
            if " to " in prompt_text.lower():
                parts = prompt_text.lower().split(" to ")
                origin = parts[0].replace('flights from', '').strip().title()
                raw_dest = parts[1].replace('?', '').strip().lower()
                
                # Chop off "for 2 days" if it exists in the destination string
                if " for " in raw_dest:
                    dest = raw_dest.split(" for ")[0].strip().title()
                else:
                    dest = raw_dest.title()

        # 1. DYNAMIC DURATION
        try:
            start_dt = datetime.strptime(state['start_date'], "%Y-%m-%d")
            end_dt = datetime.strptime(state['end_date'], "%Y-%m-%d")
            duration = max(1, (end_dt - start_dt).days)
        except:
            duration = 3
            
        # 2. SMART ERRORS
        if not origin or origin.lower() in ["city", "unknown", "none", ""]:
            return {"errors": ["Please specify your starting city (e.g., 'Dublin to Oslo')."], "current_step": "error"}
            
        if not dest or dest.lower() in ["city", "unknown", "none", ""]:
            return {"errors": ["Please specify your destination (e.g., 'Trip to Norway')."], "current_step": "error"}

        # 3. REALITY CHECK
        o_lat, o_lng = get_coords(origin)
        d_lat, d_lng = get_coords(dest)
        
        if o_lat == 0.0 and o_lng == 0.0:
            return {"errors": [f"We couldn't locate the origin city '{origin}'. Check spelling."], "current_step": "error"}
            
        if d_lat == 0.0 and d_lng == 0.0:
            return {"errors": [f"We couldn't locate the destination city '{dest}'. Check spelling."], "current_step": "error"}
        
        print(f"🌍 [DYNAMIC ROUTING] {origin} to {dest} for {duration} days.")
        
        return {
            "origin_city": origin, 
            "destination": dest, 
            "origin_lat": o_lat, 
            "origin_lng": o_lng, 
            "destination_lat": d_lat, 
            "destination_lng": d_lng, 
            "duration_days": duration, 
            "current_step": "parsed"
        }
    except Exception as e: 
        print(f"❌ [PARSE ERROR] {e}")
        return {"errors": ["Could not understand the route. Try 'Dublin to Oslo'."], "current_step": "error"}

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
    flights, hotels, pois = state.get('flights', []), state.get('hotels', []), state.get('pois', [])
    
    top_flight = flights[0] if flights else {"airline": "Global Carrier", "price_eur": 250}
    top_hotel = hotels[0] if hotels else {"name": "Local Stay", "price_per_night_eur": 120}
    
    # Extract real places from your Maps API tool
    poi_names = ", ".join([p.get('name', '') for p in pois[:15]]) if pois else "top local attractions"
    
    # Aggressive Prompt to force real data
    sys_msg = f"""You are an expert travel agent. Create a realistic {state.get('duration_days', 2)}-day itinerary for {state['destination']}.
    CRITICAL: You MUST use these real places in your itinerary: {poi_names}.
    
    Return ONLY a raw JSON object. NO markdown, NO backticks.
    SCHEMA:
    {{
      "days": [
        {{
          "day": 1,
          "theme": "Exploring History",
          "activities": [
            {{ "name": "Real Place Name", "description": "What to do here.", "time": "10:00 AM", "cost_eur": 25 }}
          ]
        }}
      ]
    }}"""
    
    try:
        resp = llm.invoke([("system", sys_msg), ("user", f"Give me the JSON itinerary for {state['destination']}.")])
        plan = json.loads(clean_json_response(resp.content))
        
        if "itinerary" in plan: plan = plan["itinerary"]
        if "days" not in plan: plan = {"days": plan} if isinstance(plan, list) else {"days": []}
        if len(plan["days"]) == 0: raise ValueError("Empty itinerary")
            
    except Exception as e:
        print(f"❌ [ITINERARY ERROR] {e}")
        # Keeping the fallback just in case the API goes down
        plan = {"days": [{"day": 1, "theme": f"Discover {state['destination']}", "activities": [{"name": "City Center Walk", "time": "10:00 AM", "description": "Explore the main squares.", "cost_eur": 0}]}]}
    
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