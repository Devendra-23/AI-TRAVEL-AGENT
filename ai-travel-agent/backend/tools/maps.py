from tools.mock_data import MOCK_POIS

USE_MOCK = True

def get_pois(destination: str) -> list:
    """Returns mock points of interest[cite: 75]."""
    print(f"📍 Finding attractions in {destination}...")
    if USE_MOCK:
        return MOCK_POIS
    return []