export const meta = {
  name: 'ledgerhunt-stage1-final-check',
  description: 'Final check of the revised stack proposal: regression against earlier review findings, fresh consistency and arithmetic, cold read of the summary',
  phases: [{ title: 'Final check', detail: 'three independent checkers; only remaining blocker and major issues are reported' }],
}

const DOC = 'C:/LEDGERHUNT CRYPTO/docs/stage-1-stack-proposal.md'
const PREV = 'C:/Users/Asus/AppData/Local/Temp/claude/C--LEDGERHUNT-CRYPTO/912b2cf7-a304-454a-a85d-20eefb54cc33/scratchpad/review.md'

const COMMON = [
  'You are doing the FINAL check of a decision document before it goes to the owners of LEDGERHUNT-CRYPTO (a platform for automated investigation of cryptocurrency thefts; MVP: USDT TRC20 on TRON). It is the Stage 1 technology-stack proposal, written in Russian, which the owners must approve before development starts. The document has already been reviewed once and revised.',
  'THE DOCUMENT: ' + DOC + ' (about 1,590 lines). Read it with the Read tool in consecutive pages of about 300 lines. Part A (summary, subsections A1-A10, decisions G1-G17) was rewritten by the lead engineer after the first review; Part B has 14 detailed sections revised by editors.',
  'Do not do web research, do not run code, do not edit any file. Report ONLY issues that are blocker (would mislead the owners, breaks an owner requirement, or an arithmetic or factual contradiction on a number the owners act on) or major (a real inconsistency between two places, a broken reference, an owner question that cannot be answered as asked). Do not report minor wording or taste. At most 15 issues, most important first. For each give: location, a verbatim quote of up to 150 characters, the problem, and the exact replacement Russian text. If you find nothing at these levels, return an empty list - that is a valid and useful result.',
].join('\n')

const LENSES = [
  {
    key: 'regression',
    prompt: [
      'YOUR LENS: regression against the first review.',
      'The first review findings are in ' + PREV + ' (about 820 lines; read all of it). It lists 98 issues from four reviewers with severity, location, problem and proposed fix. The lead engineer resolved cross-cutting questions as follows, and these resolutions take precedence over individual proposed fixes: default model limit $0.40 (not $0.45) and an overall hard limit of $1.00 with reservation (G17); request count for a 1,000-address graph stated as a range (about 3 300 to 6-7 thousand TronGrid requests, 14-30 graphs a day, 11-24 requests per second); a single LLMClient interface with the implementation under it decided at Stage 2 (G13); label test set 400-500 addresses first version, 600+ target; freeze-anchored cases and reliability tests outside the 50 scenarios; PublicNode only in development (G5); raw provider responses not handed to clients until written confirmation (G11); a new decision G16 on seed phrases; the questions in A7 renumbered (1-9 block Stage 2).',
      'TASK: read the whole current document; then for every BLOCKER and MAJOR issue of the first review decide whether it is now resolved in the current text. Report only those that are still unresolved or only partly resolved in a way that still matters, and any NEW contradiction the revision introduced (for example a section still using an old number, an old question number, an old term, or a reference to a decision that no longer says that).',
    ].join('\n'),
  },
  {
    key: 'consistency-arithmetic',
    prompt: [
      'YOUR LENS: fresh consistency and arithmetic, without looking at any earlier review.',
      'CHECK: (1) every number that appears both in Part A and in a section, or in two sections, agrees: prices, limits, request counts, quotas, versions, dates, licence names, counts of addresses or scenarios, memory figures; (2) all sums and derived figures in A5 are arithmetically right (fixed-cost totals per column given the rows; sum of per-item limits; the per-investigation share of fixed costs; the Anthropic monthly cap statement; one-off Stage 2 total) and the time allocations in A6 add up to their targets; (3) each decision G1-G17 in A4 agrees with what the sections say, and every reference to a G code or to a section number or to an A7 question number in the text points at something that really says that; (4) the status in table A1 matches the status in the "Решение" paragraph of each section; (5) the Stage 2 table in A8 does not contradict the Stage 2 lists at the end of the sections (criteria, thresholds, what happens on failure); (6) the same thing is not promised in one place and marked as not measured or not verified in another.',
      'For each issue say which side is more likely right and give the exact replacement text for the side that should change.',
    ].join('\n'),
  },
  {
    key: 'cold-read-part-a',
    prompt: [
      'YOUR LENS: cold read of the preamble and Part A (everything before "Часть B"), as the owner who will decide from it. Part B you only need to skim to check that Part A does not overstate it.',
      'The owner is technically literate, has not seen the audit, reads Russian, and is switching in from other work. They wrote the brief: it calls its parts "Промпт 0" (role and stack-selection rules), "Промпт 1" (concept and the ten agents), "Промпт 2" (MVP goals) and "Промпт 3" (measurable success criteria), so those names are familiar to them.',
      'CHECK: (1) can the owner tell within the first screen what is being asked of them and what happens next; (2) is any term, abbreviation or label used before it is explained, in a way that would actually stop this reader; (3) can each question in A7 be answered as asked - one decision per item or clearly lettered sub-items, with the recommended default stated where the engineer has one; (4) does any statement in Part A claim more than Part B supports, or read as a promise of recovering funds, as legal advice, as an accusation against a named third party, or as an instruction to collect personal data about individuals; (5) are there sentences so compressed or tangled that the owner would have to reread them, or tables whose cells hold reasoning that should be prose; (6) are there leftovers of the drafting process (internal paths, agent or reviewer vocabulary, English fragments that should be Russian, placeholders).',
    ].join('\n'),
  },
]

const SCHEMA = {
  type: 'object',
  properties: {
    verdict: { type: 'string', description: 'two or three sentences: fit to send or not on this lens, and the most important remaining fix if any' },
    issues: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          location: { type: 'string' },
          quote: { type: 'string' },
          severity: { type: 'string', enum: ['blocker', 'major'] },
          problem: { type: 'string' },
          fix: { type: 'string', description: 'exact replacement Russian text' },
        },
        required: ['location', 'quote', 'severity', 'problem', 'fix'],
      },
    },
  },
  required: ['verdict', 'issues'],
}

phase('Final check')
const out = await parallel(
  LENSES.map((l) => () => agent(COMMON + '\n\n' + l.prompt, { label: 'final:' + l.key, phase: 'Final check', schema: SCHEMA }).then((r) => ({ lens: l.key, result: r })))
)
const ok = out.filter(Boolean).filter((x) => x.result)
const failed = LENSES.map((l) => l.key).filter((k) => !ok.find((x) => x.lens === k))
if (failed.length) log('FINAL CHECK LENSES FAILED: ' + failed.join(', '))
return { reviews: ok, failed }
