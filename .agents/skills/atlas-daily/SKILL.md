---
name: atlas-daily
description: Use for generating the Atlas Daily Report, daily dashboard, daily signal triage, daily risk review, and watch-trigger summary. Do not use for framework creation, database edits, or commits.
---

# Atlas Daily

## when_to_use

Use this skill when the user asks for:

- Daily Atlas report.
- Daily dashboard.
- Daily market or signal triage.
- Daily risk, waiting triggers, or watchlist summary.
- A concise answer to whether today's information changes Atlas action.
- Candidate stocks, beneficiaries, supplier overlap, rankings, watchlists, strategic opportunities,
  industry-chain opportunities, cycle position, or technical / K-line position when requested.
- Daily action, rebalance, candidate ranking, CDE authority, or execution questions that depend on
  current price, daily change, volume, valuation, K-line, market confirmation, or price
  dislocation.

## required_reads

- `03_Trading_OS/Daily_Dashboard_Template.md`
- `00_Core/Seven_Layer_Reasoning.md`
- `00_Core/Trading_Discipline.md`
- `06_Portfolio/portfolio.local.yaml` if present, or user-provided portfolio context.
- `04_Current_State/Bottleneck_Map_v1.md`
- `04_Current_State/AI_Capital_Map_v1.md`
- `04_Current_State/Current_Holdings_Strategy.md`
- `02_Databases/Alpha_Radar.md`
- `02_Databases/Risk_Radar.md`
- `06_Portfolio/Portfolio_Rules.md`
- `10_Capital_Deployment_Engine/Capital_Deployment_Engine.md`

## output_format

Default output is Decision Brief.

Return by default:

1. Date.
2. Trade Today: YES / NO.
3. Executive Conclusion.
4. Portfolio Action using Atlas vocabulary.
5. Current Portfolio Context if available.
   Include Portfolio Source, Portfolio Last Updated, Portfolio Consistency, Exposure Sum, Cash /
   Dry Powder, and Decision Limitation.
6. Existing Portfolio Mapping.
7. Portfolio Impact.
8. Today's New Risks.
9. Waiting Triggers.
10. World Model Delta.
11. Capital Deployment Dashboard with Deployment Lifecycle, Deployment Score composition, and
   authority derivation.
12. Bias Warning.
13. Decision Confidence.
14. Strategic Candidate Dashboard only when requested by candidate, beneficiary, ranking,
    watchlist, strategic opportunity, supplier overlap, industry-chain, cycle position, or
    technical / K-line language.
15. Market Data Status when the daily answer depends on current price, daily change, K-line /
    technical status, volume / turnover, market confirmation, valuation / expectation risk, price
    dislocation, rebalance timing, intraday execution, or CDE authority affected by market movement.

Decision Brief must answer:

1. Do I need to act?
2. Has my thesis changed?
3. What should I watch next?

If these are answered, stop output.

