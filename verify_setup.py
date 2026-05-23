"""Smoke-test всей установки: импорты, инстанцирование, реальный вызов LLM.

Запуск:
    # из корня репозитория, в активированном .venv
    cp checkpoints/04_tools/my_first_agent/.env.example .env
    # отредактируйте .env и впишите GOOGLE_API_KEY
    python verify_setup.py

Что проверяется:
  1. Каждый checkpoint импортируется и `root_agent` существует.
  2. У всех агентов корректные tools/callbacks/sub_agents.
  3. InMemoryRunner запускается для каждого.
  4. (Если есть GOOGLE_API_KEY) — реальный вызов агента из checkpoint 04 и проверка ответа.
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
    """Импортирует root_agent для каждого checkpoint и возвращает их."""
    section("1/3 · Импорт всех checkpoint-агентов")
    agents = {}
    for cp in CHECKPOINTS:
        sys.path.insert(0, str(ROOT / "checkpoints" / cp))
        # сбросить кэшированный модуль, чтобы импортировать заново
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
    """Создаёт InMemoryRunner для каждого агента — без API-вызовов."""
    section("2/3 · InMemoryRunner для каждого агента")
    from google.adk.runners import InMemoryRunner

    for cp, agent in agents.items():
        runner = InMemoryRunner(agent=agent, app_name=f"smoke_{cp}")
        assert runner is not None
        print(f"  [OK] {cp}: Runner создан")


async def check_real_call() -> None:
    """Реально вызывает Gemini через checkpoint 04 (нужен GOOGLE_API_KEY)."""
    section("3/3 · Реальный вызов агента (checkpoint 04_tools)")

    if not os.environ.get("GOOGLE_API_KEY"):
        print(
            "  [SKIP] GOOGLE_API_KEY не найден.\n"
            "         Чтобы прогнать реальный тест:\n"
            "         export GOOGLE_API_KEY=ваш_ключ_из_aistudio.google.com\n"
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
    print(f"  [OK] Ответ от LLM: {full[:120]}{'…' if len(full) > 120 else ''}")
    print(f"  [OK] Tool calls: {tool_calls}")
    assert tool_calls, "Ожидался вызов get_weather"
    assert "weather" in full.lower() or "погод" in full.lower() or "york" in full.lower(), (
        f"Ответ не похож на ответ о погоде: {full!r}"
    )
    print("  [OK] Smoke-тест с реальным API прошёл.")


async def main() -> None:
    load_dotenv(ROOT / ".env")  # подтянуть GOOGLE_API_KEY, если есть

    agents = check_imports()
    check_runners(agents)
    await check_real_call()

    section("Всё OK — окружение готово к воркшопу.")


if __name__ == "__main__":
    asyncio.run(main())
