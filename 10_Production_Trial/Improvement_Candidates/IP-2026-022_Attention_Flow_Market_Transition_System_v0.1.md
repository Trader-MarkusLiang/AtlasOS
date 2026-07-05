# IP-2026-022 — Attention-Flow Market Transition System v0.1

## Category

Market Regime / Decision Engine Support / CDE Support / Strategic Candidate Dashboard / User
Experience

## Origin

ISSUE-2026-022 — Attention-Flow Regime Transition Request

## Problem

Market Regime Early Warning must not remain a static label or rule-based alert system.

The requested improvement is to model market regime transition probability through:

```text
Attention -> Flow Inference -> Price Feedback -> Regime Transition Probability
```

## Root Cause

Rule-based detection can warn after extension or breakdown is visible, but it may remain reactive.
Atlas needs a way to reason about whether attention is becoming capital flow, whether flow is
confirming in price, and whether the market is transitioning toward acceleration, exhaustion,
distribution, consolidation, or crash stress.

## Expected Improvement

Proposed future architecture should allow Atlas to output:

1. Attention State.
2. Flow Inference.
3. Price Confirmation.
4. Regime Probability Vector.
5. Transition Risk Direction.
6. Action Bias, not trade instruction.

## Proposed Architecture

### 1. Attention Layer

Potential inputs:

- search index trend
- social media discussion intensity
- news frequency acceleration
- KOL narrative synchronization
- retail sentiment clustering, including proxy data if direct data is unavailable

Potential outputs:

- `attention_score`: 0-100
- `attention_velocity`
- `attention_acceleration`
- `narrative_concentration_index`

### 2. Flow Inference Layer

Purpose:

Convert attention into capital-flow probability.

Potential outputs:

- `expected_retail_flow_probability`
- `expected_institutional_follow_through`
- `liquidity_inflow_strength`

Key principle:

Attention does not equal price movement. Attention estimates probability of flow.

### 3. Price Feedback Layer

Potential inputs:

- volume expansion
- trend acceleration
- sector rotation speed
- breadth expansion / contraction

Potential outputs:

- `price_acceleration_index`
- `trend_sustainability_score`
- `momentum_strength_curve`

### 4. Regime Transition Probability Layer

Required output probabilities:

- `bull_regime_probability`
- `distribution_risk_probability`
- `transition_to_exhaustion_probability`
- `crash_stress_probability`
- `consolidation_probability`

System must not output binary labels only.

### 5. Attention Lifecycle Model

Lifecycle:

| Stage | Name | Core Question |
|---|---|---|
| Stage 1 | Attention Build-up | Is attention rising before broad price confirmation? |
| Stage 2 | Narrative Formation | Is a coherent theme becoming synchronized? |
| Stage 3 | Flow Confirmation | Is attention converting into capital flow? |
| Stage 4 | Price Acceleration | Is price confirming flow with breadth and volume? |
| Stage 5 | Exhaustion / Distribution | Is attention high while flow / leadership weakens? |

Each stage should later define:

- detection features
- transition conditions
- probability of next stage

## Low-Data Inference Mode

The future architecture must support missing data and proxy signals.

If direct search, social, KOL, or flow data is missing, Atlas may use structured qualitative
observations, public information, and proxy signals, but confidence must be limited.

Example:

```text
Attention State: High
Flow Inference: Unverified / Medium probability
Price Confirmation: Missing
Regime Probability Vector: Confidence Limited
Transition Risk Direction: Watch exhaustion risk
Action Bias: Preserve flexibility
```

## Integration Requirements

Future implementation may integrate with:

- Market Regime Early Warning.
- Decision Brief risk context.
- Strategic Candidate Dashboard scoring.
- Rebalance Authority cap.
- CDE precision status.

Integration is not implemented by this IP.

## Forbidden Output Discipline

Future outputs must not include:

- binary Bull / Bear classification only
- purely rule-based trigger alerts
- K-line-only decision making
- trade instructions
- Buy / Sell language as Atlas action

## Requested Runtime Deliverables

The user requested:

- `regime_engine_v3.py`
- `attention_flow_model.py`
- `market_regime_transition.py`
- AGENTS update.
- Decision Brief Template update.
- Regression Tests.

These are not implemented in this task.

## Affected Modules

Potential future affected modules, subject to Architecture Review and approval:

- `10_Production_Trial/Architecture/IP-2026-021_Market_Regime_Early_Warning_Architecture.md`
- `10_Production_Trial/Improvement_Candidates/IP-2026-021_Market_Regime_Early_Warning_v0.1.md`
- `08_Daily_Operating_Cycle/Decision_Brief_Template.md`
- `.agents/skills/atlas-research/SKILL.md`
- `.agents/skills/atlas-portfolio/SKILL.md`
- `.agents/skills/atlas-daily/SKILL.md`
- `99_Verification/Regression_Tests.md`

## Priority

P1

## Status

Proposed

## Compatibility

This IP is not implemented in this task. It does not create runtime code, does not create a new
Engine, does not modify CDE formulas, does not modify Decision Brief strategy logic, does not
modify `portfolio.local.yaml`, does not store private amounts, and does not enable automatic
trading.

## Approval

Requires user discussion, Architecture Review, Acceptance Test definition, and explicit approval
before implementation.
