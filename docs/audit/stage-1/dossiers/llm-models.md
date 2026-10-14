# AREA llm-models: Language models with tool calling and structured outputs, gateways, LLM observability and evals

============================================================
PART 1 - VERIFIER REPORT (takes precedence over the researcher wherever they disagree)
============================================================

## VERIFIER SUMMARY
Перепроверено 26 утверждений по первичным источникам (официальные страницы Anthropic, OpenAI, Google, DeepSeek, Mistral, xAI, Langfuse, LangChain; LICENSE и исходники через gh api; живые keyless-запросы к OpenRouter). Фактическая
база аудита оказалась добротной: 22 утверждения подтверждены полностью, включая все цены и лимиты Anthropic и OpenAI, лицензии, статусы Portkey, Helicone, promptfoo и арифметику модели стоимости ($0.40 типично, $0.57 тяжёлый
случай — пересчитано, сходится). Найденные ошибки и неточности: - Опровергнуто: Haiku 5.5 и GPT-6 Luna не являются самыми дешёвыми моделями с vision + structured outputs + 1M context — в живом каталоге есть дешевле (gpt-4.1-nano и
gemini-2.5-flash-lite $0.10/$0.40, qwen3.5-flash $0.065/$0.26 и другие). На бюджет это не влияет: 84% стоимости дают 8 вызовов Sonnet. - Исправлено: у LiteLLM в 2026 году не два, а четыре critical advisory (всего 17, из них шесть
high). - Исправлено: 'молчаливое отбрасывание output_config' в LiteLLM происходит только при drop_params=True, с warning, и не касается Haiku 5.5 / Sonnet 5.5. - Не удалось проверить: OpenAI Services Agreement (403 при двух
способах доступа). Все пять рекомендаций устояли, но каждая требует доработки: - Модели: Anthropic как primary оправдан, однако аудит не разобрал Usage Policy (ограничения на деанонимизацию людей и сбор профилей — зона OSINT-
агента) и недооценил refusal-риск (у Haiku 5.5 нет server-side fallback, у Sonnet 5.5 он не покрывает general_harms). Strong-tier стоит сделать конфигурируемым: Haiku 5.5 с effort high, Mistral Large 4 или Grok 4.3 снижают
стоимость расследования до $0.08-0.21. - Gateway: решение без gateway верно; оценка объёма glue-кода занижена. - Observability: Langfuse self-host противоречит ограничению 'один скромный сервер'; Phoenix отклонён по слабому
основанию (ELv2 не мешает внутреннему использованию, архитектура — одно приложение с SQLite/PostgreSQL), MLflow не рассмотрен. - Evals: Inspect AI подходит, но не тестируется на Windows и Python 3.13 и требует нескольких epochs
из-за отсутствия temperature. - Воспроизводимость: подход через журнал верен; нужно учесть привязку thinking-блоков к аккаунту и append-only историю для новых аккаунтов. Пропущенные кандидаты: xAI Grok 4.3/4.7, Meta Muse Spark
1.3, маршрут Claude через Vertex AI EU, MLflow 3.x, Pydantic Logfire, Bifrost, any-llm, Instructor; TensorZero — archived. Главные блокирующие риски: соответствие Usage Policy, частота refusal на материалах о мошенничестве,
неизмеренная латентность против цели 2 минуты, непроверенный договор fallback-провайдера и передача данных жертв третьим лицам. Реальные вызовы моделей не выполнялись (ключи запрещены правилами), поэтому надёжность tool calling,
латентность и фактический расход токенов остаются непроверенными. Сырые ответы проб сохранены в scratchpad сессии: C:\Users\Asus\AppData\Local\Temp\claude\C--LEDGERHUNT-CRYPTO\912b2cf7-a304-454a-a85d-20eefb54cc33\scratchpad
(or_models.json, or_zdr.json, or_haiku_ep.json, litellm_tr.py, litellm_prices.json).

## BLOCKING RISKS
- Usage Policy Anthropic не проанализирована, а она прямо касается продукта. На странице anthropic.com/legal/aup (версия помечена 'Effective November 12, 2026', то есть вступает в силу через месяц) в разделе о surveillance запрещено
'identify, unmask, or locate' людей по анонимной или псевдонимной активности с целью harass, intimidate, surveil или cause harm; в разделе privacy — собирать и обогащать персональные данные из нескольких источников в профили для
раскрытия третьим лицам без ведома человека; отдельно — 'make or suggest decisions' в law enforcement. Исключения есть для fraud detection / AML screening по согласию, журналистики и legal research правоохранительных органов;
исключения для частных расследователей или потерпевших нет. OSINT-агент, атрибуция владельцев адресов и отчёт для бирж и полиции попадают в серую зону. Текст получен через WebFetch с извлечением коротких цитат — нужен юридический
разбор полного текста до выбора primary-провайдера; аналогичные политики OpenAI не читались.
- Refusal от safety classifiers на материалах о краже, фишинге, drainer-контрактах и отмывании. Подтверждено документацией: Haiku 5.5 не имеет server-side fallback; у Sonnet 5.5 fallback (beta, только Claude API) повторяет лишь
категории cyber и frontier_llm на Claude Sonnet 5, а general_harms не повторяется и, по словам документации, может срабатывать на добросовестной работе; refusal возвращается с HTTP 200 и тарифицируется. Частота не измерена (вызовы
API запрещены правилами аудита). До запуска — пилот на 50 сценариях и заявка в Cyber Verification Program.
- Цель 'первый отчёт <= 2 минут' и 'простая транзакция <= 30 с' не подтверждена ничем: скорость генерации Haiku 5.5 и Sonnet 5.5 не измерена, в API OpenRouter поля latency_last_30m и throughput_last_30m для Haiku 5.5 пусты. Один
вызов Sonnet 5.5 с effort high и отчётом на несколько тысяч токенов плюс первая компиляция грамматик схем (таймаут компиляции до 180 с) могут сами занять больше минуты.
- Fallback-провайдер юридически и технически не закрыт: OpenAI Services Agreement недоступен (403 при WebFetch и curl), права на коммерческое использование по договору не подтверждены; function calling с reasoning у gpt-6-luna
работает только через Responses API; датированных snapshot ID на странице модели нет; при переключении провайдера thinking-блоки теряются, а данные жертв уходят второму обработчику.
- Данные жертв (скриншоты, переписка) передаются третьим лицам в США: ZDR у Anthropic — только через sales и на организацию; Batch хранится 29 дней, flagged-контент — до 2 лет даже при ZDR; маршрут через Amazon Bedrock лишает Haiku
5.5 structured outputs. Требования GDPR и локализации владельцем не определены.
- Ограничения новой организации Anthropic: возможен старт в Evaluation tier с лимитами ниже опубликованных (числа не раскрыты), месячный cap Start tier $500 с жёстким 429 до конца месяца; для аккаунтов, созданных после 2026-08-31,
принудительно действует проверка preserved thinking — изменение system, tools или прошлых сообщений при возврате thinking-блоков даёт 400, поэтому harness агентов обязан быть append-only с первого дня.
- Langfuse self-host не помещается в ограничение 'один скромный сервер' (минимум 4 ядра / 16 GiB / 100 GiB, 6 контейнеров, compose без HA и бэкапов), а Langfuse Cloud означает вынос трасс расследований наружу. Решение по
observability нельзя принять без ответа владельца о размещении данных.
- Все объёмы токенов в модели стоимости — допущения, не замеры; модель не включает web search ($0.01 за запрос плюс результаты поиска как input), рост input из-за сохраняемых thinking-блоков в многоходовых циклах и повторные прогоны
при refusal. Запас до $1 есть, но он должен быть подтверждён реальным usage на пилоте; цены нестабильны: Haiku 5.5 вышел 7 дней назад, sale-цена Mistral Large 4 без срока, цены Gemini удваиваются 2026-12-01 и 2027-01-01.
- Inspect AI не тестируется авторами на Windows и Python 3.13 (CI: только ubuntu-latest, Python 3.10/3.11), а из-за отсутствия temperature на Claude 5.5 сравнение с baseline требует нескольких epochs — бюджет eval-прогонов кратно
выше заявленных $20-29.

## VERIFIER VERDICTS ON RECOMMENDATIONS

### NEED: Модели и провайдер: primary + fallback, tiering под бюджет <= $1
PRIMARY: Anthropic Claude API: claude-haiku-5-5 (рутина) + claude-sonnet-5-5 (планирование, отчёт); fallback OpenAI gpt-6-luna + gpt-6.1-sol через Responses API
STANDS: True
ISSUE: Цены, лимиты, лицензионные условия Anthropic и арифметика подтверждены; бюджет $1 выдерживается с запасом. Но: (1) тезис 'самые дешёвые модели' неверен (есть дешевле), хотя на бюджет не влияет — 84% стоимости дают 8 вызовов
Sonnet; (2) не проанализирована Usage Policy Anthropic: в редакции, которую страница показывает как 'Effective November 12, 2026', запрещено 'identify, unmask, or locate' людей по псевдонимной активности с целью
harass/intimidate/surveil/cause harm и сбор профилей личности для раскрытия третьим лицам — ровно зона OSINT-агента и отчёта для бирж; (3) refusal-риск реален и хуже описанного: у Haiku 5.5 нет server-side fallback, у Sonnet 5.5
он покрывает только cyber и frontier_llm, а general_harms срабатывает и на добросовестной работе; (4) цель '<= 2 минут' под угрозой из-за длинной генерации отчёта на Sonnet с effort high — не измерено; (5) договор OpenAI
(fallback) не прочитан — 403; (6) в сумму не включён web search; (7) для новой организации действуют Evaluation tier и принудительная проверка preserved thinking (аккаунты, созданные после 2026-08-31: история с thinking-блоками
должна быть append-only, иначе 400).
SUGGESTED CHANGE: Оставить Anthropic primary, но до фиксации: а) юридический разбор AUP и ограничение OSINT-агента атрибуцией сервисов и юрлиц, без установления личности физлиц, плюс human review; б) пилот на 50 сценариях с замером доли refusal по
категориям и латентности; подать заявку в Cyber Verification Program; в) сделать strong-tier конфигурируемым и включить в eval три варианта: Sonnet 5.5, Haiku 5.5 с effort high (всё расследование ~$0.08-0.15) и дешёвый внешний
strong-tier (Mistral Large 4 $0.68/$2.09 — около $0.15 за расследование; Grok 4.3 $1.25/$2.50 — около $0.21); г) тело отчёта собирать детерминированным шаблоном, LLM — только короткие секции, стримингом; д) заложить $0.10-0.25 на
web search в бюджет; е) прочитать OpenAI Services Agreement вручную до включения fallback; ж) держать prompt Haiku ниже 100K с учётом cache read.

### NEED: Gateway / слой доступа к моделям
PRIMARY: Без отдельного gateway: официальные SDK (anthropic 1.13.0, openai 3.29.0) за собственным тонким адаптером
STANDS: True
ISSUE: Вывод верен, но два аргумента неточны: в 2026 году у LiteLLM не два, а четыре critical advisory (и шесть high) — аргумент безопасности сильнее заявленного; а 'молчаливое отбрасывание output_config' происходит только при
drop_params=True, с warning, и не затрагивает Haiku 5.5 / Sonnet 5.5. Оценка '200-400 строк glue-кода' выглядит заниженной: два разных API (Messages и Responses), ступенчатые цены (>100K у Haiku, >272K у GPT-6), cache-учёт,
обработка refusal и stop_reason, стриминг. Не рассмотрены лёгкие библиотеки-абстракции (any-llm, Pydantic AI) и Bifrost как замена LiteLLM Proxy.
SUGGESTED CHANGE: Сохранить решение. Добавить: контрактные тесты расчёта стоимости по трём ценовым режимам; eval-прогоны проводить через тот же адаптер, что и production (иначе Inspect AI тестирует другой кодовый путь); если провайдеров станет
больше двух — сначала оценить mozilla-ai/any-llm (Apache-2.0, поверх официальных SDK) и только потом LiteLLM SDK с пиннингом по хешу; LiteLLM Proxy не разворачивать.

### NEED: LLM observability: журнал действий агентов, токены, стоимость
PRIMARY: Langfuse (MIT-ядро) через OpenTelemetry: Langfuse Cloud Hobby/Core или self-host через Docker Compose на отдельной VM 4 ядра / 16 GiB
STANDS: True
ISSUE: Факты о Langfuse подтверждены, но рекомендация конфликтует с ограничением 'один скромный сервер': self-host требует 6 контейнеров и минимум 16 GiB, а compose официально не production. Остаётся только Cloud-вариант — это вывод
данных расследований (включая материалы жертв) третьей стороне с доступом 30-90 дней. Отклонение Phoenix обосновано слабо: ELv2 запрещает лишь продавать сам Phoenix как managed service, внутреннему использованию в коммерческом
SaaS не мешает, а архитектурно это одно приложение с SQLite/PostgreSQL. Тезис 'единственный кандидат с разрешительной лицензией и полным набором функций' — следствие глубины аудита: Opik (Apache-2.0) и MLflow (Apache-2.0, 28 372
звезды, v3.17.1) глубоко не проверялись.
SUGGESTED CHANGE: Зафиксировать правило выбора: источник истины — собственная БД платформы + OTel-инструментирование (как и предложено); UI анализа на старте — Phoenix на том же сервере (PostgreSQL уже нужен платформе) либо Langfuse Cloud в регионе
EU, если владелец разрешает вынос данных и включено client-side masking; self-host Langfuse — только при появлении отдельной VM. До выбора за 1-2 дня сравнить Phoenix и MLflow tracing на реальном трейсе расследования.
TELEMETRY_ENABLED выключить.

### NEED: Evals: 50+ сценариев с ground truth, AI-слой против baseline
PRIMARY: Inspect AI (MIT) как раннер, сценарии в JSONL, детерминированные scorers на Python
STANDS: True
ISSUE: Лицензия, активность и набор провайдеров подтверждены. Не учтено: CI проекта покрывает только ubuntu-latest и Python 3.10/3.11 — Windows 11 и Python 3.13 не тестируются; на моделях Claude 5.5 нельзя задать temperature, поэтому для
статистически значимого сравнения с baseline нужны несколько epochs — стоимость прогона вырастает кратно ($20-29 за один проход превращаются в $60-145 при 3-5 epochs, либо вдвое меньше через Batch); встроенные провайдеры Inspect —
это не production-адаптер платформы. Версия 0.3.x выходит дважды в неделю.
SUGGESTED CHANGE: Сохранить Inspect AI. Запускать в Linux-контейнере (Docker есть на dev-машине), пиннить точную версию, вызывать production-пайплайн из собственного solver, а не через встроенные провайдеры; закладывать 3-5 epochs и парный тест по
сценариям; refusal и латентность сделать отдельными метриками. Как более лёгкую альтернативу держать в уме pydantic_evals (каталог есть в репозитории pydantic/pydantic-ai, MIT; глубоко не проверял).

