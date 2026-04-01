def calculate_total_cost(state: dict) -> dict:
    """
    Calculates the full journey cost. 
    """
    days = max(1, int(state.get('duration_days', 1) or 1))
    breakdown = {}

    # 1. Flights
    flight_data = state.get('selected_flight') or (state.get('flights')[0] if state.get('flights') else None)
    flight_cost = float(flight_data.get('price_eur', 0) if flight_data else 0)
    breakdown['flight'] = flight_cost

    # 2. Hotels
    hotel_data = state.get('selected_hotel') or (state.get('hotels')[0] if state.get('hotels') else None)
    if hotel_data:
        nightly = float(hotel_data.get('price_per_night_eur', 0))
        breakdown['hotel'] = nightly * days
    else:
        breakdown['hotel'] = 0.0

    # 3. Activities
    act_total = 0.0
    itinerary = state.get('itinerary', {})
    if isinstance(itinerary, dict) and 'days' in itinerary:
        for day in itinerary.get('days', []):
            for act in day.get('activities', []):
                act_total += float(act.get('cost_eur', 0))
    breakdown['activities'] = act_total

    # 4. Meals
    breakdown['meals'] = float(days * 60.0)

    # 5. Total + Buffer
    subtotal = sum(breakdown.values())
    buffer_amt = round(subtotal * 0.10, 2)
    total_final = subtotal + buffer_amt

    # 6. Budget Check
    user_limit = float(state.get('budget_usd') or 2000.0)

    return {
        'cost_breakdown': breakdown,
        'total_cost_eur': int(total_final),
        'within_budget': total_final <= user_limit,
        'buffer_applied': buffer_amt,
        'itinerary': itinerary,
        'selected_flight': flight_data,
        'selected_hotel': hotel_data
    }