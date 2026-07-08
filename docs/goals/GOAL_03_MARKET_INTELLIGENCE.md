# GOAL 03 — MARKET INTELLIGENCE ACTIVATION

## Objective

Make Atlas continuously aware of real market conditions without pretending missing data is zero signal.

## Channels

- price
- volume
- volatility
- breadth
- liquidity
- news
- announcements
- macro
- narrative
- attention
- portfolio-relevant events

## Every Channel Must Report

- LIVE
- DELAYED
- CACHED
- SIMULATED
- NOT_CONFIGURED
- RATE_LIMITED
- FAILED

## Runtime Path

Source
→ normalization
→ Input Router
→ EventStream
→ DecisionLoop
→ persisted state
→ UI freshness

## Priorities

1. price
2. volume
3. volatility
4. breadth
5. announcements/news
6. macro
7. attention/narrative

## Acceptance

At least:

- one live real observation reaches real runtime
- freshness is visible
- provider failure degrades honestly
- missing channels remain explicit

## Deliverable

99_Verification/GOAL_03_Market_Intelligence_Report.md

## Transition

Proceed to:

GOAL_04_PORTFOLIO_COGNITION
