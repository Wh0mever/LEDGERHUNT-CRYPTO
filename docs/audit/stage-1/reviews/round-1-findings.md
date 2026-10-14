
######################################################################
# LENS owner-format  {'major': 16, 'minor': 7}
VERDICT: Structurally the document complies with Prompt 0: all 13 needs (a)-(m) have a section, each carries the seven items and at least two alternatives with concrete rejection reasons, and the own-built components (tracer, orchestrator, HTTP
gateway, Label Store, layout) are explicitly justified. It should not go to the owners unchanged: several brief sub-needs are thin or scattered (balances and contracts in section 1; exchangers, bridges and services in section 2; users
and reports in section 7; the rationale for graph ML in section 6), and a few sections contradict Part A on the chosen solution, on licence terms or on how facts are verified. The single most important fix is to add an explicit cross-
cutting decision in Part A for the principle "seed phrases, private keys and wallet access are never requested", with a concrete input filter and a build-gate test; today it appears only as one clause in the add-on section 14. No
blockers on this lens: 16 major, 7 minor.

[1] MAJOR | Part A, A4 (cross-cutting decisions G1-G15), after G15; also A6
   QUOTE: Поискового провайдера (Tavily или Brave) выбираете вы. Платформа никогда не обещает возврат средств.
   PROBLEM: The always-on principle 'seed phrases, private keys and wallet access are never requested' has no cross-cutting decision in Part A. It appears only as one clause in section 14 (risks) and as trace masking in section 5;
   there is no control for victim-supplied screenshots and correspondence, which A7.3 plans to send to model providers.
   FIX: Добавить в A4: «**G16.** Платформа никогда не запрашивает seed-фразы, приватные ключи и доступ к кошельку: таких полей нет ни в интерфейсе, ни в API, ни в шаблонах писем. Входной фильтр проверяет текст пользователя и текст,
   распознанный во вложениях (скриншоты, переписка): найденная seed-фраза или приватный ключ не сохраняется и не передаётся моделям и поисковым провайдерам, пользователь получает предупреждение. Все инструменты — только чтение; подписи
   и отправки транзакций в системе нет (раздел 11).» В A6 добавить строку: «Seed-фразы и приватные ключи не запрашиваются и не сохраняются | входной фильтр; тест с подставной seed-фразой: 0 вхождений в БД, журналах, трассах и запросах
   к моделям — обязательное условие сборки | заложено в архитектуру».

[2] MAJOR | Section 7, 'Инфраструктура и затраты' (need g: users, investigations, events, reports)
   QUOTE: Одна база: схема приложения под RLS и отдельная схема с отдельной ролью для системных таблиц DBOS (G2).
   PROBLEM: The brief asks for storage of users, investigations, events and reports, but section 7 never says where users (profiles, organisations, roles) and reports (report.json, PDF, evidence-zip) are stored. No file or object store
   is named, the scope of restic is undefined, and there is no disk-growth estimate although raw responses are kept indefinitely on a 75 GB disk.
   FIX: Добавить в «Инфраструктура и затраты» раздела 7 (поправить, если фактический замысел иной): «Пользователи: учётные данные хранит поставщик входа (G14); в PostgreSQL — таблицы users, organizations и memberships (ключ — sub из
   токена, роли, принадлежность к расследованиям), под RLS. Отчёты: таблица reports хранит версию схемы, report.json (JSONB), оба манифеста, подпись, метку времени и sha256 файлов; report.pdf и evidence-zip лежат на томе сервера и
   попадают в резервную копию через restic (G12). Объём диска на одно расследование (сырые ответы, отчёты) не измерен.» В «Что проверить» добавить: «Замер объёма БД и файлов на стандартное расследование и на граф из 1 000 адресов;
   критерий — прогноз заполнения диска 75 GB и стоимости B2 на 12 месяцев.»

[3] MAJOR | Section 1, 'Решение' (need a: transactions, token transfers, balances, timestamps, contracts)
   QUOTE: Основной источник истории TRC20, событий контракта и internal transactions — TronGrid v1 с собственным API key (план BASIC).
   PROBLEM: Balances and contracts are required data types in the brief but are covered only in passing (balanceOf 'latest only', an unbuilt contract registry). The section never states the chosen source for current balance, how
   historical balance is derived, or how the platform tells that an address is a contract.
   FIX: Добавить после «Решения» абзац «Покрытие видов данных Промпта 0»: «Транзакции — receipt `/walletsolidity/gettransactioninfobyid` у оператора узла, отличного от TronGrid. Переводы токенов — TronGrid
   `/v1/accounts/{address}/transactions/trc20`; индекс события — `/v1/transactions/{txid}/events`. Балансы — текущий `balanceOf` через constant call у независимого узла (только latest); исторический баланс источники не отдают, он
   восстанавливается по полной истории переводов с учётом DestroyedBlackFunds, Issue и Redeem, а при неполной истории в отчёте стоит „баланс на дату недоступен“. Время — block_timestamp строки истории, сверяется с блоком в receipt; в
   отчёт идут только solidified-данные. Контракты — события через `/v1/contracts/{address}/events`; признак „адрес — контракт“ и сведения о контракте — через эндпоинт узла (кандидат `wallet/getcontract`, в аудите не проверялся,
   проверка на Этапе 2); реестр контрактов обменников и мостов — собственный (пункт 6 ниже).»

[4] MAJOR | Section 2, 'Решение' and 'Ограничения и риски' (need b: exchanges, exchangers, bridges, services)
   QUOTE: Не покрыто открытыми источниками: операционные hot wallets вне PoR, OTC, P2P-мерчанты, обменники СНГ.
   PROBLEM: The brief asks for label sources for exchanges, exchangers, bridges and services; section 2 chooses sources only for exchanges and sanctions or freezes. The contract registry for exchangers and bridges is mentioned in A3,
   A8 and section 1 but is not part of the section 2 decision and has no named source, cost or quality check.
   FIX: Добавить в «Решение» раздела 2: «Четвёртый локальный источник — курируемый реестр контрактов обменников (DEX), мостов и сервисов (SunSwap, JustLend, мосты): адрес, тип, источник записи, дата проверки, confidence; собирается до
   старта трассировщика (раздел 1, пункт 6). Для централизованных обменников, OTC и P2P-сервисов открытого источника нет: в MVP их метку даёт только платный провайдер (MistTrack), иначе в отчёте стоит „тип получателя не установлен“.»
   Там же указать, откуда берутся записи реестра (официальная документация проектов, верифицированные контракты), в «Затраты» — трудоёмкость сборки и курации, в таблицу альтернатив — строку «Bitrace, BitOK — не проверялись».

[5] MAJOR | Section 6, 'Решение', 'Почему выбрано' and the alternatives table (need f: ML on graphs)
   QUOTE: Graph ML (PyTorch Geometric 2.8.1 + py-tgb 2.3.0) — только в изолированном экспериментальном контуре.
   PROBLEM: For the graph-ML sub-need, item 1 (why) is missing: 'Почему выбрано' gives no reason for PyTorch Geometric or py-tgb and no statement of what task the experimental contour solves. Item 2 has only one alternative (DGL);
   Raphtory is named in the licence paragraph but has no row.
   FIX: Добавить в «Почему выбрано» пункт: «Graph ML: задача экспериментального контура — [назвать: например, ранжирование адресов-кандидатов]. PyTorch Geometric 2.8.1 выбран как поддерживаемый фреймворк под MIT (релиз 2026-10-06,
   бинарники pyg_lib для torch 2.14.0); py-tgb — [назвать роль: загрузчики и протокол оценки на темпоральных графах]. Результат сравнивается с детерминированным baseline и не-графовым классификатором и в отчёт не попадает.» В таблицу
   альтернатив добавить строку: «Raphtory (graph ML и темпоральная аналитика) | GPL | допустим только при чистом SaaS; [причина отказа]».

[6] MAJOR | Section 4 'Решение' vs section 5 'Решение' vs A4 G13 vs A1 rows 4-5 (needs d, e, k)
   QUOTE: Pydantic AI для LLM-шагов в точках принятия решений; всё работает на том же PostgreSQL, без отдельного сервера оркестрации
   PROBLEM: The chosen solution for the model-access layer differs by section: section 4 chooses Pydantic AI, section 5 chooses 'официальные SDK за собственным адаптером LLMClient', G13 says the choice is open until Stage 2, and A1
   does not mention Pydantic AI. Section 5 also does not justify writing its own adapter instead of reusing Pydantic AI.
   FIX: Привести к G13. Раздел 4, «Решение»: «…и собственный интерфейс LLMClient для LLM-шагов; под ним условно Pydantic AI, альтернатива — официальные SDK (решает spike Этапа 2, G13)». Раздел 5, «Решение»: «Доступ — только через
   собственный адаптер LLMClient, без LLM-gateway; реализация под ним (Pydantic AI или официальные SDK) выбирается на Этапе 2». В таблицу альтернатив раздела 5 добавить строку «Pydantic AI напрямую, без LLMClient | MIT | cost_limit
   срабатывает после превышения; 55 minor-релизов за 15.4 недели; 16 advisories — нужен собственный слой учёта стоимости и журнала». В A1, строка 4: «…; LLM-шаги — условно Pydantic AI под LLMClient».

[7] MAJOR | Section 3, 'Как проверяем качество', first bullet (contradicts A3, A6 and section 1)
   QUOTE: Каждое ребро отчёта подтверждается через /v1/transactions/{txid}/events лениво, только для рёбер, попавших в отчёт
   PROBLEM: Part A and section 1 promise that every reported fact is confirmed by a receipt from an operator other than TronGrid; section 3 confirms edges through TronGrid's own events endpoint, the same operator that supplied the
   history. Section 6 adds 'выборочная повторная сверка с первичным источником', which reads as sampling.
   FIX: Раздел 3: «Каждое ребро отчёта подтверждается receipt у оператора узла, отличного от TronGrid (раздел 1); event_index для ключа ребра берётся из /v1/transactions/{txid}/events. Обе проверки ленивые — только для рёбер, попавших
   в отчёт; идентичность ребра и фильтры — по G6.» Раздел 6, «Как проверяем качество»: заменить «выборочная повторная сверка с первичным источником» на «для рёбер отчёта — полная сверка по разделу 1, для остальных рёбер графа —
   выборочная».

[8] MAJOR | Section 14, 'Как проверяем качество' and 'Решение'; A4 G7 (contradicts section 2)
   QUOTE: Набор OFAC собирается из файлов TRX и USDT и каждую ночь сверяется с первичными файлами
   PROBLEM: Section 2 builds the sanctions list from the primary SDN_ADVANCED.XML; section 14 builds it from the two files of the 0xB10C mirror and admits that 3 of 340 addresses were not found in the primary files. G7 and section 14
   still present 340 as the full set, which conflicts with the principle that conclusions rest on primary data.
   FIX: Раздел 14: «Набор OFAC собирается из первичного файла SDN_ADVANCED.XML (раздел 2) и каждую ночь сверяется с зеркалом 0xB10C как контрольным. Адрес, найденный только в зеркале (сейчас 3 из 340), метку „OFAC SDN“ не получает,
   пока не подтверждён в первичном файле.» В «Решении» раздела 14: «полный локальный набор OFAC SDN (340 адресов TRON по зеркалу, из них 337 подтверждены в первичных файлах)». G7: «контрольное значение 340 адресов TRON по зеркалу на
   2026-10-01, из них 337 найдены в первичных файлах».

[9] MAJOR | Section 1, alternatives table (PublicNode row) and 'Лицензия и коммерческое использование'; A1 row 1; G5
   QUOTE: Нет SLA и опубликованных лимитов, условия запрещают scraping и data mining, receipt без internal_transactions. Только резерв
   PROBLEM: PublicNode is the designated reserve node in A1, A3 and G5, yet the document itself says its terms prohibit scraping and data mining, and the licence subsection of section 1 does not address PublicNode at all. A production
   fallback on those terms conflicts with the 'lawfully obtained data' principle and leaves item 3 unanswered for a chosen component.
   FIX: Добавить в «Лицензия и коммерческое использование» раздела 1: «PublicNode: бесплатный доступ „AS IS“ по отзывной лицензии; условия запрещают scraping и data mining, коммерческое использование прямо не разрешено. До письменного
   подтверждения PublicNode используется только в разработке; резервный узел production — второй платный оператор из конфигурации (GetBlock или Nodit) после чтения его условий.» В A1 (строка 1) и G5: «PublicNode — резерв без ключа, в
   production только после подтверждения условий».

[10] MAJOR | Part A, A6 (row 'Полезность отчёта') and A8 item 2; section 1 'Лицензия и коммерческое использование'
   QUOTE: Хронология, граф, адреса, ссылки; пакет доказательств с сырыми ответами API и манифестом
   PROBLEM: The evidence package hands raw API responses to the client, while section 1 reads TronGrid's terms as 'продавать отчёты можно, проксировать сырой API клиентам нельзя', Chainstack limits use to internal business purposes and
   MistTrack forbids resale of data. The Stage 2 written confirmations cover SaaS use and storage, not redistribution of raw responses.
   FIX: A8, пункт 2: «TronGrid: цена индивидуального плана, допустимость использования в SaaS, хранения ответов и передачи сырых ответов клиенту в составе пакета доказательств. Chainstack: использование в SaaS и передача квитанций в
   пакете доказательств. MistTrack: проверка коммерческого использования, экспорт меток в JSON-отчёт и включение сырого ответа в пакет доказательств.» В раздел 1, «Лицензия»: «До письменных ответов пакет доказательств для клиента
   содержит TXID, хеши сырых ответов и манифест; сами сырые ответы хранятся на платформе.»

[11] MAJOR | Section 3, 'Лицензия и коммерческое использование' (contradicts section 2)
   QUOTE: Условия коммерческого использования и кэширования у MistTrack и Arkham в документации не найдены — нужны письменные.
   PROBLEM: Section 2 states that MistTrack's Terms of Use of 2026-10-09 explicitly allow client PDF reports, commercial investigations and caching; section 3 says no such terms were found. Owners get two opposite answers to item 3 for
   the same paid provider.
   FIX: «Условия MistTrack разобраны в разделе 2: Terms of Use от 2026-10-09 разрешают клиентские отчёты, коммерческие расследования и кэширование, но до начала коммерческого использования возможны KYB и проверка бизнес-модели. У
   Arkham условия коммерческого использования и кэширования в документации не найдены — нужны письменные.»

[12] MAJOR | Section 10, 'Решение'; A1 row 10; A7 (owner decisions)
   QUOTE: Статус: принято; конкретный IdP ждёт решения владельцев и пробы на сервере.
   PROBLEM: The authentication provider has no chosen solution (Keycloak, Logto, ZITADEL or external), yet A1 row 10 is marked 'принято' and A7 contains no question about it. Other decisions that Part B leaves to the owners are also
   missing from A7.
   FIX: A1, строка 10, статус: «принято; поставщик входа — условно». Добавить в A7: «17. **Поставщик входа:** на своём сервере ([рекомендация по умолчанию: Logto при 8 GB после замера памяти, Keycloak при 16 GB и более]) или внешний
   сервис, где учётные данные хранит третья сторона; допустим ли ZITADEL под AGPL; нужны ли в MVP MFA и организации. 18. **Решения из разделов части B:** размещение трасс моделей — Phoenix на своём сервере или Langfuse Cloud EU (раздел
   5); перечень действий, требующих подтверждения человеком (раздел 4); правило ввода графовой СУБД „выигрыш не менее чем в 3 раза“ (раздел 6); нужен ли MCP-сервер платформы для клиентов (раздел 11); нужна ли квалифицированная метка
   времени eIDAS или подпись PAdES (раздел 12); допустим ли Gotenberg с Chromium как запасной движок PDF (G10); шкала confidence (раздел 2).»

