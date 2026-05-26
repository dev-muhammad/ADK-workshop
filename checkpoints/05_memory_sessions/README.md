# Checkpoint 05 · Memory & Sessions

## What's new in this step

The agent gets **structured memory** within a session, plus a demonstration of programmatic session management via `InMemoryRunner`.

Changes:
- `agent.py` — two new tools `remember_preference(key, value)` and `recall_preference(key)` working with `tool_context.state`.
- New file `run_session_demo.py` — demonstrates programmatic execution with a multi-turn conversation.

## Theory

**Three levels of "memory" in ADK:**

| Level     | Class / field                                | What it stores                                                     |
|-----------|----------------------------------------------|--------------------------------------------------------------------|
| Session   | `Session`, `InMemorySessionService`          | Message and event history of a single conversation (automatic)     |
| State     | `session.state` / `tool_context.state`       | Structured dict inside a session (name, preferences, flags)        |
| Memory    | `MemoryService`                              | Long-term memory across sessions (profile, RAG indices)            |

**Session** — the fact "conversation X for user Y". ADK manages the message history itself.

**State** — a `dict` that lives inside a session. You can:
- Read/write from a tool via `tool_context.state["key"]`.
- Pass it to a callback via `callback_context.state`.
- Watch it live in `adk web` → State tab.

**Memory** — for information that should outlive a session (e.g., "user prefers compact answers"). In production: `VertexAiMemoryService`, `DatabaseMemoryService`, etc.

**Important rule:** `InMemorySessionService` and `InMemoryRunner` are dev-only. In production pick `DatabaseSessionService` (Postgres/MySQL), `VertexAiSessionService`, or a Redis-backed one.

## Structure

```
05_memory_sessions/
├── my_first_agent/
│   ├── __init__.py
│   ├── agent.py              ← + remember_preference / recall_preference
│   └── .env.example
└── run_session_demo.py       ← programmatic run via InMemoryRunner
```

## Running

**Option A — dev UI:**

```bash
cd checkpoints/05_memory_sessions
adk web
```

Conversation script:
1. "My favorite city is Tashkent. Remember that."
2. "What's the weather there?" (should use the saved city)
3. "And what did I tell you about my preferences?"

In the dev UI open the **State** tab — watch `state["favorite_city"]` grow.

**Option B — programmatic run:**

```bash
cd checkpoints/05_memory_sessions
# prepare .env
cp my_first_agent/.env.example my_first_agent/.env
# paste GOOGLE_API_KEY

python run_session_demo.py
```

This script shows how, from your own Python code, to:
- create an `InMemoryRunner`,
- start a session,
- send messages via `runner.run_async(...)`,
- receive events and final responses.

## Things to try

- In different sessions for the same user, save different `favorite_city` values — confirm state doesn't "leak".
- Add a tool `clear_all_preferences(tool_context)` and ask the agent to forget everything.
- In `run_session_demo.py`, save `session.id` to a file and on the next run continue the conversation — remember: `InMemorySessionService` lives only in the process's memory; you need another `SessionService` for persistence.
