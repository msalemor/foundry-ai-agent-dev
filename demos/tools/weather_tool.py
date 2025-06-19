import json
import datetime
from typing import Any, Callable, Set, Dict, List, Optional


def fetch_weather(location: str) -> str:
    """
    Fetches the weather information for the specified location.

    :param location: The location to fetch weather for.
    :return: Weather information as a JSON string.
    """
    # Mock weather data for demonstration purposes
    mock_weather_data = {
        "New York": "Sunny, 25°C",
        "London": "Cloudy, 18°C",
        "Tokyo": "Rainy, 22°C",
    }
    weather = mock_weather_data.get(
        location, "Weather data not available for this location."
    )
    return json.dumps({"weather": weather})


# Define user functions
user_functions = {fetch_weather}
