# Review issues relevant to section(s) [12, 13] (reports-devops)

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

[17] MINOR | lens: owner-format | location: Section 13, 'Решение' (need m: monitoring); A1 row 13; A3
   QUOTE: сначала VictoriaLogs, Grafana Alloy, Grafana, GlitchTip и внешний heartbeat, затем VictoriaMetrics с vmalert и SLO-дашбордом
   PROBLEM: It is not stated when the second observability step lands or what sends alerts before vmalert exists. Metrics are absent from A1 and A3, and Gatus is 'предпочтён' in the alternatives table but not in the decision.
   FIX: «Наблюдаемость вводится в два шага. Шаг 1, к первому развёртыванию: VictoriaLogs, Grafana Alloy, Grafana, GlitchTip, внешний heartbeat и проверки доступности Gatus; оповещения в Telegram или e-mail — из Grafana и
   heartbeat. Шаг 2, до запуска production с клиентами: VictoriaMetrics с vmalert и SLO-дашбордом, включая долю успешного получения данных (цель ≥ 99%).» Подтвердить срок шага 2 и добавить VictoriaMetrics и Gatus в A1 (строка 13)
   и A3.

[19] MINOR | lens: owner-format | location: Part A, A9 (last row) and A5
   QUOTE: Объём собственного кода больше, чем «только клей»: трассировщик, раскладка и сворачивание графа, шлюз
   PROBLEM: The brief's strategy is not to build what already exists; the document admits the own code exceeds glue but never totals the effort. Estimates are scattered across sections 2, 3, 4, 6, 9 and 11, and sections 5, 7, 10,
   12 and 13 give none.
   FIX: Добавить в A5 абзац «Трудозатраты на собственный код (оценки аудита, не измерено)»: «трассировщик 2–3 человеко-недели; оркестратор, учёт бюджета и журнал 2–3; шлюз и реестр инструментов 1.5–2.5; интерфейс и карта 4–5
   (верификатор отдельно оценивает раскрытие ветвей, агрегацию, раскладку и экспорт в 3–4); Label Store 3–5 дней; тестовый набор меток 5–8 человеко-дней; стенд графового теста 1–2 недели. Итого около 12–18 человеко-недель; по
   адаптеру LLMClient, схеме БД, API, отчётам и эксплуатации оценки нет.»

[22] MINOR | lens: owner-format | location: Section 13, 'Инфраструктура и затраты' vs A5 (fixed costs, 'Минимум' column)
   QUOTE: Итого фиксированно в месяц: сервер €8.49 (бюджет считается без 12-месячной оплаты) + heartbeat $20 + B2 от $0 + домен
   PROBLEM: Section 13 budgets the $20 heartbeat as a fixed cost of the paid product and adds the domain; the A5 minimum shows $0 for monitoring and a total of '€8.5 + $49' with neither.
   FIX: A5, колонка «Минимум», строка «Мониторинг и журналы»: «$0 на своём сервере; внешний heartbeat healthchecks.io Business $20 — для платного продукта (раздел 13)». Строка «Итого», минимум: «около €8.5 + $49; для платного
   продукта плюс $20 heartbeat и домен около $1».

[28] MAJOR | lens: consistency | location: A5, таблица «Переменные, на стандартное расследование» и абзац под ней; раздел 5 «Инфраструктура и затраты», пункт о переменных
   QUOTE: | **Итого** | | **около $1.00** |
   PROBLEM: The default limits add up to $0.95-1.02 ($0.05 data + $0.40 labels + $0.45 models + $0.05 or $0.08 search + €0-0.04 timestamp). With Tavily and a commercial timestamp service, which section 12 says is budgeted for the
   paid product, the defaults exceed the owners' $1 cap. The next paragraph treats $0.57 on models as an allowed case although the model limit in the same table is $0.45, a figure that appears in no section. Section 5 also
   reserves «$0.10-0.25» for web search via Anthropic's built-in search, while A5, G15 and section 14 use 10 queries to Brave or Tavily for $0.05-0.08.
   FIX: Make the defaults sum to at most $1, for example a model limit of $0.40, and show the range: «**Итого** | | **$0.90–0.97; общий лимит $1 действует поверх постатейных**». Paragraph: «Запаса почти нет. Тяжёлый случай ($0.57
   на модели) превышает лимит на модели: при его достижении шаги переводятся на Haiku 5.5, а текст отчёта собирается без модели.» Section 5: «Из него $0.05–0.16 — веб-поиск: 10–20 запросов к Brave или Tavily через собственный
   адаптер (раздел 14, G15); встроенный поиск Anthropic не используется».