### NEED: Воспроизводимость: пиннинг версий моделей и параметров
PRIMARY: Конфиг моделей в git + полный журнал запросов и ответов; точные ID claude-haiku-5-5 и claude-sonnet-5-5, явный effort
STANDS: True
ISSUE: Подтверждено документацией: все ID — pinned snapshots, sampling-параметры на Haiku 5.5 и Sonnet 5.5 недоступны, default effort различается. Пробелы: thinking-блоки Haiku 5.5 привязаны к аккаунту-производителю, а для аккаунтов
после 2026-08-31 изменение system/tools/истории при возврате thinking-блоков даёт 400 — replay и компакция истории должны это учитывать; при fallback на другую модель thinking-блоки молча отбрасываются. У OpenAI датированных
snapshot для GPT-6 не видно (в OpenRouter canonical slug openai/gpt-6-luna-20260922), пиннинг fallback остаётся неподтверждённым.
SUGGESTED CHANGE: Дополнить журнал полями: заголовок anthropic-version и список beta-заголовков, inference_geo, конфигурация thinking и display, id аккаунта/workspace, признак сработавшего fallback и фактическая модель, stop_details.category.
Историю агентов вести строго append-only. Воспроизводимость определять как 'пересборка из журнала', а дрейф ловить еженедельным canary. Если владельцу нужна квази-детерминированная повторная генерация, учесть, что temperature и
seed по каталогу OpenRouter доступны у Gemini, Mistral Large 4 и Grok, но не у Claude 5.5.

## VERIFIER FACT CHECKS

- [CONFIRMED] Anthropic Claude API (Haiku 5.5 / Sonnet 5.5 / Opus 5.5) :: Цены за 1M: Haiku 5.5 $0.10 / $0.125 / $0.01 / $0.50 (при prompt >100K: $0.50 / $0.625 / $0.05 / $2.50); Sonnet 5.5 $2 / $2.50 / $0.10 / $10; Opus 5.5 $4 / $5 / $0.20 / $20; Fable 5.1 $10 / $12.50 / $0.25 / $50; Batch -50%; web
search $10 за 1000; tool-use system prompt +286 токенов.
  CORRECT VALUE: Все числа совпали с официальной таблицей. Дополнения: 1h cache write — Haiku 5.5 $0.20, Sonnet 5.5 $4; порог 100K у Haiku считает ВСЕ входные токены запроса, включая cache read и cache write, и применяется к каждому запросу
отдельно; inference_geo "us" даёт множитель 1.1x. Замечание: в кеше claude-api skill (от 2026-10-06) cache read у Sonnet 5.5 указан как $0.20 — это устарело, на живой странице $0.10 (0.05x от input).
  METHOD: WebFetch официальной страницы pricing (полный текст, 50 KB, прочитан локально); перекрёстно — живой GET https://openrouter.ai/api/v1/models (461 модель) и raw model_prices_and_context_window.json из BerriAI/litellm (4 084 записи):
три источника совпали.
  EVIDENCE: https://platform.claude.com/docs/en/about-claude/pricing

- [CONFIRMED] Anthropic Claude API :: Rate limits Start tier: 1 000 RPM, 2M ITPM, 400K OTPM на модель; cache reads не считаются в ITPM; месячный cap: Start $500, Build $1 000, Scale $200 000; новые организации могут начинать в Evaluation tier.
  CORRECT VALUE: Совпадает. Build: 5 000 RPM / 5M ITPM / 1M OTPM; Scale: 10 000 / 10M / 2M. При достижении cap — HTTP 429 без retry-after до 1-го числа следующего месяца (error_code enforced_spend_limit_reached). Числовые лимиты Evaluation tier на
странице не опубликованы.
  METHOD: WebFetch официальной страницы, таблицы прочитаны полностью.
  EVIDENCE: https://platform.claude.com/docs/en/api/rate-limits

- [CONFIRMED] Anthropic Claude API :: Линейка: claude-haiku-5-5 (релиз 2026-10-07, retirement не ранее 2027-10-07), claude-sonnet-5-5 (не ранее 2027-09-28), claude-opus-5-5 (не ранее 2027-09-22); context 1M, max output 128K, cutoff Jun 2026; dateless ID — pinned
snapshot; default effort Haiku medium / Sonnet high / Opus medium.
  CORRECT VALUE: Совпадает. Дополнительно: Fable 5.1 — retirement не ранее 2027-09-01; у Haiku 5.5 нет отдельного alias и нет датированного ID ("fixed model ID with no date suffix").
  METHOD: WebFetch models overview и страницы models/haiku-5-5/overview.
  EVIDENCE: https://platform.claude.com/docs/en/about-claude/models/overview

- [CONFIRMED] Anthropic Claude API :: Structured outputs (output_config.format, strict tools) GA на Haiku 5.5 / Sonnet 5.5 / Opus 5.5; лимиты: 20 strict tools, 24 optional-параметра, 16 union-параметров; нет рекурсии, minimum/maximum, minLength/maxLength; кеш
грамматики 24 ч; при refusal и max_tokens вывод может не соответствовать схеме; enum может отличаться регистром.
  CORRECT VALUE: Совпадает. Дополнения, которых нет в аудите: таймаут компиляции грамматики 180 с; minItems только 0 или 1; additionalProperties обязан быть false; на Amazon Bedrock structured outputs для Haiku 5.5 НЕДОСТУПНЫ (прямо сказано в
migration guide Haiku 5.5), на Google Cloud и Microsoft Foundry — GA.
  METHOD: WebFetch (первые 100K из 103K символов страницы) + WebFetch migration guide Haiku 5.5; независимо — живой GET /api/v1/models/anthropic/claude-haiku-5.5/endpoints на OpenRouter: у Amazon Bedrock и Claude Platform on AWS параметр
structured_outputs не объявлен.
  EVIDENCE: https://platform.claude.com/docs/en/build-with-claude/structured-outputs

- [CONFIRMED] Anthropic Claude API :: На Haiku 5.5 нельзя задать temperature/top_p/top_k (не-default значения дают 400); Sonnet 5.5 и Opus 5.5 не принимают forced tool_choice (any/tool) — по справке skill, не перепроверено.
  CORRECT VALUE: Sampling: на Haiku 5.5 допустимы только temperature=1 или top_p=0.99; любое top_k, top_p=1 и одновременная передача temperature+top_p дают 400; то же правило (non-default = 400) на Sonnet 5.5. Forced tool_choice: Sonnet 5.5
отвергает any/tool с 400 (подтверждено живой документацией, включая count_tokens); Haiku 5.5 forced tool_choice ПРИНИМАЕТ, но ответ тогда идёт без thinking-блока. Для Opus 5.5 утверждение осталось только по skill (живую страницу
не открывал). Новое: Haiku 5.5 не имеет server-side fallback при refusal; у Sonnet 5.5 server-side fallback (beta, только Claude API) повторяет лишь категории cyber и frontier_llm, а general_harms не повторяется, причём
документация прямо пишет, что её может вызвать и добросовестная работа.
  METHOD: WebFetch migration guide Haiku 5.5 (полностью) и Sonnet 5.5 (55 KB, целевой поиск по тексту).
  EVIDENCE: https://platform.claude.com/docs/en/models/sonnet-5-5/migration-guide

- [CONFIRMED] Anthropic Claude API :: ZDR только через sales и на организацию; Batch и Files API под ZDR не попадают; помеченный контент может храниться до 2 лет; расхождение между '30 дней' и 'conversation content is not retained by default'.
  CORRECT VALUE: Совпадает: 'Conversation content ... is not retained by default' (исключение — Covered Models: Fable/Mythos, 30 дней); Batch — хранение 29 дней; Files — до удаления; flagged — до 2 лет даже при ZDR. Privacy-статью про 30 дней сам
не открывал — расхождение подтверждено только со стороны API-страницы.
  METHOD: WebFetch (57 KB, целевой поиск по тексту).
  EVIDENCE: https://platform.claude.com/docs/en/build-with-claude/api-and-data-retention

- [CONFIRMED] Anthropic Claude API :: Commercial Terms (2025-06-17), раздел A.1 разрешает использовать сервис в продуктах для собственных клиентов; запрет перепродажи и конкурирующих моделей; outputs принадлежат клиенту; обучение на Customer Content запрещено.
  CORRECT VALUE: Effective Date June 17, 2025; A.1 — 'to power products and services Customer makes available to its own customers and end users'; ограничения в D.4; права на Outputs и запрет обучения — раздел B. Срок хранения в самих Terms не
указан (отсылка к DPA).
  METHOD: WebFetch официальной страницы (извлечение коротких цитат).
  EVIDENCE: https://www.anthropic.com/legal/commercial-terms

- [REFUTED] Anthropic Claude Haiku 5.5 / OpenAI GPT-6 Luna :: Haiku 5.5 и GPT-6 Luna — самые дешёвые модели с vision, strict structured outputs и 1M context среди проверенных ($0.10/$0.50); открытые модели у хостеров не дешевле.
  CORRECT VALUE: В живом каталоге OpenRouter есть более дешёвые модели с tools + structured_outputs + image и контекстом около 1M: google/gemini-2.5-flash-lite $0.10/$0.40 (она есть и в самом аудите; но expiration_date 2026-10-20),
openai/gpt-4.1-nano $0.10/$0.40 (1.05M), qwen/qwen3.5-flash $0.065/$0.26 (1M), xiaomi/mimo-v2.6-flash $0.14/$0.28 (1.05M), z-ai/glm-5.3-flash $0.026/$0.90; с меньшим контекстом — openai/gpt-5-nano $0.05/$0.40 (400K, есть и на
официальной странице OpenAI). Утверждение верно только для актуального поколения first-party моделей Anthropic/OpenAI. На вывод это почти не влияет: доля Haiku в модели стоимости — $0.062 из $0.40.
  METHOD: Живой keyless GET каталога OpenRouter, сортировка по цене моделей с параметрами tools и structured_outputs и image во входных модальностях; сверка gpt-5-nano с developers.openai.com/api/docs/pricing.
  EVIDENCE: https://openrouter.ai/api/v1/models

- [CONFIRMED] OpenAI API (GPT-6 Luna / GPT-6.1 Sol) :: gpt-6-luna $0.10 / $0.01 / $0.50 (cache write $0.125); gpt-6.1-sol $2 / $0.10 / $10 (cache write $2.50); gpt-6-astra $10 / $1 / $50; Batch и Flex -50%; при >272K input x2, output x1.5; data residency +10%; tiers Build ($5)
$500/мес, Launch ($100) $5 000, Grow ($500) $200 000; Luna на Build 5 000 RPM / 2M TPM.
  CORRECT VALUE: Совпадает. Уточнение по спорной строке аудита: на официальной странице gpt-5.6-sol стоит $4 / $0.40 / $20 (промо 'at least through November 21, 2026'), gpt-5.6-luna $0.20/$1.20. Есть также бесплатный tier ($100/мес).
  METHOD: WebFetch pricing, guides/rate-limits и models/gpt-6-luna; сверка с OpenRouter API и LiteLLM cost map.
  EVIDENCE: https://developers.openai.com/api/docs/pricing

- [CONFIRMED] OpenAI API (GPT-6 Luna) :: Context 1.05M при max input 922K; function calling в Chat Completions работает только при reasoning_effort none; датированных snapshot ID на странице модели нет.
  CORRECT VALUE: Совпадает: context 1 050 000, max input 922 000, max output 128 000, cutoff 2026-05-18; reasoning effort none/low/medium(default)/high/xhigh/max; на странице указан только ID gpt-6-luna. По supported_parameters OpenRouter у
gpt-6-luna и gpt-6.1-sol есть seed, но нет temperature (на странице OpenAI это не описано).
  METHOD: WebFetch страницы модели; supported_parameters — живой GET OpenRouter /api/v1/models.
  EVIDENCE: https://developers.openai.com/api/docs/models/gpt-6-luna

- [UNVERIFIABLE] OpenAI API :: Services Agreement прочитать не удалось (HTTP 403); права на коммерческое использование по тексту договора не подтверждены.
  CORRECT VALUE: Повторить не удалось: WebFetch — 403, curl с браузерным User-Agent — 403 (JS-challenge 'Enable JavaScript and cookies'). Коммерческие условия fallback-провайдера остаются непроверенными — договор нужно прочитать вручную в браузере
до подписки.
  METHOD: WebFetch + один keyless curl GET; оба вернули 403.
  EVIDENCE: https://openai.com/policies/services-agreement/

- [CONFIRMED] Google Gemini API :: gemini-3.5-flash-lite $0.30/$2.50 (cache $0.03); gemini-3.8-flash $0.75/$3.75 до 2026-12-31, затем $1.50/$7.50; gemini-4-argon $2/$10 до 2026-11-30, затем $4/$20; страница обновлена 2026-10-13; free tier использует данные для
улучшения продуктов.
  CORRECT VALUE: Совпадает ('Last updated 2026-10-13 UTC'). Дополнение: Grounding with Google Search — 5 000 бесплатных запросов в месяц, затем $14 за 1000. Gemini 4 Argon на free tier недоступен. Условия (terms) и страницу ZDR сам не открывал.
  METHOD: WebFetch официальной страницы pricing; сверка с OpenRouter API и LiteLLM cost map.
  EVIDENCE: https://ai.google.dev/gemini-api/docs/pricing

- [CONFIRMED] DeepSeek API :: deepseek-flash: input cache miss $0.15 off-peak / $0.30 peak, cache hit $0.003 / $0.006, output $0.60 / $1.20; peak 01:00-04:00 и 06:00-10:00 UTC по будням; concurrency 2 500 / 500; strict mode не указан.
  CORRECT VALUE: Совпадает, включая deepseek-v4-pro $0.66/$1.32 input и $1.98/$3.96 output; peak-часы не действуют в китайские праздники. Privacy Policy сам не открывал.
  METHOD: WebFetch официальной страницы pricing.
  EVIDENCE: https://api-docs.deepseek.com/quick_start/pricing

- [CONFIRMED] Mistral API (Large 4 / Small 4) :: Small 4 $0.15 / $0.015 / $0.60; Large 4 $0.68 / $0.07 / $2.09 (sale; list $1.36 / $0.14 / $4.18), срок sale не указан; OCR 4.1 $4 за 1000 страниц.
  CORRECT VALUE: Совпадает. Существенное дополнение: на OpenRouter у mistral-large-4-0 есть first-party endpoints mistral/zdr и mistral/eu (EU +10%: $0.748/$2.299), tools + structured_outputs + image, поддержка temperature и seed; но uptime за
сутки 94.4-95.4% (EU 98.2%) — заметно хуже, чем у Anthropic first-party (100%).
  METHOD: WebFetch docs.mistral.ai/inference/pricing; живой GET https://openrouter.ai/api/v1/models/mistralai/mistral-large-4-0/endpoints.
  EVIDENCE: https://docs.mistral.ai/inference/pricing

- [CONFIRMED] OpenRouter :: Покупка кредитов облагается 5.5% (минимум $0.80), crypto 5%; BYOK бесплатно до $25 000/мес, далее 5%; в ZDR-списке (944 endpoints) Claude Haiku 5.5 / Sonnet 5.5 есть только через Google и Amazon Bedrock, GPT-6 Luna — только через
Azure; Bedrock-endpoints Haiku 5.5 без structured_outputs.
  CORRECT VALUE: Совпадает; в моём запросе ZDR-список содержит 943 endpoints (а не 944). Уточнение: у first-party endpoint Anthropic для Haiku 5.5 OpenRouter объявляет supports_tool_choice required=false / function=false, то есть forced tool
choice через OpenRouter недоступен, хотя Anthropic API его принимает. Terms OpenRouter (п. 5.1, 5.2, 7.4, 16) сам не читал.
  METHOD: Живые keyless GET: /api/v1/endpoints/zdr, /api/v1/models/anthropic/claude-haiku-5.5/endpoints; WebFetch openrouter.ai/docs/faq.
  EVIDENCE: https://openrouter.ai/api/v1/endpoints/zdr