[13] MAJOR | Section 2, 'Как проверяем качество' (test set); A5 one-off costs; A7 item 7
   QUOTE: hard negatives из собственных платежей в шлюзы, swap-сервисы и казино
   PROBLEM: The ground-truth plan requires the team to make its own payments to casinos and swap services and control deposits to exchanges. Legality depends on the owners' jurisdiction, it needs KYC-verified exchange accounts, and
   neither point is raised in A7; this touches the principle 'only lawfully obtained data'.
   FIX: Раздел 2: «hard negatives из собственных платежей в платёжные шлюзы и swap-сервисы; платежи в казино — только при письменном подтверждении юриста, что это законно в юрисдикции владельцев (вопросы 2 и 8 в A7), иначе класс
   набирается из публично раскрытых адресов». A7, пункт 7: «…Anthropic и MistTrack, а также аккаунты на биржах для контрольных депозитов (потребуют KYC владельца аккаунта)…». A7, пункт 8: добавить «…и по допустимости контрольных
   платежей в сервисы для тестового набора меток».

[14] MAJOR | Section 10 'Лицензия и коммерческое использование'; section 9 'Лицензия и коммерческое использование'; A1 rows 9 and 10
   QUOTE: Лицензии Pydantic и uvicorn в досье не зафиксированы — не проверено.
   PROBLEM: Item 3 is unanswered for chosen components: uvicorn (the ASGI server), and in section 9 TanStack Router and zustand ('в аудите не зафиксированы — не проверено'), while A1 states 'MIT' for both rows. Pydantic is 'not
   verified' in section 10 but 'MIT' in section 12.
   FIX: Проверить по файлам LICENSE и записать. Раздел 10: «Pydantic — MIT (раздел 12); uvicorn — [лицензия по файлу LICENSE; ожидаемо BSD-3-Clause]». Раздел 9: «TanStack Router и zustand — [лицензии по файлам LICENSE; ожидаемо MIT]».
   До проверки в A1, строки 9 и 10, вместо «MIT» писать «MIT; у части зависимостей лицензия не проверена».

[15] MAJOR | Part A, A5 (variable-cost table and the paragraph under it); A6 row '≤ $1 на расследование'
   QUOTE: расчёт укладывается; не измерено
   PROBLEM: The default per-item limits in A5 add up to $0.95-1.02 ($0.05 data + $0.40 labels + $0.45 models + $0.05-0.08 search + $0-0.04 timestamp), so the Tavily plus commercial-timestamp configuration exceeds $1 while A6 says the
   estimate fits. No overall hard cap is stated.
   FIX: Под таблицей A5: «Сумма лимитов по статьям — от $0.95 (Brave, бесплатная метка времени) до $1.02 (Tavily, коммерческая метка времени). Поэтому сверх лимитов по статьям действует общий жёсткий лимит $1.00 на расследование: учёт
   бюджета отклоняет платный вызов, который вывел бы сумму за $1.00.» Либо снизить лимит моделей по умолчанию до $0.43. В A6 состояние: «расчёт укладывается только при общем лимите $1.00; не измерено».

[16] MAJOR | Section 3, 'Инфраструктура и затраты' (contradicts A2 item 3 and section 1)
   QUOTE: 6-10 тыс. вызовов на граф из 1 000 адресов, то есть 10-16 графов в день и около 20-30 QPS для 5 минут
   PROBLEM: Section 3 charges all 6-10 thousand calls to the TronGrid daily quota (10-16 graphs a day, 20-30 QPS); A2 and section 1 say only about 3 300 of them go to TronGrid (about 30 graphs a day, 11 rps). Owners see two capacity
   figures for the same free plan.
   FIX: «Расчётная оценка, не измерено: 6–10 тыс. вызовов на граф из 1 000 адресов, из них около 3 300 к TronGrid (раздел 1); суточной квоты хватает примерно на 30 таких графов, средняя нагрузка на TronGrid — около 11 запросов в
   секунду при сроке 5 минут.» Если верна оценка раздела 3, исправить A2 (пункт 3) и раздел 1.

[17] MINOR | Section 13, 'Решение' (need m: monitoring); A1 row 13; A3
   QUOTE: сначала VictoriaLogs, Grafana Alloy, Grafana, GlitchTip и внешний heartbeat, затем VictoriaMetrics с vmalert и SLO-дашбордом
   PROBLEM: It is not stated when the second observability step lands or what sends alerts before vmalert exists. Metrics are absent from A1 and A3, and Gatus is 'предпочтён' in the alternatives table but not in the decision.
   FIX: «Наблюдаемость вводится в два шага. Шаг 1, к первому развёртыванию: VictoriaLogs, Grafana Alloy, Grafana, GlitchTip, внешний heartbeat и проверки доступности Gatus; оповещения в Telegram или e-mail — из Grafana и heartbeat. Шаг
   2, до запуска production с клиентами: VictoriaMetrics с vmalert и SLO-дашбордом, включая долю успешного получения данных (цель ≥ 99%).» Подтвердить срок шага 2 и добавить VictoriaMetrics и Gatus в A1 (строка 13) и A3.

[18] MINOR | Section 8, 'Почему выбрано', fourth bullet (contradicts section 4)
   QUOTE: pydantic-ai 2.55.0 (MIT) имеет официальную durable-интеграцию с DBOS (extra `dbos>=2.10.0`) — тот же стек, что в G3.
   PROBLEM: Section 8 cites the official pydantic-ai/DBOS integration as a reason for the choice, while section 4 says that integration is deprecated, imports private DBOS modules and will not be used.
   FIX: «pydantic-ai 2.55.0 (MIT) совместим с DBOS по схеме „один запрос к модели — один @DBOS.step“; готовую durable-интеграцию (DBOSAgent) не используем: она помечена deprecated и импортирует приватные модули DBOS (раздел 4).» В
   «Ограничения и риски» раздела 8 убрать или пометить как неприменимое описание поведения готовой интеграции (буферизация стриминга, обёртка tool-функций).

[19] MINOR | Part A, A9 (last row) and A5
   QUOTE: Объём собственного кода больше, чем «только клей»: трассировщик, раскладка и сворачивание графа, шлюз
   PROBLEM: The brief's strategy is not to build what already exists; the document admits the own code exceeds glue but never totals the effort. Estimates are scattered across sections 2, 3, 4, 6, 9 and 11, and sections 5, 7, 10, 12
   and 13 give none.
   FIX: Добавить в A5 абзац «Трудозатраты на собственный код (оценки аудита, не измерено)»: «трассировщик 2–3 человеко-недели; оркестратор, учёт бюджета и журнал 2–3; шлюз и реестр инструментов 1.5–2.5; интерфейс и карта 4–5
   (верификатор отдельно оценивает раскрытие ветвей, агрегацию, раскладку и экспорт в 3–4); Label Store 3–5 дней; тестовый набор меток 5–8 человеко-дней; стенд графового теста 1–2 недели. Итого около 12–18 человеко-недель; по адаптеру
   LLMClient, схеме БД, API, отчётам и эксплуатации оценки нет.»

[20] MINOR | Part A, A1 table, licence column (rows 5, 7, 10, 12); A7 item 13
   QUOTE: коммерческие условия API; SDK MIT / Apache-2.0
   PROBLEM: The A1 licence column omits non-permissive licences of components named in Part B: Phoenix (Elastic License 2.0), psycopg 3 (LGPL-3.0, the default driver), identity-provider candidates (MPL-2.0, AGPL-3.0), and
   opentimestamps-client and docxtpl (LGPL). A7 item 13 mentions only GPL for on-premise delivery.
   FIX: Строка 5: «коммерческие условия API; SDK MIT / Apache-2.0; Phoenix — Elastic License 2.0 (только внутреннее использование)». Строка 7: «PostgreSQL License, MIT; драйвер psycopg 3 — LGPL-3.0». Строка 10: «MIT; поставщик входа —
   Apache-2.0, MPL-2.0 или AGPL-3.0 по выбору». Строка 12: «BSD-3-Clause, MIT, Apache-2.0; LGPL-библиотеки без распространения». A7, пункт 13: «…Во втором случае исключаются компоненты под GPL и пересматриваются компоненты под LGPL,
   AGPL и Elastic License 2.0.»

[21] MINOR | Section 14, 'Инфраструктура и затраты', 'Переменные'
   QUOTE: MistTrack ($0.10 за вызов address_labels) учтён в разделе 2.
   PROBLEM: $0.10 is the price only on the $1 000 package; section 2 and A5 use $0.20 per call on the $20 package as the default.
   FIX: «MistTrack ($0.10–0.20 за вызов address_labels в зависимости от пакета) учтён в разделе 2.»

[22] MINOR | Section 13, 'Инфраструктура и затраты' vs A5 (fixed costs, 'Минимум' column)
   QUOTE: Итого фиксированно в месяц: сервер €8.49 (бюджет считается без 12-месячной оплаты) + heartbeat $20 + B2 от $0 + домен
   PROBLEM: Section 13 budgets the $20 heartbeat as a fixed cost of the paid product and adds the domain; the A5 minimum shows $0 for monitoring and a total of '€8.5 + $49' with neither.
   FIX: A5, колонка «Минимум», строка «Мониторинг и журналы»: «$0 на своём сервере; внешний heartbeat healthchecks.io Business $20 — для платного продукта (раздел 13)». Строка «Итого», минимум: «около €8.5 + $49; для платного продукта
   плюс $20 heartbeat и домен около $1».

[23] MINOR | Section 1, 'Что проверить до фиксации выбора (Этап 2)', item 3
   QUOTE: Проба Chainstack: живые вызовы, internal_transactions в receipt, множитель RU для TRON (1 или 2)
   PROBLEM: The whole fact-verification design rests on Chainstack being independent of TronGrid, but that is asserted rather than verified, and the Stage 2 probe does not check it, although the same document detected a shared gateway
   between TronScan and TronGrid.
   FIX: «3. Проба Chainstack: живые вызовы; подтверждение, что узлы собственные, а не прокси TronGrid (сравнение формата ошибок и заголовков, как при проверке TronScan, и письменный ответ); internal_transactions в receipt; множитель RU
   для TRON (1 или 2); письменное подтверждение допустимости SaaS-использования.»

######################################################################
# LENS consistency  {'blocker': 1, 'major': 15, 'minor': 9}
VERDICT: Not yet fit to send on the internal-consistency lens, though it is close and needs no new research. Part A is coherent with itself, but several fact-checked sections still contradict each other and Part A on numbers the owners will act
on: TronGrid load and quota, MistTrack terms and call count, the LLM cost ceiling, default budget limits that add up to as much as $1.02, and which library is chosen for the LLM access layer. The single most important fix is to settle
where the edge key (event_index) and the edge confirmation come from, then state the TronGrid request count, quota (30 versus 10-16 graphs a day) and required speed (11 versus 20-30 requests per second) identically in A2 п. 3, G6 and
sections 1, 3 and 6. Table A1 statuses match the sections' «Решение» paragraphs except for mixed statuses flattened inconsistently in four rows.

[24] BLOCKER | A2, п. 3; раздел 1 «Инфраструктура и затраты» (граф на 1 000 адресов); раздел 3 «Инфраструктура и затраты» (квота TronGrid)
   QUOTE: По расчёту такой граф требует 6–10 тысяч запросов, из них около 3 300 к TronGrid
   PROBLEM: A2 п. 3 and section 1 say a 1,000-address graph costs about 3,300 TronGrid requests (11 rps, about 30 graphs a day on the free quota). Section 3 charges all 6-10 thousand calls to the same quota: «10-16 графов в день и
   около 20-30 QPS для 5 минут». The gap equals the per-TXID calls to /v1/transactions/{txid}/events that G6 and section 6 need for the edge key and that section 1 does not count (3,300 + 3,000-4,000 edges = 6,300-7,300, i.e. 14-16
   graphs a day, 21-24 rps). Section 3 is more likely right for the design as written; section 1 holds only if event_index can be taken from the node receipt, which the document never says. Owners see the optimistic number for a
   headline MVP criterion.
   FIX: Decide where event_index comes from and use one set of numbers in all three places. A2 п. 3: «По расчёту такой граф требует 6–10 тысяч запросов. К TronGrid из них идёт от 3 300 (если индекс события удаётся брать из квитанции
   независимого узла) до 6–7 тысяч (если для каждого ребра нужен отдельный запрос событий транзакции у TronGrid). Суточной квоты бесплатного плана (100 000 запросов) хватает на 14–30 таких графов, а нужная скорость — 11–24 запроса в
   секунду.» Put the same range into section 1 («около 3 300 запросов TronGrid…») and section 3 («6-10 тыс. вызовов…»).

[25] MAJOR | G6 (A4); A8, п. 1; раздел 1 «Что проверить», п. 5; раздел 3 «Как проверяем качество», 1-й пункт; раздел 6 «Как проверяем качество», 1-й пункт
   QUOTE: наличие поля `event_index` в `/v1/transactions/{txid}/events` (нужно для идентичности ребра)
   PROBLEM: Section 1, G6 and A8 п. 1 treat the presence of event_index as unverified. Section 3 reports a live probe of 2026-10-13/14 in which this endpoint «отдаёт block_number и event_index», and section 6 cites a live URL for it;
   those two are more likely right. Separately, section 3 says each report edge «подтверждается через /v1/transactions/{txid}/events лениво» (TronGrid itself, report edges only), while G5, A3, A6 and section 1 require a receipt from an
   operator other than TronGrid, and section 6 needs event_index in the key of every stored edge, not lazily.
   FIX: G6, last sentence: «Поле event_index в живой пробе TronGrid присутствует (разделы 3 и 6); на Этапе 2 проверяются его стабильность и совпадение с позицией лога в квитанции независимого узла.» Section 1, п. 5: replace the quoted
   fragment with «стабильность `event_index` и его соответствие позиции лога в receipt (нужно для идентичности ребра)». Section 3 bullet: «Ключ ребра (event_index) берётся из /v1/transactions/{txid}/events при записи ребра; каждое
   ребро, попавшее в отчёт, дополнительно подтверждается receipt у оператора, отличного от TronGrid (раздел 1, G5); идентичность ребра и фильтры — по G6.» A8 п. 1: «Наличие и стабильность event_index» → «Стабильность event_index и его
   соответствие логам квитанции».

