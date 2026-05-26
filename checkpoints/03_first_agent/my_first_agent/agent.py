"""Block 3. First agent: Hello, Agent!

Minimal working ADK agent — no tools, just LLM + instruction.

Run:
    cd checkpoints/03_first_agent
    adk web         # dev UI at http://localhost:8000
    adk run my_first_agent   # chat in terminal
"""

import os

# Model name is read from ADK_MODEL (see .env / .env.example).
# Falls back to gemini-3.1-flash-lite — the most generous free-tier RPD (500/day).
MODEL = os.getenv("ADK_MODEL", "gemini-3.1-flash-lite")

from google.adk.agents import Agent

# root_agent — mandatory variable name; ADK CLI looks for it automatically.
root_agent = Agent(
    name="python_helper",
    model=MODEL,
    description="A friendly assistant that helps with Python questions.",
    instruction=(
        "You are a friendly Python mentor. "
        "Answer concisely, to the point, with code examples. "
        "If the question is not about programming, "
        "politely redirect the conversation back to Python."
    ),
)