- [CORRECTED] LiteLLM :: MIT вне каталога enterprise/; компрометация PyPI 2026-03-24 (1.82.7, 1.82.8, issues #24512/#24514/#24518); по Proxy 'два critical advisory за 2026 год' (2026-09-30 и 2026-05-28), high 2026-10-01, medium SSRF 2026-08-26.
  CORRECT VALUE: Лицензия и инцидент PyPI подтверждены. Число advisories занижено: за 2026 год опубликовано 17 advisories — 4 critical (2026-04-03 OIDC cache key collision, 2026-04-20 SQL injection в проверке ключей Proxy, 2026-05-28 Host header
auth bypass, 2026-09-30 salt key privilege escalation), 6 high, 5 medium, 2 low. Последний релиз v1.105.0 (2026-10-11).
  METHOD: gh api repos/BerriAI/litellm/security-advisories?per_page=100 (подсчёт по severity и дате), gh api issues/24512, 24514, 24518, gh api contents/LICENSE.
  EVIDENCE: https://github.com/BerriAI/litellm/security/advisories

- [CORRECTED] LiteLLM :: В transformation.py есть ветка 'Dropping unsupported output_config for model' — параметры могут молча отбрасываться, что вредит воспроизводимости.
  CORRECT VALUE: Ветка срабатывает только при litellm.drop_params is True (не default), пишет warning в лог, отбрасывает только effort-часть (output_config.format сохраняется) и только для моделей без флага поддержки effort. Для claude-haiku-5-5 в
cost map стоит supports_output_config: true, supports_native_structured_output: true, supports_sampling_params: false — то есть для рекомендованных моделей отбрасывания нет. Аргумент против LiteLLM SDK слабее заявленного; аргумент
безопасности, наоборот, сильнее.
  METHOD: Чтение исходника (raw, 129 KB): константа DROP_UNSUPPORTED_OUTPUT_CONFIG_WARNING и метод _apply_output_config (строки 2150-2176); чтение записи claude-haiku-5-5 в model_prices_and_context_window.json.
  EVIDENCE: https://raw.githubusercontent.com/BerriAI/litellm/main/litellm/llms/anthropic/chat/transformation.py

- [CONFIRMED] Langfuse :: MIT для ядра, ee/ под Enterprise License, copyright ClickHouse, Inc.; куплен ClickHouse 2026-01-16; v4.58.0 (2026-10-13) и v3.225.12; compose: web, worker, ClickHouse 25.12, Postgres 17, Redis 7, MinIO; TELEMETRY_ENABLED по
умолчанию true; минимум 4 ядра / 16 GiB / 100 GiB; compose без HA и бэкапов; Cloud: Hobby 50k units, Core $29, Pro $199, Enterprise $2 499; EE-only: project-level RBAC, audit logs, retention, server-side masking, SCIM, protected
prompt labels.
  CORRECT VALUE: Всё совпало. Уточнения: billable unit = любая точка трассировки (traces, observations, scores), поэтому 106 LLM-вызовов дают минимум ~110-220 units, а с tool-spans и scores — 300+; Cloud доступен в регионах US, EU, Japan;
стартапам скидка 50% на первый год; Hobby — доступ к данным 30 дней, Core — 90 дней.
  METHOD: gh api (LICENSE, docker-compose.yml, releases); WebFetch langfuse.com/pricing, /pricing-self-host, /self-hosting/deployment/docker-compose, блог ClickHouse.
  EVIDENCE: https://langfuse.com/self-hosting/deployment/docker-compose

- [CONFIRMED] Arize Phoenix :: Лицензия Elastic License 2.0: запрещено предоставлять Phoenix третьим лицам как hosted/managed service; требования к ресурсам на прочитанной странице не указаны.
  CORRECT VALUE: ELv2 подтверждена текстом LICENSE. Дополнение, меняющее оценку: архитектура Phoenix — одно контейнерное приложение (UI + trace collector) с SQLite по умолчанию или PostgreSQL >= 14 для production; ClickHouse, Redis и object
storage не требуются; 'free to self-host with no feature limitations'. Это на порядок легче Langfuse (6 контейнеров, 16 GiB) и укладывается в 'один скромный сервер'. Ограничение ELv2 не затрагивает внутреннее использование внутри
коммерческого SaaS.
  METHOD: gh api repos/Arize-ai/phoenix/contents/LICENSE (текст прочитан); WebFetch страниц self-hosting и self-hosting/architecture.
  EVIDENCE: https://arize.com/docs/phoenix/self-hosting/architecture

- [CONFIRMED] Inspect AI :: MIT, 0.3.279 (2026-10-12), Python >= 3.10, провайдеры anthropic/openai/google/mistral/deepseek/groq/together/fireworks/openrouter/ollama/vllm/mockllm, batch-режим; работа на Windows 11 не проверена.
  CORRECT VALUE: Факты совпали (LICENSE: MIT, copyright UK AI Security Institute; есть также grok.py, bedrock.py, azureai.py, openai_responses.py, _anthropic_batch.py, _openai_batch.py, _google_batch.py). Новое: CI-матрица (build.yml, test.yml) —
только ubuntu-latest и Python 3.10/3.11; Windows и Python 3.13 в CI не тестируются. На dev-машине (Windows 11, Python 3.13) eval-раннер стоит запускать в Docker/WSL.
  METHOD: gh api: метаданные, LICENSE, pyproject.toml, список src/inspect_ai/model/_providers, чтение .github/workflows/build.yml и test.yml.
  EVIDENCE: https://github.com/UKGovernmentBEIS/inspect_ai

- [CONFIRMED] Portkey AI Gateway :: Куплен Palo Alto Networks (сделка закрыта 2026-05-29); последний релиз v1.15.2 от 2026-01-12; последний push 2026-05-25.
  CORRECT VALUE: Совпадает: пресс-релиз PANW от 2026-05-29 ('closed the acquisition of Portkey', Portkey становится ядром AI Gateway в Prisma AIRS; об open-source не сказано ничего); pushed_at 2026-05-25T13:54:51Z; MIT; 13 180 звёзд.
  METHOD: gh api (repo, releases/latest, commits) + WebFetch пресс-релиза.
  EVIDENCE: https://www.paloaltonetworks.com/company/press/2026/palo-alto-networks-completes-acquisition-of-portkey-to-secure-ai-agents

- [CONFIRMED] Helicone :: Куплен Mintlify 2026-03-03 и переведён в maintenance mode (по вторичным источникам); последний релиз 2025-08-21; последний коммит 2026-09-16.
  CORRECT VALUE: Теперь подтверждено первичным источником: пост Mintlify от 2026-03-03 — 'Helicone will continue operating in maintenance mode', клиентам обещана помощь с миграцией на другую платформу. Последний коммит в main 2026-09-16
(исправление platform-admin takeover и cross-tenant bypass); release v2025.08.21-1.
  METHOD: WebFetch блога Mintlify; gh api releases/latest и commits?sha=main.
  EVIDENCE: https://mintlify.com/blog/mintlify-acquires-helicone

- [CONFIRMED] promptfoo / DeepEval / официальные SDK :: promptfoo: 'now part of OpenAI', MIT; DeepEval: PostHog-телеметрия включена по умолчанию, отключение DEEPEVAL_TELEMETRY_OPT_OUT; SDK: anthropic 1.13.0 (2026-10-09, MIT, Python >=3.10), openai 3.29.0 (2026-10-11), google-genai
2.30.1 (2026-10-13).
  CORRECT VALUE: Всё совпало: README promptfoo содержит фразу о вхождении в OpenAI и MIT; в deepeval/telemetry/client.py зашиты PostHog project key и host https://us.i.posthog.com, opt-out через настройку DEEPEVAL_TELEMETRY_OPT_OUT; версии и даты
релизов SDK совпадают (anthropic теперь зависит от httpx2).
  METHOD: gh api contents (README promptfoo, client.py DeepEval, pyproject.toml anthropic-sdk-python), gh api releases/latest трёх SDK.
  EVIDENCE: https://github.com/confident-ai/deepeval/blob/main/deepeval/telemetry/client.py

- [CONFIRMED] Модель стоимости расследования :: Типичное расследование: 106 вызовов, Haiku 5.5 $0.062 + Sonnet 5.5 $0.334 = $0.40; тяжёлый случай $0.57; всё на Sonnet $1.55; всё на Haiku $0.08; без кеширования $0.44; 10 дополнительных Sonnet-вызовов — около $0.29.
  CORRECT VALUE: Арифметика пересчитана и сходится (Haiku: 0.0041 + 0.0030 + 0.0268 + 0.0282 = $0.0621; Sonnet: 0.0525 + 0.0013 + 0.120 + 0.160 = $0.3338). Но подтверждена только арифметика, не входные числа: все объёмы токенов — допущения.
Замечания: 84% стоимости дают 8 вызовов Sonnet; web search ($0.01 за запрос плюс результаты как input) в сумму не включён — 10-20 запросов OSINT добавят $0.10-0.25; в многоходовых tool-циклах thinking-блоки прошлых ходов остаются
в контексте и считаются как input (migration guide Haiku 5.5), что модель не учитывает; 16K output на 8 вызовов Sonnet с отчётом на русском выглядит оптимистично.
  METHOD: Пересчёт по подтверждённым ценам; чтение migration guide (поведение thinking-блоков и tokenizer +30%).
  EVIDENCE: https://platform.claude.com/docs/en/models/haiku-5-5/migration-guide

- [CONFIRMED] Anthropic Claude API (vision) :: До 600 изображений на запрос, до 10 MB каждое, запрос до 32 MB, JPEG/PNG/GIF/WebP; стоимость ceil(w/28)*ceil(h/28); скриншот 1920x1080 = 2 691 токен.
  CORRECT VALUE: Совпадает; Haiku 5.5 относится к high-resolution tier (до 2576 px по длинной стороне, до 4784 visual tokens). Если в запросе больше 20 изображений — действует более жёсткий лимит размеров (не более 2000 px). Отдельное ограничение
для OSINT: Claude 'cannot be used to name people in images'.
  METHOD: WebFetch официальной страницы (полный текст).
  EVIDENCE: https://platform.claude.com/docs/en/build-with-claude/vision

- [CONFIRMED] LangSmith :: Developer $0, 1 seat, 5k base traces/мес; Plus $39 за seat, 10k base traces; base traces хранятся 14 дней, extended 180 дней; self-hosted и hybrid только Enterprise; цена сверх включённого не приведена.
  CORRECT VALUE: Совпадает.
  METHOD: WebFetch страницы pricing.
  EVIDENCE: https://www.langchain.com/pricing

## CANDIDATES MISSED BY THE RESEARCHER (found by verifier)

- xAI Grok 4.3 / Grok 4.7 (strong tier) (https://docs.x.ai/docs/models)
  WHY: 84% стоимости расследования дают вызовы strong-модели, а у Grok output в 1.7-4 раза дешевле Sonnet 5.5: grok-4.3 $1.25 / $0.20 cached / $2.50, context 1M; grok-4.7 $2 / $0.50 / $6, context 500K.
  ASSESSMENT: Цены подтверждены на официальной странице docs.x.ai (при prompt >= 200K все токены запроса тарифицируются вдвое). По OpenRouter API: tools + structured_outputs + image, temperature и seed поддержаны, есть first-party ZDR-endpoint
(xai/zdr), uptime 100% за сутки. Документация обещает соответствие схеме для поддерживаемых конструкций (minLength/maxLength, числовые границы — поддержаны, в отличие от Claude). Не проверено: условия использования, хранение
данных, качество tool calling. Кандидат в eval-набор как альтернативный strong-tier или третий fallback.

- Meta Muse Spark 1.3 (https://openrouter.ai/api/v1/models/meta/muse-spark-1.3/endpoints)
  WHY: Новый провайдер 2026 года: $1.25 / $4.25, context 1 048 576, tools + structured_outputs, вход image/video/file.
  ASSESSMENT: В OpenRouter обслуживается first-party endpoint Meta, uptime 99.6% за сутки. Вариант 'contributor' за $0.10 / $0.20 по вторичным источникам отдаёт входы и выходы на улучшение продуктов Meta — для данных жертв неприемлем.
Официальные страницы цен и условий Meta открыть не удалось (только вторичные источники и каталог OpenRouter); по вторичным данным preview на старте был ограничен разработчиками из США. Только trial.

- Claude через Google Cloud Vertex AI (EU multi-region) как маршрут ZDR и data residency (https://platform.claude.com/docs/en/build-with-claude/structured-outputs)
  WHY: Аудит упоминает ZDR-endpoints, но не предлагает маршрут: first-party ZDR у Anthropic — только через sales, Bedrock теряет structured outputs для Haiku 5.5.
  ASSESSMENT: Документация Anthropic: structured outputs на Google Cloud — GA; на Amazon Bedrock для Haiku 5.5 недоступны. В списке ZDR OpenRouter есть google-vertex/europe, /us, /global для Haiku 5.5 и Sonnet 5.5 со structured_outputs.
Региональные и multi-region endpoints дороже на 10%; изображения только base64, до 5 MB; server-side fallback и часть beta-функций там недоступны. Обработчиком данных становится Google — условия Vertex не читал.

- MLflow 3.x (GenAI tracing и evaluation) (https://github.com/mlflow/mlflow)
  WHY: Apache-2.0 без open-core, лёгкая self-hosted альтернатива Langfuse для одного сервера; в аудите упомянут только в not_verified.
  ASSESSMENT: 28 372 звезды, v3.17.1 от 2026-10-13, LICENSE — Apache 2.0 (проверено gh api). Документация: tracing 'fully OpenTelemetry-compatible', поддержка GenAI Semantic Conventions, интеграции с OpenAI, Anthropic, Pydantic AI, отдельный
лёгкий пакет mlflow-tracing, данные на своей инфраструктуре. Не проверено в сессии: требования к backend store, учёт стоимости, зрелость prompt registry и LLM-judges.

- Pydantic Logfire (https://pydantic.dev/pricing)
  WHY: OTel-нативная SaaS-observability с большим бесплатным объёмом и регионом EU; естественная пара к Pydantic AI, который аудит пометил как needs-trial.
  ASSESSMENT: Personal — бесплатно, 10M records в месяц, хранение 30 дней, 1 seat, при превышении приём останавливается; Team $49/мес (5 seats, регион EU или US, $2 за 1M сверх лимита); Growth $249/мес; self-hosting только Enterprise. SDK
pydantic/logfire — MIT, v5.2.0 от 2026-10-13. Минус тот же, что у Langfuse Cloud: данные расследований уходят третьей стороне.

- Bifrost (Maxim AI) (https://github.com/maximhq/bifrost)
  WHY: Активный open-source gateway 2025-2026 годов — замена LiteLLM Proxy и замороженному Portkey, если отдельный gateway всё же понадобится.
  ASSESSMENT: Apache-2.0, 8 760 звёзд, push 2026-10-13, 1 206 открытых issues. Код, security-история и поддержка cache_control / output_config не проверялись. Для MVP с двумя провайдерами не нужен.

- any-llm (Mozilla AI) (https://github.com/mozilla-ai/any-llm)
  WHY: Python-библиотека единого интерфейса поверх официальных SDK — промежуточный вариант между собственным адаптером и LiteLLM SDK, без proxy и без его поверхности атаки.
  ASSESSMENT: Apache-2.0, 2 217 звёзд, релиз 1.34.0 от 2026-10-13, всего 34 открытых issues. Покрытие специфичных параметров Anthropic (cache_control, effort, output_config) не проверено.

- Instructor (https://github.com/567-labs/instructor)
  WHY: Структурированный вывод с Pydantic-валидацией и повторами — закрывает то, что constrained decoding не покрывает (числовые границы, длины строк, регистр enum).
  ASSESSMENT: MIT, 14 007 звёзд, v1.17.0 от 2026-09-09, push 2026-10-11. Работает поверх официальных SDK. Код не читал; пригоден как тонкий слой валидации в адаптере.

- Laminar и LangWatch (open-source agent observability) (https://github.com/lmnr-ai/lmnr)
  WHY: Новые Apache-2.0 платформы трассировки агентов, не вошедшие в аудит.
  ASSESSMENT: Laminar: Apache-2.0, 3 377 звёзд, v0.3.1 от 2026-10-13. LangWatch (github.com/langwatch/langwatch): Apache-2.0, 4 944 звезды, релиз 3.20.1 от 2026-10-02. Проверены только метаданные; требования к инфраструктуре неизвестны.
Приоритет ниже Phoenix и MLflow.

- TensorZero (отрицательная находка) (https://github.com/tensorzero/tensorzero)
  WHY: Часто рекомендуемый в 2025 году gateway + observability + evals; важно не выбрать по старым обзорам.
  ASSESSMENT: Репозиторий archived, последний push 2026-06-11 (gh api: archived=true). Не использовать.

- Opik — уточнение по инфраструктуре (https://www.comet.com/docs/opik/self-host/local_deployment)
  WHY: Аудит оставил Opik как alternative без проверки требований.
  ASSESSMENT: Apache-2.0 подтверждена. Локальный compose поднимает MySQL, Redis, ClickHouse, ZooKeeper, MinIO и backend; документация прямо пишет, что Docker Compose 'is not meant for production deployments' (production — Helm/Kubernetes). Для
одного скромного сервера не легче Langfuse.

============================================================
PART 2 - RESEARCHER AUDIT
============================================================

## RESEARCHER RECOMMENDATIONS

### R1. NEED: Модели и провайдер: primary + fallback, tiering под бюджет <= $1
PRIMARY: Anthropic Claude API: claude-haiku-5-5 для рутинных шагов (классификация адресов, решения по hop, verification commentary, OSINT-сводки, разбор скриншотов) и claude-sonnet-5-5 для планирования, graph-синтеза и финального отчёта.
Fallback: OpenAI gpt-6-luna + gpt-6.1-sol через Responses API.
RATIONALE: Haiku 5.5 и GPT-6 Luna - самые дешёвые модели с vision, strict structured outputs и 1M context среди проверенных ($0.10/$0.50 за 1M); открытые модели у хостеров не дешевле (gpt-oss-120b $0.15/$0.60) и без vision. Ценовые сетки
Anthropic и OpenAI совпадают по обоим tier, поэтому fallback не меняет бюджет. У Anthropic документированы pinned snapshot ID, cache reads не считаются в rate limit, обучение на данных клиента запрещено договором. Цены
подтверждены тремя независимыми источниками.
ARCHITECTURE NOTES: Общий стабильный префикс (system + tools) для всех ролей одного tier, ролевая инструкция после cache breakpoint - иначе на 8 Sonnet-вызовах cache write не окупается. Держать prompt Haiku ниже 100K токенов (выше - цена x5).
Structured outputs через output_config.format, strict: true на инструментах, не более 20 strict tools и 24 optional-параметров на запрос; числовые ограничения проверять в коде. Не просить пошаговое рассуждение в структурированном
выводе - только краткое обоснование. Скриншоты уменьшать до 1568 px по длинной стороне, если мелкий текст читается. Batch API (-50%) использовать только для eval-прогонов. Жёсткий бюджет-трекер на расследование: при 70% расхода -
только Haiku, при 100% - детерминированный отчёт без LLM-текста.
COST: Модель токенов (оценка, не замер). Типичное расследование, 45 адресов, 106 вызовов. Haiku 5.5 - 98 вызовов: cache write 33 000 x $0.125/M = $0.0041; cache read 303 000 x $0.01/M = $0.0030; uncached input 268 455 x $0.10/M =
$0.0268; output 56 325 x $0.50/M = $0.0282; итого $0.062. Sonnet 5.5 - 8 вызовов (2 плана оркестратора, 2 эскалации атрибуции, 1 graph-синтез, 1 ревью писем, 2 вызова отчёта): cache write 21 000 x $2.50/M = $0.0525; cache read 13
000 x $0.10/M = $0.0013; uncached input 60 000 x $2/M = $0.120; output 16 000 x $10/M = $0.160; итого $0.334. Всего $0.40. Тяжёлый случай (60 адресов, отчёт на русском с множителем 1.8 по output, +25% повторов): 158 вызовов, около
996K input и 113K output, $0.57. Пример строки: адресная классификация, 45 вызовов x (3 500 кешированный префикс + 1 200 динамика), output 250 видимых + 50% thinking = 375: $0.00044 + $0.00154 + $0.0054 + $0.00844 = $0.0158.
Чувствительность: без кеширования $0.44; если thinking в 3 раза больше допущенного - $0.53; отчёт на Opus 5.5 - $0.54 / $0.83; всё на Haiku 5.5 - $0.08 / $0.11. Вариант без экономии (4 плана, 3 письма и отчёт на Sonnet): $0.58 /
$0.87. Остаток под платные data-API и OSINT-поиск: $0.43-0.60. Web search Anthropic стоит $0.01 за запрос.
DATA QUALITY VERIFICATION: 1) Eval-набор 50+ сценариев в Inspect AI: доля валидных tool calls, доля schema-valid ответов, точность меток >= 95% на независимом наборе, сравнение с baseline. 2) Пост-валидатор: каждый TXID и адрес в выводе LLM обязан
существовать в детерминированном хранилище фактов, иначе фрагмент отбрасывается. 3) Проверка stop_reason на каждом ответе (refusal, max_tokens) до чтения содержимого. 4) Сверка фактической стоимости по usage (input,
cache_creation, cache_read, output) с бюджетом в каждом прогоне.
RISKS: Haiku 5.5 вышел 2026-10-07 - качество на задачах атрибуции не измерено, возможно, часть шагов придётся поднять на Sonnet (каждые 10 дополнительных Sonnet-вызовов по 7K input / 1.5K output - около $0.29). Доля thinking-токенов -
допущение. Refusal от safety classifiers на материалах о мошенничестве. Start tier ограничен $500/мес. Последовательное выполнение 106 вызовов не уложится в 2 минуты - нужны параллельные Haiku-вызовы и прогрев грамматик схем при
деплое.
REPLACEABILITY: Высокая: tier-роли задаются конфигом (cheap/strong/report), обе пары моделей имеют одинаковые цены и 1M context; переключение - смена адаптера и перепрогон eval-набора.
REJECTED ALTERNATIVES:
  - Всё на Claude Sonnet 5.5 или Opus 5.5: По той же модели токенов: $1.55 (типичный) и $2.21 (тяжёлый) на Sonnet, $3.1-4.5 на Opus - выше бюджета $1.
  - Google Gemini как primary: Цены 3.8 Flash и 4 Argon удваиваются с 2027-01-01 и 2026-12-01; output Flash-Lite $2.50 против $0.50; ZDR только через Vertex AI; structured output требует валидации значений.
  - DeepSeek: Данные хранятся в КНР и могут использоваться для обучения; strict mode не заявлен; output не дешевле Haiku 5.5.
  - Self-hosting открытых моделей: Нужен GPU (около $3 950/мес за H100) при одном скромном сервере; эта сумма равна примерно 9 900 расследованиям через API.
  - Mistral, Qwen, открытые модели у Groq/Together: Не дешевле Haiku 5.5, strict structured outputs и условия хранения данных не подтверждены; оставить как trial в eval-наборе.

### R2. NEED: Gateway / слой доступа к моделям
PRIMARY: Без отдельного gateway-процесса: официальные SDK (anthropic 1.13.0, openai 3.29.0) за собственным тонким адаптером LLMClient с fallback, учётом стоимости и бюджетными лимитами.
RATIONALE: Два провайдера не оправдывают отдельный сервис на единственном сервере. Официальные SDK дают доступ к cache_control, output_config, effort и Responses API без задержки и без молчаливого отбрасывания параметров. Меньше поверхность
атаки и нет дополнительного обработчика данных.
ARCHITECTURE NOTES: Зависимости фиксировать lock-файлом с хешами. Ключи только из secret store или переменных окружения; в логи и трейсы не писать заголовки запросов. Fallback включать по 429/5xx/timeout и по stop_reason refusal; при fallback
записывать фактическую модель в trace.
COST: $0 за ПО; 200-400 строк glue-кода (оценка).
DATA QUALITY VERIFICATION: Контрактные тесты адаптера на mock-ответах обоих провайдеров; сверка стоимости, посчитанной адаптером, с usage-отчётами консолей провайдеров; тест отказа primary с переключением на fallback.
RISKS: Собственный расчёт стоимости нужно обновлять при смене цен (можно читать цены из cost map LiteLLM как справочник, не устанавливая пакет в runtime).
REPLACEABILITY: Интерфейс адаптера свой; под ним можно подставить LiteLLM SDK или OpenRouter без изменения агентов.
REJECTED ALTERNATIVES:
  - LiteLLM Proxy: Компрометация PyPI 2026-03-24 и два critical advisory по Proxy за 2026 год; отдельный сервис для маленькой команды. LiteLLM SDK допустим как библиотека с пиннингом по хешу, если провайдеров станет больше трёх.
  - OpenRouter как основной маршрут: +5.5% на пополнение, дополнительный обработчик данных, ZDR для Claude только через Vertex/Bedrock (на Bedrock без structured_outputs). Годится как запасной маршрут и для экспериментов с
  - открытыми моделями.
  - Vercel AI Gateway: Привязка к аккаунту Vercel и TypeScript-экосистеме при Python-стеке и собственном сервере.
  - Portkey: После покупки Palo Alto Networks open-source репозиторий без коммитов с 2026-05-25 и без релизов с 2026-01-12.

### R3. NEED: LLM observability: журнал действий агентов, токены, стоимость
PRIMARY: Langfuse (MIT-ядро) с инструментированием через OpenTelemetry: на старте Langfuse Cloud Hobby/Core или self-host через Docker Compose на отдельной VM 4 ядра / 16 GiB; выбор зависит от ответа владельца о размещении данных.
RATIONALE: Единственный проверенный кандидат, у которого под разрешительной лицензией бесплатно доступны tracing, учёт стоимости, версии prompt, datasets, experiments и LLM-as-judge. Самая активная разработка (релизы ежедневно), OTel-
нативный SDK. Закрывает требование логировать версии моделей, параметры и каждое действие агента.
ARCHITECTURE NOTES: Полные запросы и ответы LLM дополнительно хранить в собственной БД платформы (источник истины для воспроизводимости), Langfuse использовать как интерфейс анализа. Включить client-side masking для ключей и персональных данных.
COST: Self-host: $0 за лицензию плюс VM 4 ядра / 16 GiB / 100 GiB (цену VM не проверял). Cloud: Hobby $0 до 50k units/мес; Core $29/мес за 100k units, далее $8 за 100k. При 106 LLM-вызовах на расследование и допущении 300 units на
расследование (определение unit не проверял) Hobby покрывает около 160 расследований в месяц.
DATA QUALITY VERIFICATION: Сверка суммарной стоимости в Langfuse с usage провайдера на 20 расследованиях; проверка, что в каждом trace есть model id, effort, хеш prompt и хеш схемы; тест маскирования: поиск по трейсам шаблонов ключей API и seed-фраз должен
давать ноль совпадений.
RISKS: Docker Compose без HA и бэкапов - нужен собственный бэкап Postgres и ClickHouse; телеметрия включена по умолчанию (TELEMETRY_ENABLED) - выключить; управление retention и audit logs только в Enterprise; владелец проекта теперь
ClickHouse.
REPLACEABILITY: Высокая при OTel-инструментировании: backend меняется на Phoenix или Opik сменой OTLP endpoint.
REJECTED ALTERNATIVES:
  - Arize Phoenix: ELv2 вместо OSI-лицензии - нужна юридическая проверка для коммерческого SaaS; оставить запасным вариантом, если 16 GiB для Langfuse недоступны.
  - LangSmith: Закрытая платформа, self-host только Enterprise, base traces хранятся 14 дней.
  - Braintrust: SaaS, on-prem только Enterprise, $249/мес за Pro, 14 дней хранения на бесплатном плане.
  - Helicone: Maintenance mode после покупки Mintlify; последний релиз 2025-08-21.

### R4. NEED: Evals: 50+ сценариев с ground truth, AI-слой против baseline
PRIMARY: Inspect AI (MIT) как раннер eval-набора; сценарии в JSONL с ground truth; scorers на Python поверх детерминированного трассировщика.
RATIONALE: Python-нативный (общий код с платформой), MIT, поддерживается государственным институтом, провайдеры Anthropic/OpenAI/Google/OpenRouter/mock в коде, новые модели добавляются в день релиза. Есть лимиты, кеш, batch-режим (-50% на
прогонах) и лог-файлы для аудита.
ARCHITECTURE NOTES: Набор сценариев версионировать в git вместе с prompt; независимый тестовый набор меток не использовать при настройке prompt.
COST: ПО $0. Прогон 50 сценариев по $0.40-0.57: $20-29 синхронно, $10-14 через Batch API.
DATA QUALITY VERIFICATION: Метрики на сценарий: точность и полнота найденных конечных адресов против ground truth, точность меток на независимом наборе (цель >= 95%), доля утверждений с TXID (цель 100%), число выдуманных TXID (цель 0), стоимость и время.
Baseline прогоняется тем же scorer; AI-слой должен превосходить его статистически (парное сравнение по сценариям). Прогон обязателен при любой смене model id, effort или prompt.
RISKS: Версия 0.3.x - возможны изменения API; LLM-судьи вносят собственную ошибку - для меток и TXID использовать только детерминированные scorers.
REPLACEABILITY: Высокая: датасет и scorers - собственные файлы.
REJECTED ALTERNATIVES:
  - promptfoo: TypeScript и Node 22.22+ при Python-платформе; владелец - OpenAI. Допустим как лёгкий регрессионный тест prompt в CI.
  - DeepEval: Телеметрия в PostHog включена по умолчанию; готовые метрики ориентированы на RAG/чат, а не на граф и TXID.
  - Braintrust / LangSmith evals: SaaS с коротким хранением и без self-host на доступных тарифах.

### R5. NEED: Воспроизводимость: пиннинг версий моделей и параметров
PRIMARY: Конфиг моделей в git + полный журнал запросов и ответов; точные ID claude-haiku-5-5 и claude-sonnet-5-5 (pinned snapshots), явный effort на каждом вызове.
RATIONALE: Документация Anthropic гарантирует неизменность весов для ID, но не поведения serving-инфраструктуры, а temperature на актуальных моделях задать нельзя. Поэтому воспроизводимость достигается воспроизведением из журнала, а не
повторной генерацией.
ARCHITECTURE NOTES: В каждой записи журнала: model id из ответа, request id, SHA-256 system prompt, схем инструментов и output-схемы, effort, max_tokens, конфигурация thinking, версии SDK, usage, stop_reason, полный ответ. Параметр effort задавать
явно: default различается (Haiku medium, Sonnet high, Opus medium). Версии prompt помечать и в Langfuse, и в git.
COST: $0; хранение журнала - единицы MB на расследование (оценка).
DATA QUALITY VERIFICATION: Тест: по журналу расследования отчёт пересобирается без вызовов LLM и совпадает побайтно. Еженедельный canary-прогон 10 сценариев для обнаружения дрейфа поведения при неизменном model id.
RISKS: Retirement моделей не ранее сентября-октября 2027 - потребуется миграция с перепрогоном eval-набора; для OpenAI способ жёсткого пиннинга не подтверждён.
REPLACEABILITY: Не зависит от провайдера.
REJECTED ALTERNATIVES:
  - temperature=0 и seed: На Claude Haiku 5.5 не-default sampling-параметры возвращают 400; для GPT-6 поддержка не подтверждена.
  - Alias вида latest: У Gemini alias latest меняется с уведомлением за 2 недели; у OpenAI датированные snapshot для GPT-6 на странице модели не показаны.

## LIVE PROBE FINDINGS
- GET https://openrouter.ai/api/v1/models (HTTP 200, 771 KB, 461 модель): цены Claude Haiku 5.5 $0.10/$0.50 (override при prompt >= 100 000: $0.50/$2.50), Sonnet 5.5 $2/$10 (cache read $0.10), Opus 5.5 $4/$20, GPT-6 Luna
$0.10/$0.50, GPT-6.1 Sol $2/$10, Gemini 3.8 Flash $0.75/$3.75, Gemini 4 Argon $2/$10 совпали с официальными страницами провайдеров.
- Тот же каталог: canonical slug содержит даты snapshot - anthropic/claude-haiku-5.5-20261007, claude-sonnet-5.5-20260928, claude-opus-5.5-20260921, openai/gpt-6-luna-20260922, gpt-6.1-sol-20260929, google/gemini-4-argon-20261013.
- GET https://openrouter.ai/api/v1/endpoints/zdr (HTTP 200, 944 endpoints): Claude Haiku 5.5 и Sonnet 5.5 присутствуют только через Google и Amazon Bedrock, GPT-6 Luna - только через Azure; first-party endpoints Anthropic и OpenAI в
ZDR-списке не найдены.
- GET https://openrouter.ai/api/v1/models/anthropic/claude-haiku-5.5/endpoints: 10 endpoints (Anthropic, Google, Azure, Amazon Bedrock, Claude Platform on AWS); параметр structured_outputs объявлен у Anthropic, Google и Azure и
отсутствует у Amazon Bedrock и Claude Platform on AWS; uptime за 30 минут 100% у first-party, 93.3% у одного из Bedrock endpoints.
- GET raw.githubusercontent.com/BerriAI/litellm/main/model_prices_and_context_window.json (2.8 MB, 4 084 записи): claude-haiku-5-5 уже есть с input_cost_per_token_above_100k_tokens = 5e-07; gpt-6-luna max_input_tokens = 922 000;
deepseek-flash записан по peak-цене ($0.30/$1.20).
- gh api repos/BerriAI/litellm/security-advisories: critical 2026-09-30 (privilege escalation через salt key), critical 2026-05-28 (auth bypass через Host header), high 2026-10-01 (чтение локальных файлов), medium SSRF 2026-08-26.
Issues #24512 и #24514 от 2026-03-24 подтверждают вредоносные версии 1.82.7 и 1.82.8 на PyPI.
- Чтение кода litellm/llms/anthropic/chat/transformation.py: output_config.format и effort поддержаны, но есть ветка с логом 'Dropping unsupported output_config for model' - параметр может быть отброшен без ошибки.
- Чтение langfuse/docker-compose.yml: сервисы langfuse-web:4, langfuse-worker:4, clickhouse-server:25.12, postgres:17, redis:7, minio; TELEMETRY_ENABLED по умолчанию true. LICENSE: copyright ClickHouse, Inc., MIT вне каталогов ee/.
- Чтение Arize-ai/phoenix LICENSE: Elastic License 2.0 с запретом предоставлять ПО третьим лицам как hosted/managed service.
- Чтение deepeval/telemetry/client.py: зашиты PostHog project key и host https://us.i.posthog.com; отключение через DEEPEVAL_TELEMETRY_OPT_OUT.
- gh api repos/Portkey-AI/gateway: последний коммит 2026-05-25, последний релиз v1.15.2 от 2026-01-12. gh api repos/Helicone/helicone: последний релиз 2025-08-21, последний коммит 2026-09-16.
- promptfoo README (gh api): 'Promptfoo is now part of OpenAI. Promptfoo remains open source and MIT licensed.'; package.json: версия 0.124.1, license MIT, node >=22.22.0.
- Inspect AI, каталог src/inspect_ai/model/_providers: файлы anthropic.py, openai.py, openai_responses.py, google.py, mistral.py, deepseek.py, groq.py, together.py, fireworks.py, openrouter.py, ollama.py, vllm.py, mockllm.py, а
также _anthropic_batch.py и _openai_batch.py.

## CANDIDATES (full audit cards)

### [RECOMMENDED] Anthropic Claude API: Claude Haiku 5.5 (рутина) + Claude Sonnet 5.5 (планирование, отчёт); Claude Opus 5.5 опционально
NEED: LLM с tool calling и strict structured outputs (основной провайдер)
KIND: public API / model
URL: https://platform.claude.com/docs/en/about-claude/pricing
LICENSE: Проприетарный API; Commercial Terms of Service (версия от 2025-06-17)
COMMERCIAL USE: Разрешено: Commercial Terms, раздел A.1 прямо разрешает использовать сервис в продуктах для собственных клиентов. Запрещено: перепродажа доступа без согласия Anthropic, создание конкурирующих моделей. Outputs принадлежат клиенту;
обучение на Customer Content запрещено (раздел B).
PROJECT STATE: Актуальная линейка (models overview): claude-haiku-5-5 (релиз 2026-10-07, retirement не ранее 2027-10-07), claude-sonnet-5-5 (retirement не ранее 2027-09-28), claude-opus-5-5 (не ранее 2027-09-22), claude-fable-5-1. Все: context
1M, max output 128K, knowledge cutoff Jun 2026, вход text+image. Официальный Python SDK anthropic 1.13.0 (MIT, релиз 2026-10-09, Python >=3.10).
CLAIMED VS ACTUAL: 1) Заявлено, что structured outputs 'always valid'; та же страница оговаривает: при stop_reason refusal или max_tokens вывод может не соответствовать схеме, значения enum могут отличаться регистром. 2) Ограничения схем: до 20
strict tools, 24 optional-параметров, 16 anyOf; нет рекурсивных схем, minimum/maximum, minLength/maxLength; первая компиляция грамматики добавляет латентность (кеш 24 ч). 3) 'Haiku 5.5 от $0.10': при prompt >100K токенов цена в 5
раз выше ($0.50/$2.50). 4) Dateless ID объявлены pinned snapshot, но документация признаёт, что serving-инфраструктура (router, classifiers, sampling) может менять поведение. 5) Расхождение по хранению: privacy-статья говорит об
удалении inputs/outputs в течение 30 дней, страница api-and-data-retention - 'conversation content is not retained by default'. 6) На Haiku 5.5 нельзя задать temperature/top_p/top_k (не-default значения дают 400), то есть
temperature=0 недоступна. 7) Новый tokenizer даёт примерно на 30% больше токенов на тот же текст.
CAPABILITIES: Tool use, strict tools (strict: true), structured outputs через output_config.format (GA, constrained decoding) на Haiku 5.5 / Sonnet 5.5 / Opus 5.5. Prompt caching (минимальный кешируемый префикс 512 токенов, TTL 5 мин или 1
час). Batch API -50%. Vision: до 600 изображений на запрос, до 10 MB каждое, JPEG/PNG/GIF/WebP; стоимость ceil(w/28)*ceil(h/28) токенов, скриншот 1920x1080 = 2 691 токен (на Haiku 5.5 это $0.00027). Adaptive thinking и параметр
effort (default: Haiku medium, Sonnet high, Opus medium).
INFRA: Только исходящий HTTPS; ключ в secret store. Изображения до 10 MB, запрос до 32 MB.
PRICING/LIMITS: За 1M токенов (input / cache write 5m / cache read / output): Haiku 5.5 $0.10 / $0.125 / $0.01 / $0.50 (при prompt >100K: $0.50 / $0.625 / $0.05 / $2.50); Sonnet 5.5 $2 / $2.50 / $0.10 / $10; Opus 5.5 $4 / $5 / $0.20 / $20; Fable
5.1 $10 / $12.50 / $0.25 / $50. Batch -50%. Системный prompt tool use +286 токенов. Web search $10 за 1000 запросов. Rate limits Start tier: 1 000 RPM, 2M ITPM, 400K OTPM на модель; cache reads не считаются в ITPM. Месячный spend
cap: Start $500, Build $1 000, Scale $200 000. Новые организации могут начинать в Evaluation tier с лимитами ниже.
RISKS: Haiku 5.5 вышел за 7 дней до аудита, независимой статистики надёжности tool calling нет. Safety classifiers могут вернуть stop_reason refusal (HTTP 200) - нужен обработчик и fallback. ZDR только через sales, на организацию; Batch
и Files API под ZDR не попадают; помеченный контент может храниться до 2 лет. Sonnet 5.5 и Opus 5.5 не принимают forced tool_choice (any/tool) - по справке claude-api skill. Batch (до 24 ч) не подходит под цель <= 2 мин.
REPLACEABILITY: Высокая при тонком адаптере: ценовая сетка OpenAI GPT-6 Luna / GPT-6.1 Sol идентична, набор возможностей тот же. Привязка только в cache_control, output_config и effort.
HOW VERIFIED: Прочитаны официальные страницы pricing, models overview, rate limits, structured outputs, api-and-data-retention, model-ids-and-versions, vision, Haiku 5.5 overview, Commercial Terms (WebFetch 2026-10-14). Цены независимо сверены
с OpenRouter /api/v1/models (живой GET) и с model_prices_and_context_window.json в репозитории LiteLLM - все три источника совпали. Реальные вызовы API не делались (ключи запрещены правилами аудита).
CONFIDENCE: high
EVIDENCE: https://platform.claude.com/docs/en/about-claude/pricing | https://platform.claude.com/docs/en/about-claude/models/overview | https://platform.claude.com/docs/en/api/rate-limits | https://platform.claude.com/docs/en/build-with-claude/structured-outputs | https://platform.claude.com/docs/en/build-with-claude/api-and-data-retention | https://platform.claude.com/docs/en/about-claude/models/model-ids-and-versions

### [ALTERNATIVE] OpenAI API: GPT-6 Luna (рутина) + GPT-6.1 Sol (сильная модель)
NEED: LLM с tool calling и strict structured outputs (fallback-провайдер)
KIND: public API / model
URL: https://developers.openai.com/api/docs/pricing
LICENSE: Проприетарный API; Services Agreement прочитать не удалось (HTTP 403)
COMMERCIAL USE: По странице 'your data': данные API по умолчанию не используются для обучения (с 2023-03-01). Текст Services Agreement о коммерческом использовании не получен - см. not_verified.
PROJECT STATE: Линейка на странице models: gpt-6-astra, gpt-6.1-sol, gpt-6-luna; на pricing также gpt-6-sol, gpt-5.6-sol/terra/luna и старые. Context 1.05M (max input 922K), max output 128K; knowledge cutoff 2026-04-30 (Astra, 6.1 Sol),
2026-05-18 (Luna). SDK openai-python 3.29.0 (Apache-2.0, релиз 2026-10-11).
CLAIMED VS ACTUAL: 1) Заявлен context 1.05M, но max input 922K. 2) Для gpt-6-luna function calling в Chat Completions работает только при reasoning_effort none; полноценно - только через Responses API. Это важно для gateway, работающих через Chat
Completions. 3) На странице модели нет датированных snapshot ID (указан только gpt-6-luna как default snapshot); OpenRouter показывает canonical slug openai/gpt-6-luna-20260922. Способ жёсткого пиннинга не подтверждён. 4) GPT-6
имеет отдельную плату за cache write ($0.125 Luna, $2.50 Sol). 5) Structured Outputs: refusal и incomplete-ответы могут не соответствовать схеме. 6) GPT-5.6 Sol: на странице OpenAI промо-цена до 2026-11-21 как минимум; извлечённая
таблица ($4/$20) расходится с OpenRouter ($2/$10) - не используем.
CAPABILITIES: Function calling, Structured Outputs (json_schema), image input, prompt caching, Batch, Responses и Chat Completions. Reasoning effort: none/low/medium/high/xhigh/max (Luna).
INFRA: Только исходящий HTTPS.
PRICING/LIMITS: За 1M (input / cached / output): gpt-6-luna $0.10 / $0.01 / $0.50; gpt-6.1-sol $2 / $0.10 / $10; gpt-6-astra $10 / $1 / $50. Batch и Flex -50%. При >272K input: input x2, output x1.5. Data residency +10%. Web search $10 за 1000
вызовов. Tiers: Build (покупка $5) - лимит $500/мес, Luna 5 000 RPM / 2M TPM, Sol 5 000 RPM / 1M TPM; Launch ($100) - $5 000/мес; Grow ($500) - $200 000/мес.
RISKS: Abuse-логи до 30 дней; ZDR и Modified Abuse Monitoring только по одобрению sales; Batch и Files не ZDR-eligible; загруженные изображения сканируются, помеченные сохраняются. Пиннинг версии не подтверждён. Поддержка
temperature/seed на GPT-6 не указана.
REPLACEABILITY: Высокая: используется как зеркальный fallback к Anthropic с той же tier-схемой и ценами.
HOW VERIFIED: Прочитаны developers.openai.com: pricing, models, models/gpt-6-luna, guides/your-data, guides/structured-outputs, guides/rate-limits (WebFetch 2026-10-14). Цены сверены с OpenRouter API и cost map LiteLLM - совпали.
openai.com/api/pricing и services-agreement вернули 403.
CONFIDENCE: medium
EVIDENCE: https://developers.openai.com/api/docs/pricing | https://developers.openai.com/api/docs/models | https://developers.openai.com/api/docs/models/gpt-6-luna | https://developers.openai.com/api/docs/guides/your-data | https://developers.openai.com/api/docs/guides/structured-outputs | https://developers.openai.com/api/docs/guides/rate-limits

