# Review issues relevant to section(s) [3] (tracing-engines)

[7] MAJOR | lens: owner-format | location: Section 3, 'Как проверяем качество', first bullet (contradicts A3, A6 and section 1)
   QUOTE: Каждое ребро отчёта подтверждается через /v1/transactions/{txid}/events лениво, только для рёбер, попавших в отчёт
   PROBLEM: Part A and section 1 promise that every reported fact is confirmed by a receipt from an operator other than TronGrid; section 3 confirms edges through TronGrid's own events endpoint, the same operator that supplied the
   history. Section 6 adds 'выборочная повторная сверка с первичным источником', which reads as sampling.
   FIX: Раздел 3: «Каждое ребро отчёта подтверждается receipt у оператора узла, отличного от TronGrid (раздел 1); event_index для ключа ребра берётся из /v1/transactions/{txid}/events. Обе проверки ленивые — только для рёбер,
   попавших в отчёт; идентичность ребра и фильтры — по G6.» Раздел 6, «Как проверяем качество»: заменить «выборочная повторная сверка с первичным источником» на «для рёбер отчёта — полная сверка по разделу 1, для остальных рёбер
   графа — выборочная».

[11] MAJOR | lens: owner-format | location: Section 3, 'Лицензия и коммерческое использование' (contradicts section 2)
   QUOTE: Условия коммерческого использования и кэширования у MistTrack и Arkham в документации не найдены — нужны письменные.
   PROBLEM: Section 2 states that MistTrack's Terms of Use of 2026-10-09 explicitly allow client PDF reports, commercial investigations and caching; section 3 says no such terms were found. Owners get two opposite answers to item
   3 for the same paid provider.
   FIX: «Условия MistTrack разобраны в разделе 2: Terms of Use от 2026-10-09 разрешают клиентские отчёты, коммерческие расследования и кэширование, но до начала коммерческого использования возможны KYB и проверка бизнес-модели. У
   Arkham условия коммерческого использования и кэширования в документации не найдены — нужны письменные.»

[16] MAJOR | lens: owner-format | location: Section 3, 'Инфраструктура и затраты' (contradicts A2 item 3 and section 1)
   QUOTE: 6-10 тыс. вызовов на граф из 1 000 адресов, то есть 10-16 графов в день и около 20-30 QPS для 5 минут
   PROBLEM: Section 3 charges all 6-10 thousand calls to the TronGrid daily quota (10-16 graphs a day, 20-30 QPS); A2 and section 1 say only about 3 300 of them go to TronGrid (about 30 graphs a day, 11 rps). Owners see two
   capacity figures for the same free plan.
   FIX: «Расчётная оценка, не измерено: 6–10 тыс. вызовов на граф из 1 000 адресов, из них около 3 300 к TronGrid (раздел 1); суточной квоты хватает примерно на 30 таких графов, средняя нагрузка на TronGrid — около 11 запросов в
   секунду при сроке 5 минут.» Если верна оценка раздела 3, исправить A2 (пункт 3) и раздел 1.

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

[26] MAJOR | lens: consistency | location: раздел 3 «Лицензия и коммерческое использование», 4-й пункт; раздел 3 «Что проверить», пункт про Arkham и MistTrack
   QUOTE: Условия коммерческого использования и кэширования у MistTrack и Arkham в документации не найдены — нужны письменные.
   PROBLEM: Section 2 reads MistTrack's Terms of Use of 2026-10-09 as the most explicit permission among vendors: client PDF reports, commercial investigations and caching are allowed, resale as a standalone data product is not,
   and a Commercial Use Review may be required. Section 3 says such terms were not found at all. Section 2 is more likely right: it cites the dated document and its URL, and A1 and G7 rely on its reading.
   FIX: Replace with: «Terms of Use MistTrack от 2026-10-09 разрешают клиентские отчёты, коммерческие расследования и кэширование (раздел 2); письменно остаётся подтвердить прохождение Commercial Use Review и экспорт меток в JSON-
   отчёт. У Arkham условия коммерческого использования и кэширования в документации не найдены — нужны письменные.» In «Что проверить»: «MistTrack: письменные условия коммерческого использования» → «MistTrack: Commercial Use
   Review по разделу 2».