Risk Changes should include only today's new risks. If no new risk appeared, write `No New Risk
Today`.

World Model Delta should describe only changed domain, changed node, weight, confidence, reason,
evidence, and counter evidence in Atlas's World Model. If nothing changed, write `No World Model
Change Today`.

Decision Confidence means evidence completeness, not probability forecast of price direction.

Capital Deployment Dashboard must show:

- Deployment Lifecycle: Observe / Pilot Deployment / Initial Deployment / Scaling / Maximum
  Opportunity / Capital Preservation.
- Deployment Score composition: World Model Stability, Evidence Quality, Price Dislocation,
  Portfolio Exposure, Dry Powder, and Market Risk.
- Today's Authority derived from Deployment Score, Deployment Lifecycle, Dry Powder, Execution Risk,
  and reason.

If current market data is required for Price Dislocation, Market Risk, Execution Risk, Technical
Confirmation, rebalance timing, or intraday action, run Market Data Fetch Gate first. If market
data cannot be retrieved, output `Market Data Missing or Unavailable — Decision Limited`, mark
`CDE Precision Limited`, and avoid precise authority.

Existing Portfolio Mapping must show direct / indirect / none exposure, impact, action, and evidence
status for each current holding affected by the input. For Cash / Dry Powder, show deployment
implication and CDE authority impact.

Portfolio context freshness must be validated before Decision Brief or Strategic Candidate
Dashboard output. If missing, stale, inconsistent, conflicting, or unverifiable, write `Portfolio
Context Stale / Inconsistent — Decision Limited`, avoid precise CDE authority, and use conservative
Hold / Observe only.

Strategic Candidate Dashboard is optional. When included, it must:

- Map existing holdings first when portfolio context exists.
- Separate existing holdings from new research candidates.
- Score candidates with Strategic Candidate Score, which is not CDE Deployment Score.
- Use research-priority language: Research Priority, Watchlist Tier, Candidate Ranking, Trigger
  Readiness.
- Include Code, Candidate, Identity Status, and Source Category for candidates extracted from image,
  screenshot, OCR, social media post, or unstructured text.
- Mark identity mismatches as `Candidate Identity Mismatch — Needs Validation` and do not score them
  normally.
- Provide compact score explanations for Top 3 candidates or candidates directly related to current
  holdings.
- Avoid Buy / Sell / Must Buy / Strong Buy language.
- Use `Data Missing` or `Needs Verification` for missing price, valuation, K-line, customer order,
  volume, or margin data.

Market Data Fetch Gate must run before filling Market Confirmation, Valuation Risk, Technical
Status, Price Dislocation, or market-sensitive candidate ranking. If unavailable, output
`Needs Market Data` / `Data Missing`, and mark Decision Limited when material.

## market_data_fetch_gate

Trigger this gate when the user asks about 调仓, 换仓, 今天能不能买, 今天能不能卖, 是否追,
是否加仓, 是否减仓, K线, 趋势, 市场确认, 资金流, 成交量, 估值, 价格错杀, 候选标的排名,
Strategic Candidate Dashboard, Rebalance Plan, or CDE Authority.

Attempt to retrieve latest available market data from providers available in the local environment,
such as Yahoo Finance / yfinance, akshare, 东方财富, 同花顺, Wind / Choice, exchange data, or web
search fallback. If no provider is available, output:

```text
Market Data Provider Missing — Configure data source
```

If market data cannot be retrieved, output:

```text
Market Data Missing or Unavailable — Decision Limited
```

For quick rebalance or intraday decision without market data, output:

```text
Fast Rebalance Decision Limited — Market Data Required
```

## rebalance_execution_plan

Do not make Rebalance Execution Plan mandatory for every daily answer. Include only the compact
block when the user asks about rebalance / switching / migration / cash redeployment / execution:

```text
Rebalance Plan Required: YES / NO
Migration Authority: 0-5% / 5-10% / 10-20% / 20-40% / 40%+
Reason:
Limits:
Next Trigger:
```

Expanded Rebalance Plan requires Portfolio Context Injection, Market Data Fetch Gate, Domestic
Market Snapshot for China / Hong Kong names, Data Anomaly Check, and CDE boundary.

Execution Plan is not Trading Authority. Migration Authority is not CDE Authority. User
confirmation is required for any actual trade.

Hide Research View, Knowledge View, and Repository View unless the user asks for them.

Research View may include evidence, Seven Layer Reasoning, counter argument, and signal assessment.

Knowledge View may include pattern, confidence, case, theory candidate, and knowledge proposal.

Repository View may include sync, repository, Git, commit, tag, audit, database, and merge details.

## forbidden_actions

- Do not add new frameworks.
- Do not edit databases unless the user explicitly asks.
- Do not commit.
- Do not expose or commit real private holdings.
- Do not turn an unconfirmed signal into an action.
- Do not output only research candidates when portfolio context exists; map current holdings first.
- Do not make Strategic Candidate Dashboard mandatory for every daily answer.
- Do not treat candidate ranking as capital deployment authority.
- Do not score identity-mismatched candidates normally.
