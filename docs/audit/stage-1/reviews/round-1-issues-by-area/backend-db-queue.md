# Review issues relevant to section(s) [7, 8, 10] (backend-db-queue)

[2] MAJOR | lens: owner-format | location: Section 7, 'Инфраструктура и затраты' (need g: users, investigations, events, reports)
   QUOTE: Одна база: схема приложения под RLS и отдельная схема с отдельной ролью для системных таблиц DBOS (G2).
   PROBLEM: The brief asks for storage of users, investigations, events and reports, but section 7 never says where users (profiles, organisations, roles) and reports (report.json, PDF, evidence-zip) are stored. No file or object
   store is named, the scope of restic is undefined, and there is no disk-growth estimate although raw responses are kept indefinitely on a 75 GB disk.
   FIX: Добавить в «Инфраструктура и затраты» раздела 7 (поправить, если фактический замысел иной): «Пользователи: учётные данные хранит поставщик входа (G14); в PostgreSQL — таблицы users, organizations и memberships (ключ — sub
   из токена, роли, принадлежность к расследованиям), под RLS. Отчёты: таблица reports хранит версию схемы, report.json (JSONB), оба манифеста, подпись, метку времени и sha256 файлов; report.pdf и evidence-zip лежат на томе
   сервера и попадают в резервную копию через restic (G12). Объём диска на одно расследование (сырые ответы, отчёты) не измерен.» В «Что проверить» добавить: «Замер объёма БД и файлов на стандартное расследование и на граф из 1
   000 адресов; критерий — прогноз заполнения диска 75 GB и стоимости B2 на 12 месяцев.»

[12] MAJOR | lens: owner-format | location: Section 10, 'Решение'; A1 row 10; A7 (owner decisions)
   QUOTE: Статус: принято; конкретный IdP ждёт решения владельцев и пробы на сервере.
   PROBLEM: The authentication provider has no chosen solution (Keycloak, Logto, ZITADEL or external), yet A1 row 10 is marked 'принято' and A7 contains no question about it. Other decisions that Part B leaves to the owners are
   also missing from A7.
   FIX: A1, строка 10, статус: «принято; поставщик входа — условно». Добавить в A7: «17. **Поставщик входа:** на своём сервере ([рекомендация по умолчанию: Logto при 8 GB после замера памяти, Keycloak при 16 GB и более]) или
   внешний сервис, где учётные данные хранит третья сторона; допустим ли ZITADEL под AGPL; нужны ли в MVP MFA и организации. 18. **Решения из разделов части B:** размещение трасс моделей — Phoenix на своём сервере или Langfuse
   Cloud EU (раздел 5); перечень действий, требующих подтверждения человеком (раздел 4); правило ввода графовой СУБД „выигрыш не менее чем в 3 раза“ (раздел 6); нужен ли MCP-сервер платформы для клиентов (раздел 11); нужна ли
   квалифицированная метка времени eIDAS или подпись PAdES (раздел 12); допустим ли Gotenberg с Chromium как запасной движок PDF (G10); шкала confidence (раздел 2).»

[14] MAJOR | lens: owner-format | location: Section 10 'Лицензия и коммерческое использование'; section 9 'Лицензия и коммерческое использование'; A1 rows 9 and 10
   QUOTE: Лицензии Pydantic и uvicorn в досье не зафиксированы — не проверено.
   PROBLEM: Item 3 is unanswered for chosen components: uvicorn (the ASGI server), and in section 9 TanStack Router and zustand ('в аудите не зафиксированы — не проверено'), while A1 states 'MIT' for both rows. Pydantic is 'not
   verified' in section 10 but 'MIT' in section 12.
   FIX: Проверить по файлам LICENSE и записать. Раздел 10: «Pydantic — MIT (раздел 12); uvicorn — [лицензия по файлу LICENSE; ожидаемо BSD-3-Clause]». Раздел 9: «TanStack Router и zustand — [лицензии по файлам LICENSE; ожидаемо
   MIT]». До проверки в A1, строки 9 и 10, вместо «MIT» писать «MIT; у части зависимостей лицензия не проверена».

[18] MINOR | lens: owner-format | location: Section 8, 'Почему выбрано', fourth bullet (contradicts section 4)
   QUOTE: pydantic-ai 2.55.0 (MIT) имеет официальную durable-интеграцию с DBOS (extra `dbos>=2.10.0`) — тот же стек, что в G3.
   PROBLEM: Section 8 cites the official pydantic-ai/DBOS integration as a reason for the choice, while section 4 says that integration is deprecated, imports private DBOS modules and will not be used.
   FIX: «pydantic-ai 2.55.0 (MIT) совместим с DBOS по схеме „один запрос к модели — один @DBOS.step“; готовую durable-интеграцию (DBOSAgent) не используем: она помечена deprecated и импортирует приватные модули DBOS (раздел 4).» В
   «Ограничения и риски» раздела 8 убрать или пометить как неприменимое описание поведения готовой интеграции (буферизация стриминга, обёртка tool-функций).

