from typing import TypedDict, Optional, List, Dict, Any

class TripState(TypedDict):
    # --- CORE USER INPUTS ---
    user_prompt: str
    destination: str
    origin_city: str
    duration_days: int
    budget_usd: float
    
    # --- IATA CODES (Automated by Gemini) ---
    origin_iata: Optional[str]
    destination_iata: Optional[str]
    
    # --- PRO FEATURES: Dates & Trip Logic ---
    start_date: str          
    end_date: str            
    trip_type: str           
    search_airport_city: Optional[str] 

    # --- 3D GLOBE COORDINATES ---
    destination_lat: Optional[float]
    destination_lng: Optional[float]
    origin_lat: Optional[float]
    origin_lng: Optional[float]

    # --- TOOL RESULTS ---
    flights: List[Dict[str, Any]]
    hotels: List[Dict[str, Any]]
    weather: Optional[Dict[str, Any]] 
    pois: List[Dict[str, Any]]
    
    # --- FINAL SELECTIONS ---
    selected_flight: Optional[Dict[str, Any]]
    selected_hotel: Optional[Dict[str, Any]]
    itinerary: Optional[Dict[str, Any]]
    total_cost_eur: Optional[int] 
    
    # --- LOGIC & HISTORY ---
    within_budget: bool
    current_step: str
    messages: List[Dict[str, Any]]
    errors: List[str] 

    # --- MISSING PRODUCTION KEYS (Fixed for 500 Error) ---
    # These keys are required because your nodes are generating them
    cost_breakdown: Optional[Dict[str, float]]
    buffer_applied: Optional[float]