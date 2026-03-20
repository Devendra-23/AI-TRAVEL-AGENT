def calculate_total_cost(state: dict) -> dict:
    """
    Calculates the full journey cost. 
    Syncs with Booking GDS 'price_per_night_eur' vs Total Stay logic.
    """
    days = max(1, int(state.get('duration_days', 1) or 1))
    breakdown = {}

    # 1. Flights (Round-Trip Total)
    # We check both the list and the selected_flight key
    flight_data = state.get('selected_flight') or (state.get('flights')[0] if state.get('flights') else None)
    flight_cost = float(flight_data.get('price_eur', 0) if flight_data else 0)
    breakdown['flight'] = flight_cost

    # 2. Hotels (Nightly * Nights)
    hotel_data = state.get('selected_hotel') or (state.get('hotels')[0] if state.get('hotels') else None)
    if hotel_data:
        # We use the nightly rate we calculated in hotels.py
        nightly = float(hotel_data.get('price_per_night_eur', 0))
        breakdown['hotel'] = nightly * days
    else:
        breakdown['hotel'] = 0.0

    # 3. Activities (Summing specific costs from the AI Itinerary)
    act_total = 0.0
    itinerary = state.get('itinerary', {})
    if isinstance(itinerary, dict) and 'days' in itinerary:
        for day in itinerary.get('days', []):
            for act in day.get('activities', []):
                act_total += float(act.get('cost_eur', 0))
    breakdown['activities'] = act_total

    # 4. Meals (Luxury Daily Average: €60)
    breakdown['meals'] = float(days * 60.0)

    # 5. Total + 10% Buffer
    subtotal = sum(breakdown.values())
    buffer_amt = round(subtotal * 0.10, 2)
    total_final = subtotal + buffer_amt

    # 6. Budget Check
    user_limit = float(state.get('budget_usd') or state.get('budget_eur') or 0.0)

    return {
        'cost_breakdown': breakdown,
        'total_cost_eur': int(total_final),
        'within_budget': total_final <= user_limit if user_limit > 0 else True,
        'buffer_applied': buffer_amt
    }