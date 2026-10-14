# AREA graph-store: Graph storage, graph analytics and machine learning on graphs

============================================================
PART 1 - VERIFIER REPORT (takes precedence over the researcher wherever they disagree)
============================================================

## VERIFIER SUMMARY
Перепроверено 28 утверждений по первичным источникам (gh api, raw-файлы лицензий и кода на конкретных тегах, PyPI/npm/Kaggle/Mendeley API, официальные страницы pricing и docs, три keyless-запроса к TronGrid). Аудит фактически
точен в главном: 17 утверждений подтверждены без поправок, в том числе самые решающие — архивация Kuzu и состояние LadybugDB, сужение Additional Use Grant в BSL Memgraph между v3.7.2 и v3.8.0 (прочитаны обе редакции), SSPL у
FalkorDB, запрет коммерческого production в ArangoDB Community, откат SQL/PGQ из PostgreSQL 19 (коммит b1f106c8, откат сделан и в master), ограничения NetworkX на мультиграфах и отсутствие Yen / max-flow / community detection в
rustworkx, заброшенность DGL, цены AuraDB. Найдены ошибки и пробелы, влияющие на решения: 1. Опровергнуто: у Grafeo wheel cp312-abi3 ставится на Python 3.13 — причина отказа 'нет wheels под 3.13' неверна (остальные причины верны).
2. Лицензии датасетов установлены: Elliptic и Elliptic2 — CC BY-NC-ND 4.0, IBM AMLworld — CDLA-Sharing-1.0. Рекомендация по датасетам в части 'семейство Elliptic' не выдерживает требования коммерческой лицензии — это единственная
рекомендация, которую я не поддерживаю в исходном виде. 3. ArcadeDB недооценён: в коде на теге 26.10.1 есть k-shortest paths, max-flow, Leiden, Louvain, betweenness (69 файлов процедур) под Apache-2.0; его нужно сделать
обязательной конфигурацией benchmark. 4. Пропущены разрешительно лицензированные компилируемые реализации Yen и max-flow — SciPy csgraph и Google OR-Tools, которые закрывают главный пробел пары NetworkX + rustworkx без GPL. 5.
TronGrid отдаёт настоящий event_index через /v1/transactions/{txid}/events — ключ ребра должен быть (txid, event_index), а не синтетический ordinal. 6. On-chain события AddedBlackList контракта USDT доступны без ключа и дают
проверяемый по TXID ground truth — аудит оставил это непроверенной идеей. 7. Риск привязки к torch 2.12 преувеличен: бинарники pyg-lib есть для torch 2.14.0, включая Windows. 8. Мелкие поправки: issue AGE #2430 закрыт 2026-06-21,
pgRouting — GPL-2.0-or-later, Leiden присутствует в теге NetworkX 3.7, у Raphtory 0.18.5 на PyPI только macOS-wheels, sigma 4.x вышла за 6 дней до аудита. Главная рекомендация (PostgreSQL 18 как единственная СУБД + in-memory
библиотеки, выделенная graph DB только по итогам benchmark) выдерживает ограничения MVP по лицензии, стоимости и эксплуатации, но с обязательной поправкой: трассировку строить итеративным frontier-BFS в приложении, а не одним
recursive CTE, у которого нет глобального visited-множества. Производительность остаётся полностью неизмеренной — ни аудит, ни эта проверка код не запускали; утверждения о сроках 30 с / 2 мин / 5 мин и о памяти на 100k узлов можно
считать только гипотезами до Этапа 2. Не удалось проверить по первичным источникам: покупку Kuzu компанией Apple, лимиты AuraDB Free, поведение LATERAL ... LIMIT внутри рекурсивного CTE, корректность алгоритмов ArcadeDB, состав
папки с данными arXiv 2512.02534.

## BLOCKING RISKS
- Лицензии датасетов: Elliptic Data Set и Elliptic2 — CC BY-NC-ND 4.0 (метаданные Kaggle, проверено keyless-запросом), Elliptic++ — производный набор без лицензии. Рекомендация аудита использовать 'семейство Elliptic' и встроенные
загрузчики PyG в коммерческой компании создаёт юридический риск; модели и производные данные, полученные на этих наборах, нельзя переносить в продукт.
- Независимого размеченного тестового набора по USDT TRC20 для цели ≥95% точности меток не существует в готовом виде: Mendeley-набор (1,150 меток) деидентифицирован, без источников и без рёбер, поэтому не удовлетворяет требованию
'source + check date'. Без собственного набора цель недоказуема. Частично закрывается on-chain событиями AddedBlackList и GraphSense TagPacks, но оба источника нужно оценить отдельно.
- Recursive CTE как механизм трассировки не проверен и структурно уязвим: нет глобального visited-множества, на схемах split → merge число строк растёт как число путей. Если baseline-трассировщик построить на одном recursive CTE,
цель '1,000 адресов за ≤ 5 мин' и воспроизводимость (обрыв по statement_timeout даёт неполный, зависящий от нагрузки результат) под угрозой. Нужен детерминированный frontier-BFS с явными cap и журналом отсечений.
- Идентичность ребра: эндпоинт trc20-истории TronGrid не содержит индекса события, в одном TXID бывает несколько Transfer, а в выдаче присутствуют Approval. Без ключа (txid, event_index) из /v1/transactions/{txid}/events возможны
слияние или дублирование рёбер и искажение сумм — прямое нарушение требования '100% фактов подтверждены TXID'.
- Ни одна оценка производительности и памяти не измерена ни аудитом, ни мной (исполнение стороннего кода запрещено). Чистый Python NetworkX — единственный в рекомендованной паре носитель k-shortest, max-flow и community detection;
на подграфе 100k узлов и нескольких параллельных расследованиях на одном скромном сервере результат неизвестен. До benchmark Этапа 2 нельзя обещать верхнюю границу нагрузки.
- Дрейф лицензий source-available вендоров: Memgraph убрал разрешение на SaaS с интегрированным решением в минорном релизе v3.8.0 (2026-02-11), меняя Change Date каждым релизом. Любой BSL/SSPL-компонент (Memgraph, ArangoDB,
SurrealDB, FalkorDB) может ужесточить условия без мажорной версии — их нельзя закладывать в архитектуру платного SaaS без письменного договора.
- GPL-компоненты (Neo4j Community GPL-3.0, python-igraph GPL-2.0-or-later, pgRouting GPL-2.0-or-later, Raphtory GPL-3.0) совместимы только с чистым SaaS. Если владелец допускает поставку on-prem или Docker-образов клиентам
(правоохранительные органы, биржи), они исключаются, и запасных вариантов для k-shortest / max-flow / Leiden в компилируемом коде остаётся три: SciPy csgraph, OR-Tools и ArcadeDB — все три аудитом не оценены или недооценены.
- Bus factor у разрешительно лицензированных графовых СУБД: LadybugDB (0.x, три релиза за три дня, 37 из 100 последних коммитов у одного автора), ArcadeDB (алгоритмам меньше 8 месяцев, один основной автор), Grafeo и NeuG (моложе
года). Если benchmark Этапа 2 укажет на выделенную graph DB, зрелой и одновременно лицензионно чистой альтернативы PostgreSQL нет.
- sigma.js 4.x — мажорная линия возрастом 6 дней на дату аудита (4.0.0 от 2026-10-08): риск регрессий и несовместимости плагинов в web-отчёте, который является доказательным артефактом.

## VERIFIER VERDICTS ON RECOMMENDATIONS

### NEED: Хранилище графа и глобальная база знаний об адресах (MVP)
PRIMARY: PostgreSQL 18 как единственная СУБД (таблицы + recursive CTE), без выделенной graph DB до benchmark Этапа 2
STANDS: True
ISSUE: Выбор PostgreSQL как system of record выдерживает все ограничения MVP (лицензия PostgreSQL, $0 переменной стоимости, один сервис, один backup, Docker на Windows 11), а лицензионные причины отказа от Memgraph, ArangoDB, FalkorDB,
Kuzu подтверждены первичными текстами лицензий. Но три места слабее, чем заявлено. (1) Recursive CTE как основной механизм трассировки на 10+ hops не проверен запуском и имеет структурный дефект: нет глобального visited-множества,
клауза CYCLE режет только циклы внутри одного пути, поэтому на схемах fan-out → fan-in число строк растёт как число путей, а не вершин — это ударит по цели '1,000 адресов за ≤ 5 мин' раньше, чем supernode. (2) Схема ребра с
синтетическим event_ordinal: TronGrid отдаёт настоящий event_index через /v1/transactions/{txid}/events (проверено вживую), а trc20-история по адресу показывает только события с участием этого адреса. (3) Утверждение, что
функционально сильнейший вариант — только Neo4j GDS под GPLv3, устарело: ArcadeDB 26.10.1 (Apache-2.0) содержит в коде k-shortest paths, max-flow, Leiden, Louvain, betweenness, all simple paths, а аудит оставил его 'low
confidence, не проверено' и опциональным в benchmark.
SUGGESTED CHANGE: Оставить PostgreSQL 18 единственной СУБД MVP. Детерминированный baseline-трассировщик строить как итеративный frontier-BFS в приложении: один индексный запрос на hop вида from_addr = ANY($frontier) с ограничением по времени и
сумме, множество посещённых адресов и cap на степень — в коде, с записью каждого шага в журнал; recursive CTE оставить для малых ad-hoc запросов и как конфигурацию E0 в benchmark. Ключ ребра — (chain, txid, event_index), где
event_index берётся из первичного ответа событий транзакции. ArcadeDB перевести из опциональных в обязательные конфигурации benchmark Этапа 2 как единственную разрешительно лицензированную СУБД с библиотекой алгоритмов уровня GDS.
Не закладываться на SQL/PGQ ни в PG19, ни в PG20 (откат сделан и в master). Архивировать тексты лицензий всех не-permissive кандидатов по версиям: Memgraph изменил условия в минорном релизе v3.8.0.

### NEED: In-process графовая аналитика подграфов расследования
PRIMARY: NetworkX 3.7 + rustworkx 0.18.1 за единым интерфейсом GraphEngine
STANDS: True
ISSUE: Лицензии (BSD-3-Clause, Apache-2.0), установка на Windows 11 / Python 3.13 и все заявленные пробелы подтверждены кодом: в rustworkx нет Yen, max-flow и community detection; NetworkX не поддерживает k-shortest и flow на
мультиграфах; Leiden в NetworkX 3.7 есть (пункт not_verified закрыт). Слабое место — именно те операции, которые нужны проекту на верхней границе (k-shortest, max-flow, Louvain/Leiden на 100k узлов), остаются только в чистом
Python NetworkX; производительность и память не измерены. При этом аудит не рассмотрел два разрешительно лицензированных компилируемых варианта, закрывающих этот пробел без GPL: SciPy csgraph (BSD-3-Clause; в v1.18.1 есть yen и
maximum_flow, wheels cp313-win_amd64) и Google OR-Tools (Apache-2.0; модули max_flow и min_cost_flow, wheels cp313-win_amd64). Единственной альтернативой в аудите назван GPL-лицензированный python-igraph. Time-respecting пути
(монотонность времени вдоль пути) ни одна из библиотек не даёт — это остаётся собственным кодом, что аудит признаёт.
SUGGESTED CHANGE: Сохранить пару NetworkX (оракул корректности) + rustworkx (обходы, кратчайшие пути, центральности) и добавить в GraphEngine третий бэкенд для k-shortest и flow на схлопнутом графе: SciPy csgraph.yen и OR-Tools max_flow /
min_cost_flow. Учесть, что scipy maximum_flow требует целочисленные ёмкости фиксированного типа (в _flow.pyx проверка dtype против ITYPE) — суммы USDT в raw-единицах (6 знаков) нужно проверять на переполнение или считать поток в
OR-Tools / NetworkX. Community detection на 100k узлов — измерить NetworkX Leiden; если не укладывается, это единственный реальный довод за python-igraph или за процедуры ArcadeDB. Обе новые библиотеки включить в benchmark Этапа 2
отдельными конфигурациями.

