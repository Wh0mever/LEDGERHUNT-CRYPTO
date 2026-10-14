# AREA agent-orchestration: AI-agent orchestration framework and the mechanism for connecting external tools

============================================================
PART 1 - VERIFIER REPORT (takes precedence over the researcher wherever they disagree)
============================================================

## VERIFIER SUMMARY
Аудит в целом добросовестный: из 31 перепроверенного утверждения 20 подтверждены первичными источниками, 8 исправлены, 3 остались непроверяемыми; опровергнутых целиком нет. Лицензии рекомендованных вариантов (DBOS Transact - MIT,
Pydantic AI - MIT) подтверждены текстами LICENSE, версии и даты релизов совпали, цены Claude, Temporal Cloud и DBOS Conductor совпали, спецификация MCP 2026-07-28 и факты о TronGrid MCP, MistTrackMCP, Blockscout MCP, Restate
подтверждены. Компрометацию LiteLLM удалось подтвердить первичным источником (issue #24518 в самом репозитории), а зависимость httpx2 оказалась пакетом pydantic/httpx2 (BSD-3-Clause, с мая 2026). Исправления: у Pydantic AI 16
advisories, а не 14; у LangGraph 5 high, а не 4; актуальный Temporal Server - v1.32.1, а не v1.31.4; PostgresSaver LangGraph пишет только изменившиеся каналы, а не всё состояние; в экосистеме LangChain есть лимиты числа вызовов
модели и инструментов; self-hosted Conductor бесплатен для разработки и платен для production; оценка стоимости верна арифметически, но опирается на допущение без tool-loop. Главное, что исследователь пропустил, - свойства DBOS,
прочитанные мной в официальных docs: шаг не может ставить workflow в очередь (это ломает предложенную схему «agent.run() с инструментами в одном шаге + очереди с лимитами») и recovery работает только при совпадении версии
приложения, которая по умолчанию равна hash кода. Оба дефекта устранимы проектным решением, поэтому обе рекомендации остаются в силе, но (a) - условно: LLM-решения следует делать без инструментов, версию приложения задавать явно,
pickle заменить, а до фиксации выбора провести spike и сравнить DBOS с более простым вариантом без durable-движка (frontier-таблицы + мемоизирующий шлюз + pgqueuer/Procrastinate), который в аудите не рассматривался. Рекомендация
(b) (in-process function tools, MCP только на границе) устояла без существенных оговорок. Не проверено мной: реальная работа и производительность (код не запускался), число инструментов и условия TronScan MCP (403), наличие
официальных MCP у Arkham/Chainalysis/TRM/Elliptic, хранилища чекпоинтов Microsoft Agent Framework (пакет postgres в репозитории оказался pgvector-хранилищем, не чекпоинтером), детали Etherscan MCP (405).

## BLOCKING RISKS
- Архитектурное противоречие в рекомендации (a): по docs DBOS из шага нельзя вызывать, стартовать или ставить в очередь workflow. Если agent.run() с инструментами завернуть в один @DBOS.step, вызовы инструментов обходят очереди с
limiter (риск 429 и нарушения условий провайдеров), а сбой посреди шага повторно оплачивает все LLM-запросы шага. Нужно решить до написания кода: LLM-решения без инструментов либо шаг на каждый запрос к модели.
- Recovery DBOS зависит от application version (по умолчанию hash исходников workflow): после деплоя незавершённые многочасовые расследования автоматически не восстановятся. Без явной версии, DBOS.patch() и процедуры деплоя
требование «checkpoint и resume для многочасовых прогонов» на практике не выполняется.
- Цели по времени (30 с / 2 мин / 1 000 адресов за 5 мин) не подтверждены ни одним измерением: polling очередей DBOS 1.0 с по умолчанию, limiter считает старты workflow, а не HTTP-запросы; в 3.0.0 чинили регрессию limiter. TronScan
без API-ключа вернул 429 с блокировкой на 50 с на единственный запрос - без ключей провайдеров цели недостижимы.
- Бюджет $1: оценка построена на 25 одиночных запросах. С tool-loop (2-4 запроса на решение) и токенизатором Claude 4.7+ (~+30% токенов) Sonnet 5.5 на всех шагах даёт $1.1-2.2. cost_limit Pydantic AI срабатывает после превышения и
не работает для моделей без цен. Нужны дешёвая модель по умолчанию и собственный ledger до первого платного вызова.
- Скорость изменений и цепочка поставок LLM-слоя: Pydantic AI - 55 minor-релизов за 15.4 недели, 16 advisories (в аудите 14), порог для V3 уже пройден; на пути всех LLM-ключей появилась транзитивная зависимость httpx2 (первый релиз
2026-05-11). Нужны pin точных версий с хэшами и адаптер-изолятор.
- Зависимость от небольшого вендора: у DBOS один автор дал 394 коммита (следующий 77), мажор 3.0.0 со сменой схемы вышел 2026-09-16, admin server удалён; UI есть только в проприетарном Conductor (self-host в production - платный
ключ, облачный вариант означает передачу метаданных расследований вендору).
- Pickle по умолчанию в системной БД DBOS: изменение классов между деплоями ломает десериализацию чекпоинтов, а право записи в БД равно исполнению кода при recovery. Для доказательной платформы нужен portable JSON или только
примитивы и ID.
- Windows 11 как dev-машина: CI DBOS и основная матрица Pydantic AI работают только на ubuntu-latest. Не блокирует при разработке в Docker/WSL2, но нативный запуск на Windows не доказан.

## VERIFIER VERDICTS ON RECOMMENDATIONS

### NEED: (a) Оркестрация AI-агентов
PRIMARY: Собственный детерминированный оркестратор на DBOS Transact + Pydantic AI для LLM-шагов; единый Postgres; MCP вне ядра
STANDS: True
ISSUE: Выбор проходит ограничения MVP (MIT у обеих библиотек подтверждён текстом LICENSE, один Postgres, без отдельного сервера, активная поддержка), но в предложенной архитектуре есть три дефекта, не замеченные исследователем. (1)
Внутреннее противоречие: рекомендовано «LLM-шаг = один @DBOS.step, внутри agent.run() с инструментами» и одновременно «очереди DBOS по провайдерам с limiter». Docs DBOS: «You cannot call, start, or enqueue workflows from within
steps» - HTTP-вызовы инструментов из шага пойдут мимо очередей и их лимитов, а сбой посреди шага повторно оплатит все LLM-запросы этого шага (at-least-once на уровне всего agent.run). (2) Recovery DBOS привязан к application
version (по умолчанию hash кода workflow): после любого деплоя незавершённые расследования автоматически не продолжатся. (3) Оценка бюджета исходит из 25 одиночных запросов; с tool-loop и новым токенизатором (+~30% токенов) Sonnet
5.5 на всех шагах даёт больше $1. Кроме того: polling очередей 1.0 с и накладные расходы чекпоинтов не измерены против целей 30 с / 5 мин; CI обеих библиотек - только Ubuntu; у DBOS не оценена альтернатива «вообще без durable-
движка».
SUGGESTED CHANGE: Оставить связку, но зафиксировать до начала разработки: 1) LLM-решения по умолчанию БЕЗ инструментов - детерминированный код заранее собирает данные через очереди, LLM получает типизированный Input и возвращает Output; один запрос
к модели = один @DBOS.step (тогда оценка 25 вызовов и $1 остаётся честной). Инструменты оставить только OSINT-агенту и вести их через тот же HTTP-шлюз с собственным in-process token bucket. 2) Задать application_version явно,
включить enable_patching и описать процедуру деплоя при незавершённых прогонах. 3) Заменить pickle на portable JSON либо передавать только ID и примитивы. 4) Жёсткий бюджет - только собственный ledger; cost_limit Pydantic AI
считать вторым контуром. 5) Модель по умолчанию - класса Haiku 5.5, Sonnet 5.5 только на эскалациях. 6) Обязательный spike (2-3 дня) в Docker/WSL2: kill -9 посреди прогона, деплой новой версии посреди прогона, 1 000 адресов с
реальным ключом TronGrid, polling_interval_sec. 7) В spike сравнить с вариантом без DBOS: таблица frontier + мемоизирующий HTTP/LLM-шлюз (он и так нужен для доказательств и replay) + pgqueuer или Procrastinate; если разница в
надёжности не видна, взять более простой вариант и убрать зависимость от вендора с bus factor 1.

### NEED: (b) Механизм подключения внешних инструментов
PRIMARY: In-process типизированные function tools через собственный реестр и единый HTTP-шлюз; MCP - только опциональный адаптер на границе и будущий внешний интерфейс
STANDS: True
ISSUE: Рекомендация устояла: первичные факты подтверждены (TronGrid MCP - 149 инструментов с broadcast и без опубликованных условий; MistTrackMCP без лицензии и тестов; Blockscout MCP запрещает SaaS-использование; спецификация MCP
2026-07-28 ломающая; 9 high-advisories у python-sdk). Замечания: (1) аргумент «149 описаний несовместимы с бюджетом $1» преувеличен - список инструментов фильтруется (FilteredToolset, tool search); решающие причины - контроль
сырого ответа, write-поверхность, закрытый код. (2) Не согласованы два механизма лимитов: limiter очередей DBOS и вызовы из инструментов агента - нужен единый лимитер в шлюзе. (3) В шлюзе предложен httpx, а Pydantic AI уже перешёл
на httpx2 (пакету 5 месяцев) - в процессе окажутся два HTTP-стека. (4) Пропущены готовые средства для опционального MCP-шлюза и сканирования. (5) TronScan без ключа отвечает 429 даже на одиночный запрос - ключи обязательны с
первого дня. (6) Число инструментов и условия TronScan MCP, отсутствие официальных MCP у Arkham/Chainalysis остались неподтверждёнными.
SUGGESTED CHANGE: Оставить как есть, добавив: единый token-bucket на провайдера внутри HTTP-шлюза, которым пользуются и очереди, и инструменты; для тестового record/replay взять vcrpy или pytest-recording вместо самописного слоя (доказательное
хранилище сырых ответов остаётся своим); если MCP-шлюз когда-либо включается - snyk/agent-scan для проверки описаний и pinning, agentgateway или docker/mcp-gateway как прокси с allowlist; зафиксировать один HTTP-клиент для
собственного кода и закрепить версии httpx2/anthropic/openai lock-файлом с хэшами.

## VERIFIER FACT CHECKS

- [CONFIRMED] DBOS Transact (Python) :: Лицензия MIT, коммерческое использование без условий
  CORRECT VALUE: MIT. Файл LICENSE: «MIT License, Copyright (c) 2024 DBOS, Inc.»; pyproject.toml: license = {text = "MIT"}; PyPI: license MIT. Ограничения касаются только отдельного продукта Conductor.
  METHOD: gh api contents/LICENSE и contents/pyproject.toml (текст прочитан), PyPI JSON API
  EVIDENCE: https://github.com/dbos-inc/dbos-transact-py/blob/main/LICENSE

