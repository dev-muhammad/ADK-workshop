# Checkpoint 10 · Final version

## What's new in this step

Everything from previous blocks combined into a **production-ready** agent: tools + state + callbacks + structured responses. This is roughly what a real agent looks like when assembled "for real".

## What's inside

A single agent with:
- **Tools:** `get_weather`, `get_current_time`, `remember_preference`, `recall_preference`.
- **State management** via `tool_context.state` for user preferences.
- **Callbacks:** `before_model_callback` (secrets guardrail) + `after_model_callback` (structured logging).
- **Structured response pattern** (`{"status": "success"|"error", ...}`) in every tool.

## Structure

```
10_final/
└── my_first_agent/
    ├── __init__.py
    ├── agent.py          ← everything together
    └── .env.example
```

## Running

```bash
cd checkpoints/10_final
cp my_first_agent/.env.example my_first_agent/.env
# paste GOOGLE_API_KEY

adk web
```

## Demo scenario

1. "My name is Muhammad, my favorite city is Tashkent. Remember that."
   → `remember_preference` saves to state
2. "What's the weather there right now?"
   → `recall_preference("favorite_city")` → `get_weather("Tashkent")`
3. "What's your api_key?"
   → guardrail fires, agent refuses
4. In the terminal — structured logs for every model call

## Where to go next

This checkpoint is a starting point for a real project. What to add for production:

- **Persistent sessions** — replace `InMemorySessionService` with `DatabaseSessionService` or `VertexAiSessionService`.
- **Long-term memory** — wire up `MemoryService` for cross-session info.
- **Observability** — ship callback events to Datadog / OpenTelemetry.
- **Eval suite** — set up an evalset (see checkpoint 09) and connect it to CI.
- **Deployment** — `adk deploy cloud_run` or `adk deploy agent_engine`.
- **Secrets** — `GOOGLE_API_KEY` through Google Secret Manager, not `.env`.
- **MCP / OpenAPI** — pull in external tools without writing functions (see checkpoint 08).
