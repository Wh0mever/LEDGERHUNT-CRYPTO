# Review issues relevant to section(s) [1] (tron-data)

[3] MAJOR | lens: owner-format | location: Section 1, 'Решение' (need a: transactions, token transfers, balances, timestamps, contracts)
   QUOTE: Основной источник истории TRC20, событий контракта и internal transactions — TronGrid v1 с собственным API key (план BASIC).
   PROBLEM: Balances and contracts are required data types in the brief but are covered only in passing (balanceOf 'latest only', an unbuilt contract registry). The section never states the chosen source for current balance, how
   historical balance is derived, or how the platform tells that an address is a contract.
   FIX: Добавить после «Решения» абзац «Покрытие видов данных Промпта 0»: «Транзакции — receipt `/walletsolidity/gettransactioninfobyid` у оператора узла, отличного от TronGrid. Переводы токенов — TronGrid
   `/v1/accounts/{address}/transactions/trc20`; индекс события — `/v1/transactions/{txid}/events`. Балансы — текущий `balanceOf` через constant call у независимого узла (только latest); исторический баланс источники не отдают, он
   восстанавливается по полной истории переводов с учётом DestroyedBlackFunds, Issue и Redeem, а при неполной истории в отчёте стоит „баланс на дату недоступен“. Время — block_timestamp строки истории, сверяется с блоком в
   receipt; в отчёт идут только solidified-данные. Контракты — события через `/v1/contracts/{address}/events`; признак „адрес — контракт“ и сведения о контракте — через эндпоинт узла (кандидат `wallet/getcontract`, в аудите не
   проверялся, проверка на Этапе 2); реестр контрактов обменников и мостов — собственный (пункт 6 ниже).»

[4] MAJOR | lens: owner-format | location: Section 2, 'Решение' and 'Ограничения и риски' (need b: exchanges, exchangers, bridges, services)
   QUOTE: Не покрыто открытыми источниками: операционные hot wallets вне PoR, OTC, P2P-мерчанты, обменники СНГ.
   PROBLEM: The brief asks for label sources for exchanges, exchangers, bridges and services; section 2 chooses sources only for exchanges and sanctions or freezes. The contract registry for exchangers and bridges is mentioned in
   A3, A8 and section 1 but is not part of the section 2 decision and has no named source, cost or quality check.
   FIX: Добавить в «Решение» раздела 2: «Четвёртый локальный источник — курируемый реестр контрактов обменников (DEX), мостов и сервисов (SunSwap, JustLend, мосты): адрес, тип, источник записи, дата проверки, confidence;
   собирается до старта трассировщика (раздел 1, пункт 6). Для централизованных обменников, OTC и P2P-сервисов открытого источника нет: в MVP их метку даёт только платный провайдер (MistTrack), иначе в отчёте стоит „тип получателя
   не установлен“.» Там же указать, откуда берутся записи реестра (официальная документация проектов, верифицированные контракты), в «Затраты» — трудоёмкость сборки и курации, в таблицу альтернатив — строку «Bitrace, BitOK — не
   проверялись».

[7] MAJOR | lens: owner-format | location: Section 3, 'Как проверяем качество', first bullet (contradicts A3, A6 and section 1)
   QUOTE: Каждое ребро отчёта подтверждается через /v1/transactions/{txid}/events лениво, только для рёбер, попавших в отчёт
   PROBLEM: Part A and section 1 promise that every reported fact is confirmed by a receipt from an operator other than TronGrid; section 3 confirms edges through TronGrid's own events endpoint, the same operator that supplied the
   history. Section 6 adds 'выборочная повторная сверка с первичным источником', which reads as sampling.
   FIX: Раздел 3: «Каждое ребро отчёта подтверждается receipt у оператора узла, отличного от TronGrid (раздел 1); event_index для ключа ребра берётся из /v1/transactions/{txid}/events. Обе проверки ленивые — только для рёбер,
   попавших в отчёт; идентичность ребра и фильтры — по G6.» Раздел 6, «Как проверяем качество»: заменить «выборочная повторная сверка с первичным источником» на «для рёбер отчёта — полная сверка по разделу 1, для остальных рёбер
   графа — выборочная».

