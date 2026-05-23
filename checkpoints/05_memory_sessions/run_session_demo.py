"""Демо программного запуска агента через InMemoryRunner.

Запуск:
    cd checkpoints/05_memory_sessions
    python run_session_demo.py

Что демонстрирует:
  - создание сессии через InMemorySessionService
  - повторные вызовы с одним session_id => агент помнит контекст
  - вывод финальных ответов
"""

import asyncio

from dotenv import load_dotenv

# load_dotenv должен идти ДО импорта агента — иначе ADK_MODEL не будет подхвачен.
load_dotenv("my_first_agent/.env")

from google.adk.runners import InMemoryRunner  # noqa: E402
from google.genai import types  # noqa: E402

from my_first_agent.agent import root_agent  # noqa: E402

APP_NAME = "workshop"
USER_ID = "user_1"


async def send(runner: InMemoryRunner, session_id: str, text: str) -> None:
    """Отправить сообщение и вывести финальный ответ."""
    print(f"\n>>> User: {text}")
    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=session_id,
        new_message=types.Content(role="user", parts=[types.Part(text=text)]),
    ):
        if event.is_final_response() and event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    print(f"<<< Agent: {part.text.strip()}")


async def main() -> None:
    runner = InMemoryRunner(agent=root_agent, app_name=APP_NAME)
    session = await runner.session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID
    )

    await send(runner, session.id, "Меня зовут Мухаммад, мой любимый город — Tashkent. Запомни.")
    await send(runner, session.id, "Какая там сейчас погода?")
    await send(runner, session.id, "А как меня зовут?")


if __name__ == "__main__":
    asyncio.run(main())