[26] MAJOR | раздел 3 «Лицензия и коммерческое использование», 4-й пункт; раздел 3 «Что проверить», пункт про Arkham и MistTrack
   QUOTE: Условия коммерческого использования и кэширования у MistTrack и Arkham в документации не найдены — нужны письменные.
   PROBLEM: Section 2 reads MistTrack's Terms of Use of 2026-10-09 as the most explicit permission among vendors: client PDF reports, commercial investigations and caching are allowed, resale as a standalone data product is not, and a
   Commercial Use Review may be required. Section 3 says such terms were not found at all. Section 2 is more likely right: it cites the dated document and its URL, and A1 and G7 rely on its reading.
   FIX: Replace with: «Terms of Use MistTrack от 2026-10-09 разрешают клиентские отчёты, коммерческие расследования и кэширование (раздел 2); письменно остаётся подтвердить прохождение Commercial Use Review и экспорт меток в JSON-
   отчёт. У Arkham условия коммерческого использования и кэширования в документации не найдены — нужны письменные.» In «Что проверить»: «MistTrack: письменные условия коммерческого использования» → «MistTrack: Commercial Use Review по
   разделу 2».

[27] MAJOR | раздел 4 «Решение»; раздел 5 «Решение»; раздел 11 «Лицензия и коммерческое использование»; G13; A1, строки 4–5; A8, п. 4
   QUOTE: и Pydantic AI для LLM-шагов в точках принятия решений; всё работает на том же PostgreSQL
   PROBLEM: Section 4 fixes Pydantic AI as the LLM layer; section 5 fixes «официальные SDK за собственным адаптером LLMClient»; section 11 lists Pydantic AI among «используемые библиотеки»; G13 says the choice between the two is made
   at Stage 2. A1 row 4 does not mention Pydantic AI and A8 has no check that decides it. G13 is the most likely intended position (Part A was written after both sections), so the two «Решение» paragraphs must be aligned to it.
   FIX: Section 4: «…на DBOS Transact (durable workflows, очереди, HITL); LLM-шаги в точках принятия решений идут через собственный интерфейс LLMClient (G13). Pydantic AI — кандидат реализации под ним; выбор между Pydantic AI и
   официальными SDK делает проверка Этапа 2; всё работает на том же PostgreSQL…». Section 5: «Доступ — только через собственный адаптер LLMClient, без LLM-gateway; под ним официальные SDK либо Pydantic AI (G13, решается на Этапе 2)».
   Section 11: «Используемые библиотеки: Pydantic AI — MIT» → «Кандидат для регистрации инструментов: Pydantic AI — MIT (G13)». A8 п. 4, add: «Выбор реализации под LLMClient: Pydantic AI или официальные SDK.»

[28] MAJOR | A5, таблица «Переменные, на стандартное расследование» и абзац под ней; раздел 5 «Инфраструктура и затраты», пункт о переменных
   QUOTE: | **Итого** | | **около $1.00** |
   PROBLEM: The default limits add up to $0.95-1.02 ($0.05 data + $0.40 labels + $0.45 models + $0.05 or $0.08 search + €0-0.04 timestamp). With Tavily and a commercial timestamp service, which section 12 says is budgeted for the paid
   product, the defaults exceed the owners' $1 cap. The next paragraph treats $0.57 on models as an allowed case although the model limit in the same table is $0.45, a figure that appears in no section. Section 5 also reserves
   «$0.10-0.25» for web search via Anthropic's built-in search, while A5, G15 and section 14 use 10 queries to Brave or Tavily for $0.05-0.08.
   FIX: Make the defaults sum to at most $1, for example a model limit of $0.40, and show the range: «**Итого** | | **$0.90–0.97; общий лимит $1 действует поверх постатейных**». Paragraph: «Запаса почти нет. Тяжёлый случай ($0.57 на
   модели) превышает лимит на модели: при его достижении шаги переводятся на Haiku 5.5, а текст отчёта собирается без модели.» Section 5: «Из него $0.05–0.16 — веб-поиск: 10–20 запросов к Brave или Tavily через собственный адаптер
   (раздел 14, G15); встроенный поиск Anthropic не используется».

[29] MAJOR | раздел 2 «Решение»; раздел 3 «Инфраструктура и затраты» и «Почему выбрано»; раздел 14 «Инфраструктура и затраты»; G7; A5
   QUOTE: При 2-4 адресах (G7) и пакетах на 100-1 000 вызовов ($0.15-0.20) это расчётно $0.30-0.80 на расследование
   PROBLEM: G7, A5 and A7 (вопрос 5) set a default of 2 paid calls, up to $0.40. Sections 2 and 3 plan «2–4» calls, and section 3 attributes that range to G7; at 4 calls ($0.80) the $1 budget cannot hold. Part A's default of 2 is the
   later, budget-driven decision. The price per call also differs: section 14 says «$0.10 за вызов address_labels», which per section 2 and A5 applies only to the $1,000 pack ($0.20 on the $20 pack the plan starts with). Section 3 says
   «$0.03-0.20 (30 адресов = $3-6)», but $0.03 × 30 is $0.90.
   FIX: Section 2: «…с оплатой за вызов; лимит по умолчанию — 2 терминальных адреса на расследование (G7), настраивается до 4». Section 3: «При лимите по умолчанию в 2 вызова (G7) и пакетах на 100–1 000 вызовов ($0.15–0.20) это
   расчётно $0.30–0.40 на расследование; при 4 вызовах — до $0.80». Section 3, «Почему выбрано»: «(30 адресов = $0.90–6)». Section 14: «MistTrack ($0.10–0.20 за вызов address_labels в зависимости от пакета) учтён в разделе 2».

[30] MAJOR | раздел 4 «Инфраструктура и затраты» и «Что проверить», п. 6; раздел 5 «Почему выбрано»; A5; A8, п. 4
   QUOTE: ориентир: LLM-часть не выше $0.30, верхней границы оценки аудита
   PROBLEM: Three ceilings exist for the same cost item. Section 4 expects $0.05-0.30 per investigation (25 model calls) and tests against $0.30; section 5 computes $0.40 typical and $0.57 heavy (106 and 158 calls); A5 sets a $0.45
   limit. Section 4 notes the divergence itself, but Part A does not, and A8 п. 4 omits the comparison of the two routing schemes that section 4 requires. Section 5 is more likely right for the routing fixed in G13; $0.30 belongs to
   the narrower «только эскалации» scheme.
   FIX: Section 4, п. 6: «…— ориентиры: не выше $0.30 для схемы «Sonnet 5.5 только на эскалациях» и не выше лимита на модели из A5 для схемы G13; расхождение в числе вызовов (25 в этой оценке, 106 в разделе 5) закрывается замером». A8
   п. 4, add: «сравнение двух схем маршрутизации моделей по фактической стоимости».

[31] MAJOR | A8, п. 1 (и A5, разовые расходы Этапа 2)
   QUOTE: Живая проба Chainstack: возвращает ли он internal transactions и как тарифицирует TRON.
   PROBLEM: G5, A2 п. 2, A6 and A9 all defer the choice of the second independent address index to Stage 2, A5 budgets its trial, and sections 1 (п. 4) and 3 list it with pass criteria. None of A8's nine items contains it, although A8
   claims to close every «не измерено», and the ≥ 99% data-retrieval criterion cannot be measured without it.
   FIX: Add to A8 п. 1: «Проба второго независимого адресного индекса (Blockbook-TRON через NOWNodes; Bitquery — только при письменно подтверждённой глубине архива). Критерий: полное совпадение с TronGrid на контрольных окнах,
   известные цена и глубина истории.»

[32] MAJOR | A8, п. 3; раздел 7 «Состояние проекта»; раздел 8 «Ограничения и риски» и «Как проверяем качество»; раздел 10 «Что проверить»
   QUOTE: DBOS против варианта без него: принудительное завершение воркера посреди расследования, деплой посреди расследования
   PROBLEM: Sections 7 and 8 both mark «Работа DBOS на PostgreSQL 18 — не проверено», and G2 and G3 fix exactly this pair, yet A8 п. 3 does not list the check. It also omits two spike criteria from sections 8 and 10: the simple
   transaction within 30 seconds end to end (two default 1.0 s polls put it at risk) and the planted key not appearing in the DBOS system database.
   FIX: Append to A8 п. 3: «Работа DBOS 3.2 на PostgreSQL 18.6 с SQLAlchemy 2.0.54; сквозной замер «простая транзакция за 30 секунд» через API, очередь и SSE при интервале опроса 0.1–0.25 с; подставной ключ не находится в системной БД
   DBOS.»

[33] MAJOR | раздел 8 «Почему выбрано», 4-й пункт; раздел 8 «Что проверить», 4-й пункт; против раздела 4 «Состояние проекта» (Pydantic AI)
   QUOTE: pydantic-ai 2.55.0 (MIT) имеет официальную durable-интеграцию с DBOS (extra `dbos>=2.10.0`) — тот же стек, что в G3.
   PROBLEM: Section 8 gives the official pydantic-ai/DBOS integration as a reason for the choice and plans to test it. Section 4 says `DBOSDurability` imports private DBOS modules, `DBOSAgent` is deprecated and «готовую интеграцию не
   используем». Section 4 is more likely right because it read the code. The reference «тот же стек, что в G3» is also wrong: G3 does not mention Pydantic AI.
   FIX: Replace the bullet with: «У pydantic-ai 2.55.0 есть durable-интеграция с DBOS (extra `dbos>=2.10.0`), но она импортирует приватные модули DBOS, а `DBOSAgent` помечен deprecated (раздел 4): готовую интеграцию не используем,
   запрос к модели оформляется обычным `@DBOS.step`.» In «Что проверить»: «Проверить один LLM-шаг через LLMClient внутри `@DBOS.step` (один запрос модели — один durable step)».

[34] MAJOR | G14 (A4); раздел 10, таблица альтернатив (Keycloak) и «Ограничения и риски»; G12 против раздела 13 «Инфраструктура и затраты»
   QUOTE: на сервере с 8 GB, где уже работают база, воркер и мониторинг, не помещается с запасом; он уместен при 16 GB и более
   PROBLEM: G14 states as fact that Keycloak does not fit with margin on the 8 GB server. Section 10 says the memory figures come from documentation («не измерено»), «хватит ли памяти — не измерено», and its table calls Keycloak the
   «IdP при сервере от 8 GB RAM»; section 13 adds that the roughly 6 GB whole-stack estimate is unmeasured and excludes the IdP. The sections' caveat is right. Related: G12 and A5 call 16-24 GB the recommended start, while section 13
   budgets production on the 8 GB VPS-2 and calls the 24 GB VPS-4 «путь роста».
   FIX: G14: «Keycloak по документации занимает 1.25–1.36 GB; поместится ли он на сервере с 8 GB рядом с базой, воркером и мониторингом, не измерено и проверяется пробой на Этапе 2; с запасом он уместен при 16 GB и более. Иначе —
   Logto, ZITADEL или внешний сервис.» Section 10 table: «IdP при сервере от 8 GB RAM» → «Кандидат IdP; на 8 GB — только после замера, с запасом — от 16 GB (G14)». Section 13: «Путь роста: OVH VPS-4» → «Рекомендуемая стартовая
   конфигурация по G12: OVH VPS-4».

[35] MAJOR | A5, таблица постоянных затрат и абзац «Разовые расходы Этапа 2»; A1, строка 13; раздел 13 «Инфраструктура и затраты»
   QUOTE: | **Итого** | **около €8.5 + $49** | **около €20 + $69–200** |
   PROBLEM: Section 13 budgets healthchecks.io Business at $20 a month for the paid product (the free tier is «для разработки») and sums the fixed cost as server €8.49 + heartbeat $20 + B2 + domain (about $1). A5 puts the $20 only
   under «Рекомендуется» and omits the domain, so its minimum is about $21 below the section's own total; A1 row 13 shows only the server. The recommended column mixes a 12-month prepaid price with a no-commitment minimum. In the one-
   off list, the €21.73 stand is a 12-month-contract price, the $50-150 for control deposits already contains the MistTrack trial listed separately, and Bitquery Pro at $99 excludes the archive add-on that sections 2 and 3 say deep
   history needs ($198 a month). Section 13 is more likely right.
   FIX: Minimum, monitoring cell: «healthchecks.io Business: $20 (бесплатный тариф — только для разработки)». Totals: «около €8.5 + $70» and «около €20 (при оплате за 12 месяцев) + $70–200», with the note «включая домен около $1». A1
   row 13: «сервер от €8.49/мес + $20 внешний контроль доступности». One-off list: «стенд замеров с выделенными ядрами €21.73/мес (цена при контракте на 12 месяцев)»; «Bitquery Pro $99–198 за месяц (с дополнением для архива)»;
   «контрольные депозиты на биржи … $50–150 (включая пробу MistTrack)».

[36] MAJOR | раздел 14 «Как проверяем качество», 2-й пункт; A6, строка «≥ 50 сценариев»; раздел 3 «Как проверяем качество» (Сценарии)
   QUOTE: Адреса из OFAC SDN и из событий AddedBlackList входят в тестовый набор как ground truth: не менее 10 из 50 сценариев
   PROBLEM: A6 and section 3 count only synthetic-exact and self-generated scenarios toward the required 50 and keep freeze-anchored cases as a separate class. Section 14 counts at least 10 sanction and freeze cases inside the 50. A6
   and section 3 agree with each other and are more likely right. A6 also says the self-made scenarios are created «в тестовой сети», while no section mentions a test network (sections 2 and 3 speak of own transfers and deposits with
   TXID).
   FIX: Section 14: «Адреса из OFAC SDN и из событий AddedBlackList образуют отдельный класс сценариев (не менее 10 кейсов) для измерения precision и recall; в 50 сценариев с точно известным ответом они не засчитываются (раздел 3,
   A6).» A6: «созданные нами в тестовой сети» → «созданные нами собственными переводами» (or name the test network in section 3 if that is the plan).

[37] MAJOR | G7 (A4); раздел 14 «Решение», «Почему выбрано» и «Как проверяем качество»; раздел 2 «Решение» и «Как проверяем качество»
   QUOTE: OFAC SDN (контрольное значение 340 адресов TRON на 2026-10-01)
   PROBLEM: 340 is the count in the 0xB10C mirror. Section 14 found only 337 of these in the primary sdn.csv and sdn_comments.csv, yet G7 and section 14's «Решение» present 340 as the control value of the OFAC list itself. The sections
   also build the set differently: section 2 parses the primary SDN_ADVANCED.XML and collects TRON addresses «из всех тикерных списков, не только TRX и USDT»; section 14 builds it «из файлов TRX и USDT» of the mirror. Section 14's
   recount against primary files is the more reliable number.
   FIX: G7: «OFAC SDN (собственный разбор первичного файла; контрольное значение — 340 адресов TRON по зеркалу 0xB10C на 2026-10-01, из них 337 найдены в первичных файлах, расхождение выясняется на Этапе 2)». Section 14 «Решение»:
   «(340 адресов TRON по зеркалу, 337 подтверждены первичными файлами)». Section 14, quality bullet: «Набор OFAC собирается разбором первичного файла по всем тикерным спискам (раздел 2) и каждую ночь сверяется с зеркалом 0xB10C».