[34] MAJOR | lens: consistency | location: G14 (A4); раздел 10, таблица альтернатив (Keycloak) и «Ограничения и риски»; G12 против раздела 13 «Инфраструктура и затраты»
   QUOTE: на сервере с 8 GB, где уже работают база, воркер и мониторинг, не помещается с запасом; он уместен при 16 GB и более
   PROBLEM: G14 states as fact that Keycloak does not fit with margin on the 8 GB server. Section 10 says the memory figures come from documentation («не измерено»), «хватит ли памяти — не измерено», and its table calls Keycloak
   the «IdP при сервере от 8 GB RAM»; section 13 adds that the roughly 6 GB whole-stack estimate is unmeasured and excludes the IdP. The sections' caveat is right. Related: G12 and A5 call 16-24 GB the recommended start, while
   section 13 budgets production on the 8 GB VPS-2 and calls the 24 GB VPS-4 «путь роста».
   FIX: G14: «Keycloak по документации занимает 1.25–1.36 GB; поместится ли он на сервере с 8 GB рядом с базой, воркером и мониторингом, не измерено и проверяется пробой на Этапе 2; с запасом он уместен при 16 GB и более. Иначе —
   Logto, ZITADEL или внешний сервис.» Section 10 table: «IdP при сервере от 8 GB RAM» → «Кандидат IdP; на 8 GB — только после замера, с запасом — от 16 GB (G14)». Section 13: «Путь роста: OVH VPS-4» → «Рекомендуемая стартовая
   конфигурация по G12: OVH VPS-4».

[35] MAJOR | lens: consistency | location: A5, таблица постоянных затрат и абзац «Разовые расходы Этапа 2»; A1, строка 13; раздел 13 «Инфраструктура и затраты»
   QUOTE: | **Итого** | **около €8.5 + $49** | **около €20 + $69–200** |
   PROBLEM: Section 13 budgets healthchecks.io Business at $20 a month for the paid product (the free tier is «для разработки») and sums the fixed cost as server €8.49 + heartbeat $20 + B2 + domain (about $1). A5 puts the $20 only
   under «Рекомендуется» and omits the domain, so its minimum is about $21 below the section's own total; A1 row 13 shows only the server. The recommended column mixes a 12-month prepaid price with a no-commitment minimum. In the
   one-off list, the €21.73 stand is a 12-month-contract price, the $50-150 for control deposits already contains the MistTrack trial listed separately, and Bitquery Pro at $99 excludes the archive add-on that sections 2 and 3 say
   deep history needs ($198 a month). Section 13 is more likely right.
   FIX: Minimum, monitoring cell: «healthchecks.io Business: $20 (бесплатный тариф — только для разработки)». Totals: «около €8.5 + $70» and «около €20 (при оплате за 12 месяцев) + $70–200», with the note «включая домен около $1».
   A1 row 13: «сервер от €8.49/мес + $20 внешний контроль доступности». One-off list: «стенд замеров с выделенными ядрами €21.73/мес (цена при контракте на 12 месяцев)»; «Bitquery Pro $99–198 за месяц (с дополнением для архива)»;
   «контрольные депозиты на биржи … $50–150 (включая пробу MistTrack)».

