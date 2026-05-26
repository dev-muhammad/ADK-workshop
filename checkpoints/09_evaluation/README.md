# Checkpoint 09 · Evaluation — measuring agent quality

## What's new in this step

We add a **`tests/` folder** with the full setup to run evaluation: `test_config.json`, `basic.evalset.json`, a pytest wrapper. This lets you run regression tests automatically on every prompt/model change.

Changes:
- `agent.py` — the baseline weather+time agent.
- New files: `tests/test_config.json`, `tests/basic.evalset.json`, `tests/test_agent.py`.

## Theory

**Why evaluation?**
After every change (new model, new prompt, new tool) you want to automatically know: did it get better or worse? Without eval, you'll run manual "smoke" tests — slowly and inconsistently.

**Three ways to run eval in ADK:**

| Method        | When                              | Command                                         |
|---------------|-----------------------------------|-------------------------------------------------|
| **Dev UI**    | Interactive debugging             | `adk web` → Eval tab                            |
| **CLI**       | For CI/CD pipelines               | `adk eval <agent_folder> <evalset_file>`        |
| **pytest**    | Regression tests in a test suite  | `AgentEvaluator.evaluate(...)`                  |

**File layout:**

- `test_config.json` — thresholds per metric. If a score < threshold — the test fails.
- `<name>.evalset.json` — eval cases in the new schema (multi-turn conversations).
- `<name>.test.json` — simple single-turn tests in the old schema.

**Seven key metrics:**

| Metric                                  | What it measures                                                | Cost                    |
|------------------------------------------|------------------------------------------------------------------|-------------------------|
| `tool_trajectory_avg_score`              | Match of the tool-call sequence                                  | Free (string match)     |
| `response_match_score`                   | ROUGE-1 similarity to reference                                  | Free                    |
| `final_response_match_v2`                | Semantic match (LLM-as-Judge)                                    | Paid (model call)       |
| `rubric_based_final_response_quality_v1` | Response quality per your rubrics                                | Paid                    |
| `rubric_based_tool_use_quality_v1`       | Tool-use quality per rubrics                                     | Paid                    |
| `hallucinations_v1`                      | Hallucination check against context                              | Paid                    |
| `safety_v1`                              | Response safety (via Vertex AI Eval SDK, needs GCP)              | Paid                    |

**Strategy:** in CI on every PR — only the cheap metrics (`tool_trajectory_avg_score` + `response_match_score`). The expensive LLM-as-Judge ones — run on a nightly cron or manually before release.

**`tool_trajectory_avg_score` match types:**
- `EXACT` (default) — exact sequence match.
- `IN_ORDER` — required tools must appear in order, extras allowed in between.
- `ANY_ORDER` — required tools must appear, order doesn't matter.

## Structure

```
09_evaluation/
└── my_first_agent/
    ├── __init__.py
    ├── agent.py
    ├── .env.example
    └── tests/
        ├── __init__.py
        ├── test_config.json        ← thresholds
        ├── basic.evalset.json      ← test cases
        └── test_agent.py           ← pytest wrapper
```

## Running

```bash
cd checkpoints/09_evaluation

# Prepare .env
cp my_first_agent/.env.example my_first_agent/.env
# paste GOOGLE_API_KEY

# Option A — via ADK CLI
adk eval my_first_agent my_first_agent/tests/basic.evalset.json

# Option B — via pytest
pytest -v my_first_agent/tests/test_agent.py
```

On success — you'll see `PASSED` and the metrics. On failure — a table with expected vs actual per invocation.

## Things to try

- Add a case to `basic.evalset.json`: "What's the weather in Tashkent?" with the expected tool call `get_weather("Tashkent")`.
- Remove `get_weather` from tools and run the tests — `tool_trajectory_avg_score` will drop.
- Add `final_response_match_v2` to `test_config.json` with threshold `0.8` — you'll see an extra paid run through LLM-as-Judge.
- Wire the tests into CI: `pytest` in GitHub Actions with `GOOGLE_API_KEY` from secrets.