- [CONFIRMED] DBOS Transact (Python) :: v3.2.0 (2026-09-29), мажор 3.0.0 от 2026-09-16, 1 626 звёзд, 6 open issues, kraftp 394 коммита (следующий 77), CI unit-test/chaos-test/publish; 3.0.0 удалил admin server, in-memory queues, in-memory scheduler, устаревшие
интеграции
  CORRECT VALUE: Всё совпало. Дополнение: release notes 3.0.0 также содержат смену схемы системной БД (вынос inputs/outputs в отдельные таблицы), «Remove Deprecated App DB», «Remove Legacy Partition Queue Interface» и «Fix Limiter Regression» (PR
#829, merged 2026-08-26) - т.е. limiter, на котором строится rate limiting, недавно ломался. На PyPI уже есть preview 3.3.0a9 (2026-10-13).
  METHOD: gh api releases, releases/tags/3.0.0, contributors, contents/.github/workflows; PyPI JSON API
  EVIDENCE: https://github.com/dbos-inc/dbos-transact-py/releases/tag/3.0.0

- [CONFIRMED] DBOS Transact (Python) :: Очереди в Postgres: global_concurrency, worker_concurrency, limiter={limit, period}, partition_limiter, priority, deduplication_id, delay_seconds; deduplication не поддерживается на partitioned queues
  CORRECT VALUE: Подтверждено docs и кодом. Не упомянуто исследователем: (1) DEFAULT_QUEUE_POLLING_INTERVAL_SEC = 1.0 (dbos/_queue.py, настраивается polling_interval_sec) - до 1 с задержки на каждый dequeue; (2) limiter ограничивает число СТАРТОВ
workflow из очереди за период (глобально по всем процессам), а не число HTTP-запросов: для точного лимита один HTTP-запрос должен быть одним queued workflow.
  METHOD: WebFetch docs + чтение dbos/_queue.py через gh api
  EVIDENCE: https://docs.dbos.dev/python/tutorials/queue-tutorial

- [CORRECTED] DBOS Transact (Python) :: Recovery с последнего завершённого шага; после завершения шаги не переисполняются
  CORRECT VALUE: Верно, но с существенным условием, которого нет в аудите: «When DBOS tries to recover workflows, it only recovers workflows whose version matches the current application version», а версия по умолчанию - hash исходного кода
workflow. После деплоя нового кода незавершённые многочасовые расследования автоматически НЕ восстанавливаются; нужны явный application_version + DBOS.patch() (enable_patching), blue-green либо ручной resume/fork. Кроме того: «You
cannot call, start, or enqueue workflows from within steps».
  METHOD: WebFetch docs (upgrading-workflows, workflow-tutorial, step-tutorial)
  EVIDENCE: https://docs.dbos.dev/python/tutorials/upgrading-workflows

- [CONFIRMED] DBOS Transact (Python) :: Чекпоинты по умолчанию сериализуются pickle
  CORRECT VALUE: DefaultSerializer: pickle.dumps + base64, имя формата «py_pickle». Есть альтернативный DBOSPortableJSONSerializer («portable_json») и возможность задать собственный serializer в конфигурации.
  METHOD: Чтение dbos/_serialization.py через gh api
  EVIDENCE: https://github.com/dbos-inc/dbos-transact-py/blob/main/dbos/_serialization.py

- [CORRECTED] DBOS Conductor :: Pro $99/мес (2 seats, 3 apps, 1M checkpoints, $50 за 1M сверх), Teams $499/мес (10 seats, 10 apps, 10M, $40 за 1M); self-host Conductor только в Enterprise
  CORRECT VALUE: Цены Pro/Teams подтверждены. Про self-host - неточно: по Conductor License (обновлена в декабре 2025) self-hosted Conductor разрешён БЕЗ лицензионного ключа в Test/Development Mode (бесплатно, только внутренние тест/разработка), а
Commercial/Production Use (включая обработку клиентских данных) требует платного ключа по Order Form; на pricing-странице опция self-host указана в Enterprise.
  METHOD: WebFetch https://www.dbos.dev/dbos-pricing и https://dbos.dev/conductor-license
  EVIDENCE: https://dbos.dev/conductor-license

- [UNVERIFIABLE] DBOS Transact (Python) :: Работает на Windows (заявление pricing-страницы); совместимость с dev-машиной Windows 11
  CORRECT VALUE: FAQ pricing-страницы действительно говорит «any Linux, MacOS, or Windows platform», но CI unit-test.yml запускается только на ubuntu-latest (Python 3.10-3.14 x SQLITE/POSTGRES); Windows в матрице нет. У Pydantic AI основная
матрица тестов тоже ubuntu-latest, classifiers пакета не содержат Windows. Работа на Windows 11 не доказана - разрабатывать в Docker/WSL2.
  METHOD: Чтение unit-test.yml (DBOS) и ci.yml (Pydantic AI) через gh api; код не запускался
  EVIDENCE: https://github.com/dbos-inc/dbos-transact-py/blob/main/.github/workflows/unit-test.yml

- [CONFIRMED] Pydantic AI :: MIT; v2.55.0 (2026-10-09); pydantic-ai-slim requires-python >=3.11; v2.0.0 2026-06-23; v1.0.0 2025-09-04; ветка v1 патчится (v1.107.7 от 2026-09-30); extras dbos>=2.10.0 без верхней границы, mcp = fastmcp-slim[client]>=3.3.0,<5,
зависимость httpx2>=2.7
  CORRECT VALUE: Всё совпало (v1.0.0 опубликован 2025-09-05T00:15Z UTC - расхождение в часовом поясе). Снятие пункта not_verified: httpx2 - это pydantic/httpx2 (BSD-3-Clause, автор Tom Christie, первый релиз на PyPI 2026-05-11, 2.13.1 от
2026-09-23, 1 550 звёзд) - HTTP-клиент возрастом 5 месяцев на пути всех LLM-ключей.
  METHOD: gh api LICENSE, releases, pyproject.toml; PyPI JSON API для httpx2; gh api repos/pydantic/httpx2
  EVIDENCE: https://github.com/pydantic/pydantic-ai/blob/main/pydantic_ai_slim/pyproject.toml

- [CONFIRMED] Pydantic AI :: UsageLimits: request_limit (default 50), tool_calls_limit, input/output/total_tokens_limit, per_request_input_tokens_limit, cost_limit в USD (Decimal); cost_limit - best-effort
  CORRECT VALUE: Поля подтверждены чтением usage.py. Уточнение: проверка стоимости - «cost > cost_limit», т.е. срабатывает ПОСЛЕ превышения; при usage.cost is None выдаётся только CostNotFoundWarning («cannot be enforced because no cost was
calculated»). Жёстким бюджетом служить не может - нужен собственный ledger.
  METHOD: Чтение usage.py (класс UsageLimits, check_before_request, check_cost) через gh api
  EVIDENCE: https://github.com/pydantic/pydantic-ai/blob/main/pydantic_ai_slim/pydantic_ai/usage.py

- [CORRECTED] Pydantic AI :: 14 опубликованных security advisories
  CORRECT VALUE: 16 опубликованных advisories (4 high, 9 medium, 3 low). Самый свежий high - GHSA-6fqq-452j-qhrp / CVE-2026-107286 от 2026-10-02 («Concurrency-limited model streams can retain slots») затрагивает ядро, а не опциональный web UI. Два
OTel-advisory о неполной редакции (GHSA-4x9p-g9wm-8q7f, GHSA-3gh4-cghq-f8v4) подтверждены.
  METHOD: gh api repos/pydantic/pydantic-ai/security-advisories (подсчёт записей)
  EVIDENCE: https://github.com/pydantic/pydantic-ai/security/advisories

- [CONFIRMED] Pydantic AI (интеграция DBOS) :: DBOSAgent deprecated и будет удалён в v3; DBOSDurability импортирует приватные dbos._error и dbos._context; требуется вызывать agent.run() внутри своего @DBOS.workflow
  CORRECT VALUE: Подтверждено кодом и docs. Дополнения: (1) custom function tools «are not automatically wrapped by DBOS» - их надо самим помечать @DBOS.step; (2) код интеграции явно учитывает поведение dbos 3.2 (DBOSWorkflowConflictIDError) -
совместимость с DBOS 3.x целевая, пункт not_verified частично снят; (3) docs советуют держать вход/выход шага ~до 2 MB.
  METHOD: Чтение _durability.py, _agent.py, __init__.py через gh api; WebFetch docs durable_execution/dbos
  EVIDENCE: https://github.com/pydantic/pydantic-ai/blob/main/pydantic_ai_slim/pydantic_ai/durable_exec/dbos/_durability.py

- [CONFIRMED] Pydantic AI :: Version policy: нет намеренных breaking changes в minor; beta-модули исключены; следующий мажор не раньше 3 месяцев после V2.0; security-фиксы V1 минимум 6 месяцев; 55 minor-релизов за ~16 недель
  CORRECT VALUE: Цитаты совпали. v2.0.0 (2026-06-23) -> v2.55.0 (2026-10-09) = 15.4 недели, ~3.6 minor-релиза в неделю. Трёхмесячный порог для V3 уже пройден (2026-09-23) - V3 с удалением DBOSAgent и legacy retry-хелперов может выйти в любой
момент.
  METHOD: WebFetch version-policy; gh api releases/tags/v2.0.0 и releases
  EVIDENCE: https://pydantic.dev/docs/ai/project/version-policy/

- [CORRECTED] LangGraph :: 11 опубликованных advisories, из них 4 high
  CORRECT VALUE: 11 advisories, из них 5 high: GHSA-fvww-7h3r-vfhp (2026-08-28), GHSA-4hm6-w6qq-w73v (2026-09-28, JS), CVE-2025-67644, CVE-2025-64439, CVE-2025-64104. Четыре десериализационных (CVE-2025-64439, CVE-2026-27794, CVE-2026-28277,
CVE-2026-48775) подтверждены. Версия 1.2.15 (2026-10-12), MIT, 43 212 звёзд, 1.0.0 от 2025-10-17 - подтверждено.
  METHOD: gh api security-advisories, releases, releases/tags/1.0.0
  EVIDENCE: https://github.com/langchain-ai/langgraph/security/advisories

- [CORRECTED] LangGraph :: Чекпоинт сериализует всё состояние на каждом superstep
  CORRECT VALUE: Для PostgresSaver неверно: значения каналов пишутся в checkpoint_blobs по ключу (thread_id, checkpoint_ns, channel, version) с ON CONFLICT DO NOTHING, т.е. записываются только каналы с новой версией. Но изменившийся канал пишется
целиком, поэтому накапливающийся список переводов всё равно переписывается - вывод «тяжёлые данные в свои таблицы» остаётся верным, аргумент против LangGraph слабее заявленного.
  METHOD: Чтение base.py (UPSERT_CHECKPOINT_BLOBS_SQL) через gh api
  EVIDENCE: https://github.com/langchain-ai/langgraph/blob/main/libs/checkpoint-postgres/langgraph/checkpoint/postgres/base.py

- [CORRECTED] LangGraph :: Бюджетных примитивов (токены/доллары/счётчики запросов) нет
  CORRECT VALUE: В ядре langgraph (types.py) их действительно нет. Но в той же экосистеме LangChain v1 есть ModelCallLimitMiddleware (thread_limit/run_limit) и ToolCallLimitMiddleware - лимиты числа вызовов модели и инструментов; лимитов в токенах
и USD нет. Счётчики запросов частично покрыты.
  METHOD: gh api: листинг agents/middleware, чтение model_call_limit.py и __init__.py; grep types.py
  EVIDENCE: https://github.com/langchain-ai/langchain/blob/master/libs/langchain_v1/langchain/agents/middleware/model_call_limit.py

- [CORRECTED] Temporal :: Server v1.31.4 (2026-10-12); sdk-python 1.34.0 (2026-09-30); MIT; Temporal Cloud от $50 за 1M actions (до $25), storage $0.042/GBh active и $0.00105/GBh retained, $150 кредитов на 90 дней, Business support от $500/мес
  CORRECT VALUE: Актуальная версия сервера - v1.32.1 (2026-10-08, releases/latest); v1.31.4 и v1.30.8 от 2026-10-12 - патчи старых веток. Остальное (MIT, sdk-python 1.34.0, все цены Cloud) подтверждено.
  METHOD: gh api releases и releases/latest; WebFetch https://temporal.io/pricing
  EVIDENCE: https://github.com/temporalio/temporal/releases/latest

- [CONFIRMED] Claude Agent SDK :: Python-обёртка MIT, TypeScript-пакет проприетарный («All rights reserved», Commercial Terms), встроенный Claude Code CLI; max_budget_usd, max_turns, can_use_tool, hooks, permission_mode, resume, mcp_servers, fallback_model в
ClaudeAgentOptions; v0.2.165 (2026-10-08)
  CORRECT VALUE: Подтверждено. LICENSE.md TS-репозитория: «© Anthropic PBC. All rights reserved. Use is subject to Anthropic's Commercial Terms of Service». README Python-SDK: CLI «automatically bundled», а раздел «License and terms»
распространяет Commercial Terms и на использование Python-SDK в продуктах для клиентов.
  METHOD: gh api LICENSE.md (TS), LICENSE и README.md (Python), чтение types.py
  EVIDENCE: https://github.com/anthropics/claude-agent-sdk-typescript/blob/main/LICENSE.md

- [CONFIRMED] Claude API (цены для оценки бюджета) :: Sonnet 5.5 $2/$10 за MTok; Haiku 5.5 $0.10/$0.50 при промпте до 100k (свыше $0.50/$2.50); Opus 5.5 $4/$20
  CORRECT VALUE: Цены совпали. Не учтено в оценке: по той же странице модели Claude 4.7 и новее используют токенизатор, дающий примерно на 30% больше токенов на тот же текст; cache hits для Sonnet/Opus 5.5 - 0.05x базовой цены.
  METHOD: WebFetch официальной pricing-страницы, чтение таблицы
  EVIDENCE: https://platform.claude.com/docs/en/about-claude/pricing

- [CORRECTED] Оценка стоимости LLM на расследование :: 25 решающих вызовов x (6k in + 1k out): Sonnet 5.5 около $0.55, Haiku 5.5 около $0.03
  CORRECT VALUE: Арифметика верна (150k x $2 + 25k x $10 = $0.55; 150k x $0.10 + 25k x $0.50 = $0.03). Но допущение «1 решение = 1 запрос к модели» несовместимо с рекомендованной схемой «agent.run() с инструментами»: tool-loop даёт 2-4 запроса на
решение с повторной отправкой контекста, плюс ~30% токенов от нового токенизатора. На одном Sonnet 5.5 это $1.1-2.2 - выше лимита $1; на Haiku 5.5 остаётся ниже $0.15. Бюджет выполняется только при дешёвой модели по умолчанию.
  METHOD: Пересчёт по подтверждённым ценам; допущения исследователя не измерялись
  EVIDENCE: https://platform.claude.com/docs/en/about-claude/pricing

- [CONFIRMED] OpenAI Agents SDK :: v0.23.1 (2026-10-02), MIT, 30 015 звёзд, 8 open issues; встроенного лимита токенов/долларов нет, только max_turns
  CORRECT VALUE: Подтверждено: в src/agents/run_config.py из run-level лимитов только max_turns (DEFAULT_MAX_TURNS = 10); прочие «limits» относятся к sandbox. Опубликованных advisories 0.
  METHOD: gh api metadata, releases, security-advisories; чтение run_config.py
  EVIDENCE: https://github.com/openai/openai-agents-python/blob/main/src/agents/run_config.py

- [CONFIRMED] Model Context Protocol (спецификация) :: Текущая ревизия 2026-07-28; убраны сессии и Mcp-Session-Id, handshake initialize, ping, logging/setLevel, resumability SSE; Tasks вынесены в расширение; Sampling/Roots/Logging, DCR, HTTP+SSE - deprecated; iss по RFC 9207; «MCP
itself cannot enforce these security principles at the protocol level»
  CORRECT VALUE: Все пункты подтверждены changelog (SEP-2567, SEP-2575, SEP-2663, SEP-2577, SEP-2596, SEP-2468, PR #2858). Дополнительно: введён обязательный server/discover, паттерн MRTR, обязательные ttlMs/cacheScope у list-результатов, политика
минимум 12 месяцев deprecation.
  METHOD: WebFetch specification/latest и changelog
  EVIDENCE: https://modelcontextprotocol.io/specification/2026-07-28/changelog

- [CONFIRMED] MCP python-sdk :: v2.3.0 (2026-10-02), v2.0.0 2026-07-28, MIT; 12 advisories, 9 high, 9 опубликованы в 2026
  CORRECT VALUE: Совпало: 12 advisories, 9 high, 9 с датой публикации в 2026 году (5 из них - за 2026-09-28..2026-10-05). LICENSE python-sdk - чистый MIT (Anthropic, 2024). Ветка v1 ещё выпускается (v1.30.0 от 2026-09-07).
  METHOD: gh api security-advisories, releases, contents/LICENSE
  EVIDENCE: https://github.com/modelcontextprotocol/python-sdk/security/advisories

- [CONFIRMED] TronGrid MCP Server :: https://mcp.trongrid.io/mcp, Streamable HTTP, протокол 2025-11-25, 149 инструментов (18+73+25+33), есть broadcast/deploy/freeze/proposal-инструменты, лимиты и условия использования не опубликованы, для Claude Desktop рекомендуют
mcp-remote
  CORRECT VALUE: Всё подтверждено docs; сервер stateful с handshake initialize (т.е. на устаревшей модели относительно 2026-07-28). Live keyless GET -> HTTP 405. Уточнение к аргументу про бюджет: 149 описаний в контексте - не неизбежность
(Pydantic AI имеет FilteredToolset и tool search), главные причины отказа - write-поверхность, закрытый код, отсутствие условий и контроля над сырым ответом.
  METHOD: WebFetch docs; curl GET https://mcp.trongrid.io/mcp (405); листинг toolsets Pydantic AI
  EVIDENCE: https://developers.tron.network/docs/mcp

- [UNVERIFIABLE] TronScan MCP Server :: 119 инструментов, протокол 2025-06-18, read-only, лимиты и условия не подтверждены
  CORRECT VALUE: mcpdoc.tronscan.org вернул HTTP 403 и мне. Подтверждено только: TRON Developer Hub (updatedAt 2026-08-18) называет «100+ endpoints», read-only; live GET https://mcp.tronscan.org/mcp -> 405. Число 119 и версия протокола остаются
неподтверждёнными.
  METHOD: WebFetch (403 на mcpdoc.tronscan.org), WebFetch Developer Hub, curl GET (405)
  EVIDENCE: https://developers.tron.network/docs/mcp-servers-on-tron

- [CONFIRMED] slowmist/MistTrackMCP :: Нет файла LICENSE (GitHub: NONE), 4 коммита одного автора (2025-05-07..2026-04-28), 39 звёзд, нет тестов/CI, api_key как URL-параметр, 20 KB summaryPrompts.ts и каталог prompts/
  CORRECT VALUE: Подтверждено: license NONE, 4 коммита (Aroundight), дерево без tests и .github, src/tools/summaryPrompts.ts 20 036 байт, 14 файлов в src/prompts, в misttrackClient.ts api_key входит в MistTrackRequestParams (URL-параметры),
rate_limit по умолчанию 1.0 rps. Замечание: ключ в query string - особенность самого MistTrack OpenAPI, а не только этой обёртки.
  METHOD: gh api metadata, commits, git/trees, чтение misttrackClient.ts
  EVIDENCE: https://github.com/slowmist/MistTrackMCP/blob/main/src/utils/misttrackClient.ts

- [CONFIRMED] blockscout/mcp-server :: LicenseRef-Blockscout v1.0 (с 2026-05-15) запрещает коммерческое и SaaS-использование без Commercial Licence (раздел 4.a)
  CORRECT VALUE: Подтверждено текстом: раздел 4.a «Restricted Commercial or Monetised Use (including SaaS and RaaS)»; сама лицензия «temporary… revocable», Derivative Works - только для внутреннего использования. v0.19.0 (последний push
2026-09-08), 46 звёзд.
  METHOD: gh api contents/LICENSE (прочитаны разделы 1, 2, 4, 5)
  EVIDENCE: https://github.com/blockscout/mcp-server/blob/main/LICENSE

- [CONFIRMED] Restate :: Server под Business Source License 1.1 с Additional Use Grant: запрещён только «Public Restate Platform Service»; sdk-python MIT, 82 звезды, v1.0.5; server v1.7.13 (2026-10-01), 1.8.0-rc.3
  CORRECT VALUE: Подтверждено дословно; лицензия явно разрешает «any type of production deployment… invoking services or workflows written by the Licensee» и платформы с собственным API поверх Restate. Change Date - 4 года после релиза, Change
License - Apache-2.0. Для LEDGERHUNT юридически допустимо.
  METHOD: gh api contents/LICENSE, releases, metadata
  EVIDENCE: https://github.com/restatedev/restate/blob/main/LICENSE

- [CONFIRMED] LiteLLM :: 24 марта 2026 версии 1.82.7 и 1.82.8 на PyPI скомпрометированы (credential stealer, .pth); подтверждено только вторичными источниками
  CORRECT VALUE: Теперь подтверждено первичным источником: в самом репозитории BerriAI/litellm issue #24518 «[Security]: litellm PyPI package (v1.82.7 + v1.82.8) compromised — full timeline and status» (2026-03-24), #24512 и #24521 про malicious
litellm_init.pth, #28025 (2026-05-15) - переход на keyless OIDC release pipeline. Дополнительно у прокси 17+ advisories за 2026, включая 4 critical.
  METHOD: gh api search/issues по репозиторию, security-advisories
  EVIDENCE: https://github.com/BerriAI/litellm/issues/24518

- [CONFIRMED] Live-пробы источников данных :: Keyless GET TronGrid trc20 -> 200 за 0.49 с, 7 957 байт; keyless GET TronScan -> 429 «allowed_rps(3)… suspended for 57 s»
  CORRECT VALUE: Повтор 2026-10-14: TronGrid -> HTTP 200, 0.51 с, 7 957 байт. TronScan -> HTTP 429 на ЕДИНСТВЕННЫЙ запрос: «request rate exceeded the allowed_rps(3), and the query server is suspended for 50 s» (IP общий с другими аудиторами).
Вывод жёстче, чем у исследователя: без API-ключа TronScan непригоден даже для одиночных запросов.
  METHOD: curl keyless GET: 1 запрос к api.trongrid.io, 1 к apilist.tronscanapi.com, по 1 GET к mcp.trongrid.io, mcp.tronscan.org, mcp.bitquery.io (301), tron-mcp-server.bankofai.io (405)
  EVIDENCE: https://api.trongrid.io/v1/accounts/TKHuVq1oKVruCGLvqVexFs6dawKv6fQgFs/transactions/trc20?limit=20&contract_address=TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t

- [UNVERIFIABLE] MCP-серверы Arkham / Chainalysis / TRM / Elliptic :: Официальных MCP-серверов этих вендоров не найдено
  CORRECT VALUE: Мой поиск тоже не нашёл официальных серверов (только community-обёртки и «ChainAnalyzer», не имеющий отношения к Chainalysis), но отсутствие не доказано. При этом исследователь пропустил существующий официальный Etherscan MCP
(docs.etherscan.io/mcp; подробности не прочитаны - страница вернула 405, сведения только из поискового сниппета).
  METHOD: WebSearch (2 запроса); WebFetch docs.etherscan.io/mcp -> 405
  EVIDENCE: https://docs.etherscan.io/mcp

- [CONFIRMED] Microsoft AutoGen / CrewAI / Inngest / Mastra (причины отклонения) :: AutoGen в Maintenance Mode; CrewAI шлёт OTLP-телеметрию на CREWAI_TELEMETRY_BASE_URL; Inngest server под SSPL + Apache 2.0 Future License; Mastra - Apache-2.0 + отдельная лицензия ee/
  CORRECT VALUE: Все четыре подтверждены первичным текстом: README AutoGen («now in maintenance mode… community managed»), telemetry.py CrewAI (endpoint {CREWAI_TELEMETRY_BASE_URL}/v1/traces, расширенные данные за share_crew), LICENSE.md Inngest и
Mastra. Мелкие расхождения метаданных: vercel/ai - 1 393 open issues (в аудите 1 610).
  METHOD: gh api README, telemetry.py, LICENSE.md, metadata
  EVIDENCE: https://github.com/microsoft/autogen/blob/main/README.md

## CANDIDATES MISSED BY THE RESEARCHER (found by verifier)

- Собственный оркестратор без durable-движка: таблицы frontier/jobs в Postgres + мемоизирующий I/O-шлюз + pgqueuer или Procrastinate (https://github.com/janbjorge/pgqueuer)
  WHY: Задание прямо допускало «justified custom controlled orchestrator», но исследователь оценил только вариант поверх DBOS. Content-addressed хранилище сырых HTTP- и LLM-ответов, которое он сам требует для доказательств и replay, уже
даёт идемпотентность: после сбоя детерминированный пайплайн перезапускается и получает cache hit на всё выполненное. Это снимает риски DBOS (version-gated recovery, pickle, bus factor, мажор 3.0).
  ASSESSMENT: pgqueuer: MIT, 1 537 звёзд, push 2026-10-12. Procrastinate: MIT, 1 419 звёзд, с 2019 года, push 2026-10-12. Оба - очереди на Postgres без отдельного сервера. Минус: паузы HITL/бюджета, таймеры и лимиты по провайдерам пишутся
самостоятельно. Проверены только metadata; нужен сравнительный spike с DBOS.

- Absurd (earendil-works/absurd) (https://github.com/earendil-works/absurd)
  WHY: Новичок 2025 года: durable execution только на Postgres, прямая альтернатива DBOS.
  ASSESSMENT: Apache-2.0, 2 488 звёзд, создан 2025-10-20, последний push 2026-08-10, описание «An experiment in durability». Экспериментальный статус и пауза в коммитах - для production-ядра рано; полезен как референс минимальной реализации.

- dbosify-py (DBOS) (https://github.com/dbos-inc/dbosify-py)
  WHY: «Postgres-Backed Drop-in Temporal Replacement» (2026) - влияет на оценку replaceability и lock-in между DBOS и Temporal.
  ASSESSMENT: MIT, 209 звёзд, создан 2026-06-09, push 2026-06-24 (три месяца без коммитов). Показывает, что код в стиле Temporal SDK можно исполнять на Postgres; как основа не годится, но снижает риск выбора API-стиля.

- Kitaru (ZenML) (https://github.com/zenml-io/kitaru)
  WHY: Новый (2026) durable-слой для Python-агентов; у Pydantic AI есть официальная страница интеграции docs/durable_execution/kitaru.md (там же airflow.md и restate.md, которых нет в аудите).
  ASSESSMENT: Apache-2.0, 308 звёзд, создан 2026-03-05, активен (push 2026-10-12). Слишком молодой и малый; глубоко не проверялся.

- Conductor OSS + Agentspan (Orkes) (https://github.com/conductor-oss/conductor)
  WHY: Зрелый durable workflow-движок, с 2026 года позиционируется как «agentic workflow engine»; Agentspan влит в Conductor.
  ASSESSMENT: Apache-2.0, 32 295 звёзд; agentspan-ai/agentspan - MIT, 496 звёзд, «now part of Orkes Conductor». Отдельный сервер на JVM - тяжело для одного скромного сервера; отклонить по тем же причинам, что Temporal.

- BAML / Instructor / Mirascope - тонкие библиотеки типизированных LLM-вызовов (https://github.com/BoundaryML/baml)
  WHY: Если LLM-шаги - это функции decide(Input) -> Output без tool-loop, полноценный агентный фреймворк с 55 minor-релизами за 15 недель не обязателен.
  ASSESSMENT: BAML: Apache-2.0, 9 401 звезда. Instructor (567-labs/instructor): MIT, 14 007 звёзд. Mirascope: MIT, 1 531 звезда. Меньше поверхность и churn, но нет встроенных UsageLimits, TestModel и evals - их пришлось бы писать. Разумный
запасной вариант для LLM-слоя; docs не читались.

- any-llm (Mozilla AI) (https://github.com/mozilla-ai/any-llm)
  WHY: Альтернатива LiteLLM для модель-агностичности без прокси с историей компрометации.
  ASSESSMENT: Apache-2.0, 2 217 звёзд, создан 2025-07-14, активен. Нужен только при отказе от нативных провайдеров Pydantic AI.

- Inspect AI + vcrpy для evals и replay (https://github.com/UKGovernmentBEIS/inspect_ai)
  WHY: Требования «50 сценариев с ground truth» и «replay с записанными fixtures» закрываются готовыми инструментами; исследователь назвал только pydantic_evals и самописный слой.
  ASSESSMENT: Inspect AI: MIT, 2 995 звёзд, активен. vcrpy: MIT, 3 021 звезда, с 2012 года, активен. Оба совместимы с выбранным стеком; vcrpy покрывает только тестовый replay, а не доказательное хранилище.

- Средства безопасности MCP: snyk/agent-scan (бывший invariantlabs-ai/mcp-scan), agentgateway, docker/mcp-gateway, IBM/mcp-context-forge (https://github.com/snyk/agent-scan)
  WHY: Исследователь предлагает «периодическое сканирование на tool poisoning» и собственный MCP-шлюз с allowlist/pinning, но не аудировал готовые решения.
  ASSESSMENT: agent-scan: Apache-2.0, 3 137 звёзд (репозиторий mcp-scan редиректит на snyk/agent-scan). agentgateway: Apache-2.0, 5 313. docker/mcp-gateway: MIT, 1 599. mcp-context-forge: Apache-2.0, 4 622 (965 open issues). Для MVP не нужны
(MCP выключен); брать при появлении MCP-границы. Проверены только metadata.

- Официальный Etherscan MCP (https://docs.etherscan.io/mcp)
  WHY: Для расширения на Ethereum/BSC; исследователь оставил его в not_verified и не внёс в кандидаты.
  ASSESSMENT: По поисковому сниппету: hosted Streamable HTTP, API-ключ как bearer, 60+ сетей, инструмент меток адресов только на платном плане. Страница вернула 405 на автоматическое чтение - не подтверждено первичным источником. Для MVP на
TRON не нужен.

- Прочие блокчейн-MCP: BofAI hosted read-only TRON MCP, AnChainAI/aml-mcp, tatumio/blockchain-mcp, alchemy-mcp-server, GoPlusSecurity/goplus-mcp (https://developers.tron.network/docs/mcp-servers-on-tron)
  WHY: Закрывают пробел аудита (поиск GoPlus/Nansen/Chainbase не выполнялся из-за лимита Search API).
  ASSESSMENT: BofAI держит hosted read-only endpoint tron-mcp-server.bankofai.io/mcp (live GET 405); TRON Developer Hub перечисляет ещё SUN, JustLend и WBTC MCP. AnChainAI/aml-mcp: AGPL-3.0, 3 звезды, заброшен с 2025-09. tatumio/blockchain-mcp:
MIT, 15 звёзд. alchemy-mcp-server: MIT, 88 звёзд. goplus-mcp: Apache-2.0, 7 звёзд, без коммитов с 2025-05. Ни один не меняет вывод «REST напрямую».

- Dapr Agents (https://github.com/dapr/dapr-agents)
  WHY: Durable-агенты поверх Dapr Workflows (CNCF); упомянут исследователем только как интеграция OpenAI Agents SDK.
  ASSESSMENT: Apache-2.0, 761 звезда, активен. Требует sidecar Dapr и state store - лишняя инфраструктура для одного сервера; отклонить.

============================================================
PART 2 - RESEARCHER AUDIT
============================================================

## RESEARCHER RECOMMENDATIONS

### R1. NEED: (a) Оркестрация AI-агентов
PRIMARY: Собственный управляемый детерминированный оркестратор на DBOS Transact (durable workflows, очереди, HITL) + Pydantic AI для LLM-шагов в точках принятия решений; единый Postgres; MCP вне ядра.
RATIONALE: Требования LEDGERHUNT (детерминированный поток, LLM только в точках решений, 100% фактов с TXID, бюджет $1, работа в пределах rate limit источников, один скромный сервер) описывают не «автономных агентов», а durable-пайплайн с
несколькими узкими LLM-вызовами. Ни один агентный фреймворк не даёт одновременно бюджетных пауз, очередей с лимитами по источникам и доказательного журнала - это всё равно пишется самостоятельно; вопрос только в том, на чём
стоять. DBOS даёт недостающую инфраструктуру библиотекой внутри процесса на уже нужном Postgres: чекпоинт каждого шага, recovery, очереди с limiter и concurrency (подтверждено docs), durable send/recv для approval и паузы по
бюджету, fork/rewind для replay. Pydantic AI закрывает LLM-слой: нативные провайдеры без LiteLLM, структурированные выходы, UsageLimits включая cost_limit в USD (подтверждено кодом), approval инструментов, TestModel/FunctionModel
и pydantic_evals для 50 сценариев. Обе библиотеки MIT. Агентные «роли» из ТЗ (blockchain-data, tracing, address-intelligence, exchange-attribution, risk, graph-intelligence, OSINT, recovery, evidence-verification) реализуются как
типизированные функции decide(Input) -> Output с собственным узким набором инструментов; оркестратор-«агент» - это детерминированный workflow-код, а evidence-verification - вообще не LLM, а детерминированная проверка.
ARCHITECTURE NOTES: ФРЕЙМВОРК (не пишем сами). DBOS Transact: durable workflow расследования, чекпоинт шагов в Postgres, recovery; очереди по провайдерам с limiter и worker_concurrency (например, отдельные очереди trongrid, tronscan, llm); durable
sleep при 429; SetWorkflowTimeout; send/recv для approval и решения по бюджету; cancel/resume/fork/rewind; list_workflow_steps. Pydantic AI: абстракция моделей и fallback, генерация JSON-схем инструментов, валидация
структурированного выхода с ретраями, UsageLimits (request_limit, tool_calls_limit, токены, cost_limit) как второй контур защиты, requires_approval для чувствительных инструментов, TestModel/FunctionModel, OTel-спаны,
pydantic_evals. СВОЙ КОД (клей, оркестрация, верификация). 1) Определения workflow: intake -> fetch -> детерминированный baseline-трассировщик (BFS с лимитами глубины и числа адресов) -> атрибуция -> точки решения LLM ->
детерминированная верификация фактов по TXID -> отчёт и черновики запросов. 2) Бюджетный ledger в Postgres (токены, USD, счётчики запросов по провайдерам): проверка перед каждым платным шагом, при превышении - событие
PAUSED_BUDGET, ожидание DBOS.recv с таймаутом, затем продолжение или финализация частичного отчёта. 3) LLM-шаг = один @DBOS.step, внутри agent.run() с узким набором read-only инструментов; выход - pydantic-модель «предложение»,
которое принимает или отклоняет детерминированный код. 4) Параллельные ветки: дочерние workflow на адрес фронтира, постановка в очереди провайдеров, дедупликация по ключу адрес+токен+страница. 5) HITL: любые внешние действия
(отправка запросов биржам, Tether, правоохранителям) только как черновики с явным approval; платные вызовы выше порога - через approval. 6) Append-only audit log с hash-цепочкой: каждый вызов инструмента и LLM (модель и версия,
параметры, хэш промпта, usage, ссылка на сырой ответ). 7) Scrubber секретов для логов, трасс и отчётов. 8) Правило размера: шаги возвращают ID строк, а не полезную нагрузку. 9) Eval-harness на 50 сценариев. Опционально: экспорт
OTel в self-hosted UI трассировки.
COST: Лицензии: $0 (DBOS Transact MIT, Pydantic AI MIT). Инфраструктура: дополнительной нет - используется тот же Postgres. Опционально DBOS Conductor Pro $99/мес (не требуется для MVP). LLM-токены на стандартное расследование
(допущение, не измерение: 25 решающих вызовов по ~6k входных и ~1k выходных токенов): на Claude Sonnet 5.5 ($2/$10 за MTok, цены прочитаны 2026-10-14) около $0.30 + $0.25 = $0.55; на Claude Haiku 5.5 ($0.10/$0.50 при промпте до
100k) около $0.03; при маршрутизации «дешёвая модель по умолчанию, сильная на спорных шагах» ожидаемо $0.05-0.30, что оставляет запас под платные API в пределах $1. Трудозатраты (оценка): каркас оркестратора, бюджетный ledger,
audit log и адаптер durable - порядка 2-3 человеко-недель.
DATA QUALITY VERIFICATION: 1) Spike на 2-3 дня до фиксации выбора: убить воркер посреди прогона и убедиться, что resume не повторяет оплаченные вызовы; проверить limiter очереди против реального 429; измерить накладные расходы чекпоинта на 1-3 тыс. шагов
(цель 1 000 адресов за 5 минут). 2) Replay-режим: все HTTP- и LLM-ответы пишутся в content-addressed хранилище; прогон в режиме cache-only должен давать побитово тот же граф и отчёт. 3) 50 сценариев с ground truth через
pydantic_evals или pytest: метрики baseline против AI-слоя на одних и тех же fixtures. 4) Тест полноты аудита: число записей tool_calls в журнале равно числу запросов, зафиксированных HTTP-шлюзом. 5) Набор тестов на prompt
injection (вредоносные имена токенов, memo, теги адресов, OSINT-страницы): агент не должен менять план или метки. 6) Тест бюджета: превышение лимита переводит прогон в PAUSED_BUDGET с сохранением результатов и возобновляется после
повышения лимита. 7) Тест утечек: grep по логам, трассам и отчётам на шаблоны ключей.
RISKS: Обе библиотеки быстро меняются (DBOS 3.0 от 2026-09-16; Pydantic AI 2.0 от 2026-06-23 и 55 minor-релизов после) - нужен pin версий и изолирующие адаптеры. DBOS - небольшой вендор с концентрированным bus factor. Интеграция
DBOSDurability в Pydantic AI опирается на приватные модули dbos - рекомендуется её не использовать, а оборачивать весь вызов агента в один @DBOS.step. cost_limit в Pydantic AI - best-effort, поэтому жёсткий бюджет ведётся в
собственном ledger по зафиксированной таблице цен. Чекпоинты DBOS сериализуются pickle - в шагах передавать только ID и примитивы. Рекомендация основана на docs и чтении кода, без запуска.
REPLACEABILITY: Durable-слой изолируется модулем-адаптером (декораторы workflow/step, очереди, send/recv): переход на Temporal или Restate не затрагивает код шагов. LLM-слой изолируется интерфейсом decide(Input) -> Output: замена Pydantic AI на
OpenAI Agents SDK или прямые SDK провайдеров локальна. Baseline-трассировщик не зависит ни от одной из библиотек.
REJECTED ALTERNATIVES:
  - LangGraph: Сильнейшая альтернатива «всё в одном» (MIT, 1.x с 2025-10-17), но: нет бюджетных примитивов и rate limit по источникам (types.py), чекпоинт всего состояния на каждом superstep плохо ложится на граф в 1 000 адресов,
  - при resume узел исполняется с начала, 4 advisories по десериализации чекпоинтов за год, зависимость от langchain-core и крен трассировки в платный LangSmith. Оставить как запасной вариант, если команда уже владеет LangGraph.
  - Temporal: Эталон durable execution, но production self-host - это отдельный кластер сервисов + БД (+ Elasticsearch в дефолтном compose); dev-сервер не для production. Избыточен для одного сервера и маленькой команды; оставлен
  - как путь миграции (модель workflow/activity совпадает).
  - Claude Agent SDK: Запускает проприетарный бинарь Claude Code, control flow задаёт модель, только Claude; не удовлетворяет требованиям детерминизма и model-agnostic.
  - OpenAI Agents SDK: Нет лимитов токенов и долларов (только max_turns), версии 0.x, не-OpenAI модели через LiteLLM/Any-LLM; durable всё равно через внешний движок.
  - Google ADK: Мажор 2.0 через год после запуска, resume с at-least-once инструментами и без поддержки в Web UI/CLI, крен в Gemini/GCP.
  - Microsoft Agent Framework / AutoGen / AG2: MAF: durable-чекпоинты для Python только в Azure Cosmos DB, pickle. AutoGen в maintenance mode. AG2 - диалоговая недетерминированная модель.
  - CrewAI: Ролевая LLM-делегация вместо детерминизма; телеметрия включена по умолчанию (подтверждено кодом).
  - LlamaIndex Workflows / Mastra / Vercel AI SDK / smolagents: LlamaIndex Workflows переориентирован на document-centric агентов и сам опирается на DBOS; Mastra и Vercel AI SDK - только TypeScript; smolagents исполняет
  - сгенерированный код и не имеет durable state.
  - Restate / Hatchet / Inngest: Restate - BSL-сервер и незрелый Python SDK (82 звезды); Hatchet - отдельный control plane; Inngest - SSPL-сервер, Python SDK 0.x, AgentKit в застое с апреля 2026.

