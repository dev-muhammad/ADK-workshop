"""Demo: programmatic agent run via InMemoryRunner.

Run:
    cd checkpoints/05_memory_sessions
    python run_session_demo.py

What it demonstrates:
  - creating a session via InMemorySessionService
  - subsequent calls with the same session_id => agent remembers context
  - printing the final responses
"""

import asyncio

from dotenv import load_dotenv

# load_dotenv must run BEFORE the agent import — otherwise ADK_MODEL won't be picked up.
load_dotenv("my_first_agent/.env")

from google.adk.runners import InMemoryRunner  # noqa: E402
from google.genai import types  # noqa: E402

from my_first_agent.agent import root_agent  # noqa: E402

APP_NAME = "workshop"
USER_ID = "user_1"


async def send(runner: InMemoryRunner, session_id: str, text: str) -> None:
    """Send a message and print the final response."""
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

    await send(runner, session.id, "My name is Muhammad, my favorite city is Tashkent. Remember that.")
    await send(runner, session.id, "What's the weather there right now?")
    await send(runner, session.id, "And what's my name?")


if __name__ == "__main__":
    asyncio.run(main())
