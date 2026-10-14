# Review issues relevant to section(s) [5] (llm-models)

[1] MAJOR | lens: owner-format | location: Part A, A4 (cross-cutting decisions G1-G15), after G15; also A6
   QUOTE: Поискового провайдера (Tavily или Brave) выбираете вы. Платформа никогда не обещает возврат средств.
   PROBLEM: The always-on principle 'seed phrases, private keys and wallet access are never requested' has no cross-cutting decision in Part A. It appears only as one clause in section 14 (risks) and as trace masking in section 5;
   there is no control for victim-supplied screenshots and correspondence, which A7.3 plans to send to model providers.
   FIX: Добавить в A4: «**G16.** Платформа никогда не запрашивает seed-фразы, приватные ключи и доступ к кошельку: таких полей нет ни в интерфейсе, ни в API, ни в шаблонах писем. Входной фильтр проверяет текст пользователя и
   текст, распознанный во вложениях (скриншоты, переписка): найденная seed-фраза или приватный ключ не сохраняется и не передаётся моделям и поисковым провайдерам, пользователь получает предупреждение. Все инструменты — только
   чтение; подписи и отправки транзакций в системе нет (раздел 11).» В A6 добавить строку: «Seed-фразы и приватные ключи не запрашиваются и не сохраняются | входной фильтр; тест с подставной seed-фразой: 0 вхождений в БД,
   журналах, трассах и запросах к моделям — обязательное условие сборки | заложено в архитектуру».

[6] MAJOR | lens: owner-format | location: Section 4 'Решение' vs section 5 'Решение' vs A4 G13 vs A1 rows 4-5 (needs d, e, k)
   QUOTE: Pydantic AI для LLM-шагов в точках принятия решений; всё работает на том же PostgreSQL, без отдельного сервера оркестрации
   PROBLEM: The chosen solution for the model-access layer differs by section: section 4 chooses Pydantic AI, section 5 chooses 'официальные SDK за собственным адаптером LLMClient', G13 says the choice is open until Stage 2, and
   A1 does not mention Pydantic AI. Section 5 also does not justify writing its own adapter instead of reusing Pydantic AI.
   FIX: Привести к G13. Раздел 4, «Решение»: «…и собственный интерфейс LLMClient для LLM-шагов; под ним условно Pydantic AI, альтернатива — официальные SDK (решает spike Этапа 2, G13)». Раздел 5, «Решение»: «Доступ — только через
   собственный адаптер LLMClient, без LLM-gateway; реализация под ним (Pydantic AI или официальные SDK) выбирается на Этапе 2». В таблицу альтернатив раздела 5 добавить строку «Pydantic AI напрямую, без LLMClient | MIT |
   cost_limit срабатывает после превышения; 55 minor-релизов за 15.4 недели; 16 advisories — нужен собственный слой учёта стоимости и журнала». В A1, строка 4: «…; LLM-шаги — условно Pydantic AI под LLMClient».

[12] MAJOR | lens: owner-format | location: Section 10, 'Решение'; A1 row 10; A7 (owner decisions)
   QUOTE: Статус: принято; конкретный IdP ждёт решения владельцев и пробы на сервере.
   PROBLEM: The authentication provider has no chosen solution (Keycloak, Logto, ZITADEL or external), yet A1 row 10 is marked 'принято' and A7 contains no question about it. Other decisions that Part B leaves to the owners are
   also missing from A7.
   FIX: A1, строка 10, статус: «принято; поставщик входа — условно». Добавить в A7: «17. **Поставщик входа:** на своём сервере ([рекомендация по умолчанию: Logto при 8 GB после замера памяти, Keycloak при 16 GB и более]) или
   внешний сервис, где учётные данные хранит третья сторона; допустим ли ZITADEL под AGPL; нужны ли в MVP MFA и организации. 18. **Решения из разделов части B:** размещение трасс моделей — Phoenix на своём сервере или Langfuse
   Cloud EU (раздел 5); перечень действий, требующих подтверждения человеком (раздел 4); правило ввода графовой СУБД „выигрыш не менее чем в 3 раза“ (раздел 6); нужен ли MCP-сервер платформы для клиентов (раздел 11); нужна ли
   квалифицированная метка времени eIDAS или подпись PAdES (раздел 12); допустим ли Gotenberg с Chromium как запасной движок PDF (G10); шкала confidence (раздел 2).»

