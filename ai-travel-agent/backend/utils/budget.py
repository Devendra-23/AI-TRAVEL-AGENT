# utils/budget.py

def calculate_total_cost(state: dict) -> dict:
    """Calculates full trip cost and returns updated budget fields.""" [cite: 87]
    breakdown = {}

    # Flight (round trip) 
    if state.get('selected_flight'):
        breakdown['flight'] = state['selected_flight']['price_usd'] [cite: 87]

    # Hotel (nightly rate × nights) 
    if state.get('selected_hotel'):
        breakdown['hotel'] = (
            state['selected_hotel']['price_per_night_usd'] * state['duration_days']
        ) [cite: 87]

    # Activities from itinerary 
    activities_cost = 0.0
    if state.get('itinerary') and 'days' in state['itinerary']:
        for day in state['itinerary']['days']:
            for activity in day.get('activities', []):
                activities_cost += activity.get('cost_usd', 0) [cite: 87]
    breakdown['activities'] = activities_cost [cite: 87]

    # Estimate meals: $40/day 
    breakdown['meals'] = state['duration_days'] * 40 [cite: 87]

    total = sum(breakdown.values()) [cite: 87]

    return {
        'cost_breakdown': breakdown,
        'total_cost_usd': total,
        'within_budget':  total <= state['budget_usd'], [cite: 87]
    }