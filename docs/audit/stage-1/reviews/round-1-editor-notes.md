
## tron-data
DECLINED:
  - [4] concerns section 2; section 1 only points to раздел 2 for the registry of exchanger and bridge contracts
  - [7] concerns sections 3 and 6
  - [31] A8 only; the second-index probe with its criterion is already Stage 2 item 4 of section 1
  - [42] concerns sections 14, 11, 8; section 1 is already the reconciled position (final isBlackListed at the independent node)
  - [43] concerns sections 3, 5, 7, 12, 13; G-references used in section 1 (G4, G5, G6, G11, G17) were checked against the final decision texts
  - [88] concerns sections 3, 4, 5, 14; in section 1 only the V5 hedging was applied (TronScan 429 body, tronpy keys, TronGrid changelog stated as observed)
  - [3] partly: the reviewer's five-item list was reduced to balances, time and contracts because transactions and token transfers are already in the Решение paragraph; the label 'Промпт 0' was not used and the method is written
  as getcontract (the dossier names it without the wallet/ prefix; it was never called live)
  - [9] partly: 'коммерческое использование прямо не разрешено' replaced by 'допустимо ли, из условий неясно', which is what the dossier records
  - [56] partly: the proposed E-edges formula (71 rps, 4-5 graphs a day) was not used because R1 fixes the numbers; only the caveat that more edges mean proportionally more requests was added
  - [72] partly: the UI status text 'ждём подтверждения сети' was not added (not in R10; belongs to the interface section if adopted)
  - [10], [48], [53], [57], [75], [82], [91], [92], [97] Part A, A-decisions and 'Как читать' portions are left to the lead engineer
NOTES FOR LEAD:
  - 99% criterion: section 1 now defines it as proposed in issue [53] (share of test-set TXIDs for which the receipt and Transfer events were obtained and verified, over all supported existing TXIDs; HTTP success share and
  address-history completeness are published separately and are outside the 99%). A6 must carry the same definition; I dropped the clause 'считает модуль проверки доказательств по журналу шлюза' for length, add it in A6 if wanted.
  - R1 arithmetic: with TronGrid at 6-7 thousand and one receipt per TXID at the node (3 000-4 000 in the dossier) the upper total is about 11 thousand, slightly above the '6-10 тыс.' of R1. Section 1 gives the R1 values and says
  'остальные — квитанции на узле' without a node figure in that sentence; '3 000-4 000 проверяемых TXID' stays only in the risks bullet. Keep A2 item 3 worded the same way or change the total to 6-11 thousand everywhere.
  - Paid production reserve node (G5) adds a fixed cost that was not in the old text: $10-49 per month (Nodit Basic $10, GetBlock Starter $49; both prices come from the re-check part of the dossier, terms of use not read). A5
  should include it. The GetBlock free-tier figures were removed from section 1 as no longer relevant.
  - Stage 2 list of section 1 now has 6 items and the contract registry is still item 6, so references 'раздел 1, пункт 6' stay valid. A8 should mirror the new content: Chainstack independence check (item 3), written permission to
  pass raw responses and receipts to clients plus reading GetBlock/Nodit terms and a written answer from PublicNode (item 2), event_index criterion on at least 1 000 TXID (item 5), live check of getcontract (item 5).
  - Solidified lag: R10 values used (18-19 blocks, 54-57 s). The dossier also records that TronGrid rows with only_confirmed=true lagged about 69 s in the probe, which is where the old '54-69 с' came from; 'моложе примерно минуты'
  covers it, but if Part A states a hard number for the primary history source, 69 s is the measured one.
  - Length is about 13 650 characters against the 13 000 target, after trimming. Removed to make room: the Dune/BigQuery table row (now only in Stage 2 item 4), the line 'TRON не поддерживают GoldRush, Etherscan API v2, Allium
  Realtime APIs', the re-check web-search caveat (assumed to live in A10 per issue [91]), the registry-not-built and REVERT risk bullets (kept as Stage 2 items 5-6), the Lite-node, search_internal, 82=82 log-count, first-blacklist
  block number and SQD public-tier details, and the TronScan transaction-info remark. If Part A cites any of these, drop it there or ask for it back. 'Стандартное расследование' stays 'около 40 адресов' (the base of the request
  calculation), compatible with 40-45 in A5.

