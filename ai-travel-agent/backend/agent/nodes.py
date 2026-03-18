import json
import os
from datetime import datetime
from langchain_google_genai import ChatGoogleGenerativeAI
from agent.state import TripState
from tools.flights import search_flights
from tools.hotels import search_hotels
from tools.weather import check_weather
from tools.maps import get_pois
from dotenv import load_dotenv

load_dotenv()

# Initialize Gemini 2.5 Flash
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash", 
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0
)

def clean_json_response(response_content):
    content = response_content
    if isinstance(content, list):
        content = "".join([part if isinstance(part, str) else part.get("text", "") for part in content])
    start_idx = content.find('{')
    end_idx = content.rfind('}')
    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
        return content[start_idx:end_idx + 1]
    return content.replace('```json', '').replace('```', '').strip()

# --- 1. PARSE INPUT ---
def parse_input_node(state: TripState) -> dict:
    print(f"🧠 [AI BRAIN] Analyzing user prompt: {state['user_prompt']}")

    # Added explicit date context so Gemini knows what "next week" means relative to today
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    prompt = f"""
    You are a professional travel geocoder. Extract details from: '{state['user_prompt']}'.
    Today's Date: {today_str}.
    
    CRITICAL INSTRUCTIONS:
    1. If the user provides a COUNTRY (e.g. Norway, Spain), you MUST pick the CAPITAL CITY.
    2. Convert cities to 3-letter IATA codes (e.g. Oslo=OSL, London=LHR, Newcastle=NCL).
    3. Provide accurate GPS coordinates for the globe.
    4. If dates are missing, assume a 5-day trip starting 1 month from today.
    
    Return ONLY JSON with these exact keys:
    - destination (City Name)
    - origin_city (City Name)
    - destination_iata (3-letter code)
    - origin_iata (3-letter code)
    - destination_lat, destination_lng (floats)
    - origin_lat, origin_lng (floats)
    - start_date, end_date (YYYY-MM-DD)
    - trip_type ('round-trip' or 'one-way')
    - budget_eur (number)
    """
    
    try:
        response = llm.invoke(prompt)
        parsed = json.loads(clean_json_response(response.content))
    except Exception as e:
        print(f"🚨 [AI BRAIN] Extraction failed: {e}")
        parsed = {}

    # Meticulous duration calculation
    try:
        s_date = parsed.get('start_date') or state.get('start_date')
        e_date = parsed.get('end_date') or state.get('end_date')
        d1 = datetime.strptime(s_date, "%Y-%m-%d")
        d2 = datetime.strptime(e_date, "%Y-%m-%d")
        duration = max(1, abs((d2 - d1).days))
    except:
        duration = 5

    return {
        "destination": parsed.get('destination') or "Stockholm",
        "origin_city": parsed.get('origin_city') or "Oslo",
        "destination_iata": parsed.get('destination_iata') or "ARN",
        "origin_iata": parsed.get('origin_iata') or "OSL",
        "destination_lat": float(parsed.get('destination_lat') or 59.3293),
        "destination_lng": float(parsed.get('destination_lng') or 18.0686),
        "origin_lat": float(parsed.get('origin_lat') or 59.9139),
        "origin_lng": float(parsed.get('origin_lng') or 10.7522),
        "start_date": parsed.get('start_date') or state.get('start_date'),
        "end_date": parsed.get('end_date') or state.get('end_date'),
        "trip_type": parsed.get('trip_type') or state.get('trip_type') or "round-trip",
        "duration_days": duration,
        "budget_usd": float(parsed.get('budget_eur') or 2000.0),
        "current_step": "parse_input"
    }

# --- 2. SEARCH FLIGHTS ---
def search_flights_node(state: TripState) -> dict:
    # FIXED: Removed hardcoded 'LHR'/'MAD'. Now uses the dynamic state from AI Brain.
    o_iata = state.get('origin_iata')
    d_iata = state.get('destination_iata')
    s_date = state.get('start_date')
    e_date = state.get('end_date')
    t_type = state.get('trip_type', 'round-trip')

    print(f"🛫 [AGENCY] Routing: {o_iata} -> {d_iata}")
    
    flights = search_flights(o_iata, d_iata, s_date, e_date, t_type)
    return {"flights": flights, "current_step": "search_flights"}

# --- 3. SEARCH HOTELS ---
def search_hotels_node(state: TripState) -> dict:
    # Meticulous night calculation to ensure API success
    try:
        d1 = datetime.strptime(state['start_date'], "%Y-%m-%d")
        d2 = datetime.strptime(state['end_date'], "%Y-%m-%d")
        actual_nights = abs((d2 - d1).days)
    except:
        actual_nights = state.get('duration_days', 3)

    hotels = search_hotels(
        state['destination'], 
        actual_nights, 
        state['start_date'], 
        state['end_date']
    )
    return {"hotels": hotels, "current_step": "search_hotels"}

# --- 4. WEATHER ---
def check_weather_node(state: TripState) -> dict:
    return {"weather": check_weather(state['destination']), "current_step": "check_weather"}

# --- 5. POIs ---
def get_pois_node(state: TripState) -> dict:
    return {"pois": get_pois(state['destination']), "current_step": "get_pois"}

# --- 6. PLANNER ---
def planner_node(state: TripState) -> dict:
    # Senior Concierge creates the daily roadmap
    system_prompt = (
        "You are a senior European travel concierge. "
        "Create a detailed daily itinerary. Output strictly JSON. "
        "Structure: {'days': [{'day': 1, 'theme': '...', 'activities': [{'time': '09:00', 'name': '...', 'cost_eur': 20}]}]}"
    )
    user_msg = f"Plan a {state['duration_days']}-day trip to {state['destination']}. Budget: {state['budget_usd']} EUR."
    
    try:
        response = llm.invoke([("system", system_prompt), ("user", user_msg)])
        plan = json.loads(clean_json_response(response.content))
    except:
        plan = {"days": []}

    return {
        "itinerary": plan,
        "selected_flight": state['flights'][0] if state.get('flights') else None,
        "selected_hotel": state['hotels'][0] if state.get('hotels') else None,
        "current_step": "planner"
    }

# --- 7. BUDGET AUDIT ---
def budget_check_node(state: TripState) -> dict:
    # This node ensures the 'total_cost_eur' key is populated for the frontend
    from utils.budget import calculate_total_cost
    result = calculate_total_cost(state)
    return result

# --- 8. FINAL COMPILATION ---
def compile_itinerary_node(state: TripState) -> dict:
    # Returns the full state including total_cost_eur and coordinates for the UI
    return {
        "destination_lat": state.get("destination_lat"),
        "destination_lng": state.get("destination_lng"),
        "origin_lat": state.get("origin_lat"),
        "origin_lng": state.get("origin_lng"),
        "destination": state.get("destination"),
        "total_cost_eur": state.get("total_cost_eur"), 
        "current_step": "final_itinerary"
    }