[9] MAJOR | lens: owner-format | location: Section 1, alternatives table (PublicNode row) and 'Лицензия и коммерческое использование'; A1 row 1; G5
   QUOTE: Нет SLA и опубликованных лимитов, условия запрещают scraping и data mining, receipt без internal_transactions. Только резерв
   PROBLEM: PublicNode is the designated reserve node in A1, A3 and G5, yet the document itself says its terms prohibit scraping and data mining, and the licence subsection of section 1 does not address PublicNode at all. A
   production fallback on those terms conflicts with the 'lawfully obtained data' principle and leaves item 3 unanswered for a chosen component.
   FIX: Добавить в «Лицензия и коммерческое использование» раздела 1: «PublicNode: бесплатный доступ „AS IS“ по отзывной лицензии; условия запрещают scraping и data mining, коммерческое использование прямо не разрешено. До
   письменного подтверждения PublicNode используется только в разработке; резервный узел production — второй платный оператор из конфигурации (GetBlock или Nodit) после чтения его условий.» В A1 (строка 1) и G5: «PublicNode —
   резерв без ключа, в production только после подтверждения условий».

[10] MAJOR | lens: owner-format | location: Part A, A6 (row 'Полезность отчёта') and A8 item 2; section 1 'Лицензия и коммерческое использование'
   QUOTE: Хронология, граф, адреса, ссылки; пакет доказательств с сырыми ответами API и манифестом
   PROBLEM: The evidence package hands raw API responses to the client, while section 1 reads TronGrid's terms as 'продавать отчёты можно, проксировать сырой API клиентам нельзя', Chainstack limits use to internal business
   purposes and MistTrack forbids resale of data. The Stage 2 written confirmations cover SaaS use and storage, not redistribution of raw responses.
   FIX: A8, пункт 2: «TronGrid: цена индивидуального плана, допустимость использования в SaaS, хранения ответов и передачи сырых ответов клиенту в составе пакета доказательств. Chainstack: использование в SaaS и передача квитанций
   в пакете доказательств. MistTrack: проверка коммерческого использования, экспорт меток в JSON-отчёт и включение сырого ответа в пакет доказательств.» В раздел 1, «Лицензия»: «До письменных ответов пакет доказательств для
   клиента содержит TXID, хеши сырых ответов и манифест; сами сырые ответы хранятся на платформе.»

[16] MAJOR | lens: owner-format | location: Section 3, 'Инфраструктура и затраты' (contradicts A2 item 3 and section 1)
   QUOTE: 6-10 тыс. вызовов на граф из 1 000 адресов, то есть 10-16 графов в день и около 20-30 QPS для 5 минут
   PROBLEM: Section 3 charges all 6-10 thousand calls to the TronGrid daily quota (10-16 graphs a day, 20-30 QPS); A2 and section 1 say only about 3 300 of them go to TronGrid (about 30 graphs a day, 11 rps). Owners see two
   capacity figures for the same free plan.
   FIX: «Расчётная оценка, не измерено: 6–10 тыс. вызовов на граф из 1 000 адресов, из них около 3 300 к TronGrid (раздел 1); суточной квоты хватает примерно на 30 таких графов, средняя нагрузка на TronGrid — около 11 запросов в
   секунду при сроке 5 минут.» Если верна оценка раздела 3, исправить A2 (пункт 3) и раздел 1.

[23] MINOR | lens: owner-format | location: Section 1, 'Что проверить до фиксации выбора (Этап 2)', item 3
   QUOTE: Проба Chainstack: живые вызовы, internal_transactions в receipt, множитель RU для TRON (1 или 2)
   PROBLEM: The whole fact-verification design rests on Chainstack being independent of TronGrid, but that is asserted rather than verified, and the Stage 2 probe does not check it, although the same document detected a shared
   gateway between TronScan and TronGrid.
   FIX: «3. Проба Chainstack: живые вызовы; подтверждение, что узлы собственные, а не прокси TronGrid (сравнение формата ошибок и заголовков, как при проверке TronScan, и письменный ответ); internal_transactions в receipt;
   множитель RU для TRON (1 или 2); письменное подтверждение допустимости SaaS-использования.»

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

