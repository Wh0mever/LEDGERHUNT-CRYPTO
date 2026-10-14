export const meta = {
  name: 'ledgerhunt-stage1-apply-review',
  description: 'Section editors apply the reviewer findings to the 14 detailed sections of the stack proposal',
  phases: [{ title: 'Edit', detail: 'one editor per area applies the relevant review issues and the resolved cross-cutting decisions' }],
}

const SP = 'C:/Users/Asus/AppData/Local/Temp/claude/C--LEDGERHUNT-CRYPTO/912b2cf7-a304-454a-a85d-20eefb54cc33/scratchpad/'

const AREAS = [
  { key: 'tron-data', sections: [1] },
  { key: 'labels-risk', sections: [2] },
  { key: 'tracing-engines', sections: [3] },
  { key: 'agent-orchestration', sections: [4, 11] },
  { key: 'llm-models', sections: [5] },
  { key: 'graph-store', sections: [6] },
  { key: 'backend-db-queue', sections: [7, 8, 10] },
  { key: 'frontend-graph-viz', sections: [9] },
  { key: 'reports-devops', sections: [12, 13] },
  { key: 'osint-recovery', sections: [14] },
]

const G_FINAL = [
  'G1. Серверная часть — Python 3.13: API, воркеры, трассировщик, агенты. TypeScript — только веб-интерфейс.',
  'G2. Один PostgreSQL 18 — единственная СУБД MVP: данные приложения, графовые таблицы, журнал событий и системные таблицы очереди в отдельной схеме и роли. Брокера сообщений в MVP нет.',
  'G3. Оркестрация — собственный детерминированный оркестратор на DBOS Transact (MIT, без платной консоли Conductor). Выбор условный: на Этапе 2 он сравнивается с вариантом без DBOS (свои таблицы и очередь Procrastinate), и если оба проходят проверки, берётся более простой. Решения модели по умолчанию идут без инструментов: данные заранее собирает код.',
  'G4. Внешние источники подключаются как типизированные функции в процессе через единый HTTP-шлюз: общий ограничитель запросов на провайдера, хранилище сырых ответов как доказательств, вырезание ключей. В MVP ограничитель работает внутри шлюза в единственном процессе воркера. MCP — необязательный адаптер на границе.',
  'G5. Данные TRON: TronGrid v1 — основной источник истории, событий и internal transactions; независимый оператор узла (Chainstack: бесплатный план для разработки, Growth $49/мес для production) — квитанции транзакций (receipt) и constant calls, включая итоговый isBlackListed. PublicNode — резерв без ключа только для разработки, пока его условия не подтверждены письменно; резерв production — второй платный оператор узла (GetBlock или Nodit) после чтения его условий. TronScan вне критического пути, его теги не хранятся до письменного согласия: по нашему прочтению, Terms of Service от 2022-01-04 запрещают сторонние приложения; опубликованных условий именно для API не найдено, и не подтверждено, что это действующая редакция, — до ответа TronScan считаем, что запрет действует. Второй независимый индекс «адрес → переводы» выбирается на Этапе 2 (кандидаты — в разделе 1).',
  'G6. Ключ ребра — (chain, txid, event_index). Поле event_index в живых пробах TronGrid присутствует; на Этапе 2 проверяется на выборке не менее 1 000 TXID, что оно есть у всех событий, не меняется при повторном запросе и совпадает с порядковым номером лога в квитанции независимого узла. При провале ключом становится (chain, txid, порядковый номер лога в квитанции). Переводы с нулевой суммой (address poisoning) хранятся отдельным классом и рёбер не создают; строки, не являющиеся Transfer, отбрасываются. Баланс учитывает события DestroyedBlackFunds, Issue и Redeem. Каждое ребро, попавшее в отчёт, подтверждается квитанцией у оператора, отличного от TronGrid; остальные рёбра графа сверяются выборочно.',
  'G7. Метки: собственный Label Store из первичных источников — события blacklist Tether; OFAC SDN (собственный разбор первичного файла по всем тикерным спискам; контрольное значение — 340 адресов TRON по зеркалу 0xB10C на 2026-10-01, из них 337 найдены в первичных файлах); курируемый реестр кошельков бирж из proof-of-reserves; курируемый реестр контрактов обменников и мостов. Платная атрибуция — MistTrack с оплатой за вызов ($0.10–0.20 в зависимости от пакета); лимит по умолчанию — 2 вызова на расследование, настраивается до 4. Эвристика «депозит → сбор на горячий кошелёк» даёт только «кандидата» с достоверностью 0.2–0.3 и никогда метку «биржа».',
  'G8. Ядро трассировки собственное. Четыре методики распределения смешанных средств (FIFO, LIFO, pro-rata, верхняя граница poison) считаются параллельно; какая из них основная в отчёте, задаёт профиль юрисдикции после консультации юриста.',
  'G9. Граф: PostgreSQL и итеративный обход в приложении (не один рекурсивный запрос); аналитика в памяти за интерфейсом GraphEngine. Отдельная графовая СУБД появляется только по итогам сравнительного теста Этапа 2, в который входит ArcadeDB. Наборы данных Elliptic в коммерческом контуре не используются.',
  'G10. Интерфейс: SPA на Vite, React и TypeScript; Cytoscape.js на canvas с жёстким лимитом одновременно видимых элементов, который обеспечивает серверная агрегация; раскладка считается вне потока интерфейса и сохраняется в снимке расследования. Картинку графа для PDF рисует сервер из того же снимка; формат (SVG или PNG) и способ выбирает проверка на Этапе 2 (кандидаты — в разделе 9). Headless Chromium в основном контуре MVP нет; Gotenberg, который его содержит, остаётся запасным движком PDF только по решению владельцев.',
  'G11. Отчёты: модели Pydantic и публикуемая JSON Schema; PDF через WeasyPrint отдельной асинхронной задачей; двухуровневый манифест, подпись Ed25519, метка времени RFC 3161; все суммы — десятичные строки. Пока провайдеры письменно не подтвердили право передавать их ответы клиенту, пакет доказательств для клиента содержит TXID, хеши сырых ответов и манифест, а сами сырые ответы остаются на платформе.',
  'G12. Эксплуатация: Docker Compose на одном сервере, Caddy, GitHub Actions. Минимальная конфигурация — 4 vCPU и 8 GB RAM (OVH VPS-2); рекомендуемая стартовая — 24 GB (OVH VPS-4), окончательно после замера потребления памяти. Замеры производительности ведутся на тарифе с выделенными ядрами. Резервные копии, наблюдаемость и секреты — раздел 13.',
  'G13. Модели: Anthropic Claude — основной провайдер. Haiku 5.5 — модель по умолчанию; Sonnet 5.5 — планирование при неоднозначности и короткие текстовые секции отчёта; тело отчёта собирает детерминированный шаблон. OpenAI — запасной провайдер, включается после чтения договора. Единственный путь к моделям — собственный интерфейс LLMClient с учётом стоимости и журналом; под ним — Pydantic AI либо официальные SDK, выбор делает проверка Этапа 2. Готовая интеграция Pydantic AI с DBOS не используется: один запрос к модели оформляется обычным сохраняемым шагом. Интерфейс просмотра журнала вызовов моделей — раздел 5.',
  'G14. Вход: серверная часть — стандартный OIDC resource server, поставщик входа заменяем. По документации Keycloak требует 1.25–1.36 GB памяти; поместится ли он на сервер с 8 GB рядом с базой, воркером и мониторингом, не измерено. Поэтому Keycloak рекомендуется при 16 GB и более, при 8 GB — Logto, ZITADEL или внешний сервис после пробы на Этапе 2.',
  'G15. OSINT работает в режиме «адреса и организации, не люди». Веб-поиск идёт через собственный сменный адаптер (Tavily или Brave, выбирают владельцы); встроенный поиск провайдера моделей не используется. Платформа никогда не обещает возврат средств.',
  'G16. Платформа никогда не запрашивает seed-фразы, приватные ключи и доступ к кошельку: таких полей нет в интерфейсе, API и шаблонах писем. Входной фильтр проверяет текст пользователя и текст, извлечённый из вложений, до сохранения и до передачи моделям и поисковым провайдерам. Все инструменты только читают данные; подписи и отправки транзакций в системе нет.',
  'G17. Бюджет расследования: лимиты по статьям (модели $0.40; платные метки 2 вызова, до $0.40; поиск 10 запросов; одна метка времени) и общий жёсткий лимит $1.00 поверх них. Учёт работает как резервирование: до отправки платного вызова резервируется его максимальная стоимость, после ответа резерв заменяется фактом. При 70% лимита моделей остаётся только Haiku 5.5; при 100% отчёт выпускается без текста модели; при общем лимите — пауза с сохранением результатов. Постоянные затраты, не зависящие от отдельного расследования (подписка на узел, сервер), по условию Промпта 3 в $1 не входят; вычисления и хранение измеряются по каждому расследованию.',
].join('\n')

