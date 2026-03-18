from typing import TypedDict, Optional, List, Dict, Any

class TripState(TypedDict):
    # Core User Inputs
    user_prompt: str
    destination: str
    origin_city: str
    duration_days: int
    budget_usd: float
    
    # IATA codes (Automated by Gemini)
    origin_iata: Optional[str]
    destination_iata: Optional[str]
    
    # --- PRO FEATURES: Dates & Trip Logic ---
    start_date: str          
    end_date: str            
    trip_type: str           
    search_airport_city: Optional[str] 
    # ----------------------------------------

    # 3D Globe Coordinates
    destination_lat: Optional[float]
    destination_lng: Optional[float]
    origin_lat: Optional[float]
    origin_lng: Optional[float]

    # Tool Results
    flights: List[Dict]
    hotels: List[Dict]
    weather: Optional[Dict] # Changed from List to Dict for better logic
    pois: List[Dict]
    
    # Final Selections
    selected_flight: Optional[Dict]
    selected_hotel: Optional[Dict]
    itinerary: Optional[Dict]
    total_cost_eur: Optional[int] # Added this for the Frontend Budget Audit
    
    # Logic & History
    within_budget: bool
    current_step: str
    messages: List[Dict]