# Changelog

## Provider Health Visualization - 2026-07-07

- Improved `/settings` provider management with a health overview, per-provider status pills,
  latency meters, last-check metadata, and compact error summaries.
- Added `/llm/providers/test_all` for safe bulk provider health checks in both FastAPI and stdlib
  fallback UI server modes.
- Preserved provider health states such as `not_configured` instead of collapsing them into
  generic errors, so the UI can distinguish missing API keys/base URLs from unavailable services.
- Extended LLM Provider UI i18n validation to cover the provider health visualization structure and
  bulk test endpoint.
- Did not modify Event Fusion, CIL, LMSE, MPCE, MLE, Decision Contract semantics, runtime cognition
  algorithms, trading execution, prediction logic, or private runtime config.

## LLM Provider Runtime + UI i18n v1.4 - 2026-07-06

- Added `ISSUE-2026-053` and `IP-2026-053` for the LLM provider runtime, UI cognitive redesign,
  and internationalization upgrade.
- Added `runtime/llm/provider_registry.py` with local provider metadata, masked UI-safe provider
  views, local API-key encryption, provider health checks, latency tracking, and fallback-chain
  configuration.
- Added `runtime/llm/provider_router.py` with active-provider routing, fallback isolation, and a
  unified raw-text response envelope.
- Updated `runtime/llm_router.py` to delegate native runtime calls to the provider router while
  preserving Decision Contract raw-text boundaries.
- Added `ui/i18n/i18n.py` and EN/CN language toggle support in the UI top bar and settings page.
- Redesigned `/settings` for multi-provider management, provider connection tests, fallback chain,
  runtime settings, and asset configuration.
- Reduced dashboard debug clutter by simplifying the left provider mini view and right intelligence
  panel while keeping the center workspace as the primary cognitive focus.
- Added LLM Provider UI i18n validation result and Regression Test Case 36.
- Did not modify Event Fusion, CIL, LMSE, MPCE, MLE, Decision Contract semantics, runtime
  cognition algorithms, `portfolio.local.yaml`, trading execution, ML / DL / RL, prediction logic,
  or broker integration.

## Bidirectional Perception Loop v1.2 - 2026-07-06

- Added `ISSUE-2026-035` and `IP-2026-035` for the Bidirectional Market Perception Loop upgrade.
- Added `runtime/cognition/bidirectional_perception_engine.py` with perception weight fields,
  input distribution deformation, attention-influenced observation, biased market view generation,
  and coupling strength metrics.
- Updated `runtime/event_stream.py` to apply bounded BMPL deformation before events are persisted
  to the queue, without modifying Event Fusion core logic.
- Added Bidirectional Perception Loop validation result and Regression Test Case 29.
- Validation showed the same event receives different EventStream priority and Fusion attention
  representation under high-attention vs low-attention system state.
- Did not modify Event Fusion core logic, CIL, LMSE, MPCE, MLE, CDE formulas, Decision Brief
  strategy logic, `portfolio.local.yaml`, trading execution, Buy / Sell recommendations, ML /
  deep learning / reinforcement learning, prediction-engine behavior, or portfolio automation.

## Unified Market Intelligence Core v1.0 - 2026-07-06

- Added `ISSUE-2026-034` and `IP-2026-034` for the Unified Market Intelligence Core upgrade.
- Added `runtime/cognition/unified_market_intelligence_core.py` with unified market state,
  closed-loop feedback, self-referential causality, co-evolution dynamics, unified interpretation,
  and internal system self-adaptation.
- Updated `runtime/decision_loop.py` to route cognition through UMIS after MLE and before State
  Controller, persisting output under `cognition_state.unified_intelligence`.
- Added Unified Market Intelligence validation result and Regression Test Case 28.
- Did not modify Event Fusion Engine logic, Regime Memory architecture, CDE formulas, Decision
  Brief strategy logic, `portfolio.local.yaml`, trading execution, ML / deep learning /
  reinforcement learning, black-box prediction, signal-generator behavior, or portfolio automation.

## Market Law Emergence Engine v0.9 - 2026-07-06

