
############################################################
# regression
VERDICT: Fit to send after seven small text fixes; no blocker remains on this lens. All three blockers and nearly all majors of the first review are resolved, and a search found no surviving old number, question number or term ($0.45, $0.95–1.02, 10–16 graphs, questions 1–8, G1–G15, «верификатор», «досье», «тестовая сеть»). The most important remaining fix is in A5: say that the $0.40 model limit leaves no margin and that the 70% step ($0.28) is reached in a typical investigation by the document's own numbers. I could not check the new claim that Prompt 3 itself excludes fixed costs from the $1 (G17, A5), because the prompt text is not in the project folder.

############################################################
# consistency-arithmetic
VERDICT: Not fit to send as is, but close: one blocker and ten major inconsistencies, each fixable with a sentence or a table cell. What I checked and found clean: both A5 fixed-cost totals, the $0.85–0.92 sum of limits, the per-investigation share of fixed costs, the Anthropic cap, the Stage 2 one-off total, all three A6 time allocations, A1 statuses against every section's "Решение" paragraph, and all G-code and A7-question references. The most important fix is in A5: the document's own numbers put the typical investigation ($0.40) above the 70% downgrade threshold ($0.28) of the limit the owners are asked to accept in question 5, and the text says only the heavy case is affected; after that, the contradictions inside A8 (row 3 and the ordering of rows 4, 8 and 9).

[8] BLOCKER | A5, bullet «Тяжёлый случай» (line 204); same claim in section 4, line 653
   QUOTE: **Тяжёлый случай.** Оценка $0.57 на модели выше лимита $0.40 и сама не является верхней границей
   PROBLEM: Arithmetic contradiction on the limit the owners accept in question 5(а). The typical estimate ($0.40) equals the model limit, and the 70% rule in G17 triggers at $0.28. Section 5 says 8 Sonnet calls make up 84% of the cost
   (about $0.042 each), so by the document's own numbers the typical investigation crosses $0.28 before the last 2–3 Sonnet calls and finishes on Haiku. Reserving the maximum cost before each call makes this stricter. A5 and section 4
   («тяжёлый случай в него не укладывается, и тогда действует снижение») present the downgrade as a heavy-case event only. The G17 arithmetic is the side that is right; the A5 and section 4 wording should change.
   FIX: **Типичный и тяжёлый случаи.** Типичная оценка $0.40 равна лимиту моделей, а порог 70% — это $0.28. Поэтому по расчёту уже типичное расследование доходит до порога, и часть вызовов, отведённых Sonnet 5.5, выполняет Haiku 5.5.
   Оценка $0.57 для тяжёлого случая выше лимита и сама не является верхней границей: она не учитывает оплачиваемые отказы модели и рост входа в многоходовых циклах. При 70% лимита моделей остаётся только Haiku 5.5; при 100% отчёт
   выпускается без текста модели, полученные результаты сохраняются. Если и в типичном случае все отведённые шаги должна выполнять Sonnet 5.5, лимит моделей или порог нужно поднять — это решается в вопросе 5. [Раздел 4, строка 653,
   заменить фразу на: «Лимит моделей по умолчанию — $0.40 (G17): типичный случай по расчёту доходит до порога 70% ($0.28), тяжёлый в лимит не укладывается; в обоих случаях действует снижение из G17.»]

[9] MAJOR | A8, table row 3 «Оркестрация» (line 296)
   QUOTE: отсутствие подставного ключа в системных таблицах, сквозной замер «простая транзакция за 30 секунд»
   PROBLEM: Row 3 lists an end-to-end 30-second measurement among the «проверки раздела 8», and its criterion is «вариант проходит все проверки». Section 8 has no such check: check 8 is a component budget (queue and checkpoint overhead
   against a mock API) and the section says explicitly it is not acceptance of the 30-second goal. Section 10 puts the end-to-end 30-second run in the single acceptance measurement, and the note under the A8 table says row 3 is a time
   share, not acceptance. As written, the DBOS decision would hinge on TronGrid and model latency rather than on the orchestration layer. Section 8 is the side that is right.
   FIX: отсутствие подставного ключа в системных таблицах, накладные расходы очереди и сохранения шагов на простой транзакции (доля из A6 — до 2 секунд) и на графе из 1 000 адресов

