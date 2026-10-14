export const meta = {
  name: 'ledgerhunt-stage1-draft-sections',
  description: 'Draft the stack-proposal sections per area from the verified audit dossiers, then fidelity-check each against its dossier',
  phases: [
    { title: 'Draft', detail: 'one writer per area turns the audit dossier into proposal sections (Prompt 0 format)' },
    { title: 'Fidelity', detail: 'independent editor checks every fact in the draft against the dossier and fixes it' },
  ],
}

const DIR = 'C:/Users/Asus/AppData/Local/Temp/claude/C--LEDGERHUNT-CRYPTO/912b2cf7-a304-454a-a85d-20eefb54cc33/scratchpad/full/'

const AREAS = [
  { key: 'tron-data', lines: 994, sections: [{ n: 1, title: 'Источники данных блокчейна TRON для USDT (TRC20)' }] },
  { key: 'labels-risk', lines: 1007, sections: [{ n: 2, title: 'Метки адресов и данные о рисках' }] },
  { key: 'tracing-engines', lines: 1006, sections: [{ n: 3, title: 'Готовые платформы и движки блокчейн-аналитики и трассировки' }] },
  { key: 'agent-orchestration', lines: 1073, sections: [{ n: 4, title: 'Оркестрация AI-агентов' }, { n: 11, title: 'Механизм подключения внешних инструментов к агентам' }] },
  { key: 'llm-models', lines: 930, sections: [{ n: 5, title: 'Языковые модели, наблюдаемость и оценка качества AI-слоя' }] },
  { key: 'graph-store', lines: 1272, sections: [{ n: 6, title: 'Графовое хранилище, графовый анализ и машинное обучение на графах' }] },
  { key: 'backend-db-queue', lines: 1723, sections: [{ n: 7, title: 'Реляционное хранилище' }, { n: 8, title: 'Очереди и фоновое выполнение длительных задач' }, { n: 10, title: 'Серверная часть и API' }] },
  { key: 'frontend-graph-viz', lines: 959, sections: [{ n: 9, title: 'Веб-интерфейс и интерактивная визуализация графа' }] },
  { key: 'reports-devops', lines: 1469, sections: [{ n: 12, title: 'Генерация отчётов в JSON и PDF, целостность доказательств' }, { n: 13, title: 'Развёртывание, мониторинг, журналы, резервное копирование, секреты' }] },
  { key: 'osint-recovery', lines: 1232, sections: [{ n: 14, title: 'Источники OSINT и каналы возврата средств (дополнительно к 13 потребностям)' }] },
]