- Added `ISSUE-2026-033` and `IP-2026-033` for the Market Law Emergence Engine upgrade.
- Added `runtime/cognition/market_law_emergence_engine.py` with law discovery, adaptive constraint
  evolution, regime-conditioned law behavior, meta-dynamics, and law consistency checks.
- Updated `runtime/decision_loop.py` to route cognition through MLE after MPCE and before State
  Controller, persisting output under `cognition_state.market_laws`.
- Added Market Law Emergence validation result and Regression Test Case 27.
- Did not modify Event Fusion Engine, Regime Memory, CDE formulas, Decision Brief strategy logic,
  `portfolio.local.yaml`, trading execution, Buy / Sell recommendations, ML / deep learning /
  reinforcement learning, black-box optimization, or portfolio automation.

## Market Physics Constraint Engine v0.8 - 2026-07-06

- Added `ISSUE-2026-032` and `IP-2026-032` for the Market Physics Constraint Engine upgrade.
- Added `runtime/cognition/market_physics_constraint_engine.py` with conservation laws, entropy
  modeling, structural invariants, dynamic-system formulation, constraint-driven regime emergence,
  and system stability monitoring.
- Updated `runtime/decision_loop.py` to route cognition through MPCE after LMSE and before State
  Controller, persisting output under `cognition_state.physics_constraints`.
- Added Market Physics Constraint validation result and Regression Test Case 26.
- Did not modify Event Fusion Engine, Regime Memory, Causal Intelligence Layer, Latent Market
  Structure Engine directly, CDE formulas, Decision Brief strategy logic, `portfolio.local.yaml`,
  trading execution, Buy / Sell recommendations, ML / deep learning / reinforcement learning, or
  portfolio automation.

## Latent Market Structure Engine v0.7 - 2026-07-06

- Added `ISSUE-2026-031` and `IP-2026-031` for the Latent Market Structure Engine upgrade.
- Added `runtime/cognition/latent_market_structure_engine.py` with latent variable inference,
  regime attractor basins, phase space geometry, attention field dynamics, structural evolution,
  and structural counterfactual simulation.
- Updated `runtime/decision_loop.py` to route cognition through LMSE after Market World Model and
  before State Controller, persisting output under `cognition_state.latent_structure`.
- Added Latent Market Structure validation result and Regression Test Case 25.
- Did not modify Event Fusion Engine, Regime Memory implementation, Causal Intelligence Layer
  directly, CDE formulas, Decision Brief strategy logic, `portfolio.local.yaml`, trading execution,
  Buy / Sell recommendations, ML / deep learning / reinforcement learning, or portfolio automation.

## Market World Model v0.6 - 2026-07-06

- Added `ISSUE-2026-030` and `IP-2026-030` for the Market World Model Layer upgrade.
- Added `runtime/cognition/world_model_engine.py` with market state space, deterministic state
  transition, attention-liquidity transformation, regime emergence dynamics, and counterfactual
  market simulation.
- Updated `runtime/decision_loop.py` to route cognition through World Model Engine after CIL and
  before State Controller, persisting output under `cognition_state.world_model`.
- Added Market World Model validation result and Regression Test Case 24.
- Did not modify Event Fusion Engine, Regime Memory system, Causal Intelligence Layer directly,
  CDE formulas, Decision Brief strategy logic, `portfolio.local.yaml`, trading execution, Buy /
  Sell recommendations, ML / deep learning / reinforcement learning, or portfolio automation.

## Causal Intelligence Layer v0.5 - 2026-07-06

- Added `ISSUE-2026-029` and `IP-2026-029` for the Causal Intelligence Layer upgrade.
- Added `runtime/cognition/causal_intelligence_layer.py` with symbolic market causal graph,
  attention meaning resolution, flow propagation, regime emergence reasoning, and lightweight
  counterfactual tests.
- Updated `runtime/decision_loop.py` to route cognition through Causal Intelligence Layer after
  Event Fusion and Regime Memory while preserving State Controller compatibility fields.
- Added Causal Intelligence Layer validation result and Regression Test Case 23.
- Fixed the v0.4.1 source-consistency validation fixture to use a fresh timestamp instead of a stale
  historical timestamp.