[38] MAJOR | lens: consistency | location: A7 (вступительная фраза и список вопросов); разделы 4, 5, 6, 10, 12 «Что проверить» (решения владельцев); G10
   QUOTE: Вопросы 1–8 блокируют начало Этапа 2; остальные можно закрыть по ходу.
   PROBLEM: Sections put decisions on the owners that are not among A7's 16 questions: the identity provider (section 10: «конкретный IdP ждёт решения владельцев»), the rule for introducing a graph database (section 6: «требует
   согласия владельцев»), where model traces are kept (section 5, п. 9), a qualified timestamp or PAdES signature (section 12, п. 4), the actions that need human approval (section 4, п. 7), and Gotenberg, which G10 allows «только
   по вашему решению». Also, question 16 says the first-case data «нужны к началу Этапа 2» but is outside the blocking range 1-8.
   FIX: First sentence: «Вопросы 1–8 и 16 блокируют начало Этапа 2; остальные можно закрыть по ходу.» Add: «17. **Поставщик входа:** свой сервер или внешний сервис (учётные данные у третьей стороны); допустим ли AGPL (ZITADEL);
   нужны ли MFA и организации в MVP. 18. **Графовая СУБД:** принимаете ли правило «вводится только при выигрыше не менее чем в 3 раза либо если базовый вариант не укладывается в сроки»; нужны ли аналитикам запросы по всему
   накопленному графу. 19. **Трассы моделей:** Phoenix на своём сервере или Langfuse Cloud EU. 20. **Метка времени и подпись:** нужна ли квалифицированная метка (eIDAS) или подпись PAdES; допустим ли Gotenberg с Chromium как
   запасной движок PDF. 21. **Действия, требующие подтверждения человеком.**»

[39] MAJOR | lens: consistency | location: A2, п. 6; раздел 14 «Почему выбрано», последний пункт; раздел 12 «Состояние проекта», последний пункт; A10
   QUOTE: Возврат средств идёт только через правоохранительные органы.
   PROBLEM: Section 12 records the verifier's correction that this thesis is «слишком широк»: TRM Beacon Network claims access for vetted security companies, and its joining conditions are a Stage 2 check. Section 14 adds that
   Tether's cs.tether.to portal was not read. A2 п. 6 and section 14 still state the conclusion flatly; section 12's caveat is more likely right. Section 12 and A10 also say Tether's requirements page returned 404, while section
   14 quotes Tether's law-enforcement policy of 2018-01-03 as read.
   FIX: A2 п. 6: «**Для жертвы возврат средств идёт через правоохранительные органы.** На сайте Tether пути для жертвы не найдено (портал cs.tether.to не прочитан): запрос принимают от органа с правовым основанием. TRM Beacon
   Network заявляет доступ для проверенных security-компаний; условия вступления проверяются на Этапе 2.» Section 14: «Возврат идёт только через органы.» → «Для жертвы возврат идёт через органы.» In A10 and section 12, name which
   Tether page returned 404, since section 14 read the law-enforcement policy.

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

[51] MAJOR | lens: measurability | location: A6, строка «30 секунд / 2 минуты / 5 минут»; G11; раздел 12; A7
   QUOTE: PDF рендерится отдельной задачей вне этих сроков
   PROBLEM: The end of the measured interval («verified result») is never defined. PDF is taken out of the interval in a table cell, with no A7 question and no time limit of its own; the document does not say that the signed,
   time-stamped package then also falls outside (the package manifest contains the hash of report.pdf, section 12), nor whether model-written sections are inside.
   FIX: Replace the cell with: «Срок считается от постановки задачи до проверенного JSON-отчёта, показанного в интерфейсе: все рёбра сверены с квитанциями, отчёт прошёл схему. Вне срока — PDF, подпись Ed25519 и метка времени:
   манифест пакета включает хеш PDF, поэтому подписанный пакет готов только после рендера; его целевой срок утверждают владельцы (ориентир аудита — 20 с рендера на 5 000 строк). Сам срок зависит от скорости TronGrid с ключом,
   настроек очереди и задержки моделей.» Add a blocking question to A7: «Что считается результатом в сроках 30 с / 2 мин / 5 мин. Предложение: проверенный JSON-отчёт в интерфейсе; PDF и подписанный пакет — отдельной задачей со
   своим сроком. Входят ли в срок текстовые секции модели.»

