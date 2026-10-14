# AREA frontend-graph-viz: Web interface and interactive graph visualisation library

============================================================
PART 1 - VERIFIER REPORT (takes precedence over the researcher wherever they disagree)
============================================================

## VERIFIER SUMMARY
Перепроверено 24 утверждения по первичным источникам (gh api, npm registry, исходники в raw.githubusercontent.com, тексты лицензий, страницы цен). Аудит фактически точен: версии, даты, лицензии, цены и счётчики совпали практически
везде; явных выдумок не найдено. Подтверждены: MIT у Cytoscape/Sigma/xyflow/G6, GPL-3.0 у cytoscape-svg, ограничение NVL продуктами Neo4j, CC-BY-NC-4.0 у Cosmograph, цены GoJS и yFiles, 41 advisory Next.js за 2026 год (3
critical), остановка разработки ядра G6 с 2026-04-16, выход Sigma 4.0.0 2026-10-08. Найденные ошибки и устаревшие места: - Ограничение WebGL-режима Cytoscape «только одна центральная подпись ребра» устарело — в коде есть
source/target-подписи; зато режим по-прежнему помечен experimental в типах, а стрелки только треугольные. - Пункт «cy.png() в WebGL не проверен» закрыт чтением кода: экспорт всегда идёт через Canvas 2D. Отсюда новый риск —
расхождение экрана и отчёта. - Доказательство медленности dagre (issue #297) — 2020 года про 0.8.x; актуальное свидетельство — PR #481 (671 узел: 2,34 с). Вывод не меняется. - Цитата мейнтейнера React Flow о пределе ~1000 узлов —
2021 года (v9). - cytoscape-elk 2.3.0 тянет elkjs ^0.9.3, а не 0.12.0. - 18,5 млн загрузок Cytoscape — транзитивные через Mermaid (18,54 млн); прямое использование ближе к 357 тыс. в неделю. - Поддержка TRON в GraphSense есть
прямо в коде, а не «косвенно». - Issue Reagraph #113 закрыт и относится к версиям 2023–2024. - В лицензии GoJS упущено ограничение «одно приложение» по умолчанию. - Node 24 уходит в Maintenance 2026-10-20, Node 26 станет LTS
2026-10-28. - Статья Zhao et al. доступна через PMC, но Cytoscape и Sigma в ней не тестировались. Все шесть рекомендаций устояли, главная — условно. Cytoscape.js остаётся разумным выбором для доказательной карты до ~1–2 тыс.
видимых элементов, но заявленный «запас по масштабу через WebGL» не подтверждён: режим экспериментальный, конфликтует с compound-узлами, а независимых замеров нет. Benchmark-spike должен стать блокирующим условием, а лимит видимых
элементов — обеспечиваться серверной агрегацией. Пропущенные кандидаты: Apache ECharts 6.1.0 (серверный SVG без браузера, Sankey), Graphviz dot как готовый layout-движок (WASM или нативно на бэкенде), Unovis Graph,
bitquery/widgets как UX-референс. Сильных новых open-source граф-библиотек 2025–2026, кроме Sigma v4 и cosmos.gl, поиск не выявил. Не проверено в этой сессии: реальная производительность любой библиотеки (сторонний код не
запускался), скорость Graphviz на наших размерах, предельные размеры canvas при полном PNG-экспорте, расход памяти headless Chromium, цены Ogma и KeyLines/ReGraph (не публикуются).

## BLOCKING RISKS
- Требование «1 000–10 000 узлов с плавным взаимодействием» ничем не доказано для рекомендованной библиотеки: единственные цифры по Cytoscape — предварительные от авторов (1200 узлов / 16000 рёбер ≈ 20 FPS на canvas, M1),
независимых бенчмарков нет, сторонний код в аудите не запускался. Без benchmark-spike до старта разработки выбор остаётся гипотезой.
- WebGL-режим Cytoscape в 3.34.3 официально experimental (index.d.ts), отсутствует в документации, рисует только треугольные стрелки и имеет открытую проблему с compound-узлами (#3376) — а compound-узлы предложены как механизм
группировки. Одновременно использовать оба способа масштабирования рискованно.
- Экран и отчёт могут расходиться: PNG-экспорт всегда идёт через Canvas 2D, экран при webgl:true — через WebGL с урезанными стилями. Для доказательного отчёта нужна одна и та же картинка — стили ограничить подмножеством,
поддерживаемым обоими рендерерами.
- Ключевые функции (раскрытие/сворачивание ветвей, агрегация параллельных рёбер, послойная раскладка, SVG-экспорт) в экосистеме Cytoscape либо не поддерживаются (expand-collapse объявлен заброшенным), либо под GPL-3.0 (cytoscape-
svg), либо сырые (pdf-export 0.0.5 с жёсткой зависимостью cytoscape 3.28.1). Это 3–4 недели собственного кода, что расходится со стратегией «свой код — только клей».
- Ни один готовый иерархический движок не укладывается в интерактивный бюджет на 1 000+ узлов: dagre — 2,34 с на 671 узел даже после оптимизации 2025 года, ELK layered — ~4 с на 406 узлов / 2301 ребро. Graphviz dot не измерен.
Раскладку нужно считать вне UI-потока и хранить в снимке расследования.
- Воспроизводимость силового вида: cytoscape-fcose по умолчанию randomize: true и не имеет seed; без сохранения позиций одинаковое расследование даст разные картинки.
- Запасной рендерер Sigma 4.0.x вышел 2026-10-08 после полной переписки, React-обёртка @react-sigma/core 5.0.6 поддерживает только sigma ^3.0.2, combo-узлов нет — в ближайшие месяцы это не готовая страховка.
- Коммерческий запасной путь дорог и непрозрачен: GoJS от $3 995 и по умолчанию на одно приложение; yFiles от $11 000 в год; KeyLines/ReGraph и Ogma цен не публикуют; NVL и Cosmograph лицензионно закрыты для нашего SaaS.
- Dev-машина на Node 23.4.0 (EOL с 2025-06-01); Nuxt 4.6.1 её не поддерживает по engines, Node 24 уходит в Maintenance 2026-10-20. Версию Node нужно зафиксировать в Docker до начала работ.
- PDF через headless-браузер добавляет на единственный скромный сервер процесс Chromium с заметным потреблением памяти; при параллельных отчётах нужна очередь и лимиты (сам расход памяти в этой сессии не измерялся).

## VERIFIER VERDICTS ON RECOMMENDATIONS

### NEED: Библиотека визуализации графа (карта движения средств)
PRIMARY: Cytoscape.js 3.34.3 (MIT), canvas по умолчанию + WebGL-режим при большом числе элементов, собственный React-адаптер
STANDS: True
ISSUE: Выбор выдерживает проверку по лицензии, активности и набору функций, но опора на WebGL как «запас по масштабу» слабее, чем подано. (1) В типах 3.34.3 режим прямо назван experimental, в документации его нет спустя 21 месяц после
preview, а основной автор занят редизайном v4 на WebGPU (ветка v4, коммиты 2026-10-12) — инвестиций в WebGL v3 ждать не стоит. (2) Два предложенных способа масштабирования конфликтуют: группировка через compound-узлы и WebGL
(issue #3376 открыт с 2025-05; документация прямо называет compound-узлы, bezier-рёбра и подписи дорогими). (3) В WebGL только треугольные стрелки, а PNG-экспорт идёт через Canvas 2D — экран и отчёт могут выглядеть по-разному. (4)
Независимого бенчмарка Cytoscape на 1–10 тыс. узлов не существует; единственные цифры — предварительные от самих авторов на M1. (5) 18,5 млн загрузок — транзитивные через Mermaid, а не показатель использования в аналитических
продуктах. Требование «10 000 узлов плавно» этим выбором НЕ доказано.
SUGGESTED CHANGE: Оставить Cytoscape основным рендерером доказательной карты, но: (а) сделать benchmark-spike (2–3 дня) блокирующим условием до начала разработки адаптера, с графами 1k/5k/10k, compound-узлами и подписями рёбер, на ноутбуке со
встроенной графикой; (б) зафиксировать жёсткий лимит одновременно видимых элементов (ориентир ~1 500 узлов / 3 000 рёбер на canvas) и обеспечивать его серверной агрегацией — тогда WebGL не нужен для приёмки; (в) не использовать в
стилях то, чего нет в WebGL (dashed, не-треугольные стрелки), чтобы экран совпадал с экспортом; (г) в тот же spike включить Sigma 4.0.x как обзорный рендерер для 10k — он единственный даёт подписи рёбер в WebGL и нативные
параллельные рёбра под MIT, но ему 6 дней.

### NEED: Layout-движок для потока слева направо и силовой раскладки
PRIMARY: Собственная послойная раскладка по глубине хопа (preset) + cytoscape-dagre 4.0.1 для малых подграфов + cytoscape-fcose 2.2.0
STANDS: True
ISSUE: Логика верна, но обоснование частично устарело и есть неточности: issue dagre #297 — 2020 года про 0.8.x (актуальное подтверждение — PR #481: 671 узел всё ещё 2,34 с после оптимизации); cytoscape-elk 2.3.0 тянет elkjs ^0.9.3, а не
0.12.0; fcose по умолчанию randomize: true и не имеет seed — силовой вид невоспроизводим без сохранения позиций; последний релиз fcose — 2023-01-17. Собственный алгоритм раскладки — это уже не «клей», и готовая альтернатива не
рассмотрена: Graphviz dot.
SUGGESTED CHANGE: До написания своего алгоритма сравнить его с Graphviz dot: нативно на бэкенде (детерминированные координаты для web/JSON/PDF, отдельный процесс под EPL-2.0 не затрагивает закрытый код) либо в Web Worker через @hpcc-js/wasm-
graphviz 1.29.2 (Apache-2.0, 467 тыс. загрузок/нед) или @viz-js/viz 3.31.0 (MIT). Для fcose задавать randomize: false и всегда сохранять позиции в снимке расследования. Если всё же нужен ELK — подключать elkjs напрямую, а не через
cytoscape-elk.

### NEED: Стек web-интерфейса
PRIMARY: Vite 8.3 + React 19.3 + TypeScript SPA, статика за nginx/Python-бэкендом, TanStack Router, Node 24 LTS
STANDS: True
ISSUE: Все версии, engines и счётчики advisories подтверждены первичными источниками (Next.js: 41 за 2026 год, 3 critical). Мелкие поправки: Node 24 уходит в Maintenance 2026-10-20, Node 26 становится Active LTS 2026-10-28; React Router
8.4.0 требует node >=22.22.0 и react >=19.2.7. Довод «в продакшене нет Node-процесса» ослабляется рекомендацией рендерить PDF headless-браузером: Chromium на сервере всё равно появится.
SUGGESTED CHANGE: Зафиксировать в Dockerfile Node 24 сейчас и запланировать переход на Node 26 LTS после 2026-10-28; предпочесть TanStack Router (node >=20.19). Headless Chromium для PDF запускать из Python (Playwright) в отдельном контейнере с
лимитом памяти и очередью, чтобы не вводить Node-сервис.

### NEED: UI-кит, загрузка данных, таблицы
PRIMARY: shadcn/ui (Tailwind 4 + Radix) + TanStack Query 5 + TanStack Table 9 + TanStack Virtual 3
STANDS: True
ISSUE: Лицензии (MIT) и версии подтверждены. Замечания не блокирующие: эталонный реестр shadcn собран на Next 16.3.8 — часть блоков/примеров придётся адаптировать под Vite; TanStack Table 9 — свежий мажор; zustand актуален 5.0.15.
SUGGESTED CHANGE: Без изменений по существу. Проверить на старте `shadcn init` для Vite-шаблона и закрепить версии в lock-файле; для таблицы TXID сразу заложить виртуализацию.

### NEED: Таймлайн и экспорт карты для PDF-отчёта
PRIMARY: Режим «ось времени» на Cytoscape (preset, x = время) + гистограмма с brush на Recharts 3; экспорт cy.png({full, scale, output:'blob-promise'})
STANDS: True
ISSUE: Риск «экспорт в WebGL-режиме не проверен» снят чтением кода (экспорт всегда через Canvas 2D), но выявлены другие: экран (WebGL) и PNG (Canvas) могут различаться; cy.png({full:true}) на большом графе создаёт canvas размером с весь
граф × scale — предельные размеры canvas в браузере в этой сессии не проверялись; cytoscape-pdf-export 0.0.5 жёстко зависит от cytoscape 3.28.1 и pdfkit ^0.12.3; векторного экспорта под разрешительной лицензией нет. Не рассмотрен
Apache ECharts, у которого есть серверный рендер SVG без браузера.
SUGGESTED CHANGE: PNG для отчёта рендерить только из свёрнутой карты с ограничением maxWidth/maxHeight и автотестом на пустое изображение. Для гистограммы времени и агрегированной диаграммы потоков в PDF рассмотреть ECharts 6.1.0 (Apache-2.0):
echarts.init(null, null, {renderer:'svg', ssr:true}) + renderToSVGString() даёт вектор на сервере без Chromium (с версии 5.3.0). cytoscape-pdf-export не подключать.

### NEED: Готовый open-source UI для исследования крипто-потоков
PRIMARY: Не переиспользовать целиком; GraphSense Dashboard и crypttrace — как UX-референсы
STANDS: True
ISSUE: Вывод подтверждён собственным поиском по GitHub (темы blockchain-forensics, запросы по TRON/USDT/fund flow): зрелых переиспользуемых компонентов нет, новые проекты 2025–2026 имеют 1–40 звёзд. Поправка: поддержка TRON в GraphSense
есть в коде (включая токены), а не «косвенно». Пропущены как референсы bitquery/widgets и TronScanner.
SUGGESTED CHANGE: Добавить в референсы bitquery/widgets (граф money flow + Sankey для TRON; legacy-стек, только как образец UX) и изучить Pathfinder GraphSense именно на TRON-данных. Код не заимствовать.

## VERIFIER FACT CHECKS

- [CONFIRMED] Cytoscape.js 3.34.3 :: Лицензия MIT; релиз v3.34.3 от 2026-09-07; 7 релизов за 2026 год; 11 237 звёзд, 28 open issues; типы TypeScript в пакете
  CORRECT VALUE: MIT (license.spdx_id), v3.34.3 опубликован 2026-09-07T15:55Z; релизы 2026 года: 3.33.2, 3.33.3, 3.33.4, 3.34.0, 3.34.1, 3.34.2, 3.34.3 = 7; 11 237 звёзд; поле types = index.d.ts. Уточнение: 28 — это issues вместе с PR, чистых
открытых issue 18.
  METHOD: API call made: gh api repos/cytoscape/cytoscape.js, /releases, search/issues; registry.npmjs.org/cytoscape/3.34.3
  EVIDENCE: https://github.com/cytoscape/cytoscape.js/releases

- [CORRECTED] Cytoscape.js 3.34.3 — WebGL-режим :: WebGL-рендерер остаётся preview: только straight/haystack/bezier, одна центральная подпись ребра, только треугольные стрелки; в документации не описан
  CORRECT VALUE: Статус подтверждён и даже жёстче: в index.d.ts версии 3.34.x опция описана как «Enables the experimental WebGL mode», в documentation/ слово webgl есть только в demos/gpu. НО ограничение «одна центральная подпись ребра» устарело:
в drawing-redraw-webgl.mjs зарегистрированы render-типы 'edge-source-label' и 'edge-target-label'. Ограничение по стрелкам актуально: в drawing-elements-webgl.mjs комментарий «Only supports drawing triangles at the moment»; issues
#3374 и #3376 (compound-узлы в WebGL) открыты с 2025-05. При zoom выше maxZoom кэша рендер автоматически возвращается на canvas.
  METHOD: code read: drawing-redraw-webgl.mjs, drawing-elements-webgl.mjs, canvas/index.mjs, index.d.ts; gh api search/code и issues
  EVIDENCE: https://raw.githubusercontent.com/cytoscape/cytoscape.js/unstable/src/extensions/renderer/canvas/webgl/drawing-redraw-webgl.mjs

- [CORRECTED] Cytoscape.js — экспорт cy.png() :: Работа cy.png() в WebGL-режиме не проверена (not_verified)
  CORRECT VALUE: Проверено по коду: bufferCanvasImage() в export-image.mjs создаёт отдельный 2D-canvas и вызывает this.drawElements(buffCxt, …) — экспорт идёт через Canvas 2D и не зависит от WebGL. Следствие, которого нет в аудите: картинка в PNG
может отличаться от экрана в WebGL-режиме (в экспорте будут не-треугольные стрелки, dashed-линии и т.п., которых WebGL не рисует).
  METHOD: code read
  EVIDENCE: https://raw.githubusercontent.com/cytoscape/cytoscape.js/unstable/src/extensions/renderer/canvas/export-image.mjs

- [CONFIRMED] Cytoscape.js — производительность :: Официальные цифры: ~1200 узлов/16000 рёбер — ~20 FPS canvas и >100 FPS WebGL; ~3200/68000 — 3 FPS canvas и 10 FPS WebGL (M1)
  CORRECT VALUE: Цифры совпадают с блогом от 2025-01-13 (Chrome, M1 MacBook Pro, авторы называют их предварительными). Независимых замеров Cytoscape не найдено: статья Zhao et al. 2025 (PMC12061801) Cytoscape и Sigma не тестировала.
  METHOD: docs only (WebFetch блога) + WebFetch PMC-версии статьи
  EVIDENCE: https://blog.js.cytoscape.org/2025/01/13/webgl-preview/

- [CORRECTED] Cytoscape.js — популярность :: 18,5 млн загрузок npm в неделю как показатель зрелости/распространённости
  CORRECT VALUE: Число верное (18 492 827 за 2026-10-05…11), но почти целиком транзитивное: mermaid 12.2.0 имеет зависимости cytoscape ^3.34.0 и cytoscape-fcose ^2.2.0 и сам скачивается 18 544 816 раз в неделю; cytoscape-fcose — 17,17 млн.
Реальный прокси прямого использования — cytoscape-dagre: 357 475 в неделю (сопоставимо с sigma 471 750).
  METHOD: API call made: api.npmjs.org/downloads, registry.npmjs.org
  EVIDENCE: https://registry.npmjs.org/mermaid/latest

- [CONFIRMED] cytoscape-svg 0.4.0 / cytoscape-pdf-export 0.0.5 :: cytoscape-svg — GPL-3.0; cytoscape-pdf-export — MIT, v0.0.5
  CORRECT VALUE: cytoscape-svg: GPL-3.0 (GitHub API) / «GNU GPLv3» (npm), релиз 2022-05-25. cytoscape-pdf-export 0.0.5 MIT. Упущено в аудите: pdf-export имеет жёсткую зависимость cytoscape: 3.28.1 (не peer) и pdfkit ^0.12.3 — в бандл попадёт
вторая, старая копия Cytoscape.
  METHOD: API call made: gh api, npm registry; чтение package.json
  EVIDENCE: https://registry.npmjs.org/cytoscape-pdf-export/latest

- [CONFIRMED] cytoscape-expand-collapse 4.1.1 :: Авторы объявили репозиторий неподдерживаемым
  CORRECT VALUE: Первая строка README: «…this repositoy is no longer being maintained»; последний push 2024-11-27, релиз 4.1.1 от 2024-08-28.
  METHOD: code read (README) + gh api
  EVIDENCE: https://raw.githubusercontent.com/iVis-at-Bilkent/cytoscape.js-expand-collapse/master/README.md

- [CORRECTED] cytoscape-dagre 4.0.1 / @dagrejs/dagre 3.1.1 :: dagre раскладывает 1000+ узлов ~3 с, участник проекта подтвердил квадратичную/кубическую сложность (issue #297); для 10 000 узлов непригоден
  CORRECT VALUE: Issue #297 — от 2020-05-07, закрыт 2020-07-30, относится к dagre 0.8.x; автор комментария gordonwoodhull имеет author_association NONE. Свежее первичное свидетельство сильнее: PR #481 (merged 2025-10-28) — граф 671 узел / 688
рёбер: 9,42 с → 2,34 с после оптимизации. Вывод аудита (секунды уже на сотнях узлов) остаётся в силе. Версии верны: @dagrejs/dagre 3.1.1 (2026-08-08), cytoscape-dagre 4.0.1 (npm 2026-08-28; dagre забандлен, runtime-зависимостей
нет, unpacked 830 КБ).
  METHOD: API call made: gh api issues/297 + comments, pulls/481; npm registry
  EVIDENCE: https://github.com/dagrejs/dagre/pull/481

- [CORRECTED] elkjs 0.12.0 / cytoscape-elk 2.3.0 :: elkjs — EPL-2.0 OR GPL-3.0-or-later; issue #372: 406 узлов / 2301 ребро ≈ 4 с, команда признаёт проблемы скорости; cytoscape-elk использует elkjs 0.12.0
  CORRECT VALUE: Лицензия и issue #372 подтверждены (soerendomroes, MEMBER: «We are well aware of the speed issues in elkjs»; WASM — PR #376, не в релизе). Ошибка в связке: cytoscape-elk 2.3.0 зависит от elkjs ^0.9.3, т.е. тянет ветку 0.9.x
(лицензия 0.9.3 — только EPL-2.0), а не 0.12.0 от 2026-07-17.
  METHOD: API call made: npm registry (cytoscape-elk, elkjs, elkjs/0.9.3), gh api issues/372 + comments; чтение LICENSE.md
  EVIDENCE: https://registry.npmjs.org/cytoscape-elk/latest

- [CONFIRMED] Sigma.js 4.0.1 + graphology 0.26.0 :: MIT; sigma@4.0.0 вышла 2026-10-08, 4.0.1 — 2026-10-13; @react-sigma/core 5.0.6 требует sigma ^3.0.2; нет combo (issue #1515 открыт)
  CORRECT VALUE: Всё совпадает: 4.0.0 — 2026-10-08, 4.0.1 — 2026-10-13, перед ними 9 бета-версий с 2026-08-09; peerDependencies @react-sigma/core 5.0.6: sigma ^3.0.2; issue #1515 open с 2025-03-12; release notes 4.0.0 подтверждают SDF-подписи
узлов и рёбер в WebGL, нативные параллельные рёбра, pathStep, layerDashed, отказ от WebGL 1.
  METHOD: API call made: gh api releases, issues/1515; npm registry
  EVIDENCE: https://github.com/jacomyal/sigma.js/releases/tag/sigma%404.0.0

- [CORRECTED] React Flow / xyflow 12.12.0 :: Мейнтейнер в issue #967: DOM-рендер, предел ~1000 узлов; RFC по виртуализации #4239 открыт без реализации
  CORRECT VALUE: Цитата moklick подлинная, но датирована 2021-03-05 и относится к React Flow v9; issue закрыт в 2021. RFC #4239 открыт с 2024-05-02, последнее содержательное обновление команды — 2024-06-27. Лицензия MIT и версия 12.12.0
(2026-09-24) подтверждены, тег next = 13.0.0-next.0 (2026-10-11). Отклонение по масштабу остаётся обоснованным, но доказательство пятилетней давности.
  METHOD: API call made: gh api issues/967 + comments, issues/4239 + comments; npm registry
  EVIDENCE: https://github.com/xyflow/xyflow/issues/967

- [CONFIRMED] AntV G6 5.1.1 :: Релиз 5.1.1 от 2026-04-17; последний коммит в packages/g6/src — 2026-04-16; issues #7534 и #7648 открыты, отвечает бот; 322 открытых issue
  CORRECT VALUE: Всё подтверждено: коммиты после 2026-04-16 — только docs/chore; в #7648 отвечает только github-actions[bot]; в #7534 один вопрос от CONTRIBUTOR и жалобы на предел 200–250 узлов. Независимое подтверждение слабости G6: статья
PMC12061801 (G6 4.8.7) — G6-Canvas держит 30 FPS лишь до 1k узлов при отношении рёбер 1 и до 300 при отношении 4.
  METHOD: API call made: gh api commits?path=packages/g6/src, issues + comments, search/issues; WebFetch PMC
  EVIDENCE: https://github.com/antvis/G6/issues/7648

- [CONFIRMED] NVL (Neo4j Visualization Library) 2.0.0 :: Лицензия разрешает использование только с Neo4j Aura или коммерческими СУБД Neo4j
  CORRECT VALUE: LICENSE.txt: «may only be used with (i) the Aura software as a service offering … or (ii) the proprietary commercial graph database products developed by Neo4j…»; npm license = SEE LICENSE IN 'LICENSE.txt'.
  METHOD: code read (текст лицензии получен curl) + npm registry
  EVIDENCE: https://unpkg.com/@neo4j-nvl/base@2.0.0/LICENSE.txt

- [CONFIRMED] cosmos.gl 3.5.1 / Cosmograph 2.5.1 :: @cosmos.gl/graph — MIT; @cosmograph/cosmograph, /react, /cosmos — CC-BY-NC-4.0; коммерческая лицензия только по запросу
  CORRECT VALUE: npm license: @cosmos.gl/graph 3.5.1 = MIT; @cosmograph/cosmograph 2.5.1, @cosmograph/react 2.5.1, @cosmograph/cosmos 3.4.1 = CC-BY-NC-4.0; страница licensing: коммерческое использование — «reach out to us for a proprietary
license», цена не указана.
  METHOD: API call made: npm registry; docs only: WebFetch страницы лицензирования
  EVIDENCE: https://cosmograph.app/licensing/

- [CORRECTED] GoJS 4.0.5 :: Individual $3 995; Team (до 3) $6 990; Group (до 20) $11 950; без runtime-отчислений; условия SaaS не раскрыты
  CORRECT VALUE: Цены и «no runtime fees or royalties» подтверждены. Упущено существенное условие: по license.html §2.1 лицензия по умолчанию ограничена ОДНИМ приложением («limited to one (1) Application», если в License Certificate не указано
больше); §2.2 запрещает передавать библиотеку третьим лицам вне Application; исходники — только при праве в сертификате. Отдельных положений про SaaS/домены в тексте нет.
  METHOD: docs only: WebFetch nwoods.com/sales; текст license.html получен curl и прочитан
  EVIDENCE: https://gojs.net/latest/license.html

- [CONFIRMED] yFiles for HTML :: В год: Single Developer €9 200 / $11 000; Project €18 400 / $22 000; Site €55 200 / $66 000; 1/2/4 домена
  CORRECT VALUE: Совпадает полностью; все тарифы срочные (годовые), бессрочных на странице нет.
  METHOD: docs only: WebFetch страницы цен
  EVIDENCE: https://www.yfiles.com/pricing

- [CONFIRMED] Next.js 16.4.0 :: 41 security advisory за 2026 год (3 critical, 14 high), включая неаутентифицированный RCE на Windows-серверах CVE-2026-75604 от 2026-08-25
  CORRECT VALUE: По годам: 2025 — 14, 2026 — 41 (critical 3, high 14, medium 21, low 3). Critical: GHSA-p293-qw3h-jr36 / CVE-2026-75604 (Windows-hosted servers, 2026-08-25), GHSA-2xp9-vwfh-vxw4 (Image Optimization API, AVIF, 2026-08-25), GHSA-
vcvr-r3jv-pc5j / CVE-2026-94545 (next/og, 2026-09-22). Vite за 2026 — 7, все про dev-сервер.
  METHOD: API call made: gh api repos/vercel/next.js/security-advisories (paginate), repos/vitejs/vite/security-advisories
  EVIDENCE: https://github.com/vercel/next.js/security/advisories

- [CORRECTED] Vite 8.3.4 + React 19.3.0, Node 24 LTS :: Vite 8.3.4 (2026-10-08), engines ^20.19.0 || >=22.12.0; React 19.3.0 (2026-09-09); Node 23 EOL 2025-06-01, на dev-машине v23.4.0; перейти на Node 24 LTS
  CORRECT VALUE: Версии, engines и EOL Node 23 подтверждены; локально node --version = v23.4.0. Уточнение по сроку: по schedule.json Node 24 переходит в Maintenance 2026-10-20 (через 6 дней), а Node 26 становится Active LTS 2026-10-28; Node 24
поддерживается до 2028-04-30. React Router 8.4.0 требует node >=22.22.0 и react >=19.2.7.
  METHOD: API call made: npm registry, raw schedule.json; локальная команда node --version
  EVIDENCE: https://raw.githubusercontent.com/nodejs/Release/main/schedule.json

- [CONFIRMED] shadcn/ui + TanStack Query/Table/Virtual + Recharts :: Всё MIT; shadcn CLI 4.21.4; в реестре v4 recharts 3.8.0, @tanstack/react-table ^9, tailwindcss ^4.3, radix-ui ^1.4.3, @base-ui/react 1.6.0; Table 9.3.1 — latest
  CORRECT VALUE: shadcn 4.21.4 (2026-10-07), tailwindcss 4.3.3, @tanstack/react-query 5.104.2, react-table 9.3.1, react-virtual 3.14.19, recharts 3.10.1 (2026-07-25) — все MIT; apps/v4/package.json: recharts 3.8.0, @tanstack/react-table ^9.0.0,
radix-ui ^1.4.3, @base-ui/react 1.6.0. Нюанс: эталонное приложение реестра построено на next 16.3.8 / react 19.2.3 — для Vite нужен отдельный init.
  METHOD: API call made: npm registry; code read package.json
  EVIDENCE: https://raw.githubusercontent.com/shadcn-ui/ui/main/apps/v4/package.json

- [CORRECTED] GraphSense Dashboard v26.09.0 :: MIT, Elm; поддержка TRON подтверждена только косвенно (ключ trx в примерах CLI)
  CORRECT VALUE: Поддержка TRON видна прямо в коде: в graphsense-dashboard поиск по 'tron' даёт 12 файлов (src/View/CurrencyMeta.elm, src/Util/Data.elm, src/View/Pathfinder/TxDetails.elm и др.); в graphsense-lib есть
spark/src/main/scala/org/graphsense/account/trx/{Tokens,Transformation,Job}.scala и transformation/account_trx.py (172 совпадения по 'trx'). Лицензия MIT, релиз v26.09.0 от 2026-09-30, язык Elm (7,8 МБ) подтверждены. Отклонение
из-за инфраструктуры остаётся верным.
  METHOD: API call made: gh api search/code, repos, releases, languages
  EVIDENCE: https://github.com/graphsense/graphsense-lib/tree/master/spark/src/main/scala/org/graphsense/account/trx

- [CORRECTED] Reagraph 4.32.0 :: Issue #113: 400 узлов — 12–28 FPS, 2600 узлов — зависание и 1–3 FPS; жалобы в 2024 году
  CORRECT VALUE: Issue #113 закрыт, открыт 2023-07-26; жалобы относятся к версиям 4.10–4.17 (2023–2024: «1000+ nodes is very slow», «~2000 … struggling»), в 2024-09 упомянуты PR с мемоизацией. Замеров для 4.32.0 (2026-06-25) нет. Лицензия
Apache-2.0 и версия подтверждены.
  METHOD: API call made: gh api issues/113 + comments; npm registry
  EVIDENCE: https://github.com/reaviz/reagraph/issues/113

- [CONFIRMED] React Flow Pro / Graphistry / Cambridge Intelligence / Ogma :: React Flow Pro $169 и $289 в месяц; Graphistry Hub $83/мес, self-hosted $1,47/час + GPU, Team $10/час; KeyLines/ReGraph и Ogma — цены только по запросу, trial 21 день, подписка 1–3 года; Ogma 6.1.0
  CORRECT VALUE: Все цифры совпадают со страницами на 2026-10-14. Graphistry: годовая оплата со скидкой 16%. Cambridge Intelligence: «Licensing is based on the expected scale of end user distribution». Ogma: в документации версия 6.1.0, цен нет.
  METHOD: docs only: WebFetch reactflow.dev/pro, graphistry.com/get-started, cambridge-intelligence.com/pricing, doc.linkurious.com/ogma/latest
  EVIDENCE: https://cambridge-intelligence.com/pricing/

- [CORRECTED] Статья «Graph visualization efficiency of popular web-based libraries» (2025) :: Текст не получен (not_verified)
  CORRECT VALUE: Доступна через PMC (PMC12061801). Тестировались D3 5.16.0 (SVG/Canvas/WebGL через NetV.js 1.1.11), ECharts 5.4.2, G6 4.8.7 на i7-12700 + RTX 3060, Chrome 106. Порог 30 FPS при отношении рёбер/узлов 1: D3-WebGL 7k, D3-Canvas 5k,
ECharts-Canvas 3k, D3-SVG 2k, G6-Canvas 1k, G6-SVG 600; при отношении 3: D3-Canvas 5k, ECharts-Canvas 2k, G6-Canvas 600. Cytoscape, Sigma, vis-network в статье НЕТ — для рекомендованной библиотеки независимого бенчмарка по-
прежнему не существует.
  METHOD: docs only: WebFetch PMC-версии (Springer уводит на авторизацию)
  EVIDENCE: https://pmc.ncbi.nlm.nih.gov/articles/PMC12061801/

- [CONFIRMED] vis-network 10.1.2 / crypttrace v0.16.0 :: vis-network: Apache-2.0 OR MIT, v10.1.2 от 2026-08-19, режим сопровождения; crypttrace: MIT, создан 2026-07-21, v0.16.0 от 2026-10-12, использует vis-network 9.1.9 с уровнями по хопам
  CORRECT VALUE: vis-network: npm license «(Apache-2.0 OR MIT)», v10.1.2 2026-08-19, содержательные коммиты в lib/ редкие (2026-08-07 TS6, 2026-05-15 physics). crypttrace: 20 звёзд, MIT, v0.16.0 2026-10-12; index.html грузит cdnjs …/vis-
network/9.1.9/…, hierarchical:{enabled:true}, level:n.level.
  METHOD: API call made: gh api, npm registry; code read index.html (grep)
  EVIDENCE: https://raw.githubusercontent.com/bobslayerX/crypttrace/main/src/crypttrace/web/index.html

## CANDIDATES MISSED BY THE RESEARCHER (found by verifier)

- Apache ECharts 6.1.0 (series graph + sankey, SSR в SVG) (https://github.com/apache/echarts)
  WHY: Apache-2.0, 67 500 звёзд, релиз 6.1.0 от 2026-05-19, 6,39 млн загрузок/нед. Graph-серия: layout none/circular/force, edgeLabel, edgeSymbol (стрелки), categories, autoCurveness для параллельных рёбер, draggable (проверено по
echarts-doc). Единственный кандидат с «zero-dependency» серверным рендером в SVG-строку (ssr: true + renderToSVGString, с 5.3.0) — закрывает векторный экспорт для PDF без headless-браузера. Sankey-серия даёт агрегированный вид
потоков.
  ASSESSMENT: Как основной граф не подходит: нет иерархического layout и combo, Sankey допускает только DAG (в документации прямо: циклов быть не должно). По независимой статье ECharts-Canvas держит 30 FPS до 2–3 тыс. узлов. Сильный кандидат на
роль таймлайна/гистограммы и векторных диаграмм отчёта вместо Recharts + headless Chromium — стоит сравнить в spike.

- Graphviz dot как layout-движок: @hpcc-js/wasm-graphviz 1.29.2, @viz-js/viz 3.31.0 или нативный dot на бэкенде (https://github.com/hpcc-systems/hpcc-js-wasm)
  WHY: Готовая послойная LR-раскладка вместо собственного алгоритма. Обёртки: @hpcc-js/wasm-graphviz — Apache-2.0, 2026-09-29, 467 тыс. загрузок/нед; @viz-js/viz — MIT, 2026-09-28, 237 тыс./нед. Сам Graphviz — EPL-2.0 (проверен LICENSE
на GitLab, проект активен 2026-10-13). На бэкенде даёт детерминированные координаты для web, JSON и PDF.
  ASSESSMENT: В аудите упомянут только как «глубоко не аудировался». Скорость на 1 000–10 000 узлов в этой сессии не измерялась (сторонний код не запускался) — нужен замер рядом с dagre и своим алгоритмом. EPL-2.0 для WASM-бандла требует той же
юридической оценки, что и elkjs; нативный вызов отдельным процессом этой проблемы не создаёт.

- Unovis Graph (@unovis/ts 1.7.1, F5) (https://github.com/f5/unovis)
  WHY: Apache-2.0, 2 856 звёзд, релиз 2026-09-29, 269 тыс. загрузок/нед. По исходникам: layout Dagre, Elk, Force, Parallel, ParallelHorizontal, Concentric, Circular, Precalculated; linkLabel, linkFlow (анимация потока), панели-группы;
обёртки для React/Svelte/Vue/Angular.
  ASSESSMENT: Готовый компонент «граф с подписями рёбер и LR-раскладкой» с минимумом кода. Рендер, насколько известно, SVG (в этой сессии не перепроверялось) — для тысяч узлов не годится. Запасной вариант для малой карты отчёта, не для
основного вида.

- bitquery/widgets 1.3.25 (https://github.com/bitquery/widgets)
  WHY: Открытые виджеты блокчейн-обозревателя Bitquery, включая граф money flow и Sankey, заявлена поддержка TRON. 133 звезды, последний коммит 2026-06-11.
  ASSESSMENT: Отклонить как зависимость: vis 4.21.0-EOL, Vue 2.7, React 16, jQuery; привязан к GraphQL API Bitquery; LICENSE в репозитории MIT, а в package.json указано ISC. Полезен только как UX-референс.

- Sankey-представление потоков (d3-sankey 0.12.3 / ECharts sankey) (https://github.com/d3/d3-sankey)
  WHY: Для «сколько ушло на какую биржу» ширина потока нагляднее графа; аудит такой вид не рассматривал вовсе. d3-sankey — BSD-3-Clause, 19,7 млн загрузок/нед.
  ASSESSMENT: d3-sankey не обновлялся с 2019-09-02 и, как и ECharts sankey, рассчитан на ациклические графы — циклы в движении средств придётся разрывать на бэкенде. Дополнительный вид для отчёта, не замена карты.

- AntV X6 3.1.8 / JointJS / maxGraph (https://github.com/antvis/X6)
  WHY: Живые диаграммные библиотеки с группами и портами: X6 — MIT, 6 726 звёзд, релиз 2026-08-11; JointJS — MPL-2.0, 5 390 звёзд; maxGraph — Apache-2.0, 1 148 звёзд (все с push 2026-10-13).
  ASSESSMENT: Класс «редактор диаграмм» на SVG/HTML, тот же потолок масштаба, что у React Flow; в аудите оставлены без оценки. Отклонить для основной карты; глубже не проверялись.

- @infinit-canvas/react 0.1.31 и @deck.gl-community/graph-layers 9.4.2 (https://github.com/visgl/deck.gl-community)
  WHY: Новички 2025–2026: совместимый с React Flow рендерер на OffscreenCanvas + Web Worker (MIT, создан 2026-03-23) и WebGL-слои графа для deck.gl (MIT, 2026-10-05).
  ASSESSMENT: Несерьёзны по зрелости: 5 и 64 загрузки в неделю соответственно, README graph-layers содержит «TBD». Упомянуты, чтобы закрыть вопрос о пропущенных новинках: сильных новых open-source граф-библиотек 2025–2026, кроме Sigma v4 и
cosmos.gl, поиск не выявил.

============================================================
PART 2 - RESEARCHER AUDIT
============================================================

## RESEARCHER RECOMMENDATIONS

### R1. NEED: Библиотека визуализации графа (карта движения средств)
PRIMARY: Cytoscape.js 3.34.3 (MIT): canvas по умолчанию, WebGL-режим при большом числе видимых элементов; собственный тонкий React-адаптер вместо react-cytoscapejs
RATIONALE: Единственный кандидат, который одновременно: (а) под MIT и активно выпускается (7 релизов в 2026), (б) нативно поддерживает направленный мультиграф с подписями рёбер и compound-узлы для группировки, (в) имеет и иерархические
(dagre/ELK), и силовые (fcose) layout, (г) умеет экспорт PNG в ядре, (д) даёт запас по масштабу через WebGL-режим. Ближайшие по функциям G6 v5 и Reagraph имеют документированные провалы производительности в диапазоне 200–2600
узлов, React Flow ограничен ~1000 узлов по словам мейнтейнера, Sigma v4 вышла 6 дней назад и не имеет комбо и иерархии.
ARCHITECTURE NOTES: Бэкенд отдаёт уже агрегированный граф: параллельные переводы между парой адресов свёрнуты в одно ребро-пучок (count, сумма, диапазон времени, список TXID), раскрытие по клику. Стартовый вид — свёрнутый: топ-N получателей на хоп по
сумме плюс мета-узел «ещё N»; раскрытие ветви — отдельный запрос. Кластеры и сервисы — compound-узлы. Автопереключение webgl:true при >~2 000 видимых элементов; LOD через min-zoomed-font-size, подписи рёбер только при приближении
или наведении. Бейджи меток и confidence — SVG data URI в background-image плюс стиль рамки. Фильтры по сумме/времени и подсветка маршрута — классы и селекторы внутри cy.batch().
COST: Лицензии $0. Переменная стоимость на расследование от визуализации — $0 (всё в браузере). Трудозатраты: адаптер + стили + взаимодействия ~2–3 недели одного разработчика; benchmark-spike 2–3 дня.
DATA QUALITY VERIFICATION: 1) Автотест круговой сверки: cy.json() после загрузки сравнивается с JSON API — каждое ребро обязано иметь непустой TXID, сумму и время, совпадающие с бэкендом (100% фактов с TXID). 2) Benchmark-стенд на Playwright с
синтетическими графами 1 000 / 5 000 / 10 000 узлов (рёбер в 1,5–3 раза больше): время до первого кадра, FPS при pan/zoom, время layout; пороги приёмки, например ≥30 FPS на 1 000 узлов с подписями и ≥15 FPS на 10 000 в WebGL-
режиме с LOD, на ноутбуке со встроенной графикой. 3) Скриншотные регрессионные тесты на эталонных сценариях из набора 50+ кейсов. 4) Проверка, что неизвестные адреса не получают биржевой бейдж: стиль бейджа строится только из поля
label.source + confidence.
RISKS: WebGL-режим остаётся preview с ограничениями стилей рёбер; на 10 тыс. видимых узлов возможна деградация — смягчается агрегацией и раскрытием по требованию; часть расширений заброшена; v4 в будущем сломает API.
REPLACEABILITY: Изолировать библиотеку за интерфейсом GraphView (load, applyFilter, highlightPath, expand, export) и хранить нейтральную модель графа (типы из OpenAPI). Тогда переход на Sigma v4 или коммерческий SDK затронет один модуль.
REJECTED ALTERNATIVES:
  - Sigma.js 4.0.1 + graphology: Лучший сырой WebGL, но мажор от 2026-10-08, нет compound/combo (issue #1515), нет LR-layout, React-обёртка ещё на v3. Оставить как запасной рендерер обзорного режима и проверить в spike.
  - AntV G6 5.1.1: Открытые issue #7534 (зависание на 2000 узлов) и #7648 (падение официального примера), 6 месяцев без коммитов в ядро, поддержка через AI-бота.
  - React Flow 12.12.0: DOM-рендер, предел ~1000 узлов (issue #967), виртуализация не реализована (#4239).
  - vis-network 10.1.2: Рабочий вариант для малого графа, но режим сопровождения, нет WebGL и compound-узлов, старые баги иерархического layout.
  - Reagraph / force-graph / cosmos.gl / D3: Соответственно: слабая производительность на 2000+ узлов; подписи рёбер и DAG-режим требуют ручного кода; нет подписей и иерархии; слишком низкий уровень.
  - NVL (Neo4j): Лицензия разрешает использование только с Neo4j Aura или коммерческими продуктами Neo4j.
  - Ogma, KeyLines/ReGraph, yFiles, GoJS, Graphistry: Цены по запросу либо $3 995–$66 000, lock-in; Graphistry требует GPU-сервер. Вернуться к GoJS/KeyLines, если spike покажет, что OSS не тянет 10 тыс. узлов.

### R2. NEED: Layout-движок для потока слева направо и силовой раскладки
PRIMARY: Собственная детерминированная послойная раскладка по глубине хопа (координаты считает бэкенд или Web Worker, Cytoscape layout 'preset') + cytoscape-dagre 4.0.1 для малых подграфов + cytoscape-fcose 2.2.0 для силового режима
RATIONALE: Общие Sugiyama-движки не укладываются в бюджет интерактива: dagre ~3 с на 1000+ узлов (issue #297), ELK layered ~4 с на 406 узлов / 2301 ребро (issue #372, подтверждено командой ELK). В трассировке слой узла естественно равен
номеру хопа от источника, поэтому расчёт линейный: слой = глубина BFS, порядок в слое — по сумме/барицентру. Это ещё и воспроизводимо (одинаковая картинка в web и PDF). dagre оставляем для аккуратной раскладки видимого подграфа до
~300 узлов, fcose — для силового вида с compound-узлами.
ARCHITECTURE NOTES: Позиции хранить вместе со снимком расследования, чтобы web, JSON и PDF показывали идентичную карту. Все тяжёлые layout — только в Web Worker с таймаутом и отменой.
COST: $0 лицензий; ~1 неделя на собственную послойную раскладку и воркер.
DATA QUALITY VERIFICATION: Property-тесты раскладки: детерминизм (одинаковый вход → одинаковые координаты), отсутствие наложений узлов, монотонность x по номеру хопа, корректная обработка циклов (обратные рёбра помечаются, а не ломают слои). Замер времени
на 1 000 / 10 000 узлов в CI.
RISKS: Простая послойная раскладка даёт больше пересечений рёбер, чем ELK; на широких веерах (fan-out в сотни адресов) слой нужно сворачивать в мета-узлы.
REPLACEABILITY: Высокая: раскладка — чистая функция (граф → координаты), рендерер получает готовые позиции.
REJECTED ALTERNATIVES:
  - elkjs 0.12.0 как основной: Медленный на наших размерах, бандл в несколько МБ, лицензия EPL-2.0 требует юридической оценки; оставить опцией «красивой» раскладки для малых графов в отчёте.
  - cytoscape-cola 2.5.1: Последний релиз 2022-02; fcose быстрее и поддерживает compound и ограничения.
  - cytoscape-expand-collapse 4.1.1: Авторы объявили репозиторий неподдерживаемым; сворачивание делать в своей модели.

### R3. NEED: Стек web-интерфейса
PRIMARY: Vite 8.3 + React 19.3 + TypeScript SPA, статическая сборка за nginx или Python-бэкендом; маршрутизация TanStack Router (или React Router 8); Node 24 LTS для сборки
RATIONALE: Продукт — закрытый кабинет расследований с клиентским canvas/WebGL-графом: SSR и SEO не нужны, а серверный Node-процесс лишь добавляет поверхность атаки. У Next.js за 2026 год 41 advisory, включая три критических RCE (в том числе
на Windows-серверах); у Vite — 7, и все про dev-сервер. Статическая сборка проще в эксплуатации на одном сервере и для маленькой команды.
ARCHITECTURE NOTES: Типы и клиент API генерировать из OpenAPI-схемы бэкенда (openapi-typescript или hey-api). Долгие расследования — опрос статуса или SSE через TanStack Query. Dev-сервер Vite слушает только localhost.
COST: $0 лицензий; хостинг — статика на уже имеющемся сервере.
DATA QUALITY VERIFICATION: CI: tsc --noEmit, линтер, unit-тесты (Vitest), e2e (Playwright) на ключевых сценариях; npm audit и Dependabot/Renovate; проверка, что в бандл и логи не попадают ключи API (ключи живут только на бэкенде).
RISKS: Node 23.4.0 на dev-машине снят с поддержки 2025-06-01 — перейти на Node 24 LTS (зафиксировать в Dockerfile и .nvmrc). Маркетинговому сайту с SEO понадобится отдельное решение.
REPLACEABILITY: Высокая: компоненты React переносимы в Next.js/Remix без переписывания логики.
REJECTED ALTERNATIVES:
  - Next.js 16.4: Избыточные серверные возможности, дублирующие Python-бэкенд; высокая частота критических уязвимостей при self-hosting.
  - SvelteKit 3.0.1: Мажор недельной давности, более узкая экосистема компонентов и обёрток граф-библиотек, 16 advisories за 2026.
  - Nuxt 4.6.1: Vue-экосистема беднее по граф-обёрткам; engines исключает Node 23 на dev-машине.

### R4. NEED: UI-кит, загрузка данных, таблицы
PRIMARY: shadcn/ui (Tailwind 4 + Radix) + TanStack Query 5 + TanStack Table 9 + TanStack Virtual 3
RATIONALE: Всё под MIT, без runtime-зависимости от поставщика кита; реестр shadcn уже включает таблицы на TanStack Table 9, графики на Recharts 3, палитру команд для поиска узлов и resizable-панели для раскладки «граф + детали + таймлайн».
TanStack Query закрывает кэш, отмену и опрос долгих задач; Virtual — списки из тысяч транзакций.
ARCHITECTURE NOTES: Состояние графа (выделение, фильтры, раскрытые ветви) держать в отдельном сторе (zustand 5), серверные данные — только в TanStack Query.
COST: $0
DATA QUALITY VERIFICATION: Storybook или визуальные тесты ключевых компонентов; проверка доступности (axe); тест, что таблица транзакций показывает ровно те TXID, что пришли из API, с ссылкой на обозреватель.
RISKS: Скопированные компоненты shadcn сопровождаются своими силами; Table v9 — свежий мажор.
REPLACEABILITY: Высокая.
REJECTED ALTERNATIVES:
  - Mantine 9.7.2: Хорошая альтернатива для быстрого старта без дизайнера; отклонена как основная из-за своей системы стилей и зависимости от одного автора.
  - Ant Design 6 / MUI 9: Тяжёлые бандлы, навязанный визуальный стиль; продвинутые гриды MUI X платные.
  - AG Grid Community 36.2.0: Избыточен для MVP; рассмотреть, если потребуются сводные таблицы и экспорт (часть функций — в платной Enterprise).

### R5. NEED: Таймлайн и экспорт карты для PDF-отчёта
PRIMARY: Режим «ось времени» на том же Cytoscape (preset-позиции, x = время) + гистограмма с brush на Recharts 3; экспорт через встроенный cy.png({full, scale, output:'blob-promise'})
RATIONALE: Не вводит вторую граф-библиотеку: узлы, подписи и TXID остаются теми же объектами, фильтр по времени управляет тем же графом. PNG высокого разрешения из ядра достаточно для PDF и не несёт лицензионных рисков.
ARCHITECTURE NOTES: Для воспроизводимости PDF рендерить ту же страницу отчёта headless-браузером на сервере из сохранённого снимка графа с зафиксированными позициями. SVG при необходимости — собственный сериализатор из позиций (узлы и рёбра
геометрически простые).
COST: $0 лицензий; ~1 неделя на режим оси времени и связку brush ↔ фильтр.
DATA QUALITY VERIFICATION: Сравнение экспортированного изображения с эталоном (pixel-diff) на тестовых сценариях; проверка, что число узлов и рёбер в экспорте равно числу в JSON-отчёте; проверка читаемости подписей при печатном разрешении.
RISKS: Большие графы в PNG тяжёлые и плохо читаются на странице — в PDF давать свёрнутую карту плюс таблицу TXID; экспорт в WebGL-режиме не проверен (при экспорте можно временно переключаться на canvas).
REPLACEABILITY: Высокая: экспорт скрыт за методом адаптера.
REJECTED ALTERNATIVES:
  - vis-timeline 8.5.4: Режим сопровождения, зависимости moment/hammerjs, не React-нативный; оставить запасным готовым виджетом.
  - KronoGraph (Cambridge Intelligence): Коммерческий, цена только по запросу.
  - cytoscape-svg 0.4.0: GPL-3.0 — несовместимо с закрытым коммерческим фронтендом.
  - cytoscape-pdf-export 0.0.5: Версия 0.0.x, 166 загрузок в неделю; проверить отдельно, если понадобится векторный PDF.

### R6. NEED: Готовый open-source UI для исследования крипто-потоков
PRIMARY: Не переиспользовать целиком: строить UI из компонентов выше; GraphSense Dashboard и crypttrace использовать как UX-референсы
RATIONALE: Единственный зрелый открытый интерфейс расследований (GraphSense Dashboard, MIT) написан на Elm и неработоспособен без Cassandra-бэкенда; остальные проекты либо заброшены, либо под AGPL/без лицензии, либо созданы одним автором
несколько месяцев назад.
COST: $0
DATA QUALITY VERIFICATION: Не применимо (код не заимствуется); при заимствовании UX-идей — проверка на собственных 50+ сценариях.
RISKS: Больше собственной работы над UX расследований; риск изобрести худший интерфейс — снизить изучением Pathfinder GraphSense.
REPLACEABILITY: Не применимо.
REJECTED ALTERNATIVES:
  - GraphSense Dashboard: Elm + обязательный graphsense-lib API на Cassandra и PostgreSQL.
  - crypttrace: 3 месяца, один автор, монолитный HTML; полезен как пример LR-раскладки по хопам на vis-network и как образец честного раздела ограничений.
  - tronscan-frontend / motif.gl / mempool / openchain viewer: Заброшены (2022–2023) либо лицензии LGPL/AGPL/отсутствует.

## LIVE PROBE FINDINGS
- gh api repos/* по 60+ репозиториям: лицензии, даты, звёзды, issues, релизы, CI — все цифры в отчёте сняты 2026-10-14.
- npm registry (registry.npmjs.org + api.npmjs.org/downloads): версии, лицензии, engines, peerDependencies и недельные загрузки для ~85 пакетов.
- Прочитан LICENSE.txt пакета @neo4j-nvl/base@2.0.0 через unpkg: использование NVL ограничено Neo4j Aura и коммерческими продуктами Neo4j.
- npm-поле license: cytoscape-svg = GPLv3 (подтверждено файлом LICENSE в репозитории kinimesi/cytoscape-svg); @cosmograph/cosmograph, @cosmograph/react и @cosmograph/cosmos = CC-BY-NC-4.0; @cosmos.gl/graph = MIT; elkjs = EPL-2.0 OR
GPL-3.0-or-later.
- sigma@4.0.0 опубликована 2026-10-08, 4.0.1 — 2026-10-13; @react-sigma/core 5.0.6 имеет peer sigma ^3.0.2 (v4 не поддержана).
- G6: последний коммит в packages/g6/src — 2026-04-16; issues #7534 (2000 узлов зависают в v5) и #7648 (официальный пример на 60 000 узлов падает) открыты, отвечает только бот.
- Cytoscape: каталог src/extensions/renderer/canvas/webgl существует и правился в 2026 году (последний коммит 2026-08-03), но в documentation/md и docmaker.json слово webgl отсутствует; issue #3486 описывает редизайн v4.
- README cytoscape.js-expand-collapse начинается с уведомления, что репозиторий больше не поддерживается.
- xyflow issue #967: мейнтейнер moklick — DOM-рендер, предел около 1000 узлов; RFC #4239 по виртуализации открыт с 2024-05.
- elkjs issue #372: 406 узлов / 2301 ребро ≈ 4 с в ELK layered, команда признаёт проблемы скорости; dagre issue #297: 1000+ узлов ≈ 3 с.
- Reagraph issue #113: 2600+ узлов — зависание 40 с и 1–3 FPS (версия 4.10.4); жалобы повторялись в 2024.
- Security advisories через gh api: Next.js — 41 за 2026 год (3 critical, 14 high), Vite — 7, SvelteKit — 16, React Router — 19.
- nodejs/Release schedule.json: Node 23 EOL 2025-06-01; локально установлен Node v23.4.0, npm 11.5.2, Docker 29.7.2. Nuxt 4.6.1 engines не включает Node 23.
- crypttrace: src/crypttrace/web/index.html подключает vis-network 9.1.9 с cdnjs и задаёт level узла по номеру хопа.
- Страницы цен: GoJS $3 995 / $6 990 / $11 950; yFiles $11 000 / $22 000 / $66 000 в год; React Flow Pro $169 и $289 в месяц; Graphistry Hub $83/мес, self-hosted $1,47/час + GPU; KeyLines/ReGraph, Ogma, Cosmograph Business — только
по запросу.

## CANDIDATES (full audit cards)

### [RECOMMENDED] Cytoscape.js 3.34.3 (+ cytoscape-dagre 4.0.1, cytoscape-fcose 2.2.0, cytoscape-elk 2.3.0, cytoscape-cola 2.5.1)
NEED: Библиотека визуализации графа (карта движения средств)
KIND: open-source
URL: https://github.com/cytoscape/cytoscape.js
LICENSE: MIT (ядро и перечисленные layout-расширения); elkjs внутри cytoscape-elk — EPL-2.0 OR GPL-3.0-or-later
COMMERCIAL USE: Да, без условий (MIT). Для cytoscape-elk учитывать EPL-2.0 у elkjs (слабый copyleft на уровне файлов).
PROJECT STATE: 11 237 звёзд, 28 open issues, не archived; релиз v3.34.3 от 2026-09-07, 7 релизов за 2026 год; 6 CI workflows; 18,5 млн загрузок npm/нед; типы TypeScript в пакете (index.d.ts). Ведётся ветка v4 (issue #3486 от 2026-07-13, GPU-
native редизайн, без обязательств по срокам). Расширения: cytoscape-dagre 4.0.1 (2026-08-28, живое), fcose 2.2.0 (последний релиз 2023-01-17, 17 млн загрузок/нед, стабильное), cola 2.5.1 (релиз 2022), elk 2.3.0 (2024-11).
CLAIMED VS ACTUAL: 1) WebGL-рендерер в основной документации (init.md, performance.md) не описан вообще — он остаётся preview: по блогу поддерживаются только straight/haystack/bezier рёбра, одна центральная подпись ребра, только треугольные стрелки,
нет dashed; issue #3374 (стрелки) и #3376 (compound в WebGL) открыты. 2) Официальные цифры скромные: ~1200 узлов/16000 рёбер — ~20 FPS на canvas и >100 FPS на WebGL; ~3200 узлов/68000 рёбер — 3 FPS canvas, 10 FPS WebGL (M1). 3)
SVG-экспорта в ядре нет; расширение cytoscape-svg — GPL-3.0. 4) cytoscape-expand-collapse прямо помечено авторами как более не поддерживаемое. 5) react-cytoscapejs: последний релиз 2022-09.
CAPABILITIES: Canvas 2D + опциональный WebGL-режим (renderer {name:'canvas', webgl:true}, с 3.31). Направленный мультиграф (bezier-рёбра автоматически разводят параллельные рёбра), подписи рёбер, compound nodes (группы/комбо), селекторы и стили
по данным (фильтры по сумме/времени, подсветка маршрута через классы), алгоритмы (BFS, кратчайшие пути), zoom/pan, встроенный экспорт cy.png()/cy.jpg() (full, scale, blob-promise). Layout: preset, breadthfirst, dagre (rankDir LR),
elk layered, fcose (compound + constraints), cola. Бейджи — через background-image (SVG data URI) или cytoscape-layers 3.1.0 (MIT).
INFRA: Только браузер; layout можно вынести в Web Worker. Серверной части не требует.
PRICING/LIMITS: $0. Лимитов нет.
RISKS: При 10 000 узлов с подписями на canvas плавности не будет — нужен WebGL-режим + LOD (min-zoomed-font-size, скрытие подписей рёбер) и агрегация. Сами авторы признают архитектурный потолок v3 (issue #3486). Часть расширений не
поддерживается (expand-collapse, react-обёртка) — писать свой тонкий слой. Иерархические layout (dagre/ELK) медленные на больших графах.
REPLACEABILITY: Средняя: держать собственную нейтральную модель графа и адаптер GraphView; стили/события Cytoscape изолировать в одном модуле. Замена на Sigma/G6 — переписывание адаптера (1–2 недели).
HOW VERIFIED: gh api (метаданные, релизы, коммиты в webgl/, issues #3486, #3374, #3376), npm registry, чтение raw documentation/md/performance.md, core/init.md, core/png.md, блог WebGL preview (WebFetch), README расширений.
CONFIDENCE: high
EVIDENCE: https://github.com/cytoscape/cytoscape.js | https://blog.js.cytoscape.org/2025/01/13/webgl-preview/ | https://github.com/cytoscape/cytoscape.js/issues/3486 | https://raw.githubusercontent.com/cytoscape/cytoscape.js/unstable/documentation/md/performance.md | https://registry.npmjs.org/cytoscape | https://github.com/cytoscape/cytoscape.js-dagre

### [NEEDS-TRIAL] Sigma.js 4.0.1 + graphology 0.26.0
NEED: Библиотека визуализации графа (карта движения средств)
KIND: open-source
URL: https://github.com/jacomyal/sigma.js
LICENSE: MIT
COMMERCIAL USE: Да, без условий
PROJECT STATE: 12 187 звёзд, 6 open issues; sigma@4.0.0 вышла 2026-10-08, 4.0.1 — 2026-10-13 (вчера); линия v3 закончилась на 3.0.3 (2026-04-30). 5 CI workflows, browser-tests в монорепо. 472 тыс. загрузок/нед. Основные авторы: jacomyal (1348
коммитов), Yomguithereal (720). graphology 0.26.0 (2025-01), 89 open issues, последний коммит 2026-09-02.
CLAIMED VS ACTUAL: 1) v4 — полная переписка системы программ, релизу 6 дней: зрелость в продакшене не подтверждена. 2) @react-sigma/core 5.0.6 (2025-12) требует sigma ^3.0.2 — React-обёртка v4 пока не поддерживает. 3) Нет compound/combo-узлов (issue
#1515 открыт с 2025-03). 4) Нет встроенного иерархического/LR layout — координаты считать самим (dagre/ELK/свой алгоритм). 5) Экспорт только растровый; SVG нет. 6) Численных бенчмарков в документации v4 нет.
CAPABILITIES: Чистый WebGL2. v4: подписи узлов и рёбер в WebGL (SDF), нативные параллельные рёбра и петли, встроенные пути рёбер (line, curved, step), dashed, opacity, depth-слои, встроенное перетаскивание узлов, декларативные styles.
@sigma/export-image 4.0.0 (PNG), @sigma/node-border, node-image, node-piechart, layout-fa2-gpu. graphology — мультиграф (MultiDirectedGraph), метрики, Louvain, ForceAtlas2.
INFRA: Браузер с WebGL2.
PRICING/LIMITS: $0
RISKS: Свежий мажор с ломающим API; нет группировки/комбо «из коробки»; иерархический layout и expand/collapse — полностью свой код; требуется WebGL2.
REPLACEABILITY: Средняя; graphology удобно использовать как нейтральную модель графа и при другом рендерере.
HOW VERIFIED: gh api (релизы, release notes 4.0.0, список packages/, issues), npm registry (версии, peerDependencies), migration guide v3→v4 (WebFetch).
CONFIDENCE: medium
EVIDENCE: https://github.com/jacomyal/sigma.js/releases/tag/sigma%404.0.0 | https://www.sigmajs.org/how-to/technical/migration-v3-v4/ | https://github.com/jacomyal/sigma.js/issues/1515 | https://registry.npmjs.org/@react-sigma%2Fcore | https://registry.npmjs.org/sigma

### [REJECTED] React Flow / xyflow (@xyflow/react 12.12.0) + elkjs
NEED: Библиотека визуализации графа (карта движения средств)
KIND: open-source (+ платная подписка Pro на примеры/поддержку)
URL: https://github.com/xyflow/xyflow
LICENSE: MIT
COMMERCIAL USE: Да (MIT). Сайт просит убирать атрибуцию только подписчикам Pro — это просьба, не условие лицензии.
PROJECT STATE: 38 655 звёзд, 149 open issues, релиз 12.12.0 от 2026-09-24, тег next 13.0.0-next.0; 9 workflows; 14 млн загрузок/нед; TypeScript.
CLAIMED VS ACTUAL: Позиционируется как универсальный, но мейнтейнер прямо писал в issue #967: DOM-рендер, предел ~1000 узлов в зависимости от сложности; RFC по виртуализации #4239 открыт с 2024-05 без реализации. Официальная страница performance не
называет лимитов. Параллельные рёбра между одной парой узлов накладываются без кастомного edge. Экспорт в PNG — только через сторонний html-to-image.
CAPABILITIES: DOM/SVG-рендер: узлы — React-компоненты (идеально для бейджей, карточек адреса), подписи рёбер, sub-flows, minimap, controls. Layout внешний (dagre/ELK).
INFRA: Браузер, React.
PRICING/LIMITS: Библиотека $0. Pro: Starter $169/мес, Professional $289/мес, Enterprise — по запросу (годовые цены на странице не видны).
RISKS: Не тянет 1 000–10 000 узлов с плавным взаимодействием; мультиграф и экспорт — свой код.
REPLACEABILITY: Низкая связность с данными, но узлы-компоненты не переносятся в canvas-библиотеки.
HOW VERIFIED: gh api (метаданные, issues #967 — комментарии мейнтейнера, #4239), npm registry, reactflow.dev/pro и /learn/advanced-use/performance (WebFetch).
CONFIDENCE: high
EVIDENCE: https://github.com/xyflow/xyflow/issues/967 | https://github.com/xyflow/xyflow/issues/4239 | https://reactflow.dev/pro | https://reactflow.dev/learn/advanced-use/performance

### [REJECTED] AntV G6 5.1.1
NEED: Библиотека визуализации графа (карта движения средств)
KIND: open-source
URL: https://github.com/antvis/G6
LICENSE: MIT
COMMERCIAL USE: Да
PROJECT STATE: 12 329 звёзд, 322 открытых issue (всего 335 с PR); релиз 5.1.1 от 2026-04-17 (npm 2026-05-08); последний коммит в packages/g6/src — 2026-04-16, далее 6 месяцев только docs/chore; с 2026-04-01 создано 24 issue, закрыто 28. На issue
отвечает в основном AI-бот. 235 тыс. загрузок/нед.
CLAIMED VS ACTUAL: Заявлена высокая производительность, фактически: issue #7534 (открыт с 2025-12, 10 комментариев) — 2000 узлов с подписями: v4 работает, v5 зависает; пользователи сообщают о пределе в 200–250 узлов; issue #7648 (открыт с 2026-04) —
официальный пример massive-data на 60 000 узлов падает в Chrome 147/149 с переполнением стека; ответов от людей нет, только бот.
CAPABILITIES: По дереву исходников ветки v5: combos (circle, rect), behaviors collapse-expand, optimize-viewport-transform, brush/lasso select, fix-element-size; плагины timebar, minimap, fisheye, edge-bundling, edge-filter-lens, hull, bubble-
sets, legend, history, toolbar, tooltip, contextmenu; рёбра line/polyline/quadratic/cubic; layout через @antv/layout 2.0.0; расширения g6-extension-react, g6-ssr. По набору функций — самое полное совпадение с требованиями (комбо +
timebar + collapse).
INFRA: Браузер.
PRICING/LIMITS: $0
RISKS: Регрессии производительности v5 именно в нашем диапазоне (1–10 тыс. узлов), фактическая остановка разработки ядра с апреля 2026, документация и issue преимущественно на китайском.
REPLACEABILITY: Средняя.
HOW VERIFIED: gh api: дерево исходников, коммиты по пути packages/g6/src, чтение issues #7534 и #7648 с комментариями, счётчики search/issues; npm registry.
CONFIDENCE: high
EVIDENCE: https://github.com/antvis/G6/issues/7534 | https://github.com/antvis/G6/issues/7648 | https://github.com/antvis/G6/tree/v5/packages/g6/src | https://registry.npmjs.org/@antv%2Fg6

### [REJECTED] Graphin 3.0.5 (@antv/graphin)
NEED: Библиотека визуализации графа (карта движения средств)
KIND: open-source
URL: https://github.com/antvis/Graphin
LICENSE: MIT
COMMERCIAL USE: Да
PROJECT STATE: 1 099 звёзд, 64 open issues, релиз 3.0.5 от 2025-04-24, последний коммит 2025-11-18, 1 workflow.
CLAIMED VS ACTUAL: Раньше (v2) был богатым набором компонентов для расследований; v3 — лишь обёртка, наследует все проблемы G6 v5; год без релизов.
CAPABILITIES: Тонкая React-обёртка над G6 v5.
PRICING/LIMITS: $0
RISKS: Заброшенность + проблемы G6 v5.
HOW VERIFIED: gh api, npm registry (версии, peerDependencies).
CONFIDENCE: medium
EVIDENCE: https://github.com/antvis/Graphin | https://registry.npmjs.org/@antv%2Fgraphin

### [ALTERNATIVE] vis-network 10.1.2
NEED: Библиотека визуализации графа (карта движения средств)
KIND: open-source
URL: https://github.com/visjs/vis-network
LICENSE: Apache-2.0 OR MIT
COMMERCIAL USE: Да
PROJECT STATE: 3 631 звезда, 351 open issue; релиз v10.1.2 от 2026-08-19; коммиты почти целиком от renovate-бота, содержательные правки lib/ редки (2026-08 поддержка TypeScript 6, 2026-05 одна фича physics); 886 тыс. загрузок/нед; типы в пакете.
CLAIMED VS ACTUAL: Проект в режиме сопровождения: многолетние открытые issue по иерархическому layout (#84 пересечения рёбер, #100 sortMethod, оба с 2019). Нет compound-узлов (только кластеры-замены), нет WebGL.
CAPABILITIES: Canvas 2D. Иерархический layout (в т.ч. LR, ручные level), физика, кластеризация API, подписи рёбер, стрелки, сглаженные рёбра для параллельных связей. Именно его использует живой OSS-трассировщик crypttrace (vis-network 9.1.9 c
level = номер хопа).
INFRA: Браузер.
PRICING/LIMITS: $0
RISKS: Canvas без WebGL — на тысячах узлов с физикой тормозит; слабая стилизация бейджей; развитие почти остановлено.
REPLACEABILITY: Средняя.
HOW VERIFIED: gh api (коммиты общие и по пути lib/, issues), npm registry; чтение index.html crypttrace.
CONFIDENCE: medium
EVIDENCE: https://github.com/visjs/vis-network | https://registry.npmjs.org/vis-network | https://github.com/bobslayerX/crypttrace/blob/main/src/crypttrace/web/index.html

### [REJECTED] Reagraph 4.32.0
NEED: Библиотека визуализации графа (карта движения средств)
KIND: open-source
URL: https://github.com/reaviz/reagraph
LICENSE: Apache-2.0
COMMERCIAL USE: Да
PROJECT STATE: 1 097 звёзд, 11 open issues, релиз 4.32.0 от 2026-06-25 (ESM-only с 4.31.0), 4 workflows, 70 тыс. загрузок/нед, 21 зависимость (three 0.184, react-three-fiber 9.6).
CLAIMED VS ACTUAL: Заявлено «high-performance WebGL», но в issue #113 пользователи сообщают: 400 узлов — 12–28 FPS, 2600 узлов — зависание 40 с и 1–3 FPS; в 2024 году — «~2000 узлов грузятся с трудом». В 4.32.0 (2026-06) заявлены оптимизации,
независимых замеров нет.
CAPABILITIES: WebGL через three.js/R3F, React-first. Layout: force 2D/3D, tree LR, hierarchical LR, radial, no-overlap, ForceAtlas2; кластеризация, expand/collapse, бейджи узлов, edge bundling, подписи рёбер, поиск пути, lasso.
PRICING/LIMITS: $0
RISKS: Каждый узел — React-компонент в R3F, масштабирование под 10 тыс. узлов не подтверждено; тяжёлый бандл (three.js); один основной мейнтейнер.
HOW VERIFIED: gh api (README, issue #113 с комментариями, коммиты), CHANGELOG.md, npm registry.
CONFIDENCE: medium
EVIDENCE: https://github.com/reaviz/reagraph/issues/113 | https://raw.githubusercontent.com/reaviz/reagraph/master/CHANGELOG.md | https://registry.npmjs.org/reagraph

### [REJECTED] force-graph 1.52.0 / react-force-graph-2d 1.29.2
NEED: Библиотека визуализации графа (карта движения средств)
KIND: open-source
URL: https://github.com/vasturiano/force-graph
LICENSE: MIT
COMMERCIAL USE: Да
PROJECT STATE: force-graph: 2 141 звезда, 151 open issue, v1.52.0 от 2026-09-28; react-force-graph: 3 324 звезды, 218 open issues; один автор (vasturiano); ~990 тыс. и ~880 тыс. загрузок/нед.
CLAIMED VS ACTUAL: linkLabel — это всплывающая подсказка, а не постоянная подпись; постоянные подписи суммы/времени/TXID нужно рисовать вручную через linkCanvasObject. dagMode по README корректно работает только на DAG — в графах движения средств
бывают циклы. Нет группировки/комбо.
CAPABILITIES: Canvas 2D + d3-force. dagMode lr/td (только для графов без циклов), linkCurvature для параллельных рёбер, кастомная отрисовка узлов/рёбер на canvas.
PRICING/LIMITS: $0
RISKS: Только силовая раскладка; много ручного кода под требования; bus factor = 1.
HOW VERIFIED: gh api (README, метаданные), npm registry.
CONFIDENCE: medium
EVIDENCE: https://github.com/vasturiano/force-graph | https://registry.npmjs.org/force-graph

### [REJECTED] cosmos.gl 3.5.1 (@cosmos.gl/graph) и Cosmograph 2.5.1 (@cosmograph/*)
NEED: Библиотека визуализации графа (карта движения средств)
KIND: open-source (cosmos.gl) / проприетарная надстройка (Cosmograph)
URL: https://github.com/cosmosgl/graph
LICENSE: cosmos.gl — MIT; @cosmograph/cosmograph, @cosmograph/react, @cosmograph/cosmos — CC-BY-NC-4.0
COMMERCIAL USE: cosmos.gl — да. Cosmograph — НЕТ без отдельной проприетарной лицензии (цена только по запросу).
PROJECT STATE: cosmosgl/graph: 1 296 звёзд, 15 open issues, v3.5.1 от 2026-10-05, 4 workflows, 58 тыс. загрузок/нед; peer-зависимость luma.gl ~9.3.0.
CLAIMED VS ACTUAL: Маркетинг Cosmograph («timeline, search, filtering») относится к некоммерческой надстройке; в MIT-ядре нет встроенных подписей узлов/рёбер, нет иерархического layout, нет комбо — всё поверх писать самим. Старое имя пакета
@cosmograph/cosmos 3.4.1 теперь тоже CC-BY-NC-4.0 — легко ошибиться пакетом.
CAPABILITIES: GPU-симуляция и рендер силового графа на сотни тысяч точек; кластерная сила, перетаскивание точек, выборка видимых связей для внешних подписей.
PRICING/LIMITS: cosmos.gl $0; Cosmograph Business — «Contact us».
RISKS: Не подходит для доказательной карты с подписями рёбер и LR-потоком; лицензионная ловушка в названиях пакетов.
HOW VERIFIED: gh api (README, метаданные), npm registry (поле license по каждому пакету), cosmograph.app/licensing (WebFetch).
CONFIDENCE: high
EVIDENCE: https://github.com/cosmosgl/graph | https://cosmograph.app/licensing/ | https://registry.npmjs.org/@cosmograph%2Fcosmograph | https://registry.npmjs.org/@cosmos.gl%2Fgraph

### [REJECTED] D3 7.9.0 (d3-force 3.0.0, d3-zoom, d3-dag 1.2.2)
NEED: Библиотека визуализации графа (карта движения средств)
KIND: open-source
URL: https://github.com/d3/d3
LICENSE: ISC (d3), MIT (d3-dag)
COMMERCIAL USE: Да
PROJECT STATE: 113 744 звезды; d3 v7.9.0 от 2024-03-12 (последний коммит 2026-05-28); d3-force 3.0.0 от 2021-06, последний коммит 2023-10; d3-dag 1.2.2 от 2026-07-05.
CLAIMED VS ACTUAL: none found (D3 и не заявляет готовый граф-компонент). Типы — отдельным пакетом @types/d3.
CAPABILITIES: Низкоуровневые примитивы: силовая симуляция, zoom, шкалы; рендер (SVG/Canvas) и всё взаимодействие — свой код.
PRICING/LIMITS: $0
RISKS: Противоречит стратегии «свой код — только клей»: придётся писать рендер, hit-testing, подписи, группировку, экспорт. Оправдан только для гистограммы времени/шкал.
HOW VERIFIED: gh api, npm registry.
CONFIDENCE: high
EVIDENCE: https://github.com/d3/d3 | https://registry.npmjs.org/d3-force

### [REJECTED] NVL — Neo4j Visualization Library 2.0.0 (@neo4j-nvl/base, /react)
NEED: Библиотека визуализации графа (карта движения средств)
KIND: проприетарная библиотека (распространяется через npm)
URL: https://www.npmjs.com/package/@neo4j-nvl/base
LICENSE: Собственное лицензионное соглашение Neo4j (LICENSE.txt в пакете), не open-source
COMMERCIAL USE: НЕТ для нашего случая: по тексту лицензии NVL разрешено использовать только совместно с Neo4j Aura либо с коммерческими СУБД Neo4j по Subscription Agreement.
PROJECT STATE: 2.0.0 от 2026-09-15; ~21 тыс. загрузок/нед; публичного репозитория исходников нет (neo4j/nvl-boilerplates — 404).
CLAIMED VS ACTUAL: На npm выглядит как свободно устанавливаемая библиотека, но поле license = «SEE LICENSE IN LICENSE.txt», а сам текст привязывает использование к продуктам Neo4j.
CAPABILITIES: По составу пакета: force-directed (в т.ч. GPU-шейдеры), hierarchical, grid, circular, free layout; обработчики взаимодействий; React-обёртка.
PRICING/LIMITS: Отдельной цены нет; требуется подписка на Neo4j Aura/Enterprise.
RISKS: Лицензионный блокер, если платформа не строится на платном Neo4j.
HOW VERIFIED: Прочитан LICENSE.txt версии 2.0.0 через unpkg (curl), npm registry, список файлов пакета.
CONFIDENCE: high
EVIDENCE: https://unpkg.com/@neo4j-nvl/base@2.0.0/LICENSE.txt | https://registry.npmjs.org/@neo4j-nvl%2Fbase

### [REJECTED] Memgraph Orb 1.1.0 (@memgraph/orb)
NEED: Библиотека визуализации графа (карта движения средств)
KIND: open-source
URL: https://github.com/memgraph/orb
LICENSE: Apache-2.0
COMMERCIAL USE: Да
PROJECT STATE: 427 звёзд, 16 open issues, v1.1.0 от 2026-09-08, 3 workflows, всего 1 851 загрузка/нед.
CLAIMED VS ACTUAL: Возможности взяты только из README; из-за малой аудитории нет независимых подтверждений производительности и зрелости WebGL-режима. Группировка/комбо и экспорт не подтверждены.
CAPABILITIES: По README: рендер Canvas 2D или WebGL, layout force (CPU/GPU), circular, grid, hierarchical, карта (leaflet), симуляция в Web Worker.
PRICING/LIMITS: $0
RISKS: Очень маленькое сообщество, зависимость от одной компании.
HOW VERIFIED: gh api (README, метаданные), npm registry. Код не читался.
CONFIDENCE: low
EVIDENCE: https://github.com/memgraph/orb | https://registry.npmjs.org/@memgraph%2Forb

### [ALTERNATIVE] GoJS 4.0.5 (Northwoods)
NEED: Библиотека визуализации графа — коммерческий вариант
KIND: commercial library
URL: https://nwoods.com/sales/index.html
LICENSE: Проприетарная (license.html), per-developer, бессрочные права на распространение
COMMERCIAL USE: Да, после покупки; по странице продаж — без runtime-отчислений и роялти. Исходный код — только при отдельном праве в сертификате.
PROJECT STATE: Репозиторий-дистрибутив: 8 489 звёзд, релиз v4.0.5 от 2026-10-02; 309 тыс. загрузок npm/нед.
CLAIMED VS ACTUAL: Условия SaaS, доменов и водяного знака оценочной версии на странице цен не раскрыты — отсылают к отделу продаж.
CAPABILITIES: Canvas-диаграммы с богатыми шаблонами узлов, layered/tree/force layout, группы, экспорт изображений/SVG (по документации, в этом аудите не перепроверялось).
PRICING/LIMITS: Individual $3 995; Team (до 3 разработчиков) $6 990; Group (до 20) $11 950; Enterprise — по запросу. Включён 1 год поддержки и обновлений; цена продления не указана.
RISKS: Ориентирована на диаграммы, а не на большие сети; закрытый код; разовая стоимость сопоставима с месяцами работы над OSS-слоем.
HOW VERIFIED: Страница продаж (WebFetch), gh api, npm registry, фрагмент license.html.
CONFIDENCE: medium
EVIDENCE: https://nwoods.com/sales/index.html | https://github.com/NorthwoodsSoftware/GoJS | https://registry.npmjs.org/gojs

### [ALTERNATIVE] KeyLines / ReGraph (+ KronoGraph) — Cambridge Intelligence
NEED: Библиотека визуализации графа — коммерческий вариант
KIND: commercial SDK
URL: https://cambridge-intelligence.com/pricing/
LICENSE: Проприетарная подписка (обычно 1–3 года), лицензируется по масштабу распространения конечным пользователям
COMMERCIAL USE: Да, только по подписке Subscription; trial и POC запрещают распространение конечным пользователям.
PROJECT STATE: Закрытый продукт; версия на сайте не показана.
CLAIMED VS ACTUAL: Цены не публикуются вообще; численных бенчмарков на странице продукта нет; time bar и форматы экспорта на странице KeyLines не упомянуты.
CAPABILITIES: По сайту: GPU-рендеринг, комбо-группировка с раскрытием, алгоритмы центральности и обхода; ReGraph — React-SDK; KronoGraph — таймлайны. Фактически отраслевой стандарт для расследований.
PRICING/LIMITS: Только по запросу. Trial 21 день (с водяным знаком); POC ~3 месяца по спеццене.
RISKS: Непрозрачная цена (не проверена), vendor lock-in, закрытый код.
HOW VERIFIED: Страницы pricing и keylines (WebFetch). Код/SDK не оценивались.
CONFIDENCE: medium
EVIDENCE: https://cambridge-intelligence.com/pricing/ | https://cambridge-intelligence.com/keylines/

### [ALTERNATIVE] Ogma 6.1.0 (Linkurious)
NEED: Библиотека визуализации графа — коммерческий вариант
KIND: commercial library
URL: https://linkurious.com/ogma/
LICENSE: Проприетарная
COMMERCIAL USE: Да, по коммерческой лицензии; условия и цена не опубликованы.
PROJECT STATE: Закрытый продукт; в документации версия 6.1.0.
CLAIMED VS ACTUAL: Заявления «10 000 узлов за 1 секунду» и «layout до 40 раз быстрее» — маркетинг без методики; независимая проверка не выполнялась. Иерархические layout на обзорной странице не перечислены.
CAPABILITIES: По сайту и документации: WebGL-first с поддержкой Canvas и SVG, группировка узлов, трансформации, таймлайн, экспорт PNG/SVG/PDF/Excel, интеграция с React.
PRICING/LIMITS: Не публикуется; бесплатный trial по запросу.
RISKS: Цена неизвестна, lock-in.
HOW VERIFIED: linkurious.com/ogma и doc.linkurious.com/ogma/latest (WebFetch).
CONFIDENCE: low
EVIDENCE: https://linkurious.com/ogma/ | https://doc.linkurious.com/ogma/latest/

### [REJECTED] yFiles for HTML (yWorks)
NEED: Библиотека визуализации графа — коммерческий вариант
KIND: commercial library
URL: https://www.yfiles.com/pricing
LICENSE: Проприетарная срочная лицензия (годовая)
COMMERCIAL USE: Да; ключи привязаны к доменам (1/2/4 домена по тарифам), есть ключ без ограничения доменов.
PROJECT STATE: Закрытый продукт.
CLAIMED VS ACTUAL: none found (цены и ограничения опубликованы открыто)
CAPABILITIES: Лучшие в отрасли автоматические layout (иерархический, органический и др.) — по общей репутации; в этом аудите возможности не перепроверялись.
PRICING/LIMITS: В год, без НДС: Single Developer €9 200 / $11 000 (1 именной разработчик, 1 домен); Project €18 400 / $22 000 (3 плавающих места, 2 домена); Site €55 200 / $66 000 (без ограничения разработчиков, 4 домена).
RISKS: Цена несоразмерна раннему этапу и целевой себестоимости; годовая лицензия.
HOW VERIFIED: Страница цен (WebFetch после редиректа с yworks.com).
CONFIDENCE: high
EVIDENCE: https://www.yfiles.com/pricing

### [REJECTED] Graphistry (Hub / self-hosted)
NEED: Библиотека визуализации графа — коммерческий вариант
KIND: commercial SaaS / self-hosted GPU-сервер
URL: https://www.graphistry.com/get-started
LICENSE: Сервер проприетарный; клиенты pygraphistry BSD-3-Clause, graphistry-js Apache-2.0
COMMERCIAL USE: Встраивание заявлено как функция, но разрешение встраивать в коммерческий SaaS на странице не указано (EULA не читалась).
PROJECT STATE: pygraphistry 0.60.0 от 2026-10-09 (2 569 звёзд); graphistry-js: последний коммит 2025-07-10, 49 звёзд.
CLAIMED VS ACTUAL: Числовые лимиты узлов/рёбер для Hub не опубликованы; JS-клиент не обновлялся более года.
CAPABILITIES: Серверный GPU-рендеринг очень больших графов, встраивание через iframe/React.
INFRA: GPU-сервер с RAPIDS либо облако Graphistry.
PRICING/LIMITS: Hub: Free $0 (приватность только через unlisted-ссылки), Professional $83/мес, Organization $83/польз./мес от 3 пользователей. Self-hosted: $1,47/час + GPU-инстанс (AWS g4dn.xlarge / Azure T4), Team $10/час + GPU.
RISKS: Нужен GPU-сервер — противоречит «одному скромному серверу»; данные расследований уходят в стороннее облако (Hub); постоянные расходы ломают лимит $1 на расследование.
HOW VERIFIED: Страница get-started (WebFetch), gh api.
CONFIDENCE: medium
EVIDENCE: https://www.graphistry.com/get-started | https://github.com/graphistry/graphistry-js

### [RECOMMENDED] @dagrejs/dagre 3.1.1 (через cytoscape-dagre 4.0.1)
NEED: Layout-движок для потока слева направо / иерархии
KIND: open-source
URL: https://github.com/dagrejs/dagre
LICENSE: MIT
COMMERCIAL USE: Да
PROJECT STATE: 5 826 звёзд, 175 open issues, переписан на TypeScript, v2.0.0 в 2025-11, npm 3.1.1, последний коммит 2026-08-08; 5,4 млн загрузок/нед.
CLAIMED VS ACTUAL: Issue #297: граф 1000+ узлов раскладывается ~3 с и дальше растёт; участник проекта подтвердил квадратичную/кубическую сложность. Для 10 000 узлов непригоден.
CAPABILITIES: Sugiyama-раскладка, rankDir LR/TB, ranker network-simplex / tight-tree / longest-path, minLen по рёбрам.
PRICING/LIMITS: $0
RISKS: Только для видимого подграфа до нескольких сотен узлов; запускать в Web Worker.
HOW VERIFIED: gh api (issue #297 с комментариями, метаданные), npm registry, README cytoscape-dagre.
CONFIDENCE: high
EVIDENCE: https://github.com/dagrejs/dagre/issues/297 | https://github.com/cytoscape/cytoscape.js-dagre

### [ALTERNATIVE] elkjs 0.12.0 (ELK layered; cytoscape-elk 2.3.0)
NEED: Layout-движок для потока слева направо / иерархии
KIND: open-source
URL: https://github.com/kieler/elkjs
LICENSE: EPL-2.0 OR GPL-3.0-or-later
COMMERCIAL USE: Да по EPL-2.0 (слабый copyleft: изменения самих файлов ELK нужно раскрывать); желательна короткая юридическая проверка для минифицированного бандла.
PROJECT STATE: 2 815 звёзд, 97 open issues, 0.12.0 от 2026-07-17, последний коммит 2026-10-06, 4 workflows, 11,7 млн загрузок/нед.
CLAIMED VS ACTUAL: Issue #372 (2026-03): 406 узлов и 2301 ребро — около 4 секунд, в отдельных случаях более 10 с; участник команды ELK признал известные проблемы скорости (GWT-компиляция Java→JS). WASM-сборка — экспериментальный PR #376, не в
релизе.
CAPABILITIES: Самая качественная layered-раскладка с портами, вложенными графами и ортогональной маршрутизацией; работает в Web Worker.
PRICING/LIMITS: $0
RISKS: Слишком медленный для 1 000+ узлов в интерактиве; бандл несколько МБ; copyleft-лицензия.
HOW VERIFIED: gh api (issue #372 с комментариями, LICENSE.md), npm registry.
CONFIDENCE: high
EVIDENCE: https://github.com/kieler/elkjs/issues/372 | https://registry.npmjs.org/elkjs

### [REJECTED] cytoscape-expand-collapse 4.1.1 / cytoscape-complexity-management 1.0.0
NEED: Группировка, сворачивание и раскрытие по требованию
KIND: open-source
URL: https://github.com/iVis-at-Bilkent/cytoscape.js-expand-collapse
LICENSE: MIT
COMMERCIAL USE: Да
PROJECT STATE: expand-collapse: 140 звёзд, 32 open issues, релиз 4.1.1 от 2024-08-28, последний коммит 2024-11-27, CI нет, 24 тыс. загрузок/нед. Преемник complexity-management: 13 звёзд, v1.0.0 от 2025-11, 2 загрузки/нед.
CLAIMED VS ACTUAL: В первой строке README авторы сообщают, что репозиторий больше не поддерживается; преемник практически никем не используется. Типов TypeScript нет.
CAPABILITIES: Сворачивание/раскрытие compound-узлов; collapseEdges / collapseEdgesBetweenNodes — схлопывание параллельных рёбер между парой узлов в одно мета-ребро (ровно наш случай мультиграфа).
PRICING/LIMITS: $0
RISKS: Неподдерживаемая зависимость в ключевом сценарии. Логику агрегации рёбер и раскрытия ветви надёжнее делать в своей модели (на бэкенде/в адаптере), используя только ядро Cytoscape (compound nodes, add/remove).
HOW VERIFIED: gh api (README, метаданные), npm registry.
CONFIDENCE: high
EVIDENCE: https://github.com/iVis-at-Bilkent/cytoscape.js-expand-collapse | https://github.com/iVis-at-Bilkent/cytoscape.js-complexity-management

### [RECOMMENDED] Vite 8.3.4 + React 19.3.0 + TypeScript (SPA, статическая сборка)
NEED: Стек web-интерфейса
KIND: open-source
URL: https://github.com/vitejs/vite
LICENSE: MIT
COMMERCIAL USE: Да
PROJECT STATE: Vite: 83 353 звезды, v8.3.4 от 2026-10-08, 196 млн загрузок/нед, engines node ^20.19.0 || >=22.12.0. React 19.3.0 (2026-09-09). Маршрутизация: @tanstack/react-router 1.170.44 (node >=20.19) или react-router 8.4.0 (node >=22.22.0,
react >=19.2.7).
CLAIMED VS ACTUAL: none found. Нюанс: 7 security advisories Vite за 2026 год касаются dev-сервера (обходы server.fs.deny, в т.ч. на Windows) — dev-сервер нельзя выставлять в сеть.
CAPABILITIES: Сборка в статические файлы, которые раздаёт nginx или сам Python-бэкенд: в продакшене нет Node-процесса. Все граф-библиотеки (canvas/WebGL) клиентские, SSR им не нужен.
INFRA: Только статика за nginx/бэкендом; сборка в Docker на Node 24 LTS.
PRICING/LIMITS: $0
RISKS: Нет SSR/SEO (для закрытого кабинета не нужно; маркетинговый сайт — отдельно). Dev-машина на Node 23.4.0 — ветка EOL с 2025-06-01, перейти на Node 24 LTS (или 22 LTS).
REPLACEABILITY: Высокая: React-компоненты переносимы в Next.js при необходимости.
HOW VERIFIED: gh api (метаданные, security-advisories), npm registry (engines), nodejs/Release schedule.json, локально node --version = v23.4.0.
CONFIDENCE: high
EVIDENCE: https://registry.npmjs.org/vite/latest | https://github.com/vitejs/vite/security/advisories | https://raw.githubusercontent.com/nodejs/Release/main/schedule.json

### [REJECTED] Next.js 16.4.0
NEED: Стек web-интерфейса
KIND: open-source
URL: https://github.com/vercel/next.js
LICENSE: MIT
COMMERCIAL USE: Да
PROJECT STATE: 143 209 звёзд, 3 663 open issues, v16.4.0 от 2026-10-07, 67,7 млн загрузок/нед, engines node >=20.9.0.
CLAIMED VS ACTUAL: Самостоятельный хостинг заявлен как полноценный, но за 2026 год опубликован 41 security advisory (3 critical, 14 high), включая неаутентифицированный RCE на Windows-серверах (CVE-2026-75604, 2026-08-25), RCE в Image Optimization
API и в next/og, SSRF, обходы middleware, cache poisoning при self-hosting. Для сравнения: в 2025 — 14.
CAPABILITIES: SSR/RSC, App Router, Server Actions, оптимизация изображений — полезно для публичных сайтов.
INFRA: Node-сервер в продакшене.
PRICING/LIMITS: $0
RISKS: Серверный Node-процесс с большой поверхностью атаки в продукте с чувствительными данными расследований; маленькой команде придётся постоянно патчить. Серверные возможности дублируют Python-бэкенд.
HOW VERIFIED: gh api repos/vercel/next.js/security-advisories (подсчёт по годам и severity), npm registry; веб-поиск по CVE-2025-55182 (вторичные источники).
CONFIDENCE: high
EVIDENCE: https://github.com/vercel/next.js/security/advisories | https://registry.npmjs.org/next/latest

### [REJECTED] SvelteKit 3.0.1 (Svelte 5.57) и Nuxt 4.6.1 (Vue 3.5)
NEED: Стек web-интерфейса
KIND: open-source
URL: https://github.com/sveltejs/kit
LICENSE: MIT
COMMERCIAL USE: Да
PROJECT STATE: SvelteKit: 20 848 звёзд, 3.0.1 от 2026-10-06 (свежий мажор), node >=22.17, 16 advisories за 2026. Nuxt: 60 938 звёзд, 4.6.1 от 2026-10-09, engines ^22.22.3 || ^24.15.0 || >=26.0.0.
CLAIMED VS ACTUAL: Nuxt 4.6.1 по полю engines не поддерживает Node 23, установленный на dev-машине. SvelteKit 3 вышел неделю назад.
CAPABILITIES: Полноценные мета-фреймворки; у xyflow есть @xyflow/svelte 1.7.0.
PRICING/LIMITS: $0
RISKS: Экосистема готовых компонентов для расследований (таблицы, граф-обёртки, UI-киты) и кадровый рынок заметно уже, чем у React; большинство граф-библиотек дают React-обёртки и примеры.
HOW VERIFIED: gh api (метаданные, security-advisories), npm registry (engines).
CONFIDENCE: medium
EVIDENCE: https://registry.npmjs.org/nuxt/latest | https://registry.npmjs.org/@sveltejs%2Fkit/latest

### [RECOMMENDED] shadcn/ui (CLI shadcn 4.21.4) + Tailwind CSS 4.3.3 + Radix UI / Base UI
NEED: UI-кит, загрузка данных, таблицы
KIND: open-source
URL: https://github.com/shadcn-ui/ui
LICENSE: MIT
COMMERCIAL USE: Да
PROJECT STATE: 125 523 звезды, 1 794 open issues, релиз shadcn@4.21.4 от 2026-10-07, 17 workflows; 11,9 млн загрузок CLI/нед. В реестре v4: recharts 3.8.0, @tanstack/react-table ^9, tailwindcss ^4.3, radix-ui ^1.4.3 и @base-ui/react 1.6.0.
CLAIMED VS ACTUAL: none found. Особенность: это не npm-библиотека, обновления компонентов — вручную через CLI.
CAPABILITIES: Компоненты копируются в репозиторий (нет runtime-зависимости от кита): таблицы на TanStack Table, графики на Recharts, command palette (cmdk) для поиска узлов, resizable panels для раскладки «граф + детали», формы, диалоги.
PRICING/LIMITS: $0
RISKS: Код компонентов становится своим — его нужно сопровождать; дизайн-система требует дисциплины.
REPLACEABILITY: Высокая (обычные React-компоненты).
HOW VERIFIED: gh api, npm registry, чтение apps/v4/package.json.
CONFIDENCE: high
EVIDENCE: https://github.com/shadcn-ui/ui | https://raw.githubusercontent.com/shadcn-ui/ui/main/apps/v4/package.json

### [ALTERNATIVE] Mantine 9.7.2
NEED: UI-кит, загрузка данных, таблицы
KIND: open-source
URL: https://github.com/mantinedev/mantine
LICENSE: MIT
COMMERCIAL USE: Да
PROJECT STATE: 31 827 звёзд, всего 24 open issues, релиз 9.7.2 от 2026-10-11, 2,8 млн загрузок/нед; требует React ^19.2.
CLAIMED VS ACTUAL: none found
CAPABILITIES: Большой готовый набор компонентов и хуков «из коробки», быстрее старт без дизайнера.
PRICING/LIMITS: $0
RISKS: Зависимость от одного основного автора; собственная система стилей вместо Tailwind.
HOW VERIFIED: gh api, npm registry.
CONFIDENCE: medium
EVIDENCE: https://github.com/mantinedev/mantine | https://registry.npmjs.org/@mantine%2Fcore/latest

### [ALTERNATIVE] Ant Design 6.6.6 / MUI 9.5.0
NEED: UI-кит, загрузка данных, таблицы
KIND: open-source
URL: https://github.com/ant-design/ant-design
LICENSE: MIT (ядро); расширенные таблицы MUI X Pro — коммерческие
COMMERCIAL USE: Да для MIT-частей
PROJECT STATE: Ant Design: 99 752 звезды, 1 113 open issues, 6.6.6 от 2026-10-12. MUI: 99 199 звёзд, 1 511 open issues, v9.5.0 от 2026-10-09.
CLAIMED VS ACTUAL: Не аудировались глубоко; проверены только метаданные.
CAPABILITIES: Зрелые корпоративные киты с мощными таблицами и формами.
PRICING/LIMITS: $0 за ядро
RISKS: Тяжёлые бандлы и жёсткий визуальный стиль; продвинутые гриды MUI платные.
HOW VERIFIED: gh api, npm registry (только метаданные).
CONFIDENCE: low
EVIDENCE: https://github.com/ant-design/ant-design | https://github.com/mui/material-ui

### [RECOMMENDED] TanStack Query 5.104.2 + TanStack Table 9.3.1 + TanStack Virtual 3.14.19
NEED: UI-кит, загрузка данных, таблицы
KIND: open-source
URL: https://github.com/TanStack/query
LICENSE: MIT
COMMERCIAL USE: Да
PROJECT STATE: Query: 50 422 звезды, 167 open issues, 65,7 млн загрузок/нед. Table: 28 487 звёзд, 75 open issues, v9 — текущий latest. Virtual: 7 142 звезды. Все обновлялись 2026-10-11…13.
CLAIMED VS ACTUAL: none found
CAPABILITIES: Кэш и опрос статуса долгих расследований, отмена запросов; headless-таблицы с сортировкой/фильтрами; виртуализация списков на тысячи транзакций.
PRICING/LIMITS: $0
RISKS: Table v9 — относительно новый мажор; headless-подход требует своей вёрстки (закрывается шаблонами shadcn). Альтернатива для таблиц — AG Grid Community 36.2.0 (MIT; Enterprise — коммерческая).
HOW VERIFIED: gh api, npm registry.
CONFIDENCE: high
EVIDENCE: https://registry.npmjs.org/@tanstack%2Freact-query/latest | https://registry.npmjs.org/@tanstack%2Freact-table/latest | https://registry.npmjs.org/ag-grid-community/latest

### [RECOMMENDED] Временная ось средствами графа (preset-layout по времени) + гистограмма с brush на Recharts 3.10.1
NEED: Таймлайн / вид по оси времени
KIND: open-source
URL: https://github.com/recharts/recharts
LICENSE: MIT
COMMERCIAL USE: Да
PROJECT STATE: Recharts: 27 628 звёзд, 459 open issues, v3.10.1 от 2026-07-25, коммиты 2026-10-13; входит в реестр shadcn (3.8.0).
CLAIMED VS ACTUAL: none found; это сборка из двух компонентов, а не готовый таймлайн-виджет.
CAPABILITIES: Гистограмма переводов по времени с выделением диапазона управляет фильтром графа; режим «ось времени» — те же узлы и рёбра Cytoscape с x = время транзакции.
PRICING/LIMITS: $0
RISKS: Свой код для связки brush ↔ фильтр графа и для шкалы времени на холсте.
HOW VERIFIED: gh api, npm registry, package.json реестра shadcn.
CONFIDENCE: medium
EVIDENCE: https://github.com/recharts/recharts | https://raw.githubusercontent.com/shadcn-ui/ui/main/apps/v4/package.json

### [ALTERNATIVE] vis-timeline 8.5.4
NEED: Таймлайн / вид по оси времени
KIND: open-source
URL: https://github.com/visjs/vis-timeline
LICENSE: Apache-2.0 OR MIT
COMMERCIAL USE: Да
PROJECT STATE: 2 568 звёзд, 308 open issues, v8.5.4 от 2026-08-12; содержательные правки lib/ редки (2026-08, 2026-07); 247 тыс. загрузок/нед; peer-зависимость moment.
CLAIMED VS ACTUAL: none found
CAPABILITIES: Готовый интерактивный таймлайн с группами, зумом и диапазонами.
PRICING/LIMITS: $0
RISKS: Режим сопровождения, устаревшие зависимости (moment, hammerjs), не React-нативный.
HOW VERIFIED: gh api (коммиты по lib/), npm registry.
CONFIDENCE: medium
EVIDENCE: https://github.com/visjs/vis-timeline | https://registry.npmjs.org/vis-timeline/latest

### [RECOMMENDED] Экспорт: встроенный cy.png() / cytoscape-pdf-export 0.0.5 / cytoscape-svg 0.4.0
NEED: Экспорт карты в PNG / SVG для PDF-отчёта
KIND: open-source
URL: https://github.com/cytoscape/cytoscape.js-pdf-export
LICENSE: cy.png — MIT (ядро); cytoscape-pdf-export — MIT; cytoscape-svg — GPL-3.0
COMMERCIAL USE: cy.png и pdf-export — да. cytoscape-svg — GPL-3.0: включение в закрытый коммерческий фронтенд недопустимо без раскрытия кода.
PROJECT STATE: cytoscape-pdf-export: официальная организация cytoscape, v0.0.5 от 2026-09-25, 2 звезды, 166 загрузок/нед, CI нет. cytoscape-svg: 42 звезды, релиз 2022-05, последний коммит 2024-03.
CLAIMED VS ACTUAL: SVG-экспорт существует только как GPL-расширение; pdf-export — версия 0.0.x с мизерной аудиторией.
CAPABILITIES: cy.png(): весь граф (full), масштаб (scale), ограничения размера, неблокирующий вывод blob-promise. pdf-export — векторный PDF.
PRICING/LIMITS: $0
RISKS: Растровый PNG большого графа тяжёлый; работа cy.png() в WebGL-режиме не проверена; при необходимости SVG — свой сериализатор.
HOW VERIFIED: raw documentation/md/core/png.md, npm registry (поля license), gh api (LICENSE cytoscape-svg).
CONFIDENCE: high
EVIDENCE: https://raw.githubusercontent.com/cytoscape/cytoscape.js/unstable/documentation/md/core/png.md | https://github.com/kinimesi/cytoscape-svg | https://registry.npmjs.org/cytoscape-pdf-export

### [REJECTED] GraphSense Dashboard v26.09.0 (Iknaio)
NEED: Готовый open-source UI для исследования крипто-потоков
KIND: open-source
URL: https://github.com/graphsense/graphsense-dashboard
LICENSE: MIT
COMMERCIAL USE: Да
PROJECT STATE: 142 звезды, 16 open issues, релиз v26.09.0 от 2026-09-30, 5 workflows; написан на Elm, сборка Vite. Старый graphsense-REST заархивирован, API теперь в graphsense-lib (v2.17.0, 2026-09-30).
CLAIMED VS ACTUAL: Нельзя использовать как самостоятельный компонент: без graphsense-lib Web API все запросы падают, а API требует кластер Cassandra и TagStore на PostgreSQL. Поддержка TRON подтверждена только косвенно (ключ валюты trx в примерах
CLI).
CAPABILITIES: Зрелый интерфейс расследований (Pathfinder): граф адресов/кластеров, теги, экспорт.
INFRA: Cassandra-кластер + PostgreSQL TagStore + полная индексация блокчейнов.
PRICING/LIMITS: $0 за код; инфраструктура Cassandra — существенные расходы.
RISKS: Elm не встраивается в React-стек; тяжёлая инфраструктура противоречит одному скромному серверу.
HOW VERIFIED: gh api (README dashboard и graphsense-lib, метаданные).
CONFIDENCE: high
EVIDENCE: https://github.com/graphsense/graphsense-dashboard | https://github.com/graphsense/graphsense-lib

### [REJECTED] crypttrace v0.16.0
NEED: Готовый open-source UI для исследования крипто-потоков
KIND: open-source
URL: https://github.com/bobslayerX/crypttrace
LICENSE: MIT
COMMERCIAL USE: Да
PROJECT STATE: 20 звёзд, 0 open issues, создан 2026-07-21, релиз v0.16.0 от 2026-10-12, 2 workflows, один автор (75 коммитов). Python + Flask, фронтенд — один index.html (46 КБ) с vis-network 9.1.9 с CDN.
CLAIMED VS ACTUAL: Позиционируется как toolkit для расследований, но это молодой проект одного автора без независимой проверки качества меток и трассировки; UI — монолитный HTML, не компонент.
CAPABILITIES: Локальное веб-приложение с интерактивным графом потоков, поддержка Tron без ключа, метки бирж/миксеров, кэш SQLite, backoff на 429; подписи рёбер с суммой, уровни по номеру хопа.
PRICING/LIMITS: $0
RISKS: Bus factor 1, возраст 3 месяца; как зависимость брать нельзя.
HOW VERIFIED: gh api (дерево репозитория, README, contributors), чтение index.html (подключаемые скрипты, конфигурация графа). Код не запускался.
CONFIDENCE: medium
EVIDENCE: https://github.com/bobslayerX/crypttrace | https://raw.githubusercontent.com/bobslayerX/crypttrace/main/src/crypttrace/web/index.html

### [REJECTED] Прочие найденные UI: tronscan-frontend, motif.gl, mempool, openchain transaction viewer
NEED: Готовый open-source UI для исследования крипто-потоков
KIND: open-source
URL: https://github.com/cylynx/motif.gl
LICENSE: tronscan-frontend — LGPL-3.0; motif.gl — MIT; mempool — AGPL-3.0 (с оговоркой о товарных знаках); openchain viewer — без лицензии
COMMERCIAL USE: mempool — AGPL, для закрытого SaaS неприемлемо; openchain — без лицензии, использовать нельзя; tronscan — LGPL, ограниченно; motif.gl — да.
PROJECT STATE: tronscan-frontend: 283 звезды, последний коммит 2022-12, релиз 2020-04. motif.gl: 139 звёзд, последний коммит 2023-08. mempool: 2 854 звезды, активен (v3.3.1). openchainxyz/ethereum-transaction-viewer-frontend: archived, 2022-12.
CLAIMED VS ACTUAL: Ни один не даёт переиспользуемого компонента трассировки для TRON; поиск GitHub по темам blockchain-forensics / crypto-forensics и восьми запросам выдал в основном репозитории с 0–40 звёздами.
CAPABILITIES: tronscan — обозреватель без карты потоков; motif.gl — граф-аналитика на G6/Graphin; mempool — диаграмма входов/выходов Bitcoin-транзакции.
PRICING/LIMITS: $0
RISKS: Заброшенность либо несовместимые лицензии.
HOW VERIFIED: gh api (метаданные, файл LICENSE mempool), gh search repositories.
CONFIDENCE: medium
EVIDENCE: https://github.com/tronscan/tronscan-frontend | https://github.com/cylynx/motif.gl | https://github.com/mempool/mempool | https://github.com/openchainxyz/ethereum-transaction-viewer-frontend

## OPEN QUESTIONS FOR OWNER (researcher)
- Какой размер графа реально должен быть на экране одновременно: типично десятки–сотни узлов со свёрнутыми ветвями или обязательно все 10 000 сразу? От этого зависит, нужен ли WebGL-режим и запасной рендерер.
- На каком железе работают следователи (ноутбуки со встроенной графикой?) — это задаёт пороги приёмки FPS.
- Обязателен ли векторный SVG-экспорт, или для PDF достаточно PNG высокого разрешения плюс таблица TXID?
- Есть ли бюджет на коммерческий SDK (GoJS от $3 995 разово, KeyLines/Ogma по запросу), если benchmark-spike покажет, что open-source не выдерживает целевой масштаб?
- Согласны ли перевести dev-окружение с Node 23.4.0 (EOL с 2025-06-01) на Node 24 LTS в Docker?
- На чём пишется бэкенд (FastAPI?) и будет ли OpenAPI-схема — от этого зависит генерация типизированного клиента.
- Можно ли на единственном сервере держать headless-браузер для серверного рендера PDF, или PDF собирается иначе?
- Нужны ли публичные SEO-страницы в том же приложении (тогда потребуется отдельный статический сайт или SSR)?
- Нужны ли в MVP совместная работа над графом, сохранение ручной расстановки узлов и аннотации следователя?
- Языки интерфейса и отчёта (русский/английский) — закладывать ли i18n с первого дня?

## NOT VERIFIED (researcher)
- Реальная производительность (FPS, время первого кадра) любой библиотеки на 1 000 / 10 000 узлов на целевом железе: сторонний код не запускался, все оценки — из документации и issue.
- Актуальные ограничения WebGL-режима Cytoscape в 3.34.3: список ограничений взят из блога про 3.31 (2025-01), часть могла быть исправлена; работа cy.png() при webgl:true не проверена.
- Стабильность Sigma v4 в продакшене и сроки поддержки v4 в react-sigma.
- Цены Ogma, KeyLines/ReGraph, KronoGraph, Cosmograph Business, GoJS Enterprise — не публикуются.
- Условия SaaS/доменов/водяного знака для GoJS и точные SaaS-условия yFiles (тексты лицензионных соглашений полностью не читались).
- Годовые цены React Flow Pro (на странице виден только помесячный тариф).
- Разрешено ли встраивание Graphistry в коммерческий SaaS (EULA не читалась).
- Числа из статьи Springer «Graph visualization efficiency of popular web-based libraries» (2025): страница ушла в редирект на авторизацию, текст не получен.
- Возможности ECharts graph, AntV X6, JointJS, maxGraph, deck.gl, Graphviz-WASM — глубоко не аудировались, проверены только метаданные.
- Возможности G6 v5 по рендерерам SVG/WebGL и полный список layout в @antv/layout 2.0 — по дереву исходников видны только плагины, behaviors и типы элементов.
- Технические возможности GoJS, yFiles, KeyLines (layout, экспорт, time bar) — только по маркетинговым страницам, SDK не оценивались.
- Юридические последствия включения elkjs (EPL-2.0) в минифицированный бандл закрытого SaaS — нужна оценка юриста.
- Поддержка TRON/TRC20 в GraphSense Dashboard — видно только упоминание ключа trx в примерах CLI graphsense-lib.
- Качество векторного вывода cytoscape-pdf-export 0.0.5.
- Детали CVE-2025-55182 (React Server Components) — только по вторичным источникам из веб-поиска; первичные advisory React/Next.js не открывались.