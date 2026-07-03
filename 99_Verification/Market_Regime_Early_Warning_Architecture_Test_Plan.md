# Market Regime Early Warning Architecture Test Plan

This is only a test plan, not a runtime test.

## Scenario 1 — Early Discovery

Input:

- low search heat
- low media saturation
- improving evidence
- early price response
- limited social crowding

Expected:

- Regime: Early Discovery
- Decision Impact: Normal
- Confidence: Medium or High depending on data
- No trade command

## Scenario 2 — Attention Momentum

Input:

- search heat rising
- media coverage rising
- social discussion rising
- price and volume confirming
- participation broadening
- evidence remains improving

Expected:

- Regime: Attention Momentum
- Decision Impact: Normal / Watch
- Do not treat rising attention as bearish

## Scenario 3 — Narrative Crowding

Input:

- search heat High / Extreme
- media saturation High
- social discussion Extreme
- "ten-bagger / faith / all-in / cannot miss" language increasing
- new hard evidence limited

Expected:

- Regime: Narrative Crowding
- Decision Impact: CDE Precision Limited
- Rebalance Authority capped
- No deployment authority created

## Scenario 4 — Attention Exhaustion

Input:

- attention remains Extreme
- price stalls
- volume expands without progress
- leaders stop making new highs
- evidence-to-narrative ratio deteriorates

Expected:

- Regime: Attention Exhaustion
- Decision Impact: Rebalance Capped
- Rebalance Authority: 0-5% / 5-10%

## Scenario 5 — Distribution Warning

Input:

- media and social heat remain High
- leaders break or show failed breakout
- breadth narrows
- candidate pool stress rises
- portfolio holdings start 5D sharp pullback

Expected:

- Regime: Distribution Warning
- Decision Impact: Rebalance Capped
- CDE Precision Limited
- No aggressive migration

## Scenario 6 — Risk-Off / Crash Stress

Input:

- leadership breaks
- breadth deteriorates sharply
- candidate pool severe ratio rises
- holdings stress high
- price confirms breakdown

Expected:

- Regime: Risk-Off or Crash Stress
- Decision Impact: Execution Blocked
- Rebalance Authority: 0-5%

## Scenario 7 — Data Insufficient

Input:

- user reports search and media heat
- no independent market data
- no breadth data
- no leadership data

Expected:

- Regime: Data Insufficient or confidence-limited Narrative Crowding
- Confidence: Low / Medium, not High
- Review Required: true