[38] MAJOR | A7 (вступительная фраза и список вопросов); разделы 4, 5, 6, 10, 12 «Что проверить» (решения владельцев); G10
   QUOTE: Вопросы 1–8 блокируют начало Этапа 2; остальные можно закрыть по ходу.
   PROBLEM: Sections put decisions on the owners that are not among A7's 16 questions: the identity provider (section 10: «конкретный IdP ждёт решения владельцев»), the rule for introducing a graph database (section 6: «требует
   согласия владельцев»), where model traces are kept (section 5, п. 9), a qualified timestamp or PAdES signature (section 12, п. 4), the actions that need human approval (section 4, п. 7), and Gotenberg, which G10 allows «только по
   вашему решению». Also, question 16 says the first-case data «нужны к началу Этапа 2» but is outside the blocking range 1-8.
   FIX: First sentence: «Вопросы 1–8 и 16 блокируют начало Этапа 2; остальные можно закрыть по ходу.» Add: «17. **Поставщик входа:** свой сервер или внешний сервис (учётные данные у третьей стороны); допустим ли AGPL (ZITADEL); нужны
   ли MFA и организации в MVP. 18. **Графовая СУБД:** принимаете ли правило «вводится только при выигрыше не менее чем в 3 раза либо если базовый вариант не укладывается в сроки»; нужны ли аналитикам запросы по всему накопленному
   графу. 19. **Трассы моделей:** Phoenix на своём сервере или Langfuse Cloud EU. 20. **Метка времени и подпись:** нужна ли квалифицированная метка (eIDAS) или подпись PAdES; допустим ли Gotenberg с Chromium как запасной движок PDF.
   21. **Действия, требующие подтверждения человеком.**»

[39] MAJOR | A2, п. 6; раздел 14 «Почему выбрано», последний пункт; раздел 12 «Состояние проекта», последний пункт; A10
   QUOTE: Возврат средств идёт только через правоохранительные органы.
   PROBLEM: Section 12 records the verifier's correction that this thesis is «слишком широк»: TRM Beacon Network claims access for vetted security companies, and its joining conditions are a Stage 2 check. Section 14 adds that Tether's
   cs.tether.to portal was not read. A2 п. 6 and section 14 still state the conclusion flatly; section 12's caveat is more likely right. Section 12 and A10 also say Tether's requirements page returned 404, while section 14 quotes
   Tether's law-enforcement policy of 2018-01-03 as read.
   FIX: A2 п. 6: «**Для жертвы возврат средств идёт через правоохранительные органы.** На сайте Tether пути для жертвы не найдено (портал cs.tether.to не прочитан): запрос принимают от органа с правовым основанием. TRM Beacon Network
   заявляет доступ для проверенных security-компаний; условия вступления проверяются на Этапе 2.» Section 14: «Возврат идёт только через органы.» → «Для жертвы возврат идёт через органы.» In A10 and section 12, name which Tether page
   returned 404, since section 14 read the law-enforcement policy.

[40] MINOR | A1, строки 4 и 8 (столбец «Заменяемость»); раздел 4 «Заменяемость»; раздел 8 «Заменяемость»
   QUOTE: Высокая при соблюдении изоляции. Durable-слой закрывается одним модулем-адаптером (декораторы workflow/step, очереди, `send/recv`)
   PROBLEM: The same DBOS layer is rated «высокая» in section 4 and A1 row 4 («закрывается одним модулем-адаптером») and «средняя» in section 8 and A1 row 8 («Декораторы … пронизывают код оркестрации»). Section 8 is more likely right:
   it read the code, and section 4 itself says the replacement effort is «не измерено».
   FIX: A1 row 4, «Заменяемость»: «средняя для durable-слоя (как в строке 8), высокая для LLM-слоя». Section 4: «Для LLM-слоя — высокая; для durable-слоя — средняя, как в разделе 8: декораторы DBOS пронизывают код оркестрации, поэтому
   нужен адаптер JobRunner.»

[41] MINOR | A9, строка 1; A2, п. 9; A2, п. 2
   QUOTE: Зависимость от одного оператора: адресный индекс и internal transactions есть только у TronGrid
   PROBLEM: Three Part A statements are firmer than their sections. (1) Section 1 says internal transactions at Chainstack are «не проверено», and A8 п. 1 tests exactly this. (2) A2 п. 9 says of the DBOS findings «Всё устранимо
   настройкой», but section 8 says automatic takeover of a crashed worker's work exists only in paid Conductor and that recovery is «на практике не проверено». (3) A2 п. 2 states the TronScan prohibition flatly, while G5 notes it is
   unconfirmed that the 2022 document is the current edition.
   FIX: (1) «…адресный индекс и internal transactions вживую подтверждены только у TronGrid (у Chainstack не проверено)». (2) «По документации и коду это закрывается настройкой и политикой перезапуска воркера; на практике не проверено,
   поэтому до Этапа 2 есть более простой запасной путь.» (3) After the ToS sentence add: «(действующая ли это редакция, не подтверждено — см. G5)».

[42] MINOR | раздел 14 «Решение» и «Почему выбрано»; раздел 11 «Как проверяем качество», 2-й пункт; раздел 8 «Инфраструктура и затраты» (Token bucket); G4, G5
   QUOTE: чёрный список контракта USDT (`isBlackListed` и события через TronGrid)
   PROBLEM: G5 and section 1 assign constant calls, including the final isBlackListed, to an operator other than TronGrid; section 14 routes isBlackListed through TronGrid. Section 11 describes the TronGrid-versus-node cross-check as
   «по выборке TXID», while section 1 and A6 require it for every fact. Section 8 places the limiter in «один fetcher-процесс на провайдера», while G4 and section 11 describe the gateway as running inside the application process. G5,
   section 1 and section 11 are the reconciled positions.
   FIX: Section 14: «чёрный список контракта USDT (события через TronGrid, итоговый `isBlackListed` — у независимого оператора узла, G5)». Section 11: «Перекрёстная сверка по выборке TXID» → «Сверка каждого факта отчёта (и выборочно —
   остальных TXID)». Section 8: «в MVP — ограничитель aiolimiter внутри HTTP-шлюза в единственном процессе воркера (G4)».

[43] MINOR | раздел 3 «Что проверить», 3-й пункт; раздел 5 «Как проверяем качество», «Состояние проекта», «Что проверить» п. 8; раздел 7 «Инфраструктура»; раздел 12 «Ограничения и риски»; раздел 13 «Ограничения и риски»
   QUOTE: Выбрать второй независимый TransferSource (кандидаты — в G5).
   PROBLEM: Several cross-references point to a G decision that does not contain the thing cited. G5 names no index candidates (section 1 does). «раздел G11» is not a section. G3 does not mention Pydantic AI (G13 does). G12 does not
   cover backups (section 13 does). G13 does not mention the trace UI (section 5 does). G10 does not name Graphviz (section 9 does).
   FIX: Section 3: «(кандидаты — в разделе 1)». Section 5: «(до подписи и timestamp, G11)»; «Pydantic AI (G13, раздел 4)»; «В спайке G3: вызовы Pydantic AI…» → «В проверке G13 (spike раздела 4): вызовы Pydantic AI…». Section 7: «Бэкап
   — pgBackRest + restic в Backblaze B2 (раздел 13)». Section 13: «UI трасс (раздел 5)». Section 12: «Кандидат G10 (SVG из Graphviz)» → «Кандидат из раздела 9 (SVG из Graphviz)».

[44] MINOR | раздел 3 «Инфраструктура и затраты», последний пункт; раздел 6 «Как проверяем качество» (Метки); раздел 2, таблица альтернатив (Arkham); A10; раздел 1 «Инфраструктура» (Кэш); раздел 10 «Лицензия»
   QUOTE: keyless-доступ TronGrid (по документации — жёсткое ограничение или отказ; не измерено)
   PROBLEM: Some «не проверено / не измерено» markers are contradicted by other sections. Section 1 measured keyless TronGrid at 3 rps, then 429 and a 5 s pause. Section 6 says RemovedBlackList and DestroyedBlackFunds were not checked
   live, while sections 1-3 report them returned live. Section 2 and A10 say arkm.com was unreachable and Arkham prices unverified, while section 3 reads prices from arkm.com/llms.txt. Section 1 gives a blacklist mirror of «около 7.8
   тыс. записей» while section 2 says no full count was made. Section 10 says Pydantic's licence is unverified while section 12 states MIT. The sections holding the concrete probe are more likely right.
   FIX: Section 3: «keyless-доступ TronGrid (без ключа измерено 3 rps, затем 429 и пауза 5 с — раздел 1)». Section 6: «RemovedBlackList и DestroyedBlackFunds получены вживую в пробах разделов 1–3». Section 2 and A10: «сайт arkm.com не
   открывался; цены Arkham прочитаны из arkm.com/llms.txt (раздел 3)». Section 1: «около 7.8 тыс. записей (оценка; полный подсчёт событий не выполнялся, раздел 2)». Section 10: «Лицензия uvicorn в досье не зафиксирована — не проверено
   (Pydantic — MIT, раздел 12)».

[45] MINOR | A8 (вступительная фраза и пп. 2, 4, 6, 7, 9); разделы 2, 5, 7, 10, 11, 12, 14 «Что проверить»
   QUOTE: Каждая закрывает конкретное «не измерено» из этого документа.
   PROBLEM: Beyond the second index and DBOS on PostgreSQL 18, A8 omits further section-level checks: the comparison of three strong-tier models and the reading of the OpenAI agreement that G13 makes a precondition for the fallback
   (section 5, пп. 3-4); Cyrillic rendering and font embedding, unverified per section 12 п. 3 although reports are in Russian; the IdP probe on the reference server (section 10); RLS overhead (section 7); calibration of the deposit
   heuristic (section 2, п. 7); replay from stored responses (sections 4 and 11); written answers from Brave, Chainabuse and SSLMate (section 14).
   FIX: Add: п. 2 — «Brave (если выбран): журнал и передача выдачи в модель; Chainabuse и SSLMate: условия.» п. 4 — «Сравнение трёх вариантов сильной модели; чтение договора OpenAI и проверка закрепления версий до включения запасного
   провайдера.» п. 6 — «Рендер кириллицы и встраивание шрифтов.» п. 7 — «Калибровка эвристики на активных горячих кошельках.» п. 9 — «Проба поставщика входа на эталонном сервере; накладные расходы RLS; повторный прогон из сохранённых
   ответов даёт тот же граф и отчёт.»

[46] MINOR | A1, столбцы «Статус» (строки 2, 9, 10, 13) и «Лицензия» (строки 5, 7, 9, 12); A7, вопрос 13
   QUOTE: pgBackRest и restic в Backblaze B2; SOPS и age | принято |
   PROBLEM: Mixed decisions are flattened inconsistently: rows 2 and 9 (accepted core, conditional part) show «условно», while rows 10 and 13 (IdP open; pgBackRest on B2 and 8 GB sufficiency conditional per section 13) show «принято».
   The licence column omits components the sections name: psycopg 3, the default driver (LGPL-3.0, sections 6-7), opentimestamps-client and docxtpl (LGPL, section 12), Phoenix (Elastic License 2.0, section 5); row 9 says «MIT» although
   section 9 leaves TanStack Router and zustand «не проверено». A7 вопрос 13 says GPL components would be excluded for on-prem delivery, but the chosen stack has none at runtime; the affected ones are LGPL, AGPL and ELv2.
   FIX: Statuses: row 2 «принято (Label Store); условно (MistTrack)»; row 9 «принято (SPA); условно (карта и раскладка)»; row 10 «принято; поставщик входа — за вами»; row 13 «принято; условно: pgBackRest на B2, достаточность 8 GB».
   Licences: row 5 add «Phoenix — Elastic License 2.0»; row 7 «PostgreSQL License, MIT; драйвер psycopg 3 — LGPL-3.0»; row 9 «MIT (TanStack Router и zustand — не проверено)»; row 12 add «клиент OpenTimestamps и docxtpl — LGPL». A7
   вопрос 13: «Во втором случае нужна юридическая оценка компонентов под LGPL (psycopg 3, клиент OpenTimestamps, docxtpl), AGPL (Grafana, ZITADEL) и Elastic License (Phoenix).»

[47] MINOR | раздел 3 «Как проверяем качество», последний пункт; раздел 2 «Как проверяем качество» и «Инфраструктура и затраты»; A2, п. 4
   QUOTE: Тест меток: >= 300 адресов из независимых источников с отрицательным классом и доверительным интервалом; 10-15 контрольных депозитов
   PROBLEM: The same label test set has three sizes: section 2 plans 600+ addresses and prices 400-500, while section 3 requires ≥ 300. Own deposit addresses are 10-30 in section 2 and A2 п. 4 but 10-15 in section 3. Section 2 is the
   dedicated section and more likely right.
   FIX: Section 3: «Тест меток — независимый набор из раздела 2 (первая версия 400–500 адресов, цель 600+) с отрицательным классом и доверительным интервалом; 10–30 контрольных депозитов дают нижнюю границу не выше 88.6% и цель не
   доказывают.»

[48] MINOR | раздел 1 «Заменяемость»; раздел 2 «Заменяемость»; раздел 3 «Заменяемость» и «Как проверяем качество»; A5; «Как читать»
   QUOTE: Интерфейс TransferHistoryProvider; вторая реализация — индекс стороннего оператора, не TronScan.
   PROBLEM: Key terms drift. The same interfaces are TransferHistoryProvider and LabelProvider in sections 1-2 but TransferSource and LabelSource in section 3. «Стандартное расследование» is about 40 addresses in section 1, 30 in
   section 3, 45 (heavy 60) in section 5 and «несколько десятков» in A5 and section 6. «Аудит» means the whole verified study in Part A, but in the sections it often means the unverified first-pass research («исходный аудит»,
   «первичный аудит», «тезис аудита опровергнут»), alongside «верификатор», «проверяющий», «перепроверка».
   FIX: Use TransferSource and LabelSource in sections 1 and 2. Define once in A5 and reuse: «стандартное расследование — 40–45 адресов (тяжёлое — 60)». Add to «Как читать»: «В части B «аудит» или «исходный аудит» — первичное
   исследование направления, «верификатор» — независимая перепроверка; там, где они расходятся, действует вывод верификатора.»

######################################################################
# LENS measurability  {'blocker': 2, 'major': 20, 'minor': 3}
VERDICT: Not fit to send yet on this lens (C:/LEDGERHUNT CRYPTO/docs/stage-1-stack-proposal.md, all 1,512 lines read). The document is candid that nothing is measured, but the per-investigation cost table does not add up to at most $1 by its
own numbers, and it leaves compute, storage and the volume assumption out of the cost definition. A6 has no row for about a third of the Prompt 3 sub-criteria, and most rows it does have name no metric or recording component. The
single most important fix is to rebuild the A5 per-investigation table around one hard global limit with stated inclusions (issues 1-2); after that, extend A6 to one row per sub-criterion with metric, recorder and status.

[49] BLOCKER | A5, таблица «Переменные, на стандартное расследование», строка «Итого»; A6, строка «≤ $1 на расследование»
   QUOTE: | **Итого** | | **около $1.00** |
   PROBLEM: The default limits do not add up to at most $1 in the document's own worst combination: labels $0.40 + models $0.45 + Tavily $0.08 + commercial timestamp about $0.04 + data share $0.05 (counted in A2.5) = $1.02. The model
   limit ($0.45) is also below the document's own heavy case ($0.57), which section 5 says omits thinking-block growth and billed refusals, so the A6 status «расчёт укладывается» is not supported.
   FIX: Replace the row with: «| **Итого по лимитам** | | **$0.90–0.97 переменных затрат; с долей подписки на узел ($0.05) — $0.95–1.02** |». Replace the paragraph after the table with: «Сумма лимитов по статьям сама по себе не
   гарантирует $1: при Tavily и коммерческой метке времени она даёт $1.02. Поэтому поверх лимитов по статьям действует общий жёсткий лимит $1.00 на расследование: платный вызов не отправляется, если его максимальная стоимость выводит
   сумму за лимит. Оценка $0.57 на модели — не верхняя граница: она не учитывает рост входа из-за thinking-блоков и оплачиваемые отказы модели. При достижении лимита моделей ($0.45) отчёт выпускается без текста модели, полученные
   результаты сохраняются.» In A6 change the status to «типичный расчёт — $0.90–0.97; гарантию даёт только общий лимит; не измерено».