[10] MAJOR | A8, first paragraph (line 290) and last sentence (line 306), against rows 4 and 9
   QUOTE: До написания ядра выполняются измерения и проверочные реализации.
   PROBLEM: A8 says every check in the table runs before the core is written and that the baseline tracer is built «после этого» (also question 17). Three checks need a working pipeline: row 4 (pilot on 50 scenarios with the criterion
   «не менее 95% запусков завершаются корректным отчётом», plus the comparison with the baseline algorithm from section 5, item 3), row 9 (peak memory during five parallel standard investigations) and row 9 again (replay gives the same
   graph and report). The dependency is real, since section 5 says Inspect AI calls the working pipeline, so the ordering statement in A8 is the side that should change.
   FIX: Строка 290: «До написания ядра выполняются измерения и проверочные реализации, которым не нужен работающий конвейер. Проверки, которым он нужен, — пилот на 50 сценариях и сравнение с базовым алгоритмом (строка 4), замер памяти
   при пяти параллельных расследованиях и повторный прогон из сохранённых ответов (строка 9) — выполняются на базовом трассировщике сразу после его постройки.» Строка 306: «После проверок, не требующих конвейера, строится базовый
   трассировщик: ввод TXID, история TRC20, проверка транзакций, граф движения средств.»

[11] MAJOR | A1, table row 4 «Оркестрация агентов» (line 58); same wording in A1 row 8 and in A2 item 9 (line 82)
   QUOTE: Собственный оркестратор на DBOS Transact; запасной путь — очередь Procrastinate и свои таблицы.
   PROBLEM: A1 and A2.9 present DBOS as the choice and Procrastinate as the fallback. G3, section 4 (item 5), section 8, A8 row 3 and question 11 all state the opposite tie rule: if both variants pass, the variant without DBOS is
   taken. So DBOS is kept only if the other variant fails. This also breaks the document's own definition of «условно» (the choice is fixed once the check passes). An owner approving A1 in question 1 approves DBOS; the rule they are
   asked about in question 11 makes the other variant the default outcome. The rule appears in five places, so the A1 and A2.9 wording should change.
   FIX: A1, строка 4: «Собственный оркестратор; слой сохранения шагов — DBOS Transact или очередь Procrastinate и свои таблицы: выбирает проверка Этапа 2, при равном результате берётся вариант без DBOS (G3). Шаги с моделью — через
   интерфейс LLMClient». A1, строка 8: «DBOS Transact на том же PostgreSQL либо очередь Procrastinate (выбор — по G3), без брокера; общий ограничитель запросов в HTTP-шлюзе». A2, пункт 9, последняя фраза: «Второй вариант проще —
   обычная очередь Procrastinate и свои таблицы; если проверки Этапа 2 проходят оба, берётся он (G3).»

[12] MAJOR | Section 1, Stage 2 list, item 1 (line 397); same in section 3, Stage 2 list (line 585)
   QUOTE: прогон синтетического графа на 1 000 адресов с порогом ≤ 5 минут и ≥ 99% успешных HTTP-ответов
   PROBLEM: Threshold contradiction between the sections and A8/A6. A8 row 1 requires the sources to fit «в свою долю 5 минут», and A6 sets that share at 240 seconds for data collection (240 + 20 + 20 + 15 + 5 = 300), adding that
   component checks are compared against these shares. Sections 1 and 3 give the data-source component the whole 5 minutes. A component that passes at 300 seconds leaves nothing for graph analytics, model steps and verification. A6 is
   the newer and more specific side; the section thresholds should change.
   FIX: Раздел 1, пункт 1: «прогон синтетического графа на 1 000 адресов с порогом: сбор данных не дольше 240 секунд (доля из A6) при ≥ 99% успешных HTTP-ответов». Раздел 3, строка 585: «Бюджет компонента: сбор данных для графа из 1
   000 адресов за 240 секунд (доля из A6) без исчерпания суточной квоты.»