[19] MINOR | lens: owner-format | location: Part A, A9 (last row) and A5
   QUOTE: Объём собственного кода больше, чем «только клей»: трассировщик, раскладка и сворачивание графа, шлюз
   PROBLEM: The brief's strategy is not to build what already exists; the document admits the own code exceeds glue but never totals the effort. Estimates are scattered across sections 2, 3, 4, 6, 9 and 11, and sections 5, 7, 10,
   12 and 13 give none.
   FIX: Добавить в A5 абзац «Трудозатраты на собственный код (оценки аудита, не измерено)»: «трассировщик 2–3 человеко-недели; оркестратор, учёт бюджета и журнал 2–3; шлюз и реестр инструментов 1.5–2.5; интерфейс и карта 4–5
   (верификатор отдельно оценивает раскрытие ветвей, агрегацию, раскладку и экспорт в 3–4); Label Store 3–5 дней; тестовый набор меток 5–8 человеко-дней; стенд графового теста 1–2 недели. Итого около 12–18 человеко-недель; по
   адаптеру LLMClient, схеме БД, API, отчётам и эксплуатации оценки нет.»

[32] MAJOR | lens: consistency | location: A8, п. 3; раздел 7 «Состояние проекта»; раздел 8 «Ограничения и риски» и «Как проверяем качество»; раздел 10 «Что проверить»
   QUOTE: DBOS против варианта без него: принудительное завершение воркера посреди расследования, деплой посреди расследования
   PROBLEM: Sections 7 and 8 both mark «Работа DBOS на PostgreSQL 18 — не проверено», and G2 and G3 fix exactly this pair, yet A8 п. 3 does not list the check. It also omits two spike criteria from sections 8 and 10: the simple
   transaction within 30 seconds end to end (two default 1.0 s polls put it at risk) and the planted key not appearing in the DBOS system database.
   FIX: Append to A8 п. 3: «Работа DBOS 3.2 на PostgreSQL 18.6 с SQLAlchemy 2.0.54; сквозной замер «простая транзакция за 30 секунд» через API, очередь и SSE при интервале опроса 0.1–0.25 с; подставной ключ не находится в
   системной БД DBOS.»

[33] MAJOR | lens: consistency | location: раздел 8 «Почему выбрано», 4-й пункт; раздел 8 «Что проверить», 4-й пункт; против раздела 4 «Состояние проекта» (Pydantic AI)
   QUOTE: pydantic-ai 2.55.0 (MIT) имеет официальную durable-интеграцию с DBOS (extra `dbos>=2.10.0`) — тот же стек, что в G3.
   PROBLEM: Section 8 gives the official pydantic-ai/DBOS integration as a reason for the choice and plans to test it. Section 4 says `DBOSDurability` imports private DBOS modules, `DBOSAgent` is deprecated and «готовую интеграцию
   не используем». Section 4 is more likely right because it read the code. The reference «тот же стек, что в G3» is also wrong: G3 does not mention Pydantic AI.
   FIX: Replace the bullet with: «У pydantic-ai 2.55.0 есть durable-интеграция с DBOS (extra `dbos>=2.10.0`), но она импортирует приватные модули DBOS, а `DBOSAgent` помечен deprecated (раздел 4): готовую интеграцию не используем,
   запрос к модели оформляется обычным `@DBOS.step`.» In «Что проверить»: «Проверить один LLM-шаг через LLMClient внутри `@DBOS.step` (один запрос модели — один durable step)».

[34] MAJOR | lens: consistency | location: G14 (A4); раздел 10, таблица альтернатив (Keycloak) и «Ограничения и риски»; G12 против раздела 13 «Инфраструктура и затраты»
   QUOTE: на сервере с 8 GB, где уже работают база, воркер и мониторинг, не помещается с запасом; он уместен при 16 GB и более
   PROBLEM: G14 states as fact that Keycloak does not fit with margin on the 8 GB server. Section 10 says the memory figures come from documentation («не измерено»), «хватит ли памяти — не измерено», and its table calls Keycloak
   the «IdP при сервере от 8 GB RAM»; section 13 adds that the roughly 6 GB whole-stack estimate is unmeasured and excludes the IdP. The sections' caveat is right. Related: G12 and A5 call 16-24 GB the recommended start, while
   section 13 budgets production on the 8 GB VPS-2 and calls the 24 GB VPS-4 «путь роста».
   FIX: G14: «Keycloak по документации занимает 1.25–1.36 GB; поместится ли он на сервере с 8 GB рядом с базой, воркером и мониторингом, не измерено и проверяется пробой на Этапе 2; с запасом он уместен при 16 GB и более. Иначе —
   Logto, ZITADEL или внешний сервис.» Section 10 table: «IdP при сервере от 8 GB RAM» → «Кандидат IdP; на 8 GB — только после замера, с запасом — от 16 GB (G14)». Section 13: «Путь роста: OVH VPS-4» → «Рекомендуемая стартовая
   конфигурация по G12: OVH VPS-4».

