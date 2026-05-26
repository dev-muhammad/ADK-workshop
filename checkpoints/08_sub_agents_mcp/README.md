# Checkpoint 08 · Sub-agents и MCP

## Что нового в этом шаге

Перешли от одиночного агента к **multi-agent системе**: координатор делегирует задачи специализированным sub-агентам. Также — концептуальный пример подключения внешних tools через MCP.

Изменили:
- `agent.py` — три агента: `researcher`, `writer` и `coordinator` с `sub_agents=[researcher, writer]`.
- В комментариях — пример с `MCPToolset` для подключения filesystem MCP-сервера.

## Теория

**Зачем нужны sub-agents?**
Когда задача сложная — единый промпт быстро становится «спагетти». Лучше разбить на специализированных агентов:

- У каждого свой узкий `instruction` и набор tools.
- Координатор сам решает, какому sub-agent передать ход (на основе их `description`).
- Каждый sub-agent — это полноценный `LlmAgent`, можно вкладывать дальше.

**Два типа multi-agent:**

1. **AgentTool pattern** (наш пример) — sub-агенты оборачиваются в `AgentTool` и передаются координатору как обычные tools. Координатор вызывает их через function-calling, получает текстовый результат.
2. **`sub_agents=[...]` handoff** — классический «передача хода». Координатор делает `transfer_to_agent("researcher")`, контекст переключается на sub-агента, потом возвращается. Гибче, но имеет важное ограничение (см. ниже).
3. **Workflow agents** — `SequentialAgent`, `ParallelAgent`, `LoopAgent` — детерминированный порядок без LLM на координации. Дешевле и предсказуемее.

### ⚠️ Почему здесь AgentTool, а не sub_agents

Gemini API **не разрешает** смешивать **built-in tools** (`google_search`, `code_execution`) с обычным function-calling в одном агенте. А при `sub_agents=[...]` ADK автоматически инжектит в sub-агента функцию `transfer_to_agent` — что вызывает ошибку:

```
400 INVALID_ARGUMENT: Please enable
tool_config.include_server_side_tool_invocations to use
Built-in tools with Function calling.
```

`AgentTool` обходит проблему: sub-агент запускается **в собственном sub-runner'е**, изолированно — никакого `transfer_to_agent` ему не добавляют, `google_search` живёт один.

**Когда `sub_agents=[...]` ОК:** если у sub-агентов нет built-in tools (только LLM или function tools).

**Что такое MCP (Model Context Protocol)?**
Открытый стандарт для подключения внешних tools и данных к AI-агентам — как «USB-C для AI». Один и тот же MCP-сервер можно подключить к ADK, Claude Desktop, Cursor, любому совместимому клиенту.

Готовые MCP-серверы существуют для: filesystem, GitHub, Slack, Notion, Postgres, Stripe и десятков других сервисов. В ADK подключаются через `MCPToolset`:

```python
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset

mcp_tools = MCPToolset(
    connection_params=...,   # как запустить MCP-сервер
)

agent = LlmAgent(
    name="file_agent",
    tools=[*mcp_tools.get_tools()],
)
```

После этого, не написав ни одной функции, агент получает доступ ко всем tools, которые экспортирует MCP-сервер.

## Структура

```
08_sub_agents_mcp/
└── my_first_agent/
    ├── __init__.py
    ├── agent.py          ← coordinator + researcher + writer
    └── .env.example
```

## Запуск

```bash
cd checkpoints/08_sub_agents_mcp
adk web
```

Попробуйте: «Напиши краткую статью про Python decorators.»

В dev UI откройте вкладку **Events** — увидите:
1. `coordinator` вызывает **tool** `researcher(request=...)` (это AgentTool, не transfer)
2. Внутри researcher: вызов `google_search`, формирование списка фактов
3. Результат AgentTool возвращается в coordinator как обычный function-response
4. `coordinator` вызывает **tool** `writer(facts=...)` — он пишет статью
5. `coordinator` возвращает финальную статью пользователю

## Что пробовать

- Поменяйте `instruction` у `coordinator`: «Сначала всегда дай слово researcher'у, потом writer'у» — посмотрите, насколько модель будет следовать.
- Замените `LlmAgent` координатора на `SequentialAgent` с `sub_agents=[researcher, writer]` — увидите детерминированный пайплайн.
- Подключите реальный MCP filesystem-сервер (`npx -y @modelcontextprotocol/server-filesystem /path/to/dir`) и попросите агента прочитать README.md.
