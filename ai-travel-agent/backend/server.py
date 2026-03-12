from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agent.graph import build_graph
from main import create_initial_state
import os

app = FastAPI()

# Allow your React app (Vite) to talk to this server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, change to your frontend URL
    allow_methods=["*"],
    allow_headers=["*"],
)

class TravelRequest(BaseModel):
    prompt: str

@app.post("/plan")
async def plan_trip(request: TravelRequest):
    try:
        graph = build_graph() # [cite: 61]
        initial_state = create_initial_state(request.prompt) # [cite: 56]
        result = graph.invoke(initial_state) # [cite: 105]
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)