[38] MAJOR | lens: consistency | location: A7 (вступительная фраза и список вопросов); разделы 4, 5, 6, 10, 12 «Что проверить» (решения владельцев); G10
   QUOTE: Вопросы 1–8 блокируют начало Этапа 2; остальные можно закрыть по ходу.
   PROBLEM: Sections put decisions on the owners that are not among A7's 16 questions: the identity provider (section 10: «конкретный IdP ждёт решения владельцев»), the rule for introducing a graph database (section 6: «требует
   согласия владельцев»), where model traces are kept (section 5, п. 9), a qualified timestamp or PAdES signature (section 12, п. 4), the actions that need human approval (section 4, п. 7), and Gotenberg, which G10 allows «только
   по вашему решению». Also, question 16 says the first-case data «нужны к началу Этапа 2» but is outside the blocking range 1-8.
   FIX: First sentence: «Вопросы 1–8 и 16 блокируют начало Этапа 2; остальные можно закрыть по ходу.» Add: «17. **Поставщик входа:** свой сервер или внешний сервис (учётные данные у третьей стороны); допустим ли AGPL (ZITADEL);
   нужны ли MFA и организации в MVP. 18. **Графовая СУБД:** принимаете ли правило «вводится только при выигрыше не менее чем в 3 раза либо если базовый вариант не укладывается в сроки»; нужны ли аналитикам запросы по всему
   накопленному графу. 19. **Трассы моделей:** Phoenix на своём сервере или Langfuse Cloud EU. 20. **Метка времени и подпись:** нужна ли квалифицированная метка (eIDAS) или подпись PAdES; допустим ли Gotenberg с Chromium как
   запасной движок PDF. 21. **Действия, требующие подтверждения человеком.**»

[40] MINOR | lens: consistency | location: A1, строки 4 и 8 (столбец «Заменяемость»); раздел 4 «Заменяемость»; раздел 8 «Заменяемость»
   QUOTE: Высокая при соблюдении изоляции. Durable-слой закрывается одним модулем-адаптером (декораторы workflow/step, очереди, `send/recv`)
   PROBLEM: The same DBOS layer is rated «высокая» in section 4 and A1 row 4 («закрывается одним модулем-адаптером») and «средняя» in section 8 and A1 row 8 («Декораторы … пронизывают код оркестрации»). Section 8 is more likely
   right: it read the code, and section 4 itself says the replacement effort is «не измерено».
   FIX: A1 row 4, «Заменяемость»: «средняя для durable-слоя (как в строке 8), высокая для LLM-слоя». Section 4: «Для LLM-слоя — высокая; для durable-слоя — средняя, как в разделе 8: декораторы DBOS пронизывают код оркестрации,
   поэтому нужен адаптер JobRunner.»

[41] MINOR | lens: consistency | location: A9, строка 1; A2, п. 9; A2, п. 2
   QUOTE: Зависимость от одного оператора: адресный индекс и internal transactions есть только у TronGrid
   PROBLEM: Three Part A statements are firmer than their sections. (1) Section 1 says internal transactions at Chainstack are «не проверено», and A8 п. 1 tests exactly this. (2) A2 п. 9 says of the DBOS findings «Всё устранимо
   настройкой», but section 8 says automatic takeover of a crashed worker's work exists only in paid Conductor and that recovery is «на практике не проверено». (3) A2 п. 2 states the TronScan prohibition flatly, while G5 notes it
   is unconfirmed that the 2022 document is the current edition.
   FIX: (1) «…адресный индекс и internal transactions вживую подтверждены только у TronGrid (у Chainstack не проверено)». (2) «По документации и коду это закрывается настройкой и политикой перезапуска воркера; на практике не
   проверено, поэтому до Этапа 2 есть более простой запасной путь.» (3) After the ToS sentence add: «(действующая ли это редакция, не подтверждено — см. G5)».

[42] MINOR | lens: consistency | location: раздел 14 «Решение» и «Почему выбрано»; раздел 11 «Как проверяем качество», 2-й пункт; раздел 8 «Инфраструктура и затраты» (Token bucket); G4, G5
   QUOTE: чёрный список контракта USDT (`isBlackListed` и события через TronGrid)
   PROBLEM: G5 and section 1 assign constant calls, including the final isBlackListed, to an operator other than TronGrid; section 14 routes isBlackListed through TronGrid. Section 11 describes the TronGrid-versus-node cross-check
   as «по выборке TXID», while section 1 and A6 require it for every fact. Section 8 places the limiter in «один fetcher-процесс на провайдера», while G4 and section 11 describe the gateway as running inside the application
   process. G5, section 1 and section 11 are the reconciled positions.
   FIX: Section 14: «чёрный список контракта USDT (события через TronGrid, итоговый `isBlackListed` — у независимого оператора узла, G5)». Section 11: «Перекрёстная сверка по выборке TXID» → «Сверка каждого факта отчёта (и
   выборочно — остальных TXID)». Section 8: «в MVP — ограничитель aiolimiter внутри HTTP-шлюза в единственном процессе воркера (G4)».