[13] MAJOR | A2, item 3 (line 76); same figure in section 1 (line 373) and section 3 (line 560)
   QUOTE: хватает на 14–30 таких графов, а нужная скорость — 11–24 запроса в секунду
   PROBLEM: The 11–24 requests per second figure is 3 300–7 000 requests divided by the full 300 seconds. A6 gives data collection only 240 seconds, which makes the required average 3 300/240 ≈ 14 to 7 000/240 ≈ 30. This is the rate
   the owners would quote to TronGrid when asking for a Custom plan (A8 row 2), and it is understated by about 25% against the document's own time budget. A6 is the side that is right; A2.3 and the two section sentences should carry
   both numbers.
   FIX: A2, пункт 3: «Суточной квоты бесплатного плана (100 000 запросов) хватает на 14–30 таких графов, а нужная средняя скорость — 11–24 запроса в секунду, если отдать сбору данных все 5 минут, и 14–30 при доле сбора данных в 240
   секунд (A6).» Разделы 1 и 3: «нужная средняя скорость за 5 минут — 11–24 запроса в секунду, а в пределах доли сбора данных 240 секунд (A6) — 14–30».»

[14] MAJOR | A8, table row 8 «Тестовые данные и справочники» (line 301), against A6, criterion 9 (line 246)
   QUOTE: **Тестовые данные и справочники.** Не менее 50 сценариев и итоговый набор; реестр контрактов обменников и мостов
   PROBLEM: A8 puts the final (holdout) set among the first Stage 2 checks, before the core is written, with the criterion «набор заморожен до замеров». A6 says the final set of at least 20 scenarios «собирается после заморозки кода,
   хранится у вас и при разработке не используется». It cannot be both, and the owners are the ones who keep that set. A6 is the more specific and methodologically coherent side; A8 should change.
   FIX: Первая ячейка: «**Тестовые данные и справочники.** Не менее 50 сценариев основного набора (итоговый набор собирается после заморозки кода и хранится у вас — A6); реестр контрактов обменников и мостов; сверка справочника
   получателей с другого сетевого выхода, включая условия доступа TRM Beacon Network и портал cs.tether.to; три адреса OFAC, найденные только в зеркале». Критерий: «Основной набор заморожен до замеров; у каждой записи справочника —
   источник и дата проверки».»

[15] MAJOR | A5, paragraph under the fixed-cost table (line 179); echoed in A7 question 7
   QUOTE: Поэтому на 8 GB эти два сервиса выносятся наружу, и вариант с сервером 24 GB может оказаться дешевле.
   PROBLEM: A5 states as settled that on 8 GB the identity provider and the model-log viewer go to external services. G14, section 10 and question 18 offer self-hosted Logto or ZITADEL on 8 GB after a Stage 2 probe. Section 5 (Stage 2
   item 5) plans to measure Phoenix memory on exactly the 8 GB server, and question 18 names self-hosting as the default for the model log. An owner who wants credentials and model logs on their own server would conclude from A5 that 8
   GB is ruled out. G14 and the sections are the more precise side.
   FIX: Поэтому в расчёте для 8 GB эти два сервиса вынесены наружу; поместятся ли на таком сервере Logto или ZITADEL (G14) и Phoenix (раздел 5), покажет проба Этапа 2. Вариант с сервером 24 GB может оказаться дешевле.