### R2. NEED: (b) Механизм подключения внешних инструментов
PRIMARY: In-process типизированные function tools через собственный реестр инструментов и единый HTTP-шлюз; MCP - только как опциональный адаптер на границе (allowlist, pinning, read-only) и как будущий внешний интерфейс платформы.
RATIONALE: Доказательная платформа должна владеть HTTP-слоем: хранить сырой ответ первичного источника для каждого факта, управлять ключами, лимитами и повторами, воспроизводить прогон из fixtures. MCP-сервер между агентом и API отнимает
этот контроль и ничего не добавляет: официальные TRON-серверы - тонкие обёртки над теми же REST API (TronGrid MCP: 149 инструментов, включая broadcast; TronScan MCP: 100+ инструментов), а их списки инструментов в контексте LLM
несовместимы с бюджетом $1. Аудит сторонних серверов показал низкое качество и риски: MistTrackMCP - 4 коммита, без тестов и файла лицензии, ключ в URL, инструкции для модели в выдаче; BofAI - сторонний RPC-прокси по умолчанию и
кошелёк; Bitquery MCP - закрытый, интерактивный OAuth; Blockscout MCP - с 2026-05-15 запрещает коммерческое использование без отдельной лицензии; официальных серверов Arkham/Chainalysis не найдено. Сам протокол в июле 2026 пережил
ломающую переделку (stateless, без сессий и handshake), у python-sdk 9 advisories за 2026 год, а tool poisoning и injection через результаты признаны нерешёнными на уровне протокола. Live-проба подтвердила, что прямой REST прост и
быстр (TronGrid: 200 за 0.49 с) и что лимиты надо держать самим (TronScan: 429 при 3 rps без ключа).
ARCHITECTURE NOTES: ФРЕЙМВОРК: Pydantic AI - регистрация function tools и генерация схем, toolsets (filtered, approval_required), валидация аргументов; httpx - HTTP; очереди DBOS - лимиты по провайдерам; при необходимости официальный mcp SDK v2 -
клиент и сервер. СВОЙ КОД: 1) Реестр инструментов: для каждого - pydantic-модели входа и выхода и политика (side_effect none/read/write, класс стоимости, провайдер и очередь, requires_approval, разрешённые роли агентов). 2) HTTP-
шлюз: подстановка ключей из секрет-хранилища в заголовки в последний момент, редакция в логах, retry/backoff, запись сырого ответа в хранилище доказательств, режимы live / record / replay. 3) Выход для LLM: компактные
типизированные сводки со ссылками raw_ref, source, fetched_at; свободный текст из внешних источников помечается как недоверенный и обрезается. 4) Все инструменты агентов - read-only; действий с подписью и трансляцией транзакций в
системе нет вообще. 5) MCP-шлюз (выключен по умолчанию): allowlist серверов, pinning описаний, только read-only, никакой автозагрузки новых инструментов, никогда не использовать mcp-remote. 6) Будущий собственный MCP-сервер
платформы для клиентов: read-only инструменты расследования, OAuth 2.1 с проверкой audience, на ревизии 2026-07-28.
COST: $0 лицензий. Разработка: 10-15 типизированных клиентов эндпоинтов на MVP + HTTP-шлюз + реестр инструментов - оценочно 1.5-2.5 человеко-недели. Экономия токенов: агент получает 3-8 узких инструментов вместо 100-149 описаний MCP-
сервера (оценка порядка 10-30 тыс. входных токенов на вызов модели, не измерялась).
DATA QUALITY VERIFICATION: Контрактные тесты каждого клиента на записанных fixtures и периодический live-smoke с проверкой схемы ответа. Перекрёстная сверка TronGrid и TronScan по выборке TXID (сумма, отправитель, получатель, блок, время). Каждая запись
сырого ответа: sha256, URL без секретов, статус, fetched_at, источник; верификатор отклоняет любой факт отчёта без ссылки на такую запись. Если MCP-сервер всё же разрешается: фиксируется список инструментов и sha256 их описаний и
схем на момент ревью, при расхождении сервер отключается; разрешены только read-only инструменты; результаты проходят тот же санитайзер и хранилище доказательств; периодическое сканирование на tool poisoning.
RISKS: Поддержка клиентов при изменении API провайдеров ложится на команду (смягчается контрактными тестами). Пользовательские поля из блокчейна и эксплореров (имена токенов, memo, публичные теги) и OSINT-страницы остаются каналом prompt
injection и при прямых вызовах - нужны типизация, ограничение длины, пометка недоверенных полей и запрет на изменение плана по содержимому результатов. Некоторые API требуют ключ в URL (MistTrack) - нужна специальная редакция в
шлюзе.
REPLACEABILITY: Полная: реестр инструментов не зависит от транспорта. Любой инструмент можно выставить наружу через MCP (официальный mcp SDK v2 или FastMCP) или заменить провайдера за адаптером без изменений в агентах и оркестраторе.
REJECTED ALTERNATIVES:
  - MCP как основной транспорт инструментов: Дрейф спецификации (ревизии 2025-11-25 и 2026-07-28 за 8 месяцев, вторая ломающая), наследуемое доверие к серверу без pinning, раздувание контекста, канал prompt injection; уместен
  - только на границе.
  - TronGrid MCP / TronScan MCP (официальные hosted): Закрытый код, изменяемые списки из 100-149 инструментов, у TronGrid - write-операции, отсутствуют опубликованные лимиты и условия; данные те же, что в REST. TronScan MCP
  - допустим только как инструмент ручного исследования в dev.
  - slowmist/MistTrackMCP: Нет LICENSE, тестов и CI; 4 коммита; API-ключ в query string; встроенные инструкции для модели в результатах.
  - Bitquery MCP / Dune MCP: Bitquery: только интерактивный OAuth и закрытый код, сервису меньше месяца. Dune: преимущественно write-инструменты аккаунта, TRON-покрытие не подтверждено; вернуться при расширении на EVM через REST.
  - blockscout/mcp-server: LicenseRef-Blockscout запрещает коммерческое и SaaS-использование без Commercial Licence.
  - Автогенерация инструментов из OpenAPI: Сотни инструментов с неподходящими описаниями, отсутствие контроля сырых ответов, SSRF-уязвимости генераторов (CVE-2026-32871 в FastMCP).
  - OSINT MCP-серверы (Tavily, Brave, Exa, Firecrawl): Тонкие обёртки над REST; веб-контент - главный канал prompt injection, его надо пропускать через собственный санитайзер, поэтому вызывать REST напрямую.