## labels-risk
DECLINED:
  - [12] concerns A1 and A7 only; section 2 keeps the confidence scale as an owner decision (Stage 2 item 4)
  - [74] concerns A7 only
  - [19] effort total belongs to A5
  - [81] concerns A9 and A7
  - [35] concerns A5, A1 and section 13
  - [71] concerns A5, A7 and section 13
  - [36] concerns section 14 and A6; section 2 has no scenario count
  - [43] wrong G references are in other sections; the G5, G7, G17 references added here were checked against the final decision text
  - [45] concerns A8
  - [73] concerns sections 3, 4 and 14
  - [88] concerns sections 3, 4, 5 and 14
  - [4] partly: SunSwap and JustLend names and the pointer «раздел 1, пункт 6» not used - neither is in the dossier or current text; reference is to «раздел 1» only
  - [69] partly: single size «400» not used - R4 sets 400-500 for the first version and 600+ as target
  - [68] partly: the general rule for other thresholds and the 50-of-50 = 92.9% example left for A7
NOTES FOR LEAD:
  - TronGrid without a key: the re-check for this area got HTTP 429 on the second consecutive request to the events endpoint (allowed_rps=1), while R7 gives 3 requests per second. Section 2 now states both, attributing 3 rps to
  section 1; please confirm section 1 does not contradict this.
  - Contract registry (issue 4): the dossier has no named sources, effort estimate or example projects for it. Section 2 says its assembly and curation are «не оценены» and points to «раздел 1» without an item number. Please check
  that section 1 really describes it, add an estimate to A5 if you have one, and note that G7 says «обменников и мостов» while section 2 says «обменников (DEX), мостов и сервисов».
  - A7 needs three items that section 2 now refers to as «вопрос — в A7» without a number: (a) lawyer's answer on control payments to services and casinos for the label test set; (b) who opens KYC-verified exchange accounts for
  control deposits; (c) the general rule for percentage criteria - simple proportion with interval or lower bound of the interval (50 of 50 gives a Wilson lower bound of 92.9%).
  - Budget consistency for A5 and A7: at 4 MistTrack calls ($0.80) only $0.20 remains under the $1.00 hard limit, below the $0.40 model limit of G17 - section 2 says so explicitly. Also the $20 pack is only 100 calls, so measuring
  the whole 400-500 test set needs the $10 trial (its limits are not verified) or the $150 pack; A5 one-off costs should match.
  - OFAC rule for section 14 and G7: section 2 now states that an address found only in the 0xB10C mirror (3 of 340) gets no «OFAC SDN» label until confirmed in the primary file, and that the mirror is checked daily as a control.
  The figure 337 is taken from G7; section 2 has no own recount.
  - Length was estimated by hand, not measured (no code run): about 14 000 characters, above the 13 000 target because of the required additions. Already cut: the development sandbox bullet (Bitquery trial details, MistTrack
  sandbox), most of the deferred-subscriptions bullet, the «обзор рынка неполон» bullet (folded into the Bitrace/BitOK table row), the Bitquery bullet in project state. If other sections cite section 2 for the MistTrack sandbox or
  the Bitquery trial limits, those facts are no longer here.

## tracing-engines
DECLINED:
  - [19] concerns Part A (A5 effort total); section 3 keeps its own 2-3 person-weeks estimate unchanged
  - [81] concerns Part A (A9 row and A7 question 1)
  - [35] concerns Part A cost table and section 13; section 3 already states Bitquery archive add-on and that Bitquery is removed from the plan
  - [97] glossary belongs to «Как читать» in Part A; only wording inside section 3 was aligned
  - [56] the per-edge formula (1 300 + E) belongs to section 1 and conflicts with the resolved R1 range; section 3 uses R1
  - [69] proposed single size of 400 addresses not used: R4 fixes 400-500 first version and 600+ target
  - [26] proposed phrase «экспорт меток в JSON-отчёт» not used: not supported by R3 or the dossier; replaced by «нужно письменное подтверждение» with reference to section 2
  - [48] definition of «стандартное расследование» (40-45 addresses) is for A5; section 3 only removed its own «30 адресов» size from the Stage 2 check