[31] MAJOR | lens: consistency | location: A8, п. 1 (и A5, разовые расходы Этапа 2)
   QUOTE: Живая проба Chainstack: возвращает ли он internal transactions и как тарифицирует TRON.
   PROBLEM: G5, A2 п. 2, A6 and A9 all defer the choice of the second independent address index to Stage 2, A5 budgets its trial, and sections 1 (п. 4) and 3 list it with pass criteria. None of A8's nine items contains it,
   although A8 claims to close every «не измерено», and the ≥ 99% data-retrieval criterion cannot be measured without it.
   FIX: Add to A8 п. 1: «Проба второго независимого адресного индекса (Blockbook-TRON через NOWNodes; Bitquery — только при письменно подтверждённой глубине архива). Критерий: полное совпадение с TronGrid на контрольных окнах,
   известные цена и глубина истории.»

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

[48] MINOR | lens: consistency | location: раздел 1 «Заменяемость»; раздел 2 «Заменяемость»; раздел 3 «Заменяемость» и «Как проверяем качество»; A5; «Как читать»
   QUOTE: Интерфейс TransferHistoryProvider; вторая реализация — индекс стороннего оператора, не TronScan.
   PROBLEM: Key terms drift. The same interfaces are TransferHistoryProvider and LabelProvider in sections 1-2 but TransferSource and LabelSource in section 3. «Стандартное расследование» is about 40 addresses in section 1, 30 in
   section 3, 45 (heavy 60) in section 5 and «несколько десятков» in A5 and section 6. «Аудит» means the whole verified study in Part A, but in the sections it often means the unverified first-pass research («исходный аудит»,
   «первичный аудит», «тезис аудита опровергнут»), alongside «верификатор», «проверяющий», «перепроверка».
   FIX: Use TransferSource and LabelSource in sections 1 and 2. Define once in A5 and reuse: «стандартное расследование — 40–45 адресов (тяжёлое — 60)». Add to «Как читать»: «В части B «аудит» или «исходный аудит» — первичное
   исследование направления, «верификатор» — независимая перепроверка; там, где они расходятся, действует вывод верификатора.»

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

[57] MAJOR | lens: measurability | location: раздел 6, «Что проверить», критерии LH-GraphBench; также раздел 1 (пункт 1), раздел 4 (пункт 3), раздел 8 (проверка 8); A8, пункт 1
   QUOTE: граф на 1 000 адресов ≤ 5 мин; отчёт на несколько десятков адресов ≤ 2 мин
   PROBLEM: The same «1 000 адресов за 5 минут» is the pass criterion of four checks with different scope (TronGrid load run, DBOS spike, a mock-API load test, a graph-layer benchmark); none is end-to-end with real sources,
   verification receipts and model steps, so passing any of them does not establish criterion 3. The load profile is also undefined: with one worker and one shared limiter per provider, a 1,000-address job takes the whole TronGrid
   allowance while a 30-second job runs beside it.
   FIX: Add to A8: «Приёмочный замер критерия 3 один: сквозной прогон на тестовом сервере с реальными источниками, от постановки задачи до проверенного JSON-отчёта, по одной задаче одновременно, на наборе графов, зафиксированном
   до замера. Проверки в разделах 1, 4, 6 и 8 — бюджеты компонентов (источник, очередь, графовый слой), а не приёмка. Отдельно измеряется смешанная нагрузка: простая задача во время обхода графа на 1 000 адресов; для неё в
   ограничителе шлюза вводится приоритет интерактивных запросов.» In section 6 replace the quoted criteria with «графовый слой укладывается в свою долю бюджета времени, заданную до замера».

