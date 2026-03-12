# backend/tools/flights.py
from tools.mock_data import MOCK_FLIGHTS

USE_MOCK = True

def search_flights(origin: str, destination: str, duration_days: int) -> list:
    """Returns mock flight data for testing."""
    if USE_MOCK:
        return MOCK_FLIGHTS
    # Future real API logic goes here 
    return []