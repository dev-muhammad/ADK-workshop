"""Блок 5. Memory & Sessions: Session / State / Memory.

К погоде/времени добавлены два tool'а, которые читают и пишут в session.state:
  - remember_preference(key, value)
  - recall_preference(key)

Это даёт агенту структурированную «короткую» память внутри одной сессии.

Запуск:
    cd checkpoints/05_memory_sessions
    adk web
"""

import os

# Имя модели читается из ADK_MODEL (см. .env / .env.example).
# Fallback на gemini-3.1-flash-lite — у него самый щедрый free-tier RPD (500/день).
MODEL = os.getenv("ADK_MODEL", "gemini-3.1-flash-lite")

import datetime
from zoneinfo import ZoneInfo

from google.adk.agents import Agent
from google.adk.tools.tool_context import ToolContext


def get_weather(city: str) -> dict:
    """Возвращает текущую погоду в указанном городе.

    Args:
        city: Название города на английском.
    """
    fake_data = {
        "new york": "В Нью-Йорке солнечно, 25°C.",
        "london": "В Лондоне облачно, 14°C.",
        "tashkent": "В Ташкенте ясно, 28°C.",
    }
    report = fake_data.get(city.lower())
    if report:
        return {"status": "success", "report": report}
    return {"status": "error", "error_message": f"Нет данных по городу {city}."}


def get_current_time(city: str) -> dict:
    """Возвращает текущее время в указанном городе."""
    tz_map = {
        "new york": "America/New_York",
        "london": "Europe/London",
        "tashkent": "Asia/Tashkent",
    }
    tz_id = tz_map.get(city.lower())
    if not tz_id:
        return {"status": "error", "error_message": f"Нет таймзоны для {city}."}
    now = datetime.datetime.now(ZoneInfo(tz_id))
    return {"status": "success", "report": now.strftime("%Y-%m-%d %H:%M:%S %Z")}


def remember_preference(key: str, value: str, tool_context: ToolContext) -> dict:
    """Сохраняет предпочтение пользователя в session state.

    Args:
        key: Ключ (например, "favorite_city").
        value: Значение (например, "Tashkent").
        tool_context: Контекст сессии (передаётся ADK автоматически).
    """
    tool_context.state[key] = value
    return {"status": "success", "saved": {key: value}}


def recall_preference(key: str, tool_context: ToolContext) -> dict:
    """Достаёт сохранённое предпочтение пользователя.

    Args:
        key: Ключ, по которому искать.
        tool_context: Контекст сессии (передаётся ADK автоматически).
    """
    value = tool_context.state.get(key)
    if value is None:
        return {"status": "error", "error_message": f"Нет значения для {key}."}
    return {"status": "success", "value": value}


root_agent = Agent(
    name="weather_time_agent_with_memory",
    model=MODEL,
    description=(
        "Агент, отвечающий на вопросы о погоде/времени и помнящий "
        "предпочтения пользователя."
    ),
    instruction=(
        "Ты — полезный ассистент. Используй инструменты:\n"
        "- get_weather / get_current_time — для погоды и времени;\n"
        "- remember_preference — когда пользователь говорит свои предпочтения "
        "(например, любимый город);\n"
        "- recall_preference — когда пользователь спрашивает о ранее "
        "сохранённых данных.\n"
        "Если запомнил любимый город — используй его по умолчанию."
    ),
    tools=[
        get_weather,
        get_current_time,
        remember_preference,
        recall_preference,
    ],
)
