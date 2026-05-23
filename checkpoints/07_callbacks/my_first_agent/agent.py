"""Блок 7. Callbacks: логирование, guardrails, фильтры.

Демонстрирует 4 callback'а на одном агенте:
  - before_agent_callback  — логирование входа
  - before_model_callback  — guardrail (блокировка по ключевым словам)
  - before_tool_callback   — нормализация аргументов tool
  - after_model_callback   — добавление подписи к ответу

Запуск:
    cd checkpoints/07_callbacks
    adk web
"""

import os

# Имя модели читается из ADK_MODEL (см. .env / .env.example).
# Fallback на gemini-3.1-flash-lite — у него самый щедрый free-tier RPD (500/день).
MODEL = os.getenv("ADK_MODEL", "gemini-3.1-flash-lite")

from typing import Any, Dict, Optional

from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest, LlmResponse
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext
from google.genai import types


# --- Tool ---

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


# --- Callback 1: логирование входа в агента ---

def log_entry(callback_context: CallbackContext) -> Optional[types.Content]:
    """Просто логирует — возвращает None, чтобы агент выполнился как обычно."""
    print(
        f"[LOG] enter agent={callback_context.agent_name} "
        f"inv={callback_context.invocation_id}"
    )
    return None


# --- Callback 2: guardrail на вход (before_model_callback) ---

BLOCKED_WORDS = ("api_key", "password", "пароль", "секрет")


def block_secrets(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    """Если в последнем сообщении пользователя есть запрещённые слова —
    подменяем ответ и не вызываем LLM."""
    last_text = ""
    if llm_request.contents:
        last = llm_request.contents[-1]
        if last.parts:
            last_text = (last.parts[0].text or "").lower()

    if any(word in last_text for word in BLOCKED_WORDS):
        print(f"[GUARDRAIL] blocked: '{last_text[:50]}...'")
        return LlmResponse(
            content=types.Content(
                role="model",
                parts=[
                    types.Part(
                        text="⚠️ Я не обсуждаю секретные данные. "
                        "Пожалуйста, переформулируйте вопрос."
                    )
                ],
            )
        )
    return None  # продолжаем как обычно


# --- Callback 3: нормализация аргументов tool ---

def normalize_city(
    tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext
) -> Optional[Dict]:
    """Подменяет args['city'] на нормализованную форму до вызова tool."""
    if tool.name == "get_weather" and "city" in args:
        original = args["city"]
        args["city"] = original.strip().title()
        if original != args["city"]:
            print(f"[Callback] normalized city '{original}' -> '{args['city']}'")
    return None


# --- Callback 4: пост-обработка ответа модели ---

SIGNATURE = "\n\n— Ответ сгенерирован агентом ADK 🤖"


def append_signature(
    callback_context: CallbackContext, llm_response: LlmResponse
) -> Optional[LlmResponse]:
    """Добавляет подпись к финальному текстовому ответу."""
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


# --- Агент со всеми callback'ами ---

root_agent = LlmAgent(
    name="guarded_weather_agent",
    model=MODEL,
    description="Агент с логированием, guardrail'ом и пост-обработкой.",
    instruction=(
        "Ты — полезный ассистент. Отвечай на вопросы о погоде, "
        "используя инструмент get_weather."
    ),
    tools=[get_weather],
    before_agent_callback=log_entry,
    before_model_callback=block_secrets,
    before_tool_callback=normalize_city,
    after_model_callback=append_signature,
)