### NEED: Graph ML для изолированного экспериментального контура
PRIMARY: PyTorch Geometric 2.8.1 (TGN, Node2Vec) + протоколы Temporal Graph Benchmark (py-tgb 2.3.0)
STANDS: True
ISSUE: Выбор PyG подтверждён: MIT, релиз 2.8.1 от 2026-10-06, Python 3.10–3.14; DGL действительно заброшен (последний коммит 2025-07-31, открытая ACE-уязвимость #7932). Две поправки. (1) Риск 'нужно фиксировать torch 2.12' преувеличен:
на data.pyg.org есть каталоги для torch 2.13.0 и 2.14.0, включая pyg_lib-0.9.0 abi3 для win_amd64 под torch 2.14.0; устарел README, а не бинарники. (2) Встроенные загрузчики EllipticBitcoinDataset / EllipticBitcoinTemporalDataset
скачивают данные под CC BY-NC-ND 4.0 — в коммерческой компании ими нельзя пользоваться как штатным учебным набором без юридической оценки. py-tgb 2.3.0 требует numpy>=2.0.2 и pandas>=2.2.3, torch-geometric — только как extra;
лицензия в метаданных PyPI не заполнена (репозиторий MIT).
SUGGESTED CHANGE: Оставить PyG + TGB. Зафиксировать конкретную связку torch / pyg-lib по фактическому индексу data.pyg.org, а не по README. В контуре по умолчанию использовать наборы с допускающей коммерческое использование лицензией: IBM AMLworld
(CDLA-Sharing-1.0), Mendeley TRON (CC BY 4.0), собственные снимки TRON; Elliptic-загрузчики отключить до решения юриста. Сохранить правило аудита: результаты ML не становятся фактами отчёта и не присваивают метки биржа/сервис.

### NEED: Эталонные датасеты и модели для illicit-flow detection
PRIMARY: Собственный набор ≥50 сценариев по USDT TRC20; Mendeley TRON dataset для экспериментов; семейство Elliptic для отработки методик
STANDS: False
ISSUE: Первая часть (собственный набор как основной эталон) верна и остаётся. Вторая часть не выдерживает требования коммерческой лицензии: Elliptic Data Set и Elliptic2 опубликованы под CC BY-NC-ND 4.0 (метаданные Kaggle, проверено
вживую), что запрещает коммерческое использование и производные; Elliptic++ — производный набор без лицензии. Аудит записал эти лицензии как 'не подтверждены' и всё равно включил семейство Elliptic в рекомендацию и в benchmark.
Кроме того, Mendeley-набор не содержит рёбер (только таблицы адресов и признаков, три CSV по 131–211 KB) и не содержит источников меток, поэтому он не годится ни для графовых моделей без самостоятельной догрузки истории, ни как
независимый тестовый набор для цели ≥95% (нет source и check date). Упущен проверяемый первичный источник ground truth именно для USDT TRC20: события AddedBlackList контракта USDT, которые TronGrid отдаёт без ключа вместе с TXID и
номером блока.
SUGGESTED CHANGE: Убрать семейство Elliptic из рекомендации для коммерческого контура (допустимо только как отдельно согласованное некоммерческое исследование без переноса моделей и производных в продукт). Состав наборов: (1) собственные ≥50
сценариев с TXID; (2) on-chain события AddedBlackList / RemovedBlackList / DestroyedBlackFunds контракта USDT как первичные, проверяемые по TXID метки 'заморожен Tether' — и как источник реальных кейсов для сценариев; (3) IBM
AMLworld (CDLA-Sharing-1.0) для отладки детектора split/merge и пайплайна обучения; (4) Mendeley TRON (CC BY 4.0) только как вспомогательные слабые метки в ML-контуре; (5) оценить набор TRON-USDT из arXiv 2512.02534 (≈1.04 млн
адресов, 2.6 млн транзакций, 193 группы; данные на Google Drive, лицензия не указана — нужен запрос авторам).

### NEED: Сравнительный benchmark Этапа 2
PRIMARY: Собственный harness LH-GraphBench: один набор данных и запросов на семи конфигурациях движков
STANDS: True
ISSUE: Подход корректен и необходим: ни одно утверждение о производительности в аудите не измерено, и я их тоже не измерял. Набор конфигураций неполон и местами не соответствует проверенным фактам: ArcadeDB (единственная Apache-2.0 СУБД
с k-shortest, max-flow, Leiden в коде) стоит как опциональная; нет SciPy csgraph и OR-Tools; E0 описывает только recursive CTE, хотя реалистичный baseline — итеративный frontier-BFS; D3 помечен 'при допустимой лицензии', хотя
лицензия AMLworld уже известна (CDLA-Sharing-1.0, полный набор ≈41.6 GB — брать Small-варианты). В E5 не зафиксированы лимиты GDS Community (4 ядра, 3 модели в каталоге), без чего сравнение с другими движками будет нечестным. Не
заданы параметры целевого сервера, а правило '3x по p95' бессмысленно без них.
SUGGESTED CHANGE: Добавить обязательные конфигурации: E0b PostgreSQL frontier-BFS в приложении; E7 ArcadeDB 26.10.x (server и embedded); E8 PostgreSQL + SciPy csgraph / OR-Tools для Q5 и Q7. Добавить запрос на time-respecting пути с проверкой по
посаженному ground truth и запрос, проверяющий, что несколько Transfer в одном TXID не схлопываются (ключ txid + event_index). Зафиксировать профиль сервера (ядра, RAM) до запуска и записывать лимиты редакций (GDS CE: concurrency
4). Для каждой конфигурации сохранять текст лицензии и версию. Elliptic из данных benchmark исключить.

### NEED: Графовая модель и визуализация на стороне TypeScript/UI
PRIMARY: graphology 0.26.0 + sigma.js 4.0.1 (оба MIT)
STANDS: True
ISSUE: Лицензии и версии подтверждены по npm. Но sigma 4.0.0 вышла 2026-10-08, а 4.0.1 — за день до аудита: рекомендована мажорная линия возрастом 6 дней, совместимость окружающих пакетов (обёртки для React, плагины) с v4 не проверялась.
Ядро graphology не обновлялось с 2025-01-26 — аудит это отметил. Производительность рендера на 100k узлов не измерена.
SUGGESTED CHANGE: Для MVP зафиксировать sigma 3.0.3 (2026-04-30) либо принять 4.0.x только после проверки совместимости используемых плагинов и нескольких недель стабилизации; версию закрепить в lock-файле. Остальное (расчёты только на Python-
стороне, обмен node-link JSON, cytoscape.js как замена) оставить без изменений.

## VERIFIER FACT CHECKS

- [CONFIRMED] Kuzu (kuzudb/kuzu) :: Репозиторий архивирован, последний push и релиз v0.11.3 от 2025-10-10, MIT, 4,022 stars; README объявляет об архивации.
  CORRECT VALUE: archived=true, pushed_at 2025-10-10T15:34:00Z, v0.11.3 от 2025-10-10T14:32:42Z, MIT, 4,022 stars, 329 open issues. README: 'Kuzu is working on something new! We are archiving the KuzuDB project'. Форки: Kineviz/bighorn 135 stars
(push 2026-08-10), Vela-Engineering/kuzu 48 (2026-09-27), opencypher/cypherdb archived, predictable-labs/ryugraph 146 (NOASSERTION, push 2026-01-20).
  METHOD: API call (gh api repos/kuzudb/kuzu, releases, forks) + code read (README через raw.githubusercontent.com)
  EVIDENCE: https://github.com/kuzudb/kuzu

- [CONFIRMED] LadybugDB 0.21.2 :: MIT, создан 2025-10-07, v0.21.2 от 2026-10-01, 1,845 stars, wheels cp313 win_amd64; single-writer; в algo только K-Core/Louvain/PageRank/SCC/WCC; нет k-shortest, max-flow, betweenness, Leiden.
  CORRECT VALUE: Всё совпало: LICENSE = MIT (Copyright Kùzu Inc. 2022-2025 + Ladybug Memory Inc. 2025-2026); created 2025-10-07; релизы v0.21.0/0.21.1/0.21.2 за 2026-09-29..10-01 (и 0.20.0-0.20.4 за две недели до того); PyPI ladybug 0.21.2 имеет
cp313-win_amd64 и cp314; в последних 100 коммитах 9 авторов, Arun Sharma 37. Docs /concurrency: один READ_WRITE Database-объект ИЛИ несколько READ_ONLY, смешивать небезопасно. Docs /extensions/algo: K-Core, Louvain, PageRank, SCC,
WCC; проекции привязаны к Connection. Code search: k_shortest=0, max_flow=0, betweenness=0, leiden=0 (32 совпадения по 'yen' не разбирались).
  METHOD: API call (gh api repos, releases, commits, search/code; PyPI JSON) + code read (LICENSE) + docs read (WebFetch concurrency, extensions/algo, extensions/algo/path)
  EVIDENCE: https://docs.ladybugdb.com/concurrency

- [CONFIRMED] Memgraph Community 3.13.2 :: BSL 1.1; Additional Use Grant сужен: до v3.7.2 разрешал Integrated Solution по модели SaaS, с v3.8.0 (коммит cef597d639 от 2026-01-28) остались только 'internal business purposes'; Change Date 2030-09-10.
  CORRECT VALUE: Прочитал три ревизии licenses/BSL.txt. Тег v3.7.2 (2025-12-23): Authorised Purpose включает п.2 'integrate the Licensed Work with your own proprietary software ... (Integrated Solution)' и п.3 'host the Integrated Solution ...
software-as-a-service'. Тег v3.8.0 (2026-02-11) и master: 'Authorised Purpose means your internal business purposes' с запретами embed/distribute, DBaaS, competing; заголовок 'AS AMENDED ... January 1, 2026'. Коммит cef597d639
'Update licenses (#3719)' от 2026-01-28 меняет BSL.txt, MEL.txt, MEL.pdf, README. Change Date на master 2030-09-10. Важно: Change Date сдвигается КАЖДЫМ релизом (коммиты 'Update BSL change date' при v3.9..v3.13.2), то есть
лицензия версионная и уже менялась в минорном релизе.
  METHOD: code read (BSL.txt на v3.7.2, v3.8.0, master) + API call (gh api commits/cef597d639, commits?path=licenses/BSL.txt, releases)
  EVIDENCE: https://raw.githubusercontent.com/memgraph/memgraph/v3.7.2/licenses/BSL.txt

- [CONFIRMED] memgraph/mage :: Репозиторий MAGE архивирован после слияния в memgraph/memgraph; слитый код под BSL.
  CORRECT VALUE: archived=true, pushed_at 2026-01-23, SPDX самого архивного репозитория остаётся Apache-2.0 (старые версии MAGE можно брать под Apache-2.0). README: объявление о слиянии датировано 'November 7th, 2025'. Коммит лицензий cef597d639
затрагивает и mage/README.md в основном репозитории. Точную фразу 'завершено 2026-01-22' я не перечитывал.
  METHOD: API call (gh api repos/memgraph/mage) + code read (README, первые 1500 символов)
  EVIDENCE: https://github.com/memgraph/mage

- [CONFIRMED] FalkorDB 6.0.2 :: SSPL-1.0; линии релизов v6.0.x и v4.22.0 параллельно; Cloud Startup 'From $73/1GB/Month', Pro 'From $350/8GB/Month'.
  CORRECT VALUE: LICENSE в main — 'Server Side Public License VERSION 1, OCTOBER 16, 2018'. Релизы: v6.0.2 (2026-10-08), v6.0.1 (10-01), v4.22.0 (09-30), v6.0.0 (09-29). 9,567 stars, 1,002 open issues. Страница plans: STARTUP 'From $73/1GB/Month',
PRO 'From $350/8GB/Month', FREE без TLS/HA/backup; лимит памяти Free на странице не указан (100 MB из аудита не подтверждён мной).
  METHOD: code read (LICENSE) + API call (releases) + docs read (WebFetch falkordb.com/plans)
  EVIDENCE: https://raw.githubusercontent.com/FalkorDB/FalkorDB/main/LICENSE

- [CONFIRMED] ArangoDB 3.12 :: Исходники BSL 1.1; Community Edition запрещает коммерческое использование в production, лимит 100 GiB, нет права distribute/embed.
  CORRECT VALUE: LICENSE (devel): Business Source License 1.1, Licensed Work 'ArangoDB Self Managed (Release Date: March 2024)', Change Date — 4 года после релиза, Additional Use Grant запрещает 'commercial offering that allows one or more third
parties ... to access, create or manage databases'. Docs 3.12/features: 'The use for commercial purposes is prohibited for production', 'The dataset size is limited to a 100 GiB', 'does not include the right to distribute, embed
within other products'.
  METHOD: code read (LICENSE devel) + docs read (WebFetch)
  EVIDENCE: https://docs.arango.ai/arangodb/3.12/features/

- [CONFIRMED] PostgreSQL 18 / 19 (SQL/PGQ) :: SQL/PGQ откатан из PostgreSQL 19 коммитом b1f106c8 от 2026-09-07 (2b9e1aff в REL_19_STABLE); PG19 не GA (Beta 4 от 2026-09-24); текущая стабильная 18.6.
  CORRECT VALUE: Коммит b1f106c80c 'Revert SQL Property Graph Queries (SQL/PGQ)' (2026-09-07) перечисляет ~36 откатываемых коммитов начиная с 2f094e7ac69; в REL_19_STABLE тот же откат — 2b9e1aff4d (2026-09-07T19:03Z).
src/backend/commands/propgraphcmds.c даёт 404 и в master, и в REL_19_STABLE; страницы docs/19/sql-create-property-graph.html и docs/devel/... — 404. postgresql.org: 'PostgreSQL 19 Beta 4 Released! 2026-09-24'; versioning: 18 →
18.6, first release 2025-09-25, final 2030-11-14; 17.11; 16.15. Откат выполнен и в master, то есть фича не гарантирована и в PG20. В docs/18/queries-with.html присутствуют SEARCH BREADTH FIRST, SEARCH DEPTH FIRST и CYCLE.
  METHOD: API call (gh api search/commits, commits/b1f106c8, commits?sha=REL_19_STABLE, contents) + docs read (curl postgresql.org)
  EVIDENCE: https://github.com/postgres/postgres/commit/b1f106c80cbeb18d3a0219994d98a51a6eca8ede

- [UNVERIFIABLE] PostgreSQL recursive CTE как механизм трассировки :: WITH RECURSIVE + CYCLE + LATERAL ... LIMIT закрывает ограниченный по глубине forward trace на 10+ hops.
  CORRECT VALUE: Синтаксис SEARCH/CYCLE в документации 18 есть, но ни один запрос не выполнялся (исполнение стороннего кода запрещено). Существенное ограничение, не названное в аудите: у recursive CTE нет глобального множества посещённых вершин —
CYCLE отсекает только циклы внутри одного пути, а строки с разными depth/path не дедуплицируются UNION. На графе с fan-out и последующим fan-in (типичная схема split/merge) число строк равно числу путей, а не вершин, и растёт
экспоненциально уже без supernode. Допустимость LATERAL-подзапроса с LIMIT внутри рекурсивного члена тоже не проверена запуском.
  METHOD: docs only (наличие клауз проверено curl); поведение не измерялось
  EVIDENCE: https://www.postgresql.org/docs/18/queries-with.html

- [CORRECTED] Apache AGE 1.8.0 :: Apache-2.0; релизы PG18/v1.8.0-rc0 (2026-07-09), PG15/v1.8.0-rc0 (2026-09-19), PG17 только 1.7.0; issue #2430 закрыт 2026-06-03; apache-age-python на PyPI застрял на 0.0.7 (2023-09-22).
  CORRECT VALUE: Issue #2430 'Add shortest_path / all_shortest_paths SRFs' закрыт 2026-06-21 (не 06-03). Релиз PG15/v1.8.0-rc0 помечен GitHub как prerelease=true, PG18/v1.8.0-rc0 — нет. Существует тег PG19/v1.8.0-rc0. Остальное подтверждено:
Apache-2.0, 4,887 stars, 255 open issues, push 2026-10-13, README: PostgreSQL 11–18, PyPI apache-age-python 0.0.7 от 2023-09-22.
  METHOD: API call (gh api repos, releases, tags, issues/2430; PyPI JSON) + code read (README)
  EVIDENCE: https://github.com/apache/age/releases

- [CORRECTED] pgRouting 4.0.2 :: GPL-2.0; v4.0.2 от 2026-09-05; в sql/ есть ksp, max_flow, mincut, components, dominator.
  CORRECT VALUE: README: 'Most features are available under GPL-2.0-or-later', часть Boost-расширений под Boost license, часть кода под MIT-X (GitHub SPDX показывает GPL-2.0). Релизы v4.0.2 (2026-09-05), v4.0.1 (2026-01-31), v4.0.0 (2025-11-07) и
каталоги ksp, max_flow, mincut, components, dominator, contraction, traversal подтверждены.
  METHOD: API call (gh api repos, releases, contents/sql) + code read (LICENSE, README)
  EVIDENCE: https://github.com/pgRouting/pgrouting/blob/main/README.md

- [CONFIRMED] Neo4j Community + GDS :: Neo4j Community — GPL-3.0; OpenGDS — GPL-3.0, бинарник GDS содержит закрытые исходники; GDS Community ограничен 4 ядрами; в Community нет online backup.
  CORRECT VALUE: neo4j/neo4j SPDX GPL-3.0, теги 2026.09.0 / 2026.08.1. GDS LICENSE.txt: 'licensed under the GNU GENERAL PUBLIC LICENSE Version 3'; README.adoc: 'as built and distributed by Neo4j includes the sources in this repository as well a
suite of closed sources'. GDS releases 2026.09.0 (2026-09-21). Docs GDS System requirements: 'The maximum concurrency in the library is limited to 4' (CE). Pricing: GDS Community — максимум 4 CPU cores и model catalog 3 модели
(это закрывает пункт not_verified о лимите model catalog). Operations Manual: online backup, RBAC, clustering отнесены к Enterprise (таблица редакций в WebFetch без галочек, подтверждено текстом).
  METHOD: code read (LICENSE.txt, README.adoc GDS) + API call (repos, releases, tags) + docs read (WebFetch pricing, GDS docs, operations manual)
  EVIDENCE: https://neo4j.com/docs/graph-data-science/current/installation/System-requirements/

- [CONFIRMED] Neo4j AuraDB :: Professional $0.09/GB/час при минимуме 1 GB; Business Critical $0.20/GB/час, минимум 2 GB; Aura Graph Analytics $0.40/GB/час.
  CORRECT VALUE: Страница pricing: Professional $0.09/GB/hour, min 1GB, до 128GB; Business Critical $0.20/GB/hour, min 2GB; Aura Graph Analytics $0.40/GB/hour, до 512 GB. Числовых лимитов AuraDB Free на странице нет ('places limits on the number
of nodes and relationships') — лимиты Free остаются непроверенными.
  METHOD: docs read (WebFetch)
  EVIDENCE: https://neo4j.com/pricing/

- [CORRECTED] NetworkX 3.7 :: BSD-3-Clause, 3.7 от 2026-09-21; shortest_simple_paths не работает на multigraph; flow не поддерживает MultiDiGraph; Leiden есть (в аудите — только в main, для 3.7 не проверено).
  CORRECT VALUE: Все ограничения подтверждены на теге networkx-3.7 (а не только main): simple_paths.py строка 422 '@not_implemented_for("multigraph")' перед shortest_simple_paths; flow/utils.py строки 108-109 'MultiGraph and MultiDiGraph not
supported (yet).' Уточнение: leiden.py ПРИСУТСТВУЕТ в теге networkx-3.7 (leiden_communities, leiden_partitions, параметр seed, ветка is_directed для DiGraph) — пункт not_verified закрыт. PyPI: 3.7, BSD-3-Clause, requires_python
'!=3.14.1,>=3.12', wheel py3-none-any. Реализации Louvain/Leiden — чистый Python.
  METHOD: code read (simple_paths.py, flow/utils.py, leiden.py на теге networkx-3.7) + API call (releases, contents; PyPI JSON)
  EVIDENCE: https://github.com/networkx/networkx/blob/networkx-3.7/networkx/algorithms/community/leiden.py

- [CONFIRMED] rustworkx 0.18.1 :: Apache-2.0; 0.18.1 от 2026-07-29; abi3 wheels win_amd64; нет Louvain, Leiden, max-flow, Yen; k_shortest_path_lengths возвращает только длины.
  CORRECT VALUE: Релизы 0.18.1 (2026-07-29), 0.18.0 (2026-06-18); PyPI: Apache-2.0, rustworkx-0.18.1-cp310-abi3-win_amd64.whl. Code search: louvain=0, leiden=0, max_flow=0, yen=0, label_propagation=0, minimum_cut=0 (есть только
stoer_wagner_min_cut для неориентированных графов). В rustworkx/__init__.py (тег 0.18.1) есть k_shortest_path_lengths, all_shortest_paths, all_simple_paths, betweenness_centrality, edge_betweenness_centrality,
bfs_search/dfs_search/dijkstra_search, condensation, networkx_converter; функции, возвращающей k кратчайших путей, нет.
  METHOD: code read (__init__.py на теге) + API call (releases, search/code; PyPI JSON). Один запрос code search упал по rate limit и заменён чтением файла.
  EVIDENCE: https://github.com/Qiskit/rustworkx/blob/0.18.1/rustworkx/__init__.py

- [CONFIRMED] python-igraph 1.0.0 :: GPL-2.0-or-later; 1.0.0 от 2025-10-23; abi3 wheels cp39 win_amd64; есть get_k_shortest_paths, maxflow, community_leiden, all_st_mincuts, gomory_hu_tree, dominator.
  CORRECT VALUE: GitHub SPDX GPL-2.0; setup.py и PyPI: 'GNU General Public License (GPL)'; релиз 1.0.0 от 2025-10-23; igraph-1.0.0-cp39-abi3-win_amd64.whl. В src/_igraph/graphobject.c (тег 1.0.0) найдены get_k_shortest_paths, maxflow,
community_leiden, all_st_mincuts, gomory_hu_tree, dominator, community_multilevel, personalized_pagerank. C core igraph/igraph — GPL-2.0.
  METHOD: code read (graphobject.c, setup.py) + API call (repos, releases; PyPI JSON)
  EVIDENCE: https://github.com/igraph/python-igraph/blob/1.0.0/src/_igraph/graphobject.c

- [CORRECTED] PyTorch Geometric 2.8.1 :: MIT, 2.8.1 от 2026-10-06; Node2Vec требует pyg-lib>=0.6.0; README перечисляет бинарники только до PyTorch 2.12 при torch 2.14.1 — версию torch нужно фиксировать под 2.12; наличие wheels pyg-lib для Python 3.13 + Windows не
проверено.
  CORRECT VALUE: README действительно заканчивается на PyTorch 2.12, но индекс data.pyg.org/whl содержит каталоги для torch 2.13.0 и 2.14.0. Для torch-2.14.0+cpu опубликован pyg_lib-0.9.0+pt214cpu-cp310-abi3-win_amd64.whl (abi3 — ставится на
Python 3.13); для torch-2.12.0+cpu есть pyg_lib-0.7.0 cp313-win_amd64 и torch_scatter/torch_sparse cp313-win_amd64. То есть README устарел, а не бинарники: привязка к torch 2.12 не обязательна, пункт not_verified закрыт. Для torch
2.14.0 на странице всего 4 файла — torch_scatter/torch_sparse там отсутствуют. Остальное подтверждено: релиз 2.8.1 (2026-10-06), PyPI 2.8.1 (2026-10-12), MIT, 'Python 3.10 to Python 3.14', node2vec.py строки 61-63.
  METHOD: API call (curl data.pyg.org/whl index и страницы torch-2.12.0+cpu, torch-2.14.0+cpu; gh api releases; PyPI JSON) + code read (README, node2vec.py)
  EVIDENCE: https://data.pyg.org/whl/torch-2.14.0+cpu.html

- [CONFIRMED] DGL 2.4.0 :: Фактически не сопровождается: последний коммит 2025-07-31, релиз v2.4.0 от 2024-09-03, PyPI 2.2.1 без cp313; открыты issues #7932 (ACE) и #7934.
  CORRECT VALUE: Последний коммит 3d16000b от 2025-07-31, предыдущий 2025-02-11; v2.4.0 (2024-09-03); PyPI dgl 2.2.1 (2024-05-13), wheels cp38–cp312; #7932 'Arbitrary Code Execution in DGL via load_info and Graphbolt Torch-Data Loading' open
(2026-08-29); #7934 'Fails to build with PyTorch-2.14.0' open (2026-09-13). Не архивирован.
  METHOD: API call (gh api repos, commits, releases, issues; PyPI JSON)
  EVIDENCE: https://github.com/dmlc/dgl/issues/7932

- [CORRECTED] Elliptic Data Set и Elliptic2 :: Лицензия Elliptic на Kaggle не подтверждена (страницу прочитать не удалось); лицензия данных Elliptic2 не проверена.
  CORRECT VALUE: Kaggle API (keyless) отдаёт для ellipticco/elliptic-data-set: licenseName = 'Attribution-NonCommercial-NoDerivatives 4.0 International (CC BY-NC-ND 4.0)', lastUpdated 2019-07-31, 697 MB. Для ellipticco/elliptic2-data-set: та же CC
BY-NC-ND 4.0, lastUpdated 2024-04-23, ≈88 GB. Обе лицензии запрещают коммерческое использование и распространение производных. PyG лишь зеркалирует файлы и лицензию не меняет. Elliptic++ — производный набор от Elliptic без
собственной лицензии (license=null подтверждено), то есть наследует как минимум те же ограничения.
  METHOD: API call (keyless GET Kaggle API для двух датасетов; gh api repos/git-disl/EllipticPlusPlus) + code read (README Elliptic2, Elliptic++)
  EVIDENCE: https://www.kaggle.com/api/v1/datasets/view/ellipticco/elliptic-data-set

- [CORRECTED] IBM AMLworld (IBM Transactions for Anti Money Laundering) :: Лицензия датасета на Kaggle не подтверждена.
  CORRECT VALUE: Kaggle API: licenseName = 'Community Data License Agreement - Sharing - Version 1.0' (CDLA-Sharing-1.0), lastUpdated 2025-07-08, общий объём ≈41.6 GB. Лицензия допускает коммерческое использование; share-alike действует на
публикуемые производные данные. IBM/Multi-GNN — Apache-2.0, push 2025-09-18.
  METHOD: API call (keyless GET Kaggle API; gh api repos/IBM/Multi-GNN)
  EVIDENCE: https://www.kaggle.com/api/v1/datasets/view/ealtman2019/ibm-transactions-for-anti-money-laundering-aml

- [CONFIRMED] Mendeley TRON TRC20-USDT dataset (62dmsngtfb) :: Версия 3, DOI 10.17632/62dmsngtfb.3, CC BY 4.0, 1,150 меток, поведенческое подмножество 1,024 адресов TRC20-USDT, единственный контрибьютор Meng Ling Tsai; содержимое не проверялось.
  CORRECT VALUE: Public API Mendeley: version 3, DOI 10.17632/62dmsngtfb.3, лицензия с описанием CC BY, контрибьютор Meng Ling Tsai. Описание: '1,150 judicially grounded single-role virtual asset address labels, a TRON TRC20-USDT behavioral-
analysis subset of 1,024 addresses'; исключены идентификаторы дел, судов, даты, URL источников. Состав файлов (новое): judicial_ground_truth_address_labels_public_v2.csv (131 KB), tron_trc20_usdt_behavioral_analysis_subset_v2.csv
(192 KB), tron_trc20_usdt_single_case_grouped_classification_subset_v2.csv (211 KB), DATA_DICTIONARY.md, два скрипта. Графовой структуры (рёбер) в наборе нет — только таблицы адресов и признаков. Файлы не скачивались.
  METHOD: API call (keyless GET Mendeley public API)
  EVIDENCE: https://data.mendeley.com/public-api/datasets/62dmsngtfb

- [CORRECTED] ArcadeDB 26.10.1 :: Apache-2.0; набор графовых алгоритмов и зрелость Cypher 'не проверялись', confidence low; в benchmark включён только как опциональная конфигурация.
  CORRECT VALUE: Алгоритмы проверяемы и есть в коде: каталог engine/.../query/opencypher/procedures/algo на теге 26.10.1 содержит 69 файлов (71 в main), включая AlgoKShortestPaths, AlgoMaxFlow, AlgoAllSimplePaths, AlgoDijkstra, AlgoBellmanFord,
AlgoLeiden, AlgoLouvain, AlgoLabelPropagation, AlgoBetweenness, AlgoPageRank, AlgoPersonalizedPageRank, AlgoSCC, AlgoWCC, AlgoKCore, AlgoNode2Vec, AlgoFastRP, AlgoSteinerTree; в каталоге тестов 99 файлов. Это единственная
проверенная СУБД под разрешительной лицензией (Apache-2.0), где одновременно есть k-shortest, max-flow, Leiden и betweenness — функциональный аналог Neo4j GDS без GPL и лимита 4 ядер. Оговорки: первый коммит этих процедур —
2026-02-23 (коду менее 8 месяцев), основной автор lvca (7,992 коммита) → bus factor; arcadedb-embedded 26.10.1 — wheels cp313-win_amd64 размером ≈70 MB (встроенный JRE). Корректность алгоритмов не проверялась.
  METHOD: API call (gh api contents на main и теге 26.10.1, search/code, commits?path, releases, contributors; PyPI JSON) + code read (LICENSE)
  EVIDENCE: https://github.com/ArcadeData/arcadedb/tree/26.10.1/engine/src/main/java/com/arcadedb/query/opencypher/procedures/algo

- [REFUTED] Grafeo 0.5.44 :: PyPI-wheels для Windows только cp312, под Python 3.13 нет — одна из причин отказа.
  CORRECT VALUE: Файл на PyPI — grafeo-0.5.44-cp312-abi3-win_amd64.whl: тег abi3 означает stable ABI, wheel ставится на CPython 3.12 и новее, включая 3.13 (аудит сам правильно трактует abi3 у rustworkx и igraph). Эта причина отказа неверна.
Остальные причины подтверждены: репозиторий создан 2026-01-26, Apache-2.0, 811 stars, релизы v0.5.44 (2026-10-04) и v0.6.0-beta.1 (2026-10-11).
  METHOD: API call (PyPI JSON; gh api repos, releases)
  EVIDENCE: https://pypi.org/project/grafeo/#files

- [CORRECTED] TronGrid /v1/accounts/{addr}/transactions/trc20 :: В ответе нет log index; среди 200 записей 197 Transfer и 3 Approval; 199 уникальных TXID; ключ ребра нужно делать (txid, event_ordinal); наличие log index в других источниках не проверено.
  CORRECT VALUE: Повторный keyless-запрос: HTTP 200, 71,313 байт, 1.07 с, 200 записей, поля block_timestamp/from/to/token_info/transaction_id/type/value, 197 Transfer + 3 Approval, 199 уникальных TXID — совпало. Но стабильный индекс события
существует: GET /v1/transactions/{txid}/events возвращает поле event_index (плюс block_number, contract_address, caller_contract_address). Для проверенного TXID e156ca1e... событий 9, из них три USDT Transfer с event_index 1, 4, 7
и два Approval. Ключ ребра должен быть (txid, event_index) из первичных данных, а не синтетический порядковый номер; эндпоинт trc20-истории по адресу показывает только события с участием этого адреса (2 из 3 Transfer в данном
TXID).
  METHOD: API call (2 keyless GET к api.trongrid.io)
  EVIDENCE: https://api.trongrid.io/v1/transactions/e156ca1e6ae57b7cdf0b72af27f4993410d7fb9cc4873963e2a855fa246f8eb8/events

- [CONFIRMED] graphology 0.26.0 + sigma.js 4.0.1 :: Оба MIT; graphology core 0.26.0 от 2025-01-26; sigma 4.0.1 от 2026-10-13, 'активно обновляется'.
  CORRECT VALUE: npm: graphology latest 0.26.0 (2025-01-26), MIT; sigma latest 4.0.1 (2026-10-13), MIT; cytoscape 3.34.3 (2026-09-07). Существенная деталь, не выделенная в аудите: sigma 4.0.0 опубликована 2026-10-08, то есть мажорной линии 4.x на
дату аудита 6 дней (бета-цикл шёл до 2026-10-05); последняя 3.x — 3.0.3 от 2026-04-30. В монорепозитории graphology есть communities-leiden, communities-louvain, shortest-path, simple-path, layout-forceatlas2, metrics.
  METHOD: API call (npm registry JSON; gh api releases, contents/src)
  EVIDENCE: https://registry.npmjs.org/sigma

- [CORRECTED] Raphtory 0.18.5 :: GPL-3.0; наличие wheels для Windows через PyPI API подтвердить не удалось.
  CORRECT VALUE: GPL-3.0 подтверждено (GitHub SPDX), 647 stars, push 2026-10-13. PyPI JSON для 0.18.5 перечисляет только два файла: raphtory-0.18.5-cp311-cp311-macosx_10_12_x86_64.whl и ...macosx_11_0_arm64.whl — wheels для Windows и Linux у этой
версии на PyPI нет. Для dev-машины (Windows 11, Python 3.13) пакет из PyPI не ставится.
  METHOD: API call (PyPI JSON; gh api repos)
  EVIDENCE: https://pypi.org/pypi/raphtory/0.18.5/json

- [CONFIRMED] Драйверы PostgreSQL :: psycopg 3.3.6 (LGPL-3.0-only), asyncpg 0.32.0 (Apache-2.0), pg 8.23.1 (MIT).
  CORRECT VALUE: PyPI: psycopg 3.3.6, license_expression LGPL-3.0-only, requires_python >=3.10; asyncpg 0.32.0, Apache-2.0, есть cp313-win_amd64; npm pg 8.23.1 (2026-09-30), MIT; neo4j-driver 6.2.0 Apache-2.0. Для on-prem поставки psycopg
потребует соблюдения условий LGPL (Python-импорт их выполняет), asyncpg ограничений не несёт.
  METHOD: API call (PyPI JSON, npm registry JSON)
  EVIDENCE: https://pypi.org/pypi/psycopg/json

- [CONFIRMED] DuckDB 1.5.6 + DuckPGQ, SurrealDB, NebulaGraph, JanusGraph, Dgraph, TypeDB :: DuckDB v1.5.6 (2026-09-28), DuckPGQ — research project без GitHub Releases; SurrealDB — BSL 1.1 с запретом Database Service, Change Date 2030-01-01; NebulaGraph v3.8.0 (2024-05-17); JanusGraph v1.1.0 (2024-11-09); Dgraph v25.5.0
(2026-10-13); TypeDB 3.13.6 (2026-09-22), MPL-2.0.
  CORRECT VALUE: Все даты и версии совпали. DuckPGQ README строка 11: 'DuckPGQ is a research project and a work in progress', releases=0, MIT, 505 stars. SurrealDB LICENSE: Licensed Work 'SurrealDB 3.0', запрет использования как 'Database Service'
(третьи лица создают/управляют схемами или таблицами), Change Date 2030-01-01. Dgraph Apache-2.0, 21,808 stars.
  METHOD: API call (gh api repos, releases) + code read (LICENSE SurrealDB, README DuckPGQ)
  EVIDENCE: https://raw.githubusercontent.com/surrealdb/surrealdb/main/LICENSE

- [UNVERIFIABLE] Kuzu / Apple, AuraDB Free :: Kuzu куплена Apple (по прессе); лимиты AuraDB Free 200k узлов / 400k связей.
  CORRECT VALUE: Первичных документов я не видел: в поисковой выдаче упоминается раскрытие по EU Digital Markets Act с датой соглашения 2025-10-09, но сам документ не читался. Страница neo4j.com/pricing числовых лимитов Free не содержит. Оба
утверждения на выбор не влияют.
  METHOD: search snippet only
  EVIDENCE: https://neo4j.com/pricing/

## CANDIDATES MISSED BY THE RESEARCHER (found by verifier)

- SciPy sparse.csgraph (scipy 1.18.1) (https://github.com/scipy/scipy/blob/v1.18.1/scipy/sparse/csgraph/__init__.py)
  WHY: Закрывает главный пробел рекомендованной пары NetworkX + rustworkx: компилируемые Yen k-shortest paths (yen) и maximum_flow (Dinic, Edmonds-Karp), а также dijkstra, bellman_ford, connected_components — под BSD-3-Clause, без GPL.
Уже является транзитивной зависимостью научного стека Python.
  ASSESSMENT: Проверено чтением __init__.py на теге v1.18.1: yen и maximum_flow присутствуют; PyPI 1.18.1 (2026-08-21) имеет wheel cp313-win_amd64. Ограничения: работает на CSR-матрице (простой взвешенный граф, без мультирёбер и атрибутов —
подходит только для схлопнутого представления); maximum_flow требует целочисленные ёмкости фиксированного dtype (проверка против ITYPE в _flow.pyx) — суммы в raw-единицах USDT могут не поместиться. Включить в benchmark.

- Google OR-Tools 9.15 (max_flow, min_cost_flow) (https://github.com/google/or-tools/tree/stable/ortools/graph/python)
  WHY: Промышленная реализация max-flow и min-cost-flow с 64-битными ёмкостями под Apache-2.0 — прямой кандидат для атрибуции сумм между источником и стоками на схлопнутом графе без GPL (альтернатива igraph.maxflow).
  ASSESSMENT: gh api: Apache-2.0, 14,190 stars, push 2026-10-13; в ortools/graph/python есть max_flow.cc, min_cost_flow.cc; PyPI ortools 9.15.6755 (2026-01-14) имеет wheel cp313-win_amd64. Только flow-задачи, без путей и сообществ. Функционал и
производительность не запускались.

- ArcadeDB — встроенная библиотека графовых алгоритмов (недооценён, а не пропущен) (https://github.com/ArcadeData/arcadedb/tree/26.10.1/engine/src/main/java/com/arcadedb/query/opencypher/procedures/algo)
  WHY: Единственная проверенная СУБД под Apache-2.0, где в коде одновременно есть k-shortest paths, max-flow, all simple paths, Leiden, Louvain, betweenness, personalized PageRank, node2vec, FastRP — то есть то, ради чего в аудите
эталоном назван Neo4j GDS под GPLv3 с лимитом 4 ядра. Есть Bolt, openCypher, Postgres wire protocol и embedded-пакет для Python.
  ASSESSMENT: 69 файлов процедур на теге 26.10.1, 99 файлов тестов; релизы ежемесячные (26.10.1 от 2026-10-05). Риски: процедурам менее 8 месяцев (первый коммит 2026-02-23), основной автор один (lvca), JVM, корректность не проверялась. Должен
быть обязательной конфигурацией benchmark Этапа 2, а не опциональной.

- On-chain события AddedBlackList контракта USDT TRC20 (TronGrid events API) (https://api.trongrid.io/v1/contracts/TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t/events?event_name=AddedBlackList&limit=3)
  WHY: Первичный, бесплатный и проверяемый по TXID источник ground truth именно для USDT TRC20: адреса, замороженные Tether, с номером блока и временем. Годится и как метка с source + check date, и как генератор реальных кейсов для 50+
сценариев и для независимого тестового набора. В аудите идея записана как непроверенная.
  ASSESSMENT: Проверено вживую без ключа: success=true, вернулись 3 события AddedBlackList с block_number 87075502 / 87052932 / 87052931, transaction_id и адресом в поле _user (hex-формат, нужна конвертация в base58). Метка означает только факт
заморозки, а не тип преступления; лимиты и полнота пагинации не проверялись.

- GraphSense (graphsense-lib, graphsense-tagpacks) (https://github.com/graphsense/graphsense-lib)
  WHY: Открытая (MIT) платформа крипто-аналитики с поддержкой TRON на уровне кода и публичным репозиторием атрибуционных меток TagPacks, где каждая метка обязана иметь dereferenceable-ссылку на источник — ровно требование проекта 'метка
+ источник'. Референс-архитектура показывает, что зрелая open-source платформа трассировки обходится без графовой СУБД (Cassandra + TagStore на PostgreSQL), что поддерживает вывод аудита.
  ASSESSMENT: gh api: graphsense-lib MIT, push 2026-10-13, 20 stars; code search 'trx' — 172 совпадения (transformation/account_trx.py, spark/.../account/trx/Model.scala). graphsense-tagpacks MIT, push 2026-10-13: packs/ содержит exchange-
wallets-binance/okx/kucoin/huobi/bybit, ofac, lazarus, hacks и др. Инфраструктура (Cassandra + Spark) избыточна для одного сервера — брать идеи и TagPacks, а не платформу. Доля TRON-адресов в TagPacks не проверялась.

- Apache HugeGraph 1.7.0 (https://github.com/apache/hugegraph)
  WHY: Apache-2.0 графовая СУБД с режимом standalone (один узел, RocksDB), Gremlin + OpenCypher и встроенными REST-traverser'ами под антифрод-сценарии: k-out, k-neighbor, paths, customized paths, rings, rays, crosspoints, shortest / all
shortest / weighted / multi-node shortest path, personal rank. В аудите отсутствует, хотя по лицензии и набору обходов сопоставим с отобранными кандидатами.
  ASSESSMENT: gh api: Apache-2.0, 3,192 stars, 386 open issues, push 2026-10-13, релиз 1.7.0 от 2025-11-16; каталог api/traversers содержит 26 API. Минусы: JVM, k-shortest и max-flow среди traverser'ов нет, тяжёлые алгоритмы вынесены в
отдельный hugegraph-computer (65 stars), релизы примерно раз в год. Кандидат второго ряда для benchmark.

- NeuG (Alibaba GraphScope) 0.2.1 (https://github.com/alibaba/neug)
  WHY: Новый (2026) embedded + service графовый движок с Cypher под Apache-2.0 — прямой конкурент LadybugDB в нише 'DuckDB для графов', появившийся после архивации Kuzu.
  ASSESSMENT: gh api: создан 2026-03-02, Apache-2.0, 169 stars, релизы v0.2.1 (2026-09-30), v0.2.0 (2026-09-03); PyPI neug 0.2.1 имеет wheels cp313-win_amd64. Docs: расширение GDS (с v0.1.3) — PageRank, BFS, SSSP, WCC, LCC, K-Core, Label
Propagation, Louvain, Leiden; k-shortest, max-flow, betweenness нет. Версия 0.x, 7 месяцев, benchmark'и только от вендора. Наблюдать, в MVP не закладывать.

- TRON-USDT dataset из статьи 'Detection of Crowdsourcing Cryptocurrency Laundering via Multi-Task Collaboration' (arXiv 2512.02534) (https://arxiv.org/abs/2512.02534)
  WHY: Единственный найденный графовый размеченный набор именно по USDT на TRON: по статье ≈1,043K адресов, 2.6M транзакций, 18,997 меток транзакционных групп в 193 группах — на порядки больше Mendeley-набора и с рёбрами.
  ASSESSMENT: Статья от 2025-12-02 (Sun Yat-sen University); ссылка на данные — папка Google Drive, лицензия не указана, код модели не опубликован. Состав папки не проверялся. До письменного разрешения авторов использовать нельзя; стоит
запросить.

- OneSparse (GraphBLAS / LAGraph внутри PostgreSQL) (https://github.com/OneSparse/OneSparse)
  WHY: Расширение PostgreSQL на SuiteSparse:GraphBLAS и LAGraph под Apache-2.0 — способ получить графовые алгоритмы внутри единственной СУБД без GPL pgRouting и без agtype-хранилища AGE.
  ASSESSMENT: gh api: Apache-2.0, 409 stars, push 2026-10-13, 0 open issues; README описывает сборку контейнера с PostgreSQL + GraphBLAS + LAGraph. Набор алгоритмов, поддерживаемые версии PostgreSQL и зрелость не проверялись; малое сообщество.
Кандидат на пробу вместо pgRouting.

- IBM AMLworld — лицензия установлена (уточнение к кандидату аудита) (https://www.kaggle.com/datasets/ealtman2019/ibm-transactions-for-anti-money-laundering-aml)
  WHY: В аудите набор понижен из-за неподтверждённой лицензии; фактически это единственный из рассмотренных публичных AML-наборов с графовой структурой и лицензией, допускающей коммерческое использование.
  ASSESSMENT: Kaggle API: CDLA-Sharing-1.0, обновлён 2025-07-08, ≈41.6 GB суммарно. Синтетика банковских переводов, не блокчейн; подходит для отладки детектора split/merge и пайплайна обучения вместо Elliptic.

- HelixDB 3.5.1 и pathpyG (рассмотрены и не рекомендуются) (https://github.com/HelixDB/helix-db)
  WHY: Заметные новые проекты 2025–2026, которые могут всплыть при выборе: HelixDB — graph-vector СУБД на Rust (6,198 stars), pathpyG — библиотека темпоральных путей.
  ASSESSMENT: HelixDB: Apache-2.0 (LICENSE прочитан), релиз v3.5.1 от 2026-10-08, собственный язык запросов и фокус на RAG/агентов, графовые алгоритмы не проверялись — не профильный. pathpyG: AGPL-3.0 (gh api), 59 stars — сетевая клауза AGPL
делает его непригодным для закрытого коммерческого SaaS.

============================================================
PART 2 - RESEARCHER AUDIT
============================================================

## RESEARCHER RECOMMENDATIONS

### R1. NEED: Хранилище графа и глобальная база знаний об адресах (MVP)
PRIMARY: PostgreSQL 18 как единственная СУБД (таблицы address / transfer / label / investigation + recursive CTE), без выделенной graph DB до результатов benchmark Этапа 2
RATIONALE: Оценка 'PostgreSQL only + in-memory библиотека' против выделенной graph DB. (1) Узкое место MVP — лимиты внешних API, а не графовый движок: живой запрос к TronGrid вернул 200 записей TRC20 за 0.77 с (71 KB); подграф на 1,000
адресов строится сетевыми запросами, после чего целиком помещается в память. (2) Подграфы 100–100,000 узлов — масштаб in-memory библиотек; graph DB здесь добавляет второй stateful-сервис, двойную запись и отдельный backup без
функциональной необходимости. (3) Лицензии: из проверенных graph DB чистыми для коммерческого SaaS и возможной on-prem поставки остаются только Apache AGE (Apache-2.0), LadybugDB (MIT), ArcadeDB (Apache-2.0). Neo4j Community —
GPLv3 (допустимо для SaaS, блокер для закрытой дистрибуции, нет online backup). Memgraph — BSL, grant сужен в январе 2026 до 'internal business purposes'. ArangoDB Community — коммерческий production запрещён. FalkorDB — SSPL. (4)
Глобальное знание об адресах в MVP — это поиск по индексу (метки, 'встречался ли адрес в других расследованиях', переводы адреса за окно времени), что PostgreSQL делает лучше графовой СУБД. (5) Требования к меткам (source, check
date, confidence), аудит-логу действий агентов и воспроизводимости естественно ложатся на реляционную схему. (6) Один сервис — один backup и одна процедура восстановления для маленькой команды.
ARCHITECTURE NOTES: Схема: transfer(chain, txid, event_ordinal, from_addr, to_addr, asset_contract, amount_raw NUMERIC, decimals, block_ts, block_number, source, fetched_at, raw_hash); индексы (from_addr, block_ts) и (to_addr, block_ts). ВАЖНО по
результату живого запроса: ответ TronGrid не содержит log index, в одном TXID бывает несколько событий (в выборке из 200 записей — TXID с 2 событиями), и в выдаче есть события type='Approval' (3 из 200) — их нужно отфильтровывать,
а ключ ребра делать (txid, event_ordinal), а не txid. label(address, category, entity, source, source_url, checked_at, confidence, evidence). investigation_edge фиксирует состав подграфа для воспроизводимости; снимок подграфа
экспортируется в Parquet/JSON с sha256. Recursive CTE — только с лимитом глубины, клаузой CYCLE, LATERAL ... LIMIT на fan-out и statement_timeout; обход останавливается на адресах с меткой exchange/service (защита от supernode).
Не закладываться на SQL/PGQ: откатан из PostgreSQL 19 (2026-09-07). Доступ к графу — через собственный интерфейс GraphStore, чтобы после Этапа 2 можно было подключить LadybugDB / AGE / Neo4j без переписывания агентов.
COST: Лицензии $0. Вклад графового слоя в переменную стоимость расследования ≈ $0 (CPU собственного сервера). Для сравнения фиксированные расходы альтернатив: AuraDB Professional от ≈ $65.70/мес за 1 GB ($0.09/GB/час), FalkorDB Cloud
Startup от $73/мес за 1 GB, Neptune db.r5.large ≈ $254/мес ($0.348/час) без учёта storage и I/O, TigerGraph Savanna от $1.00/час. Стоимость самого сервера не оценивалась.
DATA QUALITY VERIFICATION: Каждое ребро имеет NOT NULL txid и ссылку на сырой ответ источника (хэш); выборочная повторная сверка рёбер с первичным источником по TXID; идемпотентная повторная загрузка (тот же набор рёбер даёт то же число строк); property-
based тесты: результат recursive CTE на тестовых подграфах совпадает с эталоном NetworkX; регулярная проверка восстановления из backup (restore + сверка контрольных сумм таблиц).
RISKS: Деградация recursive CTE на supernode и при глубоких запросах по глобальному графу — проявится при росте числа расследований; отсутствие Cypher для ad-hoc запросов аналитиков; если владельцу понадобятся многошаговые запросы по
всему накопленному графу как продуктовая функция, потребуется graph DB или AGE.
REPLACEABILITY: Высокая: рёбра — обычные таблицы, выгружаются в Parquet/CSV и загружаются в LadybugDB, Neo4j или AGE; интерфейс GraphStore изолирует остальной код.
REJECTED ALTERNATIVES:
  - Neo4j Community + GDS: Функционально сильнейший вариант (Yen, max flow, Leiden в production-tier GDS), но GPLv3, в Community нет online backup, нескольких баз и RBAC, GDS CE ограничен 4 ядрами; второй stateful-сервис на JVM.
  - Оставить как эталон 'выделенной graph DB' в benchmark Этапа 2.
  - Memgraph Community + MAGE: BSL 1.1; коммитом от 2026-01-28 из Additional Use Grant удалено разрешение хостить интегрированное решение как SaaS — осталось только 'internal business purposes'. Для платного SaaS нужна OEM/SaaS-
  - лицензия с непубличной ценой. MAGE после слияния тоже под BSL.
  - ArangoDB: Документация 3.12: коммерческое использование Community Edition в production запрещено, лимит 100 GiB; исходники под BSL 1.1.
  - FalkorDB: SSPL-1.0: при предоставлении сервиса внешним пользователям требуется открыть код всего сервиса или купить коммерческую лицензию; линия 6.x на Rust вышла 2026-09-29.
  - Kuzu: Репозиторий архивирован 2025-10-10, последний релиз v0.11.3; сопровождения нет.
  - LadybugDB: Не отклонён, а отложен до сравнительного теста: MIT, embedded, активен (v0.21.2 от 2026-10-01), но версия 0.x с частыми релизами, модель single-writer, нет k-shortest / max-flow / betweenness.
  - Apache AGE: Не отклонён, а отложен до теста: Apache-2.0, сохраняет единый PostgreSQL, с 1.8.0 есть shortest_path SRF; но теги релизов '-rc0', хранение в agtype отдельно от реляционных таблиц, нет аналитических алгоритмов.
  - DuckDB + DuckPGQ: README DuckPGQ: исследовательский проект в разработке; только недетерминированный ANY SHORTEST; один мейнтейнер, нет релизов. DuckDB полезен отдельно как аналитический движок по Parquet-снимкам.
  - NebulaGraph, JanusGraph, Dgraph, TigerGraph, Amazon Neptune: Распределённые или облачные системы, избыточные для одного скромного сервера: NebulaGraph без релизов с 2024-05-17; JanusGraph требует Cassandra/HBase и индексный
  - движок, последний релиз 2024-11-09; Dgraph сменил владельца в 2025 и не поддерживает Cypher; TigerGraph проприетарен; Neptune — от сотен долларов в месяц и привязка к AWS.
  - SurrealDB, TypeDB, Grafeo, прочие форки Kuzu: SurrealDB — BSL и собственный язык без профильной графовой аналитики; TypeDB — иная парадигма (TypeQL); Grafeo — проекту менее 9 месяцев и один разработчик; Bighorn / Vela /
  - RyuGraph — малые сообщества по сравнению с LadybugDB.

### R2. NEED: In-process графовая аналитика подграфов расследования
PRIMARY: NetworkX 3.7 (эталон и полнота алгоритмов) + rustworkx 0.18.1 (ускоренные обходы, кратчайшие пути и центральности) за единым внутренним интерфейсом GraphEngine
RATIONALE: Обе библиотеки под разрешительными лицензиями (BSD-3-Clause и Apache-2.0), ставятся на Windows 11 / Python 3.13 готовыми wheels и не ограничивают будущую on-prem поставку. NetworkX покрывает всё требуемое: MultiDiGraph, simple
paths, Yen, max-flow, Louvain/Leiden, dominators, SCC/WCC — и служит эталоном корректности в тестах. rustworkx закрывает горячие пути (BFS/DFS с visitor, Dijkstra, all_simple_paths, betweenness, PageRank) на верхней границе
нагрузки. По отдельности каждая недостаточна: в rustworkx нет Yen, max-flow и community detection (0 совпадений в коде), а NetworkX на 100k узлов медленный и прожорливый по памяти. Сама логика трассировки (времени-упорядоченные
пути, пороги сумм, атрибуция потоков, остановка на сервисах) в любом случае остаётся собственным детерминированным кодом — библиотеки дают только примитивы.
ARCHITECTURE NOTES: Два представления одного подграфа: (а) темпоральный мультиграф — каждое ребро это отдельный Transfer с TXID, amount, timestamp, asset; (б) схлопнутый взвешенный DiGraph (сумма и число переводов на пару адресов со списком исходных
TXID) — обязателен для k-shortest и max-flow, потому что NetworkX не поддерживает их на мультиграфах (подтверждено кодом). Любой результат на схлопнутом графе разворачивается обратно в конкретные TXID. Детерминизм: сортировка
соседей, фиксированные seed для Louvain/Leiden, запись версий библиотек в журнал расследования. Betweenness на крупных подграфах — только приближённый (k-сэмплирование) либо через rustworkx. Алгоритмы на стороне UI (graphology) не
являются источником фактов.
COST: $0 лицензий; переменная стоимость — только CPU/RAM сервера. Потребление памяти и время на подграфе 100k узлов не измерялись и должны быть получены в benchmark Этапа 2.
DATA QUALITY VERIFICATION: Перекрёстная проверка движков: на тестовых сценариях результаты rustworkx должны совпадать с NetworkX (множества путей, длины, значения центральностей в пределах допуска). Инварианты: каждое ребро пути имеет TXID; сумма входящих и
исходящих по схлопнутому ребру равна сумме исходных Transfer; время вдоль пути не убывает. Синтетические графы с посаженными паттернами (peel chain, fan-out, fan-in, цикл) с известным ответом — часть обязательных 50+ сценариев.
RISKS: Память при нескольких параллельных расследованиях на 100k узлов; rustworkx в версии 0.x; ошибки при схлопывании мультиграфа могут исказить суммы потоков — нужен отдельный набор тестов.
REPLACEABILITY: Высокая: интерфейс GraphEngine позволяет заменить реализацию отдельного алгоритма на python-igraph, NetworKit или процедуру graph DB без изменения агентов.
REJECTED ALTERNATIVES:
  - python-igraph 1.0.0: Технически лучший одиночный кандидат (нативные мультирёбра, get_k_shortest_paths, maxflow, Leiden в C-ядре), но GPL-2.0-or-later: для SaaS допустимо, для закрытой поставки клиенту — блокер. Включить в
  - benchmark; использовать, только если владелец исключает on-prem дистрибуцию.
  - NetworKit 11.2.2: MIT и wheels под cp313 win_amd64, но ориентирован на простые графы с числовыми весами — годится только как ускоритель отдельных метрик, не как основная модель темпорального мультиграфа.
  - graph-tool 3.9: Нет сборки под Windows (conda-forge: только linux и osx), не ставится через pip.
  - cuGraph / nx-cugraph: Требует NVIDIA GPU и Linux — противоречит ограничению 'один скромный сервер'.
  - Raphtory 0.18.5: Темпоральная модель из коробки, но GPL-3.0 для линкуемой библиотеки, on-disk режим по подписке, малое сообщество.

### R3. NEED: Graph ML для изолированного экспериментального контура
PRIMARY: PyTorch Geometric 2.8.1 (включая встроенные TGN и Node2Vec) + протоколы оценки Temporal Graph Benchmark (py-tgb 2.3.0)
RATIONALE: PyG — единственный активно сопровождаемый универсальный GNN-фреймворк из проверенных (релиз 2.8.1 от 2026-10-06, Python 3.10–3.14, MIT), уже содержит загрузчики Elliptic и Elliptic Temporal, DGraphFin и реализацию TGN. DGL
фактически заброшен (последний релиз 2024-09, нет wheels под Python 3.13, открытая уязвимость исполнения кода). Оригинальные репозитории TGN, DyGLib и TGL не обновляются с 2023–2024 годов. TGB даёт корректные временные разбиения —
без них сравнение AI-слоя с baseline будет завышено из-за утечки будущего.
ARCHITECTURE NOTES: Контур физически изолирован: отдельный Linux-контейнер, вход — только замороженные снимки подграфов (Parquet), выход — оценки и ранжирование с пометкой 'ML-derived, not evidence'. Результаты ML не попадают в факты отчёта и не
используются для присвоения меток биржа/сервис: цель ≥95% точности меток должна достигаться проверяемыми источниками, а не GNN. Зафиксировать версию torch под доступные бинарники pyg-lib (README перечисляет до PyTorch 2.12 при
текущем torch 2.14.1). Первые эксперименты — классические признаки графа (степени, доли потоков, временные интервалы) + градиентный бустинг как baseline, затем GNN; на Elliptic такие baseline исторически конкурентны. Логировать
версии моделей, seed, датасет и хэш снимка.
COST: $0 лицензий; обучение на графах масштаба Elliptic (≈200k узлов) выполнимо на CPU. Для TGN на больших потоках событий может понадобиться GPU — не оценивалось.
DATA QUALITY VERIFICATION: Только временные разбиения train/val/test (обучение на прошлом, проверка на будущем); метрики PR-AUC и recall при фиксированной precision, а не accuracy (класс illicit ≈ 2%); обязательное сравнение с детерминированным baseline и с
не-графовым классификатором на тех же разбиениях; отдельная проверка на данных TRON, а не только Bitcoin.
RISKS: Доменный сдвиг: публичные размеченные датасеты почти все по Bitcoin (UTXO), по TRON найден один малый набор — ML-слой может не дать измеримого выигрыша в MVP. Хрупкая матрица совместимости torch ↔ pyg-lib.
REPLACEABILITY: Средняя: модели — стандартный PyTorch, формат данных PyG специфичен.
REJECTED ALTERNATIVES:
  - DGL: Последний коммит 2025-07-31, последний релиз v2.4.0 от 2024-09-03, на PyPI нет wheels для Python 3.13; issue #7934 (не собирается с PyTorch 2.14) и #7932 (arbitrary code execution) открыты.
  - PyTorch Geometric Temporal: Рассчитан на дискретные срезы и spatio-temporal сигналы, а не на событийный поток переводов; низкая активность (PyPI 0.56.2 от 2025-07-16).
  - twitter-research/tgn, DyGLib, amazon-science/tgl: Не обновлялись с 2024-05-28, 2023-09-28 и 2023-12-25 соответственно.
  - TGM (tgm-lib 0.1.0b1): Beta, 124 stars — пробовать позже, не закладывать в основу.
  - node2vec как основной метод: Трансдуктивен: эмбеддинги не переносятся на новые адреса без переобучения; годится только как дополнительный признак.

### R4. NEED: Эталонные датасеты и модели для illicit-flow detection
PRIMARY: Собственный набор ≥50 сценариев с ground truth по USDT TRC20 как основной эталон; из публичных — Mendeley TRON TRC20-USDT dataset (CC BY 4.0) для экспериментов и семейство Elliptic для отработки методик
RATIONALE: Публичного общепринятого benchmark по illicit-адресам TRON/TRC20 не найдено. Единственный специализированный набор — Mendeley (1,150 меток, 1,024 адреса TRC20-USDT, версия 3 от 2026-08-03, CC BY 4.0), он мал и деидентифицирован.
Elliptic / Elliptic++ / Elliptic2 — стандарт в литературе, но это Bitcoin, а лицензии либо не подтверждены, либо отсутствуют (у Elliptic++ нет файла лицензии). Поэтому требуемый независимый тестовый набор придётся собирать
самостоятельно из публичных кейсов, где каждый факт проверяется по TXID.
ARCHITECTURE NOTES: Три уровня данных: (1) собственные сценарии — реальные кейсы краж USDT TRC20 с известным исходом и синтетические графы с посаженными паттернами; (2) Mendeley TRON — только в ML-контуре, метки из него не попадают в продуктовую базу
меток без независимого подтверждения; (3) Elliptic / Elliptic2 / AMLworld — для отладки пайплайнов обучения и детектора split/merge. Набор для оценки точности меток (≥95%) должен быть независим от источников, которыми метки
присваиваются, иначе оценка будет завышена.
COST: $0 за данные; основная стоимость — ручная разметка и проверка 50+ сценариев (трудозатраты команды, не оценивались).
DATA QUALITY VERIFICATION: Для каждого сценария: список TXID, ожидаемые конечные адреса и суммы, источник истины (публичный отчёт, on-chain событие); двойная независимая разметка части сценариев; запрет использовать один и тот же источник и для присвоения
метки, и для её проверки; версионирование набора с хэшем.
RISKS: Юридическая неопределённость лицензий Elliptic, Elliptic2, Elliptic++ и AMLworld; метки Mendeley нельзя проверить первичным источником; малый размер TRON-набора не позволит обучить устойчивую модель.
REPLACEABILITY: Высокая: датасеты используются только в экспериментальном контуре.
REJECTED ALTERNATIVES:
  - Elliptic Data Set: Bitcoin, узлы — транзакции с анонимизированными признаками; лицензия на Kaggle не подтверждена. Использовать только для отладки методики.
  - Elliptic++: Адресный уровень (822,942 кошелька) полезен, но в репозитории нет лицензии — коммерческое использование без разрешения авторов недопустимо.
  - Elliptic2: Разметка подграфов методически близка к задаче, но лицензия данных не проверена, домен — Bitcoin.
  - IBM AMLworld: Синтетика банковских переводов, не блокчейн; лицензия данных не подтверждена. Годится только для тестов детектора паттернов.

### R5. NEED: Сравнительный benchmark Этапа 2 (обоснование окончательного выбора графового слоя)
PRIMARY: Собственный harness LH-GraphBench: один набор запросов и данных на семи конфигурациях движков
RATIONALE: В рамках аудита сторонний код не запускался, поэтому все утверждения о производительности — ожидания, а не измерения. Владелец требует, чтобы выбор следовал из сравнительного теста. Публичные benchmark (LDBC SNB и подобные)
измеряют социальные графы и не отражают нагрузку проекта: темпоральный мультиграф, времени-упорядоченные пути 10+ hops, supernode бирж, схлопывание мультирёбер для flow.
ARCHITECTURE NOTES: ДАННЫЕ. D1 — четыре реальных подграфа USDT TRC20 (≈100 / 1,000 / 10,000 / 100,000 уникальных адресов), собранные собственным загрузчиком из публичных кейсов и замороженные в Parquet с sha256; обязательно кейс с hot wallet биржи
(supernode) и кейс с цепочкой ≥10 hops. D2 — синтетический генератор с посаженным ground truth: peel chain на 10–20 hops, fan-out 1→k, fan-in k→1, циклы, несколько Transfer в одном TXID, пылевые ветви; масштабы 1 млн и 10 млн
рёбер для глобального слоя. D3 (опционально) — AMLworld для детектора split/merge при допустимой лицензии. КОНФИГУРАЦИИ. E0 PostgreSQL 18 только recursive CTE; E1 PostgreSQL + NetworkX 3.7; E2 PostgreSQL + rustworkx 0.18.1; E3
PostgreSQL + python-igraph 1.0.0; E4 LadybugDB 0.21.x; E5 Neo4j Community 2026.09 + GDS; E6 Apache AGE 1.8.0 на PG18; опционально DuckDB 1.5.6 + DuckPGQ и ArcadeDB 26.10.1. ЗАПРОСЫ. Q1 массовая и инкрементальная идемпотентная
загрузка рёбер; Q2 k-hop окрестность (k=1..3) с ограничением по времени; Q3 прямой trace на 10, 15 и 20 hops с монотонностью времени, порогом суммы и cap на степень; Q4 кратчайший путь от источника до множества размеченных
адресов; Q5 k-shortest paths (k=5, 10); Q6 все простые пути длиной ≤ L; Q7 max-flow / атрибуция суммы между источником и стоками на схлопнутом графе; Q8 детекция split/merge (fan-out ≥ k за окно Δt, fan-in); Q9 WCC/SCC; Q10
PageRank и приближённый betweenness на 100k узлов; Q11 Louvain/Leiden; Q12 кросс-расследовательские запросы на 10 млн рёбер (общие адреса двух расследований, все переводы адреса за окно); Q13 пять параллельных расследований с
одновременной записью и чтением. Прогоны — на целевом сервере и на dev-машине (Windows 11 + Docker), 5 повторов, cold и warm, с зафиксированными версиями; сетевые вызовы заменены воспроизведением записанных ответов API.
COST: Лицензии $0 (все конфигурации бесплатны для тестирования). Оценка трудозатрат: порядка 1–2 недель одного инженера на harness, генератор и отчёт — это предположение, не проверенная величина.
DATA QUALITY VERIFICATION: МЕТРИКИ. Корректность: точное совпадение с эталоном (посаженный ground truth в D2 и результаты NetworkX как оракул) — множества путей, значения flow, состав компонент; доля рёбер результата с TXID = 100%. Производительность:
p50/p95 латентности cold и warm, время загрузки подграфа из PostgreSQL в память, пиковый RSS, размер на диске, скорость загрузки (рёбер/с), сквозное время графа на 1,000 адресов (цель ≤ 5 мин) и отчёта на несколько десятков
адресов (цель ≤ 2 мин). Эксплуатация: время backup и проверенного restore, число контейнеров, шаги обновления версии, объём glue-кода, поведение при превышении памяти. Лицензионный фильтр: pass/fail для коммерческого SaaS и
отдельно для on-prem поставки. ПРАВИЛО РЕШЕНИЯ: остаётся 'PostgreSQL + in-memory', если выделенная graph DB не даёт выигрыша не менее чем в 3 раза по p95 на обязательных запросах уровня 100k узлов или не закрывает запрос, который
базовый вариант не укладывает в целевые сроки; при равенстве выбирается вариант с меньшим числом сервисов.
RISKS: Результат зависит от репрезентативности реальных подграфов D1; тюнинг движков (индексы, память JVM, проекции GDS) может исказить сравнение — настройки нужно зафиксировать и опубликовать вместе с результатами.
REPLACEABILITY: Harness остаётся регрессионным тестом производительности для последующего расширения на Ethereum, Bitcoin, BSC и Solana.
REJECTED ALTERNATIVES:
  - LDBC Social Network Benchmark: Измеряет социальный граф и интерактивные запросы; нет темпорального мультиграфа переводов, времени-упорядоченных путей и supernode бирж.
  - Опора на опубликованные вендорами benchmark: Маркетинговые сравнения выполнены на чужих данных и настройках; владелец требует собственный сравнительный тест.
  - Выбор без теста по результатам аудита: В аудите запрещено исполнение стороннего кода — измерений производительности нет.

### R6. NEED: Графовая модель и визуализация на стороне TypeScript/UI
PRIMARY: graphology 0.26.0 + sigma.js 4.0.1 (оба MIT)
RATIONALE: graphology даёт типизированную модель multi/directed графа для Node 23 и браузера и стандартную библиотеку (shortest-path, simple-path, Louvain, Leiden, metrics, layouts, GraphML/GEXF); sigma.js — WebGL-рендер для web-отчёта,
активно обновляется (4.0.1 от 2026-10-13).
ARCHITECTURE NOTES: UI получает готовый подграф и результаты расчётов с Python-стороны в формате node-link JSON; на клиенте выполняются только layout, фильтрация и подсветка. Расчёты, влияющие на факты отчёта, на клиенте не дублируются.
COST: $0.
DATA QUALITY VERIFICATION: Контрактные тесты формата обмена: число узлов и рёбер и набор TXID в UI совпадают с серверным снимком.
RISKS: Ядро graphology не обновлялось с 2025-01-26 (стабильно, но малоактивно); производительность рендера на 100k узлов не измерялась — для таких графов потребуется агрегация или постраничное раскрытие.
REPLACEABILITY: Высокая: cytoscape.js 3.34.3 (MIT) как прямая замена.
REJECTED ALTERNATIVES:
  - cytoscape.js 3.34.3: Равноценная альтернатива (MIT, активна), но canvas-рендер хуже масштабируется на тысячи узлов, чем WebGL в sigma.js — предположение, требующее проверки.
  - Дублирование алгоритмов трассировки на JS: Две реализации одной логики расходятся и подрывают воспроизводимость.
  - Neo4j Bloom / Memgraph Lab: Привязаны к соответствующим СУБД и их лицензиям; не встраиваются в собственный web-отчёт.

## LIVE PROBE FINDINGS
- gh api repos/kuzudb/kuzu: archived=true, pushed_at 2025-10-10, последний релиз v0.11.3 (2025-10-10), 4,022 stars; README начинается с 'Kuzu is working on something new! We are archiving the KuzuDB project'. Крупнейшие форки по
stars: Kineviz/bighorn (135), Vela-Engineering/kuzu (48).
- gh api repos/LadybugDB/ladybug: создан 2025-10-07, fork=false, MIT, 1,845 stars, 158 forks, релиз v0.21.2 (2026-10-01), последний коммит 2026-10-13; в последних 100 коммитах 9 авторов (Arun Sharma — 37). PyPI ladybug 0.21.2 имеет
wheels cp313 win_amd64; npm @ladybugdb/core 0.21.2.
- Чтение licenses/BSL.txt в memgraph/memgraph на двух ревизиях: на коммите 23c55aa2e0 (2025-12-23) Authorised Purpose включал интеграцию в собственное ПО и хостинг 'on a software-as-a-service' модели; на master (редакция 'January 1,
2026', коммит cef597d639 'Update licenses' от 2026-01-28) осталось только 'your internal business purposes'. Первый релиз под новой редакцией — v3.8.0 (2026-02-11).
- gh api repos/memgraph/mage: archived=true, последний коммит 2026-01-23 'Add merge completion details to README'; README: слияние в memgraph/memgraph завершено 2026-01-22, слитый код выпускается под BSL.
- FalkorDB: файл LICENSE в main — Server Side Public License v1; Cargo.toml: name='falkordb-rs', license='SSPL-1.0'; релизы v6.0.2 (2026-10-08) и параллельно v4.22.0 (2026-09-30).
- ArangoDB LICENSE (ветка devel): Business Source License 1.1, Additional Use Grant запрещает использование 'in a commercial offering that allows one or more third parties ... to access, create or manage databases'. Документация
3.12: 'The use for commercial purposes is prohibited for production', лимит 100 GiB.
- postgres/postgres: коммит b1f106c8 'Revert SQL Property Graph Queries (SQL/PGQ)' от 2026-09-07 (автор Peter Eisentraut), аналогичный 2b9e1aff в REL_19_STABLE; файла propgraphcmds.c нет ни в master, ни в REL_19_STABLE; страница
sql-commands документации 19 не содержит PROPERTY GRAPH; PostgreSQL 19 — Beta 4 от 2026-09-24, текущая стабильная 18.6.
- Apache AGE: релизы 'PG18/v1.8.0-rc0' (2026-07-09) и 'PG15/v1.8.0-rc0' (2026-09-19); строка shortestPath найдена в age--1.7.0--1.8.0.sql и age_vle.c; issue #2430 'Add shortest_path / all_shortest_paths SRFs' закрыт 2026-06-03; PyPI
apache-age-python — 0.0.7 от 2023-09-22.
- NetworkX (main): shortest_simple_paths помечен @not_implemented_for('multigraph') (simple_paths.py, строка 422); flow/utils.py, строки 108–109: 'MultiGraph and MultiDiGraph not supported (yet)'. В algorithms/community есть
louvain.py и leiden.py.
- rustworkx: поиск по коду репозитория даёт 0 совпадений для louvain, leiden, max_flow, yen и 59 для multigraph; в Python API есть k_shortest_path_lengths, но нет функции, возвращающей k кратчайших путей.
- python-igraph (graphobject.c): присутствуют методы get_k_shortest_paths, maxflow, maxflow_value, all_st_mincuts, gomory_hu_tree, dominator, community_leiden, community_multilevel, community_infomap, betweenness,
personalized_pagerank, count_multiple.
- DGL: последний коммит 2025-07-31, последний релиз v2.4.0 (2024-09-03), PyPI 2.2.1 (2024-05-13) с wheels только cp38–cp312; открытые issues #7934 (не собирается с PyTorch 2.14.0, 2026-09-13), #7932 (Arbitrary Code Execution,
2026-08-29), #7925 (Jenkins deprecated, 2026-06-19).
- PyTorch Geometric: релиз 2.8.1 (2026-10-06); в nn/models/node2vec.py — ImportError при отсутствии 'pyg-lib>=0.6.0'; в datasets есть elliptic.py, elliptic_temporal.py, dgraph.py, jodie.py; в nn/models — tgn.py. README перечисляет
бинарники расширений до PyTorch 2.12 при torch 2.14.1 на PyPI.
- Neo4j: распарсена таблица редакций Operations Manual — в Community отсутствуют Online backup and restore, Multiple databases, Role-based access control, Parallel Cypher runtime, Block format, Autonomous clustering; есть Offline
backup (dump). В neo4j/graph-data-science — класс OpenGdsConcurrencyValidator с сообщением 'Community users cannot exceed ...'.
- Живой keyless-запрос к api.trongrid.io (TRC20-история контракта USDT, limit=200): HTTP 200 за 0.77 с, 71,313 байт (≈357 байт на запись); поля записи: transaction_id, token_info{symbol,address,decimals,name}, block_timestamp (мс),
from, to, type, value (строка); log index отсутствует; среди 200 записей 197 Transfer и 3 Approval; 199 уникальных TXID (один TXID с двумя событиями).
- Пакетные реестры: graph-tool 3.9 на conda-forge только для linux и osx; cugraph 26.10.00 только linux; igraph 1.0.0 и rustworkx 0.18.1 имеют abi3-wheels win_amd64; networkit 11.2.2 — wheels cp313 win_amd64; grafeo 0.5.44 —
Windows-wheels только cp312.
- DuckPGQ: README — 'DuckPGQ is a research project and a work in progress'; GitHub Releases отсутствуют; документация — поддерживается только недетерминированный ANY SHORTEST.
- Состояние релизов: NebulaGraph — последний v3.8.0 от 2024-05-17; JanusGraph — v1.1.0 от 2024-11-09; Dgraph — v25.5.0 от 2026-10-13 (Apache-2.0); SurrealDB — BSL 1.1 с Change Date 2030-01-01; TypeDB — MPL-2.0, 3.13.6 от 2026-09-22.
- Датасеты: git-disl/EllipticPlusPlus — license=null, последний push 2023-11-25; Mendeley 62dmsngtfb — версия 3 от 2026-08-03, CC BY 4.0, 1,150 меток и 1,024 адреса TRC20-USDT.

## CANDIDATES (full audit cards)

### [RECOMMENDED] PostgreSQL 18 (таблица transfers + recursive CTE), без выделенной graph DB
NEED: Хранилище графа и глобальная база знаний об адресах (system of record)
KIND: open-source
URL: https://www.postgresql.org/
LICENSE: PostgreSQL License (permissive, BSD-подобная)
COMMERCIAL USE: Разрешено без условий, включая закрытый коммерческий SaaS и on-prem поставку.
PROJECT STATE: Текущая стабильная ветка 18.6 (первый релиз 18 — 2025-09-25, поддержка до 2030-11-14); 17.11, 16.15 поддерживаются. PostgreSQL 19 на 2026-10-14 не GA: Beta 4 от 2026-09-24.
CLAIMED VS ACTUAL: Широко анонсированная поддержка SQL/PGQ (GRAPH_TABLE, CREATE PROPERTY GRAPH) в PostgreSQL 19 НЕ состоится: фича была закоммичена в марте 2026, но откатана коммитом 'Revert SQL Property Graph Queries (SQL/PGQ)' от 2026-09-07
(b1f106c8 в master, 2b9e1aff в REL_19_STABLE); в документации 19 страниц PROPERTY GRAPH нет, в release notes 19 упоминаний нет. Блоги и поисковая выдача всё ещё описывают её как часть PG19.
CAPABILITIES: Рёбра-переводы как строки (TXID, amount, timestamp, asset) — мультиграф и темпоральность получаются естественно. WITH RECURSIVE с клаузами SEARCH BREADTH FIRST и CYCLE (есть в документации 18) закрывает ограниченный по глубине
k-hop/forward trace; LATERAL ... LIMIT даёт cap на fan-out. JSONB для сырых ответов API, ACID, row-level security, pg_dump/pg_basebackup/WAL-архив для backup. k-shortest, max-flow, community, centrality в ядре нет — выносятся в
in-memory библиотеку или pgRouting.
INFRA: Один контейнер Docker (работает на Windows 11 через Docker Desktop и на одном скромном Linux-сервере). Python: psycopg 3.3.6 (LGPL-3.0-only) или asyncpg 0.32.0 (Apache-2.0); TypeScript: pg 8.23.1 (MIT), postgres 3.4.9 (Unlicense).
PRICING/LIMITS: Лицензия $0. Переменная стоимость на расследование от графового слоя ≈ $0 (только CPU собственного сервера).
RISKS: Recursive CTE взрывается на supernode (hot wallet биржи с миллионами рёбер) — нужны обязательные cap на степень, statement_timeout и правило 'остановиться на размеченном сервисе'. Нет встроенных графовых алгоритмов. Запросы 10+
hops по глобальному графу без ограничений будут медленными — производительность не измерялась (см. benchmark Этапа 2).
REPLACEABILITY: Высокая: схема рёбер — обычные таблицы; экспорт в Parquet/CSV позволяет в любой момент загрузить данные в LadybugDB, Neo4j или AGE.
HOW VERIFIED: docs read (postgresql.org versioning, queries-with, release-19, sql-commands 19 через curl); API call (gh api search/commits и commits/b1f106c8 в postgres/postgres); PyPI/npm JSON API для драйверов.
CONFIDENCE: high
EVIDENCE: https://www.postgresql.org/support/versioning/ | https://www.postgresql.org/docs/18/queries-with.html | https://www.postgresql.org/docs/19/release-19.html | https://github.com/postgres/postgres/commit/b1f106c80cbeb18d3a0219994d98a51a6eca8ede | https://pypi.org/project/psycopg/ | https://pypi.org/project/asyncpg/

### [NEEDS-TRIAL] Apache AGE 1.8.0 (openCypher-расширение PostgreSQL)
NEED: Хранилище графа и глобальная база знаний об адресах (system of record)
KIND: open-source
URL: https://github.com/apache/age
LICENSE: Apache-2.0
COMMERCIAL USE: Разрешено, включая коммерческий SaaS.
PROJECT STATE: Не архивирован; 4,887 stars, 255 open issues; последний коммит 2026-10-13. Релизы: 'PG18/v1.8.0-rc0' (2026-07-09), 'PG15/v1.8.0-rc0' (2026-09-19), 'PG17/v1.7.0-rc0' (2026-02-11). README: поддержка PostgreSQL 11–18; есть ветка
PG19. CI: installcheck.yaml + workflows для драйверов python/nodejs/go/jdbc.
CLAIMED VS ACTUAL: Все теги релизов имеют суффикс '-rc0' при названии 'Release v1.8.0'; для PG17 версии 1.8.0 на дату аудита нет (только 1.7.0). Пакет apache-age-python на PyPI застрял на 0.0.7 от 2023-09-22, хотя драйвер в репозитории развивается —
ставить придётся из исходников.
CAPABILITIES: openCypher поверх PostgreSQL, variable-length edges (age_vle.c), с 1.8.0 — SRF shortest_path / all_shortest_paths (issue #2430 закрыт 2026-06-03, #2442 — фильтры по типу связи и min hops). Сохраняет единый Postgres в эксплуатации
(один backup, одна транзакционность). k-shortest, max-flow, community, centrality отсутствуют.
INFRA: Docker-образ apache/age; нативной сборки под Windows нет (только Docker).
PRICING/LIMITS: Лицензия $0.
RISKS: Данные хранятся в отдельных label-таблицах с типом agtype — либо дублирование реляционной таблицы transfers, либо синхронизация. Производительность VLE на supernode неизвестна. Не на всех managed PostgreSQL доступен. Аналитические
алгоритмы всё равно придётся брать из in-memory библиотеки.
REPLACEABILITY: Средняя: Cypher-запросы переносимы в Neo4j/LadybugDB, но agtype-хранилище специфично.
HOW VERIFIED: API call (gh api repos/apache/age, releases, branches, commits, search/code, search/issues); code read (README, drivers/python/setup.py); PyPI JSON API.
CONFIDENCE: medium
EVIDENCE: https://github.com/apache/age | https://github.com/apache/age/releases | https://github.com/apache/age/issues/2430 | https://pypi.org/project/apache-age-python/

### [ALTERNATIVE] pgRouting 4.0.2 (графовые алгоритмы внутри PostgreSQL)
NEED: Хранилище графа и глобальная база знаний об адресах (system of record)
KIND: open-source
URL: https://github.com/pgRouting/pgrouting
LICENSE: GPL-2.0 (LICENSE в репозитории)
COMMERCIAL USE: Для SaaS допустимо (GPL не срабатывает без распространения; расширение загружается в сервер PostgreSQL, а не линкуется с приложением). При поставке on-prem клиенту возникают copyleft-обязательства на само расширение.
PROJECT STATE: Не архивирован; 1,439 stars; релизы v4.0.2 (2026-09-05), v4.0.1 (2026-01-31), v4.0.0 (2025-11-07); коммиты до 2026-10-09.
CLAIMED VS ACTUAL: Проект ориентирован на дорожные сети: требует целочисленных id вершин и модели cost/reverse_cost; мультиграф и временные ограничения переводов придётся кодировать вручную. Расхождений между заявленным и фактическим не найдено.
CAPABILITIES: В каталоге sql/ есть семейства ksp (k-shortest paths), max_flow, mincut, dijkstra, bdDijkstra, components, dominator, metrics, contraction, traversal — то есть k-shortest и flow доступны прямо в SQL поверх таблицы рёбер.
INFRA: Расширение PostgreSQL; готовые Docker-образы pgrouting/pgrouting; под Windows — только через Docker.
PRICING/LIMITS: Лицензия $0.
RISKS: GPL-2.0 при on-prem поставке; маппинг TRON-адресов в bigint; нет community detection; алгоритмы загружают выбранный подграф в память backend-процесса.
REPLACEABILITY: Высокая: используется точечно, как набор функций.
HOW VERIFIED: API call (gh api repos, releases, commits, contents/sql); code read (LICENSE).
CONFIDENCE: medium
EVIDENCE: https://github.com/pgRouting/pgrouting | https://github.com/pgRouting/pgrouting/tree/develop/sql

### [NEEDS-TRIAL] LadybugDB 0.21.2 (преемник Kuzu, embedded graph DB)
NEED: Хранилище графа и глобальная база знаний об адресах (system of record)
KIND: open-source
URL: https://github.com/LadybugDB/ladybug
LICENSE: MIT
COMMERCIAL USE: Разрешено без условий.
PROJECT STATE: Репозиторий создан 2025-10-07 (за 3 дня до архивации Kuzu), не помечен как GitHub-fork, но история коммитов Kuzu сохранена. 1,845 stars, 158 forks, 106 open issues. Релизы v0.21.2 (2026-10-01), v0.21.1 (09-30), v0.21.0 (09-29),
v0.20.4 (09-10); коммиты ежедневно, последний 2026-10-13. В последних 100 коммитах 9 авторов, 37 — Arun Sharma. CI: ci-workflow, nightly-sanitizers, codeql, python-wheel, nodejs, wasm.
CLAIMED VS ACTUAL: README повторяет формулировки Kuzu о production-готовности, но версия 0.x с тремя релизами за три дня (0.21.0–0.21.2) говорит о нестабильности. k-shortest paths, max-flow, betweenness и Leiden отсутствуют. Сторонние гайды по
миграции предупреждают, что файлы Kuzu нельзя просто переименовать — нужен EXPORT/IMPORT.
CAPABILITIES: Embedded, Cypher, колоночное хранение, ACID. Рекурсивные пути: SHORTEST, ALL SHORTEST, WSHORTEST(prop), ALL WSHORTEST, семантики WALK/TRAIL/ACYCLIC, верхняя граница hops по умолчанию 30. Расширение algo: K-Core, Louvain, PageRank,
SCC, WCC. Python: pip install ladybug (0.21.2, есть wheels cp313 win_amd64); Node: @ladybugdb/core 0.21.2 (MIT, с типами).
INFRA: Библиотека в процессе приложения, без сервера. Работает на Windows 11 / Python 3.13 нативно.
PRICING/LIMITS: Лицензия $0. Конкурентность: один READ_WRITE Database-объект на файл либо несколько READ_ONLY; смешивать нельзя.
RISKS: Молодой проект с концентрацией на одном лидере, финансирование и governance не подтверждены. Модель single-writer осложняет параллельные расследования в нескольких процессах. Backup — копирование файла или EXPORT DATABASE.
Проекции графа для алгоритмов привязаны к Connection.
REPLACEABILITY: Высокая: Cypher + импорт/экспорт Parquet/CSV.
HOW VERIFIED: API call (gh api repos, releases, commits, contributors, contents/.github/workflows); code read (README); docs read (concurrency, match, extensions/algo); PyPI и npm JSON API.
CONFIDENCE: medium
EVIDENCE: https://github.com/LadybugDB/ladybug | https://docs.ladybugdb.com/concurrency | https://docs.ladybugdb.com/cypher/query-clauses/match | https://docs.ladybugdb.com/extensions/algo | https://pypi.org/project/ladybug/

### [REJECTED] Kuzu (kuzudb/kuzu)
NEED: Хранилище графа и глобальная база знаний об адресах (system of record)
KIND: open-source
URL: https://github.com/kuzudb/kuzu
LICENSE: MIT
COMMERCIAL USE: Формально разрешено, но проект мёртв.
PROJECT STATE: АРХИВИРОВАН: archived=true, последний push 2025-10-10, последний релиз v0.11.3 (2025-10-10), 4,022 stars, 329 open issues заморожены. В README: 'Kuzu is working on something new! We are archiving the KuzuDB project'. Сайт снят,
документация перенесена на kuzudb.github.io. По сообщениям прессы (BetaKit, MacDailyNews, февраль 2026, со ссылкой на раскрытие в ЕС) компанию купила Apple.
CLAIMED VS ACTUAL: Во многих обзорах и сравнениях 2025–2026 годов Kuzu всё ещё рекомендуется как 'DuckDB для графов'; фактически исправлений безопасности и новых релизов не будет, сервер расширений отключён (в 0.11.3 часть расширений встроена).
CAPABILITIES: Функционально то же, что LadybugDB на момент форка; PyPI kuzu 0.11.3 ещё имеет wheels cp313 win_amd64.
PRICING/LIMITS: $0.
RISKS: Нет сопровождения и security-патчей; несовместимость с будущими версиями Python неизбежна.
REPLACEABILITY: Миграция на LadybugDB через EXPORT/IMPORT DATABASE.
HOW VERIFIED: API call (gh api repos/kuzudb/kuzu, releases, commits, forks); code read (README); search snippet only — для сделки с Apple.
CONFIDENCE: high
EVIDENCE: https://github.com/kuzudb/kuzu | https://betakit.com/apple-strikes-deal-to-acquire-canadian-database-software-startup-kuzu/

### [REJECTED] Прочие форки Kuzu: Kineviz/bighorn, Vela-Engineering/kuzu, predictable-labs/ryugraph
NEED: Хранилище графа и глобальная база знаний об адресах (system of record)
KIND: open-source
URL: https://github.com/Kineviz/bighorn
LICENSE: MIT (bighorn, Vela); ryugraph — лицензия не распознана GitHub (NOASSERTION)
COMMERCIAL USE: MIT-форки — разрешено; ryugraph — не проверено.
PROJECT STATE: Kineviz/bighorn: 135 stars, последний push 2026-08-10. Vela-Engineering/kuzu: 48 stars, push 2026-09-27. predictable-labs/ryugraph: 146 stars, push 2026-01-20. opencypher/cypherdb (форк) — архивирован, push 2026-01-26.
CLAIMED VS ACTUAL: Каждый форк позиционируется как продолжение Kuzu, но по активности и сообществу все на порядок слабее LadybugDB (1,845 stars, ежедневные коммиты).
PRICING/LIMITS: $0.
RISKS: Малое сообщество, риск заброшенности, фрагментация экосистемы.
HOW VERIFIED: API call (gh api repos/kuzudb/kuzu/forks и repos/* для каждого).
CONFIDENCE: medium
EVIDENCE: https://github.com/Kineviz/bighorn | https://github.com/Vela-Engineering/kuzu | https://github.com/predictable-labs/ryugraph

### [ALTERNATIVE] Neo4j Community Edition 2026.09 + Graph Data Science (GDS) 2026.09
NEED: Хранилище графа и глобальная база знаний об адресах (system of record)
KIND: open-source
URL: https://github.com/neo4j/neo4j
LICENSE: Neo4j Community: GPL-3.0. GDS: открытые исходники (OpenGDS) под GPL-3.0; бинарник GDS от Neo4j включает закрытые модули и распространяется по собственной лицензии. Драйверы: Python neo4j 6.4.0 (Apache-2.0), JS neo4j-driver 6.2.0
(Apache-2.0).
COMMERCIAL USE: Для SaaS, где Neo4j — внутренний сервер, а приложение ходит по Bolt через Apache-2.0 драйвер, GPLv3 формально не требует раскрытия кода приложения (нет network-клаузы, в отличие от AGPL). При поставке on-prem / распространении
образов вместе с Neo4j возникают обязательства GPLv3. Позицию нужно подтвердить у юриста.
PROJECT STATE: neo4j/neo4j: 17,314 stars, push 2026-10-09, теги 2026.09.0 / 2026.08.1. neo4j/graph-data-science: 825 stars, релизы 2026.09.0 (2026-09-21), 2026.08.1 (2026-09-11).
CLAIMED VS ACTUAL: 'Free and open source' скрывает ограничения Community: по таблице в Operations Manual в Community НЕТ online backup/restore (только offline dump), нескольких баз, RBAC, parallel runtime, block format, кластера, constraints
существования/ключа. GDS Community ограничен 4 ядрами CPU (страница pricing); в OpenGDS есть валидатор 'Community users cannot exceed ...'. README GDS прямо говорит, что официальный бинарник содержит закрытые исходники.
CAPABILITIES: Самый полный набор под нагрузку проекта: в GDS в production-tier числятся Yen's k-shortest, Dijkstra, A*, BFS/DFS, Maximum flow, Minimum cost maximum flow, Bellman-Ford, Steiner tree; плюс Louvain/Leiden, centrality, node
embeddings.
INFRA: JVM-сервер, Docker; для графов до 100k узлов нужен heap + page cache порядка нескольких ГБ. Второй stateful-сервис рядом с PostgreSQL.
PRICING/LIMITS: Community — $0. Enterprise и GDS Enterprise — 'contact sales', цены не публикуются.
RISKS: Нет горячего backup в Community (остановка для dump); двойная запись PostgreSQL + Neo4j и согласованность; GPLv3 блокирует закрытую on-prem поставку; лимит 4 ядра в GDS CE; операционная нагрузка для маленькой команды.
REPLACEABILITY: Средняя: Cypher переносим в LadybugDB/AGE/Memgraph, процедуры GDS — нет.
HOW VERIFIED: API call (gh api repos, releases, tags, search/code); code read (LICENSE.txt обоих репозиториев, README.adoc GDS, OpenGdsConcurrencyValidator.java); docs read (operations-manual/introduction — таблица редакций распарсена через
curl; algorithms/pathfinding; pricing).
CONFIDENCE: high
EVIDENCE: https://github.com/neo4j/neo4j | https://github.com/neo4j/graph-data-science | https://neo4j.com/docs/operations-manual/current/introduction/ | https://neo4j.com/docs/graph-data-science/current/algorithms/pathfinding/ | https://neo4j.com/pricing/ | https://neo4j.com/licensing/

### [REJECTED] Neo4j AuraDB (managed) и Aura Graph Analytics
NEED: Хранилище графа и глобальная база знаний об адресах (system of record)
KIND: commercial SaaS
URL: https://neo4j.com/pricing/
LICENSE: Проприетарный managed-сервис
COMMERCIAL USE: Разрешено на платных тарифах по условиям сервиса (условия не акцептовались и детально не читались).
PROJECT STATE: Действующий коммерческий сервис.
CLAIMED VS ACTUAL: Страница pricing не называет конкретных лимитов Free ('places limits on the number of nodes and relationships'); цифры 200k узлов / 400k связей и пауза после 3 дней простоя найдены только в поисковой выдаче по FAQ, при этом другие
страницы Neo4j показывают 50k/175k.
CAPABILITIES: Управляемый Neo4j; алгоритмы GDS доступны отдельным serverless-продуктом Aura Graph Analytics.
PRICING/LIMITS: Professional: от $0.09/GB/час при минимуме 1 GB (≈ $65.70/мес при 730 ч — мой расчёт). Business Critical: от $0.20/GB/час, минимум 2 GB (≈ $292/мес). Aura Graph Analytics: $0.40/GB/час. Virtual Dedicated Cloud и AuraDS Enterprise
— contact sales.
RISKS: Постоянная месячная плата до появления выручки; данные расследований уходят третьей стороне (юрисдикция, конфиденциальность); Free непригоден для production (пауза, малые лимиты, нет backup).
REPLACEABILITY: Средняя (dump/restore в self-hosted Neo4j).
HOW VERIFIED: docs only (neo4j.com/pricing); search snippet only — лимиты Free.
CONFIDENCE: medium
EVIDENCE: https://neo4j.com/pricing/ | https://neo4j.com/cloud/platform/aura-graph-database/faq/

### [REJECTED] Memgraph Community 3.13.2 + MAGE
NEED: Хранилище графа и глобальная база знаний об адресах (system of record)
KIND: open-source
URL: https://github.com/memgraph/memgraph
LICENSE: Business Source License 1.1 (source-available, НЕ open source) с Additional Use Grant в редакции от 2026-01-01; Change Date 2030-09-10 → Apache-2.0. Enterprise — Memgraph Enterprise License. MAGE после слияния — тоже BSL.
COMMERCIAL USE: Для коммерческого SaaS — юридически рискованно без отдельной OEM/SaaS-лицензии. Текущий grant разрешает только 'internal business purposes' с запретами embed/distribute, DBaaS и конкурирующих продуктов.
PROJECT STATE: 4,613 stars, 861 open issues, push 2026-10-13; релизы v3.13.2 (2026-10-09), v3.13.1 (09-14), v3.13.0 (09-09). memgraph/mage АРХИВИРОВАН 2026-01-23: слияние в memgraph/memgraph завершено 2026-01-22.
CLAIMED VS ACTUAL: Страница pricing: 'Free, forever, open source' — но BSL не является open source (это написано в самом тексте лицензии). КЛЮЧЕВОЕ: до 2025-12-23 grant прямо разрешал интегрировать Memgraph в собственный продукт и хостить такой
'Integrated Solution' по модели software-as-a-service; коммитом cef597d639 'Update licenses' от 2026-01-28 эти пункты удалены. Последний релиз со старым grant — v3.7.2 (2025-12-23); с v3.8.0 (2026-02-11) действует новый. MAGE был
Apache-2.0, после слияния новый код — под BSL. Dynamic-алгоритмы (online PageRank, betweenness, node2vec_online и др.) с Memgraph 3.0 — только Enterprise.
CAPABILITIES: In-memory Cypher-СУБД (Bolt, совместима с neo4j-драйверами; pymgclient 1.6.0 с wheels cp313 win_amd64). Алгоритмы: BFS/DFS, weighted shortest path, all shortest paths, K shortest paths, max_flow, betweenness, PageRank, Louvain,
Leiden, node2vec, temporal_graph_networks, gnn_link_prediction.
INFRA: Отдельный сервис, весь граф в RAM (плюс snapshots/WAL).
PRICING/LIMITS: Community — $0. Enterprise и Cloud: цены не публикуются ('Priced on total memory', 1–32 GB RAM, contact us). Есть отдельная OEM / SaaS лицензия.
RISKS: Сужение лицензии в 2026 году показывает, что условия могут ужесточаться и дальше; в Community нет RBAC, multi-tenancy, HA, TTL, CRON-snapshots; память — основной ограничитель и основа ценообразования.
REPLACEABILITY: Средняя: Cypher/Bolt переносимы, MAGE-процедуры — нет.
HOW VERIFIED: code read (licenses/BSL.txt на master и на коммите 23c55aa2e0 — сравнение двух редакций; LICENSE; README mage); API call (gh api commits?path=licenses/BSL.txt, commits/cef597d639, releases, repos/memgraph/mage); docs read
(memgraph.com/pricing, /legal, available-algorithms, enabling-memgraph-enterprise).
CONFIDENCE: high
EVIDENCE: https://github.com/memgraph/memgraph/blob/master/licenses/BSL.txt | https://github.com/memgraph/memgraph/commit/cef597d639 | https://github.com/memgraph/memgraph/blob/23c55aa2e0/licenses/BSL.txt | https://github.com/memgraph/mage | https://memgraph.com/pricing | https://memgraph.com/legal

### [REJECTED] ArangoDB 3.12 (Community / Enterprise)
NEED: Хранилище графа и глобальная база знаний об адресах (system of record)
KIND: open-source
URL: https://github.com/arangodb/arangodb
LICENSE: Исходники: Business Source License 1.1 (Change License Apache-2.0 через 4 года после релиза). Бинарники и образы Community Edition: ArangoDB Community License.
COMMERCIAL USE: Запрещено для production в Community Edition. Для коммерческого использования нужна Enterprise Edition.
PROJECT STATE: 14,280 stars, 868 open issues, push 2026-10-13; теги v3.12.12.1, v3.12.12; GitHub Releases не публикуются. Компания переехала на домен arango.ai; в документации есть ветки 4.x.
CLAIMED VS ACTUAL: До версии 3.12 ArangoDB был Apache-2.0, и многие обзоры до сих пор так его описывают. Фактически: документация 3.12 — 'The use for commercial purposes is prohibited for production', лимит датасета 100 GiB, нет права 'distribute,
embed within other products'. BSL-grant для исходников запрещает коммерческое предложение, где третьи лица получают доступ к базам. Блог 2024 года говорил о лимите '100 GB на кластер, до трёх кластеров', текущие docs — о едином
лимите 100 GiB.
CAPABILITIES: Multi-model (document + graph), AQL с обходами, K_SHORTEST_PATHS; драйверы python-arango 8.3.6 (MIT), arangojs 10.5.0 (Apache-2.0).
PRICING/LIMITS: Community — $0 (не для коммерческого production, ≤100 GiB). Enterprise — цена по запросу.
RISKS: Лицензионный блокер для платного SaaS; AQL — отдельный язык (lock-in).
HOW VERIFIED: code read (LICENSE в ветке devel); docs read (docs.arango.ai/arangodb/3.12/features); API call (gh api repos, tags). Полный текст Community License (PDF) прочитать не удалось.
CONFIDENCE: high
EVIDENCE: https://github.com/arangodb/arangodb/blob/devel/LICENSE | https://docs.arango.ai/arangodb/3.12/features/ | https://arango.ai/wp-content/uploads/2025/11/ADB-Community-License_31OCT2023.pdf

### [REJECTED] FalkorDB 6.0.2
NEED: Хранилище графа и глобальная база знаний об адресах (system of record)
KIND: open-source
URL: https://github.com/FalkorDB/FalkorDB
LICENSE: Server Side Public License v1 (SSPL-1.0) — подтверждено файлом LICENSE и полем license в Cargo.toml. Клиенты: falkordb (PyPI 1.7.1), falkordb (npm 6.8.0, MIT).
COMMERCIAL USE: Рискованно для SaaS. По собственному FAQ FalkorDB: внутреннее использование не требует раскрытия кода, но если FalkorDB является частью сервиса для внешних пользователей — нужно открыть исходники всего сервиса под SSPLv1 либо
купить коммерческую лицензию.
PROJECT STATE: 9,566 stars, 1,002 open issues, push 2026-10-13. Две параллельные линии релизов: v6.0.2 (2026-10-08), v6.0.1, v6.0.0 (2026-09-29) и v4.22.0 (2026-09-30). Ветка main — Rust workspace (пакет falkordb-rs).
CLAIMED VS ACTUAL: Позиционируется как 'open source', но SSPL не одобрена OSI. Мажорная линия 6.x (переписывание на Rust) вышла за две недели до аудита при параллельно живущей 4.x — зрелость 6.x под вопросом.
CAPABILITIES: Property graph на разреженных матрицах (GraphBLAS), openCypher, протокол Redis, multi-graph/multi-tenancy.
PRICING/LIMITS: FalkorDB Cloud: Free (без TLS, HA, backup; по docs 100 MB); Startup 'From $73/1GB/Month'; Pro 'From $350/8GB/Month'; Enterprise — по запросу. Цена коммерческой self-hosted лицензии не публикуется.
RISKS: SSPL — лицензионный блокер для платного SaaS без коммерческого договора; более 1,000 открытых issues; свежая мажорная версия.
HOW VERIFIED: code read (LICENSE, Cargo.toml, README); API call (gh api repos, releases); docs read (docs.falkordb.com/references/license, falkordb.com/plans).
CONFIDENCE: high
EVIDENCE: https://github.com/FalkorDB/FalkorDB/blob/main/LICENSE | https://docs.falkordb.com/references/license | https://www.falkordb.com/plans/

### [ALTERNATIVE] DuckDB 1.5.6 + DuckPGQ (SQL/PGQ community extension)
NEED: Хранилище графа и глобальная база знаний об адресах (system of record)
KIND: open-source
URL: https://github.com/cwida/duckpgq-extension
LICENSE: DuckDB — MIT; DuckPGQ — MIT
COMMERCIAL USE: Разрешено.
PROJECT STATE: DuckDB: 42,162 stars, v1.5.6 (2026-09-28). DuckPGQ: 505 stars, 36 open issues, коммиты до 2026-10-13 (порт на PEG grammar extension), GitHub Releases НЕТ; распространяется как community extension; единственный мейнтейнер на
странице расширения — Dtenwolde (CWI).
CLAIMED VS ACTUAL: README: 'DuckPGQ is a research project and a work in progress'. Документация: поддерживается только ANY SHORTEST (недетерминированный), ALL SHORTEST / k-shortest / взвешенные пути в синтаксисе путей не описаны, OPTIONAL MATCH не
поддержан. Описания функций на странице расширения пустые.
CAPABILITIES: CREATE PROPERTY GRAPH поверх обычных таблиц, GRAPH_TABLE MATCH, квантификаторы {n,m}, *, +; функции shortestpath, cheapest_path_length, pagerank, weakly_connected_component, local_clustering_coefficient, reachability. Сам DuckDB
полезен как встроенный аналитический движок по Parquet-снимкам расследований (wheels cp313 win_amd64, Node @duckdb/node-api 1.5.6).
PRICING/LIMITS: $0.
RISKS: Исследовательский статус, один мейнтейнер, нет релизов; недетерминированный ANY SHORTEST плохо сочетается с требованием воспроизводимости; DuckDB — single-writer, не подходит как основное OLTP-хранилище.
REPLACEABILITY: Высокая (работает поверх Parquet/таблиц).
HOW VERIFIED: API call (gh api repos, commits, branches, releases); code read (README DuckPGQ); docs read (duckpgq.org/documentation/sql_pgq, duckdb.org/community_extensions/extensions/duckpgq.html); PyPI/npm JSON API.
CONFIDENCE: medium
EVIDENCE: https://github.com/cwida/duckpgq-extension | https://duckpgq.org/documentation/sql_pgq/ | https://duckdb.org/community_extensions/extensions/duckpgq.html | https://github.com/duckdb/duckdb/releases

### [NEEDS-TRIAL] ArcadeDB 26.10.1
NEED: Хранилище графа и глобальная база знаний об адресах (system of record)
KIND: open-source
URL: https://github.com/ArcadeData/arcadedb
LICENSE: Apache-2.0
COMMERCIAL USE: Разрешено; README: 'Free for any usage', есть GOVERNANCE.md с обязательством оставаться open source.
PROJECT STATE: 1,201 stars, push 2026-10-13, ежемесячные релизы 26.10.1 (2026-10-05), 26.9.1, 26.8.1. Основной автор lvca (7,992 коммита), второй — robfrank (1,519).
CLAIMED VS ACTUAL: Заявлена совместимость с Neo4j Cypher и Bolt — полнота совместимости и набор графовых алгоритмов в рамках аудита не проверялись. Высокая концентрация разработки на одном человеке.
CAPABILITIES: Multi-model СУБД на Java: SQL, openCypher, Gremlin, Bolt-совместимость, Postgres wire protocol; есть embedded-пакет для Python arcadedb-embedded 26.10.1 с встроенным JRE и wheels cp313 win_amd64.
INFRA: JVM-сервер либо embedded с встроенным JRE.
PRICING/LIMITS: $0.
RISKS: Малое сообщество, bus factor; зрелость Cypher-движка и алгоритмов неизвестна.
REPLACEABILITY: Средняя.
HOW VERIFIED: API call (gh api repos, releases, contributors); code read (README); PyPI JSON API.
CONFIDENCE: low
EVIDENCE: https://github.com/ArcadeData/arcadedb | https://pypi.org/project/arcadedb-embedded/

### [REJECTED] NebulaGraph 3.8.0 (Community)
NEED: Хранилище графа и глобальная база знаний об адресах (system of record)
KIND: open-source
URL: https://github.com/vesoft-inc/nebula
LICENSE: Apache-2.0
COMMERCIAL USE: Разрешено.
PROJECT STATE: 12,426 stars, 692 open issues. Последний релиз v3.8.0 от 2024-05-17 — более двух лет без релизов; коммиты редкие (2026-09-08, 2026-09-07, 2026-05-18).
CLAIMED VS ACTUAL: Маркетинг вендора сосредоточен на NebulaGraph Enterprise v5 с нативным GQL; open-source линия 3.x фактически в режиме поддержки.
CAPABILITIES: Распределённая графовая СУБД (metad/storaged/graphd), язык nGQL.
PRICING/LIMITS: $0 (Community).
RISKS: Трёхкомпонентная распределённая архитектура избыточна для одного сервера; стагнация open-source ветки; nGQL — нестандартный язык.
HOW VERIFIED: API call (gh api repos, releases, commits); search snippet only — про Enterprise v5.
CONFIDENCE: medium
EVIDENCE: https://github.com/vesoft-inc/nebula | https://github.com/vesoft-inc/nebula/releases

### [REJECTED] JanusGraph 1.1.0
NEED: Хранилище графа и глобальная база знаний об адресах (system of record)
KIND: open-source
URL: https://github.com/JanusGraph/janusgraph
LICENSE: Apache-2.0 (код), CC-BY-4.0 (документация)
COMMERCIAL USE: Разрешено.
PROJECT STATE: 5,856 stars, 583 open issues; коммиты до 2026-10-12, но последний релиз v1.1.0 от 2024-11-09.
CLAIMED VS ACTUAL: Расхождений не найдено; проект рассчитан на распределённые кластеры, а не на один сервер.
CAPABILITIES: Gremlin/TinkerPop поверх внешнего хранилища (Cassandra/ScyllaDB/HBase/BerkeleyDB) и внешнего индекса (Elasticsearch/Solr/Lucene).
PRICING/LIMITS: $0.
RISKS: Минимум 2–3 дополнительных stateful-сервиса; JVM; Gremlin вместо Cypher/SQL; почти два года без релиза.
HOW VERIFIED: API call (gh api repos, releases, commits, contents).
CONFIDENCE: medium
EVIDENCE: https://github.com/JanusGraph/janusgraph

### [REJECTED] Dgraph v25.5.0
NEED: Хранилище графа и глобальная база знаний об адресах (system of record)
KIND: open-source
URL: https://github.com/dgraph-io/dgraph
LICENSE: Apache-2.0
COMMERCIAL USE: Разрешено.
PROJECT STATE: 21,809 stars, 105 open issues; релиз v25.5.0 (2026-10-13), v25.4.1 (2026-08-24). По поисковой выдаче: в октябре 2025 Dgraph куплен Istari Digital у Hypermode — третий владелец за несколько лет.
CLAIMED VS ACTUAL: Покрытие графовых алгоритмов в рамках аудита не проверялось. Частая смена владельцев противоречит образу стабильного проекта.
CAPABILITIES: Распределённая графовая СУБД (Zero + Alpha), языки DQL и GraphQL.
PRICING/LIMITS: $0.
RISKS: Нет Cypher/SQL; двухкомпонентный кластер; риск смены стратегии у нового владельца, чей основной бизнес — не базы данных.
HOW VERIFIED: API call (gh api repos, releases, commits); search snippet only — про владельца.
CONFIDENCE: medium
EVIDENCE: https://github.com/dgraph-io/dgraph | https://www.istaridigital.com/resources/istari-acquires-dgraph

### [REJECTED] TigerGraph (Community Edition / Savanna)
NEED: Хранилище графа и глобальная база знаний об адресах (system of record)
KIND: commercial SaaS
URL: https://www.tigergraph.com/pricing/
LICENSE: Проприетарная (license agreement обновлён 2026-03-05)
COMMERCIAL USE: Не подтверждено: условия коммерческого использования Community Edition прочитать не удалось.
PROJECT STATE: Коммерческий продукт; открыт только tigergraph/ecosys (Apache-2.0, 300 stars).
CLAIMED VS ACTUAL: Сторонний обзор приписывает Community лимит 16 CPU — на официальной странице этого нет.
CAPABILITIES: MPP-графовая СУБД с языком GSQL и библиотекой алгоритмов.
PRICING/LIMITS: Community: Free, 'Up to 300 GB Graph+Vector Storage', 'Single Server'. Savanna: $45 за GB/мес (24-7, US/Tier 1), Business Critical $126 за GB/мес; почасовые ставки от TG-00 (2 vCPU, 16 GB) $1.00/час; storage $0.025/GB/мес.
RISKS: Закрытый код, GSQL lock-in, тяжёлая установка, неясные условия коммерческого использования бесплатной редакции.
HOW VERIFIED: docs only (tigergraph.com/pricing); search snippet only — остальное.
CONFIDENCE: low
EVIDENCE: https://www.tigergraph.com/pricing/ | https://www.tigergraph.com/license-agreement/

### [REJECTED] SurrealDB 3.x
NEED: Хранилище графа и глобальная база знаний об адресах (system of record)
KIND: open-source
URL: https://github.com/surrealdb/surrealdb
LICENSE: Business Source License 1.1 (Licensed Work: SurrealDB 3.0; Change Date 2030-01-01 → Apache-2.0)
COMMERCIAL USE: Разрешено, кроме использования как 'Database Service' (когда третьи лица могут создавать и управлять схемами или таблицами). Обычный SaaS с SurrealDB как внутренним бэкендом под запрет не попадает.
PROJECT STATE: 33,128 stars, 656 open issues; релизы v3.2.5 (2026-10-06), v3.3.0 (2026-09-28), параллельно v2.7.0.
CLAIMED VS ACTUAL: Позиционируется как open source, но BSL — source-available. Покрытие графовых алгоритмов не проверялось.
CAPABILITIES: Multi-model (document/graph/vector) с собственным языком SurrealQL.
PRICING/LIMITS: Self-hosted $0. Cloud: первый инстанс бесплатно (1 GB), далее от $0.021/час; Scale $0.192/час за узел, минимум 3 узла.
RISKS: Нестандартный язык (lock-in), молодая линия 3.x, графовая аналитика не является фокусом продукта.
HOW VERIFIED: code read (LICENSE); API call (gh api repos, releases); docs only (surrealdb.com/pricing).
CONFIDENCE: medium
EVIDENCE: https://github.com/surrealdb/surrealdb/blob/main/LICENSE | https://surrealdb.com/pricing

### [REJECTED] TypeDB 3.13.6
NEED: Хранилище графа и глобальная база знаний об адресах (system of record)
KIND: open-source
URL: https://github.com/typedb/typedb
LICENSE: MPL-2.0 (сервер), драйверы Apache-2.0
COMMERCIAL USE: Разрешено.
PROJECT STATE: 4,480 stars, 316 open issues; релиз 3.13.6 (2026-09-22); коммиты до 2026-10-13.
CLAIMED VS ACTUAL: Не графовая СУБД в смысле property graph; наличие алгоритмов путей и центральностей не проверялось.
CAPABILITIES: Строго типизированная БД с языком TypeQL и логическим выводом.
PRICING/LIMITS: $0 self-hosted.
RISKS: TypeQL — отдельная парадигма с высоким порогом входа; не решает задачи k-shortest / flow / community.
HOW VERIFIED: API call (gh api repos, releases, commits).
CONFIDENCE: low
EVIDENCE: https://github.com/typedb/typedb

### [REJECTED] Amazon Neptune (Database / Serverless / Analytics)
NEED: Хранилище графа и глобальная база знаний об адресах (system of record)
KIND: commercial SaaS
URL: https://aws.amazon.com/neptune/pricing/
LICENSE: Проприетарный managed-сервис AWS
COMMERCIAL USE: Разрешено по условиям AWS.
PROJECT STATE: Действующий сервис AWS.
CLAIMED VS ACTUAL: Страница pricing не даёт полной таблицы цен: названы только db.r5.large ($0.348/час, US East) и db.r5d.2xlarge ($1.92/час, Frankfurt).
CAPABILITIES: openCypher/Gremlin/SPARQL; Neptune Analytics — in-memory движок с алгоритмами.
PRICING/LIMITS: db.r5.large $0.348/час (≈ $254/мес — мой расчёт) + storage $0.10/GB-мес + I/O $0.20 за млн запросов. Serverless: стартовая ёмкость 1 NCU. Neptune Analytics: из примера на странице 256 m-NCU = $7.68/час, то есть ≈ $0.03 за m-NCU-
час (вывод, не заявленная ставка).
RISKS: Противоречит установке 'один скромный сервер'; привязка к AWS; постоянные расходы в сотни долларов в месяц; данные расследований в стороннем облаке.
HOW VERIFIED: docs only (aws.amazon.com/neptune/pricing).
CONFIDENCE: medium
EVIDENCE: https://aws.amazon.com/neptune/pricing/

### [REJECTED] Grafeo 0.5.44
NEED: Хранилище графа и глобальная база знаний об адресах (system of record)
KIND: open-source
URL: https://github.com/GrafeoDB/grafeo
LICENSE: Apache-2.0
COMMERCIAL USE: Разрешено.
PROJECT STATE: Репозиторий создан 2026-01-26; 811 stars; релизы еженедельно (v0.5.44 от 2026-10-04, v0.6.0-beta.1 от 2026-10-11). 1,740 коммитов у одного автора (StevenBtw), следующий человек — 41.
CLAIMED VS ACTUAL: Заявлена 'high-performance' при возрасте проекта менее 9 месяцев и фактически одном разработчике; PyPI-wheels для Windows только cp312, под Python 3.13 нет.
CAPABILITIES: Embedded graph DB на чистом Rust с биндингами Python/JS/WASM.
PRICING/LIMITS: $0.
RISKS: Bus factor 1, незрелость, нет wheels под Python 3.13 на Windows.
HOW VERIFIED: API call (gh api repos, releases, contributors); PyPI JSON API.
CONFIDENCE: medium
EVIDENCE: https://github.com/GrafeoDB/grafeo | https://pypi.org/project/grafeo/

### [RECOMMENDED] NetworkX 3.7
NEED: In-process графовая аналитика (per-investigation подграфы)
KIND: open-source
URL: https://github.com/networkx/networkx
LICENSE: BSD-3-Clause
COMMERCIAL USE: Разрешено без условий.
PROJECT STATE: 17,325 stars, 319 open issues; релиз networkx-3.7 от 2026-09-21; push 2026-10-06; requires_python >=3.12 (совместим с 3.13), чистый Python (wheel py3-none-any).
CLAIMED VS ACTUAL: Ограничения, подтверждённые чтением кода: shortest_simple_paths помечен @not_implemented_for('multigraph'); flow/utils.py бросает 'MultiGraph and MultiDiGraph not supported (yet)'. Для k-shortest и flow мультиграф нужно схлопывать
в DiGraph с агрегированными суммами, сохраняя отображение на исходные TXID.
CAPABILITIES: MultiDiGraph с произвольными атрибутами рёбер (TXID, amount, timestamp, asset), all_simple_paths / all_simple_edge_paths, shortest_simple_paths (Yen), maximum_flow / min-cost flow, Louvain, Leiden (leiden.py в main), label
propagation, betweenness с k-сэмплированием, PageRank, SCC/WCC, dominators. Backends: nx-parallel 0.4, nx-cugraph, graphblas-algorithms.
INFRA: Только Python; ставится на Windows 11 / Python 3.13 без компиляции.
PRICING/LIMITS: $0.
RISKS: Чистый Python: большой расход памяти и низкая скорость на верхней границе (100k узлов и сотни тысяч–миллион рёбер); точный betweenness на 100k узлов нереалистичен. Производительность не измерялась.
REPLACEABILITY: Высокая: де-факто стандартный API; rustworkx и igraph умеют конвертировать из NetworkX.
HOW VERIFIED: code read (simple_paths.py, flow/utils.py, список community/, LICENSE.txt); API call (gh api repos, releases); PyPI JSON API.
CONFIDENCE: high
EVIDENCE: https://github.com/networkx/networkx/blob/main/networkx/algorithms/simple_paths.py | https://github.com/networkx/networkx/blob/main/networkx/algorithms/flow/utils.py | https://pypi.org/project/networkx/

### [RECOMMENDED] rustworkx 0.18.1
NEED: In-process графовая аналитика (per-investigation подграфы)
KIND: open-source
URL: https://github.com/Qiskit/rustworkx
LICENSE: Apache-2.0
COMMERCIAL USE: Разрешено.
PROJECT STATE: 1,771 stars, 146 open issues; релизы 0.18.1 (2026-07-29), 0.18.0 (2026-06-18); push 2026-10-13. Wheels abi3 cp310 для win_amd64 и manylinux (подходят для Python 3.13).
CLAIMED VS ACTUAL: Называется 'high-performance graph library', но покрытие алгоритмов уже, чем у NetworkX: поиск по коду репозитория даёт 0 совпадений для louvain, leiden, max_flow, yen. k_shortest_path_lengths возвращает только длины, не сами
пути. Flow и community detection придётся брать из NetworkX или igraph.
CAPABILITIES: PyDiGraph с поддержкой multigraph и произвольным Python-payload на рёбрах; BFS/DFS с visitor-API, dijkstra, bellman-ford, all_shortest_paths, all_simple_paths, k_shortest_path_lengths, betweenness (в том числе edge и group),
closeness, eigenvector, katz, pagerank/hits, SCC/condensation, dominance, core_number, networkx_converter, экспорт GraphML и node-link JSON.
INFRA: Готовые бинарные wheels, компилятор не нужен.
PRICING/LIMITS: $0.
RISKS: Версия 0.x, API ещё меняется; проект развивается в экосистеме Qiskit (приоритеты задаёт квантовое сообщество); нет flow/community/Yen.
REPLACEABILITY: Высокая при работе через тонкий собственный интерфейс GraphEngine.
HOW VERIFIED: code read (rustworkx/__init__.py — перечень функций; список src/); API call (gh api repos, releases, search/code); PyPI JSON API.
CONFIDENCE: high
EVIDENCE: https://github.com/Qiskit/rustworkx | https://pypi.org/project/rustworkx/

### [ALTERNATIVE] python-igraph 1.0.0 (igraph C core 1.0.1)
NEED: In-process графовая аналитика (per-investigation подграфы)
KIND: open-source
URL: https://github.com/igraph/python-igraph
LICENSE: GPL-2.0-or-later
COMMERCIAL USE: Для SaaS допустимо (код выполняется на сервере, не распространяется). При поставке продукта клиенту (on-prem, образ) приложение, импортирующее igraph, попадает под copyleft — блокер для закрытой дистрибуции.
PROJECT STATE: python-igraph: 1,464 stars, релиз 1.0.0 (2025-10-23), push 2026-10-06. C core: 2,012 stars, релиз 1.0.1 (2025-12-26). Wheels abi3 cp39 для win_amd64 (подходят для 3.13).
CLAIMED VS ACTUAL: Расхождений не найдено.
CAPABILITIES: Самое полное покрытие нужных примитивов в одном быстром C-ядре, с нативной поддержкой мультирёбер: get_k_shortest_paths, maxflow / maxflow_value, all_st_mincuts, gomory_hu_tree, dominator, community_leiden, community_multilevel
(Louvain), community_infomap, betweenness, personalized_pagerank, is_multiple / count_multiple.
PRICING/LIMITS: $0.
RISKS: GPL ограничивает будущие модели поставки; атрибуты рёбер хранятся отдельными списками (менее удобно для богатых payload); целочисленные id вершин.
REPLACEABILITY: Высокая за интерфейсом GraphEngine.
HOW VERIFIED: code read (src/_igraph/graphobject.c — имена методов); API call (gh api repos, releases); PyPI и conda API.
CONFIDENCE: high
EVIDENCE: https://github.com/igraph/python-igraph | https://pypi.org/project/igraph/

### [ALTERNATIVE] NetworKit 11.2.2
NEED: In-process графовая аналитика (per-investigation подграфы)
KIND: open-source
URL: https://github.com/networkit/networkit
LICENSE: MIT
COMMERCIAL USE: Разрешено.
PROJECT STATE: 879 stars, push 2026-10-09; PyPI 11.2.2 (2026-09-15) с wheels cp313 win_amd64.
CLAIMED VS ACTUAL: Не проверялось детально.
CAPABILITIES: Параллельная (OpenMP) аналитика больших графов: приближённые центральности, community detection — полезно именно для betweenness/PageRank/Louvain на 100k+ узлов. Конкретный список алгоритмов в рамках аудита по коду не сверялся.
PRICING/LIMITS: $0.
RISKS: Ориентирован на простые графы с числовыми весами: атрибуты TXID/timestamp и мультирёбра придётся хранить снаружи. Небольшое сообщество.
REPLACEABILITY: Высокая (используется как ускоритель отдельных метрик).
HOW VERIFIED: API call (gh api repos); PyPI и conda API. Функциональность — по общим сведениям, не по коду.
CONFIDENCE: medium
EVIDENCE: https://github.com/networkit/networkit | https://pypi.org/project/networkit/

### [REJECTED] graph-tool 3.9
NEED: In-process графовая аналитика (per-investigation подграфы)
KIND: open-source
URL: https://graph-tool.skewed.de/
LICENSE: LGPL-3.0-or-later
COMMERCIAL USE: Разрешено (LGPL допускает использование в закрытом ПО при динамическом связывании).
PROJECT STATE: conda-forge: версия 3.9, обновлено 2026-09-24; платформы linux-64, linux-aarch64, osx-64, osx-arm64. Пакет graph-tool на PyPI (2.11) — нерабочий устаревший stub.
CLAIMED VS ACTUAL: Расхождений не найдено.
CAPABILITIES: Очень быстрая C++/Boost-библиотека, сильна в статистическом выводе сообществ (stochastic block models).
INFRA: Только conda или Docker; сборка win-64 отсутствует.
PRICING/LIMITS: $0.
RISKS: Нет нативной поддержки Windows 11 (dev-машина) — только через Docker/WSL; не ставится через pip; тяжёлые зависимости.
HOW VERIFIED: API call (api.anaconda.org/package/conda-forge/graph-tool); PyPI JSON API.
CONFIDENCE: medium
EVIDENCE: https://anaconda.org/conda-forge/graph-tool | https://pypi.org/project/graph-tool/

### [REJECTED] RAPIDS cuGraph 26.10 / nx-cugraph
NEED: In-process графовая аналитика (per-investigation подграфы)
KIND: open-source
URL: https://github.com/rapidsai/cugraph
LICENSE: Apache-2.0
COMMERCIAL USE: Разрешено.
PROJECT STATE: rapidsai/cugraph: 2,246 stars, push 2026-10-13; conda 26.10.00 (2026-10-08), только linux-64 и linux-aarch64; PyPI cugraph-cu12 26.10.0 — только manylinux. rapidsai/nx-cugraph: push 2026-10-12.
CLAIMED VS ACTUAL: Расхождений не найдено. Отдельно: RAPIDS прекратил выпуск cuGraph-DGL (notice RSN 46, последний релиз 25.06).
CAPABILITIES: GPU-ускорение графовых алгоритмов, в том числе как backend NetworkX без изменения кода.
INFRA: Linux + NVIDIA GPU + CUDA.
PRICING/LIMITS: $0 за ПО; требуется NVIDIA GPU.
RISKS: Противоречит ограничению 'один скромный сервер'; не работает на Windows нативно; для графов до 100k узлов выигрыш не оправдывает сложность.
HOW VERIFIED: API call (gh api repos; api.anaconda.org; PyPI JSON API); search snippet — RSN 46.
CONFIDENCE: high
EVIDENCE: https://github.com/rapidsai/cugraph | https://docs.rapids.ai/notices/rsn0046/

### [ALTERNATIVE] Raphtory 0.18.5 (темпоральный графовый движок)
NEED: In-process графовая аналитика (per-investigation подграфы)
KIND: open-source
URL: https://github.com/Pometry/Raphtory
LICENSE: GPL-3.0
COMMERCIAL USE: Для SaaS допустимо; при распространении продукта — copyleft на приложение, импортирующее библиотеку. README упоминает платную подписку для on-disk режима.
PROJECT STATE: 647 stars, push 2026-10-13; релизы v0.18.5 и v0.18.0 (2026-06-23), v0.17.0 (2026-03-09); PyPI 0.18.5, requires_python >=3.11.
CLAIMED VS ACTUAL: README заявляет масштаб 'hundreds of millions of edges on your laptop' — не проверялось. Наличие wheels для Windows через PyPI API подтвердить не удалось.
CAPABILITIES: Единственный найденный движок, где темпоральность — первичная модель: in-memory векторизованный граф на Rust с Python API, time-travel представления, temporal motifs, GraphQL-сервер.
PRICING/LIMITS: Open-source часть $0; out-of-memory (on-disk) режим — по подписке, цена не публикуется.
RISKS: GPL-3.0 для линкуемой библиотеки; небольшое сообщество; часть функций за подпиской; специфичный API (lock-in).
REPLACEABILITY: Средняя.
HOW VERIFIED: API call (gh api repos, releases); code read (README); PyPI JSON API.
CONFIDENCE: low
EVIDENCE: https://github.com/Pometry/Raphtory | https://pypi.org/project/raphtory/

### [RECOMMENDED] graphology 0.26.0 + sigma.js 4.0.1
NEED: Графовая модель на стороне TypeScript/UI
KIND: open-source
URL: https://github.com/graphology/graphology
LICENSE: MIT (оба)
COMMERCIAL USE: Разрешено.
PROJECT STATE: graphology: 1,760 stars, push 2026-09-02 (core 0.26.0 от 2025-01-26; пакеты метрик обновляются — 'Bump metrics 2.4.2' от 2026-09-02). sigma: 12,187 stars, npm 4.0.1 от 2026-10-13. Альтернатива: cytoscape 3.34.3 (MIT, 2026-09-07).
CLAIMED VS ACTUAL: Расхождений не найдено; ядро graphology не обновлялось с января 2025 (стабильно, но малоактивно).
CAPABILITIES: Модель графа для JS/TS с типами, поддержка multi/directed графов; стандартная библиотека в монорепозитории: shortest-path, simple-path, communities-louvain, communities-leiden, components, metrics, traversal, layout-forceatlas2,
gexf/graphml. sigma.js — WebGL-рендер графов на тысячи узлов для web-отчёта.
PRICING/LIMITS: $0.
RISKS: Алгоритмы на JS не должны быть источником фактов отчёта — только визуализация и интерактив; расчёты остаются на Python-стороне, чтобы не было двух расходящихся реализаций.
REPLACEABILITY: Высокая (обмен через node-link JSON / GraphML).
HOW VERIFIED: API call (gh api repos, contents/src, commits); npm registry API.
CONFIDENCE: high
EVIDENCE: https://github.com/graphology/graphology | https://www.npmjs.com/package/graphology | https://www.npmjs.com/package/sigma

### [RECOMMENDED] PyTorch Geometric (PyG) 2.8.1
NEED: Graph ML для изолированного экспериментального контура
KIND: open-source
URL: https://github.com/pyg-team/pytorch_geometric
LICENSE: MIT
COMMERCIAL USE: Разрешено.
PROJECT STATE: 24,116 stars, 1,373 open issues; релизы 2.8.1 (2026-10-06), 2.8.0 (2026-06-05), 2.7.0 (2025-10-14); PyPI 2.8.1 (2026-10-12). README: Python 3.10–3.14; базовая установка требует только PyTorch.
CLAIMED VS ACTUAL: 'Without any external library' верно только для базовых функций: Node2Vec в коде требует 'pyg-lib>=0.6.0'. README перечисляет готовые бинарники pyg-lib/torch-scatter/torch-sparse только до PyTorch 2.12, тогда как на PyPI уже torch
2.14.1 — версию torch нужно фиксировать.
CAPABILITIES: В дереве исходников: datasets EllipticBitcoinDataset, EllipticBitcoinTemporalDataset, DGraphFin, JODIE, BitcoinOTC; модели TGN (nn/models/tgn.py), Node2Vec, MetaPath2Vec, DeepGraphInfomax; полный набор GNN-слоёв, гетерогенные
графы, neighbor sampling.
INFRA: PyTorch (есть wheels cp313 win_amd64); изолированный контейнер; GPU не обязателен.
PRICING/LIMITS: $0; обучение на CPU возможно для графов масштаба Elliptic (≈200k узлов).
RISKS: Зависимость от матрицы совместимости torch ↔ pyg-lib; модели, обученные на Bitcoin-датасетах, не переносятся на TRON без собственной разметки.
REPLACEABILITY: Средняя (формат данных PyG специфичен, сами модели — стандартный PyTorch).
HOW VERIFIED: code read (README, nn/models/node2vec.py, datasets/elliptic.py, списки datasets/ и nn/models/); API call (gh api repos, releases, commits); PyPI JSON API.
CONFIDENCE: high
EVIDENCE: https://github.com/pyg-team/pytorch_geometric | https://github.com/pyg-team/pytorch_geometric/blob/master/torch_geometric/nn/models/node2vec.py | https://pypi.org/project/torch-geometric/

### [REJECTED] DGL (Deep Graph Library) 2.4.0
NEED: Graph ML для изолированного экспериментального контура
KIND: open-source
URL: https://github.com/dmlc/dgl
LICENSE: Apache-2.0
COMMERCIAL USE: Разрешено.
PROJECT STATE: ФАКТИЧЕСКИ НЕ СОПРОВОЖДАЕТСЯ: последний коммит 2025-07-31 (предыдущий — 2025-02-11), последний GitHub-релиз v2.4.0 от 2024-09-03, на PyPI — 2.2.1 от 2024-05-13 без wheels для Python 3.13 (только cp38–cp312). 14,283 stars, 610 open
issues. Репозиторий не архивирован, официального объявления о прекращении не найдено.
CLAIMED VS ACTUAL: Сторонние агрегаторы (Snyk) показывают статус сопровождения 'sustainable', но открытые issues говорят об обратном: #7934 'Fails to build with PyTorch-2.14.0' (2026-09-13), #7932 'Arbitrary Code Execution in DGL via load_info and
Graphbolt Torch-Data Loading' (2026-08-29, открыт), #7925 'DGL Jenkins System is deprecated' (2026-06-19). RAPIDS прекратил выпуск cuGraph-DGL.
CAPABILITIES: Исторически второй по популярности GNN-фреймворк.
PRICING/LIMITS: $0.
RISKS: Нет совместимости с Python 3.13 и актуальным PyTorch; незакрытая уязвимость исполнения кода; нет CI.
HOW VERIFIED: API call (gh api repos, commits, releases, issues); PyPI и conda API; search snippet — RSN 46.
CONFIDENCE: high
EVIDENCE: https://github.com/dmlc/dgl | https://github.com/dmlc/dgl/issues/7934 | https://github.com/dmlc/dgl/issues/7932 | https://pypi.org/project/dgl/

### [ALTERNATIVE] PyTorch Geometric Temporal 0.56.2
NEED: Graph ML для изолированного экспериментального контура
KIND: open-source
URL: https://github.com/benedekrozemberczki/pytorch_geometric_temporal
LICENSE: MIT
COMMERCIAL USE: Разрешено.
PROJECT STATE: 2,992 stars, 30 open issues; PyPI 0.56.2 от 2025-07-16; последние коммиты 2026-05-30 (мелкие исправления загрузчиков датасетов).
CLAIMED VS ACTUAL: Заявлена как 'temporal extension', но ориентирована на прогноз сигналов на фиксированном графе (трафик, эпидемии), а не на событийный поток переводов (continuous-time) — для потока транзакций ближе TGN из ядра PyG.
CAPABILITIES: Рекуррентные и attention-модели для дискретных временных срезов графа и spatio-temporal сигналов.
PRICING/LIMITS: $0.
RISKS: Низкая активность; несоответствие модели данных задаче.
HOW VERIFIED: API call (gh api repos, commits); PyPI JSON API.
CONFIDENCE: medium
EVIDENCE: https://github.com/benedekrozemberczki/pytorch_geometric_temporal | https://pypi.org/project/torch-geometric-temporal/

### [ALTERNATIVE] Temporal Graph Benchmark (py-tgb 2.3.0) + TGN из PyG
NEED: Graph ML для изолированного экспериментального контура
KIND: open-source
URL: https://github.com/shenyangHuang/TGB
LICENSE: MIT
COMMERCIAL USE: Код — разрешено; лицензии входящих датасетов не проверялись.
PROJECT STATE: 265 stars, push 2026-07-27; PyPI py-tgb 2.3.0 от 2026-07-27. Референсная реализация twitter-research/tgn (Apache-2.0) не обновлялась с 2024-05-28; DyGLib (MIT) — с 2023-09-28; amazon-science/tgl — с 2023-12-25.
CLAIMED VS ACTUAL: Расхождений не найдено; оригинальные репозитории TGN, DyGLib, TGL заброшены — использовать реализацию TGN из PyG.
CAPABILITIES: Стандартизованные протоколы оценки continuous-time моделей (temporal link / node property prediction) с корректными временными разбиениями и negative sampling — готовый каркас для честного сравнения AI-слоя с baseline.
PRICING/LIMITS: $0.
RISKS: Задачи TGB (предсказание связей) не совпадают напрямую с классификацией illicit-адресов; потребуется собственный загрузчик TRON-данных.
HOW VERIFIED: API call (gh api repos для TGB, tgn, DyGLib, tgl); PyPI JSON API; code read (наличие nn/models/tgn.py в PyG).
CONFIDENCE: medium
EVIDENCE: https://github.com/shenyangHuang/TGB | https://pypi.org/project/py-tgb/ | https://github.com/twitter-research/tgn

### [NEEDS-TRIAL] TGM (tgm-lib 0.1.0b1)
NEED: Graph ML для изолированного экспериментального контура
KIND: open-source
URL: https://github.com/tgm-team/tgm
LICENSE: MIT
COMMERCIAL USE: Разрешено.
PROJECT STATE: 124 stars, push 2026-09-22; PyPI tgm-lib 0.1.0b1 от 2026-01-24 (beta).
CLAIMED VS ACTUAL: Beta-статус, функциональность не проверялась.
CAPABILITIES: Новая модульная библиотека 'Efficient and Modular ML on Temporal Graphs' — кандидат на замену заброшенным DyGLib/TGL.
PRICING/LIMITS: $0.
RISKS: Незрелость, малое сообщество, API нестабилен.
HOW VERIFIED: API call (gh api repos); PyPI JSON API.
CONFIDENCE: low
EVIDENCE: https://github.com/tgm-team/tgm | https://pypi.org/project/tgm-lib/

### [ALTERNATIVE] Реализации node2vec: PyG Node2Vec, PecanPy 2.0.9, eliorc/node2vec 0.5.0
NEED: Graph ML для изолированного экспериментального контура
KIND: open-source
URL: https://github.com/krishnanlab/PecanPy
LICENSE: PyG — MIT; PecanPy — BSD-3-Clause; eliorc/node2vec — MIT
COMMERCIAL USE: Разрешено для всех трёх.
PROJECT STATE: PecanPy: 176 stars, push 2026-10-12, PyPI 2.0.9 от 2024-01-10. eliorc/node2vec: 1,303 stars, push 2025-10-06, PyPI 0.5.0 от 2024-08-02. Малоактивные: VHRanger/nodevectors (push 2024-12-25), louisabraham/fastnode2vec (2023-06-27),
shenweichen/GraphEmbedding (2026-04-26).
CLAIMED VS ACTUAL: PyG Node2Vec требует pyg-lib>=0.6.0 (подтверждено кодом). node2vec трансдуктивен: эмбеддинги не переносятся на новые адреса без переобучения — плохо подходит для потока новых расследований.
CAPABILITIES: Структурные эмбеддинги адресов как признаки для классических классификаторов и ранжирования. Также node2vec и FastRP есть в Neo4j GDS, node2vec — в Memgraph.
PRICING/LIMITS: $0.
RISKS: Трансдуктивность; недетерминизм без фиксации seed (важно для воспроизводимости); чистые Python-реализации медленны на больших графах.
REPLACEABILITY: Высокая.
HOW VERIFIED: API call (gh api repos); PyPI JSON API; code read (PyG node2vec.py).
CONFIDENCE: medium
EVIDENCE: https://github.com/krishnanlab/PecanPy | https://github.com/eliorc/node2vec | https://github.com/pyg-team/pytorch_geometric/blob/master/torch_geometric/nn/models/node2vec.py

### [NEEDS-TRIAL] PyGOD 1.1.0 (graph outlier detection)
NEED: Graph ML для изолированного экспериментального контура
KIND: open-source
URL: https://github.com/pygod-team/pygod
LICENSE: BSD-2-Clause
COMMERCIAL USE: Разрешено.
PROJECT STATE: 1,499 stars; PyPI 1.1.0 от 2024-02-04; последний push 2024-11-14 — почти два года без активности.
CLAIMED VS ACTUAL: Совместимость с PyG 2.8 и Python 3.13 не проверялась; проект выглядит заброшенным.
CAPABILITIES: Набор unsupervised-детекторов аномалий на графах поверх PyG — потенциально полезно при отсутствии разметки по TRON.
PRICING/LIMITS: $0.
RISKS: Стагнация; возможная несовместимость с актуальными версиями.
HOW VERIFIED: API call (gh api repos); PyPI JSON API.
CONFIDENCE: low
EVIDENCE: https://github.com/pygod-team/pygod | https://pypi.org/project/pygod/

### [RECOMMENDED] Judicially Grounded Virtual Asset Address Labels and TRON TRC20-USDT Behavioral Analysis Dataset (Mendeley Data)
NEED: Эталонные датасеты и модели для illicit-flow detection
KIND: dataset
URL: https://data.mendeley.com/datasets/62dmsngtfb
LICENSE: CC BY 4.0 (указано на странице датасета)
COMMERCIAL USE: CC BY 4.0 разрешает коммерческое использование с атрибуцией. Нужно проверить оговорку в футере сайта о резервировании прав на text and data mining / AI training (относится к контенту сайта).
PROJECT STATE: Версия 3 опубликована 2026-08-03, DOI 10.17632/62dmsngtfb.3; единственный контрибьютор — Meng Ling Tsai.
CLAIMED VS ACTUAL: Страница не перечисляет категории ролей и не говорит, есть ли графовая структура. Данные деидентифицированы (нет номеров дел и URL источников) — происхождение отдельной метки независимо не проверить.
CAPABILITIES: 1,150 адресных меток с единственной ролью, основанных на судебных решениях; поведенческое подмножество из 1,024 адресов TRON TRC20-USDT; словари данных и скрипты анализа. Единственный найденный публичный размеченный датасет именно
по USDT TRC20.
PRICING/LIMITS: $0.
RISKS: Малый объём; один автор; неизвестная юрисдикция и смещение выборки; метки нельзя подтвердить первичным источником, поэтому в отчётах их использовать нельзя — только для экспериментов.
HOW VERIFIED: docs only (страница data.mendeley.com); сам датасет не скачивался.
CONFIDENCE: medium
EVIDENCE: https://data.mendeley.com/datasets/62dmsngtfb

### [ALTERNATIVE] Elliptic Data Set (Bitcoin, уровень транзакций)
NEED: Эталонные датасеты и модели для illicit-flow detection
KIND: dataset
URL: https://www.kaggle.com/datasets/ellipticco/elliptic-data-set
LICENSE: Не подтверждена (страницу Kaggle прочитать не удалось)
COMMERCIAL USE: Не подтверждено — до проверки лицензии считать 'только исследования'.
PROJECT STATE: Опубликован в 2019; зеркалируется PyG (data.pyg.org/datasets/elliptic) и доступен как EllipticBitcoinDataset / EllipticBitcoinTemporalDataset.
CLAIMED VS ACTUAL: Признаки анонимизированы, нельзя сопоставить с реальными транзакциями. UTXO-модель Bitcoin: узлы — транзакции, а не адреса — напрямую не переносится на account-модель TRON.
CAPABILITIES: 203,769 транзакций-узлов, 234,355 рёбер, 165 признаков, 49 временных шагов; 4,545 illicit (2%), 42,019 licit (21%), остальное unknown. Канонический benchmark для GCN/GAT в AML.
PRICING/LIMITS: $0.
RISKS: Доменный сдвиг (BTC ≠ TRON); неясная лицензия; данные 2019 года.
HOW VERIFIED: code read (docstring и URL в torch_geometric/datasets/elliptic.py); страница Kaggle вернула только заголовок.
CONFIDENCE: medium
EVIDENCE: https://github.com/pyg-team/pytorch_geometric/blob/master/torch_geometric/datasets/elliptic.py | https://www.kaggle.com/datasets/ellipticco/elliptic-data-set

### [NEEDS-TRIAL] Elliptic++ (Bitcoin, транзакции + кошельки)
NEED: Эталонные датасеты и модели для illicit-flow detection
KIND: dataset
URL: https://github.com/git-disl/EllipticPlusPlus
LICENSE: Лицензия НЕ указана (в репозитории нет LICENSE; GitHub API: license=null)
COMMERCIAL USE: Не разрешено по умолчанию: при отсутствии лицензии права не предоставлены. Только после письменного разрешения авторов.
PROJECT STATE: 168 stars, последний push 2023-11-25; данные лежат на Google Drive; статья KDD 2023.
CLAIMED VS ACTUAL: Широко используется в статьях как открытый датасет, но юридически лицензия отсутствует.
CAPABILITIES: Расширение Elliptic уровнем адресов: 822,942 кошелька (14,266 illicit, 251,088 licit, 557,588 unknown), 2,868,964 рёбер addr-addr, 1,314,241 рёбер addr-tx-addr, 56 признаков адреса; транзакции: 203,769 узлов и 183 признака. Ближе
всех к адресной постановке задачи LEDGERHUNT.
PRICING/LIMITS: $0.
RISKS: Нет лицензии; хостинг на Google Drive может исчезнуть; Bitcoin, не TRON.
HOW VERIFIED: API call (gh api repos); code read (README).
CONFIDENCE: high
EVIDENCE: https://github.com/git-disl/EllipticPlusPlus

### [ALTERNATIVE] Elliptic2 (Bitcoin, уровень подграфов)
NEED: Эталонные датасеты и модели для illicit-flow detection
KIND: dataset
URL: https://github.com/MITIBMxGraph/Elliptic2
LICENSE: Код репозитория — Apache-2.0; лицензия самих данных (скачиваются с elliptic.co/elliptic2) не проверена
COMMERCIAL USE: Для данных не подтверждено.
PROJECT STATE: 29 stars, последний push 2025-01-23; статья arXiv 2404.19109.
CLAIMED VS ACTUAL: Не проверялось; для запуска нужны сторонние репозитории GLASS и sub2vec.
CAPABILITIES: Разметка на уровне подграфов (форма схемы отмывания) — методически ближе всего к задаче 'классифицировать целый trace', а не отдельный узел. Baseline-модели: GLASS, GNNSeg, Sub2Vec.
PRICING/LIMITS: $0.
RISKS: Доменный сдвиг (BTC); неясная лицензия данных; малоактивный репозиторий.
HOW VERIFIED: API call (gh api repos); code read (README).
CONFIDENCE: medium
EVIDENCE: https://github.com/MITIBMxGraph/Elliptic2 | https://arxiv.org/abs/2404.19109

### [ALTERNATIVE] IBM AMLworld synthetic transactions (IBM Transactions for Anti Money Laundering) + IBM/Multi-GNN
NEED: Эталонные датасеты и модели для illicit-flow detection
KIND: dataset
URL: https://github.com/IBM/Multi-GNN
LICENSE: IBM/Multi-GNN и IBM/AMLSim — Apache-2.0; лицензия датасета на Kaggle не подтверждена
COMMERCIAL USE: Код — разрешено; данные — не подтверждено.
PROJECT STATE: IBM/Multi-GNN: 124 stars, push 2025-09-18. IBM/AMLSim: 405 stars, push 2025-09-17.
CLAIMED VS ACTUAL: Банковская (fiat) симуляция, не блокчейн; число транзакций и состав паттернов взяты только из поисковой выдачи.
CAPABILITIES: Синтетические транзакции с размеченными типологиями отмывания; по поисковой выдаче — шесть наборов (HI/LI × small/medium/large) и файлы паттернов. Подходит для тестов детектора split/merge с известным ground truth без юридических
рисков реальных меток.
PRICING/LIMITS: $0.
RISKS: Синтетика не отражает поведение TRON (энергия, hot wallets бирж, мосты); лицензия данных не проверена.
HOW VERIFIED: API call (gh api repos); search snippet only — описание датасета.
CONFIDENCE: low
EVIDENCE: https://github.com/IBM/Multi-GNN | https://github.com/IBM/AMLSim

## OPEN QUESTIONS FOR OWNER (researcher)
- Планируется ли когда-либо поставка продукта клиенту (on-prem, Docker-образы для правоохранительных органов или бирж), а не только SaaS? От этого зависит допустимость GPL-компонентов: Neo4j Community (GPLv3), python-igraph
(GPL-2.0+), pgRouting (GPL-2.0), Raphtory (GPL-3.0). При чистом SaaS они допустимы, при дистрибуции — нет.
- Должны ли многошаговые запросы по всему накопленному графу всех расследований быть продуктовой функцией уже в MVP, или достаточно поиска адресов и меток между расследованиями? Первое сдвигает выбор в сторону graph DB или Apache
AGE.
- Нужен ли аналитикам ad-hoc язык запросов (Cypher) к графу расследования? Если да, приоритет в benchmark получают LadybugDB, AGE и Neo4j.
- Каковы параметры целевого сервера (ядра CPU, RAM) и ожидаемое число одновременных расследований? Без этого нельзя оценить, помещаются ли несколько подграфов по 100k узлов в память.
- Есть ли бюджет на коммерческую лицензию graph DB (Memgraph OEM/SaaS, Neo4j Enterprise, FalkorDB commercial) на этапе платных тарифов, и готов ли владелец запросить у вендоров письменные условия и цены?
- Готов ли владелец привлечь юриста для подтверждения трактовки GPLv3 (Neo4j Community как бэкенд SaaS) и текущей редакции BSL Memgraph, прежде чем включать их в benchmark как реальных кандидатов?
- Доступен ли GPU для экспериментального ML-контура, или контур должен работать только на CPU?
- Каковы требования к изоляции данных между клиентами и к срокам хранения расследований? Это влияет на схему (row-level security, отдельные схемы или базы) и на возможность общей базы знаний об адресах.
- Допустимо ли использовать в экспериментальном контуре датасеты с неподтверждённой или отсутствующей лицензией (Elliptic, Elliptic2, Elliptic++) исключительно для внутренних исследований, или нужен только юридически чистый набор?
- Кто и из каких источников будет формировать независимый размеченный тестовый набор для проверки точности меток ≥95% и 50+ сценариев с ground truth? Публичного готового набора по USDT TRC20 такого качества не найдено.
- Согласен ли владелец с правилом решения для Этапа 2: оставаться на 'PostgreSQL + in-memory', если выделенная graph DB не даёт выигрыша не менее чем в 3 раза по p95 на обязательных запросах либо не закрывает запрос, недостижимый
базовым вариантом?

## NOT VERIFIED (researcher)
- Производительность любых кандидатов: benchmark не запускались (исполнение стороннего кода запрещено правилами аудита). Все оценки скорости и памяти — ожидания, подлежащие измерению на Этапе 2.
- Цены Neo4j Enterprise, GDS Enterprise, Memgraph Enterprise / OEM-SaaS, коммерческой лицензии FalkorDB, ArangoDB Enterprise, TigerGraph Enterprise — не публикуются (contact sales).
- Лимиты AuraDB Free (200,000 узлов / 400,000 связей, пауза через 3 дня, удаление через 30 дней) — только поисковая выдача; страница pricing конкретных чисел не содержит, а другие страницы Neo4j показывают 50k/175k.
- Полный текст ArangoDB Community License (PDF не удалось разобрать) — использованы формулировки из документации 3.12.
- Юридическая трактовка: допустимость Neo4j Community (GPLv3) как бэкенда закрытого коммерческого SaaS и охватывает ли 'internal business purposes' в текущей BSL Memgraph клиентский SaaS — требуется заключение юриста и/или
письменный ответ вендора.
- Условия лицензии бинарного дистрибутива Neo4j GDS (в отличие от OpenGDS под GPLv3) и точные лимиты GDS Community помимо 4 ядер (например, лимит model catalog).
- Условия коммерческого использования TigerGraph Community Edition и лимит 16 CPU (упомянут только сторонним обзором).
- Цены Neptune для db.t3/t4g.medium и db.r6g.large, цена NCU-часа Serverless, заявленная ставка и минимальная ёмкость Neptune Analytics (ставка ≈$0.03 за m-NCU-час выведена из примера на странице).
- Закрытость NebulaGraph Enterprise v5 и планы по open-source линии 3.x — только посты вендора 2024 года.
- Покупка Kuzu компанией Apple и покупка Dgraph компанией Istari Digital — только поисковая выдача (BetaKit, MacDailyNews, пресс-релиз), первичные документы не читались.
- Совместимость формата файлов LadybugDB с Kuzu 0.11.3; источники финансирования и модель governance LadybugDB.
- Лицензии датасетов: Elliptic Data Set на Kaggle (страница отдала только заголовок), Elliptic2 (данные на elliptic.co), IBM AMLworld на Kaggle; у Elliptic++ лицензия отсутствует. Число транзакций и состав паттернов AMLworld —
только поисковая выдача.
- Содержимое датасета Mendeley (категории ролей, наличие графовой структуры) — файл не скачивался; применимость оговорки сайта о text and data mining к самому датасету.
- Наличие wheels pyg-lib для сочетания Python 3.13 + Windows + актуальный torch (README PyG перечисляет до PyTorch 2.12).
- Наличие нативной реализации Leiden именно в релизе NetworkX 3.7 (файл leiden.py проверен в ветке main).
- Набор алгоритмов и поддержка мультирёбер в NetworKit; покрытие графовых алгоритмов в ArcadeDB, SurrealDB, TypeDB, Dgraph, JanusGraph — по коду не сверялись.
- Наличие Windows-wheels Raphtory (PyPI API не вернул список файлов) и заявление 'hundreds of millions of edges on your laptop'.
- Доступность Apache AGE и pgRouting у managed-провайдеров PostgreSQL.
- Совместимость PyGOD 1.1.0 и torch-geometric-temporal 0.56.2 с PyG 2.8.1 и Python 3.13.
- Наличие log index TRC20-событий в других источниках данных TRON (в ответе TronGrid его нет) — относится к области источников данных.
- Использование on-chain событий blacklist контракта USDT как первичного источника меток — идея не проверялась в этом аудите.
- Стоимость сервера и трудозатраты на benchmark и разметку 50+ сценариев — не оценивались по первичным данным.
- Производительность рендера sigma.js и cytoscape.js на графах 100k узлов.