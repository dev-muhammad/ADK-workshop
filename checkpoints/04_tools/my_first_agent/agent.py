"""Block 4. Tools: function tools + built-in google_search.

Demonstrates two patterns:
  1. Your own functions as tools — get_weather, get_current_time
  2. Built-in tool google_search

IMPORTANT: type hints and docstrings are what the LLM sees. Write them carefully.

Run:
    cd checkpoints/04_tools
    adk web
"""

import os

# Model name is read from ADK_MODEL (see .env / .env.example).
# Falls back to gemini-3.1-flash-lite — the most generous free-tier RPD (500/day).
MODEL = os.getenv("ADK_MODEL", "gemini-3.1-flash-lite")

import datetime
from zoneinfo import ZoneInfo

from google.adk.agents import Agent


def get_weather(city: str) -> dict:
    """Returns the current weather in the specified city.

    Args:
        city: City name in English (e.g., "New York").

    Returns:
        Dict with status and a report, or an error message.
    """
    fake_data = {
        "new york": "It's sunny in New York, 25°C.",
        "london": "It's cloudy in London, 14°C.",
        "tashkent": "It's clear in Tashkent, 28°C.",
    }
    report = fake_data.get(city.lower())
    if report:
        return {"status": "success", "report": report}
    return {
        "status": "error",
        "error_message": f"No data for {city}.",
    }


def get_current_time(city: str) -> dict:
    """Returns the current time in the specified city.

    Args:
        city: City name in English (e.g., "New York").

    Returns:
        Dict with status and a report, or an error message.
    """
    tz_map = {
        "new york": "America/New_York",
        "london": "Europe/London",
        "tashkent": "Asia/Tashkent",
    }
    tz_id = tz_map.get(city.lower())
    if not tz_id:
        return {
            "status": "error",
            "error_message": f"No timezone for {city}.",
        }
    now = datetime.datetime.now(ZoneInfo(tz_id))
    return {
        "status": "success",
        "report": now.strftime("%Y-%m-%d %H:%M:%S %Z"),
    }


# Tools are passed as a plain list of functions.
root_agent = Agent(
    name="weather_time_agent",
    model=MODEL,
    description="Agent that answers questions about weather and time in a city.",
    instruction=(
        "You are a helpful assistant. "
        "When the user asks about weather or time — use the tools. "
        "If the city is not in the data — say so honestly."
    ),
    tools=[get_weather, get_current_time],
)


# --- Bonus: same agent but with built-in google_search ---
# Uncomment to try grounding in Google.
#
# from google.adk.tools import google_search
#
# root_agent = Agent(
#     name="search_agent",
#     model=MODEL,
#     description="Agent that searches answers in Google.",
#     instruction="You are an expert researcher. Always rely on facts.",
#     tools=[google_search],
# )