[50] BLOCKER | A5, строка «Данные TRON» и текст после таблицы; A6, строка «≤ $1 на расследование»; A7, вопрос 5
   QUOTE: около $0.05 при 1 000 расследований в месяц; в пределах квот $0
   PROBLEM: Criterion 6 requires each investigation's cost to be measured including compute and storage, but the proposal counts only paid calls (Part B calls compute «около $0») and names no component that records CPU time or stored
   bytes per investigation. The one fixed cost it does allocate, the $49 node, is divided by an assumed 1,000 investigations a month: at 100 a month it is $0.49 and the total passes $1, and at 1,000 a month the heavy-case model spend
   ($570) exceeds the $500 monthly Anthropic cap quoted in section 5.
   FIX: Add after the variable-cost table: «Что входит в $1. Мы предлагаем считать критерий по переменным затратам: токены моделей, платные API, поиск, метка времени. Вычисления и хранение измеряются по каждому расследованию:
   оркестратор пишет в таблицу учёта затрат секунды CPU воркера и рендера и объём сохранённых сырых ответов и отчётов; в деньги они пересчитываются по ставке из месячной цены сервера и хранилища. Доля постоянных затрат (узел $49 и
   сервер) показывается отдельной строкой: около $0.06 при 1 000 расследований в месяц и около $0.60 при 100. При 1 000 расследований в месяц расход на модели ($400–570) упирается в месячный потолок Anthropic Start tier ($500): уровень
   нужно поднять заранее.» Add to A7 question 5: «Входит ли в $1 доля постоянных затрат (узел, сервер, хранилище).»

[51] MAJOR | A6, строка «30 секунд / 2 минуты / 5 минут»; G11; раздел 12; A7
   QUOTE: PDF рендерится отдельной задачей вне этих сроков
   PROBLEM: The end of the measured interval («verified result») is never defined. PDF is taken out of the interval in a table cell, with no A7 question and no time limit of its own; the document does not say that the signed, time-
   stamped package then also falls outside (the package manifest contains the hash of report.pdf, section 12), nor whether model-written sections are inside.
   FIX: Replace the cell with: «Срок считается от постановки задачи до проверенного JSON-отчёта, показанного в интерфейсе: все рёбра сверены с квитанциями, отчёт прошёл схему. Вне срока — PDF, подпись Ed25519 и метка времени: манифест
   пакета включает хеш PDF, поэтому подписанный пакет готов только после рендера; его целевой срок утверждают владельцы (ориентир аудита — 20 с рендера на 5 000 строк). Сам срок зависит от скорости TronGrid с ключом, настроек очереди и
   задержки моделей.» Add a blocking question to A7: «Что считается результатом в сроках 30 с / 2 мин / 5 мин. Предложение: проверенный JSON-отчёт в интерфейсе; PDF и подписанный пакет — отдельной задачей со своим сроком. Входят ли в
   срок текстовые секции модели.»

[52] MAJOR | A6, строка «Показатели AI-слоя; превосходство над базовым алгоритмом»; раздел 14, последний пункт «Что проверить»; раздел 3, последний пункт «Что проверить»
   QUOTE: подзадачи, где ожидается выигрыш, фиксируются заранее | количественных подтверждений нет ни у кого на рынке
   PROBLEM: Five AI criteria are collapsed into one row with no thresholds and no scorer: nothing says how the 90% of conclusions with references is counted, what a correct run is for the 95% criterion, or what detects a forbidden
   claim (money recovered, owner identified, exchange confirmed). For «better than baseline» there is no metric, threshold or consequence, and section 14 moves a component that shows no gain «вне MVP-метрик», which silently turns an
   owner criterion into an optional one; the status cell is market commentary, not a status.
   FIX: Replace the row with four rows: «| ≥ 90% существенных выводов агентов со ссылкой или пометкой «гипотеза» | Каждый вывод — запись типа «факт» или «гипотеза» со списком ссылок; детерминированный scorer считает по журналу прогона
   долю записей с непустыми ссылками или типом «гипотеза» | заложено в архитектуру; не измерено |», «| ≥ 95% запусков заканчиваются корректным отчётом или понятной ошибкой | Запуск засчитан, если отчёт прошёл JSON Schema и проверку
   доказательств либо завершился записью ошибки с кодом и текстом для пользователя; считает оркестратор по статусам прогонов | не измерено; доля отказов моделей неизвестна |», «| Все действия агентов в журнале; нет заявлений «деньги
   возвращены», «владелец установлен», «биржа подтверждена» без доказательств | Число записей журнала равно числу вызовов шлюза и LLMClient; пост-валидатор отчёта и писем отклоняет утверждения этих трёх классов без ссылки на
   доказательство; тест на провокационных сценариях: 0 пропусков | scorer предстоит написать |», «| AI лучше базового алгоритма по скорости или полноте | Парное сравнение на одном наборе, 3–5 прогонов; метрика — полнота найденных
   конечных адресов при одинаковом лимите бюджета; порог — прирост больше нуля с 95%-м доверительным интервалом. Выигрыша по скорости не ожидаем: модель добавляет задержку | не измерено; риск невыполнения высокий |». In section 14
   replace «иначе модуль остаётся отключаемым и вне MVP-метрик» with «иначе модуль отключается, а результат сравнения остаётся в отчёте о метриках как невыполненный пункт критерия».

[53] MAJOR | A6, строка «≥ 99% успешного получения данных»; раздел 1 («Как проверяем качество», пункт 1 «Что проверить»); раздел 3 («Что проверить»)
   QUOTE: Повторы и резервный узел; выборочная сверка полноты со вторым независимым индексом; ежедневная контрольная проверка
   PROBLEM: The owner metric is the share of supported, available test transactions whose data were retrieved, but the document uses «99%» for three other things: successful HTTP responses in a load run (section 1, check 1),
   completeness of an address history against a second index (section 1), and agreement on a sample of addresses (section 3). None has a numerator and denominator, and the A6 status ties the criterion to a second index the owner metric
   does not need.
   FIX: Replace the cell with: «Метрика: доля TXID тестового набора, для которых платформа получила и проверила квитанцию и события Transfer (числитель — TXID со статусом «проверено», знаменатель — все поддерживаемые и существующие
   TXID набора); считает проверка доказательств по журналу шлюза. Отдельно публикуются доля успешных HTTP-ответов по провайдерам и полнота истории адреса против второго индекса — это дополнительные метрики, в 99% они не входят.»
   Status: «не измерено; для основной метрики второй индекс не нужен».

[54] MAJOR | раздел 13, «Как проверяем качество», последний пункт; A6, строка «30 секунд / 2 минуты / 5 минут»
   QUOTE: каждая цель измеряется не менее 5 раз, публикуются медиана и p95
   PROBLEM: Criterion 3 asks for time from task start to verified result, with waiting on external sources recorded separately, and at least 95% of completed tasks within the limit; no component is named that records either number. A
   p95 over five runs is just the maximum, and one miss in five is 80%, so five runs cannot show 95%.
   FIX: Replace with: «Протокол замеров: SKU, модель CPU, steal, sysbench, digest образов. Оркестратор пишет в журнал событий время постановки задачи и время появления проверенного отчёта; HTTP-шлюз суммирует по расследованию время
   ожидания внешних источников (ответ провайдера, ожидание в ограничителе, повторы) отдельным полем. Каждая цель измеряется не менее чем на 20 запусках; критерий — не менее 95% завершённых запусков в пределах лимита (не более одного
   превышения из 20); публикуются доля, медиана, максимум и доля времени ожидания источников.»

[55] MAJOR | раздел 5, «Ограничения и риски»; G13; раздел 8, «Состояние проекта»
   QUOTE: Латентность не измерена: вызов Sonnet с effort high плюс первая компиляция грамматик может занять больше минуты
   PROBLEM: By the document's own figures the 30-second target does not fit on paper if the path contains one Sonnet call: such a call may take over a minute, grammar compilation can take up to 180 s with a 24-hour cache (so warm-up at
   deploy is not enough), and default DBOS polling adds 10-60 s. G13 still puts Sonnet on planning and report sections of every investigation, and no per-step time budget is given for any of the three targets.
   FIX: Add under the A6 table: «Бюджет времени, расчёт (уточняется замером Этапа 2). Простая транзакция, 30 с: очередь и чекпойнты — до 2 с; TronGrid и узел — до 10 с; шаги Haiku параллельно — до 10 с; проверка доказательств и сборка
   JSON — до 5 с; запас — 3 с. На этом пути нет вызовов Sonnet и режима effort high; схемы структурированного вывода прогреваются при деплое и не реже раза в 24 часа (срок кеша грамматик). Такие же таблицы составляются для 2 минут и 5
   минут до начала замеров.»

[56] MAJOR | раздел 1, «Инфраструктура и затраты»; A2, пункт 3; раздел 3, «Инфраструктура и затраты»
   QUOTE: около 3 300 запросов TronGrid (11 rps в среднем за 300 с) и 3 000–4 000 к узлу
   PROBLEM: The count leaves out the per-TXID call to /v1/transactions/{txid}/events, which sections 3 and 6 name as the only source of event_index for the edge key, and it assumes about four verified edges per address although section
   12 expects «тысячи и десятки тысяч строк TXID» in a 1,000-address report. Section 3 derives different numbers from the same total (10-16 graphs a day, 20-30 QPS) than A2 and section 1 (about 30 graphs, 11 rps).
   FIX: Replace the sentence in section 1 with: «Граф на 1 000 адресов, расчёт: история — около 1 300 запросов TronGrid; контекст энергии — ещё 2 000 (считается лениво); событие транзакции для ключа ребра — один запрос TronGrid на
   каждый TXID отчёта; квитанция — один запрос к узлу на каждый TXID. При E рёбрах в отчёте: TronGrid — около 1 300 + E, узел — около E. При E = 3 500 это 4 800 запросов TronGrid (16 rps за 300 с) и около 20 графов в сутки на квоте
   BASIC; при E = 20 000 — 71 rps и 4–5 графов в сутки, цель 5 минут на бесплатном плане по расчёту недостижима.» Bring A2 item 3 and section 3 («10-16 графов в день и около 20-30 QPS») to the same formula.

[57] MAJOR | раздел 6, «Что проверить», критерии LH-GraphBench; также раздел 1 (пункт 1), раздел 4 (пункт 3), раздел 8 (проверка 8); A8, пункт 1
   QUOTE: граф на 1 000 адресов ≤ 5 мин; отчёт на несколько десятков адресов ≤ 2 мин
   PROBLEM: The same «1 000 адресов за 5 минут» is the pass criterion of four checks with different scope (TronGrid load run, DBOS spike, a mock-API load test, a graph-layer benchmark); none is end-to-end with real sources,
   verification receipts and model steps, so passing any of them does not establish criterion 3. The load profile is also undefined: with one worker and one shared limiter per provider, a 1,000-address job takes the whole TronGrid
   allowance while a 30-second job runs beside it.
   FIX: Add to A8: «Приёмочный замер критерия 3 один: сквозной прогон на тестовом сервере с реальными источниками, от постановки задачи до проверенного JSON-отчёта, по одной задаче одновременно, на наборе графов, зафиксированном до
   замера. Проверки в разделах 1, 4, 6 и 8 — бюджеты компонентов (источник, очередь, графовый слой), а не приёмка. Отдельно измеряется смешанная нагрузка: простая задача во время обхода графа на 1 000 адресов; для неё в ограничителе
   шлюза вводится приоритет интерактивных запросов.» In section 6 replace the quoted criteria with «графовый слой укладывается в свою долю бюджета времени, заданную до замера».

[58] MAJOR | A5, таблица постоянных затрат, столбец «Минимум»; G12; раздел 13, пункт 1 «Что проверить»
   QUOTE: | **Итого** | **около €8.5 + $49** | **около €20 + $69–200** |
   PROBLEM: The «Минимум» column prices an 8 GB server together with a self-hosted login provider and self-hosted Phoenix at $0, which does not fit by the document's own figures: the roughly 6 GB stack estimate (unmeasured) excludes
   both, the login provider adds 0.5-1.4 GB, PDF rendering peaks at 0.2-0.5 GB, and section 6 wants five parallel investigations in RAM. The Stage 2 memory check has no numeric pass criterion.
   FIX: Add under the table: «Столбец «Минимум» по расчёту не проходит по памяти: оценка стека около 6 GB (не измерена) не включает поставщика входа (0.5–1.4 GB) и интерфейс трасс, а на 8 GB нужен ещё запас под рендер PDF (0.2–0.5 GB)
   и параллельные расследования. На 8 GB поставщик входа и интерфейс трасс выносятся во внешние сервисы (плюс $0–129 в месяц); всё на своём сервере — только при 24 GB.» In section 13, check 1, add: «Критерий: пиковый суммарный RSS при
   пяти параллельных стандартных расследованиях и одном рендере PDF не выше 75% RAM; иначе эталон — 24 ГБ.»

[59] MAJOR | раздел 4, «Ограничения и риски», пункт «Бюджет $1»; A5, абзац после таблицы переменных затрат
   QUOTE: собственном ledger, проверяющем лимит до каждого платного вызова
   PROBLEM: A check before the call cannot hold a hard $1: a model call's cost is known only after the response, and the latency plan relies on parallel Haiku calls that can all pass the check at once and overshoot together. No
   reservation mechanism is described, and Pydantic AI's cost_limit fires after the overrun.
   FIX: Add: «Учёт бюджета работает как резервирование: перед вызовом в одной транзакции резервируется его максимальная стоимость (для модели — подсчитанные входные токены плюс max_tokens по цене выхода; для платного API — цена
   вызова), после ответа резерв заменяется фактом. Вызов не отправляется, если сумма фактов и резервов превышает лимит. Тест: 20 параллельных вызовов при остатке на 5 — отправлено не больше 5, итог не выше лимита.»

[60] MAJOR | раздел 4, «Что проверить», пункт 6; A5 (лимит моделей $0.45); раздел 5, «Как проверяем качество», пункт «Бюджет-трекер»
   QUOTE: ориентир: LLM-часть не выше $0.30, верхней границы оценки аудита
   PROBLEM: Three incompatible model budgets: a Stage 2 threshold of $0.30 (section 4), a default limit of $0.45 (A5) and an expected spend of $0.40 typical and $0.57 heavy (section 5), so the typical estimate already fails the section
   4 threshold. Behaviour at the limit also differs: pause (A5), PAUSED_BUDGET with resume (section 4), and «при 70% — только Haiku, при 100% — отчёт без LLM-текста» (section 5) without saying 70% of what.
   FIX: Section 4, item 6: «ориентир: LLM-часть не выше лимита моделей из A5 ($0.45); схема «Sonnet только на эскалациях» должна уложиться в $0.30». Section 5: «Бюджет-трекер: при 70% лимита моделей ($0.45 по умолчанию) — только Haiku;
   при 100% лимита моделей — отчёт без текста модели; при достижении общего лимита расследования — пауза PAUSED_BUDGET с сохранением результатов.»