NOTES FOR LEAD:
  - Section 3 now states the 99% criterion as «доля TXID тестового набора, по которым получены и проверены квитанция и события Transfer» and treats two-source history completeness as an additional metric outside the 99% (from
  issue [53]); A6 must carry the same definition or section 3 needs adjusting.
  - Section 3 last Stage 2 item fixes the AI-vs-baseline comparison as a paired run at equal budget with metric «полнота найденных конечных адресов» and consequence «остаётся в отчёте о метриках как невыполненный пункт критерия»;
  A6 row and section 14 should use the same metric, threshold and consequence.
  - Section 3 refers to «раздел 13» for the single end-to-end acceptance measurement (R11) and calls its own TronGrid speed check a component budget; confirm section 13 actually holds the measurement protocol, otherwise change the
  reference to A6.
  - Scenarios: section 3 says 25+ counted scenarios are designed (20 synthetic + 5+ own) and that own scenarios are made by our own transfers on the main network (R5). The first-pass research had planned the own scenarios in a
  test network, so the '5+ own' figure is carried over from that plan; A6 should say the same and not mention a test network.
  - Section 3 cites R2 as «$0.40 типичное и $0.57 тяжёлое расследование (раздел 5)» next to the default model limit $0.40 (G17): the heavy estimate exceeds the default limit, which A5 should make explicit. The size «30 адресов»
  survives only as a price illustration (30 адресов = $3-6), not as the definition of a standard investigation.
  - For length (V9) section 3 dropped the java-tron recommended configuration (16+ cores / 4 TB), the upper MistTrack price ladder ($30 000 per 1 000 000 calls) and Arkham heavy-endpoint detail in «Состояние»; the Arkham note per
  R6 (site did not open, data read from arkm.com/llms.txt) sits under the alternatives table. Estimated length is about 13 500-14 000 characters, slightly above the 13 000 target.

## agent-orchestration
DECLINED:
  - [18][33] касаются раздела 8 (интеграция pydantic-ai с DBOS); в р.4 формулировка уже согласована с G13
  - [19][81] итог трудозатрат — часть A (A5, A9); оценки 2–3 и 1.5–2.5 человеко-недели в разделах сохранены
  - [45] дополнения A8 — часть A; проверки повторного прогона в р.4 и р.11 оставлены
  - [12][38][74] сам список A7 — часть A; в разделах только уточнены пункты решений владельцев
  - [62] строки A6 и вопрос A7 — часть A; в р.11 добавлены только сами тесты
  - [70] столбцы «Критерий / При провале» в A8 — часть A; порог отказов модели и пороги карты не относятся к р.4 и р.11
  - [1] текст G16 и строка A6 — часть A
  - [42] части про разделы 14 и 8 — не мои разделы
  - [43] перечисленные неверные ссылки находятся в разделах 3, 5, 7, 12, 13
  - [44] части про разделы 1, 2, 3, 6, 10 и A10 — не мои разделы
  - [48] определения в A5 и «Как читать», интерфейсы в разделах 1–3 — не мои разделы
  - [88] части про разделы 3, 5, 14; предложенное «по опубликованному advisory проекта» для LiteLLM не подтверждается: первичный источник перепроверки — issue #24518, так и написано
  - [60][89] предложенное рецензентом значение $0.45 заменено на $0.40 по R2 и G17
  - [97] определения терминов в «Как читать» и правки A1/A5/A6 — часть A
NOTES FOR LEAD:
  - Разделы 4 и 11 ссылаются на «часть A, A8» как на место описания единственного сквозного приёмочного замера (R11); р.11 п.1 добавляет проверку смешанной нагрузки с возможным приоритетом интерактивных запросов в ограничителе
  шлюза. Если в A8 этого не будет, ссылки и пункт нужно поправить.
  - Правило выбора в р.4 п.5: «если оба варианта проходят проверки разделов 4 и 8 — более простой (по оценке перепроверки — вариант без DBOS); если один — он». Случай «не прошёл ни один» не определён ни в G3, ни в резолюциях;
  раздел 8 пишет «при провале — Procrastinate». Нужно одно правило в A8 и в разделе 8.
  - Тяжёлый случай $0.57 превышает лимит моделей $0.40 (G17). В р.4 сказано, что тогда действует снижение из G17 (с 70% только Haiku 5.5, со 100% отчёт без текста модели); ориентиры Этапа 2 — $0.30 для схемы «только эскалации» и
  $0.40 для схемы G13. A5 и раздел 5 должны говорить то же.
  - Для A7: из р.4 — кто вправе повышать лимит после паузы (пользователь или оператор) и перечень действий с подтверждением человеком (по умолчанию — любая отправка обращений, платформа готовит только черновики; опора — первичное
  исследование); из р.11 — MCP-сервер платформы для клиентов (по умолчанию нет) и ручной доступ аналитиков через сторонние MCP в среде разработки (я поставил «по умолчанию — нет», в резолюциях этого значения нет — подтвердить).
  - LiteLLM: в р.4 написано «по issue #24518 в репозитории проекта» (так подтверждено при перепроверке) и добавлен источник; раздел 5 должен использовать ту же формулировку, а не «advisory». Заменяемость слоя DBOS в р.4 теперь
  «средняя» (JobRunner) — строка 4 таблицы A1 должна совпасть. pgqueuer из р.4 убран (G3 называет только Procrastinate, раздел 8 оценивает PgQueuer отрицательно).
  - Раздел 8 пишет, что критерии проверочной реализации «войдут в набор из 50+ сценариев» — это противоречит R5; в р.4 тесты надёжности считаются отдельно от 50. Длину разделов я оценивал вручную (код не запускался): оба близки к
  13 000 знаков, стоит проверить счётчиком.