## LIVE PROBE FINDINGS
- gh api repos/... выполнен для ~60 репозиториев (license, pushed_at, archived, stars, open issues, releases, workflows) 2026-10-13/14; ни один из проверенных репозиториев не archived.
- Обнаружены переименования через редиректы GitHub API: run-llama/workflows-py -> run-llama/llama-agents; strands-agents/sdk-python -> strands-agents/harness-sdk; jlowin/fastmcp -> PrefectHQ/fastmcp.
- Чтение кода pydantic/pydantic-ai pydantic_ai_slim/pydantic_ai/usage.py: класс UsageLimits содержит cost_limit: Decimal | None («The maximum cost allowed in USD»), request_limit: int | None = 50, tool_calls_limit,
input/output/total_tokens_limit, per_request_input_tokens_limit; при превышении - UsageLimitExceeded; есть предупреждение, если cost_limit задан, а стоимость не вычислена.
- Чтение pydantic_ai/durable_exec/dbos/_durability.py: импорт приватных модулей dbos._error и dbos._context; DBOSDurability требует вызывать agent.run() внутри собственного @DBOS.workflow.
- Чтение pydantic-ai-slim pyproject.toml: requires-python >=3.11; extras dbos = dbos>=2.10.0 (без верхней границы), temporal = temporalio>=1.27.0, mcp = fastmcp-slim[client]>=3.3.0,<5; зависимость httpx2>=2.7.
- Чтение anthropics/claude-agent-sdk-python src/claude_agent_sdk/types.py: ClaudeAgentOptions содержит max_budget_usd, max_turns, can_use_tool, hooks, permission_mode, resume, fork_session, mcp_servers, agents, sandbox,
fallback_model. LICENSE.md TypeScript-репозитория: «© Anthropic PBC. All rights reserved. Use is subject to Anthropic's Commercial Terms of Service».
- Чтение langchain-ai/langgraph libs/langgraph/langgraph/types.py (v1.2.15): Durability = Literal['sync','async','exit'], RetryPolicy, TimeoutPolicy, CachePolicy, Interrupt, Send, Command; бюджетных или стоимостных примитивов нет.
pyproject: зависимость langchain-core>=1.4.7,<2, langgraph-checkpoint>=4.3.0,<5.
- gh api security-advisories: langchain-ai/langgraph - 11 (4 high), включая CVE-2025-64439, CVE-2026-27794, CVE-2026-28277, CVE-2026-48775, CVE-2025-67644; modelcontextprotocol/python-sdk - 12 (9 high), 9 опубликованы в 2026;
PrefectHQ/fastmcp - 8; pydantic/pydantic-ai - 14; dbos-transact-py, openai-agents-python, adk-python, crewAI - 0 опубликованных.
- README microsoft/autogen: бейдж и блок «Maintenance Mode… will not receive new features or enhancements and is community managed»; последний коммит 2026-04-06.
- Чтение crewAI lib/crewai/src/crewai/telemetry/telemetry.py: OTLP-экспорт на CREWAI_TELEMETRY_BASE_URL/v1/traces, расширенные данные только при share_crew.
- Тексты лицензий прочитаны через gh api: restatedev/restate - Business Source License 1.1 с Additional Use Grant; inngest/inngest - SSPL v1 + Apache 2.0 Future License; Arize-ai/phoenix - Elastic License 2.0; mastra-ai/mastra -
Apache-2.0 + отдельная лицензия для каталогов ee/; blockscout/mcp-server - LicenseRef-Blockscout v1.0 (effective 2026-05-15) с запретом коммерческого и SaaS-использования без Commercial Licence; проекты modelcontextprotocol -
переход MIT -> Apache-2.0.
- slowmist/MistTrackMCP: дерево файлов, package.json (version 1.1.0, license ISC, test = «no test specified», @modelcontextprotocol/sdk ^1.11.0), файла LICENSE нет; src/utils/misttrackClient.ts добавляет api_key в URL-параметры для
GET и POST; src/tools/summaryPrompts.ts (20 KB) содержит инструкции для модели; всего 4 коммита одного автора.
- BofAI/mcp-server-tron README: без TRONGRID_API_KEY mainnet-RPC по умолчанию https://hptg.bankofai.io; кошельки через agent-wallet; флаг --readonly скрывает write-инструменты; последний коммит 2026-03-30.
- bitquery/mcp README (обновлён 2026-10-02): endpoint https://mcp.bitquery.io, вход только OAuth 2.1 через браузер, кода сервера в репозитории нет.
- Keyless GET https://mcp.trongrid.io/mcp -> HTTP 405, тело {"status":405,"error":"Method Not Allowed","path":"/mcp"}; keyless GET https://mcp.tronscan.org/mcp -> HTTP 405. Оба сервиса живы и принимают только POST; tools/list не
вызывался.
- Keyless GET https://api.trongrid.io/v1/accounts/TKHuVq1oKVruCGLvqVexFs6dawKv6fQgFs/transactions/trc20?limit=20&contract_address=TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t -> HTTP 200, 0.49 с, 7 957 байт.
- Keyless GET https://apilist.tronscanapi.com/api/token_trc20/transfers?... -> HTTP 429: «request rate exceeded the allowed_rps(3), and the query server is suspended for 57 s» (вероятно, из-за параллельных запросов других аудиторов
с того же IP); дальнейшие запросы к хосту не выполнялись.
- NVD API (keyless GET): CVE-2025-6514 (mcp-remote, OS command injection, CVSS 9.6, 2025-07-09); CVE-2025-49596 (MCP Inspector < 0.14.1, RCE, CVSS 9.4, 2025-06-13); CVE-2025-54136 (Cursor <= 1.2.4, CVSS 7.2 по NVD, 2025-08-02).
- modelcontextprotocol.io: спецификация ссылается на schema/2026-07-28; changelog 2026-07-28 подтверждает удаление сессий и handshake, вынос Tasks в расширение, deprecated Sampling/Roots/Logging/DCR/HTTP+SSE. Release notes python-
sdk v2.0.0 (2026-07-28): поддержка ревизии 2026-07-28, v1.x в maintenance mode.
- developers.tron.network/docs/mcp (updatedAt 2026-10-12): TronGrid MCP - 149 инструментов (18 + 73 + 25 + 33), протокол 2025-11-25, включает broadcastTransaction, deployContract и др.; числовые лимиты и условия использования не
указаны.
- platform.claude.com/docs/en/about-claude/pricing (2026-10-14): Claude Sonnet 5.5 $2/$10 за MTok, Claude Haiku 5.5 $0.10/$0.50 (промпт до 100k токенов) и $0.50/$2.50 (свыше), Claude Opus 5.5 $4/$20.
- GitHub Search API исчерпал лимит 30 запросов/мин (общий для параллельных агентов) - поиск по запросам goplus mcp, nansen mcp, chainbase mcp не выполнен.

## CANDIDATES (full audit cards)

### [RECOMMENDED] DBOS Transact (Python) как durable-ядро собственного детерминированного оркестратора
NEED: (a) Оркестрация: durable state, checkpoint/resume многочасовых прогонов, очереди с rate limit по источникам, пауза по бюджету, HITL
KIND: open-source library (+ опциональный commercial SaaS Conductor)
URL: https://github.com/dbos-inc/dbos-transact-py
LICENSE: MIT (pyproject.toml: license MIT; GitHub SPDX MIT)
COMMERCIAL USE: Да, без условий (MIT). Conductor / DBOS Cloud - отдельные платные продукты, для работы библиотеки не обязательны.
PROJECT STATE: v3.2.0 (2026-09-29), последний коммит 2026-10-13, 1 626 звёзд, 6 open issues, не archived. CI: unit-test.yml, chaos-test.yml, publish.yml; каталог tests - 52 элемента. Релизы каждые 1-2 недели. Мажор 3.0.0 вышел 2026-09-16. Топ-
контрибьютор kraftp - 394 коммита (следующий 77): bus factor сконцентрирован. Security advisories: 0 опубликовано.
CLAIMED VS ACTUAL: (1) Заявлено «free forever, ultra-lightweight» - верно для библиотеки, но консоль наблюдаемости, distributed recovery, alerting, RBAC находятся в платном Conductor; self-host Conductor только в Enterprise. (2) 3.0.0 удалил admin
server, in-memory queues, in-memory scheduler и устаревшие интеграции - обратная совместимость ломалась месяц назад. (3) Детерминизм workflow-кода статически не проверяется: DBOSStepNondeterminismError возникает только при
recovery. (4) Чекпоинты по умолчанию pickle; docs Pydantic AI советуют держать вход/выход шага до ~2 MB - тяжёлые данные надо хранить в своих таблицах, а в шагах передавать ID. (5) Deduplication не поддерживается на partitioned
queues.
CAPABILITIES: Workflow/step с чекпоинтом каждого шага в Postgres (или SQLite); recovery с последнего завершённого шага; шаги at-least-once, после завершения не переисполняются. Очереди в Postgres: global_concurrency, worker_concurrency,
limiter={limit, period}, partition_limiter, priority, deduplication_id, delay_seconds. Durable sleep, SetWorkflowTimeout. DBOS.send/recv и set_event/get_event (durable, подходят для HITL и паузы по бюджету). cancel_workflow /
resume_workflow / fork_workflow (с выбранного шага) / rewind_workflow; list_workflows, list_workflow_steps. OTel extra. Python 3.10-3.14 в classifiers.
INFRA: Только Postgres (можно тот же инстанс, что у платформы); воркер живёт внутри процесса приложения, отдельного сервера оркестрации нет. Страница pricing заявляет работу на Linux, macOS и Windows.
PRICING/LIMITS: Библиотека $0. Conductor Pro $99/мес (2 seats, 3 apps, 1M checkpoints/мес, далее $50 за 1M), Teams $499/мес (10 seats, 10 apps, 10M checkpoints, $40 за 1M), Enterprise - custom (https://www.dbos.dev/dbos-pricing, прочитано
2026-10-14).
RISKS: Молодой вендор и небольшое сообщество (1.6k звёзд против 23.7k у Temporal); bus factor; pickle в чекпоинтах (нельзя класть недоверенные объекты); без Conductor нет готового UI; масштабирование упирается в один Postgres; мажорные
версии с удалением API.
REPLACEABILITY: Высокая: модель workflow/step 1:1 переносится на Temporal (workflow/activity) или Restate; шаги - обычные Python-функции; декораторы изолируются в одном модуле-адаптере.
HOW VERIFIED: gh api (metadata, releases, pyproject.toml, release notes 3.0.0, contributors, workflows, security-advisories); чтение docs (queue-tutorial, workflow-tutorial, workflow-management, workflow-communication, pricing). Код не
запускался.
CONFIDENCE: medium
EVIDENCE: https://github.com/dbos-inc/dbos-transact-py | https://github.com/dbos-inc/dbos-transact-py/releases/tag/3.0.0 | https://docs.dbos.dev/python/tutorials/queue-tutorial | https://docs.dbos.dev/python/tutorials/workflow-tutorial | https://docs.dbos.dev/python/tutorials/workflow-management | https://docs.dbos.dev/python/tutorials/workflow-communication