[54] MAJOR | lens: measurability | location: раздел 13, «Как проверяем качество», последний пункт; A6, строка «30 секунд / 2 минуты / 5 минут»
   QUOTE: каждая цель измеряется не менее 5 раз, публикуются медиана и p95
   PROBLEM: Criterion 3 asks for time from task start to verified result, with waiting on external sources recorded separately, and at least 95% of completed tasks within the limit; no component is named that records either
   number. A p95 over five runs is just the maximum, and one miss in five is 80%, so five runs cannot show 95%.
   FIX: Replace with: «Протокол замеров: SKU, модель CPU, steal, sysbench, digest образов. Оркестратор пишет в журнал событий время постановки задачи и время появления проверенного отчёта; HTTP-шлюз суммирует по расследованию
   время ожидания внешних источников (ответ провайдера, ожидание в ограничителе, повторы) отдельным полем. Каждая цель измеряется не менее чем на 20 запусках; критерий — не менее 95% завершённых запусков в пределах лимита (не
   более одного превышения из 20); публикуются доля, медиана, максимум и доля времени ожидания источников.»

[56] MAJOR | lens: measurability | location: раздел 1, «Инфраструктура и затраты»; A2, пункт 3; раздел 3, «Инфраструктура и затраты»
   QUOTE: около 3 300 запросов TronGrid (11 rps в среднем за 300 с) и 3 000–4 000 к узлу
   PROBLEM: The count leaves out the per-TXID call to /v1/transactions/{txid}/events, which sections 3 and 6 name as the only source of event_index for the edge key, and it assumes about four verified edges per address although
   section 12 expects «тысячи и десятки тысяч строк TXID» in a 1,000-address report. Section 3 derives different numbers from the same total (10-16 graphs a day, 20-30 QPS) than A2 and section 1 (about 30 graphs, 11 rps).
   FIX: Replace the sentence in section 1 with: «Граф на 1 000 адресов, расчёт: история — около 1 300 запросов TronGrid; контекст энергии — ещё 2 000 (считается лениво); событие транзакции для ключа ребра — один запрос TronGrid на
   каждый TXID отчёта; квитанция — один запрос к узлу на каждый TXID. При E рёбрах в отчёте: TronGrid — около 1 300 + E, узел — около E. При E = 3 500 это 4 800 запросов TronGrid (16 rps за 300 с) и около 20 графов в сутки на
   квоте BASIC; при E = 20 000 — 71 rps и 4–5 графов в сутки, цель 5 минут на бесплатном плане по расчёту недостижима.» Bring A2 item 3 and section 3 («10-16 графов в день и около 20-30 QPS») to the same formula.

[58] MAJOR | lens: measurability | location: A5, таблица постоянных затрат, столбец «Минимум»; G12; раздел 13, пункт 1 «Что проверить»
   QUOTE: | **Итого** | **около €8.5 + $49** | **около €20 + $69–200** |
   PROBLEM: The «Минимум» column prices an 8 GB server together with a self-hosted login provider and self-hosted Phoenix at $0, which does not fit by the document's own figures: the roughly 6 GB stack estimate (unmeasured)
   excludes both, the login provider adds 0.5-1.4 GB, PDF rendering peaks at 0.2-0.5 GB, and section 6 wants five parallel investigations in RAM. The Stage 2 memory check has no numeric pass criterion.
   FIX: Add under the table: «Столбец «Минимум» по расчёту не проходит по памяти: оценка стека около 6 GB (не измерена) не включает поставщика входа (0.5–1.4 GB) и интерфейс трасс, а на 8 GB нужен ещё запас под рендер PDF (0.2–0.5
   GB) и параллельные расследования. На 8 GB поставщик входа и интерфейс трасс выносятся во внешние сервисы (плюс $0–129 в месяц); всё на своём сервере — только при 24 GB.» In section 13, check 1, add: «Критерий: пиковый суммарный
   RSS при пяти параллельных стандартных расследованиях и одном рендере PDF не выше 75% RAM; иначе эталон — 24 ГБ.»