[29] MAJOR | lens: consistency | location: раздел 2 «Решение»; раздел 3 «Инфраструктура и затраты» и «Почему выбрано»; раздел 14 «Инфраструктура и затраты»; G7; A5
   QUOTE: При 2-4 адресах (G7) и пакетах на 100-1 000 вызовов ($0.15-0.20) это расчётно $0.30-0.80 на расследование
   PROBLEM: G7, A5 and A7 (вопрос 5) set a default of 2 paid calls, up to $0.40. Sections 2 and 3 plan «2–4» calls, and section 3 attributes that range to G7; at 4 calls ($0.80) the $1 budget cannot hold. Part A's default of 2 is
   the later, budget-driven decision. The price per call also differs: section 14 says «$0.10 за вызов address_labels», which per section 2 and A5 applies only to the $1,000 pack ($0.20 on the $20 pack the plan starts with).
   Section 3 says «$0.03-0.20 (30 адресов = $3-6)», but $0.03 × 30 is $0.90.
   FIX: Section 2: «…с оплатой за вызов; лимит по умолчанию — 2 терминальных адреса на расследование (G7), настраивается до 4». Section 3: «При лимите по умолчанию в 2 вызова (G7) и пакетах на 100–1 000 вызовов ($0.15–0.20) это
   расчётно $0.30–0.40 на расследование; при 4 вызовах — до $0.80». Section 3, «Почему выбрано»: «(30 адресов = $0.90–6)». Section 14: «MistTrack ($0.10–0.20 за вызов address_labels в зависимости от пакета) учтён в разделе 2».

[35] MAJOR | lens: consistency | location: A5, таблица постоянных затрат и абзац «Разовые расходы Этапа 2»; A1, строка 13; раздел 13 «Инфраструктура и затраты»
   QUOTE: | **Итого** | **около €8.5 + $49** | **около €20 + $69–200** |
   PROBLEM: Section 13 budgets healthchecks.io Business at $20 a month for the paid product (the free tier is «для разработки») and sums the fixed cost as server €8.49 + heartbeat $20 + B2 + domain (about $1). A5 puts the $20 only
   under «Рекомендуется» and omits the domain, so its minimum is about $21 below the section's own total; A1 row 13 shows only the server. The recommended column mixes a 12-month prepaid price with a no-commitment minimum. In the
   one-off list, the €21.73 stand is a 12-month-contract price, the $50-150 for control deposits already contains the MistTrack trial listed separately, and Bitquery Pro at $99 excludes the archive add-on that sections 2 and 3 say
   deep history needs ($198 a month). Section 13 is more likely right.
   FIX: Minimum, monitoring cell: «healthchecks.io Business: $20 (бесплатный тариф — только для разработки)». Totals: «около €8.5 + $70» and «около €20 (при оплате за 12 месяцев) + $70–200», with the note «включая домен около $1».
   A1 row 13: «сервер от €8.49/мес + $20 внешний контроль доступности». One-off list: «стенд замеров с выделенными ядрами €21.73/мес (цена при контракте на 12 месяцев)»; «Bitquery Pro $99–198 за месяц (с дополнением для архива)»;
   «контрольные депозиты на биржи … $50–150 (включая пробу MistTrack)».

[36] MAJOR | lens: consistency | location: раздел 14 «Как проверяем качество», 2-й пункт; A6, строка «≥ 50 сценариев»; раздел 3 «Как проверяем качество» (Сценарии)
   QUOTE: Адреса из OFAC SDN и из событий AddedBlackList входят в тестовый набор как ground truth: не менее 10 из 50 сценариев
   PROBLEM: A6 and section 3 count only synthetic-exact and self-generated scenarios toward the required 50 and keep freeze-anchored cases as a separate class. Section 14 counts at least 10 sanction and freeze cases inside the 50.
   A6 and section 3 agree with each other and are more likely right. A6 also says the self-made scenarios are created «в тестовой сети», while no section mentions a test network (sections 2 and 3 speak of own transfers and
   deposits with TXID).
   FIX: Section 14: «Адреса из OFAC SDN и из событий AddedBlackList образуют отдельный класс сценариев (не менее 10 кейсов) для измерения precision и recall; в 50 сценариев с точно известным ответом они не засчитываются (раздел 3,
   A6).» A6: «созданные нами в тестовой сети» → «созданные нами собственными переводами» (or name the test network in section 3 if that is the plan).

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

