# Changelog

## v1.0 RC - 2026-06-29

- Added Decision First user experience: default output is Decision Brief.
- Added Atlas Interaction Principle: Decision First, Reasoning on Demand.
- Added `08_Daily_Operating_Cycle/Atlas_Response_Policy.md`.
- Added `08_Daily_Operating_Cycle/Decision_Brief_Template.md`.
- Updated `AGENTS.md` so internal layers are hidden unless explicitly requested.
- Updated `atlas-daily` skill to default to Decision Brief and expand Research, Knowledge, and
  Repository views only on request.
- Updated Daily Report Template so the detailed report is an expanded view, not the default.
- Added Decision Engine Presentation Layer note without changing Decision Engine internals.
- Added `99_Verification/Audit_Report_v1.0_RC_User_Experience.md`.

## Portfolio OS v1.2.1 - 2026-06-29

- Added Portfolio Consistency Rules as a self-check layer before Portfolio Action.
- Required Deployment + Cash Allocation to equal 100% for each account.
- Required Bucket Exposure totals to stay within Deployment.
- Required Holding Weight totals to equal Bucket Exposure.
- Required Global Portfolio account weights to equal 100% when Global Portfolio is declared.
- Standardized weight format as percentage with at most one decimal place.
- Added Daily Report Portfolio Consistency status and failure stop rule.
- Added Portfolio Validation -> Consistency Check before Portfolio Action in Decision Gate.
- Updated `AGENTS.md` with the rule that inconsistent Portfolio data blocks Portfolio Action and
  requires user confirmation.
- Added `99_Verification/Audit_Report_Portfolio_Consistency_v1.2.1.md`.

## Portfolio OS v1.2 - 2026-06-29

- Added scale-aware privacy principle: Atlas is wealth-blind, but scale-aware.
- Added Capital Scale Tier as Capital Management Complexity, not wealth ranking.
- Added S0-S8 scale tier reference bands for allocation, execution, liquidity, and risk-budget
  complexity classification.
- Added `capital_profile` to `06_Portfolio/Portfolio_Template.yaml` with `scale_tier`,
  `management_mode`, `execution_complexity`, `liquidity_sensitivity`, and `risk_budget`.
- Updated Portfolio privacy rules to allow only abstract scale-awareness fields, never exact
  account value, balance, net worth, currency amount, cost, market value, or position amount.
- Documented scale-aware privacy in `README.md`, `AGENTS.md`, and
  `06_Portfolio/Portfolio_README.md`.
- Added `99_Verification/Audit_Report_Portfolio_Scale_v1.2.md`.

## Portfolio Allocation v1.1 - 2026-06-29

- Upgraded Portfolio OS to allocation-based privacy architecture.
- Rebuilt `06_Portfolio/Portfolio_Template.yaml` around Capital System, Account, Capital Thesis,
  Capital Bucket, and Holding.
- Removed cost, balance, currency, account value, market value, net worth, and position amount from
  the Git-tracked portfolio template.
- Added account-level cash weight and deployment status.
- Added bucket-level exposure thesis.
- Added Portfolio Privacy Rule and Allocation First Principle.
- Updated Daily Report Portfolio Impact to show deployment, cash allocation, exposure, and action
  without money fields.
- Documented Privacy Design in `README.md` and Capital Allocation OS positioning in
  `06_Portfolio/Portfolio_README.md`.
- Added `99_Verification/Audit_Report_Portfolio_Privacy_v1.1.md`.

## v1.0 - 2026-06-29

- Added Atlas Principle 9: Atlas does not accumulate information; Atlas distills reusable reasoning
  patterns.
- Added `09_Knowledge/` as the Knowledge Distillation Engine template library.
- Added `Knowledge_Philosophy.md` defining Signal, Evidence, Case, and Pattern layers.
- Added `Knowledge_Distillation.md` defining the Signal -> Evidence -> Reasoning -> Pattern
  Extraction -> Case Generation -> Knowledge Merge -> Repository flow.
- Added `Pattern_Template.md`, `Case_Template.md`, and `Proposal_Template.md`.
- Added `Knowledge_Merge_Rules.md` redefining repository updates as Knowledge Merge.
- Added empty `09_Knowledge/Patterns/` and `09_Knowledge/Cases/` library directories.
- Updated `README.md` and `VERSION.md` for v1.0.
- Added `99_Verification/Audit_Report_v1.0.md`.
- Kept scope limited to knowledge architecture and templates: no crawler, program, scripts,
  agents, Seven Layer changes, Framework changes, Decision Engine changes, Portfolio changes, or
  Trading Discipline changes.

## v0.8 Alpha - 2026-06-29

- Added `08_Daily_Operating_Cycle/` for daily Atlas operation.
- Added `Daily_Input_Protocol.md` for daily user input types and first-response classification.
- Added `Daily_Routing_Rules.md` mapping daily tasks to Atlas skills.
- Added `Daily_Update_Workflow.md` defining the daily sequence from input to report and optional
  repository sync.
- Added `Daily_Report_Template.md` as the one-page daily output template.
- Updated `AGENTS.md` with Daily Operating Cycle routing rules and required sources.
- Documented daily use in `README.md`.
- Updated `VERSION.md` to v0.8 Alpha.
- Added `99_Verification/Audit_Report_v0.8_Alpha.md`.
- Kept scope limited to daily operating procedure and template: no new investment framework,
  Core changes, Portfolio Rules changes, software, scripts, automation, or agents.

## v0.7 Alpha - 2026-06-29

