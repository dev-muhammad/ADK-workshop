"""Block 5. Memory & Sessions: Session / State / Memory.

In addition to weather/time, two tools that read and write session.state:
  - remember_preference(key, value)
  - recall_preference(key)

This gives the agent structured "short-term" memory within a single session.

Run:
    cd checkpoints/05_memory_sessions
    adk web
"""

import os

# Model name is read from ADK_MODEL (see .env / .env.example).
# Falls back to gemini-3.1-flash-lite — the most generous free-tier RPD (500/day).
MODEL = os.getenv("ADK_MODEL", "gemini-3.1-flash-lite")

import datetime
from zoneinfo import ZoneInfo

from google.adk.agents import Agent
from google.adk.tools.tool_context import ToolContext


def get_weather(city: str) -> dict:
    """Returns the current weather in the specified city.

    Args:
        city: City name in English.
    """
    fake_data = {
        "new york": "It's sunny in New York, 25°C.",
        "london": "It's cloudy in London, 14°C.",
        "tashkent": "It's clear in Tashkent, 28°C.",
    }
    report = fake_data.get(city.lower())
    if report:
        return {"status": "success", "report": report}
    return {"status": "error", "error_message": f"No data for {city}."}


def get_current_time(city: str) -> dict:
    """Returns the current time in the specified city."""
    tz_map = {
        "new york": "America/New_York",
        "london": "Europe/London",
        "tashkent": "Asia/Tashkent",
    }
    tz_id = tz_map.get(city.lower())
    if not tz_id:
        return {"status": "error", "error_message": f"No timezone for {city}."}
    now = datetime.datetime.now(ZoneInfo(tz_id))
    return {"status": "success", "report": now.strftime("%Y-%m-%d %H:%M:%S %Z")}


def remember_preference(key: str, value: str, tool_context: ToolContext) -> dict:
    """Saves a user preference to session state.

    Args:
        key: Key (e.g., "favorite_city").
        value: Value (e.g., "Tashkent").
        tool_context: Session context (passed by ADK automatically).
    """
    tool_context.state[key] = value
    return {"status": "success", "saved": {key: value}}


def recall_preference(key: str, tool_context: ToolContext) -> dict:
    """Retrieves a saved user preference.

    Args:
        key: Key to look up.
        tool_context: Session context (passed by ADK automatically).
    """
    value = tool_context.state.get(key)
    if value is None:
        return {"status": "error", "error_message": f"No value for {key}."}
    return {"status": "success", "value": value}


root_agent = Agent(
    name="weather_time_agent_with_memory",
    model=MODEL,
    description=(
        "Agent that answers about weather/time and remembers user preferences."
    ),
    instruction=(
        "You are a helpful assistant. Use the tools:\n"
        "- get_weather / get_current_time — for weather and time;\n"
        "- remember_preference — when the user states a preference "
        "(e.g., favorite city);\n"
        "- recall_preference — when the user asks about previously saved data.\n"
        "If a favorite city is remembered — use it by default."
    ),
    tools=[
        get_weather,
        get_current_time,
        remember_preference,
        recall_preference,
    ],
)
