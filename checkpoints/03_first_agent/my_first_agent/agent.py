"""Блок 3. Первый агент: Hello, Agent!

Минимальный рабочий агент ADK — никаких инструментов, только LLM + instruction.

Запуск:
    cd checkpoints/03_first_agent
    adk web         # dev UI на http://localhost:8000
    adk run my_first_agent   # чат в терминале
"""

import os

# Имя модели читается из ADK_MODEL (см. .env / .env.example).
# Fallback на gemini-3.1-flash-lite — у него самый щедрый free-tier RPD (500/день).
MODEL = os.getenv("ADK_MODEL", "gemini-3.1-flash-lite")

from google.adk.agents import Agent

# root_agent — обязательное имя переменной, ADK CLI его ищет автоматически.
root_agent = Agent(
    name="python_helper",
    model=MODEL,
    description="Дружелюбный ассистент, помогающий с вопросами по Python.",
    instruction=(
        "Ты — дружелюбный наставник по Python. "
        "Отвечай кратко, по делу и с примерами кода. "
        "Если вопрос не связан с программированием, "
        "вежливо переводи разговор обратно к Python."
    ),
)
