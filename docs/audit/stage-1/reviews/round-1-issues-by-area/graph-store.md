# Review issues relevant to section(s) [6] (graph-store)

[5] MAJOR | lens: owner-format | location: Section 6, 'Решение', 'Почему выбрано' and the alternatives table (need f: ML on graphs)
   QUOTE: Graph ML (PyTorch Geometric 2.8.1 + py-tgb 2.3.0) — только в изолированном экспериментальном контуре.
   PROBLEM: For the graph-ML sub-need, item 1 (why) is missing: 'Почему выбрано' gives no reason for PyTorch Geometric or py-tgb and no statement of what task the experimental contour solves. Item 2 has only one alternative (DGL);
   Raphtory is named in the licence paragraph but has no row.
   FIX: Добавить в «Почему выбрано» пункт: «Graph ML: задача экспериментального контура — [назвать: например, ранжирование адресов-кандидатов]. PyTorch Geometric 2.8.1 выбран как поддерживаемый фреймворк под MIT (релиз 2026-10-06,
   бинарники pyg_lib для torch 2.14.0); py-tgb — [назвать роль: загрузчики и протокол оценки на темпоральных графах]. Результат сравнивается с детерминированным baseline и не-графовым классификатором и в отчёт не попадает.» В
   таблицу альтернатив добавить строку: «Raphtory (graph ML и темпоральная аналитика) | GPL | допустим только при чистом SaaS; [причина отказа]».

[7] MAJOR | lens: owner-format | location: Section 3, 'Как проверяем качество', first bullet (contradicts A3, A6 and section 1)
   QUOTE: Каждое ребро отчёта подтверждается через /v1/transactions/{txid}/events лениво, только для рёбер, попавших в отчёт
   PROBLEM: Part A and section 1 promise that every reported fact is confirmed by a receipt from an operator other than TronGrid; section 3 confirms edges through TronGrid's own events endpoint, the same operator that supplied the
   history. Section 6 adds 'выборочная повторная сверка с первичным источником', which reads as sampling.
   FIX: Раздел 3: «Каждое ребро отчёта подтверждается receipt у оператора узла, отличного от TronGrid (раздел 1); event_index для ключа ребра берётся из /v1/transactions/{txid}/events. Обе проверки ленивые — только для рёбер,
   попавших в отчёт; идентичность ребра и фильтры — по G6.» Раздел 6, «Как проверяем качество»: заменить «выборочная повторная сверка с первичным источником» на «для рёбер отчёта — полная сверка по разделу 1, для остальных рёбер
   графа — выборочная».

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

[24] BLOCKER | lens: consistency | location: A2, п. 3; раздел 1 «Инфраструктура и затраты» (граф на 1 000 адресов); раздел 3 «Инфраструктура и затраты» (квота TronGrid)
   QUOTE: По расчёту такой граф требует 6–10 тысяч запросов, из них около 3 300 к TronGrid
   PROBLEM: A2 п. 3 and section 1 say a 1,000-address graph costs about 3,300 TronGrid requests (11 rps, about 30 graphs a day on the free quota). Section 3 charges all 6-10 thousand calls to the same quota: «10-16 графов в день и
   около 20-30 QPS для 5 минут». The gap equals the per-TXID calls to /v1/transactions/{txid}/events that G6 and section 6 need for the edge key and that section 1 does not count (3,300 + 3,000-4,000 edges = 6,300-7,300, i.e.
   14-16 graphs a day, 21-24 rps). Section 3 is more likely right for the design as written; section 1 holds only if event_index can be taken from the node receipt, which the document never says. Owners see the optimistic number
   for a headline MVP criterion.
   FIX: Decide where event_index comes from and use one set of numbers in all three places. A2 п. 3: «По расчёту такой граф требует 6–10 тысяч запросов. К TronGrid из них идёт от 3 300 (если индекс события удаётся брать из
   квитанции независимого узла) до 6–7 тысяч (если для каждого ребра нужен отдельный запрос событий транзакции у TronGrid). Суточной квоты бесплатного плана (100 000 запросов) хватает на 14–30 таких графов, а нужная скорость —
   11–24 запроса в секунду.» Put the same range into section 1 («около 3 300 запросов TronGrid…») and section 3 («6-10 тыс. вызовов…»).

