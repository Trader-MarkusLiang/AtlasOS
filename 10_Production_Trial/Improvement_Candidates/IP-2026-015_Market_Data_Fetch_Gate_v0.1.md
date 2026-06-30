# IP-2026-015 — Market Data Fetch Gate v0.1

## Category

Decision Engine / Portfolio / Capital Deployment / User Experience

## Origin

ISSUE-2026-015 — Market Data Fetch Gate Missing

## Problem

Before Atlas produces Decision Brief, Strategic Candidate Dashboard, CDE output, or Rebalance Plan,
it does not consistently determine whether current market data is required.

This can cause Atlas to either leave market-sensitive fields as `Data Missing` without an attempted
fetch, or to risk implying market confirmation, technical status, valuation risk, price
dislocation, rebalance timing, or CDE authority without enough current data.

## Root Cause

Market-sensitive output fields were added during Production Trial, but the operating rules did not
include a required pre-output gate for market data availability.

## Expected Improvement

Add Market Data Fetch Gate v0.1:

- Before market-sensitive outputs, Atlas determines whether current market data is required.
- If required, Atlas attempts to retrieve latest available market data from locally available
  providers or web-search fallback.
- If unavailable, Atlas explicitly marks decision limitations.
- Atlas avoids strong claims about K-line, valuation, market confirmation, price dislocation,
  intraday execution, and precise CDE authority when data is unavailable.

## Affected Modules

- `AGENTS.md`
- `08_Daily_Operating_Cycle/Decision_Brief_Template.md`
- `.agents/skills/atlas-research/SKILL.md`
- `.agents/skills/atlas-portfolio/SKILL.md`
- `.agents/skills/atlas-daily/SKILL.md`
- `99_Verification/Regression_Tests.md`

## Market Data Fetch Gate Rule

When an output depends on any of the following, Atlas must first attempt to retrieve latest
available market data:

- Current stock price.
- Daily price change.
- K-line / technical status.
- Volume / turnover.
- Market confirmation.
- Valuation / expectation risk.
- Price dislocation.
- Rebalance timing.
- Intraday execution.
- Candidate ranking with market confirmation.
- CDE deployment authority affected by price or market movement.

If market data cannot be retrieved, Atlas must output:

```text
Market Data Missing or Unavailable — Decision Limited
```

If no provider is available, Atlas must output:

```text
Market Data Provider Missing — Configure data source
```

## Minimum Required Market Data

For each current holding and each Top candidate when market data is material, Atlas should attempt
to collect:

- Code / ticker.
- Latest price.
- Price timestamp.
- Daily change %.
- Volume / turnover if available.
- 5-day change %.
- 20-day change %.
- 60-day change %.
- Distance from 20-day moving average if available.
- Distance from 60-day moving average if available.
- Market cap if available.
- PE / PB if available.
- Data source.
- Data freshness.

If fields are unavailable, mark them individually as `Data Missing`.

## Output Requirement

When market data is relevant, include:

| Scope | Status | Source | Timestamp | Limitation |
|---|---|---|---|---|
| Current Holdings | Available / Partial / Unavailable | source name | time | limitation |
| Candidate Pool | Available / Partial / Unavailable | source name | time | limitation |
| Valuation | Available / Partial / Unavailable | source name | time | limitation |
| Technical / K-line | Available / Partial / Unavailable | source name | time | limitation |

## CDE Constraint

CDE Deployment Score must not include Price Dislocation, Market Risk, Execution Risk, or Technical
Confirmation as precise components unless market data is available.

If market data is missing, CDE must mark:

```text
CDE Precision Limited
```

and avoid precise authority.

## Priority

P1

## Status

Implemented

## Compatibility

This is a gate and output discipline fix. It does not modify Seven Layer Reasoning, World Model,
Knowledge Distillation, Decision Engine logic, Portfolio Rules, Capital Deployment Engine logic,
database structure, or private portfolio data.
