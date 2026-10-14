# Review issues relevant to section(s) [14] (osint-recovery)

[1] MAJOR | lens: owner-format | location: Part A, A4 (cross-cutting decisions G1-G15), after G15; also A6
   QUOTE: Поискового провайдера (Tavily или Brave) выбираете вы. Платформа никогда не обещает возврат средств.
   PROBLEM: The always-on principle 'seed phrases, private keys and wallet access are never requested' has no cross-cutting decision in Part A. It appears only as one clause in section 14 (risks) and as trace masking in section 5;
   there is no control for victim-supplied screenshots and correspondence, which A7.3 plans to send to model providers.
   FIX: Добавить в A4: «**G16.** Платформа никогда не запрашивает seed-фразы, приватные ключи и доступ к кошельку: таких полей нет ни в интерфейсе, ни в API, ни в шаблонах писем. Входной фильтр проверяет текст пользователя и
   текст, распознанный во вложениях (скриншоты, переписка): найденная seed-фраза или приватный ключ не сохраняется и не передаётся моделям и поисковым провайдерам, пользователь получает предупреждение. Все инструменты — только
   чтение; подписи и отправки транзакций в системе нет (раздел 11).» В A6 добавить строку: «Seed-фразы и приватные ключи не запрашиваются и не сохраняются | входной фильтр; тест с подставной seed-фразой: 0 вхождений в БД,
   журналах, трассах и запросах к моделям — обязательное условие сборки | заложено в архитектуру».

[8] MAJOR | lens: owner-format | location: Section 14, 'Как проверяем качество' and 'Решение'; A4 G7 (contradicts section 2)
   QUOTE: Набор OFAC собирается из файлов TRX и USDT и каждую ночь сверяется с первичными файлами
   PROBLEM: Section 2 builds the sanctions list from the primary SDN_ADVANCED.XML; section 14 builds it from the two files of the 0xB10C mirror and admits that 3 of 340 addresses were not found in the primary files. G7 and section
   14 still present 340 as the full set, which conflicts with the principle that conclusions rest on primary data.
   FIX: Раздел 14: «Набор OFAC собирается из первичного файла SDN_ADVANCED.XML (раздел 2) и каждую ночь сверяется с зеркалом 0xB10C как контрольным. Адрес, найденный только в зеркале (сейчас 3 из 340), метку „OFAC SDN“ не
   получает, пока не подтверждён в первичном файле.» В «Решении» раздела 14: «полный локальный набор OFAC SDN (340 адресов TRON по зеркалу, из них 337 подтверждены в первичных файлах)». G7: «контрольное значение 340 адресов TRON
   по зеркалу на 2026-10-01, из них 337 найдены в первичных файлах».

[21] MINOR | lens: owner-format | location: Section 14, 'Инфраструктура и затраты', 'Переменные'
   QUOTE: MistTrack ($0.10 за вызов address_labels) учтён в разделе 2.
   PROBLEM: $0.10 is the price only on the $1 000 package; section 2 and A5 use $0.20 per call on the $20 package as the default.
   FIX: «MistTrack ($0.10–0.20 за вызов address_labels в зависимости от пакета) учтён в разделе 2.»

[28] MAJOR | lens: consistency | location: A5, таблица «Переменные, на стандартное расследование» и абзац под ней; раздел 5 «Инфраструктура и затраты», пункт о переменных
   QUOTE: | **Итого** | | **около $1.00** |
   PROBLEM: The default limits add up to $0.95-1.02 ($0.05 data + $0.40 labels + $0.45 models + $0.05 or $0.08 search + €0-0.04 timestamp). With Tavily and a commercial timestamp service, which section 12 says is budgeted for the
   paid product, the defaults exceed the owners' $1 cap. The next paragraph treats $0.57 on models as an allowed case although the model limit in the same table is $0.45, a figure that appears in no section. Section 5 also
   reserves «$0.10-0.25» for web search via Anthropic's built-in search, while A5, G15 and section 14 use 10 queries to Brave or Tavily for $0.05-0.08.
   FIX: Make the defaults sum to at most $1, for example a model limit of $0.40, and show the range: «**Итого** | | **$0.90–0.97; общий лимит $1 действует поверх постатейных**». Paragraph: «Запаса почти нет. Тяжёлый случай ($0.57
   на модели) превышает лимит на модели: при его достижении шаги переводятся на Haiku 5.5, а текст отчёта собирается без модели.» Section 5: «Из него $0.05–0.16 — веб-поиск: 10–20 запросов к Brave или Tavily через собственный
   адаптер (раздел 14, G15); встроенный поиск Anthropic не используется».

[29] MAJOR | lens: consistency | location: раздел 2 «Решение»; раздел 3 «Инфраструктура и затраты» и «Почему выбрано»; раздел 14 «Инфраструктура и затраты»; G7; A5
   QUOTE: При 2-4 адресах (G7) и пакетах на 100-1 000 вызовов ($0.15-0.20) это расчётно $0.30-0.80 на расследование
   PROBLEM: G7, A5 and A7 (вопрос 5) set a default of 2 paid calls, up to $0.40. Sections 2 and 3 plan «2–4» calls, and section 3 attributes that range to G7; at 4 calls ($0.80) the $1 budget cannot hold. Part A's default of 2 is
   the later, budget-driven decision. The price per call also differs: section 14 says «$0.10 за вызов address_labels», which per section 2 and A5 applies only to the $1,000 pack ($0.20 on the $20 pack the plan starts with).
   Section 3 says «$0.03-0.20 (30 адресов = $3-6)», but $0.03 × 30 is $0.90.
   FIX: Section 2: «…с оплатой за вызов; лимит по умолчанию — 2 терминальных адреса на расследование (G7), настраивается до 4». Section 3: «При лимите по умолчанию в 2 вызова (G7) и пакетах на 100–1 000 вызовов ($0.15–0.20) это
   расчётно $0.30–0.40 на расследование; при 4 вызовах — до $0.80». Section 3, «Почему выбрано»: «(30 адресов = $0.90–6)». Section 14: «MistTrack ($0.10–0.20 за вызов address_labels в зависимости от пакета) учтён в разделе 2».

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

