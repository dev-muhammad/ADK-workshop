"""Блок 4. Tools: function tools + built-in google_search.

Демонстрирует два паттерна:
  1. Свои функции как tools — get_weather, get_current_time
  2. Встроенный tool google_search

ВАЖНО: type hints и docstring — это то, что увидит LLM. Пишите их аккуратно.

Запуск:
    cd checkpoints/04_tools
    adk web
"""

import os

# Имя модели читается из ADK_MODEL (см. .env / .env.example).
# Fallback на gemini-3.1-flash-lite — у него самый щедрый free-tier RPD (500/день).
MODEL = os.getenv("ADK_MODEL", "gemini-3.1-flash-lite")

import datetime
from zoneinfo import ZoneInfo

from google.adk.agents import Agent


def get_weather(city: str) -> dict:
    """Возвращает текущую погоду в указанном городе.

    Args:
        city: Название города на английском (например, "New York").

    Returns:
        Словарь со статусом и отчётом либо сообщением об ошибке.
    """
    fake_data = {
        "new york": "В Нью-Йорке солнечно, 25°C.",
        "london": "В Лондоне облачно, 14°C.",
        "tashkent": "В Ташкенте ясно, 28°C.",
    }
    report = fake_data.get(city.lower())
    if report:
        return {"status": "success", "report": report}
    return {
        "status": "error",
        "error_message": f"Нет данных по городу {city}.",
    }


def get_current_time(city: str) -> dict:
    """Возвращает текущее время в указанном городе.

    Args:
        city: Название города на английском (например, "New York").

    Returns:
        Словарь со статусом и отчётом либо сообщением об ошибке.
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
            "error_message": f"Нет таймзоны для {city}.",
        }
    now = datetime.datetime.now(ZoneInfo(tz_id))
    return {
        "status": "success",
        "report": now.strftime("%Y-%m-%d %H:%M:%S %Z"),
    }


# Tools передаются обычным списком функций.
root_agent = Agent(
    name="weather_time_agent",
    model=MODEL,
    description="Агент, отвечающий на вопросы о погоде и времени в городе.",
    instruction=(
        "Ты — полезный ассистент. "
        "Когда пользователь спрашивает о погоде или времени — используй инструменты. "
        "Если города нет в данных — честно скажи об этом."
    ),
    tools=[get_weather, get_current_time],
)


# --- Бонус: тот же агент, но со встроенным google_search ---
# Раскомментируйте, чтобы попробовать grounding в Google.
#
# from google.adk.tools import google_search
#
# root_agent = Agent(
#     name="search_agent",
#     model="gemini-2.5-flash",
#     description="Агент, ищущий ответы в Google.",
#     instruction="Ты — эксперт-исследователь. Всегда опирайся на факты.",
#     tools=[google_search],
# )
