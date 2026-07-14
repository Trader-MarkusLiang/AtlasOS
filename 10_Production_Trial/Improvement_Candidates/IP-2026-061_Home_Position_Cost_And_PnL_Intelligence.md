# IP-2026-061 - Home Position Cost and PnL Intelligence

Date: 2026-07-14
Status: Accepted for implementation
Category: User Experience / Portfolio / Engineering

## Linked Issue

ISSUE-2026-061 - Home Position Cost and PnL Intelligence Needed

## Objective

Add private local position-cost inputs, deterministic valuation calculations, and compact Home
visualizations so an ordinary user can compare configured allocation, average cost, latest market
price, unrealized return, and optional amount metrics without exposing private portfolio data to
Atlas cognition, external LLMs, persistence telemetry, or Git.

## Implementation Boundary

Allowed:

- Optional local average cost, quantity, cost currency, cost timestamp, and privacy preferences.
- Field-level validation and bilingual Settings controls.
- Deterministic decimal return, total-cost, market-value, and PnL calculations.
- Explicit market freshness, identity, currency, and FX limitation states.
- A private localhost Home projection and investor-focused valuation visualizations.
- Synthetic tests, browser evidence, privacy scans, reports, and presentation-version updates.

Forbidden:

- Changes to Event Fusion, CIL, LMSE, MPCE, MLE, UMIS, trust, forecasts, or CDE semantics.
- Exact private values in general `/state`, telemetry, snapshots, replay, logs, reports, or Git.
- Exact private values in external LLM prompts.
- Inferring missing cost, quantity, account value, price, currency, or FX rates.
- Broker connectivity, trading execution, Buy/Sell outputs, prediction, ML, DL, or RL.
- Treating profit as thesis validation or loss as thesis invalidation.

## Required Result

- Settings accepts optional cost and quantity without JSON in Chinese and English.
- Home shows cost versus latest usable price and a signed PnL bar when mathematically valid.
- Amounts and quantity remain hidden by default and follow local privacy controls.
- Missing, stale, simulated, failed, mismatched-currency, and identity-mismatch data never becomes
  zero or a fabricated valuation.
- Configured allocation remains distinct from estimated current weight.
- Cognition-facing portfolio context and LLM request contexts remain free of private fields.
- Desktop and mobile behavior is browser-validated on canonical port 8765.

## Release Position

Portfolio presentation and Atlas UI minor track only. Atlas Core remains v2.1 RC Production Trial;
runtime cognition and trading authority remain unchanged.