### [RECOMMENDED] Pydantic AI
NEED: (a) Слой LLM-шагов в точках принятия решений: модель-агностичные агенты, structured outputs, лимиты токенов/долларов, approval инструментов, тестовые модели, evals
KIND: open-source library
URL: https://github.com/pydantic/pydantic-ai
LICENSE: MIT
COMMERCIAL USE: Да, без условий (MIT). Logfire (SaaS наблюдаемости того же вендора) опционален.
PROJECT STATE: v2.55.0 (2026-10-09), последний коммит 2026-10-13, 20 595 звёзд, 1 373 open issues+PR, 54 CI workflows, tests - 150 элементов. v1.0.0 вышел 2025-09-04, v2.0.0 - 2026-06-23; ветка v1 ещё патчится (v1.107.7 от 2026-09-30). 14
опубликованных security advisories (большинство в опциональных web UI, web_fetch, UI-адаптерах и OTel-редакции).
CLAIMED VS ACTUAL: (1) Version policy обещает отсутствие breaking changes в minor, но за ~16 недель после 2.0 вышло 55 minor-релизов; beta-модули и «bug fixes that may break» из гарантии исключены. (2) DBOSAgent уже помечен deprecated и будет удалён
в v3 - замена на DBOSDurability произошла внутри v2. (3) cost_limit - best-effort: cost=None для моделей без цен, docs прямо говорят не считать его жёсткой биллинговой гарантией. (4) В v2 удалён модуль persistence из
pydantic_graph - собственного чекпоинтинга у графа нет, durability только через внешние движки. (5) DBOS-интеграция импортирует приватные модули dbos._error и dbos._context - хрупкая связка двух быстро меняющихся библиотек. (6)
pydantic-ai-slim требует Python >=3.11.
CAPABILITIES: Нативные провайдеры (каталог models/): anthropic, openai, google, bedrock, groq, mistral, cohere, openrouter, ollama, xai, huggingface, cerebras и др.; FallbackModel. UsageLimits: request_limit (default 50), tool_calls_limit,
input/output/total_tokens_limit, per_request_input_tokens_limit, cost_limit в USD (Decimal) - подтверждено чтением usage.py. agent.iter() для пошагового исполнения. Deferred tools: requires_approval, ApprovalRequired,
DeferredToolRequests/DeferredToolResults. models/test.py и models/function.py (TestModel/FunctionModel) для тестов без сети. pydantic_evals (dataset, evaluators, reporting). Toolsets: filtered, prefixed, approval_required.
durable_exec: temporal, dbos, prefect в репозитории; docs называют ещё Restate и AWS Lambda. OTel-инструментирование. MCP-клиент через fastmcp-slim.
INFRA: Нет (библиотека).
PRICING/LIMITS: $0. Следующий мажор - не ранее чем через 3 месяца после v2.0; security-фиксы v1 - минимум 6 месяцев после v2 (version-policy).
RISKS: Очень высокая скорость релизов - нужен pin точной версии и регулярное обновление; advisories GHSA-4x9p-g9wm-8q7f и GHSA-3gh4-cghq-f8v4 (OTel include_content=False не редактировал исключения и retry-промпты) прямо касаются
требования «ключи не утекают в логи» - нужен собственный scrubber; серия SSRF-advisories по web_fetch - не давать агентам встроенный web_fetch.
REPLACEABILITY: Высокая при дисциплине: каждый агент оформляется как функция decide(Input) -> Output на pydantic-моделях; замена на OpenAI Agents SDK или прямые SDK провайдеров затрагивает один модуль.
HOW VERIFIED: gh api + чтение кода (pydantic_ai/usage.py, pyproject.toml, durable_exec/dbos/_durability.py, листинги каталогов); docs (changelog, version-policy, agent, deferred-tools, durable_execution overview и dbos); список security
advisories через gh api. Код не запускался.
CONFIDENCE: high
EVIDENCE: https://github.com/pydantic/pydantic-ai | https://github.com/pydantic/pydantic-ai/blob/main/pydantic_ai_slim/pydantic_ai/usage.py | https://pydantic.dev/docs/ai/project/changelog/ | https://pydantic.dev/docs/ai/project/version-policy/ | https://pydantic.dev/docs/ai/tools-toolsets/deferred-tools/ | https://pydantic.dev/docs/ai/integrations/durable_execution/overview/

### [ALTERNATIVE] LangGraph
NEED: (a) Оркестрация «всё в одном»: граф, чекпоинты, interrupt, параллельные ветки
KIND: open-source library (+ commercial LangSmith / LangGraph Platform)
URL: https://github.com/langchain-ai/langgraph
LICENSE: MIT
COMMERCIAL USE: Да (MIT). LangSmith и платформа деплоя - отдельные коммерческие продукты.
PROJECT STATE: v1.2.15 (2026-10-12), последний коммит 2026-10-13, 43 212 звёзд, 812 open issues, 17 CI workflows. 1.0.0 вышел 2025-10-17. Отдельные пакеты: checkpoint 4.3.0, checkpoint-postgres 3.1.3, checkpoint-sqlite 3.1.2, checkpoint-
conformance. 11 опубликованных advisories, из них 4 high.
CLAIMED VS ACTUAL: (1) Бюджетных примитивов (токены/доллары/счётчики запросов) в ядре нет - в types.py отсутствуют; придётся писать самим. (2) При resume узел исполняется с начала, код до interrupt() повторяется - побочные эффекты должны быть
идемпотентны (прямо в docs). (3) Чекпоинт сериализует всё состояние на каждом superstep - для графа на 1 000 адресов и десятки тысяч переводов состояние всё равно придётся выносить в свои таблицы. (4) Rate limiting по внешним
источникам данных не встроен. (5) История десериализационных уязвимостей чекпоинтов: CVE-2025-64439 (RCE в JsonPlusSerializer, high), CVE-2026-27794, CVE-2026-28277 (msgpack), CVE-2026-48775 (JSON), плюс SQL-инъекция в SQLite-
чекпоинтере CVE-2025-67644. (6) Жёсткая зависимость langchain-core>=1.4.7.
CAPABILITIES: Граф с детерминированными и условными рёбрами; чекпоинтеры PostgresSaver / SqliteSaver / InMemorySaver; режимы Durability sync/async/exit; RetryPolicy, TimeoutPolicy, CachePolicy; Send для fan-out; interrupt() +
Command(resume=...) для HITL (в т.ч. параллельные interrupt по ID); time travel по чекпоинтам. Python 3.10-3.13.
INFRA: Postgres для чекпоинтов; отдельного сервера не требуется.
PRICING/LIMITS: $0 за библиотеку. Ограничение Postgres-чекпоинтера: thread_id до 255 символов; чекпоинты накапливаются и требуют pruning (docs).
RISKS: Lock-in на модель state/channels/reducers и экосистему LangChain; лучший UX трассировки - в платном LangSmith; частые релизы (15 патчей 1.2.x за 5 месяцев).
REPLACEABILITY: Средняя: узлы - Python-функции, но state-схема, reducers и чекпоинтер пронизывают код.
HOW VERIFIED: gh api (metadata, releases, pyproject.toml, чтение libs/langgraph/langgraph/types.py, security-advisories); docs (interrupts, persistence). Страница durable-execution через WebFetch вернула содержимое persistence - детали durable
execution подтверждены только по коду types.py.
CONFIDENCE: high
EVIDENCE: https://github.com/langchain-ai/langgraph | https://github.com/langchain-ai/langgraph/blob/main/libs/langgraph/langgraph/types.py | https://docs.langchain.com/oss/python/langgraph/interrupts | https://docs.langchain.com/oss/python/langgraph/durable-execution | https://github.com/langchain-ai/langgraph/security/advisories

### [ALTERNATIVE] Temporal (server + sdk-python)
NEED: (a) Durable execution промышленного уровня; целевая точка миграции при росте
KIND: open-source server + SDK (+ commercial Temporal Cloud)
URL: https://temporal.io
LICENSE: MIT (server и sdk-python)
COMMERCIAL USE: Да (MIT).
PROJECT STATE: Server v1.31.4 (2026-10-12), 23 674 звезды, 22 CI workflows; sdk-python 1.34.0 (2026-09-30), 1 221 звезда, 70 open issues, CI: ci.yml, nightly.yml, run-bench.yml. Проект с 2019 года.
CLAIMED VS ACTUAL: Dev-сервер из CLI (SQLite) позиционируется в docs только для локальной разработки и тестов, не для production; production self-host - это Temporal Server + UI server + БД (в Docker Compose по умолчанию PostgreSQL и Elasticsearch)
и ручное управление схемой через admin-tools. Для одного скромного сервера и маленькой команды это заметная операционная нагрузка.
CAPABILITIES: Workflows/activities, signals/queries/updates (HITL), timers, child workflows, replay-тестирование, versioning. Pydantic AI и OpenAI Agents SDK имеют интеграции с Temporal.
INFRA: Отдельный кластер сервисов + БД (+ Elasticsearch в дефолтном compose) либо Temporal Cloud.
PRICING/LIMITS: Self-host $0. Temporal Cloud: от $50 за 1M actions (со скидками до $25), storage $0.042/GBh active и $0.00105/GBh retained, $150 кредитов на 90 дней новым пользователям; Business support от $500/мес (https://temporal.io/pricing,
прочитано 2026-10-14).
RISKS: Операционная сложность self-host; sandbox детерминизма в Python требует дисциплины; для MVP избыточен.
REPLACEABILITY: Средняя; является естественной заменой DBOS при росте (та же модель workflow/activity).
HOW VERIFIED: gh api (metadata, releases, workflows); docs (self-hosted-guide/deployment, pricing). Код не запускался.
CONFIDENCE: high
EVIDENCE: https://github.com/temporalio/temporal | https://github.com/temporalio/sdk-python | https://docs.temporal.io/self-hosted-guide/deployment | https://temporal.io/pricing

### [REJECTED] Claude Agent SDK (Python / TypeScript)
NEED: (a) Агентный harness с готовым agent loop, hooks, permissions, subagents
KIND: SDK-обёртка над проприетарным бинарём Claude Code
URL: https://code.claude.com/docs/en/agent-sdk/overview
LICENSE: Python-обёртка: MIT. TypeScript-пакет: проприетарный («All rights reserved», Anthropic Commercial Terms of Service). Встроенный Claude Code CLI - проприетарный.
COMMERCIAL USE: Разрешено по Anthropic Commercial Terms, включая продукты для своих клиентов; запрещено предлагать claude.ai login без одобрения - только API-ключи; брендинг «Claude Code» использовать нельзя.
PROJECT STATE: Python v0.2.165 (2026-10-08), 8 266 звёзд, 545 open issues, 14 CI workflows; TypeScript v0.3.296 (2026-10-09), 1 805 звёзд. Версии 0.x, релизы почти ежедневно.
CLAIMED VS ACTUAL: (1) Это не библиотека оркестрации, а запуск бинаря Claude Code как подпроцесса (docs: «A library that runs the Claude Code binary») - управляющий поток задаёт модель, а не детерминированный граф. (2) Только модели Claude -
требование model-agnostic не выполняется. (3) Заявленный MIT относится лишь к Python-обёртке; ядро проприетарное. (4) Версии 0.x без гарантий стабильности API.
CAPABILITIES: ClaudeAgentOptions (подтверждено чтением types.py): max_budget_usd, max_turns, can_use_tool, hooks (PreToolUse/PostToolUse и ещё около 20 событий), permission_mode, resume, fork_session, mcp_servers, agents (subagents), sandbox,
fallback_model. Custom tools через in-process SDK MCP server.
INFRA: Node-бинарь Claude Code в составе wheel; локальная файловая система для сессий.
PRICING/LIMITS: SDK бесплатен; оплата токенов Claude API (на 2026-10-14: Sonnet 5.5 $2/$10 за MTok, Haiku 5.5 $0.10/$0.50 до 100k токенов промпта, Opus 5.5 $4/$20).
RISKS: Vendor lock-in на одного провайдера; недетерминированный control flow; сложнее воспроизводимость и replay; проприетарное ядро.
REPLACEABILITY: Низкая: hooks, permissions и сессии специфичны для Claude Code.
HOW VERIFIED: gh api (metadata, LICENSE.md TS-репозитория, README и types.py Python-репозитория); docs code.claude.com/docs/en/agent-sdk/overview; цены - platform.claude.com/docs/en/about-claude/pricing.
CONFIDENCE: high
EVIDENCE: https://github.com/anthropics/claude-agent-sdk-python | https://github.com/anthropics/claude-agent-sdk-typescript/blob/main/LICENSE.md | https://code.claude.com/docs/en/agent-sdk/overview | https://platform.claude.com/docs/en/about-claude/pricing

### [ALTERNATIVE] OpenAI Agents SDK (Python)
NEED: (a) Лёгкий агентный слой: handoffs, guardrails, HITL, tracing
KIND: open-source library
URL: https://github.com/openai/openai-agents-python
LICENSE: MIT
COMMERCIAL USE: Да (MIT).
PROJECT STATE: v0.23.1 (2026-10-02), последний коммит 2026-10-13, 30 015 звёзд, всего 8 open issues, 10 CI workflows. Всё ещё 0.x; 12 релизов за август-октябрь 2026. Опубликованных advisories нет.
CLAIMED VS ACTUAL: (1) Встроенного лимита токенов или долларов нет - единственный run-level лимит max_turns (docs). (2) RunState.from_json не аутентифицирует снимки - docs требуют самостоятельно обеспечивать целостность. (3) Модель-агностичность не
нативная, а через сторонние адаптеры; часть функций (conversation_id, previous_response_id) работает только с OpenAI Responses API. (4) Control flow задаёт модель; детерминированный оркестратор всё равно пишется снаружи.
CAPABILITIES: Agent loop, handoffs, guardrails, sessions, needs_approval + RunState (to_json/from_json) для паузы и возобновления, MCP, tracing; docs называют интеграции durable execution: Temporal, DBOS, Restate, Dapr; не-OpenAI модели через
адаптеры LiteLLM / Any-LLM.
INFRA: Нет.
PRICING/LIMITS: $0.
RISKS: 0.x - breaking changes в minor; OpenAI-first; нужен LiteLLM для других провайдеров (инцидент supply chain в марте 2026).
REPLACEABILITY: Высокая (тонкий слой).
HOW VERIFIED: gh api (metadata, releases, advisories); docs (running_agents, human_in_the_loop).
CONFIDENCE: high
EVIDENCE: https://github.com/openai/openai-agents-python | https://openai.github.io/openai-agents-python/running_agents/ | https://openai.github.io/openai-agents-python/human_in_the_loop/

### [REJECTED] Google Agent Development Kit (ADK, Python)
NEED: (a) Агентный фреймворк с workflow-агентами и графами
KIND: open-source library
URL: https://github.com/google/adk-python
LICENSE: Apache-2.0
COMMERCIAL USE: Да (Apache-2.0).
PROJECT STATE: v2.12.0 (2026-10-13), 21 807 звёзд, 416 open issues, 15 CI workflows. 2.0.0 вышел 2026-05-19, через ~13.5 месяцев после создания репозитория (2025-04-01); ветка 1.x поддерживалась параллельно до v1.39.1 (2026-08-27).
CLAIMED VS ACTUAL: (1) Resumability: инструменты исполняются at-least-once и могут повториться при resume; ADK Web UI и CLI resume не поддерживают; изменение состава агентов в остановленном workflow не поддерживается; для custom-агентов resume надо
реализовывать вручную. (2) Бюджетных лимитов в долларах на странице обзора нет. (3) Gemini-first; прочие модели через адаптеры.
CAPABILITIES: Sequential/Parallel/Loop workflow-агенты, graph-based workflows (новое в 2.0), action confirmations, evaluation, MCP, адаптеры Claude/OpenAI/Ollama/LiteLLM; Python, TypeScript, Go, Java, Kotlin.
INFRA: Session service; для production-персистентности ориентирован на Google Cloud.
PRICING/LIMITS: $0.
RISKS: Мажорная смена API через год после запуска; экосистемный крен в GCP/Gemini; две параллельные ветки версий.
REPLACEABILITY: Средняя.
HOW VERIFIED: gh api (metadata, releases); docs adk.dev (главная и runtime/resume).
CONFIDENCE: medium
EVIDENCE: https://github.com/google/adk-python | https://adk.dev/ | https://adk.dev/runtime/resume/

