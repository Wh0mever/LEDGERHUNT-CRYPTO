# Review issues relevant to section(s) [4, 11] (agent-orchestration)

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

[27] MAJOR | lens: consistency | location: раздел 4 «Решение»; раздел 5 «Решение»; раздел 11 «Лицензия и коммерческое использование»; G13; A1, строки 4–5; A8, п. 4
   QUOTE: и Pydantic AI для LLM-шагов в точках принятия решений; всё работает на том же PostgreSQL
   PROBLEM: Section 4 fixes Pydantic AI as the LLM layer; section 5 fixes «официальные SDK за собственным адаптером LLMClient»; section 11 lists Pydantic AI among «используемые библиотеки»; G13 says the choice between the two is
   made at Stage 2. A1 row 4 does not mention Pydantic AI and A8 has no check that decides it. G13 is the most likely intended position (Part A was written after both sections), so the two «Решение» paragraphs must be aligned to
   it.
   FIX: Section 4: «…на DBOS Transact (durable workflows, очереди, HITL); LLM-шаги в точках принятия решений идут через собственный интерфейс LLMClient (G13). Pydantic AI — кандидат реализации под ним; выбор между Pydantic AI и
   официальными SDK делает проверка Этапа 2; всё работает на том же PostgreSQL…». Section 5: «Доступ — только через собственный адаптер LLMClient, без LLM-gateway; под ним официальные SDK либо Pydantic AI (G13, решается на Этапе
   2)». Section 11: «Используемые библиотеки: Pydantic AI — MIT» → «Кандидат для регистрации инструментов: Pydantic AI — MIT (G13)». A8 п. 4, add: «Выбор реализации под LLMClient: Pydantic AI или официальные SDK.»

[30] MAJOR | lens: consistency | location: раздел 4 «Инфраструктура и затраты» и «Что проверить», п. 6; раздел 5 «Почему выбрано»; A5; A8, п. 4
   QUOTE: ориентир: LLM-часть не выше $0.30, верхней границы оценки аудита
   PROBLEM: Three ceilings exist for the same cost item. Section 4 expects $0.05-0.30 per investigation (25 model calls) and tests against $0.30; section 5 computes $0.40 typical and $0.57 heavy (106 and 158 calls); A5 sets a
   $0.45 limit. Section 4 notes the divergence itself, but Part A does not, and A8 п. 4 omits the comparison of the two routing schemes that section 4 requires. Section 5 is more likely right for the routing fixed in G13; $0.30
   belongs to the narrower «только эскалации» scheme.
   FIX: Section 4, п. 6: «…— ориентиры: не выше $0.30 для схемы «Sonnet 5.5 только на эскалациях» и не выше лимита на модели из A5 для схемы G13; расхождение в числе вызовов (25 в этой оценке, 106 в разделе 5) закрывается
   замером». A8 п. 4, add: «сравнение двух схем маршрутизации моделей по фактической стоимости».

[33] MAJOR | lens: consistency | location: раздел 8 «Почему выбрано», 4-й пункт; раздел 8 «Что проверить», 4-й пункт; против раздела 4 «Состояние проекта» (Pydantic AI)
   QUOTE: pydantic-ai 2.55.0 (MIT) имеет официальную durable-интеграцию с DBOS (extra `dbos>=2.10.0`) — тот же стек, что в G3.
   PROBLEM: Section 8 gives the official pydantic-ai/DBOS integration as a reason for the choice and plans to test it. Section 4 says `DBOSDurability` imports private DBOS modules, `DBOSAgent` is deprecated and «готовую интеграцию
   не используем». Section 4 is more likely right because it read the code. The reference «тот же стек, что в G3» is also wrong: G3 does not mention Pydantic AI.
   FIX: Replace the bullet with: «У pydantic-ai 2.55.0 есть durable-интеграция с DBOS (extra `dbos>=2.10.0`), но она импортирует приватные модули DBOS, а `DBOSAgent` помечен deprecated (раздел 4): готовую интеграцию не используем,
   запрос к модели оформляется обычным `@DBOS.step`.» In «Что проверить»: «Проверить один LLM-шаг через LLMClient внутри `@DBOS.step` (один запрос модели — один durable step)».

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

