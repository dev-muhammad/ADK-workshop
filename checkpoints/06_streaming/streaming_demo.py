"""Демонстрация SSE streaming.

Что показывает:
  - StreamingMode.SSE даёт token-by-token поток
  - event.partial = True для промежуточных чанков
  - max_llm_calls ограничивает количество вызовов LLM (защита от runaway)

Запуск:
    cd checkpoints/06_streaming
    python streaming_demo.py
"""

import asyncio

from dotenv import load_dotenv

# load_dotenv должен идти ДО импорта агента — иначе ADK_MODEL не будет подхвачен.
load_dotenv("my_first_agent/.env")

from google.adk.agents.run_config import RunConfig, StreamingMode  # noqa: E402
from google.adk.runners import InMemoryRunner  # noqa: E402
from google.genai import types  # noqa: E402

from my_first_agent.agent import root_agent  # noqa: E402

APP_NAME = "workshop_streaming"
USER_ID = "user_1"


async def main() -> None:
    runner = InMemoryRunner(agent=root_agent, app_name=APP_NAME)
    session = await runner.session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID
    )

    run_config = RunConfig(
        streaming_mode=StreamingMode.SSE,
        max_llm_calls=20,  # защита от бесконечного цикла
    )

    print(">>> User: Расскажи длинную историю про кота-программиста.\n")
    print("<<< Agent: ", end="", flush=True)

    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=session.id,
        new_message=types.Content(
            role="user",
            parts=[types.Part(text="Расскажи длинную историю про кота-программиста.")],
        ),
        run_config=run_config,
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    # Промежуточные чанки (event.partial=True) выводим без переноса,
                    # финальный — с переносом.
                    print(part.text, end="", flush=True)
        if event.is_final_response():
            print()  # перенос строки в конце


if __name__ == "__main__":
    asyncio.run(main())
