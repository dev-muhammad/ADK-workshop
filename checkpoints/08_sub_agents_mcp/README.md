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

1. **LLM-coordinator** (наш пример) — координатор сам выбирает, кому делегировать, на основе `description` sub-агентов. Гибко, но недетерминированно.
2. **Workflow agents** — `SequentialAgent`, `ParallelAgent`, `LoopAgent` — детерминированный порядок без LLM на координации. Дешевле и предсказуемее.

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
1. `coordinator` вызывает делегирование к `researcher`
2. `researcher` ищет факты (если подключен `google_search`)
3. `coordinator` делегирует к `writer`
4. `writer` собирает финальный текст
5. Возврат к `coordinator` и финальный ответ пользователю

## Что пробовать

- Поменяйте `instruction` у `coordinator`: «Сначала всегда дай слово researcher'у, потом writer'у» — посмотрите, насколько модель будет следовать.
- Замените `LlmAgent` координатора на `SequentialAgent` с `sub_agents=[researcher, writer]` — увидите детерминированный пайплайн.
- Подключите реальный MCP filesystem-сервер (`npx -y @modelcontextprotocol/server-filesystem /path/to/dir`) и попросите агента прочитать README.md.