[43] MINOR | lens: consistency | location: раздел 3 «Что проверить», 3-й пункт; раздел 5 «Как проверяем качество», «Состояние проекта», «Что проверить» п. 8; раздел 7 «Инфраструктура»; раздел 12 «Ограничения и риски»; раздел 13 «Ограничения и риски»
   QUOTE: Выбрать второй независимый TransferSource (кандидаты — в G5).
   PROBLEM: Several cross-references point to a G decision that does not contain the thing cited. G5 names no index candidates (section 1 does). «раздел G11» is not a section. G3 does not mention Pydantic AI (G13 does). G12 does
   not cover backups (section 13 does). G13 does not mention the trace UI (section 5 does). G10 does not name Graphviz (section 9 does).
   FIX: Section 3: «(кандидаты — в разделе 1)». Section 5: «(до подписи и timestamp, G11)»; «Pydantic AI (G13, раздел 4)»; «В спайке G3: вызовы Pydantic AI…» → «В проверке G13 (spike раздела 4): вызовы Pydantic AI…». Section 7:
   «Бэкап — pgBackRest + restic в Backblaze B2 (раздел 13)». Section 13: «UI трасс (раздел 5)». Section 12: «Кандидат G10 (SVG из Graphviz)» → «Кандидат из раздела 9 (SVG из Graphviz)».

[44] MINOR | lens: consistency | location: раздел 3 «Инфраструктура и затраты», последний пункт; раздел 6 «Как проверяем качество» (Метки); раздел 2, таблица альтернатив (Arkham); A10; раздел 1 «Инфраструктура» (Кэш); раздел 10 «Лицензия»
   QUOTE: keyless-доступ TronGrid (по документации — жёсткое ограничение или отказ; не измерено)
   PROBLEM: Some «не проверено / не измерено» markers are contradicted by other sections. Section 1 measured keyless TronGrid at 3 rps, then 429 and a 5 s pause. Section 6 says RemovedBlackList and DestroyedBlackFunds were not
   checked live, while sections 1-3 report them returned live. Section 2 and A10 say arkm.com was unreachable and Arkham prices unverified, while section 3 reads prices from arkm.com/llms.txt. Section 1 gives a blacklist mirror of
   «около 7.8 тыс. записей» while section 2 says no full count was made. Section 10 says Pydantic's licence is unverified while section 12 states MIT. The sections holding the concrete probe are more likely right.
   FIX: Section 3: «keyless-доступ TronGrid (без ключа измерено 3 rps, затем 429 и пауза 5 с — раздел 1)». Section 6: «RemovedBlackList и DestroyedBlackFunds получены вживую в пробах разделов 1–3». Section 2 and A10: «сайт
   arkm.com не открывался; цены Arkham прочитаны из arkm.com/llms.txt (раздел 3)». Section 1: «около 7.8 тыс. записей (оценка; полный подсчёт событий не выполнялся, раздел 2)». Section 10: «Лицензия uvicorn в досье не
   зафиксирована — не проверено (Pydantic — MIT, раздел 12)».

[45] MINOR | lens: consistency | location: A8 (вступительная фраза и пп. 2, 4, 6, 7, 9); разделы 2, 5, 7, 10, 11, 12, 14 «Что проверить»
   QUOTE: Каждая закрывает конкретное «не измерено» из этого документа.
   PROBLEM: Beyond the second index and DBOS on PostgreSQL 18, A8 omits further section-level checks: the comparison of three strong-tier models and the reading of the OpenAI agreement that G13 makes a precondition for the
   fallback (section 5, пп. 3-4); Cyrillic rendering and font embedding, unverified per section 12 п. 3 although reports are in Russian; the IdP probe on the reference server (section 10); RLS overhead (section 7); calibration of
   the deposit heuristic (section 2, п. 7); replay from stored responses (sections 4 and 11); written answers from Brave, Chainabuse and SSLMate (section 14).
   FIX: Add: п. 2 — «Brave (если выбран): журнал и передача выдачи в модель; Chainabuse и SSLMate: условия.» п. 4 — «Сравнение трёх вариантов сильной модели; чтение договора OpenAI и проверка закрепления версий до включения
   запасного провайдера.» п. 6 — «Рендер кириллицы и встраивание шрифтов.» п. 7 — «Калибровка эвристики на активных горячих кошельках.» п. 9 — «Проба поставщика входа на эталонном сервере; накладные расходы RLS; повторный прогон
   из сохранённых ответов даёт тот же граф и отчёт.»