- Did not modify Event Fusion Engine, Regime Memory implementation, Input Router, DSA adapter layer,
  CDE formulas, Decision Brief strategy logic, `portfolio.local.yaml`, trading execution, Buy /
  Sell recommendations, machine learning, or portfolio automation.

## Input Abstraction Layer v0.4.1 - 2026-07-06

- Added `ISSUE-2026-028` and `IP-2026-028` for EventStream direct DSA coupling.
- Added `runtime/adapter/input_router.py` as the source-neutral Input Abstraction Layer.
- Updated `runtime/event_stream.py` to depend on Input Router instead of `dsa_bridge.py`.
- Updated `runtime/adapter/dsa_bridge.py` into a compatibility wrapper around Input Router.
- Updated dashboard infrastructure status to use Input Router diagnostics.
- Added recursive illegal-field stripping and neutral `market_event` downgrade for poisoned inputs.
- Added Input Abstraction Layer validation result and Regression Test Case 22.
- Did not modify cognitive layer logic, CDE formulas, Decision Brief strategy logic,
  `portfolio.local.yaml`, trading execution, strategy logic, stock-picking functionality, or
  portfolio automation.

## DSA Infrastructure Adapter v0.4 - 2026-07-06

- Added `ISSUE-2026-027` and `IP-2026-027` for DSA infrastructure adapter integration.
- Added `runtime/adapter/dsa_bridge.py` with unified Atlas event schema and DSA-style signal
  normalization.
- Added `runtime/adapter/data_fetch.py` with optional DSA data-fetch boundary and safe
  `not_configured` fallback.
- Updated EventStream inbox ingestion to accept native Atlas events and DSA-style unified events.
- Added optional LiteLLM backend selection through `ATLAS_LLM_BACKEND=litellm` while preserving
  native LLM router behavior by default.
- Added dashboard infrastructure status for adapter, data source, and LLM backend.
- Added DSA adapter validation script, validation result, and Regression Test Case 21.
- Did not modify Atlas cognitive core logic, import DSA stock-picking logic, add trading execution,
  bypass CDE, modify portfolio files, add broker integration, or convert Atlas into a stock
  analysis bot.

## Cognitive Market OS v0.4 Roadmap - 2026-07-06

- Added proposed Atlas OS v0.4 Cognitive Market OS roadmap.
- Defined future phases for DSA infrastructure reuse, Atlas Adapter Layer, cognitive stabilization,
  causal reasoning, regime intelligence, and full Cognitive OS target architecture.
- Linked the roadmap from Production Trial, README, CDE roadmap, and IP-2026-026.
- Added roadmap review confirming the change is documentation only.
- Did not implement a DSA adapter, runtime code, causal engine, regime intelligence, trading
  execution, CDE bypass, portfolio automation, heavy ML framework, or broker integration.

## Cognitive Runtime v0.3 - 2026-07-05

- Added cognitive runtime layer under `runtime/cognition/`.
- Added Event Fusion Engine, Regime Memory, Causal Market Inference, Anti-overwrite State
  Controller, and Attention vs Liquidity separation model.
- Updated decision loop from latest-event state transition to fused market reality transition.
- Added `CRASH_STRESS` runtime state route without changing trading authority.
- Added `ISSUE-2026-026`, `IP-2026-026`, validation script, validation result, and Regression Test
  Case 20.
- Did not modify runtime host, daemon, scheduler logic, Decision Brief interface, CDE logic,
  portfolio files, trading execution, broker integration, deep learning, reinforcement learning, or
  distributed systems.

## Autonomous Runtime v0.2 - 2026-07-05

- Added launchd-compatible daemon entrypoint in `runtime/atlas_daemon.py`.
- Added SQLite-backed event stream with queue, listener, prioritization, and append-only event
  history.
- Added runtime state machine with `NORMAL`, `ATTENTION_EXPANSION`, `RISK_OFF`, `BREAKOUT`,
  `DISTRIBUTION`, and `HIGH_VOLATILITY`.
- Added continuous decision loop for event -> state -> orchestrator -> Decision Brief -> state
  store updates.
- Enhanced orchestrator with state-driven autonomous routing.
- Enhanced state store with system state, event history, state transitions, and time-series query
  support.
