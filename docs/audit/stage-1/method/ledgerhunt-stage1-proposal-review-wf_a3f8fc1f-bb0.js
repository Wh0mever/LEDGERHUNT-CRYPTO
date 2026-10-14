export const meta = {
  name: 'ledgerhunt-stage1-proposal-review',
  description: 'Four independent reviewers check the assembled stack proposal: owner-format compliance, internal consistency, measurability and budget, cold-reader clarity and safety',
  phases: [{ title: 'Review', detail: 'four lenses over the full document' }],
}

const DOC = 'C:/LEDGERHUNT CRYPTO/docs/stage-1-stack-proposal.md'

const COMMON = [
  'You are reviewing a decision document before it goes to the owners of LEDGERHUNT-CRYPTO (a platform for automated investigation of cryptocurrency thefts; MVP: USDT TRC20 on TRON). The document is the Stage 1 deliverable: a technology-stack proposal the owners must approve before any development starts. It is written in Russian.',
  '',
  'THE DOCUMENT: ' + DOC + ' (about 1,510 lines). Read ALL of it with the Read tool in consecutive pages of about 300 lines (offset/limit) until the end; do not skip pages. Part A is the summary written by the lead engineer; Part B has 14 detailed sections, each already fact-checked against an audit dossier. Do not do web research, do not run code, do not edit any file: your output is a list of issues.',
  '',
  'HOW TO REPORT: return at most 25 issues, most important first. For each: the location (section number or Part A subsection, plus a verbatim quote of up to 150 characters from the document so the editor can find it), severity (blocker = would mislead the owners or breaks an owner requirement; major = a real inconsistency or gap; minor = wording or polish), the problem in one or two sentences, and a concrete fix - where possible the exact replacement Russian text. Do not report matters of taste. Do not pad the list: if the document is fine on your lens, return few issues. Also return a short overall verdict.',
].join('\n')