### [REJECTED] Microsoft Agent Framework (MAF)
NEED: (a) Агентный фреймворк с graph workflows и чекпоинтами
KIND: open-source library
URL: https://github.com/microsoft/agent-framework
LICENSE: MIT
COMMERCIAL USE: Да (MIT); для сторонних моделей и серверов действует оговорка Microsoft Product Terms («at your own risk»).
PROJECT STATE: python-1.21.0 (2026-10-08), dotnet-1.24.0 (2026-10-07), 14 115 звёзд, 757 open issues, 30 CI workflows. python-1.0.0 вышел 2026-04-02; с тех пор 21 minor-релиз. Go - public preview.
CLAIMED VS ACTUAL: (1) Встроенные хранилища чекпоинтов для Python: только InMemory, File и Azure Cosmos DB - Postgres нет, production-вариант привязан к Azure. (2) Чекпоинты используют pickle с restricted unpickler - docs прямо называют хранилище
чекпоинтов границей доверия. (3) Python 1.13.0 внёс «minor breaking changes» в порядок чекпоинтов уже после 1.0.
CAPABILITIES: Агенты, Harness Agent, functional и graph-based workflows с superstep-чекпоинтами, HITL request/response, middleware, MCP-клиенты; провайдеры Foundry, Azure OpenAI, OpenAI, Anthropic, Ollama.
INFRA: Для durable-чекпоинтов вне Azure нужен собственный CheckpointStorage.
PRICING/LIMITS: $0; Cosmos DB оплачивается отдельно.
RISKS: Крен в Azure/Foundry; молодой 1.x; pickle.
REPLACEABILITY: Средняя.
HOW VERIFIED: gh api (metadata, releases); docs learn.microsoft.com (overview, workflows/checkpoints).
CONFIDENCE: high
EVIDENCE: https://github.com/microsoft/agent-framework | https://learn.microsoft.com/en-us/agent-framework/overview/agent-framework-overview | https://learn.microsoft.com/en-us/agent-framework/workflows/checkpoints

### [REJECTED] AutoGen (Microsoft) и AG2 (форк сообщества)
NEED: (a) Мультиагентные диалоговые фреймворки
KIND: open-source libraries
URL: https://github.com/microsoft/autogen
LICENSE: AutoGen: GitHub API сообщает CC-BY-4.0 на уровне репозитория; AG2: Apache-2.0
COMMERCIAL USE: AG2 - да (Apache-2.0). AutoGen - лицензия кода требует отдельной проверки, но вопрос неактуален из-за статуса проекта.
PROJECT STATE: AutoGen: README объявляет Maintenance Mode («will not receive new features… community managed»), последний коммит 2026-04-06, последний релиз python-v0.7.5 от 2025-09-30, 61 387 звёзд, 1 105 open issues. AG2: v1.2.0 (2026-10-11),
4 993 звезды, 70 open issues, активен.
CLAIMED VS ACTUAL: AutoGen по звёздам выглядит лидером, но фактически заморожен; Microsoft сам направляет новых пользователей на Agent Framework. AG2 - диалоговая (conversation-driven) оркестрация, а не детерминированный граф с durable-чекпоинтами.
PRICING/LIMITS: $0.
RISKS: AutoGen - тупиковая ветка; AG2 - малое сообщество, недетерминированный групповой чат как основная модель управления.
REPLACEABILITY: Не применимо.
HOW VERIFIED: gh api (metadata, README AutoGen, releases).
CONFIDENCE: high
EVIDENCE: https://github.com/microsoft/autogen | https://github.com/ag2ai/ag2

### [REJECTED] CrewAI
NEED: (a) Ролевые «команды» агентов и Flows
KIND: open-source library (+ commercial платформа)
URL: https://github.com/crewAIInc/crewAI
LICENSE: MIT
COMMERCIAL USE: Да (MIT).
PROJECT STATE: 1.15.27 (2026-10-09), 59 659 звёзд, 653 open issues, 16 CI workflows; 1.0.0 вышел 2025-10-20. Monorepo: lib/crewai, crewai-core, crewai-tools, crewai-files, cli.
CLAIMED VS ACTUAL: (1) Телеметрия включена по умолчанию: модуль telemetry/telemetry.py отправляет OTLP-трейсы на CREWAI_TELEMETRY_BASE_URL (данные задач уходят только при share_crew) - для платформы расследований это нежелательный исходящий канал,
требует явного отключения. (2) Базовая модель Crew - LLM-управляемая делегация ролей, т.е. противоположность «LLM только в точках решений»; детерминизм дают лишь Flows. (3) Затронут компрометацией LiteLLM (вторичные источники
называют CrewAI среди downstream-проектов).
PRICING/LIMITS: $0 за библиотеку.
RISKS: Недетерминированность, скрытые промпты и расход токенов на ролевую «болтовню»; телеметрия; тяжёлые зависимости.
REPLACEABILITY: Низкая-средняя.
HOW VERIFIED: gh api (metadata, releases, чтение lib/crewai/src/crewai/telemetry/telemetry.py); поиск по инциденту LiteLLM.
CONFIDENCE: medium
EVIDENCE: https://github.com/crewAIInc/crewAI | https://github.com/crewAIInc/crewAI/blob/main/lib/crewai/src/crewai/telemetry/telemetry.py

### [REJECTED] LlamaIndex Workflows (репозиторий переименован в run-llama/llama-agents)
NEED: (a) Event-driven workflow-библиотека
KIND: open-source library
URL: https://github.com/run-llama/llama-agents
LICENSE: MIT
COMMERCIAL USE: Да (MIT).
PROJECT STATE: llama-index-workflows@2.26.0 (2026-10-11), 460 звёзд, 20 open issues, 10 CI workflows. Запрос repos/run-llama/workflows-py теперь редиректит на run-llama/llama-agents. В monorepo есть пакет llama-agents-dbos (DBOS как backend
durability).
CLAIMED VS ACTUAL: Позиционирование сместилось: README описывает «framework for building and shipping document-centric agents» (OCR, extraction, review) - не общий оркестратор расследований. Durability «pluggable» - реальная надёжность снова
приходит от внешнего движка (DBOS).
PRICING/LIMITS: $0.
RISKS: Маленькое сообщество отдельного пакета, переименования и смена фокуса; бюджетных примитивов нет (не проверено по коду).
REPLACEABILITY: Средняя.
HOW VERIFIED: gh api (metadata, README, листинг packages).
CONFIDENCE: medium
EVIDENCE: https://github.com/run-llama/llama-agents | https://github.com/run-llama/llama_index

### [REJECTED] Mastra
NEED: (a) TypeScript-фреймворк агентов и workflows
KIND: open-source library (+ enterprise-каталоги)
URL: https://github.com/mastra-ai/mastra
LICENSE: Apache-2.0 для основного кода; каталоги ee/ (в т.ч. @mastra/core/auth/ee, agent-builder/ee, editor/ee) - под отдельной лицензией ee/LICENSE
COMMERCIAL USE: Да для Apache-части; ee-функции требуют отдельной лицензии.
PROJECT STATE: @mastra/core@1.76.0 (2026-10-13), 28 792 звезды, 588 open issues, 36 CI workflows.
CLAIMED VS ACTUAL: GitHub показывает лицензию NOASSERTION: фактически это смешанная модель Apache-2.0 + ee. Только TypeScript.
PRICING/LIMITS: $0 за OSS-часть.
RISKS: Только TS, тогда как дата-стек расследований (графы, аналитика, evals) естественнее в Python; смешанная лицензия; 76 minor-версий ядра 1.x.
REPLACEABILITY: Низкая (смена языка).
HOW VERIFIED: gh api (metadata, текст LICENSE, releases). Функциональность по docs глубоко не читалась.
CONFIDENCE: medium
EVIDENCE: https://github.com/mastra-ai/mastra | https://github.com/mastra-ai/mastra/blob/main/LICENSE.md

### [REJECTED] Vercel AI SDK
NEED: (a) TypeScript toolkit для LLM-вызовов и tool loop
KIND: open-source library
URL: https://github.com/vercel/ai
LICENSE: Apache-2.0 (текст LICENSE прочитан; GitHub SPDX показывает NOASSERTION)
COMMERCIAL USE: Да (Apache-2.0).
PROJECT STATE: ai@7.0.139 (2026-10-13), 27 301 звезда, 1 610 open issues, 14 CI workflows.
CLAIMED VS ACTUAL: Это toolkit вызовов моделей и UI-стриминга, а не durable-оркестратор: чекпоинты, очереди и resume требуют отдельного движка.
PRICING/LIMITS: $0.
RISKS: Только TS; частые мажоры (уже 7.x); нет durable state из коробки.
REPLACEABILITY: Высокая как слой вызова моделей на фронтенде.
HOW VERIFIED: gh api (metadata, LICENSE, releases). Docs глубоко не читались.
CONFIDENCE: medium
EVIDENCE: https://github.com/vercel/ai

### [REJECTED] smolagents (Hugging Face)
NEED: (a) Минималистичные code-агенты
KIND: open-source library
URL: https://github.com/huggingface/smolagents
LICENSE: Apache-2.0
COMMERCIAL USE: Да (Apache-2.0).
PROJECT STATE: v1.26.0 от 2026-05-29 - последний релиз 4.5 месяца назад; последний коммит 2026-10-06; 29 821 звезда, 929 open issues, 6 CI workflows.
CLAIMED VS ACTUAL: Основная модель - агент пишет и исполняет Python-код; это противоречит требованиям детерминизма, воспроизводимости и безопасной обработки недоверенных данных из блокчейна и OSINT. Durable state, бюджетов и HITL-approval нет. Темп
релизов заметно упал.
PRICING/LIMITS: $0.
RISKS: Исполнение сгенерированного кода; слабая управляемость; большой backlog issues.
REPLACEABILITY: Не применимо.
HOW VERIFIED: gh api (metadata, releases).
CONFIDENCE: medium
EVIDENCE: https://github.com/huggingface/smolagents

### [NEEDS-TRIAL] DSPy
NEED: (a, дополнение) Оптимизация промптов LLM-шагов по размеченному набору, а не оркестрация
KIND: open-source library
URL: https://github.com/stanfordnlp/dspy
LICENSE: MIT
COMMERCIAL USE: Да (MIT).
PROJECT STATE: 3.4.1 (2026-10-12), 38 614 звёзд, 808 open issues, 7 CI workflows.
CLAIMED VS ACTUAL: Часто упоминается в ряду «agent frameworks», но durable-оркестрации, чекпоинтов, HITL и бюджетов не даёт. По вторичным источникам, был среди downstream-проектов, затронутых компрометацией LiteLLM (март 2026).
PRICING/LIMITS: $0.
RISKS: Зависимость от LiteLLM; оптимизированные промпты надо версионировать как артефакты для воспроизводимости.
REPLACEABILITY: Высокая (офлайн-инструмент).
HOW VERIFIED: gh api (metadata, releases); поиск по инциденту LiteLLM. Код и docs глубоко не читались.
CONFIDENCE: low
EVIDENCE: https://github.com/stanfordnlp/dspy

### [ALTERNATIVE] Restate
NEED: (a) Durable execution одним бинарём
KIND: source-available server (BSL) + open-source SDK
URL: https://restate.dev
LICENSE: Server: Business Source License 1.1 с Additional Use Grant (запрещён только «Public Restate Platform Service»); sdk-python: MIT
COMMERCIAL USE: Да для нашего сценария: лицензия прямо разрешает любое production-развёртывание, исполняющее сервисы самого лицензиата; запрещено лишь предоставлять третьим лицам managed-доступ к API Restate.
PROJECT STATE: Server v1.7.13 (2026-10-01), 1.8.0-rc.3 (2026-10-13), 4 555 звёзд, 472 open issues, 17 CI workflows. sdk-python v1.0.5 (2026-09-02), всего 82 звезды, 24 open issues.
CLAIMED VS ACTUAL: GitHub показывает NOASSERTION - это BSL, не OSI open source. Python SDK заметно менее зрелый, чем сервер (82 звезды).
INFRA: Отдельный серверный процесс (single binary) рядом с приложением.
PRICING/LIMITS: Self-host $0. Цены Restate Cloud не получены (страница pricing не отдала содержимое).
RISKS: BSL; маленькое Python-сообщество; дополнительный компонент в эксплуатации.
REPLACEABILITY: Средняя.
HOW VERIFIED: gh api (metadata, releases, текст LICENSE). Docs не читались.
CONFIDENCE: medium
EVIDENCE: https://github.com/restatedev/restate | https://github.com/restatedev/sdk-python

### [ALTERNATIVE] Hatchet
NEED: (a) Очередь задач и durable workflows на Postgres
KIND: open-source server + SDK (+ cloud)
URL: https://github.com/hatchet-dev/hatchet
LICENSE: MIT
COMMERCIAL USE: Да (MIT).
PROJECT STATE: 8 110 звёзд, 148 open issues, 31 CI workflows, последний коммит 2026-10-13; последний релиз в списке - rb/0.10.0 (Ruby SDK, 2026-10-09).
CLAIMED VS ACTUAL: Требует отдельный control plane (API server + engine + dashboard) и Postgres; RabbitMQ опционален; hatchet-lite - единый образ для dev и «low-throughput production». Это больше компонентов, чем библиотека внутри процесса.
INFRA: Postgres + контейнер(ы) Hatchet.
PRICING/LIMITS: Self-host $0; цены cloud не проверялись.
RISKS: Дополнительный сервис в эксплуатации; агентные интеграции (Pydantic AI и др.) не проверены.
REPLACEABILITY: Средняя.
HOW VERIFIED: gh api (metadata, releases); docs self-hosting.
CONFIDENCE: medium
EVIDENCE: https://github.com/hatchet-dev/hatchet | https://docs.hatchet.run/self-hosting

### [REJECTED] Inngest (+ AgentKit)
NEED: (a) Event-driven durable functions и агентный kit
KIND: source-available server + SDK (+ cloud)
URL: https://github.com/inngest/inngest
LICENSE: Server: Server Side Public License v1 с отложенным переходом на Apache 2.0; inngest-py и agent-kit: Apache-2.0
COMMERCIAL USE: Использование как backend своего SaaS допустимо, но SSPL - не OSI-лицензия и создаёт юридические вопросы при встраивании; требует оценки юристом.
PROJECT STATE: Server v1.46.0 (2026-10-06), 5 940 звёзд. inngest-py 0.5.19 (2026-06-23) - всё ещё 0.x, 217 звёзд. AgentKit: последний релиз 0.13.2 от 2025-11-13, последний коммит 2026-04-29 - фактически застой, и только TypeScript.
CLAIMED VS ACTUAL: AgentKit продвигается как агентный слой, но не обновлялся почти полгода и не имеет Python-версии; Python SDK не достиг 1.0.
INFRA: Отдельный сервер Inngest или cloud.
PRICING/LIMITS: Не проверялись.
RISKS: SSPL; незрелый Python SDK; застой AgentKit.
REPLACEABILITY: Средняя.
HOW VERIFIED: gh api (metadata, releases, текст LICENSE).
CONFIDENCE: medium
EVIDENCE: https://github.com/inngest/inngest | https://github.com/inngest/inngest-py | https://github.com/inngest/agent-kit

### [REJECTED] Дополнительно найденные: Agno, Strands Agents, Apache Burr, Haystack, Prefect
NEED: (a) Прочие агентные и workflow-фреймворки
KIND: open-source libraries
URL: https://github.com/apache/burr
LICENSE: Все Apache-2.0
COMMERCIAL USE: Да (Apache-2.0).
PROJECT STATE: Agno v3.1.3 (2026-10-12), 42 709 звёзд, 1 897 open issues. Strands: репозиторий переименован в strands-agents/harness-sdk, python/v1.60.0 (2026-10-12), 8 792 звезды, 1 006 open issues. Apache Burr v0.43.0-incubating (2026-08-29),
2 570 звёзд, последний коммит 2026-09-20. Haystack v3.3.0 (2026-10-01), 26 737 звёзд. Prefect 3.8.x, 24 016 звёзд.
CLAIMED VS ACTUAL: Глубоко не аудировались. Agno и Strands - model-driven агентные рантаймы (Strands тяготеет к AWS Bedrock); Burr - state-machine с персистентностью, но всё ещё incubating и с малым сообществом; Haystack - прежде всего RAG-
пайплайны; Prefect - data-оркестратор с отдельным сервером (Pydantic AI имеет интеграцию).
PRICING/LIMITS: $0.
RISKS: Ни один не даёт сочетания «durable + очереди с rate limit + бюджеты» лучше, чем выбранная связка; большие backlog-и issues у Agno и Strands.
REPLACEABILITY: Не применимо.
HOW VERIFIED: Только gh api metadata и releases; docs и код не читались.
CONFIDENCE: low
EVIDENCE: https://github.com/agno-agi/agno | https://github.com/strands-agents/harness-sdk | https://github.com/apache/burr | https://github.com/deepset-ai/haystack | https://github.com/PrefectHQ/prefect

