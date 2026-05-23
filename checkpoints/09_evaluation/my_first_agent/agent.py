"""Блок 9. Evaluation: измеряем качество агента.

Возвращаемся к базовому weather/time агенту — этот же агент будем оценивать
через evalset, CLI и pytest.

Запуск тестов:
    cd checkpoints/09_evaluation
    adk eval my_first_agent my_first_agent/tests/basic.evalset.json
    # или
    pytest -v my_first_agent/tests/test_agent.py
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
    """Возвращает текущее время в указанном городе.

    Args:
        city: Название города на английском (например, "New York").
    """
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


root_agent = Agent(
    name="weather_time_agent",
    model=MODEL,
    description="Агент, отвечающий на вопросы о погоде и времени в городе.",
    instruction=(
        "Ты — полезный ассистент. Когда пользователь спрашивает о погоде "
        "или времени — обязательно используй инструменты get_weather "
        "и get_current_time."
    ),
    tools=[get_weather, get_current_time],
)
