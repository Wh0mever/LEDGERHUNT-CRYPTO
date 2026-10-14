# Review issues relevant to section(s) [2] (labels-risk)

[4] MAJOR | lens: owner-format | location: Section 2, 'Решение' and 'Ограничения и риски' (need b: exchanges, exchangers, bridges, services)
   QUOTE: Не покрыто открытыми источниками: операционные hot wallets вне PoR, OTC, P2P-мерчанты, обменники СНГ.
   PROBLEM: The brief asks for label sources for exchanges, exchangers, bridges and services; section 2 chooses sources only for exchanges and sanctions or freezes. The contract registry for exchangers and bridges is mentioned in
   A3, A8 and section 1 but is not part of the section 2 decision and has no named source, cost or quality check.
   FIX: Добавить в «Решение» раздела 2: «Четвёртый локальный источник — курируемый реестр контрактов обменников (DEX), мостов и сервисов (SunSwap, JustLend, мосты): адрес, тип, источник записи, дата проверки, confidence;
   собирается до старта трассировщика (раздел 1, пункт 6). Для централизованных обменников, OTC и P2P-сервисов открытого источника нет: в MVP их метку даёт только платный провайдер (MistTrack), иначе в отчёте стоит „тип получателя
   не установлен“.» Там же указать, откуда берутся записи реестра (официальная документация проектов, верифицированные контракты), в «Затраты» — трудоёмкость сборки и курации, в таблицу альтернатив — строку «Bitrace, BitOK — не
   проверялись».

[8] MAJOR | lens: owner-format | location: Section 14, 'Как проверяем качество' and 'Решение'; A4 G7 (contradicts section 2)
   QUOTE: Набор OFAC собирается из файлов TRX и USDT и каждую ночь сверяется с первичными файлами
   PROBLEM: Section 2 builds the sanctions list from the primary SDN_ADVANCED.XML; section 14 builds it from the two files of the 0xB10C mirror and admits that 3 of 340 addresses were not found in the primary files. G7 and section
   14 still present 340 as the full set, which conflicts with the principle that conclusions rest on primary data.
   FIX: Раздел 14: «Набор OFAC собирается из первичного файла SDN_ADVANCED.XML (раздел 2) и каждую ночь сверяется с зеркалом 0xB10C как контрольным. Адрес, найденный только в зеркале (сейчас 3 из 340), метку „OFAC SDN“ не
   получает, пока не подтверждён в первичном файле.» В «Решении» раздела 14: «полный локальный набор OFAC SDN (340 адресов TRON по зеркалу, из них 337 подтверждены в первичных файлах)». G7: «контрольное значение 340 адресов TRON
   по зеркалу на 2026-10-01, из них 337 найдены в первичных файлах».

[11] MAJOR | lens: owner-format | location: Section 3, 'Лицензия и коммерческое использование' (contradicts section 2)
   QUOTE: Условия коммерческого использования и кэширования у MistTrack и Arkham в документации не найдены — нужны письменные.
   PROBLEM: Section 2 states that MistTrack's Terms of Use of 2026-10-09 explicitly allow client PDF reports, commercial investigations and caching; section 3 says no such terms were found. Owners get two opposite answers to item
   3 for the same paid provider.
   FIX: «Условия MistTrack разобраны в разделе 2: Terms of Use от 2026-10-09 разрешают клиентские отчёты, коммерческие расследования и кэширование, но до начала коммерческого использования возможны KYB и проверка бизнес-модели. У
   Arkham условия коммерческого использования и кэширования в документации не найдены — нужны письменные.»

