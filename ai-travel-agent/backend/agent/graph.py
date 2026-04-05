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

# --- ROUTING LOGIC FUNCTIONS ---

def route_after_parse(state: TripState):
    """Gatekeeper: Stop if the AI couldn't find a real destination."""
    if state.get("errors"):
        return "error_exit"
    return "continue"

def route_after_search(state: TripState):
    """Availability Check: If no flights or hotels found, don't try to plan."""
    if not state.get("flights") and not state.get("hotels"):
        return "no_results"
    return "proceed"

def route_budget_check(state: TripState):
    """Financial Auditor: Loop back to planner if over budget to try cheaper options."""
    if state.get('within_budget', True):
        return "finalize"
    # If the user has tried looping more than twice, stop to prevent infinite loops
    if len(state.get("messages", [])) > 5: 
        return "finalize"
    return "replan"

def build_graph() -> StateGraph:
    """Build and return the compiled travel agent graph with intelligent routing."""
    graph = StateGraph(TripState)

    # 1. Register Nodes
    graph.add_node('parse_input',        parse_input_node)
    graph.add_node('search_flights',     search_flights_node)
    graph.add_node('search_hotels',      search_hotels_node)
    graph.add_node('check_weather',      check_weather_node)
    graph.add_node('get_pois',           get_pois_node)
    graph.add_node('planner',            planner_node)
    graph.add_node('budget_check',       budget_check_node)
    graph.add_node('compile_itinerary',  compile_itinerary_node)

    # 2. Set Entry Point
    graph.set_entry_point('parse_input')

    # 3. Conditional Edge: PARSE CHECK
    # Prevents searching for flights to "unknown" cities
    graph.add_conditional_edges(
        "parse_input",
        route_after_parse,
        {
            "error_exit": END,
            "continue": "search_flights"
        }
    )

    # 4. Sequential Tool Flow
    graph.add_edge('search_flights',    'search_hotels')
    
    # 5. Conditional Edge: AVAILABILITY CHECK
    graph.add_conditional_edges(
        "search_hotels",
        route_after_search,
        {
            "no_results": "compile_itinerary", # Go to summary to show what went wrong
            "proceed": "check_weather"
        }
    )

    graph.add_edge('check_weather',     'get_pois')
    graph.add_edge('get_pois',          'planner')
    graph.add_edge('planner',           'budget_check')

    # 6. Conditional Edge: BUDGET LOOP
    # If over budget, it sends it back to the planner to find cheaper activities
    graph.add_conditional_edges(
        'budget_check',
        route_budget_check,
        {
            'finalize': 'compile_itinerary',
            'replan': 'planner',
        }
    )

    graph.add_edge('compile_itinerary', END)

    return graph.compile()