[39] MAJOR | lens: consistency | location: A2, п. 6; раздел 14 «Почему выбрано», последний пункт; раздел 12 «Состояние проекта», последний пункт; A10
   QUOTE: Возврат средств идёт только через правоохранительные органы.
   PROBLEM: Section 12 records the verifier's correction that this thesis is «слишком широк»: TRM Beacon Network claims access for vetted security companies, and its joining conditions are a Stage 2 check. Section 14 adds that
   Tether's cs.tether.to portal was not read. A2 п. 6 and section 14 still state the conclusion flatly; section 12's caveat is more likely right. Section 12 and A10 also say Tether's requirements page returned 404, while section
   14 quotes Tether's law-enforcement policy of 2018-01-03 as read.
   FIX: A2 п. 6: «**Для жертвы возврат средств идёт через правоохранительные органы.** На сайте Tether пути для жертвы не найдено (портал cs.tether.to не прочитан): запрос принимают от органа с правовым основанием. TRM Beacon
   Network заявляет доступ для проверенных security-компаний; условия вступления проверяются на Этапе 2.» Section 14: «Возврат идёт только через органы.» → «Для жертвы возврат идёт через органы.» In A10 and section 12, name which
   Tether page returned 404, since section 14 read the law-enforcement policy.

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

[65] MAJOR | lens: measurability | location: раздел 14, «Как проверяем качество», пункт 2; раздел 8, «Как проверяем качество», первая строка; A6, последняя строка; раздел 3
   QUOTE: не менее 10 из 50 сценариев для измерения precision и recall
   PROBLEM: A6 and section 3 say only synthetic-exact and self-generated scenarios count toward the 50 and freeze-anchored cases are a separate class, but section 14 puts at least 10 OFAC and blacklist scenarios inside the 50 and
   section 8 says its eight crash and limit checks «войдут в набор из 50+ сценариев». Counted that way about 32 tracing scenarios remain, and section 3 admits the current design yields only 25+.
   FIX: Section 14: «Адреса из OFAC SDN и из событий AddedBlackList входят в отдельный класс freeze-anchored — не менее 10 сценариев сверх 50 — для измерения precision и recall.» Section 8: «Критерии spike; они же войдут в
   регрессионные тесты надёжности, отдельно от 50 сценариев трассировки:». A6, last row, add: «Сейчас спроектировано 25+ засчитываемых сценариев; нужно ещё не менее 25 и итоговый набор.»

[73] MINOR | lens: measurability | location: раздел 4, «Инфраструктура и затраты», пункт «Переменные (LLM-токены)»; также раздел 3 («Почему выбрано», пункт 3) и раздел 14 («Переменные»)
   QUOTE: Sonnet 5.5 на всех шагах дал бы $1.1–2.2, то есть выше лимита
   PROBLEM: $0.55 times 2-4 requests gives $1.1-2.2 without the +30% tokens named in the same sentence; with it the range is $1.4-2.9 (the Haiku figure «менее $0.15» does include both factors). Two similar slips: section 3 prices
   a MistTrack call at $0.03-0.20 but gives «30 адресов = $3-6», which matches $0.10-0.20, and section 14 quotes MistTrack at $0.10 per call although the A5 default is $0.20.
   FIX: Section 4: «Sonnet 5.5 на всех шагах дал бы $1.4–2.9, то есть выше лимита». Section 3: «вызов MistTrack стоит $0.10–0.20 на пакетах до 10 000 вызовов (30 адресов = $3–6)». Section 14: «MistTrack ($0.10–0.20 за вызов
   address_labels) учтён в разделе 2».

[80] MAJOR | lens: reader-safety | location: A2 item 6; also A1 row 14 and the title of section 14
   QUOTE: **Возврат средств идёт только через правоохранительные органы.** У Tether нет канала для жертвы
   PROBLEM: Stated as fact, but it rests on a 2018 policy, an unread portal (cs.tether.to) and a 404 page; section 12 itself says the thesis «слишком широк» because TRM Beacon Network claims access for vetted security companies.
   Separately, «каналы возврата средств» in A1 and the section 14 title can be read as the platform offering recovery channels.
   FIX: Replace item 6 with: «6. **Канала возврата для самой жертвы не найдено; найденные каналы рассчитаны на правоохранительные органы.** По опубликованной политике Tether (2018) запрос принимается от органа с правовым
   основанием; портал cs.tether.to не прочитан, страница требований отдаёт 404. TRM Beacon Network заявляет доступ для проверенных компаний по безопасности — условия не проверены. Реквизиты бирж первичными источниками не
   подтверждены: их сайты были недоступны из сети аудита. Платформа готовит пакет доказательств и черновики обращений; заморозку и возврат она не выполняет и не обещает.» Rename A1 row 14 to «OSINT и адресаты обращений» and
   section 14 (and the contents line) to «Источники OSINT и адресаты обращений о заморозке и возврате».

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
