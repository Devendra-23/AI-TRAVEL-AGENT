import os
import traceback
from pathlib import Path
from dotenv import load_dotenv

# 1. Load Environment Variables
load_dotenv() 

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# 2. These imports need the environment variables loaded first
from agent.graph import build_graph

# 3. INITIALIZE THE APP (Must happen before @app.post)
app = FastAPI(title="Gemini Travel Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TravelRequest(BaseModel):
    prompt: str

# 4. DEFINE ROUTES
@app.post("/plan")
async def plan_trip(request: dict): # Use dict to capture all fields
    try:
        # 1. Extract EVERYTHING from the request body
        prompt = request.get("prompt")
        start = request.get("start_date")
        end = request.get("end_date")
        t_type = request.get("trip_type", "round-trip")

        graph = build_graph() 
        
        initial_state = {
            "user_prompt": prompt,
            "current_step": "start",
            "origin_iata": None,
            "destination_iata": None,
            "start_date": start, # Now properly passed
            "end_date": end,     # Now properly passed
            "trip_type": t_type,
            "destination_lat": 0.0,
            "destination_lng": 0.0,
            "origin_lat": 0.0,
            "origin_lng": 0.0,
            "flights": [],
            "hotels": [],
            "pois": []
        }
        
        result = graph.invoke(initial_state) 
        return result
        
    except Exception as e:
        print("\n" + "="*50)
        print("💥 CRASH DETECTED!")
        traceback.print_exc()
        print("="*50 + "\n")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "online", "agent": "Gemini-3-Flash"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)