- Enhanced dashboard with system state, event stream, state transitions, and attention heat index.
- Added macOS launchd plist under `deployment/atlas_os.plist`.
- Added `ISSUE-2026-025`, `IP-2026-025`, validation script, validation result, and Regression Test
  Case 19.
- Did not introduce OpenClaw, CrewAI, Conductor, heavy frameworks, trading execution, automatic
  portfolio modification, CDE bypass, broker integration, full backtesting, or autonomous trading.

## Lightweight Execution Kernel v0.1 - 2026-07-05

- Added macOS-friendly Atlas runtime host under `runtime/atlas_host.py`.
- Expanded runtime scheduler with `intraday_run` and supported event triggers.
- Added multi-provider LLM router abstraction for GPT, Claude, Kimi, and GLM aliases with safe
  offline fallback when API keys are unavailable.
- Added SQLite state store for redacted portfolio metadata, regime state, attention history,
  runtime Decision Briefs, and system logs.
- Added non-binding runtime Decision Brief generator.
- Added minimal web dashboard under `web/app.py` with optional FastAPI support and standard-library
  fallback.
- Added `ISSUE-2026-024`, `IP-2026-024`, validation script, validation result, and Regression Test
  Case 18.
- Did not use OpenClaw, CrewAI, Conductor, heavy agent frameworks, trading execution, automatic
  portfolio modification, CDE bypass, full backtesting, or regime prediction implementation.

## Runtime v0.1 Step 1 - 2026-07-05

- Implemented minimal Runtime Step 1 scheduler and orchestrator backbone under `runtime/`.
- Added manual entrypoints for `daily_run`, `weekly_run`, and `event_trigger`.
- Added runtime-generated Decision Brief stub and JSONL execution metadata logging.
- Added `IP-2026-023` and updated `ISSUE-2026-023` to Step 1 Implemented only.
- Added Runtime Step 1 validation script, validation result, and Regression Test Case 17.
- Did not implement automatic trading, state store, full event engine, simulation engine, regime
  prediction, backtesting, CDE logic changes, Decision Brief strategy logic changes,
  `portfolio.local.yaml` changes, portfolio weight changes, or a new investment engine.

## Roadmap Update - 2026-07-05

- Updated Atlas OS roadmap in `README.md` and Capital Deployment Engine documentation.
- Recorded `ISSUE-2026-023` for Runtime System v0.1 request.
- Marked Market Regime Early Warning v0.1 and Attention-Flow Market Transition System v0.1 as
  Proposed Architecture, not implemented.
- Marked Runtime System v0.1 as Issue Recorded / Watching, not Planned implementation.
- Added roadmap verification review.
- Did not implement runtime code, create a new Engine, modify CDE formulas, modify Decision Brief
  strategy logic, modify `portfolio.local.yaml`, store private amounts, or create automatic
  trading.

## Attention-Flow Regime Transition Request - 2026-07-05

- Created `ISSUE-2026-022` for Attention-Flow regime transition request.
- Created proposed-only `IP-2026-022` for Attention-Flow Market Transition System v0.1.
- Added boundary review and test plan for probabilistic regime transition architecture.
- Preserved the Attention -> Flow -> Price -> Transition Probability concept without runtime
  implementation.
- Did not create `regime_engine_v3.py`, `attention_flow_model.py`, or
  `market_regime_transition.py`.
- Did not modify AGENTS, Decision Brief strategy logic, CDE formulas, `portfolio.local.yaml`,
  private amounts, or automatic trading logic.

## Atlas OS v2.2 Architecture Diagrams - 2026-07-05

- Added Chinese and English Atlas OS v2.2 Production Trial architecture diagrams.
- Added `docs/architecture/Atlas_OS_v2.2_Architecture_Check.md`.
- Updated architecture index and README current architecture references.
- Did not modify release version, runtime code, CDE formulas, Decision Brief strategy logic,
  `portfolio.local.yaml`, allocation percentages, or private portfolio data.

## Market Regime Early Warning Architecture - 2026-07-03

- Added proposed architecture for Market Regime Early Warning v0.1, centered on Attention Momentum,
  Narrative Crowding, Attention Exhaustion, and Attention-Price Divergence.
