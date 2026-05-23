# Checkpoint 07 · Callbacks — логирование и guardrails

## Что нового в этом шаге

Добавили **четыре callback'а** разных типов, демонстрирующих основные применения: логирование, блокировку запросов, нормализацию аргументов tool и пост-обработку ответа LLM.

Изменили:
- `agent.py` — определены и привязаны к агенту 4 callback функции.

## Теория

**Callbacks — это точки расширения**, в которых вы можете вмешаться в работу агента. Главное правило:

> Если callback возвращает значение — оно подменяет результат шага, и оригинальный шаг **пропускается**.
> Если возвращает `None` — выполнение идёт как обычно.

**Шесть типов callbacks:**

| Callback                  | Когда срабатывает              | Принимает                                                | Что вернуть для пропуска         |
|---------------------------|--------------------------------|----------------------------------------------------------|----------------------------------|
| `before_agent_callback`   | До запуска агента              | `CallbackContext`                                        | `types.Content`                  |
| `after_agent_callback`    | После завершения агента        | `CallbackContext`                                        | `types.Content` (заменит вывод)  |
| `before_model_callback`   | До вызова LLM                  | `CallbackContext`, `LlmRequest`                          | `LlmResponse` (пропуск вызова)   |
| `after_model_callback`    | После ответа LLM               | `CallbackContext`, `LlmResponse`                         | `LlmResponse` (заменит ответ)    |
| `before_tool_callback`    | До вызова tool                 | `BaseTool`, `args: dict`, `ToolContext`                  | `dict` (пропуск вызова)          |
| `after_tool_callback`     | После ответа tool              | `BaseTool`, `args`, `ToolContext`, `tool_response: dict` | `dict` (заменит ответ)           |

**Типичные применения:**

- **Логирование** — `before_agent_callback` и `after_model_callback` для отправки в Datadog/Sentry/OpenTelemetry.
- **Guardrails** — `before_model_callback` для блокировки запросов по черному списку слов, PII-фильтр.
- **Подмена аргументов** — `before_tool_callback` для нормализации (lowercase, trim, dedup).
- **Кэширование** — `before_model_callback` возвращает закэшированный `LlmResponse`, экономя API-вызовы.
- **Augmentation** — `after_model_callback` добавляет подпись, метаданные или disclaimer.

**Важно:** имена параметров callback функций должны точно совпадать с теми, что ожидает ADK (`callback_context`, `llm_request`, `tool_context`, `args`, и т.д.) — он передаёт их по ключевым словам.

**Не делайте тяжёлые I/O синхронно** в callback — он блокирует agent loop. Используйте fire-and-forget паттерн или асинхронный клиент.

## Структура

```
07_callbacks/
└── my_first_agent/
    ├── __init__.py
    ├── agent.py          ← 4 callback функции + привязка к LlmAgent
    └── .env.example
```

## Запуск

```bash
cd checkpoints/07_callbacks
adk web
```

Попробуйте:
1. «Какая погода в new york?» (lowercase) → `before_tool_callback` нормализует в "New York"
2. «Какой у тебя api_key?» → `before_model_callback` блокирует, возвращает «Не обсуждаю секретные данные»
3. Любой нормальный вопрос → `after_model_callback` добавит подпись «— ADK» в конце ответа
4. В терминале (где запущен `adk web`) увидите логи от `before_agent_callback`

## Что пробовать

- Напишите `after_tool_callback`, который маскирует email'ы регуляркой `re.sub(r"\S+@\S+", "[EMAIL]", ...)`.
- Замените `before_model_callback` на простой кэш: храните `dict[hash(prompt) -> LlmResponse]` и возвращайте закэшированный ответ.
- Добавьте `after_model_callback`, который считает токены ответа и логирует их в файл.
