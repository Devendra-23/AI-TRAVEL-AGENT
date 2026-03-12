# backend/tools/hotels.py
from tools.mock_data import MOCK_HOTELS

USE_MOCK = True

def search_hotels(destination: str, duration_days: int) -> list:
    """Returns mock hotel data for testing."""
    if USE_MOCK:
        return MOCK_HOTELS
    return []