[16] MAJOR | A6, criterion 4, row «Отдельный пакет доказательств для потенциальной биржи» (line 227), against section 12 (line 1373)
   QUOTE: Для каждого адреса с меткой биржи формируется отдельный пакет: переводы на адрес с TXID, суммами и временем
   PROBLEM: The Prompt 3 criterion is about a potential exchange. Section 12 builds a package for every address the report assigns «к бирже или к кандидатам в биржу». A6 narrows this to addresses that carry an exchange label, which
   excludes candidates. The two places then define the acceptance test («число пакетов равно числу таких адресов») over different sets. Section 12 matches the owner requirement; A6 should change.
   FIX: Для каждого адреса, который отчёт относит к бирже или к кандидатам в биржу, формируется отдельный пакет: переводы на адрес с TXID, суммами и временем, источник и дата метки, хеши в манифесте. Тест: число пакетов равно числу
   таких адресов в отчёте

[17] MAJOR | Section 9, «Инфраструктура и затраты», labour bullet (line 1112)
   QUOTE: Это отступление от принципа «свой код — только клей» (см. A9).
   PROBLEM: Broken reference. A9 is the risk table and has no row about the volume of own code or the «только клей» principle. The departure is stated in A2 item 10 and put to the owners in A7 question 1.
   FIX: Это отступление от принципа «свой код — только клей» (см. пункт 10 в A2 и вопрос 1 в A7).

[18] MAJOR | A7, question 18, last bullet (line 286)
   QUOTE: - шкала достоверности меток (раздел 2).
   PROBLEM: Question 18 is headed «Решения с вариантом по умолчанию», and every other bullet names its default. This one names neither the decision nor the default, so the owners cannot answer it without assembling the scale from
   scattered sentences in section 2 (line 459). Section 2 (Stage 2 item 4) requires the owners to approve the scale before measurement.
   FIX: - шкала достоверности меток: по умолчанию предварительные значения раздела 2 — события Tether 1.00, OFAC 0.95, кошельки из proof-of-reserves 0.90, метка одного провайдера 0.70, эвристика не выше 0.2–0.3 (раздел 2).

############################################################
# cold-read-part-a
VERDICT: No blockers on this lens: the first screen states the ask and the next step, Part A makes no promise of recovering funds, licence readings are hedged as an engineer's reading, and nothing instructs collecting personal data. It is not quite fit to send as is, because A7 does not yet carry every decision the owner has to make. The most important fix is to add decision points for the criterion readings adopted in A6 (the 99% metric, the composition of the 50 scenarios, the under-one-minute transaction exception) and to letter the multi-part questions 6, 7 and 13. Two Part A passages are also rosier than Part B: the Anthropic usage policy (A2 item 7) and the model limit having no margin in the typical case (A5).

[19] MAJOR | A6 (rows «≥ 99% успешного получения данных», «30 секунд / 2 минуты / 5 минут», «9. План тестирования»), A8 row 4; missing counterpart in A7 question 4
   QUOTE: Кейсы по заморозкам Tether и публичным инцидентам, а также тесты надёжности ведутся отдельно и в 50 не входят
   PROBLEM: A6 and A8 adopt readings of the owners' own Prompt 3 criteria and label some of them «Предложение»/«(предложение)»: the 99% metric counts TXIDs, not HTTP success or history completeness; only synthetic and own-transfer
   scenarios count toward the 50; the final set of 20 is to be held by the owners; a deadline passes with one overrun in 20; no-model-text reports are capped at 10%. A7 has no item asking the owner to accept these: question 1 covers
   only table A1 and question 4 only the share-vs-interval rule. The owner would answer 1–9 and the engineer would proceed on definitions nobody approved.
   FIX: Заменить вопрос 4 на: «4. **Правило подсчёта и прочтение критериев Промпта 3.** (а) Рекомендую для всех порогов Промпта 3 считать простую долю и публиковать доверительный интервал; для меток — точность положительных меток по
   всему набору плюс отчёт по классам, без обязательного порога для малых классов. Для сравнения: 50 сценариев из 50 дают нижнюю границу интервала 92.9%. Согласны? (б) Принимаете ли вы прочтения критериев из A6 и A8: «≥ 99% успешного
   получения данных» — доля TXID тестового набора с полученной и проверенной квитанцией, а доля успешных HTTP-ответов и полнота истории адреса публикуются отдельно; в 50 сценариев засчитываются только синтетические сценарии и наши
   собственные переводы, кейсы по заморозкам Tether и публичным инцидентам ведутся отдельно; итоговый набор из 20 сценариев хранится у вас; срок считается выполненным при не более чем одном превышении из 20 запусков; доля отчётов,
   вышедших без текста модели из-за её отказа, — не выше 10%. Если с каким-то прочтением не согласны — назовите своё.»

