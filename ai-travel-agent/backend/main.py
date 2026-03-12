import sys
import os
import importlib.util
from pathlib import Path
from dotenv import load_dotenv

# Force the backend directory into the search path
current_dir = Path(__file__).resolve().parent
sys.path.append(str(current_dir))

load_dotenv()

from agent.graph import build_graph

# ULTIMATE FIX: Manually load the formatter module
formatter_path = current_dir / "utils" / "formatter.py"
spec = importlib.util.spec_from_file_location("utils.formatter", str(formatter_path))
formatter_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(formatter_module)
print_itinerary = formatter_module.print_itinerary

def create_initial_state(user_prompt: str) -> dict:
    """Initializes the TripState schema."""
    return {
        'user_prompt': user_prompt,
        'destination': '',
        'origin_city': '',
        'duration_days': 0,
        'budget_usd': 0.0,
        'flights': [],
        'hotels': [],
        'weather': [],
        'pois': [],
        'selected_flight': None,
        'selected_hotel': None,
        'itinerary': None,
        'cost_breakdown': {},
        'total_cost_usd': 0.0,
        'within_budget': True,
        'messages': [],
        'current_step': 'start',
        'errors': []
    }

def run(user_prompt: str):
    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ Error: GOOGLE_API_KEY missing from .env")
        return

    print(f"🚀 Running Gemini Travel Agent for: {user_prompt}")
    
    graph = build_graph()
    initial_state = create_initial_state(user_prompt)
    
    try:
        result = graph.invoke(initial_state)
        print_itinerary(result) # Uses the manually loaded formatter
    except Exception as e:
        print(f"⚠️ Error: {e}")

if __name__ == '__main__':
    prompt = sys.argv[1] if len(sys.argv) > 1 else 'Plan a 4 day trip to Tokyo under $1500'
    run(prompt)