## llm-models
DECLINED:
  - [6] числа «cost_limit срабатывает после превышения; 55 minor-релизов за 15.4 недели; 16 advisories» не подтверждаются источником фактов этого направления — в строке таблицы дана поддержанная формулировка
  - [28] «$0.05–0.16 за 10–20 запросов»: цен Brave и Tavily в источнике фактов нет, а G17 фиксирует 10 запросов — сумма не указана, дана ссылка на раздел 14
  - [49][60][76][89] лимит моделей $0.45 из предложений рецензентов заменён на $0.40 по G17
  - [1] текст G16 и строка A6 — Часть A
  - [12][38][74] вопросы A7 — Часть A; в разделе 5 только вариант по умолчанию и пункт 9
  - [19] сводка трудозатрат в A5 — Часть A
  - [44] замечания относятся к разделам 1, 2, 3, 6, 10 и A10
  - [45] дополнения A8 — Часть A (пункты 3, 4, 8 раздела 5 сохранены)
  - [46] статусы и лицензии A1, вопрос 13 в A7 — Часть A
  - [48] определение стандартного расследования в A5 и абзац «Как читать» — Часть A
  - [92] формулы «разрешено без условий» в разделе 5 не было; оговорка об инженерном прочтении переносится в «Как читать» (Часть A)
  - [97] словарь терминов в «Как читать», правки A1, A5, A6 — Часть A
NOTES FOR LEAD:
  - Длина: раздел около 14 400 знаков при цели 13 000 (исходный был 13 144). Обязательные дополнения дали примерно +1 900 знаков. Убраны: опровергнутый тезис о «самых дешёвых моделях», счёт «26 утверждений», цены Mistral и Grok за
  1M, контекст OpenAI 1.05M / 922K, отказ Sonnet от принудительного tool_choice, лимиты токенов в минуту, детали тарифа Langfuse Core, упоминание потоковой выдачи. Если предел жёсткий, с наименьшей потерей снимаются строки таблицы
  «promptfoo, DeepEval» и «Модели на своём GPU» и фраза про Vertex AI / Bedrock (около 430 знаков).
  - Pydantic AI: числа рецензента (cost_limit, 55 релизов, 16 advisories) в раздел не внесены — в источнике фактов этого направления их нет. Если они есть в разделе 4, ссылка «G13, раздел 4» достаточна; A1 строка 4 и A8 п. 4
  должны говорить «LLMClient, под ним Pydantic AI либо официальные SDK». Критерия выбора между ними в G13 нет — в пункте 8 раздела 5 написано «по результату выбирается реализация».
  - Веб-поиск: раздел 5 больше не называет сумму и не упоминает встроенный поиск Anthropic за $0.01; он отсылает к разделу 14 за ценами. В A5 и разделе 14 должна стоять цена 10 запросов; прежняя формула «$0.10–0.25 резерв на web
  search» нигде не должна остаться.
  - Бюджет: в разделе 5 лимит моделей $0.40 равен типичной оценке (запаса нет), тяжёлый случай $0.57 упирается в лимит. Потолок Anthropic Start $500 пересчитан как 1 250 расследований по $0.40 без прогонов оценки качества — фразу
  из замечания [50] про «$400–570» в A5 нужно согласовать. Раздел 5 ссылается на раздел 4 как на место описания механизма резервирования.
  - Время: раздел 5 утверждает, что на пути простой транзакции (30 с) нет вызовов Sonnet и effort high, а схемы прогреваются при развёртывании и не реже раза в 24 ч — то же должно стоять в бюджете времени A6. Ссылка «приёмка —
  одно сквозное измерение, раздел 13» предполагает, что протокол замера описан в разделе 13.
  - Журнал вызовов моделей: по умолчанию Phoenix на своём сервере; Langfuse Cloud EU — только с разрешения владельцев и с маскированием на стороне клиента. С этим должны совпасть A1 строка 5 (лицензия Phoenix — Elastic License
  2.0), вопрос A7 о размещении журнала, ZDR и языке отчётов и A8 п. 4 (сравнение трёх вариантов сильной модели, чтение договора OpenAI и закрепление версии, сравнение двух схем маршрутизации, сравнение Phoenix и MLflow).

