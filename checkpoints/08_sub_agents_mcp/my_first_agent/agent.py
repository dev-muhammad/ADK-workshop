"""Блок 8. Sub-agents и MCP.

Demo multi-agent системы: coordinator делегирует задачи researcher и writer.

ВАЖНОЕ ОГРАНИЧЕНИЕ Gemini API:
    Встроенные tools (google_search, code_execution) НЕЛЬЗЯ использовать
    одновременно с обычным function-calling в одном агенте. А ADK при
    sub_agents=[...] инжектит в каждого sub-агента функцию transfer_to_agent —
    что вызывает ошибку:
        400 INVALID_ARGUMENT: Please enable
        tool_config.include_server_side_tool_invocations to use
        Built-in tools with Function calling.

РЕШЕНИЕ — паттерн AgentTool:
    Оборачиваем researcher/writer как tools координатора через AgentTool.
    Каждый sub-агент запускается изолированно (отдельный sub-runner),
    в своём контексте — никаких injected функций. Координатор просто
    вызывает их как обычные функции и получает текстовый результат.

Запуск:
    cd checkpoints/08_sub_agents_mcp
    adk web
"""

import os

# Имя модели читается из ADK_MODEL (см. .env / .env.example).
# Fallback на gemini-3.1-flash-lite — у него самый щедрый free-tier RPD (500/день).
MODEL = os.getenv("ADK_MODEL", "gemini-3.1-flash-lite")

from google.adk.agents import LlmAgent
from google.adk.tools import google_search
from google.adk.tools.agent_tool import AgentTool

# --- Sub-agent 1: исследователь (с built-in google_search) ---
# Изолирован: его google_search НЕ конфликтует ни с чем,
# потому что researcher запускается как AgentTool, без injected transfer_to_agent.
researcher = LlmAgent(
    name="researcher",
    model=MODEL,
    description="Ищет факты в интернете через Google Search.",
    instruction=(
        "Ты — исследователь. Используй google_search, чтобы найти "
        "актуальные факты по запросу. Верни структурированный список "
        "из 3–5 ключевых фактов с источниками."
    ),
    tools=[google_search],
)

# --- Sub-agent 2: писатель (без tools, только LLM) ---
writer = LlmAgent(
    name="writer",
    model=MODEL,
    description="Пишет краткие статьи на основе предоставленных фактов.",
    instruction=(
        "Ты — писатель. На основе фактов, которые передал coordinator, "
        "напиши краткую статью в 3–4 абзацах. Стиль — нейтральный, "
        "понятный широкой аудитории."
    ),
)

# --- Координатор (root agent) ---
# Использует AgentTool вместо sub_agents=[...].
# Это обходит ограничение Gemini на смешивание built-in tools и function-calling.
root_agent = LlmAgent(
    name="research_coordinator",
    model=MODEL,
    description="Координирует исследование и написание статьи.",
    instruction=(
        "Ты — координатор. На запрос пользователя:\n"
        "1. Вызови tool `researcher` — он соберёт факты через Google Search.\n"
        "2. Передай эти факты в tool `writer` — он напишет статью.\n"
        "3. Верни пользователю финальную статью.\n"
        "Не выдумывай факты сам — всегда опирайся на то, что вернул researcher."
    ),
    tools=[
        AgentTool(agent=researcher),
        AgentTool(agent=writer),
    ],
)


# --- Альтернатива: классический sub_agents pattern ---
# Работает, ТОЛЬКО если у sub-агентов НЕТ built-in tools (google_search и т.п.).
# Раскомментируйте, если хотите попробовать handoff-стиль:
#
# researcher_no_search = LlmAgent(
#     name="researcher",
#     model=MODEL,
#     description="Ищет факты (без google_search — генерирует из памяти).",
#     instruction="Опиши, что ты знаешь по теме, как факты со ссылками.",
# )
# root_agent = LlmAgent(
#     name="research_coordinator",
#     model=MODEL,
#     instruction="Делегируй researcher и writer через transfer_to_agent.",
#     sub_agents=[researcher_no_search, writer],
# )


# --- Пример MCP (закомментирован, требует MCP-сервера) ---
# Чтобы использовать MCP-сервер (например, filesystem), раскомментируйте:
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
#     instruction="Используй filesystem tools для работы с файлами в /tmp.",
#     tools=[fs_toolset],
# )