[48] MINOR | lens: consistency | location: раздел 1 «Заменяемость»; раздел 2 «Заменяемость»; раздел 3 «Заменяемость» и «Как проверяем качество»; A5; «Как читать»
   QUOTE: Интерфейс TransferHistoryProvider; вторая реализация — индекс стороннего оператора, не TronScan.
   PROBLEM: Key terms drift. The same interfaces are TransferHistoryProvider and LabelProvider in sections 1-2 but TransferSource and LabelSource in section 3. «Стандартное расследование» is about 40 addresses in section 1, 30 in
   section 3, 45 (heavy 60) in section 5 and «несколько десятков» in A5 and section 6. «Аудит» means the whole verified study in Part A, but in the sections it often means the unverified first-pass research («исходный аудит»,
   «первичный аудит», «тезис аудита опровергнут»), alongside «верификатор», «проверяющий», «перепроверка».
   FIX: Use TransferSource and LabelSource in sections 1 and 2. Define once in A5 and reuse: «стандартное расследование — 40–45 адресов (тяжёлое — 60)». Add to «Как читать»: «В части B «аудит» или «исходный аудит» — первичное
   исследование направления, «верификатор» — независимая перепроверка; там, где они расходятся, действует вывод верификатора.»

[57] MAJOR | lens: measurability | location: раздел 6, «Что проверить», критерии LH-GraphBench; также раздел 1 (пункт 1), раздел 4 (пункт 3), раздел 8 (проверка 8); A8, пункт 1
   QUOTE: граф на 1 000 адресов ≤ 5 мин; отчёт на несколько десятков адресов ≤ 2 мин
   PROBLEM: The same «1 000 адресов за 5 минут» is the pass criterion of four checks with different scope (TronGrid load run, DBOS spike, a mock-API load test, a graph-layer benchmark); none is end-to-end with real sources,
   verification receipts and model steps, so passing any of them does not establish criterion 3. The load profile is also undefined: with one worker and one shared limiter per provider, a 1,000-address job takes the whole TronGrid
   allowance while a 30-second job runs beside it.
   FIX: Add to A8: «Приёмочный замер критерия 3 один: сквозной прогон на тестовом сервере с реальными источниками, от постановки задачи до проверенного JSON-отчёта, по одной задаче одновременно, на наборе графов, зафиксированном
   до замера. Проверки в разделах 1, 4, 6 и 8 — бюджеты компонентов (источник, очередь, графовый слой), а не приёмка. Отдельно измеряется смешанная нагрузка: простая задача во время обхода графа на 1 000 адресов; для неё в
   ограничителе шлюза вводится приоритет интерактивных запросов.» In section 6 replace the quoted criteria with «графовый слой укладывается в свою долю бюджета времени, заданную до замера».

[59] MAJOR | lens: measurability | location: раздел 4, «Ограничения и риски», пункт «Бюджет $1»; A5, абзац после таблицы переменных затрат
   QUOTE: собственном ledger, проверяющем лимит до каждого платного вызова
   PROBLEM: A check before the call cannot hold a hard $1: a model call's cost is known only after the response, and the latency plan relies on parallel Haiku calls that can all pass the check at once and overshoot together. No
   reservation mechanism is described, and Pydantic AI's cost_limit fires after the overrun.
   FIX: Add: «Учёт бюджета работает как резервирование: перед вызовом в одной транзакции резервируется его максимальная стоимость (для модели — подсчитанные входные токены плюс max_tokens по цене выхода; для платного API — цена
   вызова), после ответа резерв заменяется фактом. Вызов не отправляется, если сумма фактов и резервов превышает лимит. Тест: 20 параллельных вызовов при остатке на 5 — отправлено не больше 5, итог не выше лимита.»