[12] MAJOR | lens: owner-format | location: Section 10, 'Решение'; A1 row 10; A7 (owner decisions)
   QUOTE: Статус: принято; конкретный IdP ждёт решения владельцев и пробы на сервере.
   PROBLEM: The authentication provider has no chosen solution (Keycloak, Logto, ZITADEL or external), yet A1 row 10 is marked 'принято' and A7 contains no question about it. Other decisions that Part B leaves to the owners are
   also missing from A7.
   FIX: A1, строка 10, статус: «принято; поставщик входа — условно». Добавить в A7: «17. **Поставщик входа:** на своём сервере ([рекомендация по умолчанию: Logto при 8 GB после замера памяти, Keycloak при 16 GB и более]) или
   внешний сервис, где учётные данные хранит третья сторона; допустим ли ZITADEL под AGPL; нужны ли в MVP MFA и организации. 18. **Решения из разделов части B:** размещение трасс моделей — Phoenix на своём сервере или Langfuse
   Cloud EU (раздел 5); перечень действий, требующих подтверждения человеком (раздел 4); правило ввода графовой СУБД „выигрыш не менее чем в 3 раза“ (раздел 6); нужен ли MCP-сервер платформы для клиентов (раздел 11); нужна ли
   квалифицированная метка времени eIDAS или подпись PAdES (раздел 12); допустим ли Gotenberg с Chromium как запасной движок PDF (G10); шкала confidence (раздел 2).»

[13] MAJOR | lens: owner-format | location: Section 2, 'Как проверяем качество' (test set); A5 one-off costs; A7 item 7
   QUOTE: hard negatives из собственных платежей в шлюзы, swap-сервисы и казино
   PROBLEM: The ground-truth plan requires the team to make its own payments to casinos and swap services and control deposits to exchanges. Legality depends on the owners' jurisdiction, it needs KYC-verified exchange accounts,
   and neither point is raised in A7; this touches the principle 'only lawfully obtained data'.
   FIX: Раздел 2: «hard negatives из собственных платежей в платёжные шлюзы и swap-сервисы; платежи в казино — только при письменном подтверждении юриста, что это законно в юрисдикции владельцев (вопросы 2 и 8 в A7), иначе класс
   набирается из публично раскрытых адресов». A7, пункт 7: «…Anthropic и MistTrack, а также аккаунты на биржах для контрольных депозитов (потребуют KYC владельца аккаунта)…». A7, пункт 8: добавить «…и по допустимости контрольных
   платежей в сервисы для тестового набора меток».

[19] MINOR | lens: owner-format | location: Part A, A9 (last row) and A5
   QUOTE: Объём собственного кода больше, чем «только клей»: трассировщик, раскладка и сворачивание графа, шлюз
   PROBLEM: The brief's strategy is not to build what already exists; the document admits the own code exceeds glue but never totals the effort. Estimates are scattered across sections 2, 3, 4, 6, 9 and 11, and sections 5, 7, 10,
   12 and 13 give none.
   FIX: Добавить в A5 абзац «Трудозатраты на собственный код (оценки аудита, не измерено)»: «трассировщик 2–3 человеко-недели; оркестратор, учёт бюджета и журнал 2–3; шлюз и реестр инструментов 1.5–2.5; интерфейс и карта 4–5
   (верификатор отдельно оценивает раскрытие ветвей, агрегацию, раскладку и экспорт в 3–4); Label Store 3–5 дней; тестовый набор меток 5–8 человеко-дней; стенд графового теста 1–2 недели. Итого около 12–18 человеко-недель; по
   адаптеру LLMClient, схеме БД, API, отчётам и эксплуатации оценки нет.»

[21] MINOR | lens: owner-format | location: Section 14, 'Инфраструктура и затраты', 'Переменные'
   QUOTE: MistTrack ($0.10 за вызов address_labels) учтён в разделе 2.
   PROBLEM: $0.10 is the price only on the $1 000 package; section 2 and A5 use $0.20 per call on the $20 package as the default.
   FIX: «MistTrack ($0.10–0.20 за вызов address_labels в зависимости от пакета) учтён в разделе 2.»

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

[37] MAJOR | lens: consistency | location: G7 (A4); раздел 14 «Решение», «Почему выбрано» и «Как проверяем качество»; раздел 2 «Решение» и «Как проверяем качество»
   QUOTE: OFAC SDN (контрольное значение 340 адресов TRON на 2026-10-01)
   PROBLEM: 340 is the count in the 0xB10C mirror. Section 14 found only 337 of these in the primary sdn.csv and sdn_comments.csv, yet G7 and section 14's «Решение» present 340 as the control value of the OFAC list itself. The
   sections also build the set differently: section 2 parses the primary SDN_ADVANCED.XML and collects TRON addresses «из всех тикерных списков, не только TRX и USDT»; section 14 builds it «из файлов TRX и USDT» of the mirror.
   Section 14's recount against primary files is the more reliable number.
   FIX: G7: «OFAC SDN (собственный разбор первичного файла; контрольное значение — 340 адресов TRON по зеркалу 0xB10C на 2026-10-01, из них 337 найдены в первичных файлах, расхождение выясняется на Этапе 2)». Section 14 «Решение»:
   «(340 адресов TRON по зеркалу, 337 подтверждены первичными файлами)». Section 14, quality bullet: «Набор OFAC собирается разбором первичного файла по всем тикерным спискам (раздел 2) и каждую ночь сверяется с зеркалом 0xB10C».

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

