# backend/agent/state.py
from typing import TypedDict, Optional, List, Dict, Any

class TripState(TypedDict):
    user_prompt: str
    destination: str
    origin_city: str
    duration_days: int
    budget_usd: float
    
    # --- NEW: Added coordinates for the 3D Globe ---
    destination_lat: float
    destination_lng: float
    # -----------------------------------------------
    # Add these right under destination_lat and destination_lng
    origin_lat: float
    origin_lng: float

    flights: List[Dict]
    hotels: List[Dict]
    weather: List[Dict]
    pois: List[Dict]
    selected_flight: Optional[Dict]
    selected_hotel: Optional[Dict]
    itinerary: Optional[Dict]
    within_budget: bool
    current_step: str
    messages: List[Dict] # Added for Gemini conversation history