# Atlas OS

Atlas OS is an AI-model-driven investment research and trading decision knowledge system.

This repository stores the core Atlas framework in Git so the principles, reasoning chains,
market maps, trading discipline, and verification cases can be versioned and reused by Codex,
ChatGPT, and future agents.

Current Core stage: v2.1 Production Trial.

Current productization stage: Clean-room verification complete; production trial candidate, not
Release Candidate. Atlas Core remains an investment research operating system; the runtime and UI layers
are product surfaces around that core, not replacements for the reasoning framework or CDE.

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
| `09_World_Model/` | Atlas World Model: the highest active knowledge structure |
| `10_Capital_Deployment_Engine/` | Capital deployment authority, stages, dry powder, and unlock rules |
| `10_Production_Trial/` | Production Trial issue tracking, weekly reviews, and improvement candidates |
| `99_Verification/` | Migration checklist, regression tests, and acceptance criteria |
| `.agents/skills/` | Repo-scoped Codex workflow routing skills |

## Version

Current Core version: v2.1 RC.

Runtime, UI, and Data tracks use separate version labels because they mature independently:

| Track | Current State |
|---|---|
| Atlas Core / Knowledge OS | v2.1 RC Production Trial |
| Atlas Runtime | v1.6 lean pipeline (fusion + state controller + regime memory + LLM decision + forecast ledger) over the real daemon / EventStream / DecisionLoop path; single daemon entry `runtime.atlas_runtime_daemon`; no 24h proof |
| Atlas Cognitive Overlay | symbolic cognition overlays archived behind `cognition_mode="full"` (not in the default pipeline); most layer validations remain controlled-fixture evidence |
| Atlas UI / Product | first-user setup/start/ask/stop and local position-valuation paths proven; real-time Brief revision polling added; exhaustive bilingual parity and stale-server guard remain partial |
| Atlas Data / Market Intelligence | live market fetch with persistent cache, stale `CACHED` fallback, and rate-limit backoff; breadth/news/macro/narrative channels explicitly not configured |

Current evidence levels:

| Area | Current Evidence |
|---|---|
| LLM provider inference and fallback | `LIVE_PROVEN` through local cc-switch / ARK-compatible route |
| Portfolio context runtime path | `REAL_RUNTIME_PROVEN` through UI config -> daemon -> Decision Brief |
| Forecast lineage and self-iteration | `REAL_RUNTIME_PROVEN` / `LIVE_PROVEN` for treatment-control behavioral delta |
| Daily cycle dispatch | `REAL_RUNTIME_PROVEN` through daemon phase dispatch |
| Live market observation | `PARTIAL` — persistent cache / stale fallback / backoff mitigate provider disconnects and rate limits; channel breadth still limited |
| Release readiness | `PRODUCTION_TRIAL_CANDIDATE`; not RC |
| Real-duration stability | `REAL_RUNTIME_PROVEN` for 2h+ GOAL 07 / clean-room CR08 soaks; 24h still not proven |

Latest release tag: ais-v1.0.

Release lifecycle:

```text
Alpha
 ↓
RC
 ↓
Production Trial
 ↓
Final
```

Production Trial means:

- Architecture frozen.
- Daily real usage.
- Only bug fixes.
- Only usability improvements.
- Issue recording before iteration.
- No new Engine.
- No workflow redesign.

Current architecture diagram:

- `docs/assets/atlas-os-v2.2-architecture.png`
- `docs/assets/atlas-os-v2.2-architecture_en.png`
- `docs/architecture/Atlas_OS_v2.2_Architecture_Check.md`
- `docs/assets/atlas-os-v2-cognitive-world-model-architecture.png`
- `docs/architecture/Atlas_OS_v2_Cognitive_World_Model_Check.md`

## Architecture Principle

Atlas does not collect news.

Atlas continuously updates its understanding of the world.

Atlas does not accumulate information.

Atlas distills reusable reasoning patterns.

Atlas does not remember the market.

Atlas learns how markets work.

Atlas 不积累信息。

Atlas 沉淀可复用的推理模式。

Atlas 不记住市场。

Atlas 学习市场运行规律。

Atlas 不收集新闻。

Atlas 持续更新自己对世界的理解。

Atlas evolves from real investment decisions, not imagined features.

