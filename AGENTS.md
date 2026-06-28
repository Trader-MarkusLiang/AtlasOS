# Atlas OS Codex Instructions

## Identity

Atlas OS is an AI investment research operating system, not a normal software project.

This repository stores investment reasoning, market maps, trading discipline, portfolio process,
and verification records as versioned Markdown knowledge assets.

Do not treat Atlas as a dashboard, crawler, API, database program, trading bot, or generic app
unless the user explicitly changes the project scope.

## Hard Rules

- Treat every user-provided market item, news item, chart, opinion, or company note as a `Signal`
  first, never as a direct trade.
- Every research output must pass through `00_Core/Seven_Layer_Reasoning.md`.
- Do not trade headlines directly.
- Do not confuse Signal with Action.
- Portfolio and trading actions may use only:
  - Research
  - Observe
  - Build
  - Accumulate
  - Hold
  - Reduce
  - Exit
- Do not use Buy / Sell language in Atlas portfolio outputs.
- If evidence is missing or unsupported, write `Unknown` or `Unverified`.
- Real holdings, account details, execution prices, broker data, and private portfolio files must
  not be committed to Git.
- Keep real portfolio data in local-only files such as `portfolio.local.yaml`.
- A trading or allocation action is incomplete unless it includes the Trading Decision Table fields:
  Action, Confidence, Logic Chain, Evidence, Risk / Reward, Trigger, Counter Argument, Review Plan.
- If any required trading-action field is unknown, default to Observe / Watch.
- Do not add new frameworks, automation, dashboards, crawlers, APIs, or database programs unless the
  user explicitly asks for that project-stage change.

## Routing Rules

Use the matching repo skill when the task fits:

- `atlas-research`: industry information, company research, signal judgment, seven-layer reasoning,
  evidence classification, or Living Database update suggestions.
- `atlas-daily`: daily Atlas report, daily signal triage, daily dashboard, daily watch triggers, or
  daily risk summary.
- `atlas-portfolio`: portfolio, position state, `portfolio.local.yaml`, Execution Log, allocation,
  capital actions, or position review.
- `atlas-repository`: Git, Markdown maintenance, audit files, commits, tags, changelog, versioning,
  or repository hygiene.
- `atlas-architecture`: framework review, module boundaries, audit package design, release gate,
  project-stage control, or Atlas system architecture.

If more than one skill matches, use the smallest set that covers the task.

## Required Atlas Sources

Prefer existing Atlas files over new abstractions:

- Core reasoning: `00_Core/Atlas_Principles.md`, `00_Core/Seven_Layer_Reasoning.md`,
  `00_Core/Trading_Discipline.md`
- Trading OS: `03_Trading_OS/Daily_Dashboard_Template.md`,
  `03_Trading_OS/Trading_Decision_Table.md`
- Living database: `02_Databases/AI_Shovel_100.md`, `02_Databases/Alpha_Radar.md`,
  `02_Databases/Risk_Radar.md`, `02_Databases/Order_Book.md`,
  `02_Databases/Price_Transmission.md`
- Current state: `04_Current_State/Bottleneck_Map_v1.md`,
  `04_Current_State/AI_Capital_Map_v1.md`, `04_Current_State/Current_Holdings_Strategy.md`
- Portfolio: `06_Portfolio/Portfolio_Rules.md`, `06_Portfolio/Allocation_Playbook.md`,
  `06_Portfolio/Execution_Log.md`
- Verification: `99_Verification/Audit_Methodology.md`, `99_Verification/Release_Gate.md`

## Session Logging

For task-bearing Atlas conversations, maintain `docs/codex-sessions/` logs according to the global
Codex logging rules.
