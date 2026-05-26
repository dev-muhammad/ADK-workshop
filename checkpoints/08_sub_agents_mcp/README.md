# Checkpoint 08 · Sub-agents and MCP

## What's new in this step

We go from a single agent to a **multi-agent system**: a coordinator delegates tasks to specialized sub-agents. Also — a conceptual example of attaching external tools via MCP.

Changes:
- `agent.py` — three agents: `researcher`, `writer`, and `coordinator` using `AgentTool` (see why below).
- Commented section — example with `MCPToolset` for connecting a filesystem MCP server.

## Theory

**Why sub-agents?**
When a task gets complex, a single prompt quickly becomes spaghetti. Better to split into specialized agents:

- Each gets its own narrow `instruction` and tool set.
- The coordinator decides who to delegate to, based on the sub-agents' `description`.
- Each sub-agent is a full `LlmAgent` — you can nest further.

**Two main types of multi-agent:**

1. **AgentTool pattern** (our example) — sub-agents are wrapped in `AgentTool` and given to the coordinator as regular tools. The coordinator calls them via function-calling, gets a text result.
2. **`sub_agents=[...]` handoff** — classic "pass the turn". The coordinator calls `transfer_to_agent("researcher")`, context switches to the sub-agent, then returns. More flexible but has a major caveat (see below).
3. **Workflow agents** — `SequentialAgent`, `ParallelAgent`, `LoopAgent` — deterministic order, no LLM as coordinator. Cheaper and predictable.

### ⚠️ Why AgentTool here and not sub_agents

The Gemini API **does not allow** mixing **built-in tools** (`google_search`, `code_execution`) with regular function-calling on the same agent. And with `sub_agents=[...]`, ADK auto-injects a `transfer_to_agent` function into each sub-agent — which triggers:

```
400 INVALID_ARGUMENT: Please enable
tool_config.include_server_side_tool_invocations to use
Built-in tools with Function calling.
```

`AgentTool` works around this: the sub-agent runs **in its own sub-runner**, in isolation — no `transfer_to_agent` is injected, `google_search` lives alone.

**When `sub_agents=[...]` is fine:** if the sub-agents have no built-in tools (LLM only or function tools only).

**MCP (Model Context Protocol)?**
An open standard for connecting external tools and data to AI agents — like "USB-C for AI". The same MCP server can be plugged into ADK, Claude Desktop, Cursor, any compatible client.

Pre-built MCP servers exist for: filesystem, GitHub, Slack, Notion, Postgres, Stripe, and dozens of other services. Wire them into ADK via `MCPToolset`:

```python
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset

mcp_tools = MCPToolset(
    connection_params=...,   # how to launch the MCP server
)

agent = LlmAgent(
    name="file_agent",
    tools=[*mcp_tools.get_tools()],
)
```

After that — without writing a single function — your agent has access to every tool the MCP server exposes.

## Structure

```
08_sub_agents_mcp/
└── my_first_agent/
    ├── __init__.py
    ├── agent.py          ← coordinator + researcher + writer (AgentTool)
    └── .env.example
```

## Running

```bash
cd checkpoints/08_sub_agents_mcp
adk web
```

Try: "Write a short article about Python decorators."

In the dev UI open the **Events** tab — you'll see:
1. `coordinator` calls the **tool** `researcher(request=...)` (it's an AgentTool, not a transfer)
2. Inside researcher: a `google_search` call, then building the list of facts
3. The AgentTool result is returned to the coordinator as a regular function-response
4. `coordinator` calls the **tool** `writer(facts=...)` — it writes the article
5. `coordinator` returns the final article to the user

## Things to try

- Change `coordinator`'s `instruction`: "Always give the floor to researcher first, then writer" — observe how closely the model follows.
- Replace the coordinator `LlmAgent` with a `SequentialAgent` and `sub_agents=[researcher, writer]` — you'll see a deterministic pipeline.
- Wire up a real filesystem MCP server (`npx -y @modelcontextprotocol/server-filesystem /path/to/dir`) and ask the agent to read README.md.