- Added `07_Decision_Engine/` as the Atlas Decision Engine operating mechanism.
- Added `Decision_State_Machine.md` with the full decision state flow from Market Signal to Archive.
- Added `Decision_Gate.md` with required gates for evidence, seven-layer reasoning, counter
  argument, risk/reward, portfolio impact, and execution review.
- Added `Decision_Review.md` with the mandatory post-decision review template.
- Added `Decision_Lifecycle.md` assigning state ownership across Research, Trading OS, Portfolio,
  Repository, Daily, and Architecture.
- Documented Decision Engine in `README.md`.
- Updated `VERSION.md` to v0.7 Alpha.
- Added `99_Verification/Audit_Report_v0.7_Alpha.md`.
- Kept scope limited to operating mechanism: no new framework, no changes to Core, Trading OS,
  Portfolio Rules, Living Database structure, software, scripts, or agents.

## v0.6 Alpha - 2026-06-29

- Added root `AGENTS.md` with Atlas hard rules and Codex routing rules.
- Added repo-scoped Codex skills under `.agents/skills/`:
  - `atlas-research`
  - `atlas-daily`
  - `atlas-portfolio`
  - `atlas-repository`
  - `atlas-architecture`
- Documented Codex routing in `README.md`.
- Updated `VERSION.md` to v0.6 Alpha.
- Added `99_Verification/Audit_Report_v0.6_Alpha.md`.
- Kept scope limited to project-level Codex instructions and skill routing: no dashboard, crawler,
  API, database program, automation, or trading bot.

## Portfolio OS Alpha - 2026-06-29

- Added `06_Portfolio/` as the Portfolio Layer.
- Added `Portfolio_README.md`, `Portfolio_Template.yaml`, `Portfolio_Rules.md`, `Execution_Log.md`, and `Allocation_Playbook.md`.
- Added Portfolio responsibility boundaries: Living Database = Research, Portfolio = Capital, Execution = Trade, Review = Learning.
- Added position lifecycle, capital action vocabulary, conviction, priority, and review frequency rules.
- Added portfolio review checklist for daily, weekly, and monthly review.
- Added allocation playbook for pullback, acceleration, and risk-release scenarios.
- Added `portfolio.local.yaml` and `06_Portfolio/portfolio.local.yaml` to `.gitignore`.
- Added `99_Verification/Audit_Report_Portfolio_OS_Alpha.md`.
- Kept scope limited to Portfolio Layer: no new framework, dashboard, agent, program, automation script, or core-principle change.

## v0.5 Alpha - 2026-06-29

- Seeded the first Atlas Living Database in `02_Databases/AI_Shovel_100.md`.
- Added Priority S portfolio/core holdings records for 泰金新能, 罗博特科, 东山精密, 德福科技, DRAM ETF, and Micron.
- Added Priority A core research records across Memory, Equipment, Materials, and Bandwidth.
- Added Priority B watch-pool records.
- Added Company Score records using `Unverified` where public or repository evidence is not yet recorded.
- Upgraded Order Book, Alpha Radar, Risk Radar, and Price Transmission with living seed ledgers.
- Added `99_Verification/Audit_Report_v0.5_Alpha.md`.
- Kept scope limited to Markdown database seeding: no new framework, directory, dashboard, agent, program, or core-principle change.

## v0.4 Alpha - 2026-06-29

- Added company-level scoring fields to AI Shovel 100.
- Added real order, capacity, delivery, backlog, shipment, utilization, and qualification evidence fields to Order Book.
- Added external signal recording fields to Alpha Radar.
- Added company and financial mapping fields to Price Transmission.
- Added trigger threshold fields to Risk Radar.
- Clarified repository release version versus knowledge snapshot version semantics.
- Added `99_Verification/Audit_Report_v0.4_Alpha.md`.
- Kept scope limited to Markdown research database maintenance: no new framework, dashboard, agent, database program, code, or large directory.

## v0.3 Alpha - 2026-06-28

- Cleared high-priority `TBD` placeholders from database and Trading OS templates.
- Filled Alpha Radar, Order Book, Risk Radar, Price Transmission, Daily Dashboard Template, Trading Decision Table, and Capital Rotation Table with maintainable baseline content.
- Clarified framework/snapshot authority for Capital Relay, AI Capital Map, AI Bottleneck Index, and Bottleneck Map.
- Converted the first six regression cases into the unified seven-layer reasoning format.
- Added `99_Verification/Audit_Report_v0.3_Alpha.md`.
- Kept scope limited to Markdown knowledge maintenance: no new framework, dashboard, agent, database program, or code.

## v0.2 Alpha - 2026-06-28

- Added the v0.2 migration blueprint under `docs/`.
- Added Atlas Audit methodology with four audit levels: Structure, Knowledge, Reasoning, and Trading.
- Added v0.2 Audit Report and Release Gate.
- Expanded reasoning audit coverage with HBM Supercycle and DRAM Supercycle cases.
- Updated regression tests and acceptance criteria for v0.2 Alpha.
- Preserved the no-dashboard, no-agent, no-crawler, no-API, no-database-program stage boundary.

## v0.1 Alpha - 2026-06-28

- Created the Atlas OS Git knowledge repository.
- Added core directories for framework, databases, trading OS, current state, cases, and verification.
- Migrated Atlas principles, seven-layer reasoning, AI Bottleneck Index, Capital Relay, ROI Engine, Efficiency Multiplier, Trading OS templates, current holdings strategy, AI Shovel 100, regression tests, and acceptance criteria.
- Initialized Git version management for the migration baseline.