- Linked `IP-2026-021` to the architecture and kept status as `Proposed`.
- Added architecture test plan and review file.
- Did not implement runtime code, create a new Engine, modify CDE formulas, modify Decision Brief
  strategy logic, modify `portfolio.local.yaml`, store private amounts, or create automatic trading.

## A-share Breakdown Early Warning Review - 2026-07-03

- Added A-share market breakdown early-warning review.
- Created `ISSUE-2026-021` for missing market-regime early warning.
- Created proposed-only `IP-2026-021` for Market Regime Early Warning v0.1.
- Final decision: `PARTIAL — EXECUTION WARNING ONLY`.
- Confirmed Atlas previously warned through Severe anomaly, Execution Blocked, and `0-5%`
  migration cap, but did not yet provide full market-regime detection.
- Did not modify CDE formulas, Decision Brief strategy logic, `portfolio.local.yaml`, private
  amounts, create a new Engine, or implement automatic trading.

## GLW Decision Brief Correction - 2026-07-01

- Added GLW Decision Brief correction, marking missing US market data source verification requirements.

## Rebalance Execution Plan Production Trial Exam - 2026-07-01

- Added `99_Verification/Rebalance_Execution_Plan_Production_Trial_Exam.md`.
- Exam result: `PASS`.
- Final decision: `SAFE FOR DAILY PRODUCTION TRIAL`.
- No new Issue created because no defect was found.

## Rebalance Execution Plan v0.1 - 2026-06-30

- Added `ISSUE-2026-020` and `IP-2026-020` for Rebalance Execution Plan v0.1.
- Added `tools/market_data/data_anomaly_check.py`.
- Added Rebalance Execution Plan template under `06_Portfolio/`.
- Added integration guidance to `AGENTS.md` and Atlas skills.
- Added validation result:
  `99_Verification/Rebalance_Execution_Plan_Test_Result.md`.
- Added audit report:
  `99_Verification/Audit_Report_Rebalance_Execution_Plan_v0.1.md`.
- Added Regression Test Case 16.
- Validation detected severe anomaly and capped migration authority at `0-5%`.
- Safety boundaries preserved: no CDE formula, Decision Brief strategy logic, portfolio allocation,
  private amount, new Engine, automatic trading, or Buy / Sell action language.

## Domestic Market Data Support v0.2 - 2026-06-30

- Added `ISSUE-2026-019` and `IP-2026-019` for domestic market data support.
- Added `tools/market_data/domestic_market_snapshot.py`.
- Added `get_domestic_market_snapshot(ticker, market)` to the market data utility interface.
- Added derived domestic indicators: 5D / 10D / 20D / 60D changes, MA5 / MA10 / MA20 / MA60,
  price gaps, high / low distances, volume ratios, turnover ratios when available, market
  structure, execution readiness, and data freshness.
- Added domestic validation result:
  `99_Verification/Domestic_Market_Snapshot_Result.md`.
- Added audit report:
  `99_Verification/Audit_Report_Domestic_Market_Data_Support_v0.2.md`.
- Added Regression Test Case 15.
- Added ticker registry entries for 太极实业, 广钢气体, and 昊华科技.
- Final domestic market data decision: `DOMESTIC READY`.
- Safety boundaries preserved: no strategy logic, CDE logic, Decision Brief strategy logic,
  `portfolio.local.yaml`, allocation percentages, private amounts, automatic trading, dashboard, or
  new Engine modified / added.

## Taijin Ticker Mapping Confirmed - 2026-06-30

- Confirmed `泰金新能` ticker mapping as `688813`, A-share, SH, with `akshare: 688813` and
  `yfinance: 688813.SS`.
- Updated `ISSUE-2026-018` so only `DRAM ETF` remains `Needs Manual Mapping`.
- Reran provider smoke test; `泰金新能` quote, 60-day history, volume, and MA20 / MA60 are available.
- Updated smoke test and audit outputs; final provider status remains `PARTIAL` because `DRAM ETF`
  is still unmapped.
- Did not modify CDE, Decision Brief strategy logic, Strategic Candidate Dashboard logic,
  `portfolio.local.yaml`, allocation percentages, private amounts, or create a new Engine.