### [REJECTED] LiteLLM (как обязательный model gateway)
NEED: (a) Модель-агностичность через единый прокси/SDK
KIND: open-source library + proxy (enterprise-каталог отдельно)
URL: https://github.com/BerriAI/litellm
LICENSE: MIT для основного кода; каталог enterprise/ под отдельной лицензией
COMMERCIAL USE: Да для MIT-части.
PROJECT STATE: v1.106.0-rc.1 (2026-10-11), 61 165 звёзд, 5 548 open issues, 41 CI workflow.
CLAIMED VS ACTUAL: 24 марта 2026 версии 1.82.7 и 1.82.8 на PyPI были скомпрометированы (credential stealer, включая переменные окружения и крипто-кошельки; 1.82.8 исполнялся через .pth при старте интерпретатора). Подтверждено только по вторичным
источникам - официальный postmortem не читался.
PRICING/LIMITS: $0.
RISKS: Пакет с огромной поверхностью и прецедентом supply-chain атаки стоит на пути всех API-ключей - прямо против требования «ключи не утекают». 5.5k open issues.
REPLACEABILITY: Высокая: Pydantic AI имеет нативные провайдеры и LiteLLM не требует.
HOW VERIFIED: gh api (metadata, LICENSE); веб-поиск по инциденту (вторичные источники).
CONFIDENCE: medium
EVIDENCE: https://github.com/BerriAI/litellm | https://pypistats.com/blog/litellm-pypi-supply-chain-compromise-how-a-popular-llm-proxy-became-a-credential-stealing-backdoor-march-24-2026

### [NEEDS-TRIAL] Langfuse (self-hosted) / Pydantic Logfire / Arize Phoenix - UI трассировки поверх собственного audit log
NEED: (a) Наблюдаемость агентных шагов; не заменяет собственный доказательный журнал
KIND: open-source / SaaS
URL: https://langfuse.com/self-hosting
LICENSE: Langfuse: MIT вне каталогов ee/ (copyright ClickHouse, Inc.); Logfire SDK: MIT, backend - SaaS; Phoenix: Elastic License 2.0
COMMERCIAL USE: Langfuse и Logfire SDK - да. Phoenix (ELv2) нельзя предоставлять третьим лицам как hosted/managed service - для внутреннего использования допустимо.
PROJECT STATE: Langfuse v4.58.0 (2026-10-13), 35 778 звёзд. Logfire v5.2.0 (2026-10-13), 4 511 звёзд. Phoenix arize-phoenix-v20.21.2 (2026-10-13), 11 822 звезды.
CLAIMED VS ACTUAL: Langfuse self-host - это 2 контейнера приложения + PostgreSQL + ClickHouse + Redis/Valkey + S3-хранилище; Docker Compose заявлен только для «local use and testing», production - Kubernetes/облака. Для одного скромного сервера это
тяжело.
INFRA: Langfuse: Postgres + ClickHouse + Redis + S3. Phoenix: один контейнер (не проверено по docs).
PRICING/LIMITS: Не проверялись.
RISKS: Отправка данных расследований во внешний SaaS требует решения владельца; ни один инструмент не является доказательным журналом с привязкой к TXID.
REPLACEABILITY: Высокая (OTel-экспорт).
HOW VERIFIED: gh api (metadata, тексты LICENSE); docs langfuse.com/self-hosting.
CONFIDENCE: medium
EVIDENCE: https://github.com/langfuse/langfuse | https://langfuse.com/self-hosting | https://github.com/pydantic/logfire | https://github.com/Arize-ai/phoenix

### [RECOMMENDED] In-process типизированные function tools (собственный реестр инструментов поверх HTTP-клиентов)
NEED: (b) Основной механизм подключения блокчейн-эксплореров, аналитических API и внутренних инструментов
KIND: собственный код-клей + возможности Pydantic AI (function tools, toolsets)
URL: https://github.com/pydantic/pydantic-ai/tree/main/pydantic_ai_slim/pydantic_ai/toolsets
LICENSE: Не применимо (свой код); Pydantic AI - MIT
COMMERCIAL USE: Да; ограничения задаются только условиями самих API-провайдеров (зона другого аудита).
PROJECT STATE: Паттерн, а не продукт. Поддержка в Pydantic AI подтверждена листингом toolsets/ (function.py, filtered.py, approval_required.py, prefixed.py).
CLAIMED VS ACTUAL: none found
CAPABILITIES: Полный контроль над HTTP: ключи в заголовках в последний момент, собственные retry/backoff, очереди с rate limit по провайдеру, сохранение сырого ответа (sha256, URL без секретов, fetched_at) как доказательства и fixture для
replay; типизированные входы и выходы; узкий список инструментов на роль агента (экономия токенов).
INFRA: Нет дополнительной инфраструктуры.
PRICING/LIMITS: $0. Live-проба: keyless GET https://api.trongrid.io/v1/accounts/{addr}/transactions/trc20?limit=20 вернул HTTP 200 за 0.49 с (7 957 байт). Keyless GET к apilist.tronscanapi.com вернул HTTP 429: «request rate exceeded the
allowed_rps(3), and the query server is suspended for 57 s» - подтверждает необходимость собственных очередей с лимитами.
RISKS: Клиенты под каждый API пишутся и поддерживаются самостоятельно (10-15 эндпоинтов на MVP); нет автоматического обнаружения новых инструментов - для доказательной платформы это достоинство.
REPLACEABILITY: Высокая: любой инструмент можно дополнительно выставить через MCP или описать OpenAPI без изменения ядра.
HOW VERIFIED: Live keyless GET (2 запроса); чтение листинга toolsets Pydantic AI; сопоставление с аудитом MCP-серверов ниже.
CONFIDENCE: high
EVIDENCE: https://github.com/pydantic/pydantic-ai/tree/main/pydantic_ai_slim/pydantic_ai/toolsets | https://api.trongrid.io

### [ALTERNATIVE] Model Context Protocol (спецификация 2026-07-28 и официальные SDK)
NEED: (b) Стандарт подключения внешних инструментов; уместен на границе системы
KIND: standard + open-source SDK
URL: https://modelcontextprotocol.io/specification/latest
LICENSE: Проект переходит с MIT на Apache-2.0 (текст LICENSE: новые вклады - Apache-2.0, часть старых остаётся под MIT); python-sdk: MIT по SPDX
COMMERCIAL USE: Да.
PROJECT STATE: Текущая стабильная ревизия спецификации - 2026-07-28 (предыдущие: 2025-11-25, 2025-06-18, 2025-03-26, 2024-11-05). python-sdk v2.3.0 (2026-10-02), v2.0.0 вышел 2026-07-28, ветка v1.x - maintenance mode (только security); 24 566
звёзд. typescript-sdk v2.3.1 (2026-10-05). servers v1.0.0 (2026-10-11), registry v1.8.1, inspector 2.10.1.
CLAIMED VS ACTUAL: (1) Ревизия 2026-07-28 - масштабная ломающая переделка: убраны сессии и Mcp-Session-Id, убран handshake initialize, удалены ping и logging/setLevel, Tasks вынесены из ядра в расширение, Sampling/Roots/Logging и Dynamic Client
Registration объявлены deprecated, HTTP+SSE deprecated, убрана resumability SSE-потоков. (2) Протокол сам признаёт, что не может обеспечить безопасность на своём уровне («MCP itself cannot enforce these security principles at the
protocol level»); описания инструментов следует считать недоверенными. (3) В официальном security best practices нет раздела про tool poisoning и prompt injection через результаты инструментов - они описаны внешними исследованиями
(Invariant Labs, CyberArk, CSA) и OWASP MCP Top 10 (beta: MCP03 Tool Poisoning, MCP06 Prompt Injection via Contextual Payloads). (4) У python-sdk 12 опубликованных advisories, 9 из них high; 9 опубликованы в 2026 году (например,
CVE-2026-52869, CVE-2026-52870, CVE-2026-59950, CVE-2026-59951). (5) Проверенные через NVD связанные CVE: CVE-2025-6514 mcp-remote, CVSS 9.6; CVE-2025-49596 MCP Inspector, 9.4; CVE-2025-54136 Cursor, 7.2 по NVD.
CAPABILITIES: Tools/resources/prompts поверх JSON-RPC; transports stdio и Streamable HTTP; OAuth 2.1 с resource indicators, проверкой iss (RFC 9207), Client ID Metadata Documents; расширения Tasks, MCP Apps; OTel trace context в _meta; python-
sdk v2 обслуживает и старые ревизии.
INFRA: MCP-клиент в процессе; для удалённых серверов - исходящий HTTPS и OAuth/ключи.
PRICING/LIMITS: $0.
RISKS: Быстрый дрейф протокола (две крупные ревизии за 8 месяцев); доверие к серверу наследуется без непрерывной проверки (rug pull через изменение описаний); большие списки инструментов съедают контекст и бюджет; результаты инструментов
- канал prompt injection.
REPLACEABILITY: Высокая, если MCP остаётся адаптером на границе, а не ядром.
HOW VERIFIED: Чтение спецификации и changelog на modelcontextprotocol.io; gh api (releases, release notes v2.0.0, security-advisories, LICENSE); NVD API (3 CVE); owasp.org; веб-поиск по tool poisoning (вторичные источники).
CONFIDENCE: high
EVIDENCE: https://modelcontextprotocol.io/specification/latest | https://modelcontextprotocol.io/specification/2026-07-28/changelog | https://modelcontextprotocol.io/specification/2026-07-28/basic/security_best_practices | https://github.com/modelcontextprotocol/python-sdk/releases/tag/v2.0.0 | https://github.com/modelcontextprotocol/python-sdk/security/advisories | https://owasp.org/www-project-mcp-top-10/

### [ALTERNATIVE] FastMCP (PrefectHQ)
NEED: (b) Библиотека для публикации собственного MCP-сервера платформы (поздний этап) и MCP-клиент
KIND: open-source library
URL: https://github.com/PrefectHQ/fastmcp
LICENSE: Apache-2.0
COMMERCIAL USE: Да (Apache-2.0).
PROJECT STATE: v4.1.0 (2026-10-08), 28 067 звёзд, 497 open issues, 23 CI workflows; v4.0.0 вышел 2026-08-31, ветка 3.x ещё патчится (v3.4.8 от 2026-10-04). Репозиторий jlowin/fastmcp редиректит на PrefectHQ/fastmcp.
CLAIMED VS ACTUAL: 8 опубликованных advisories, включая CVE-2026-32871 (SSRF и path traversal в OpenAPI Provider, high), CVE-2026-27124 (confused deputy в OAuth Proxy, high), CVE-2025-69196 (переиспользование токенов между серверами). Автогенерация
инструментов из OpenAPI и OAuth-прокси - именно те функции, где находили уязвимости.
PRICING/LIMITS: $0.
RISKS: Мажор 4.0 полтора месяца назад; поверхность атаки OAuth-прокси и OpenAPI-провайдера.
REPLACEABILITY: Высокая (официальный mcp SDK v2 даёт MCPServer с тем же декораторным API).
HOW VERIFIED: gh api (metadata, releases, security-advisories).
CONFIDENCE: medium
EVIDENCE: https://github.com/PrefectHQ/fastmcp | https://github.com/PrefectHQ/fastmcp/security/advisories

### [REJECTED] TronGrid MCP Server (официальный hosted, mcp.trongrid.io)
NEED: (b) Готовый MCP-доступ к данным TRON
KIND: public hosted MCP service (закрытый код)
URL: https://developers.tron.network/docs/mcp
LICENSE: Не указана; условия использования на странице docs не приведены
COMMERCIAL USE: Не подтверждено: на странице документации условий нет.
PROJECT STATE: Страница docs обновлена 2026-10-12. Endpoint https://mcp.trongrid.io/mcp, Streamable HTTP, протокол 2025-11-25 (не текущая ревизия 2026-07-28). Live GET вернул HTTP 405 с JSON в стиле Spring Boot - сервис жив и принимает только
POST.
CLAIMED VS ACTUAL: (1) Сервер не read-only: включает broadcastTransaction, broadcastHex, createTransaction, triggerSmartContract, deployContract, freezeBalanceV2, proposalCreate. Ключи он не хранит (транслирует подписанные клиентом транзакции), но
для платформы расследований write-поверхность недопустима без allowlist. (2) Числовые лимиты запросов не опубликованы. (3) Для Claude Desktop docs рекомендуют обёртку npx mcp-remote - пакет, имевший CVE-2025-6514 (CVSS 9.6). (4)
149 описаний инструментов в контексте LLM несовместимы с бюджетом $1 на расследование. (5) Данные те же, что в REST API TronGrid, - новых сведений сервер не добавляет.
CAPABILITIES: 149 инструментов: 18 TronGrid API query, 73 wallet operation, 25 WalletSolidity read-only, 33 JSON-RPC.
INFRA: Исходящий HTTPS.
PRICING/LIMITS: Опциональный заголовок TRON-PRO-API-KEY; лимиты не опубликованы.
RISKS: Дополнительный посредник между фактом и первичным источником; закрытый код; изменяемый список инструментов (rug pull); write-инструменты; нет SLA.
REPLACEABILITY: Полная: прямые вызовы REST TronGrid.
HOW VERIFIED: Чтение docs developers.tron.network/docs/mcp и /docs/mcp-servers-on-tron; live keyless GET (405). tools/list не вызывался (POST вне разрешённых правил аудита).
CONFIDENCE: medium
EVIDENCE: https://developers.tron.network/docs/mcp | https://developers.tron.network/docs/mcp-servers-on-tron | https://mcp.trongrid.io/mcp

### [NEEDS-TRIAL] TronScan MCP Server (официальный hosted, mcp.tronscan.org)
NEED: (b) Read-only MCP-доступ к индексированным данным TronScan
KIND: public hosted MCP service (закрытый код)
URL: https://mcpdoc.tronscan.org/en
LICENSE: Не указана
COMMERCIAL USE: Не подтверждено (документация mcpdoc.tronscan.org и support.tronscan.org вернули HTTP 403 на автоматическое чтение).
PROJECT STATE: Endpoint https://mcp.tronscan.org/mcp; live GET вернул HTTP 405 - сервис жив. По странице TRON Developer Hub (обновлена 2026-08-18): «100+ endpoints», tool surface read-only. По поисковому сниппету: 119 инструментов, протокол
2025-06-18. Есть репозиторий tronscan-support/skills (MIT, 0 звёзд, 2026-04-27).
CLAIMED VS ACTUAL: Анонс запуска называл 105 инструментов, текущая документация по сниппету - 119: список инструментов меняется без версионирования, что и есть сценарий rug pull. Протокол отстаёт на две ревизии. Данные те же, что в REST API TronScan
(включая теги адресов), но без контроля над сырым ответом.
INFRA: Исходящий HTTPS.
PRICING/LIMITS: Без ключа запросы ограничиваются; с ключом - заголовок TRON-PRO-API-KEY. Числа не подтверждены. Для REST TronScan live-проба показала лимит 3 rps без ключа и блокировку на 57 с.
RISKS: Закрытый код, 100+ инструментов в контексте, пользовательские теги адресов как канал prompt injection, отсутствие условий использования в доступном виде.
REPLACEABILITY: Полная: прямые вызовы REST TronScan.
HOW VERIFIED: Live keyless GET (405); чтение developers.tron.network/docs/mcp-servers-on-tron; число инструментов и версия протокола - только поисковый сниппет.
CONFIDENCE: low
EVIDENCE: https://mcp.tronscan.org/mcp | https://mcpdoc.tronscan.org/en | https://developers.tron.network/docs/mcp-servers-on-tron | https://github.com/tronscan-support/skills

### [REJECTED] Сторонние TRON MCP-серверы: BofAI/mcp-server-tron, TronLink/mcp-server-tronlink, fbsobreira/gotron-mcp, Hovsteder/merx-mcp
NEED: (b) Community MCP-серверы для TRON
KIND: open-source MCP servers
URL: https://github.com/BofAI/mcp-server-tron
LICENSE: BofAI: MIT; TronLink: MIT; gotron-mcp: LGPL-3.0; merx-mcp: MIT
COMMERCIAL USE: MIT - да; LGPL-3.0 - с условиями (допустимо как отдельный процесс).
PROJECT STATE: BofAI: 24 звезды, 96 коммитов за 2026-01-22..2026-03-30, с тех пор без активности, есть tests/ и vitest. TronLink: 14 звёзд, 9 коммитов, последний 2026-03-29. gotron-mcp: 4 звезды, один автор, активен (коммит 2026-10-13), есть
SECURITY.md и policy.yaml. merx-mcp: 3 звезды, последний push 2026-04-08.
CLAIMED VS ACTUAL: BofAI: (1) при отсутствии TRONGRID_API_KEY сервер по умолчанию ходит через сторонний RPC-хост hptg.bankofai.io - данные идут не из первичного источника; (2) это кошелёк-сервер с write-инструментами (переводы, staking, governance),
read-only только флагом --readonly; (3) застой с марта 2026. TronLink - сервер подписи транзакций, для расследований не нужен. merx-mcp - торговля energy и отправка USDT.
PRICING/LIMITS: $0.
RISKS: Единичные мейнтейнеры, минимальное число звёзд, кошельковая функциональность рядом с данными расследований, сторонние RPC-прокси.
REPLACEABILITY: Полная.
HOW VERIFIED: gh api (metadata, дерево файлов, README BofAI, история коммитов).
CONFIDENCE: high
EVIDENCE: https://github.com/BofAI/mcp-server-tron | https://github.com/TronLink/mcp-server-tronlink | https://github.com/fbsobreira/gotron-mcp | https://github.com/Hovsteder/merx-mcp