### [ALTERNATIVE] Google Gemini API: Gemini 3.5 Flash-Lite / 3.8 Flash / Gemini 4 Argon
NEED: LLM с tool calling и structured outputs (альтернативный провайдер)
KIND: public API / model
URL: https://ai.google.dev/gemini-api/docs/pricing
LICENSE: Проприетарный API; Gemini API Additional Terms (effective 2026-03-23)
COMMERCIAL USE: Paid Services предназначены для профессионального/бизнес-использования; prompts и responses платного уровня не используются для улучшения продуктов. Для пользователей в EEA/UK/Швейцарии разрешены только Paid Services. Запрещена
разработка конкурирующих моделей.
PROJECT STATE: Страница pricing обновлена 2026-10-13. Stable: gemini-4-argon (в каталоге OpenRouter с 2026-10-13), gemini-3.8-flash, gemini-3.6-flash, gemini-3.5-flash-lite; context 1 048 576, max output 65 536 (по OpenRouter и LiteLLM). SDK
google-genai 2.30.1 (Apache-2.0).
CLAIMED VS ACTUAL: 1) Цены временные: Gemini 4 Argon $2/$10 только до 2026-11-30, с 2026-12-01 - $4/$20; 3.8 Flash и 3.6 Flash $0.75/$3.75 до 2026-12-31, с 2027-01-01 - $1.50/$7.50. 2) Про structured output документация сама пишет: JSON
синтаксически корректен, но значения нужно валидировать в приложении. 3) Совмещение structured output с function calling - preview. 4) ZDR на Developer API не гарантируется (abuse-логи 'limited period' без числа дней);
гарантированный ZDR - только Vertex AI. 5) Free tier использует данные для улучшения продуктов.
CAPABILITIES: Function calling, structured output (подмножество JSON Schema, включая minimum/maximum и рекурсию через $ref), вход image/video/audio/PDF, context caching, Batch -50%.
INFRA: Только исходящий HTTPS; проект Google Cloud с billing.
PRICING/LIMITS: За 1M (input / output): gemini-3.5-flash-lite $0.30 / $2.50 (cache $0.03); gemini-3.8-flash $0.75 / $3.75 до 2026-12-31, затем $1.50 / $7.50; gemini-4-argon $2 / $10 до 2026-11-30, затем $4 / $20; gemini-2.5-flash-lite $0.10 /
$0.40. Tiers: Tier 1 - привязка billing (cap $250), Tier 2 - $100 расходов + 3 дня (cap $2 000), Tier 3 - $1 000 + 30 дней. RPM/TPM по моделям на странице не опубликованы.
RISKS: Удвоение цен через 1.5-2.5 месяца после аудита; alias 'latest' меняется с уведомлением за 2 недели; output дороже, чем у Haiku 5.5 и GPT-6 Luna, в 5 раз ($2.50 против $0.50).
REPLACEABILITY: Высокая через адаптер; отдельный SDK и формат схем.
HOW VERIFIED: Прочитаны ai.google.dev: pricing (дважды, с уточнением дат), models, rate-limits, terms, structured-output, zdr (WebFetch 2026-10-14). Цены сверены с OpenRouter API и LiteLLM cost map - совпали.
CONFIDENCE: medium
EVIDENCE: https://ai.google.dev/gemini-api/docs/pricing | https://ai.google.dev/gemini-api/docs/models | https://ai.google.dev/gemini-api/docs/rate-limits | https://ai.google.dev/gemini-api/terms | https://ai.google.dev/gemini-api/docs/structured-output | https://ai.google.dev/gemini-api/docs/zdr

