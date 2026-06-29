---
name: atlas-portfolio
description: Use for Atlas OS portfolio, position state, portfolio.local.yaml, Execution Log, allocation playbook, capital action vocabulary, and position review. Never commit real holdings or private portfolio data.
---

# Atlas Portfolio

## when_to_use

Use this skill when the task involves:

- Portfolio or position review.
- Capital action suggestions.
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

## forbidden_actions

- Do not commit real holdings, account data, or `portfolio.local.yaml`.
- Do not use Buy / Sell language.
- Do not propose position increase if high-severity risks are unresolved.
- Do not treat execution records as research evidence.
- Do not bypass the Trading Decision Table.
- Do not open a new thematic branch for a highly deployed account unless evidence quality is high,
  direct portfolio mapping exists, CDE authority allows it, and the user explicitly approves.