[20] MAJOR | A7, question 6 (and A6, paragraph «Предварительный бюджет времени для простой транзакции»)
   QUOTE: PDF и подписанный пакет доказательств готовятся отдельной задачей со своим сроком; какой срок для неё приемлем?
   PROBLEM: Question 6 holds two unlettered decisions (definition of the result; deadline for the PDF), so a one-word answer leaves one of them open. A third decision is missing altogether: A6 says the 30-second target is «недостижим
   по построению» for a transaction younger than a minute and that the wait «учитывается отдельно», but nowhere states whether that wait is excluded from the 30 seconds, and the owner is not asked. Section 13's protocol only records
   the wait in a separate field, so such runs would simply fail the criterion.
   FIX: «6. **Что считается результатом в сроках 30 секунд / 2 минуты / 5 минут.** (а) Предлагаю считать результатом проверенный JSON-отчёт в интерфейсе; PDF и подписанный пакет доказательств готовятся отдельной задачей. Согласны? (б)
   Какой срок готовности PDF и подписанного пакета приемлем? Моего предложения пока нет: скорость рендера не измерена. (в) Для транзакции моложе минуты срок 30 секунд недостижим: окончательное подтверждение сети отстаёт на 54–57 секунд
   (A6). Предлагаю: это ожидание в срок не входит и публикуется отдельной строкой, а приёмочные замеры идут на транзакциях старше минуты. Согласны?»

[21] MAJOR | A2, item 7 (compare section 5, «Лицензия и коммерческое использование» and «Ограничения и риски»)
   QUOTE: Поэтому OSINT ограничен сервисами и юридическими лицами, а до закрепления провайдера нужен юридический разбор.
   PROBLEM: Part A reads as if limiting OSINT to services and legal entities answers the policy concern. Section 5 says more: the policy also restricts prompting decisions in law-enforcement work, its exceptions «не покрывают частных
   расследователей и потерпевших», and «OSINT и отчёты для бирж и полиции — серая зона»; only short quotes were read. The owner deciding from Part A does not learn that the core deliverable (reports for exchanges and police), not just
   the OSINT agent, is in the grey zone for the main model provider.
   FIX: «7. **Политика использования Anthropic затрагивает продукт.** Редакция, вступающая в силу 2026-11-12, ограничивает установление личности людей по псевдонимной активности, сбор профилей и подсказку решений в правоохранительной
   деятельности; её исключения, по нашему прочтению, не покрывают частных расследователей и потерпевших (прочитаны короткие цитаты, не полный текст). Поэтому OSINT ограничен сервисами и юридическими лицами, но отчёты для бирж и полиции
   остаются серой зоной: до закрепления провайдера нужен юридический разбор (вопрос 9, пункт а).»