[68] MAJOR | lens: measurability | location: A2, пункт 4; A7, вопрос 4; раздел 2, «Ограничения и риски»
   QUOTE: статистически недоказуема в исходной формулировке: нужно минимум 73 безошибочных примера
   PROBLEM: The owners' wording is a share on a test set; «недоказуема» follows only from a requirement the document adds itself, that the lower bound of a 95% Wilson interval be at least 95%, and Part A does not say so. The same
   standard is not applied to the other thresholds: 50 scenarios out of 50 give a lower bound of 92.9%, so «95% of scenarios» would be just as unprovable.
   FIX: Replace the sentence with: «Цель «95% точности» для класса депозитных адресов нельзя подтвердить с запасом: если требовать, чтобы нижняя граница 95%-го доверительного интервала (Wilson) была не ниже 95%, нужно минимум 73
   безошибочных примера, а собственных депозитных адресов реально собрать 10–30. Как простую долю критерий посчитать можно, но на 10–30 адресах он мало что доказывает. Для остальных порогов Промпта 3 (90%, 95%, 99%) мы считаем
   простую долю и публикуем интервал: при 50 сценариях из 50 нижняя граница — 92.9%.» Add to A7 question 4: «Общее правило для всех процентных критериев: простая доля с интервалом или нижняя граница интервала.»

[69] MAJOR | lens: measurability | location: раздел 2, «Как проверяем качество» и «Инфраструктура и затраты»; раздел 3, «Как проверяем качество»; A5, разовые расходы; A7, вопрос 7
   QUOTE: Независимый тестовый набор на 600+ адресов, истина не из проверяемых источников
   PROBLEM: The label test set has four sizes: 600+ here, at least 300 in section 3, 400 in the threshold example, and a cost estimate ($50-150, 5-8 person-days) stated for 400-500 with 600+ «не измерено». The MistTrack probe is
   budgeted at $10-20, but a $20 package is 100 calls, and A7 does not say who opens the exchange accounts needed for control deposits.
   FIX: Set one size: «Независимый тестовый набор первой версии — 400 адресов (порог: 389 верных положительных меток из 400 по нижней границе Wilson); расширение до 600+ — после Этапа 2.» A5: «проба MistTrack $10–20 (до 100
   адресов) либо пакет $150 на 1 000 вызовов для всего набора». A7 question 7, add: «и аккаунты на биржах для контрольных депозитов (нужна верификация личности владельца аккаунта)».

[71] MINOR | lens: measurability | location: A5, абзац «Разовые расходы Этапа 2»; A7, вопрос 6; раздел 13
   QUOTE: стенд замеров с выделенными ядрами €21.73/мес
   PROBLEM: Section 13 gives this price «при контракте на 12 месяцев», so the commitment is about €261, not a one-off monthly fee, and A7 question 6 presents the stand as optional although G12 runs all performance measurements on
   it and criterion 3 needs a fixed test server. The list has no total, and the $50-150 for control deposits already includes the $10 MistTrack trial listed separately (section 2).
   FIX: Replace with: «стенд замеров с выделенными ядрами €21.73/мес при контракте на 12 месяцев (обязательство около €261); он же — тестовый сервер для критерия 3. Итого без юриста, NOWNodes и внешнего хоста для сверки
   справочника: около $180–410 и €261.» A7 question 6: replace «нужен ли отдельный стенд для замеров» with «согласны ли вы оплатить стенд замеров (контракт на 12 месяцев, около €261): без него сроки из критерия 3 нельзя измерить
   воспроизводимо».

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