### [REJECTED] slowmist/MistTrackMCP
NEED: (b) MCP-обёртка над MistTrack OpenAPI (риск-скоринг, метки, трассировка)
KIND: open-source MCP server (npm-пакет misttrack)
URL: https://github.com/slowmist/MistTrackMCP
LICENSE: Файла LICENSE в репозитории нет (GitHub: NONE); в package.json указано ISC - противоречие
COMMERCIAL USE: Юридически не определено из-за отсутствия файла лицензии; сам MistTrack API требует платного плана с доступом к OpenAPI.
PROJECT STATE: 39 звёзд, всего 4 коммита одного автора (2025-05-07..2026-04-28), 1 open issue, CI нет, тестов нет (scripts.test = «no test specified»), package version 1.1.0, зависимость @modelcontextprotocol/sdk ^1.11.0 (SDK v1, maintenance).
CLAIMED VS ACTUAL: (1) API-ключ передаётся как query-параметр api_key в URL (misttrackClient.ts) - попадает в HTTP-логи и трассировки; дополнительно CLI принимает ключ аргументом --key, видимым в списке процессов. (2) Сервер намеренно встраивает в
выдачу инструкции для модели (summaryPrompts.ts на 20 KB, каталог prompts/ с «recursiveTransactionAnalysisPrompt» и др.) - результаты инструментов управляют поведением агента, что противоречит правилу «tool result = данные». (3)
Дефолтный лимит 1 запрос/с. (4) Нет лицензии, тестов и CI при бренде SlowMist.
PRICING/LIMITS: Сервер $0; требуется платный план MistTrack с OpenAPI (цены - вне этого аудита).
RISKS: Утечка ключа через URL; инъекция инструкций в контекст; заброшенность; юридическая неопределённость лицензии.
REPLACEABILITY: Полная: прямой типизированный клиент к openapi.misttrack.io с ключом вне логов.
HOW VERIFIED: gh api: дерево файлов, package.json, README, чтение src/utils/misttrackClient.ts и src/tools/summaryPrompts.ts.
CONFIDENCE: high
EVIDENCE: https://github.com/slowmist/MistTrackMCP | https://github.com/slowmist/MistTrackMCP/blob/main/src/utils/misttrackClient.ts | https://github.com/slowmist/MistTrackMCP/blob/main/src/tools/summaryPrompts.ts

### [REJECTED] Bitquery MCP Server (официальный hosted, mcp.bitquery.io)
NEED: (b) MCP-доступ к Bitquery: трассировка переводов на 19 сетях включая Tron, address_labels
KIND: commercial hosted MCP service (закрытый код)
URL: https://github.com/bitquery/mcp
LICENSE: Проприетарный сервис; репозиторий bitquery/mcp без лицензии содержит только конфиги и README
COMMERCIAL USE: Определяется условиями Bitquery (не проверялись в этом аудите).
PROJECT STATE: Репозиторий создан 2026-09-21, 12 коммитов, 0 звёзд, README обновлён 2026-10-02. Сервис очень новый (менее месяца).
CLAIMED VS ACTUAL: Аутентификация только через OAuth 2.1 с интерактивным входом в браузере («No API key to paste») - рассчитано на чат-клиентов, а не на серверный backend. Кода сервера нет - аудит качества невозможен. README сам показывает
отставание данных на 14 минут в примере.
CAPABILITIES: Инструменты и guided prompts money_flow, risk_screen, address_report, address_labels, btc_related_addresses, execute_sql (платные планы); Streamable HTTP.
PRICING/LIMITS: Не проверялись; execute_sql - только платные планы.
RISKS: Закрытый hosted-сервис с guided prompts (инструкции в контексте), интерактивный OAuth, возраст менее месяца.
REPLACEABILITY: Полная: прямой GraphQL/REST API Bitquery с API-ключом.
HOW VERIFIED: gh api (metadata, README).
CONFIDENCE: medium
EVIDENCE: https://github.com/bitquery/mcp

### [ALTERNATIVE] Dune MCP (официальный remote, api.dune.com/mcp/v1)
NEED: (b) MCP-доступ к Dune для расширения на EVM-сети
KIND: commercial hosted MCP service
URL: https://docs.dune.com/api-reference/agents/mcp
LICENSE: Проприетарный сервис
COMMERCIAL USE: Определяется условиями Dune (не проверялись).
PROJECT STATE: Официальная страница docs.dune.com/api-reference/agents/mcp; дата страницы не указана. Community-серверы (kukapay/dune-analytics-mcp, 41 звезда, последний push 2025-05-04 и др.) заброшены.
CLAIMED VS ACTUAL: Docs допускают передачу ключа как query-параметр api_key - этого варианта надо избегать. Покрытие TRON на странице не указано. Большинство инструментов - создание и изменение запросов и дашбордов, т.е. write-операции в аккаунте
Dune.
CAPABILITIES: 26 инструментов: discovery (searchTables, listBlockchains...), жизненный цикл запросов, materialized views, визуализации, дашборды, getUsage. Auth: OAuth 2.0 или API-ключ в заголовке x-dune-api-key.
PRICING/LIMITS: Исполнение запросов расходует credits; тарифы не проверялись.
RISKS: Для MVP на TRON не нужен; write-инструменты; расход credits под управлением LLM.
REPLACEABILITY: Полная: Dune REST API.
HOW VERIFIED: Чтение официальной docs-страницы; gh search по community-серверам.
CONFIDENCE: medium
EVIDENCE: https://docs.dune.com/api-reference/agents/mcp | https://github.com/kukapay/dune-analytics-mcp

### [REJECTED] blockscout/mcp-server
NEED: (b) MCP-сервер для EVM-эксплореров Blockscout (расширение на Ethereum/BSC)
KIND: source-available MCP server (+ hosted)
URL: https://github.com/blockscout/mcp-server
LICENSE: LicenseRef-Blockscout, версия 1.0, действует с 2026-05-15 (не OSI)
COMMERCIAL USE: Нет без отдельной Commercial Licence: раздел 4.a запрещает коммерческое и монетизируемое использование, включая SaaS и managed-сервисы.
PROJECT STATE: v0.19.0 (2026-09-08), 46 звёзд, 15 open issues, 5 CI workflows.
CLAIMED VS ACTUAL: В каталогах MCP-серверов всё ещё описывается как open-source; фактически с мая 2026 действует ограничительная собственная лицензия, несовместимая с коммерческой SaaS-платформой.
PRICING/LIMITS: Commercial Licence - по запросу.
RISKS: Лицензионный блокер.
REPLACEABILITY: Полная: REST API Blockscout/Etherscan напрямую.
HOW VERIFIED: gh api (metadata, чтение текста LICENSE, releases).
CONFIDENCE: high
EVIDENCE: https://github.com/blockscout/mcp-server | https://github.com/blockscout/mcp-server/blob/main/LICENSE

### [REJECTED] MCP-серверы Arkham / Chainalysis / TRM / Elliptic
NEED: (b) MCP-доступ к коммерческим источникам атрибуции
KIND: community MCP servers (официальных не найдено)
URL: https://github.com/ibash2/arkham-mcp
LICENSE: ibash2/arkham-mcp - без лицензии; fikriaf/Arkham-MCP - MIT; srotzin/hive-mcp-agent-kyc - MIT
COMMERCIAL USE: Не применимо: зависит от договора с вендором данных.
PROJECT STATE: Официальных MCP-серверов Arkham, Chainalysis, TRM Labs и Elliptic поиском не найдено. Community: ibash2/arkham-mcp (1 звезда, 2026-05-24), fikriaf/Arkham-MCP (0 звёзд, 2026-03-07), srotzin/hive-mcp-agent-kyc (0 звёзд) - брокер-
обёртка над Chainalysis/TRM/Elliptic.
CLAIMED VS ACTUAL: Репозитории с названиями вендоров - любительские обёртки с 0-1 звездой, без гарантий корректности атрибуции. Отсутствие официальных серверов поиском не доказано.
PRICING/LIMITS: Не применимо.
RISKS: Нулевая доверенность кода; метки бирж требуют источника с проверяемым происхождением.
REPLACEABILITY: Полная: официальные REST API вендоров по договору.
HOW VERIFIED: gh search (repositories), веб-поиск. Код не читался.
CONFIDENCE: low
EVIDENCE: https://github.com/ibash2/arkham-mcp | https://github.com/fikriaf/Arkham-MCP | https://github.com/srotzin/hive-mcp-agent-kyc

### [ALTERNATIVE] OSINT / web-search MCP-серверы: Tavily, Brave Search, Exa, Firecrawl
NEED: (b) Веб-поиск и извлечение страниц для OSINT-агента
KIND: open-source MCP-обёртки над коммерческими API
URL: https://github.com/brave/brave-search-mcp-server
LICENSE: Все четыре - MIT
COMMERCIAL USE: Обёртки - да; сами API - по тарифам вендоров (вне этого аудита).
PROJECT STATE: tavily-ai/tavily-mcp: 2 429 звёзд, последний коммит 2026-09-16, без релизов и CI workflows. brave/brave-search-mcp-server: v2.1.4 (2026-09-17), 1 497 звёзд. exa-labs/exa-mcp-server: 5 120 звёзд, коммит 2026-10-07.
firecrawl/firecrawl-mcp-server: 7 596 звёзд, последний релиз v3.2.1 от 2025-09-26 при активных коммитах.
CLAIMED VS ACTUAL: Все - тонкие обёртки над REST API того же вендора; результаты поиска и содержимое страниц - самый прямой канал prompt injection в систему.
PRICING/LIMITS: Не проверялись.
RISKS: Недоверенный контент из интернета попадает в контекст; у части репозиториев нет релизов и CI.
REPLACEABILITY: Полная: REST API вендоров через собственный tool с санитизацией.
HOW VERIFIED: gh api (metadata, releases). Код не читался.
CONFIDENCE: medium
EVIDENCE: https://github.com/tavily-ai/tavily-mcp | https://github.com/brave/brave-search-mcp-server | https://github.com/exa-labs/exa-mcp-server | https://github.com/firecrawl/firecrawl-mcp-server

### [ALTERNATIVE] Инструменты, автогенерируемые из OpenAPI-описаний
NEED: (b) Подключение REST API через спецификацию без ручных клиентов
KIND: паттерн / функции библиотек (например, OpenAPI provider в FastMCP)
URL: https://github.com/PrefectHQ/fastmcp/security/advisories
LICENSE: Зависит от библиотеки (FastMCP - Apache-2.0)
COMMERCIAL USE: Да.
PROJECT STATE: Паттерн. В FastMCP OpenAPI Provider была уязвимость CVE-2026-32871 (SSRF и path traversal, high, опубликована 2026-03-31).
CLAIMED VS ACTUAL: Автогенерация превращает каждый эндпоинт в отдельный инструмент: десятки-сотни инструментов с описаниями, не рассчитанными на LLM, - рост стоимости контекста и ошибок выбора. Наличие официальных OpenAPI-спецификаций у TronGrid и
TronScan не проверялось.
PRICING/LIMITS: $0.
RISKS: Нет контроля над сохранением сырых ответов и секретами; SSRF-класс уязвимостей в генераторах; раздувание контекста.
REPLACEABILITY: Высокая.
HOW VERIFIED: gh api (security advisories FastMCP). Практическая генерация не выполнялась.
CONFIDENCE: low
EVIDENCE: https://github.com/PrefectHQ/fastmcp/security/advisories

## OPEN QUESTIONS FOR OWNER (researcher)
- Подтверждаете ли Python как основной язык backend и оркестрации (рекомендация исходит из этого; Mastra и Vercel AI SDK отклонены в том числе как TypeScript-only)?
- Каких LLM-провайдеров разрешено использовать и можно ли передавать им адреса, TXID и материалы дела (юрисдикция, условия обработки данных)? От этого зависит набор моделей и нужен ли локальный fallback.
- Подтверждаете ли Postgres как единую БД платформы (он же будет system database для DBOS)?
- Семантика бюджетного лимита: жёсткая остановка с частичным отчётом или пауза с запросом у пользователя на повышение лимита? Кто вправе повышать лимит - пользователь или оператор?
- Какие действия считаются чувствительными и требуют approval человека: только отправка запросов биржам, Tether и правоохранителям, или также платные API-вызовы выше порога и OSINT по персональным данным? Кто одобряет - сам
пользователь или внутренний аналитик?
- Допустимо ли отправлять трассы агентных шагов во внешний SaaS наблюдаемости (Logfire, Langfuse Cloud) или только self-hosted? Self-hosted Langfuse требует Postgres + ClickHouse + Redis + S3.
- Планируется ли выставлять платформу наружу как MCP-сервер для агентов клиентов (платный тариф)? Это влияет на то, закладывать ли MCP-слой сразу.
- Нужна ли возможность ручного исследовательского доступа аналитиков через сторонние MCP-серверы (например, TronScan MCP в dev-среде), или это запрещается политикой полностью?
- Готовы ли выделить 2-3 дня на spike (crash/resume, лимиты очередей, накладные расходы чекпоинтов на 1 000 адресов) до окончательной фиксации связки DBOS + Pydantic AI?
- Приемлем ли при росте переход на платный managed-оркестратор (Temporal Cloud от $50 за 1M actions или DBOS Conductor от $99/мес)?

## NOT VERIFIED (researcher)
- Ни один фреймворк не устанавливался и не запускался (правила аудита): работа DBOS и Pydantic AI на Windows 11 / Python 3.13, реальное поведение recovery, накладные расходы чекпоинта и достижимость цели «1 000 адресов за 5 минут»
не измерены.
- Совместимость extras pydantic-ai[dbos] с DBOS 3.x: в pyproject указано dbos>=2.10.0 без верхней границы, фактическая работа с 3.2.0 не проверена.
- Природа зависимости httpx2>=2.7 в pydantic-ai-slim не исследовалась.
- TronScan MCP: число инструментов (119), версия протокола (2025-06-18) и лимиты - только по поисковому сниппету; mcpdoc.tronscan.org и support.tronscan.org вернули HTTP 403 на автоматическое чтение. Условия использования обоих
официальных TRON MCP-серверов не найдены.
- tools/list официальных MCP-серверов TronGrid и TronScan не вызывался (нужен POST, а правила разрешают только keyless GET), поэтому описания инструментов не проверены на tool poisoning, а заявленные количества инструментов не
подтверждены вживую.
- Существование официальных MCP-серверов Arkham, Chainalysis, TRM Labs, Elliptic: поиском не найдено, но отсутствие не доказано; документация Arkham API не получена (цепочка редиректов).
- Детали официального Etherscan MCP (endpoint, auth, лимиты) не получены; покрытие TRON в Dune MCP не подтверждено.
- Цены и лимиты Restate Cloud, Hatchet Cloud, Inngest, Langfuse Cloud, Logfire, API поисковых вендоров (Tavily, Brave, Exa, Firecrawl) не проверялись.
- Инцидент LiteLLM (версии 1.82.7 и 1.82.8, 2026-03-24) подтверждён только вторичными источниками; официальный postmortem и advisory не читались. Затронутость CrewAI и DSPy - по вторичному источнику.
- Статистика успешности tool poisoning (MCPTox: 36.5% против «более 60%» и 72.8% в разных источниках) противоречива и по первоисточнику не проверена. Оценка CVE-2025-54136: NVD API дал 7.2, заметка CSA приводит 8.8.
- Страница docs LangGraph durable-execution через WebFetch вернула содержимое о persistence; детали durable execution подтверждены только по types.py и release-заметкам из поиска.
- Функциональность Mastra, Vercel AI SDK, Agno, Strands, Burr, Haystack, Prefect, DSPy, smolagents, Hatchet, Restate, Inngest оценена по metadata, лицензиям и релизам; их docs и код глубоко не читались.
- Модель-агностичность Claude Agent SDK (поддержка Bedrock/Vertex/сторонних шлюзов) и место хранения сессий в этом аудите не проверялись; вывод «только Claude» основан на том, что SDK запускает бинарь Claude Code.
- Наличие официальных OpenAPI-спецификаций у TronGrid и TronScan не проверялось.
- Персистентность resumability в Google ADK через DatabaseSessionService и статус функции (experimental/GA) на странице не указаны.
- Лицензия кода microsoft/autogen: GitHub API сообщает CC-BY-4.0 на уровне репозитория, раздельные лицензии кода и документации не проверялись.
- Оценки трудозатрат, числа LLM-вызовов на расследование и экономии токенов - допущения аудитора, не измерения.
- Найденные в поиске, но не аудированные репозитории: bakulbadwal/tracehound (агентный трассировщик с evals как read-only MCP, 1 звезда), traql/mcp-server (AML-скоринг для TRON и др., 0 звёзд), osintph/falconeye (OSINT-toolkit,
AGPL-3.0), CryptoAPIs-io/cryptoapis-mcp-aml. Поиск по GoPlus, Nansen, Chainbase MCP не выполнен из-за лимита GitHub Search API.