const GLOBAL = [
  'PROJECT: LEDGERHUNT-CRYPTO, a platform for automated investigation of cryptocurrency thefts; MVP scope is USDT TRC20 on TRON. Today is 2026-10-14. Stage 1 deliverable is a STACK PROPOSAL that the owners must approve before any development starts. You are writing part of that proposal.',
  '',
  'OWNER REQUIREMENTS FOR EVERY NEED (all seven must be present in each section): (1) the chosen solution and why; (2) at least two alternatives and why they were rejected; (3) licence and whether commercial use is allowed; (4) project state (support, tests, maturity) and discrepancies found between claimed and real; (5) infrastructure requirements and expected costs including paid API requests; (6) limitations, risks and how data quality will be verified; (7) how easily the solution can be replaced later.',
  '',
  'MEASURABLE MVP TARGETS: >= 99% retrieval of available transactions; 100% of facts backed by TXID; simple transaction <= 30 s; report for a few dozen addresses <= 2 min; 1,000-address graph <= 5 min; label accuracy >= 95% on an independent labelled set; variable cost <= $1 per standard investigation; >= 50 test scenarios with ground truth; AI must measurably beat the deterministic baseline; full reproducibility; API keys never leak; commercial SaaS use planned; small team; one modest server at the start.',
  '',
  'GLOBAL DECISIONS ALREADY TAKEN ACROSS AREAS (stay consistent with them; if your dossier contradicts one, follow the dossier facts and report the conflict in conflicts_with_global):',
  'G1. Backend language is Python 3.13 (API, workers, tracer, agents); TypeScript is used only for the web UI.',
  'G2. A single PostgreSQL 18 instance is the only database in the MVP: relational data, graph tables (address / transfer / label), event log, and the durable-execution system tables in a separate schema and role. No message broker in the MVP.',
  'G3. Orchestration is our own deterministic orchestrator on DBOS Transact (MIT, without the paid Conductor) plus Pydantic AI for LLM steps at decision points. This choice is CONDITIONAL on a spike in Stage 2; the fallback is Procrastinate plus our own frontier tables. By default LLM decisions run WITHOUT tools (deterministic code gathers data first; one model request = one durable step).',
  'G4. External tools are in-process typed function tools behind one HTTP gateway (per-provider shared token bucket, raw-response evidence store, key redaction). MCP is only an optional adapter at the boundary and a possible future external interface.',
  'G5. TRON data: TronGrid v1 with our own API key is the primary source for TRC20 history, contract events and internal transactions; an independent node operator (Chainstack: free Developer plan for development, Growth $49/month for production) supplies receipts and constant calls for per-fact verification; PublicNode is the keyless reserve. TronScan is NOT in the critical path and its tags are not stored: its 2022 Terms of Service forbid third-party applications without prior written consent, so it becomes optional enrichment only after written consent. A second independent address index for completeness sampling is still to be chosen in Stage 2 (candidates: Blockbook-TRON via NOWNodes, offline SQL cross-checks in Dune or BigQuery). Bitquery self-service plans have no deep history without a paid archive add-on and Coinpath is Enterprise-only.',
  'G6. Edge identity is (chain, txid, event_index) taken from /v1/transactions/{txid}/events; rows with value = 0 (address poisoning) and non-Transfer rows are filtered; the ledger also accounts for DestroyedBlackFunds, Issue and Redeem events.',
  'G7. Labels: our own Label Store built from primary sources (Tether blacklist events on-chain, OFAC SDN: TRX-tagged plus USDT-tagged TRON addresses = 340, a curated registry of exchange proof-of-reserves wallets). Paid attribution in the MVP is MistTrack pay-per-call for 2-4 terminal addresses per investigation; Bitquery labels are only a candidate after measurement. The deposit-sweep heuristic yields only a "candidate" with confidence 0.2-0.3 and never the label "exchange".',
  'G8. Tracing core is our own deterministic baseline tracer (no ready OSS engine is usable as a base; GraphSense is a reference). FIFO, LIFO, pro-rata (haircut) and poison-bound are computed in parallel; the "official" method is a jurisdiction-profile parameter to be agreed with a lawyer.',
  'G9. Graph: PostgreSQL plus an application-level iterative frontier-BFS (not one recursive CTE); in-process analytics with NetworkX + rustworkx + SciPy csgraph / OR-Tools behind a GraphEngine interface; a dedicated graph database only if the Stage 2 benchmark (which must include ArcadeDB) proves the need; PyTorch Geometric only in the isolated experimental contour; Elliptic-family datasets are excluded from the commercial contour (CC BY-NC-ND).',
  'G10. Web UI: Vite + React + TypeScript SPA; Cytoscape.js on canvas with a hard cap on simultaneously visible elements enforced by server-side aggregation; layout computed outside the UI thread and persisted in the investigation snapshot. Sigma.js is only a later alternative. The graph picture for the PDF report is rendered on the server deterministically (candidate: Graphviz dot to SVG; ECharts server-side SVG for charts), to be confirmed by a spike; no headless Chromium in the MVP.',
  'G11. Reports: Pydantic models -> published JSON Schema; WeasyPrint + Jinja2 for PDF (PDF/A-3 with attachments) as an asynchronous task outside the 30 s / 2 min targets; two-level manifest (content-manifest inside the PDF, package-manifest outside) + Ed25519 signature + RFC 3161 timestamp; all amounts are decimal strings.',
  'G12. Operations: Docker Compose on one VPS + Caddy + GitHub Actions; reference server 4 vCPU / 8 GB RAM (performance measurements on a dedicated-core plan), growth path to 16-24 GB; VictoriaLogs + Grafana Alloy + Grafana + GlitchTip first, metrics later; pgBackRest + restic to Backblaze B2; SOPS + age for secrets.',
  'G13. LLM: Anthropic Claude API is primary (claude-haiku-5-5 for routine steps, claude-sonnet-5-5 for planning and the final report, strong tier configurable), OpenAI is the fallback, our own thin LLMClient adapter and no gateway process; the source of truth for traces is our own database plus OpenTelemetry instrumentation; the trace UI is Arize Phoenix on the same server or Langfuse Cloud EU depending on the owner decision about data location; Inspect AI runs evals inside a Linux container.',
  'G14. Auth: the backend is a standard OIDC resource server; the identity provider is chosen by available RAM and jurisdiction (Keycloak at >= 8 GB dedicated headroom, otherwise Logto / ZITADEL or a SaaS IdP).',
  'G15. OSINT works in the mode "addresses and organisations, not people"; the web-search provider (Tavily versus Brave with restricted logging) is an open owner decision. The platform never promises recovery of funds.',
].join('\n')

