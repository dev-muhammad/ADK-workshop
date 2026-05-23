# Checkpoint 03 · Первый агент: Hello, Agent!

## Что нового в этом шаге

Это **самый первый** агент. Здесь нет ни инструментов, ни памяти — только LLM и инструкция.

Добавили:
- `my_first_agent/__init__.py` — `from . import agent` (обязательно для импорта).
- `my_first_agent/agent.py` — определение `root_agent` через `Agent(...)`.
- `my_first_agent/.env.example` — шаблон для GOOGLE_API_KEY.

## Теория

**Что такое агент в ADK?**
Минимальный агент — это `LlmAgent` (alias `Agent`) с тремя обязательными полями:

- `name` — уникальное имя (используется в логах и multi-agent сценариях).
- `model` — какой LLM вызывать (`gemini-2.5-flash`, `gemini-2.0-flash`, и т.д.).
- `instruction` — системный промпт, задающий роль и стиль ответа.

**Почему нужна именно эта структура папок?**
ADK CLI (`adk run`, `adk web`) ищет:
1. Папку с любым именем (это будет `agent_name` в dev UI).
2. Внутри неё — `__init__.py` с `from . import agent`.
3. И `agent.py` с переменной `root_agent`.

Если хоть одно нарушить — агент не появится в dropdown'е `adk web`.

**`Agent` vs `LlmAgent`** — это один и тот же класс, `Agent` просто короче.

## Структура

```
03_first_agent/
└── my_first_agent/
    ├── __init__.py       ← from . import agent
    ├── agent.py          ← root_agent = Agent(...)
    └── .env.example      ← скопируйте в .env и впишите ключ
```

## Запуск

```bash
# 1. Скопировать .env.example в .env и вписать GOOGLE_API_KEY
cd checkpoints/03_first_agent/my_first_agent
cp .env.example .env
# отредактируйте .env: GOOGLE_API_KEY=ваш_ключ

# 2. Перейти в родительскую папку checkpoint'а (важно!)
cd ..

# 3. Запустить
adk web           # dev UI на http://localhost:8000
# или
adk run my_first_agent   # терминал
```

В dev UI выберите `my_first_agent` в dropdown'е и спросите:
- «Что такое list comprehension?»
- «Объясни *args и **kwargs»

## Что пробовать

- Поменяйте `instruction` — добавьте «отвечай только на английском» и посмотрите, как агент изменит поведение.
- Замените `model="gemini-2.5-flash"` на `"gemini-2.0-flash"` и сравните скорость.
- Спросите агента о погоде — увидите, что без инструментов он отвечает общими словами или признаётся, что не знает.