const RESOLVED = [
  'RESOLVED FACTS AND DECISIONS (use these exact values wherever the topic appears in your sections, so that all sections and Part A agree):',
  'R1. Request count for a 1,000-address graph (calculation, not measured): 6-10 thousand requests in total. To TronGrid: from about 3 300 (if the event index can be taken from the node receipt) up to 6-7 thousand (if every edge needs its own TronGrid events request). The free daily quota of 100 000 requests then covers 14-30 such graphs a day, and the required average rate over 5 minutes is 11-24 requests per second.',
  'R2. Model cost per standard investigation (estimates, not measured): $0.40 typical and $0.57 heavy for the routing scheme of G13 (106 and 158 calls, section 5); $0.05-0.30 belongs to the narrower scheme "Sonnet only on escalations" (25 calls, section 4). Both schemes are measured in Stage 2. The default model limit is $0.40 (G17). Sonnet 5.5 on all steps with a tool loop: $0.55 x 2-4 requests x 1.3 tokens = about $1.4-2.9.',
  'R3. MistTrack: Terms of Use dated 2026-10-09 were read (section 2). By our reading they allow client reports, commercial investigations and caching, forbid resale as a standalone data product, and a business-model review (KYB / Commercial Use Review) is possible before commercial use; written confirmation is still needed. Price per address_labels call: $0.20 on the $20 pack, $0.15 on the $150 pack, $0.10 on the $1 000 pack. Default 2 calls per investigation (up to $0.40), configurable up to 4 (up to $0.80).',
  'R4. Label test set: independent, first version 400-500 addresses, target 600+ (section 2 is authoritative; other sections refer to it). 10-30 own deposit addresses are realistic; they cannot prove 95% with margin (30 of 30 gives a Wilson lower bound of 88.6%).',
  'R5. Scenario sets: the ">= 50 scenarios with an exactly known answer" count only (a) synthetic scenarios on recorded API responses and (b) scenarios created by our own transfers on the main network. Freeze-anchored cases (OFAC, Tether blacklist events), public incidents and reliability / crash tests are separate classes and are NOT inside the 50.',
  'R6. Arkham: the site arkm.com did not open from the audit network; prices were read from arkm.com/llms.txt (section 3); commercial-use and caching terms were not found.',
  'R7. Keyless TronGrid was measured: 3 requests per second, then HTTP 429 and a 5-second pause (section 1). RemovedBlackList and DestroyedBlackFunds events were returned live in the probes of sections 1-3.',
  'R8. Licences verified on 2026-10-14 through the GitHub API: uvicorn BSD-3-Clause; Pydantic MIT; TanStack Router MIT; zustand MIT; React MIT; TypeScript Apache-2.0; Vite MIT.',
  'R9. Title of section 14 becomes: "Источники OSINT и адресаты обращений о заморозке и возврате (дополнительно к 13 потребностям)". Wording: for the victim, recovery goes through law enforcement (not "only through law enforcement" as an absolute): TRM Beacon Network claims access for vetted security companies (conditions not verified), the Tether portal cs.tether.to was not read. T3 FCU is not entered into the recipients directory until its domain is confirmed.',
  'R10. The measured interval for the 30 s / 2 min / 5 min targets runs from task start to the verified JSON report shown in the UI; PDF rendering, signature and timestamp are a separate asynchronous task with its own target (owners decide). Only solidified data go into a report; they lag the chain by 18-19 blocks (54-57 s), so for a transaction younger than about a minute the wait for network confirmation is recorded separately as waiting on an external source.',
  'R11. Acceptance of the performance criterion is ONE end-to-end measurement on the test server with real sources; the checks inside individual sections (source load run, queue spike, graph-layer benchmark) are component budgets, not acceptance.',
].join('\n')

