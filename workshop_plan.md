# Воркшоп: «Build your first AI agent!»

**Тема:** Полный цикл разработки AI-агента с помощью Google ADK (Agent Development Kit) на Python — от первого `Hello, Agent!` до streaming, callbacks, evaluation и деплоя.
**Целевая аудитория:** Python-разработчики без опыта с AI-агентами.
**Формат:** Guided Jupyter / Google Colab notebook + локальный проект `adk run` / `adk web`.
**LLM backend:** Google Gemini (через AI Studio API key — бесплатный tier).
**Базовая длительность:** ~2 ч 30 мин (модульно — можно сократить до 1.5 ч, см. ниже).

---

## Цели воркшопа

К концу воркшопа участник сможет:

1. Объяснить, что такое AI-агент, и описать его архитектуру: LLM, instruction, tools, memory, sub-agents, MCP, callbacks, streaming.
2. С нуля собрать рабочий ADK-проект (правильная структура папок, `.env`, `adk run`, `adk web`, `adk api_server`).
3. Подключить к агенту function tools и встроенные tools (`google_search`).
4. Управлять сессией и состоянием (`Session`, `State`, `Memory`).
5. Включить streaming-вывод ответа (SSE) и понимать, когда нужен BIDI/Live.
6. Использовать callbacks для логирования, guardrail'ов и подмены поведения модели/инструментов.
7. Написать evalset, оценить агента через `adk eval` и pytest, понимать метрики `tool_trajectory_avg_score`, `response_match_score` и LLM-as-a-Judge.
8. Знать варианты деплоя (Agent Engine, Cloud Run, GKE) и куда смотреть дальше.

---

## Что понадобится участникам заранее

- Python 3.10+ установлен локально (для `adk web` / `adk run` — обязательно локально).
- Аккаунт Google + бесплатный API-ключ Gemini: https://aistudio.google.com/apikey
- IDE на выбор (VS Code / PyCharm).
- Установленные пакеты:

  ```bash
  python -m venv .venv
  source .venv/bin/activate   # Windows: .venv\Scripts\activate
  pip install google-adk python-dotenv pytest
  ```

> **Совет организатору:** заранее раздайте репозиторий с заготовкой структуры проекта, готовым `.env.example` и checkpoint-ветками по каждому блоку — это съедает 10–15 минут, если делать на самом воркшопе.

