"""Block 6. Streaming.

The agent itself stays the same — streaming is controlled via RunConfig
in the Runner, see streaming_demo.py.

Run:
    cd checkpoints/06_streaming
    python streaming_demo.py
"""

import os

# Model name is read from ADK_MODEL (see .env / .env.example).
# Falls back to gemini-3.1-flash-lite — the most generous free-tier RPD (500/day).
MODEL = os.getenv("ADK_MODEL", "gemini-3.1-flash-lite")

from google.adk.agents import Agent

root_agent = Agent(
    name="storytelling_agent",
    model=MODEL,
    description="Agent that tells long stories — perfect for demonstrating streaming.",
    instruction=(
        "You are a storyteller. When asked — tell long, detailed stories "
        "with rich descriptions. At least 5-6 paragraphs."
    ),
)