[67] MAJOR | lens: measurability | location: A4, G6; раздел 1, «Что проверить», пункт 5
   QUOTE: Наличие и стабильность поля event_index проверяется на Этапе 2.
   PROBLEM: The edge key, and with it the «no duplicate transactions» criterion, depends on this field, but the check has no pass criterion and no fallback. Section 3 reports the field present in single probes only.
   FIX: Replace with: «Проверка на Этапе 2: на выборке не менее 1 000 TXID, включая транзакции с несколькими Transfer, поле event_index есть у 100% событий, не меняется при повторном запросе через 24 часа и совпадает с порядковым
   номером лога в квитанции независимого узла. При провале ключом ребра становится (chain, txid, порядковый номер лога в квитанции узла).»

[72] MINOR | lens: measurability | location: раздел 1, «Ограничения и риски»
   QUOTE: Solidified-данные отстают на 18–19 блоков (54–69 с); в отчёт идут только они.
   PROBLEM: For a transaction younger than about a minute the 30-second target cannot be met on paper, because the report uses only data that lag by 54-69 s; the document does not connect this to criterion 3 or say the wait counts
   as waiting on an external source. Also 18-19 blocks at 3 s is 54-57 s, not 54-69 s.
   FIX: Add after the sentence: «Для транзакции моложе минуты срок 30 секунд поэтому недостижим: ожидание подтверждения сети учитывается отдельно как ожидание внешнего источника, а в интерфейсе показывается статус «ждём
   подтверждения сети».» Check the range: 18–19 blocks at 3 s give 54–57 s.

[75] MAJOR | lens: reader-safety | location: A7, question 11
   QUOTE: **Горячие кошельки бирж:** остановка на помеченной границе или лимит страниц на адрес; пороги по умолчанию (минимальная сумма, окно транзита).
   PROBLEM: Cannot be answered as asked. The problem is not stated, the two options are presented as either/or although sections 1 and 6 say both are needed, and the owner is asked for thresholds («минимальная сумма», «окно
   транзита») that appear nowhere else in the document and have no proposed values.
   FIX: Replace with: «11. **Трассировка через кошельки бирж.** Горячий кошелёк биржи принимает тысячи переводов в час; пролистать его историю целиком нельзя, а проследить средства дальше него нельзя по смыслу. Предлагаю:
   трассировка останавливается на адресе с меткой биржи (в отчёте — «переведено на опубликованный кошелёк биржи»); для непомеченных адресов с очень большой историей действует лимит страниц на адрес, ветвь помечается как усечённая.
   Согласны? Числовые пороги (минимальная сумма ветви, окно времени транзита) я предложу по итогам замеров Этапа 2; сейчас значения от вас не нужны.»

[82] MAJOR | lens: reader-safety | location: A2 item 2; A4 G5 (last sentence)
   QUOTE: **TronScan нельзя закладывать в коммерческий продукт.** Его Terms of Service от 2022-01-04 запрещают сторонние приложения
   PROBLEM: A categorical legal conclusion in bold, while G5 admits it is not confirmed that the 2022 document is the current edition or covers the API. Sections 1 and 2 also disagree on whom the ToS excludes («организации» vs
   «резидентов»). «Один из проверявших» and «строгое правило» in G5 are drafting residue.
   FIX: A2.2: «2. **TronScan не закладываем в критический путь до письменного согласия.** По нашему прочтению, его Terms of Service от 2022-01-04 запрещают сторонние приложения без письменного согласия; действует ли эта редакция и
   распространяется ли она на API, не подтверждено — нужен ответ TronScan или юриста. Основной источник — TronGrid; каждый факт отчёта дополнительно подтверждается квитанцией транзакции у независимого оператора узла. Второй
   независимый индекс «адрес → переводы» пока не выбран.» G5 tail: «Оговорка: опубликованных условий именно для API TronScan не найдено, и не подтверждено, что документ 2022 года — действующая редакция; до ответа TronScan считаем,
   что запрет действует.»

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