[61] MAJOR | A6, строка «≥ 95% тестовых сценариев; все известные маршруты; ≥ 10 переходов; без дублей»
   QUOTE: Собственный набор сценариев; ключ ребра исключает дубли и слияния
   PROBLEM: The row names a data set but no metric or recording component for «all known routes found» and «at least 10 hops with configurable depth». The design cuts routes on purpose (stop at a labelled boundary, page limit per
   address, degree cap, model choosing branches when budget runs short), so «all known routes» can fail by design, and «исключает дубли» is stated as fact although event_index is still unverified (G6).
   FIX: Replace the cell with: «Scorer набора сценариев сравнивает найденные маршруты (последовательности TXID) с эталонными: доля сценариев, пройденных в заданной глубине (цель ≥ 95%), и полнота маршрутов в контрольных сценариях (цель
   100%). В набор входят цепочки не короче 10 переходов; глубина — параметр запуска. Тест на дубли: число рёбер равно числу эталонных событий Transfer. Отсечения (помеченная граница, лимит страниц, лимит степени, нехватка бюджета)
   пишутся в отчёт; контрольные сценарии выполняются с лимитами, которые известные маршруты не обрезают.» Status: «набор предстоит собрать; ключ ребра зависит от проверки event_index на Этапе 2».

[62] MAJOR | A6, строка «Ключи не попадают в отчёты и журналы»; A7
   QUOTE: Секреты через SOPS и age; вырезание ключей в шлюзе; тест на утечку подставного ключа — обязательное условие сборки
   PROBLEM: Only one of the four security criteria has a row. Missing: no seed phrases or private keys, permission and control for agent actions that affect external systems (the registry has requires_approval, but no test, and the
   list of actions is deferred to owners in section 4 without an A7 question), and reporting the limitation when a source is unavailable (no test forces an outage and checks the report).
   FIX: Add three rows: «| Платформа не принимает и не хранит seed-фразы и приватные ключи | Полей для них нет в API и интерфейсе; входной фильтр отклоняет текст, похожий на seed-фразу или приватный ключ; тот же поиск по журналам,
   трассам и отчётам в CI — 0 совпадений | тест предстоит написать |», «| Действия агентов во внешних системах — только с разрешением | У каждого инструмента в реестре признак побочного эффекта и requires_approval; все инструменты MVP
   только читают; тест: вызов инструмента с побочным эффектом без записи об одобрении отклоняется и попадает в журнал | заложено в архитектуру; перечень действий утверждают владельцы |», «| При недоступности источника отчёт называет
   ограничение | Тест с принудительным отказом каждого провайдера: в отчёте есть запись об ограничении с именем источника и затронутыми адресами, зависящие выводы помечены как неполные | тест предстоит написать |». Add to A7: «Перечень
   действий агентов, для которых нужно одобрение человека.»

[63] MAJOR | A6, строка «Полезность отчёта; воспроизводимость независимым специалистом»
   QUOTE: Хронология, граф, адреса, ссылки; пакет доказательств с сырыми ответами API и манифестом
   PROBLEM: None of the four usefulness criteria has a measurement, and the list of next actions with documents and recipients is not in the row (exchange recipients are currently unverified and hidden from reports, A2 item 6).
   Independent reproduction is equated with shipping stored raw responses: the only reproducibility test is a cache-only replay from the platform's own store, the public verify CLI checks package integrity rather than conclusions, and
   exchange attribution rests on paid MistTrack data a third party cannot re-query.
   FIX: Replace the cell with: «Проверка схемы: отчёт не выпускается без разделов «хронология», «граф», «значимые адреса», «ссылки на доказательства» и «следующие действия» (у каждого действия — документы и получатель из справочника со
   статусом проверки). Запуск по TXID или адресу — e2e-тест интерфейса. Воспроизводимость: автотест «чистая комната» берёт только report.json, заново запрашивает каждую квитанцию у публичного узла без ключей платформы и пересчитывает
   конечные адреса и суммы; цель — совпадение основных выводов в 100% сценариев. Выводы, которые опираются на платные метки, помечаются как невоспроизводимые без доступа к провайдеру.» Status: «автотест воспроизводимости предстоит
   написать; получатели-биржи не проверены».

[64] MAJOR | A6, строка «≥ 95% точности меток»; раздел 12
   QUOTE: Независимый размеченный набор; источник метки не используется для её же проверки
   PROBLEM: The row covers one of the four exchange-identification criteria. The «separate evidence package for a potential exchange» is not described anywhere (only the general evidence zip and letter templates), and the other two
   (source, date and confidence on every classification; unknown addresses never called an exchange) have tests in sections 9 and 12 but no row here.
   FIX: Add three rows: «| У каждой классификации — источник, дата проверки, достоверность | Обязательные поля модели Pydantic: отчёт без них не сериализуется; тест схемы на всех сценариях | заложено в архитектуру |», «| Неизвестный
   адрес не называется биржей по косвенному сходству | Эвристика даёт только «кандидата»; тест на наборе hard negatives: 0 меток «биржа» без первичного источника или метки провайдера | набор предстоит собрать |», «| Отдельный пакет
   доказательств для потенциальной биржи | Для каждого адреса-кандидата формируется отдельный файл пакета: переводы на адрес с TXID и квитанциями, источник и дата метки, сырой ответ провайдера, хеши в манифесте; тест: число пакетов
   равно числу кандидатов в отчёте | предстоит спроектировать (раздел 12) |».

[65] MAJOR | раздел 14, «Как проверяем качество», пункт 2; раздел 8, «Как проверяем качество», первая строка; A6, последняя строка; раздел 3
   QUOTE: не менее 10 из 50 сценариев для измерения precision и recall
   PROBLEM: A6 and section 3 say only synthetic-exact and self-generated scenarios count toward the 50 and freeze-anchored cases are a separate class, but section 14 puts at least 10 OFAC and blacklist scenarios inside the 50 and
   section 8 says its eight crash and limit checks «войдут в набор из 50+ сценариев». Counted that way about 32 tracing scenarios remain, and section 3 admits the current design yields only 25+.
   FIX: Section 14: «Адреса из OFAC SDN и из событий AddedBlackList входят в отдельный класс freeze-anchored — не менее 10 сценариев сверх 50 — для измерения precision и recall.» Section 8: «Критерии spike; они же войдут в
   регрессионные тесты надёжности, отдельно от 50 сценариев трассировки:». A6, last row, add: «Сейчас спроектировано 25+ засчитываемых сценариев; нужно ещё не менее 25 и итоговый набор.»

[66] MAJOR | A6, строка «≥ 50 сценариев и отдельный итоговый набор»; A8, пункт 8
   QUOTE: В 50 засчитываются сценарии с точно известным ответом: синтетические и созданные нами в тестовой сети.
   PROBLEM: The held-out set has no size, no rule on whether it sits inside or on top of the 50, and no custody (the same engineer builds the system and both sets), and there is no mapping to the seven categories of Prompt 3. Synthetic
   and test-network scenarios never touch the production sources, so retrieval, timing and label criteria cannot be measured on them, «known deposit addresses» cannot exist in a test network, and the fees for scenarios on the main
   network are not budgeted.
   FIX: Replace the cell with: «Основной набор — не менее 50 сценариев с точно известным ответом, не менее 5 в каждой из семи категорий Промпта 3 (прямые переводы, разветвления, слияния, длинные цепочки, повторные адреса, известные
   депозитные адреса, неполные данные). Синтетические сценарии на записанных ответах API проверяют логику трассировки; сценарии на реальных транзакциях основной сети — получение данных, сроки и метки; тестовая сеть используется только
   для отладки. Итоговый набор — не менее 20 сценариев сверх 50 по тем же категориям; он собирается после заморозки кода, хранится у владельцев и при разработке не используется. Стоимость создания реальных сценариев (комиссии сети)
   оценивается до старта Этапа 2. Кейсы по заморозкам Tether и публичным инцидентам ведутся отдельно.» The counts 5 and 20 are a proposal for the owners.

[67] MAJOR | A4, G6; раздел 1, «Что проверить», пункт 5
   QUOTE: Наличие и стабильность поля event_index проверяется на Этапе 2.
   PROBLEM: The edge key, and with it the «no duplicate transactions» criterion, depends on this field, but the check has no pass criterion and no fallback. Section 3 reports the field present in single probes only.
   FIX: Replace with: «Проверка на Этапе 2: на выборке не менее 1 000 TXID, включая транзакции с несколькими Transfer, поле event_index есть у 100% событий, не меняется при повторном запросе через 24 часа и совпадает с порядковым
   номером лога в квитанции независимого узла. При провале ключом ребра становится (chain, txid, порядковый номер лога в квитанции узла).»

[68] MAJOR | A2, пункт 4; A7, вопрос 4; раздел 2, «Ограничения и риски»
   QUOTE: статистически недоказуема в исходной формулировке: нужно минимум 73 безошибочных примера
   PROBLEM: The owners' wording is a share on a test set; «недоказуема» follows only from a requirement the document adds itself, that the lower bound of a 95% Wilson interval be at least 95%, and Part A does not say so. The same
   standard is not applied to the other thresholds: 50 scenarios out of 50 give a lower bound of 92.9%, so «95% of scenarios» would be just as unprovable.
   FIX: Replace the sentence with: «Цель «95% точности» для класса депозитных адресов нельзя подтвердить с запасом: если требовать, чтобы нижняя граница 95%-го доверительного интервала (Wilson) была не ниже 95%, нужно минимум 73
   безошибочных примера, а собственных депозитных адресов реально собрать 10–30. Как простую долю критерий посчитать можно, но на 10–30 адресах он мало что доказывает. Для остальных порогов Промпта 3 (90%, 95%, 99%) мы считаем простую
   долю и публикуем интервал: при 50 сценариях из 50 нижняя граница — 92.9%.» Add to A7 question 4: «Общее правило для всех процентных критериев: простая доля с интервалом или нижняя граница интервала.»

[69] MAJOR | раздел 2, «Как проверяем качество» и «Инфраструктура и затраты»; раздел 3, «Как проверяем качество»; A5, разовые расходы; A7, вопрос 7
   QUOTE: Независимый тестовый набор на 600+ адресов, истина не из проверяемых источников
   PROBLEM: The label test set has four sizes: 600+ here, at least 300 in section 3, 400 in the threshold example, and a cost estimate ($50-150, 5-8 person-days) stated for 400-500 with 600+ «не измерено». The MistTrack probe is
   budgeted at $10-20, but a $20 package is 100 calls, and A7 does not say who opens the exchange accounts needed for control deposits.
   FIX: Set one size: «Независимый тестовый набор первой версии — 400 адресов (порог: 389 верных положительных меток из 400 по нижней границе Wilson); расширение до 600+ — после Этапа 2.» A5: «проба MistTrack $10–20 (до 100 адресов)
   либо пакет $150 на 1 000 вызовов для всего набора». A7 question 7, add: «и аккаунты на биржах для контрольных депозитов (нужна верификация личности владельца аккаунта)».

[70] MAJOR | A8, вводный абзац и пункты 1, 3, 4, 5; раздел 4 (пункт 5), раздел 8 («Что проверить»), раздел 9 (пункты 1–3)
   QUOTE: Каждая закрывает конкретное «не измерено» из этого документа.
   PROBLEM: A8 lists what is measured but not what counts as a pass or what follows a failure, so the owners approve Stage 2 without go or no-go rules. Missing where clearly needed: a threshold for model refusals; one DBOS decision
   rule (section 4 says «если разница в надёжности не видна», section 8 says «при провале»); map thresholds that section 9 leaves to the owners but A7 never asks for; and what happens if 5 minutes is unreachable on the free TronGrid
   plan (section 3 says «пересмотр цели», a change to an owner criterion).
   FIX: Add «Критерий» and «При провале» to each A8 item, including: item 1 — «При провале цели 5 минут: индивидуальный план TronGrid или второй провайдер; изменение самой цели — только решением владельцев»; item 3 — «Критерий: вариант
   проходит все восемь проверок раздела 8; если проходят оба, берётся вариант без DBOS; если один — он»; item 4 — «Критерий: не менее 95% запусков заканчиваются корректным отчётом или понятной ошибкой; доля запусков, где из-за отказа
   модели отчёт вышел без её текста, — не выше порога владельцев (предложение: 10%). При провале: смена модели или режим без текста модели по умолчанию». Add to A7 question 12: «пороги приёмки карты: кадров в секунду на 1 000 узлов и
   предельное время раскладки (ориентир аудита — 30 кадров в секунду)».

[71] MINOR | A5, абзац «Разовые расходы Этапа 2»; A7, вопрос 6; раздел 13
   QUOTE: стенд замеров с выделенными ядрами €21.73/мес
   PROBLEM: Section 13 gives this price «при контракте на 12 месяцев», so the commitment is about €261, not a one-off monthly fee, and A7 question 6 presents the stand as optional although G12 runs all performance measurements on it
   and criterion 3 needs a fixed test server. The list has no total, and the $50-150 for control deposits already includes the $10 MistTrack trial listed separately (section 2).
   FIX: Replace with: «стенд замеров с выделенными ядрами €21.73/мес при контракте на 12 месяцев (обязательство около €261); он же — тестовый сервер для критерия 3. Итого без юриста, NOWNodes и внешнего хоста для сверки справочника:
   около $180–410 и €261.» A7 question 6: replace «нужен ли отдельный стенд для замеров» with «согласны ли вы оплатить стенд замеров (контракт на 12 месяцев, около €261): без него сроки из критерия 3 нельзя измерить воспроизводимо».

[72] MINOR | раздел 1, «Ограничения и риски»
   QUOTE: Solidified-данные отстают на 18–19 блоков (54–69 с); в отчёт идут только они.
   PROBLEM: For a transaction younger than about a minute the 30-second target cannot be met on paper, because the report uses only data that lag by 54-69 s; the document does not connect this to criterion 3 or say the wait counts as
   waiting on an external source. Also 18-19 blocks at 3 s is 54-57 s, not 54-69 s.
   FIX: Add after the sentence: «Для транзакции моложе минуты срок 30 секунд поэтому недостижим: ожидание подтверждения сети учитывается отдельно как ожидание внешнего источника, а в интерфейсе показывается статус «ждём подтверждения
   сети».» Check the range: 18–19 blocks at 3 s give 54–57 s.

[73] MINOR | раздел 4, «Инфраструктура и затраты», пункт «Переменные (LLM-токены)»; также раздел 3 («Почему выбрано», пункт 3) и раздел 14 («Переменные»)
   QUOTE: Sonnet 5.5 на всех шагах дал бы $1.1–2.2, то есть выше лимита
   PROBLEM: $0.55 times 2-4 requests gives $1.1-2.2 without the +30% tokens named in the same sentence; with it the range is $1.4-2.9 (the Haiku figure «менее $0.15» does include both factors). Two similar slips: section 3 prices a
   MistTrack call at $0.03-0.20 but gives «30 адресов = $3-6», which matches $0.10-0.20, and section 14 quotes MistTrack at $0.10 per call although the A5 default is $0.20.
   FIX: Section 4: «Sonnet 5.5 на всех шагах дал бы $1.4–2.9, то есть выше лимита». Section 3: «вызов MistTrack стоит $0.10–0.20 на пакетах до 10 000 вызовов (30 адресов = $3–6)». Section 14: «MistTrack ($0.10–0.20 за вызов
   address_labels) учтён в разделе 2».