### [REJECTED] DeepSeek API (deepseek-flash = V4.1 Flash, deepseek-v4-pro)
NEED: Дешёвая модель для рутинных шагов
KIND: public API / model
URL: https://api-docs.deepseek.com/quick_start/pricing
LICENSE: Проприетарный API; веса DeepSeek-V4.1-Flash опубликованы на Hugging Face (лицензию весов не проверял)
COMMERCIAL USE: Условия использования API отдельно не прочитаны. Privacy Policy (обновлена 2026-02-10): данные собираются, обрабатываются и хранятся в КНР; User Input может использоваться для обучения моделей, есть право opt-out.
PROJECT STATE: Актуальные модели: deepseek-flash (DeepSeek-V4.1-Flash, vision) и deepseek-v4-pro (V4-Pro-0813, без vision). Context 1M, max output 384K. Старые имена deepseek-v4-flash обслуживаются новой моделью.
CLAIMED VS ACTUAL: 1) Цена зависит от времени суток: off-peak вдвое дешевле peak; peak - 01:00-04:00 и 06:00-10:00 UTC по будням. 2) В каталоге OpenRouter цена deepseek-v4.1-flash $0.044/$0.765 не совпадает с официальной ($0.15-0.30 / $0.60-1.20),
потому что OpenRouter показывает сторонних хостеров. 3) Output $0.60-1.20 за 1M - дороже, чем у Haiku 5.5 ($0.50), то есть ценового выигрыша на рутине нет.
CAPABILITIES: JSON Output, Tool Calls, Responses API и Anthropic-совместимый API. Strict mode в таблице возможностей не указан.
PRICING/LIMITS: За 1M (off-peak / peak): deepseek-flash input cache miss $0.15 / $0.30, cache hit $0.003 / $0.006, output $0.60 / $1.20; deepseek-v4-pro input $0.66 / $1.32, output $1.98 / $3.96. Concurrency limit 2 500 (flash), 500 (pro).
RISKS: Хранение данных жертв (скриншоты, переписка) в КНР и возможное обучение на них несовместимо с продуктом по расследованию краж; гарантированной schema-валидации (strict) не заявлено.
REPLACEABILITY: Высокая (OpenAI- и Anthropic-совместимый API).
HOW VERIFIED: Прочитаны официальная страница pricing и Privacy Policy (WebFetch 2026-10-14); сверка с OpenRouter API, LiteLLM cost map и страницей Together.
CONFIDENCE: medium
EVIDENCE: https://api-docs.deepseek.com/quick_start/pricing | https://cdn.deepseek.com/policies/en-US/deepseek-privacy-policy.html | https://www.together.ai/pricing

