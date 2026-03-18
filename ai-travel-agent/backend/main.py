def create_initial_state(user_prompt: str) -> dict:
    """
    Initializes the TripState schema.
    Setting values to None ensures the AI Parse Node fills them based on the prompt.
    """
    return {
        'user_prompt': user_prompt,
        'current_step': 'start',
        
        # --- THE FIX: Start with None to force AI Extraction ---
        'destination': None,
        'origin_city': None,
        'origin_iata': None,      # Added: Crucial for Flights.py
        'destination_iata': None, # Added: Crucial for Flights.py
        
        # --- DATES & TRIP LOGIC ---
        'start_date': None,       # Added: For dynamic dates
        'end_date': None,         # Added: For dynamic dates
        'trip_type': 'round-trip',# Default
        'duration_days': 0,
        'budget_usd': 0.0,
        
        # --- GLOBE COORDINATES ---
        'destination_lat': 0.0,
        'destination_lng': 0.0,
        'origin_lat': 0.0,
        'origin_lng': 0.0,

        # --- DATA CONTAINERS ---
        'flights': [],
        'hotels': [],
        'weather': {},           # Changed to dict for better tool handling
        'pois': [],
        
        # --- FINAL RESULTS ---
        'selected_flight': None,
        'selected_hotel': None,
        'itinerary': None,
        'total_cost_eur': 0,      # Added: For the Frontend display
        'within_budget': True,
        'messages': [],
        'errors': []
    }