## Ticker Registry and Provider Smoke Test - 2026-06-30

- Added `ISSUE-2026-018` for incomplete current holding ticker mapping.
- Updated `tools/market_data/ticker_registry.yaml` with `aliases` fields.
- Normalized `建滔集团` as the registry name for HK ticker `00148` and retained `建韬集团` as an alias.
- Kept `泰金新能` and `DRAM ETF` as `Needs Manual Mapping`.
- Added `99_Verification/smoke_test_market_data_provider.py`.
- Generated `99_Verification/Market_Data_Provider_Smoke_Test_Result.md`.
- Added `99_Verification/Audit_Report_Ticker_Registry_And_Provider_Smoke_Test.md`.
- Added Regression Test Case 14.
- Final provider smoke test decision: `PARTIAL`.
- Did not modify CDE, Decision Brief strategy logic, `portfolio.local.yaml` allocation, create a new
  Engine, implement IDA, or implement Rebalance Execution Plan.

## Market Data Provider Setup v0.1 - 2026-06-30

- Added `IP-2026-017` for Market Data Provider Setup v0.1.
- Converted `ISSUE-2026-017` to an Improvement Proposal.
- Installed and verified importable market data packages:
  - `akshare`
  - `yfinance`
  - `beautifulsoup4`
  - `lxml`
  - `pandas_market_calendars`
- Added lightweight provider utility under `tools/market_data/`.
- Added identity-only ticker registry with no position size, cost, account value, or private amount.
- Added `99_Verification/validate_market_data_provider.py`.
- Generated `99_Verification/Market_Data_Provider_Validation_Result.md`.
- Added `99_Verification/Audit_Report_Market_Data_Provider_Setup.md`.
- Added Regression Test Case 13.
- Final provider decision: `PARTIAL`.
- Did not modify strategy logic, CDE logic, Decision Brief strategy logic, `portfolio.local.yaml`,
  add a new Engine, implement IDA, implement Rebalance Execution Plan, or automatic trading.

## Market Data Fetch Gate v0.1 - 2026-06-30

- Added `ISSUE-2026-015` for Market Data Fetch Gate Missing.
- Added `IP-2026-015` for Market Data Fetch Gate v0.1.
- Required Atlas to attempt market data retrieval before market-sensitive Decision Brief,
  Strategic Candidate Dashboard, CDE, or Rebalance outputs.
- Added Market Data Status block with Current Holdings, Candidate Pool, Valuation, and Technical /
  K-line scopes.
- Added limitation language:
  - `Market Data Missing or Unavailable — Decision Limited`
  - `Market Data Provider Missing — Configure data source`
  - `Fast Rebalance Decision Limited — Market Data Required`
  - `CDE Precision Limited`
- Updated Strategic Candidate Dashboard discipline so Market Confirmation, Valuation Risk,
  Technical Status, and Price Dislocation require market data.
- Updated atlas-research, atlas-portfolio, and atlas-daily skills.
- Updated Execution Log notes so market-sensitive execution records require Market Data Fetch Gate.
- Added Regression Test Case 12.
- Added `99_Verification/Audit_Report_Market_Data_Fetch_Gate.md`.
- Did not add a new Engine, IDA, CDE redesign, Strategic Candidate Dashboard redesign, market data
  crawler, API, trading system, or private portfolio modification.

## Portfolio Freshness and Candidate Identity Fix - 2026-06-30

- Added `ISSUE-2026-012` for Portfolio Context Source Inconsistency.
- Added `ISSUE-2026-013` for Candidate Identity Validation Missing.
- Added Portfolio Context Freshness Check requirements before Decision Brief and Strategic
  Candidate Dashboard outputs.
- Required Portfolio Source, Portfolio Last Updated, Portfolio Consistency, Exposure Sum, Cash /
  Dry Powder, and Decision Limitation in relevant outputs.
- Required `Total Exposure + Cash = 100%` validation for each account.
- Added limitation language for stale, inconsistent, conflicting, or unverifiable portfolio context.
- Added Candidate Identity Validation fields: Code, Candidate, Identity Status, and Source Category.
- Required identity-mismatched candidates to be marked `Candidate Identity Mismatch — Needs
  Validation` and not scored normally.
