---
name: atlas-research
description: Use for Atlas OS industry information, company research, signal judgment, seven-layer reasoning, evidence classification, and Living Database update suggestions. Do not use for Git-only maintenance or direct trade execution.
---

# Atlas Research

## when_to_use

Use this skill when the task involves:

- Industry, company, supply-chain, earnings, order, pricing, or policy information.
- Deciding whether a user-provided item is a real Atlas Signal.
- Running `Fact -> Physics -> Engineering -> Economics -> Finance -> Capital -> Trading`.
- Suggesting updates to Living Database, Alpha Radar, Risk Radar, Order Book, or Price Transmission.
- Candidate stocks, beneficiaries, supplier overlap, rankings, watchlists, industry-chain
  opportunities, strategic opportunities, capital market confirmation, technical / K-line position,
  cycle position, or which names deserve deeper research.

## required_reads

- `00_Core/Atlas_Principles.md`
- `00_Core/Seven_Layer_Reasoning.md`
- `00_Core/Trading_Discipline.md`
- `06_Portfolio/portfolio.local.yaml` if present, or user-provided portfolio context.
- `06_Portfolio/Portfolio_Rules.md`
- `10_Capital_Deployment_Engine/Capital_Deployment_Engine.md`
- `02_Databases/AI_Shovel_100.md`
- `02_Databases/Alpha_Radar.md`
- `02_Databases/Risk_Radar.md`
- `02_Databases/Order_Book.md`
- `02_Databases/Price_Transmission.md`
- `04_Current_State/Bottleneck_Map_v1.md`
- `04_Current_State/AI_Capital_Map_v1.md`

## output_format

Return:

1. Current Portfolio Context if available; otherwise state
   `Portfolio Context Missing or Stale — Decision Limited`.
   Include Portfolio Source, Portfolio Last Updated, Portfolio Consistency, Exposure Sum, Cash /
   Dry Powder, and Decision Limitation.
2. Existing Portfolio Mapping:
   - Direct / Indirect / None exposure.
   - Impact.
   - Action.
   - Evidence status.
3. CDE authority impact.
4. Signal classification: Fact / Signal / Evidence / Risk / Price Action / Noise.
5. Seven-layer reasoning table.
6. Affected bottleneck and current Atlas rank.
7. Evidence quality: Low / Medium / High.
8. Counter argument.
9. Required confirmation.
10. Atlas action: Research / Observe only unless a separate portfolio workflow is requested.
11. Suggested database update, if any, with target file and fields.
12. Strategic Candidate Dashboard only when the user asks about candidates, rankings, watchlists,
    beneficiaries, supplier overlap, strategic opportunities, industry-chain mapping, technical
    position, cycle position, or research priority.

## strategic_candidate_dashboard

Strategic Candidate Dashboard is an optional output layer, not a new Engine and not a trading
recommendation system.

It must include current holdings first when portfolio context exists, then new research candidates.
Use the compact table:

Code | Candidate | Identity Status | Source Category | Type | Exposure | Thesis Fit | Cycle | Evidence | Market Confirmation | Valuation Risk | Technical Status | Portfolio Fit | Trigger | Score | Tier | Atlas Stance

Strategic Candidate Score is 0-100:

- Thesis Fit: 20.
- Industry Cycle Position: 15.
- Evidence Quality: 15.
- Capital Market Confirmation: 15.
- Valuation / Expectation Risk: 10.
- Technical / K-line Structure: 10.
- Portfolio Fit: 10.
- Trigger Readiness: 5.

Tiering:

- 85-100: S, strategic priority research candidate.
- 75-84: A, strong research candidate; wait for trigger.
- 65-74: B, valid watchlist candidate.
- 50-64: C, low priority / needs more proof.
- <50: Reject / Ignore.

Research Priority Is Not Trading Authority. CDE Deployment Score remains the only deployment
authority. Do not describe S Tier as Buy / Sell / Must Buy / Strong Buy.

Candidate identity validation is required for candidates extracted from images, screenshots, OCR,
social media posts, or unstructured text:

- Ticker / Code.
- Chinese Name.
- Category.
- Source Mention.
- Identity Status: Validated / Needs Validation / Mismatch / Data Missing.

If code and name do not match, output `Candidate Identity Mismatch — Needs Validation` and do not
score the candidate normally.

For the Top 3 candidates, or candidates directly related to current holdings, provide compact score
explanations with thesis fit, evidence quality, portfolio fit, missing data, and main trigger. Do
not over-explain every candidate.

Do not invent stock price, PE / PB, market cap, K-line status, volume breakout, valuation level,
customer order, or margin change. If unavailable, write `Data Missing` or `Needs Verification`.

## forbidden_actions

- Do not directly execute trades.
- Do not use Buy / Sell language.
- Do not commit changes unless the user explicitly asks for repository work.
- Do not invent evidence; write `Unknown` or `Unverified`.
- Do not promote a signal to action without trigger and counter argument.
- Do not output research candidates before mapping the signal to existing holdings and Dry Powder
  when portfolio context exists.
- Do not open a new thematic branch for a highly deployed account unless evidence quality is high,
  direct portfolio mapping exists, CDE authority allows it, and the user explicitly approves.
- Do not treat Strategic Candidate Score as CDE Deployment Score.
- Do not turn candidate ranking into a direct trading action.
- Do not score an identity-mismatched candidate normally.