## graph-store
DECLINED:
  - [19] concerns A5 only; section 6 keeps its own estimate (test stand 1-2 weeks, not verified; scenario labelling not estimated)
  - [12] A1/A7 text is Part A; section 6 only keeps its owner decisions visible in 'Что проверить'
  - [38] A7 list is Part A; no section-6 text to change beyond keeping the two owner decisions
  - [74] A7 list is Part A
  - [88] concerns sections 3, 4, 5, 14; in section 6 only V5 wording was tightened (DGL issue described as an open report, Memgraph licence change stated as read from two licence texts)
  - [5] partly: reviewer's label for Raphtory ('graph ML') not used - the fact source describes it as an in-memory temporal graph engine for analytics, GPL-3.0, only macOS builds on PyPI for 0.18.5
  - [57] partly: the A8 paragraph and the mixed-load / interactive-priority wording belong to Part A and section 4, not added here
NOTES FOR LEAD:
  - A7 must carry the two owner decisions section 6 still raises: (a) the rule 'graph DB only at a 3x p95 gain or if the base variant misses the time targets'; (b) on-prem delivery (legal review of GPL and LGPL components) and
  whether MVP needs multi-step queries over the whole accumulated graph and Cypher for analysts.
  - Section 6 now points to section 13 for the single end-to-end acceptance run (R11) and says the graph layer must fit 'its share of the time and memory budget, set before the measurement'. Nobody has set that share numerically:
  section 13 or A8 must define the per-component budget, otherwise the criterion is still unmeasurable.
  - Section 6 cites section 1 for the R1 figures (about 3 300 vs 6-7 thousand TronGrid requests per 1 000-address graph, depending on whether event_index can be taken from the node receipt) and G6 for the key, the zero-value-
  transfer rule and the 1 000-TXID check; section 1 and A2 item 3 must contain exactly these numbers.
  - The graph-ML task wording ('проверить, даёт ли обучаемая модель измеримый выигрыш над базовым алгоритмом в оценке и ранжировании адресов-кандидатов') is a design statement derived from the first-pass research (output: scores
  and ranking, marked as not evidence); confirm it matches Part A. PyTorch Geometric Temporal 0.56.2 (MIT) was added to the DGL row as a second ML alternative from the fact source.
  - The bullet reconciling the first-pass recommendation (graphology + sigma.js) with section 9 (Cytoscape.js) was removed from section 6 as drafting narration; only 'render speed at 100 000 nodes not measured (раздел 9)' remains.
  If the fact 'sigma.js 4.x line released 2026-10-08' matters, it belongs in section 9.
  - Section 6 names both drivers (asyncpg Apache-2.0, psycopg 3.3.6 LGPL-3.0-only) without saying which is the default; section 7 and A1 row 7 must state the chosen driver. Section is about 14 000 characters after the required
  additions (original 13 673), slightly over the 13 000 target; the Sources list (about 1 150 characters) is the only block left that could be shortened without losing content.