[19] MINOR | lens: owner-format | location: Part A, A9 (last row) and A5
   QUOTE: Объём собственного кода больше, чем «только клей»: трассировщик, раскладка и сворачивание графа, шлюз
   PROBLEM: The brief's strategy is not to build what already exists; the document admits the own code exceeds glue but never totals the effort. Estimates are scattered across sections 2, 3, 4, 6, 9 and 11, and sections 5, 7, 10,
   12 and 13 give none.
   FIX: Добавить в A5 абзац «Трудозатраты на собственный код (оценки аудита, не измерено)»: «трассировщик 2–3 человеко-недели; оркестратор, учёт бюджета и журнал 2–3; шлюз и реестр инструментов 1.5–2.5; интерфейс и карта 4–5
   (верификатор отдельно оценивает раскрытие ветвей, агрегацию, раскладку и экспорт в 3–4); Label Store 3–5 дней; тестовый набор меток 5–8 человеко-дней; стенд графового теста 1–2 недели. Итого около 12–18 человеко-недель; по
   адаптеру LLMClient, схеме БД, API, отчётам и эксплуатации оценки нет.»

[27] MAJOR | lens: consistency | location: раздел 4 «Решение»; раздел 5 «Решение»; раздел 11 «Лицензия и коммерческое использование»; G13; A1, строки 4–5; A8, п. 4
   QUOTE: и Pydantic AI для LLM-шагов в точках принятия решений; всё работает на том же PostgreSQL
   PROBLEM: Section 4 fixes Pydantic AI as the LLM layer; section 5 fixes «официальные SDK за собственным адаптером LLMClient»; section 11 lists Pydantic AI among «используемые библиотеки»; G13 says the choice between the two is
   made at Stage 2. A1 row 4 does not mention Pydantic AI and A8 has no check that decides it. G13 is the most likely intended position (Part A was written after both sections), so the two «Решение» paragraphs must be aligned to
   it.
   FIX: Section 4: «…на DBOS Transact (durable workflows, очереди, HITL); LLM-шаги в точках принятия решений идут через собственный интерфейс LLMClient (G13). Pydantic AI — кандидат реализации под ним; выбор между Pydantic AI и
   официальными SDK делает проверка Этапа 2; всё работает на том же PostgreSQL…». Section 5: «Доступ — только через собственный адаптер LLMClient, без LLM-gateway; под ним официальные SDK либо Pydantic AI (G13, решается на Этапе
   2)». Section 11: «Используемые библиотеки: Pydantic AI — MIT» → «Кандидат для регистрации инструментов: Pydantic AI — MIT (G13)». A8 п. 4, add: «Выбор реализации под LLMClient: Pydantic AI или официальные SDK.»

[28] MAJOR | lens: consistency | location: A5, таблица «Переменные, на стандартное расследование» и абзац под ней; раздел 5 «Инфраструктура и затраты», пункт о переменных
   QUOTE: | **Итого** | | **около $1.00** |
   PROBLEM: The default limits add up to $0.95-1.02 ($0.05 data + $0.40 labels + $0.45 models + $0.05 or $0.08 search + €0-0.04 timestamp). With Tavily and a commercial timestamp service, which section 12 says is budgeted for the
   paid product, the defaults exceed the owners' $1 cap. The next paragraph treats $0.57 on models as an allowed case although the model limit in the same table is $0.45, a figure that appears in no section. Section 5 also
   reserves «$0.10-0.25» for web search via Anthropic's built-in search, while A5, G15 and section 14 use 10 queries to Brave or Tavily for $0.05-0.08.
   FIX: Make the defaults sum to at most $1, for example a model limit of $0.40, and show the range: «**Итого** | | **$0.90–0.97; общий лимит $1 действует поверх постатейных**». Paragraph: «Запаса почти нет. Тяжёлый случай ($0.57
   на модели) превышает лимит на модели: при его достижении шаги переводятся на Haiku 5.5, а текст отчёта собирается без модели.» Section 5: «Из него $0.05–0.16 — веб-поиск: 10–20 запросов к Brave или Tavily через собственный
   адаптер (раздел 14, G15); встроенный поиск Anthropic не используется».