[22] MAJOR | A5, bullet «Тяжёлый случай» under «Как это работает (G17)»; bears on question 5(а)
   QUOTE: Оценка $0.57 на модели выше лимита $0.40 и сама не является верхней границей
   PROBLEM: Part A presents the downgrade (Haiku only at 70%, report without model text at 100%) under the heading «Тяжёлый случай», as if it were the exception. The typical estimate in the same table is $0.40, equal to the limit, and
   70% of the limit is $0.28, so by the document's own numbers the 70% threshold fires in a typical investigation. Section 5 says this outright («запаса над типичной оценкой нет»); Part A does not, yet question 5(а) asks the owner to
   accept the $0.40 limit.
   FIX: Заменить пункт на: «- **Запаса нет и в типичном случае.** Типичная оценка моделей ($0.40) равна лимиту, поэтому порог 70% ($0.28) по расчёту срабатывает уже в типичном расследовании: оставшиеся шаги идут на Haiku 5.5. Оценка
   тяжёлого случая ($0.57) выше лимита и сама не является верхней границей: она не учитывает оплачиваемые отказы модели и рост входа в многоходовых циклах. При 100% лимита отчёт выпускается без текста модели, полученные результаты
   сохраняются.»

[23] MAJOR | Preamble, paragraph «Про лицензии и условия использования»; A7 question 9
   QUOTE: Спорные случаи вынесены в вопрос 9.
   PROBLEM: Broken reference. Question 9 lists five legal opinions (Anthropic policy, allocation methodology, templates, data-protection assessment, control payments) and none of them concerns licences or terms of service. The licence
   cases are in A2 items 2 and 8 and question 14, and A2 item 8 says «подтверждает юрист» without any matching item in question 9.
   FIX: В преамбуле: «Спорные случаи перечислены в A2 (пункты 2 и 8); кто и когда даёт по ним юридическое заключение — вопросы 9 и 14 из A7.» В вопросе 9 после пункта (д) добавить: «(е) лицензии и условия сервисов из A2 (пункты 2 и 8):
   Grafana (AGPL-3.0), psycopg 3 (LGPL-3.0), Arize Phoenix (Elastic License 2.0), условия TronGrid и TronScan.»

[24] MAJOR | A1 rows 4 and 8, A2 item 9 — against G3, A8 row 3 and A7 question 11
   QUOTE: Собственный оркестратор на DBOS Transact; запасной путь — очередь Procrastinate и свои таблицы.
   PROBLEM: A1 and A2 present DBOS as the choice and Procrastinate as the fallback («запасной путь»), i.e. used if DBOS fails. G3, A8 row 3 and question 11 state the opposite preference: if both pass, the variant without DBOS is taken,
   so DBOS is used only when the other variant fails. An owner approving table A1 «целиком» approves DBOS, then is asked in question 11 to approve a rule under which DBOS loses every tie.
   FIX: Строка 4 таблицы A1, столбец «Выбор»: «Собственный оркестратор. Слой сохранения шагов — DBOS Transact либо очередь Procrastinate и свои таблицы: выбирает сравнение на Этапе 2, при равном результате берётся вариант без DBOS (G3,
   вопрос 11). Шаги с моделью — через интерфейс LLMClient». Строка 8: «Очередь на том же PostgreSQL, без брокера: DBOS Transact либо Procrastinate — по итогам того же сравнения (G3); общий ограничитель запросов в HTTP-шлюзе». Последнее
   предложение A2, пункт 9: «Вариант без DBOS проще: обычная очередь Procrastinate и свои таблицы; если на Этапе 2 проверки проходят оба варианта, берём его (вопрос 11).»

[25] MAJOR | A7, question 18, first and last bullets; A5, paragraph after the fixed-cost table
   QUOTE: шкала достоверности меток (раздел 2).
   PROBLEM: Question 18 is headed «Решения с вариантом по умолчанию», but two bullets state no default. The confidence-scale bullet is neither a question nor a default, though section 2 has preliminary values. The identity-provider
   bullet does not mark which option is the default, and for an 8 GB server it says «иначе Logto после пробы» (self-hosted) while A5 says on 8 GB the identity provider «выносятся наружу» and prices it as an external service.
   FIX: Первый пункт: «поставщик входа: по умолчанию — на своём сервере (Keycloak на сервере от 16 GB; на 8 GB — Logto после пробы, а если он не помещается по памяти — внешний сервис, как посчитано в A5); альтернатива — сразу внешний
   сервис, где учётные данные хранит третья сторона. ZITADEL рассматривается, только если вы допускаете лицензию AGPL (раздел 10);» Последний пункт: «шкала достоверности меток: по умолчанию — предварительные значения раздела 2 (события
   Tether 1.00; OFAC 0.95; кошельки из proof-of-reserves 0.90; одна метка провайдера 0.70; эвристика не выше 0.2–0.3).» В A5: «Поэтому в расчёте для 8 GB эти два сервиса вынесены наружу (лёгкий поставщик входа на своём сервере возможен
   только после пробы, G14), и вариант с сервером 24 GB может оказаться дешевле.»

