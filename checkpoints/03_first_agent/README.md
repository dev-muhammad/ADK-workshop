# Checkpoint 03 · First agent: Hello, Agent!

## What's new in this step

This is the **very first** agent. No tools, no memory — just an LLM and an instruction.

Added:
- `my_first_agent/__init__.py` — `from . import agent` (required for import).
- `my_first_agent/agent.py` — defines `root_agent` via `Agent(...)`.
- `my_first_agent/.env.example` — template for GOOGLE_API_KEY.

## Theory

**What is an ADK agent?**
A minimal agent is an `LlmAgent` (aliased as `Agent`) with three required fields:

- `name` — unique identifier (used in logs and multi-agent scenarios).
- `model` — which LLM to call (`gemini-2.5-flash`, `gemini-2.0-flash`, etc.).
- `instruction` — the system prompt that sets the role and response style.

**Why this exact folder structure?**
ADK CLI (`adk run`, `adk web`) looks for:
1. Any folder name (this becomes the `agent_name` in dev UI).
2. Inside it — `__init__.py` with `from . import agent`.
3. And `agent.py` with a `root_agent` variable.

Break any of these and the agent won't show up in the `adk web` dropdown.

**`Agent` vs `LlmAgent`** — same class, `Agent` is just shorter.

## Structure

```
03_first_agent/
└── my_first_agent/
    ├── __init__.py       ← from . import agent
    ├── agent.py          ← root_agent = Agent(...)
    └── .env.example      ← copy to .env and paste your key
```

## Running

```bash
# 1. Copy .env.example to .env and paste GOOGLE_API_KEY
cd checkpoints/03_first_agent/my_first_agent
cp .env.example .env
# edit .env: GOOGLE_API_KEY=your_key

# 2. Go up to the checkpoint's parent folder (important!)
cd ..

# 3. Run
adk web           # dev UI on http://localhost:8000
# or
adk run my_first_agent   # terminal
```

In the dev UI pick `my_first_agent` from the dropdown and ask:
- "What's a list comprehension?"
- "Explain *args and **kwargs"

## Things to try

- Change `instruction` — add "answer in English only" and observe how behavior shifts.
- Swap `model="gemini-2.5-flash"` for `"gemini-2.0-flash"` and compare speed.
- Ask the agent about the weather — you'll see that without tools it gives generic answers or admits it doesn't know.
