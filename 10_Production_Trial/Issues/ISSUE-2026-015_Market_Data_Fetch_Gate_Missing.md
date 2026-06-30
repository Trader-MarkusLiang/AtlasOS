# ISSUE-2026-015 — Market Data Fetch Gate Missing

## Status

Accepted

## Origin

Production Trial / User Feedback

## Date First Seen

2026-06-30

## Date Last Seen

2026-06-30

## Frequency

1

## Affected Area

Market Data / Strategic Candidate Dashboard / CDE / Rebalance / Decision Brief / Execution

## Problem

Atlas can evaluate industry logic and portfolio context, but it does not reliably attempt to fetch
latest market data when market data is required for decision quality.

As a result, Atlas may output:

- `Data Missing`
- `Market Confirmation unavailable`
- `Technical Status unavailable`
- `Valuation Risk unavailable`

without first checking whether current market data is available.

## Context

Production Trial usage now includes candidate rankings, current holdings review, rebalance
questions, price dislocation judgments, K-line / technical context, and CDE authority questions.
These outputs can depend on current stock price, daily change, volume, valuation, or recent price
structure.

## Impact

High

This can affect:

- Candidate ranking.
- K-line assessment.
- Price dislocation judgment.
- Rebalance timing.
- CDE authority.
- Execution window detection.

## Evidence

Production Trial has repeatedly required Atlas to mark market confirmation, technical status,
valuation risk, or price dislocation as `Data Missing` while no explicit market data fetch attempt
was required by the operating rules.

## Root Cause Hypothesis

Atlas has strong portfolio context and research rules, but lacks a gate that decides whether
current market data is required before Decision Brief, Strategic Candidate Dashboard, CDE output, or
rebalance output.

## Possible Solutions

- Add a Market Data Fetch Gate before outputs that depend on price, volume, valuation, K-line, or
  market confirmation.
- Use any locally available provider, such as Yahoo Finance / yfinance, akshare, 东方财富, 同花顺,
  Wind / Choice, exchange data, or web search fallback.
- If market data cannot be retrieved, explicitly output
  `Market Data Missing or Unavailable — Decision Limited`.
- If no provider is available, output `Market Data Provider Missing — Configure data source`.
- Avoid precise CDE authority, price dislocation, K-line, valuation, or intraday execution claims
  when market data is unavailable.

## Priority

P1

## Decision

Accepted / Converted to Improvement Proposal

## Linked IP

IP-2026-015 — Market Data Fetch Gate v0.1

## Notes

This is a lightweight Production Trial gate. It does not add a new Engine, trading system, market
data crawler, IDA, or CDE redesign.