const VOCAB = [
  'VOCABULARY AND STYLE RULES (apply to every line you touch and fix existing violations in your sections):',
  'V1. The reader is an owner who has not seen the audit. Use only two process terms: «первичное исследование» (first-pass research) and «перепроверка» (independent re-check). Remove «досье», «исследователь», «верификатор» (as a process word), «проверяющий», «аудит этой области», «исходный аудит», «первичный аудит», «лимит веб-поиска закончился» and similar drafting narration; keep such a remark only if it changes a decision, rephrased with the two terms. The platform component is called «модуль проверки доказательств».',
  'V2. «не измерено» / «не проверено» must agree grammatically with the subject («скорость и память не измерены»).',
  'V3. The «Решение» paragraph and running prose are in Russian: основной провайдер, запасной провайдер, сильная модель, шлюз моделей, оценка качества, проверочная реализация (spike), базовый алгоритм (baseline), известный правильный ответ (ground truth), поставщик входа (IdP), служба меток времени (TSA), подтверждение человеком. Product names, licence names, API paths, code identifiers and model ids stay in English. Spell consistently: TronScan, чекпойнт.',
  'V4. Licence and terms-of-use statements are an engineer reading, not legal advice: phrase conclusions about LGPL / AGPL / proprietary terms with «по нашему прочтению». For MIT write «разрешено; условие MIT — сохранять уведомление об авторских правах и текст лицензии» instead of «разрешено без условий».',
  'V5. Negative statements about third-party projects, companies or repositories are limited to what was actually observed and say how it was observed. For the two repositories flagged in section 3 write «с признаками вредоносного кода; код не исполнялся, вывод предварительный» and keep their names only in the deny-list sentence.',
  'V6. Interface names are TransferSource and LabelSource everywhere.',
  'V7. A reference to a decision code (G1-G17) must point to a decision that really contains the thing referred to (the final text of all decisions is given below); otherwise refer to the section number.',
  'V8. Thousands separator is a space (1 000), decimal separator is a point ($0.40). Introduce any name the reader cannot know in one short clause or remove it.',
  'V9. Keep the template headings and their order exactly. Keep each section under about 13 000 characters: when you add required content, trim repetition elsewhere in the same section.',
].join('\n')

