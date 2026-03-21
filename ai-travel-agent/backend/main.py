from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langgraph.graph import StateGraph, END
import uvicorn
import os
from typing import Optional

# Importing your logic
from agent.state import TripState
from agent.nodes import (
    parse_input_node, search_flights_node, search_hotels_node,
    check_weather_node, get_pois_node, planner_node,
    budget_check_node, compile_itinerary_node
)

app = FastAPI(title="TravelDev AI Agent GDS")

# --- CORS CONFIGURATION ---
# Authorized to allow your specific Vercel Frontend and local testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://ai-travel-agent-mu.vercel.app", 
        "http://localhost:5173",  # Vite Local
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 1. STATE INITIALIZATION ---
def create_initial_state(user_prompt: str, start_date: str = "", end_date: str = "") -> dict:
    """Initializes the dictionary with all keys defined in TripState."""
    return {
        'user_prompt': user_prompt,
        'current_step': 'start',
        'destination': "",
        'origin_city': "",
        'origin_iata': "",
        'destination_iata': "",
        'start_date': start_date, 
        'end_date': end_date,     
        'duration_days': 0,
        'trip_type': "leisure",
        'search_airport_city': None,
        'destination_lat': 0.0,
        'destination_lng': 0.0,
        'origin_lat': 0.0,
        'origin_lng': 0.0,
        'flights': [],
        'hotels': [],
        'weather': {},
        'pois': [],
        'itinerary': {},
        'selected_flight': {}, 
        'selected_hotel': {},  
        'total_cost_eur': 0,
        'budget_usd': 2000.0,
        'within_budget': True,
        'messages': [],
        'errors': [],
        # --- FIXED: Added missing keys to match updated state.py ---
        'cost_breakdown': {},
        'buffer_applied': 0.0
    }

# --- 2. GRAPH DEFINITION ---
workflow = StateGraph(TripState)

# Nodes (Names must be unique and separate from State keys)
workflow.add_node("parser", parse_input_node)
workflow.add_node("fetch_flights", search_flights_node)
workflow.add_node("fetch_hotels", search_hotels_node)
workflow.add_node("fetch_weather", check_weather_node) 
workflow.add_node("fetch_pois", get_pois_node)        
workflow.add_node("planner", planner_node)
workflow.add_node("budget_audit", budget_check_node)   
workflow.add_node("compiler", compile_itinerary_node)

# Flow
workflow.set_entry_point("parser")
workflow.add_edge("parser", "fetch_flights")
workflow.add_edge("fetch_flights", "fetch_hotels")
workflow.add_edge("fetch_hotels", "fetch_weather")
workflow.add_edge("fetch_weather", "fetch_pois")
workflow.add_edge("fetch_pois", "planner")
workflow.add_edge("planner", "budget_audit")
workflow.add_edge("budget_audit", "compiler")
workflow.add_edge("compiler", END)

# Compile
travel_agent = workflow.compile()

# --- 3. API ENDPOINTS ---
class PlanRequest(BaseModel):
    prompt: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None

@app.post("/plan")
async def generate_plan(request: PlanRequest):
    print(f"🚀 [API] Production Request Received: {request.prompt}")
    
    # Initialize state with all required fields
    initial_state = create_initial_state(
        request.prompt, 
        request.start_date or "", 
        request.end_date or ""
    )
    
    try:
        # Run the LangGraph
        # This will now succeed because the 'cost_breakdown' key exists
        final_state = travel_agent.invoke(initial_state)
        return final_state
    except Exception as e:
        print(f"❌ [GRAPH ERROR] {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Agent Execution Failed: {str(e)}")

@app.get("/health")
@app.get("/")
async def root():
    return {
        "status": "online", 
        "agent": "TravelDev GDS v1.0", 
        "deployment": "Fly.io",
        "authorized_origin": "https://ai-travel-agent-mu.vercel.app"
    }

if __name__ == "__main__":
    # Fly.io environment port
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)