[26] MAJOR | A7, question 7
   QUOTE: Отдельно: согласны ли вы оплатить стенд замеров с выделенными ядрами (около €261 за год)?
   PROBLEM: Two separate money decisions (production server size and a 12-month commitment; a €261 benchmark stand) sit in one unlettered item, so «7 — да» does not say which was approved. «доли украденного времени» is also unexplained
   in Part A; the gloss exists only in section 13.
   FIX: «7. **Сервер и стенд замеров.** (а) Рабочий сервер. Рекомендую сразу OVH VPS-4 (24 GB) с оплатой за 12 месяцев: €19.96/мес, около €240 за год. Альтернатива — 8 GB за €8.49/мес без обязательств, с выносом части сервисов наружу
   (A5). Какой вариант выбираете? (б) Стенд замеров с выделенными ядрами: около €261 за год. Без него сроки из критерия производительности нельзя измерить воспроизводимо; замена — замеры на рабочем сервере с записью модели процессора и
   доли процессорного времени, отнятого соседями по серверу. Оплачиваете стенд?»

[27] MAJOR | A7, question 1 (compare A3, table «Как десять агентов из Промпта 1 ложатся на эту схему», and A2 item 10)
   QUOTE: Принимаете ли вы таблицу A1 целиком, включая объём собственного кода (A5), или какие строки требуют пересмотра.
   PROBLEM: The engineer asks explicit confirmation for one departure from the brief (own code beyond glue) but not for the parallel one in A3: order of steps is set by code, two of the ten agents (Blockchain Intelligence, Evidence
   Verification) run with no model, and only OSINT has tools. If Prompt 1 describes ten AI agents, this is a reinterpretation of the owners' concept that question 1 does not cover; I have not seen Prompt 1, so the lead should confirm
   it is a departure. The item also carries two decisions unlettered.
   FIX: «1. **Согласование стека.** (а) Принимаете ли вы таблицу A1 целиком или какие строки требуют пересмотра? (б) Подтверждаете ли объём собственного кода (A5) — отступление от принципа «свой код — только клей»? (в) Принимаете ли
   раскладку десяти агентов из A3: порядок шагов задаёт код, Blockchain Intelligence и Evidence Verification работают без модели, инструменты есть только у OSINT?»

[28] MAJOR | A5, «Разовые расходы Этапа 2» (third bullet and «Итого») — against A8 row 4 and section 5 «Инфраструктура и затраты»
   QUOTE: Оценка качества AI-слоя: $20–145 за один запуск 50 сценариев.
   PROBLEM: The Stage 2 total ($170–500) counts one evaluation run. Section 5 prices one pass at $20–29 and a run with 3–5 repeats at $60–145, and A8 row 4 plans a pilot plus comparison of two routing schemes and three strong-model
   variants, i.e. at least four configurations. The total the owners would budget from is therefore understated against the plan in the same Part A. The replacement figures below are my arithmetic from section 5's per-run numbers (4 ×
   $60–145), not figures from the document.
   FIX: «- Оценка качества AI-слоя: $20–29 за один проход 50 сценариев, $60–145 за прогон с 3–5 повторами. Проверка 4 в A8 сравнивает не менее четырёх конфигураций (две схемы маршрутизации и три варианта сильной модели, одна
   конфигурация общая) — до $240–580; в пакетном режиме вдвое меньше.» и «- Итого без юриста, NOWNodes и внешнего хоста для сверки справочника получателей: около $170–500 при одном прогоне оценки качества и около $390–930 при четырёх;
   плюс €261.»

