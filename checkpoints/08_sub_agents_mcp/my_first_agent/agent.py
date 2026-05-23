"""Блок 8. Sub-agents и MCP.

Demo multi-agent системы: coordinator делегирует задачи researcher и writer.

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

# --- Sub-agent 1: исследователь ---
researcher = LlmAgent(
    name="researcher",
    model=MODEL,
    description="Ищет факты в интернете через Google Search.",
    instruction=(
        "Ты — исследователь. Используй google_search, чтобы найти "
        "актуальные факты по запросу пользователя. Верни структурированный "
        "список из 3-5 ключевых фактов с источниками."
    ),
    tools=[google_search],
)

# --- Sub-agent 2: писатель ---
writer = LlmAgent(
    name="writer",
    model=MODEL,
    description="Пишет краткие статьи на основе предоставленных фактов.",
    instruction=(
        "Ты — писатель. На основе фактов, которые передал researcher, "
        "напиши краткую статью в 3-4 абзацах. Стиль — нейтральный, "
        "понятный широкой аудитории."
    ),
)

# --- Координатор (root agent) ---
root_agent = LlmAgent(
    name="research_coordinator",
    model=MODEL,
    description="Координирует исследование и написание статьи.",
    instruction=(
        "Ты — координатор. На запрос пользователя:\n"
        "1. Передай задачу researcher для сбора фактов.\n"
        "2. Затем передай факты writer для написания статьи.\n"
        "3. Верни пользователю финальную статью."
    ),
    sub_agents=[researcher, writer],
)


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
#     model="gemini-2.5-flash",
#     instruction="Используй filesystem tools для работы с файлами в /tmp.",
#     tools=[fs_toolset],
# )