[25] MAJOR | lens: consistency | location: G6 (A4); A8, п. 1; раздел 1 «Что проверить», п. 5; раздел 3 «Как проверяем качество», 1-й пункт; раздел 6 «Как проверяем качество», 1-й пункт
   QUOTE: наличие поля `event_index` в `/v1/transactions/{txid}/events` (нужно для идентичности ребра)
   PROBLEM: Section 1, G6 and A8 п. 1 treat the presence of event_index as unverified. Section 3 reports a live probe of 2026-10-13/14 in which this endpoint «отдаёт block_number и event_index», and section 6 cites a live URL for
   it; those two are more likely right. Separately, section 3 says each report edge «подтверждается через /v1/transactions/{txid}/events лениво» (TronGrid itself, report edges only), while G5, A3, A6 and section 1 require a
   receipt from an operator other than TronGrid, and section 6 needs event_index in the key of every stored edge, not lazily.
   FIX: G6, last sentence: «Поле event_index в живой пробе TronGrid присутствует (разделы 3 и 6); на Этапе 2 проверяются его стабильность и совпадение с позицией лога в квитанции независимого узла.» Section 1, п. 5: replace the
   quoted fragment with «стабильность `event_index` и его соответствие позиции лога в receipt (нужно для идентичности ребра)». Section 3 bullet: «Ключ ребра (event_index) берётся из /v1/transactions/{txid}/events при записи ребра;
   каждое ребро, попавшее в отчёт, дополнительно подтверждается receipt у оператора, отличного от TronGrid (раздел 1, G5); идентичность ребра и фильтры — по G6.» A8 п. 1: «Наличие и стабильность event_index» → «Стабильность
   event_index и его соответствие логам квитанции».

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

[56] MAJOR | lens: measurability | location: раздел 1, «Инфраструктура и затраты»; A2, пункт 3; раздел 3, «Инфраструктура и затраты»
   QUOTE: около 3 300 запросов TronGrid (11 rps в среднем за 300 с) и 3 000–4 000 к узлу
   PROBLEM: The count leaves out the per-TXID call to /v1/transactions/{txid}/events, which sections 3 and 6 name as the only source of event_index for the edge key, and it assumes about four verified edges per address although
   section 12 expects «тысячи и десятки тысяч строк TXID» in a 1,000-address report. Section 3 derives different numbers from the same total (10-16 graphs a day, 20-30 QPS) than A2 and section 1 (about 30 graphs, 11 rps).
   FIX: Replace the sentence in section 1 with: «Граф на 1 000 адресов, расчёт: история — около 1 300 запросов TronGrid; контекст энергии — ещё 2 000 (считается лениво); событие транзакции для ключа ребра — один запрос TronGrid на
   каждый TXID отчёта; квитанция — один запрос к узлу на каждый TXID. При E рёбрах в отчёте: TronGrid — около 1 300 + E, узел — около E. При E = 3 500 это 4 800 запросов TronGrid (16 rps за 300 с) и около 20 графов в сутки на
   квоте BASIC; при E = 20 000 — 71 rps и 4–5 графов в сутки, цель 5 минут на бесплатном плане по расчёту недостижима.» Bring A2 item 3 and section 3 («10-16 графов в день и около 20-30 QPS») to the same formula.

[57] MAJOR | lens: measurability | location: раздел 6, «Что проверить», критерии LH-GraphBench; также раздел 1 (пункт 1), раздел 4 (пункт 3), раздел 8 (проверка 8); A8, пункт 1
   QUOTE: граф на 1 000 адресов ≤ 5 мин; отчёт на несколько десятков адресов ≤ 2 мин
   PROBLEM: The same «1 000 адресов за 5 минут» is the pass criterion of four checks with different scope (TronGrid load run, DBOS spike, a mock-API load test, a graph-layer benchmark); none is end-to-end with real sources,
   verification receipts and model steps, so passing any of them does not establish criterion 3. The load profile is also undefined: with one worker and one shared limiter per provider, a 1,000-address job takes the whole TronGrid
   allowance while a 30-second job runs beside it.
   FIX: Add to A8: «Приёмочный замер критерия 3 один: сквозной прогон на тестовом сервере с реальными источниками, от постановки задачи до проверенного JSON-отчёта, по одной задаче одновременно, на наборе графов, зафиксированном
   до замера. Проверки в разделах 1, 4, 6 и 8 — бюджеты компонентов (источник, очередь, графовый слой), а не приёмка. Отдельно измеряется смешанная нагрузка: простая задача во время обхода графа на 1 000 адресов; для неё в
   ограничителе шлюза вводится приоритет интерактивных запросов.» In section 6 replace the quoted criteria with «графовый слой укладывается в свою долю бюджета времени, заданную до замера».

