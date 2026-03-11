# main.py
import sys
from dotenv import load_dotenv
from agent.graph import build_graph
from agent.state import TripState

load_dotenv()  # Injects GOOGLE_API_KEY from .env 

def create_initial_state(user_prompt: str):
    # Initializes all state fields as empty except the user prompt [cite: 56]
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
        'within_budget': True,
        'messages': [],
        'current_step': 'start'
    }

def run(user_prompt: str):
    graph = build_graph() # Wires nodes together [cite: 61]
    state = create_initial_state(user_prompt)
    result = graph.invoke(state) # Starts execution [cite: 105]
    print(f"Plan for {result['destination']} complete!")

if __name__ == '__main__':
    prompt = sys.argv[1] if len(sys.argv) > 1 else '4 days in Japan under $1500'
    run(prompt)