## backend-db-queue
DECLINED:
  - [19] Part A (A5) effort summary; sources hold no estimates for sections 7 and 10, none invented
  - [32] A8 item 3 is Part A; sections 7, 8, 10 already carry these three checks
  - [38] A7 additions are Part A; section 10 keeps the owner decisions with the G14 default
  - [74] A7 item 17 is Part A; sections 8 and 10 now state the default variants
  - [40] concerns section 4 and A1 row 4; section 8 already rates the DBOS layer «средняя»
  - [41] Part A statements (A9, A2); section 8 text already matches the corrected wording
  - [45] A8 additions are Part A; the IdP probe and RLS overhead checks stay in sections 10 and 7
  - [46] A1 status and licence columns and A7 question 13 are Part A
  - [48] TransferSource/LabelSource do not occur in 7, 8, 10; definitions go to A5 and «Как читать»
  - [79] Part A wording; section 10 uses the final G14 text
  - [88] sections 3, 4, 5, 14 only
  - [93] A2 item 9 is Part A
  - [55] the per-step time-budget table belongs under A6 (lead)
  - [2] partial: the «75 GB» disk figure not written - absent from this area's dossier, section text and resolved list
  - [18]/[33] partial: «импортирует приватные модули DBOS» and «DBOSAgent deprecated» not restated - absent from this area's dossier; section 8 points to section 4 and G13
  - [42]/[43]/[44] parts for sections 1, 2, 3, 5, 6, 11, 12, 13, 14 and A10 - other editors
NOTES FOR LEAD:
  - Section 7 says report PDF and evidence-package files sit on the server volume and are backed up by restic, the database by pgBackRest, both to Backblaze B2 (section 13). This is the reviewer's proposed design, not a dossier
  fact: confirm it matches sections 12 and 13. The disk size (75 GB in issue [2]) is left out; insert it from section 13 if wanted.
  - Section 8 no longer explains why the ready pydantic-ai/DBOS integration is rejected (private DBOS modules, DBOSAgent deprecated): those facts are not in this area's dossier. It refers to section 4 and G13, so section 4 must
  carry them.
  - G3 says «берётся более простой» without naming which variant is simpler; issues [70] and [93] assume the one without DBOS. Section 8 repeats the G3 wording. A8 item 3 should name it, bearing in mind that the variant without
  DBOS needs its own checkpoint and limiter code (section 8 table).
  - Sections 7, 8 and 10 point to «протокол — раздел 13» for the single end-to-end acceptance run (R11); section 10 carries the R10 interval and the 18-19 block lag. Section 13 or A8 must actually contain that protocol. Section 7
  also points to section 12 for the timestamp service and to section 13 for backup storage cost.
  - Part A alignment: A1 row 10 status «принято; поставщик входа — условно», licences now Pydantic MIT and uvicorn BSD-3-Clause; A1 row 7 should name psycopg 3 as LGPL-3.0-only; A2 item 9 «всё устранимо настройкой» conflicts with
  section 8 (automatic takeover of a crashed worker exists only in paid Conductor; with one worker it is closed by restart, not verified in practice).
  - Wording dropped or changed for V5/V7: «на венчурном финансировании» removed from section 8 (no observed source in the dossier); section 10 no longer cites G14 for jurisdiction (final G14 does not mention it) and uses 1.25-1.36
  GB everywhere; «эталонный сервер G12» became «минимальная конфигурация G12 (8 GB)», with Keycloak as the default on the recommended 24 GB start.

## frontend-graph-viz
DECLINED:
  - [19] абзац с суммой трудозатрат в A5 — часть A (в разделе 9 только свой итог)
  - [43] правки ссылок в разделах 3, 5, 7, 12, 13 — не мой раздел
  - [44] противоречивые «не проверено» в разделах 1, 2, 3, 6, 10 и A10 — не мой раздел; в разделе 9 «не проверено» по лицензиям снято через R8
  - [46] статусы и столбец лицензий A1, вопрос 13 в A7 — часть A
  - [48] определение «стандартного расследования» в A5 и пояснение в «Как читать» — часть A; предложенное пояснение слов «аудит/верификатор» противоречит V1, вместо него слова убраны
  - [64] три новые строки A6 — часть A
  - [70] столбцы «Критерий» и «При провале» в A8 и дополнение вопроса 12 в A7 — часть A
  - [74] пункт 17 в A7 — часть A
  - [81] замена строки A9 и дополнение вопроса 1 в A7 — часть A
  - [88] формулировки о двух репозиториях, Serper/SerpApi, LiteLLM, DeepSeek, T3 FCU — разделы 3, 4, 5, 14
  - [92] перенос оговорки о лицензиях в «Как читать» — часть A
  - [97] глоссарий терминов в «Как читать», правки A1/A5/A6 — часть A
  - [98] абзацы «Решение» разделов 3, 4, 5 — не мой раздел
  - [14]/[46] предложенный текст «лицензия не проверена» для строки 9 A1 устарел: по R8 TanStack Router и zustand — MIT