[46] MINOR | lens: consistency | location: A1, столбцы «Статус» (строки 2, 9, 10, 13) и «Лицензия» (строки 5, 7, 9, 12); A7, вопрос 13
   QUOTE: pgBackRest и restic в Backblaze B2; SOPS и age | принято |
   PROBLEM: Mixed decisions are flattened inconsistently: rows 2 and 9 (accepted core, conditional part) show «условно», while rows 10 and 13 (IdP open; pgBackRest on B2 and 8 GB sufficiency conditional per section 13) show
   «принято». The licence column omits components the sections name: psycopg 3, the default driver (LGPL-3.0, sections 6-7), opentimestamps-client and docxtpl (LGPL, section 12), Phoenix (Elastic License 2.0, section 5); row 9
   says «MIT» although section 9 leaves TanStack Router and zustand «не проверено». A7 вопрос 13 says GPL components would be excluded for on-prem delivery, but the chosen stack has none at runtime; the affected ones are LGPL,
   AGPL and ELv2.
   FIX: Statuses: row 2 «принято (Label Store); условно (MistTrack)»; row 9 «принято (SPA); условно (карта и раскладка)»; row 10 «принято; поставщик входа — за вами»; row 13 «принято; условно: pgBackRest на B2, достаточность 8
   GB». Licences: row 5 add «Phoenix — Elastic License 2.0»; row 7 «PostgreSQL License, MIT; драйвер psycopg 3 — LGPL-3.0»; row 9 «MIT (TanStack Router и zustand — не проверено)»; row 12 add «клиент OpenTimestamps и docxtpl —
   LGPL». A7 вопрос 13: «Во втором случае нужна юридическая оценка компонентов под LGPL (psycopg 3, клиент OpenTimestamps, docxtpl), AGPL (Grafana, ZITADEL) и Elastic License (Phoenix).»

[48] MINOR | lens: consistency | location: раздел 1 «Заменяемость»; раздел 2 «Заменяемость»; раздел 3 «Заменяемость» и «Как проверяем качество»; A5; «Как читать»
   QUOTE: Интерфейс TransferHistoryProvider; вторая реализация — индекс стороннего оператора, не TronScan.
   PROBLEM: Key terms drift. The same interfaces are TransferHistoryProvider and LabelProvider in sections 1-2 but TransferSource and LabelSource in section 3. «Стандартное расследование» is about 40 addresses in section 1, 30 in
   section 3, 45 (heavy 60) in section 5 and «несколько десятков» in A5 and section 6. «Аудит» means the whole verified study in Part A, but in the sections it often means the unverified first-pass research («исходный аудит»,
   «первичный аудит», «тезис аудита опровергнут»), alongside «верификатор», «проверяющий», «перепроверка».
   FIX: Use TransferSource and LabelSource in sections 1 and 2. Define once in A5 and reuse: «стандартное расследование — 40–45 адресов (тяжёлое — 60)». Add to «Как читать»: «В части B «аудит» или «исходный аудит» — первичное
   исследование направления, «верификатор» — независимая перепроверка; там, где они расходятся, действует вывод верификатора.»

[55] MAJOR | lens: measurability | location: раздел 5, «Ограничения и риски»; G13; раздел 8, «Состояние проекта»
   QUOTE: Латентность не измерена: вызов Sonnet с effort high плюс первая компиляция грамматик может занять больше минуты
   PROBLEM: By the document's own figures the 30-second target does not fit on paper if the path contains one Sonnet call: such a call may take over a minute, grammar compilation can take up to 180 s with a 24-hour cache (so warm-
   up at deploy is not enough), and default DBOS polling adds 10-60 s. G13 still puts Sonnet on planning and report sections of every investigation, and no per-step time budget is given for any of the three targets.
   FIX: Add under the A6 table: «Бюджет времени, расчёт (уточняется замером Этапа 2). Простая транзакция, 30 с: очередь и чекпойнты — до 2 с; TronGrid и узел — до 10 с; шаги Haiku параллельно — до 10 с; проверка доказательств и
   сборка JSON — до 5 с; запас — 3 с. На этом пути нет вызовов Sonnet и режима effort high; схемы структурированного вывода прогреваются при деплое и не реже раза в 24 часа (срок кеша грамматик). Такие же таблицы составляются для
   2 минут и 5 минут до начала замеров.»

[57] MAJOR | lens: measurability | location: раздел 6, «Что проверить», критерии LH-GraphBench; также раздел 1 (пункт 1), раздел 4 (пункт 3), раздел 8 (проверка 8); A8, пункт 1
   QUOTE: граф на 1 000 адресов ≤ 5 мин; отчёт на несколько десятков адресов ≤ 2 мин
   PROBLEM: The same «1 000 адресов за 5 минут» is the pass criterion of four checks with different scope (TronGrid load run, DBOS spike, a mock-API load test, a graph-layer benchmark); none is end-to-end with real sources,
   verification receipts and model steps, so passing any of them does not establish criterion 3. The load profile is also undefined: with one worker and one shared limiter per provider, a 1,000-address job takes the whole TronGrid
   allowance while a 30-second job runs beside it.
   FIX: Add to A8: «Приёмочный замер критерия 3 один: сквозной прогон на тестовом сервере с реальными источниками, от постановки задачи до проверенного JSON-отчёта, по одной задаче одновременно, на наборе графов, зафиксированном
   до замера. Проверки в разделах 1, 4, 6 и 8 — бюджеты компонентов (источник, очередь, графовый слой), а не приёмка. Отдельно измеряется смешанная нагрузка: простая задача во время обхода графа на 1 000 адресов; для неё в
   ограничителе шлюза вводится приоритет интерактивных запросов.» In section 6 replace the quoted criteria with «графовый слой укладывается в свою долю бюджета времени, заданную до замера».

