# utils/budget.py

def calculate_total_cost(state: dict) -> dict:
    """Calculates full trip cost and returns updated budget fields."""
    breakdown = {}

    # Flight (round trip)
    if state.get('selected_flight'):
        breakdown['flight'] = state['selected_flight'].get('price_usd', 0.0)

    # Hotel (nightly rate × nights)
    if state.get('selected_hotel'):
        # Ensure duration_days is at least 1 to avoid zeroing out if data is missing
        days = state.get('duration_days', 1)
        breakdown['hotel'] = (
            state['selected_hotel'].get('price_per_night_usd', 0.0) * days
        )

    # Activities from itinerary
    activities_cost = 0.0
    if state.get('itinerary') and 'days' in state['itinerary']:
        for day in state['itinerary']['days']:
            for activity in day.get('activities', []):
                activities_cost += activity.get('cost_usd', 0)
    breakdown['activities'] = activities_cost

    # Estimate meals: $40/day
    breakdown['meals'] = state.get('duration_days', 1) * 40

    total = sum(breakdown.values())

    # DEFENSIVE FIX: Ensure state['budget_usd'] is a float and not None
    user_budget = state.get('budget_usd')
    if user_budget is None:
        user_budget = 0.0 

    return {
        'cost_breakdown': breakdown,
        'total_cost_usd': total,
        # Now comparing float <= float (Safe)
        'within_budget': total <= user_budget if user_budget > 0 else True,
    }