"""Блок 10. Final: всё вместе.

Финальная версия агента, объединяющая всё из воркшопа:
  - tools: погода, время, память
  - callbacks: логирование, guardrail, нормализация, подпись
  - готова к streaming (через RunConfig в любом runner)
  - готова к evaluation (tests/ рядом)

Запуск:
    cd checkpoints/10_final
    adk web
"""

import os

# Имя модели читается из ADK_MODEL (см. .env / .env.example).
# Fallback на gemini-3.1-flash-lite — у него самый щедрый free-tier RPD (500/день).
MODEL = os.getenv("ADK_MODEL", "gemini-3.1-flash-lite")

import datetime
from typing import Any, Dict, Optional
from zoneinfo import ZoneInfo

from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest, LlmResponse
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext
from google.genai import types


# === TOOLS ===

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
    """Возвращает текущее время в указанном городе.

    Args:
        city: Название города на английском.
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


def remember_preference(key: str, value: str, tool_context: ToolContext) -> dict:
    """Сохраняет предпочтение пользователя в session state.

    Args:
        key: Ключ (например, "favorite_city").
        value: Значение.
        tool_context: Контекст сессии (передаётся ADK автоматически).
    """
    tool_context.state[key] = value
    return {"status": "success", "saved": {key: value}}


def recall_preference(key: str, tool_context: ToolContext) -> dict:
    """Достаёт сохранённое предпочтение.

    Args:
        key: Ключ, по которому искать.
        tool_context: Контекст сессии (передаётся ADK автоматически).
    """
    value = tool_context.state.get(key)
    if value is None:
        return {"status": "error", "error_message": f"Нет значения для {key}."}
    return {"status": "success", "value": value}


# === CALLBACKS ===

BLOCKED_WORDS = ("api_key", "password", "пароль", "секрет")
SIGNATURE = "\n\n— Ответ сгенерирован агентом ADK 🤖"


def log_entry(callback_context: CallbackContext) -> Optional[types.Content]:
    print(
        f"[LOG] enter agent={callback_context.agent_name} "
        f"inv={callback_context.invocation_id}"
    )
    return None


def block_secrets(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    last_text = ""
    if llm_request.contents:
        last = llm_request.contents[-1]
        if last.parts:
            last_text = (last.parts[0].text or "").lower()
    if any(word in last_text for word in BLOCKED_WORDS):
        return LlmResponse(
            content=types.Content(
                role="model",
                parts=[types.Part(text="⚠️ Я не обсуждаю секретные данные.")],
            )
        )
    return None


def normalize_city(
    tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext
) -> Optional[Dict]:
    if tool.name in ("get_weather", "get_current_time") and "city" in args:
        args["city"] = args["city"].strip().title()
    return None


def append_signature(
    callback_context: CallbackContext, llm_response: LlmResponse
) -> Optional[LlmResponse]:
    if not llm_response.content or not llm_response.content.parts:
        return None
    original = llm_response.content.parts[0].text or ""
    if not original:
        return None
    return LlmResponse(
        content=types.Content(
            role="model",
            parts=[types.Part(text=original + SIGNATURE)],
        )
    )


# === AGENT ===

root_agent = LlmAgent(
    name="final_weather_agent",
    model=MODEL,
    description="Финальная версия агента воркшопа: tools + memory + callbacks.",
    instruction=(
        "Ты — полезный ассистент. Инструменты:\n"
        "- get_weather / get_current_time — погода и время;\n"
        "- remember_preference — запомнить предпочтения пользователя "
        "(например, любимый город);\n"
        "- recall_preference — достать сохранённое.\n"
        "Если знаешь любимый город пользователя — используй его по умолчанию."
    ),
    tools=[get_weather, get_current_time, remember_preference, recall_preference],
    before_agent_callback=log_entry,
    before_model_callback=block_secrets,
    before_tool_callback=normalize_city,
    after_model_callback=append_signature,
)