const LENSES = [
  {
    key: 'owner-format',
    prompt: [
      'YOUR LENS: compliance with the owner brief ("Prompt 0").',
      'The brief requires, for EACH platform need, all seven items: (1) the chosen solution and why; (2) at least two alternatives and why each was rejected; (3) licence and whether commercial use is allowed; (4) project state (support, tests, maturity) and discrepancies found between claimed and real; (5) infrastructure requirements and expected costs including paid API requests; (6) limitations, risks and how data quality will be verified; (7) how easily the solution can be replaced later.',
      'The needs that MUST be covered: (a) TRON blockchain data sources for USDT TRC20 - transactions, token transfers, balances, timestamps, contracts - preferably several independent sources for cross-checking; (b) address-label sources (exchanges, exchangers, bridges, services) and risk data, including commercial analytics services if terms and prices allow; (c) ready-made blockchain analytics / tracing platforms or engines usable as a base or prototype; (d) an AI-agent orchestration framework or a justified custom orchestrator; (e) language models with tool calling and structured outputs; (f) graph storage and graph-analysis tools including machine learning on graphs; (g) relational storage for users, investigations, events, reports; (h) queues and background execution of long tasks; (i) web interface and an interactive graph-visualisation library; (j) backend and API; (k) a mechanism for connecting external tools to agents; (l) report generation in JSON and PDF; (m) deployment, monitoring, centralised logs, backup, secure secret storage.',
      'The brief also sets always-on principles: only public and lawfully obtained data; seed phrases, private keys and wallet access are never requested; every substantial conclusion is backed by primary data (TXID, source) or explicitly marked as a hypothesis; experimental functions are isolated from the verified contour and compared with a deterministic baseline; when data is unavailable the system reports the limitation and invents nothing. And the strategy: do not build from scratch what already exists.',
      'CHECK: every need (a)-(m) is covered and each of the seven items is present AND substantive (not a placeholder) in its section; each section names at least two real alternatives with concrete rejection reasons; sub-needs are not silently dropped (for example balances and contracts under (a), users and reports under (g), centralised logs and backup under (m), ML on graphs under (f)); the always-on principles are reflected in the design and nothing in the document contradicts them; where the proposal builds its own component instead of reusing one, the justification is explicit. Report gaps.',
    ].join('\n'),
  },
  {
    key: 'consistency',
    prompt: [
      'YOUR LENS: internal consistency.',
      'CHECK across Part A and all 14 sections of Part B: the same price, limit, version, date, licence or count must not appear with different values in different places; the status of each choice (accepted / conditional) in table A1 must match the "Решение" paragraph of its section; the cross-cutting decisions G1-G15 in A4 must match what the sections actually say (flag every section sentence that contradicts a G decision, and every G decision that a section contradicts with facts); the cost tables in A5 must match the cost subsections of the sections; the Stage 2 checks in A8 must cover the checks the sections list under "Что проверить до фиксации выбора" (flag important section-level checks missing from A8); cross-references to section numbers must point to the right section; the same thing must be called by the same name throughout (flag confusing synonym drift for key terms). Also flag any statement in Part A presented as established fact that the corresponding section marks as "не проверено" or "не измерено".',
      'For each inconsistency say which side is more likely right and why (the sections were fact-checked against audit dossiers; Part A was written afterwards).',
    ].join('\n'),
  },
  {
    key: 'measurability',
    prompt: [
      'YOUR LENS: measurability, feasibility and budget arithmetic against the owner success criteria ("Prompt 3").',
      'The owner criteria (the system must be designed so each is automatically measurable): (1) Data: 100% of transactional facts in a report are backed by a TXID and available primary data; at least 99% successful retrieval for supported and available test transactions; 100% of evidence links lead to existing transactions or verifiable sources; 0 unconfirmed claims presented as facts. (2) Tracing: at least 95% of prepared test scenarios with known history handled within the set depth; all known routes in control scenarios found; at least 10 consecutive hops with configurable depth; correct handling of fan-outs, merges and repeated addresses without duplicate transactions; for mixed flows the uncertainty of origin is stated explicitly. (3) Performance on a test server with fixed hardware and sources: simple transaction up to 30 seconds; first report for a few dozen addresses up to 2 minutes; a 1,000-unique-address graph up to 5 minutes; at least 95% of completed tasks within the limit; time measured from task start to verified result, with waiting on external sources recorded separately. (4) Exchange/service identification: at least 95% accuracy on an independent labelled test set; source, check date and confidence stored for every classification; unknown addresses not classified as exchanges on indirect similarity; a separate evidence package for a potential exchange. (5) AI agents: at least 90% of substantial agent conclusions carry references or an explicit hypothesis mark; at least 95% of runs end with a correct structured report or a clear error message; every agent action logged with tools and results; no agent declares money recovered, an owner identified or an exchange confirmed without evidence; AI components show measurable improvement in speed or completeness over the baseline on the same test set. (6) Cost: every investigation cost is measured including AI tokens, external APIs, compute and storage; standard scenario budget at most $1; configurable limits of spend, depth and requests for large investigations; on reaching the limit expensive operations pause and results are kept. (7) Usefulness: launch by TXID or address without reading code; the report automatically contains timeline, graph, significant addresses and evidence links; a list of next actions with required documents and potential recipients; an independent specialist can reproduce the main conclusions without access to closed platform data. (8) Security: no seed phrases or private keys; API keys in protected configuration and never in reports or logs; agent actions affecting external systems need permissions and control; when a source is unavailable the limitation is reported. (9) Test plan: at least 50 scenarios (direct transfers, fan-outs, merges, long chains, repeated addresses, known deposit addresses, incomplete data) with known expected results; final evaluation on a separate held-out set.',
      'CHECK: for every criterion above, does the proposal say how it will be met AND how it will be automatically measured (which component records the number)? Flag criteria that are missing, hand-waved, or silently redefined (for example a target moved outside the measured interval without telling the owners plainly). Check all arithmetic in the cost tables of Part A (sums, per-investigation totals, request counts versus quotas, whether the stated caps really keep a standard investigation at or under $1 in the worst case the document itself describes). Flag any place where the document promises or implies something it also says is unmeasured, and any Stage 2 check that has no pass criterion although one is obviously needed. Flag feasibility risks the document ignores (for example components whose combined memory cannot fit the stated server, or a time budget that the listed steps cannot fit even on paper).',
    ].join('\n'),
  },
  {
    key: 'reader-safety',
    prompt: [
      'YOUR LENS: the cold reader, and safety of claims.',
      'The reader is a technically literate owner who has NOT seen the audit, reads Russian, and will decide from Part A, dipping into Part B. They are switching in from other work.',
      'CHECK Part A closely and Part B more lightly: (1) terms, abbreviations and internal labels used before they are explained or never explained (flag only the ones a technical owner would plausibly stumble on, and propose the explanation); (2) sentences that are hard to follow, over-compressed, or that hide the point; places where the conclusion or the decision requested is not stated first; (3) hype, filler, hedging stacked on hedging, or false confidence; (4) questions to the owners in A7 that cannot be answered as asked (too vague, two questions in one, missing the default the engineer recommends); (5) anything a reader could take as a promise of recovering stolen funds, as an accusation against a named person or organisation, or as an instruction to collect personal data about individuals; (6) third-party projects, repositories or companies described as malicious, fraudulent or unsafe: is each such statement hedged to what was actually observed, and is naming them necessary; (7) statements about what a law, licence or terms of service allows that read as legal advice rather than as an engineer reading that needs a lawyer; (8) leftovers of the drafting process visible to the reader (internal file paths, references to "dossier", "verifier", "researcher", "audit agent", drafting notes, English fragments that should be Russian, placeholder text).',
      'Propose exact replacement text for each issue in Part A.',
    ].join('\n'),
  },
]

const SCHEMA = {
  type: 'object',
  properties: {
    verdict: { type: 'string', description: 'two to four sentences: is the document fit to send to the owners on this lens, and what is the single most important fix' },
    issues: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          location: { type: 'string' },
          quote: { type: 'string', description: 'verbatim text from the document, up to 150 characters' },
          severity: { type: 'string', enum: ['blocker', 'major', 'minor'] },
          problem: { type: 'string' },
          fix: { type: 'string', description: 'concrete fix; exact replacement Russian text where possible' },
        },
        required: ['location', 'quote', 'severity', 'problem', 'fix'],
      },
    },
  },
  required: ['verdict', 'issues'],
}

phase('Review')
const out = await parallel(
  LENSES.map((l) => () =>
    agent(COMMON + '\n\n' + l.prompt, { label: 'review:' + l.key, phase: 'Review', schema: SCHEMA }).then((r) => ({ lens: l.key, result: r }))
  )
)
const ok = out.filter(Boolean).filter((x) => x.result)
const failed = LENSES.map((l) => l.key).filter((k) => !ok.find((x) => x.lens === k))
if (failed.length) log('REVIEW LENSES FAILED: ' + failed.join(', '))
return { reviews: ok, failed }