[65] MAJOR | lens: measurability | location: раздел 14, «Как проверяем качество», пункт 2; раздел 8, «Как проверяем качество», первая строка; A6, последняя строка; раздел 3
   QUOTE: не менее 10 из 50 сценариев для измерения precision и recall
   PROBLEM: A6 and section 3 say only synthetic-exact and self-generated scenarios count toward the 50 and freeze-anchored cases are a separate class, but section 14 puts at least 10 OFAC and blacklist scenarios inside the 50 and
   section 8 says its eight crash and limit checks «войдут в набор из 50+ сценариев». Counted that way about 32 tracing scenarios remain, and section 3 admits the current design yields only 25+.
   FIX: Section 14: «Адреса из OFAC SDN и из событий AddedBlackList входят в отдельный класс freeze-anchored — не менее 10 сценариев сверх 50 — для измерения precision и recall.» Section 8: «Критерии spike; они же войдут в
   регрессионные тесты надёжности, отдельно от 50 сценариев трассировки:». A6, last row, add: «Сейчас спроектировано 25+ засчитываемых сценариев; нужно ещё не менее 25 и итоговый набор.»

[70] MAJOR | lens: measurability | location: A8, вводный абзац и пункты 1, 3, 4, 5; раздел 4 (пункт 5), раздел 8 («Что проверить»), раздел 9 (пункты 1–3)
   QUOTE: Каждая закрывает конкретное «не измерено» из этого документа.
   PROBLEM: A8 lists what is measured but not what counts as a pass or what follows a failure, so the owners approve Stage 2 without go or no-go rules. Missing where clearly needed: a threshold for model refusals; one DBOS
   decision rule (section 4 says «если разница в надёжности не видна», section 8 says «при провале»); map thresholds that section 9 leaves to the owners but A7 never asks for; and what happens if 5 minutes is unreachable on the
   free TronGrid plan (section 3 says «пересмотр цели», a change to an owner criterion).
   FIX: Add «Критерий» and «При провале» to each A8 item, including: item 1 — «При провале цели 5 минут: индивидуальный план TronGrid или второй провайдер; изменение самой цели — только решением владельцев»; item 3 — «Критерий:
   вариант проходит все восемь проверок раздела 8; если проходят оба, берётся вариант без DBOS; если один — он»; item 4 — «Критерий: не менее 95% запусков заканчиваются корректным отчётом или понятной ошибкой; доля запусков, где
   из-за отказа модели отчёт вышел без её текста, — не выше порога владельцев (предложение: 10%). При провале: смена модели или режим без текста модели по умолчанию». Add to A7 question 12: «пороги приёмки карты: кадров в секунду
   на 1 000 узлов и предельное время раскладки (ориентир аудита — 30 кадров в секунду)».

[74] MAJOR | lens: reader-safety | location: A7, opening line (and the whole list)
   QUOTE: Вопросы 1–8 блокируют начало Этапа 2; остальные можно закрыть по ходу.
   PROBLEM: Part B names at least nine further owner decisions that never appear in A7: IdP hosting and AGPL (s.10), where model traces live and ZDR (s.5), which actions need human approval (s.4), the graph-DB decision rule (s.6),
   young single-vendor library and a job-monitoring UI (s.8), FPS and hardware thresholds (s.9), a platform MCP server (s.11), eIDAS or PAdES (s.12), the confidence scale (s.2). An owner deciding from Part A will not know they
   exist.
   FIX: Add item 17 to A7 (defaults taken from A4/A5; author to confirm): «17. **Решения с вариантом по умолчанию** (если ответа нет, действует вариант по умолчанию; подробности — в конце разделов части B): поставщик входа — на
   своём сервере (Keycloak при 16 GB и более, иначе Logto после пробы) или внешний сервис; допустима ли лицензия AGPL (раздел 10). Журнал вызовов моделей — на своём сервере (по умолчанию) или в облаке ЕС (раздел 5). Действия,
   требующие подтверждения человеком: по умолчанию — любая отправка обращений (раздел 4). Правило ввода графовой СУБД (раздел 6). Готовый веб-интерфейс мониторинга задач: по умолчанию нет (раздел 8). Пороги плавности карты и
   целевое оборудование (раздел 9). Внешний MCP-интерфейс платформы: по умолчанию нет (раздел 11). Квалифицированная метка времени eIDAS или подпись PAdES: по умолчанию нет (раздел 12). Шкала достоверности меток (раздел 2).»