- Required Top 3 Strategic Candidate Dashboard score explanations.
- Added Regression Test Case 11.
- Added `99_Verification/Audit_Report_Portfolio_Freshness_Candidate_Identity.md`.
- Did not add a new Engine, IDA, Research redesign, Strategic Candidate Dashboard redesign, or
  private portfolio modification.

## Strategic Candidate Dashboard v0.1 - 2026-06-30

- Added `ISSUE-2026-011` for missing strategic candidate evaluation dashboard during Production
  Trial.
- Added `IP-2026-011` for Strategic Candidate Dashboard v0.1.
- Added Research Priority Is Not Trading Authority rule.
- Added optional Strategic Candidate Dashboard section to Decision Brief Template.
- Added Strategic Candidate Score with dimensions for thesis fit, cycle position, evidence
  quality, capital market confirmation, valuation / expectation risk, technical / K-line structure,
  portfolio fit, and trigger readiness.
- Added S/A/B/C/Reject tiering as research priority, not trading authority.
- Updated atlas-research, atlas-portfolio, and atlas-daily skills to trigger the dashboard only for
  candidate, ranking, watchlist, beneficiary, supplier overlap, strategic opportunity, industry
  chain, cycle, or technical-position requests.
- Added Regression Test Case 10 for Strategic Candidate Dashboard.
- Added `99_Verification/Audit_Report_Strategic_Candidate_Dashboard.md`.
- Did not implement a new Engine, IDA, Knowledge Context Injection, research redesign, CDE
  modification, or private portfolio file change.

## Atlas Issue System v1.0 - 2026-06-29

- Established lightweight Production Trial issue tracking under `10_Production_Trial/`.
- Added Issue Template, Issue Policy, Weekly Review Template, and Improvement Candidate Template.
- Added Issue lifecycle: Observed -> Recorded -> Watching -> Discussed -> Accepted / Rejected ->
  Converted to IP -> Implemented -> Validated.
- Added priority rules P0, P1, P2, and P3.
- Updated roadmap: Current now includes v2.1 Production Trial and Atlas Issue System v1.0.
- Added Atlas Engineering System v0.1 to Planned, alongside Risk Budget Engine, Execution
  Governance Engine, Performance Attribution, and Meta Learning Engine.
- Required Planned modules to be validated by Issues before implementation.
- Updated AGENTS with Production Trial Issue Rule: No Issue, No Iteration.
- Added `99_Verification/Audit_Report_AIS_v1.0.md`.
- Did not implement AES, add a new Engine, modify core architecture, or touch private portfolio
  files.

## v2.1 RC Polish - 2026-06-29

- Polished v2.1 RC before Production Trial without adding new capabilities or engines.
- Standardized Improvement Proposal IDs as `IP-YYYY-NNN` with independent Category.
- Added roadmap stage meanings: Released, Current, Planned, Ideas, and Deprecated.
- Added Deprecated roadmap record for the Old Stage Model replaced by Deployment Lifecycle.
- Strengthened Release Gate with Production Trial Validation.
- Defined release lifecycle: Alpha -> RC -> Production Trial -> Final.
- Defined Production Trial as frozen architecture, daily real usage, bug fixes and usability
  improvements only, no new Engine, and no workflow redesign.
- Standardized CDE explainability around What, Why, Limits, and Change Trigger.
- Added `99_Verification/Audit_Report_v2.1_RC_Final_Polish.md`.
- Did not modify Seven Layer Reasoning, World Model, Knowledge Distillation, Decision Engine,
  Portfolio Rules, Capital Deployment logic, Daily Operating Cycle, databases, or private portfolio
  files.

## v2.1 RC - 2026-06-29

- Entered Run First stage: freeze major architecture expansion and make Atlas usable every trading
  day.
- Refined existing Capital Deployment Engine instead of adding new systems.
- Added explainable Deployment Score composition: World Model Stability, Evidence Quality, Price
  Dislocation, Portfolio Exposure, Dry Powder, and Market Risk.
- Added Authority Explainability: Today's Authority must derive from Deployment Score, Deployment
  Lifecycle, Dry Powder, Execution Risk, and a reason.
