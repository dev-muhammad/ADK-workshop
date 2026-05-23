"""Блок 6. Streaming.

Сам агент остаётся прежним — streaming управляется через RunConfig
в Runner, см. streaming_demo.py.

Запуск:
    cd checkpoints/06_streaming
    python streaming_demo.py
"""

import os

# Имя модели читается из ADK_MODEL (см. .env / .env.example).
# Fallback на gemini-3.1-flash-lite — у него самый щедрый free-tier RPD (500/день).
MODEL = os.getenv("ADK_MODEL", "gemini-3.1-flash-lite")

from google.adk.agents import Agent

root_agent = Agent(
    name="storytelling_agent",
    model=MODEL,
    description="Агент, который рассказывает длинные истории — идеально для демонстрации streaming.",
    instruction=(
        "Ты — рассказчик. Когда пользователь просит — рассказывай длинные, "
        "детальные истории с описаниями. Минимум 5-6 абзацев."
    ),
)