[60] MAJOR | lens: measurability | location: раздел 4, «Что проверить», пункт 6; A5 (лимит моделей $0.45); раздел 5, «Как проверяем качество», пункт «Бюджет-трекер»
   QUOTE: ориентир: LLM-часть не выше $0.30, верхней границы оценки аудита
   PROBLEM: Three incompatible model budgets: a Stage 2 threshold of $0.30 (section 4), a default limit of $0.45 (A5) and an expected spend of $0.40 typical and $0.57 heavy (section 5), so the typical estimate already fails the
   section 4 threshold. Behaviour at the limit also differs: pause (A5), PAUSED_BUDGET with resume (section 4), and «при 70% — только Haiku, при 100% — отчёт без LLM-текста» (section 5) without saying 70% of what.
   FIX: Section 4, item 6: «ориентир: LLM-часть не выше лимита моделей из A5 ($0.45); схема «Sonnet только на эскалациях» должна уложиться в $0.30». Section 5: «Бюджет-трекер: при 70% лимита моделей ($0.45 по умолчанию) — только
   Haiku; при 100% лимита моделей — отчёт без текста модели; при достижении общего лимита расследования — пауза PAUSED_BUDGET с сохранением результатов.»

[62] MAJOR | lens: measurability | location: A6, строка «Ключи не попадают в отчёты и журналы»; A7
   QUOTE: Секреты через SOPS и age; вырезание ключей в шлюзе; тест на утечку подставного ключа — обязательное условие сборки
   PROBLEM: Only one of the four security criteria has a row. Missing: no seed phrases or private keys, permission and control for agent actions that affect external systems (the registry has requires_approval, but no test, and
   the list of actions is deferred to owners in section 4 without an A7 question), and reporting the limitation when a source is unavailable (no test forces an outage and checks the report).
   FIX: Add three rows: «| Платформа не принимает и не хранит seed-фразы и приватные ключи | Полей для них нет в API и интерфейсе; входной фильтр отклоняет текст, похожий на seed-фразу или приватный ключ; тот же поиск по журналам,
   трассам и отчётам в CI — 0 совпадений | тест предстоит написать |», «| Действия агентов во внешних системах — только с разрешением | У каждого инструмента в реестре признак побочного эффекта и requires_approval; все инструменты
   MVP только читают; тест: вызов инструмента с побочным эффектом без записи об одобрении отклоняется и попадает в журнал | заложено в архитектуру; перечень действий утверждают владельцы |», «| При недоступности источника отчёт
   называет ограничение | Тест с принудительным отказом каждого провайдера: в отчёте есть запись об ограничении с именем источника и затронутыми адресами, зависящие выводы помечены как неполные | тест предстоит написать |». Add to
   A7: «Перечень действий агентов, для которых нужно одобрение человека.»

[70] MAJOR | lens: measurability | location: A8, вводный абзац и пункты 1, 3, 4, 5; раздел 4 (пункт 5), раздел 8 («Что проверить»), раздел 9 (пункты 1–3)
   QUOTE: Каждая закрывает конкретное «не измерено» из этого документа.
   PROBLEM: A8 lists what is measured but not what counts as a pass or what follows a failure, so the owners approve Stage 2 without go or no-go rules. Missing where clearly needed: a threshold for model refusals; one DBOS
   decision rule (section 4 says «если разница в надёжности не видна», section 8 says «при провале»); map thresholds that section 9 leaves to the owners but A7 never asks for; and what happens if 5 minutes is unreachable on the
   free TronGrid plan (section 3 says «пересмотр цели», a change to an owner criterion).
   FIX: Add «Критерий» and «При провале» to each A8 item, including: item 1 — «При провале цели 5 минут: индивидуальный план TronGrid или второй провайдер; изменение самой цели — только решением владельцев»; item 3 — «Критерий:
   вариант проходит все восемь проверок раздела 8; если проходят оба, берётся вариант без DBOS; если один — он»; item 4 — «Критерий: не менее 95% запусков заканчиваются корректным отчётом или понятной ошибкой; доля запусков, где
   из-за отказа модели отчёт вышел без её текста, — не выше порога владельцев (предложение: 10%). При провале: смена модели или режим без текста модели по умолчанию». Add to A7 question 12: «пороги приёмки карты: кадров в секунду
   на 1 000 узлов и предельное время раскладки (ориентир аудита — 30 кадров в секунду)».