[47] MINOR | lens: consistency | location: раздел 3 «Как проверяем качество», последний пункт; раздел 2 «Как проверяем качество» и «Инфраструктура и затраты»; A2, п. 4
   QUOTE: Тест меток: >= 300 адресов из независимых источников с отрицательным классом и доверительным интервалом; 10-15 контрольных депозитов
   PROBLEM: The same label test set has three sizes: section 2 plans 600+ addresses and prices 400-500, while section 3 requires ≥ 300. Own deposit addresses are 10-30 in section 2 and A2 п. 4 but 10-15 in section 3. Section 2 is
   the dedicated section and more likely right.
   FIX: Section 3: «Тест меток — независимый набор из раздела 2 (первая версия 400–500 адресов, цель 600+) с отрицательным классом и доверительным интервалом; 10–30 контрольных депозитов дают нижнюю границу не выше 88.6% и цель не
   доказывают.»

[48] MINOR | lens: consistency | location: раздел 1 «Заменяемость»; раздел 2 «Заменяемость»; раздел 3 «Заменяемость» и «Как проверяем качество»; A5; «Как читать»
   QUOTE: Интерфейс TransferHistoryProvider; вторая реализация — индекс стороннего оператора, не TronScan.
   PROBLEM: Key terms drift. The same interfaces are TransferHistoryProvider and LabelProvider in sections 1-2 but TransferSource and LabelSource in section 3. «Стандартное расследование» is about 40 addresses in section 1, 30 in
   section 3, 45 (heavy 60) in section 5 and «несколько десятков» in A5 and section 6. «Аудит» means the whole verified study in Part A, but in the sections it often means the unverified first-pass research («исходный аудит»,
   «первичный аудит», «тезис аудита опровергнут»), alongside «верификатор», «проверяющий», «перепроверка».
   FIX: Use TransferSource and LabelSource in sections 1 and 2. Define once in A5 and reuse: «стандартное расследование — 40–45 адресов (тяжёлое — 60)». Add to «Как читать»: «В части B «аудит» или «исходный аудит» — первичное
   исследование направления, «верификатор» — независимая перепроверка; там, где они расходятся, действует вывод верификатора.»

[52] MAJOR | lens: measurability | location: A6, строка «Показатели AI-слоя; превосходство над базовым алгоритмом»; раздел 14, последний пункт «Что проверить»; раздел 3, последний пункт «Что проверить»
   QUOTE: подзадачи, где ожидается выигрыш, фиксируются заранее | количественных подтверждений нет ни у кого на рынке
   PROBLEM: Five AI criteria are collapsed into one row with no thresholds and no scorer: nothing says how the 90% of conclusions with references is counted, what a correct run is for the 95% criterion, or what detects a forbidden
   claim (money recovered, owner identified, exchange confirmed). For «better than baseline» there is no metric, threshold or consequence, and section 14 moves a component that shows no gain «вне MVP-метрик», which silently turns
   an owner criterion into an optional one; the status cell is market commentary, not a status.
   FIX: Replace the row with four rows: «| ≥ 90% существенных выводов агентов со ссылкой или пометкой «гипотеза» | Каждый вывод — запись типа «факт» или «гипотеза» со списком ссылок; детерминированный scorer считает по журналу
   прогона долю записей с непустыми ссылками или типом «гипотеза» | заложено в архитектуру; не измерено |», «| ≥ 95% запусков заканчиваются корректным отчётом или понятной ошибкой | Запуск засчитан, если отчёт прошёл JSON Schema и
   проверку доказательств либо завершился записью ошибки с кодом и текстом для пользователя; считает оркестратор по статусам прогонов | не измерено; доля отказов моделей неизвестна |», «| Все действия агентов в журнале; нет
   заявлений «деньги возвращены», «владелец установлен», «биржа подтверждена» без доказательств | Число записей журнала равно числу вызовов шлюза и LLMClient; пост-валидатор отчёта и писем отклоняет утверждения этих трёх классов
   без ссылки на доказательство; тест на провокационных сценариях: 0 пропусков | scorer предстоит написать |», «| AI лучше базового алгоритма по скорости или полноте | Парное сравнение на одном наборе, 3–5 прогонов; метрика —
   полнота найденных конечных адресов при одинаковом лимите бюджета; порог — прирост больше нуля с 95%-м доверительным интервалом. Выигрыша по скорости не ожидаем: модель добавляет задержку | не измерено; риск невыполнения высокий
   |». In section 14 replace «иначе модуль остаётся отключаемым и вне MVP-метрик» with «иначе модуль отключается, а результат сравнения остаётся в отчёте о метриках как невыполненный пункт критерия».

