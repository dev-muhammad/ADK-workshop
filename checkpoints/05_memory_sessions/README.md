# Checkpoint 05 · Memory & Sessions

## Что нового в этом шаге

Добавили агенту **структурированную память** в рамках сессии и показали, как программно управлять сессией через `InMemoryRunner`.

Изменили:
- `agent.py` — добавлены два tool'а `remember_preference(key, value)` и `recall_preference(key)`, которые работают с `tool_context.state`.
- Новый файл `run_session_demo.py` — демонстрация программного запуска с многошаговым разговором.

## Теория

**Три уровня «памяти» в ADK:**

| Уровень   | Класс / поле                                | Что хранит                                                        |
|-----------|---------------------------------------------|-------------------------------------------------------------------|
| Session   | `Session`, `InMemorySessionService`          | История сообщений и событий одного разговора (автоматически)      |
| State     | `session.state` / `tool_context.state`       | Структурированный dict внутри сессии (имя, предпочтения, флаги)   |
| Memory    | `MemoryService`                              | Долговременная память между сессиями (профиль, RAG-индексы)       |

**Session** — это сам факт «разговор номер X у пользователя Y». ADK сам ведёт историю сообщений.

**State** — это `dict`, который живёт внутри сессии. Можно:
- Читать/писать из tool через `tool_context.state["key"]`.
- Передавать в callback через `callback_context.state`.
- Видеть в реальном времени в `adk web` → вкладка State.

**Memory** — для информации, которая должна пережить сессию (например, «пользователь любит компактные ответы»). В production используются `VertexAiMemoryService`, `DatabaseMemoryService` и т.д.

**Важное правило:** `InMemorySessionService` и `InMemoryRunner` — только для dev. В production выбирайте `DatabaseSessionService` (Postgres/MySQL), `VertexAiSessionService`, или Redis-backed.

## Структура

```
05_memory_sessions/
├── my_first_agent/
│   ├── __init__.py
│   ├── agent.py              ← + remember_preference / recall_preference
│   └── .env.example
└── run_session_demo.py       ← программный запуск через InMemoryRunner
```

## Запуск

**Вариант A — dev UI:**

```bash
cd checkpoints/05_memory_sessions
adk web
```

Сценарий разговора:
1. «Мой любимый город — Tashkent. Запомни.»
2. «Какая там погода?» (должен использовать сохранённый город)
3. «А что я тебе говорил про мои предпочтения?»

В dev UI откройте вкладку **State** — увидите, как растёт `state["favorite_city"]`.

**Вариант B — программный запуск:**

```bash
cd checkpoints/05_memory_sessions
# подготовить .env
cp my_first_agent/.env.example my_first_agent/.env
# вписать GOOGLE_API_KEY

python run_session_demo.py
```

Этот скрипт показывает, как в собственном Python-коде:
- создать `InMemoryRunner`,
- завести сессию,
- слать сообщения через `runner.run_async(...)`,
- получать события и финальные ответы.

## Что пробовать

- В разных сессиях у одного пользователя сохраните разные `favorite_city` — убедитесь, что state не «протекает».
- Добавьте tool `clear_all_preferences(tool_context)` и попросите агента забыть всё.
- В `run_session_demo.py` сохраните `session.id` в файл и при следующем запуске продолжите разговор — но помните: `InMemorySessionService` живёт только в памяти процесса, для persistence нужен другой `SessionService`.
