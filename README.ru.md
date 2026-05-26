# ADK Workshop · «Build your first AI agent!»

**Languages:** 🇷🇺 Русский (вы здесь) · [🇬🇧 English](README.md)

Материалы воркшопа по Google ADK (Agent Development Kit) на Python — полный цикл разработки агента: от первого `Hello, Agent!` до streaming, callbacks, evaluation и деплоя.

## 📅 Событие

**Workshop: Exploring Google AI Studio & ADK** — организует **GDG Khujand**.

👉 [Регистрация и детали на GDG Community](https://gdg.community.dev/events/details/google-gdg-khujand-presents-workshop-exploring-google-ai-studio-amp-adk/)

## Автор

**Мухаммад Абдугафаров** — AI Product Engineer, Founder of [Lookona Labs](https://lookona.com).

- Сейчас — создаю AI-агентов для бизнеса.
- До этого — 8 лет в разработке ПО.
- На сцене — 3 года выступаю на Tech-митапах и организую их в рамках **GDG Khujand**.

**Связь:**
- Website: [muhammads.site](https://muhammads.site)
- LinkedIn: [muhammad-abdugafarov](https://www.linkedin.com/in/muhammad-abdugafarov/)
- GitHub: [@dev-muhammad](https://github.com/dev-muhammad)
- Telegram: [@muhammad_babolo](https://t.me/muhammad_babolo)
- Instagram: [@muhammad.babolo](https://instagram.com/muhammad.babolo)

## 🎤 Презентация воркшопа

**Google Slides (рекомендуется для просмотра и шеринга):**
👉 [docs.google.com/presentation/d/14VwUGWvSDmtGe7Y-PQBkPfETlWek4qiruJYJARlvvV4](https://docs.google.com/presentation/d/14VwUGWvSDmtGe7Y-PQBkPfETlWek4qiruJYJARlvvV4/edit?usp=sharing)

Английская версия: [docs.google.com/presentation/d/1UivU9RYczYTz6pb1b-q2OAP6EcZUi6Yi2W81f8A1WMw](https://docs.google.com/presentation/d/1UivU9RYczYTz6pb1b-q2OAP6EcZUi6Yi2W81f8A1WMw/edit?usp=sharing)


## Что в папке

| Файл / папка                   | Что это                                                                                  |
|--------------------------------|------------------------------------------------------------------------------------------|
| `workshop_plan.md`             | Подробный план воркшопа на 2 ч 30 мин (11 блоков) — для спикера                          |
| Слайды                         | См. [Google Slides](https://docs.google.com/presentation/d/14VwUGWvSDmtGe7Y-PQBkPfETlWek4qiruJYJARlvvV4/edit?usp=sharing) выше (исходник в pptx не коммитится) |
| `workshop_notebook.ipynb`      | Colab/Jupyter ноутбук со всеми блоками — для самостоятельной работы                      |
| `pyproject.toml`               | Зависимости проекта (для `uv`)                                                            |
| `requirements.txt`             | То же для `pip` (если без `uv`)                                                          |
| `verify_setup.py`              | Скрипт-самопроверка: импортирует все checkpoint'ы и (при наличии ключа) делает один вызов |
| `checkpoints/`                 | 8 готовых ADK-проектов — по одному на блок                                               |

## Checkpoints

В каждой папке — самостоятельный ADK-проект и свой `README.md` с теорией, что нового и как запустить.

| Папка                          | Блок воркшопа              | Что демонстрирует                                                                |
|--------------------------------|----------------------------|----------------------------------------------------------------------------------|
| [`03_first_agent/`](checkpoints/03_first_agent/README.md)               | Блок 3                     | Минимальный агент: LLM + instruction                                             |
| [`04_tools/`](checkpoints/04_tools/README.md)                           | Блок 4                     | Function tools (погода, время) + закомментирован `google_search`                 |
| [`05_memory_sessions/`](checkpoints/05_memory_sessions/README.md)       | Блок 5                     | Session/State через `tool_context.state` + `run_session_demo.py`                 |
| [`06_streaming/`](checkpoints/06_streaming/README.md)                   | Блок 6                     | `RunConfig(streaming_mode=StreamingMode.SSE)` + `streaming_demo.py`              |
| [`07_callbacks/`](checkpoints/07_callbacks/README.md)                   | Блок 7                     | 4 callback'а: логирование, guardrail, нормализация args, подпись                 |
| [`08_sub_agents_mcp/`](checkpoints/08_sub_agents_mcp/README.md)         | Блок 8                     | Multi-agent: coordinator → researcher + writer; пример MCP закомментирован       |
| [`09_evaluation/`](checkpoints/09_evaluation/README.md)                 | Блок 9                     | `tests/` с `test_config.json`, `basic.evalset.json`, `test_agent.py` (pytest)    |
| [`10_final/`](checkpoints/10_final/README.md)                           | Блок 10                    | Финальная версия — всё вместе                                                    |

## Быстрый старт через `uv`

[uv](https://docs.astral.sh/uv/) — быстрый Python package manager, рекомендованный для этого воркшопа.

```bash
# 1. Установить uv (если ещё нет)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Создать venv и установить зависимости
cd ADK-workshop
uv venv --python 3.12
source .venv/bin/activate           # Windows: .venv\Scripts\activate
uv pip install -e .

# 3. (Опционально) с dev и eval инструментами
uv pip install -e ".[dev,eval]"

# 4. API-ключ Gemini (бесплатно): https://aistudio.google.com/apikey
# Способ A — через export в shell (один раз на всю сессию, удобно для воркшопа):
export GOOGLE_GENAI_USE_VERTEXAI=FALSE
export GOOGLE_API_KEY="ваш_ключ_из_aistudio.google.com"
export ADK_MODEL="gemini-3.1-flash-lite"   # опционально, см. ниже
# Способ B — через .env в каждом checkpoint'е (см. ниже)
#
# ВАЖНО: free-ключ имеет жёсткие лимиты (см. раздел «Лимиты free tier» ниже).
# По умолчанию агенты используют gemini-3.1-flash-lite (500 запросов в день
# вместо 20 у gemini-2.5-flash) — менять можно через ADK_MODEL.

# 5. Самопроверка
python verify_setup.py

# 6. Запуск первого агента
cd checkpoints/03_first_agent
cp my_first_agent/.env.example my_first_agent/.env  # вписать ключ
adk web                              # dev UI на http://localhost:8000
```

Альтернатива без uv:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Конфигурация ключа и модели: `export` vs `.env`

Есть **два способа** сказать ADK, какой API-ключ и какую модель использовать. Выбирайте удобный — оба работают, можно смешивать.

### Способ A · `export` в shell (рекомендуется для воркшопа)

Установить переменные **один раз** на всю сессию — и они работают сразу во всех checkpoint'ах. Не нужно копировать `.env.example → .env` в каждой из 8 папок.

```bash
# macOS / Linux (zsh / bash)
export GOOGLE_GENAI_USE_VERTEXAI=FALSE
export GOOGLE_API_KEY="ваш_ключ_из_aistudio.google.com"
export ADK_MODEL="gemini-3.1-flash-lite"      # опционально

# Windows PowerShell
$env:GOOGLE_GENAI_USE_VERTEXAI = "FALSE"
$env:GOOGLE_API_KEY = "ваш_ключ"
$env:ADK_MODEL = "gemini-3.1-flash-lite"

# Windows CMD
set GOOGLE_GENAI_USE_VERTEXAI=FALSE
set GOOGLE_API_KEY=ваш_ключ
set ADK_MODEL=gemini-3.1-flash-lite
```

После этого любой checkpoint работает без `.env`:

```bash
cd checkpoints/03_first_agent
adk web                  # подхватит ключ из shell
```

**Сделать постоянным** (чтобы не вводить каждый раз при открытии терминала):

```bash
# macOS (zsh) — добавить в ~/.zshrc
echo 'export GOOGLE_API_KEY="ваш_ключ"' >> ~/.zshrc
echo 'export ADK_MODEL="gemini-3.1-flash-lite"' >> ~/.zshrc
source ~/.zshrc

# Linux (bash) — в ~/.bashrc
echo 'export GOOGLE_API_KEY="ваш_ключ"' >> ~/.bashrc
echo 'export ADK_MODEL="gemini-3.1-flash-lite"' >> ~/.bashrc
source ~/.bashrc
```

Для пер-проектной конфигурации без правки `~/.zshrc` удобно использовать [direnv](https://direnv.net/):

```bash
# В корне ADK-workshop:
echo 'export GOOGLE_API_KEY="ваш_ключ"' > .envrc
echo 'export ADK_MODEL="gemini-3.1-flash-lite"' >> .envrc
direnv allow
```

### Способ B · `.env` в каждом checkpoint'е

ADK автоматически подгружает `.env` из папки агента при запуске `adk web` / `adk run`. Полезно, если у разных checkpoint'ов должны быть разные настройки.

```bash
cd checkpoints/03_first_agent/my_first_agent
cp .env.example .env
# отредактируйте .env, вставьте GOOGLE_API_KEY и, опционально, ADK_MODEL
```

### Приоритет

Если переменная задана и в shell (через `export`), и в `.env` — **значение из shell `export` обычно побеждает**, так как оно уже в `os.environ` к моменту, когда `load_dotenv` пытается его установить. Если хотите чтобы `.env` всегда перезаписывал shell, используйте `load_dotenv(override=True)` (это уже не дефолт ADK, нужно делать вручную в собственном коде).

### Что выбрать

| Сценарий                                         | Способ                                         |
|--------------------------------------------------|------------------------------------------------|
| Воркшоп, один общий ключ, быстро прогнать все 8 checkpoint'ов | **`export` в shell**                  |
| Разработка нескольких независимых агентов        | `.env` в каждом                                |
| Production / CI                                  | shell env (через secret manager)               |
| Несколько проектов на машине                     | `direnv` + `.envrc`                            |

## Как переключаться между checkpoint'ами

Каждый checkpoint самостоятельный. Чтобы перейти к следующему:

```bash
cd checkpoints/<N>_<name>
cp my_first_agent/.env.example my_first_agent/.env  # вписать ключ
adk web
```

И смотрите соответствующий `README.md` внутри папки — там описано **что нового добавлено**, **теория** и **что попробовать**.

## ⚠️ Лимиты free tier (Google AI Studio)

Free-ключ из AI Studio имеет **жёсткие лимиты по запросам в минуту (RPM), токенам в минуту (TPM) и запросам в день (RPD)**. Для воркшопа это критично — на 20 человек × 20 запросов в день модели легко не хватит. Ниже актуальные лимиты для самых полезных моделей.

### Text-out модели (то, что используется в воркшопе)

| Модель                                  | RPM | TPM     | RPD   | Где применять в воркшопе                                  |
|-----------------------------------------|-----|---------|-------|------------------------------------------------------------|
| `gemini-2.5-flash`                      | 5   | 250 000 | **20**| Default во всех checkpoint'ах. **Скудный дневной лимит!**  |
| `gemini-2.5-flash-lite`                 | 10  | 250 000 | 20    | Быстрее и легче, но тот же RPD                             |
| `gemini-3-flash`                        | 5   | 250 000 | 20    | Альтернатива 2.5 flash                                     |
| `gemini-3.5-flash`                      | 5   | 250 000 | 20    | Альтернатива 2.5 flash                                     |
| `gemini-3.1-flash-lite`                 | 15  | 250 000 | **500** | **Лучший free-вариант** для экспериментов и evaluation   |
| `gemini-2.5-pro` / `gemini-3.1-pro`     | 0   | 0       | 0     | На free tier недоступны — нужен paid plan                  |

### Другие модели

| Модель              | RPM | TPM     | RPD     | Применение                                            |
|---------------------|-----|---------|---------|--------------------------------------------------------|
| `gemma-4-26b`       | 15  | ∞       | 1 500   | Open-weight, без лимита токенов — для batch-экспериментов |
| `gemma-4-31b`       | 15  | ∞       | 1 500   | То же, чуть мощнее                                     |
| `gemini-embedding-1`| 100 | 30 000  | 1 000   | Если делаете RAG поверх агента                         |
| `gemini-2.5-flash-tts` | 3 | 10 000 | 10      | Text-to-speech (для голосовых демо)                    |

### Live API (для блока про BIDI / голос)

| Модель                                | RPM | TPM     | RPD   |
|---------------------------------------|-----|---------|-------|
| `gemini-2.5-flash-native-audio-dialog`| ∞   | 1M      | ∞     |
| `gemini-3-flash-live`                 | ∞   | 65 000  | ∞     |

### Search grounding (для `google_search` tool)

- Gemini 2.x: **1 500 запросов с grounding в день**
- Gemini 3.x: пока 0 (не доступно на free tier)

### Стратегии экономии для воркшопа

**Для спикера на этапе подготовки:**
- Прогоните полный сценарий заранее, чтобы знать примерный расход.
- Заведите несколько API-ключей — AI Studio разрешает создавать их на разные Google-аккаунты.
- Eval с `num_runs > 1` × 2 (default) умножает расход — для воркшопа достаточно `num_runs=1`.

**Для участников:**
1. **Используйте `gemini-3.1-flash-lite` вместо `gemini-2.5-flash`** в большинстве примеров — 500 RPD вместо 20.
   ```python
   root_agent = Agent(model="gemini-3.1-flash-lite", ...)
   ```
2. **Перед запуском evaluation** уменьшите `num_runs` до 1 и используйте только дешёвые метрики (`tool_trajectory_avg_score`, `response_match_score` — без LLM-as-Judge).
3. **Не гоняйте streaming-демо в цикле** — длинные истории быстро съедают TPM.
4. **Избегайте `google_search` в каждом примере** — он считается отдельно.

**Если упёрлись в лимит:**
- Сообщение `429 RESOURCE_EXHAUSTED` — подождите минуту или до следующего дня (по UTC).
- Можно переключиться на **Vertex AI Express Mode** (бесплатный tier, отдельные квоты): `GOOGLE_GENAI_USE_VERTEXAI=TRUE` в `.env`.
- Или на **Gemma** через AI Studio — у неё RPD намного выше (1 500).

> Источник лимитов: ваша персональная страница [aistudio.google.com → API keys → Plan & billing](https://aistudio.google.com/apikey). Лимиты могут меняться — Google периодически обновляет квоты для free tier.

## Запуск тестов (блок 9)

```bash
cd checkpoints/09_evaluation

# Вариант A — через ADK CLI
adk eval my_first_agent my_first_agent/tests/basic.evalset.json

# Вариант B — через pytest
pytest -v my_first_agent/tests/test_agent.py
```

## Запуск ноутбука

```bash
uv pip install jupyter
jupyter notebook workshop_notebook.ipynb
```

Или загрузите `workshop_notebook.ipynb` в [Google Colab](https://colab.research.google.com/).

## Проверка окружения

```bash
python verify_setup.py
```

Скрипт проверит:
1. Все 8 checkpoint'ов корректно импортируются.
2. У каждого правильно установлены tools / callbacks / sub_agents.
3. `InMemoryRunner` создаётся для каждого.
4. (Если есть `GOOGLE_API_KEY` в `.env`) — реальный вызов агента из checkpoint 04 и проверка ответа.

## Рекомендуемый порядок для участников

1. Открыть слайды (Google Slides выше) и `workshop_plan.md` рядом — план содержит больше деталей, чем умещается на слайды.
2. Идти по checkpoint'ам последовательно, читая `README.md` в каждом и запуская через `adk web`.
3. После блока 5 переключиться на `workshop_notebook.ipynb` для streaming/callbacks/eval — там удобнее показывать программный запуск.
4. На блоке 9 запустить `pytest` локально.

## Ссылки

- [Документация ADK](https://google.github.io/adk-docs/)
- [Quickstart](https://google.github.io/adk-docs/get-started/quickstart/)
- [Gemini API (AI Studio)](https://aistudio.google.com/)
- [Примеры на GitHub](https://github.com/google/adk-samples)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [uv documentation](https://docs.astral.sh/uv/)
