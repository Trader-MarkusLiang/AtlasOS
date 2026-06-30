---
name: atlas-portfolio
description: Use for Atlas OS portfolio, position state, portfolio.local.yaml, Execution Log, allocation playbook, capital action vocabulary, and position review. Never commit real holdings or private portfolio data.
---

# Atlas Portfolio

## when_to_use

Use this skill when the task involves:

- Portfolio or position review.
- Capital action suggestions.
- Candidate fit versus existing holdings, portfolio overlap, supplier overlap, watchlist priority,
  concentration risk, or strategic opportunity mapping.
- `portfolio.local.yaml` or local-only portfolio records.
- Execution Log entries.
- Allocation Playbook decisions.
- Position lifecycle, risk release, reduction, accumulation, or review cadence.

## required_reads

- `06_Portfolio/Portfolio_Rules.md`
- `06_Portfolio/portfolio.local.yaml` if present, or user-provided portfolio context.
- `06_Portfolio/Allocation_Playbook.md`
- `06_Portfolio/Execution_Log.md`
- `03_Trading_OS/Trading_Decision_Table.md`
- `03_Trading_OS/Capital_Allocation_Board.md`
- `10_Capital_Deployment_Engine/Capital_Deployment_Engine.md`
- `00_Core/Seven_Layer_Reasoning.md`
- `02_Databases/Risk_Radar.md`
- `04_Current_State/Current_Holdings_Strategy.md`

## output_format

Return:

1. Portfolio context and affected position.
   Include Portfolio Source, Portfolio Last Updated, Portfolio Consistency, Exposure Sum, Cash /
   Dry Powder, and Decision Limitation.
2. Existing Portfolio Mapping for any market, industry, company, supply-chain, pricing, macro,
   social media, or thematic investment input.
3. CDE authority impact.
4. Position lifecycle state.
5. Capital action: Research / Observe / Build / Accumulate / Hold / Reduce / Exit.
6. Trading Decision Table fields.
7. Source of funds and destination, if relevant.
8. Risk and invalidation trigger.
9. Execution Log update suggestion, if a trade occurred.
10. Privacy check: confirm no private holding details are being committed.
11. Strategic Candidate Dashboard only when the user asks about candidates, rankings, watchlists,
    beneficiaries, supplier overlap, strategic opportunities, or industry-chain mapping.

## strategic_candidate_dashboard

Strategic Candidate Dashboard must obey Portfolio Context Injection.

Before Decision Brief or Strategic Candidate Dashboard output, validate portfolio freshness:

- Portfolio Source.
- Portfolio Last Updated.
- Portfolio Consistency.
- Exposure Sum.
- Cash / Dry Powder.
- Decision Limitation.

For each account, validate `Total Exposure + Cash = 100%` within small rounding tolerance. If not,
mark `Portfolio Consistency: FAIL`.

If portfolio source is missing, stale, inconsistent, conflicting, or cannot be verified, output
`Portfolio Context Stale / Inconsistent — Decision Limited`, avoid precise CDE authority, and use
conservative Hold / Observe only.

If multiple portfolio versions exist and the latest valid source cannot be determined, output
`Portfolio Context Conflict — Decision Limited`.

When portfolio context exists, include current holdings first. For each current holding show:

- Exposure: Direct / Indirect / None / Unknown.
- Strategic Impact.
- Portfolio Role.
- Action: Hold / Verify / Watch / Reduce Risk / No Change.
- Evidence Status.

Then show new research candidates with:

- Code.
- Candidate.
- Identity Status.
- Source Category.
- Business Link.
- Thesis Fit.
- Evidence Quality.
- Cycle Position.
- Capital Market Confirmation.
- Valuation / Expectation Risk.
- Technical / K-line Status.
- Portfolio Fit.
- Trigger Readiness.
- Tier.

Research Priority Is Not Trading Authority. Strategic Candidate Score ranks research priority; CDE
Deployment Score authorizes capital deployment. A candidate can be S Tier with CDE Authority 0%.

If data is unavailable, write `Data Missing` or `Needs Verification`. Do not invent price,
valuation, K-line, volume, customer order, or margin data.

For candidates extracted from image, screenshot, OCR, social media post, or unstructured text,
validate code and Chinese name. If code and name do not match, output `Candidate Identity Mismatch
— Needs Validation` and do not score the candidate normally.

## forbidden_actions

- Do not commit real holdings, account data, or `portfolio.local.yaml`.
- Do not use Buy / Sell language.
- Do not propose position increase if high-severity risks are unresolved.
- Do not treat execution records as research evidence.
- Do not bypass the Trading Decision Table.
- Do not open a new thematic branch for a highly deployed account unless evidence quality is high,
  direct portfolio mapping exists, CDE authority allows it, and the user explicitly approves.
- Do not treat Strategic Candidate Dashboard ranking as a direct Accumulate / Reduce instruction.
- Do not calculate precise CDE authority when portfolio context is stale, inconsistent, conflicting,
  or cannot be verified.
