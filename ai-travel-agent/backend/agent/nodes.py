import json
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from agent.state import TripState
from tools.flights import search_flights
from tools.hotels import search_hotels
from tools.weather import check_weather
from tools.maps import get_pois

# Initialize Gemini 3
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite", # 1,000 requests/day vs 20
    temperature=0
)


def clean_json_response(response_content):
    """Helper to handle Gemini list-type responses and strip conversational text."""
    content = response_content
    
    # Handle list of parts if returned
    if isinstance(content, list):
        content = "".join([part if isinstance(part, str) else part.get("text", "") for part in content])
    
    # THE FIX: Find the first '{' and the last '}' to strip conversational filler
    start_idx = content.find('{')
    end_idx = content.rfind('}')
    
    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
        # Extract strictly what is between the braces
        return content[start_idx:end_idx + 1]
    
    # Fallback just in case
    return content.replace('```json', '').replace('```', '').strip()

def parse_input_node(state: TripState) -> dict:
    """Uses Gemini to extract structured data from user prompt."""
    prompt = f"""
    Extract travel details from this request: '{state['user_prompt']}'
    Return ONLY a JSON object with these exact keys:
    {{
        "destination": "city name",
        "origin_city": "assume 'New York' if not specified",
        "duration_days": 3,
        "budget_usd": 2000.0
    }}
    """
    response = llm.invoke(prompt)
    content = clean_json_response(response.content)
    
    try:
        parsed = json.loads(content)
    except Exception:
        parsed = {}

    # --- THE FIX: Safely extract values before converting ---
    raw_budget = parsed.get('budget_usd')
    # If it's None or missing, set to 2000.0; otherwise convert to float
    safe_budget = float(raw_budget) if raw_budget is not None else 2000.0
    
    raw_days = parsed.get('duration_days')
    safe_days = int(raw_days) if raw_days is not None else 3

    return {
        "destination": parsed.get('destination', 'Unknown'),
        "origin_city": parsed.get('origin_city', 'New York'),
        "duration_days": safe_days,
        "budget_usd": safe_budget,
        "current_step": "parse_input"
    }

def search_flights_node(state: TripState) -> dict:
    flights = search_flights(state['origin_city'], state['destination'], state['duration_days'])
    return {"flights": flights, "current_step": "search_flights"}

def search_hotels_node(state: TripState) -> dict:
    hotels = search_hotels(state['destination'], state['duration_days'])
    return {"hotels": hotels, "current_step": "search_hotels"}

def check_weather_node(state: TripState) -> dict:
    weather = check_weather(state['destination'])
    return {"weather": weather, "current_step": "check_weather"}

def get_pois_node(state: TripState) -> dict:
    pois = get_pois(state['destination'])
    return {"pois": pois, "current_step": "get_pois"}

def planner_node(state: TripState) -> dict:
    print(f"🤖 Gemini is crafting your itinerary for {state['destination']}... (this may take a moment)")

    system_prompt = "You are a travel planning expert. Build a JSON itinerary based on provided data. Output strictly JSON and absolutely no other text."
    
    user_msg = f"""
    Plan a {state['duration_days']}-day trip to {state['destination']}.
    Budget: ${state['budget_usd']}
    Flights: {json.dumps(state['flights'][:3])}
    Hotels: {json.dumps(state['hotels'][:3])}
    Weather: {json.dumps(state['weather'])}
    Attractions: {json.dumps(state['pois'])}

    Return JSON with this exact structure:
    {{
      "selected_flight_index": 0,
      "selected_hotel_index": 0,
      "days": [
        {{ "day": 1, "theme": "...", "activities": [{{ "time": "09:00", "name": "...", "cost_usd": 0 }}] }}
      ]
    }}
    """
    
    response = llm.invoke([("system", system_prompt), ("user", user_msg)])
    content = clean_json_response(response.content)
    
    # THE FIX: Add a try/except block so a bad JSON string doesn't crash the server
    try:
        plan = json.loads(content)
    except Exception as e:
        print(f"⚠️ JSON Parsing Failed! Raw LLM Output: {content}")
        # Provide a safe fallback so the frontend still receives data
        plan = {
            "selected_flight_index": 0,
            "selected_hotel_index": 0,
            "days": []
        }
    
    return {
        "itinerary": plan,
        "selected_flight": state['flights'][plan.get('selected_flight_index', 0)] if state['flights'] else None,
        "selected_hotel": state['hotels'][plan.get('selected_hotel_index', 0)] if state['hotels'] else None,
        "current_step": "planner"
    }
def budget_check_node(state: TripState) -> dict:
    from utils.budget import calculate_total_cost
    return calculate_total_cost(state)

def compile_itinerary_node(state: TripState) -> dict:
    return {"current_step": "compile_itinerary"}