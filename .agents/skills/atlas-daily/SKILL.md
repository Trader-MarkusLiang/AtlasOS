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

Existing Portfolio Mapping must show direct / indirect / none exposure, impact, action, and evidence
status for each current holding affected by the input. For Cash / Dry Powder, show deployment
implication and CDE authority impact.

Strategic Candidate Dashboard is optional. When included, it must:

- Map existing holdings first when portfolio context exists.
- Separate existing holdings from new research candidates.
- Score candidates with Strategic Candidate Score, which is not CDE Deployment Score.
- Use research-priority language: Research Priority, Watchlist Tier, Candidate Ranking, Trigger
  Readiness.
- Avoid Buy / Sell / Must Buy / Strong Buy language.
- Use `Data Missing` or `Needs Verification` for missing price, valuation, K-line, customer order,
  volume, or margin data.

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
