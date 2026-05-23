# Checkpoint 09 · Evaluation — измеряем качество агента

## Что нового в этом шаге

Добавили **папку `tests/`** с полным набором файлов для запуска evaluation: `test_config.json`, `basic.evalset.json`, pytest-обёртка. Это позволяет автоматически прогонять regression-тесты при каждом изменении промпта или модели.

Изменили:
- `agent.py` — финальная версия weather+time agent'а.
- Новые: `tests/test_config.json`, `tests/basic.evalset.json`, `tests/test_agent.py`.

## Теория

**Зачем нужен evaluation?**
После каждого изменения (новая модель, новый промпт, новый tool) хочется автоматически знать: стало лучше или хуже? Без eval'а — будете гонять ручные «smoke»-тесты, медленно и непоследовательно.

**Три способа запустить eval в ADK:**

| Способ        | Когда                              | Команда                                          |
|---------------|------------------------------------|--------------------------------------------------|
| **Dev UI**    | Интерактивная отладка              | `adk web` → вкладка Eval                          |
| **CLI**       | Для CI/CD пайплайнов               | `adk eval <agent_folder> <evalset_file>`         |
| **pytest**    | Регрессионные тесты в test-suite   | `AgentEvaluator.evaluate(...)`                   |

**Структура файлов:**

- `test_config.json` — пороги по метрикам. Если score < threshold — тест падает.
- `<name>.evalset.json` — eval-кейсы в новой schema (multi-turn разговоры).
- `<name>.test.json` — простые одноходовые тесты в старой schema.

**Семь главных метрик:**

| Метрика                                  | Что измеряет                                                    | Стоимость               |
|------------------------------------------|------------------------------------------------------------------|-------------------------|
| `tool_trajectory_avg_score`              | Совпадение последовательности tool-вызовов                       | Бесплатно (string match)|
| `response_match_score`                   | ROUGE-1 сходство текста с эталоном                               | Бесплатно               |
| `final_response_match_v2`                | Семантическое сходство (LLM-as-Judge)                            | Платно (вызов модели)   |
| `rubric_based_final_response_quality_v1` | Качество ответа по вашим рубрикам                                | Платно                  |
| `rubric_based_tool_use_quality_v1`       | Качество использования tools по рубрикам                         | Платно                  |
| `hallucinations_v1`                      | Проверка на галлюцинации против контекста                        | Платно                  |
| `safety_v1`                              | Безопасность ответа (через Vertex AI Eval SDK, нужен GCP)        | Платно                  |

**Стратегия:** в CI на каждый PR — только дешёвые метрики (`tool_trajectory_avg_score` + `response_match_score`). Дорогие LLM-as-Judge — гоняйте по nightly cron'у или вручную перед релизом.

**`tool_trajectory_avg_score` match types:**
- `EXACT` (default) — точное совпадение последовательности.
- `IN_ORDER` — ключевые tools в нужном порядке, между ними допустимы лишние.
- `ANY_ORDER` — нужные tools должны быть, порядок не важен.

## Структура

```
09_evaluation/
└── my_first_agent/
    ├── __init__.py
    ├── agent.py
    ├── .env.example
    └── tests/
        ├── __init__.py
        ├── test_config.json        ← пороги
        ├── basic.evalset.json      ← тестовые кейсы
        └── test_agent.py           ← pytest-обёртка
```

## Запуск

```bash
cd checkpoints/09_evaluation

# Подготовить .env
cp my_first_agent/.env.example my_first_agent/.env
# вписать GOOGLE_API_KEY

# Вариант A — через ADK CLI
adk eval my_first_agent my_first_agent/tests/basic.evalset.json

# Вариант B — через pytest
pytest -v my_first_agent/tests/test_agent.py
```

При успехе — увидите `PASSED` и метрики. При падении — таблицу с expected vs actual для каждого invocation'а.

## Что пробовать

- Добавьте кейс в `basic.evalset.json`: «Какая погода в Tashkent?» с ожидаемым tool call `get_weather("Tashkent")`.
- Уберите `get_weather` из tools и прогоните тесты — увидите, что `tool_trajectory_avg_score` упадёт.
- Включите `final_response_match_v2` в `test_config.json`, добавив порог `0.8` — увидите дополнительный платный прогон через LLM-as-Judge.
- Подключите тесты к CI: `pytest` в GitHub Actions с GOOGLE_API_KEY из secrets.