[30] MAJOR | lens: consistency | location: раздел 4 «Инфраструктура и затраты» и «Что проверить», п. 6; раздел 5 «Почему выбрано»; A5; A8, п. 4
   QUOTE: ориентир: LLM-часть не выше $0.30, верхней границы оценки аудита
   PROBLEM: Three ceilings exist for the same cost item. Section 4 expects $0.05-0.30 per investigation (25 model calls) and tests against $0.30; section 5 computes $0.40 typical and $0.57 heavy (106 and 158 calls); A5 sets a
   $0.45 limit. Section 4 notes the divergence itself, but Part A does not, and A8 п. 4 omits the comparison of the two routing schemes that section 4 requires. Section 5 is more likely right for the routing fixed in G13; $0.30
   belongs to the narrower «только эскалации» scheme.
   FIX: Section 4, п. 6: «…— ориентиры: не выше $0.30 для схемы «Sonnet 5.5 только на эскалациях» и не выше лимита на модели из A5 для схемы G13; расхождение в числе вызовов (25 в этой оценке, 106 в разделе 5) закрывается
   замером». A8 п. 4, add: «сравнение двух схем маршрутизации моделей по фактической стоимости».

[38] MAJOR | lens: consistency | location: A7 (вступительная фраза и список вопросов); разделы 4, 5, 6, 10, 12 «Что проверить» (решения владельцев); G10
   QUOTE: Вопросы 1–8 блокируют начало Этапа 2; остальные можно закрыть по ходу.
   PROBLEM: Sections put decisions on the owners that are not among A7's 16 questions: the identity provider (section 10: «конкретный IdP ждёт решения владельцев»), the rule for introducing a graph database (section 6: «требует
   согласия владельцев»), where model traces are kept (section 5, п. 9), a qualified timestamp or PAdES signature (section 12, п. 4), the actions that need human approval (section 4, п. 7), and Gotenberg, which G10 allows «только
   по вашему решению». Also, question 16 says the first-case data «нужны к началу Этапа 2» but is outside the blocking range 1-8.
   FIX: First sentence: «Вопросы 1–8 и 16 блокируют начало Этапа 2; остальные можно закрыть по ходу.» Add: «17. **Поставщик входа:** свой сервер или внешний сервис (учётные данные у третьей стороны); допустим ли AGPL (ZITADEL);
   нужны ли MFA и организации в MVP. 18. **Графовая СУБД:** принимаете ли правило «вводится только при выигрыше не менее чем в 3 раза либо если базовый вариант не укладывается в сроки»; нужны ли аналитикам запросы по всему
   накопленному графу. 19. **Трассы моделей:** Phoenix на своём сервере или Langfuse Cloud EU. 20. **Метка времени и подпись:** нужна ли квалифицированная метка (eIDAS) или подпись PAdES; допустим ли Gotenberg с Chromium как
   запасной движок PDF. 21. **Действия, требующие подтверждения человеком.**»

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

[49] BLOCKER | lens: measurability | location: A5, таблица «Переменные, на стандартное расследование», строка «Итого»; A6, строка «≤ $1 на расследование»
   QUOTE: | **Итого** | | **около $1.00** |
   PROBLEM: The default limits do not add up to at most $1 in the document's own worst combination: labels $0.40 + models $0.45 + Tavily $0.08 + commercial timestamp about $0.04 + data share $0.05 (counted in A2.5) = $1.02. The
   model limit ($0.45) is also below the document's own heavy case ($0.57), which section 5 says omits thinking-block growth and billed refusals, so the A6 status «расчёт укладывается» is not supported.
   FIX: Replace the row with: «| **Итого по лимитам** | | **$0.90–0.97 переменных затрат; с долей подписки на узел ($0.05) — $0.95–1.02** |». Replace the paragraph after the table with: «Сумма лимитов по статьям сама по себе не
   гарантирует $1: при Tavily и коммерческой метке времени она даёт $1.02. Поэтому поверх лимитов по статьям действует общий жёсткий лимит $1.00 на расследование: платный вызов не отправляется, если его максимальная стоимость
   выводит сумму за лимит. Оценка $0.57 на модели — не верхняя граница: она не учитывает рост входа из-за thinking-блоков и оплачиваемые отказы модели. При достижении лимита моделей ($0.45) отчёт выпускается без текста модели,
   полученные результаты сохраняются.» In A6 change the status to «типичный расчёт — $0.90–0.97; гарантию даёт только общий лимит; не измерено».

