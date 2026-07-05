# Attention-Flow Regime Transition Test Plan

This is a test plan only. It is not a runtime regression test.

## Purpose

Validate whether a future Attention-Flow Market Transition implementation can reason probabilistically
about regime transitions instead of producing static labels.

## Required Output Fields

Every future regime analysis must output:

1. Attention State.
2. Flow Inference.
3. Price Confirmation.
4. Regime Probability Vector.
5. Transition Risk Direction.
6. Action Bias, not trade instruction.

## Scenario 1 — Attention Spike Without Price Follow-through

Input:

- search heat rises sharply
- social discussion intensity rises
- news frequency accelerates
- price stalls
- volume expands without price progress
- breadth does not expand

Expected:

- Attention State: High / Accelerating
- Flow Inference: Weak or unconfirmed
- Price Confirmation: Stalling
- Regime Probability Vector: elevated exhaustion / distribution probability
- Transition Risk Direction: Attention Exhaustion
- Action Bias: preserve flexibility / avoid aggressive migration

## Scenario 2 — Price Rally Without Attention Support

Input:

- price rises
- volume confirms
- search heat remains low
- media coverage remains low
- social discussion remains low
- breadth expands quietly

Expected:

- Attention State: Low / Early
- Flow Inference: possible institutional or low-noise accumulation
- Price Confirmation: Confirming
- Regime Probability Vector: elevated early discovery / bull continuation probability
- Transition Risk Direction: constructive, but evidence review required
- Action Bias: research priority may rise; no automatic deployment

## Scenario 3 — Narrative Exhaustion Phase Detection

Input:

- search heat extreme
- KOL narratives synchronized
- retail sentiment clustering extreme
- hard evidence density declines
- leaders fail to make new highs
- followers underperform

Expected:

- Attention State: Extreme / crowded
- Flow Inference: deteriorating
- Price Confirmation: stalling or weakening
- Regime Probability Vector: elevated transition-to-exhaustion and distribution risk
- Transition Risk Direction: Distribution Warning
- Action Bias: CDE precision limited / rebalance capped

## Scenario 4 — Regime Transition Early Warning Accuracy

Input:

- attention velocity positive
- attention acceleration turns negative
- flow probability stops improving
- price acceleration slows
- breadth narrows
- leadership fragility rises

Expected:

- Attention State: High but decelerating
- Flow Inference: weakening follow-through
- Price Confirmation: slowing
- Regime Probability Vector: rising consolidation / exhaustion probability
- Transition Risk Direction: from acceleration toward exhaustion
- Action Bias: reduce aggressiveness, require review

## Scenario 5 — Low-Data Inference Mode

Input:

- user reports search / social / media surge
- independent attention data missing
- market data partial
- breadth data missing

Expected:

- Attention State: user-observed / confidence-limited
- Flow Inference: Unknown / proxy only
- Price Confirmation: Data Missing or Partial
- Regime Probability Vector: confidence-limited
- Transition Risk Direction: Watch
- Action Bias: no precise CDE authority

## Fail Conditions

The future implementation fails if it:

- outputs only binary Bull / Bear labels
- outputs only rule-based trigger alerts
- uses K-line-only decision making
- creates deployment authority without CDE
- uses Buy / Sell language as Atlas action
- treats attention as price movement rather than flow probability
