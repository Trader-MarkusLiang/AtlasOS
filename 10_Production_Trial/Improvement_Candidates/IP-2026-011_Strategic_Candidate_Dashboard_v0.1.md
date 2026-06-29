# IP-2026-011 — Strategic Candidate Dashboard v0.1

## Category

Research / Decision Brief / Candidate Evaluation / Portfolio

## Origin

ISSUE-2026-011 — Strategic Candidate Evaluation Dashboard Missing

## Problem

Atlas can explain current portfolio impact and CDE authority, but it lacks a consistent optional
format for evaluating candidate stocks, beneficiary chains, supplier overlap, rankings, watchlists,
strategic opportunities, and industry-cycle opportunity sets.

## Root Cause

The default Decision Brief is designed to answer today's trading action, thesis change, portfolio
impact, and waiting triggers. Candidate evaluation is related but different: it ranks research
priority, not capital deployment authority.

## Expected Improvement

Add a lightweight optional Strategic Candidate Dashboard v0.1 that:

- Evaluates current holdings first when portfolio context exists.
- Separates existing holdings from new research candidates.
- Scores candidates by strategic research priority.
- Distinguishes evidence status, market confirmation, valuation / expectation risk, technical
  status, portfolio fit, and trigger readiness.
- Explicitly states that Research Priority is not Trading Authority.
- Keeps CDE Deployment Score separate from Strategic Candidate Score.

## Affected Modules

- `AGENTS.md`
- `08_Daily_Operating_Cycle/Decision_Brief_Template.md`
- `.agents/skills/atlas-research/SKILL.md`
- `.agents/skills/atlas-portfolio/SKILL.md`
- `.agents/skills/atlas-daily/SKILL.md`
- `99_Verification/Regression_Tests.md`

## Strategic Candidate Score

Strategic Candidate Score ranges from 0 to 100 and answers:

```text
Is this candidate worth research priority?
```

It does not answer:

```text
Is capital deployment allowed today?
```

| Dimension | Weight |
|---|---:|
| Thesis Fit | 20 |
| Industry Cycle Position | 15 |
| Evidence Quality | 15 |
| Capital Market Confirmation | 15 |
| Valuation / Expectation Risk | 10 |
| Technical / K-line Structure | 10 |
| Portfolio Fit | 10 |
| Trigger Readiness | 5 |

## Tiering

| Score | Tier | Meaning |
|---|---|---|
| 85-100 | S | Strategic priority research candidate |
| 75-84 | A | Strong research candidate; wait for trigger |
| 65-74 | B | Valid watchlist candidate |
| 50-64 | C | Low priority / needs more proof |
| <50 | Reject / Ignore | Not enough strategic value |

Tier is research priority, not trading action. S Tier does not mean Buy. A low-ranked current
holding does not automatically mean Sell. Trading still requires CDE authority.

## Required Output Table

| Candidate | Type | Exposure | Thesis Fit | Cycle | Evidence | Market Confirmation | Valuation Risk | Technical Status | Portfolio Fit | Trigger | Score | Tier | Atlas Stance |
|---|---|---|---|---|---|---|---|---|---|---:|---|---|
| Example | Existing Holding / New Candidate / Sector / Chain | Direct / Indirect / None / Unknown | Data Missing | Data Missing | Known / Partially Verified / Unverified / Data Missing | Confirmed / Partially Confirmed / Not Confirmed / Overcrowded / Broken / Data Missing | Underpriced / Reasonably priced / Fully priced / Overpriced / Bubble risk / Data Missing | Data Missing — needs market data verification | Complements / Duplicates / Concentration risk / Replacement / Irrelevant | Data Missing | __ | __ | Hold / Verify / Research / Watch / Wait for Pullback / Avoid / Replace Candidate / Data Missing |

## Priority

P2

## Status

Implemented

## Compatibility

This is an optional output layer. It does not modify Seven Layer Reasoning, Decision Engine,
Capital Deployment Engine, Portfolio Rules, World Model, Knowledge Distillation, database
structure, or private portfolio data.