const FORMAT = [
  'OUTPUT LANGUAGE AND STYLE: Russian. Keep product names, licence names, API paths and technical terms in English. Plain, concrete, businesslike prose for a technical owner who has not seen the audit. No hype, no emojis, no filler, no rhetorical questions. Every number carries its unit and, for prices and limits, the note that it was read on 2026-10-13/14. Anything the audit could not confirm is marked explicitly with the words "не проверено" or "не измерено". Never invent a fact, price, version or URL that is not in the dossier.',
  '',
  'SECTION TEMPLATE (use exactly these subsection headings, in this order):',
  '## {N}. {TITLE}',
  '**Решение.** One to three sentences naming the choice and its status (accepted / conditional on a Stage 2 check).',
  '### Почему выбрано',
  '(3-7 bullets with concrete evidence from the dossier: what was checked and how.)',
  '### Альтернативы и причины отказа',
  '(A markdown table with columns: Вариант | Лицензия / условия | Причина отказа или роль. At least 2 rows, normally 5-9 rows covering the most serious alternatives. One line per row, concrete reason.)',
  '### Лицензия и коммерческое использование',
  '### Состояние проекта и расхождения «заявлено — на деле»',
  '### Инфраструктура и затраты',
  '(Fixed monthly cost and variable cost per standard investigation, separately; what is free only for development.)',
  '### Ограничения и риски',
  '### Как проверяем качество',
  '(Concrete checks, tests and acceptance gates; for data sources, how correctness and completeness are cross-validated.)',
  '### Заменяемость',
  '### Что проверить до фиксации выбора (Этап 2)',
  '(Spikes, measurements and written confirmations that must happen before the choice is final, each with a pass criterion where possible.)',
  '### Источники',
  '(5-12 of the most important primary URLs from the dossier, as a bullet list of bare links with 2-6 words of description each.)',
  '',
  'LENGTH: 7,000-11,000 characters per section. When one area yields several sections, do not repeat the same content across them; cross-reference by section number instead. Sub-needs inside one section (for example ORM, RLS and audit log inside the relational-storage section) are covered inside the same template, not as extra top-level sections.',
].join('\n')

const DRAFT_SCHEMA = {
  type: 'object',
  properties: {
    sections: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          number: { type: 'integer' },
          title: { type: 'string' },
          markdown: { type: 'string', description: 'full section text in Russian markdown starting with the "## N. Title" heading' },
        },
        required: ['number', 'title', 'markdown'],
      },
    },
    summary_rows: {
      type: 'array',
      description: 'one row per section for the master table',
      items: {
        type: 'object',
        properties: {
          number: { type: 'integer' },
          need: { type: 'string' },
          choice: { type: 'string', description: 'max 160 characters' },
          status: { type: 'string', enum: ['accepted', 'conditional'] },
          licence: { type: 'string', description: 'max 80 characters' },
          fixed_cost_per_month: { type: 'string' },
          variable_cost_per_investigation: { type: 'string' },
          replaceability: { type: 'string', description: 'низкая / средняя / высокая plus up to 10 words' },
        },
        required: ['number', 'need', 'choice', 'status', 'licence', 'fixed_cost_per_month', 'variable_cost_per_investigation', 'replaceability'],
      },
    },
    open_questions_for_owner: { type: 'array', items: { type: 'string' }, description: 'decisions only the owners can take, each one sentence, in Russian, most important first, max 6' },
    stage2_gates: { type: 'array', items: { type: 'string' }, description: 'checks that must pass before the choice is final, in Russian, max 8' },
    top_risks: { type: 'array', items: { type: 'string' }, description: 'in Russian, max 6' },
    conflicts_with_global: { type: 'array', items: { type: 'string' } },
  },
  required: ['sections', 'summary_rows', 'open_questions_for_owner', 'stage2_gates', 'top_risks', 'conflicts_with_global'],
}