### [NEEDS-TRIAL] Mistral API (Mistral Small 4, Mistral Large 4, OCR 4.1)
NEED: Дешёвая/европейская модель; open-weight вариант
KIND: public API / model (часть моделей open-weight)
URL: https://docs.mistral.ai/inference/pricing
LICENSE: API проприетарный; веса Mistral Small 4 - Apache 2.0, Medium 3.5 - Modified MIT, Ministral 3 - Apache 2.0 (по странице models overview)
COMMERCIAL USE: Условия API не читал. Веса Small 4 под Apache 2.0 допускают коммерческое использование.
PROJECT STATE: Mistral Large 4 (v26.10, в каталоге OpenRouter с 2026-10-06), Medium 3.5 (v26.04), Small 4 (v26.03), Ministral 3 (v25.12); линейка Magistral помечена deprecated.
CLAIMED VS ACTUAL: Расхождение цен между страницами: mistral.ai/pricing показывает Mistral Large $0.50/$1.50, docs.mistral.ai - Large 4 $0.68/$2.09 как sale (list $1.36/$4.18). Срок действия sale не указан. API model id на странице даны как slug, не
как подтверждённые идентификаторы.
CAPABILITIES: По данным OpenRouter и LiteLLM: tools, structured_outputs/response_format, vision; context 262K (Small 4), 1M (Large 4). OCR 4.1 с bounding boxes.
PRICING/LIMITS: За 1M (input / cached / output): Small 4 $0.15 / $0.015 / $0.60; Large 4 $0.68 / $0.07 / $2.09 (sale; list $1.36 / $0.14 / $4.18); Medium 3.5 $1.50 / $0.15 / $7.50. OCR 4.1 - $4 за 1000 страниц. Batch -50% (mistral.ai/pricing).
RISKS: Small 4 дороже Haiku 5.5 по input ($0.15 против $0.10) и output ($0.60 против $0.50). Надёжность strict structured outputs не подтверждена первичной документацией. Rate limits и retention не проверены.
REPLACEABILITY: Высокая.
HOW VERIFIED: Прочитаны mistral.ai/pricing, docs.mistral.ai/inference/pricing, docs.mistral.ai models overview (WebFetch); сверка с OpenRouter API.
CONFIDENCE: low
EVIDENCE: https://mistral.ai/pricing | https://docs.mistral.ai/inference/pricing | https://docs.mistral.ai/getting-started/models/models_overview/

### [REJECTED] Qwen через Alibaba Cloud Model Studio (qwen3.8-max, qwen-plus, qwen-flash)
NEED: Дешёвая модель для рутинных шагов
KIND: public API / model
URL: https://www.alibabacloud.com/help/en/model-studio/model-pricing
LICENSE: Проприетарный API; часть весов Qwen открыта (лицензии не проверял)
COMMERCIAL USE: Не проверено (условия Model Studio не читал).
PROJECT STATE: В каталоге OpenRouter: qwen3.8-max-0902 (2026-09-03), qwen3.8-flash (2026-08-26), qwen3.7-flash (2026-07-27).
CLAIMED VS ACTUAL: Цена qwen-plus и qwen-flash ступенчатая: при input >256K - в 3-5 раз выше.
CAPABILITIES: Context до 1M; context cache (hit 10% цены, явное создание 125%); batch -50%, не суммируется с cache. Поддержка function calling и JSON schema на странице цен не указана; у qwen3.7-flash на OpenRouter нет параметра
structured_outputs.
PRICING/LIMITS: Singapore, за 1M (input / output): qwen3.8-max $2 / $6; qwen-plus $0.40 / $1.20 (non-thinking, <=256K); qwen-flash $0.05 / $0.40 (<=256K).
RISKS: Юрисдикция и политика хранения данных не проверены; strict structured outputs не подтверждены; qwen3.8-max не дешевле Sonnet 5.5 по input.
REPLACEABILITY: Высокая.
HOW VERIFIED: Прочитана страница model-pricing (первые 100K символов из 139K); сверка с OpenRouter API.
CONFIDENCE: low
EVIDENCE: https://www.alibabacloud.com/help/en/model-studio/model-pricing | https://openrouter.ai/api/v1/models

### [NEEDS-TRIAL] Открытые модели через хостинг: Groq, Together AI, Fireworks (gpt-oss-120b, Qwen, GLM, DeepSeek)
NEED: Cost-efficient вариант для рутинных шагов
KIND: commercial SaaS (inference open-weight моделей)
URL: https://console.groq.com/docs/models
LICENSE: Зависит от модели; условия хостеров не читал
COMMERCIAL USE: Не проверено по условиям хостеров.
PROJECT STATE: Groq production: openai/gpt-oss-120b (около 500 ток/с, context 131 072, max output 65 536), openai/gpt-oss-20b, llama-3.3-70b-versatile, llama-3.1-8b-instant. Together serverless: Qwen3.8, Kimi K3, GLM-5.3, DeepSeek V4.x, gpt-
oss-120B.
CLAIMED VS ACTUAL: 1) Groq: для Llama-моделей цена на странице - 'Contact sales'. 2) Fireworks: страница pricing не содержит цен serverless-чата за токен. 3) Самый дешёвый открытый вариант (gpt-oss-120b, $0.15/$0.60) дороже Claude Haiku 5.5 и GPT-6
Luna ($0.10/$0.50) и уступает по context и vision - ценового смысла в MVP нет.
CAPABILITIES: В каталоге OpenRouter gpt-oss-120b помечен как tools + structured_outputs; вход только text (нет vision). Knowledge cutoff gpt-oss-120b: 2024-06-30.
PRICING/LIMITS: Groq: gpt-oss-120b $0.15 / $0.60, gpt-oss-20b $0.075 / $0.30, qwen3.8-27b (preview) $0.80 / $4.00. Together: gpt-oss-120B $0.15 / $0.60; DeepSeek V4.1 Flash $0.30 / $1.20; GLM-5.3-Flash $0.15 / $0.50; Qwen3.7-Max $1.50 / $4.50;
Llama 3.3 70B $1.04 / $1.04; dedicated H100 $5.49/час. Fireworks on-demand: H100 $8/час, B200 $13/час.
RISKS: Качество tool calling у открытых моделей зависит от хостера и квантизации; нет vision у gpt-oss; rate limits и retention не проверены.
REPLACEABILITY: Высокая (OpenAI-совместимые API).
HOW VERIFIED: Прочитаны console.groq.com/docs/models, together.ai/pricing, fireworks.ai/pricing (WebFetch); сверка с OpenRouter API и LiteLLM cost map.
CONFIDENCE: medium
EVIDENCE: https://console.groq.com/docs/models | https://www.together.ai/pricing | https://fireworks.ai/pricing

### [REJECTED] Self-hosting открытых моделей (vLLM, Ollama)
NEED: Независимость от API-провайдеров и контроль данных
KIND: open-source
URL: https://github.com/vllm-project/vllm
LICENSE: vLLM - Apache-2.0; Ollama - MIT
COMMERCIAL USE: Разрешено лицензиями инструментов; лицензии весов проверять по каждой модели.
PROJECT STATE: vLLM: 93 730 звёзд, v0.31.0 (2026-10-05), коммиты 2026-10-13, 8 813 открытых issues. Ollama: 183 045 звёзд, v0.40.3 (2026-10-11), коммиты 2026-10-13. Оба не archived, есть tests и CI.
CLAIMED VS ACTUAL: none found
CAPABILITIES: OpenAI-совместимый сервер; guided decoding / JSON schema и tool calling зависят от модели и шаблона чата (в коде не проверял).
INFRA: GPU-сервер; на одном скромном сервере без GPU конкурентные модели не запускаются.
PRICING/LIMITS: ПО бесплатно. GPU: выделенный H100 у Together $5.49/час - это около $3 950 в месяц при 24/7. При $0.40 за расследование на API эта сумма покрывает около 9 900 расследований в месяц.
RISKS: Не укладывается в ограничение 'один скромный сервер, маленькая команда'; эксплуатация и качество tool calling ложатся на команду.
REPLACEABILITY: Высокая (OpenAI-совместимый endpoint подключается через тот же адаптер).
HOW VERIFIED: GitHub API (gh api repos/...): лицензия, pushed_at, релизы, коммиты, workflows. Цены GPU - со страниц Together и Fireworks.
CONFIDENCE: medium
EVIDENCE: https://github.com/vllm-project/vllm | https://github.com/ollama/ollama | https://www.together.ai/pricing

### [RECOMMENDED] Официальные SDK провайдеров (anthropic, openai, google-genai) за тонким собственным адаптером
NEED: Слой доступа к моделям (вместо отдельного gateway)
KIND: open-source
URL: https://github.com/anthropics/anthropic-sdk-python
LICENSE: anthropic - MIT; openai - Apache-2.0; google-genai - Apache-2.0
COMMERCIAL USE: Разрешено без условий (MIT / Apache-2.0).
PROJECT STATE: anthropic 1.13.0 (2026-10-09, Python >=3.10, 3 967 звёзд, CI); openai 3.29.0 (2026-10-11, 31 840 звёзд); google-genai 2.30.1 (2026-10-13). Все активны, генерируются из спецификаций API (Stainless).
CLAIMED VS ACTUAL: none found
CAPABILITIES: Полный доступ к функциям провайдера в день релиза: cache_control, output_config.format и effort, strict tools, Responses API OpenAI (нужен для function calling с reasoning на GPT-6 Luna).
INFRA: Нет отдельного процесса; библиотеки в приложении.
PRICING/LIMITS: Бесплатно; без наценки и без дополнительного сетевого хопа.
RISKS: Fallback, учёт стоимости и бюджетные лимиты пишутся самостоятельно (по оценке, 200-400 строк glue-кода).
REPLACEABILITY: Адаптер - собственный интерфейс; под ним можно позже подставить LiteLLM или OpenRouter.
HOW VERIFIED: GitHub API: лицензии, релизы, коммиты; pyproject.toml прочитан через gh api contents.
CONFIDENCE: high
EVIDENCE: https://github.com/anthropics/anthropic-sdk-python | https://github.com/openai/openai-python | https://github.com/googleapis/python-genai