[58] MAJOR | lens: measurability | location: A5, таблица постоянных затрат, столбец «Минимум»; G12; раздел 13, пункт 1 «Что проверить»
   QUOTE: | **Итого** | **около €8.5 + $49** | **около €20 + $69–200** |
   PROBLEM: The «Минимум» column prices an 8 GB server together with a self-hosted login provider and self-hosted Phoenix at $0, which does not fit by the document's own figures: the roughly 6 GB stack estimate (unmeasured)
   excludes both, the login provider adds 0.5-1.4 GB, PDF rendering peaks at 0.2-0.5 GB, and section 6 wants five parallel investigations in RAM. The Stage 2 memory check has no numeric pass criterion.
   FIX: Add under the table: «Столбец «Минимум» по расчёту не проходит по памяти: оценка стека около 6 GB (не измерена) не включает поставщика входа (0.5–1.4 GB) и интерфейс трасс, а на 8 GB нужен ещё запас под рендер PDF (0.2–0.5
   GB) и параллельные расследования. На 8 GB поставщик входа и интерфейс трасс выносятся во внешние сервисы (плюс $0–129 в месяц); всё на своём сервере — только при 24 GB.» In section 13, check 1, add: «Критерий: пиковый суммарный
   RSS при пяти параллельных стандартных расследованиях и одном рендере PDF не выше 75% RAM; иначе эталон — 24 ГБ.»

[74] MAJOR | lens: reader-safety | location: A7, opening line (and the whole list)
   QUOTE: Вопросы 1–8 блокируют начало Этапа 2; остальные можно закрыть по ходу.
   PROBLEM: Part B names at least nine further owner decisions that never appear in A7: IdP hosting and AGPL (s.10), where model traces live and ZDR (s.5), which actions need human approval (s.4), the graph-DB decision rule (s.6),
   young single-vendor library and a job-monitoring UI (s.8), FPS and hardware thresholds (s.9), a platform MCP server (s.11), eIDAS or PAdES (s.12), the confidence scale (s.2). An owner deciding from Part A will not know they
   exist.
   FIX: Add item 17 to A7 (defaults taken from A4/A5; author to confirm): «17. **Решения с вариантом по умолчанию** (если ответа нет, действует вариант по умолчанию; подробности — в конце разделов части B): поставщик входа — на
   своём сервере (Keycloak при 16 GB и более, иначе Logto после пробы) или внешний сервис; допустима ли лицензия AGPL (раздел 10). Журнал вызовов моделей — на своём сервере (по умолчанию) или в облаке ЕС (раздел 5). Действия,
   требующие подтверждения человеком: по умолчанию — любая отправка обращений (раздел 4). Правило ввода графовой СУБД (раздел 6). Готовый веб-интерфейс мониторинга задач: по умолчанию нет (раздел 8). Пороги плавности карты и
   целевое оборудование (раздел 9). Внешний MCP-интерфейс платформы: по умолчанию нет (раздел 11). Квалифицированная метка времени eIDAS или подпись PAdES: по умолчанию нет (раздел 12). Шкала достоверности меток (раздел 2).»

[75] MAJOR | lens: reader-safety | location: A7, question 11
   QUOTE: **Горячие кошельки бирж:** остановка на помеченной границе или лимит страниц на адрес; пороги по умолчанию (минимальная сумма, окно транзита).
   PROBLEM: Cannot be answered as asked. The problem is not stated, the two options are presented as either/or although sections 1 and 6 say both are needed, and the owner is asked for thresholds («минимальная сумма», «окно
   транзита») that appear nowhere else in the document and have no proposed values.
   FIX: Replace with: «11. **Трассировка через кошельки бирж.** Горячий кошелёк биржи принимает тысячи переводов в час; пролистать его историю целиком нельзя, а проследить средства дальше него нельзя по смыслу. Предлагаю:
   трассировка останавливается на адресе с меткой биржи (в отчёте — «переведено на опубликованный кошелёк биржи»); для непомеченных адресов с очень большой историей действует лимит страниц на адрес, ветвь помечается как усечённая.
   Согласны? Числовые пороги (минимальная сумма ветви, окно времени транзита) я предложу по итогам замеров Этапа 2; сейчас значения от вас не нужны.»

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
