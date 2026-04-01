from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langgraph.graph import StateGraph, END
import uvicorn
import os
from typing import Optional

from agent.state import TripState
from agent.nodes import (
    parse_input_node, search_flights_node, search_hotels_node,
    check_weather_node, get_pois_node, planner_node,
    budget_check_node, compile_itinerary_node
)

app = FastAPI(title="TravelDev AI Agent GDS")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://ai-travel-agent-mu.vercel.app", 
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def create_initial_state(user_prompt: str, start_date: str = "", end_date: str = "") -> dict:
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
        'cost_breakdown': {},
        'buffer_applied': 0.0
    }

workflow = StateGraph(TripState)
workflow.add_node("parser", parse_input_node)
workflow.add_node("fetch_flights", search_flights_node)
workflow.add_node("fetch_hotels", search_hotels_node)
workflow.add_node("fetch_weather", check_weather_node) 
workflow.add_node("fetch_pois", get_pois_node)        
workflow.add_node("planner", planner_node)
workflow.add_node("budget_audit", budget_check_node)   
workflow.add_node("compiler", compile_itinerary_node)

workflow.set_entry_point("parser")
workflow.add_edge("parser", "fetch_flights")
workflow.add_edge("fetch_flights", "fetch_hotels")
workflow.add_edge("fetch_hotels", "fetch_weather")
workflow.add_edge("fetch_weather", "fetch_pois")
workflow.add_edge("fetch_pois", "planner")
workflow.add_edge("planner", "budget_audit")
workflow.add_edge("budget_audit", "compiler")
workflow.add_edge("compiler", END)

travel_agent = workflow.compile()

class PlanRequest(BaseModel):
    prompt: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None

@app.post("/plan")
async def generate_plan(request: PlanRequest):
    initial_state = create_initial_state(request.prompt, request.start_date or "", request.end_date or "")
    try:
        final_state = travel_agent.invoke(initial_state)
        return final_state
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

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
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)