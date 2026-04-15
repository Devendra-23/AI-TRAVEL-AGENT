def calculate_total_cost(state: dict) -> dict:
    """
    Calculates the full journey cost and ensures flights/hotels stay in the state.
    """
    days = max(1, int(state.get('duration_days', 1) or 1))
    breakdown = {}

    # 1. Flights - PERSISTED
    # We look for selected_flight first, then fallback to the first flight in the list
    flight_data = state.get('selected_flight') or (state.get('flights')[0] if state.get('flights') else None)
    flight_cost = float(flight_data.get('price_eur', 0) if flight_data else 0)
    breakdown['flight'] = flight_cost

    # 2. Hotels - PERSISTED
    hotel_data = state.get('selected_hotel') or (state.get('hotels')[0] if state.get('hotels') else None)
    nightly = float(hotel_data.get('price_per_night_eur', 0) if hotel_data else 0)
    hotel_total = nightly * days
    breakdown['hotel'] = hotel_total

    # 3. Activities
    act_total = 0.0
    itinerary = state.get('itinerary', {})
    
    # Logic to handle both nested and flat itinerary structures
    days_list = []
    if isinstance(itinerary, dict):
        days_list = itinerary.get('days', [])
    elif isinstance(itinerary, list):
        days_list = itinerary

    for day in days_list:
        for act in day.get('activities', []):
            act_total += float(act.get('cost_eur', 0))
    
    breakdown['activities'] = act_total

    # 4. Meals & Ground Costs
    breakdown['meals'] = float(days * 40.0)

    # 5. Calculation with 5% Buffer (Buffer only on ground costs, not fixed flights)
    ground_subtotal = breakdown['hotel'] + breakdown['activities'] + breakdown['meals']
    buffer_amt = round(ground_subtotal * 0.05, 2)
    total_final = flight_cost + ground_subtotal + buffer_amt

    # 6. Budget Check
    user_limit = float(state.get('budget_usd') or 2000.0)

    # IMPORTANT: We return the prices AND the data objects so the UI stays filled
    return {
        **state,  # This keeps all other data (weather, pois, etc.) intact
        'cost_breakdown': breakdown,
        'total_cost_eur': int(total_final),
        'within_budget': total_final <= user_limit,
        'buffer_applied': int(buffer_amt),
        'selected_flight': flight_data, # Crucial for UI
        'selected_hotel': hotel_data     # Crucial for UI
    }