const FIDELITY_SCHEMA = {
  type: 'object',
  properties: {
    sections: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          number: { type: 'integer' },
          title: { type: 'string' },
          markdown: { type: 'string', description: 'the corrected final section text' },
        },
        required: ['number', 'title', 'markdown'],
      },
    },
    issues_fixed: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          section: { type: 'integer' },
          kind: { type: 'string', enum: ['wrong-fact', 'contradicts-verifier', 'unsupported-claim', 'missing-required-item', 'unverified-presented-as-fact', 'inconsistent-with-global', 'style'] },
          what: { type: 'string' },
        },
        required: ['section', 'kind', 'what'],
      },
    },
    remaining_concerns: { type: 'array', items: { type: 'string' } },
  },
  required: ['sections', 'issues_fixed', 'remaining_concerns'],
}

function dossierNote(a) {
  return 'YOUR DOSSIER: read the WHOLE file ' + DIR + a.key + '.md (' + a.lines + ' lines; read it in consecutive pages with the Read tool using offset and limit of about 350 lines until the end - do not skip pages). PART 1 is the adversarial verifier report and TAKES PRECEDENCE over PART 2 (the original researcher audit) wherever they disagree: use corrected values, drop refuted claims, and where the verifier says a recommendation does not stand, present the verifier suggested change as the decision. Candidates found only by the verifier are legitimate alternatives.'
}

function sectionList(a) {
  return a.sections.map((s) => '## ' + s.n + '. ' + s.title).join('\n')
}

function draftPrompt(a) {
  return [
    GLOBAL,
    '',
    '=== YOUR TASK: write the proposal section(s) below from the audit dossier ===',
    sectionList(a),
    '',
    dossierNote(a),
    'Do not do new web research and do not run code: the dossier is your only source of facts. Do not write any files; return the text through structured output.',
    '',
    FORMAT,
    '',
    'Also return: one summary row per section, the questions only the owners can decide, the Stage 2 gates, the top risks, and any conflict between the dossier and the global decisions.',
  ].join('\n')
}

function fidelityPrompt(a, draft) {
  return [
    GLOBAL,
    '',
    '=== YOUR ROLE: FIDELITY EDITOR for the section(s) below ===',
    sectionList(a),
    '',
    'A writer drafted these sections from an audit dossier. Your job is to make sure the owners are not misled. Assume the draft contains errors.',
    dossierNote(a),
    '',
    'CHECK AND FIX, line by line:',
    '1. Every number, price, limit, version, date, licence name and commercial-use statement in the draft must match the dossier, with the verifier (PART 1) winning over the researcher (PART 2). Fix mismatches.',
    '2. Nothing refuted by the verifier may survive; nothing the dossier lists as not verified or not measured may be presented as an established fact - mark it "не проверено" / "не измерено".',
    '3. No fact, URL, price or version may appear that is absent from the dossier. Remove or soften unsupported claims.',
    '4. All seven owner-required items are present for each section, with at least two rejected alternatives carrying concrete reasons, and the template headings are intact and in order.',
    '5. The section is consistent with the global decisions; where the dossier facts contradict a global decision, keep the facts and say so plainly in the section.',
    '6. Style: plain businesslike Russian, no hype, no emojis; trim repetition; keep the section within about 7,000-11,000 characters.',
    'Do not do new web research and do not run code. Do not write files. Return the corrected final text of every section (full text, not a diff) and the list of issues you fixed.',
    '',
    FORMAT,
    '',
    'THE DRAFT (JSON):',
    JSON.stringify(draft.sections),
  ].join('\n')
}

const results = await pipeline(
  AREAS,
  (a) => agent(draftPrompt(a), { label: 'draft:' + a.key, phase: 'Draft', schema: DRAFT_SCHEMA }),
  async (draft, a) => {
    if (!draft) {
      log('draft FAILED for ' + a.key)
      return { key: a.key, draft: null, final: null }
    }
    log('draft done: ' + a.key + ' (' + draft.sections.map((s) => s.markdown.length).join('+') + ' chars) -> fidelity check')
    const final = await agent(fidelityPrompt(a, draft), { label: 'fidelity:' + a.key, phase: 'Fidelity', schema: FIDELITY_SCHEMA })
    if (!final) log('fidelity check FAILED for ' + a.key + ' - draft kept unverified')
    else log('fidelity done: ' + a.key + ' (' + final.issues_fixed.length + ' issues fixed)')
    return { key: a.key, draft, final }
  }
)

const done = results.filter(Boolean)
return {
  areas: done,
  failed_drafts: AREAS.filter((a) => !done.find((r) => r.key === a.key && r.draft)).map((a) => a.key),
  unchecked: done.filter((r) => r.draft && !r.final).map((r) => r.key),
}
