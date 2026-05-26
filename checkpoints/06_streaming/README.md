# Checkpoint 06 · Streaming (SSE)

## What's new in this step

We turn on **streamed output** — tokens arrive at the client as they're generated, not as one final blob. This is the classic "chat" UX.

Changes:
- `agent.py` — instruction changed to "storyteller" so streaming is visually obvious on long answers.
- New file `streaming_demo.py` — shows `RunConfig(streaming_mode=StreamingMode.SSE)`.

## Theory

**Streaming in ADK is controlled by the runtime, not the agent.** The same agent can run in any of three modes:

| Mode                   | What it means                                                                | When to use                                              |
|------------------------|------------------------------------------------------------------------------|----------------------------------------------------------|
| `StreamingMode.NONE`   | No streaming, response returned all at once (default)                       | Batch processing, simple tasks                           |
| `StreamingMode.SSE`    | Server-Sent Events — token-by-token one-way stream from server to client   | Chatbots, assistants — improves UX                       |
| `StreamingMode.BIDI`   | Bidirectional via Gemini Live API — two-way channel                          | Real-time voice/video, barge-in                          |

**Things to remember:**
- In SSE mode `runner.run_async()` is still `async for event in ...` — just more events.
- Intermediate chunks are flagged `event.partial = True`. The final event has `event.is_final_response() == True`.
- `max_llm_calls` in `RunConfig` — mandatory for production: protects against infinite loops when the LLM "ping-pongs" on tool calls.

**BIDI / Live API** — requires a different model (`gemini-2.0-flash-live-001` and friends) and runs over WebSocket. `adk web` has mic and camera buttons — try them on any agent with a Live model.

## Structure

```
06_streaming/
├── my_first_agent/
│   ├── __init__.py
│   ├── agent.py             ← storyteller agent (good for visible streaming)
│   └── .env.example
└── streaming_demo.py        ← example with StreamingMode.SSE
```

## Running

**Option A — dev UI (SSE by default):**

```bash
cd checkpoints/06_streaming
adk web
```

Ask: "Tell me a long story about a coding cat."
Watch the text appear progressively.

**Option B — programmatic (you see the streaming code itself):**

```bash
cd checkpoints/06_streaming
cp my_first_agent/.env.example my_first_agent/.env
# paste GOOGLE_API_KEY

python streaming_demo.py
```

The script prints the response character by character with `flush=True` — you'll see it "drip" into the terminal.

## Things to try

- Swap `StreamingMode.SSE` for `StreamingMode.NONE` and compare — you'll see the response only appears at the end.
- Drop `max_llm_calls` to 1 and ask something that needs multiple steps — the agent will stop before finishing.
- To try BIDI/voice — switch the model to `gemini-2.0-flash-live-001`, run `adk web`, and click the mic button. Before launching: `export SSL_CERT_FILE=$(python -m certifi)`.