[73] MINOR | lens: measurability | location: раздел 4, «Инфраструктура и затраты», пункт «Переменные (LLM-токены)»; также раздел 3 («Почему выбрано», пункт 3) и раздел 14 («Переменные»)
   QUOTE: Sonnet 5.5 на всех шагах дал бы $1.1–2.2, то есть выше лимита
   PROBLEM: $0.55 times 2-4 requests gives $1.1-2.2 without the +30% tokens named in the same sentence; with it the range is $1.4-2.9 (the Haiku figure «менее $0.15» does include both factors). Two similar slips: section 3 prices
   a MistTrack call at $0.03-0.20 but gives «30 адресов = $3-6», which matches $0.10-0.20, and section 14 quotes MistTrack at $0.10 per call although the A5 default is $0.20.
   FIX: Section 4: «Sonnet 5.5 на всех шагах дал бы $1.4–2.9, то есть выше лимита». Section 3: «вызов MistTrack стоит $0.10–0.20 на пакетах до 10 000 вызовов (30 адресов = $3–6)». Section 14: «MistTrack ($0.10–0.20 за вызов
   address_labels) учтён в разделе 2».

[74] MAJOR | lens: reader-safety | location: A7, opening line (and the whole list)
   QUOTE: Вопросы 1–8 блокируют начало Этапа 2; остальные можно закрыть по ходу.
   PROBLEM: Part B names at least nine further owner decisions that never appear in A7: IdP hosting and AGPL (s.10), where model traces live and ZDR (s.5), which actions need human approval (s.4), the graph-DB decision rule (s.6),
   young single-vendor library and a job-monitoring UI (s.8), FPS and hardware thresholds (s.9), a platform MCP server (s.11), eIDAS or PAdES (s.12), the confidence scale (s.2). An owner deciding from Part A will not know they
   exist.
   FIX: Add item 17 to A7 (defaults taken from A4/A5; author to confirm): «17. **Решения с вариантом по умолчанию** (если ответа нет, действует вариант по умолчанию; подробности — в конце разделов части B): поставщик входа — на
   своём сервере (Keycloak при 16 GB и более, иначе Logto после пробы) или внешний сервис; допустима ли лицензия AGPL (раздел 10). Журнал вызовов моделей — на своём сервере (по умолчанию) или в облаке ЕС (раздел 5). Действия,
   требующие подтверждения человеком: по умолчанию — любая отправка обращений (раздел 4). Правило ввода графовой СУБД (раздел 6). Готовый веб-интерфейс мониторинга задач: по умолчанию нет (раздел 8). Пороги плавности карты и
   целевое оборудование (раздел 9). Внешний MCP-интерфейс платформы: по умолчанию нет (раздел 11). Квалифицированная метка времени eIDAS или подпись PAdES: по умолчанию нет (раздел 12). Шкала достоверности меток (раздел 2).»

[81] MAJOR | lens: reader-safety | location: A9, last row
   QUOTE: Это следствие отсутствия готовых решений, а не выбор; заимствуются идеи и тесты из проектов под MIT
   PROBLEM: The stack departs from the owners' «свой код — только клей» principle (section 9 says so explicitly), but Part A mentions it only in the last risk row, defensively, with no size and no request for consent. Part B
   contains the estimates.
   FIX: Replace the row with: «| Объём собственного кода больше, чем принцип «свой код — только клей»: трассировщик, оркестратор, HTTP-шлюз с реестром инструментов, раскладка и сворачивание графа, хранилище меток. Сумма оценок
   разделов 2, 3, 4, 9 и 11 — порядка 10–15 человеко-недель (не измерено) | Готовых решений для этих частей не найдено; заимствуются идеи и тесты из проектов под MIT. Это отступление от принципа — прошу подтвердить его в вопросе 1
   |» and add to A7 question 1: «в том числе объём собственного кода из A9».

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
