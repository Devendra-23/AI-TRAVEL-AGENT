from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langgraph.graph import StateGraph, END
import uvicorn
import os

# Importing your logic
from agent.state import TripState
from agent.nodes import (
    parse_input_node, search_flights_node, search_hotels_node,
    check_weather_node, get_pois_node, planner_node,
    budget_check_node, compile_itinerary_node
)

app = FastAPI(title="TravelDev AI Agent GDS")

# --- CORS CONFIGURATION ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 1. STATE INITIALIZATION ---
def create_initial_state(user_prompt: str) -> dict:
    return {
        'user_prompt': user_prompt,
        'current_step': 'start',
        'destination': "",
        'origin_city': "",
        'origin_iata': "",
        'destination_iata': "",
        'start_date': "",
        'end_date': "",
        'duration_days': 0,
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
        'errors': []
    }

# --- 2. GRAPH DEFINITION ---
workflow = StateGraph(TripState)

# Add nodes with UNIQUE names (different from State attributes)
workflow.add_node("parser", parse_input_node)
workflow.add_node("fetch_flights", search_flights_node)
workflow.add_node("fetch_hotels", search_hotels_node)
workflow.add_node("fetch_weather", check_weather_node) # Renamed from 'weather'
workflow.add_node("fetch_pois", get_pois_node)        # Renamed from 'pois'
workflow.add_node("planner", planner_node)
workflow.add_node("budget_check", budget_check_node)   # Renamed from 'budget'
workflow.add_node("compiler", compile_itinerary_node)

# Set the flow (Edges)
workflow.set_entry_point("parser")
workflow.add_edge("parser", "fetch_flights")
workflow.add_edge("fetch_flights", "fetch_hotels")
workflow.add_edge("fetch_hotels", "fetch_weather")
workflow.add_edge("fetch_weather", "fetch_pois")
workflow.add_edge("fetch_pois", "planner")
workflow.add_edge("planner", "budget_check")
workflow.add_edge("budget_check", "compiler")
workflow.add_edge("compiler", END)

# Compile the Agent
travel_agent = workflow.compile()

# --- 3. API ENDPOINTS ---
class PlanRequest(BaseModel):
    prompt: str

@app.post("/plan")
async def generate_plan(request: PlanRequest):
    print(f"🚀 [API] Starting Journey for: {request.prompt}")
    initial_state = create_initial_state(request.prompt)
    
    try:
        # Run the LangGraph synchronously
        final_state = travel_agent.invoke(initial_state)
        return final_state
    except Exception as e:
        print(f"❌ [GRAPH ERROR] {e}")
        raise HTTPException(status_code=500, detail=f"Graph Execution Failed: {str(e)}")

@app.get("/health")
@app.get("/")
async def root():
    return {"status": "online", "agent": "TravelDev GDS v1.0"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)