NOTES FOR LEAD:
  - A1, строка 9: по R8 TanStack Router и zustand — MIT, TypeScript — Apache-2.0; пометку «не проверено» из предложений [14]/[46] ставить не нужно. Статус строки в разделе 9: принято (SPA); условно (карта и раскладка).
  - A7 (вопрос 12 или пункт 17): раздел 9 теперь даёт порог по умолчанию — не менее 30 кадров в секунду на 1 000 узлов с подписями, ноутбук со встроенной графикой. Числовой порог на лимите 1 500/3 000, предельное время раскладки и
  порог для обзорного вида Sigma в первичном исследовании и перепроверке не заданы — оставлены владельцам, их нужно спросить явно.
  - Раздел 9 прямо говорит, что требование «1 000-10 000 узлов» закрывается свёрнутой картой в пределах лимита с раскрытием ветвей, а не показом всех узлов сразу. Это прочтение требования владельцев — стоит вынести на
  подтверждение в A7 (в первичном исследовании это открытый вопрос к владельцам).
  - Правила «при провале» в пунктах 1-4 раздела 9 — мои проектные формулировки, не факты из исследования: снижение лимита, затем Sigma либо GoJS/KeyLines по решению владельцев; без обзорного вида на 10 000 узлов в MVP; «если
  Graphviz dot проходит, собственный алгоритм не пишется»; Gotenberg для картинки графа только по решению владельцев (G10). Прошу подтвердить и отразить в A8.
  - Раздел 9 ссылается на раздел 13 как на место протокола сквозного замера (R10/R11), на A9 как на место риска «свой код больше, чем клей» и на G11 для асинхронной задачи PDF. В A5 при суммировании трудозатрат не складывать 4-5
  недель и 3-4 недели механически: раскладка входит в обе оценки.
  - Кандидаты серверной картинки графа в разделе 9: Graphviz dot → SVG, собственная сборка SVG из позиций снимка (из первичного исследования), ECharts с серверным SVG для диаграмм. Раздел 12 должен называть тот же список. Тест
  меток в разделе 9 теперь проверяет показ источника, даты и достоверности — согласовать со строками A6 из [64]. Длина раздела — по моей оценке около 13 300 знаков (посчитать точно не мог: код не запускал).

## reports-devops
DECLINED:
  - [14] concerns sections 9, 10 and A1; section 12 already states Pydantic MIT, matching R8
  - [19] concerns A5; the dossier has no effort estimate for reports or operations, nothing supportable to add
  - [44] concerns sections 1, 2, 3, 6, 10 and A10; no contradicting marker in 12 or 13
  - [56] request-count formula belongs to sections 1, 3 and A2; only the row-count sentence in 12 was aligned
  - [17] reviewer text 'оповещения из Grafana' not used: the dossier says log alert rules are vmalert files and Grafana Alerting UI does not show them, so step-1 alerts are attributed to Gatus and heartbeat
  - [64] reviewer text 'сырой ответ провайдера' in the exchange package not used: it contradicts G11; the package carries hashes of receipts and provider responses
  - [12], [22], [35], [38], [45], [46], [74], [85], [95] Part A portions (A1, A5, A7, A8) left to the lead engineer
  - [92] disclaimer in 'Как читать' and sections 4, 7, 8, 9 are outside my sections
NOTES FOR LEAD:
  - Observability: add Gatus (step 1) and VictoriaMetrics + vmalert (step 2) to A1 row 13 and A3. The step-2 deadline 'до приёма первых клиентов' is my design wording, please confirm. Step-1 alerts are attributed to Gatus and
  heartbeat, not Grafana (dossier: VictoriaLogs alert rules are vmalert files).
  - Costs for A5, A1 row 13, A7 Q6 (section 13 values): VPS-2 €8.49 without commitment or €7.21 at 12-month prepay; VPS-4 €19.96 exists in the dossier only as 12-month prepay (about €240 a year), its no-commitment price is marked
  'не прочитана'; heartbeat $20 for the paid product; domain about $1 (not verified); stand €21.73/мес only on a 12-month contract (about €261), a 1-month term exists but its price is not shown.
  - Criteria taken from reviewers as design statements, so A6 and A8 need the same numbers: memory check = peak total RSS not above 75% RAM at five parallel standard investigations plus one PDF render on 8 ГБ, otherwise 24 ГБ;
  timing = at least 20 runs per target, at least 95% within the limit (no more than one miss in 20, a sample share with no statistical margin), start and end from the orchestrator event log, external-source wait (including
  solidification wait for a transaction younger than about a minute) summed by the HTTP gateway.
  - A7 should carry the owner decisions section 12 now names: target time for PDF plus signed package (R10), eIDAS / PAdES (default: none in MVP), Gotenberg with Chromium (G10). A6 row on the separate exchange evidence package:
  section 12 describes it with hashes of receipts and provider responses, not raw responses (G11), and lists its composition as a Stage 2 item.
  - Tether 404: the dossier names two addresses, tether.io/law-enforcement/ (перепроверка) and tether.io/legal (первичное исследование); section 12 cites both and points to section 14 for the published policy, so A10 and section
  14 should match. Section 12 also says the request calculation in section 1 assumes thousands of edges (derived from R1): check against the final section 1.
  - Housekeeping: sections 12-13 keep 'ГБ/МБ' while G12/G14 use 'GB'; both sections ended at about 13.3k and 13.5k characters after the mandatory additions; G17 contains 'по условию Промпта 3' (drafting vocabulary, V1); A1 row 12
  licences should add LGPL (opentimestamps-client, docxtpl) and A8 п. 6 the Cyrillic / font-embedding check.

