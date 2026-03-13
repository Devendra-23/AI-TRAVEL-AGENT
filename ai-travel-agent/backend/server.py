import os
from dotenv import load_dotenv

# MUST be the first thing that happens
load_dotenv() 

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Now these imports will have access to the GOOGLE_API_KEY
from agent.graph import build_graph
from main import create_initial_state

app = FastAPI(title="Gemini Travel Agent API")

# Allow your React app (Vite usually runs on port 5173) to talk to this server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TravelRequest(BaseModel):
    prompt: str

@app.post("/plan")
async def plan_trip(request: TravelRequest):
    try:
        # 1. Build the LangGraph state machine
        graph = build_graph() 
        
        # 2. Initialize the state using the prompt from the frontend
        initial_state = create_initial_state(request.prompt) 
        
        # 3. Invoke the graph (this triggers the LLM and tools)
        result = graph.invoke(initial_state) 
        
        # 4. Return the full state (itinerary, weather, etc.) as JSON
        return result
        
    except Exception as e:
        # Provides the frontend with a clear error message if the LLM fails
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "online", "agent": "Gemini-3-Flash"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)