[53] MAJOR | lens: measurability | location: A6, строка «≥ 99% успешного получения данных»; раздел 1 («Как проверяем качество», пункт 1 «Что проверить»); раздел 3 («Что проверить»)
   QUOTE: Повторы и резервный узел; выборочная сверка полноты со вторым независимым индексом; ежедневная контрольная проверка
   PROBLEM: The owner metric is the share of supported, available test transactions whose data were retrieved, but the document uses «99%» for three other things: successful HTTP responses in a load run (section 1, check 1),
   completeness of an address history against a second index (section 1), and agreement on a sample of addresses (section 3). None has a numerator and denominator, and the A6 status ties the criterion to a second index the owner
   metric does not need.
   FIX: Replace the cell with: «Метрика: доля TXID тестового набора, для которых платформа получила и проверила квитанцию и события Transfer (числитель — TXID со статусом «проверено», знаменатель — все поддерживаемые и
   существующие TXID набора); считает проверка доказательств по журналу шлюза. Отдельно публикуются доля успешных HTTP-ответов по провайдерам и полнота истории адреса против второго индекса — это дополнительные метрики, в 99% они
   не входят.» Status: «не измерено; для основной метрики второй индекс не нужен».

[56] MAJOR | lens: measurability | location: раздел 1, «Инфраструктура и затраты»; A2, пункт 3; раздел 3, «Инфраструктура и затраты»
   QUOTE: около 3 300 запросов TronGrid (11 rps в среднем за 300 с) и 3 000–4 000 к узлу
   PROBLEM: The count leaves out the per-TXID call to /v1/transactions/{txid}/events, which sections 3 and 6 name as the only source of event_index for the edge key, and it assumes about four verified edges per address although
   section 12 expects «тысячи и десятки тысяч строк TXID» in a 1,000-address report. Section 3 derives different numbers from the same total (10-16 graphs a day, 20-30 QPS) than A2 and section 1 (about 30 graphs, 11 rps).
   FIX: Replace the sentence in section 1 with: «Граф на 1 000 адресов, расчёт: история — около 1 300 запросов TronGrid; контекст энергии — ещё 2 000 (считается лениво); событие транзакции для ключа ребра — один запрос TronGrid на
   каждый TXID отчёта; квитанция — один запрос к узлу на каждый TXID. При E рёбрах в отчёте: TronGrid — около 1 300 + E, узел — около E. При E = 3 500 это 4 800 запросов TronGrid (16 rps за 300 с) и около 20 графов в сутки на
   квоте BASIC; при E = 20 000 — 71 rps и 4–5 графов в сутки, цель 5 минут на бесплатном плане по расчёту недостижима.» Bring A2 item 3 and section 3 («10-16 графов в день и около 20-30 QPS») to the same formula.

[65] MAJOR | lens: measurability | location: раздел 14, «Как проверяем качество», пункт 2; раздел 8, «Как проверяем качество», первая строка; A6, последняя строка; раздел 3
   QUOTE: не менее 10 из 50 сценариев для измерения precision и recall
   PROBLEM: A6 and section 3 say only synthetic-exact and self-generated scenarios count toward the 50 and freeze-anchored cases are a separate class, but section 14 puts at least 10 OFAC and blacklist scenarios inside the 50 and
   section 8 says its eight crash and limit checks «войдут в набор из 50+ сценариев». Counted that way about 32 tracing scenarios remain, and section 3 admits the current design yields only 25+.
   FIX: Section 14: «Адреса из OFAC SDN и из событий AddedBlackList входят в отдельный класс freeze-anchored — не менее 10 сценариев сверх 50 — для измерения precision и recall.» Section 8: «Критерии spike; они же войдут в
   регрессионные тесты надёжности, отдельно от 50 сценариев трассировки:». A6, last row, add: «Сейчас спроектировано 25+ засчитываемых сценариев; нужно ещё не менее 25 и итоговый набор.»