const SCHEMA = {
  type: 'object',
  properties: {
    sections: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          number: { type: 'integer' },
          markdown: { type: 'string', description: 'the full corrected section text, starting with its "## N. Title" heading' },
        },
        required: ['number', 'markdown'],
      },
    },
    applied: { type: 'array', items: { type: 'string' }, description: 'issue ids applied, each with 3-10 words on what changed, e.g. "[24] request-count range unified"' },
    declined: { type: 'array', items: { type: 'string' }, description: 'issue ids not applied in your sections and why (e.g. concerns Part A only, or the proposed text contradicts the dossier)' },
    notes_for_lead: { type: 'array', items: { type: 'string' }, description: 'anything the lead engineer must reconcile in Part A, max 6' },
  },
  required: ['sections', 'applied', 'declined', 'notes_for_lead'],
}

function prompt(a) {
  const files = a.sections.map((n) => SP + 'sections/' + (n < 10 ? '0' + n : '' + n) + '.md').join(', ')
  return [
    'You are the editor of part of a decision document for the owners of LEDGERHUNT-CRYPTO (a platform for automated investigation of cryptocurrency thefts; MVP: USDT TRC20 on TRON). The document is the Stage 1 stack proposal, written in Russian. Four reviewers found problems; the lead engineer has resolved the cross-cutting questions. Your job is to produce the corrected final text of your section(s).',
    '',
    'YOUR SECTIONS: ' + a.sections.join(', ') + '. Read the current text of each in full: ' + files + '.',
    'REVIEW ISSUES for your sections: ' + SP + 'issues/' + a.key + '.md (read all of it). Each issue has a location, a quote, the problem and a proposed fix. Many issues touch several sections or Part A: apply only what concerns YOUR sections; Part A is edited by the lead engineer.',
    'FACT SOURCE: ' + SP + 'full/' + a.key + '.md is the audit dossier for your area (PART 1, the adversarial re-check, takes precedence over PART 2). Consult it whenever you add or change a fact, number, licence, price, version or date, to make sure the new text is supported. Read the parts you need; you do not have to re-read all of it.',
    '',
    'HOW TO WORK:',
    '1. Apply every issue that concerns your sections. Use the reviewer proposed text as a starting point, not as gospel: where a proposed replacement contains a bracketed placeholder or a fact you cannot support from the dossier or from the resolved list below, write the supported version instead (or mark the item «не проверено») and say so in notes_for_lead.',
    '2. Where an issue conflicts with the RESOLVED list or the final decisions G1-G17 below, the RESOLVED list and the decisions win.',
    '3. Reviewers asked for some content to be added (for example: where balances, timestamps and contract data come from in section 1; the registry of exchanger and bridge contracts as a label source in section 2; the reason for the graph-ML choice and a Raphtory row in section 6; where users and reports are stored in section 7; the reservation mechanism of the budget ledger in section 4; the two-step rollout of observability and the measurement protocol in section 13). Add it as a design statement, concisely, without inventing third-party facts.',
    '4. Do not introduce any new third-party fact, price, version, licence or URL that is absent from the dossier, the current section text or the resolved list. Do not do web research and do not run code. Do not write files.',
    '5. Leave untouched whatever is not affected. Return the FULL text of each section, not a diff.',
    '',
    RESOLVED,
    '',
    VOCAB,
    '',
    'FINAL TEXT OF THE CROSS-CUTTING DECISIONS (Part A, A4) - for consistency and for checking references:',
    G_FINAL,
  ].join('\n')
}

phase('Edit')
const out = await parallel(
  AREAS.map((a) => () => agent(prompt(a), { label: 'edit:' + a.key, phase: 'Edit', schema: SCHEMA }).then((r) => ({ key: a.key, expected: a.sections, result: r })))
)
const ok = out.filter(Boolean).filter((x) => x.result)
const failed = AREAS.map((a) => a.key).filter((k) => !ok.find((x) => x.key === k))
if (failed.length) log('EDITORS FAILED: ' + failed.join(', '))
return { areas: ok, failed }
