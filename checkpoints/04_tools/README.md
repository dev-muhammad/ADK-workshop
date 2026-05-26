# Checkpoint 04 · Tools — function tools and built-in google_search

## What's new in this step

The base agent gets **tools** — functions the agent can call on its own to fetch facts or perform actions.

Changes:
- `agent.py` — two functions `get_weather(city)` and `get_current_time(city)` passed as `tools=[...]`.
- At the bottom of the file — a commented-out example with the built-in `google_search`.

## Theory

**What is a tool in ADK?**
Any plain Python function. ADK:
1. Reads its signature (name, parameters, type hints).
2. Parses the docstring (description + Args).
3. Turns all that into a JSON schema the LLM understands.
4. When the LLM decides to call a tool — ADK executes the function and feeds the result back into context.

**Why docstrings and type hints are critical:**
The LLM only sees what you wrote in the docstring and signature. Wrong type hints or missing descriptions → the model passes wrong arguments or skips the tool entirely.

**Recommended return pattern** — a `dict` with status:

```python
{"status": "success", "report": "..."}
{"status": "error", "error_message": "..."}
```

This lets the LLM tell from the shape of the response whether the tool succeeded, and handle errors gracefully.

**Built-in tools:**
- `google_search` — search with grounding in Google results.
- `code_execution` — sandboxed Python execution (Gemini 2.0+).

These cannot be mixed with regular function tools on the same agent — it's a Gemini limitation.

## Structure

```
04_tools/
└── my_first_agent/
    ├── __init__.py
    ├── agent.py          ← +2 functions + tools=[...]
    └── .env.example
```

## Running

```bash
cd checkpoints/04_tools
adk web
```

Try:
- "What's the weather in New York?" → should call `get_weather("New York")`
- "What time is it in London?" → `get_current_time("London")`
- "And in Moscow?" → agent should honestly say no data is available (sees `status: error`)

Open the **Events** tab in the dev UI — you'll see the function call and its arguments.

## Things to try

- Add your own tool, e.g. `get_exchange_rate(from_currency, to_currency)` (with a stub) and ask: "how many dollars is 100 euros?".
- Uncomment the `google_search` block (commenting out the main `root_agent`) and try "Who won the most recent FIFA World Cup?".
- Remove the docstring from `get_weather` and watch the agent stop calling it correctly.
