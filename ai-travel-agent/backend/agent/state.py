from typing import TypedDict, Optional, List, Dict, Any

class TripState(TypedDict):
    user_prompt: str
    destination: str
    origin_city: str
    duration_days: int
    budget_usd: float
    origin_iata: Optional[str]
    destination_iata: Optional[str]
    start_date: str          
    end_date: str            
    trip_type: str           
    search_airport_city: Optional[str] 
    destination_lat: Optional[float]
    destination_lng: Optional[float]
    origin_lat: Optional[float]
    origin_lng: Optional[float]
    flights: List[Dict[str, Any]]
    hotels: List[Dict[str, Any]]
    weather: Optional[Dict[str, Any]] 
    pois: List[Dict[str, Any]]
    selected_flight: Optional[Dict[str, Any]]
    selected_hotel: Optional[Dict[str, Any]]
    itinerary: Optional[Dict[str, Any]]
    total_cost_eur: Optional[int] 
    within_budget: bool
    current_step: str
    messages: List[Dict[str, Any]]
    errors: List[str] 
    cost_breakdown: Optional[Dict[str, Any]]
    buffer_applied: Optional[float]