- Replaced simple Stage labels with Deployment Lifecycle: Observe, Pilot Deployment, Initial
  Deployment, Scaling, Maximum Opportunity, and Capital Preservation.
- Added Run First development principle: Atlas evolves from real investment decisions, not imagined
  features.
- Added future milestones as Planned only: Risk Budget Engine, Execution Governance Engine,
  Performance Attribution, and Meta Learning Engine.
- Updated Decision Brief Template, AGENTS, README, VERSION, and CDE documentation.
- Added `99_Verification/Audit_Report_v2.1_RC_Run_First.md`.
- Did not implement new engines or modify Seven Layer Reasoning, Decision Engine, Portfolio Rules,
  Knowledge Distillation, World Model hierarchy, or databases.

## v2.1 Alpha - 2026-06-29

- Added `10_Capital_Deployment_Engine/Capital_Deployment_Engine.md`.
- Established architecture: World Model -> Decision Engine -> Capital Deployment Engine ->
  Portfolio -> Execution.
- Added Deployment Stages: Stage 0 Observe, Stage 1 Initial Deployment, Stage 2 Deep Pullback,
  Stage 3 Maximum Opportunity.
- Added Deployment Score dimensions: World Model Stability, Fundamental Evidence, Price
  Dislocation, Portfolio Exposure, Dry Powder, and Market Risk.
- Added Capital Authority as maximum additional capital allowed today, not mandatory action.
- Added explicit unlock rules for each deployment stage.
- Updated Decision Brief Template with Capital Deployment Dashboard before Portfolio Impact.
- Updated AGENTS, README, VERSION, and atlas-daily skill references.
- Added `99_Verification/Audit_Report_v2.1_Alpha_CDE.md`.
- Did not modify Seven Layer Reasoning, World Model hierarchy, Knowledge Distillation, Decision
  Engine state machine, Portfolio Rules, or databases.

## v2.0 Alpha - 2026-06-29

- Upgraded Atlas OS from Knowledge Operating System to Cognitive World Model.
- Added Atlas first principle: Atlas does not collect news; Atlas continuously updates its
  understanding of the world.
- Added `09_World_Model/` with `World_Model.md` as the root World Model.
- Established hierarchy: Theory -> World Model -> Pattern -> Case -> Evidence -> Signal.
- Added AI World nodes for Compute, Memory, Networking, Optical Interconnect, Power, Manufacturing,
  Materials, Robotics, and Industry AI.
- Updated Knowledge Philosophy and Knowledge Distillation so World Model is the highest active
  knowledge structure.
- Updated Pattern Template: every Pattern must belong to a World Model Node.
- Updated Case Template: every Case must validate a Pattern and identify the affected World Model
  Node before merge.
- Upgraded Decision Brief from Knowledge Delta to World Model Delta and added World Model Status.
- Updated AGENTS and atlas-daily skill for World Model Delta.
- Added `99_Verification/Audit_Report_v2.0_Alpha_World_Model.md`.
- Kept scope as Markdown knowledge architecture: no Seven Layer, Decision Engine, Portfolio Rules,
  Daily workflow, or database changes.

## v1.1 RC - 2026-06-29

- Upgraded Atlas Decision Experience for CIO-style first-screen reporting.
- Rebuilt `08_Daily_Operating_Cycle/Decision_Brief_Template.md` around Executive Conclusion,
  Today's Action, simplified Portfolio Impact, Today's New Risks, Waiting Triggers, Knowledge
  Delta, Bias Warning, and Decision Confidence.
- Updated `08_Daily_Operating_Cycle/Atlas_Response_Policy.md` with Decision Experience Principle,
  Knowledge Delta Rule, Risk Presentation Rule, and Thesis Health Rule.
- Updated `AGENTS.md` so default answers stop after answering action need, thesis change, and
  next triggers.
- Updated `atlas-daily` skill to keep Research, Knowledge, and Repository views hidden unless
  explicitly requested.
- Added `99_Verification/Audit_Report_v1.1_RC_Decision_Experience.md`.
- Kept scope limited to presentation: no Seven Layer, Decision Engine, Portfolio Rules, or Database
  changes.

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
