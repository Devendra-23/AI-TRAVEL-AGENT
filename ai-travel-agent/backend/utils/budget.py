def calculate_total_cost(state: dict) -> dict:
    days = max(1, int(state.get('duration_days', 1) or 1))
    
    flight_data = state.get('selected_flight') or (state.get('flights')[0] if state.get('flights') else {})
    hotel_data = state.get('selected_hotel') or (state.get('hotels')[0] if state.get('hotels') else {})
    
    f_cost = float(flight_data.get('price_eur', 0))
    h_total = float(hotel_data.get('price_per_night_eur', 0)) * days

    act_total = 0.0
    itinerary = state.get('itinerary', {})
    
    days_list = itinerary.get('days', []) if isinstance(itinerary, dict) else []
    
    for day in days_list:
        for act in day.get('activities', []):
            act_total += float(act.get('cost_eur', 0))

    meals_total = float(days * 40.0)
    ground_total = h_total + act_total + meals_total
    buffer = int(ground_total * 0.05) # 5% buffer only on ground costs
    
    total_final = int(f_cost + ground_total + buffer)

    return {
        **state, # CRITICAL: Keeps your Globe coordinates intact
        "total_cost_eur": total_final,
        "buffer_applied": buffer,
        "selected_flight": flight_data,
        "selected_hotel": hotel_data,
        "itinerary": itinerary, # CRITICAL: Passes the Itinerary to the UI
        "cost_breakdown": {
            "flight": f_cost,
            "hotel": h_total,
            "activities": act_total,
            "meals": meals_total
        }
    }