[50] BLOCKER | lens: measurability | location: A5, строка «Данные TRON» и текст после таблицы; A6, строка «≤ $1 на расследование»; A7, вопрос 5
   QUOTE: около $0.05 при 1 000 расследований в месяц; в пределах квот $0
   PROBLEM: Criterion 6 requires each investigation's cost to be measured including compute and storage, but the proposal counts only paid calls (Part B calls compute «около $0») and names no component that records CPU time or
   stored bytes per investigation. The one fixed cost it does allocate, the $49 node, is divided by an assumed 1,000 investigations a month: at 100 a month it is $0.49 and the total passes $1, and at 1,000 a month the heavy-case
   model spend ($570) exceeds the $500 monthly Anthropic cap quoted in section 5.
   FIX: Add after the variable-cost table: «Что входит в $1. Мы предлагаем считать критерий по переменным затратам: токены моделей, платные API, поиск, метка времени. Вычисления и хранение измеряются по каждому расследованию:
   оркестратор пишет в таблицу учёта затрат секунды CPU воркера и рендера и объём сохранённых сырых ответов и отчётов; в деньги они пересчитываются по ставке из месячной цены сервера и хранилища. Доля постоянных затрат (узел $49 и
   сервер) показывается отдельной строкой: около $0.06 при 1 000 расследований в месяц и около $0.60 при 100. При 1 000 расследований в месяц расход на модели ($400–570) упирается в месячный потолок Anthropic Start tier ($500):
   уровень нужно поднять заранее.» Add to A7 question 5: «Входит ли в $1 доля постоянных затрат (узел, сервер, хранилище).»

[55] MAJOR | lens: measurability | location: раздел 5, «Ограничения и риски»; G13; раздел 8, «Состояние проекта»
   QUOTE: Латентность не измерена: вызов Sonnet с effort high плюс первая компиляция грамматик может занять больше минуты
   PROBLEM: By the document's own figures the 30-second target does not fit on paper if the path contains one Sonnet call: such a call may take over a minute, grammar compilation can take up to 180 s with a 24-hour cache (so warm-
   up at deploy is not enough), and default DBOS polling adds 10-60 s. G13 still puts Sonnet on planning and report sections of every investigation, and no per-step time budget is given for any of the three targets.
   FIX: Add under the A6 table: «Бюджет времени, расчёт (уточняется замером Этапа 2). Простая транзакция, 30 с: очередь и чекпойнты — до 2 с; TronGrid и узел — до 10 с; шаги Haiku параллельно — до 10 с; проверка доказательств и
   сборка JSON — до 5 с; запас — 3 с. На этом пути нет вызовов Sonnet и режима effort high; схемы структурированного вывода прогреваются при деплое и не реже раза в 24 часа (срок кеша грамматик). Такие же таблицы составляются для
   2 минут и 5 минут до начала замеров.»

[60] MAJOR | lens: measurability | location: раздел 4, «Что проверить», пункт 6; A5 (лимит моделей $0.45); раздел 5, «Как проверяем качество», пункт «Бюджет-трекер»
   QUOTE: ориентир: LLM-часть не выше $0.30, верхней границы оценки аудита
   PROBLEM: Three incompatible model budgets: a Stage 2 threshold of $0.30 (section 4), a default limit of $0.45 (A5) and an expected spend of $0.40 typical and $0.57 heavy (section 5), so the typical estimate already fails the
   section 4 threshold. Behaviour at the limit also differs: pause (A5), PAUSED_BUDGET with resume (section 4), and «при 70% — только Haiku, при 100% — отчёт без LLM-текста» (section 5) without saying 70% of what.
   FIX: Section 4, item 6: «ориентир: LLM-часть не выше лимита моделей из A5 ($0.45); схема «Sonnet только на эскалациях» должна уложиться в $0.30». Section 5: «Бюджет-трекер: при 70% лимита моделей ($0.45 по умолчанию) — только
   Haiku; при 100% лимита моделей — отчёт без текста модели; при достижении общего лимита расследования — пауза PAUSED_BUDGET с сохранением результатов.»

[74] MAJOR | lens: reader-safety | location: A7, opening line (and the whole list)
   QUOTE: Вопросы 1–8 блокируют начало Этапа 2; остальные можно закрыть по ходу.
   PROBLEM: Part B names at least nine further owner decisions that never appear in A7: IdP hosting and AGPL (s.10), where model traces live and ZDR (s.5), which actions need human approval (s.4), the graph-DB decision rule (s.6),
   young single-vendor library and a job-monitoring UI (s.8), FPS and hardware thresholds (s.9), a platform MCP server (s.11), eIDAS or PAdES (s.12), the confidence scale (s.2). An owner deciding from Part A will not know they
   exist.
   FIX: Add item 17 to A7 (defaults taken from A4/A5; author to confirm): «17. **Решения с вариантом по умолчанию** (если ответа нет, действует вариант по умолчанию; подробности — в конце разделов части B): поставщик входа — на
   своём сервере (Keycloak при 16 GB и более, иначе Logto после пробы) или внешний сервис; допустима ли лицензия AGPL (раздел 10). Журнал вызовов моделей — на своём сервере (по умолчанию) или в облаке ЕС (раздел 5). Действия,
   требующие подтверждения человеком: по умолчанию — любая отправка обращений (раздел 4). Правило ввода графовой СУБД (раздел 6). Готовый веб-интерфейс мониторинга задач: по умолчанию нет (раздел 8). Пороги плавности карты и
   целевое оборудование (раздел 9). Внешний MCP-интерфейс платформы: по умолчанию нет (раздел 11). Квалифицированная метка времени eIDAS или подпись PAdES: по умолчанию нет (раздел 12). Шкала достоверности меток (раздел 2).»

