# Atlas OS

Atlas OS is an AI-model-driven investment research and trading decision knowledge system.

This repository stores the core Atlas framework in Git so the principles, reasoning chains,
market maps, trading discipline, and verification cases can be versioned and reused by Codex,
ChatGPT, and future agents.

Current stage: Decision Operating System Alpha.

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
| `99_Verification/` | Migration checklist, regression tests, and acceptance criteria |
| `.agents/skills/` | Repo-scoped Codex workflow routing skills |

## Version

Current version: v0.7 Alpha.

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

See `VERSION.md` and `CHANGELOG.md`.

## Audit

Every release must pass the Atlas Audit levels in `99_Verification/Audit_Methodology.md`
and the release gate in `99_Verification/Release_Gate.md`.