### [ALTERNATIVE] LiteLLM (Python SDK и Proxy)
NEED: Gateway / унификация провайдеров
KIND: open-source (open core)
URL: https://github.com/BerriAI/litellm
LICENSE: MIT для всего вне каталога enterprise/ (у enterprise/ отдельная лицензия); GitHub API показывает NOASSERTION
COMMERCIAL USE: Разрешено для MIT-части. SSO/SAML, audit logs - Enterprise.
PROJECT STATE: 61 165 звёзд, 5 548 открытых issues, pushed 2026-10-13, релиз v1.105.0 (2026-10-11), pyproject 1.107.0, Python >=3.10,<3.15, 136 workflows, каталог tests. Не archived.
CLAIMED VS ACTUAL: 1) Supply-chain компрометация PyPI 2026-03-24: версии 1.82.7 и 1.82.8 содержали credential stealer (litellm_init.pth), подтверждено issues #24512, #24514, #24518. 2) Поток security advisories по Proxy: critical 2026-09-30
(privilege escalation через salt key), critical 2026-05-28 (auth bypass через Host header), high 2026-10-01, medium SSRF 2026-08-26. 3) В коде есть ветка 'Dropping unsupported output_config for model' - параметры могут молча
отбрасываться, что вредит воспроизводимости. 4) Документация размыто разделяет бесплатные и Enterprise-функции (spend tracking указан в обоих списках).
CAPABILITIES: Единый интерфейс к 100+ провайдерам, Router (retry/fallback), расчёт стоимости по cost map (4 084 записи; claude-haiku-5-5 уже есть вместе с tier >100K), callbacks в Langfuse/OTel. В адаптере Anthropic (transformation.py, 129 KB)
есть поддержка output_config.format и effort.
INFRA: SDK - библиотека. Proxy - отдельный контейнер; требования к Postgres/Redis в прочитанной странице не указаны.
PRICING/LIMITS: Бесплатно (MIT-часть). Enterprise - по запросу.
RISKS: Большая поверхность атаки и история инцидентов; отставание или молчаливое отбрасывание новых параметров провайдеров; GPT-6 Luna с tool calling требует Responses API.
REPLACEABILITY: Высокая (OpenAI-формат).
HOW VERIFIED: GitHub API (метаданные, релизы, issues, security-advisories), прочитаны LICENSE, pyproject.toml, фрагменты litellm/llms/anthropic/chat/transformation.py, model_prices_and_context_window.json (raw); docs.litellm.ai.
CONFIDENCE: high
EVIDENCE: https://github.com/BerriAI/litellm | https://github.com/BerriAI/litellm/issues/24512 | https://github.com/BerriAI/litellm/issues/24518 | https://github.com/BerriAI/litellm/security/advisories | https://raw.githubusercontent.com/BerriAI/litellm/main/model_prices_and_context_window.json | https://docs.litellm.ai/docs/

### [ALTERNATIVE] OpenRouter
NEED: Gateway / единый ключ ко многим моделям, запасной маршрут
KIND: commercial SaaS
URL: https://openrouter.ai/docs/faq
LICENSE: Проприетарный сервис; Terms обновлены 2026-08-31
COMMERCIAL USE: Terms допускают встраивание в собственные продукты (п. 5.1), но запрещают перепродажу доступа к API (п. 7.4), требуют соблюдать условия каждой модели и передавать их клиентам (п. 5.2); п. 16 снимает гарантии пригодности для
customer-facing использования.
PROJECT STATE: Живой каталог: 461 модель (GET /api/v1/models, 2026-10-14); новые модели появляются в день релиза (gemini-4-argon - 2026-10-13).
CLAIMED VS ACTUAL: 1) 'No markup' на inference верно, но покупка кредитов облагается 5.5% (минимум $0.80), crypto - 5%; BYOK бесплатно до $25 000/мес, далее 5%. 2) В ZDR-списке Claude Haiku 5.5 и Sonnet 5.5 есть только через Google и Amazon Bedrock,
first-party endpoint Anthropic в списке отсутствует; GPT-6 Luna - только через Azure. 3) Для Haiku 5.5 endpoints Amazon Bedrock и Claude Platform on AWS не объявляют параметр structured_outputs, то есть ZDR-маршрут через Bedrock
теряет strict-схемы. 4) Цена открытых моделей в каталоге - это цена конкретного стороннего хостера, она не совпадает с официальной ценой автора модели.
CAPABILITIES: Автоматический fallback между провайдерами, параметры tools / structured_outputs по каждому endpoint, ZDR на уровне аккаунта, guardrail и запроса, список ZDR-endpoints (944 записи).
INFRA: Только исходящий HTTPS.
PRICING/LIMITS: Цены моделей равны ценам провайдеров; +5.5% на пополнение. Бесплатные модели: 50 запросов/день, 1 000/день после покупки 10 кредитов. Лимиты платных аккаунтов в FAQ не приведены.
RISKS: Дополнительный обработчик данных между платформой и провайдером; +5.5% к бюджету $1; специфичные функции провайдера (cache_control, effort) доступны с задержкой или через нормализацию.
REPLACEABILITY: Высокая (OpenAI-совместимый API).
HOW VERIFIED: Живые keyless GET: /api/v1/models, /api/v1/endpoints/zdr, /api/v1/models/anthropic/claude-haiku-5.5/endpoints; прочитаны FAQ, ZDR guide, Terms.
CONFIDENCE: high
EVIDENCE: https://openrouter.ai/api/v1/models | https://openrouter.ai/api/v1/endpoints/zdr | https://openrouter.ai/docs/faq | https://openrouter.ai/docs/guides/features/zdr | https://openrouter.ai/terms

### [REJECTED] Vercel AI Gateway (и AI SDK vercel/ai)
NEED: Gateway
KIND: commercial SaaS
URL: https://vercel.com/docs/ai-gateway/pricing
LICENSE: Сервис проприетарный; лицензия репозитория vercel/ai через GitHub API - NOASSERTION (текст не читал)
COMMERCIAL USE: Не проверено по условиям Vercel.
PROJECT STATE: Документация обновлена 2026-09-08. vercel/ai: 27 301 звезда, релиз ai@7.0.139 (2026-10-13), TypeScript.
CLAIMED VS ACTUAL: 'Zero markup' подтверждено документацией, но есть платные надстройки: team-wide ZDR $0.10 за 1000 запросов, provider allowlist $0.10 за 1000, trace drains $0.05 за 1000 traces + $0.50/GB, custom reporting $0.075 за 1000 записей.
ZDR и BYOK доступны только на платном уровне (Pro/Enterprise).
CAPABILITIES: Единый endpoint, BYOK, бюджеты на команду/проект/ключ, ZDR-маршрутизация, trace drains в OpenTelemetry.
INFRA: Аккаунт команды Vercel.
PRICING/LIMITS: Токены по list price провайдера; комиссии платёжной системы на клиенте. Rate limits не проверены.
RISKS: Привязка к аккаунту Vercel и экосистеме TypeScript при Python-стеке платформы и развёртывании на собственном сервере; ещё один обработчик данных.
REPLACEABILITY: Высокая.
HOW VERIFIED: Прочитана страница docs/ai-gateway/pricing (полный текст); GitHub API для vercel/ai.
CONFIDENCE: medium
EVIDENCE: https://vercel.com/docs/ai-gateway/pricing | https://github.com/vercel/ai

### [REJECTED] Portkey AI Gateway
NEED: Gateway
KIND: open-source + commercial SaaS
URL: https://github.com/Portkey-AI/gateway
LICENSE: MIT (open-source gateway)
COMMERCIAL USE: Разрешено для MIT-части.
PROJECT STATE: 13 180 звёзд, 296 открытых issues; последний релиз v1.15.2 от 2026-01-12; последний push 2026-05-25. Компания куплена Palo Alto Networks (сделка закрыта 2026-05-29, пресс-релиз PANW). Не archived.
CLAIMED VS ACTUAL: README обещает 'Gateway 2.0', где enterprise-ядро вливается в open-source, но релизов нет с января 2026, а коммитов в main - с 2026-05-25, то есть с момента закрытия сделки. Страница цен противоречива в том, что считается overage
(requests или recorded logs).
CAPABILITIES: Routing, retries, fallbacks, guardrails, базовый dashboard.
INFRA: Node/Docker для self-host.
PRICING/LIMITS: Developer - бесплатно, 10k логов/мес, хранение 3 дня, 'not for production'; Production $49/мес, 100k логов, +$9 за 100k; Enterprise - по запросу (VPC, SSO).
RISKS: Остановка open-source разработки после поглощения; смена продуктового фокуса на security-покупателей (оценка сторонних источников).
REPLACEABILITY: Высокая.
HOW VERIFIED: GitHub API (релизы, коммиты, README), страница pricing, WebSearch с пресс-релизом Palo Alto Networks.
CONFIDENCE: high
EVIDENCE: https://github.com/Portkey-AI/gateway | https://portkey.ai/pricing | https://www.paloaltonetworks.com/company/press/2026/palo-alto-networks-completes-acquisition-of-portkey-to-secure-ai-agents

### [NEEDS-TRIAL] Pydantic AI
NEED: Абстракция провайдеров с типизированными structured outputs (альтернатива gateway)
KIND: open-source
URL: https://github.com/pydantic/pydantic-ai
LICENSE: MIT
COMMERCIAL USE: Разрешено.
PROJECT STATE: 20 595 звёзд, 1 373 открытых issues, v2.55.0 (2026-10-09), коммиты 2026-10-13, 53 workflows, tests. Не archived.
CLAIMED VS ACTUAL: Глубоко не аудировал; расхождений не искал.
CAPABILITIES: Агенты с типизированным выводом на Pydantic, несколько провайдеров. Коммит 2026-10-13 'Stop AnthropicModel picking native structured output that ...' показывает, что поддержка native structured outputs Anthropic ещё
стабилизируется.
INFRA: Библиотека Python.
PRICING/LIMITS: Бесплатно.
RISKS: Это agent framework, выходящий за рамки области аудита; быстрый темп мажорных версий (v2.55).
REPLACEABILITY: Средняя (фреймворк проникает в код агентов).
HOW VERIFIED: Только GitHub API (метаданные, релизы, последние коммиты). Код не читал.
CONFIDENCE: low
EVIDENCE: https://github.com/pydantic/pydantic-ai

### [RECOMMENDED] Langfuse (self-hosted OSS или Langfuse Cloud)
NEED: LLM observability: трассировка действий агентов, учёт токенов и стоимости, версии prompt, datasets
KIND: open-source (open core) + managed OSS
URL: https://github.com/langfuse/langfuse
LICENSE: MIT для ядра; каталоги ee/, web/src/ee/, worker/src/ee/ - Langfuse Enterprise License. Copyright ClickHouse, Inc. (GitHub API: NOASSERTION)
COMMERCIAL USE: Разрешено: ядро под MIT можно self-host в коммерческом продукте. EE-функции требуют лицензии.
PROJECT STATE: 35 778 звёзд, 1 054 открытых issues, v4.58.0 (2026-10-13), параллельно поддерживается ветка v3 (v3.225.12, 2026-10-12), 48 workflows включая License Compliance Check. Куплен ClickHouse 2026-01-16. Python SDK langfuse 4.17.0 (MIT,
Python >=3.10, 2026-10-05).
CLAIMED VS ACTUAL: 1) 'Open source' верно для ядра; EE-only: project-level RBAC, audit logs, управление data retention, server-side masking, SCIM, protected prompt labels. 2) Docker Compose официально описан как 'local use and testing', без HA,
масштабирования и бэкапов; production - Kubernetes. 3) В docker-compose.yml TELEMETRY_ENABLED по умолчанию true. 4) Enterprise self-host теперь продаётся как надбавка к коммерческому плану ClickHouse.
CAPABILITIES: В бесплатном self-host: tracing, sessions, учёт токенов и стоимости, OpenTelemetry, datasets, experiments, LLM-as-judge, очереди аннотаций, версионирование prompt, playground, dashboards, client-side masking, SSO, org-level RBAC.
INFRA: 6 контейнеров: langfuse-web, langfuse-worker, ClickHouse 25.12, Postgres 17, Redis 7, MinIO. Рекомендация документации: минимум 4 ядра, 16 GiB RAM, 100 GiB диска; настроить ротацию docker-логов.
PRICING/LIMITS: Self-host OSS - $0. Cloud: Hobby бесплатно (50k units/мес, 30 дней, 2 пользователя); Core $29/мес (100k units, далее $8 за 100k, 90 дней); Pro $199/мес (3 года); Enterprise $2 499/мес.
RISKS: 16 GiB RAM может не поместиться на 'скромном сервере' рядом с приложением; управление retention и audit logs платные; зависимость дорожной карты от ClickHouse.
REPLACEABILITY: Высокая, если инструментировать через OpenTelemetry: backend меняется на Phoenix или Opik без переписывания агентов.
HOW VERIFIED: GitHub API; прочитаны LICENSE, ee/LICENSE, docker-compose.yml; страницы pricing, pricing-self-host, self-hosting, docker-compose guide; WebSearch + блог ClickHouse о сделке.
CONFIDENCE: high
EVIDENCE: https://github.com/langfuse/langfuse | https://github.com/langfuse/langfuse/blob/main/LICENSE | https://langfuse.com/pricing | https://langfuse.com/pricing-self-host | https://langfuse.com/self-hosting | https://langfuse.com/self-hosting/deployment/docker-compose

### [ALTERNATIVE] Arize Phoenix
NEED: LLM observability и evals (лёгкая self-hosted альтернатива)
KIND: open-source (source-available)
URL: https://github.com/Arize-ai/phoenix
LICENSE: Elastic License 2.0 (ELv2), не OSI
COMMERCIAL USE: Разрешено использовать внутри своего продукта. Запрещено предоставлять сам Phoenix третьим лицам как hosted/managed service и обходить license key.
PROJECT STATE: 11 822 звезды, 1 142 открытых issues, arize-phoenix v20.21.2 (2026-10-13), коммиты 2026-10-13, 60 workflows, tests. Python >=3.11,<3.15.
CLAIMED VS ACTUAL: Позиционируется как open source, фактически ELv2. Для LEDGERHUNT ограничение значимо только если показывать интерфейс Phoenix клиентам как часть сервиса.
CAPABILITIES: Tracing (OpenTelemetry/OpenInference), evals, datasets, experiments, prompt management; аутентификация OAuth2/LDAP/local. Документация: self-host без ограничений функций.
INFRA: Варианты: CLI, Docker/Compose, Kubernetes. Требования к ресурсам на прочитанной странице не указаны.
PRICING/LIMITS: Self-host бесплатно.
RISKS: Нестандартная лицензия требует юридической проверки при платных тарифах; очень быстрый темп мажорных версий (v20).
REPLACEABILITY: Высокая (OTel).
HOW VERIFIED: GitHub API; прочитаны LICENSE и pyproject.toml; страница self-hosting.
CONFIDENCE: high
EVIDENCE: https://github.com/Arize-ai/phoenix | https://github.com/Arize-ai/phoenix/blob/main/LICENSE | https://arize.com/docs/phoenix/self-hosting

### [REJECTED] LangSmith
NEED: LLM observability и evals
KIND: commercial SaaS
URL: https://www.langchain.com/pricing
LICENSE: Платформа проприетарная; langsmith-sdk - MIT
COMMERCIAL USE: Разрешено как SaaS-подписка; self-hosted и hybrid - только Enterprise.
PROJECT STATE: langsmith-sdk: 1 077 звёзд, v0.14.8 (2026-10-13), активен.
CLAIMED VS ACTUAL: SDK открыт, но сервер закрыт. Цена за трейсы сверх включённых на странице не приведена ('pay as you go'). Base traces хранятся 14 дней, extended - 180 дней.
CAPABILITIES: Tracing, datasets, evals, deployments.
INFRA: SaaS; self-host только Enterprise.
PRICING/LIMITS: Developer: $0, 1 seat, 5k base traces/мес. Plus: $39 за seat в месяц, 10k base traces/мес. Enterprise - по запросу.
RISKS: Данные расследований уходят третьей стороне; нет self-host на доступных тарифах; 5k трейсов - это около 47 расследований в месяц при 106 вызовах на расследование, если каждый вызов - отдельный trace.
REPLACEABILITY: Средняя.
HOW VERIFIED: Страница pricing (WebFetch); GitHub API для SDK.
CONFIDENCE: medium
EVIDENCE: https://www.langchain.com/pricing | https://github.com/langchain-ai/langsmith-sdk