[79] MAJOR | lens: reader-safety | location: A1 first paragraph; A2 item 1; A6 row «Показатели AI-слоя»; A4 G14
   QUOTE: Готового движка трассировки, пригодного как основа, не существует, поэтому ядро — собственный детерминированный трассировщик
   PROBLEM: Four Part A statements are more confident than Part B and A10, which say the candidate search was incomplete and nothing was measured: «не существует», «Готового движка трассировки нет», «нет ни у кого на рынке», and
   G14 «Keycloak занимает 1.25–1.4 GB и … не помещается с запасом» (section 10: figures from documentation, «хватит ли памяти — не измерено»).
   FIX: (a) A1: «Готового движка трассировки, пригодного как основа, аудит не нашёл (поиск неполон, см. A10), поэтому ядро — собственный детерминированный трассировщик поверх публичных API TRON.» (b) A2.1 heading: «**Готового
   движка трассировки не найдено.**» (c) A6 state: «не измерено; опубликованных количественных подтверждений у других проектов не найдено (поиск неполон)». (d) G14: «Вход: серверная часть — стандартный OIDC resource server,
   поставщик входа заменяем. По документации Keycloak требует 1.25–1.4 GB памяти; поместится ли он на сервер с 8 GB рядом с базой, воркером и мониторингом, не измерено. Поэтому Keycloak рекомендуется при 16 GB и более, при 8 GB —
   Logto, ZITADEL или внешний сервис после пробы на Этапе 2. Выбор зависит также от юрисдикции (вопрос 2).»

[88] MAJOR | lens: reader-safety | location: Section 3, «Состояние проекта…» (also «Почему выбрано», «Ограничения и риски», «Что проверить»); sections 4, 5, 14
   QUOTE: Wallet-Risk-Scanner (190 stars за 3 недели) — загрузчик нативного кода под Windows; stolen-funds-finder — clipboard hijacker.
   PROBLEM: Part A says «с признаками вредоносного кода», but section 3 calls the two named repositories «вредоносных» as fact in four places although the code was never run. Other third-party statements are also firmer than what
   was observed: «Serper и SerpApi — скрейпинг Google, суды не завершены» (s.14), DeepSeek data practices (s.5), LiteLLM PyPI compromise (s.4), the crypttrace author-account remark (s.3). Section 14 also contradicts itself on T3
   FCU («В справочнике — статус press» vs «до этого в справочник не вносится»).
   FIX: Section 3: «…и два репозитория с признаками вредоносного кода»; «Wallet-Risk-Scanner (190 stars за 3 недели) по статическим признакам похож на загрузчик нативного кода под Windows, stolen-funds-finder — на подменщик буфера
   обмена. Код не исполнялся, вывод предварительный»; «один из репозиториев с признаками вредоносного кода нацелен на Windows»; «deny-list двух репозиториев с признаками вредоносного кода». Keep the names only in the deny-list
   sentence. Section 14: «Serper и SerpApi получают выдачу Google скрейпингом; по публичным сообщениям, идут судебные споры (не проверено)»; «T3 FCU в справочник не вносится до подтверждения домена». Add the source to the LiteLLM
   and DeepSeek statements («по опубликованному advisory проекта», «по условиям сервиса, в аудите не перечитывались») and «это наблюдение, а не вывод о вредоносности» after the crypttrace account remark.

[91] MAJOR | lens: reader-safety | location: Part B throughout (e.g. s.10 «Лицензия…», s.8, s.11, s.3, s.6, s.2); A10 bullet 4
   QUOTE: Лицензии Pydantic и uvicorn в досье не зафиксированы — не проверено.
   PROBLEM: Drafting-process vocabulary is visible and inconsistent: «досье», «исследователь», «верификатор», «проверяющий аудитор», «исходный/первичный аудит», «аудит этой области», «поправка перепроверки», «лимит веб-поиска
   закончился». In section 11 «верификатор отклоняет любой факт отчёта» uses the same word for a platform component. Names appear with no introduction (LOCARD, tronetl, «список BlockSec», «CSV BitOK», Raphtory, Grafeo, NeuG, arXiv
   2512.02534), and the fixed tag «не измерено/не проверено» breaks grammar («Скорость и память не измерено»).
   FIX: Use two terms only, «первичное исследование» and «перепроверка», and delete narration that does not change a decision. Exact replacements: s.10 «Лицензии Pydantic и uvicorn в аудите не проверялись.»; s.8 «Независимых
   отчётов о production-эксплуатации не найдено (поиск неполон).»; s.11 «модуль проверки доказательств отклоняет любой факт отчёта без ссылки на такую запись»; A10 «**Новые участники рынка 2025–2026 годов:** на этапе перепроверки
   поиск был ограничен и по части направлений не завершён; список альтернатив может быть неполон.» Introduce each dangling name in one clause or remove it; fix agreement («скорость и память не измерены»).

[92] MAJOR | lens: reader-safety | location: Sections 4, 8, 9 «Лицензия и коммерческое использование» (also s.7, s.12, s.13); A10 bullet 5
   QUOTE: Коммерческое SaaS-использование разрешено без условий.
   PROBLEM: Reads as legal advice and is inexact: MIT does carry a condition (keep the copyright notice and licence text). Similar flat conclusions cover LGPL and AGPL components («обязательств на код платформы не создают», «код
   платформы не затронут»). The only disclaimer is the fifth bullet of A10, which a reader dipping into Part B will not see.
   FIX: Replace «разрешено без условий» in sections 4, 8 and 9 with «разрешено; условие MIT — сохранять уведомление об авторских правах и текст лицензии». Prefix the LGPL/AGPL conclusions in sections 7, 12 and 13 with «по нашему
   прочтению». Move the disclaimer into «Как читать»: «Все прочтения лицензий и условий использования в этом документе — выводы инженера, а не заключения юриста; спорные случаи вынесены в вопрос 8.»