[29] MAJOR | Preamble, paragraph «Откуда данные»
   QUOTE: Собранный документ прочитали четыре независимых рецензента; их замечания внесены.
   PROBLEM: The previous sentence says the audit passes were done by AI agents; this one does not say what the reviewers were, and «независимых рецензента» reads as human peers. If they were AI agents (I infer so from the process but
   cannot confirm it from the document), the owner would overestimate the assurance behind the text. The count is also stale after this final round. The lead should confirm before applying the fix.
   FIX: «Собранный документ прочитали независимые рецензенты — тоже AI-агенты, не люди; их замечания внесены. Специалист-человек и юрист документ не проверяли.»

[30] MAJOR | Part B, section 9, «Инфраструктура и затраты», bullet «Трудозатраты»
   QUOTE: Это отступление от принципа «свой код — только клей» (см. A9).
   PROBLEM: Broken reference left from before Part A was rewritten: A9 is the risk table and does not mention this departure. It is now in A2 item 10 and question 1 of A7.
   FIX: «Это отступление от принципа «свой код — только клей» (см. A2, пункт 10, и вопрос 1 в A7).»

[31] MAJOR | A7, intro line and question 3
   QUOTE: По умолчанию до вашего ответа действует (г): в модель уходят только публичные данные блокчейна.
   PROBLEM: The intro says questions 1–9 block the start of Stage 2 and that defaults apply only to the remaining questions, yet blocking question 3 carries a default «до вашего ответа». The owner cannot tell whether question 3 must be
   answered now; if they rely on the default, the engineer is still blocked by the first-screen rule «До этого к Этапу 2 я не перехожу».
   FIX: Заменить последнее предложение вопроса 3 на: «Начало Этапа 2 блокирует только выбор на время измерений: если вы не готовы решать сейчас, подтвердите (г) как временный вариант — в модель уходят только публичные данные
   блокчейна.»

[32] MAJOR | A6, row «Отдельный пакет доказательств для потенциальной биржи» — against section 12, «Ограничения и риски», «Пакет для потенциальной биржи»
   QUOTE: Для каждого адреса с меткой биржи формируется отдельный пакет
   PROBLEM: Part A limits the package to addresses labelled as an exchange. Section 12 builds it for every address «который отчёт относит к бирже или к кандидатам в биржу». The criterion speaks of a potential exchange, so the two parts
   disagree on whether candidates get a package and on what the test counts.
   FIX: «Для каждого адреса, который отчёт относит к бирже или к кандидатам в биржу, формируется отдельный пакет: переводы на адрес с TXID, суммами и временем, источник, дата и достоверность метки, хеши в манифесте. Тест: число пакетов
   равно числу таких адресов в отчёте»

[33] MAJOR | A7, question 13
   QUOTE: Достаточно ли лимита около 1 500 узлов и 3 000 рёбер на экране? На каком оборудовании работают следователи?
   PROBLEM: Four separate asks in one unlettered item (element limit, hardware, smoothness threshold, maximum layout time). The engineer's default for hardware exists in section 9 («ноутбук со встроенной графикой») but is not stated
   here, and the layout-time ask has neither a default nor a note that there is none.
   FIX: «13. **Карта.** Большие графы показываются свёрнутыми, с раскрытием ветвей по запросу; все узлы одновременно не показываются. (а) Достаточно ли лимита около 1 500 узлов и 3 000 рёбер на экране? (б) На каком оборудовании
   работают следователи? По умолчанию — ноутбук со встроенной графикой. (в) Порог приёмки по плавности: по умолчанию 30 кадров в секунду на 1 000 узлов с подписями; подтвердите или назовите свой. (г) Предельное время расчёта раскладки:
   назовите; моего ориентира нет.»