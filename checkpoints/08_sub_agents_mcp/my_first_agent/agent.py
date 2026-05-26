"""Block 8. Sub-agents and MCP.

Multi-agent demo: a coordinator delegates tasks to researcher and writer.

IMPORTANT Gemini API LIMITATION:
    Built-in tools (google_search, code_execution) CANNOT be used together
    with regular function-calling on the same agent. And with sub_agents=[...],
    ADK auto-injects a `transfer_to_agent` function into each sub-agent —
    which triggers:
        400 INVALID_ARGUMENT: Please enable
        tool_config.include_server_side_tool_invocations to use
        Built-in tools with Function calling.

SOLUTION — the AgentTool pattern:
    Wrap researcher/writer as tools of the coordinator via AgentTool.
    Each sub-agent runs in isolation (its own sub-runner), in its own context —
    no injected functions. The coordinator simply calls them like regular
    functions and gets a textual result back.

Run:
    cd checkpoints/08_sub_agents_mcp
    adk web
"""

import os

# Model name is read from ADK_MODEL (see .env / .env.example).
# Falls back to gemini-3.1-flash-lite — the most generous free-tier RPD (500/day).
MODEL = os.getenv("ADK_MODEL", "gemini-3.1-flash-lite")

from google.adk.agents import LlmAgent
from google.adk.tools import google_search
from google.adk.tools.agent_tool import AgentTool

# --- Sub-agent 1: researcher (with built-in google_search) ---
# Isolated: its google_search does NOT conflict with anything,
# because researcher is run as an AgentTool, without an injected transfer_to_agent.
researcher = LlmAgent(
    name="researcher",
    model=MODEL,
    description="Searches the web for facts using Google Search.",
    instruction=(
        "You are a researcher. Use google_search to find "
        "current facts on the user's query. Return a structured list "
        "of 3–5 key facts with sources."
    ),
    tools=[google_search],
)

# --- Sub-agent 2: writer (no tools, LLM only) ---
writer = LlmAgent(
    name="writer",
    model=MODEL,
    description="Writes short articles based on provided facts.",
    instruction=(
        "You are a writer. Based on the facts handed over by the coordinator, "
        "write a short 3–4 paragraph article. Style: neutral, accessible "
        "to a general audience."
    ),
)

# --- Coordinator (root agent) ---
# Uses AgentTool instead of sub_agents=[...].
# This sidesteps Gemini's restriction on mixing built-in tools and function-calling.
root_agent = LlmAgent(
    name="research_coordinator",
    model=MODEL,
    description="Coordinates research and article writing.",
    instruction=(
        "You are the coordinator. For the user's request:\n"
        "1. Call the `researcher` tool — it will gather facts via Google Search.\n"
        "2. Pass those facts to the `writer` tool — it will draft the article.\n"
        "3. Return the final article to the user.\n"
        "Do not invent facts yourself — always rely on what researcher returned."
    ),
    tools=[
        AgentTool(agent=researcher),
        AgentTool(agent=writer),
    ],
)


# --- Alternative: classic sub_agents pattern ---
# Works ONLY when sub-agents have NO built-in tools (google_search etc.).
# Uncomment to try the handoff style:
#
# researcher_no_search = LlmAgent(
#     name="researcher",
#     model=MODEL,
#     description="Looks up facts (no google_search — generates from memory).",
#     instruction="Describe what you know on the topic, as facts with references.",
# )
# root_agent = LlmAgent(
#     name="research_coordinator",
#     model=MODEL,
#     instruction="Delegate to researcher and writer via transfer_to_agent.",
#     sub_agents=[researcher_no_search, writer],
# )


# --- MCP example (commented out, requires an MCP server) ---
# To use an MCP server (e.g., filesystem), uncomment:
#
# from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters
#
# fs_toolset = MCPToolset(
#     connection_params=StdioServerParameters(
#         command="npx",
#         args=["-y", "@modelcontextprotocol/server-filesystem", "/tmp"],
#     ),
# )
#
# root_agent = LlmAgent(
#     name="file_agent",
#     model=MODEL,
#     instruction="Use filesystem tools to work with files under /tmp.",
#     tools=[fs_toolset],
# )