> **⚠️ Лимиты free tier:** `gemini-2.5-flash` на free-ключе AI Studio имеет всего **20 запросов в день** (RPD = 20, RPM = 5). На воркшоп из 20 участников это критично — рекомендуйте всем сразу заменить модель на `gemini-3.1-flash-lite` (500 RPD, 15 RPM) в `agent.py`:
> ```python
> root_agent = Agent(model="gemini-3.1-flash-lite", ...)
> ```
> Полная таблица лимитов и стратегии экономии — в [README.md](README.md#%EF%B8%8F-лимиты-free-tier-google-ai-studio) → раздел «Лимиты free tier».

---

## Структура воркшопа

Полная версия — 11 блоков, ~2 ч 30 мин. Можно проводить как:

- **Compact (1.5 ч):** блоки 1–5 + 7 + 11.
- **Standard (2.5 ч):** все блоки.
- **Extended (3+ ч):** добавить hands-on по callbacks/eval и реальный деплой в Cloud Run.

| #  | Время       | Блок                                                  | Формат               |
|----|-------------|-------------------------------------------------------|----------------------|
| 1  | 00:00–00:15 | Что такое AI-агент и его архитектура                  | Слайды + обсуждение  |
| 2  | 00:15–00:25 | Project setup: структура, `.env`, ADK CLI             | Live setup           |
| 3  | 00:25–00:40 | Первый агент: Hello, Agent!                           | Код + `adk run`      |
| 4  | 00:40–00:55 | Tools: function tools + `google_search`               | Код + `adk web`      |
| 5  | 00:55–01:10 | Memory & Sessions (Session / State / Memory)          | Код                  |
| 6  | 01:10–01:25 | Streaming (SSE, partial events, краткий обзор BIDI)   | Код + демо           |
| 7  | 01:25–01:45 | Callbacks: логирование, guardrails, фильтры           | Код                  |
| 8  | 01:45–01:55 | Sub-agents и MCP — обзор                              | Демо                 |
| 9  | 01:55–02:15 | Evaluation: evalset, `adk eval`, pytest, метрики      | Код + CLI            |
| 10 | 02:15–02:25 | Deployment: Agent Engine / Cloud Run / GKE — обзор    | Слайды               |
| 11 | 02:25–02:35 | Q&A + куда двигаться дальше                           | Обсуждение           |

---

## Блок 1. Что такое AI-агент и его архитектура (15 мин)

### Ключевые тезисы

**Что такое агент?**
Агент — это система, в которой LLM сама решает, какие действия выполнить, чтобы достичь цели пользователя. В отличие от обычного `prompt → response`, агент работает в цикле «думай → действуй → наблюдай → думай дальше», пока задача не будет решена.

**LLM vs Agent — простая аналогия:**

- LLM — это «мозг», который умеет рассуждать и генерировать текст.
- Агент — это «сотрудник» с мозгом (LLM), инструкциями (system prompt), доступом к инструментам (tools), памятью (memory), коллегами (sub-agents), охраной (callbacks) и микрофоном для прямой связи (streaming).

### Компоненты архитектуры ADK

1. **LLM (модель)** — «мозг» агента. У нас — Gemini (`gemini-2.5-flash`, `gemini-2.0-flash`).
2. **Instruction / System prompt** — роль, правила, стиль, ограничения.
3. **Tools** — функции, которые агент может вызвать: поиск, калькулятор, обращение к API.
4. **Sessions / State / Memory** — что агент помнит внутри сессии и между сессиями.
5. **Sub-agents** — другие агенты, которым можно делегировать задачи.
6. **MCP (Model Context Protocol)** — стандарт подключения к внешним серверам с инструментами.
7. **Callbacks** — точки расширения для логирования, guardrail'ов, подмены поведения.
8. **Streaming** — потоковая выдача ответа (SSE) или двусторонний канал (BIDI / Live API).
9. **Evaluation** — измерение качества агента (tool trajectory, response match, hallucinations, safety).
10. **Runtime / Deployment** — где и как агент крутится: `adk run`, `adk web`, `adk api_server`, Agent Engine, Cloud Run, GKE.

### Почему именно ADK?

- Официальный фреймворк от Google, open-source (есть Python, TypeScript, Go, Java).
- Из коробки: Gemini, function tools, sessions, memory, sub-agents, MCP, A2A, callbacks, streaming, evaluation.
- Встроенный dev UI (`adk web`) с инспекцией событий, traces, и eval-вкладкой.
- Production-ready: тот же фреймворк используется внутри Google и деплоится в Vertex AI Agent Engine.

> **Интерактив:** «Какую задачу из вашей работы вы бы хотели поручить агенту?» Соберите 2–3 примера — к ним возвращайтесь по ходу воркшопа (особенно в блоке Evaluation).

---

## Блок 2. Project setup: структура, `.env`, ADK CLI (10 мин)

ADK ожидает строго определённую структуру папок, иначе CLI и dev UI не найдут агента.

### Создание окружения

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install google-adk
```

### Структура проекта

```
parent_folder/
└── my_first_agent/         # имя папки = имя агента в dropdown'е adk web
    ├── __init__.py
    ├── agent.py            # ОБЯЗАТЕЛЬНО содержит переменную root_agent
    └── .env                # ключи и режим (AI Studio vs Vertex AI)
```

**`__init__.py`:**

```python
from . import agent
```

**`.env` (для AI Studio):**

```
GOOGLE_GENAI_USE_VERTEXAI=FALSE
GOOGLE_API_KEY=PASTE_YOUR_KEY_HERE
```

### Команды ADK CLI

| Команда                | Зачем                                                                  |
|------------------------|------------------------------------------------------------------------|
| `adk run my_first_agent` | Чат с агентом в терминале                                            |
| `adk web`              | Локальный dev UI на http://localhost:8000 с инспекцией событий и trace |
| `adk api_server`       | Локальный FastAPI-сервер для тестов через cURL                         |
| `adk eval ...`         | Запуск evalset (блок 9)                                                |
| `adk deploy ...`       | Деплой в Cloud Run / Agent Engine (блок 10)                            |

> **Подводный камень:** `adk web` нужно запускать **из родительской папки**, а не из папки самого агента. Иначе агент не появится в dropdown'е.
>
> **Подводный камень (Windows):** при ошибке `_make_subprocess_transport NotImplementedError` запускайте `adk web --no-reload`.

---

## Блок 3. Первый агент: Hello, Agent! (15 мин)

### Цель

Сделать минимального рабочего агента в правильной структуре и потрогать его через `adk web`.

### `my_first_agent/agent.py`

```python
from google.adk.agents import Agent

root_agent = Agent(
    name="python_helper",
    model="gemini-2.5-flash",
    description="Дружелюбный ассистент, помогающий с вопросами по Python.",
    instruction=(
        "Ты — дружелюбный наставник по Python. "
        "Отвечай кратко, по делу и с примерами кода. "
        "Если вопрос не связан с программированием, вежливо переводи разговор обратно к Python."
    ),
)
```

### Запуск

```bash
# из parent_folder
adk web
# открыть http://localhost:8000, выбрать my_first_agent
```

или в терминале:

```bash
adk run my_first_agent
```

### Что обсудить

- `Agent` — это alias `LlmAgent`. Оба валидны.
- `name`, `description`, `instruction`, `model` — обязательный минимум.
- В `adk web` вкладка **Events** показывает каждое сообщение / function call / model response, вкладка **Trace** — латентность каждого шага. Это главный инструмент отладки.
- Поэкспериментируйте с `instruction`: уберите строку про Python и посмотрите, как меняется поведение.

---

## Блок 4. Tools: function tools + built-in tools (15 мин)

### Function tools

ADK сам превращает Python-функцию в tool по её сигнатуре и docstring. **Type hints и docstring обязательны** — это то, что увидит LLM.

```python
import datetime
from zoneinfo import ZoneInfo
from google.adk.agents import Agent


def get_weather(city: str) -> dict:
    """Возвращает текущую погоду в указанном городе.

    Args:
        city: Название города на английском (например, "New York").

    Returns:
        Словарь со статусом и отчётом либо сообщением об ошибке.
    """
    if city.lower() == "new york":
        return {
            "status": "success",
            "report": "В Нью-Йорке солнечно, 25°C.",
        }
    return {
        "status": "error",
        "error_message": f"Нет данных по городу {city}.",
    }


def get_current_time(city: str) -> dict:
    """Возвращает текущее время в указанном городе."""
    if city.lower() == "new york":
        tz = ZoneInfo("America/New_York")
    else:
        return {"status": "error", "error_message": f"Нет таймзоны для {city}."}
    now = datetime.datetime.now(tz)
    return {"status": "success", "report": now.strftime("%Y-%m-%d %H:%M:%S %Z")}


root_agent = Agent(
    name="weather_time_agent",
    model="gemini-2.5-flash",
    description="Агент, отвечающий на вопросы о погоде и времени в городе.",
    instruction="Ты — полезный ассистент. Используй инструменты для ответа.",
    tools=[get_weather, get_current_time],
)
```

### Built-in tools

```python
from google.adk.tools import google_search

root_agent = Agent(
    name="search_agent",
    model="gemini-2.5-flash",
    description="Агент, ищущий ответы в Google.",
    instruction="Ты — эксперт-исследователь. Всегда опирайся на факты.",
    tools=[google_search],
)
```

### Что обсудить

- Возвращайте `dict` со структурой `{"status": "success"|"error", ...}` — это рекомендуемый паттерн ADK.
- Имена параметров, type hints и docstring уходят в LLM как описание tool — пишите их аккуратно и на английском (модель лучше распознаёт).
- В `adk web` → вкладка **Events** видно, какие tools вызывались и с какими аргументами — отлично для отладки.

> **Упражнение (3 мин):** добавьте свой tool `get_exchange_rate(from_currency, to_currency)` (можно с заглушкой) и спросите агента «во сколько долларов 100 евро?».

---

## Блок 5. Memory & Sessions (15 мин)

### Три уровня «памяти» в ADK

| Уровень   | Класс / поле                                  | Что хранит                                                                             |
|-----------|-----------------------------------------------|----------------------------------------------------------------------------------------|
| Session   | `Session` (`InMemorySessionService` и др.)    | История сообщений и событий одного разговора                                           |
| State     | `session.state` (dict-like)                   | Структурированные данные внутри сессии (имя, предпочтения, флаги, временные значения)  |
| Memory    | `MemoryService`                               | Долговременная память между сессиями (профиль пользователя, RAG-индексы и т.п.)        |

### Запуск программно

```python
from google.adk.runners import InMemoryRunner
from google.genai import types

runner = InMemoryRunner(agent=root_agent, app_name="workshop")
session = await runner.session_service.create_session(
    app_name="workshop", user_id="user_1"
)

async for event in runner.run_async(
    user_id="user_1",
    session_id=session.id,
    new_message=types.Content(
        role="user",
        parts=[types.Part(text="Меня зовут Мухаммад. Запомни.")],
    ),
):
    if event.is_final_response() and event.content:
        print(event.content.parts[0].text)
```

При повторном вызове с тем же `session_id` агент помнит контекст:

```python
async for event in runner.run_async(
    user_id="user_1",
    session_id=session.id,
    new_message=types.Content(
        role="user", parts=[types.Part(text="Как меня зовут?")]
    ),
):
    if event.is_final_response() and event.content:
        print(event.content.parts[0].text)
```

### Работа со State из tool

```python
from google.adk.tools.tool_context import ToolContext


def remember_preference(key: str, value: str, tool_context: ToolContext) -> dict:
    """Сохраняет предпочтение пользователя в session state."""
    tool_context.state[key] = value
    return {"status": "success", "saved": {key: value}}


def recall_preference(key: str, tool_context: ToolContext) -> dict:
    """Достаёт сохранённое предпочтение."""
    value = tool_context.state.get(key)
    return {"status": "success", "value": value}
```

### Что обсудить

- `InMemorySessionService` — только для dev. В production используются `DatabaseSessionService`, `VertexAiSessionService`, и т.п.
- `MemoryService` нужен, когда информация должна жить **между** сессиями (пользовательский профиль).
- В `adk web` вкладка **State** показывает текущее состояние сессии в реальном времени.

---

## Блок 6. Streaming (15 мин)

### Зачем streaming

Без streaming пользователь видит ответ только когда модель полностью его сгенерировала. Со streaming — буква за буквой, что даёт привычный «chat»-ощущение и снижает воспринимаемую латентность.

### Три режима в ADK

```python
from google.adk.agents.run_config import RunConfig, StreamingMode
```

| Режим                  | Что значит                                                                  | Когда использовать                                                   |
|------------------------|------------------------------------------------------------------------------|----------------------------------------------------------------------|
| `StreamingMode.NONE`   | Без streaming, ответ возвращается целиком (default)                          | Простые задачи, batch-обработка                                      |
| `StreamingMode.SSE`    | Server-Sent Events — token-by-token односторонний поток от сервера к клиенту | Чат-боты, ассистенты — улучшает UX                                   |
| `StreamingMode.BIDI`   | Bidirectional через Live API — двусторонний канал                            | Голос/видео в реальном времени, прерывания, streaming tools          |

### Минимальный пример SSE

```python
from google.adk.agents.run_config import RunConfig, StreamingMode
from google.adk.runners import InMemoryRunner
from google.genai import types

runner = InMemoryRunner(agent=root_agent, app_name="workshop")
session = await runner.session_service.create_session(
    app_name="workshop", user_id="user_1"
)

run_config = RunConfig(
    streaming_mode=StreamingMode.SSE,
    max_llm_calls=20,   # защита от бесконечного цикла
)

async for event in runner.run_async(
    user_id="user_1",
    session_id=session.id,
    new_message=types.Content(
        role="user",
        parts=[types.Part(text="Объясни рекурсию длинным примером.")],
    ),
    run_config=run_config,
):
    if event.content and event.content.parts:
        for part in event.content.parts:
            if part.text:
                # event.partial=True у промежуточных чанков, False — у финального
                print(part.text, end="", flush=True)
```

### Live API (BIDI) — что важно знать (без глубокого кода)

- Использует другие модели — Gemini Live API (`gemini-2.0-flash-live-001` и аналоги). Список — в Google AI Studio / Vertex AI docs.
- В `adk web` есть **кнопки микрофона и камеры** — попробуйте на любом агенте с Live-моделью: «Какая погода в Нью-Йорке?» голосом.
- Параметры: `response_modalities=["AUDIO", "TEXT"]`, `speech_config=types.SpeechConfig(...)`, `output_audio_transcription=...`.
- Текст-чат с native-audio моделями не работает — только голос.
- Перед запуском `adk web` нужно установить SSL-сертификаты:

  ```bash
  export SSL_CERT_FILE=$(python -m certifi)
  ```

### Что обсудить

- Streaming в коде на агенте не меняется — только `RunConfig`. Это очень удобно: один агент, разные UI.
- `max_llm_calls` — обязательно ставить в production (защита от runaway loop).
- Для собственного web-приложения с BIDI смотрите гид «Gemini Live API Toolkit» (5 частей).

---

## Блок 7. Callbacks: логирование, guardrails, фильтры (20 мин)

Callbacks — это точки расширения, где можно вмешаться в работу агента. **Если callback возвращает значение, оно подменяет результат шага и шаг пропускается.** Возвращаете `None` — выполнение идёт как обычно.

### Шесть типов callbacks

| Callback                  | Когда срабатывает                              | Принимает                                                | Возврат для пропуска шага        |
|---------------------------|------------------------------------------------|----------------------------------------------------------|----------------------------------|
| `before_agent_callback`   | До запуска агента                              | `CallbackContext`                                        | `types.Content`                  |
| `after_agent_callback`    | После завершения агента                        | `CallbackContext`                                        | `types.Content` (заменит вывод)  |
| `before_model_callback`   | До вызова LLM                                  | `CallbackContext`, `LlmRequest`                          | `LlmResponse` (пропуск вызова)   |
| `after_model_callback`    | После ответа LLM                               | `CallbackContext`, `LlmResponse`                         | `LlmResponse` (заменит ответ)    |
| `before_tool_callback`    | До вызова tool                                 | `BaseTool`, `args: dict`, `ToolContext`                  | `dict` (пропуск вызова)          |
| `after_tool_callback`     | После ответа tool                              | `BaseTool`, `args: dict`, `ToolContext`, `tool_response` | `dict` (заменит ответ)           |

### Импорты

```python
from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest, LlmResponse
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext
from google.genai import types
from typing import Optional, Dict, Any
```

### Пример 1. Логирование (`before_agent_callback`)

```python
def log_entry(callback_context: CallbackContext) -> Optional[types.Content]:
    print(
        f"[LOG] enter agent={callback_context.agent_name} "
        f"inv={callback_context.invocation_id}"
    )
    return None  # продолжаем как обычно
```

### Пример 2. Guardrail на вход — блокировка по ключевому слову (`before_model_callback`)

```python
def block_secrets(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    last_user_text = ""
    if llm_request.contents:
        last = llm_request.contents[-1]
        if last.parts:
            last_user_text = (last.parts[0].text or "").lower()

    if "api_key" in last_user_text or "password" in last_user_text:
        return LlmResponse(
            content=types.Content(
                role="model",
                parts=[types.Part(text="Я не обсуждаю секретные данные.")],
            )
        )
    return None  # пропускаем дальше — LLM получит запрос
```

### Пример 3. Подмена аргументов tool (`before_tool_callback`)

```python
def normalize_city(
    tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext
) -> Optional[Dict]:
    if tool.name == "get_weather" and "city" in args:
        args["city"] = args["city"].strip().title()
        print(f"[Callback] normalized city -> {args['city']}")
    return None
```

### Пример 4. Пост-обработка ответа модели (`after_model_callback`)

```python
def append_signature(
    callback_context: CallbackContext, llm_response: LlmResponse
) -> Optional[LlmResponse]:
    if not llm_response.content or not llm_response.content.parts:
        return None
    original = llm_response.content.parts[0].text or ""
    new_text = original + "\n\n— Ответ сгенерирован агентом ADK 🤖"
    return LlmResponse(
        content=types.Content(role="model", parts=[types.Part(text=new_text)])
    )
```

### Привязка к агенту

```python
root_agent = LlmAgent(
    name="guarded_agent",
    model="gemini-2.5-flash",
    instruction="Ты — полезный ассистент.",
    tools=[get_weather],
    before_agent_callback=log_entry,
    before_model_callback=block_secrets,
    before_tool_callback=normalize_city,
    after_model_callback=append_signature,
)
```

### Что обсудить

- **Имена параметров callback-функций должны точно совпадать** с документированными (`callback_context`, `llm_request`, `tool_context` и т.д.) — ADK передаёт их по ключевым словам.
- Callbacks — отличное место для: логирования в Datadog/Sentry, PII-фильтра, кэша на уровне LLM, инжекта метаданных в prompt, добавления безопасности.
- **Не делать тяжёлые I/O синхронно** в callback — он блокирует agent loop.

> **Упражнение (5 мин):** напишите `after_tool_callback`, который маскирует email'ы в ответе tool регуляркой.

---

## Блок 8. Sub-agents и MCP — обзор (10 мин)

### Multi-agent системы

Сложные задачи разбиваем на специализированных агентов:

```python
researcher = LlmAgent(
    name="researcher",
    model="gemini-2.5-flash",
    description="Ищет факты в интернете.",
    instruction="Найди информацию по запросу пользователя.",
    tools=[google_search],
)

writer = LlmAgent(
    name="writer",
    model="gemini-2.5-flash",
    description="Пишет статьи на основе фактов.",
    instruction="Напиши краткую статью на основе предоставленных фактов.",
)

coordinator = LlmAgent(
    name="coordinator",
    model="gemini-2.5-flash",
    instruction=(
        "Ты — координатор. Сначала делегируй researcher для сбора фактов, "
        "затем writer — для написания статьи."
    ),
    sub_agents=[researcher, writer],
)
```

Координатор сам выбирает, какому sub-agent передать ход. Есть также workflow-агенты с детерминированным порядком: `SequentialAgent`, `ParallelAgent`, `LoopAgent`.

### MCP (Model Context Protocol)

MCP — **«USB-C для AI-агентов»**: единый стандарт подключения внешних источников tools и данных. Готовые серверы есть для filesystem, GitHub, Slack, Notion, Postgres и десятков других сервисов.

В ADK подключается через `MCPToolset`:

```python
# Концептуальный пример — точная сигнатура: https://google.github.io/adk-docs/mcp/
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset

# далее MCPToolset собирает tools с указанного MCP-сервера и
# отдаёт их агенту через параметр tools=[...]
```

### Что показать на демо

Подключите filesystem MCP-сервер и попросите агента «прочитай README.md в проекте и расскажи, о чём он». Не написав ни одной функции, мы дали агенту доступ к файлам.

---

## Блок 9. Evaluation: измеряем качество агента (20 мин)

### Зачем

После каждого изменения промпта или модели хочется знать: стало лучше или хуже? ADK даёт три способа оценки:

1. **Web UI** — `adk web` → вкладка Eval (интерактивно).
2. **CLI** — `adk eval <agent_folder> <evalset_file>` (для CI).
3. **Pytest** — `AgentEvaluator.evaluate(...)` (для регрессионных тестов).

### Структура файлов для eval

```
my_first_agent/
├── __init__.py
├── agent.py
├── .env
└── tests/
    ├── test_config.json           # пороги по метрикам
    ├── basic.evalset.json         # тестовые кейсы (multi-turn)
    └── test_agent.py              # pytest-обёртка
```

### `tests/test_config.json` — пороги по метрикам

```json
{
  "criteria": {
    "tool_trajectory_avg_score": 1.0,
    "response_match_score": 0.8
  }
}
```

### `tests/basic.evalset.json` — минимальный пример

```json
{
  "eval_set_id": "basic",
  "name": "Базовый набор",
  "eval_cases": [
    {
      "eval_id": "weather_ny",
      "conversation": [
        {
          "invocation_id": "1",
          "user_content": {
            "parts": [{"text": "Какая погода в Нью-Йорке?"}],
            "role": "user"
          },
          "final_response": {
            "parts": [{"text": "В Нью-Йорке солнечно, 25°C."}],
            "role": "model"
          },
          "intermediate_data": {
            "tool_uses": [
              {"name": "get_weather", "args": {"city": "New York"}}
            ]
          }
        }
      ]
    }
  ]
}
```

> **Подсказка:** простые тесты можно складывать в файлы вида `<name>.test.json` (один кейс на файл). Сложные multi-turn — в `<name>.evalset.json`.

### Запуск из CLI

```bash
adk eval my_first_agent my_first_agent/tests/basic.evalset.json
```

### Запуск через pytest

```python
# tests/test_agent.py
import pathlib
import pytest
from google.adk.evaluation.agent_evaluator import AgentEvaluator


@pytest.mark.asyncio
async def test_basic_evalset():
    await AgentEvaluator.evaluate(
        agent_module="my_first_agent",
        eval_dataset_file_path_or_dir=str(
            pathlib.Path(__file__).parent / "basic.evalset.json"
        ),
    )
```

```bash
pytest -v my_first_agent/tests/test_agent.py
```

### Главные метрики

| Метрика                                  | Что измеряет                                                       | Когда брать                              |
|------------------------------------------|--------------------------------------------------------------------|------------------------------------------|
| `tool_trajectory_avg_score`              | Совпадение последовательности tool-вызовов (EXACT/IN_ORDER/ANY_ORDER) | Регрессии по логике агента            |
| `response_match_score`                   | ROUGE-1 совпадение текста ответа с эталоном                        | Быстрый baseline                         |
| `final_response_match_v2`                | Семантическое сходство ответа с эталоном (LLM-as-Judge)            | Когда формулировка может варьироваться   |
| `rubric_based_final_response_quality_v1` | Качество ответа по вашим рубрикам (LLM-as-Judge)                   | Тон, стиль, helpfulness                  |
| `rubric_based_tool_use_quality_v1`       | Качество использования tools по рубрикам                           | «Сначала geocoding, потом weather»       |
| `hallucinations_v1`                      | Проверка на «галлюцинации» против контекста                        | Grounding / RAG                          |
| `safety_v1`                              | Безопасность ответа (через Vertex AI Eval SDK, нужен GCP)          | User-facing продукты                     |

### Что обсудить

- Начинайте с `tool_trajectory_avg_score` + `response_match_score` — дёшево, быстро, ловит регрессии.
- LLM-as-Judge метрики (`*_v2`, `rubric_*`, `hallucinations_v1`, `safety_v1`) платные (вызывают модель-судью) — гоняйте в CI пореже.
- Для `safety_v1` нужен `GOOGLE_CLOUD_PROJECT` и `GOOGLE_CLOUD_LOCATION` в `.env`.

---

## Блок 10. Deployment: куда деплоить ADK-агентов (10 мин)

Три основных варианта от Google:

| Платформа              | Когда                                                                            | Команда                                   |
|------------------------|----------------------------------------------------------------------------------|-------------------------------------------|
| **Vertex AI Agent Engine** | Production-grade, полностью managed, авто-скейлинг, A2A, sessions/memory из коробки | `adk deploy agent_engine ...`         |
| **Cloud Run**          | Serverless контейнер, простой и дешёвый, своё хранилище сессий                    | `adk deploy cloud_run ...`                |
| **GKE**                | Kubernetes — для тех, кто уже живёт в нём                                         | `adk deploy gke ...`                      |

### Что важно знать заранее

- Локально работающий агент с `InMemorySessionService` в production не годится — выберите `DatabaseSessionService`, `VertexAiSessionService`, Redis-backed или подобный.
- `.env` с `GOOGLE_API_KEY` ≠ production-секреты. Используйте Secret Manager.
- Для Agent Engine есть «Agent Starter Pack» — шаблон с CI/CD, observability, eval.

### Что показать на демо (если есть время)

`adk deploy cloud_run --project <PROJECT> --region us-central1 my_first_agent` — и через 3–5 минут получаем публичный URL с FastAPI-эндпоинтом агента.

---

## Блок 11. Q&A + куда двигаться дальше (10 мин)

### Что осталось за бортом и где почитать

- **Workflow-agents:** `SequentialAgent`, `ParallelAgent`, `LoopAgent` — детерминированные пайплайны без LLM на координации.
- **Custom agents** — наследуемся от `BaseAgent` и пишем свой `_run_async_impl`.
- **A2A protocol** — агенты общаются между собой по стандарту, в том числе кросс-фреймворк.
- **OpenAPI tools** — автогенерация tools из OpenAPI-спеки.
- **LiteLLM / Claude / Ollama** — ADK поддерживает не только Gemini.
- **Context caching / compression** — экономия токенов на длинных сессиях.
- **Plugins** — упаковка ваших MCP/skills/tools для распространения.
- **Observability** — встроенный logging + интеграции (Datadog, OpenTelemetry).

### Полезные ссылки

- Документация ADK: https://google.github.io/adk-docs/
- Quickstart (multi-tool agent): https://google.github.io/adk-docs/get-started/quickstart/
- Streaming dev guide (5 частей): https://google.github.io/adk-docs/streaming/dev-guide/part1/
- Callbacks (типы): https://google.github.io/adk-docs/callbacks/types-of-callbacks/
- Callbacks (паттерны): https://google.github.io/adk-docs/callbacks/design-patterns-and-best-practices/
- Evaluation: https://google.github.io/adk-docs/evaluate/
- Eval criteria: https://google.github.io/adk-docs/evaluate/criteria/
- RunConfig / Streaming modes: https://google.github.io/adk-docs/runtime/runconfig/
- Deployment: https://google.github.io/adk-docs/deploy/
- Примеры на GitHub: https://github.com/google/adk-samples
- Codelab по evaluation: https://codelabs.developers.google.com/adk-eval/instructions
- Gemini API (AI Studio): https://aistudio.google.com/
- Model Context Protocol: https://modelcontextprotocol.io/

---

## Чек-лист подготовки спикера

- [ ] Готовый репозиторий с папкой `my_first_agent/`, заглушкой `.env.example` и checkpoint-ветками по каждому блоку.
- [ ] Резервный Gemini API key на случай, если у участника проблемы с получением своего.
- [ ] Слайд с архитектурой агента (10 компонентов из блока 1).
- [ ] Локально установленный ADK + проверенный `adk run`, `adk web`, `adk eval`.
- [ ] Заранее заготовленный `basic.evalset.json` + `test_config.json` для демо блока 9.
- [ ] (Опционально) GCP-проект с включённым Vertex AI для демо `adk deploy cloud_run`.
- [ ] 2–3 «вау-промта» для агента, чтобы держать внимание зала.

---

## Возможные сокращения для 1.5-часового формата

Если времени всего 1.5 часа:

- Блок 6 (Streaming) — сократить до 5 мин теории, без BIDI.
- Блок 8 (Sub-agents/MCP) — пропустить или дать 3 мин.
- Блок 9 (Evaluation) — показать только концепцию + один CLI-запуск (5 мин).
- Блок 10 (Deployment) — одна слайд-сводка (3 мин).

Получится 1ч 25м: блоки 1–7 + 11 в полном объёме + сокращённые 8–10 как сводка.
