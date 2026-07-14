# ISSUE-2026-061 - Home Position Cost and PnL Intelligence Needed

## Status

Converted to IP

## Origin

User Feedback / Real Usage

## Date First Seen

2026-07-14

## Date Last Seen

2026-07-14

## Frequency

1 explicit request during portfolio-first Home review.

## Affected Area

Decision Brief / Portfolio / User Experience / Engineering

## Problem

Home shows configured allocation and market observations, but an ordinary user cannot configure or
compare average cost, optional quantity, current market value, unrealized return, or unrealized PnL.
This weakens position-risk review and makes later portfolio guidance less grounded in the user's
actual execution context.

## Context

The user explicitly approved a local position-cost and PnL visualization. Atlas already has an
ignored local portfolio configuration and normalized market observations. The cognition-facing
portfolio context is intentionally percentage-only and must remain free of exact private values.

## Impact

High

## Evidence

User request:

```text
Home should visualize holding cost, current market price, and profit/loss ratio in addition to
portfolio allocation so later decisions have appropriate position context.
```

## Root Cause Hypothesis

Portfolio setup was designed for allocation-aware cognition before local execution-context
valuation was added. Home therefore has market observations and portfolio percentages but no
bounded local valuation layer joining them.

## Possible Solutions

- Extend ignored local position configuration with optional validated cost, quantity, and currency.
- Add a deterministic local valuation helper outside cognition and LLM paths.
- Add privacy controls and a portfolio-first valuation board on Home.
- Preserve explicit missing, stale, identity, currency, and FX limitation states.

## Priority

P0

## Decision

Convert to Improvement Proposal. The user explicitly approved implementation. This is bounded
Portfolio/UI infrastructure and must not create a cognition, prediction, trading, or CDE Engine.

## Linked IP

IP-2026-061 - Home Position Cost and PnL Intelligence

## Notes

Exact cost, quantity, total cost, market value, PnL amount, account value, broker data, and execution
history are private local data. They must not enter Git, telemetry, snapshots, replay, runtime logs,
or external LLM prompts. Cost is execution and risk context, not thesis evidence.