[93] MAJOR | lens: reader-safety | location: A2 item 9
   QUOTE: Чтение кода показало: два опроса по 1.0 секунды по умолчанию, восстановление привязано к версии приложения, состояние по умолчанию хранится в pickle
   PROBLEM: Over-compressed: it does not say what DBOS is, what is polled or why any of the four points matters, and Conductor, pickle and Procrastinate are unexplained although Q10 asks the owners to rule on DBOS. «Всё устранимо
   настройкой» overstates: automatic takeover exists only in paid Conductor (section 8).
   FIX: Replace with: «9. **Оркестрация на DBOS — условный выбор.** DBOS Transact — библиотека Python, которая сохраняет каждый шаг расследования в PostgreSQL и после сбоя продолжает с последнего шага. Чтение её кода показало
   четыре особенности настроек по умолчанию: очередь опрашивается раз в секунду, что добавляет 1–2 секунды на каждый вызов через очередь и угрожает цели «30 секунд»; после выкладки новой версии незавершённые расследования сами не
   продолжаются; состояние шагов хранится в формате pickle (небезопасен и ломается при изменении кода); работу упавшего воркера автоматически перехватывает только платная консоль Conductor (от $99/мес). Первые три устраняются
   настройкой, четвёртая в MVP с одним воркером закрывается его перезапуском. Всё это проверяется на Этапе 2; запасной путь проще — обычная очередь Procrastinate и свои таблицы.»

[97] MINOR | lens: reader-safety | location: A4 G6 and G8; A1 row 5 and A5 («интерфейс трасс»); A6; Part B terminology
   QUOTE: Четыре методики распределения смешанных средств (FIFO, LIFO, pro-rata, верхняя граница poison) считаются параллельно
   PROBLEM: «poison» (taint method, G8) and «address poisoning» (zero-value transfers, G6) are different things two bullets apart, neither explained. «Трассы моделей» collides with «трассировка» of funds. A6 uses «30 секунд / 2
   минуты / 5 минут» without saying what each measures and «заложено в архитектуру» could be read as done. Part B uses spike, baseline, ground truth, IdP, TSA, ZDR, RPO/RTO, HITL where Part A uses Russian terms, with no mapping.
   FIX: Add to «Как читать»: «**Термины.** poison — методика, по которой после смешивания «заражённой» считается вся сумма (верхняя граница); address poisoning — рассылка переводов с нулевой суммой, к методике poison не относится;
   трассы моделей — журнал вызовов языковых моделей, а не трассировка средств; spike — короткая проверочная реализация на 2–3 дня; baseline — детерминированный алгоритм без модели, с которым сравнивается AI-слой; ground truth —
   заранее известный правильный ответ; IdP — поставщик входа; TSA — служба меток времени; ZDR — режим без хранения данных у провайдера модели; RPO и RTO — допустимая потеря данных и время восстановления; HITL — шаг с
   подтверждением человеком. «Заложено в архитектуру» в A6 значит: предусмотрено проектом, кода и замеров ещё нет.» In A6: «30 секунд (простая транзакция) / 2 минуты (стандартный отчёт) / 5 минут (граф на 1 000 адресов)». In A1
   and A5: «интерфейс просмотра журнала вызовов моделей».

[98] MINOR | lens: reader-safety | location: Section 5 «Решение» (also «Решение» in sections 3 and 4)
   QUOTE: **Решение.** Primary — Anthropic Claude API: `claude-haiku-5-5` на рутинных шагах
   PROBLEM: The decision paragraphs of sections 3, 4 and 5 are half English (Primary, Fallback, strong-tier, LLM-gateway, evals, «deterministic baseline tracer», «durable workflows, очереди, HITL», spike), while Part A says the
   same things in Russian. Spellings also drift («чекпоинт/чекпойнт», «Tronscan/TronScan»).
   FIX: Section 5: «**Решение.** Основной провайдер — Anthropic Claude API: `claude-haiku-5-5` на рутинных шагах, `claude-sonnet-5-5` для планирования и коротких секций отчёта; сильная модель задаётся настройкой. Запасной
   провайдер — OpenAI (`gpt-6-luna`, `gpt-6.1-sol` через Responses API). Доступ — официальные SDK за собственным адаптером LLMClient, без промежуточного шлюза моделей; журнал вызовов моделей хранится в своей БД и передаётся по
   OpenTelemetry, интерфейс просмотра — Arize Phoenix либо Langfuse Cloud EU (по решению владельцев о размещении данных); оценка качества — Inspect AI в Linux-контейнере. Статус: условно — до юридического разбора политики
   использования, пилота на 50 сценариях и чтения договора OpenAI.» Section 3: «ядро — собственный детерминированный трассировщик (G8)». Section 4: «на DBOS Transact (сохраняемые сценарии, очереди, шаги с подтверждением
   человеком)» and «после проверочной реализации на Этапе 2». Unify «чекпоинт» and «TronScan».