## osint-recovery
DECLINED:
  - [44] concerns sections 1, 2, 3, 6, 10 and A10 only; nothing in section 14 contradicts R6-R8
  - [45] A8 is Part A; section 14 already lists the written answers (see notes_for_lead)
  - [1] the G16 text and the A6 row are Part A; only the reference was added in section 14
  - [28] A5 table and section 5 are outside section 14; section 14 figures ($0.05/$0.08 for 10 queries) already agree
  - [29] sections 2 and 3 parts not mine; only the MistTrack price in section 14 changed
  - [39] A2 item 6, A10 and section 12 parts left to the lead and the section 12 editor
  - [52] the four A6 rows are Part A
  - [80] A1 row 14 and the contents line are Part A
  - [88] sections 3, 4, 5 parts not mine
  - [91][92][97][98] the «Как читать» glossary/disclaimer and other sections are outside section 14
NOTES FOR LEAD:
  - Title changed per R9: rename A1 row 14 and the contents line to match, and reword A2 item 6 (not «только через органы»). Section 14 now says T3 FCU is not in the directory until its domain is confirmed, while TRM Beacon
  Network is entered with status press.
  - A8 should list the Stage 2 checks of section 14: written answers from Brave (if chosen), Chainabuse, SSLMate and TronScan; plus three I added as design statements: read TRM Beacon Network access conditions, read the
  cs.tether.to portal, and resolve the 3 OFAC addresses found only in the mirror.
  - OFAC: the 337-of-340 match was made against sdn.csv and sdn_comments.csv, not against SDN_ADVANCED.XML, which section 2 names as the file to parse; own parsing of SDN_ADVANCED.XML was not run in this area. G7's «найдены в
  первичных файлах» is accurate, but section 2 should not imply the XML parse was already verified.
  - A6 alignment: section 14 measures the OSINT agent gain as the number of snapshot-confirmed claims about addresses that the baseline lacks (paired comparison with and without the module, same budget, 3-5 runs). The reviewer's
  A6 row uses «полнота найденных конечных адресов», which the OSINT module does not affect; please reconcile. Section 14 also points to «раздел 3, A6» for the rule that freeze-anchored cases (at least 10) are outside the 50.
  - Two wording choices to confirm: (a) «Заменяемость» now ties address sources to LabelSource (section 2) and drops the signature lookup(address) -> [claims], to avoid a third interface name; (b) «с сети аудита» became «с сети
  разработки» (the first-pass research describes the same machine). The Beacon statement («заявляет доступ для проверенных компаний по безопасности; условия не проверены») rests on R9, not on this area's sources, which only say
  access is via law enforcement or a network participant. On the Tether 404 conflict in A10/section 12: in this area the 2018-01-03 law-enforcement policy was read from tether.to page data; only cs.tether.to was not read.
  - Length: about 13.5 thousand characters by manual estimate (no code was run), slightly over the 13 000 guide after the required additions. To offset I removed the separate «Сторонние санкционные проверки» bullet (its numbers
  moved into the table row), the 334-s detail stays, the card notes moved to «Бесплатные квоты», and the T3 FCU domains are no longer repeated in the risks. If a hard cap applies, the cheapest cuts are the ScamSniffer and
  Parallel/Linkup rows and the list of unverified candidate sources.