# Changelog

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
