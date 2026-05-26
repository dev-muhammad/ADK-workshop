# ADK Workshop · "Build your first AI agent!"

**Languages:** 🇬🇧 English (you are here) · [🇷🇺 Русский](README.ru.md)

Workshop materials for Google ADK (Agent Development Kit) with Python — the full agent development cycle: from a first `Hello, Agent!` to streaming, callbacks, evaluation, and deployment.

## 📅 Event

**Workshop: Exploring Google AI Studio & ADK** — organized by **GDG Khujand**.

👉 [Registration and details on GDG Community](https://gdg.community.dev/events/details/google-gdg-khujand-presents-workshop-exploring-google-ai-studio-amp-adk/)

## Author

**Muhammad Abdugafarov** — AI Product Engineer, Founder of [Lookona Labs](https://lookona.com).

- Now — building AI agents for businesses.
- Before — 8 years in software development.
- On stage — 3 years speaking at tech meetups and organizing them as part of **GDG Khujand**.

**Connect:**
- Website: [muhammads.site](https://muhammads.site)
- LinkedIn: [muhammad-abdugafarov](https://www.linkedin.com/in/muhammad-abdugafarov/)
- GitHub: [@dev-muhammad](https://github.com/dev-muhammad)
- Telegram: [@muhammad_babolo](https://t.me/muhammad_babolo)
- Instagram: [@muhammad.babolo](https://instagram.com/muhammad.babolo)

## 🎤 Workshop slides

**Google Slides (recommended for viewing and sharing):**
👉 [docs.google.com/presentation/d/1UivU9RYczYTz6pb1b-q2OAP6EcZUi6Yi2W81f8A1WMw](https://docs.google.com/presentation/d/1UivU9RYczYTz6pb1b-q2OAP6EcZUi6Yi2W81f8A1WMw/edit?usp=sharing)

Russian version: [docs.google.com/presentation/d/14VwUGWvSDmtGe7Y-PQBkPfETlWek4qiruJYJARlvvV4](https://docs.google.com/presentation/d/14VwUGWvSDmtGe7Y-PQBkPfETlWek4qiruJYJARlvvV4/edit?usp=sharing)

## What's in this repo

| File / folder                  | What it is                                                                                |
|--------------------------------|-------------------------------------------------------------------------------------------|
| `workshop_plan.md`             | Detailed 2.5-hour workshop plan (11 blocks) — for the speaker (currently RU)              |
| Slides                         | See [Google Slides](https://docs.google.com/presentation/d/1UivU9RYczYTz6pb1b-q2OAP6EcZUi6Yi2W81f8A1WMw/edit?usp=sharing) above (pptx source is not committed) |
| `workshop_notebook.ipynb`      | Colab/Jupyter notebook covering all blocks — for self-paced study                         |
| `pyproject.toml`               | Project dependencies (for `uv`)                                                            |
| `requirements.txt`             | Same for `pip` (if not using `uv`)                                                        |
| `verify_setup.py`              | Self-check script: imports every checkpoint and (with a key) makes a single live call     |
| `checkpoints/`                 | 8 ready-to-run ADK projects — one per block                                               |

## Checkpoints

Each folder is a self-contained ADK project with its own `README.md` covering theory, what's new, and how to run.

| Folder                         | Workshop block             | What it demonstrates                                                              |
|--------------------------------|----------------------------|-----------------------------------------------------------------------------------|
| [`03_first_agent/`](checkpoints/03_first_agent/README.md)               | Block 3                    | Minimal agent: LLM + instruction                                                  |
| [`04_tools/`](checkpoints/04_tools/README.md)                           | Block 4                    | Function tools (weather, time) + commented-out `google_search`                    |
| [`05_memory_sessions/`](checkpoints/05_memory_sessions/README.md)       | Block 5                    | Session/State via `tool_context.state` + `run_session_demo.py`                    |
| [`06_streaming/`](checkpoints/06_streaming/README.md)                   | Block 6                    | `RunConfig(streaming_mode=StreamingMode.SSE)` + `streaming_demo.py`               |
| [`07_callbacks/`](checkpoints/07_callbacks/README.md)                   | Block 7                    | 4 callbacks: logging, guardrail, arg normalization, signature                     |
| [`08_sub_agents_mcp/`](checkpoints/08_sub_agents_mcp/README.md)         | Block 8                    | Multi-agent: coordinator → researcher + writer via AgentTool; MCP example         |
| [`09_evaluation/`](checkpoints/09_evaluation/README.md)                 | Block 9                    | `tests/` with `test_config.json`, `basic.evalset.json`, `test_agent.py` (pytest)  |
| [`10_final/`](checkpoints/10_final/README.md)                           | Block 10                   | Final version — everything combined                                               |

## Quick start with `uv`

[uv](https://docs.astral.sh/uv/) is a fast Python package manager — recommended for this workshop.

```bash
# 1. Install uv (one-time)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Create a venv and install dependencies
cd ADK-workshop
uv venv --python 3.12
source .venv/bin/activate            # Windows: .venv\Scripts\activate
uv pip install -e .

# 3. (Optional) with dev and eval extras
uv pip install -e ".[dev,eval]"

# 4. Gemini API key (free): https://aistudio.google.com/apikey
# Option A — export in shell (one-shot, convenient for a workshop):
export GOOGLE_GENAI_USE_VERTEXAI=FALSE
export GOOGLE_API_KEY="your_key_from_aistudio.google.com"
export ADK_MODEL="gemini-3.1-flash-lite"   # optional, see below
# Option B — .env file in each checkpoint (see below)
#
# IMPORTANT: the free key has strict daily quotas (see "Free tier limits" below).
# Agents default to gemini-3.1-flash-lite (500 requests/day vs 20 for
# gemini-2.5-flash) — switch with ADK_MODEL.

# 5. Self-check
python verify_setup.py

# 6. Run the first agent
cd checkpoints/03_first_agent
cp my_first_agent/.env.example my_first_agent/.env  # paste your key
adk web                              # dev UI on http://localhost:8000
```

Alternative without uv:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Key & model configuration: `export` vs `.env`

There are **two ways** to tell ADK which API key and model to use. Pick whichever is more convenient — they can be mixed.

### Option A · `export` in your shell (recommended for workshops)

Set the variables **once** for your whole shell session — they work across all 8 checkpoints. No need to copy `.env.example → .env` in each folder.

```bash
# macOS / Linux (zsh / bash)
export GOOGLE_GENAI_USE_VERTEXAI=FALSE
export GOOGLE_API_KEY="your_key_from_aistudio.google.com"
export ADK_MODEL="gemini-3.1-flash-lite"      # optional

# Windows PowerShell
$env:GOOGLE_GENAI_USE_VERTEXAI = "FALSE"
$env:GOOGLE_API_KEY = "your_key"
$env:ADK_MODEL = "gemini-3.1-flash-lite"

# Windows CMD
set GOOGLE_GENAI_USE_VERTEXAI=FALSE
set GOOGLE_API_KEY=your_key
set ADK_MODEL=gemini-3.1-flash-lite
```

After this, any checkpoint works without a `.env`:

```bash
cd checkpoints/03_first_agent
adk web                  # picks up the key from your shell
```

**Make it persistent** (so you don't re-type it on every terminal):

```bash
# macOS (zsh) — add to ~/.zshrc
echo 'export GOOGLE_API_KEY="your_key"' >> ~/.zshrc
echo 'export ADK_MODEL="gemini-3.1-flash-lite"' >> ~/.zshrc
source ~/.zshrc

# Linux (bash) — add to ~/.bashrc
echo 'export GOOGLE_API_KEY="your_key"' >> ~/.bashrc
echo 'export ADK_MODEL="gemini-3.1-flash-lite"' >> ~/.bashrc
source ~/.bashrc
```

For per-project config without touching `~/.zshrc`, use [direnv](https://direnv.net/):

```bash
# In the ADK-workshop root:
echo 'export GOOGLE_API_KEY="your_key"' > .envrc
echo 'export ADK_MODEL="gemini-3.1-flash-lite"' >> .envrc
direnv allow
```

### Option B · `.env` per checkpoint

ADK auto-loads `.env` from the agent folder when you run `adk web` / `adk run`. Useful when different checkpoints need different settings.

```bash
cd checkpoints/03_first_agent/my_first_agent
cp .env.example .env
# edit .env, paste GOOGLE_API_KEY and, optionally, ADK_MODEL
```

### Precedence

If the same variable is set both in the shell (via `export`) and in `.env`, **the shell value usually wins** because it's already in `os.environ` by the time `load_dotenv` runs. To make `.env` always override the shell, you'd need `load_dotenv(override=True)` in your own code — not ADK's default.

### Which to pick

| Scenario                                                       | Approach                              |
|----------------------------------------------------------------|---------------------------------------|
| Workshop, one shared key, run all 8 checkpoints quickly        | **`export` in shell**                 |
| Developing several independent agents                          | `.env` per checkpoint                 |
| Production / CI                                                | shell env (via a secret manager)      |
| Multiple projects on the same machine                          | `direnv` + `.envrc`                   |

## Moving between checkpoints

Every checkpoint is self-contained. To move to the next one:

```bash
cd checkpoints/<N>_<name>
cp my_first_agent/.env.example my_first_agent/.env  # paste your key
adk web
```

Open the corresponding `README.md` inside the folder — it explains **what's new**, the **theory**, and **what to try**.

## ⚠️ Free tier limits (Google AI Studio)

The free AI Studio key has **strict per-minute (RPM), per-minute-tokens (TPM), and per-day (RPD) quotas**. For a workshop this matters a lot — 20 people × 20 requests/day on `gemini-2.5-flash` will run out fast. Current limits for the most useful models:

### Text-out models (what we use in the workshop)

| Model                                   | RPM | TPM     | RPD     | Where to use                                                  |
|-----------------------------------------|-----|---------|---------|---------------------------------------------------------------|
| `gemini-2.5-flash`                      | 5   | 250,000 | **20**  | Capable, but **very tight daily limit**                        |
| `gemini-2.5-flash-lite`                 | 10  | 250,000 | 20      | Faster and lighter, same RPD                                   |
| `gemini-3-flash`                        | 5   | 250,000 | 20      | Alternative to 2.5 flash                                       |
| `gemini-3.5-flash`                      | 5   | 250,000 | 20      | Alternative to 2.5 flash                                       |
| `gemini-3.1-flash-lite`                 | 15  | 250,000 | **500** | **Best free option** — workshop default                        |
| `gemini-2.5-pro` / `gemini-3.1-pro`     | 0   | 0       | 0       | Not available on free tier — paid plan required                |

### Other models

| Model                | RPM | TPM     | RPD     | Use                                                       |
|----------------------|-----|---------|---------|-----------------------------------------------------------|
| `gemma-4-26b`        | 15  | ∞       | 1,500   | Open-weight, unlimited tokens — good for batch jobs       |
| `gemma-4-31b`        | 15  | ∞       | 1,500   | Same, a bit more capable                                  |
| `gemini-embedding-1` | 100 | 30,000  | 1,000   | If you do RAG on top of an agent                          |
| `gemini-2.5-flash-tts` | 3 | 10,000  | 10      | Text-to-speech (for voice demos)                          |

### Live API (for the BIDI / voice block)

| Model                                    | RPM | TPM      | RPD   |
|------------------------------------------|-----|----------|-------|
| `gemini-2.5-flash-native-audio-dialog`   | ∞   | 1M       | ∞     |
| `gemini-3-flash-live`                    | ∞   | 65,000   | ∞     |

### Search grounding (for the `google_search` tool)

- Gemini 2.x: **1,500 grounded requests per day**
- Gemini 3.x: 0 (not available on free tier yet)

### Saving quota for the workshop

**For the speaker, during prep:**
- Walk through the full scenario in advance to estimate consumption.
- Create multiple API keys — AI Studio allows several per Google account.
- `num_runs > 1` in eval (default is 2) multiplies the cost — `num_runs=1` is enough for a workshop.

**For participants:**
1. **Use `gemini-3.1-flash-lite` instead of `gemini-2.5-flash`** in most examples — 500 RPD vs 20.
   ```python
   root_agent = Agent(model="gemini-3.1-flash-lite", ...)
   ```
2. **Before running evaluation**, set `num_runs=1` and use only cheap metrics (`tool_trajectory_avg_score`, `response_match_score` — skip LLM-as-Judge ones).
3. **Don't loop the streaming demo** — long stories burn through TPM quickly.
4. **Avoid putting `google_search` in every example** — it counts separately.

**If you hit a limit:**
- `429 RESOURCE_EXHAUSTED` — wait a minute, or until UTC midnight for daily reset.
- Switch to **Vertex AI Express Mode** (free tier with separate quotas): `GOOGLE_GENAI_USE_VERTEXAI=TRUE` in `.env`.
- Or switch to **Gemma** via AI Studio — much higher RPD (1,500).

> Source of these limits: your personal page at [aistudio.google.com → API keys → Plan & billing](https://aistudio.google.com/apikey). Google updates free-tier quotas periodically.

## Running tests (Block 9)

```bash
cd checkpoints/09_evaluation

# Option A — via ADK CLI
adk eval my_first_agent my_first_agent/tests/basic.evalset.json

# Option B — via pytest
pytest -v my_first_agent/tests/test_agent.py
```

## Running the notebook

```bash
uv pip install jupyter
jupyter notebook workshop_notebook.ipynb
```

Or upload `workshop_notebook.ipynb` to [Google Colab](https://colab.research.google.com/).

## Environment self-check

```bash
python verify_setup.py
```

The script verifies:
1. All 8 checkpoints import correctly.
2. Each one has the right tools / callbacks / sub_agents wired up.
3. `InMemoryRunner` can be constructed for each.
4. (If `GOOGLE_API_KEY` is set) — runs a real call against checkpoint 04 and validates the response.

## Recommended path for participants

1. Open the slides (Google Slides link above) and `workshop_plan.md` side by side — the plan has more detail than fits on slides.
2. Walk through the checkpoints in order, reading the `README.md` in each one and running it via `adk web`.
3. After Block 5, switch to `workshop_notebook.ipynb` for streaming/callbacks/eval — it's more convenient for showing programmatic runs.
4. In Block 9, run `pytest` locally.

## Links

- [ADK documentation](https://google.github.io/adk-docs/)
- [Quickstart](https://google.github.io/adk-docs/get-started/quickstart/)
- [Gemini API (AI Studio)](https://aistudio.google.com/)
- [Examples on GitHub](https://github.com/google/adk-samples)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [uv documentation](https://docs.astral.sh/uv/)