Atlas 的成长来自真实投资决策，而不是不断增加功能。

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

## Capital Deployment Engine

v2.1 RC refines the Capital Deployment Engine between Decision Engine and Portfolio.

```text
World Model
 ↓
Decision Engine
 ↓
Capital Deployment Engine
 ↓
Portfolio
 ↓
Execution
```

CDE decides deployment rhythm:

- Whether deployment is allowed today.
- Today's explainable authority.
- Current deployment lifecycle stage.
- Remaining Dry Powder.
- Next lifecycle unlock conditions.

CDE output must be explainable:

- Deployment Score is broken into World Model Stability, Evidence Quality, Price Dislocation,
  Portfolio Exposure, Dry Powder, and Market Risk.
- Today's Authority must show its origin from Deployment Score, Deployment Lifecycle, Dry Powder,
  Execution Risk, and a short reason.
- Deployment Score, Authority, and Deployment Lifecycle should all answer: What, Why, what limits
  the decision, and what could change the decision.

Deployment Lifecycle:

```text
Observe
 ↓
Pilot Deployment
 ↓
Initial Deployment
 ↓
Scaling
 ↓
Maximum Opportunity
 ↓
Capital Preservation
```

CDE never predicts prices and never executes trades. Authority is permission, not mandatory action.

Run First roadmap:

Roadmap stage meanings:

| Stage | Meaning |
|---|---|
| Released | Production-ready capability. |
| Current | Actively under refinement. |
| Planned | Architecture approved but intentionally not implemented. |
| Ideas | Interesting concepts or proposed architectures waiting for validation / approval. |
| Deprecated | Historical capability retained only for traceability. |

Released:

- Seven Layer Reasoning.
- Decision Engine.
- World Model.
- Portfolio OS.
- Daily Operating Cycle.
- Decision First user experience.

Current:

- v2.1 Production Trial.
- Atlas Issue System v1.0.
- Explainable Capital Deployment Engine.
- Deployment Lifecycle.
- Authority Explainability.
- Market Data Fetch Gate.
- Market Data Provider v0.1 / Domestic Market Data Support v0.2.
- Data Anomaly Check.
- Rebalance Execution Plan v0.1.
- Runtime v0.1 Step 1 scheduler / orchestrator backbone.
- Lightweight Execution Kernel v0.1 local runtime trial.
- Autonomous Runtime v0.2 event-driven local runtime trial.
- Cognitive Runtime v0.3 event fusion / regime memory local trial.
- DSA Infrastructure Adapter v0.4 boundary trial.
- Input Abstraction Layer v0.4.1 cognitive isolation fix.
- Causal Intelligence Layer v0.5 symbolic causal reasoning local trial.
- Market World Model v0.6 structural evolution simulation local trial.
- Latent Market Structure Engine v0.7 market-physics local trial.
- Market Physics Constraint Engine v0.8 constraint-system local trial.
- Market Law Emergence Engine v0.9 adaptive law-emergence local trial.
- Unified Market Intelligence Core v1.0 closed-loop cognition local trial.
- Bidirectional Perception Loop v1.2 input-deformation local trial.

Planned:

| Future Milestone | Status |
|---|---|
| Atlas Engineering System v0.1 | Planned |
| Risk Budget Engine | Planned |
| Execution Governance Engine | Planned |
| Performance Attribution | Planned |
| Meta Learning Engine | Planned |

These modules are not implemented in v2.1 RC. Atlas will add them only if real operation exposes
the need.

Planned modules cannot be implemented until validated by Issues.

Ideas:

| Idea / Proposed Architecture | Status | Boundary |
|---|---|---|
| Market Regime Early Warning v0.1 | Proposed Architecture | `IP-2026-021`; not implemented. |
| Attention-Flow Market Transition System v0.1 | Proposed Architecture | `IP-2026-022`; no runtime code. |
| Runtime System v0.1 / v0.2 / v0.3 | Partial Runtime Trial | `IP-2026-023`, `IP-2026-024`, `IP-2026-025`, and `IP-2026-026`; local host, scheduler, event stream, state machine, cognitive fusion layer, regime memory, causal inference, decision loop, orchestrator, SQLite state, LLM router abstraction, launchd plist, and dashboard are implemented. No trading execution, CDE bypass, portfolio auto-modification, full simulation, broker integration, autonomous trading, deep learning, reinforcement learning, or full backtesting. |
| Cognitive Market OS v0.4 Roadmap | Proposed Roadmap | `10_Production_Trial/Architecture/Atlas_OS_v0.4_Cognitive_Market_OS_Roadmap.md`; Phase 1 adapter boundary is tracked separately in `IP-2026-027`. Full DSA infrastructure merge, causal engine, and regime intelligence remain proposed only. No trading execution, CDE bypass, or portfolio automation is authorized. |
| DSA Infrastructure Adapter v0.4 | Adapter Boundary Trial | `IP-2026-027`; unified schema adapter, inbox ingestion, optional data-fetch hook, optional LiteLLM backend selection, and dashboard infrastructure status are implemented. External DSA source is not bundled or required. No DSA business logic, stock picking, strategy scoring, trading execution, CDE bypass, or portfolio automation. |
| Input Abstraction Layer v0.4.1 | Cognitive Isolation Fix | `IP-2026-028`; EventStream now depends on source-neutral Input Router instead of `dsa_bridge.py`. Illegal strategy/trading fields are stripped and neutralized to `market_event`. No cognitive logic, CDE, portfolio, trading, or stock-picking behavior added. |
| Causal Intelligence Layer v0.5 | Symbolic Causal Reasoning Trial | `IP-2026-029`; adds causal graph, attention meaning resolution, flow propagation, regime emergence reasoning, and lightweight counterfactual inference inside runtime cognition. No Event Fusion, Regime Memory, Input Router, DSA adapter, CDE, Decision Brief strategy, trading execution, ML, or portfolio automation changes are authorized. |
| Market World Model v0.6 | Structural Evolution Simulation Trial | `IP-2026-030`; adds continuous MarketState(t), deterministic state transition, attention-liquidity transformation, regime emergence dynamics, and counterfactual trajectory simulation. Not a forecast model, not trading authority, and no Event Fusion, Regime Memory, CIL, CDE, Decision Brief strategy, ML, or portfolio automation changes are authorized. |
| Latent Market Structure Engine v0.7 | Market Physics Trial | `IP-2026-031`; adds latent variables, regime attractor basins, phase space geometry, attention field dynamics, structural evolution, and structural counterfactual simulation. Not a prediction engine, not trading authority, and no Event Fusion, Regime Memory, CIL, CDE, Decision Brief strategy, ML, or portfolio automation changes are authorized. |
| Market Physics Constraint Engine v0.8 | Constraint-System Trial | `IP-2026-032`; adds liquidity / attention / flow conservation checks, entropy modeling, structural invariants, dynamic-system formulation, constraint-driven regime emergence, and stability monitoring. Not a forecasting engine, not trading authority, and no Event Fusion, Regime Memory, CIL, LMSE, CDE, Decision Brief strategy, ML, or portfolio automation changes are authorized. |
| Market Law Emergence Engine v0.9 | Adaptive Law-Emergence Trial | `IP-2026-033`; adds law discovery, adaptive constraint evolution, regime-conditioned law behavior, meta-dynamics, and contradiction coexistence checks. Not a prediction engine, not trading authority, and no Event Fusion, Regime Memory, CDE, Decision Brief strategy, ML, black-box optimization, or portfolio automation changes are authorized. |
| Unified Market Intelligence Core v1.0 | Closed-Loop Cognition Trial | `IP-2026-034`; adds unified market state, closed-loop feedback, self-referential causality, co-evolution dynamics, unified interpretation, and internal interpretation-weight adaptation. Not a prediction engine, not trading authority, not a signal generator, and no Event Fusion, Regime Memory, CDE, Decision Brief strategy, ML, black-box prediction, or portfolio automation changes are authorized. |
| Bidirectional Perception Loop v1.2 | Input-Deformation Trial | `IP-2026-035`; adds system-state-influenced perception weighting before EventStream queue persistence. Same raw event can receive different internal priority and Fusion representation under different system states. Not a prediction engine, not trading authority, and no Event Fusion core logic, CIL, LMSE, MPCE, MLE, CDE, Decision Brief strategy, ML, or portfolio automation changes are authorized. |

Ideas are not implementation approval.