[64] MAJOR | lens: measurability | location: A6, строка «≥ 95% точности меток»; раздел 12
   QUOTE: Независимый размеченный набор; источник метки не используется для её же проверки
   PROBLEM: The row covers one of the four exchange-identification criteria. The «separate evidence package for a potential exchange» is not described anywhere (only the general evidence zip and letter templates), and the other
   two (source, date and confidence on every classification; unknown addresses never called an exchange) have tests in sections 9 and 12 but no row here.
   FIX: Add three rows: «| У каждой классификации — источник, дата проверки, достоверность | Обязательные поля модели Pydantic: отчёт без них не сериализуется; тест схемы на всех сценариях | заложено в архитектуру |», «|
   Неизвестный адрес не называется биржей по косвенному сходству | Эвристика даёт только «кандидата»; тест на наборе hard negatives: 0 меток «биржа» без первичного источника или метки провайдера | набор предстоит собрать |», «|
   Отдельный пакет доказательств для потенциальной биржи | Для каждого адреса-кандидата формируется отдельный файл пакета: переводы на адрес с TXID и квитанциями, источник и дата метки, сырой ответ провайдера, хеши в манифесте;
   тест: число пакетов равно числу кандидатов в отчёте | предстоит спроектировать (раздел 12) |».

[71] MINOR | lens: measurability | location: A5, абзац «Разовые расходы Этапа 2»; A7, вопрос 6; раздел 13
   QUOTE: стенд замеров с выделенными ядрами €21.73/мес
   PROBLEM: Section 13 gives this price «при контракте на 12 месяцев», so the commitment is about €261, not a one-off monthly fee, and A7 question 6 presents the stand as optional although G12 runs all performance measurements on
   it and criterion 3 needs a fixed test server. The list has no total, and the $50-150 for control deposits already includes the $10 MistTrack trial listed separately (section 2).
   FIX: Replace with: «стенд замеров с выделенными ядрами €21.73/мес при контракте на 12 месяцев (обязательство около €261); он же — тестовый сервер для критерия 3. Итого без юриста, NOWNodes и внешнего хоста для сверки
   справочника: около $180–410 и €261.» A7 question 6: replace «нужен ли отдельный стенд для замеров» with «согласны ли вы оплатить стенд замеров (контракт на 12 месяцев, около €261): без него сроки из критерия 3 нельзя измерить
   воспроизводимо».

[74] MAJOR | lens: reader-safety | location: A7, opening line (and the whole list)
   QUOTE: Вопросы 1–8 блокируют начало Этапа 2; остальные можно закрыть по ходу.
   PROBLEM: Part B names at least nine further owner decisions that never appear in A7: IdP hosting and AGPL (s.10), where model traces live and ZDR (s.5), which actions need human approval (s.4), the graph-DB decision rule (s.6),
   young single-vendor library and a job-monitoring UI (s.8), FPS and hardware thresholds (s.9), a platform MCP server (s.11), eIDAS or PAdES (s.12), the confidence scale (s.2). An owner deciding from Part A will not know they
   exist.
   FIX: Add item 17 to A7 (defaults taken from A4/A5; author to confirm): «17. **Решения с вариантом по умолчанию** (если ответа нет, действует вариант по умолчанию; подробности — в конце разделов части B): поставщик входа — на
   своём сервере (Keycloak при 16 GB и более, иначе Logto после пробы) или внешний сервис; допустима ли лицензия AGPL (раздел 10). Журнал вызовов моделей — на своём сервере (по умолчанию) или в облаке ЕС (раздел 5). Действия,
   требующие подтверждения человеком: по умолчанию — любая отправка обращений (раздел 4). Правило ввода графовой СУБД (раздел 6). Готовый веб-интерфейс мониторинга задач: по умолчанию нет (раздел 8). Пороги плавности карты и
   целевое оборудование (раздел 9). Внешний MCP-интерфейс платформы: по умолчанию нет (раздел 11). Квалифицированная метка времени eIDAS или подпись PAdES: по умолчанию нет (раздел 12). Шкала достоверности меток (раздел 2).»

