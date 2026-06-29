# Atlas OS

Atlas OS is an AI-model-driven investment research and trading decision knowledge system.

This repository stores the core Atlas framework in Git so the principles, reasoning chains,
market maps, trading discipline, and verification cases can be versioned and reused by Codex,
ChatGPT, and future agents.

Current stage: Knowledge Distillation Engine v1.0.

This stage does not build a dashboard, API, database, crawler, agent automation, or complex
software architecture.

## Repository Map

| Directory | Purpose |
|---|---|
| `00_Core/` | Core principles, reasoning chain, and trading discipline |
| `01_Framework/` | AI bottleneck, capital relay, ROI, efficiency, and timing frameworks |
| `02_Databases/` | Initial research databases and watchlists |
| `03_Trading_OS/` | Templates that turn research into trading actions |
| `04_Current_State/` | Current maps, holdings strategy, and growth-curve state |
| `05_Cases/` | Case notes used by the framework |
| `06_Portfolio/` | Portfolio layer for capital, execution, and review governance |
| `07_Decision_Engine/` | Decision lifecycle, gates, review, and state-machine operating mechanism |
| `08_Daily_Operating_Cycle/` | Daily input protocol, routing rules, update workflow, and report template |
| `09_Knowledge/` | Knowledge philosophy, distillation rules, proposal templates, case and pattern library |
| `99_Verification/` | Migration checklist, regression tests, and acceptance criteria |
| `.agents/skills/` | Repo-scoped Codex workflow routing skills |

## Version

Current version: v1.0.

## Architecture Principle

Atlas does not accumulate information.

Atlas distills reusable reasoning patterns.

Atlas does not remember the market.

Atlas learns how markets work.

Atlas 不积累信息。

Atlas 沉淀可复用的推理模式。

Atlas 不记住市场。

Atlas 学习市场运行规律。

## Codex Routing

Atlas OS uses Codex project-level routing so new conversations can inherit core operating rules
without repeating a long prompt.

- `AGENTS.md` is the root project instruction file. It stores only hard rules and routing rules.
- `.agents/skills/atlas-research/` handles research, signal judgment, seven-layer reasoning, and
  Living Database update suggestions.
- `.agents/skills/atlas-daily/` handles daily Atlas reports and daily signal triage.
- `.agents/skills/atlas-portfolio/` handles portfolio, position, allocation, and Execution Log
  workflows.
- `.agents/skills/atlas-repository/` handles Git, Markdown maintenance, audit reports, commits,
  tags, and version work.
- `.agents/skills/atlas-architecture/` handles framework review, module boundaries, audit package
  design, and release gate checks.

All user-provided market information starts as a Signal. Research must pass through Seven Layer
Reasoning before it can affect trading or portfolio action.

## Decision Engine

v0.7 Alpha adds the Atlas Decision Engine as an operating mechanism, not a new investment
framework.

Atlas now runs market information through a complete decision lifecycle:

```text
Market Signal
 ↓
Signal Classification
 ↓
Evidence Collection
 ↓
Seven Layer Reasoning
 ↓
Confidence Scoring
 ↓
Research Conclusion
 ↓
Trading Decision
 ↓
Portfolio Action
 ↓
Execution Review
 ↓
Knowledge Update
 ↓
Archive
```

Decision Engine connects Research, Trading OS, Portfolio, Review, Repository, Daily, and
Architecture into one closed loop. It does not change Atlas Principles, Seven Layer Reasoning,
Trading Discipline, Portfolio Rules, or the Living Database structure.

## Daily Use

v0.8 Alpha adds the Daily Operating Cycle. Each day, the user can input market, industry, company,
portfolio, risk, trading, or repository information in rough form.

Atlas processes daily input in this order:

```text
Classify input
 ↓
Route to the matching skill
 ↓
Place item into Decision Engine state
 ↓
Update research judgment if evidence supports it
 ↓
Review portfolio impact if relevant
 ↓
Output Atlas Daily Report
 ↓
Prepare Repository Sync only if the user confirms
```

If routing is unclear, Atlas defaults to Research and marks missing evidence as `Unknown` or
`Unverified`.

## Knowledge Distillation Engine

v1.0 upgrades Atlas from Knowledge Database to Knowledge Distillation Engine.

Atlas no longer treats news as knowledge. News is Signal. Verified records are Evidence. Durable
knowledge starts when Atlas extracts reusable reasoning, decision logic, Case learning, or Pattern
logic.

Knowledge follows the Atlas Knowledge Pyramid:

```text
Theory
 ↑
Pattern
 ↑
Case
 ↑
Evidence
 ↑
Signal
```

Signal triggers research. Evidence validates Signal. Case validates Pattern. Pattern is extracted
from multiple Cases. Theory cannot be designed; it can only emerge after multiple Patterns remain
stable across years, industries, and cycles.

Knowledge Distillation flow:

```text
Signal
 ↓
Evidence
 ↓
Reasoning
 ↓
Pattern Extraction
 ↓
Case Generation
 ↓
Pattern Validation
 ↓
Knowledge Merge
 ↓
Repository
```

Every durable update starts as a Knowledge Proposal. Proposal comes before Merge. Repository commits
represent Knowledge Merge, not News Archive.

Companies are not Atlas's primary knowledge unit. Companies are instances of Patterns.

## Living Database

Starting in v0.5 Alpha, Atlas tracks companies as living research records:

- Priority S: current portfolio and core capital exposure, reviewed first.
- Priority A: Atlas core research pool, updated after Priority S.
- Priority B: watch pool, promoted only after evidence improves.

Unknown or unsupported data must be recorded as `Unknown` or `Unverified`.

## Portfolio Layer

Portfolio OS Alpha adds a portfolio layer around real capital:

- Living Database handles Research.
- Portfolio handles Capital.
- Execution handles Trade.
- Review handles Learning.

Real holdings must stay out of Git in `portfolio.local.yaml`; Git stores only the template.

## Privacy Design

Atlas Portfolio is a Capital Allocation Operating System, not a wealth tracker.

Atlas is designed not to know the user's asset scale.

Atlas does not store:

- Money.
- Balance.
- Net worth.
- Currency amount.
- Market value.
- Position amount.
- Cost basis.

Atlas stores only:

- Allocation.
- Exposure.
- Thesis.
- Risk.

Therefore Git, Case, Audit, and Session records should not leak wealth information. They should
describe only how capital is allocated, what exposure exists, what thesis the capital serves, and
what risk must be reviewed.

See `VERSION.md` and `CHANGELOG.md`.

## Audit

Every release must pass the Atlas Audit levels in `99_Verification/Audit_Methodology.md`
and the release gate in `99_Verification/Release_Gate.md`.
