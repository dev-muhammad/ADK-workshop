"""End-to-end smoke test of the install: imports, instantiation, real LLM call.

Run:
    # from the repo root, with .venv activated
    cp checkpoints/04_tools/my_first_agent/.env.example .env
    # edit .env and paste your GOOGLE_API_KEY

    python verify_setup.py

What it checks:
  1. Every checkpoint imports and exposes a `root_agent`.
  2. All agents have the expected tools/callbacks/sub_agents.
  3. InMemoryRunner can be constructed for each.
  4. (If GOOGLE_API_KEY is set) — runs a real call against checkpoint 04 and
     validates the response.
"""

from __future__ import annotations

import asyncio
import importlib
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).parent
CHECKPOINTS = [
    "03_first_agent",
    "04_tools",
    "05_memory_sessions",
    "06_streaming",
    "07_callbacks",
    "08_sub_agents_mcp",
    "09_evaluation",
    "10_final",
]


def section(title: str) -> None:
    print()
    print("=" * 70)
    print(title)
    print("=" * 70)


def check_imports() -> dict[str, object]:
    """Import root_agent for each checkpoint and return them."""
    section("1/3 · Importing every checkpoint agent")
    agents = {}
    for cp in CHECKPOINTS:
        sys.path.insert(0, str(ROOT / "checkpoints" / cp))
        # Drop cached modules so each checkpoint is imported fresh.
        for m in list(sys.modules):
            if m.startswith("my_first_agent"):
                del sys.modules[m]
        mod = importlib.import_module("my_first_agent.agent")
        agent = mod.root_agent
        tools = [getattr(t, "name", getattr(t, "__name__", "?")) for t in (agent.tools or [])]
        subs = [a.name for a in (agent.sub_agents or [])]
        cbs = sum(
            1
            for n in (
                "before_agent_callback",
                "after_agent_callback",
                "before_model_callback",
                "after_model_callback",
                "before_tool_callback",
                "after_tool_callback",
            )
            if getattr(agent, n, None)
        )
        print(
            f"  [OK] {cp:25} name={agent.name!r:35} "
            f"tools={len(tools)} sub_agents={len(subs)} callbacks={cbs}"
        )
        agents[cp] = agent
        sys.path.pop(0)
    return agents


def check_runners(agents: dict[str, object]) -> None:
    """Create an InMemoryRunner for each agent — no API calls."""
    section("2/3 · InMemoryRunner for every agent")
    from google.adk.runners import InMemoryRunner

    for cp, agent in agents.items():
        runner = InMemoryRunner(agent=agent, app_name=f"smoke_{cp}")
        assert runner is not None
        print(f"  [OK] {cp}: Runner created")


async def check_real_call() -> None:
    """Real call to Gemini via checkpoint 04 (requires GOOGLE_API_KEY)."""
    section("3/3 · Real agent call (checkpoint 04_tools)")

    if not os.environ.get("GOOGLE_API_KEY"):
        print(
            "  [SKIP] GOOGLE_API_KEY not found.\n"
            "         To run the real test:\n"
            "         export GOOGLE_API_KEY=your_key_from_aistudio.google.com\n"
            "         python verify_setup.py"
        )
        return

    sys.path.insert(0, str(ROOT / "checkpoints" / "04_tools"))
    for m in list(sys.modules):
        if m.startswith("my_first_agent"):
            del sys.modules[m]
    mod = importlib.import_module("my_first_agent.agent")

    from google.adk.runners import InMemoryRunner
    from google.genai import types

    runner = InMemoryRunner(agent=mod.root_agent, app_name="smoke_real")
    session = await runner.session_service.create_session(
        app_name="smoke_real", user_id="smoke_user"
    )

    response_chunks: list[str] = []
    tool_calls: list[str] = []
    async for event in runner.run_async(
        user_id="smoke_user",
        session_id=session.id,
        new_message=types.Content(
            role="user",
            parts=[types.Part(text="What's the weather in New York?")],
        ),
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    response_chunks.append(part.text)
                if part.function_call:
                    tool_calls.append(part.function_call.name)

    full = "".join(response_chunks).strip()
    print(f"  [OK] LLM response: {full[:120]}{'…' if len(full) > 120 else ''}")
    print(f"  [OK] Tool calls: {tool_calls}")
    assert tool_calls, "Expected a get_weather call"
    assert "weather" in full.lower() or "york" in full.lower() or "sunny" in full.lower(), (
        f"Response doesn't look weather-related: {full!r}"
    )
    print("  [OK] Real-API smoke test passed.")


async def main() -> None:
    load_dotenv(ROOT / ".env")  # picks up GOOGLE_API_KEY if present

    agents = check_imports()
    check_runners(agents)
    await check_real_call()

    section("All OK — environment is ready for the workshop.")


if __name__ == "__main__":
    asyncio.run(main())
