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