### [REJECTED] Braintrust (+ autoevals)
NEED: Evals и observability
KIND: commercial SaaS (+ open-source библиотеки)
URL: https://www.braintrust.dev/pricing
LICENSE: Платформа проприетарная; autoevals - MIT; SDK - Apache-2.0
COMMERCIAL USE: Разрешено как SaaS; on-prem только Enterprise.
PROJECT STATE: autoevals: 1 056 звёзд, py-0.4.0 (2026-10-07). braintrust-sdk-javascript: релиз 3.37.2 (2026-10-09).
CLAIMED VS ACTUAL: none found
CAPABILITIES: Experiments, scorers, playground, логирование.
INFRA: SaaS.
PRICING/LIMITS: Starter $0: 1 GB данных (далее $4/GB), 10k scores (далее $2.50 за 1k), хранение 14 дней. Pro $249/мес: 5 GB, 50k scores, 30 дней.
RISKS: Нет self-host ниже Enterprise; 14 дней хранения на бесплатном плане несовместимы с требованием воспроизводимости; autoevals по умолчанию использует GPT-6 Luna как судью (коммит 2026-10-01).
REPLACEABILITY: Средняя.
HOW VERIFIED: Страница pricing; GitHub API для autoevals и SDK.
CONFIDENCE: medium
EVIDENCE: https://www.braintrust.dev/pricing | https://github.com/braintrustdata/autoevals

### [REJECTED] Helicone
NEED: LLM observability / proxy-gateway
KIND: open-source + SaaS
URL: https://github.com/Helicone/helicone
LICENSE: Apache-2.0
COMMERCIAL USE: Разрешено.
PROJECT STATE: 6 218 звёзд; последний GitHub-релиз 2025-08-21; с июля 2026 только редкие исправления, последний коммит 2026-09-16 (security-fix cross-tenant bypass). По вторичным источникам куплен Mintlify 2026-03-03 и переведён в maintenance
mode.
CLAIMED VS ACTUAL: README не упоминает maintenance mode (поиск по README ничего не нашёл), хотя активность коммитов и вторичные источники указывают на прекращение развития.
CAPABILITIES: Логирование запросов через proxy, учёт стоимости, кеш.
INFRA: Self-host: несколько сервисов, включая ClickHouse (по структуре репозитория и названиям workflows).
PRICING/LIMITS: Не проверял.
RISKS: Нет новых функций; недавно исправлялась уязвимость cross-tenant.
REPLACEABILITY: Высокая.
HOW VERIFIED: GitHub API (релизы, 10 последних коммитов, README); WebSearch (Dealroom и другие вторичные источники).
CONFIDENCE: medium
EVIDENCE: https://github.com/Helicone/helicone | https://ai-startups.dealroom.co/news/feed/mintlify-acquires-open-source-ai-observability-platform-helicone

### [ALTERNATIVE] OpenLLMetry (Traceloop)
NEED: Vendor-neutral инструментирование LLM-вызовов в OpenTelemetry
KIND: open-source / standard (OTel)
URL: https://github.com/traceloop/openllmetry
LICENSE: Apache-2.0
COMMERCIAL USE: Разрешено.
PROJECT STATE: 7 488 звёзд, 779 открытых issues, 0.62.4 (2026-09-29), коммиты 2026-10-13, CI; traceloop-sdk требует Python >=3.10.
CLAIMED VS ACTUAL: Свежие коммиты исправляют учёт thinking-токенов в gen_ai.usage для Google - учёт стоимости reasoning-моделей ещё дорабатывается.
CAPABILITIES: 35 пакетов инструментирования, включая anthropic, openai, google-generativeai, mistralai, groq, litellm, mcp; экспорт в любой OTLP-backend (Langfuse, Phoenix).
INFRA: Библиотека + OTLP endpoint.
PRICING/LIMITS: Бесплатно.
RISKS: Отдельного UI нет; поведение телеметрии самого SDK не проверял.
REPLACEABILITY: Высокая (стандарт OTel).
HOW VERIFIED: GitHub API; список packages/ и pyproject.toml прочитаны через gh api contents.
CONFIDENCE: high
EVIDENCE: https://github.com/traceloop/openllmetry

### [ALTERNATIVE] Opik (Comet)
NEED: LLM observability и evals (альтернатива Langfuse)
KIND: open-source
URL: https://github.com/comet-ml/opik
LICENSE: Apache-2.0
COMMERCIAL USE: Разрешено.
PROJECT STATE: 22 575 звёзд, 188 открытых issues, 2.2.99 (2026-10-13), ежедневные релизы, 101 workflow.
CLAIMED VS ACTUAL: Глубоко не аудировал.
CAPABILITIES: Tracing, evals, optimization studio (по названиям коммитов и workflows).
INFRA: Не проверял (в репозитории есть Helm chart и Docker-образы).
PRICING/LIMITS: Self-host бесплатно; облачные цены не проверял.
RISKS: Требования к инфраструктуре и набор бесплатных функций не подтверждены.
REPLACEABILITY: Высокая.
HOW VERIFIED: Только GitHub API.
CONFIDENCE: low
EVIDENCE: https://github.com/comet-ml/opik

### [RECOMMENDED] Inspect AI (UK AI Security Institute)
NEED: Evals: 50+ сценариев с ground truth, сравнение AI-слоя с детерминированным baseline
KIND: open-source
URL: https://github.com/UKGovernmentBEIS/inspect_ai
LICENSE: MIT
COMMERCIAL USE: Разрешено.
PROJECT STATE: 2 995 звёзд, 395 открытых issues, 0.3.279 (2026-10-12), коммиты 2026-10-13 (в том числе 'support Gemini 4 Argon'), 20 workflows, tests. Python >=3.10. Поддерживают UK AISI и Meridian Labs.
CLAIMED VS ACTUAL: none found
CAPABILITIES: Datasets (CSV/JSON/HF), solvers, scorers (match, pattern, model-graded, custom), tool use и агенты, eval sets, параллелизм, лимиты, кеширование, batch-режим, лог-файлы .eval и viewer. Провайдеры в коде: anthropic, openai, google,
mistral, deepseek, groq, together, fireworks, openrouter, ollama, vllm, openai_compatible, mockllm.
INFRA: Python-пакет; Docker нужен только для sandbox-сценариев.
PRICING/LIMITS: Бесплатно; расходы - только токены моделей.
RISKS: Версия 0.3.x (API может меняться); работу на Windows 11 не проверял (Docker на dev-машине есть).
REPLACEABILITY: Высокая: сценарии хранятся как JSONL с ground truth и переносимы в promptfoo или DeepEval.
HOW VERIFIED: GitHub API; прочитаны pyproject.toml, списки файлов model/_providers и scorer; сайт inspect.aisi.org.uk.
CONFIDENCE: high
EVIDENCE: https://github.com/UKGovernmentBEIS/inspect_ai | https://inspect.aisi.org.uk/

### [ALTERNATIVE] promptfoo
NEED: Evals и регрессионные тесты prompt в CI
KIND: open-source
URL: https://github.com/promptfoo/promptfoo
LICENSE: MIT
COMMERCIAL USE: Разрешено.
PROJECT STATE: 25 976 звёзд, 713 открытых issues, 0.124.1 (2026-10-08), коммиты 2026-10-13, 46 workflows. Требует Node >=22.22.0. README: 'Promptfoo is now part of OpenAI. Promptfoo remains open source and MIT licensed.'
CLAIMED VS ACTUAL: Лицензия осталась MIT (проверено по README и package.json), но владелец теперь OpenAI - риск нейтральности и приоритетов при сравнении провайдеров.
CAPABILITIES: Декларативные YAML-тесты, assertions, сравнение моделей side-by-side, red teaming, CI-интеграция.
INFRA: Node 22.22+ (на dev-машине Node 23).
PRICING/LIMITS: Бесплатно.
RISKS: TypeScript-экосистема при Python-платформе: scorer для графа и TXID придётся писать отдельно от основного кода.
REPLACEABILITY: Высокая.
HOW VERIFIED: GitHub API; README и package.json прочитаны через gh api contents; WebSearch о сделке.
CONFIDENCE: high
EVIDENCE: https://github.com/promptfoo/promptfoo

### [ALTERNATIVE] DeepEval (Confident AI)
NEED: Evals (pytest-стиль, готовые LLM-метрики)
KIND: open-source
URL: https://github.com/confident-ai/deepeval
LICENSE: Apache-2.0
COMMERCIAL USE: Разрешено.
PROJECT STATE: 18 822 звезды, 723 открытых issues, python-v4.2.4 (2026-09-22), pyproject 4.2.8, коммиты 2026-10-12, 29 workflows. Python >=3.9.
CLAIMED VS ACTUAL: В коде deepeval/telemetry/client.py зашит PostHog project key и host us.i.posthog.com: телеметрия включена по умолчанию, отключается через DEEPEVAL_TELEMETRY_OPT_OUT. В корне репозитория лежат служебные файлы a.py, b.py, c.py -
признак слабой гигиены репозитория.
CAPABILITIES: Готовые метрики (LLM-as-judge), интеграция с pytest, синтетические данные.
INFRA: Python-пакет.
PRICING/LIMITS: Бесплатно; облако Confident AI не проверял.
RISKS: Телеметрия по умолчанию при работе с данными расследований; метрики-судьи сами тратят токены.
REPLACEABILITY: Высокая.
HOW VERIFIED: GitHub API; прочитаны pyproject.toml и deepeval/telemetry/client.py; дерево репозитория.
CONFIDENCE: high
EVIDENCE: https://github.com/confident-ai/deepeval | https://github.com/confident-ai/deepeval/blob/main/deepeval/telemetry/client.py

## OPEN QUESTIONS FOR OWNER (researcher)
- На каком языке формируются отчёты и письма (русский, английский, оба)? Для русского текста output-токенов заметно больше; в модели заложен множитель 1.8, тяжёлый случай $0.57.
- Как делится бюджет $1 между LLM и платными data-API/OSINT-поиском? При рекомендованном tiering LLM занимает $0.40-0.57; подходит ли остаток $0.43-0.60?
- Допустимо ли отправлять скриншоты и переписку жертв провайдерам в США (Anthropic, OpenAI) со стандартным хранением до 30 дней, или нужен ZDR? ZDR у обоих оформляется только через sales и на организацию.
- Есть ли требования к юрисдикции и локализации персональных данных пользователей (страны клиентов, GDPR для EEA/UK)? От этого зависит выбор между Langfuse Cloud и self-host и допустимость OpenRouter.
- Готовы ли выделить под observability отдельную VM 4 ядра / 16 GiB, или на старте использовать Langfuse Cloud (Hobby/Core) либо более лёгкий Phoenix под ELv2?
- Нужен ли юридический обзор ELv2 (Phoenix) и Terms OpenRouter (запрет перепродажи доступа, обязанность передавать условия моделей клиентам) до включения их в коммерческий продукт?
- OSINT-поиск выполняется встроенным web search провайдера ($10 за 1000 запросов) или отдельным поисковым API из другой области аудита?
- Допускается ли деградация до отчёта без LLM-текста (только детерминированные факты) при исчерпании бюджета, refusal модели или недоступности обоих провайдеров?
- Требуется ли обязательная проверка человеком перед отправкой черновиков писем биржам, Tether и правоохранительным органам?
- Какой ожидаемый объём расследований в месяц на запуске? Start tier Anthropic ограничен $500/мес (около 880-1 250 расследований по $0.40-0.57); при большем объёме нужно заранее запросить повышение tier.

## NOT VERIFIED (researcher)
- Фактическая надёжность tool calling и доля schema-valid ответов Claude Haiku 5.5, Sonnet 5.5, GPT-6 Luna на схемах проекта: реальные вызовы API не выполнялись (ключи запрещены правилами аудита).
- Все числа токенов в модели стоимости - оценки, не замеры: размеры префиксов и динамического контекста, число вызовов, доля thinking-токенов (допущено 50% видимого output для Haiku и для отчёта/писем, 100% для планирования на
Sonnet), множитель 1.8 для русскоязычного вывода.
- Латентность: укладывается ли первый отчёт в 2 минуты и простая транзакция в 30 секунд - скорость генерации моделей и время компиляции грамматик схем не измерялись.
- OpenAI Services Agreement (HTTP 403) и openai.com/api/pricing (HTTP 403): права на коммерческое использование по тексту договора не подтверждены; использована только страница 'your data'.
- Наличие датированных snapshot ID у GPT-6 в API OpenAI и поддержка temperature/seed; list-цена GPT-5.6 Sol против промо-цены.
- Фактические стартовые лимиты Anthropic Evaluation tier для новой организации.
- Расхождение о хранении данных Anthropic по умолчанию: 30 дней (privacy-статья) или отсутствие хранения содержимого (страница api-and-data-retention) - какое правило действует для обычного аккаунта без ZDR.
- Сведения из справки claude-api skill (кеш от 2026-10-06), не перепроверенные по живой документации: лимиты PDF (32 MB, 600 страниц), несовместимость citations со structured outputs, отказ forced tool_choice на Sonnet 5.5 / Opus
5.5, параметр fallbacks при refusal, список категорий safety classifiers.
- Частота ложных refusal на материалах о криптомошенничестве и OSINT; применимость Anthropic Usage Policy и политик OpenAI к расследованиям и OSINT по лицам не анализировалась.
- Gemini: срок хранения abuse-логов в днях; RPM/TPM по tier для конкретных моделей; token limits со страниц моделей (взяты из OpenRouter и LiteLLM).
- Mistral: срок действия sale-цены Large 4, точные API model id, rate limits, условия хранения данных, strict structured outputs по первичной документации.
- DeepSeek: отдельные правила обработки данных для API (open platform), условия использования, наличие strict mode.
- Alibaba Model Studio: последние 39K символов страницы цен не прочитаны; поддержка function calling и JSON schema, условия использования и хранения данных.
- Groq: цены Llama-моделей (на странице 'Contact sales'); Fireworks: цены serverless за токен; условия и retention у Groq, Together, Fireworks.
- Helicone: maintenance mode подтверждён только вторичными источниками и активностью коммитов, первичного заявления Mintlify не читал.
- Langfuse: поведение под реальной нагрузкой на одном сервере, возможность работать на менее чем 16 GiB, определение billing unit в Cloud, содержимое телеметрии.
- Arize Phoenix: требования к ресурсам; Opik и MLflow: набор функций и инфраструктура (проверены только метаданные репозиториев).
- LangSmith: цена за трейсы сверх включённых. Vercel AI Gateway: rate limits, условия использования, лицензия vercel/ai (GitHub API вернул NOASSERTION).
- Inspect AI и Langfuse SDK на Windows 11 с Python 3.13: по pyproject версии Python подходят, запуск не проверялся (код не устанавливался по правилам аудита).
- Pydantic AI: код не читал, оценка только по метаданным репозитория.