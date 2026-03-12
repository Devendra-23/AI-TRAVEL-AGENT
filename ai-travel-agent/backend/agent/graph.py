from langgraph.graph import StateGraph, END
from agent.state import TripState
from agent.nodes import (
    parse_input_node,
    search_flights_node,
    search_hotels_node,
    check_weather_node,
    get_pois_node,
    planner_node,
    budget_check_node,
    compile_itinerary_node,
)

def build_graph() -> StateGraph:
    """Build and return the compiled travel agent graph."""
    graph = StateGraph(TripState)

    # 1. Register every node
    graph.add_node('parse_input',        parse_input_node)
    graph.add_node('search_flights',     search_flights_node)
    graph.add_node('search_hotels',      search_hotels_node)
    graph.add_node('check_weather',      check_weather_node)
    graph.add_node('get_pois',           get_pois_node)
    graph.add_node('planner',            planner_node)
    graph.add_node('budget_check',       budget_check_node)
    graph.add_node('compile_itinerary',  compile_itinerary_node)

    # 2. Set entry point
    graph.set_entry_point('parse_input')

    # 3. Define sequential edges
    graph.add_edge('parse_input',       'search_flights')
    graph.add_edge('search_flights',    'search_hotels')
    graph.add_edge('search_hotels',     'check_weather')
    graph.add_edge('check_weather',     'get_pois')
    graph.add_edge('get_pois',          'planner')
    graph.add_edge('planner',           'budget_check')

    # 4. Conditional edge
    graph.add_conditional_edges(
        'budget_check',
        lambda state: 'compile_itinerary' if state.get('within_budget', True) else 'planner',
        {
            'compile_itinerary': 'compile_itinerary',
            'planner': 'planner',
        }
    )

    graph.add_edge('compile_itinerary', END)

    return graph.compile()