Runtime or engine-like work requires Issue discussion, Architecture Review, Acceptance Test
definition, and explicit user approval before coding.

Deprecated:

| Deprecated Concept | Replaced By | Reason |
|---|---|---|
| Old Stage Model | Deployment Lifecycle | Lower explainability. |

## Improvement Proposals

Future Improvement Proposal IDs must be globally unique.

Use `IP-YYYY-NNN`, for example `IP-2026-001`.

Do not encode module names in the ID. Use an independent `Category` field.

Supported categories:

- Knowledge
- World Model
- Decision Engine
- Portfolio
- Capital Deployment
- User Experience
- Engineering

## Issue System

Atlas Production Trial follows:

```text
No Issue, No Iteration.
```

没有 Issue，就不进入迭代。

Any new idea must first be recorded as an Issue under `10_Production_Trial/Issues/`.

An Issue is not an Improvement Proposal. It may become an IP only after discussion, priority
review, and user approval.

## Daily Use

v0.8 Alpha adds the Daily Operating Cycle. Each day, the user can input market, industry, company,
portfolio, risk, trading, or repository information in rough form.

Atlas presents daily input through Decision First user experience:

```text
Decision Brief
(default)
 ↓
Research View
(on request)
 ↓
Knowledge View
(on request)
 ↓
Repository View
(on request)
```

The default user is the Chief Investment Officer. Atlas should answer first with the investment
conclusion, action, portfolio impact, risk changes, waiting triggers, and today's learning.

Internal reasoning, Seven Layer detail, Decision Engine state, knowledge proposal, repository
proposal, audit, and Git workflow remain hidden unless requested.

Internally, Atlas still processes daily input in this order:

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

v2.0 Alpha upgrades Atlas from Knowledge Operating System to Cognitive Operating System.

World Model becomes the highest active knowledge structure. Database, Pattern, Case, Evidence, and
Signal are components of World Model.

Knowledge follows the Atlas Knowledge Pyramid:

```text
Theory
 ↑
World Model
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
from multiple Cases. World Model organizes Patterns into Atlas's current understanding of the AI
world. Theory cannot be designed; it can only emerge after multiple Patterns remain stable across
years, industries, and cycles.

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
World Model Update
 ↓
Knowledge Merge
 ↓
Repository
```

Every durable update starts as a Knowledge Proposal. Proposal comes before Merge. Repository commits
represent Knowledge Merge, not News Archive. A Knowledge Merge should explain the World Model
change, or explicitly state that there was no World Model change.

Companies are not Atlas's primary knowledge unit. Companies are instances of Patterns.

Patterns cannot exist without a World Model Node. Cases cannot merge unless they validate a Pattern
and identify the affected World Model Node.

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

Atlas is designed not to know the user's exact asset scale.

Portfolio OS v1.2 refines this rule:

Atlas is wealth-blind, but scale-aware.

Atlas 不感知具体财富金额，但感知资金规模层级。

Atlas cognition, telemetry, and Git do not store:

- Money.
- Balance.
- Net worth.
- Currency amount.
- Market value.
- Position amount.
- Cost basis.

Portfolio OS v1.3 adds an explicit local-only exception for Home valuation. A user may optionally
store average cost, quantity, and currency in the ignored `runtime/config/user_config.json`. Exact
values are used only by deterministic localhost UI rendering and do not enter cognition, external
LLM prompts, telemetry, replay, runtime logs, verification evidence, or Git. They remain execution
and risk context, never thesis evidence.

Atlas stores only:

- Allocation.
- Exposure.
- Thesis.
- Risk.
- Capital Scale Tier.
- Management Mode.
- Execution Complexity.
- Liquidity Sensitivity.
- Risk Budget.

Capital Scale Tier is not a wealth ranking. It is a Capital Management Complexity tier used to
decide how much execution, liquidity, allocation, and review discipline the Portfolio Layer needs.

Therefore Git, Case, Audit, and Session records should not leak wealth information. They should
describe only how capital is allocated, what exposure exists, what thesis the capital serves, and
what risk must be reviewed.

See `VERSION.md` and `CHANGELOG.md`.

## Audit

Every release must pass the Atlas Audit levels in `99_Verification/Audit_Methodology.md`
and the release gate in `99_Verification/Release_Gate.md`.
