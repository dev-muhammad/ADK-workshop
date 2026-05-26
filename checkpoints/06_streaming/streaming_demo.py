"""SSE streaming demonstration.

What it shows:
  - StreamingMode.SSE produces a token-by-token stream
  - event.partial = True on intermediate chunks
  - max_llm_calls limits the number of LLM calls (runaway protection)

Run:
    cd checkpoints/06_streaming
    python streaming_demo.py
"""

import asyncio

from dotenv import load_dotenv

# load_dotenv must run BEFORE the agent import — otherwise ADK_MODEL won't be picked up.
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
        max_llm_calls=20,  # runaway-loop protection
    )

    print(">>> User: Tell me a long story about a coding cat.\n")
    print("<<< Agent: ", end="", flush=True)

    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=session.id,
        new_message=types.Content(
            role="user",
            parts=[types.Part(text="Tell me a long story about a coding cat.")],
        ),
        run_config=run_config,
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    # Intermediate chunks (event.partial=True) print without newline;
                    # the final one adds a newline.
                    print(part.text, end="", flush=True)
        if event.is_final_response():
            print()  # newline at the end


if __name__ == "__main__":
    asyncio.run(main())