[67] MAJOR | lens: measurability | location: A4, G6; раздел 1, «Что проверить», пункт 5
   QUOTE: Наличие и стабильность поля event_index проверяется на Этапе 2.
   PROBLEM: The edge key, and with it the «no duplicate transactions» criterion, depends on this field, but the check has no pass criterion and no fallback. Section 3 reports the field present in single probes only.
   FIX: Replace with: «Проверка на Этапе 2: на выборке не менее 1 000 TXID, включая транзакции с несколькими Transfer, поле event_index есть у 100% событий, не меняется при повторном запросе через 24 часа и совпадает с порядковым
   номером лога в квитанции независимого узла. При провале ключом ребра становится (chain, txid, порядковый номер лога в квитанции узла).»

[69] MAJOR | lens: measurability | location: раздел 2, «Как проверяем качество» и «Инфраструктура и затраты»; раздел 3, «Как проверяем качество»; A5, разовые расходы; A7, вопрос 7
   QUOTE: Независимый тестовый набор на 600+ адресов, истина не из проверяемых источников
   PROBLEM: The label test set has four sizes: 600+ here, at least 300 in section 3, 400 in the threshold example, and a cost estimate ($50-150, 5-8 person-days) stated for 400-500 with 600+ «не измерено». The MistTrack probe is
   budgeted at $10-20, but a $20 package is 100 calls, and A7 does not say who opens the exchange accounts needed for control deposits.
   FIX: Set one size: «Независимый тестовый набор первой версии — 400 адресов (порог: 389 верных положительных меток из 400 по нижней границе Wilson); расширение до 600+ — после Этапа 2.» A5: «проба MistTrack $10–20 (до 100
   адресов) либо пакет $150 на 1 000 вызовов для всего набора». A7 question 7, add: «и аккаунты на биржах для контрольных депозитов (нужна верификация личности владельца аккаунта)».

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

[90] MAJOR | lens: reader-safety | location: Section 3, «Лицензия и коммерческое использование» (contradicts section 2)
   QUOTE: Условия коммерческого использования и кэширования у MistTrack и Arkham в документации не найдены — нужны письменные.
   PROBLEM: Section 2 says the MistTrack Terms of Use of 2026-10-09 were read and explicitly allow client reports and caching; section 3 says no such terms were found. The owner gets two opposite readings of the terms of the only
   paid data source in the stack.
   FIX: Replace with: «Условия MistTrack прочитаны (раздел 2): по нашему прочтению, отчёты для клиентов и кэширование разрешены, перепродажа данных запрещена, до коммерческого использования возможна проверка бизнес-модели — нужно
   письменное подтверждение. У Arkham условия коммерческого использования и кэширования в документации не найдены — нужны письменные.»

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

[94] MINOR | lens: reader-safety | location: Section 3, «Инфраструктура и затраты» (contradicts A2 item 3 and section 1)
   QUOTE: 6-10 тыс. вызовов на граф из 1 000 адресов, то есть 10-16 графов в день и около 20-30 QPS для 5 минут
   PROBLEM: A2.3 and section 1 say the free daily quota covers «примерно 30» such graphs at about 11 rps (3 300 TronGrid requests per graph); section 3 says 10–16 graphs and 20–30 QPS from the same 6–10 thousand calls. A reader
   checking A2.3 against Part B finds two different answers.
   FIX: Replace with: «Расчётная оценка, не измерено: 6–10 тыс. вызовов на граф из 1 000 адресов, из них около 3 300 к TronGrid (раздел 1) — суточной квоты хватает примерно на 30 графов при 11 запросах в секунду; если бы все
   вызовы шли в TronGrid, квоты хватало бы на 10–16 графов при 20–30 запросах в секунду.»

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
