from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langgraph.graph import StateGraph, END
from agent.state import TripState
from agent.nodes import (
    parse_input_node, search_flights_node, search_hotels_node,
    check_weather_node, get_pois_node, planner_node,
    budget_check_node, compile_itinerary_node
)

app = FastAPI(title="TravelDev AI Agent GDS")

# Enable CORS for your Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 1. STATE INITIALIZATION ---
def create_initial_state(user_prompt: str) -> dict:
    return {
        'user_prompt': user_prompt,
        'current_step': 'start',
        'destination': None,
        'origin_city': None,
        'origin_iata': None,
        'destination_iata': None,
        'start_date': None,
        'end_date': None,
        'duration_days': 0,
        'destination_lat': 0.0,
        'destination_lng': 0.0,
        'origin_lat': 0.0,
        'origin_lng': 0.0,
        'flights': [],
        'hotels': [],
        'weather': {},
        'pois': [],
        'itinerary': None,
        'total_cost_eur': 0,
        'errors': []
    }

# --- 2. GRAPH DEFINITION ---
workflow = StateGraph(TripState)

# Add all our "Brain" nodes
workflow.add_node("parser", parse_input_node)
workflow.add_node("flights", search_flights_node)
workflow.add_node("hotels", search_hotels_node)
workflow.add_node("weather", check_weather_node)
workflow.add_node("pois", get_pois_node)
workflow.add_node("planner", planner_node)
workflow.add_node("budget", budget_check_node)
workflow.add_node("compiler", compile_itinerary_node)

# Set the flow (Edges)
workflow.set_entry_point("parser")
workflow.add_edge("parser", "flights")
workflow.add_edge("flights", "hotels")
workflow.add_edge("hotels", "weather")
workflow.add_edge("weather", "pois")
workflow.add_edge("pois", "planner")
workflow.add_edge("planner", "budget")
workflow.add_edge("budget", "compiler")
workflow.add_edge("compiler", END)

# Compile the Agent
travel_agent = workflow.compile()

# --- 3. API ENDPOINTS ---
class PlanRequest(BaseModel):
    prompt: str

@app.post("/plan")
async def generate_plan(request: PlanRequest):
    print(f"🚀 [API] Received request: {request.prompt}")
    initial_state = create_initial_state(request.prompt)
    
    try:
        # Run the LangGraph synchronously for the UI
        final_state = travel_agent.invoke(initial_state)
        return final_state
    except Exception as e:
        print(f"❌ [API ERROR] {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)