def calculate_total_cost(state: dict) -> dict:
    """
    Calculates full trip cost in EUR and returns audited budget fields.
    Standardized for European market requirements.
    """
    breakdown = {}
    days = int(state.get('duration_days', 1) or 1)

    # 1. Flight (Standardized to price_eur from RapidAPI)
    selected_flight = state.get('selected_flight')
    if selected_flight:
        # We check price_eur, fallback to price_usd if necessary, then 0.0
        breakdown['flight'] = float(selected_flight.get('price_eur') or selected_flight.get('price_usd') or 0.0)
    else:
        breakdown['flight'] = 0.0

    # 2. Hotel (Nightly rate × nights)
    selected_hotel = state.get('selected_hotel')
    if selected_hotel:
        nightly_rate = float(selected_hotel.get('price_per_night_eur') or selected_hotel.get('price_per_night_usd') or 0.0)
        breakdown['hotel'] = nightly_rate * days
    else:
        breakdown['hotel'] = 0.0

    # 3. Activities (Iterating through the roadmap)
    activities_cost = 0.0
    itinerary = state.get('itinerary', {})
    if isinstance(itinerary, dict) and 'days' in itinerary:
        for day in itinerary['days']:
            for act in day.get('activities', []):
                # AI is commanded to use cost_eur in nodes.py
                activities_cost += float(act.get('cost_eur') or act.get('cost_usd') or 0.0)
    
    breakdown['activities'] = activities_cost

    # 4. Meals Estimate (European Daily Average: €50)
    breakdown['meals'] = float(days * 50.0)

    # 5. Total Calculation with 10% "Safety Buffer"
    subtotal = sum(breakdown.values())
    breakdown['buffer'] = round(subtotal * 0.10, 2)
    total = subtotal + breakdown['buffer']

    # Financial Audit against User Budget
    # Ensure user_budget is handled as EUR
    user_budget = float(state.get('budget_usd') or 0.0) 

    return {
        'cost_breakdown': breakdown,
        'total_cost_eur': round(total, 2),
        'total_cost': round(total, 2), # Duplicate for UI safety
        'within_budget': total <= user_budget if user_budget > 0 else True,
    }