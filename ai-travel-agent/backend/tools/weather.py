from tools.mock_data import MOCK_WEATHER

USE_MOCK = True

def check_weather(destination: str) -> list:
    """Returns mock weather data[cite: 75, 85]."""
    print(f"🌦️  Fetching weather for {destination}...")
    if USE_MOCK:
        return MOCK_WEATHER
    return []