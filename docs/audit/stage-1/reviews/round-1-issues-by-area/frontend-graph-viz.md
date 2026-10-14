# Review issues relevant to section(s) [9] (frontend-graph-viz)

[14] MAJOR | lens: owner-format | location: Section 10 'Лицензия и коммерческое использование'; section 9 'Лицензия и коммерческое использование'; A1 rows 9 and 10
   QUOTE: Лицензии Pydantic и uvicorn в досье не зафиксированы — не проверено.
   PROBLEM: Item 3 is unanswered for chosen components: uvicorn (the ASGI server), and in section 9 TanStack Router and zustand ('в аудите не зафиксированы — не проверено'), while A1 states 'MIT' for both rows. Pydantic is 'not
   verified' in section 10 but 'MIT' in section 12.
   FIX: Проверить по файлам LICENSE и записать. Раздел 10: «Pydantic — MIT (раздел 12); uvicorn — [лицензия по файлу LICENSE; ожидаемо BSD-3-Clause]». Раздел 9: «TanStack Router и zustand — [лицензии по файлам LICENSE; ожидаемо
   MIT]». До проверки в A1, строки 9 и 10, вместо «MIT» писать «MIT; у части зависимостей лицензия не проверена».

[19] MINOR | lens: owner-format | location: Part A, A9 (last row) and A5
   QUOTE: Объём собственного кода больше, чем «только клей»: трассировщик, раскладка и сворачивание графа, шлюз
   PROBLEM: The brief's strategy is not to build what already exists; the document admits the own code exceeds glue but never totals the effort. Estimates are scattered across sections 2, 3, 4, 6, 9 and 11, and sections 5, 7, 10,
   12 and 13 give none.
   FIX: Добавить в A5 абзац «Трудозатраты на собственный код (оценки аудита, не измерено)»: «трассировщик 2–3 человеко-недели; оркестратор, учёт бюджета и журнал 2–3; шлюз и реестр инструментов 1.5–2.5; интерфейс и карта 4–5
   (верификатор отдельно оценивает раскрытие ветвей, агрегацию, раскладку и экспорт в 3–4); Label Store 3–5 дней; тестовый набор меток 5–8 человеко-дней; стенд графового теста 1–2 недели. Итого около 12–18 человеко-недель; по
   адаптеру LLMClient, схеме БД, API, отчётам и эксплуатации оценки нет.»

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

[64] MAJOR | lens: measurability | location: A6, строка «≥ 95% точности меток»; раздел 12
   QUOTE: Независимый размеченный набор; источник метки не используется для её же проверки
   PROBLEM: The row covers one of the four exchange-identification criteria. The «separate evidence package for a potential exchange» is not described anywhere (only the general evidence zip and letter templates), and the other
   two (source, date and confidence on every classification; unknown addresses never called an exchange) have tests in sections 9 and 12 but no row here.
   FIX: Add three rows: «| У каждой классификации — источник, дата проверки, достоверность | Обязательные поля модели Pydantic: отчёт без них не сериализуется; тест схемы на всех сценариях | заложено в архитектуру |», «|
   Неизвестный адрес не называется биржей по косвенному сходству | Эвристика даёт только «кандидата»; тест на наборе hard negatives: 0 меток «биржа» без первичного источника или метки провайдера | набор предстоит собрать |», «|
   Отдельный пакет доказательств для потенциальной биржи | Для каждого адреса-кандидата формируется отдельный файл пакета: переводы на адрес с TXID и квитанциями, источник и дата метки, сырой ответ провайдера, хеши в манифесте;
   тест: число пакетов равно числу кандидатов в отчёте | предстоит спроектировать (раздел 12) |».

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