[76] MAJOR | lens: reader-safety | location: A7, question 5
   QUOTE: **Распределение бюджета $1** и лимит платных вызовов меток (предложено 2). Что происходит при исчерпании: жёсткая остановка с частичным отчётом
   PROBLEM: Three decisions in one item, and the exhaustion behaviour has no recommended default although A5 and A6 already assume «пауза с сохранением»; section 5 describes a third behaviour (70%: Haiku only, 100%: report without
   model text).
   FIX: Replace with: «5. **Бюджет $1.** (а) Принимаете ли лимиты по умолчанию из A5: модели $0.45, платные метки 2 вызова (до $0.40), поиск 10 запросов? (б) Что происходит при исчерпании лимита: рекомендую паузу с сохранением
   результатов и запросом на повышение лимита (так сформулирован критерий Промпта 3); альтернатива — жёсткая остановка с частичным отчётом.» Align section 5 («Бюджет-трекер») with the chosen behaviour.

[88] MAJOR | lens: reader-safety | location: Section 3, «Состояние проекта…» (also «Почему выбрано», «Ограничения и риски», «Что проверить»); sections 4, 5, 14
   QUOTE: Wallet-Risk-Scanner (190 stars за 3 недели) — загрузчик нативного кода под Windows; stolen-funds-finder — clipboard hijacker.
   PROBLEM: Part A says «с признаками вредоносного кода», but section 3 calls the two named repositories «вредоносных» as fact in four places although the code was never run. Other third-party statements are also firmer than what
   was observed: «Serper и SerpApi — скрейпинг Google, суды не завершены» (s.14), DeepSeek data practices (s.5), LiteLLM PyPI compromise (s.4), the crypttrace author-account remark (s.3). Section 14 also contradicts itself on T3
   FCU («В справочнике — статус press» vs «до этого в справочник не вносится»).
   FIX: Section 3: «…и два репозитория с признаками вредоносного кода»; «Wallet-Risk-Scanner (190 stars за 3 недели) по статическим признакам похож на загрузчик нативного кода под Windows, stolen-funds-finder — на подменщик буфера
   обмена. Код не исполнялся, вывод предварительный»; «один из репозиториев с признаками вредоносного кода нацелен на Windows»; «deny-list двух репозиториев с признаками вредоносного кода». Keep the names only in the deny-list
   sentence. Section 14: «Serper и SerpApi получают выдачу Google скрейпингом; по публичным сообщениям, идут судебные споры (не проверено)»; «T3 FCU в справочник не вносится до подтверждения домена». Add the source to the LiteLLM
   and DeepSeek statements («по опубликованному advisory проекта», «по условиям сервиса, в аудите не перечитывались») and «это наблюдение, а не вывод о вредоносности» after the crypttrace account remark.

[89] MAJOR | lens: reader-safety | location: Section 4, «Инфраструктура и затраты» and «Что проверить», item 6
   QUOTE: **Расхождение с общим решением по LLM:** там Sonnet 5.5 закреплён за планированием и финальным отчётом, что шире, чем «только эскалации».
   PROBLEM: An unresolved drafting note on the most-watched number. Section 4 gives the model cost as $0.05–0.30 with a target of «не выше $0.30», while A5 and section 5 give $0.40–0.57 with a $0.45 limit; a reader dipping into
   section 4 cannot tell which is the proposal.
   FIX: Replace the note with: «В сводке (G13, A5) принята более широкая схема: Sonnet 5.5 на планировании и коротких секциях отчёта. Её расчётная стоимость — $0.40–0.57 на расследование (раздел 5); оценка $0.05–0.30 выше
   относится к схеме «Sonnet только на эскалациях». Обе схемы замеряются на Этапе 2 (пункт 6 ниже).» In item 6 replace «ориентир: LLM-часть не выше $0.30, верхней границы оценки аудита» with «ориентир: не выше лимита $0.45 из A5».

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