######################################################################
# LENS reader-safety  {'major': 20, 'minor': 5}
VERDICT: Not ready to send as is, but close: Part A is candid and puts conclusions first, and I found no promise of recovering funds and no instruction to collect personal data. The single most important fix is A7: several questions bundle two
or three decisions, lack the engineer's default or cannot be answered as asked (Q5, Q8, Q11), and owner decisions named in Part B never reach A7. Second, a handful of Part A headlines are more confident than Part B supports ("не
существует", "только через правоохранительные органы", "ловушки обойдены", "около $1.00"). Third, Part B still shows drafting leftovers ("досье", "исследователь/верификатор", "исходный аудит") and states the two flagged repositories as
malicious without the hedge Part A uses. Replacement texts that add a default or a number not already in the document (Q3, Q9, Q11, the A7 item 17 defaults, the A8 duration) are my proposals and need the author's confirmation.

[74] MAJOR | A7, opening line (and the whole list)
   QUOTE: Вопросы 1–8 блокируют начало Этапа 2; остальные можно закрыть по ходу.
   PROBLEM: Part B names at least nine further owner decisions that never appear in A7: IdP hosting and AGPL (s.10), where model traces live and ZDR (s.5), which actions need human approval (s.4), the graph-DB decision rule (s.6),
   young single-vendor library and a job-monitoring UI (s.8), FPS and hardware thresholds (s.9), a platform MCP server (s.11), eIDAS or PAdES (s.12), the confidence scale (s.2). An owner deciding from Part A will not know they exist.
   FIX: Add item 17 to A7 (defaults taken from A4/A5; author to confirm): «17. **Решения с вариантом по умолчанию** (если ответа нет, действует вариант по умолчанию; подробности — в конце разделов части B): поставщик входа — на своём
   сервере (Keycloak при 16 GB и более, иначе Logto после пробы) или внешний сервис; допустима ли лицензия AGPL (раздел 10). Журнал вызовов моделей — на своём сервере (по умолчанию) или в облаке ЕС (раздел 5). Действия, требующие
   подтверждения человеком: по умолчанию — любая отправка обращений (раздел 4). Правило ввода графовой СУБД (раздел 6). Готовый веб-интерфейс мониторинга задач: по умолчанию нет (раздел 8). Пороги плавности карты и целевое оборудование
   (раздел 9). Внешний MCP-интерфейс платформы: по умолчанию нет (раздел 11). Квалифицированная метка времени eIDAS или подпись PAdES: по умолчанию нет (раздел 12). Шкала достоверности меток (раздел 2).»

[75] MAJOR | A7, question 11
   QUOTE: **Горячие кошельки бирж:** остановка на помеченной границе или лимит страниц на адрес; пороги по умолчанию (минимальная сумма, окно транзита).
   PROBLEM: Cannot be answered as asked. The problem is not stated, the two options are presented as either/or although sections 1 and 6 say both are needed, and the owner is asked for thresholds («минимальная сумма», «окно транзита»)
   that appear nowhere else in the document and have no proposed values.
   FIX: Replace with: «11. **Трассировка через кошельки бирж.** Горячий кошелёк биржи принимает тысячи переводов в час; пролистать его историю целиком нельзя, а проследить средства дальше него нельзя по смыслу. Предлагаю: трассировка
   останавливается на адресе с меткой биржи (в отчёте — «переведено на опубликованный кошелёк биржи»); для непомеченных адресов с очень большой историей действует лимит страниц на адрес, ветвь помечается как усечённая. Согласны?
   Числовые пороги (минимальная сумма ветви, окно времени транзита) я предложу по итогам замеров Этапа 2; сейчас значения от вас не нужны.»

[76] MAJOR | A7, question 5
   QUOTE: **Распределение бюджета $1** и лимит платных вызовов меток (предложено 2). Что происходит при исчерпании: жёсткая остановка с частичным отчётом
   PROBLEM: Three decisions in one item, and the exhaustion behaviour has no recommended default although A5 and A6 already assume «пауза с сохранением»; section 5 describes a third behaviour (70%: Haiku only, 100%: report without
   model text).
   FIX: Replace with: «5. **Бюджет $1.** (а) Принимаете ли лимиты по умолчанию из A5: модели $0.45, платные метки 2 вызова (до $0.40), поиск 10 запросов? (б) Что происходит при исчерпании лимита: рекомендую паузу с сохранением
   результатов и запросом на повышение лимита (так сформулирован критерий Промпта 3); альтернатива — жёсткая остановка с частичным отчётом.» Align section 5 («Бюджет-трекер») with the chosen behaviour.

[77] MAJOR | A7, question 8
   QUOTE: **Юрист.** Нужны заключения по политике использования Anthropic, по методике распределения смешанных средств для целевых юрисдикций
   PROBLEM: This is a statement, not a question, and it sits among the items that block the start of Stage 2, while A9 says «заключения юриста до релиза» and A8.4 puts the legal review inside Stage 2. Read literally, the owners would
   hold all work until four legal opinions arrive.
   FIX: Replace with: «8. **Юрист.** Есть ли у вас юрист для целевых юрисдикций и кто ставит ему задачу? Нужны четыре заключения: (а) политика использования Anthropic — до закрепления провайдера моделей; (б) методика распределения
   смешанных средств; (в) шаблоны обращений; (г) оценка воздействия на защиту данных — эти три до релиза. Начало Этапа 2 блокирует только ответ «кто и когда», а не сами заключения.»

[78] MAJOR | A5, per-investigation table, total row (also A6 row «≤ $1 на расследование»)
   QUOTE: | **Итого** | | **около $1.00** |
   PROBLEM: The owner criterion is a hard ≤ $1, yet the default limits in this table sum to $0.95 (Brave, free timestamp) up to about $1.02 (Tavily, commercial timestamp): 0.05 + 0.40 + 0.45 + 0.05–0.08 + 0–0.04. «Около $1.00» hides
   that one combination exceeds the limit, and A6 says «расчёт укладывается».
   FIX: Replace the row with: «| **Итого по лимитам по умолчанию** | | **от $0.95** (Brave, бесплатная метка времени) **до примерно $1.02** (Tavily, коммерческая метка времени) |» and add after the table: «В сочетании Tavily и
   коммерческой метки времени сумма лимитов превышает $1 на $0.02; какой лимит снижается, решается в вопросе 5.» In A6 change the state to «расчёт укладывается при лимитах A5, кроме сочетания Tavily и коммерческой метки времени; не
   измерено».

[79] MAJOR | A1 first paragraph; A2 item 1; A6 row «Показатели AI-слоя»; A4 G14
   QUOTE: Готового движка трассировки, пригодного как основа, не существует, поэтому ядро — собственный детерминированный трассировщик
   PROBLEM: Four Part A statements are more confident than Part B and A10, which say the candidate search was incomplete and nothing was measured: «не существует», «Готового движка трассировки нет», «нет ни у кого на рынке», and G14
   «Keycloak занимает 1.25–1.4 GB и … не помещается с запасом» (section 10: figures from documentation, «хватит ли памяти — не измерено»).
   FIX: (a) A1: «Готового движка трассировки, пригодного как основа, аудит не нашёл (поиск неполон, см. A10), поэтому ядро — собственный детерминированный трассировщик поверх публичных API TRON.» (b) A2.1 heading: «**Готового движка
   трассировки не найдено.**» (c) A6 state: «не измерено; опубликованных количественных подтверждений у других проектов не найдено (поиск неполон)». (d) G14: «Вход: серверная часть — стандартный OIDC resource server, поставщик входа
   заменяем. По документации Keycloak требует 1.25–1.4 GB памяти; поместится ли он на сервер с 8 GB рядом с базой, воркером и мониторингом, не измерено. Поэтому Keycloak рекомендуется при 16 GB и более, при 8 GB — Logto, ZITADEL или
   внешний сервис после пробы на Этапе 2. Выбор зависит также от юрисдикции (вопрос 2).»

[80] MAJOR | A2 item 6; also A1 row 14 and the title of section 14
   QUOTE: **Возврат средств идёт только через правоохранительные органы.** У Tether нет канала для жертвы
   PROBLEM: Stated as fact, but it rests on a 2018 policy, an unread portal (cs.tether.to) and a 404 page; section 12 itself says the thesis «слишком широк» because TRM Beacon Network claims access for vetted security companies.
   Separately, «каналы возврата средств» in A1 and the section 14 title can be read as the platform offering recovery channels.
   FIX: Replace item 6 with: «6. **Канала возврата для самой жертвы не найдено; найденные каналы рассчитаны на правоохранительные органы.** По опубликованной политике Tether (2018) запрос принимается от органа с правовым основанием;
   портал cs.tether.to не прочитан, страница требований отдаёт 404. TRM Beacon Network заявляет доступ для проверенных компаний по безопасности — условия не проверены. Реквизиты бирж первичными источниками не подтверждены: их сайты
   были недоступны из сети аудита. Платформа готовит пакет доказательств и черновики обращений; заморозку и возврат она не выполняет и не обещает.» Rename A1 row 14 to «OSINT и адресаты обращений» and section 14 (and the contents line)
   to «Источники OSINT и адресаты обращений о заморозке и возврате».

[81] MAJOR | A9, last row
   QUOTE: Это следствие отсутствия готовых решений, а не выбор; заимствуются идеи и тесты из проектов под MIT
   PROBLEM: The stack departs from the owners' «свой код — только клей» principle (section 9 says so explicitly), but Part A mentions it only in the last risk row, defensively, with no size and no request for consent. Part B contains
   the estimates.
   FIX: Replace the row with: «| Объём собственного кода больше, чем принцип «свой код — только клей»: трассировщик, оркестратор, HTTP-шлюз с реестром инструментов, раскладка и сворачивание графа, хранилище меток. Сумма оценок разделов
   2, 3, 4, 9 и 11 — порядка 10–15 человеко-недель (не измерено) | Готовых решений для этих частей не найдено; заимствуются идеи и тесты из проектов под MIT. Это отступление от принципа — прошу подтвердить его в вопросе 1 |» and add to
   A7 question 1: «в том числе объём собственного кода из A9».

[82] MAJOR | A2 item 2; A4 G5 (last sentence)
   QUOTE: **TronScan нельзя закладывать в коммерческий продукт.** Его Terms of Service от 2022-01-04 запрещают сторонние приложения
   PROBLEM: A categorical legal conclusion in bold, while G5 admits it is not confirmed that the 2022 document is the current edition or covers the API. Sections 1 and 2 also disagree on whom the ToS excludes («организации» vs
   «резидентов»). «Один из проверявших» and «строгое правило» in G5 are drafting residue.
   FIX: A2.2: «2. **TronScan не закладываем в критический путь до письменного согласия.** По нашему прочтению, его Terms of Service от 2022-01-04 запрещают сторонние приложения без письменного согласия; действует ли эта редакция и
   распространяется ли она на API, не подтверждено — нужен ответ TronScan или юриста. Основной источник — TronGrid; каждый факт отчёта дополнительно подтверждается квитанцией транзакции у независимого оператора узла. Второй независимый
   индекс «адрес → переводы» пока не выбран.» G5 tail: «Оговорка: опубликованных условий именно для API TronScan не найдено, и не подтверждено, что документ 2022 года — действующая редакция; до ответа TronScan считаем, что запрет
   действует.»

[83] MAJOR | A2 item 8
   QUOTE: **Лицензионные ловушки обойдены.** Не используются: Memgraph (BSL, условия сужены в минорном релизе), FalkorDB (SSPL)
   PROBLEM: Reads as a legal all-clear in a colloquial tone, while the chosen stack still contains components whose use depends on conditions or on a lawyer (Grafana AGPL-3.0, psycopg 3 LGPL-3.0, Phoenix Elastic License 2.0).
   FIX: Replace with: «8. **Компоненты, лицензии которых, по нашему прочтению, ограничивают коммерческий SaaS, в стек не включены.** Это Memgraph (BSL, условия сужены в минорном релизе), FalkorDB (SSPL), ArangoDB Community (запрет
   коммерческого production), наборы данных Elliptic (CC BY-NC-ND), cytoscape-svg (GPL-3.0), Cosmograph (CC-BY-NC), Neo4j NVL (только для продуктов Neo4j), Chainabuse API (только некоммерческое использование). В стеке остаются
   компоненты с условными лицензиями — Grafana (AGPL-3.0, без модификаций), psycopg 3 (LGPL-3.0), Arize Phoenix (Elastic License 2.0); их допустимость, в том числе при установке у клиента (вопрос 13), подтверждает юрист.»

[84] MAJOR | A7, questions 3 and 9
   QUOTE: Можно ли отправлять скриншоты и переписку провайдерам в США, или нужен режим без хранения данных либо маршрут через ЕС.
   PROBLEM: Neither question gives the engineer's default or the cost of each option. Q3 is also the first place Part A mentions victims' screenshots and correspondence, which contain third parties' personal data. In Q9 «состав
   журнала» is opaque to a cold reader.
   FIX: Q3 (default is my proposal): «3. **Данные жертв и провайдеры моделей.** Можно ли отправлять материалы жертвы (скриншоты, переписку) провайдерам моделей в США? Варианты: (а) можно; (б) только в режиме без хранения данных — у
   Anthropic он оформляется через отдел продаж, помеченный контент всё равно хранится до 2 лет; (в) только через ЕС — Vertex AI, +10% к цене, условия не проверены; (г) не отправлять. По умолчанию до заключения юриста действует (г): в
   модель уходят только публичные данные блокчейна.» Q9 (recommendation is my proposal): «9. **Поисковый провайдер.** Tavily: выдачу можно хранить в журнале расследования, но провайдер вправе использовать запросы для обучения. Brave:
   дешевле, но хранить выдачу запрещено — в журнале остаются запрос, время и наши снимки страниц; нужно письменное подтверждение Brave. Рекомендую на Этап 2 Tavily (бесплатная квота без карты; в запросах только публичные адреса, TXID и
   домены). Согласны?»

[85] MAJOR | A7, question 6; A5 «Разовые расходы Этапа 2»
   QUOTE: **Сервер:** 8 GB или сразу 16–24 GB; готовность оплатить 12 месяцев вперёд; нужен ли отдельный стенд для замеров.
   PROBLEM: Three decisions without the recommendation that A5 and G12 already contain. G12 says measurements run on dedicated cores, so «нужен ли стенд» is not really open. A5 lists the stand as a one-off «€21.73/мес», but section 13
   says that price requires a 12-month contract.
   FIX: Q6: «6. **Сервер.** Рекомендую сразу OVH VPS-4 (24 GB) с оплатой за 12 месяцев: €19.96/мес, около €240 за год. Альтернатива — 8 GB за €8.49/мес без обязательств, с риском нехватки памяти (A5, G12). Согласны? Отдельно: для
   замеров Этапа 2 нужен стенд с выделенными ядрами — €21.73/мес при контракте на 12 месяцев (около €261 за год); подтвердите или укажите, чем его заменить.» In A5: «стенд замеров с выделенными ядрами €21.73/мес при контракте на 12
   месяцев (цену проверить при заказе)».

