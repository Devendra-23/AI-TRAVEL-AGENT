# agent/state.py 
from typing import TypedDict, Optional, List, Dict, Any

class TripState(TypedDict):
    user_prompt: str
    destination: str
    origin_city: str
    duration_days: int
    budget_usd: float
    flights: List[Dict]
    hotels: List[Dict]
    weather: List[Dict]
    pois: List[Dict]
    selected_flight: Optional[Dict]
    selected_hotel: Optional[Dict]
    itinerary: Optional[Dict]
    within_budget: bool
    current_step: str