[80] MAJOR | lens: reader-safety | location: A2 item 6; also A1 row 14 and the title of section 14
   QUOTE: **Возврат средств идёт только через правоохранительные органы.** У Tether нет канала для жертвы
   PROBLEM: Stated as fact, but it rests on a 2018 policy, an unread portal (cs.tether.to) and a 404 page; section 12 itself says the thesis «слишком широк» because TRM Beacon Network claims access for vetted security companies.
   Separately, «каналы возврата средств» in A1 and the section 14 title can be read as the platform offering recovery channels.
   FIX: Replace item 6 with: «6. **Канала возврата для самой жертвы не найдено; найденные каналы рассчитаны на правоохранительные органы.** По опубликованной политике Tether (2018) запрос принимается от органа с правовым
   основанием; портал cs.tether.to не прочитан, страница требований отдаёт 404. TRM Beacon Network заявляет доступ для проверенных компаний по безопасности — условия не проверены. Реквизиты бирж первичными источниками не
   подтверждены: их сайты были недоступны из сети аудита. Платформа готовит пакет доказательств и черновики обращений; заморозку и возврат она не выполняет и не обещает.» Rename A1 row 14 to «OSINT и адресаты обращений» and
   section 14 (and the contents line) to «Источники OSINT и адресаты обращений о заморозке и возврате».

[85] MAJOR | lens: reader-safety | location: A7, question 6; A5 «Разовые расходы Этапа 2»
   QUOTE: **Сервер:** 8 GB или сразу 16–24 GB; готовность оплатить 12 месяцев вперёд; нужен ли отдельный стенд для замеров.
   PROBLEM: Three decisions without the recommendation that A5 and G12 already contain. G12 says measurements run on dedicated cores, so «нужен ли стенд» is not really open. A5 lists the stand as a one-off «€21.73/мес», but
   section 13 says that price requires a 12-month contract.
   FIX: Q6: «6. **Сервер.** Рекомендую сразу OVH VPS-4 (24 GB) с оплатой за 12 месяцев: €19.96/мес, около €240 за год. Альтернатива — 8 GB за €8.49/мес без обязательств, с риском нехватки памяти (A5, G12). Согласны? Отдельно: для
   замеров Этапа 2 нужен стенд с выделенными ядрами — €21.73/мес при контракте на 12 месяцев (около €261 за год); подтвердите или укажите, чем его заменить.» In A5: «стенд замеров с выделенными ядрами €21.73/мес при контракте на
   12 месяцев (цену проверить при заказе)».

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

[95] MINOR | lens: reader-safety | location: A7, questions 16 and 14
   QUOTE: **Данные первого кейса:** публичный адрес кошелька или TXID кражи. Нужны к началу Этапа 2.
   PROBLEM: Q16 says the data are needed at the start of Stage 2 but sits in the group that «можно закрыть по ходу», and it does not say that only public on-chain data are wanted. Q14 is a list of four topics with no proposal the
   owners could accept or amend.
   FIX: Q16: «16. **Данные первого кейса:** публичный адрес кошелька или TXID кражи — только данные из блокчейна, без личных данных жертвы. Нужны к началу построения базового трассировщика, то есть после измерений Этапа 2.» Q14:
   «14. **Сохранность данных.** Назовите: (а) сколько минут последних данных допустимо потерять при аварии и за какое время сервис должен быть восстановлен — если ответа нет, ориентиром станет результат пробного восстановления на
   Этапе 2; (б) срок хранения расследований; (в) нужно ли удаление по запросу клиента — оно конфликтует с неизменяемыми резервными копиями (раздел 13).»

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