[86] MAJOR | A7, question 7; A5 «Разовые расходы Этапа 2»
   QUOTE: Кто заводит аккаунты TronGrid, Chainstack, Anthropic и MistTrack, принимает их условия и ведёт переписку о коммерческом использовании.
   PROBLEM: A5 budgets «контрольные депозиты на биржи» ($50–150), which need someone's verified exchange accounts and real payments. Q7 does not ask who does this, and also omits the search provider and hosting/backup accounts.
   FIX: Replace with: «7. **Аккаунты, ключи и платежи.** Кто заводит аккаунты TronGrid, Chainstack, Anthropic, MistTrack, поискового провайдера, хостинга и хранилища резервных копий, принимает их условия и ведёт переписку о
   коммерческом использовании? Отдельно: кто делает контрольные депозиты на биржи со своих верифицированных аккаунтов для тестового набора меток ($50–150, A5)? Я аккаунты не создаю, условия не принимаю и платежи не провожу.»

[87] MAJOR | A8, opening paragraph
   QUOTE: До написания ядра выполняются измерения и короткие проверочные реализации. Каждая закрывает конкретное «не измерено» из этого документа.
   PROBLEM: The owners are asked to approve the start of Stage 2, and A5 gives its cost but nothing in Part A gives its duration. The estimates exist only scattered through Part B.
   FIX: Add after the paragraph (sum of Part B estimates; author to confirm): «Ориентир по срокам (сумма оценок части B, не измерено): проверочные реализации и замеры — около 4–6 недель работы одного инженера. Письменные ответы
   провайдеров и заключения юриста идут параллельно, и их сроки от нас не зависят.»

[88] MAJOR | Section 3, «Состояние проекта…» (also «Почему выбрано», «Ограничения и риски», «Что проверить»); sections 4, 5, 14
   QUOTE: Wallet-Risk-Scanner (190 stars за 3 недели) — загрузчик нативного кода под Windows; stolen-funds-finder — clipboard hijacker.
   PROBLEM: Part A says «с признаками вредоносного кода», but section 3 calls the two named repositories «вредоносных» as fact in four places although the code was never run. Other third-party statements are also firmer than what was
   observed: «Serper и SerpApi — скрейпинг Google, суды не завершены» (s.14), DeepSeek data practices (s.5), LiteLLM PyPI compromise (s.4), the crypttrace author-account remark (s.3). Section 14 also contradicts itself on T3 FCU («В
   справочнике — статус press» vs «до этого в справочник не вносится»).
   FIX: Section 3: «…и два репозитория с признаками вредоносного кода»; «Wallet-Risk-Scanner (190 stars за 3 недели) по статическим признакам похож на загрузчик нативного кода под Windows, stolen-funds-finder — на подменщик буфера
   обмена. Код не исполнялся, вывод предварительный»; «один из репозиториев с признаками вредоносного кода нацелен на Windows»; «deny-list двух репозиториев с признаками вредоносного кода». Keep the names only in the deny-list
   sentence. Section 14: «Serper и SerpApi получают выдачу Google скрейпингом; по публичным сообщениям, идут судебные споры (не проверено)»; «T3 FCU в справочник не вносится до подтверждения домена». Add the source to the LiteLLM and
   DeepSeek statements («по опубликованному advisory проекта», «по условиям сервиса, в аудите не перечитывались») and «это наблюдение, а не вывод о вредоносности» after the crypttrace account remark.

[89] MAJOR | Section 4, «Инфраструктура и затраты» and «Что проверить», item 6
   QUOTE: **Расхождение с общим решением по LLM:** там Sonnet 5.5 закреплён за планированием и финальным отчётом, что шире, чем «только эскалации».
   PROBLEM: An unresolved drafting note on the most-watched number. Section 4 gives the model cost as $0.05–0.30 with a target of «не выше $0.30», while A5 and section 5 give $0.40–0.57 with a $0.45 limit; a reader dipping into section
   4 cannot tell which is the proposal.
   FIX: Replace the note with: «В сводке (G13, A5) принята более широкая схема: Sonnet 5.5 на планировании и коротких секциях отчёта. Её расчётная стоимость — $0.40–0.57 на расследование (раздел 5); оценка $0.05–0.30 выше относится к
   схеме «Sonnet только на эскалациях». Обе схемы замеряются на Этапе 2 (пункт 6 ниже).» In item 6 replace «ориентир: LLM-часть не выше $0.30, верхней границы оценки аудита» with «ориентир: не выше лимита $0.45 из A5».

[90] MAJOR | Section 3, «Лицензия и коммерческое использование» (contradicts section 2)
   QUOTE: Условия коммерческого использования и кэширования у MistTrack и Arkham в документации не найдены — нужны письменные.
   PROBLEM: Section 2 says the MistTrack Terms of Use of 2026-10-09 were read and explicitly allow client reports and caching; section 3 says no such terms were found. The owner gets two opposite readings of the terms of the only paid
   data source in the stack.
   FIX: Replace with: «Условия MistTrack прочитаны (раздел 2): по нашему прочтению, отчёты для клиентов и кэширование разрешены, перепродажа данных запрещена, до коммерческого использования возможна проверка бизнес-модели — нужно
   письменное подтверждение. У Arkham условия коммерческого использования и кэширования в документации не найдены — нужны письменные.»

[91] MAJOR | Part B throughout (e.g. s.10 «Лицензия…», s.8, s.11, s.3, s.6, s.2); A10 bullet 4
   QUOTE: Лицензии Pydantic и uvicorn в досье не зафиксированы — не проверено.
   PROBLEM: Drafting-process vocabulary is visible and inconsistent: «досье», «исследователь», «верификатор», «проверяющий аудитор», «исходный/первичный аудит», «аудит этой области», «поправка перепроверки», «лимит веб-поиска
   закончился». In section 11 «верификатор отклоняет любой факт отчёта» uses the same word for a platform component. Names appear with no introduction (LOCARD, tronetl, «список BlockSec», «CSV BitOK», Raphtory, Grafeo, NeuG, arXiv
   2512.02534), and the fixed tag «не измерено/не проверено» breaks grammar («Скорость и память не измерено»).
   FIX: Use two terms only, «первичное исследование» and «перепроверка», and delete narration that does not change a decision. Exact replacements: s.10 «Лицензии Pydantic и uvicorn в аудите не проверялись.»; s.8 «Независимых отчётов о
   production-эксплуатации не найдено (поиск неполон).»; s.11 «модуль проверки доказательств отклоняет любой факт отчёта без ссылки на такую запись»; A10 «**Новые участники рынка 2025–2026 годов:** на этапе перепроверки поиск был
   ограничен и по части направлений не завершён; список альтернатив может быть неполон.» Introduce each dangling name in one clause or remove it; fix agreement («скорость и память не измерены»).

[92] MAJOR | Sections 4, 8, 9 «Лицензия и коммерческое использование» (also s.7, s.12, s.13); A10 bullet 5
   QUOTE: Коммерческое SaaS-использование разрешено без условий.
   PROBLEM: Reads as legal advice and is inexact: MIT does carry a condition (keep the copyright notice and licence text). Similar flat conclusions cover LGPL and AGPL components («обязательств на код платформы не создают», «код
   платформы не затронут»). The only disclaimer is the fifth bullet of A10, which a reader dipping into Part B will not see.
   FIX: Replace «разрешено без условий» in sections 4, 8 and 9 with «разрешено; условие MIT — сохранять уведомление об авторских правах и текст лицензии». Prefix the LGPL/AGPL conclusions in sections 7, 12 and 13 with «по нашему
   прочтению». Move the disclaimer into «Как читать»: «Все прочтения лицензий и условий использования в этом документе — выводы инженера, а не заключения юриста; спорные случаи вынесены в вопрос 8.»

[93] MAJOR | A2 item 9
   QUOTE: Чтение кода показало: два опроса по 1.0 секунды по умолчанию, восстановление привязано к версии приложения, состояние по умолчанию хранится в pickle
   PROBLEM: Over-compressed: it does not say what DBOS is, what is polled or why any of the four points matters, and Conductor, pickle and Procrastinate are unexplained although Q10 asks the owners to rule on DBOS. «Всё устранимо
   настройкой» overstates: automatic takeover exists only in paid Conductor (section 8).
   FIX: Replace with: «9. **Оркестрация на DBOS — условный выбор.** DBOS Transact — библиотека Python, которая сохраняет каждый шаг расследования в PostgreSQL и после сбоя продолжает с последнего шага. Чтение её кода показало четыре
   особенности настроек по умолчанию: очередь опрашивается раз в секунду, что добавляет 1–2 секунды на каждый вызов через очередь и угрожает цели «30 секунд»; после выкладки новой версии незавершённые расследования сами не
   продолжаются; состояние шагов хранится в формате pickle (небезопасен и ломается при изменении кода); работу упавшего воркера автоматически перехватывает только платная консоль Conductor (от $99/мес). Первые три устраняются
   настройкой, четвёртая в MVP с одним воркером закрывается его перезапуском. Всё это проверяется на Этапе 2; запасной путь проще — обычная очередь Procrastinate и свои таблицы.»

[94] MINOR | Section 3, «Инфраструктура и затраты» (contradicts A2 item 3 and section 1)
   QUOTE: 6-10 тыс. вызовов на граф из 1 000 адресов, то есть 10-16 графов в день и около 20-30 QPS для 5 минут
   PROBLEM: A2.3 and section 1 say the free daily quota covers «примерно 30» such graphs at about 11 rps (3 300 TronGrid requests per graph); section 3 says 10–16 graphs and 20–30 QPS from the same 6–10 thousand calls. A reader
   checking A2.3 against Part B finds two different answers.
   FIX: Replace with: «Расчётная оценка, не измерено: 6–10 тыс. вызовов на граф из 1 000 адресов, из них около 3 300 к TronGrid (раздел 1) — суточной квоты хватает примерно на 30 графов при 11 запросах в секунду; если бы все вызовы шли
   в TronGrid, квоты хватало бы на 10–16 графов при 20–30 запросах в секунду.»

[95] MINOR | A7, questions 16 and 14
   QUOTE: **Данные первого кейса:** публичный адрес кошелька или TXID кражи. Нужны к началу Этапа 2.
   PROBLEM: Q16 says the data are needed at the start of Stage 2 but sits in the group that «можно закрыть по ходу», and it does not say that only public on-chain data are wanted. Q14 is a list of four topics with no proposal the
   owners could accept or amend.
   FIX: Q16: «16. **Данные первого кейса:** публичный адрес кошелька или TXID кражи — только данные из блокчейна, без личных данных жертвы. Нужны к началу построения базового трассировщика, то есть после измерений Этапа 2.» Q14: «14.
   **Сохранность данных.** Назовите: (а) сколько минут последних данных допустимо потерять при аварии и за какое время сервис должен быть восстановлен — если ответа нет, ориентиром станет результат пробного восстановления на Этапе 2;
   (б) срок хранения расследований; (в) нужно ли удаление по запросу клиента — оно конфликтует с неизменяемыми резервными копиями (раздел 13).»

[96] MINOR | Preamble: first paragraph and «Откуда данные»
   QUOTE: Каждое из 10 направлений прошёл исследователь, затем независимый верификатор, которому было поручено опровергать, а не соглашаться.
   PROBLEM: The request to the owners is not stated first. «Аудит» is used from the next paragraph on without being named here; «10 направлений» is not reconciled with 13 needs and 14 sections; «379 кандидатов» does not say candidates
   for what. «Исследователь» and «независимый верификатор» suggest human reviewers; if these were AI agents, that should be said. «Промпт 0/1/3» are never glossed.
   FIX: First paragraph: «Это результат Этапа 1: предложение по технологиям и готовым компонентам для каждой из 13 потребностей вашего задания (Промпт 0). **От вас нужно:** согласовать таблицу A1 и ответить на вопросы 1–8 из A7; до
   этого к Этапу 2 я не перехожу.» «Откуда данные»: «Документу предшествовал аудит рынка в два прохода: первичное исследование и независимая перепроверка, задачей которой было опровергать, а не соглашаться [указать, кем выполнены
   проходы]. Аудит шёл по 10 направлениям; его результаты разложены по 14 разделам части B. Рассмотрено 379 кандидатов — сервисов, библиотек и наборов данных.» Then the existing figures. Gloss on first use: «Промпт 1 (описание
   агентов)», «Промпт 3 (изм

[97] MINOR | A4 G6 and G8; A1 row 5 and A5 («интерфейс трасс»); A6; Part B terminology
   QUOTE: Четыре методики распределения смешанных средств (FIFO, LIFO, pro-rata, верхняя граница poison) считаются параллельно
   PROBLEM: «poison» (taint method, G8) and «address poisoning» (zero-value transfers, G6) are different things two bullets apart, neither explained. «Трассы моделей» collides with «трассировка» of funds. A6 uses «30 секунд / 2 минуты
   / 5 минут» without saying what each measures and «заложено в архитектуру» could be read as done. Part B uses spike, baseline, ground truth, IdP, TSA, ZDR, RPO/RTO, HITL where Part A uses Russian terms, with no mapping.
   FIX: Add to «Как читать»: «**Термины.** poison — методика, по которой после смешивания «заражённой» считается вся сумма (верхняя граница); address poisoning — рассылка переводов с нулевой суммой, к методике poison не относится;
   трассы моделей — журнал вызовов языковых моделей, а не трассировка средств; spike — короткая проверочная реализация на 2–3 дня; baseline — детерминированный алгоритм без модели, с которым сравнивается AI-слой; ground truth — заранее
   известный правильный ответ; IdP — поставщик входа; TSA — служба меток времени; ZDR — режим без хранения данных у провайдера модели; RPO и RTO — допустимая потеря данных и время восстановления; HITL — шаг с подтверждением человеком.
   «Заложено в

[98] MINOR | Section 5 «Решение» (also «Решение» in sections 3 and 4)
   QUOTE: **Решение.** Primary — Anthropic Claude API: `claude-haiku-5-5` на рутинных шагах
   PROBLEM: The decision paragraphs of sections 3, 4 and 5 are half English (Primary, Fallback, strong-tier, LLM-gateway, evals, «deterministic baseline tracer», «durable workflows, очереди, HITL», spike), while Part A says the same
   things in Russian. Spellings also drift («чекпоинт/чекпойнт», «Tronscan/TronScan»).
   FIX: Section 5: «**Решение.** Основной провайдер — Anthropic Claude API: `claude-haiku-5-5` на рутинных шагах, `claude-sonnet-5-5` для планирования и коротких секций отчёта; сильная модель задаётся настройкой. Запасной провайдер —
   OpenAI (`gpt-6-luna`, `gpt-6.1-sol` через Responses API). Доступ — официальные SDK за собственным адаптером LLMClient, без промежуточного шлюза моделей; журнал вызовов моделей хранится в своей БД и передаётся по OpenTelemetry,
   интерфейс просмотра — Arize Phoenix либо Langfuse Cloud EU (по решению владельцев о размещении данных); оценка качества — Inspect AI в Linux-контейнере. Статус: условно — до юридического разбора политики использования, пилота на 50
   сценариях и чте